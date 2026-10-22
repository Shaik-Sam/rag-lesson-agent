import difflib
import json
import re
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from .checks import run_rule_checks
from .judge import extract_json, judge_lesson
from .models import CheckResult
from .prompts import (
    GENERATOR_SYSTEM,
    PLANNER_SYSTEM,
    feedback_block,
    generator_prompt,
    planner_prompt,
)
from .reporting import new_run_id, write_run_outputs
from .rubric import by_id, ids
from .textstats import all_sentences, flesch_kincaid_grade, word_count

INJECTED_ERROR = "RAG was invented by OpenAI in 2015, and it guarantees 100% correct answers every time."


class LessonState(TypedDict, total=False):
    run_id: str
    topic: str
    attempt: int
    max_retries: int
    inject_error: bool
    injected_error: str
    guidelines: List[str]
    watchlist: Dict[str, List[str]]
    outline: Dict[str, Any]
    lesson: str
    lessons: List[str]
    feedback: str
    attempts: List[Dict[str, Any]]
    rejection_log: List[Dict[str, Any]]
    status: str
    final_lesson: str
    final_attempt: int
    promoted: List[str]
    summary: Dict[str, Any]


def strip_fences(text):
    text = text.strip()
    match = re.match(r"^```(?:markdown|md)?\s*\n(.*?)\n```$", text, re.DOTALL)
    return match.group(1).strip() if match else text


def inject_false_claim(lesson):
    lines = lesson.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^##\s+why", line, re.IGNORECASE):
            lines[index + 1:index + 1] = ["", INJECTED_ERROR]
            return "\n".join(lines)
    return lesson + "\n\n" + INJECTED_ERROR


class Pipeline:
    def __init__(self, settings, llm, memory, log=print):
        self.settings = settings
        self.llm = llm
        self.memory = memory
        self.log = log
        self.graph = self.build()

    def build(self):
        graph = StateGraph(LessonState)
        graph.add_node("load_memory", self.load_memory)
        graph.add_node("plan", self.plan)
        graph.add_node("generate", self.generate)
        graph.add_node("evaluate", self.evaluate)
        graph.add_node("revise", self.revise)
        graph.add_node("ship", self.ship)
        graph.add_node("escalate", self.escalate)
        graph.add_node("persist", self.persist)
        graph.set_entry_point("load_memory")
        graph.add_edge("load_memory", "plan")
        graph.add_edge("plan", "generate")
        graph.add_edge("generate", "evaluate")
        graph.add_conditional_edges("evaluate", self.route, {"ship": "ship", "retry": "revise", "escalate": "escalate"})
        graph.add_edge("revise", "generate")
        graph.add_edge("ship", "persist")
        graph.add_edge("escalate", "persist")
        graph.add_edge("persist", END)
        return graph.compile()

    def run(self, topic, inject_error=False, max_retries=None):
        initial = {
            "run_id": new_run_id(topic),
            "topic": topic,
            "attempt": 1,
            "max_retries": self.settings.clamped_retries(max_retries),
            "inject_error": inject_error,
            "feedback": "",
            "lessons": [],
            "attempts": [],
            "rejection_log": [],
        }
        return self.graph.invoke(initial, {"recursion_limit": 40})

    def load_memory(self, state):
        guidelines = self.memory.active_guidelines()
        watchlist = self.memory.judge_watchlist()
        self.log(f"[memory] {len(guidelines)} learned guideline(s) loaded, {len(watchlist)} judge watch-list item(s)")
        return {"guidelines": guidelines, "watchlist": watchlist}

    def plan(self, state):
        self.log("[plan] building the lesson outline")
        raw = self.llm.complete("plan", PLANNER_SYSTEM, planner_prompt(state["topic"], state["guidelines"]), max_tokens=2000, temperature=0.3)
        try:
            outline = extract_json(raw)
        except Exception:
            outline = {"sections": [], "audience_notes": "Write for a complete beginner."}
        count = len(outline.get("sections", []))
        self.log(f"[plan] outline ready with {count} section(s)")
        return {"outline": outline}

    def generate(self, state):
        attempt = state["attempt"]
        self.log(f"[generate] writing attempt {attempt} of {state['max_retries'] + 1}")
        previous = state["lessons"][-1] if state["lessons"] else None
        prompt = generator_prompt(state["topic"], state["outline"], state["guidelines"], previous, state["feedback"] or None)
        lesson = strip_fences(self.llm.complete("generate", GENERATOR_SYSTEM, prompt, max_tokens=4000, temperature=0.5))
        update = {}
        if state["inject_error"] and attempt == 1:
            lesson = inject_false_claim(lesson)
            update["injected_error"] = INJECTED_ERROR
            self.log("[generate] DELIBERATE ERROR injected into attempt 1 to test the evaluator")
        update["lesson"] = lesson
        update["lessons"] = state["lessons"] + [lesson]
        self.log(f"[generate] attempt {attempt} has {word_count(lesson)} words")
        return update

    def evaluate(self, state):
        attempt = state["attempt"]
        lesson = state["lesson"]
        self.log(f"[evaluate] checking attempt {attempt} against {len(ids())} hard pass/fail checkpoints")
        results = run_rule_checks(lesson) + judge_lesson(self.llm, lesson, state["watchlist"])
        order = {check_id: index for index, check_id in enumerate(ids())}
        results.sort(key=lambda r: order[r.id])
        for result in results:
            mark = "PASS" if result.passed else "FAIL"
            self.log(f"    {mark}  {result.id:<22} {result.reason}")
        failed_ids = [r.id for r in results if not r.passed]
        record = {
            "attempt": attempt,
            "passed": not failed_ids,
            "failed_ids": failed_ids,
            "word_count": word_count(lesson),
            "reading_grade": round(flesch_kincaid_grade(all_sentences(lesson)), 2),
            "results": [r.to_dict() for r in results],
        }
        rejection_log = [dict(entry) for entry in state["rejection_log"]]
        if attempt > 1 and rejection_log:
            previous = state["attempts"][-1]
            before = set(previous["failed_ids"])
            after = set(failed_ids)
            rejection_log[-1]["outcome_after_retry"] = {
                "fixed": sorted(before - after),
                "still_failing": sorted(before & after),
                "newly_failing": sorted(after - before),
                "words_before": previous["word_count"],
                "words_after": record["word_count"],
                "similarity": round(difflib.SequenceMatcher(None, state["lessons"][-2], lesson).ratio(), 2),
            }
        verdict = "PASSED all checkpoints" if not failed_ids else f"REJECTED ({len(failed_ids)} failed)"
        self.log(f"[evaluate] attempt {attempt}: {verdict}")
        return {"attempts": state["attempts"] + [record], "rejection_log": rejection_log}

    def route(self, state):
        if state["attempts"][-1]["passed"]:
            return "ship"
        if state["attempt"] <= state["max_retries"]:
            return "retry"
        return "escalate"

    def revise(self, state):
        last = state["attempts"][-1]
        failed = [r for r in last["results"] if not r["passed"]]
        feedback = feedback_block(failed)
        entry = {
            "attempt": state["attempt"],
            "failed": [
                {
                    "id": r["id"],
                    "name": by_id()[r["id"]].name,
                    "dimension": by_id()[r["id"]].dimension,
                    "reason": r["reason"],
                    "evidence": r["evidence"],
                }
                for r in failed
            ],
            "revision_instructions": feedback,
            "outcome_after_retry": None,
        }
        self.log(f"[revise] sending {len(failed)} failure reason(s) back to the generator")
        return {
            "feedback": feedback,
            "attempt": state["attempt"] + 1,
            "rejection_log": state["rejection_log"] + [entry],
        }

    def ship(self, state):
        self.log("[ship] lesson cleared the bar and is ready for a human")
        return {"status": "SHIPPED", "final_lesson": state["lesson"], "final_attempt": state["attempt"]}

    def escalate(self, state):
        last = state["attempts"][-1]
        failed = [r for r in last["results"] if not r["passed"]]
        entry = {
            "attempt": state["attempt"],
            "failed": [
                {
                    "id": r["id"],
                    "name": by_id()[r["id"]].name,
                    "dimension": by_id()[r["id"]].dimension,
                    "reason": r["reason"],
                    "evidence": r["evidence"],
                }
                for r in failed
            ],
            "revision_instructions": feedback_block(failed),
            "outcome_after_retry": None,
        }
        best = min(range(len(state["attempts"])), key=lambda i: (len(state["attempts"][i]["failed_ids"]), -i))
        self.log("[escalate] retries used up - best draft goes to a human reviewer, NOT shipped")
        return {
            "status": "NEEDS_HUMAN_REVIEW",
            "final_lesson": state["lessons"][best],
            "final_attempt": best + 1,
            "rejection_log": state["rejection_log"] + [entry],
        }

    def persist(self, state):
        attempts = state["attempts"]
        first = attempts[0]
        first_reasons = {r["id"]: r["reason"] for r in first["results"] if not r["passed"]}
        all_failed = sorted({i for a in attempts for i in a["failed_ids"]})
        summary = {
            "first_attempt_failed": first["failed_ids"],
            "all_failed": all_failed,
            "first_attempt_reasons": first_reasons,
            "record": {
                "run_id": state["run_id"],
                "topic": state["topic"],
                "status": state["status"],
                "attempts": len(attempts),
                "first_attempt_failed": first["failed_ids"],
            },
        }
        promoted = self.memory.record_run(summary)
        merged = dict(state)
        merged["promoted"] = promoted
        run_dir = self.settings.output_root / state["run_id"]
        result = write_run_outputs(merged, run_dir)
        result["output_dir"] = str(run_dir)
        if promoted:
            self.log(f"[memory] promoted new guideline(s) from repeated failures: {', '.join(promoted)}")
        self.log(f"[output] files written to {run_dir}")
        return {"promoted": promoted, "summary": result}

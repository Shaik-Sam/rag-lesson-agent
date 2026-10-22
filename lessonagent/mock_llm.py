import json
import re

from .checks import heading_positions
from .data import read_text, reference_facts
from .llm import BaseLLM
from .prompts import LESSON_END, LESSON_START
from .rubric import llm_checkpoints
from .textstats import parse_sections, shorten

INDIA_TERMS = ["india", "hyderabad", "pune", "college", "exam", "scholarship", "whatsapp", "rupee", "ravi", "shop"]
OUTSIDE_REFERENCES = ["previous lesson", "as discussed earlier", "as we saw", "see chapter", "refer to the book"]


def extract_lesson(prompt):
    start = prompt.rfind(LESSON_START)
    if start == -1:
        return ""
    end = prompt.find(LESSON_END, start)
    return prompt[start + len(LESSON_START):end].strip()


class MockLLM(BaseLLM):
    name = "mock"

    def __init__(self, scenario="struggle"):
        self.scenario = scenario
        self.generate_calls = 0

    def complete(self, role, system, user, max_tokens=4000, temperature=0.4):
        if role == "plan":
            return read_text("mock/outline.json")
        if role == "generate":
            self.generate_calls += 1
            if self.scenario == "clean":
                return read_text("mock/final.md")
            names = ["draft_1", "draft_2", "final"]
            return read_text(f"mock/{names[min(self.generate_calls, 3) - 1]}.md")
        return json.dumps({"results": self.judge(extract_lesson(user))})

    def judge(self, lesson):
        results = []
        for checkpoint in llm_checkpoints():
            method = getattr(self, f"judge_{checkpoint.id.lower()}")
            passed, reason, evidence = method(lesson)
            results.append({"id": checkpoint.id, "passed": passed, "reason": reason, "evidence": evidence})
        return results

    def judge_fact_supported(self, lesson):
        patterns = [
            r"\b(?:invented|created|developed|introduced)\s+by\s+(?!Facebook|Meta|researchers)\w+",
            r"\bguarantee[sd]?\b",
            r"\b\d+\s?%",
            r"\b(?!2020\b)(?:19|20)\d{2}\b",
        ]
        evidence = []
        for pattern in patterns:
            match = re.search(pattern, lesson, re.IGNORECASE)
            if match:
                evidence.append(shorten(match.group(0), 90))
        if evidence:
            return False, "The lesson makes a claim that the reference facts do not support.", evidence
        return True, "Every statement matches the reference facts.", []

    def judge_example_relatable(self, lesson):
        sections = parse_sections(lesson)
        body = ""
        for section in sections:
            if "example" in section.title.lower():
                body = " ".join(section.lines).lower()
        if any(re.search(rf"\b{term}\b", body) for term in INDIA_TERMS):
            return True, "The example uses a familiar student or shop situation.", []
        return False, "The example is generic and does not use a situation familiar to an Indian learner.", [shorten(body, 120)]

    def judge_flow_coherent(self, lesson):
        positions = heading_positions(lesson)
        ordered = [positions[k] for k in ["what", "why", "how", "example"] if k in positions]
        if len(ordered) == 4 and ordered == sorted(ordered):
            return True, "Ideas are introduced in a logical order.", []
        return False, "The lesson jumps ahead and skips the step-by-step build-up.", []

    def judge_standalone(self, lesson):
        lowered = lesson.lower()
        hits = [p for p in OUTSIDE_REFERENCES if p in lowered]
        if hits:
            return False, "The lesson depends on outside material.", hits
        if len(lesson.split()) < 300:
            return False, "The lesson is too short to teach a learner from zero.", []
        return True, "A learner with no background can follow the lesson.", []

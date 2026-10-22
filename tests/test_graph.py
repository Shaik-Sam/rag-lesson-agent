import json

import pytest

from lessonagent.config import Settings
from lessonagent.graph import INJECTED_ERROR, Pipeline, inject_false_claim
from lessonagent.judge import extract_json, judge_lesson
from lessonagent.llm import BaseLLM
from lessonagent.memory import Memory
from lessonagent.mock_llm import MockLLM


def make_pipeline(tmp_path, llm):
    settings = Settings()
    settings.memory_path = tmp_path / "memory.json"
    settings.output_root = tmp_path / "out"
    memory = Memory(settings.memory_path, settings.promote_threshold)
    return Pipeline(settings, llm, memory, log=lambda *_: None), settings, memory


def test_clean_scenario_ships_on_first_attempt(tmp_path):
    pipeline, _, _ = make_pipeline(tmp_path, MockLLM("clean"))
    state = pipeline.run("RAG")
    assert state["status"] == "SHIPPED"
    assert len(state["attempts"]) == 1
    assert state["rejection_log"] == []


def test_struggle_scenario_recovers_within_two_retries(tmp_path):
    pipeline, _, _ = make_pipeline(tmp_path, MockLLM("struggle"))
    state = pipeline.run("RAG")
    assert state["status"] == "SHIPPED"
    assert len(state["attempts"]) == 3
    assert len(state["rejection_log"]) == 2
    assert state["rejection_log"][0]["outcome_after_retry"]["fixed"]


def test_injected_error_is_caught_and_fixed(tmp_path):
    pipeline, _, _ = make_pipeline(tmp_path, MockLLM("clean"))
    state = pipeline.run("RAG", inject_error=True)
    first = state["attempts"][0]
    assert "NO_FORBIDDEN_CLAIMS" in first["failed_ids"]
    assert "FACT_SUPPORTED" in first["failed_ids"]
    assert INJECTED_ERROR not in state["final_lesson"]
    assert state["status"] == "SHIPPED"


def test_loop_always_terminates_and_escalates(tmp_path):
    class AlwaysBad(MockLLM):
        def complete(self, role, system, user, max_tokens=4000, temperature=0.4):
            if role == "generate":
                from lessonagent.data import read_text
                return read_text("mock/draft_1.md")
            return super().complete(role, system, user, max_tokens, temperature)

    pipeline, _, _ = make_pipeline(tmp_path, AlwaysBad())
    state = pipeline.run("RAG", max_retries=2)
    assert state["status"] == "NEEDS_HUMAN_REVIEW"
    assert len(state["attempts"]) == 3


def test_retries_are_capped_at_two(tmp_path):
    pipeline, _, _ = make_pipeline(tmp_path, MockLLM("struggle"))
    state = pipeline.run("RAG", max_retries=9)
    assert state["max_retries"] == 2


def test_zero_retries_escalates_after_one_attempt(tmp_path):
    pipeline, _, _ = make_pipeline(tmp_path, MockLLM("struggle"))
    state = pipeline.run("RAG", max_retries=0)
    assert state["status"] == "NEEDS_HUMAN_REVIEW"
    assert len(state["attempts"]) == 1


def test_output_files_are_written(tmp_path):
    pipeline, settings, _ = make_pipeline(tmp_path, MockLLM("struggle"))
    state = pipeline.run("RAG")
    run_dir = settings.output_root / state["run_id"]
    for name in ["lesson.md", "rejection_log.json", "rejection_log.md", "run_summary.json", "attempt_1.md", "evaluation_attempt_1.json"]:
        assert (run_dir / name).exists()


def test_memory_promotes_guideline_after_repeated_failures(tmp_path):
    pipeline, _, memory = make_pipeline(tmp_path, MockLLM("struggle"))
    pipeline.run("RAG")
    assert memory.active_guidelines() == []
    pipeline.llm = MockLLM("struggle")
    pipeline.run("RAG")
    assert any("sentence" in g.lower() for g in memory.active_guidelines())
    reloaded = Memory(memory.path, 2)
    assert reloaded.data["learned_guidelines"]


def test_human_feedback_is_persisted(tmp_path):
    _, _, memory = make_pipeline(tmp_path, MockLLM("clean"))
    memory.add_feedback("Use more rupee examples", "EXAMPLE_RELATABLE")
    assert Memory(memory.path).active_guidelines() == ["Reviewer feedback: Use more rupee examples"]


def test_inject_false_claim_places_it_under_why_heading():
    lesson = "# T\n\n## Why Do We Need RAG?\n\nText."
    assert INJECTED_ERROR in inject_false_claim(lesson)


def test_extract_json_handles_surrounding_text():
    assert extract_json('Here you go: {"a": 1} thanks')["a"] == 1


def test_judge_fails_closed_on_garbage_reply():
    class Garbage(BaseLLM):
        def complete(self, *args, **kwargs):
            return "not json"

    results = judge_lesson(Garbage(), "lesson", {})
    assert results and all(not r.passed for r in results)


def test_judge_fails_closed_on_missing_verdict():
    class Partial(BaseLLM):
        def complete(self, *args, **kwargs):
            return json.dumps({"results": [{"id": "FACT_SUPPORTED", "passed": True, "reason": "ok", "evidence": []}]})

    results = {r.id: r for r in judge_lesson(Partial(), "lesson", {})}
    assert results["FACT_SUPPORTED"].passed
    assert not results["FLOW_COHERENT"].passed

import json
import re

from .models import CheckResult
from .prompts import JUDGE_SYSTEM, judge_prompt
from .rubric import llm_checkpoints


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in judge reply")
    return json.loads(text[start:end + 1])


def judge_lesson(llm, lesson, watchlist):
    expected = [c.id for c in llm_checkpoints()]
    try:
        raw = llm.complete("judge", JUDGE_SYSTEM, judge_prompt(lesson, watchlist), max_tokens=2500, temperature=0.0)
        payload = extract_json(raw)
        items = {item.get("id"): item for item in payload.get("results", [])}
    except Exception as error:
        return [
            CheckResult(check_id, False, f"The judge reply could not be read, so the check failed safely ({error}).", [])
            for check_id in expected
        ]
    results = []
    for check_id in expected:
        item = items.get(check_id)
        if item is None or not isinstance(item.get("passed"), bool):
            results.append(CheckResult(check_id, False, "The judge gave no clear verdict, so the check failed safely.", []))
            continue
        evidence = [str(e) for e in item.get("evidence", [])][:3]
        results.append(CheckResult(check_id, bool(item["passed"]), str(item.get("reason", "")).strip(), evidence))
    return results

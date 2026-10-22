import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .prompts import GUIDELINE_LIBRARY


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_store():
    return {
        "version": 1,
        "runs": [],
        "first_attempt_failures": {},
        "total_failures": {},
        "recent_reasons": {},
        "learned_guidelines": [],
        "human_feedback": [],
    }


class Memory:
    def __init__(self, path, promote_threshold=2):
        self.path = Path(path)
        self.promote_threshold = promote_threshold
        self.data = self.load()

    def load(self):
        if not self.path.exists():
            return empty_store()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return empty_store()
        base = empty_store()
        base.update(data)
        return base

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle, temp_name = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(self.data, stream, indent=2, ensure_ascii=False)
        os.replace(temp_name, self.path)

    def reset(self):
        self.data = empty_store()
        self.save()

    def active_guidelines(self):
        lines = []
        for item in self.data["learned_guidelines"]:
            lines.append(item["text"])
        for item in self.data["human_feedback"]:
            lines.append(f"Reviewer feedback: {item['text']}")
        return lines

    def judge_watchlist(self):
        return {k: list(v)[-2:] for k, v in self.data["recent_reasons"].items() if v}

    def add_feedback(self, text, check_id=None):
        self.data["human_feedback"].append({"text": text, "check_id": check_id, "added_at": now()})
        self.save()

    def record_run(self, summary):
        store = self.data
        first_failed = summary["first_attempt_failed"]
        for check_id in first_failed:
            store["first_attempt_failures"][check_id] = store["first_attempt_failures"].get(check_id, 0) + 1
        for check_id in summary["all_failed"]:
            store["total_failures"][check_id] = store["total_failures"].get(check_id, 0) + 1
        for check_id, reason in summary["first_attempt_reasons"].items():
            reasons = store["recent_reasons"].setdefault(check_id, [])
            reasons.append(reason)
            store["recent_reasons"][check_id] = reasons[-3:]
        known = {g["check_id"] for g in store["learned_guidelines"]}
        promoted = []
        for check_id, count in store["first_attempt_failures"].items():
            if count >= self.promote_threshold and check_id not in known and check_id in GUIDELINE_LIBRARY:
                store["learned_guidelines"].append(
                    {
                        "check_id": check_id,
                        "text": GUIDELINE_LIBRARY[check_id],
                        "failed_first_attempt_in_runs": count,
                        "last_reason": store["recent_reasons"].get(check_id, [""])[-1],
                        "promoted_at": now(),
                    }
                )
                promoted.append(check_id)
        store["runs"].append({**summary["record"], "promoted_guidelines": promoted})
        store["runs"] = store["runs"][-50:]
        self.save()
        return promoted

    def snapshot(self):
        store = self.data
        return {
            "runs_recorded": len(store["runs"]),
            "first_attempt_failures": store["first_attempt_failures"],
            "learned_guidelines": store["learned_guidelines"],
            "human_feedback": store["human_feedback"],
            "recent_runs": store["runs"][-5:],
        }

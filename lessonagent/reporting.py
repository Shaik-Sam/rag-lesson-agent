import json
import re
from datetime import datetime
from pathlib import Path

from .rubric import by_id


def new_run_id(topic):
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:30]
    return f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slug}"


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def render_rejection_markdown(state):
    checks = by_id()
    lines = ["# Rejection Log", "", f"Topic: {state['topic']}", f"Final status: {state['status']}", f"Attempts used: {len(state['attempts'])}", ""]
    if state.get("injected_error"):
        lines += ["Deliberate error injected into attempt 1:", "", f"> {state['injected_error']}", ""]
    if not state["rejection_log"]:
        lines.append("No attempt was rejected. The first draft passed every checkpoint.")
        return "\n".join(lines) + "\n"
    for entry in state["rejection_log"]:
        lines += [f"## Attempt {entry['attempt']} - rejected", ""]
        lines += ["| Checkpoint | Dimension | Why it failed |", "| --- | --- | --- |"]
        for item in entry["failed"]:
            dimension = checks[item["id"]].dimension
            lines.append(f"| {item['id']} | {dimension} | {item['reason']} |")
        lines.append("")
        lines.append("Evidence:")
        for item in entry["failed"]:
            for evidence in item["evidence"][:2]:
                lines.append(f"- {item['id']}: {evidence}")
        lines += ["", "Instructions sent back to the generator:", "", "```", entry["revision_instructions"], "```", ""]
        outcome = entry.get("outcome_after_retry")
        if outcome:
            lines += [
                "What changed on the retry:",
                "",
                f"- Fixed: {', '.join(outcome['fixed']) or 'none'}",
                f"- Still failing: {', '.join(outcome['still_failing']) or 'none'}",
                f"- Newly failing: {', '.join(outcome['newly_failing']) or 'none'}",
                f"- Word count: {outcome['words_before']} to {outcome['words_after']}",
                f"- Text similarity to the rejected draft: {outcome['similarity']}",
                "",
            ]
        else:
            lines += ["No retry was left. The best draft was sent to a human reviewer.", ""]
    return "\n".join(lines) + "\n"


def write_run_outputs(state, run_dir):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    for index, attempt in enumerate(state["attempts"], start=1):
        (run_dir / f"attempt_{index}.md").write_text(state["lessons"][index - 1], encoding="utf-8")
        write_json(run_dir / f"evaluation_attempt_{index}.json", attempt)
    filename = "lesson.md" if state["status"] == "SHIPPED" else "lesson_needs_review.md"
    (run_dir / filename).write_text(state["final_lesson"], encoding="utf-8")
    write_json(run_dir / "rejection_log.json", state["rejection_log"])
    (run_dir / "rejection_log.md").write_text(render_rejection_markdown(state), encoding="utf-8")
    write_json(run_dir / "outline.json", state["outline"])
    summary = {
        "run_id": state["run_id"],
        "topic": state["topic"],
        "status": state["status"],
        "attempts_used": len(state["attempts"]),
        "max_retries": state["max_retries"],
        "final_attempt": state["final_attempt"],
        "injected_error": state.get("injected_error"),
        "active_guidelines_used": state["guidelines"],
        "promoted_guidelines": state.get("promoted", []),
    }
    write_json(run_dir / "run_summary.json", summary)
    return summary

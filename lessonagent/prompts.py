import json

from .data import language_rules, lesson_spec, reference_facts
from .rubric import CHECKPOINTS, llm_checkpoints

LESSON_START = "<<<LESSON"
LESSON_END = ">>>"

GUIDELINE_LIBRARY = {
    "FACT_SUPPORTED": "Use only statements from the reference facts. Never add extra names, dates or numbers.",
    "NO_FORBIDDEN_CLAIMS": "Never say RAG guarantees correct answers. Never name a company that created RAG other than Facebook AI Research (Meta). Mention only the year 2020.",
    "READING_GRADE": "Write at a reading grade of 7 or lower. Prefer words with one or two syllables. Avoid long, formal words.",
    "SHORT_SENTENCES": "Keep every sentence under 20 words and the average under 12 words. One idea per sentence.",
    "SIMPLE_VOCABULARY": "Do not use formal words such as leverage, utilize, comprehensive, robust or furthermore. Do not use English idioms.",
    "WORKED_EXAMPLE": "Include the section A Worked Example with one real question written inside quotes, followed through every step.",
    "EXAMPLE_RELATABLE": "Build the worked example around an Indian college student or a local shop, for example exam fees, scholarships or WhatsApp.",
    "JARGON_DEFINED": "Define each technical term in the same sentence where it first appears, using words like 'is called', 'means' or 'stands for'.",
    "KEY_CONCEPTS_COVERED": "Cover chunks, embeddings, vector database, retrieval, augmentation, generation and limits.",
    "SECTION_ORDER": "Use exactly these H2 headings in order: What Is RAG?, Why Do We Need RAG?, How RAG Works, A Worked Example, Where RAG Can Go Wrong, Quick Recap, Key Words.",
    "FLOW_COHERENT": "Explain every idea before you use it. Use words like first, then and so to connect steps.",
    "STANDALONE": "Never refer to other lessons or outside material. Assume the learner knows nothing.",
    "LENGTH_WITHIN_RANGE": "Keep the lesson between 650 and 1000 words.",
}

PLANNER_SYSTEM = (
    "You are a curriculum planner for beginner technical lessons. "
    "You reply with one JSON object and nothing else."
)

GENERATOR_SYSTEM = (
    "You are an expert teacher who writes beginner lessons for 12th-grade graduates from India. "
    "They have limited English vocabulary, come from non-English-medium schools, and want to start an AI career. "
    "You write in simple, short sentences with everyday words. "
    "You only state facts that appear in the reference facts. "
    "You reply with the lesson in Markdown and nothing else."
)

JUDGE_SYSTEM = (
    "You are a strict quality reviewer for beginner lessons. "
    "Each checkpoint is hard pass or fail. There is no partial credit. If you are unsure, fail the checkpoint. "
    "You reply with one JSON object and nothing else."
)


def facts_block():
    facts = reference_facts()["facts"]
    return "\n".join(f'{f["id"]}: {f["statement"]}' for f in facts)


def headings_block():
    return "\n".join(f"- {h['label']}" for h in lesson_spec()["headings"])


def planner_prompt(topic, guidelines):
    learned = "\n".join(f"- {g}" for g in guidelines) or "- none yet"
    return (
        f"Topic: {topic}\n\n"
        f"Reference facts:\n{facts_block()}\n\n"
        f"Required section headings, in this order:\n{headings_block()}\n\n"
        f"Lessons learned from earlier runs:\n{learned}\n\n"
        "Plan a standalone beginner lesson. Return JSON with the keys: audience_notes, analogy, example_idea, "
        "sections. Each item in sections has heading, goal and key_points (a list). "
        "The example_idea must be a situation a student or shop owner in India knows well."
    )


def generator_prompt(topic, outline, guidelines, previous_lesson=None, feedback=None):
    rules = language_rules()
    learned = "\n".join(f"- {g}" for g in guidelines) or "- none yet"
    parts = [
        f"Topic: {topic}",
        f"Reference facts (the only source of truth):\n{facts_block()}",
        f"Lesson plan:\n{json.dumps(outline, indent=2)}",
        f"Use exactly these H2 headings in this order:\n{headings_block()}",
        "Style rules:\n"
        f"- Reading grade {rules['max_reading_grade']} or lower.\n"
        f"- Average sentence {rules['max_average_sentence_words']} words or fewer. No sentence over {rules['max_sentence_words']} words.\n"
        "- Define every technical term in the sentence where it first appears.\n"
        "- Do not use formal words or idioms.\n"
        "- The worked example must use an Indian student or shop situation and one question inside quotes.\n"
        f"- Length between {lesson_spec()['min_words']} and {lesson_spec()['max_words']} words.\n"
        "- Start with one H1 title.",
        f"Lessons learned from earlier runs (follow them):\n{learned}",
    ]
    if previous_lesson and feedback:
        parts.append(f"Your previous version:\n{LESSON_START}\n{previous_lesson}\n{LESSON_END}")
        parts.append(f"A reviewer rejected it. Fix every point below. Keep the parts that already passed.\n{feedback}")
        parts.append("Write the complete corrected lesson now.")
    else:
        parts.append("Write the complete lesson now.")
    return "\n\n".join(parts)


def judge_prompt(lesson, watchlist):
    checks = "\n".join(f"- {c.id}: {c.requirement}" for c in llm_checkpoints())
    watch_lines = []
    for check_id, reasons in watchlist.items():
        for reason in reasons:
            watch_lines.append(f"- {check_id}: earlier lessons failed because: {reason}")
    watch = "\n".join(watch_lines) or "- none yet"
    return (
        f"Reference facts:\n{facts_block()}\n\n"
        f"Checkpoints to judge:\n{checks}\n\n"
        f"Known failure patterns from earlier runs. Look for them closely:\n{watch}\n\n"
        f"Lesson to review:\n{LESSON_START}\n{lesson}\n{LESSON_END}\n\n"
        'Return JSON exactly like {"results": [{"id": "CHECK_ID", "passed": true, "reason": "one short sentence", '
        '"evidence": ["short quote from the lesson"]}]}. Include every checkpoint id once. '
        "When a checkpoint fails, quote the exact words that caused it in evidence."
    )


def feedback_block(failed):
    by_id = {c.id: c for c in CHECKPOINTS}
    lines = []
    for index, item in enumerate(failed, start=1):
        checkpoint = by_id[item["id"]]
        lines.append(f"{index}. {item['id']} - {checkpoint.requirement}")
        lines.append(f"   Why it failed: {item['reason']}")
        for evidence in item.get("evidence", [])[:3]:
            lines.append(f"   Evidence: {evidence}")
        lines.append(f"   How to fix: {checkpoint.fix_hint}")
    return "\n".join(lines)

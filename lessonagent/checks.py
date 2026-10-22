import re

from .data import language_rules, lesson_spec, reference_facts
from .models import CheckResult
from .textstats import (
    all_sentences,
    flesch_kincaid_grade,
    parse_sections,
    sentence_lengths,
    shorten,
    word_count,
)

DEFINITION_TEMPLATES = [
    r"{t}\s+(?:is|are|means|mean|stands\s+for|refers\s+to)\b",
    r"\b(?:called|known\s+as|name\s+for|short\s+for)\s+(?:a\s+|an\s+|the\s+)?{t}",
    r"\b(?:is|are)\s+(?:also\s+)?(?:a|an)\s+{t}",
    r"{t}\s*\(",
    r"\(\s*{t}",
    r"\bor\s+{t}\b",
]


def check_no_forbidden_claims(lesson):
    facts = reference_facts()
    found = []
    for rule in facts["forbidden_patterns"]:
        match = re.search(rule["pattern"], lesson, re.IGNORECASE)
        if match:
            found.append(f'"{shorten(match.group(0), 90)}" - {rule["reason"]}')
    for year in re.findall(r"\b(?:19|20)\d{2}\b", lesson):
        if year not in facts["allowed_years"]:
            found.append(f'The year {year} is not in the reference facts.')
    allowed_pct = set(facts["allowed_percentages"])
    for pct in re.findall(r"\b\d+(?:\.\d+)?\s?%", lesson):
        if pct.replace(" ", "") not in allowed_pct:
            found.append(f'The number {pct} is not in the reference facts.')
    if found:
        return CheckResult("NO_FORBIDDEN_CLAIMS", False, "Found a false or unsupported claim.", found[:4])
    return CheckResult("NO_FORBIDDEN_CLAIMS", True, "No false claims or invented numbers found.")


def check_reading_grade(lesson):
    limit = language_rules()["max_reading_grade"]
    sentences = all_sentences(lesson)
    grade = flesch_kincaid_grade(sentences)
    if grade <= limit:
        return CheckResult("READING_GRADE", True, f"Reading grade is {grade:.1f}, within the limit of {limit}.")
    hardest = sorted(sentences, key=lambda s: len(s), reverse=True)[:3]
    return CheckResult(
        "READING_GRADE", False,
        f"Reading grade is {grade:.1f}, above the limit of {limit}.",
        [shorten(s) for s in hardest],
    )


def check_short_sentences(lesson):
    rules = language_rules()
    sentences = all_sentences(lesson)
    lengths = sentence_lengths(sentences)
    if not lengths:
        return CheckResult("SHORT_SENTENCES", False, "No sentences were found.")
    average = sum(lengths) / len(lengths)
    too_long = [s for s, n in zip(sentences, lengths) if n > rules["max_sentence_words"]]
    problems = []
    if average > rules["max_average_sentence_words"]:
        problems.append(f"Average sentence length is {average:.1f} words (limit {rules['max_average_sentence_words']}).")
    if too_long:
        problems.append(f"{len(too_long)} sentence(s) are longer than {rules['max_sentence_words']} words.")
    if problems:
        return CheckResult("SHORT_SENTENCES", False, " ".join(problems), [shorten(s) for s in too_long[:3]])
    return CheckResult("SHORT_SENTENCES", True, f"Average sentence length is {average:.1f} words.")


def check_simple_vocabulary(lesson):
    rules = language_rules()
    lowered = lesson.lower()
    hits = []
    for word in rules["banned_words"]:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            hits.append(word)
    for idiom in rules["banned_idioms"]:
        if idiom in lowered:
            hits.append(idiom)
    if hits:
        return CheckResult("SIMPLE_VOCABULARY", False, "Hard words or idioms were used.", sorted(set(hits)))
    return CheckResult("SIMPLE_VOCABULARY", True, "No hard words or idioms found.")


def section_matching(sections, pattern):
    for section in sections:
        if section.title and re.search(pattern, section.title, re.IGNORECASE):
            return section
    return None


def check_worked_example(lesson):
    spec = lesson_spec()
    sections = parse_sections(lesson)
    heading = next(h for h in spec["headings"] if h["id"] == "example")
    section = section_matching(sections, heading["pattern"])
    if section is None:
        return CheckResult("WORKED_EXAMPLE", False, "There is no worked example section.", [])
    body = "\n".join(section.lines)
    problems = []
    if len(body.split()) < spec["example_min_words"]:
        problems.append(f"The example section has fewer than {spec['example_min_words']} words.")
    if '"' not in body and "\u201c" not in body:
        problems.append("The example has no concrete question in quotes.")
    markers = len(re.findall(r"\b(?:for example|example|imagine|let us follow)\b", lesson, re.IGNORECASE))
    if markers < spec["example_min_markers"]:
        problems.append("The lesson has fewer than two example markers.")
    if problems:
        return CheckResult("WORKED_EXAMPLE", False, " ".join(problems), [])
    return CheckResult("WORKED_EXAMPLE", True, "A concrete worked example with a quoted question is present.")


def first_unit_index(units, pattern):
    for index, unit in enumerate(units):
        if re.search(rf"\b{pattern}\b", unit, re.IGNORECASE):
            return index
    return None


def is_defined(units, index, pattern):
    window = " ".join(units[index:index + 2])
    for template in DEFINITION_TEMPLATES:
        if re.search(template.format(t=pattern), window, re.IGNORECASE):
            return True
    return False


def check_jargon_defined(lesson):
    spec = lesson_spec()
    glossary = next(h for h in spec["headings"] if h["id"] == "words")
    units = all_sentences(lesson, skip_title_pattern=glossary["pattern"])
    missing = []
    for entry in language_rules()["jargon_terms"]:
        index = first_unit_index(units, entry["pattern"])
        if index is None:
            continue
        if not is_defined(units, index, entry["pattern"]):
            missing.append(f'{entry["term"]}: first used in "{shorten(units[index], 100)}"')
    if missing:
        return CheckResult("JARGON_DEFINED", False, "Some technical terms are used without a definition.", missing)
    return CheckResult("JARGON_DEFINED", True, "Every technical term is explained where it first appears.")


def check_key_concepts(lesson):
    spec = lesson_spec()
    lowered = lesson.lower()
    missing = [c["label"] for c in spec["required_concepts"] if not any(k in lowered for k in c["any_of"])]
    if missing:
        return CheckResult("KEY_CONCEPTS_COVERED", False, "Some key concepts are missing.", missing)
    return CheckResult("KEY_CONCEPTS_COVERED", True, "All key concepts are covered.")


def heading_positions(lesson):
    spec = lesson_spec()
    sections = [s for s in parse_sections(lesson) if s.level >= 2]
    positions = {}
    for heading in spec["headings"]:
        for index, section in enumerate(sections):
            if re.search(heading["pattern"], section.title, re.IGNORECASE):
                positions[heading["id"]] = index
                break
    return positions


def check_section_order(lesson):
    spec = lesson_spec()
    positions = heading_positions(lesson)
    missing = [h["label"] for h in spec["headings"] if h["id"] not in positions]
    if missing:
        return CheckResult("SECTION_ORDER", False, "Required sections are missing.", missing)
    ordered = [positions[h["id"]] for h in spec["headings"]]
    if ordered != sorted(ordered):
        return CheckResult("SECTION_ORDER", False, "Sections are not in the required order.", [h["label"] for h in spec["headings"]])
    return CheckResult("SECTION_ORDER", True, "All sections are present in the correct order.")


def check_length(lesson):
    spec = lesson_spec()
    count = word_count(lesson)
    if spec["min_words"] <= count <= spec["max_words"]:
        return CheckResult("LENGTH_WITHIN_RANGE", True, f"The lesson has {count} words.")
    return CheckResult(
        "LENGTH_WITHIN_RANGE", False,
        f"The lesson has {count} words, outside the range {spec['min_words']} to {spec['max_words']}.",
    )


RULE_CHECKS = [
    check_no_forbidden_claims,
    check_reading_grade,
    check_short_sentences,
    check_simple_vocabulary,
    check_worked_example,
    check_jargon_defined,
    check_key_concepts,
    check_section_order,
    check_length,
]


def run_rule_checks(lesson):
    return [check(lesson) for check in RULE_CHECKS]

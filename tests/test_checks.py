from lessonagent.checks import (
    check_jargon_defined,
    check_length,
    check_no_forbidden_claims,
    check_reading_grade,
    check_section_order,
    check_simple_vocabulary,
    check_worked_example,
    run_rule_checks,
)
from lessonagent.data import read_text


def final():
    return read_text("mock/final.md")


def test_final_lesson_passes_every_rule_check():
    assert all(r.passed for r in run_rule_checks(final()))


def test_weak_draft_fails_many_rule_checks():
    failed = [r.id for r in run_rule_checks(read_text("mock/draft_1.md")) if not r.passed]
    assert {"READING_GRADE", "SHORT_SENTENCES", "SIMPLE_VOCABULARY", "WORKED_EXAMPLE", "SECTION_ORDER"} <= set(failed)


def test_false_claim_is_caught():
    lesson = final() + "\n\nRAG was invented by OpenAI in 2015 and guarantees 100% correct answers."
    result = check_no_forbidden_claims(lesson)
    assert not result.passed
    assert len(result.evidence) >= 3


def test_year_2020_is_allowed():
    assert check_no_forbidden_claims("Researchers shared this idea in 2020.").passed


def test_unapproved_percentage_is_caught():
    assert not check_no_forbidden_claims("It is 90% accurate.").passed


def test_hard_word_is_caught():
    assert not check_simple_vocabulary("We leverage a comprehensive method.").passed


def test_idiom_is_caught():
    assert not check_simple_vocabulary("This is a silver bullet.").passed


def test_undefined_jargon_is_caught():
    lesson = final().replace(
        "These chatbots run on a large language model, or LLM. An LLM is a computer program that learned to read and write by studying a huge amount of text.",
        "These chatbots run on an LLM. It is good.",
    )
    assert not check_jargon_defined(lesson).passed


def test_missing_example_section_is_caught():
    lesson = final().replace("## A Worked Example", "## Something Else")
    assert not check_worked_example(lesson).passed


def test_wrong_section_order_is_caught():
    lesson = final().replace("## Quick Recap", "## TEMP").replace("## Key Words", "## Quick Recap").replace("## TEMP", "## Key Words")
    assert not check_section_order(lesson).passed


def test_length_limits():
    assert not check_length("Short text.").passed
    assert check_length(final()).passed


def test_reading_grade_fails_on_dense_text():
    dense = "Retrieval-augmented generation fundamentally enhances comprehensive architectural capabilities. " * 8
    assert not check_reading_grade(dense).passed

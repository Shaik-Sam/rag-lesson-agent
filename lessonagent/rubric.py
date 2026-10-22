from .models import Checkpoint

CHECKPOINTS = [
    Checkpoint(
        "FACT_SUPPORTED", "Every fact is supported by the reference facts", "Accurate and grounded", "llm",
        "Every factual statement in the lesson is supported by the reference facts. Nothing is invented, exaggerated or contradicted.",
        "Remove or correct any statement that is not in the reference facts. Do not add dates, names or numbers that are not given.",
    ),
    Checkpoint(
        "NO_FORBIDDEN_CLAIMS", "No false claims, guarantees or invented numbers", "Accurate and grounded", "rule",
        "The lesson contains none of the known false claims, no guarantees of correctness, and no year or percentage outside the approved list.",
        "Delete the false or unsupported claim. RAG reduces mistakes but never guarantees correct answers. Only the year 2020 may be mentioned.",
    ),
    Checkpoint(
        "READING_GRADE", "Reading grade level is 7.0 or lower", "Beginner-friendly language", "rule",
        "The Flesch-Kincaid reading grade of the lesson is 7.0 or lower.",
        "Use shorter sentences and shorter everyday words. Replace long words with simple ones.",
    ),
    Checkpoint(
        "SHORT_SENTENCES", "Sentences are short", "Beginner-friendly language", "rule",
        "The average sentence has 15 words or fewer and no sentence has more than 28 words.",
        "Split long sentences. Keep one idea in each sentence.",
    ),
    Checkpoint(
        "SIMPLE_VOCABULARY", "No hard words or idioms", "Beginner-friendly language", "rule",
        "The lesson uses none of the hard words or English idioms on the banned list.",
        "Replace each flagged word or idiom with a simple, literal everyday word.",
    ),
    Checkpoint(
        "WORKED_EXAMPLE", "Contains a concrete worked example", "Teaches by example", "rule",
        "There is an example section with a concrete question and answer, and at least two example markers in the lesson.",
        "Add a section named A Worked Example that follows one real question through every step, with the question in quotes.",
    ),
    Checkpoint(
        "EXAMPLE_RELATABLE", "Example is relatable to an Indian learner", "Teaches by example", "llm",
        "The worked example uses a situation a 12th-grade learner in India knows from daily life, such as college, exams, scholarships, shops or WhatsApp.",
        "Rewrite the worked example around a familiar Indian student or shop situation.",
    ),
    Checkpoint(
        "JARGON_DEFINED", "Every technical term is explained when first used", "Clear, no unexplained jargon", "rule",
        "Each technical term is defined in the same sentence or the next sentence where it first appears.",
        "Add a simple definition right where each flagged term first appears.",
    ),
    Checkpoint(
        "KEY_CONCEPTS_COVERED", "All key concepts are covered", "Covers the key points", "rule",
        "The lesson covers what RAG is, why it is needed, chunks, embeddings, vector database, retrieval, augmentation, generation and limits.",
        "Add a short, simple explanation for each missing concept.",
    ),
    Checkpoint(
        "SECTION_ORDER", "Sections follow the teaching order", "Coherent teaching flow", "rule",
        "The lesson has the sections What Is RAG, Why, How, Worked Example, Where It Can Go Wrong, Quick Recap and Key Words, in this order.",
        "Add the missing sections and put them in the required order.",
    ),
    Checkpoint(
        "FLOW_COHERENT", "Ideas build step by step", "Coherent teaching flow", "llm",
        "Each idea is introduced before it is used, steps follow in a logical order, and there are no jumps.",
        "Reorder or add transitions so each idea is explained before it is used.",
    ),
    Checkpoint(
        "STANDALONE", "Understandable with zero background", "Clear, no unexplained jargon", "llm",
        "A learner with no background can finish the lesson and understand it without any other material.",
        "Remove references to outside material and explain every step from zero.",
    ),
    Checkpoint(
        "LENGTH_WITHIN_RANGE", "Length is suitable for a beginner lesson", "Covers the key points", "rule",
        "The lesson has between 550 and 1100 words.",
        "Adjust the length to stay between 550 and 1100 words.",
    ),
]


def by_id():
    return {c.id: c for c in CHECKPOINTS}


def ids():
    return [c.id for c in CHECKPOINTS]


def llm_checkpoints():
    return [c for c in CHECKPOINTS if c.kind == "llm"]


def rule_checkpoints():
    return [c for c in CHECKPOINTS if c.kind == "rule"]

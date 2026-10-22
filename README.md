# Self-Evaluating Lesson Content Generator

An agentic system that writes a beginner lesson, judges its own work against a hard pass/fail rubric, and regenerates until the lesson is good enough to ship. Built with Python, LangGraph and the Anthropic API.

Topic for this submission: **Introduction to RAG (Retrieval-Augmented Generation)**
Target learner: a 12th-grade graduate from India, limited English vocabulary, starting from zero.

## What it does

```
INPUT topic
   |
   v
load memory --> plan outline --> generate lesson --> evaluate (13 pass/fail checks)
                                      ^                       |
                                      |                 all pass? --yes--> ship --> save outputs + memory
                                      |                       |no
                                      |                retries left? --no--> escalate to human (not shipped)
                                      |                       |yes
                                      +------ revise (failure reasons fed back)
```

Output of every run:

- the passing lesson (`lesson.md`)
- a rejection log (`rejection_log.md` and `rejection_log.json`): what failed, why, and what changed on the retry
- every attempt and its full evaluation
- an updated memory file that makes the next run better

## Setup

Requirements: Python 3.10 or newer.

```bash
cd rag-lesson-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your Anthropic API key after `ANTHROPIC_API_KEY=`.

On Windows, activate the environment with `.venv\Scripts\activate` and copy the file with `copy .env.example .env`.

## Run

Real run with the model:

```bash
python main.py run
```

Real run with a deliberate error injected into the first draft, to prove the evaluator catches it:

```bash
python main.py run --inject-error
```

Offline demo with no API key (a scripted stand-in model, used for tests and screen recordings):

```bash
python main.py run --llm mock --scenario struggle
python main.py run --llm mock --scenario clean --inject-error
```

Options:

| Option | Meaning |
| --- | --- |
| `--topic "..."` | Topic to teach. Default is Introduction to RAG |
| `--llm anthropic or mock` | Model backend. Default is anthropic |
| `--scenario struggle or clean` | Mock only. struggle needs 3 attempts, clean passes at once |
| `--max-retries 0, 1 or 2` | Retries after the first draft. Hard-capped at 2 |
| `--inject-error` | Adds a false sentence to attempt 1 |
| `--output-dir PATH` | Where run folders are written. Default is `outputs/` |
| `--memory-path PATH` | Where memory is stored. Default is `memory/store.json` |

Exit code is 0 when the lesson shipped and 1 when it needs human review.

## Memory and self-improvement

```bash
python main.py memory
python main.py feedback "Use more examples from WhatsApp" --check EXAMPLE_RELATABLE
python main.py reset-memory
python main.py rubric
```

- Every run records which checks failed on the first attempt and why.
- When the same check fails on the first attempt in 2 or more runs, a guideline for that check is promoted into the generator prompt for all future runs.
- The latest failure reasons are shown to the judge as a watch-list of known problems.
- Human feedback saved with `feedback` is added to the generator prompt as well.

## Rubric (13 hard pass/fail checkpoints)

| Dimension | Checkpoint | Type |
| --- | --- | --- |
| Accurate and grounded | FACT_SUPPORTED | LLM judge |
| Accurate and grounded | NO_FORBIDDEN_CLAIMS | Rule |
| Beginner-friendly language | READING_GRADE | Rule |
| Beginner-friendly language | SHORT_SENTENCES | Rule |
| Beginner-friendly language | SIMPLE_VOCABULARY | Rule |
| Teaches by example | WORKED_EXAMPLE | Rule |
| Teaches by example | EXAMPLE_RELATABLE | LLM judge |
| Clear, no unexplained jargon | JARGON_DEFINED | Rule |
| Clear, no unexplained jargon | STANDALONE | LLM judge |
| Covers the key points | KEY_CONCEPTS_COVERED | Rule |
| Covers the key points | LENGTH_WITHIN_RANGE | Rule |
| Coherent teaching flow | SECTION_ORDER | Rule |
| Coherent teaching flow | FLOW_COHERENT | LLM judge |

A lesson ships only when all 13 pass. There is no partial credit.

## Project structure

```
rag-lesson-agent/
  main.py                      command line entry point
  requirements.txt
  .env.example
  lessonagent/
    graph.py                   LangGraph pipeline: plan, generate, evaluate, revise, ship, escalate, persist
    rubric.py                  the 13 checkpoints
    checks.py                  deterministic rule checks
    judge.py                   LLM judge with fail-closed parsing
    prompts.py                 planner, generator and judge prompts, guideline library
    memory.py                  persistent memory and guideline promotion
    llm.py                     Anthropic client
    mock_llm.py                scripted offline model for tests and demos
    textstats.py               sentence, syllable and reading-grade helpers
    reporting.py               output files and rejection log
    config.py, data.py, models.py, cli.py
  data/
    reference_facts.json       ground-truth facts and forbidden claims
    lesson_spec.json           required sections, concepts and length
    language_rules.json        reading limits, banned words, jargon terms
    mock/                      scripted drafts for the offline model
  tests/                       25 automated tests
  docs/
    ARCHITECTURE.md            design choices and trade-offs
    VIDEO_GUIDE.md             how to run the demo and the video script
  deliverables/                final lesson as .md and .docx
  sample_output/               three recorded runs and the memory they produced
  memory/                      runtime memory is stored here
```

## Tests

```bash
python -m pytest -q
```

## Notes on the offline mock

`--llm mock` replays three stored drafts (a weak first draft, a better second draft, the final lesson) and judges the four judgement-based checks with simple keyword heuristics. It exists so the full loop, the rejection log and the memory can be tested and demonstrated without an API key. The 9 rule-based checks, the retry loop, the escalation path and the memory are the same code in both modes.

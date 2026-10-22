# Video Guide: How to Run, What to Show, What to Say

Required by the assignment (15 to 20 minutes, Loom, face visible):

1. Your agentic workflow running end to end
2. Your evaluator catching a deliberate error
3. A face-visible walkthrough of how the workflow works

## Part A. Before you record

1. Get an Anthropic API key from console.anthropic.com and put it in `.env`.
2. Install and test:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

3. Clear old memory so the demo starts clean:

```bash
python main.py reset-memory
```

4. Do one private test run so you know what the output looks like:

```bash
python main.py run --inject-error
```

5. If the real model passes on the first attempt, that is fine. For the video, the deliberate error run still shows a rejection and a retry.
6. If you have no API key or the API is down, use `--llm mock`. Say clearly in the video that it is the offline test model.
7. Open these in separate tabs or windows before recording: the terminal, the repo in VS Code, `docs/ARCHITECTURE.md`, and the final lesson Google Doc.
8. Turn off notifications. Use a large terminal font (at least 16 pt). Record with your camera on and visible in the Loom bubble.

## Part B. Recording order and exact commands

| Time | What is on screen | Commands or actions |
| --- | --- | --- |
| 0:00 to 1:30 | Your face, then the README | Introduce yourself and the goal |
| 1:30 to 5:00 | Architecture diagram, then code | Open `docs/ARCHITECTURE.md`, then `lessonagent/graph.py` |
| 5:00 to 7:30 | Rubric and checks | `python main.py rubric`, then open `checks.py` and `judge.py` |
| 7:30 to 12:00 | Terminal: full run | `python main.py run` |
| 12:00 to 15:00 | Terminal: deliberate error | `python main.py run --inject-error` then open `rejection_log.md` |
| 15:00 to 17:00 | Terminal: memory | `python main.py run`, then `python main.py memory` |
| 17:00 to 19:00 | Final lesson and wrap-up | Open the Google Doc, then summarise trade-offs |

If the real run is faster than expected, spend the spare time showing `rejection_log.json` and `evaluation_attempt_1.json`.

To show memory learning quickly, run the real flow twice with `--inject-error`, or use the offline demo:

```bash
python main.py run --llm mock --scenario struggle
python main.py run --llm mock --scenario struggle
python main.py memory
```

The second run promotes guidelines because the same checks failed in two runs.

## Part C. Script (read in your own words)

Speak slowly. The script is about 1,800 words (roughly 12 minutes of talking). The runs, pauses and file tours fill the rest, so the video lands at 17 to 19 minutes.

### 0:00 to 1:30 Introduction (face visible)

"Hi, my name is [YOUR NAME]. I am applying for the GenAI Engineer, Content Systems role at NxtWave. In this video I will show the system I built for the take-home assessment. It is a self-evaluating lesson generator.

The task was not to write one good prompt. The task was to build a loop. The system writes a beginner lesson, judges its own lesson against a rubric, and if the lesson fails, it fixes it and tries again. It does this before a human ever sees the content.

The topic is Introduction to RAG. The learner is a 12th-grade graduate from India, with limited English, who is starting from zero. That learner shaped almost every decision I made, and I will point that out as we go.

I will do three things in this video. First, I will explain how the workflow is designed. Second, I will run it end to end. Third, I will inject a deliberate error and show that the evaluator catches it."

### 1:30 to 5:00 Architecture walkthrough (show ARCHITECTURE.md, then graph.py)

"Let me start with the flow. This diagram is in my architecture document.

There are eight steps. The first is load memory. The system reads what it learned from earlier runs. I will come back to this.

The second is plan. Before writing, the system creates an outline. It decides the section order, an analogy, and an example idea. I did this because lessons written from a plan are more consistent, and when something fails, I can see whether the plan or the writing was the problem.

The third is generate. The model writes the lesson using the plan, the reference facts, and the style rules for this learner. Short sentences. Everyday words. Every technical term explained the first time it appears.

The fourth is evaluate. This is the heart of the project. There are 13 checkpoints. Each one is a hard pass or fail. There is no partial credit. The lesson ships only if all 13 pass.

If anything fails, we go to revise. Revise takes every failure and turns it into an instruction: what the rule is, why it failed, the exact evidence, and how to fix it. The old draft and those instructions go back to the generator.

I limit retries to two. The code clamps it, so even if someone passes a bigger number, the loop always ends. There are only two exits. Ship, or escalate to a human with the best draft clearly marked as not shipped.

Finally, persist. The system saves the lesson, every attempt, every evaluation, the rejection log, and it updates memory.

I used LangGraph because this is a state machine with a conditional loop. In this file, graph.py, you can see the nodes, and here is the conditional edge after evaluate with three exits: ship, retry, and escalate. [Scroll to the build function and the route function.]"

### 5:00 to 7:30 The rubric and evaluator design (run rubric, open checks.py and judge.py)

"Now the evaluator. Let me print the rubric. [Run: python main.py rubric]

These 13 checkpoints cover the six dimensions in the assignment. Accurate and grounded. Beginner-friendly language. Teaches by example. Clear, no unexplained jargon. Covers the key points. And coherent teaching flow.

The most important design decision is this. I split the evaluator into two layers.

Nine checks are rules in code. For example, reading grade level must be 7 or lower. Average sentence length must be 15 words or fewer. There is a banned list of hard words and idioms, like leverage or silver bullet, that a non-English-medium learner may not know. Every technical term must be defined in the same sentence or the next sentence where it first appears. The sections must be present and in the right order. [Show checks.py.]

These rule checks are fast, free, and consistent. A model cannot argue its way past a rule.

Four checks need judgement, so I use the LLM judge: is every fact supported, is the example relatable to an Indian learner, does the lesson build step by step, and can a person with zero background follow it.

Two more safety decisions. First, the judge is told to fail when unsure, and it runs at temperature 0. Second, look at judge.py. If the judge returns something that is not valid JSON, or forgets a checkpoint, I mark it as failed. I call this failing closed. A broken judge can never let a bad lesson through.

For grounding, I wrote a small reference-facts file. Both the generator and the judge see it. The rule layer also blocks any year or percentage that is not approved, and it blocks known false claims, such as saying RAG guarantees correct answers."

### 7:30 to 12:00 Live end-to-end run (run: python main.py run)

"Now I will run the full workflow with the real model. [Run: python main.py run]

At the top you can see the topic, the model, and the retry limit.

First, memory is loaded. Then the planner builds the outline. Now the generator is writing attempt one.

Here comes the evaluation. Each line is one checkpoint, with PASS or FAIL and a reason. [Read two or three lines aloud.]

[If something fails:] You can see attempt one was rejected. [Name a failed checkpoint] failed because [read the reason]. The system now sends this reason back, and the generator writes attempt two. Let me wait for the second evaluation.

[If everything passes the first time:] The first attempt passed all 13 checkpoints, so the lesson shipped without a retry. That is a valid outcome. The loop only retries when it needs to. In the next section I will force a failure so you can see the retry path.

When the run finishes, the system tells me the output folder. Let me open it. [Open the folder.]

There is lesson.md, the passing lesson. There is attempt_1.md and, if there were retries, the later attempts. There is an evaluation file for every attempt, so every decision can be audited. And there is rejection_log.md. I will open that in the next section."

### 12:00 to 15:00 Deliberate error (run: python main.py run --inject-error, then open rejection_log.md)

"Now the test that matters most. Can the evaluator catch a mistake? I added a flag called inject-error. After the model writes attempt one, the system inserts a false sentence under the Why section: 'RAG was invented by OpenAI in 2015, and it guarantees 100% correct answers every time.'

This sentence is wrong in several ways. RAG came from Facebook AI Research, now Meta, in 2020. And no AI system can guarantee correct answers. [Run: python main.py run --inject-error]

Watch the log. It says: deliberate error injected into attempt one. Now evaluation. Look at these two failures. FACT_SUPPORTED, the judge says a claim is not supported by the reference facts. And NO_FORBIDDEN_CLAIMS, the rule layer found the word guarantees, found 'invented by OpenAI', and found the year 2015 and the number 100 percent, which are not approved.

Two independent layers caught the same error. One uses reasoning, one uses rules. That is why I built it this way.

The system now sends these reasons back. In attempt two, the false sentence is gone and all checks pass. Let me prove it. [Open rejection_log.md.]

This is the rejection log required by the assignment. It shows the attempt that was rejected, which checkpoints failed, why, and the evidence. Below that are the exact instructions sent to the generator. And at the bottom, what changed on the retry: which checkpoints were fixed, which still fail, which are new, the word count before and after, and how similar the new draft is to the old one.

This log is also useful for people. A reviewer can see in seconds why a draft was rejected."

### 15:00 to 17:00 Memory and self-evolving (run again, then python main.py memory)

"The assignment also asks for memory and for the system to learn from repeated failures. Let me show that.

Memory is a JSON file in the memory folder. After every run, the system records which checkpoints failed on the first attempt, and the reason. [Run: python main.py memory]

Here you can see the failure counts. The rule is simple. If the same checkpoint fails on the first attempt in two different runs, the system promotes a guideline for it into the generator prompt for all future runs. For example, if the first draft keeps using long sentences, a new rule appears in the prompt: keep every sentence under 20 words.

[If a guideline is visible:] Here is one that was promoted. You can see how many runs it failed in, and the last reason.

Two more learning paths. The judge gets a watch-list of the latest failure reasons, so it looks for the same problems. And a human can teach the system directly. [Run: python main.py feedback 'Use more examples from WhatsApp' --check EXAMPLE_RELATABLE] That feedback is saved and sent to the generator in every run.

So the prompts improve from evidence, not from my guesses."

### 17:00 to 19:00 Final lesson, trade-offs, close (show the Google Doc)

"Here is the final lesson, as a document. It starts from zero. It explains what an LLM is before it explains RAG. It uses the open-book exam analogy. It walks through preparing documents and answering a question step by step. It follows one real example, a student in Hyderabad asking about an exam fee date, with and without RAG. It is honest about where RAG can go wrong, and it ends with a recap and a key words list.

Now, honest trade-offs. The reading-level score is a formula. It is a good proxy, but it does not fully measure how an Indian learner reads English. The jargon check looks for a definition nearby, but it cannot judge if the definition is good, so I added the LLM-judged standalone check as a second layer. The LLM judge can still be wrong, so a human should always review the shipped lesson. And the memory is count-based and simple.

If I had more time, I would test the lesson with real learners and feed their quiz results into memory, add a quiz generator with its own rubric, and add a way to retire guidelines that stop helping.

To summarise: the system plans, writes, judges against 13 hard checkpoints, retries at most twice, ships or escalates, logs every rejection, and learns from repeated failures. The code, the README, and this lesson are all in the submission. Thank you for watching. I look forward to discussing it with you."

## Part D. After recording: what to submit

1. **GitHub repo link.** Create a new public repo and push this folder.

```bash
cd rag-lesson-agent
git init
git add .
git commit -m "Self-evaluating lesson content generator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/rag-lesson-agent.git
git push -u origin main
```

2. **Document link.** Upload `deliverables/final_lesson.docx` to Google Drive, right-click, Open with Google Docs, then Share and set "Anyone with the link can view". If you ran the real model, use the lesson from your own run folder instead and say so in the video.
3. **Loom link.** Make sure the video is 15 to 20 minutes and your face is visible.
4. Open the submission form and paste all three links: https://forms.gle/a7MJUNoTxvSdRB8R6
5. Deadline: 10:00 AM, 22 October 2026. Submit early.

## Part E. Questions you may be asked

- Why not one big prompt? Because a single prompt cannot tell you whether its own output is good. The loop gives a decision to ship.
- Why hard pass/fail? It is auditable and removes vague scores.
- Why rules and an LLM judge? Rules for what can be measured, the model only for judgement.
- What if the judge is wrong? It fails closed on bad output, a rule layer backs it up, and a human reviews shipped lessons.
- How does it learn? Repeated first-attempt failures become permanent prompt guidelines. The judge gets a watch-list. Humans can add feedback.
- How do you know the loop ends? Retries are capped at 2 in code, and the graph has a recursion limit.

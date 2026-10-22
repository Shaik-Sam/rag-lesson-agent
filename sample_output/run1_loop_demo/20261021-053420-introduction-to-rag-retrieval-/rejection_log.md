# Rejection Log

Topic: Introduction to RAG (Retrieval-Augmented Generation)
Final status: SHIPPED
Attempts used: 3

## Attempt 1 - rejected

| Checkpoint | Dimension | Why it failed |
| --- | --- | --- |
| READING_GRADE | Beginner-friendly language | Reading grade is 21.9, above the limit of 7.0. |
| SHORT_SENTENCES | Beginner-friendly language | Average sentence length is 38.3 words (limit 15). 5 sentence(s) are longer than 28 words. |
| SIMPLE_VOCABULARY | Beginner-friendly language | Hard words or idioms were used. |
| WORKED_EXAMPLE | Teaches by example | There is no worked example section. |
| EXAMPLE_RELATABLE | Teaches by example | The example is generic and does not use a situation familiar to an Indian learner. |
| JARGON_DEFINED | Clear, no unexplained jargon | Some technical terms are used without a definition. |
| SECTION_ORDER | Coherent teaching flow | Required sections are missing. |
| FLOW_COHERENT | Coherent teaching flow | The lesson jumps ahead and skips the step-by-step build-up. |
| STANDALONE | Clear, no unexplained jargon | The lesson is too short to teach a learner from zero. |
| LENGTH_WITHIN_RANGE | Covers the key points | The lesson has 268 words, outside the range 550 to 1100. |

Evidence:
- READING_GRADE: Retrieval-Augmented Generation (RAG) is a comprehensive architectural paradigm that fundamentally enhances the capabilities of large lang...
- READING_GRADE: Large language models frequently exhibit hallucination, which is a phenomenon where the model generates plausible-sounding but factually ...
- SHORT_SENTENCES: Retrieval-Augmented Generation (RAG) is a comprehensive architectural paradigm that fundamentally enhances the capabilities of large lang...
- SHORT_SENTENCES: In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM can utilize relevant chunks within the pro...
- SIMPLE_VOCABULARY: comprehensive
- SIMPLE_VOCABULARY: fundamentally
- EXAMPLE_RELATABLE: 
- JARGON_DEFINED: LLM: first used in "In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM ca..."
- JARGON_DEFINED: embedding: first used in "In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM ca..."
- SECTION_ORDER: A Worked Example
- SECTION_ORDER: Quick Recap

Instructions sent back to the generator:

```
1. READING_GRADE - The Flesch-Kincaid reading grade of the lesson is 7.0 or lower.
   Why it failed: Reading grade is 21.9, above the limit of 7.0.
   Evidence: Retrieval-Augmented Generation (RAG) is a comprehensive architectural paradigm that fundamentally enhances the capabilities of large lang...
   Evidence: Large language models frequently exhibit hallucination, which is a phenomenon where the model generates plausible-sounding but factually ...
   Evidence: Subsequently, when a user submits a query, the query is embedded using the same model, the vector database returns the top-k most similar...
   How to fix: Use shorter sentences and shorter everyday words. Replace long words with simple ones.
2. SHORT_SENTENCES - The average sentence has 15 words or fewer and no sentence has more than 28 words.
   Why it failed: Average sentence length is 38.3 words (limit 15). 5 sentence(s) are longer than 28 words.
   Evidence: Retrieval-Augmented Generation (RAG) is a comprehensive architectural paradigm that fundamentally enhances the capabilities of large lang...
   Evidence: In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM can utilize relevant chunks within the pro...
   Evidence: Large language models frequently exhibit hallucination, which is a phenomenon where the model generates plausible-sounding but factually ...
   How to fix: Split long sentences. Keep one idea in each sentence.
3. SIMPLE_VOCABULARY - The lesson uses none of the hard words or English idioms on the banned list.
   Why it failed: Hard words or idioms were used.
   Evidence: comprehensive
   Evidence: fundamentally
   Evidence: furthermore
   How to fix: Replace each flagged word or idiom with a simple, literal everyday word.
4. WORKED_EXAMPLE - There is an example section with a concrete question and answer, and at least two example markers in the lesson.
   Why it failed: There is no worked example section.
   How to fix: Add a section named A Worked Example that follows one real question through every step, with the question in quotes.
5. EXAMPLE_RELATABLE - The worked example uses a situation a 12th-grade learner in India knows from daily life, such as college, exams, scholarships, shops or WhatsApp.
   Why it failed: The example is generic and does not use a situation familiar to an Indian learner.
   Evidence: 
   How to fix: Rewrite the worked example around a familiar Indian student or shop situation.
6. JARGON_DEFINED - Each technical term is defined in the same sentence or the next sentence where it first appears.
   Why it failed: Some technical terms are used without a definition.
   Evidence: LLM: first used in "In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM ca..."
   Evidence: embedding: first used in "In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM ca..."
   Evidence: vector: first used in "In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM ca..."
   How to fix: Add a simple definition right where each flagged term first appears.
7. SECTION_ORDER - The lesson has the sections What Is RAG, Why, How, Worked Example, Where It Can Go Wrong, Quick Recap and Key Words, in this order.
   Why it failed: Required sections are missing.
   Evidence: A Worked Example
   Evidence: Quick Recap
   Evidence: Key Words
   How to fix: Add the missing sections and put them in the required order.
8. FLOW_COHERENT - Each idea is introduced before it is used, steps follow in a logical order, and there are no jumps.
   Why it failed: The lesson jumps ahead and skips the step-by-step build-up.
   How to fix: Reorder or add transitions so each idea is explained before it is used.
9. STANDALONE - A learner with no background can finish the lesson and understand it without any other material.
   Why it failed: The lesson is too short to teach a learner from zero.
   How to fix: Remove references to outside material and explain every step from zero.
10. LENGTH_WITHIN_RANGE - The lesson has between 550 and 1100 words.
   Why it failed: The lesson has 268 words, outside the range 550 to 1100.
   How to fix: Adjust the length to stay between 550 and 1100 words.
```

What changed on the retry:

- Fixed: FLOW_COHERENT, LENGTH_WITHIN_RANGE, READING_GRADE, SECTION_ORDER, SHORT_SENTENCES, SIMPLE_VOCABULARY, STANDALONE, WORKED_EXAMPLE
- Still failing: EXAMPLE_RELATABLE, JARGON_DEFINED
- Newly failing: none
- Word count: 268 to 907
- Text similarity to the rejected draft: 0.03

## Attempt 2 - rejected

| Checkpoint | Dimension | Why it failed |
| --- | --- | --- |
| EXAMPLE_RELATABLE | Teaches by example | The example is generic and does not use a situation familiar to an Indian learner. |
| JARGON_DEFINED | Clear, no unexplained jargon | Some technical terms are used without a definition. |

Evidence:
- EXAMPLE_RELATABLE: let us follow rag inside a small app. a company made a help chatbot for its customers. the company put its rule book,...
- JARGON_DEFINED: fine-tuning: first used in "You could use fine-tuning instead."

Instructions sent back to the generator:

```
1. EXAMPLE_RELATABLE - The worked example uses a situation a 12th-grade learner in India knows from daily life, such as college, exams, scholarships, shops or WhatsApp.
   Why it failed: The example is generic and does not use a situation familiar to an Indian learner.
   Evidence: let us follow rag inside a small app. a company made a help chatbot for its customers. the company put its rule book,...
   How to fix: Rewrite the worked example around a familiar Indian student or shop situation.
2. JARGON_DEFINED - Each technical term is defined in the same sentence or the next sentence where it first appears.
   Why it failed: Some technical terms are used without a definition.
   Evidence: fine-tuning: first used in "You could use fine-tuning instead."
   How to fix: Add a simple definition right where each flagged term first appears.
```

What changed on the retry:

- Fixed: EXAMPLE_RELATABLE, JARGON_DEFINED
- Still failing: none
- Newly failing: none
- Word count: 907 to 935
- Text similarity to the rejected draft: 0.95


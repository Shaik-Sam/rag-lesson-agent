# Rejection Log

Topic: Introduction to RAG (Retrieval-Augmented Generation)
Final status: SHIPPED
Attempts used: 2

Deliberate error injected into attempt 1:

> RAG was invented by OpenAI in 2015, and it guarantees 100% correct answers every time.

## Attempt 1 - rejected

| Checkpoint | Dimension | Why it failed |
| --- | --- | --- |
| FACT_SUPPORTED | Accurate and grounded | The lesson makes a claim that the reference facts do not support. |
| NO_FORBIDDEN_CLAIMS | Accurate and grounded | Found a false or unsupported claim. |

Evidence:
- FACT_SUPPORTED: invented by OpenAI
- FACT_SUPPORTED: guarantees
- NO_FORBIDDEN_CLAIMS: "guarantees" - RAG cannot guarantee correct answers; it only reduces mistakes.
- NO_FORBIDDEN_CLAIMS: "invented by OpenAI" - The RAG idea came from Facebook AI Research (Meta) in 2020, not from another company.

Instructions sent back to the generator:

```
1. FACT_SUPPORTED - Every factual statement in the lesson is supported by the reference facts. Nothing is invented, exaggerated or contradicted.
   Why it failed: The lesson makes a claim that the reference facts do not support.
   Evidence: invented by OpenAI
   Evidence: guarantees
   Evidence: 100%
   How to fix: Remove or correct any statement that is not in the reference facts. Do not add dates, names or numbers that are not given.
2. NO_FORBIDDEN_CLAIMS - The lesson contains none of the known false claims, no guarantees of correctness, and no year or percentage outside the approved list.
   Why it failed: Found a false or unsupported claim.
   Evidence: "guarantees" - RAG cannot guarantee correct answers; it only reduces mistakes.
   Evidence: "invented by OpenAI" - The RAG idea came from Facebook AI Research (Meta) in 2020, not from another company.
   Evidence: The year 2015 is not in the reference facts.
   How to fix: Delete the false or unsupported claim. RAG reduces mistakes but never guarantees correct answers. Only the year 2020 may be mentioned.
```

What changed on the retry:

- Fixed: FACT_SUPPORTED, NO_FORBIDDEN_CLAIMS
- Still failing: none
- Newly failing: none
- Word count: 950 to 935
- Text similarity to the rejected draft: 0.99


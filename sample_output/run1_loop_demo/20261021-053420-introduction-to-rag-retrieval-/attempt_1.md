# Introduction to RAG

## What Is RAG?

Retrieval-Augmented Generation (RAG) is a comprehensive architectural paradigm that fundamentally enhances the capabilities of large language models by seamlessly integrating an external information retrieval mechanism, thereby enabling the system to ground its responses in authoritative, up-to-date knowledge sources rather than relying exclusively upon the parametric knowledge that was encoded during the pre-training phase.

In a nutshell, RAG leverages the embedding of documents into a vector database so that the LLM can utilize relevant chunks within the prompt whenever a user poses a query that requires specialized information.

## Why Do We Need RAG?

Large language models frequently exhibit hallucination, which is a phenomenon where the model generates plausible-sounding but factually incorrect content, and this problem is particularly pronounced when the queries pertain to proprietary or recently published information that was absent from the training corpus. Furthermore, fine-tuning is expensive, so RAG is regarded as a silver bullet for organizations that need to maintain accuracy.

## How RAG Works

The pipeline begins with an ingestion phase in which documents are split into chunks, each chunk is converted into an embedding using an embedding model, and the resulting vectors are persisted in a vector database that supports approximate nearest-neighbour search across high-dimensional spaces.

Subsequently, when a user submits a query, the query is embedded using the same model, the vector database returns the top-k most similar chunks, and these chunks are concatenated with the original query to construct an augmented prompt that is passed to the LLM, which then generates a grounded response.

## Where RAG Can Go Wrong

Retrieval quality is a bottleneck, and if the chunks that are returned are irrelevant, then the generated answer will be wrong, so practitioners should evaluate retrieval carefully.
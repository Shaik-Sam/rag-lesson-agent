# Introduction to RAG: Teach an AI to Look Things Up

## What Is RAG?

You may have used an AI chatbot like ChatGPT. These chatbots run on a large language model, or LLM. An LLM is a computer program that learned to read and write by studying a huge amount of text.

An LLM has one big problem. It only knows what it saw while it was learning. It does not know new things that happened later. It also does not know your private information, like your college notes or your company files.

RAG fixes this problem. RAG stands for Retrieval-Augmented Generation. Researchers shared this idea in 2020. The name sounds hard, but the idea is simple:

- Retrieval means finding the right information.
- Augmented means made stronger by adding something extra.
- Generation means writing the answer.

So RAG means: first find useful information, then give it to the AI, then let the AI write the answer. Think of an open-book exam. A student can look into the book while writing an answer. RAG lets the AI do the same.

## Why Do We Need RAG?

LLMs are smart, but they have three weak points.

- Old knowledge. An LLM stops learning on a fixed date. It may not know last month's news or the new exam rules.
- No private knowledge. It has never seen your own files.
- Made-up answers. When an LLM does not know something, it may still give an answer that sounds correct but is wrong. This is called a hallucination.

You could teach the LLM again with new data. This is called fine-tuning. It is slow and costs a lot of money.

RAG is cheaper and faster. When your information changes, you only change the documents. You do not need to teach the LLM again. RAG can also show you which document an answer came from. So you can check the answer yourself.

## How RAG Works, Step by Step

RAG has two parts. First, we prepare our documents one time. After that, we answer questions again and again.

**Part 1: Prepare the documents (done once)**

1. Collect your documents. These can be PDFs, web pages, or notes.
2. Split each document into small pieces. Each small piece is called a chunk. A chunk may be a few short paragraphs.
3. Turn each chunk into numbers. A computer cannot read meaning from words directly. So we use a special tool that changes the meaning of a text into a list of numbers. This list of numbers is called an embedding. Another name for this list of numbers is a vector. Chunks with similar meaning get similar numbers.
4. Save all the embeddings in a vector database. A vector database is a special storage place. It can quickly find numbers that are close to each other.

**Part 2: Answer a question (every time)**

5. The user asks a question. For example: "What is the last date to apply for the scholarship?"
6. Turn the question into an embedding too. Use the same tool as before.
7. Search the vector database. Find the chunks whose numbers are closest to the question. These chunks have the most similar meaning. This step is called retrieval.
8. Build a prompt. A prompt is the message we send to the LLM. We put the question and the best chunks together in the prompt. We also tell the LLM to use only this information. This step is called augmentation, because we add extra information to the prompt.
9. The LLM reads the prompt and writes the answer. This step is called generation. The LLM can also name the document that the answer came from.

## A Worked Example

Let us follow RAG inside a small app. Ravi is a student in Hyderabad. His college made a help chatbot. The college put its rule book, fee list, and exam notices into the RAG system.

Ravi asks: "When is the last date to pay the exam fee?"

- Without RAG: The LLM has never seen the college notices. It may guess a date. The date may be wrong, and Ravi may miss the deadline.
- With RAG: The system turns Ravi's question into an embedding. It searches the vector database. It finds this chunk from the exam notice: "The last date to pay the exam fee is 15 November." The system puts this chunk into the prompt. The LLM reads it and answers: "The last date is 15 November. Source: Exam Notice."

Here is one more example. A shop owner in Pune loads her product list into RAG. Now a WhatsApp helper can answer customer questions with the latest prices. When prices change, she only updates the list.

## Where RAG Can Go Wrong

RAG is useful, but it is not perfect.

- If the search finds the wrong chunks, the answer will be wrong.
- If the documents are old or have mistakes, the answer will also have mistakes.
- RAG lowers made-up answers, but it does not remove them. Always check important answers.
- RAG adds extra steps, so it can be a little slower than a plain LLM.

## Quick Recap

- An LLM knows only what it learned during training.
- RAG lets an LLM look up information before it answers.
- The steps are: prepare the documents, search for matching chunks, add them to the prompt, and write the answer.
- To update the knowledge, change the documents. No new training is needed.

An easy way to remember RAG: Find, Add, Write.

## Key Words

- LLM: A computer program that reads and writes text.
- RAG: A method where the AI finds information first and then writes the answer.
- Chunk: A small piece of a document.
- Embedding: A list of numbers that stores the meaning of a text.
- Vector database: A storage place that finds similar embeddings fast.
- Prompt: The message sent to the LLM.
- Hallucination: A made-up answer that sounds correct.
- Fine-tuning: Teaching an LLM again with new data.

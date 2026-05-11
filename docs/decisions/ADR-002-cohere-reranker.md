# ADR-002: Add Cohere reranker for parent-child candidate reranking

## Status
Accepted

## Date
2026-05-12

## Context

We maintain a hierarchical document retrieval pipeline that returns candidate "child" chunks (fine-grained passages) and associated parent documents. The retrieval stage aims for high recall, producing an ordered list of candidates that are then passed to the answer generation step. However, ranking quality from the initial retrieval (embedding-similarity + simple heuristics) is insufficient in several cases:

- Sibling passages from the same parent can crowd out more relevant content from different parents.
- Embedding-only similarity sometimes prefers lexical overlap rather than contextual relevance for the current query.
- We want to improve the quality of top-k candidates sent to the generator to reduce hallucination risk and improve citation grounding.

We evaluated options including in-house cross-encoder re-rankers (costly CPU/GPU and maintenance), using open-source models locally, and managed API re-rankers. Cohere offers a managed reranking endpoint with a simple API, reasonable latency for our traffic, and a cost structure that aligns with expected usage for reranking a small number of candidates per query.

## Decision

Adopt the Cohere reranker as a secondary ranking stage applied after the initial candidate retrieval. The reranker operates on candidate children and produces a relevance score used to reorder candidates. We use a two-step candidate flow:

1. Child rerank: For each query, the initial retriever returns up to C children (fine-grained chunks). Send these children to the Cohere reranker to obtain rerank scores.
2. Map parents: After reranking children, group candidates by parent document and surface top candidates while preserving reranked order when building the final parent/child candidate set for the generator.

Implementation will live in rag_core as a focused module: rag_core/cohere_reranker.py and integration glue in rag_core/rerank_retriever.py and step3_vector_db.py. The reranker will be a best-effort, fail-open component (see Fail-Open).

## Alternatives Considered

1. Local cross-encoder (e.g., SentenceTransformers cross-encoders)
   - Pros: Lower per-query cost at high volume, full control over inference.
   - Cons: Requires GPU/CPU infrastructure, model lifecycle management, adds operational complexity.

2. Open-source models served via managed infra (e.g., repackaged LLMs)
   - Pros: Flexible, avoid vendor lock-in.
   - Cons: Still operational overhead, potentially higher latency unless provisioned carefully.

3. No reranker, rely on improved retriever heuristics
   - Pros: Simpler, fewer components.
   - Cons: Limited ability to alter relative ordering without changing retriever design; generator quality suffers from poorer top-k candidates.

Rationale: Cohere strikes a balance between improved ranking quality, predictable latency, and minimal operational burden. It can be swapped later if needed; ADR should be revisited if cost, latency, or accuracy become unacceptable.

## Consequences

- Improved top-k candidate relevance and citation accuracy for the generator.
- Additional external dependency (Cohere API) and associated credentials to manage in .env.
- Small increase in per-query latency (typically tens to low hundreds of ms depending on candidate set size and network). We expect the generator's latency to still dominate in many cases.
- Monitoring and fallback paths are required to maintain availability and low error rates.

## Fail-Open

The reranker is not critical for correctness. If the Cohere reranker is unreachable, returns errors, or exceeds latency thresholds, the system will:

1. Log the error at warning/error level with context (query id, candidate count, error details).
2. Continue processing using the original retriever ordering (embedding similarity + heuristics).
3. Emit a metric (counter + latency histogram) so that the incident is observable in monitoring dashboards.

The policy preserves availability and avoids blocking user requests for reranker failures.

## Candidate Flow

1. Initial retrieval: step3_vector_db.py (or the retriever) returns up to R_RETRIEVE_CANDIDATES children per query (configurable).
2. Child grouping: Candidates are prepared with metadata (source, page, doc_id, parent_id, score).
3. Cohere reranker call: rag_core/cohere_reranker.py sends the children and query to Cohere's reranking endpoint. The reranker returns per-child relevance scores.
4. Reordering: rag_core/rerank_retriever.py applies the rerank scores to reorder the child list.
5. Parent-level mapping: After child rerank, we map children back to parents and optionally perform a parent-level selection step (e.g., choose top N parents while keeping child-level ordering within each parent) used by the generator.

The code must preserve original metadata (source, page, doc_id) so that generation and citation-based answers can reference the exact passage.

## Configuration & Parameters

The reranker will expose the following configurable parameters (environment variables or rag_core/config.py):

- RERANK_ENABLED (bool): Enable/disable reranking.
- RERANK_PROVIDER (str): 'cohere' (current default) — allows swapping provider later.
- RERANK_CANDIDATE_K (int): Number of child candidates to send to the reranker per query (default: 20). This bounds cost and latency.
- RERANK_TIMEOUT_MS (int): Network/inference timeout for reranker calls (default: 1000 ms).
- RERANK_FAIL_OPEN (bool): Whether to fail open (default: true).
- COHERE_API_KEY (string): API key stored in .env and never checked into git.
- COHERE_RERANK_MODEL (string): Cohere reranker model identifier (configurable).

Reasonable defaults should be set and documented in rag_core/config.py. Keep RERANK_CANDIDATE_K modest to control cost and latency; tuning can be performed after deployment.

## Observability

- Logs: warn/error logs when reranker calls fail; info logs for sampling successful rerank decisions (do not log full text in production).
- Metrics: counters for rerank requests, successes, failures; histograms for latency; gauge for active retries.
- Tracing: include spans around external calls to Cohere to measure distributed latency.

## Security and Privacy

- The data sent to Cohere will only include the query and candidate passage text required for reranking. Do not send unredacted PII unless policy and user consent allow it.
- Store COHERE_API_KEY in .env and load via rag_core/config.py. Never commit keys.

## When to Revisit

- If per-query cost grows beyond budget.
- If latency increases beyond acceptable thresholds for user experience.
- If reranker quality does not yield measurable improvements in answer quality and citation grounding.

## Related ADRs

- ADR-001: (placeholder) — decisions about the retriever or vector DB should be referenced here if they affect candidate generation.

---

Authors: engineering team


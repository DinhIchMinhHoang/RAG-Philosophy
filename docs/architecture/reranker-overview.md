# Reranker Architecture Overview

This document describes the reranker subsystem, runtime behavior, and where the implementation lives in the codebase.

Goals

- Improve the relevance ordering of top-k candidates sent to the generator.
- Keep operational complexity low (managed provider) while preserving observability and fail-open behavior.

Key Components and Code Locations

- rag_core/cohere_reranker.py — adapter for the Cohere reranking API. Responsible for preparing requests, calling the external endpoint, handling timeouts/errors, and returning per-candidate scores.
- rag_core/rerank_retriever.py — integration layer that orchestrates initial retrieval, invokes the reranker when enabled, applies new ordering to child candidates, and maps reranked children back to parent documents.
- step3_vector_db.py — initial candidate retrieval step that produces the child candidates and metadata (source, page, doc_id, parent_id). This is the upstream provider of candidates for reranking.

Runtime Flow

1. Request arrives with a user query.
2. The retriever (step3_vector_db.py) returns up to R_RETRIEVE_CANDIDATES child passages with metadata.
3. If RERANK_ENABLED and provider is cohere, rerank_retriever invokes cohere_reranker with the query and the top RERANK_CANDIDATE_K children.
4. cohere_reranker returns per-child scores. rerank_retriever reorders children by score (descending) and then maps children back to parents for parent-level selection.
5. The top candidates (parents+children) are forwarded to the generator component.
6. If the reranker fails or times out, rerank_retriever logs and uses the original retriever order (fail-open).

Operational Notes

- Logs: Reranker errors should be logged with context (query id, candidate count, exception). Avoid logging full passage text in high-volume production logs. Sampled info logs can include small excerpts for debugging.
- Metrics: Track rerank request count, success/failure counts, and latency histograms. Add an alert for elevated failure-rate or latency beyond RERANK_TIMEOUT_MS.
- Tracing: Wrap external calls in a tracing span so end-to-end latency is visible in distributed tracing dashboards.
- Secrets: COHERE_API_KEY must be stored in .env and accessed via rag_core/config.py. Never commit secrets.

Performance Expectations

- Latency: Expect added latency proportional to RERANK_CANDIDATE_K and network latency to Cohere. Typical median additional latency should be tens to low hundreds of milliseconds.
- Throughput: Keep RERANK_CANDIDATE_K modest (default: 20) to control cost and throughput impact. If throughput grows, consider batching, caching, or moving to a local cross-encoder.
- Cost: Cohere billing is aligned to requests and tokens. Keep candidate windows small and monitor cost metrics.

Failure Modes

- Network errors / timeouts: fail-open and log. Consider retry with backoff only for transient network errors and if within latency budget.
- Provider degradation / cost spikes: have a runbook to temporarily disable reranking (flip RERANK_ENABLED to false) and revisit later.

Extensibility

- Provider abstraction: rag_core/cohere_reranker exposes a small adapter interface so additional providers can be added (RERANK_PROVIDER config). Keep the adapter surface minimal: accept (query, candidates, timeout) and return scored candidates.
- Tuning: RERANK_CANDIDATE_K, RERANK_TIMEOUT_MS, and COHERE_RERANK_MODEL are primary tuning knobs.

Related Documents

- docs/decisions/ADR-002-cohere-reranker.md — ADR describing the decision and trade-offs.

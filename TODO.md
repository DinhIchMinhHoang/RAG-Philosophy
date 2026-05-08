# TODO

- Verify RAGAS eval succeeds using cached records (`--records-in data/ragas_records.json`).
- If timeouts persist, raise `RunConfig(timeout=...)` in `rag_core/ragas_eval.py`.
- If Gemini async errors recur, strip `top_p`, `top_k`, or `n` in `_agenerate`.
- Decide whether to reintroduce rate limiting for free-tier stability.

# TODO

## Completed
- ✅ Pipeline refactor: added `rag_core/common/` (logging_utils, pdf_utils, embeddings) and `rag_core/pipeline.py` with orchestration layer
- ✅ Refactored step1–step4 to use shared logging + step3 uses shared embeddings builder
- ✅ Refactored `main_test.py` to use `pipeline.build_pipeline()` + `pipeline.query()`
- ✅ Refactored `ragas_eval.py` to use `pipeline.ingest()` and shared `build_embeddings`
- ✅ Added 4 unit test files (9 tests), all passing

## Pending
- (none currently)

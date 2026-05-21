# Retrieval Metrics

## Overview

Retrieval quality is measured using RAGAS (RAG Assessment) metrics.

## Metrics

### Faithfulness

Measures if LLM response is grounded in retrieved context.

```
faithfulness = (claims_in_answer / total_claims) × 100%
```

### Answer Relevancy

Measures how relevant the answer is to the question.

```
relevancy = f(answer, question_embedding) → cosine similarity
```

### Context Precision

Measures if relevant chunks are ranked higher.

```
precision = Σ(precision_at_k × relevance_at_k) / Σ(relevant_items)
```

### Context Recall

Measures if all relevant information is retrieved.

```
recall = retrieved_relevant_chunks / total_relevant_chunks
```

## Running Evaluation

```bash
# Full evaluation
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv

# Reuse cached records
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv --records-in data/ragas_records.json
```

## Interpreting Results

- **Faithfulness > 80%**: Most claims supported by context
- **Answer Relevancy > 70%**: Answer addresses question
- **Context Precision > 60%**: Top results are relevant
- **Context Recall > 70%**: Most relevant info retrieved

## Known Limitations

- Metrics rely on LLM-as-judge
- May penalize creative but correct answers
- Does not measure citation accuracy
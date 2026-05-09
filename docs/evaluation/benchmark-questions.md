# Benchmark Questions

## Overview

These questions are used to evaluate the RAG system's retrieval and generation quality.

## Philosophy Domain Questions

### Basic Factual

1. "Triết học là gì?" (What is philosophy?)
2. "Ai là người sáng lập chủ nghĩa Marx?" (Who founded Marxism?)
3. "Năm nào Karl Marx viết Tuyên ngôn Đảng Cộng sản?"
4. "Chủ nghĩa hiện thực (realism) trong triết học định nghĩa thế nào?"

### Concept Explanation

5. "Giải thích sự khác biệt giữa chủ nghĩa duy vật và chủ nghĩa duy tâm."
6. "Phép biện chứng là gì? Cho ví dụ."
7. "Ý nghĩa của 'đấu tranh giai cấp' trong triết học Marx."

### Multi-part Questions

8. "So sánh quan điểm của Hegel và Marx về lịch sử."
9. "Liệt kê các giai đoạn phát triển của triết học phương Tây."

### Critical Thinking

10. "Theo bạn, lý thuyết của Nietzsche có mâu thuẫn với Darwin không?"

## Evaluation Dataset

The evaluation uses `data/dataset.json` with format:

```json
[
    {
        "question": "Triết học là gì?",
        "answer": "Triết học là...",
        "sources": ["philosophy.pdf"]
    }
]
```

## RAGAS Evaluation

Run evaluation:

```bash
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv
```

Reuse cached records:

```bash
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv --records-in data/ragas_records.json
```
# Hallucination Checklist

## Overview

This checklist helps identify and prevent hallucinations in LLM responses.

## Checklist

### Before Response Generation

- [ ] Verify retriever returned non-empty context
- [ ] Check context contains relevant information
- [ ] Ensure at least 1 source document matches query topic

### After Response Generation

- [ ] Review answer against retrieved context
- [ ] Verify all factual claims appear in context
- [ ] Check citations match actual sources
- [ ] Ensure no external knowledge used (unless explicitly needed)

### System Prompt Verification

- [ ] System prompt instructs: "Chỉ sử dụng thông tin từ tài liệu được cung cấp"
- [ ] System prompt instructs: "Nếu thông tin không đủ, hãy chỉ ra phần nào thiếu"

## Warning Signs

| Symptom | Likely Cause |
|---------|---------------|
| Answer says "the text doesn't mention..." | Good - acknowledging gap |
| Answer provides specific facts not in sources | Potential hallucination |
| Answer diverges from source content | Check prompt adherence |
| No sources at end of answer | Check RAGService code |

## Manual Testing

1. Ask question with known answer in PDF
2. Verify answer matches source exactly
3. Check citation page numbers
4. Test edge case: ask about topic not in documents

```python
# Should return: "Không tìm thấy tài liệu phù hợp"
query("What is quantum physics?")  # If no quantum docs loaded
```

## System Prompt Reminder

The current system prompt enforces citation from provided context. If hallucinations persist, consider:

1. Reducing temperature (currently 0.2)
2. Adding more explicit "only use context" instructions
3. Implementing fact-checking layer
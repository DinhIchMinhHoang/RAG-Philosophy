# Chunking Strategy

## Overview

The system uses a **Parent-Child Chunking Strategy** to balance retrieval precision with context richness for the LLM.

## Configuration

Defined in `rag_core/config.py`:

```python
# Parent Chunks (for LLM context)
PARENT_CHUNK_SIZE: int = 2000    # Max characters per parent chunk
PARENT_CHUNK_OVERLAP: int = 200  # Overlap between parent chunks

# Child Chunks (for vector search)
CHILD_CHUNK_SIZE: int = 500      # Max characters per child chunk
CHILD_CHUNK_OVERLAP: int = 100   # Overlap between child chunks
```

## Chunking Algorithm

### Step 1: Page ? Parent Chunks

```
Input: Document(page_content=page_text, metadata={source, page})

RecursiveCharacterTextSplitter(chunk_size=2000, overlap=200)
    ¦
    ?
For each raw_parent in splitted_documents:
    doc_id = UUID()
    parent = Document(
        page_content = raw_parent.page_content,
        metadata = {source, page, doc_id}
    )
    all_parents.append(parent)
```

### Step 2: Parent ? Child Chunks

```
For each parent in all_parents:
    RecursiveCharacterTextSplitter(chunk_size=500, overlap=100)
        ¦
        ?
    For each raw_child in splitted_documents:
        child = Document(
            page_content = raw_child.page_content,
            metadata = {source, page, doc_id}  # Inherit from parent
        )
        all_children.append(child)
```

## Separators

Both splitters use the same separator hierarchy:

```python
separators = ["\n\n", "\n", ". ", " ", ""]
```

This ensures chunks respect paragraph boundaries first, then sentences, then words.

## doc_id Linkage

The `doc_id` is a UUID generated for each parent chunk. All child chunks derived from that parent inherit the same `doc_id`. This enables the MultiVectorRetriever to map child matches back to parent context:

```
Query ? Qdrant (child) ? doc_id ? InMemoryStore (parent)
```

### Step 3 Validation

`step3_vector_db.py` validates that every `child_docs` item has a `doc_id` before indexing and raises `KeyError` if any child is missing it. The same metadata key is required for parent docs as well.

`BM25ChildIndex` also builds over the `child_docs` list, so hybrid retrieval depends on the same `doc_id` linkage.

Tokenization uses `SPARSE_MIN_TOKEN_LEN` from `rag_core/config.py`; a regex word tokenizer is used as the fallback tokenizer path.

## Metadata Preservation

| Metadata Key | Added At | Preserved To |
|--------------|----------|--------------|
| `source` | Step 1 (parser) | Parent + Child |
| `page` | Step 1 (parser) | Parent + Child |
| `doc_id` | Step 2 (chunker) | Parent + Child |

## Chunk Statistics

Expected output for a typical 10-page PDF:

| Document Type | Approximate Count |
|---------------|-------------------|
| Pages (Step 1) | 10 |
| Parent Chunks | ~50 (2000 chars/page ? 10 chunks/page) |
| Child Chunks | ~200 (500 chars/parent ? 4 children/parent) |

## Trade-offs

### Advantages

1. **Granular matching**: Small child chunks capture specific concepts
2. **Rich context**: Parent chunks provide full sentences/paragraphs
3. **No loss**: Every child belongs to a parent (no orphans)

### Disadvantages

1. **Memory**: InMemoryStore holds full parent documents
2. **Complexity**: doc_id linking adds implementation overhead
3. **Overlap**: Overlapping chunks may cause redundant retrieval

## Validation

The `step2_chunker.py` self-test verifies no orphan children:

```python
parent_ids = {p.metadata["doc_id"] for p in parent_docs}
child_ids  = {c.metadata["doc_id"] for c in child_docs}
orphan_children = child_ids - parent_ids
assert not orphan_children  # Every child has a parent
```

# Graph RAG Notes

## Current Status

**Not Implemented**

The current system uses a standard parent-child chunking approach with MultiVectorRetriever. Graph RAG (knowledge graph-based retrieval augmentation) has not been implemented.

## Potential Implementation

If Graph RAG were to be added, the following approach would be considered:

### Concept

Build a knowledge graph from documents:
- **Entities**: Key concepts, people, organizations, locations
- **Relationships**: Links between entities with context

### Pipeline Addition

1. **Entity Extraction**: Use LLM to extract named entities from each chunk
2. **Graph Construction**: Create nodes (entities) and edges (relationships)
3. **Graph Storage**: Use graph database (Neo4j) or in-memory graph
4. **Hybrid Retrieval**: Combine vector search + graph traversal

### Benefits

- Better handling of multi-hop questions
- Explainable reasoning via graph paths
- Relationship-aware context

### Resources

- LangChain graph retrieval: `langchain.graphs` module
- Graph databases: Neo4j, NetworkX (in-memory)
- Entity extraction: Prompt-based LLM extraction

## Open Questions

1. Which graph database to use?
2. How to define entity extraction prompts for philosophy texts?
3. What is the expected performance impact?

## See Also

- Related papers in `docs/references/papers.md`
- Evaluation metrics in `docs/evaluation/retrieval-metrics.md`
from __future__ import annotations

from typing import List

from langchain.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

try:
    from .common.embeddings import build_embeddings as build_embeddings_from_common
    from .config import Config
    from .hybrid_retriever import BM25ChildIndex, HybridParentRetriever
    from .rerank_retriever import ChildRerankParentRetriever
except ImportError:  # pragma: no cover
    from common.embeddings import build_embeddings as build_embeddings_from_common
    from config import Config
    from hybrid_retriever import BM25ChildIndex, HybridParentRetriever
    from rerank_retriever import ChildRerankParentRetriever


def _init_embeddings() -> HuggingFaceEmbeddings:
    return build_embeddings_from_common()


def _build_qdrant_store(
    child_docs: List[Document],
    embeddings: HuggingFaceEmbeddings,
    ids: List[str],
) -> QdrantVectorStore:
    return QdrantVectorStore.from_documents(
        documents=child_docs,
        embedding=embeddings,
        location=Config.QDRANT_LOCATION,
        collection_name=Config.QDRANT_COLLECTION,
        ids=ids,
    )


def _validate_child_docs(child_docs: List[Document]) -> None:
    for idx, doc in enumerate(child_docs):
        if not doc.metadata.get("doc_id"):
            raise KeyError(f"child_docs[{idx}] missing doc_id in metadata")


def _build_doc_store(parent_docs: List[Document]) -> InMemoryStore:
    store = InMemoryStore()
    for idx, doc in enumerate(parent_docs):
        if "doc_id" not in doc.metadata:
            raise KeyError(f"parent_docs[{idx}] missing doc_id in metadata")
    store.mset([(doc.metadata["doc_id"], doc) for doc in parent_docs])
    return store


def build_vector_db(child_docs: List[Document], parent_docs: List[Document]):
    if not child_docs:
        raise ValueError("child_docs is empty")
    if not parent_docs:
        raise ValueError("parent_docs is empty")

    _validate_child_docs(child_docs)

    # Bóc tách ID vật lý (Lập trình phòng thủ — Fail-fast)
    child_ids: List[str] = []
    for idx, doc in enumerate(child_docs):
        point_id = doc.metadata.pop("_child_point_id", None)
        if point_id is None:
            raise ValueError(
                f"child_docs[{idx}] missing '_child_point_id' in metadata. "
                "Ensure step 2 ran correctly."
            )
        child_ids.append(point_id)

    embeddings = _init_embeddings()
    vectorstore = _build_qdrant_store(child_docs, embeddings, ids=child_ids)
    doc_store = _build_doc_store(parent_docs)

    # Rerank mode: always use dense+BM25 to get child candidates, rerank children,
    # then map to parent docs (fail-open if Cohere not available).
    if Config.RERANK_ENABLED:
        bm25_index = BM25ChildIndex.from_documents(child_docs)
        final_parent_k = Config.HYBRID_FINAL_K if Config.HYBRID_ENABLED else Config.TOP_K_RESULTS
        return ChildRerankParentRetriever(
            vectorstore=vectorstore,
            docstore=doc_store,
            bm25_index=bm25_index,
            id_key="doc_id",
            final_parent_k=final_parent_k,
        )

    if Config.HYBRID_ENABLED:
        return HybridParentRetriever(
            vectorstore=vectorstore,
            docstore=doc_store,
            bm25_index=BM25ChildIndex.from_documents(child_docs),
            id_key="doc_id",
        )

    return MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=doc_store,
        id_key="doc_id",
        search_kwargs={"k": Config.TOP_K_RESULTS},
    )

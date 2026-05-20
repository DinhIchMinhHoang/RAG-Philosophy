import unittest
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from rag_core.pipeline import PipelineArtifacts, build_pipeline, ingest


class TestPipeline(unittest.TestCase):
    @patch("rag_core.pipeline.build_vector_db")
    @patch("rag_core.pipeline.chunk_documents")
    @patch("rag_core.pipeline.HybridPDFParser")
    @patch("rag_core.pipeline.pdf_utils.collect_pdf_paths")
    def test_ingest_builds_retriever(
        self,
        mock_collect,
        mock_parser_cls,
        mock_chunk,
        mock_build,
    ) -> None:
        mock_collect.return_value = ["C:/tmp/a.pdf"]

        parser_instance = MagicMock()
        parser_instance.parse_pdf.return_value = [
            Document(page_content="text", metadata={"source": "a.pdf", "page": 1})
        ]
        mock_parser_cls.return_value = parser_instance

        child_docs = [Document(page_content="c", metadata={"source": "a.pdf", "page": 1, "doc_id": "1"})]
        parent_docs = [Document(page_content="p", metadata={"source": "a.pdf", "page": 1, "doc_id": "1"})]
        mock_chunk.return_value = (child_docs, parent_docs)
        mock_build.return_value = "retriever"

        artifacts = ingest()

        self.assertIsInstance(artifacts, PipelineArtifacts)
        self.assertEqual(artifacts.child_docs_count, 1)
        self.assertEqual(artifacts.parent_docs_count, 1)
        self.assertEqual(artifacts.retriever, "retriever")
        self.assertEqual(artifacts.pdf_paths, ["C:/tmp/a.pdf"])

    @patch("rag_core.pipeline.setup_rag_chain")
    @patch("rag_core.pipeline.ingest")
    def test_build_pipeline_returns_chain(self, mock_ingest, mock_setup) -> None:
        mock_ingest.return_value = PipelineArtifacts(
            retriever="retriever",
            child_docs_count=1,
            parent_docs_count=1,
            pdf_paths=["C:/tmp/a.pdf"],
        )
        mock_setup.return_value = "chain"

        artifacts, chain = build_pipeline()

        self.assertEqual(artifacts.retriever, "retriever")
        self.assertEqual(chain, "chain")

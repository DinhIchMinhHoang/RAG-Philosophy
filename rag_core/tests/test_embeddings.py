<<<<<<< HEAD
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from unittest.mock import patch

from config import Config
from common.embeddings import build_embeddings


class TestEmbeddings(unittest.TestCase):
    @patch("common.embeddings.HuggingFaceEmbeddings")
=======
import unittest
from unittest.mock import patch

from rag_core.config import Config
from rag_core.common.embeddings import build_embeddings


class TestEmbeddings(unittest.TestCase):
    @patch("rag_core.common.embeddings.HuggingFaceEmbeddings")
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
    def test_build_embeddings_calls_model(self, mock_cls) -> None:
        build_embeddings()
        mock_cls.assert_called_once()
        kwargs = mock_cls.call_args.kwargs

        self.assertEqual(kwargs["model_name"], Config.EMBEDDING_MODEL_NAME)
        self.assertEqual(kwargs["model_kwargs"]["device"], Config.DEVICE)
        self.assertTrue(kwargs["model_kwargs"]["trust_remote_code"])
        self.assertTrue(kwargs["encode_kwargs"]["normalize_embeddings"])


if __name__ == "__main__":
<<<<<<< HEAD
    unittest.main()
=======
    unittest.main()
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

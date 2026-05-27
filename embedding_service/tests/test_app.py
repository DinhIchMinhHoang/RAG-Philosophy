from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from embedding_service.app import main


class _FakeModel:
    def encode(self, texts, batch_size: int, normalize_embeddings: bool):
        assert normalize_embeddings is True
        return [[float(index), float(index) + 0.5] for index, _text in enumerate(texts)]


def _fake_load_model() -> None:
    main.state.model = _FakeModel()
    main.state.ready = True
    main.state.error = None
    main.state.dimension = 2
    main.state.device = "cpu"
    main.state.loaded_at = 1.0


class EmbeddingServiceEndpointTests(unittest.TestCase):
    def test_health_info_embed_and_embed_batch(self) -> None:
        with patch.object(main, "load_model", side_effect=_fake_load_model):
            with TestClient(main.app) as client:
                health = client.get("/health")
                self.assertEqual(health.status_code, 200)
                self.assertEqual(health.json()["ready"], True)

                info = client.get("/info")
                self.assertEqual(info.status_code, 200)
                self.assertEqual(info.json()["model_name"], main.settings.model_name)
                self.assertEqual(info.json()["embedding_dimension"], 2)
                self.assertEqual(info.json()["device"], "cpu")
                self.assertEqual(info.json()["configured_device"], main.settings.device)
                self.assertEqual(info.json()["normalize_embeddings"], True)
                self.assertIn("cuda", info.json())

                embed = client.post("/embed", json={"text": "hello"})
                self.assertEqual(embed.status_code, 200)
                self.assertEqual(embed.json()["embedding"], [0.0, 0.5])

                batch = client.post("/embed-batch", json={"texts": ["a", "b", "c"], "batch_size": 2})
                self.assertEqual(batch.status_code, 200)
                self.assertEqual(batch.json()["embeddings"], [[0.0, 0.5], [1.0, 1.5], [2.0, 2.5]])

    def test_auto_device_uses_cuda_when_available(self) -> None:
        with patch.object(main, "_cuda_status", return_value={"available": True, "device_count": 1}):
            self.assertEqual(main._resolve_device("auto"), "cuda")

    def test_auto_and_cuda_devices_fall_back_to_cpu_when_cuda_unavailable(self) -> None:
        with patch.object(main, "_cuda_status", return_value={"available": False, "device_count": 0}):
            self.assertEqual(main._resolve_device("auto"), "cpu")
            self.assertEqual(main._resolve_device("cuda"), "cpu")


if __name__ == "__main__":
    unittest.main()

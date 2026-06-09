import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from google.genai.errors import ClientError

from infrastructure.google_embeddings import GoogleGenAIEmbeddings


class FakeClient:
    class Models:
        def embed_content(self, model, contents):
            raise ClientError(429, {"error": {"message": "quota exceeded"}})

    models = Models()


class GoogleEmbeddingsFallbackTests(unittest.TestCase):
    def test_falls_back_to_local_embeddings_on_quota_error(self):
        os.environ["USE_LOCAL_EMBEDDINGS"] = "1"
        try:
            with patch("infrastructure.google_embeddings.genai.Client", return_value=FakeClient()):
                with patch("infrastructure.google_embeddings.DefaultEmbeddingFunction") as fake_default:
                    fake_default.return_value = lambda texts: [[0.1, 0.2] for _ in texts]
                    embeddings = GoogleGenAIEmbeddings(api_key="test-key", model="gemini-embedding-001")

                    result = embeddings.embed_documents(["texto de prueba"])

                    self.assertEqual(result, [[0.1, 0.2]])
        finally:
            os.environ.pop("USE_LOCAL_EMBEDDINGS", None)


if __name__ == "__main__":
    unittest.main()

import sys
import json
sys.path.insert(0, "/home/sinan/GitHub/reservix/ai-assistant/etl/pipeline/notebooks")

try:
    from sentence_transformers import SentenceTransformer

    class EmbeddingProvider:
        def __init__(self, model_name: str = "all-mpnet-base-v2"):
            self.model = SentenceTransformer(model_name)

        def embed(self, text: str) -> list[float]:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()

except ImportError:
    print("Warning: sentence-transformers not available in MCP server venv")
    print("Using embeddings from notebooks venv as fallback")

    import subprocess
    import os

    class EmbeddingProvider:
        def __init__(self, model_name: str = "all-mpnet-base-v2"):
            self.model_name = model_name

        def embed(self, text: str) -> list[float]:
            notebook_venv = "/home/sinan/GitHub/reservix/ai-assistant/etl/pipeline/notebooks/venv"
            python_exe = f"{notebook_venv}/bin/python"

            script = f"""
import sys
sys.path.insert(0, '/home/sinan/GitHub/reservix/ai-assistant/etl/pipeline/notebooks')
from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer('{self.model_name}')
embedding = model.encode('''{text}''', convert_to_tensor=False)
print(json.dumps(embedding.tolist()))
"""

            result = subprocess.run(
                [python_exe, "-c", script],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Embedding generation failed: {result.stderr}")

            return json.loads(result.stdout.strip())

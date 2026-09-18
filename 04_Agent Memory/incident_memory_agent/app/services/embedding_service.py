"""Turn text into NVIDIA-generated embedding vectors, explicit about document vs. query intent."""

from openai import OpenAI

from app.config.settings import EMBEDDING_DIMS, EMBEDDING_MODEL, NVIDIA_KEY

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

client = OpenAI(api_key=NVIDIA_KEY, base_url=NVIDIA_BASE_URL)


def embed_document(text: str) -> list[float]:
    """Embed text meant to be stored as a memory (passage mode)."""
    return _embed(text, input_type="passage")


def embed_query(text: str) -> list[float]:
    """Embed text meant to search against stored memories (query mode)."""
    return _embed(text, input_type="query")


def _embed(text: str, input_type: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text cannot be empty.")

    if input_type not in {"passage", "query"}:
        raise ValueError("Invalid input_type.")

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text],
        extra_body={"input_type": input_type, "truncate": "NONE"},
    )

    vector = response.data[0].embedding

    if len(vector) != EMBEDDING_DIMS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMS}-dimensional embedding, got {len(vector)}."
        )

    return vector

"""Text embedder using sentence-transformers."""

from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None
MODEL_NAME = "all-mpnet-base-v2"


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    return model.encode(texts, convert_to_numpy=True).tolist()

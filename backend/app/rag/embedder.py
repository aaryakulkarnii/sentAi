"""Text embedder using sentence-transformers."""

from app.core.config import settings

_model = None
MODEL_NAME = "all-mpnet-base-v2"

def get_embedder():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed(texts: list[str]) -> list[list[float]]:
    if settings.DISABLE_LOCAL_EMBEDDINGS:
        # Mock embedder that returns zeroes for 768-dim vectors
        return [[0.0] * 768 for _ in texts]
    
    model = get_embedder()
    return model.encode(texts, convert_to_numpy=True).tolist()

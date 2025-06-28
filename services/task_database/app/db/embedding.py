from typing import List

from sentence_transformers import SentenceTransformer

EMBEDDING_SIZE = 384
try:
    _embedding_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
except ImportError:
    raise ImportError(
        "Please install sentence-transformers: pip install sentence-transformers"
    )


def generate_embedding(text: str) -> List[float]:
    """
    Generates an embedding for the given text using a pre-trained SentenceTransformer model.

    Args:
        text (str): The input text to embed.

    Returns:
        List[float]: The dense vector representation of the text.
    """
    embedding = _embedding_model.encode(text, convert_to_numpy=True).tolist()
    return embedding

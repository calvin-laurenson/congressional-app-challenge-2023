from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
from numpy.typing import NDArray

model = SentenceTransformer("jinaai/jina-embeddings-v2-base-en")


def cosine_similarity(A: NDArray, B: NDArray):
    return np.dot(A, B) / (norm(A) * norm(B))

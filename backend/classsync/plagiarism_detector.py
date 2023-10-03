from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
from numpy.typing import NDArray

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def cosine_similarity(A: NDArray, B: NDArray):
    return np.dot(A,B)/(norm(A)*norm(B))

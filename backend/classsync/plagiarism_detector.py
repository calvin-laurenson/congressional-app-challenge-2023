from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def cosine_similarity(A,B):
    return np.dot(A,B)/(norm(A)*norm(B))

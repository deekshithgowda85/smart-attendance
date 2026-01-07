import numpy as np


def euclidean_distance(a, b):
    """Calculate Euclidean distance between two embeddings."""
    return np.linalg.norm(np.array(a) - np.array(b))


def match_embedding(detected_emb, known_embeddings):
    """
    Match detected embedding against known embeddings.
    
    Args:
        detected_emb: Single embedding to match
        known_embeddings: List of embeddings for ONE student
    
    Returns:
        best_distance (float) or None
    """
    if not known_embeddings:
        return None
    
    distances = [euclidean_distance(detected_emb, e) for e in known_embeddings]
    return min(distances)

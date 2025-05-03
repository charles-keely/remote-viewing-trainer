import numpy as np
import json
from app.services.ai import embed

def cosine(a, b):
    """Calculate the cosine similarity between two vectors"""
    a, b = np.array(a), np.array(b)
    return float(a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def score(notes: str, desc: dict) -> dict:
    """Score the similarity between user notes and target description"""
    # Get embeddings for both texts
    v1 = embed(notes)
    v2 = embed(json.dumps(desc))
    
    # Calculate cosine similarity
    cos = cosine(v1, v2)
    
    # Generate rubric scores based on similarity
    rubric = {
        k: int(cos * 3) for k in ["color", "shape", "sensory", "concept"]
    }
    
    # Calculate total score (weighted average)
    total = 0.4 * cos * 3 + 0.6 * sum(rubric.values()) / len(rubric)
    
    return {
        "cosine": cos,
        "rubric": rubric,
        "total": round(total, 3)
    } 
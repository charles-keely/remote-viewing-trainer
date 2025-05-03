import numpy as np
import json
from app.services.ai import embed

def cosine(a, b):
    """Calculate the cosine similarity between two vectors"""
    a, b = np.array(a), np.array(b)
    return float(a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def score(notes: str, desc: dict) -> dict:
    """Score the similarity between user notes and target description
    
    This improved version evaluates each category separately by creating
    focused embeddings for specific aspects of the image description.
    """
    # Get embeddings for the notes
    notes_emb = embed(notes)
    
    # Calculate overall similarity
    full_desc = json.dumps(desc)
    full_desc_emb = embed(full_desc)
    cos = cosine(notes_emb, full_desc_emb)
    
    # Calculate category-specific similarities
    rubric = {}
    
    # Color similarity - add more context to help embeddings focus better
    color_text = f"Colors present in the image: {', '.join(desc['colors'])}"
    color_emb = embed(color_text)
    color_sim = cosine(notes_emb, color_emb)
    # Apply a stricter threshold to improve discrimination
    rubric["color"] = min(int(max(0, color_sim - 0.3) * 4), 3)
    
    # Shape similarity
    shape_text = f"Shapes and forms in the image: {', '.join(desc['shapes'])}"
    shape_emb = embed(shape_text)
    shape_sim = cosine(notes_emb, shape_emb)
    rubric["shape"] = min(int(max(0, shape_sim - 0.3) * 4), 3)
    
    # Object/concept similarity
    concept_text = f"Objects and items in the image: {', '.join(desc['objects'])}"
    concept_emb = embed(concept_text)
    concept_sim = cosine(notes_emb, concept_emb)
    rubric["concept"] = min(int(max(0, concept_sim - 0.3) * 4), 3)
    
    # Sensory/setting similarity
    sensory_text = f"Setting and atmosphere of the image: {desc['setting']}. Materials present: {', '.join(desc['materials'])}"
    sensory_emb = embed(sensory_text)
    sensory_sim = cosine(notes_emb, sensory_emb)
    rubric["sensory"] = min(int(max(0, sensory_sim - 0.3) * 4), 3)
    
    # Calculate total score (weighted average with higher weight on overall similarity)
    # Apply a curve to make discrimination better between good and poor matches
    total = 0.5 * max(0, cos - 0.25) * 4 + 0.5 * sum(rubric.values()) / len(rubric)
    
    return {
        "cosine": cos,
        "rubric": rubric,
        "total": round(total, 3)
    } 
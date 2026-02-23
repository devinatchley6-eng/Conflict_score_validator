import numpy as np


def scalar_field(embeddings: np.ndarray, center: np.ndarray | None = None) -> np.ndarray:
    """Compute an inverse-distance scalar field F(h)."""
    if center is None:
        center = np.mean(embeddings, axis=0)
    d = np.linalg.norm(embeddings - center, axis=1)
    return 1.0 / (1.0 + d)

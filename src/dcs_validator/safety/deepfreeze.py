import numpy as np
from scipy.linalg import svd


def deepfreeze(matrix: np.ndarray, rank_reduction: float = 0.5) -> np.ndarray:
    """Irreversible rank collapse via SVD."""
    U, s, Vt = svd(matrix, full_matrices=False)
    k = max(1, int(len(s) * (1 - rank_reduction)))
    s[k:] = 0
    return U @ np.diag(s) @ Vt

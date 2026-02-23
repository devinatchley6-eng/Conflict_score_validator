import numpy as np


def conflict_energy(conflicts: np.ndarray, weights: np.ndarray | None = None) -> float:
    if weights is None:
        weights = np.ones_like(conflicts)
    return float(np.sum(np.abs(conflicts) * weights))

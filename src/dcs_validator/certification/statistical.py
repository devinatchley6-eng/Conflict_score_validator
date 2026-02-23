import numpy as np


def benjamini_hochberg(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    p_values = np.asarray(p_values)
    n = len(p_values)
    order = np.argsort(p_values)
    ranked = p_values[order]
    thresholds = alpha * (np.arange(1, n + 1) / n)
    passed = ranked <= thresholds
    result = np.zeros(n, dtype=bool)
    if np.any(passed):
        k = np.max(np.where(passed)[0])
        result[order[: k + 1]] = True
    return result


def replication_probability(conflict_score: float) -> float:
    return float(max(0.0, min(1.0, 1.0 - 2 * conflict_score)))

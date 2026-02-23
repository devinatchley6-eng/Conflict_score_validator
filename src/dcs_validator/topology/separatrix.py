from heapq import heappop, heappush

import numpy as np
from scipy.spatial import KDTree


def saddle_height(
    blob_i: np.ndarray,
    blob_j: np.ndarray,
    all_points: np.ndarray,
    field_values: np.ndarray,
    k: int = 5,
) -> float:
    """Compute ΔV between two blobs using a kNN graph and minimax Dijkstra."""
    tree = KDTree(all_points)
    n = len(all_points)
    edges = [[] for _ in range(n)]
    for i in range(n):
        _, idxs = tree.query(all_points[i], k=min(k + 1, n))
        for j in np.atleast_1d(idxs)[1:]:
            w = max(field_values[i], field_values[j])
            edges[i].append((j, w))
            edges[j].append((i, w))

    is_j = np.zeros(n, dtype=bool)
    is_j[blob_j] = True

    best = np.full(n, np.inf)
    pq = []
    for idx in blob_i:
        best[idx] = field_values[idx]
        heappush(pq, (field_values[idx], idx))

    while pq:
        cur_max, u = heappop(pq)
        if cur_max > best[u]:
            continue
        if is_j[u]:
            max_i = float(np.max(field_values[blob_i]))
            max_j = float(np.max(field_values[blob_j]))
            return max(max_i, max_j) - float(cur_max)
        for v, w in edges[u]:
            new_max = max(cur_max, w)
            if new_max < best[v]:
                best[v] = new_max
                heappush(pq, (new_max, v))
    return float("inf")

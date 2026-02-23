from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class Blob:
    id: int
    samples: np.ndarray
    density: float
    volume: float
    tenacity: float


class BlobExtractor:
    """Minimal threshold-based blob extractor."""

    def extract(self, points: np.ndarray, values: np.ndarray, threshold: float) -> List[Blob]:
        mask = values >= threshold
        if not np.any(mask):
            return []
        selected = points[mask]
        density = float(np.mean(values[mask]))
        volume = float(len(selected))
        tenacity = float(np.std(values[mask]))
        return [Blob(id=0, samples=selected, density=density, volume=volume, tenacity=tenacity)]

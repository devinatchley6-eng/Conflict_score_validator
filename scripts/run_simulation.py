#!/usr/bin/env python3
import numpy as np

from dcs_validator.core.blob import BlobExtractor
from dcs_validator.core.field import scalar_field


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    points = rng.normal(size=(100, 2))
    field = scalar_field(points)
    blobs = BlobExtractor().extract(points, field, threshold=float(np.quantile(field, 0.75)))
    print(f"Extracted blobs: {len(blobs)}")

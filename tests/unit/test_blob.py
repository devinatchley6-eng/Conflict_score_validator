import numpy as np

from dcs_validator.core.blob import BlobExtractor


def test_blob_extract_returns_blob_above_threshold():
    points = np.array([[0.0, 0.0], [1.0, 1.0]])
    values = np.array([0.1, 0.9])
    blobs = BlobExtractor().extract(points, values, threshold=0.5)
    assert len(blobs) == 1
    assert blobs[0].volume == 1.0

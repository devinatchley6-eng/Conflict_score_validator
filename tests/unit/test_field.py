import numpy as np

from dcs_validator.core.field import scalar_field


def test_scalar_field_shape():
    pts = np.array([[0.0, 0.0], [1.0, 1.0]])
    field = scalar_field(pts)
    assert field.shape == (2,)
    assert (field > 0).all()

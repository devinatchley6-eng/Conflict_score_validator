import numpy as np

from dcs_validator.conflict.energy import conflict_energy
from dcs_validator.core.field import scalar_field


def test_minimal_pipeline():
    pts = np.random.default_rng(1).normal(size=(10, 2))
    field = scalar_field(pts)
    energy = conflict_energy(field)
    assert energy > 0

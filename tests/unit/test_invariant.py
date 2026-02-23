from dcs_validator.core.invariant import AtchleyInvariant, AtchleyState


def test_invariant_compute():
    inv = AtchleyInvariant(C=0.1)
    state = AtchleyState(phi=0.5, E=1.0, kappa=0.2, tau=0.3)
    val = inv.compute(state)
    assert val >= 0

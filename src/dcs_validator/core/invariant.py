from dataclasses import dataclass


@dataclass
class AtchleyState:
    """System state for Atchley containment."""

    phi: float
    E: float
    kappa: float
    tau: float


class AtchleyInvariant:
    """Enforces |dphi/dt| * E * |kappa| ≤ C."""

    def __init__(self, C: float = 0.1):
        self.C = C

    def compute(self, state: AtchleyState, dt: float = 1.0e-1) -> float:
        """Compute a bounded surrogate invariant term."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        dphi_dt = abs(state.phi) / dt
        return dphi_dt * max(state.E, 0.0) * abs(state.kappa)

    def is_safe(self, state: AtchleyState, dt: float = 1.0e-1) -> bool:
        return self.compute(state, dt=dt) <= self.C

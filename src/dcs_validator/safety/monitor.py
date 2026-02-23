from dcs_validator.core.invariant import AtchleyInvariant, AtchleyState


class SafetyMonitor:
    def __init__(self, invariant: AtchleyInvariant | None = None):
        self.invariant = invariant or AtchleyInvariant()

    def check(self, state: AtchleyState) -> bool:
        return self.invariant.is_safe(state)

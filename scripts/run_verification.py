#!/usr/bin/env python3
import argparse

import numpy as np

from dcs_validator.certification.statistical import replication_probability
from dcs_validator.conflict.energy import conflict_energy
from dcs_validator.core.invariant import AtchleyInvariant, AtchleyState


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DCS verification.")
    parser.add_argument("--strict", action="store_true", help="Fail if invariant is unsafe.")
    args = parser.parse_args()

    state = AtchleyState(phi=0.05, E=1.0, kappa=0.5, tau=0.3)
    invariant = AtchleyInvariant(C=0.5)
    safe = invariant.is_safe(state)

    conflicts = np.array([0.001, 0.059, 0.130, 0.008])
    energy = conflict_energy(conflicts)
    p_rep = replication_probability(float(np.mean(conflicts)))

    print(f"Invariant safe: {safe}")
    print(f"Conflict energy: {energy:.4f}")
    print(f"Replication probability estimate: {p_rep:.4f}")

    if args.strict and not safe:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

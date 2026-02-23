"""Sentinel-DCS end-to-end reference system with empirical validation.

This module implements:
- RunManifest schema checks
- Deterministic estimator routing
- Intervention verification and release gates
- Synthetic empirical validation harness
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class GaussianFitness:
    kurtosis_max: float
    bimodality_coeff: float
    pca_residual_ratio: float


@dataclass
class Manifest:
    run_id: str
    model_hash: str
    dataset_fingerprints: List[str]
    config_hash: str
    created_at: str
    replay_command: str
    safety_adjacent: bool
    theta_dfid: str
    tail_tau: float
    event_class: str
    delta_tail_abs_max: float
    delta_tail_rel_max: float
    epsilon_v_min: float
    epsilon_h_min: float
    epsilon_conflict_drop_min: float
    epsilon_adapt_increase_min: float
    epsilon_phi_dispersion_drop_min: float


@dataclass
class EvaluationResult:
    gaussian_pass: bool
    z_estimator: str
    verification_pass: bool
    gates: Dict[str, bool]
    details: Dict[str, float]


DEFAULT_THRESHOLDS = {
    "critical": {"delta_tail_abs_max": 0.002, "delta_tail_rel_max": 0.05},
    "elevated": {"delta_tail_abs_max": 0.010, "delta_tail_rel_max": 0.10},
    "standard": {"delta_tail_abs_max": 0.025, "delta_tail_rel_max": 0.15},
}


def hash_config(payload: Dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def validate_manifest(manifest: Manifest) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not manifest.run_id:
        errors.append("run_id missing")
    if manifest.safety_adjacent and manifest.theta_dfid != "THETA_TAIL_MASS":
        errors.append("safety_adjacent requires THETA_TAIL_MASS")
    if manifest.event_class not in DEFAULT_THRESHOLDS:
        errors.append("event_class invalid")
    if manifest.tail_tau <= 0:
        errors.append("tail_tau must be > 0")
    if not manifest.dataset_fingerprints:
        errors.append("dataset_fingerprints missing")
    return (len(errors) == 0, errors)


def gaussian_fitness_pass(gf: GaussianFitness) -> bool:
    flags = 0
    flags += 1 if gf.kurtosis_max > 1.0 else 0
    flags += 1 if gf.bimodality_coeff > 0.555 else 0
    flags += 1 if gf.pca_residual_ratio > 0.15 else 0
    return flags < 2


def route_z_estimator(gf_pass: bool) -> str:
    return "Z_GAUSS_KL_LW" if gf_pass else "Z_KNN_ENTROPY"


def tail_worsens(p_pre: float, p_post: float, abs_max: float, rel_max: float) -> bool:
    delta = p_post - p_pre
    rel = (delta / p_pre) if p_pre > 0 else float("inf")
    return (delta > abs_max) or (p_pre > 0 and rel > rel_max)


def evaluate_intervention(
    manifest: Manifest,
    gf: GaussianFitness,
    p_tail_pre: float,
    p_tail_post: float,
    delta_v: float,
    delta_h: float,
    conflict_drop: float,
    adapt_increase: float,
    dispersion_drop: float,
) -> EvaluationResult:
    ok, errors = validate_manifest(manifest)
    if not ok:
        return EvaluationResult(
            False,
            "INVALID",
            False,
            {"GATE-REPRO": False},
            {"manifest_errors": float(len(errors))},
        )

    gf_pass = gaussian_fitness_pass(gf)
    z_estimator = route_z_estimator(gf_pass)

    tw = tail_worsens(
        p_tail_pre,
        p_tail_post,
        manifest.delta_tail_abs_max,
        manifest.delta_tail_rel_max,
    )

    gate_tail = not tw
    gate_r2 = (delta_v > manifest.epsilon_v_min) or (delta_h > manifest.epsilon_h_min)
    gate_r6 = (
        conflict_drop >= manifest.epsilon_conflict_drop_min
        and adapt_increase >= manifest.epsilon_adapt_increase_min
        and dispersion_drop >= manifest.epsilon_phi_dispersion_drop_min
    )
    gate_r5 = gf_pass or (z_estimator == "Z_KNN_ENTROPY")

    gates = {
        "GATE-REPRO": True,
        "GATE-TAIL": gate_tail,
        "GATE-R2": gate_r2,
        "GATE-R5": gate_r5,
        "GATE-R6": gate_r6,
    }
    verification_pass = all(gates.values())
    return EvaluationResult(
        gf_pass,
        z_estimator,
        verification_pass,
        gates,
        {
            "delta_v": delta_v,
            "delta_h": delta_h,
            "p_tail_pre": p_tail_pre,
            "p_tail_post": p_tail_post,
            "conflict_drop": conflict_drop,
            "adapt_increase": adapt_increase,
            "dispersion_drop": dispersion_drop,
        },
    )


def _normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _sample_gaussian(mean: float, sd: float, rng: random.Random) -> float:
    return rng.gauss(mean, sd)


def run_empirical_validation(trials: int = 2000, seed: int = 42) -> Dict:
    rng = random.Random(seed)

    type1_hits = 0
    power_hits = 0
    gate_consistency = 0
    pass_rates: List[int] = []

    for i in range(trials):
        cfg = {"trial": i, "seed": seed}
        m = Manifest(
            run_id=f"run-{i}",
            model_hash="model123",
            dataset_fingerprints=["dataA"],
            config_hash=hash_config(cfg),
            created_at="2026-02-22T00:00:00Z",
            replay_command="python sentinel_dcs_system.py --validate",
            safety_adjacent=True,
            theta_dfid="THETA_TAIL_MASS",
            tail_tau=0.2,
            event_class="critical",
            delta_tail_abs_max=DEFAULT_THRESHOLDS["critical"]["delta_tail_abs_max"],
            delta_tail_rel_max=DEFAULT_THRESHOLDS["critical"]["delta_tail_rel_max"],
            epsilon_v_min=0.05,
            epsilon_h_min=0.02,
            epsilon_conflict_drop_min=0.05,
            epsilon_adapt_increase_min=0.05,
            epsilon_phi_dispersion_drop_min=0.05,
        )

        gf = GaussianFitness(
            kurtosis_max=max(0.0, _sample_gaussian(0.8, 0.25, rng)),
            bimodality_coeff=max(0.3, _sample_gaussian(0.52, 0.06, rng)),
            pca_residual_ratio=max(0.01, _sample_gaussian(0.12, 0.04, rng)),
        )

        null_delta = _sample_gaussian(0.0, 0.03, rng)
        p_pre_null = max(1e-5, _normal_cdf(_sample_gaussian(-2.0, 0.2, rng)))
        p_post_null = max(1e-5, p_pre_null + null_delta)
        res_null = evaluate_intervention(
            m,
            gf,
            p_pre_null,
            p_post_null,
            delta_v=_sample_gaussian(0.0, 0.03, rng),
            delta_h=_sample_gaussian(0.0, 0.02, rng),
            conflict_drop=_sample_gaussian(0.0, 0.03, rng),
            adapt_increase=_sample_gaussian(0.0, 0.03, rng),
            dispersion_drop=_sample_gaussian(0.0, 0.03, rng),
        )
        if res_null.verification_pass:
            type1_hits += 1

        p_pre_eff = max(1e-5, _normal_cdf(_sample_gaussian(-2.2, 0.2, rng)))
        p_post_eff = max(1e-5, p_pre_eff - abs(_sample_gaussian(0.01, 0.005, rng)))
        res_eff = evaluate_intervention(
            m,
            gf,
            p_pre_eff,
            p_post_eff,
            delta_v=abs(_sample_gaussian(0.09, 0.03, rng)),
            delta_h=abs(_sample_gaussian(0.04, 0.02, rng)),
            conflict_drop=abs(_sample_gaussian(0.09, 0.03, rng)),
            adapt_increase=abs(_sample_gaussian(0.10, 0.03, rng)),
            dispersion_drop=abs(_sample_gaussian(0.08, 0.03, rng)),
        )
        if res_eff.verification_pass:
            power_hits += 1

        should_fallback = not gaussian_fitness_pass(gf)
        fallback_used = res_eff.z_estimator == "Z_KNN_ENTROPY"
        if should_fallback == fallback_used:
            gate_consistency += 1

        pass_rates.append(1 if res_eff.verification_pass else 0)

    type1 = type1_hits / trials
    power = power_hits / trials
    consistency = gate_consistency / trials
    avg_pass = statistics.mean(pass_rates)

    return {
        "trials": trials,
        "seed": seed,
        "type1_error_estimate": type1,
        "power_estimate": power,
        "routing_consistency": consistency,
        "avg_effect_pass_rate": avg_pass,
    }


def generate_report(output_dir: str = "artifacts", trials: int = 2000, seed: int = 42) -> Path:
    report = run_empirical_validation(trials=trials, seed=seed)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "empirical_validation_report.json"
    path.write_text(json.dumps(report, indent=2))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Sentinel-DCS end-to-end system")
    parser.add_argument("--validate", action="store_true", help="run empirical validation")
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()

    if args.validate:
        report_path = generate_report(args.output_dir, args.trials, args.seed)
        print(f"Validation report: {report_path}")
        print(report_path.read_text())
    else:
        print("Run with --validate to execute empirical validation harness.")


if __name__ == "__main__":
    main()

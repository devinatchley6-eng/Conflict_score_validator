import unittest

from sentinel_dcs_system import (
    DEFAULT_THRESHOLDS,
    GaussianFitness,
    Manifest,
    evaluate_intervention,
    gaussian_fitness_pass,
    run_empirical_validation,
    validate_manifest,
)


class SentinelDCSTest(unittest.TestCase):
    def _manifest(self):
        return Manifest(
            run_id="r1",
            model_hash="m",
            dataset_fingerprints=["d"],
            config_hash="c",
            created_at="2026-02-22",
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

    def test_manifest_validation(self):
        ok, errors = validate_manifest(self._manifest())
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_gaussian_routing(self):
        gf_pass = GaussianFitness(0.5, 0.5, 0.1)
        gf_fail = GaussianFitness(1.4, 0.62, 0.2)
        self.assertTrue(gaussian_fitness_pass(gf_pass))
        self.assertFalse(gaussian_fitness_pass(gf_fail))

    def test_intervention_pass(self):
        m = self._manifest()
        gf = GaussianFitness(0.5, 0.5, 0.1)
        r = evaluate_intervention(
            m,
            gf,
            p_tail_pre=0.03,
            p_tail_post=0.02,
            delta_v=0.08,
            delta_h=0.03,
            conflict_drop=0.08,
            adapt_increase=0.08,
            dispersion_drop=0.08,
        )
        self.assertTrue(r.verification_pass)

    def test_empirical_validation_deterministic(self):
        out1 = run_empirical_validation(trials=200, seed=123)
        out2 = run_empirical_validation(trials=200, seed=123)
        self.assertEqual(out1, out2)
        self.assertGreaterEqual(out1["routing_consistency"], 0.95)


if __name__ == "__main__":
    unittest.main()

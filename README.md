# AUFSAFETY- Sentinel-DCS End-to-End Reference

This repository now includes an executable **Sentinel-DCS end-to-end reference system** with reproducible synthetic empirical validation.

## Files
- `sentinel_dcs_system.py` — end-to-end pipeline:
  - manifest validation
  - GaussianFitness routing
  - intervention verification and release gates
  - synthetic empirical validation harness
- `tests/test_sentinel_dcs_system.py` — deterministic tests
- `artifacts/empirical_validation_report.json` — generated validation report (after run)

## Run full empirical validation
```bash
python sentinel_dcs_system.py --validate --trials 2000 --seed 42
```

## Run tests
```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Notes
- This is an **end-to-end implementation** with a full, reproducible validation harness.
- Validation is **synthetic (simulation-based)**; real-world deployment still requires external datasets and protocol registration.

# Sentinel-DCS: A Preregistered Black-Box Framework for Behavioral Drift and Integrity Monitoring in Large Language Models

## Subtitle (Academic)
**The Directional Conflict Score (DCS) Theory of Tail-Rate Drift and Mode Bifurcation in Black-Box Systems**

**ATCHLEY DCS PLATFORM**  
Engineering Design Document — Section III  
Version 0.4 (locked — incorporating prior section revisions)  
February 2026

---

## Section Intent
This section closes the machine-enforceable threshold gap from Section II. All direction functions, estimator choices, and manifest fields are anchored to registered, auditable gates. No informal judgment is allowed in release-blocking decision paths.

---

## 1) Direction Function (DFID) Catalog

Every signed influence score references a registered Direction Function ID (DFID). Addition of any new DFID requires RunManifest update and pre-registration.

> **Safety rule:** For `safety_adjacent: true` claims, DFID **must** be `THETA_TAIL_MASS`.

| DFID | Domain | Definition | Default For | Allowed When | Assumptions |
|---|---|---|---|---|---|
| THETA_TAIL_MASS | θ (Belief) | \(P(\theta \ge \tau)\) | Safety-adjacent claims | safety_adjacent: true (mandatory) | \(\tau\) pre-registered |
| THETA_MEAN | θ (Belief) | \(E[\theta]\) | Central tendency claims | safety_relevant: nil | Approx. symmetry |
| THETA_Q | θ (Belief) | \(Q(\alpha)\) | Robustness check | only as robustness check of THETA_TAIL_MASS | \(\alpha\) pre-registered |
| Z_LOGDET_VOL | z (State) | \(\frac{1}{2}\log\det\Sigma\) | Volume direction | GaussianFitness.pass=true | Gaussian approximation valid |
| Z_ENTROPY | z (State) | \(\frac{1}{2}\log((2\pi e)^d\det\Sigma)\) | Density direction | GaussianFitness.pass=true | Equivalent ordering to Z_LOGDET_VOL under Gaussian |
| Z_KNN_ENTROPY | z (State) | \(\hat H_{kNN}\) | Nonparametric fallback | GaussianFitness.pass=false | PCA reduction registered |
| PHI_SPECTRAL_GAP | φ (Network) | \(1-E[\lambda_2(W)]\) | Consensus/integration | row-stochastic \(W\) pre-registered | Influence matrix construction fixed |
| PHI_KL_DISPERSION | φ (Network) | \(E_{i\ne j}[KL(p_i\|p_j)]\) | Polarization/fragmentation | agent distributions accessible | Pairwise KL estimable |

### 1.1 Enforced hierarchy
- Safety-adjacent claim:
  - **Primary:** THETA_TAIL_MASS (mandatory)
  - **Robustness:** THETA_Q (only as robustness of tail mass)
  - **Forbidden:** THETA_MEAN
- Central tendency claim (`safety_relevant: nil`):
  - **Primary:** THETA_MEAN
  - **Optional robustness:** THETA_Q

### 1.2 Deterministic state routing
- If `GaussianFitness.pass=true`:
  - Volume: Z_LOGDET_VOL
  - Density: Z_ENTROPY
- If `GaussianFitness.pass=false` (R5 trigger):
  - Density: Z_KNN_ENTROPY
  - Volume: unavailable (`geometry_uncertain`)
  - Gaussian-based gates invalid until recalibrated

### 1.3 Network domain non-substitution rule
`PHI_SPECTRAL_GAP` and `PHI_KL_DISPERSION` are not interchangeable and must be pre-registered before first evaluation.

---

## 2) Estimator Catalog

Estimator choice is deterministic by domain and Gaussian fitness status.

| Estimator ID | Domain | Method | Allowed When | Fallback Of |
|---|---|---|---|---|
| THETA_MC_1D | θ | Monte Carlo KL (1D KDE) | low-dim, nonparametric prior | primary |
| THETA_ANALYTIC | θ | Analytic KL (Beta/Normal) | known parametric form | preferred when valid |
| Z_GAUSS_KL_LW | z | Gaussian KL + Ledoit-Wolf covariance | GaussianFitness.pass=true | canonical |
| Z_LOGDET_LW | z | \(\log\det\Sigma_{LW}\) via Cholesky | GaussianFitness.pass=true | used inside Z_GAUSS_KL_LW |
| Z_KNN_ENTROPY | z | kNN entropy on PCA-reduced space | GaussianFitness.pass=false | fallback of Z_GAUSS_KL_LW |
| PHI_SPECTRAL | φ | eigendecomposition of row-stochastic \(W\) | \(W\) available | primary for spectral gap |
| PHI_KL_DISP | φ | pairwise KL over agent states | state distributions accessible | primary for KL dispersion |

### 2.1 Canonical z-domain pipeline
1. Matched-n subsampling (required; seeded; repeated)
2. Ledoit-Wolf covariance estimation for full and minus-i sets
3. Shrinkage artifact check: flag FM-1 if ratio > 0.25 or sign flips
4. Output averaging over repeats: KL(z), \(\Delta V\), volume, entropy
5. Numerical fallback: increment shrinkage floor up to 3 retries; else `geometry_degenerate`

### 2.2 GaussianFitness gate
Run before z-estimation:
- T1: max projection excess kurtosis > 1.0 (flag)
- T2: bimodality coefficient > 0.555 (flag)
- T3: PCA residual ratio > 0.15 (flag)

If flags >= 2 ⇒ `GaussianFitness.pass=false` (R5 trigger), else pass.

### 2.3 kNN entropy fallback
When Gaussian fails:
- PCA to \(d'\) with explained variance >= 0.85
- kNN entropy with k=5
- bootstrap CI width test; unstable estimates block slice-level entropy gates

### 2.4 Network estimators
- `PHI_SPECTRAL`: return spectral gap, second eigenvalue, full spectrum
- `PHI_KL_DISP`: mean pairwise KL; cap/subsample if agents > 50

---

## 3) RunManifest (Authoritative Record)

A release cannot proceed without schema-valid RunManifest.

### 3.1 Identity & reproducibility (required)
- run_id
- model_hash
- dataset_fingerprints
- config_hash
- created_at
- replay_command

### 3.2 Direction registration
- theta_default_safety: THETA_TAIL_MASS
- tail_tau (pre-registered)
- optional central dfid: THETA_MEAN
- robustness check: THETA_Q + alpha
- network dfids + W construction method

### 3.3 State estimation fields
- layer selection, token selector
- matched_n=true (mandatory)
- repeats >= 3 (default 5)
- matched_n_seed
- shrinkage_floor >= 0.01
- shrinkage_artifact_ratio_max (default 0.25)

### 3.4 GaussianFitness thresholds
Defaults:
- excess_kurtosis_max=1.0
- bimodality_coeff_max=0.555
- pca_residual_ratio_max=0.15
- projection_count=64
- pca_rank=128
- min_variance_explained=0.85

> All threshold overrides require `override_reason`.

### 3.5 Hotspot selection
- rule: fraction_of_total
- defaults: \(\rho_\theta=0.15, \rho_z=0.10, \rho_\phi=0.15\)

### 3.6 Regime policy
- persistent R5 logic
- mandatory nonparametric routing on R5
- unresolved R2/R4/R6/R7 blocking switches

### 3.7 Verification thresholds
- Tail thresholds by event class (`critical/elevated/standard`)
- epsilon thresholds for volume, entropy, calibration, conflict, asymmetry, adaptation, dispersion
- confidence_level=0.95
- matched_n_repeats=5

### 3.8 Calibration section
- feature set selection
- held-out fingerprint
- forecast model
- thresholds_frozen_at must precede evaluation
- theta-only fallback explicitly flagged

---

## 4) Verification Checklist (Machine-Enforceable)

A claim is verified only if all applicable checklist rows pass. Baseline is always pre-intervention run on the same matched slice.

Core intervention checks include:
- R2 resolution: volume increase and/or entropy increase without tail worsening
- R4 resolution: controlled volume decrease without collapse
- calibration improvement on frozen holdout
- conflict reduction without creating new regime failures
- R6 mitigation via asymmetry drop, adaptation increase, dispersion drop
- R7 resolution via dispersion reduction, spectral gap increase, cluster collapse

### 4.1 Tail risk worsening (formal)
\[
\Delta_{tail}=P_{post}(\theta\ge\tau)-P_{pre}(\theta\ge\tau)
\]
`tail_worsens=true` if absolute or relative threshold exceeds manifest bounds.

### 4.2 R6 VolGap non-criterion
VolGap is structural and **must not** be treated as R6 mitigation success.

### 4.3 R2→R4 transition guard
All R2 interventions must be evaluated for overshoot into R4 and blocked/reverted when triggered.

### 4.4 Non-negotiable calibration gate
Must pass Brier/AUC/tail reliability, held-out hash match, and frozen-threshold timing.

---

## 5) Known DCS Pipeline Failure Modes

- **FM-1 Shrinkage artifact:** instability across matched-n repeats; mitigate with repeats, shrinkage floor, PCA; if unresolved, block z-gates.
- **FM-2 Slice leakage:** LOO underestimation due to neighboring slice similarity; mitigate with partitioning/orthogonalization and conservative reporting.
- **FM-3 Agent protocol confound:** gains disappear across message protocol variants; treat protocol as explicit unit and require invariance.
- **FM-4 R5 substantive signal:** persistent non-Gaussian geometry is evidence, not merely estimator failure; open causal investigation ticket and keep R5 unresolved until investigation completes.

---

## 6) Release Gate Summary

Blocking gates:
- GATE-REPRO
- GATE-CAL
- GATE-TAIL
- GATE-R2
- GATE-R4
- GATE-R5
- GATE-R6
- GATE-R7
- GATE-FM
- GATE-LEDGER

`GATE-REPRO` is non-negotiable. Non-reproducible artifacts are not releasable.

---

## 7) What Comes Next (Priority Ordered)

1. **Operator Playbook wiring**: map interventions directly to GATE IDs and manifest fields.
2. **Unit implementation contracts**: complete `apply/remove/perturb`, domain effects, and direction bindings.
3. **Example magnitude calibration**: ground epsilon defaults in representative model runs.
4. **Multi-agent manifest extension**: formalize agent graph construction, row-stochastic W normalization, and AdaptRate logging.

Items 1→2 should be sequential. Items 3 and 4 can proceed in parallel.

---

## 8) What Still Needs to Be Covered and Refined

This section defines the remaining work to move from a locked specification to a deployment-ready, audit-grade implementation.

### 8.1 Schema-complete machine validation
- Publish an explicit JSON Schema (or equivalent) for RunManifest with:
  - enum constraints for DFIDs/estimators/gates,
  - required-field assertions by claim class,
  - conditional logic (`if safety_adjacent=true then DFID=THETA_TAIL_MASS`),
  - strict override policy (`override_reason` non-empty when defaults changed).
- Add schema-version migration policy (`manifest_version`, compatibility guarantees, deprecation windows).

### 8.2 Reference implementation parity checks
- Add canonical test vectors for each estimator (theta, z, phi domains).
- Add deterministic seed/replay tests for matched-n and kNN fallback.
- Add cross-implementation parity checks (e.g., Python reference vs production runtime).

### 8.3 Quantitative threshold calibration package
- Provide empirical calibration appendix for all epsilon defaults:
  - `epsilon_V_min`, `epsilon_H_min`, `epsilon_H_CI_max`, and tail thresholds by event class,
  - expected ranges under benign, borderline, and failure regimes,
  - sensitivity/ablation curves and confidence intervals.
- Require dataset fingerprints and calibration provenance in the manifest.

### 8.4 Multi-agent manifest extension (formal)
- Add required fields for:
  - agent graph construction method,
  - CommInf edge normalization to row-stochastic \(W\),
  - AdaptRate collection windowing,
  - cluster assignment method and persistence criteria.
- Add invariance test requirements across protocol variants to operationalize FM-3 gating.

### 8.5 Audit trail and cryptographic integrity
- Add signed manifest + signed result bundle requirements (hash chain + timestamping).
- Define tamper-evident storage policy for:
  - raw inputs,
  - intermediate estimator outputs,
  - final gate decisions.
- Add re-audit replay procedure proving decision reproducibility from hashes only.

### 8.6 Human-operator safety constraints
- Map each gate failure to a deterministic operator runbook action:
  - block/revert/escalate actions,
  - mandatory evidence artifacts,
  - maximum allowed manual intervention scope.
- Add rule that narrative justification cannot override gate failures.

### 8.7 Evidence-quality and external validity boundaries
- Define minimum sample adequacy criteria by domain before certification claims are allowed.
- Add domain-transfer policy clarifying when thresholds are portable vs re-registration required.
- Add explicit “unsupported claim classes” list to prevent overreach in release notes.

### 8.8 Statistical robustness expansions
- Add multiplicity policy across all simultaneously evaluated units/slices/gates.
- Add posterior predictive checks and residual diagnostics for theta-domain models.
- Add uncertainty propagation rules from estimator instability to final gate confidence.

### 8.9 Completion criteria for Section III lock
Section III should be considered fully operational only when all of the following are true:
1. Manifest schema validator is released and CI-enforced.
2. Estimator test vectors and replay tests pass in CI.
3. Threshold calibration appendix is published with provenance.
4. Multi-agent extension fields are integrated and validated.
5. Signed audit bundle replay succeeds end-to-end.

---

## Appendix A — AUF Investor/Publication Qualification Notes

This dossier includes an explicit qualification framework:
- Deepfreeze rank reduction and entropy-loss behavior verified in controlled settings.
- DCS v1 CDF-gap form is degenerate for large N and must be replaced by KL-surprise formulation.
- LLM-scale validation and adversarial evaluation remain required for strong deployment claims.
- Structural metrics and theorem statements should be presented with explicit limitations where proofs/large-scale tests remain pending.

---

## Appendix B — METIS/CODES-2 Program Context

Included as project context:
- CODES-2 simulation package, reproducibility checks, and scaling-analysis workflow.
- Honest framing on simulation bounds vs physical instantiation.
- Recommended publication path: open code, explicit limitations, prospective validation, workshop submission.

---

**Author:** Devin Earl Atchley  
**Release:** Section III machine-enforceable spec (v0.4 locked)

# Section A execution plan (185 synthetic runs, this VM)

**Status:** plan only — awaiting owner's proceed binary. Nothing below has executed.
**Source of truth:** `docs/paper/experiment_matrix.md` (run total corrected 179 → 185, commit e2abd9f).
**Runner pattern:** same as `scripts/run_v3_matrix.sh` — `moe_control.cli`
hydra overrides, run dirs immutable under a new paper output root
(e.g. `docs/control_experiment_results/paper_runs/`), pre-registered
predictions committed to git before the first run.

## Phase 0 — pre-computation (before any run)

1. Compute `X_seed` in float64 via `v3_notes/predict_flip_time.py`
   for S-T1a seeds {17,23,42,101,7} and the S-T1d small_batch affinity
   tensors (seeds {17,42,101}); commit to git.
2. Compute `X_seed(gamma) = X_seed(1)/gamma²` for S-T1b
   (gamma ∈ {0.5,1,2}, seeds {17,42,101}); commit to git.
3. Record SHA-256 of affinity batches for all paired rows
   (S-T2a, S-T2b, S-T3/S-T3′, S-F2c) — pairing must be exact.
4. Confirm `scripts/verify_findings.py` has the `paper` suite encoding
   each row's falsification criterion (matrix §F expects it).

## Phase 1 — flip-time law family (T1 core; kill-priority first)

| row | runs | config |
|-----|------|--------|
| S-T1a | 40 | shortage, requested, eta {0.02…0.6}, seeds {17,23,42,101,7}, 1200 steps |
| S-T1b | 27 | same, gamma {0.5,1,2}, seeds {17,42,101}, eta {0.05,0.2,0.4} |
| S-T1c | 18 | requested_leaky, delta {0.01,0.05}, seeds {17,42,101}, eta {0.05,0.2,0.4}, 1200 steps |
| S-T1d | 12 | small_batch (T=64), requested, seeds {17,42,101}, eta {0.05,0.1,0.2,0.4}, 800 steps |

## Phase 2 — gauge equivalence + phantom gradient

| row | runs | config |
|-----|------|--------|
| S-T2a | 5 paired | shortage, {requested, capacity_relative}, seeds {17,23,42,99,101}, eta 0.05, 800 steps |
| S-T2b | 6 paired | {admitted, admitted_centered} × (uniform mu: 3 seeds; nonuniform_target+hetero_balanced: 3 seeds), 800 steps |
| S-T3 | 5 | nonuniform_target + hetero_shortage, admitted, seeds {17,23,42,99,101}, 800 steps |
| S-T3′ | 5 paired | identical batch to S-T3 (SHA-256-paired), admitted_antiwindup |

## Phase 3 — failure regimes (negative-result robustness)

| row | runs | config |
|-----|------|--------|
| S-F1 | 8 | nonuniform_target: hetero_shortage admitted_centered (5 seeds) + hetero_balanced (3 seeds), 800 steps |
| S-F2a | 15 | demand_shift, bias_integral, bias_gamma {0.001,0.003,0.01,0.03,0.1}, seeds {17,42,101}, 1000 steps |
| S-F2b | 4 | adversarial_init, requested_leaky (delta 0.05), seeds {17,23,42,99}, 800 steps |
| S-F2c | 5 paired | adversarial_batches, {requested, requested_no_projection}, seeds {23,42,99,101,7}, 1000 steps |

## Phase 4 — empirical basin + attainability

| row | runs | config |
|-----|------|--------|
| S-ETA | 25 | demand_shift, requested, eta {0.03…10.0} × 3 seeds + {5.0,7.0} × 2 seeds, 1000 steps |
| S-NU | 10 | nonuniform_target + hetero_balanced, requested, 2000 steps, 5 seeds × eta {0.05,0.2} |
| S-PF | 0 | descriptive analysis of stored S-T1a per-step metrics (flips/window, settle time, cascade indicator) |

## Run discipline

- Row-level completion markers; resume from the last completed row
  (interruption is expected over ~a day of unattended VM time).
- Per-step metrics series recorded for every run (S-PF consumes S-T1a's).
- Verifier `paper` suite runs after each row; a failing check is a
  **finding**, not a bug to fix.
- v1/v2/v3 result docs stay immutable; paper artifacts are new files.

# Control experiment results: requested vs admitted feedback under capacity saturation

**Date:** 2026-10-11 (initial 16-run study; reproducibility and sensitivity
follow-up same day — see section 6)
**Protocol version:** 0.1.0
**Git commit:** `4e7c58f` for all published runs below (see section 6 for
provenance details)
**Scope:** synthetic control experiment only. No pretrained-router integration, no model
training, no downstream quality evaluation, no external-baseline study.

## 1. What was run

Three run batches, all E=8, K=2, T=1024, uniform target mu=1/8, gamma=1.0,
delta=0.0, CPU, deterministic mode:

| Batch | Runs | Steps | Seeds | Step sizes |
|---|---|---|---|---|
| Main matrix | 48 = 4 scenarios x 4 controllers x 3 seeds | 500 | 17, 23, 42 | eta = 0.05 (shared) |
| Shortage eta sweep | 16 = 4 controllers x 4 etas | 2000 | 17 | eta = 0.05, 0.1, 0.2, 0.4 (shared) |

Total: 64 published runs. Every scenario/controller/seed combination ran on the
identical affinity batch (the batch is a pure function of the scenario seed;
SHA-256 hashes match across controllers within each scenario and seed), so all
controller comparisons are paired.

Published artifacts: `docs/control_experiment_results/runs/<run_id>/` (committed
alongside this report; each holds `config.resolved.yaml`, `manifest.json`,
`metrics.parquet`, `summary.json`, `affinity_reference.json`).

Reproduce with (from the repo root, `.venv` active):

```bash
OUT=docs/control_experiment_results/runs
# main matrix, seed 17
for pair in "shortage shortage" "exact_total exact_total" "slack slack" "demand_shift shortage"; do
  set -- $pair
  python -m moe_control.cli scenario=$1 capacity=$2 \
    controller=requested,admitted,admitted_centered,capacity_relative \
    experiment.output_root=$OUT --multirun
done
# additional paired seeds
for sd in 23 42; do
  for pair in "shortage shortage" "exact_total exact_total" "slack slack" "demand_shift shortage"; do
    set -- $pair
    python -m moe_control.cli scenario=$1 capacity=$2 \
      controller=requested,admitted,admitted_centered,capacity_relative \
      experiment.seed=$sd scenario.seed=$sd experiment.output_root=$OUT --multirun
  done
done
# shortage step-size sweep, 2000 steps
for eta in 0.05 0.1 0.2 0.4; do
  python -m moe_control.cli scenario=shortage capacity=shortage \
    controller=requested,admitted,admitted_centered,capacity_relative \
    controller.step_size=$eta experiment.steps=2000 \
    experiment.output_root=$OUT --multirun
done
```

Regenerate the summary tables and run the findings verification from the
artifacts with:

```bash
python scripts/summarize_runs.py --runs-dir docs/control_experiment_results/runs
python scripts/verify_findings.py --runs-dir docs/control_experiment_results/runs
```

## 2. Run inventory

64 published runs in `docs/control_experiment_results/runs/`, named
`<timestamp>-saturation_signal_test-<scenario>-<controller>-<hex8>`:

- Main matrix: 4 scenarios x 4 controllers x seeds {17, 23, 42}, 500 steps
  (48 runs; the seed-17 block reproduces the original exploratory 16).
- Shortage eta sweep: 4 controllers x etas {0.05, 0.1, 0.2, 0.4}, 2000 steps,
  seed 17 (16 runs).

Each run directory carries its full provenance (`manifest.json` with git
commit, versions, device, seed, gauge-equivalence class; `config.resolved.yaml`;
`metrics.parquet`; `summary.json`; `affinity_reference.json`).

## 3. Results by scenario

Metrics used: `viol` = requested max violation `max_e |R_e/(KT) - mu_e|`;
`cv` = coefficient of variation of R; `ov` = total overflow `sum_e relu(R_e - C_e)`;
`prange` = pressure range `max_e q_e - min_e q_e` (min is always 0 by gauge
normalization). Saturation = fraction of steps with every `R_e >= C_e`.

### 3.1 Shortage (uniform C = 192; aggregate shortage KT - sum(C) = 512)

Initial condition verified against realized counts: every expert at or above
capacity at step 0 (`R = [300, 300, 270, 270, 240, 240, 214, 214]`).

| Controller | sat. frac | viol 0 -> 500 | ov 0 -> 500 | prange final |
|---|---|---|---|---|
| requested | 1.00 | 0.0215 -> 0.0215 | 512 -> 512 | 1.0498 |
| capacity_relative | 1.00 | 0.0215 -> 0.0215 | 512 -> 512 | 1.0498 |
| admitted | 1.00 | 0.0215 -> 0.0215 | 512 -> 512 | 0.0000 |
| admitted_centered | 1.00 | 0.0215 -> 0.0215 | 512 -> 512 | 0.0000 |

Findings:

- **Saturation-freeze confirmed exactly.** Under admitted feedback the per-step
  feedback vector is the constant `-0.03125` on every coordinate, i.e. exactly
  `(c-1)/E` with `c = 0.75`, as the formal document's theorem predicts. The gauge
  update then removes the common mode and pressure stays `[0]*8` for all 500
  steps: admitted feedback induces no relative pressure change while global
  saturation persists.
- **Requested feedback observes the imbalance.** Pressure differentiates steadily
  (range 0 -> 1.05 at `eta * range(feedback) = 0.05 * 0.042 = 0.0021` per step),
  with the pattern tracking the requested-load skew. The two feedback sources
  produce qualitatively different pressure states under identical saturation.
- **Counts do not move in 500 steps at eta = 0.05.** The Top-K flip threshold is
  set by the favorite-pair offsets (2.0/1.9); a pressure range of ~1.05 is not
  enough to displace any token's selection, so `R` is unchanged and the violation
  stays 0.0215. The pressure signal is observable, but routing is unchanged on
  this horizon and step size.
- **Overflow is fixed at 512 for every controller.** This equals the aggregate
  capacity shortage and cannot be reduced by any controller here; no overflow
  reduction is claimed in this regime.

### 3.2 Exact-total boundary (uniform C = 256; sum(C) = KT)

Balanced initial condition verified: `R_e = 256 = KT/E` for every expert at
step 0.

| Controller | sat. frac | viol 0 -> 500 | ov 0 -> 500 | prange final |
|---|---|---|---|---|
| requested | 1.00 | 0.0000 -> 0.0000 | 0 -> 0 | 0.0000 |
| capacity_relative | 1.00 | 0.0000 -> 0.0000 | 0 -> 0 | 0.0000 |
| admitted | 1.00 | 0.0000 -> 0.0000 | 0 -> 0 | 0.0000 |
| admitted_centered | 1.00 | 0.0000 -> 0.0000 | 0 -> 0 | 0.0000 |

The `c = 1` boundary result holds: global saturation coincides with balanced
requested load, feedback is zero for all variants, and nothing moves. This is
the degenerate case the formal document identifies, and the experiment
reproduces it without exception.

### 3.3 Slack (uniform C = 288; aggregate surplus 256)

Initial: `R = [340, 340, 300, 300, 220, 220, 164, 164]` (viol 0.0449, cv 0.2675,
overflow 128). Saturation never holds globally (fraction 0.00), as designed:
some experts saturate while others stay below capacity.

| Controller | viol 0 -> 500 | min viol (step) | ov 0 -> 500 | first routing change | prange final |
|---|---|---|---|---|---|
| requested | 0.0449 -> 0.0215 | 0.0215 (442) | 128 -> 24 | step 344 | 1.8794 |
| capacity_relative | 0.0449 -> 0.0215 | 0.0215 (442) | 128 -> 24 | step 344 | 1.8794 |
| admitted | 0.0449 -> 0.0444 | 0.0444 (499) | 128 -> 125 | step 488 | 1.5136 |
| admitted_centered | 0.0449 -> 0.0444 | 0.0444 (499) | 128 -> 125 | step 488 | 1.5136 |

Findings:

- **Requested-direction controllers rebalance and cut overflow 128 -> 24.**
  Because aggregate capacity suffices here, this overflow reduction is legitimate:
  the formal document's Schur-convexity proposition says balanced requested load
  minimizes overflow, and the controller moves the system toward it
  (final `R = [267, 250, 300, 300, 220, 220, 244, 247]`).
- **Admitted-direction controllers are effectively frozen by censoring.**
  With `A_e = min(R_e, C_e)`, the two most overloaded experts report 288 instead
  of 340, so admitted feedback understates their excess by ~2.6x; the imbalance
  barely moves (0.0449 -> 0.0444) and overflow stays 128 -> 125. The first
  routing change comes 144 steps later than under requested feedback.
- Rebalancing is slow at this step size: the violation halves at step 442 of
  500. Step-size selection was fixed in advance (eta = 0.05 for all controllers),
  not tuned per controller.

### 3.4 Demand shift (affinity preferences flip at step 250; C = 192)

Pre-shift behavior matches the shortage scenario (saturation 1.00, overflow
fixed 512). At step 250:

- Requested counts flip affinity-first:
  `[300, 300, 270, 270, 240, 240, 214, 214]` ->
  `[214, 214, 240, 240, 270, 270, 300, 300]`.
- The pressure state is preserved exactly across the shift
  (`pressure_before[250] == pressure_after[249]`, verified in the artifacts).

Post-shift (steps 250-499), requested/capacity_relative:

- The stale pressure pattern (high on experts 0 and 1, range 0.52) unwinds to
  range 0.02 over the remaining 250 steps while a new pattern forms on the
  newly over-requested experts (final pressure `[0.024, 0.024, 0, 0, 0, 0,
  0.024, 0.024]`). The controller dismantles the outdated pressure rather than
  carrying it forward, because post-shift feedback is negative exactly on the
  previously overloaded coordinates.
- Admitted/admitted_centered pressure stays `[0]*8` throughout (freeze persists
  under saturation on both sides of the shift).

## 4. Cross-cutting checks

- **Gauge equivalence holds empirically.** Requested vs capacity_relative produce
  bit-identical pressure trajectories and feedback vectors (the centered
  feedback equals the requested feedback exactly under uniform capacity/target).
  Admitted vs admitted_centered produce pressure trajectories identical up to
  floating-point rounding (max coordinate difference 4.9e-14 over all steps in
  the slack runs; bit-identical in the degenerate frozen runs), with feedback
  differing only by a common-mode component. Under the uniform capacity/target
  regime used here these are not independent findings; the run manifests record
  the equivalence classes.
- **Paired comparisons verified.** Affinity SHA-256 content hashes are identical
  across the four controllers within each scenario and seed.
- **Determinism.** Same seed reproduces identical trajectories.
  Deterministic algorithms were enabled; runs are CPU float32/float64 as
  recorded in each manifest.

## 5. What these results do and do not show

- The core formal predictions reproduce: saturation freeze under admitted
  feedback (constant `(c-1)/E` feedback, zero relative pressure change),
  requested feedback observing the censored imbalance, the `c = 1` boundary
  degeneracy, and the gauge equivalences between controller variants.
- In the slack regime, requested-direction feedback rebalances load and reduces
  overflow where admitted-direction feedback stalls. In the shortage regime,
  overflow is fixed by aggregate shortage for all controllers and no reduction
  is claimed.
- The step-size sweep (section 6) answers the open question from the initial
  study: with a longer horizon, requested feedback does change routing in the
  shortage regime (violation 0.0215 -> 0.0000 at eta >= 0.1), while admitted
  feedback stays frozen at every step size.
- Limitations: three seeds (not a statistical study); shared step-size sweep
  only in the shortage regime; synthetic affinities only; no oscillation was
  observed in any run's tail, but long-horizon cycling is not ruled out in
  general. Convergence behavior remains an empirical matter the formal document
  does not settle.
- No pretrained-router, training, or downstream-quality experiments were run;
  those are later phases per the architecture plan.

## 6. Reproducibility and sensitivity follow-up

### 6.1 Provenance

The initial 16 runs were executed against uncommitted implementation files.
All 64 published runs were regenerated from the clean commit `4e7c58f` into
`docs/control_experiment_results/runs/` and are committed alongside this
report. Manifests record `dirty=true` for all but the first run; the dirt
consists solely of the runs' own untracked output directories — no tracked
file differs from `4e7c58f` (`git status` shows no `M` entries), and the first
reproduction run records `dirty=false`. The seed-17 reproduction matches the
original findings exactly (see `scripts/verify_findings.py`: all checks pass
on the published artifacts).

`scripts/verify_findings.py` encodes the headline findings (F1 saturation
freeze, F2 gauge equivalence, F3 slack contrast, F4 demand-shift mechanics, F5
paired batches) as per-(scenario, seed) checks. Two of its expectations needed
calibration during this follow-up, both in the direction the formal document
requires: the admitted_centered freeze check now asserts the feedback differs
from admitted feedback by a common-mode vector only (it is `[0]*8`, not
`(c-1)/E`, under saturation), and the gauge-equivalence check uses a 1e-9
tolerance instead of bit-equality for non-degenerate trajectories (float
rounding, max observed diff 4.9e-14).

### 6.2 Seed robustness (seeds 17, 23, 42; 500 steps; eta = 0.05)

All headline findings replicate across the three paired seeds:

| Scenario | Finding | seed 17 | seed 23 | seed 42 |
|---|---|---|---|---|
| shortage | admitted pressure frozen at `[0]*8` | yes | yes | yes |
| shortage | requested pressure range final | 1.05 | 1.05 | 1.05 |
| slack | requested overflow 128 -> | 24 | 22 | 23 |
| slack | admitted overflow 128 -> | 125 | 124 | 125 |
| slack | requested first routing change (step) | 344 | 339 | 349 |
| slack | admitted first routing change (step) | 488 | 460 | 461 |
| exact_total | violation stays 0.0000 | yes | yes | yes |
| demand_shift | pressure preserved across shift | yes | yes | yes |

### 6.3 Shortage step-size sweep (2000 steps, seed 17, shared etas)

Separating pressure response, routing changes, overflow, and oscillation:

| eta | Controller | first routing change | viol 0 -> 2000 | overflow | prange final | viol range, last 500 steps |
|---|---|---|---|---|---|---|
| 0.05 | requested / capacity_relative | step 703 | 0.0215 -> 0.0068 | 512 fixed | 1.83 | 0.00098 |
| 0.05 | admitted / admitted_centered | never | 0.0215 -> 0.0215 | 512 fixed | 0.00 | 0.00000 |
| 0.10 | requested / capacity_relative | step 352 | 0.0215 -> 0.0000 | 512 fixed | 1.82 | 0.00000 |
| 0.10 | admitted / admitted_centered | never | 0.0215 -> 0.0215 | 512 fixed | 0.00 | 0.00000 |
| 0.20 | requested / capacity_relative | step 176 | 0.0215 -> 0.0000 | 512 fixed | 1.82 | 0.00000 |
| 0.20 | admitted / admitted_centered | never | 0.0215 -> 0.0215 | 512 fixed | 0.00 | 0.00000 |
| 0.40 | requested / capacity_relative | step 88 | 0.0215 -> 0.0005 | 512 fixed | 1.82 | 0.00000 |
| 0.40 | admitted / admitted_centered | never | 0.0215 -> 0.0215 | 512 fixed | 0.00 | 0.00000 |

Findings:

- **Requested feedback changes routing in the shortage regime given enough
  horizon.** At eta = 0.1 and 0.2 the requested load balances exactly
  (`R = [256]*8`, violation 0.0000) while global saturation persists
  (every `R_e >= 192` at every step). The 500-step horizon at eta = 0.05 was
  simply too short: pressure was moving the right way but had not crossed the
  Top-K flip threshold.
- **First-flip step scales inversely with eta** (703, 352, 176, 88;
  `eta x step ~= 35.2` in all four cases): the pressure needed to displace a
  token's Top-2 selection is fixed by the affinity structure, so doubling the
  step size halves the time to the first routing change. The settled pressure
  pattern is eta-independent (final range ~1.82 in all cases).
- **No step size rescues admitted feedback.** It stays exactly frozen
  (pressure `[0]*8`, no routing change in 2000 steps) at every eta, because the
  feedback is exactly constant under saturation and eta only scales the
  common-mode component the gauge projection removes.
- **Overflow is fixed at 512 throughout the sweep** for every controller and
  step size: rebalancing redistributes the fixed rejected mass, it cannot
  reduce it. No overflow reduction is claimed here.
- **No oscillation observed.** At eta >= 0.1 the violation is exactly constant
  over the final 500 steps. At eta = 0.05 the final-window range is 0.00098
  (= 2/2048) from two single-token routing changes, both downward (the window
  minimum equals the final value), so the run is still settling toward balance,
  not oscillating. A longer horizon would be needed to see eta = 0.05 settle.

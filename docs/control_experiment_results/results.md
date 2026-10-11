# Control experiment results: requested vs admitted feedback under capacity saturation

**Date:** 2026-10-11
**Protocol version:** 0.1.0
**Git commit:** `a8eca05e` (all 16 runs; implementation files uncommitted, as instructed)
**Scope:** synthetic control experiment only. No pretrained-router integration, no model
training, no downstream quality evaluation, no external-baseline study.

## 1. What was run

16 runs: 4 scenarios x 4 controllers, 500 control steps each, one seed.

| Setting | Value |
|---|---|
| Experts E / Top-K / tokens T | 8 / 2 / 1024 |
| Target mu | uniform 1/8 |
| Pressure gain gamma | 1.0 |
| Step size eta | 0.05 |
| Pressure decay delta | 0.0 |
| Seed | 17 (Python, NumPy, PyTorch; deterministic algorithms on) |
| Device | CPU, float32 affinities, float64 pressure |

Every scenario/controller pair ran on the identical affinity batch (the batch is a
pure function of the scenario seed; SHA-256 hashes match across controllers within
each scenario), so controller comparisons are paired.

Reproduce with (from the repo root, `.venv` active):

```bash
for pair in "shortage shortage" "exact_total exact_total" "slack slack" "demand_shift shortage"; do
  set -- $pair
  python -m moe_control.cli scenario=$1 capacity=$2 \
    controller=requested,admitted,admitted_centered,capacity_relative --multirun
done
```

Per-step data lives in `results/runs/<run_id>/metrics.parquet`; regenerate the
tables below from the artifacts with:

```bash
python scripts/summarize_runs.py
```

## 2. Run inventory

All runs below have 500 steps and seed 17.

| Scenario | Controller | Run ID |
|---|---|---|
| shortage | requested | 20261011-074228-saturation_signal_test-shortage-requested-821665e6 |
| shortage | admitted | 20261011-074229-saturation_signal_test-shortage-admitted-68de3e87 |
| shortage | admitted_centered | 20261011-074229-saturation_signal_test-shortage-admitted_centered-a49a7850 |
| shortage | capacity_relative | 20261011-074229-saturation_signal_test-shortage-capacity_relative-5987e6e8 |
| exact_total | requested | 20261011-074239-saturation_signal_test-exact_total-requested-048328e6 |
| exact_total | admitted | 20261011-074239-saturation_signal_test-exact_total-admitted-68cc70ca |
| exact_total | admitted_centered | 20261011-074240-saturation_signal_test-exact_total-admitted_centered-d3aa0498 |
| exact_total | capacity_relative | 20261011-074240-saturation_signal_test-exact_total-capacity_relative-e06bc1c0 |
| slack | requested | 20261011-074245-saturation_signal_test-slack-requested-95cd3f5d |
| slack | admitted | 20261011-074246-saturation_signal_test-slack-admitted-6efd116b |
| slack | admitted_centered | 20261011-074246-saturation_signal_test-slack-admitted_centered-13b1bb54 |
| slack | capacity_relative | 20261011-074246-saturation_signal_test-slack-capacity_relative-af706a7d |
| demand_shift | requested | 20261011-074251-saturation_signal_test-demand_shift-requested-02cf5c02 |
| demand_shift | admitted | 20261011-074251-saturation_signal_test-demand_shift-admitted-ab522968 |
| demand_shift | admitted_centered | 20261011-074252-saturation_signal_test-demand_shift-admitted_centered-c7b56fc4 |
| demand_shift | capacity_relative | 20261011-074252-saturation_signal_test-demand_shift-capacity_relative-1764f4c6 |

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
  bit-identical pressure trajectories and feedback vectors; admitted vs
  admitted_centered produce identical pressure trajectories with feedback
  differing only by a common-mode component. Under the uniform capacity/target
  regime used here these are not independent findings; the run manifests record
  the equivalence classes.
- **Paired comparisons verified.** Affinity SHA-256 content hashes are identical
  across the four controllers within each scenario.
- **Determinism.** Same seed reproduces identical trajectories (requested vs
  capacity_relative runs are independent executions with identical output).
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
- Limitations: single seed (no statistical claims); one fixed step size
  (eta = 0.05, no sweep, so the 500-step horizon is too short to flip routing in
  the shortage regime); 500-step horizon only; synthetic affinities only.
  Convergence, cycling, or long-horizon behavior is an empirical matter the
  formal document does not settle, and these runs do not settle it either.
- No pretrained-router, training, or downstream-quality experiments were run;
  those are later phases per the architecture plan.

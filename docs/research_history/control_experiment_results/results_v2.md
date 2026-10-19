# Hardened control experiments v2: windup, adversarial demand, and the bias-controller head-to-head

**Date:** 2026-10-11
**Protocol version:** 0.2.0
**Branch:** `feat/control-experiment-v2-hardened`
**Scope:** synthetic deterministic closed-loop control experiments only. No
pretrained-router integration, no model training, no downstream quality
evaluation. The trained-model transfer experiment is explicitly out of scope
(see section 8 for why it is the bar for belief).

This report extends the v1 study (`docs/research_history/control_experiment_results/results.md`,
protocol 0.1.0, 64 runs). v1 artifacts under `runs/` are frozen and untouched;
all v2 runs live under `docs/research_history/control_experiment_results/v2_runs/`.

## 1. Motivation

The literature review (`docs/research_history/literature_reviews/moe_routing_load_balancing.md`)
identifies the sharpest theoretical claim available to this project: under
capacity saturation, admitted-direction feedback suffers the equivalent of
classical integrator windup — admitted load stops reflecting demand while
saturated, so a controller integrating it builds state from a censored signal —
while requested-direction feedback avoids windup by construction. The review
also demands: (a) a head-to-head against DeepSeek's aux-loss-free bias
controller (a pure sign-based integral controller, the closest deployed
method), not a strawman; (b) ablations isolating the leak `(1-delta)` and the
gauge projection; (c) adversarial demand (collapsed initializations, bursty
shifts, small batches); (d) a specialization probe, because the SimBal result
(balance metrics can anti-correlate with model quality) makes balance-only
evaluation untrustworthy; (e) a gain-sensitivity (thrash) map.

## 2. What was run

93 published runs, E=8, K=2, uniform target mu=1/8, gamma=1.0, CPU,
deterministic mode. Every scenario/controller/seed combination ran on the
identical affinity batch (SHA-256 content hashes match across controllers
within each scenario and seed; verifier check W6), so all controller
comparisons are paired.

| Batch | Runs | Steps | Seeds |
|---|---|---|---|
| Head-to-head: 5 scenarios x 7 controllers x 2 seeds | 70 | 800-1200 | 17, 23 |
| Pressure eta sweep (demand_shift) | 9 | 1000 | 17 |
| Bias gamma sweep (demand_shift, shortage + exact_total) | 14 | 1000 | 17 |

Controllers: `requested`, `admitted`, `admitted_centered`,
`capacity_relative` (v1 four), plus `bias_integral` (DeepSeek-style sign-based
per-expert bias, gamma=0.001, added to scores for Top-K selection only,
updated from ADMITTED counts outside autograd — see manifest notes), plus two
ablations: `requested_leaky` (delta=0.05, isolates the leak) and
`requested_no_projection` (identity instead of gauge projection, isolates the
projection).

Scenarios (all deterministic, seeded):
- `saturation_windup` (1200 steps): base skew [300,270,240,214], demand spike
  [600,300,80,44] on steps [400,800) saturating experts 0-3 at tight capacity
  C=256 (c=1.0), then release to base. Records overshoot/oscillation after
  release.
- `adversarial_init` (800 steps): expert 0 dominant for every token (+3.0
  offset; R_0=T=1024 at step 0), capacity C=192. Rich-get-richer escape test.
- `adversarial_batches` (1000 steps): near-identical token affinities
  (preference_gap=0.15, noise=0.01) with the favored expert pair re-permuted
  every 100 steps, capacity C=256. Bursty tracking test.
- `specialization_probe` (800 steps): planted skill blocks with unbalanced
  skill sizes [400,300,200,124], capacity C=192. Per-step mutual information
  between skill label and top-1 expert assignment is recorded.
- `small_batch` (800 steps): T=64 tokens/step, capacity C=12 (c=0.75). Load-
  estimate noise stress.

Reproduce with `bash scripts/run_v2_matrix.sh` (from repo root, `.venv`
active). Analyze with `scripts/analyze_v2.py`; verify with
`scripts/verify_findings.py --suite v2 --runs-dir
docs/research_history/control_experiment_results/v2_runs` (all checks pass; the v1 suite is
unaffected).

## 3. Saturation windup: the requested/admitted dissociation, confirmed

Seed 17 (seed 23 in parentheses):

| Controller | viol at spike end (step 799) | post-release overshoot | final viol |
|---|---|---|---|
| requested / capacity_relative / no_projection | 0.0215 (0.0215) | +0.046 (+0.048) | 0.0068 (0.0063) |
| admitted / admitted_centered | 0.1245 (0.1191) | +0.040 (+0.035) | 0.0063 (0.0020) |
| bias_integral | 0.1655 (0.1660) | -0.0005 (-0.0005) | 0.0010 (0.0015) |
| requested_leaky | 0.1680 | +0.0000 | 0.0215 |

During the spike, requested-direction rebalances fully (viol 0.0215 at spike
end) while admitted-direction stalls at 0.12 (its feedback is censored on the
saturated experts: A_e=C_e is constant, so excess demand R_e-C_e is invisible).
This is the predicted dissociation, and it replicates on both seeds (verifier
W2). The bias controller, which also observes admitted counts, stalls the same
way (0.166) — and more slowly, since gamma=0.001 moves the bias at most 0.4
over the 400-step spike.

Precision on the "windup" framing: what we observe is censored-feedback
**under-correction during saturation**, not unbounded integrator growth — with
c=1.0 the saturated feedback coordinate is exactly 0, so pressure does not
run away; it miscalibrates. Post-release transients are bounded for all
controllers (overshoot < 0.05 above the pre-spike baseline; verifier W2).
Classical unbounded windup would require a feedback sign that persists under
saturation; the gauge projection removes the constant component that would
otherwise accumulate.

## 4. Head-to-head: where each controller wins

**adversarial_init** (expert 0 starts at R_0=1024, viol 0.375):
- requested-direction escapes fully: viol 0.375 -> 0.0215, R_0 1024 -> 300
  (both seeds).
- admitted-direction stalls: viol -> 0.198, R_0 -> 661. Under global
  saturation its feedback is constant, so it is nearly blind; as R_0 falls
  below capacity it partially recovers but never escapes.
- bias_integral: viol -> 0.165, R_0 -> 594. Same censoring as admitted, plus
  the sign step is too slow for this timescale.
- requested_leaky: viol 0.375 -> 0.375, R_0 unchanged at 1024. **Completely
  frozen** — see section 6.

**adversarial_batches** (bursty, 100-step preference shifts):
- requested-direction rebalances between bursts but cannot track them:
  seed 17 ends at viol 0.125 (one expert empty), seed 23 at 0.0005. The outcome
  is seed-dependent because the controller's adaptation time (~300+ steps at
  eta=0.05) exceeds the burst period. A stateful integral controller optimizes
  time-averaged balance; instantaneous balance under 100-step shifts needs
  faster gains or a stateless per-batch method.
- admitted-direction and bias_integral barely move (final viol 0.33-0.38,
  overflow 768-1458 vs 2-256 for requested).

**small_batch** (T=64):
- requested-direction works, slowly: first routing change at step 657-687,
  viol 0.0234 -> 0.008-0.016.
- admitted-direction and bias_integral never move (first_change=None): global
  saturation (every R_e >= 12) makes admitted counts uniform, so both are
  exactly blind — the bias controller's saturation freeze, verified as a
  [note] in W4.

**specialization_probe** (skills [400,300,200,124], C=192):
- requested-direction reaches the overflow floor (648 -> 512, the minimum
  achievable since every expert must carry >= 192) at an MI cost:
  1.301 -> 1.060 (seed 17) / 1.071 (seed 23) nats.
- admitted-direction preserves MI perfectly (1.301 -> 1.301) but keeps
  overflow at 648 and viol at 0.0703.
- This is the Pareto frontier the review demanded: (overflow 512, MI ~1.06)
  vs (overflow 648, MI 1.30). Requested-direction finds the better balance
  point, but it does pay in specialization — balance by partial smearing.
  Whether that trade is acceptable is a model-quality question this harness
  cannot answer (section 8).

## 5. Thrash mapping: stability boundaries

Demand shift at step 250, 1000 steps. Classification on the final 200 steps:
inert (never moved), converged (flat tail), settling, oscillating
(>=20 direction changes), thrash (final viol > 2x init or > 0.4).

**Pressure (requested), eta over 0.001 -> 10 (4 orders):**

| eta | class | final viol | tail osc |
|---|---|---|---|
| 0.001 - 0.03 | inert | 0.0215 | 0 |
| 0.1, 0.3 | settling/converged | 0.0078, 0.0015 | 0 |
| 1.0, 3.0 | converged | 0.0005, 0.0020 | 0 |
| 10.0 | **thrash (limit cycle)** | 0.0215 | 143 |

**Bias (exact_total, uncensored), gamma over 1e-4 -> 0.1:**

| gamma | class | final viol | tail osc |
|---|---|---|---|
| <= 0.001 | inert | 0.0215 | 0 |
| 0.003 - 0.03 | converged **with chatter** | 0.0015 - 0.0088 | 132 - 198 |
| 0.1 | degraded | 0.0396 (> init) | 132 |

(On shortage capacity the bias sweep is uninformative — global saturation
censors it at every gamma — which is itself a finding about its operating
envelope.)

The pressure controller has a wide clean basin (eta 0.1-3.0, over an order of
magnitude, zero tail oscillation); the bias controller's working band is
narrower and it chatters (100+ tail direction changes) even when converging —
the sign-based update keeps flipping marginal tokens every step, the
DeepSeek gamma-too-large mode appearing already at moderate gains. At
eta=10 the pressure controller enters a genuine limit cycle (tail range
0.099, viol swinging to 0.13).

## 6. Ablations: the leak can be fatal, the projection is numerical hygiene

**requested_leaky (delta=0.05).** The leak imposes a pressure ceiling: at
steady state, delta*q = eta*gamma*eps, so q* = (eta*gamma/delta)*eps. With
eta=0.05, gamma=1, delta=0.05, the ceiling is |eps| itself. Consequences
observed:
- adversarial_init: ceiling 0.375 on expert 0, but diversion needs q_0 > ~1.0
  (dominant offset 3.0 vs group offset 2.0). The controller converges to
  q_0=0.467 and **never diverts a single token** (R_0=1024 at step 799).
- small_batch: ceiling |eps|~0.047, below the score noise floor (0.1) — the
  controller is permanently inert (first_change=None).
- saturation_windup: pressure range during spike only 0.27 (vs 2.0 for the
  pure integrator); it rides out the spike without reacting.
The leak is not a mild regularizer here: when the required correction exceeds
(eta*gamma/delta)*|eps|, or when |eps| is below the selection margin, the
leaky controller is provably stuck. Forgetting helps track changing demand
only when the leak timescale 1/delta is matched to the demand timescale; a
mismatched leak is worse than none.

**requested_no_projection (identity).** Routing is bit-identical to
`requested` in 9 of 10 scenario-seed pairs, confirming the formal prediction
that routing depends only on the gauge class. In the 10th
(adversarial_batches seed 23), 46 of 1000 steps show single-token flips from
floating-point near-ties: without gauge fixing, common-mode drift (~-0.7)
interacts with float32 score arithmetic at the Top-K boundary. The violation
trajectories are bit-identical (max |diff| = 0), so no scientific conclusion
changes — but the projection is doing real work as numerical hygiene, not
just mathematical bookkeeping. (Verifier W3 encodes both halves of this.)

## 7. Separation of pressure, routing, overflow, oscillation, specialization

- **Pressure:** requested-direction builds large, fast pressure (range ~2.0
  during spike); admitted-direction builds miscalibrated pressure from
  censored signals; the leak caps pressure at (eta*gamma/delta)*|eps|; the
  bias moves at most gamma/step.
- **Routing:** requested-direction changes routing earliest and most
  (first_change step 5 on batches, 219-687 elsewhere); admitted-direction
  changes little or never under saturation; bias_integral changes routing
  only when uncensored and slowly.
- **Overflow:** fixed by aggregate shortage where saturated (512 in
  shortage/windup-tight regimes — no controller reduces it there);
  reducible to its floor 512 in specialization_probe only by requested-
  direction (admitted-direction leaves 648).
- **Oscillation:** no limit cycles for pressure at eta <= 3.0; genuine
  limit cycle at eta=10 (tail_osc=143); bias chatters (tail_osc 132-198)
  at all working gains; post-release transients are bounded, not
  oscillatory, for pressure controllers.
- **Specialization:** MI 1.301 -> 1.060/1.071 (seeds 17/23) for
  requested-direction on the probe
  (balance at partial smearing cost); preserved at 1.301 by frozen
  controllers that also fail to rebalance.

## 8. Limitations (read before citing)

1. **No trained-model transfer.** Per the literature review's central caution
   (SimBal: near-perfect balance metrics with worse perplexity), nothing here
   implies the pressure controller trains a better model. The minimum bar for
   belief is a small LM trained with (a) top-k + aux loss, (b) DeepSeek-style
   bias control, (c) the best pressure variant at matched FLOPs, reporting
   validation perplexity — not run here (needs training infrastructure).
2. Synthetic affinities, fixed E=8/K=2, CPU, no wall-clock comparison.
3. The bias head-to-head uses the faithful DeepSeek default gamma=0.001;
   the sweep shows its working band is 0.003-0.03 on uncensored demand —
   the head-to-head flatters requested-direction on timescale, which the
   thrash map corrects.
4. Two seeds per scenario for v2 (three for v1); seed-dependence was observed
   (adversarial_batches 0.125 vs 0.0005), so seed-averaged claims are weak.
5. No convergence is proven; "settling"/"converged" are operational
   descriptions of finite trajectories.
6. The inference story (frozen vs reset vs per-sequence pressure) is
   unspecified and untested.

## 9. Files

- Runs: `docs/research_history/control_experiment_results/v2_runs/` (93 runs; each with
  `config.resolved.yaml`, `manifest.json`, `metrics.parquet`, `summary.json`,
  `affinity_reference.json`; manifests record protocol 0.2.0 and
  controller-specific notes).
- Analysis: `scripts/analyze_v2.py`; verification:
  `scripts/verify_findings.py --suite v2`; matrix:
  `scripts/run_v2_matrix.sh`.
- New code: `src/moe_control/controllers/base.py` (bias_integral),
  `src/moe_control/scenarios/hardened.py` (4 scenarios),
  `src/moe_control/metrics.py` (overshoot, settling_time,
  oscillation_count, specialization_mi), `src/moe_control/dynamics/gauge.py`
  (projection switch), `src/moe_control/runner.py` (score sign, projection,
  per-step MI), `src/moe_control/config.py` + `configs/` (new groups).

# Utmost-version control experiments v3: non-uniform targets, anti-windup, theorem, DeepSeek head-to-head, trained-router probe

**Date:** 2026-10-11
**Protocol version:** 0.3.0
**Branch:** `feat/control-experiment-v3-utmost`
**Scope:** synthetic deterministic closed-loop control experiments only,
plus a toy trained-router *feasibility probe* (explicitly not evidence --
see section 9). No pretrained-router integration, no model training for
belief, no downstream quality evaluation.

This report extends v1 (`results.md`, protocol 0.1.0, 64 runs) and v2
(`results_v2.md`, protocol 0.2.0, 93 runs). v1 artifacts under `runs/`
and v2 artifacts under `v2_runs/` are frozen and untouched (verifier
check V3-IMM confirms byte-identity via git); all v3 runs live under
`docs/control_experiment_results/v3_runs/` (79 runs). Every
scenario/controller/seed combination ran on the identical affinity batch
(SHA-256 content hashes match across controllers within each scenario and
seed; verifier V3-PAIR), so all controller comparisons are paired.
Within v3, every declared comparison group shares one identical affinity
batch: verifier V3-PAIR enforces the exact expected controller set for
each declared (scenario, capacity-regime, seed) group -- T1's 6-controller
matrix, T5's requested-vs-bias_integral pairs, the T3 freeze-retest pair --
and fails loudly on any undeclared group, so no comparison is vacuously
"paired". Declared singleton groups (T2 probe runs, T4 prospective runs,
T3 eta sweeps) are asserted as exactly those singletons; the T3 leaky
retest shares its batch with the T5 seed-42 pair and is declared as that
full group.
The T2 antiwindup runs additionally share their affinity batch with the
v2 runs of the same scenario and seed (cross-suite hash check in V3-PAIR),
so the antiwindup-vs-v2 comparisons are paired too; T3 eta sweeps share
the batch across etas.

Reproduce with `bash scripts/run_v3_matrix.sh` (from repo root, `.venv`
active). Verify with `scripts/verify_findings.py --suite v3 --runs-dir
docs/control_experiment_results/v3_runs` (164 checks, all pass; the v1
and v2 suites are unaffected and still pass).

## 1. What was run

79 runs, E=8, K=2, T=1024 (except small_batch T=64), gamma=1.0, CPU,
deterministic mode.

| Track | Runs | Design |
|---|---|---|
| T1 non-uniform target | 36 = 2 capacity regimes x 6 controllers x seeds {17, 23, 42} | explicit feasible integer-count target K*T*mu = [384, 352, 320, 288, 256, 224, 128, 96]; heterogeneous capacities hetero_balanced (sum C = KT = 2048) and hetero_shortage (sum C = 1536); 800 steps |
| T2 anti-windup | 10 = 5 v2 scenarios x seeds {17, 23} | new `admitted_antiwindup` controller (conditional integration) on saturation_windup (1200 steps), adversarial_init, adversarial_batches, specialization_probe, small_batch |
| T3 claim re-verification | 11 | flip-invariant: shortage x requested x etas {0.05, 0.1, 0.2, 0.4} x seeds {23, 42} (1200 steps); freeze retest: shortage x {requested, admitted} x seed 99 (500 steps); requested_leaky x adversarial_init x seed 42 (800 steps) |
| T4 theorem prospective | 2 | shortage x requested x etas {0.15, 0.3} x seed 17 (1200 steps); predictions committed *before* these runs executed |
| T5 DeepSeek head-to-head | 20 = 2 controllers x 5 scenarios x seeds {42, 99} | requested vs bias_integral; v2 already covered seeds 17, 23, giving 4-seed paired statistics |

Controllers: the v1 four (`requested`, `admitted`, `admitted_centered`,
`capacity_relative`), `bias_integral` (DeepSeek-style), plus the new
**`admitted_antiwindup`** (section 3). The v2 ablations
(`requested_leaky`, `requested_no_projection`) appear only in the T3
leaky retest.

## 2. T1: non-uniform targets and heterogeneous capacities

Motivation (reviewer's proposal): v1/v2 used uniform capacity and uniform
target throughout, a regime where (R)==(C) and (A)==(A0) on the gauge
quotient. T1 breaks both uniformities at once to test the controllers
where the equivalences fail.

Setup: explicit target mu with K*T*mu_e = [384, 352, 320, 288, 256, 224,
128, 96] (integers summing to 2048; each <= 1/K = 0.5, so the formal
necessary conditions for exact requested-load matching hold). Two
heterogeneous capacity regimes: hetero_balanced, C = [384, 320, 288, 256,
224, 192, 192, 192] (sum 2048, skewed); hetero_shortage, C = [300, 270,
240, 210, 180, 150, 120, 66] (sum 1536, aggregate c = 0.75, skewed).
Affinity group structure matches v1 ([300, 270, 240, 214]), so step-0
R = [300, 300, 270, 270, 240, 240, 214, 214] in every run (paired).

### 2.1 Exact balance is not attained; requested gets closest

No controller attains R == K*T*mu exactly in 800 steps on any seed or
regime (verifier T1-exact). The best any controller does is requested at
within 18 tokens of the target (final viol 0.0088, all 3 seeds, both
regimes); admitted reaches within 17-18 tokens on hetero_balanced only.
Whether the target is hard-Top-K-attainable at all is not established --
the formal necessary conditions (integer counts, mu <= 1/K) are not
sufficient, and this experiment does not resolve attainability.

### 2.2 Phantom gradient vs exact freeze (hetero_shortage)

Under global saturation (fraction 1.00 for requested/admitted/
admitted_antiwindup/capacity_relative on all seeds) with heterogeneous
capacity, the admitted signal is 100% censored -- and the two
admitted-direction controllers diverge exactly as the anti-windup design
predicts:

- `admitted` integrates the phantom gradient P_0(C/(K*T) - mu): pressure
  moves on 799/799 consecutive saturated step pairs, building range 1.484
  over 800 steps while routing stays frozen (viol constant 0.0576). The
  state is pure windup: 1.48 units of pressure built from a signal
  containing zero *current-demand* information -- it is independent of R
  while saturation persists, though it still encodes the target mu.
- `admitted_antiwindup` is exactly frozen: feedback `[0]*8` on all 800
  saturated steps, zero pressure movement (max step delta 0.0),
  bit-identical freeze.

This is the cleanest experimental dissociation of the design: same
censored signal, one controller hallucinates 1.48 units of state, the
other builds exactly 0.

### 2.3 admitted_centered diverges under heterogeneous capacity

`(A_0)` -- which the formal document presents as a valid variant,
gauge-equivalent to (A) only under uniform target -- is actively
destructive here. On hetero_shortage (all 3 seeds): viol 0.0576 ->
0.4106-0.4126, overflow 512 -> 1065-1072, saturation fraction collapsing
to 0.35-0.37. Final R e.g. [146, 143, 135, 135, 88, 238, 225, 938]
(seed 17): expert 7 (capacity 66) is driven to 938 requests. Mechanism:
(A_0) = P_0(A/(K*T)) ignores the target entirely and equalizes the
*censored* admitted load; under heterogeneous capacity that diverts
demand away from high-capacity experts onto low-capacity ones, more than
doubling overflow past the aggregate shortage. On hetero_balanced it is
worse than doing nothing (viol 0.0576 -> 0.088-0.091, overflow 122 ->
314-316). The v1 gauge equivalence is fragile: outside the
uniform/uniform regime, (A_0) optimizes the wrong objective.

### 2.4 hetero_balanced: no dominant controller (Pareto)

With sum(C) = KT but skewed capacities, balancing toward mu conflicts
with overflow minimization (the v1 Schur-convexity result required
uniform capacity). Final (viol, overflow), consistent across all 3 seeds:

| controller | viol | overflow | note |
|---|---|---|---|
| requested | 0.0088 | 151-152 | best violation; overflow *rises* 122 -> 152 |
| capacity_relative | 0.052-0.053 | 61-63 | best overflow; violation barely moves |
| admitted | 0.018-0.022 | 204-210 | moves on partially-censored signal; overflow rises |
| admitted_centered | 0.088-0.091 | 314-316 | worse than initial on both |
| admitted_antiwindup | 0.0576 | 122 | routing frozen; pressure integrates (range 0.66) but sub-flip-threshold |
| bias_integral | 0.060-0.064 | 136-155 | slightly worse than initial |

No controller achieves viol <= 0.01 and overflow <= 70 jointly
(verifier T1-pareto). Note the requested overflow increase is inherent
to the target, not a controller failure: the target itself demands
[384, 352, 320, 288, 256] on capacities [384, 320, 288, 256, 224], i.e.
the "feasible integer-count target" is count-feasible in the formal
sense but not capacity-feasible (sum of relu(target - C) = 160 > 122).

## 3. T2: the anti-windup controller -- honest verdict

**Design.** `admitted_antiwindup` (new, backward-compatible; `src/
moe_control/controllers/base.py`): a conditional-integration-inspired rule
on
the admitted signal. Per-coordinate saturation is R_e >= C_e; saturated
coordinates are frozen at the unsaturated mean before the zero-sum
projection (their relative feedback is exactly 0); unsaturated
coordinates integrate A_e/(K*T) - mu_e; global saturation gives epsilon
= 0 (full freeze). Reduction properties proved by unit test
(`scripts/check_antiwindup_unit.py`, all pass): unsaturated ->
gauge update bit-identical to (A) admitted; global saturation ->
epsilon = 0 while (A)/(A_0) integrate the phantom P_0(C/(K*T) - mu).

**Verdict: it does not beat requested / admitted / bias_integral on any
rebalancing metric.** It never beats requested on final violation in any
of the 10 scenario-seed pairs (verifier V3-T2). Head-to-head:

- saturation_windup: worst spike-end violation (0.1680 vs 0.1245/0.1191
  admitted, 0.0215 requested -- it refuses the censored signal while
  admitted exploits its ordinal content), but **zero post-release
  overshoot** (0.0000 vs +0.040/+0.048 for requested/admitted) and exact
  return to baseline (final 0.0215).
- adversarial_init: frozen on the dominant expert (viol 0.3750, R_0 =
  1024 unchanged) while admitted partially escapes (0.198) and requested
  fully escapes (0.0215). It diligently rebalances the *unsaturated*
  coordinates (experts 2-7 equalize toward ~120) but cannot touch the
  saturated coordinate that matters.
- adversarial_batches / specialization_probe / small_batch: frozen
  (0.3750 / 0.0703+648 / 0.0234), matching admitted -- when unsaturated
  coordinates carry no differential signal, conditional integration is a
  full freeze.

The conditional-integration-inspired fix prevents miscalibration but
cannot recover the
information censoring destroys -- it trades under-correction for
no-correction. The admitted controller's partial successes exploit
*ordinal* information in the censored signal (saturated = at least as
loaded as unsaturated) that pure conditional integration discards; the
uncensored requested signal remains the only thing that actually
rebalances. The design's unambiguous win is the T1 phantom-vs-freeze
dissociation (section 2.2): under fully-censored heterogeneous
saturation it builds exactly 0 state where admitted builds 1.48 units of
windup.

## 4. T3: claim-by-claim re-verification (all pass)

Each v1/v2 headline finding re-verified by a dedicated check; several on
fresh runs at new seeds, two with fully independent recomputation:

- **C1 saturation-freeze exactness:** v1 artifacts re-asserted (admitted
  feedback exactly -0.03125 = (c-1)/E, pressure `[0]*8`, all seeds) plus
  a fresh seed-99 retest (admitted frozen; requested pressure range
  1.05, matching the v1 seed 17/23/42 value).
- **C2 the 35.2 invariant:** see section 5 (theorem; 14/14 exact).
- **C3 requested_leaky adversarial_init failure:** v1/v2 artifacts
  (R_0 = 1024, viol = 0.3750 frozen, seeds 17/23) plus a fresh seed-42
  retest (still frozen).
- **C4 bias-integral chatter:** tail oscillation counts recomputed from
  the v2 thrash artifacts: 185/198/132 at gamma 0.003/0.01/0.03 (report:
  132-198), gamma=0.1 degraded (viol 0.0215 -> 0.0396).
- **C5 specialization Pareto:** overflow 648 -> 512 and MI 1.301 ->
  1.060/1.071 (seeds 17/23) for requested; admitted preserves MI 1.301
  and keeps overflow 648. The recorded MI was **independently
  recomputed** from the regenerated affinity tensor plus the recorded
  pressure_before series through a separate code path: agreement to
  < 1e-9 at step 0 and the final step on both seeds.
- **C6 pressure eta-basin edges:** v2 thrash artifacts: eta <= 0.03
  inert; eta 0.1/0.3/1.0/3.0 converge with zero tail oscillation;
  eta = 10 limit cycle (tail range 0.0991).
- **C7 sweep-tail no-oscillation:** v1 sweep artifacts: tail exactly
  flat at eta >= 0.1; eta = 0.05 tail range exactly 2/2048 = 0.00098 with
  window minimum equal to the final value (settling, not oscillating).

## 5. T4: the eta x first-flip-step theorem -- proved and verified 14/14

In the pre-flip linear regime (delta = 0, requested feedback, R
constant), pressure grows as q_t = t*eta*gamma*(eps - min(eps)) with eps
= R/(K*T) - mu (lemma, by induction; the gauge min-shift cancels in
score differences). The first Top-K flip over the batch is then exactly

    t_flip(eta) = ceil(X / eta),  X = min_{i,e,e'} (a_{i,e} - a_{i,e'})
                                                / (gamma^2 (eps_e - eps_e'))

a pure function of the affinity tensor and step-0 counts -- no dynamics
simulated. Full derivation, assumptions, and limits in
`v3_notes/eta_flip_theorem.md`. In particular: **"35.2" is
seed-17-specific** (X = 35.115/34.622/36.457 for seeds 17/23/42); the
seed-independent invariant is eta * t_flip = X_seed. Uniform capacity is
not actually required (capacity never enters pre-flip
requested-feedback dynamics).

The predictions were committed to git *before* the prospective runs
executed. Verification (verifier C2), all exact (|err| = 0):

| seed | X | eta=0.05 | 0.1 | 0.15 | 0.2 | 0.3 | 0.4 |
|---|---|---|---|---|---|---|---|
| 17 | 35.1151 | 703 | 352 | **235** | 176 | **118** | 88 |
| 23 | 34.6217 | 693 | 347 | 231 | 174 | 116 | 87 |
| 42 | 36.4574 | 730 | 365 | 244 | 183 | 122 | 92 |

Bold = prospective (predicted before any run existed at those etas):
observed 235 and 118, exact. The seed-23/42 columns are fresh-run
verification of the per-seed X. No convergence result is claimed: the
theorem covers only the linear pre-flip regime; post-flip cascades, the
eta <= 3.0 clean basin, and the eta = 10 limit cycle remain empirical.

## 6. T5: DeepSeek head-to-head, done properly (4 seeds)

requested vs bias_integral on the 5 v2 scenarios x seeds {17, 23} (v2
runs) + {42, 99} (new v3 runs): paired comparisons on identical affinity
batches, final-violation paired wins:

| scenario | requested (mean over 4 seeds) | bias_integral (mean) | paired wins |
|---|---|---|---|
| saturation_windup | 0.0067 | 0.0015 | bias 4-0 |
| adversarial_init | 0.0215 | 0.1653 | requested 4-0 |
| adversarial_batches | 0.0323 | 0.3746 | requested 4-0 |
| specialization_probe | 0.0112 | 0.0693 | requested 4-0 |
| small_batch | 0.0117 | 0.0234 | requested 4-0 |

Requested-direction wins 16/20 paired comparisons. The 4 bias wins are
all on saturation_windup final violation (bias 0.0010-0.0020 vs
requested 0.0063-0.0068, consistent across all 4 seeds) -- reported
honestly as a genuine bias win on that metric, with the counterweight
that its spike-end violation is ~8x worse (0.166 vs 0.0215, v2). The
adversarial_batches seed-dependence from v2 replicates (requested seed
17: 0.1250; seeds 23/42/99: 0.0005-0.0024).

## 7. Run manifest and duplicate detection

Every v3 run directory carries `config.resolved.yaml`, `manifest.json`
(git commit, protocol 0.3.0, gauge-equivalence class, controller notes),
`metrics.parquet`, `summary.json`, `affinity_reference.json`. Verifier
V3-DUP builds a canonical key from each resolved config and fails loudly
on any collision: 79 unique configs, zero duplicates.

## 8. Limitations (read before citing)

1. **Synthetic only.** All closed-loop results use synthetic affinities,
   E=8/K=2, CPU. Nothing here implies the pressure controller trains a
   better model; the SimBal caution stands.
2. **The anti-windup verdict is negative on rebalancing.** The rule is
   conditional-integration-inspired, faithfully implemented; the
   experiment shows its limits, not its triumph. Do not cite it as an
   improvement over requested/admitted on balance metrics.
3. **(A_0) divergence is regime-specific.** It holds for heterogeneous
   capacity and/or non-uniform target; under uniform/uniform it is
   gauge-equivalent to (A) and harmless (v1). The fragility is the
   finding, not a general indictment.
4. **Exact balance unattained.** The 18-token gap may be attainability,
   horizon, or step size; not disentangled.
5. **Seeds.** Three seeds for T1/T2, four for T5; seed-dependence was
   observed (adversarial_batches), so seed-averaged claims stay weak.
6. **No convergence proven** beyond the pre-flip theorem; post-flip
   behavior is empirical finite-horizon description.
7. **The toy trained-router probe (section 9) is feasibility only** and
   must not be cited as trained-model evidence.

## 9. Track 3: toy trained-router feasibility probe

**Verdict: GO on feasibility, NO-GO as belief-grade evidence.**
Estimate written before any compute; smoke test
(`v3_notes/trained_router_smoke.py`, 3 conditions x 300 steps, 8-expert
MLP MoE + learned top-2 router, CPU) ran in **17.7 s wall-clock**,
inside the 15-minute budget. The real `RequestedFeedback` controller
balances the learned router (viol 0.018-0.035, ~4-5x lower than the
aux-loss baseline's 0.09-0.15) at matched task loss (0.233 vs 0.229)
and accuracy (0.902 vs 0.922). Full detail and pre-stated verdict
criteria in `v3_notes/trained_router_feasibility.md`. The bar for
belief remains a small LM at matched FLOPs reporting validation
perplexity -- beyond this VM's scope.

## 10. Files

- Runs: `docs/control_experiment_results/v3_runs/` (79 runs).
- This report: `docs/control_experiment_results/results_v3.md` (draft).
- Notes: `docs/control_experiment_results/v3_notes/` (theorem + proof
  script, feasibility estimate + verdict, smoke test, T1/T2/T5 analyses).
- Verification: `scripts/verify_findings.py --suite v3` (164 checks);
  unit checks `scripts/check_antiwindup_unit.py`; matrix
  `scripts/run_v3_matrix.sh`.
- New code: `src/moe_control/controllers/base.py`
  (`AdmittedAntiwindupFeedback`), `src/moe_control/config.py`
  (DictConfig `values`-key collision fix), `configs/controller/
  admitted_antiwindup.yaml`, `configs/scenario/nonuniform_target.yaml`,
  `configs/capacity/{hetero_balanced,hetero_shortage}.yaml`.

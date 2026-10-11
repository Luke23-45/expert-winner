# Experiment Matrix: feedback control for capacity-limited MoE routing

**Status:** evaluation spec (draft, pre-registration). Branch
`feat/paper-feedback-moe-routing`. This document is the complete,
runnable specification of the paper's evidence plan. Nothing in it is
evidence yet — it is the *plan* against which evidence will be judged.

**Track A dependency:** `docs/paper/formal_core.md` does not exist yet
(the theorist is writing it in parallel). Rows below are marked
`[Track A: proved in v3_notes]` where the statement already has a proof
on record (`docs/control_experiment_results/v3_notes/eta_flip_theorem.md`),
and `[Track A: pending confirmation]` where the formal statement the row
tests lives with the theorist. A pending row may run, but its verdict
language must stay provisional until Track A lands.

## 0. Standing rules (non-negotiable)

1. **Evidence tiers are labeled in every claim.** `SYNTHETIC` =
   deterministic closed-loop harness, fixed affinities, CPU.
   `TRAINED-TINY` = learned router on a synthetic task (debug/mechanics
   only — never model-quality evidence). `TRAINED-LM` = small language
   model at matched FLOPs reporting validation perplexity — the only
   tier that can support a model-quality claim. A sentence that omits
   its tier is a defect.
2. **Matched budgets everywhere.** Every controller comparison in
   Section B runs on identical data, identical training-token budget,
   identical architecture, and an identical *tuning* budget
   (same number of hyperparameter trials × same token sub-budget;
   selection criterion pre-registered). A controller that got more
   tuning than its rival proves nothing.
3. **Uncertainty is mandatory.** No single-seed claims. Every reported
   number is mean ± std over ≥3 seeds, or a 95% CI; paired comparisons
   on identical affinity batches / data shards where the harness allows
   it (the v1–v3 SHA-256 batch-pairing discipline carries over).
4. **Pre-registration.** Quantitative predictions (Section A) are
   committed to git *before* the runs they predict execute — the
   mechanism v3 T4 used (`predict_flip_time.py` on regenerated affinity
   tensors, no run artifacts touched). A prediction written after the
   run is a description, not a test.
5. **Falsification criteria are part of the row.** A row without a
   stated observation that would break it is not in the matrix.
6. **The SimBal lesson governs Section B.** Balance-metric wins do not
   imply model-quality wins (v3 literature review §c: SimBal itself
   *improves* perplexity over the load-balance loss, 8.304 vs 8.517 —
   the "balance trap" example was the LBL baseline inside SimBal's
   comparison, not SimBal). The pre-registered primary metric for every
   trained comparison is **validation perplexity** (downstream tasks
   secondary); routing metrics are diagnostics, not objectives.
7. **Frozen history.** `docs/control_experiment_results/runs/`,
   `v2_runs/`, `results.md`, `results_v2.md` stay byte-identical.
   v3 (`results_v3.md`, `v3_runs/`) is exploratory groundwork: its
   numbers may motivate rows but no paper claim rests on v3 alone —
   every load-bearing finding gets a fresh pre-registered run in this
   matrix.

**Scenario/controller vocabulary** (inherited from v1–v3, unchanged):
scenarios `shortage`, `exact_total`, `slack`, `demand_shift`,
`saturation_windup`, `adversarial_init`, `adversarial_batches`,
`specialization_probe`, `small_batch`, `nonuniform_target`
(hetero_balanced: sum C = KT = 2048 skewed; hetero_shortage: sum C =
1536, aggregate c = 0.75, skewed); controllers `requested` (R),
`admitted` (A), `admitted_centered` (A₀), `capacity_relative` (C),
`bias_integral` (DeepSeek-style sign integrator, bias_gamma = 0.001 =
DeepSeek-V3 value), `admitted_antiwindup` (AW, conditional-integration),
ablations `requested_leaky` (delta = 0.05), `requested_no_projection`.
Unless stated otherwise: E = 8, K = 2, T = 1024, gamma = 1.0, delta =
0, deterministic CPU, seeds drawn from {17, 23, 42, 99, 101, 7, 11}
(fresh seeds 101/7/11 reserved for rows needing generalization beyond
v1–v3's seed pool).

---

## A. Synthetic theorem-testing matrix (runs on this VM)

Each row: theorem tested → exact configuration → quantitative
prediction (pre-registered) → falsification criterion → Track A status.
`X_seed` below is computed per seed in float64 from the regenerated
affinity tensor by `v3_notes/predict_flip_time.py` *before* any run at
that seed executes.

### S-T1a. The flip-time law (core theorem)

- **Theorem:** T1 — `t_flip(eta) = ceil(X / eta)`, X a pure function of
  the affinity tensor + step-0 counts; pre-flip linear regime,
  assumptions delta = 0, requested feedback, gamma symbolic.
  `[Track A: proved in v3_notes/eta_flip_theorem.md]`
- **Config:** scenario `shortage`, uniform capacity C = 192
  (`configs/capacity/shortage.yaml`), uniform target mu = 1/8,
  controller `requested`, delta = 0, gamma = 1.0, seeds
  {17, 23, 42, 101, 7} (101/7 fully fresh), eta grid
  {0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6}, 1200 steps.
  5 × 8 = **40 runs**.
- **Prediction (pre-registered):** observed first-flip step
  `t_obs = ceil(X_seed / eta) ± 2` (the ±2 is the float32-vs-float64
  tolerance from the theorem note §4; empirically v1 matched exactly).
  Additionally `eta * t_obs ∈ [X_seed, X_seed + eta)` per seed.
- **Falsification:** any seed/eta with `|t_obs − ceil(X_seed/eta)| > 2`;
  or `X_seed` recomputed from the regenerated tensor disagreeing with
  the committed value (would mean X is not the claimed pure function).
- **v3 status:** exploratory data exists (14/14 exact, §5 of
  results_v3.md); this row is the pre-registered generalization to
  fresh seeds and a wider eta grid.

### S-T1b. Gamma-scaling boundary of T1

- **Theorem:** T1 keeps gamma symbolic: `X ∝ 1/gamma²`. v3 verified
  only gamma = 1. `[Track A: proved in v3_notes (symbolic); numeric
  extension pending confirmation]`
- **Config:** as S-T1a, gamma ∈ {0.5, 1.0, 2.0}, seeds {17, 42, 101},
  eta ∈ {0.05, 0.2, 0.4}. 3 × 3 × 3 = **27 runs**.
- **Prediction:** `t_obs = ceil(X_seed(gamma) / eta) ± 2` with
  `X_seed(gamma) = X_seed(1) / gamma²`, each pre-computed in float64
  before runs.
- **Falsification:** systematic deviation scaling with gamma
  (e.g. gamma = 2 law holds but gamma = 0.5 breaks) — would localize a
  hidden gamma assumption in the induction step.

### S-T1c. Leak boundary of T1 (assumption stress)

- **Theorem:** T1 assumes delta = 0; the note (§1) asserts a leak breaks
  linearity (pressure asymptotes to `(eta·gamma/delta)·eps`).
  `[Track A: pending confirmation — the asymptotic form is asserted in
  the note, not proved]`
- **Config:** as S-T1a, controller `requested_leaky` with delta ∈
  {0.01, 0.05}, seeds {17, 42, 101}, eta ∈ {0.05, 0.2, 0.4}, 1200 steps.
  2 × 3 × 3 = **18 runs**.
- **Prediction:** `t_obs` deviates from `ceil(X_seed/eta)` beyond the
  ±2 tolerance on a majority of (delta, seed, eta) cells, in the
  direction of *later-or-never* flips (leak caps pressure growth);
  at delta = 0.05 and eta = 0.05 the first flip is predicted to not
  occur within 1200 steps on at least 2/3 seeds.
- **Falsification (of the boundary claim):** the clean `ceil(X/eta)`
  law surviving with delta = 0.05 — would mean the leak does not break
  linearity as asserted and the theorem's assumption is vacuous.

### S-T1d. Small-batch boundary of T1

- **Theorem:** the note (§"Where a proof was NOT achieved") states T1
  does not cover small_batch; T = 64 changes the affinity tensor,
  hence X. `[Track A: pending confirmation]`
- **Config:** scenario `small_batch` (T = 64), `requested`, seeds
  {17, 42, 101}, eta ∈ {0.05, 0.1, 0.2, 0.4}, 800 steps.
  3 × 4 = **12 runs**.
- **Prediction:** the law holds with X recomputed from the small_batch
  affinity tensor: `t_obs = ceil(X_seed^T64 / eta) ± 2`
  (pre-registered per seed).
- **Falsification:** failure of the recomputed law — would show the
  small-batch regime breaks something beyond the affinity tensor
  (e.g. count-quantization interacting with the gauge projection).

### S-T2a. Gauge equivalence: requested == capacity_relative

- **Theorem:** T2 — (R) == (C) under uniform C (gauge equivalence:
  identical routing trajectories). `[Track A: pending confirmation]`
- **Config:** scenario `shortage`, uniform capacity C = 192, controller
  pair {`requested`, `capacity_relative`}, seeds {17, 23, 42, 99, 101},
  eta = 0.05, 800 steps. **5 paired runs**.
- **Prediction:** pressure trajectories identical to float tolerance
  (max |Δq| ≤ 1e-9 all steps); routing metrics (viol, overflow,
  per-step R) bit-identical.
- **Falsification:** any step with max |Δq| > 1e-6, or any routing
  divergence — would break the gauge-equivalence claim outright.
- **v3 status:** v1 established this; v3 did not re-test. Fresh,
  tighter assertion (per-step pressure equality, not just final
  metrics).

### S-T2b. Gauge equivalence: admitted vs admitted_centered, iff uniform mu

- **Theorem:** T2 — (A) gauge-equivalent to (A₀) *iff* mu uniform.
  `[Track A: pending confirmation]`
- **Config:** two sub-cases. (i) uniform mu: scenario `shortage`,
  uniform C, pair {`admitted`, `admitted_centered`}, seeds {17, 42,
  101}, 800 steps — **3 paired runs**, prediction: trajectories
  identical (max |Δq| ≤ 1e-9). (ii) non-uniform mu: scenario
  `nonuniform_target` + hetero_balanced, same pair and seeds —
  **3 paired runs**, prediction: trajectories *differ*
  (max |Δq| > 0.01 by step 800; routing violations differ by > 0.02).
- **Falsification:** (i) any divergence under uniform mu breaks the
  equivalence; (ii) coincidence under non-uniform mu breaks the
  "only-if" direction.

### S-T3. Phantom gradient under full saturation

- **Theorem:** T3 — under full saturation, admitted feedback =
  P₀(C/(KT) − mu): blind to current excess R − C, but still a function
  of C and mu. `[Track A: pending confirmation]`
- **Config:** scenario `nonuniform_target` + hetero_shortage
  (saturation fraction 1.00 on all v3 seeds), controller `admitted`,
  seeds {17, 23, 42, 99, 101}, 800 steps. **5 runs**.
- **Prediction (pre-registered):** on every step with saturation
  fraction = 1.00, feedback vector equals P₀(C/(KT) − mu) to 1e-9;
  pressure range accumulates monotonically (v3: 1.484 over 800 steps —
  predict range ∈ [1.2, 1.8] as a sanity band, exact value
  seed-dependent and pre-computable); routing frozen (final viol =
  initial viol ± 0.001).
- **Falsification:** feedback deviating from the phantom gradient during
  full saturation; or pressure *not* accumulating while routing is
  frozen (would deny the windup mechanism, not just its size).

### S-T3′. Anti-windup exact freeze (dissociation)

- **Design claim:** `admitted_antiwindup` under global saturation gives
  feedback exactly 0 and zero pressure movement (conditional
  integration), vs admitted's phantom windup on the identical batch.
  `[Track A: pending confirmation of the reduction properties; unit
  tests in scripts/check_antiwindup_unit.py already encode them]`
- **Config:** identical batch to S-T3 (paired via SHA-256 affinity
  hash), controller `admitted_antiwindup`, same 5 seeds, 800 steps.
  **5 runs**.
- **Prediction:** feedback `[0]*8` on all saturated steps; max pressure
  step-delta exactly 0.0 (bit-identical freeze); routing identical to
  step-0 throughout.
- **Falsification:** any nonzero pressure movement under global
  saturation — the "exact freeze" is an exact claim and any violation
  breaks it.

### S-F1. admitted_centered divergence (failure regime)

- **Failure condition:** F1 — (A₀) diverges under heterogeneous C +
  non-uniform mu (v3: viol 0.058 → 0.41, overflow 512 → 1065+,
  expert driven to ~938 vs capacity 66). Regime-specific: harmless
  under uniform/uniform (v1). `[Track A: pending confirmation —
  mechanism story is empirical]`
- **Config:** (i) scenario `nonuniform_target` + hetero_shortage,
  controller `admitted_centered`, seeds {17, 23, 42, 99, 101},
  800 steps — **5 runs**. (ii) boundary: same scenario +
  hetero_balanced, seeds {17, 42, 101} — **3 runs**.
- **Prediction:** (i) final viol ∈ [0.35, 0.45] (v3: 0.4106–0.4126),
  final overflow ≥ 1000 (v3: 1065–1072), max expert load ≥ 800 with
  capacity 66 on ≥4/5 seeds. (ii) final viol ∈ [0.07, 0.12]
  (v3: 0.088–0.091) — worse than initial 0.0576 but not catastrophic;
  overflow ∈ [250, 400] (v3: 314–316).
- **Falsification:** (i) viol staying ≤ 0.10 or overflow ≤ 600 on any
  seed — the divergence fails to replicate; (ii) viol *improving*
  below initial on hetero_balanced — would contradict the
  worse-than-nothing boundary finding.
- **Design note:** this row tests a *negative* result's robustness.
  If (i) replicates, (A₀) is excluded from all trained comparisons
  except as a documented negative control on the heterogeneous arm.

### S-F2a. bias_integral chatter (relay limit cycle)

- **Failure condition:** F2 — sign-based integral control chatters:
  v2/v3 tail direction changes 132–198 at working gains; gamma = 0.1
  degraded. Mechanism: relay nonlinearity → limit cycle (Åström–
  Hägglund; v3 literature review §a.2). `[Track A: pending confirmation
  — mechanism mapping is synthesis, not proved]`
- **Config:** scenario `demand_shift`, controller `bias_integral`,
  bias_gamma ∈ {0.001 (DeepSeek-V3 deployed value), 0.003, 0.01,
  0.03, 0.1}, seeds {17, 42, 101}, 1000 steps. 5 × 3 = **15 runs**.
- **Prediction:** tail (last 200 steps) direction-change count ∈
  [100, 250] at gamma ∈ {0.001, 0.003, 0.01, 0.03} on ≥7/9 runs;
  gamma = 0.1 shows degraded final violation (≥ 1.5× the gamma = 0.01
  value) with *fewer* direction changes (large-step thrash, not
  chatter). Non-monotone gain→chatter relationship.
- **Falsification:** clean convergence (≤ 10 tail direction changes)
  at any working gain 0.001–0.03 — would contradict the relay-chatter
  mechanism; or a monotone gain→chatter curve — would contradict the
  predicted inert/chatter/degraded three-regime structure.

### S-F2b. requested_leaky dead-zone (σ-modification tradeoff)

- **Failure condition:** F2 — leak caps pressure below the diversion
  threshold: `requested_leaky` (delta = 0.05) frozen on
  adversarial_init (v1/v2: R₀ = 1024, viol = 0.3750). Classical
  σ-modification tradeoff (v3 lit review §a.3).
  `[Track A: pending confirmation]`
- **Config:** scenario `adversarial_init`, controller
  `requested_leaky` (delta = 0.05), seeds {17, 23, 42, 99}, 800 steps.
  **4 runs**.
- **Prediction:** frozen: final R₀ = 1024 ± 0, final viol = 0.3750 ±
  0.001, on all 4 seeds; pressure range asymptotes (range over last
  200 steps ≤ 0.05).
- **Falsification:** escape on any seed (final viol < 0.20) — would
  break the dead-zone mechanism story.

### S-F2c. Gauge projection as numerical hygiene

- **Finding:** v2 — `requested_no_projection` routing bit-identical to
  `requested` in 9/10 pairs; the 10th (adversarial_batches seed 23)
  showed 46/1000 single-token flips from float32 near-ties as
  common-mode drift (~−0.7) interacted with Top-K boundary arithmetic;
  violation trajectories bit-identical regardless.
  `[Track A: pending confirmation]`
- **Config:** scenario `adversarial_batches`, pair {`requested`,
  `requested_no_projection`}, seeds {23, 42, 99, 101, 7}, 1000 steps.
  **5 paired runs**.
- **Prediction:** violation trajectories bit-identical (max |diff| =
  0) on all 5; ≥1 pair shows ≥10 single-token routing flips
  attributable to common-mode drift (|sum(q)| > 0.3 coinciding with
  flip steps); zero flips when |sum(q)| < 0.05.
- **Falsification:** violation divergence (max |diff| > 0) on any pair
  — would promote the projection from hygiene to load-bearing; or
  flips occurring with no common-mode drift — would break the
  attributed mechanism.

### S-ETA. The eta basin (open empirical — NOT a theorem)

- **Status:** v2/v3 observation only: eta ≤ 0.03 inert; eta ∈
  {0.1, 0.3, 1.0, 3.0} converge with zero tail oscillation; eta = 10
  limit cycle (tail range 0.0991). No convergence result is claimed
  anywhere. `[Track A: n/a — explicitly empirical]`
- **Config:** scenario `demand_shift`, controller `requested`, eta ∈
  {0.03, 0.05, 0.1, 0.3, 1.0, 3.0, 10.0}, seeds {17, 42, 101},
  1000 steps. 7 × 3 = **21 runs**.
- **Prediction:** eta = 0.03: max pressure range over 1000 steps <
  0.05 (inert). eta ∈ {0.1, 0.3, 1.0, 3.0}: final viol ≤ 0.03 and
  zero tail oscillation (tail range = 0 exactly over last 200 steps)
  on ≥10/12 runs. eta = 10: sustained oscillation, tail range ∈
  [0.05, 0.15] (v3: 0.0991).
- **Falsification:** oscillation (tail range > 0.01) at any eta ≤ 3.0
  — breaks the basin; convergence (tail range < 0.01) at eta = 10 —
  breaks the limit-cycle claim. Either outcome is publishable: the
  basin edges are currently just numbers.
- **Sharp edge to probe:** eta = 3.0 vs 10.0 leaves the transition
  unmapped; add eta ∈ {5.0, 7.0} × seeds {17, 42} = **4 runs**,
  prediction: transition to oscillation occurs in (3.0, 10.0],
  direction of first crossing recorded, no quantitative prediction
  (genuinely unknown).

### S-NU. Non-uniform exact-balance attainability (open question)

- **Status:** v3 T1 found no controller attains R == KT·mu exactly in
  800 steps (best: requested within 18 tokens, viol 0.0088); the
  18-token gap is unattributed (attainability vs horizon vs step
  size). `[Track A: pending — attainability conditions are the
  theorist's open problem]`
- **Config:** scenario `nonuniform_target` + hetero_balanced,
  controller `requested`, seeds {17, 23, 42, 99, 101}, 2000 steps
  (2.5× v3 horizon), eta ∈ {0.05, 0.2}. 5 × 2 = **10 runs**.
- **Prediction:** viol stays > 0.005 at step 800 on all runs
  (replicating v3); the 2000-step question is open — record whether
  viol ≤ 0.001 is ever sustained for ≥200 steps.
- **Falsification (of "unattainable"):** sustained viol ≤ 0.001 —
  would show the gap was horizon/step-size, and the formal
  attainability question gets an empirical answer in the positive
  direction. **Non-falsification is also a result:** persistent gap at
  2000 steps + a smaller-eta arm strengthens the attainability
  doubt honestly.

### S-PF. Post-flip cascade characterization (open empirical)

- **Status:** the theorem covers only the pre-flip linear regime;
  post-flip cascades are unproved and undescribed. `[Track A: n/a]`
- **Config:** no new runs — analyze stored per-step metrics from
  S-T1a trajectories (R_t, q_t series already recorded).
- **Measurements (pre-registered):** flips per 100-step window after
  t_flip; time from first flip to viol < 0.02 (settle time); whether
  ≥2 flips occur within 50 steps of the first (cascade indicator);
  correlation of cascade depth with eta.
- **Falsification:** n/a (descriptive). **Kill criterion:** if
  post-flip behavior shows no eta-dependence distinguishable from
  seed noise across the 40 trajectories, report that plainly and do
  not manufacture a cascade narrative.

**Section A run total:** 40 + 27 + 18 + 12 + 5 + 6 + 5 + 5 + 8 + 15 +
4 + 5 + 21 + 4 + 10 = **179 runs** (S-PF reuses S-T1a artifacts: 0 new).
At v3 pace (79 runs, CPU, minutes each including analysis) this is a
few hours of wall-clock on this VM, dominated by analysis scripting,
not compute.

---

## B. Trained-MoE experiments

### B.0 What each scale is and is not

| scale | what it is | evidence tier | model-quality claims? |
|---|---|---|---|
| S0 tiny | 8-expert MLP MoE, learned top-2 router, synthetic 8-class task, **with capacity + token dropping** (new vs the v3 smoke test), CPU | TRAINED-TINY | **No.** Debug/mechanics only: does the trained loop (router co-adapting with pressure state, dropping under saturation) run without errors and produce jointly measurable loss + balance + overflow. |
| S1 paper | ~180M-total / ~50M-active decoder-only LM MoE, 8 experts top-2, 10B tokens FineWeb-Edu | TRAINED-LM | **Yes — this is the belief tier.** |
| S2 large (optional) | ~1B-total / ~300M-active, 16 experts top-2, 50B tokens | TRAINED-LM | Yes; only if S1 shows a real effect worth scaling. |

### B.1 S0 — tiny trained probe (this VM, DEBUG ONLY)

- **Model/task:** v3 smoke design, extended: E = 8 experts, each
  MLP(16→32→8) + ReLU; router Linear(16→8); top-2; output =
  softmax-weighted sum of selected experts' logits; 8-class Gaussian
  clusters (std 1.0, centers on circle radius 4), input dim 16.
  **New:** per-expert capacity C with canonical dropping, so the
  requested/admitted distinction exists (the smoke test had no
  capacity). Batch T = 256, Adam lr = 3e-3.
- **Conditions:** (a) aux-loss baseline (0.01·E·Σ frac·prob);
  (b) `bias_integral` gamma = 0.001; (c) `requested` eta ∈ {0.3, 0.5},
  gamma = 1.0, no aux loss; (d) `admitted_antiwindup` eta = 0.5.
  Controllers imported from `moe_control.controllers` (real code, not
  reimplementation) — same discipline as the smoke test.
- **Capacity arms:** c ∈ {1.0 (saturation every step), 1.5} × uniform C.
- **Seeds:** 5. Steps: 3000. Total: 5 conditions × 2 arms × 5 seeds =
  **50 runs**, ~25–45 s each (smoke: 8–14 ms/step) → **~30–45 min**
  wall-clock on this VM.
- **Recorded:** CE loss, accuracy, requested viol, overflow/dropped
  tokens, |q| range, per-expert bias range (for bias_integral).
- **Success criterion (pre-registered, mechanics only):** all
  conditions train (loss decreases); pressure/bias loops interface
  with the learned router without errors under dropping; loss +
  balance + overflow jointly measurable per step. **Failure to meet
  it blocks S1 design finalization** (the harness, not the science,
  is at fault) — it does not support or weaken any paper claim.
- **Explicit non-claim:** nothing about S0 may appear in the paper
  beyond at most one sentence ("the trained loop was mechanics-tested
  on a toy task before cluster training").

### B.2 S1 — paper-credible trained comparison (GPU cluster)

- **Architecture (fixed for all conditions):** decoder-only
  Transformer, 12 layers, d_model = 512, 8 experts/layer, top-2
  routing, SwiGLU experts (d_ff = 1024), vocab 32k.
  Params: per layer attention 4·512² ≈ 1.05M; MoE 8 × 3·512·1024 ≈
  12.6M total (2 active ≈ 3.15M); + embeddings 16.4M →
  **~180M total, ~50M active per token.**
- **Data:** FineWeb-Edu 10B-token slice, fixed token order per seed
  (shard seeds differ across the 3 run-seeds; data identical across
  controllers within a seed — the trained analogue of v1–v3's
  batch pairing).
- **Capacity model:** per-expert capacity with canonical dropping
  (Switch-style); base arm uniform C at aggregate c = 1.25.
- **Conditions (9, matched):**
  1. `aux-loss` — top-k + Switch-style aux loss (coef from matched
     tuning, see below). The incumbent baseline.
  2. `bias_integral` — DeepSeek-style: per-expert bias, sign update
     gamma = 0.001 **plus the tiny sequence-wise aux loss
     alpha = 0.0001** exactly as DeepSeek-V3 deploys it (v3 lit
     review §b.1). Faithful replication, not a strawman.
  3. `smebu-style` — soft-clamped momentum bias updates after
     Arcee Trinity Large (arXiv:2602.17004). **Reproducibility: TO BE
     CONFIRMED** — the update equations must be recoverable from the
     public report text; if they are not, this condition is cut and
     the paper says so plainly (no invented SMEBU).
  4. `id-pid` — PID-structure balancer after ID Balancing
     (arXiv:2609.39137). **Reproducibility: TO BE CONFIRMED** — same
     rule as (3). The report frames recent balancers as incomplete
     PID; our novelty claim does not depend on this condition
     existing (see §D of the paper outline), but the comparison is
     the honest one to attempt.
  5. `requested` — our pressure controller, (R) feedback, eta from
     matched tuning.
  6. `admitted` — (A) feedback.
  7. `admitted_centered` — (A₀): included **only on the
     heterogeneous-capacity arm as a documented negative control**
     (S-F1 predicts divergence); excluded from the base arm to avoid
     spending cluster budget re-proving a synthetic result — the
     paper cites S-F1 instead.
  8. `capacity_relative` — (C) feedback.
  9. `admitted_antiwindup` — (AW) conditional integration.
- **Tuning (matched, pre-registered):** each of conditions 1, 2, 5, 6,
  8, 9 gets the same budget: 3 hyperparameter values × 1 seed × 2B
  tokens, selection by validation perplexity. Conditions 3, 4 use
  published values if reproducible (no tuning budget spent inventing
  them). Tuning spend is reported alongside results.
- **Base arm (full):** uniform C (c = 1.25), uniform target, seq len
  2048. 9 conditions × 3 seeds = **27 runs**.
- **Factor arms (reduced — 3 controllers: `requested`,
  `bias_integral`, `aux-loss`; × 3 seeds each):**
  - **F-mu:** non-uniform target (skewed mu, v3-T1 analogue at model
    scale: target shares [0.19, 0.17, 0.155, 0.14, 0.125, 0.11, 0.06,
    0.045]-style — exact vector fixed at run time, recorded in
    manifest). Tests whether the T1 Pareto (no controller jointly
    optimizes viol + overflow) appears in trained quality.
  - **F-Chet:** heterogeneous capacity (per-expert C skewed,
    sum = KT·1.0 — the hetero_balanced analogue). Includes
    `admitted_centered` as the 4th controller here (negative
    control): 4 × 3 = 12 runs.
  - **F-sat:** saturation severity, aggregate c ∈ {1.0, 0.75}
    (uniform C). 2 sub-arms × 3 × 3 = 18 runs.
  - **F-batch:** batch size {512, 8192} tokens/step vs base 2048
    (small-batch noise stress, v2 `small_batch` analogue).
    2 × 3 × 3 = 18 runs.
  - **F-topk:** top-K ∈ {1, 4} vs base 2 (routing sparsity).
    2 × 3 × 3 = 18 runs.
  - **F-shift:** demand shift at 50% of training (domain-mixture
    change, e.g. code-heavy → prose-heavy FineWeb-Edu slices;
    `demand_shift`/`adversarial_batches` analogue): does the
    controller track without quality collapse. 1 × 3 × 3 = 9 runs.
  - Factor-arm total: 9 + 12 + 18 + 18 + 18 + 9 = **84 runs**.
- **S1 run total: 27 + 84 = 111 runs.**
- **Metrics (every run):** validation perplexity (**pre-registered
  primary**), downstream (HellaSwag, ARC-Easy, PIQA via
  lm-eval-harness — cheap, secondary), routing violation
  max|R/(KT) − mu|, overflow/dropped-token fraction, throughput
  (tokens/s), stability (loss-spike count > 3σ, tail oscillation of
  controller state). Reported as mean ± std over 3 seeds with 95%
  CIs; head-to-head claims use paired (same-seed) differences.
- **Falsification / kill criteria (pre-registered):**
  - If `requested` does not beat `aux-loss` on val perplexity by
    more than the 95% CI on the base arm, the paper's central
    trained claim is **dead** — report the null plainly; the
    synthetic theorems still stand as theorems, but the paper
    becomes a theory + negative-result paper (still publishable,
    still honest).
  - If val perplexity and routing violation *anti-correlate*
    (SimBal direction) on any arm, that arm's routing metrics are
    demoted to diagnostic and the paper says so.
  - If `bias_integral` matches `requested` on perplexity within CI
    while chattering (S-F2a mechanism in the trained loop), the
    honest conclusion is "balance quality, not controller elegance,
    drives perplexity here" — not a win for either side.

### B.3 S2 — larger scale (optional, only if S1 shows a real effect)

- **Config:** 32 layers, d = 1024, 16 experts top-2, ~1B total /
  ~300M active, 50B tokens, base arm only, 8 conditions × 3 seeds =
  **24 runs**. No factor arms — S2 exists to check that the S1
  effect survives scale, not to re-map the factor space.
- **Gate:** S1 base-arm perplexity effect > 2× the 95% CI width and
  consistent sign across all 3 seeds. Otherwise S2 is not run and
  the paper does not pretend it was needed.

---

## C. Compute budget (with arithmetic shown)

Assumptions: training FLOPs ≈ 6 · N_active · D (standard). GPU =
NVIDIA H100 SXM, 989 TFLOPS BF16 dense peak. Assumed sustained
throughput for small single-node MoE training: **30% MFU ≈ 300
TFLOPS** (conservative: all-to-all + small-model kernel inefficiency;
large-scale multi-node runs assume 25%).

### S0 (this VM, CPU)

- Per run: 3000 steps × ~12 ms/step ≈ 36 s. 50 runs ≈ **30–45 min**
  wall-clock. Negligible cost. Memory < 1 GB.

### S1 — per-run arithmetic

- FLOPs/run = 6 × 50e6 × 10e9 = **3.0e18**.
- Wall-clock/run (1× H100) = 3.0e18 / 3.0e14 ≈ 1.0e4 s ≈ **2.8 h**.
- 111 runs × 2.8 h ≈ **311 GPU-hours ≈ 13.0 GPU-days** (1× H100).
- Tuning: 6 tuned conditions × 3 values × 1 seed × 2B tokens:
  6·3·(6·50e6·2e9 = 6.0e17) = 1.08e19 FLOPs ≈ **10 GPU-hours**.
- Eval (perplexity + 3 harness tasks, amortized): ≈ **8 GPU-hours**.
- **S1 total ≈ 330 GPU-hours ≈ 14 H100-days.** On 8× H100:
  ≈ **1.7 days** wall-clock (plus queue/scheduling overhead —
  budget 3 days).

### S2 — per-run arithmetic (if gated)

- FLOPs/run = 6 × 300e6 × 50e9 = **9.0e19**.
- 8× H100 at 25% MFU ≈ 8 × 2.47e14 ≈ 2.0e15 FLOP/s →
  9.0e19 / 2.0e15 ≈ 4.5e4 s ≈ **12.6 h/run**.
- 24 runs ≈ **300 h on 8× H100 ≈ 2400 GPU-hours ≈ 100 GPU-days**
  (single-GPU-equivalent).

### Budget summary

| item | GPU-hours (H100-equiv) | wall-clock |
|---|---|---|
| Section A (synthetic, this VM CPU) | 0 | ~hours |
| S0 (tiny trained, this VM CPU) | 0 | ~45 min |
| S1 base arm (27 runs) | ~80 | — |
| S1 factor arms (84 runs) | ~250 | — |
| S1 tuning + eval | ~18 | — |
| **S1 total** | **~350** | **~2 days on 8× H100** |
| S2 (gated, optional) | ~2400 | ~12.5 days on 8× H100 |

At typical academic-cluster accounting this is a small-to-medium
allocation; on commercial cloud (H100 ≈ $2–3/GPU-h, 2026 spot
varies) S1 ≈ **$700–$1,050**. The owner has zero budget (standing
fact) — so S1/S2 require a cluster grant, collaborator compute, or a
funded follow-up; the number exists so the ask is concrete.

---

## D. Feasibility assessment for this VM (CPU-only, torch CPU, no GPUs)

**Plain statement.** This VM can produce: the entire Section A
synthetic matrix (179 runs, deterministic CPU — v3's 79 runs ran in
minutes each including analysis); the S0 mechanics probe (~45 min);
all verification/analysis scripting; the formal core's computational
checks. **This VM cannot produce paper-grade trained evidence.**
A single S1 run needs 3.0e18 FLOPs; at an optimistic ~50 GFLOPS
sustained on torch CPU that is ~700 days per run — infeasible by
~3 orders of magnitude, before even considering memory bandwidth,
multi-seed, or tuning budgets. Do not attempt S1 here; do not cite
S0 as model-quality evidence (Section B.1's explicit non-claim).

**The honest boundary (unchanged from v3):** this VM delivers the
formal core + this matrix + the compute budget + the full synthetic
theorem-testing program. Real training evidence needs a GPU cluster.
The S1 spec above is written so that a collaborator or cluster grant
can execute it without redesign — that is the deliverable, not a
pretense that CPU training substitutes for it.

---

## E. Open problems (per-section)

**Section A.**
1. T2/T3/F1/F2 formal statements are `[Track A: pending confirmation]`
   — the theorist's `formal_core.md` may sharpen, weaken, or re-scope
   them; rows marked pending must be re-checked against the landed
   statements before their predictions count as theorem tests.
2. S-T1c's asymptotic leak form `(eta·gamma/delta)·eps` is asserted,
   not proved — needs Track A or downgrade to pure boundary probe.
3. The eta-basin transition (3.0, 10.0] is genuinely unmapped; S-ETA's
   extra arm may find the edge is not a clean threshold at all.
4. S-NU may return "gap persists at 2000 steps" — an honest
   non-result that still needs the attainability theory to interpret.
5. Post-flip cascades (S-PF) have no theory; if the descriptive
   analysis finds nothing beyond seed noise, the paper must say the
   theorem's jurisdiction ends at the first flip — a clean, honest
   boundary.

**Section B.**
1. **Reproducibility of SMEBU** (arXiv:2602.17004) and **ID Balancing
   PID** (arXiv:2609.39137) from public text is **to be confirmed**.
   If either paper's update equations are not recoverable, the
   condition is cut — no invented comparator. This is the largest
   external dependency in the matrix.
2. The trained-loop failure modes the synthetic harness cannot model
   (router co-adaptation with pressure state, noted in the v3 smoke
   verdict) are first exercised in S0 and then for real in S1 —
   S1's kill criteria (§B.2) exist because the honest prior includes
   "the controllers don't matter at LM scale."
3. Factor-arm controller reduction (3 instead of 9) is a budget
   decision: if S1 base shows `admitted` or `capacity_relative`
   unexpectedly competitive, the F-mu/F-Chet arms should be widened —
   pre-register the widening rule now: any formal variant within CI
   of `requested` on base-arm perplexity joins all factor arms.
4. **Compute is the binding constraint.** S1/S2 need ~350 / ~2400
   H100-hours the owner does not have. Until cluster access exists,
   the paper program's trained half is a funded-proposal artifact —
   complete, costed, and gated — not an in-progress experiment.

## F. Run-manifest discipline (carried forward from v1–v3)

Every run (synthetic or trained) records: resolved config, git commit,
protocol version, controller gauge-equivalence class, SHA-256 of the
affinity batch / data shard (pairing across controllers within a
seed), per-step metrics series, and a duplicate-detection canonical
key. Pre-registered predictions live in git before execution. The
verifier (`scripts/verify_findings.py`, suite-aware) gains a `paper`
suite encoding each row's falsification criterion — a failing check
is a finding, not a bug to fix.

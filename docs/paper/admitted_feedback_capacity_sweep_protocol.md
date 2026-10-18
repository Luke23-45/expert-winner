# Capacity-regime synthetic experiment: protocol and decision gates

**Status:** protocol fixed before running the sweep. This is an exploratory,
paired synthetic mechanism study of the existing Top-K plus per-expert
capacity model. It does not test model quality or production prevalence.

## Question

How does the existing sign-bias controller behave as independent per-expert
capacity moves from global saturation through partial saturation to spare
capacity, when its feedback is requested counts `R`, admitted counts `A`, or
zero feedback? Does changing which routes are retained within each expert
change any count-level result?

This directly follows the formal model `A_e=min(R_e,C_e)` and the professor
report's proposed mechanism. It does not replace the admission rule with a
shared-device rule or claim that score ranking changes `A` under independent
per-expert caps.

## Fixed plant and paired arms

- `E=8`, `K=2`, `T=128`; the same seeded affinity matrix and zero initial bias
  are used for every arm in a seed block.
- Use the existing ring-pair affinity generator and seeds `0..19`.
- Run 120 updates with mean-centered sign feedback and fixed bias step
  `0.025`; no hyperparameter tuning after inspecting outcomes.
- Capacity is uniform within each arm: `C in {24,28,32,36}`. These equal
  `ceil(T*K/E * cf)` for factors `cf in {0.75,0.875,1.0,1.125}`.
- For every `(C, seed)`, pair the six arms formed by feedback
  `{requested, admitted, none}` and route retention order `{score, position}`.
  Each expert admits exactly `min(R_e,C)` routes. The admission order affects
  route identities only.
- Add a no-admission negative control for requested and admitted sensors,
  which must be trajectory-identical because `R=A`.

## Pre-stated mathematical controls

1. **Per-expert cardinality identity.** For any route set `S_e` and any
   retention ranking that fills available slots,
   `|admit(S_e)|=min(|S_e|,C)`. For equal initial requests, the score and
   position arms must have identical `A`, feedback, and bias trajectories.
2. **Global-saturation freeze.** At `C=24`, the generated initial requests
   satisfy `R_e>=24` for all eight experts. Thus `A=24*1`; admitted sign
   feedback is exactly zero. The zero-bias admitted arm must remain fixed,
   remain globally saturated, and have per-step overflow `KT-EC=64`.
3. **Dropless negative control.** In the no-admission arm, `R=A`; requested
   and admitted feedback trajectories must be identical.
4. **Mass accounting.** Every step must satisfy `sum(R)=K*T`,
   `A_e=min(R_e,C)`, and `sum(R-A)=sum(R)-sum(A)`.
5. **Saturated-pair bias-gap invariance.** Under the admitted sign-bias
   update, any two experts saturated at a given step have equal admitted
   counts `A_e=A_f=C`, receive equal updates, and retain their pairwise bias
   difference after that update (up to floating-point tolerance).

Any failure invalidates the affected run; do not explain it away as a
scientific outcome.

## Outcomes

Report, by capacity and controller, the complete per-seed trajectories and
paired descriptive summaries for:

- request imbalance `||R-(K*T/E)1||_1`;
- admitted imbalance `||A-mean(A)1||_1`;
- overflow `sum(R-A)`;
- global-saturation indicator and fraction of experts saturated;
- bias norm and first routing-change step.

Do not combine imbalance, overflow, and bias into one weighted score. Report
means and ranges across the 20 perturbations, but do not treat these hand-built
variants of one ring plant as population samples or make a statistical
generalization claim from their standard errors.

## Interpretation and training gate

- The theorem predicts the exact freeze only in the globally saturated,
  uniform-capacity arm. It does **not** predict that requested feedback
  reduces overflow, that admitted feedback winds up under uniform capacities,
  or that either controller improves a trained model.
- At partial saturation, results are exploratory evidence about this plant.
  A difference between requested and admitted feedback is not, by itself, a
  benefit.
- Do not start a training run based only on pressure movement or lower request
  imbalance. Training requires a preregistered objective whose connection to
  served/computed routes is justified, a pretraining repeatable advantage
  over both no-feedback and the other signal on that objective, and an
  implementation path that matches the pinned stack's aggregation semantics.
- If requested feedback improves request imbalance while increasing overflow,
  the experiment has not selected a winner; specify the system objective and
  derive its trade-off before training.

## Reproducibility

The executable is `scripts/run_capacity_regime_sweep.py`. It writes
`results/capacity_regime_sweep/summary.json` and
`results/capacity_regime_sweep/trajectories.csv`. The exact protocol, source
revision, and all deterministic controls are recorded in the summary.

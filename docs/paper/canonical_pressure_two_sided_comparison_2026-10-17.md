# Two-sided signal comparison for canonical proportional pressure

**Status:** exact constructive result with two rational witnesses and a
controlled synthetic audit. This is a theorem about the proportional
gauge-pressure controller in `formal.md`; it is separate from the signed
expert-bias theorem in
[`bidirectional_bias_comparison_theorem_2026-10-17.md`](bidirectional_bias_comparison_theorem_2026-10-17.md).

## Model

Fix a deterministic static affinity matrix, Top-$K$ routing with a fixed
tie-break, uniform target $mu_e=1/E$, and canonical per-expert admission
\[
R_e(q)=\#\{\text{requested routes to }e\},\qquad
A_e(q)=\min\{R_e(q),C_e\}.
\]
For signal $L\in\{R,A\}$, the pressure update is
\[
q^+=\Pi_g\!\left(q+\eta\gamma\left(\frac{L}{KT}-\mu\right)\right),
\qquad s_{t,e}=a_{t,e}-\gamma q_e,
\]
with zero decay, zero initial pressure, and $\Pi_g$ the canonical
minimum-subtracting gauge representative. Overflow in one batch is
\[
J(q)=\sum_e(R_e(q)-A_e(q)).
\]

## Theorem: neither signal universally dominates

There are two strict-margin instances, both with uniform per-expert
capacities, exact total capacity $\sum_e C_e=KT$, a uniform target, and the
same proportional pressure dynamics, on which the strict finite-horizon
overflow ranking reverses:

1. **Admitted better.** Let $E=3$, $K=1$, $T=3$, $C=(1,1,1)$,
   $\gamma=1$, $\eta=4$, $H=12$, and let the three affinity rows be
   $(0,0,1),(0,0,1),(0,1,0)$. With lower expert index winning ties,
   \[
   J_{12}(A)=18 < 23=J_{12}(R).
   \]
   No feedback has overflow 12. The same route paths and costs hold for every
   $\eta\in(3,\infty)$ on this fixed matrix. At $\eta=4$, every entrywise
   affinity perturbation of magnitude less than $1/6$ preserves all routes:
   the minimum selected/unselected score margin is $1/3$, and a pairwise gap
   changes by less than twice the perturbation magnitude. For the checked
   radius $1/10$, two exact perturbation matrices preserve every path. If
   every row is repeated $m$ times and capacities are scaled by $m$, the
   normalized feedback and pressure path are unchanged while overflow scales
   to $18m$ and $23m$; no-feedback overflow is $12m$.

2. **Requested better.** Let $E=8$, $K=2$, $T=128$, $C_e=32$,
   $\gamma=1$, $H=120$, and use the exact affinity fixture
   [`uniform_capacity_seed5_affinities.csv`](fixtures/uniform_capacity_seed5_affinities.csv).
   At $\eta=1$,
   \[
   J_{120}(R)=1874 < 1920=J_{120}(A).
   \]
   No feedback also has overflow 1920. The same strict ranking holds on the
   exact open step-size interval
   \[
   \left(\frac{18944223025711}{18945312500000},
   \frac{38087479892954599}{38085937500000000}\right).
   \]
   This interval is the intersection of all selected-versus-unselected
   affine score inequalities along the three 120-step paths. At $\eta=1$,
   every entrywise affinity perturbation of magnitude at most $10^{-6}$ also
   preserves those paths: the largest pairwise gap change is $2\cdot10^{-6}$,
   below the exact controlled-arm minimum cutoff margin
   $47149144803/2500000000000000$. The exact audit checks two such
   perturbations per signal arm.

Thus, within this controller and admission model, neither requested nor
admitted feedback has a universal cumulative-overflow advantage. Both
instances have strict routes, so the reversal is not caused by tie-breaking.
The result is constructive and exact, not a statistical claim about randomly
sampled routers.

## Proof and reproduction

Each instance is simulated with `fractions.Fraction` arithmetic. In the
pressure quotient, for a fixed route sequence and zero decay, the pressure is
linear in the step size: $[q_t(\eta)]=\eta v_t$. Every top-$K$ set is fixed by
finitely many selected-versus-unselected score inequalities, each affine in
$\eta$. Intersecting these inequalities proves the stated open step-size
intervals. A strict cutoff margin gives the affinity-perturbation result by
induction: unchanged routes imply unchanged counts and pressure increments.

Reproduce the admitted-better witness with
[`audit_canonical_pressure_admitted_better.py`](../../scripts/audit_canonical_pressure_admitted_better.py)
and its exact result at
[`canonical_pressure_admitted_better.json`](../../results/bidirectional_bias_comparison/canonical_pressure_admitted_better.json).
That script SHA-256 is
`f89f1c66d7c23196a5f62d0fdde8a1eee4aabbff2b8a841bf9623ca9cff372fa`;
the three-row fixture SHA-256 is
`cf457272476603ad64d7566997adf4b73854fc6a0b4cf4faff8ced5a1bc87723`.
Reproduce the requested-better witness and exact step-size certificate with
[`audit_canonical_pressure_uniform_fixture.py`](../../scripts/audit_canonical_pressure_uniform_fixture.py)
and
[`canonical_pressure_uniform_fixture.json`](../../results/bidirectional_bias_comparison/canonical_pressure_uniform_fixture.json).
That script SHA-256 is
`0899cf9e0e78b792adac889988e311a6797b00ab48344b875e2fae712904673c`.

## Scope

This proves a precise negative result: no signal can be recommended as
universally overflow-optimal for the stated proportional controller and
per-expert clipping model. It does **not** give a condition predicting which
signal wins from a new router instance, establish a family-level advantage
over an independently specified polyhedral testing benchmark, measure
telemetry cost, or show a trained-model quality gain. The admitted-better
instance also has lower overflow with no feedback, so it is not evidence that
admitted feedback improves the plant over doing nothing. This result sharpens
the model-level research claim but does not by itself establish a
top-conference contribution or justify a training run.

## Prior-art boundary

The additive expert-bias mechanism with a sign update is already described by
Loss-Free Balancing: it adds expert-wise bias before Top-$K$ routing and
updates bias from the previous batch's load deviation
([Wang et al., *Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts*](https://arxiv.org/abs/2408.15664), Algorithm 1 and §3). The signed-bias results elsewhere in this directory therefore do not claim a new controller. The present proportional-pressure theorem also does not claim a new routing rule. Its exact statement is the two-sided finite-horizon comparison of requested and admitted count signals under the declared pressure law and clipping map. The research contribution still needs to be assessed against general outcome-cost testing and control benchmarks; the two witnesses alone do not establish novelty.

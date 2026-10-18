# Preregistered parameter sweep for the two-step overflow theorem

**Status:** fixed before execution of this sweep. It evaluates the
parameterized theorem in
[`heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`](heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md).
This is a controlled synthetic diagnostic within the existing canonical
pressure model, not a trained-model study or a separate research direction.

## Question and endpoint

Across multiple under-capacity fractions, capacity splits, and controller
gains, does the paired two-step overflow gap follow the formula's dependence
on $d=\eta r$ and remain insensitive to how the residual capacity is split
between the two experts whose capacities are at least $T/3$?

The primary plant-level endpoint is

\[
G_T(\eta,r,s)=\frac{J_0^A+J_1^A-J_0^R-J_1^R}{T},
\qquad g(\eta,r)=d-d^3/3,\quad d=\eta r.
\]

No cell is excluded or selected after observing outcomes. The full
parameter grid and uncertainty estimates will be reported.

## Fixed model and factorial grid

- Canonical hard Top-1 router: $E=3$, $K=1$, $\gamma=1$, target
  $\mu=(1/3,1/3,1/3)$, zero leak, and $q_0=0$.
- Under-capacity fractions $r\in\{1/12,1/6,1/4\}$.
- Capacity split $s\in\{0,r/2,r\}$, giving
  $C/T=(1/3-r,1/3+s,1/3+r-s)$ and exact total capacity $T$.
- Gains $\eta\in\{1/2,1,2,3\}$; every registered cell satisfies
  $0<\eta r<1$.
- Batch sizes $T\in\{120,240,480,960,1920\}$, which make all capacities
  integral for every registered $(r,s)$.
- 200 independent affinity plants per batch size. Each matrix has iid
  integer entries uniformly sampled from $\{0,\ldots,2^{30}\}$ and is reused
  for every registered $(r,s,\eta)$ and all paired arms at that $(T,r)$.
  Replicate $k$ uses seed `20261020 + 100000*T + k`, $k=0,\ldots,199$.
- Integer cross-multiplication implements all pressure-score comparisons;
  lower expert index resolves exact ties. The same static matrix is reused
  at both routing steps.

## Arms and registered checks

For each matrix and parameter cell, run requested feedback, admitted
feedback, and no feedback under the registered capacity. At each first step
compute $A_e=\min(R_e,C_e)$ and update feedback arms exactly by
$q_1=\Pi_g(q_0+\eta(L_0/T-\mu))$. No feedback keeps pressure at zero.

For every arm and step verify $\sum_eR_e=T$, $A=\min(R,C)$, exact overflow
accounting, and shared step-zero overflow across paired feedback arms.
Also run a no-clipping signal-invariance diagnostic per matrix/gain: with
$C=(T,T,T)$, requested and admitted feedback must have identical two-step
routes and zero overflow.

Report by $(T,r,s,\eta)$ the mean $G_T$, standard error and 95% t interval,
the theoretical limit, absolute mean error to that limit, fraction of paired
plants with positive gap, both feedback-arm mean costs, no-feedback mean
cost, and exact-tie counts. Report the effect of varying $s$ at fixed
$(T,r,\eta)$ directly; do not pool split cells to hide disagreement.

## Interpretation boundary

This sweep can detect implementation mistakes or a contradiction in the
finite-grid trend. It does not prove the asymptotic theorem, establish
general controller superiority, demonstrate model-quality improvement, or
resolve the outcome-map benchmark reduction. The theorem and experiment are
separate evidence.

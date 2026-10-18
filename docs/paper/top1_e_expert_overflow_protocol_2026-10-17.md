# Preregistered expert-count experiment for the Top-1 overflow theorem

**Status:** fixed before execution. This experiment tests the $E$-dependence
of the theorem in
[`top1_e_expert_two_step_overflow_theorem_2026-10-17.md`](top1_e_expert_two_step_overflow_theorem_2026-10-17.md).
It stays within the canonical model and does not change the research question.

## Primary endpoint

For each paired plant, record
\[
G_T(E,d)=\frac{J_0^A+J_1^A-J_0^R-J_1^R}{T},
\qquad g_E(d)=d-d^E/E.
\]
The registered comparison is the finite-sample mean against this asymptotic
limit for every grid cell. No endpoint or parameter cell will be dropped.

## Registered design

- Expert counts $E\in\{3,4,8,16\}$; $K=1$, $\gamma=1$,
  $\mu=\mathbf1/E$, zero leak, $q_0=0$.
- Under-capacity fraction $r=1/(2E)$. Split the excess equally:
  $\sigma_e=r/(E-1)$ for $e=2,\ldots,E$. Thus
  $C_1/T=1/(2E)$ and
  $C_e/T=1/E+1/(2E(E-1))$ for $e\ge2$.
- Gains $\eta\in\{E/2,E,3E/2\}$, giving the three fixed normalized
  pressure displacements $d=\eta r\in\{1/4,1/2,3/4\}$.
- Batch sizes $T\in\{3360,6720,13440\}$; all capacities are integers for
  every registered expert count.
- 100 independent plants per $(E,T)$. Each matrix has iid integer entries
  uniform on $\{0,\ldots,2^{30}\}$, divided by $2^{30}$, and is reused at
  both steps, all three gains, and all feedback arms. Replicate $k$ uses
  seed `20261021 + 100000*E + 1000*T_index + k`, with zero-based
  `T_index` and $k=0,\ldots,99$.
- Exact integer cross-multiplication determines all scores; ties go to the
  lowest expert index. All arms share the same initial routes and matrix.

## Arms and checks

Run requested, admitted, and no-feedback arms under the registered capacity.
At step zero compute $A=\min(R,C)$ and apply the canonical pressure update
once for the two feedback arms. Also run a no-clipping R/A diagnostic at each
$(E,T,\text{replicate},\eta)$.

For each recorded routing step, verify $\sum_eR_e=T$, $A=\min(R,C)$, exact
overflow accounting, and identical step-zero cost across paired arms. The
no-clipping diagnostic must have zero overflow and identical R/A trajectories.
Record exact tie counts. Report cell means, standard errors, 95% t intervals,
the theoretical limit, absolute distance to the limit, fraction of positive
paired gaps, and each arm's mean overflow. No stopping or seed selection is
allowed after observing signs.

## Interpretation boundary

This is a finite-grid numerical check of an asymptotic theorem for iid
continuous affinities. It cannot prove the limit, establish a $K>1$ result,
claim trained-model quality, or defeat the finite-instance outcome-map
reduction.

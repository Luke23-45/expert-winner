# Preregistered exact-grid experiment: two-step heterogeneous-capacity overflow

**Status:** design fixed before execution. This experiment tests the finite-size
approach to the theorem in
[`heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`](heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md).
It uses the existing canonical Top-1, per-expert clipping, gauge-pressure
model; it does not introduce a new controller or observation-cost model.

## Question and primary endpoint

For a paired static affinity matrix, does admitted-count pressure feedback
increase the two-step overflow relative to requested-count feedback by an
amount approaching the theorem's population limit as batch size grows?

For each paired plant, the primary endpoint is

\[
G_T(\eta)=\frac{(J_0^A+J_1^A)-(J_0^R+J_1^R)}{T}.
\]

The registered theoretical limit is

\[
g(\eta)=d-d^3/3,\qquad d=\eta/6,
\]

for every tested \(0<\eta<6\). No acceptance threshold is imposed on the
finite-size error; the report will show estimates, uncertainty, and distance
to the limit without selecting favorable gains or batch sizes.

## Fixed model and implementation

- Experts \(E=3\), Top-1 routing \(K=1\), target
  \(\mu=(1/3,1/3,1/3)\), score gain \(\gamma=1\), leak \(\delta=0\), and
  initial gauge pressure \(q_0=(0,0,0)\).
- For each plant, draw one \(T\times3\) matrix of independent integer
  affinities uniformly from \(\{0,\ldots,2^{30}\}\), divided by \(2^{30}\).
  Reuse this same matrix at both routing steps and in all paired signal arms.
- Capacities are exactly
  \(C=(T/6,T/2,T/3)\), for \(T\in\{60,120,240,480,960,1920\}\).
- Gains are \(\eta\in\{1/2,1,2,4,5\}\), all strictly inside the theorem's
  interval. Pressure and score comparisons are implemented with integer
  cross-multiplication; no floating-point tie decisions are used.
- Use 500 independent matrices per batch size. The seed for replicate \(r\)
  at batch size \(T\) is `20261019 + 100000*T + r`, for
  \(r=0,\ldots,499\). The identical matrix is reused across all five gains
  and all arms at that \((T,r)\).
- At each step, choose the highest score with lower expert index breaking an
  exact tie; set \(A_e=\min(R_e,C_e)\), \(J_e=R_e-A_e\). For feedback
  \(L\in\{R,A\}\), update once using exactly
  \(q_1=\Pi_g(q_0+\eta(L_0/T-\mu))\). The no-feedback arm holds pressure
  fixed at zero.

## Arms and controls

For every paired matrix and gain, run:

1. requested-count feedback (R);
2. admitted-count feedback (A);
3. no feedback;
4. no-clipping diagnostic, with \(C=(T,T,T)\), separately for R and A.

The first three arms share the registered heterogeneous capacity. The
no-clipping diagnostic must have zero overflow and identical R- and A-feedback
trajectories because \(A=R\) at every step. It is a code-path negative
control, not another estimate of the theorem.

## Recorded quantities and integrity checks

Save one plant-level row for each \((T,\eta,r)\), including the initial
request/admission counts, both-step counts and overflow for each arm, the
normalized paired gap, the theoretical limit, and exact-tie counts. Check for
every row that \(\sum_eR_{s,e}=T\), \(A_s=\min(R_s,C)\), overflow accounting
is exact, and step-zero overflow is shared by R/A/no-feedback. Check the
no-clipping control's zero overflow and identical signal trajectories.

Report, by \((T,\eta)\), the mean primary endpoint, standard error, 95% t
interval, mean arm costs, the paired fraction with \(G_T>0\), and absolute
distance between the observed mean and \(g(\eta)\). Report every registered
cell, including any cell that disagrees with the limit trend. Do not tune
seeds, gains, capacities, or endpoints after seeing outcomes.

## Interpretation boundary

The experiment is a finite-grid diagnostic of one exact asymptotic theorem.
It cannot establish the theorem, generalize to trained routers, show a
telemetry-collection cost, or defeat the independently specified outcome-map
benchmark. The theorem and empirical findings must be stated separately.

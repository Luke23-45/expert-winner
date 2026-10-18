# Exact one-update delay under admitted feedback

**Evidence class:** finite-instance analytic proof with exact-rational
routing-inequality audit. This is a result in the existing requested-versus-
admitted Top-1 model.

## Theorem

Use the $E=3$, $K=1$, $T=3$ affinity batch and capacities
$C=(1,1,1)$ in
[`admitted_feedback_noncyclicity_2026-10-17.md`](admitted_feedback_noncyclicity_2026-10-17.md).
Let $\mu=(1/3,1/3,1/3)$, $\gamma=1$, zero leak $\delta=0$, min-coordinate
gauge projection, and initial pressure $q_0=(0,2,3)$. Run the formal updates
$$
q_{t+1}=\Pi_g\left(q_t+\eta\left(\frac{L(q_t)}{T}-\mu\right)\right),
$$
with $L=R$ for requested feedback and $L=A=\min(R,C)$ for admitted feedback.

For every
$$
\frac{7}{100}<\eta<\frac{21}{200},
$$
requested feedback reaches the balanced state $R=A=(1,1,1)$ after two
saturated updates, while admitted feedback needs three saturated updates.
Consequently cumulative rejected assignments up to the first balanced state
are respectively $2$ and $3$.

For every positive integer $m$, repeat each affinity row $m$ times and set
$T=3m$, $C=(m,m,m)$. The same normalized feedback and pressure path result,
and cumulative rejection becomes $2m$ versus $3m$. Thus the admitted policy
incurs exactly $m$ extra rejected assignments, or $1/3$ extra rejection per
requested slot during this transient, throughout the same open step-size
interval.

## Proof by exact state sequence

At every state where $R=(0,1,2)$, clipping gives $A=(0,1,1)$. Their
normalized errors are
$$
\varepsilon_R=(-1/3,0,1/3),\qquad
\varepsilon_A=(-1/3,0,0).
$$
Subtracting the minimum coordinate after each update gives the following
candidate state sequences:

| Arm | State before routing | Routing outcome |
|---|---|---|
| Both, $t=0$ | $(0,2,3)$ | $R=(0,1,2)$ |
| Requested, $t=1$ | $(0,2+\eta/3,3+2\eta/3)$ | $R=(0,1,2)$ |
| Requested, $t=2$ | $(0,2+2\eta/3,3+4\eta/3)$ | $R=(1,1,1)$ |
| Admitted, $t=1$ | $(0,2+\eta/3,3+\eta/3)$ | $R=(0,1,2)$ |
| Admitted, $t=2$ | $(0,2+2\eta/3,3+2\eta/3)$ | $R=(0,1,2)$ |
| Admitted, $t=3$ | $(0,2+\eta,3+\eta)$ | $R=(1,1,1)$ |

Once the requested count is $(1,1,1)$, both feedback errors are zero, so that
state is fixed and has no overflow. Every saturated step has total overflow
$\sum_e(R_e-A_e)=1$ in the base instance.

It remains to verify that the proposed route sequence holds over the claimed
interval. Every score difference between the proposed winner and each
competitor is affine in $\eta$. Exact comparison of all $6\cdot3\cdot2=36$
inequalities yields the two active constraints:

* At the requested arm's first updated state, token 2 must continue choosing
  expert 3 over expert 1. Its margin is $7/100-2\eta/3>0$, giving
  $\eta<21/200$.
* At the admitted arm's third updated state, token 2 must choose expert 1
  over expert 3. Its margin is $\eta-7/100>0$, giving $\eta>7/100$.

The other 34 winner-versus-competitor inequalities remain strict throughout
this interval. `scripts/audit_closed_loop_admission_delay.py` derives their
exact affine forms, verifies the intersection is exactly the stated open
interval, and runs exact-rational trajectories for $m=1,2,10$ at
$\eta=1/10$. At the interval endpoints a binding routing tie occurs, so the
strict result is stated on the open interval.

### Robustness corollary

Restrict the step size to the compact interval $\eta\in[2/25,1/10]$.
Minimizing every one of the 36 winner-versus-competitor affine margins over
this interval and the six proposed states gives the exact minimum $1/300$.
If every affinity entry is perturbed by at most $1/1200$, each score
difference changes by at most $1/600$. All required winners therefore remain
strict, with margin at least $1/600$, and the two-update versus three-update
route sequences and overflow totals remain unchanged. The uniform margin
calculation is machine-checked in
[`scripts/run_robust_delay_experiment.py`](../../scripts/run_robust_delay_experiment.py);
the paired finite audit is reported in
[`closed_loop_delay_robustness_results_2026-10-17.md`](closed_loop_delay_robustness_results_2026-10-17.md).

This is a robustness result for the same fixed three-expert Top-1 family. It
does not turn the family into an arbitrary-router theorem.

## Controlled synthetic experiment

The separate 16-condition deterministic trajectory audit in
[`admitted_noncyclicity_trajectory_results_2026-10-17.md`](admitted_noncyclicity_trajectory_results_2026-10-17.md)
checks four initial witness states and four step sizes. This theorem isolates
one initial state and proves a step-size interval rather than extrapolating
from that grid. The theorem is exact for its fixed affinity family; the grid
is a supporting mechanism audit, not an independent-seed experiment.

## Benchmark and claim boundary

This theorem is **not** a fixed-instance separation from B1. The fixed
affinity batch induces a finite arrangement of score-tie hyperplanes. B1 can
label each cell with this exact $R$, clipped $A$, overflow, and feedback
history while retaining the same quotient metric and pressure transition.
Consequently it reproduces the trajectories and the delay exactly. The
replication theorem is a useful closed-form MoE mechanism result, but its
instance-level consequence transfers to the unrestricted polyhedral
benchmark. This is consistent with the existing class-level no-go assessment;
the theorem does not close the top-conference novelty gate.

The professor report's proposed windup language also needs this scope
distinction. This construction has partial expert saturation and a finite
one-update lag, followed by zero-error balance. It is not a counterexample to
the separate global-saturation freeze theorem, whose assumptions are not met
here, and it does not establish generic windup.

## Scope

Established: a robust step-size interval and an exact replicated-family
transient-overflow gap in one static Top-1 affinity family.

Not established: a worst-case or minimax gap against every admitted policy;
optimality of either controller; extension to arbitrary $E,K$, affinity
sequences, or score-ranked device-cap admission; superiority over the
polyhedral adaptive-testing benchmark; or a trained-model benefit. This is a
proved mechanism result, not yet the final conference-level contribution.

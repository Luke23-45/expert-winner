# Exact Top-1 counterexample: admitted feedback is not a convex subgradient

**Evidence class:** exact-rational finite counterexample, recomputed by
`scripts/audit_admitted_noncyclicity.py`.

## Statement

There is a fixed three-token, three-expert Top-1 routing plant with positive
capacities whose total equals the requested slot count, and four strict-routing
pressure states on its gauge quotient, for which the gauge-centered
admitted-feedback field violates cyclic monotonicity. Therefore that field is
not the subgradient of any convex potential on this plant.

This is a structural counterexample for the existing requested-versus-admitted
model. It adds no priced-observation or real-training premise.

## Exact instance

Use $E=3$, $K=1$, $T=3$, $\gamma=1$, uniform target
$\mu=(1/3,1/3,1/3)$, and capacities $C=(1,1,1)$. Thus
$\sum_e C_e=KT=3$. The three token affinity rows are

$$
A=\begin{pmatrix}
1/2 & 43/50 & 371/100\\
381/100 & 11/10 & 172/25\\
191/100 & 189/25 & 27/4
\end{pmatrix}.
$$

At quotient-chart point $(x,y)=(q_1-q_3,q_2-q_3)$, use representative
$q=(x,y,0)$, with scores $s_{t,e}=a_{t,e}-q_e$. These representatives
need not be nonnegative: adding a common constant leaves routing unchanged.
Their minimum-zero representatives are shown below.

| $i$ | Chart point $(x,y)$ | Minimum-zero $q$ | Strict Top-1 routes | $R(q_i)$ | Admitted $A(q_i)=\min(R,C)$ | Minimum score margin |
|---:|---:|---:|---|---|---|---:|
| 0 | $(-3,-1)$ | $(0,2,3)$ | $(3,3,2)$ | $(0,1,2)$ | $(0,1,1)$ | $7/100$ |
| 1 | $(-2,-2)$ | $(0,0,2)$ | $(3,3,2)$ | $(0,1,2)$ | $(0,1,1)$ | $17/20$ |
| 2 | $(3,1)$ | $(3,1,0)$ | $(3,3,3)$ | $(0,0,3)$ | $(0,0,1)$ | $19/100$ |
| 3 | $(-3,4)$ | $(0,7,3)$ | $(3,3,3)$ | $(0,0,3)$ | $(0,0,1)$ | $7/100$ |

Routes in the table are one-based expert IDs. Every choice is strict, so no
Top-1 tie convention is involved. The ordered cycle is
$q_0,q_1,q_2,q_3,q_0$.

This is not an isolated affinity matrix: if every affinity entry is perturbed
by less than $7/200$ in absolute value, every winner-versus-runner-up score
margin remains positive at these four pressures. The route counts, admitted
fields, and $2/3$ violation are therefore unchanged throughout that open
neighborhood.

## Quotient calculation

For a load vector $L$, define the centered field
$$
g(L)=P_0(KT\mu-L)=P_0((1,1,1)-L).
$$
The first two components of $g(L)$ are the covector components in the
quotient chart $(q_1-q_3,q_2-q_3)$. Exact values are

| $i$ | $g(R(q_i))$ in quotient coordinates | $g(A(q_i))$ in quotient coordinates |
|---:|---:|---:|
| 0 | $(1,0)$ | $(2/3,-1/3)$ |
| 1 | $(1,0)$ | $(2/3,-1/3)$ |
| 2 | $(1,1)$ | $(1/3,1/3)$ |
| 3 | $(1,1)$ | $(1/3,1/3)$ |

For any convex function $\Phi$, subgradients $g_i\in\partial\Phi(q_i)$
must satisfy cyclic monotonicity:
$$
\sum_{i=0}^{3}\langle g_i,q_{i+1}-q_i\rangle\le 0,
\qquad q_4=q_0.
$$
Substitution in the exact quotient coordinates gives
$$
\sum_i\langle g(R(q_i)),q_{i+1}-q_i\rangle=-2,
$$
whereas
$$
\sum_i\langle g(A(q_i)),q_{i+1}-q_i\rangle=\frac{2}{3}>0.
$$
The admitted field therefore fails a necessary condition for being a convex
subgradient field. The requested field passes this particular cycle test;
the general requested-potential result is established separately in the
formal core.

## Exact replicated family

For any integer $m\ge 1$, replicate every row of the affinity matrix $m$
times, set $T=3m$, and set $C=(m,m,m)$. Keep the same four quotient pressures.
Because each row is duplicated, the strict route pattern at every pressure is
the base pattern repeated $m$ times. Hence both $R$ and $A$ and their centered
fields scale by $m$. The capacity identity still holds:
$\sum_e C_e=3m=KT$. The admitted cycle sum is exactly $2m/3$, or $2/9$ per
token, for every $m$. The affinity perturbation radius preserving all four
route patterns remains $7/200$.

The audit checks this family at $m\in\{1,2,3,10\}$ with exact rational
arithmetic. The all-$m$ statement follows directly from the replication
construction, not from extrapolating those four checks.

An independent $E=4$, $K=1$ witness and its replicated family are documented
in [`admitted_feedback_noncyclicity_e4_2026-10-17.md`](admitted_feedback_noncyclicity_e4_2026-10-17.md).

The cyclic-monotonicity condition used here is the necessary direction of
Rockafellar's characterization of convex subdifferentials; see the original
[1966 paper](https://msp.org/pjm/1966/17-3/pjm-v17-n3-p08-p.pdf). In this
finite argument it also follows immediately by summing the convex
subgradient inequality around a cycle.

## Controlled audit and reproducibility

The audit script uses rational arithmetic throughout. It checks four replica
scales and fails unless it reproduces the strict routing outcomes, capacity
identity, requested circulation $-2m$, and admitted circulation $2m/3$. Run
from the repository root:

```powershell
python scripts/audit_admitted_noncyclicity.py
```

No random seed or sampling is involved. This is an exact synthetic
counterexample audit, not a multi-seed performance experiment.

## Interpretation and limits

Established: coordinatewise admission clipping can destroy the convex
subgradient structure that the requested Top-1 load field has, even when
capacity sums exactly to $KT$, with positive capacities and no routing ties.

Not established: that admitted-feedback dynamics diverge, cycle, or have worse
overflow on this instance; that no nonconvex Lyapunov function exists; a
general theorem for all capacities or $E,K,T$; a separation from the
polyhedral adaptive-testing benchmark; or a trained-model or production
benefit. This is an exact lemma/counterexample in the existing research line,
not by itself the paper's final contribution.

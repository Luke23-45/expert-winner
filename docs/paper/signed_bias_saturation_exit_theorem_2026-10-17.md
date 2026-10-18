# Finite exit from global saturation under signed admitted-bias feedback

## Model and theorem

Fix a static batch of affinity rows $a_{t,e}$, $E>K\ge1$, positive
per-expert capacities $C_e$, and a deterministic Top-$K$ tie rule. Scores are
$a_{t,e}+b_e$. Let $R_e(b)$ be requested counts and
$A_e(b)=\min(R_e(b),C_e)$. The signed integral controller used in
`BiasIntegralFeedback` is
\[
b_{n+1}=b_n+\gamma u(L_n),\qquad
u_e(L)=\operatorname{sign}(\overline L-L_e),\qquad \gamma>0,
\]
where $L_n=A_n$ for admitted feedback or $L_n=R_n$ for requested feedback.
Call state $n$ globally saturated if $R_e(b_n)\ge C_e$ for every expert.

**Theorem.** Suppose state $0$ is globally saturated and the admitted
controller is used. Set
\[
u=\operatorname{sign}(\overline C\mathbf1-C),
\]
where $\overline C=E^{-1}\sum_e C_e$. Order the coordinates of $u$
decreasingly and suppose $u_{(K)}>u_{(K+1)}$. Let $M$ be the indices of its
largest $K$ coordinates. Define
\[
N=\max\!\left(0,\max_{t,\,i\in M,\,j\notin M}
\left[\left\lfloor
\frac{a_{t,j}+b_{0,j}-a_{t,i}-b_{0,i}}
{\gamma(u_i-u_j)}
\right\rfloor+1\right]\right).
\]
Then the first state index $\tau$ that is not globally saturated satisfies
\[
\boxed{\tau\le N.}
\]

**Proof.** While a state is globally saturated, $A_n=C$ and hence the
feedback is the same vector $u$ at every such state. If saturation persists
through state $n$, the exact bias is $b_n=b_0+n\gamma u$. For each token,
each $i\in M$, and each $j\notin M$, the definition of $N$ ensures
\[
a_{t,i}+b_{n,i}>a_{t,j}+b_{n,j}\qquad(n\ge N).
\]
Thus, if the trajectory has remained saturated until state $N$, all tokens
route to exactly $M$ there. Since $K<E$ and all capacities are positive,
every expert outside $M$ then has request count zero and is unsaturated. So
state $N$ cannot be globally saturated. If the trajectory left earlier,
the bound already holds. $\square$

The result bounds one uninterrupted saturated episode. It does **not** bound
the total bias over repeated episodes, prove that saturation cannot recur,
or imply a long-run performance ordering. The strict slope-gap condition is
sufficient, not necessary; if it fails, this argument gives no finite bound.

If $\sum_e C_e=KT$, any globally saturated state has $R=C$ by mass
conservation. Therefore requested and admitted signed feedback agree on
every state of such an episode. Comparisons in which the two signals differ
while globally saturated require aggregate capacity below $KT$.

## Corollary: exact cumulative-overflow ordering from balanced requests

Assume the same static Top-$K$ plant and signed-bias update. Suppose the
initial requests are exactly balanced,
\[
R_e(b_0)=n=KT/E\quad\text{for every }e,
\]
and the positive capacities satisfy $C_e\le n$ and
\[
D=KT-\sum_e C_e>0.
\]
Define $u=\operatorname{sign}(\overline C\mathbf1-C)$ as in the theorem and
assume the strict slope gap $u_{(K)}>u_{(K+1)}$. Compare three trajectories
from the same $b_0$: admitted feedback, requested feedback, and no update.
For any horizon $H$ let $J_L(t)=\sum_e(R_e(b_t)-C_e)_+$ denote overflow.
Then
\[
\sum_{t=0}^{H-1}J_R(t)=\sum_{t=0}^{H-1}J_{\mathrm{none}}(t)=HD,
\qquad
\sum_{t=0}^{H-1}J_A(t)\ge HD.
\]
If $\tau$ is the first non-globally-saturated state of the admitted
trajectory, then the inequality is strict for every $H>\tau$, and the
explicit $N$ in the theorem guarantees strictness for every $H>N$.

**Proof.** At $b_0$, requested counts all equal $n$, so their signed
deviation from their mean is zero. The requested controller and no-update
controller therefore remain at $b_0$. Since $C_e\le n$, their admitted
counts are $C_e$ and their overflow is exactly $D$ each round.

For any Top-$K$ request vector, $\sum_e R_e=KT$ and
\[
J_A(t)=KT-\sum_e\min(R_e(b_t),C_e)=KT-\sum_e A_e(b_t).
\]
Consequently
\[
J_A(t)-D=\sum_e(C_e-A_e(b_t))\ge0,
\]
with strict inequality whenever the state is not globally saturated.
Applying the finite-exit theorem gives a first such state by $N$. Summing
the per-state inequalities proves the claims. $\square$

This result applies to the signed integral expert-bias law used by
Megatron-Core, whereas the neighboring proportional-pressure cost theorem
uses a different controller. It is a Top-$K$ family theorem with a
checkable initial-count and capacity-order condition; it is not a universal
ranking for arbitrary initial states, targets, fresh-batch workloads, or
controller laws. A fixed finite affinity instance still has a finite
outcome-map representation, so this corollary alone does not establish a
value separation from an instance-matched adaptive-testing benchmark.

## Exact controlled audit of the cost corollary

[`audit_signed_bias_balanced_cost_corollary.py`](../../scripts/audit_signed_bias_balanced_cost_corollary.py)
constructs a deterministic factorial grid from cyclic Top-$K$ plants. For
each registered $E\in\{3,4,5,6,8\}$ and every $K=1,\ldots,E-1$, it uses
$T=2E$ rows consisting of two copies of all cyclic windows of $K$
consecutive experts. Thus every expert is requested exactly $2K$ times.
The first $K$ experts have capacity $1$ and the remaining experts capacity
$2K$; the admitted-feedback slope is therefore exactly $(+1)^K(-1)^{E-K}$,
with a strict gap at the Top-$K$ cut. Gains are
$\gamma\in\{1/1000,1/16,1/4\}$. Bias, routing, overflow, and the theorem's
exit bound are calculated exactly with rational arithmetic.

All 63 registered $(E,K,\gamma)$ cells passed: initial count balance,
capacity/shortage hypotheses, the strict slope condition, the exact
overflow identity, finite exit by $N$, nonnegative admitted-minus-floor
overflow at every recorded state, and a strict cumulative gap by horizon
$N+1$. For $\gamma=1/1000$, all 21 cells exited at state $500$ under the
declared tie rule and the bound was $501$; for $1/16$, exit was state $8$
with bound $9$; for $1/4$, exit was state $2$ with bound $3$. Two complete
executions reproduced the same output hashes. The machine-readable records
are [`cells.csv`](../../results/signed_bias_balanced_cost_2026-10-18/cells.csv)
and [`summary.json`](../../results/signed_bias_balanced_cost_2026-10-18/summary.json).

This is an exact theorem audit on a structured synthetic family, not a
random-workload study or a runtime measurement. The theorem itself—not the
finite grid—provides the all-static-plants guarantee under its stated
hypotheses.

## Exact controlled plant

Use $E=4$, $K=2$, $T=8$, $C=(1,2,3,3)$, and $\gamma=1/1000$. Affinity is
one on each listed pair and zero on its complement; the eight rows are
\[
(1,2),\quad(1,4),\quad(2,4),(2,4),(2,4),\quad
(3,4),(3,4),(3,4).
\]
The initial requests are $R_0=(2,4,3,7)$, so the plant is globally
saturated and $A_0=C$. The admitted sign is $(+1,+1,-1,-1)$; the requested
sign is $(+1,0,+1,-1)$. For all states $n<500$, every row retains its initial
Top-2 set. At $n=500$, ties resolved by lower expert index give:

| Signal | $R_{500}$ | $A_{500}$ | Overflow at state 500 | Bias at state 500 |
|---|---|---|---:|---|
| Admitted | $(8,8,0,0)$ | $(1,2,0,0)$ | 13 | $(1/2,1/2,-1/2,-1/2)$ |
| Requested | $(8,4,4,0)$ | $(1,2,3,0)$ | 10 | $(1/2,0,1/2,-1/2)$ |

For the admitted arm, the theorem gives $N=501$ and the exact trajectory exits
at $\tau=500$. Under the stated lower-index tie rule, both feedback arms
spend the same 500 saturated states in this base plant, but admitted
feedback's first unsaturated routing state has three more rejected
assignments. Both exits occur at score ties, so this finite cost comparison
is tie-rule-sensitive and is not an open-set robustness result; the
perturbation audit below shows no invariant exit-cost ordering. It is not a
long-run controller ranking.

The exact-rational audit also perturbs every affinity entry by an independent
choice from $\{-1/100,0,1/100\}$ for 20 paired plants and evaluates gains
$\gamma\in\{1/1000,1/500,1/100\}$. All 60 plants retain the same initial
requested and admitted counts, and every admitted exit occurs within the
computed bound. The run and machine-readable output are documented in
[`signed_bias_saturation_exit_results_2026-10-17.md`](signed_bias_saturation_exit_results_2026-10-17.md)
and [`audit_signed_bias_saturation_exit.py`](../../scripts/audit_signed_bias_saturation_exit.py).

## Interpretation boundary

This theorem gives a Top-$K$-specific event-time bound for the exact
signed-bias controller under a checkable slope condition. The theorem is
about a single saturated episode, and its finite affinity-induced outcome
map can still be represented by the general polyhedral benchmark. It does
not establish a novel class-level value separation, a deployment effect, or
the professor report's proposed general windup claim. The useful correction
is narrower and precise: under the strict slope gap, relative bias cannot
grow without bound *while that one episode remains globally saturated*;
once it exits, the resulting allocation can still be poor.

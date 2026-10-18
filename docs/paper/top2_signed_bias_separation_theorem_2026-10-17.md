# Exact admitted-versus-requested result for a Top-2 signed-bias family

**Claim type:** finite-horizon control theorem in the existing requested vs.
admitted Top-K line.  
**Controller:** the signed expert-bias update in `formal_core.md` and
`BiasIntegralFeedback`, not the proportional pressure controller.  
**Evidence:** analytic route-sequence proof, exact replication family, and a
paired rational perturbation audit.

## Theorem

For every integer replication factor $m\ge1$, form a static batch with
$T=20m$, $E=3$, $K=2$, uniform per-expert capacity $C=10m$, and affinity
rows repeated $m$ times from this base multiset:

\[
 (0,5,11/10)\quad(1\text{ row}),\qquad
 (0,101,100)\quad(10\text{ rows}),\qquad
 (2,6/5,0)\quad(9\text{ rows}).
\]

For each token, Top-2 selects the two largest affinity-plus-bias scores,
equivalently omitting the unique lowest-scoring expert. Initialize $b_0=0$.
At each batch, observe $L=R$ (requested) or $L=A=\min(R,C)$ (admitted),
compute
\[
u_e=\operatorname{sign}(\overline L-L_e),\qquad
b^+=P_0(b+\alpha u),
\]
and use scores $a_{t,e}+b_e$. Here $P_0$ subtracts the common mean; it is
routing-equivalent to the unprojected bias update because Top-2 rankings are
unchanged by a common shift. The no-feedback comparator fixes $b$.

For every gain
\[
\boxed{1/5<\alpha<11/40},
\]
the request counts over the first nine batches (indices $0$ through $8$) are
exactly:

| Batch indices | Admitted feedback | Requested feedback | No feedback |
|---|---|---|---|
| $0,1,2$ | $(9,20,11)m$ | $(9,20,11)m$ | $(9,20,11)m$ |
| $3$ | $(10,20,10)m$ | $(9,11,20)m$ | $(9,20,11)m$ |
| $4$ | $(10,20,10)m$ | $(9,20,11)m$ | $(9,20,11)m$ |
| $5$ | $(10,20,10)m$ | $(9,11,20)m$ | $(9,20,11)m$ |
| $6$ | $(10,20,10)m$ | $(9,20,11)m$ | $(9,20,11)m$ |
| $7$ | $(10,20,10)m$ | $(9,11,20)m$ | $(9,20,11)m$ |
| $8$ | $(10,20,10)m$ | $(10,20,10)m$ | $(9,20,11)m$ |

Thus admitted feedback first reaches the globally saturated set at batch 3,
requested feedback at batch 8, and no feedback does not reach it in this
horizon. Since $KT=40m$ and total capacity is $30m$, the minimum possible
per-batch overflow is $10m$. The exact nine-batch cumulative overflows are
\[
\boxed{J_9(A)=93m,\qquad J_9(R)=98m,\qquad J_9(\text{none})=99m.}
\]
The admitted-sign controller therefore saves $5m$ overflow assignments
against requested-sign feedback and $6m$ against no feedback on this
parameterized family and horizon.

## Proof

At zero bias, the omitted experts are 0 for the first eleven rows and 2 for
the remaining nine. Each token requests the other two experts, so
\[
R_0=(9,20,11)m,\qquad A_0=(9,10,10)m.
\]
The admitted mean is $29m/3$, hence its sign vector is $(+1,-1,-1)$. While
this route pattern persists, $b_0-b_2$ increases by $2\alpha$ per update,
while $b_1-b_2$ is unchanged. The special first token has initial
score difference
\[
(a_0+b_0)-(a_2+b_2)=-11/10.
\]
After two admitted updates it is $-11/10+4\alpha<0$ because
$\alpha<11/40$; it still omits expert 0. After three it is
$-11/10+6\alpha>0$ because $\alpha>1/5$; it now omits expert 2. The ten
high-margin rows continue to omit expert 0, and all nine final rows continue
to omit expert 2. Counts become $(10,20,10)m$, so $A=(10,10,10)m$ and the
admitted sign vector is zero. The admitted bias and routes are then fixed.

For requested feedback, the initial mean request is $40m/3$, with sign vector
$(+1,-1,+1)$. The special row's expert-0 versus expert-2 score difference
does not change during these updates. For each of the nine rows initially
omitting expert 2, the expert-1 minus expert-2 score difference is initially
$6/5$ and decreases by $2\alpha$ per update. After two updates it is
$6/5-4\alpha>0$; after three it is $6/5-6\alpha<0$. Consequently those nine
rows change to omit expert 1 at batch 3, giving $(9,11,20)m$. The requested
signs become $(+1,+1,-1)$. One update in this state raises the same score
difference by $2\alpha$, to $6/5-4\alpha>0$, returning those rows to omit
expert 2 at batch 4. The two route-count patterns then alternate through
batch 7.

At every alternating update with signs $(+1,+1,-1)$,
$b_0-b_2$ increases by $2\alpha$; at each intervening baseline update it is
unchanged. The special row therefore has difference $-11/10+4\alpha<0$
through batch 7 and $-11/10+6\alpha>0$ at batch 8. It switches from omitting
expert 0 to omitting expert 2. The counts are then $(10,20,10)m$, the first
globally saturated requested-feedback batch. The ten high-margin rows stay
strictly in their original routes throughout these nine batches.

Before global saturation, each batch has admitted counts $(9,10,10)m$ and
overflow $11m$. From its first globally saturated batch onward, each feedback
arm pays overflow $10m$ in the remaining batches of the nine-batch window.
Admitted feedback pays
$3(11m)+6(10m)=93m$; requested feedback pays $8(11m)+10m=98m$. No feedback
keeps its initial route map and pays $9(11m)=99m$. This proves the stated
identities.

## All-horizon corollary for the same static family

Let $J_H(L)$ denote cumulative overflow over batches $0,\ldots,H-1$ under
the controller observing $L$. The nine-batch route proof above gives an
exact extension without assuming any particular later route sequence for
the requested-feedback controller:

\[
J_H(A)=
\begin{cases}
11Hm,&1\le H\le2,\\
10Hm+3m,&H\ge3,
\end{cases}
\qquad
J_H(\mathrm{none})=11Hm\quad(H\ge1).
\]

The two admitted formulas agree at $H=3$. For requested feedback,
\[
J_H(R)=11Hm\quad(1\le H\le8),
\]
because batches $0$ through $7$ each have overflow $11m$. For every
$H\ge9$, the first eight batches contribute $88m$; every later batch has
overflow at least $KT-\sum_e C_e=10m$. Therefore
\[
J_H(R)\ge 88m+10m(H-8)=10Hm+8m\quad(H\ge9).
\]
Consequently, all three controllers tie through $H=3$, while for every
$H\ge4$ admitted feedback has strictly lower cumulative overflow than both
requested feedback and no feedback. Its advantage over requested feedback
is exactly $(H-3)m$ for $4\le H\le8$, and at least $5m$ for $H\ge9$; its
advantage over no feedback is exactly $(H-3)m$ for every $H\ge4$.

**Proof.** At batch 3 the admitted trajectory reaches
$R=(10,20,10)m$, so $A=(10,10,10)m$. Its feedback is then zero. The bias
and route map remain fixed thereafter, with per-batch overflow $10m$;
before batch 3 the first three batches each cost $11m$. The no-feedback
controller keeps its initial route map, whose overflow is $11m$ each
batch. The requested-feedback costs through batch 7 follow from the table.
For later batches, total demand is $40m$ and total capacity is $30m$, so
overflow cannot be below $10m$, independently of how requests are
distributed. These facts give the displayed formulas and inequalities. ∎

This is an all-horizon comparison for this exact replicated family. It does
not establish a uniform positive *normalized* gap as $H\to\infty$, a
controller-class theorem, or separation from a benchmark that encodes the
finite instance's outcome map. A separate exact-rational audit checks the
closed-loop trajectories through $H=100$ for the registered gain and
replication grid; see
[`top2_all_horizon_results_2026-10-17.md`](top2_all_horizon_results_2026-10-17.md).

The inequalities are strict over the entire open gain interval, so the route
sequence is not a tie-breaking artifact. For the requested arm, the final
rows in batches 3--8 alternate between the two B-row cutoff margins
$6\alpha-6/5$ and $6/5-4\alpha$; both are positive for
$1/5<\alpha<11/40$. The special row remains excluded at batches 0--7 with
margin at least $11/10-4\alpha>0$, then switches at batch 8 with margin
$6\alpha-11/10>0$. The admitted arm's corresponding special-row margins
are $11/10-4\alpha$ through batch 2 and $6\alpha-11/10$ at batch 3. The ten
remaining rows have cutoff margins above 95 throughout the nine batches.
Thus all Top-2 cutoffs are strict on the claimed open interval.

On the compact subinterval $[9/40,1/4]$, the minimum base Top-2 cutoff
margin over all nine batches is exactly $1/10$, attained by the special row.
The experiment scales every affinity and gain by $1/250$, preserving all
routes and count trajectories while placing the gain grid at
`{0.0009,0.00096,0.001}`. In those scaled units the compact interval is
$[9/10000,1/1000]$, the minimum base cutoff margin is $1/2500$, and
entrywise perturbations of at most $1/250000$ can reduce a pairwise score
difference by at most $1/125000$, leaving margin at least $49/125000$. The
robust version and experiment are recorded in
[`top2_signed_bias_separation_protocol_2026-10-17.md`](top2_signed_bias_separation_protocol_2026-10-17.md)
and
[`top2_signed_bias_separation_results_2026-10-17.md`](top2_signed_bias_separation_results_2026-10-17.md).

## Why this addresses the professor's suggestions

This tests the professor's proposed score-ranked dropping explanation without
changing the formal admission rule. Under independent per-expert slots, both
score-ranked and position-ranked retention yield the same count vector
$A_e=\min(R_e,C_e)$; the controller observes counts, so retained token
identities do not alter this theorem. The no-clipping control has $A=R$ and
therefore identical requested/admitted feedback paths. The result also
directly compares the same signed-bias controller under requested,
admitted, and absent feedback, with overflow as the fixed endpoint.

## Claim boundary and benchmark attack

This proves a parameterized, replicated Top-2 example where admitted-sign
feedback is strictly better than requested-sign feedback and no feedback for
the registered finite horizon. It is not a universal ranking, a result for
the proportional gauge-pressure controller, or evidence of trained-model
quality or deployment prevalence. A benchmark that copies the finite
affinity-derived outcome map reproduces this instance exactly, so this theorem
alone does not defeat the existing polyhedral outcome-map reduction. The
remaining conference-level task is to determine whether a broader family
statement with explicit Top-K structure survives that reduction and the
relevant controller prior art. Do not present this result as completing that
task.

# Rejected-load identity for the first requested/admitted route divergence

**Status:** exact lemma plus exact-rational audit. This is a bridge result in
the existing proportional gauge-pressure model. It does not assert which
feedback arm has lower cumulative overflow.

## Setup

Fix one static affinity matrix, Top-$K$ routing with a fixed tie rule,
per-expert capacities, and the canonical admission map
\[
A_e(q)=\min\{R_e(q),C_e\},\qquad J(q)=R(q)-A(q).
\]
Start requested and admitted pressure trajectories from the same state
`q^R_0=q^A_0`, and use the same `eta>0`, `gamma>0`, `delta in [0,1)`, target
`mu`, and min-coordinate gauge projection:
\[
q^L_{t+1}=\Pi_g\!\left((1-\delta)q^L_t+
\eta\gamma\left(\frac{L(q^L_t)}{KT}-\mu\right)\right),
\quad L=R\text{ or }A.
\]

## Exact common-prefix identity

Suppose the two trajectories have identical token-to-expert route sets at
every state `s=0,...,t-1`. They then have the same `R_s`, `A_s`, and `J_s`
at each of those states. For every expert pair `i,j`, define the relative
pressure separation
\[
\Delta_{ij}(t)=
(q^R_{t,i}-q^R_{t,j})-(q^A_{t,i}-q^A_{t,j}).
\]
Then exactly
\[
\boxed{\displaystyle
\Delta_{ij}(t)=\frac{\eta\gamma}{KT}
\sum_{s=0}^{t-1}(1-\delta)^{t-1-s}(J_{s,i}-J_{s,j}).}
\]
For `delta=0` this is the cumulative centered rejected-load contrast. It
shows that the two sensors create the same route choices only while the
accumulated rejected-load differences have not crossed a relevant Top-$K$
score margin.

## First-divergence condition

At state `t`, compare the two score matrices. For a token whose admitted-arm
Top-$K$ set is `S`, and any `i in S`, `j notin S`, let
\[
m_{t,i,j}=(a_{t,i}-\gamma q^A_{t,i})-
(a_{t,j}-\gamma q^A_{t,j}).
\]
The corresponding requested-arm gap is exactly
\[
m^R_{t,i,j}=m_{t,i,j}-\gamma\Delta_{ij}(t).
\]
If `m^R_{t,i,j}>0` for every token and every selected/unselected pair, the
two Top-$K$ route sets are identical at state `t`. If the route sets differ,
at least one such comparison is nonpositive (with equality resolved by the
declared tie rule). Therefore the first route divergence is certified by a
rejected-load contrast reaching a selected/unselected score margin. This is
an exact, Top-$K$-specific route condition; it is not a guarantee that either
trajectory has lower cost.

## Proof

Subtract the two pressure updates at a common-prefix step. For any pair
`i,j`, the gauge projections subtract the same scalar from every coordinate
and hence cancel in coordinate differences. The target terms also cancel:
\[
\Delta_{ij}(s+1)=(1-\delta)\Delta_{ij}(s)+
\frac{\eta\gamma}{KT}\big((R_{s,i}-A_{s,i})-(R_{s,j}-A_{s,j})\big).
\]
Since `Delta_ij(0)=0`, iteration gives the boxed sum. The score-gap formula
follows from `s^L_{t,e}=a_{t,e}-gamma*q^L_{t,e}`. A Top-$K$ set is unchanged
exactly when all its selected scores remain above all unselected scores,
subject to the fixed rule at ties. This proves the stated conditions.

## Exact audit and limits

[`audit_rejected_load_first_divergence.py`](../../scripts/audit_rejected_load_first_divergence.py)
reconstructs the same 40 integer-affinity plants from the facet-to-trajectory
experiment, then checks the identity at every shared-prefix state for each
capacity profile and seed using `Fraction` arithmetic. It also verifies the
selected/unselected score-gap witness at the first divergence, when one occurs
within the 120-state horizon.

This lemma provides a precise trajectory-level diagnostic to replace a static
sampled-facet mismatch fraction when studying the first divergence. It does
not yet predict cumulative overflow after the paths split. A theorem relating
the subsequent sequence of route cells to cost, or a benchmark-robust value
result, remains open; the audit cannot by itself clear the conference-level
novelty gate.

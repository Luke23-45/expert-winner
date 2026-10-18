# Probe-versus-wait value theorem for the E=3 instance

**Date:** 2026-10-16  
**Branch:** `feat/research-censored-feedback`  
**Status:** analytic upper and lower bounds for all causal admitted policies in the fixed two-world instance; exact leading small-step coefficient. This is not yet a novelty result beyond constrained adaptive testing.

## 1. Model and notation

Use the exact E=3, K=1, two-static-world instance and tie rule in
[`phase1_cost_info_lemma_2026-10-16.md`](phase1_cost_info_lemma_2026-10-16.md):
capacities `(50, 50, 30)`, batch size `T=120`, excess load `E_S=20`,
affinity margins `(m,M)=(1,3)`, equal prior, initial pressure zero, and
no pressure leakage (`delta=0`). Take `eta>0`, `gamma>0`, and `B>0`.
The admitted policy may be any causal randomized policy using the full
admitted-observation history and any update satisfying the pressure-reach
constraint. Its objective is expected cumulative raw overflow.

In relative score coordinates `x=gamma(q_1-q_3)`,
`y=gamma(q_2-q_3)`, use the metric

\[
d(z,z')=\sqrt{\frac23\bigl(\Delta x^2-\Delta x\Delta y+\Delta y^2\bigr)}.
\]

The exact reachability equivalence in
[`phase1_h3_dp_reduction.md`](phase1_h3_dp_reduction.md) permits precisely
the transitions satisfying `d(z_t,z_{t+1}) <= beta`, where
`beta=eta*gamma^2*B`. Define

\[
\rho=\frac1{\sqrt2},\qquad D=\sqrt{\frac23},\qquad
n(\beta)=\left\lfloor\frac{\rho}{\beta}\right\rfloor+1.
\]

Let `Z_i` be the zero-overflow pressure set in world `i`, and let
`I={z:A^1(z) != A^2(z)}` be the informative set. Distances to these sets
mean infimum distances; several relevant boundaries are tie boundaries,
so the infimum need not be attained by a zero-cost point.

For the horizon condition, write
\[
n_D=\left\lceil D/\beta\right\rceil,\qquad
n_{D+\rho}=\left\lceil(D+\rho)/\beta\right\rceil.
\]

## 2. First-informative-pressure decomposition

For a deterministic pressure path, let `tau` be the first round whose
admitted vector differs between the two worlds. Before `tau`, the admitted
history is identical in both worlds, so the posterior remains uniform and
the controller follows one common pressure path. At `tau`, the distinct
admitted vector identifies the world exactly. From the next round onward,
the problem is a known-world pressure-control problem.

This decomposition also covers randomized policies: condition on the
controller's private random seed, which is independent of the hidden world;
apply the deterministic argument to each realized policy, then average.
Thus a lower bound for every first-signal
path is a lower bound for every causal randomized admitted policy. The
Bellman recursion in `phase1_h3_dp_reduction.md` is the dynamic-programming
form of the same decomposition.

## 3. Geometric lemma from the exact score cells

The exact 13-row score-cell table gives the following facts:

1. At every uninformative pressure, both worlds have the same overflow,
   at least `E_S`.
2. At every informative pressure, equal-prior expected current overflow
   is at least `E_S`.
3. In either world, every positive overflow is at least `E_S`.
4. The only zero-overflow winner patterns are `(3,1,2,2)` in world 1
   and `(1,1,3,2)` in world 2 (winner indices are one-based).
   Their closures satisfy
   \[
   \overline Z_1\subseteq\{x\ge1,y\le1\},\qquad
   \overline Z_2\subseteq\{x\le1,y\ge1\},
   \]
   and both closures contain `c=(1,1)`.
5. The informative winner patterns are
   `(1,1,1,2)`, `(1,1,3,2)`, `(2,1,2,2)`, `(3,1,2,2)`,
   `(3,1,3,2)`, `(3,1,3,3)`, and `(3,3,3,2)`.

For every informative pressure `z`,

\[
d(0,z)+\frac12d(z,Z_1)+\frac12d(z,Z_2)\ge D,
\tag{G}
\]

and the infimum is exactly `D`.

*Proof.* For the two zero-cost informative cells, `z` lies in the closure
of one zero set. Suppose `z=(1+u,1-v)` with `u,v>=0`, the world-1 case.
The closest point in the opposing quadrant
`{x<=1,y>=1}` is `c`, so
`d(z,Z_2)>=d(z,c)`. The metric norm satisfies the supporting-hyperplane
bound

\[
d(0,z)\ge D+\frac{u-v}{\sqrt6}.
\]

Also `d(z,c)^2=(2/3)(u^2+uv+v^2)`, and hence
`d(z,c)/2 >= (v-u)/sqrt(6)` whenever `v>=u`; when `u>=v` the
supporting term is already nonnegative. Therefore
`d(0,z)+d(z,Z_2)/2>=D`. The world-2 case is symmetric.

The informative cell `(3,1,3,2)` lies in `x>=1,y>=1`, where the
minimum distance from the origin is `d(0,c)=D`. In each of the four
remaining informative cells, the exact winner inequalities imply the
following separating half-plane: `(1,1,1,2)` implies `x<=-3` (from
`L_2` choosing expert 1); `(2,1,2,2)` implies `y<=-3` (from `L_1`
choosing expert 2); `(3,1,3,3)` implies `y>3` (from `H_2` choosing
expert 3); and `(3,3,3,2)` implies `x>3` (from `H_1` choosing expert
3). Minimizing the quadratic form over any corresponding closed
half-plane gives distance at least `3/sqrt(2)>D`. This proves
the lower bound in (G). For tightness, approach `c` from the informative
cell `(3,1,3,2)`. Both zero-set closures contain `c`, so the expression
tends to `D`. The exact winner conditions and costs are in the companion
score-cell table. `\square`

## 4. Theorem: long-horizon admitted value and signal gap

**Theorem.** For every `beta>0` and integer horizon satisfying

\[
H\ge n_D+n_{D+\rho}+3
=\left\lceil\frac{D}{\beta}\right\rceil
+\left\lceil\frac{D+\rho}{\beta}\right\rceil+3,
\tag{H}
\]
the optimal values obey

\[
E_S\frac{D}{\beta}\le V_A(H)
\le E_S\left(\left\lceil\frac{D}{\beta}\right\rceil+2\right),
\qquad
V_R(H)=E_S\left(\left\lfloor\frac{\rho}{\beta}\right\rfloor+1\right).
\tag{V}
\]
The lower bound is against **every** causal randomized admitted policy.
Consequently,

\[
E_S\left(\frac{D-\rho}{\beta}-1\right)
\le V_A(H)-V_R(H)
\le E_S\left(\frac{D-\rho}{\beta}+3\right).
\tag{Gap}
\]
Since `D-rho > 0`, the raw value gap grows as `Theta(1/beta)` as
`beta` decreases, provided the horizon grows at least as in (H).

### Proof: requested value

The nearest zero-overflow region in either known world has infimum distance
`rho` from the origin. Before it is reached, requested feedback can pay no
less than `E_S` per round; the straight-line construction in
[`phase1_parameterized_small_b_2026-10-16.md`](phase1_parameterized_small_b_2026-10-16.md)
reaches an arbitrarily close zero-overflow point in exactly `n(beta)`
updates. Requested feedback identifies the world at the initial pressure.
Thus, when `H>=n(beta)+1`, its value is exactly `E_S*n(beta)`. Condition
(H) implies this horizon condition.

### Proof: admitted lower bound

If the policy never observes an informative vector, every round costs at
least `E_S`; (H) implies `H>=D/beta`, so this is at least
`E_S*D/beta`.

Otherwise let `tau` be the first informative round and `z` its pressure.
The `tau` preceding rounds cost at least `E_S` each; the equal-prior
expected overflow at the informative round is at least `E_S`. The path
constraint gives `tau*beta >= d(0,z)`. If `d(0,z)>=D`, these costs alone
are at least `E_S*D/beta`.

It remains to consider `d(0,z)<D` and `tau<D/beta`; if instead
`tau>=D/beta`, the blind prefix alone proves the claim. Since `tau` is an
integer, `tau<=n_D-1`. For either world,
`d(z,Z_i)<=d(0,z)+rho<D+rho`. The number of rounds after the informative
round is `N=H-tau-1`, and (H) gives
`N>=n_{D+rho}+3>=ceil(d(z,Z_i)/beta)`. Thus the remaining horizon is
long enough to charge the travel lower bound even if the policy uses all
available rounds before reaching a zero-cost point. Reaching `Z_i` from
`z` requires at least `d(z,Z_i)/beta` updates. If it takes `m_i` updates,
there are at least `m_i-1` positive-cost future stages before the first
zero-cost stage; if the horizon ends first, all remaining stages are
positive-cost. Since every positive overflow costs at least `E_S`, the
future expected cost is at least

\[
E_S\left[\frac{d(z,Z_1)+d(z,Z_2)}{2\beta}-1\right].
\]

The `-1` allows for the final update that lands in a zero set. Adding the
prefix and informative-round costs cancels this additive `-1`, yielding

\[
E_S\frac{d(0,z)+\frac12d(z,Z_1)+\frac12d(z,Z_2)}{\beta}
\ge E_S\frac D\beta
\]
by (G). Conditioning on a randomized policy's private seed and averaging
preserves the bound.

### Proof: admitted upper bound

Let `m=ceil(D/beta)` and take `m` equal pressure steps from `(0,0)` to
`c=(1,1)`. The whole segment lies in the common uninformative square, and
each visited round costs `E_S`. Choose sufficiently small `epsilon>0`
and probe at `z_1=(1+epsilon,1-epsilon)`. Its admitted outcomes are
different: world 1 has zero overflow and world 2 has overflow `2E_S`, so
the expected probe-round cost is `E_S` and the observation reveals the
world. If world 1 is present, hold `z_1`. If world 2 is present, move to
`z_2=(1-epsilon,1+epsilon)`, a zero-overflow point for world 2. The
transition distance is `2*sqrt(2)*epsilon`, which is less than `beta` for
small enough `epsilon`. The total expected cost is `E_S*(m+2)`, proving
the upper bound. The horizon condition includes all required rounds.

The gap inequalities follow from
`rho/beta <= n(beta) <= rho/beta+1` and
`D/beta <= ceil(D/beta) <= D/beta+1`. `\square`

At horizons chosen at the scale in (H), the lower bound also gives a
non-vanishing normalized separation as `beta` tends to zero. If
`H=n_D+n_{D+rho}+3`, then
\[
\liminf_{\beta\downarrow0}
\frac{V_A(H)-V_R(H)}{HKT}
\ge \frac{E_S(D-\rho)}{(2D+\rho)KT}>0.
\]
For this instance (`E_S=20`, `K=1`, `T=120`) the right-hand side is
approximately `0.00779`. This statement is only for horizons scaling as
in (H); for horizons growing faster, the normalized lower bound need not
stay positive.

## 5. What this result establishes—and what it does not

This solves the long-horizon probe-versus-wait tradeoff to its exact
leading coefficient for this fixed MoE instance. The coefficient is the
geometric difference

\[
D-\rho=\sqrt{\frac23}-\frac1{\sqrt2}>0,
\]

between (i) the weighted blind-transit/known-world-recovery distance imposed
by the admitted signal and (ii) the known-world distance to a safe routing
cell. It is a pressure-metric/Top-K-score-cell calculation, not a claim
that every admitted controller follows `(A₀)` or the earlier specific
probe path.

The reduction boundary remains decisive. Replacing each pressure cell by
an abstract test with the same two-world outcome, overflow cost, and
`d<=beta` transition relation preserves the Bellman recursion and the
proof above verbatim. Thus this theorem is a quantitative result for a
MoE-induced constrained-testing instance; it does **not** establish a
limitation unavailable to the corresponding generic state-constrained
adaptive-testing model. A conference claim needs a broader theorem whose
sharp constant, scaling, or structure is specific to Top-K/gauge systems
and cannot be transferred unchanged to that abstraction.

The closest primary-source models located so far are adjacent, not exact
matches. Davenport et al. constrain adaptive sensing to a finite set of
measurement vectors and study sparse recovery, rather than continuous
pressure movement with this overflow cost ([paper](https://arxiv.org/abs/1506.05889)).
Li et al. formulate finite- and infinite-horizon Bayesian hypothesis tests
with sensor-usage constraints and different sampling costs, rather than a
metric transition constraint on the selected test
([paper](https://arxiv.org/abs/1601.06447)). Nitinawarat and Veeravalli
study controlled Markovian observations with non-uniform control costs and
asymptotic testing guarantees ([paper](https://arxiv.org/abs/1310.1844)).
These scope differences mean those papers do not, from their stated models,
settle the E=3 specialization. They also do not rescue a novelty claim:
our own exact abstraction already preserves this theorem, so the broader
claim requires a general result or an explicit separation from the best
bound in the corresponding abstract model. This is a scope audit, not a
claim of an exhaustive literature search.

No parameter sweep or experiment was run. The result is analytic and
depends on the exact score-cell table and reach metric cited above.

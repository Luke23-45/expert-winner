# Explicit curvature bound for the swapped-saturation value gap

**Purpose.** The arbitrary-Top-K theorem proves `v_* > 0` by compactness and
inverse-gradient continuity, but leaves `v_*` implicit. This note derives an
explicit lower bound for a registered parameterized subfamily and audits its
size. It does not claim a new benchmark separation or a top-conference
contribution.

## Exact subfamily

Fix `E>=3` and `1<=K<E`. The world-0 Gumbel-Top-K score weights are
`(5/4,1,...,1)`; world 1 swaps the first two. Define capacity fractions `c`
to be the exact Top-K inclusion probabilities at target weights
`(1/2,1/2,1,...,1)`. These are rational because every Plackett-Luce
selection probability is rational for rational weights. The target score is
known exactly modulo common shifts:

```text
theta_c = (log(1/2), log(1/2), 0, ..., 0).
```

The target has `c_1=c_2`; exact-rational enumeration verifies that under
world 0, `p_1>c_1`, `p_2>c_2`, and `p_j<c_j` for every `j>=3` in all
registered `E={3,4,6,8}`, `K in {1,floor(E/2),E-1}` profiles. Scaling by the
least common denominator of `c` gives admissible integer capacity vectors.

## Facet curvature lemma

Let `P_{E,K}={z in [0,1]^E: sum z=K}` and
`Psi(theta)=E[h_{P_{E,K}}(theta+G)]`, where `G` has iid standard Gumbel
coordinates. Work on the common-shift quotient with its Euclidean norm.
The distributional Hessian of the support function is supported on the
normal-fan facets. Each facet is indexed by an unordered pair `{i,j}` and a
set `U` of `K-1` other coordinates that lie above the tied pair; all
remaining coordinates lie below it. Its normal is `e_i-e_j`, and its
quadratic contribution after convolution is

```text
(v_i-v_j)^2 / sqrt(2) * integral_facet product_l g(y_l-theta_l) dH^(E-1)(y),
```

where `g(x)=exp(-x-exp(-x))` is the standard Gumbel density. This follows
from the jump `e_i-e_j` of the support-function gradient across the facet
and the distributional derivative formula for a piecewise-linear convex
function.

Set `D=sqrt(2)*log(5/4)` and `r=D/2`. For a pair `{i,j}`, let
`t0=(theta_c_i+theta_c_j)/2`. Choose `epsilon=0.30` and `g0=0.61`. On the
facet indexed by `{i,j,U}`, take the rectangular patch

```text
y_i=y_j=t in [t0-epsilon,t0+epsilon]
y_u in [max(theta_c_u,t0+g0)-epsilon, max(theta_c_u,t0+g0)+epsilon]  (u in U)
y_v in [min(theta_c_v,t0-g0)-epsilon, min(theta_c_v,t0-g0)+epsilon]  (v outside U union {i,j}).
```

Because `g0>2*epsilon`, this patch lies strictly inside the intended facet.
Its surface measure is `sqrt(2)*(2*epsilon)^(E-1)`.

For any `theta` in the quotient ball `||theta-theta_c||<=r`, define each
coordinate interval

```text
I_l = [a_l-epsilon-theta_c_l-r, a_l+epsilon-theta_c_l+r],
```

where `a_i=a_j=t0`, `a_u=max(theta_c_u,t0+g0)` for `u in U`, and
`a_v=min(theta_c_v,t0-g0)` otherwise. Let

```text+m_l = min(g(left endpoint of I_l), g(right endpoint of I_l))
w_ij = sum over |U|=K-1 of (2*epsilon)^(E-1) * product_l m_l.
```

The Gumbel log-density is concave with its maximum at zero, so its minimum
over an interval occurs at an endpoint. The facet formula therefore gives,
uniformly on this ball,

```text+nabla^2 Psi(theta)[v,v] >= sum_{i<j} w_ij * (v_i-v_j)^2.
```

With `w_min=min_{i<j}w_ij`, the right side is at least
`E*w_min*||v||^2` for every zero-sum `v`, since
`sum_{i<j}(v_i-v_j)^2=E*||v||^2`. Thus `Psi` is strongly convex on the ball
with modulus `m=E*w_min`.

The two world score vectors have quotient distance `D`. For every common
pressure action, at least one of the two resulting score vectors is at
distance at least `D/2` from `theta_c`. Strong convexity on the radius-`D/2`
ball and convex-gradient monotonicity outside it imply, for that world,
`||rho^h(q)-c||_2 >= m*D/2`. Since
`L_h(q)=||rho^h(q)-c||_1/(2K) >= ||rho^h(q)-c||_2/(2K)`, averaging over the
two worlds proves the explicit bound

```text
v_* >= E * w_min * D / (8*K) > 0.
```

This is a quantitative strengthening of the compactness-only positivity
argument for this subfamily. It is not a minimax or multi-round theorem.

## Controlled numerical audit and decision

[`../../scripts/audit_topk_swapped_saturation_explicit_bound.py`](../../scripts/audit_topk_swapped_saturation_explicit_bound.py)
evaluates the stated lower bound using exact rational Plackett-Luce inclusion
fractions and floating-point facet-density calculations. It checks the
strict saturation margins and reports the first approximate admissible
batch scale at which substituting this bound into the existing finite-`T`
inequality makes that inequality positive. The output is explicitly a
floating-point diagnostic, not interval-certified arithmetic. The controlled
count-law experiment already reported in
[`topk_swapped_saturation_value_results_2026-10-17.md`](topk_swapped_saturation_value_results_2026-10-17.md)
tests the associated request/admission predictions across 33 cells; this
calculation is not a replacement for that experiment.

For the registered profile grid, the numerical lower bounds range from
about `2.5e-14` to `2.8e-4`. The finite-batch inequality becomes positive
only at approximate batch sizes from `2.9e7` to `1.0e29`, depending on
`(E,K)`. Thus the explicit proof closes the formal `v_*` gap but does **not**
give a useful finite-scale guarantee. This is evidence against presenting
this bound as the paper's main quantitative result.

The exact adaptive-testing reduction remains unchanged: this is still a
one-step two-world censored decision problem. The bound does not survive as
a separation from that broader benchmark. The next paper-level gate remains
a family result whose quantitative content uses Top-K/gauge structure and
is not implied by the general polyhedral/adaptive-testing model, or a
separately measured system value/cost result.

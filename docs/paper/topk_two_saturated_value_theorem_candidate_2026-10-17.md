# Top-2 two-saturated value gap: theorem candidate in the canonical model

## Status (proof audit: 2026-10-18)

The all-policy theorem and proof are complete for the stated `E=3,K=2`
family. The comparison covers the optimal admitted-signal policy and the
optimal requested-signal policy over **all** gauge-fixed pressure actions.
The common-action constant has the exact rational certificate
`27/200 <= v_* <= 459/3080`; the upper endpoint is a feasible-action value,
not a proved global minimum. The original Hoeffding finite-batch inequality
is rationally certified positive at `T=1680`; a sharper exact-binomial
certificate is positive at `T=540` and exceeds `0.11389` at `T=1680`.
This is a proved MoE-realizable one-step value theorem, not a separation from
generic outcome-costed adaptive testing or a general controller theorem.

## Model and theorem

Let `E=3`, `K=2`, and `T` be a positive multiple of 20. There are two
equally likely static worlds `h in {0,1}`. In each batch, token affinities
are independent standard Gumbel variables, and scores are

```text
s_{t,e} = theta^h_e - q_e + G_{t,e},
theta^0 = (log 2, 0, 0),
theta^1 = (0, log 2, 0).
```

Route each token to its two highest-scoring experts. In the first batch use
`q=0`, observe either the requested count vector `R` or the clipped admitted
vector

```text
A_e = min(R_e,C_e),    C/T = c = (11/20, 11/20, 9/10).
```

The capacities are integral for the registered `T` and sum to `K*T`.
After observing the signal, a deterministic or randomized policy selects an
arbitrary gauge-fixed pressure `q` for a **fresh independent batch** in the
same world. The primary finite-batch cost is expected normalized overflow

```text
ell_{h,T}(q) = (1/T) E[sum_e (X_e-C_e)_+],
X ~ Multinomial over the Top-2 request outcomes at pressure q in world h.
```

Write `V_R(T)` and `V_A(T)` for the minimum equal-prior expected cost over
all such policies based on the full first-batch `R` and `A`, respectively.

For the population request inclusion vector `rho^h(q)`, define

```text
L_h(q) = sum_e (rho^h_e(q)-c_e)_+,
v_* = inf_q 1/2 * (L_0(q)+L_1(q)).
```

Then `v_*>0`, and the following explicit finite-batch bound holds:

```text
V_A(T)-V_R(T)
  >= v_*
     - 2*(2*exp(-T/450) + exp(-361*T/1800))
     - 2*exp(-T/32)
     - 3/(2*sqrt(T)).
```

In particular, for all sufficiently large multiples of 20, the optimal
requested-signal policy has strictly smaller expected realized overflow
than every admitted-signal policy in this declared Top-2 family.

## Proof

### 1. Population routing map and target actions

Work on the quotient `V=R^3/span{1}` and let
`P={x in [0,1]^3 : sum x_e=2}` be the Top-2 hypersimplex. For
`theta in V`, let

```text
Psi(theta) = E[sum of the two largest coordinates of theta+G].
```

The following lemma supplies the needed map properties.

**Lemma.** `Psi` is differentiable and strictly convex on `V`, and
`nabla Psi` is a homeomorphism from `V` onto `relint(P)`.

**Proof.** The support function `h_P(z)=max_{x in P} x dot z` is the sum of
the two largest coordinates of `z`, so `Psi(theta)=E[h_P(theta+G)]`.
Every Top-2 subset has positive probability because the independent Gumbel
density is positive everywhere. Ties have probability zero. The envelope
theorem and dominated convergence therefore give
`nabla Psi(theta)=E[argmax_{x in P} x dot (theta+G)]`, exactly the inclusion
probability vector. This vector lies in `relint(P)` because every subset
has positive probability.

For strict convexity, take distinct quotient points `theta,theta'`. Their
difference is nonconstant, so choose experts `i,j` with unequal coordinate
differences; let `k` be the third expert. There is an open set of affinity
vectors for which expert `k` scores above both `i` and `j`, while the
relative order of `i` and `j` reverses between `theta+G` and `theta'+G`.
The maximizing Top-2 subset then changes from `{k,i}` to `{k,j}`. The
support-function convexity inequality is strict on this open set. Full
support gives it positive probability; averaging proves strict convexity.

For each `c in relint(P)`, consider `F_c(theta)=Psi(theta)-c dot theta`.
Since `c` is interior in `V`, there is `r>0` with `c+r B_V subset P`.
The support-function representation gives
`h_P(theta)-c dot theta >= r||theta||`. Also
`|Psi(theta)-h_P(theta)| <= sqrt(2) E||G||`, because every point of `P`
has Euclidean norm at most `sqrt(2)`. Hence `F_c` is coercive. It has a
unique minimizer by coercivity and strict convexity, and differentiability
gives `nabla Psi(theta_c)=c`. This proves surjectivity; strict convexity
proves injectivity.

To prove continuity of the inverse, let `c_n->c` inside `relint(P)` and
write `theta_n=(nabla Psi)^{-1}(c_n)`. For all sufficiently large `n`, the
points `c_n` share a positive interior-ball radius, so the same coercivity
bound is uniform in `n`. Since `F_{c_n}(theta_n)<=F_{c_n}(0)`, the sequence
`theta_n` is bounded. Every convergent subsequence has a limit mapped to
`c` by continuity of `nabla Psi`; injectivity makes that limit `theta_c`.
Thus the entire sequence converges. `□`

Here the target `c=(11/20,11/20,9/10)` is interior. Direct Plackett-Luce
ranking enumeration gives

```text
nabla Psi(log(1/3,1/3,1)) = c.
```

Thus the target-matching pressures are
`q^0=(log 6,log 3,0)` and `q^1=(log 3,log 6,0)`, and they give zero
population overflow in their corresponding worlds.

### 2. Every common pressure has positive average population cost

Because `sum rho^h=sum c=2`,
`L_h(q)=1/2 * ||rho^h(q)-c||_1`. Suppose for contradiction that `v_*=0`.
There would then be a sequence `q_n` with both `rho^0(q_n)->c` and
`rho^1(q_n)->c`. The inverse-gradient property above implies that both
`theta^0-q_n` and `theta^1-q_n`, modulo common shifts, converge to the same
unique quotient point `theta_c` satisfying `nabla Psi(theta_c)=c`. Their
difference would therefore converge to zero in the quotient. But the fixed
difference `theta^0-theta^1=(log 2,-log 2,0)` is not a common shift. This
contradiction proves `v_*>0`.

This argument proves a strictly positive gap constant; it does not identify
the minimizing common action or give a closed form for `v_*`.

There is also an exact feasible common-action upper bound. Choosing `q^0`
gives the target vector in world 0. In world 1, the adjusted Plackett-Luce
weights are proportional to `(1,4,6)`, whose Top-2 inclusion vector is
`(97/385,46/55,351/385)`. Its overflow is `459/1540`; hence

```text
0 < v_* <= 459/3080.
```

The pilot's bounded numerical search attained the upper endpoint at `q^0`
and its symmetric counterpart `q^1`. This is evidence for equality, not a
global-optimality proof.

### 2.1 Explicit all-pressure lower bound

Represent a pressure action by positive variables `x,y`, so the effective
Plackett-Luce weights in the worlds are `(2x,y,1)` and `(x,2y,1)`. Define

```text
r = 2x/y,       t = 1/y.
```

After scaling weights by a common positive factor, the worlds have weights
`(r,1,t)` and `(r/4,1,t/2)`. Let `d_i(r,t)` denote the probability that
expert `i` is ranked last, equivalently omitted by Top-2. Summing the six
Plackett-Luce ranking probabilities gives

```text
d_1(r,t) = t*(2*r+t+1)/((r+1)*(r+t)*(r+t+1)),
d_2(r,t) = r*t*(r+t+2)/((r+1)*(t+1)*(r+t+1)),
d_3(r,t) = r*(r+1+2*t)/((r+t+1)*(r+t)*(t+1)).
```

Write `z=d_3(r,t)` and `D=d_1-d_2`. Direct simplification gives

```text
|D| = (1-z) * |r-1|/(r+1) * Q(r,t),
Q(r,t) = 1 + 2*r/(r^2+2*r*t+r+t^2+2*t+1) >= 1.
```

For world 1 the same identity uses `(r/4,t/2)`. Define
`g(s)=|s-1|/(s+1)`. A case split at `r=1` and `r=4` gives

```text
g(r)+g(r/4) >= 3/5.
```

For each world `h`, let `z_h` be its omitted-expert-3 probability,
`D_h=d_1^h-d_2^h`, and `b_h=|z_h-1/10|`. The target omitted distribution
is `d*=(9/20,9/20,1/10)`. For any omitted distribution,

```text
TV(d^h,d*) = (max{|D_h|,b_h}+b_h)/2
            >= (|D_h|+b_h)/2.
```

Since `0<=g<=1` and `1-z_h=9/10-(z_h-1/10)`, the displayed identity
implies `|D_h| >= (9/10)g_h-b_h`. Summing the two worlds cancels the
`b_h` terms:

```text
v(q) = (TV(d^0,d*)+TV(d^1,d*))/2
     >= (|D_0|+|D_1|+b_0+b_1)/4
     >= (9/10)*(g(r)+g(r/4))/4
     >= 27/200.
```

This holds for every positive `x,y`; boundary pressure limits follow by
continuity. Therefore the unrestricted common-action value satisfies
`27/200 <= v_* <= 459/3080`.

### 3. Admitted first-batch laws approach one common law

At `q=0`, exact Top-2 probabilities are

```text
rho^0=(5/6,7/12,7/12),
rho^1=(7/12,5/6,7/12).
```

Let `Z_3~Binomial(T,7/12)` and `Q_T` be the law of
`(11T/20,11T/20,Z_3)`. In either world, on

```text
G_h = {R_1 >= 11T/20, R_2 >= 11T/20, R_3 < 9T/10},
```

the admitted vector equals `(11T/20,11T/20,R_3)`, whose reference law is
`Q_T` in both worlds. Each count `R_e` is marginally binomial. Hoeffding's
inequality gives

```text
Pr_h(G_h^c) <= eps(T)
eps(T) = 2*exp(-T/450) + exp(-361*T/1800).
```

The coupling inequality yields `TV(P_h^A,Q_T)<=eps(T)` for both worlds.
Any admitted-signal policy, evaluated under the common observation law
`Q_T`, selects the same action distribution in both worlds and therefore
has population risk at least `v_*`. Normalized overflow is bounded above by
`K=2`, and Jensen's inequality gives `ell_{h,T}(q)>=L_h(q)`. Replacing each
world's admitted law by `Q_T` changes the prior-averaged risk by at most
`2*eps(T)`. Hence

```text
V_A(T) >= v_* - 2*eps(T).
```

### 4. Requested counts identify the world and select its target pressure

Choose world 0 when `R_1/T > 17/24`, and world 1 otherwise. The threshold is
`1/8` from each world's mean `R_1/T` (`5/6` and `7/12`), so each
classification error is at most `exp(-T/32)`. On a correct classification,
use `q^h`. The next-batch marginal count for expert `e` is
`Binomial(T,c_e)`, so its expected normalized positive deviation above the
integer cap is at most `1/(2*sqrt(T))`. Summing over three experts gives
`3/(2*sqrt(T))`. On a classification error the normalized overflow is at
most `K=2`. Therefore

```text
V_R(T) <= 2*exp(-T/32) + 3/(2*sqrt(T)).
```

Combining the admitted lower bound and requested upper bound proves the
theorem. `□`

Substituting the proved all-pressure bound `v_*>=27/200` into the admitted
and requested value bounds gives the explicit certificate

```text
V_A(T)-V_R(T)
  >= 27/200
     - 2*(2*exp(-T/450) + exp(-361*T/1800))
     - 2*exp(-T/32)
     - 3/(2*sqrt(T)).
```

For feasible `T` divisible by 20, this particular Hoeffding-only expression
first becomes positive at `T=1680` in a double-precision scan; its value
there is approximately `0.0027518`. The inequality and rational constant
are proved, while the scan does not certify the minimum threshold. The next
subsection gives a sharper exact-binomial certificate that is positive
already at `T=540`.

### Exact finite-count sharpening

The preceding Hoeffding display is valid but unnecessarily loose. Jensen's
inequality gives `ell_{h,T}(q)>=L_h(q)` for every action, so the admitted
policy incurs no finite-batch approximation penalty when lower-bounding its
population risk. For an exact finite-count bound, define

```text
a_T = Pr[Bin(T,7/12) < 11T/20]
    + Pr[Bin(T,5/6)  < 11T/20]
    + Pr[Bin(T,7/12) >= 9T/10],
h_T = floor(17T/24),
e_0(T) = Pr[Bin(T,5/6) <= h_T],
e_1(T) = Pr[Bin(T,7/12) > h_T],
b_T = (sqrt(99)+3)/(20*sqrt(T)).
```

Here `a_T` is a union bound for failure of the two-saturated clipping event
in either world; `e_0,e_1` are the exact errors of the declared requested
count threshold rule. At a correctly selected target pressure, each fresh
batch count has mean its capacity. Since
`E[(X-E X)_+]=E|X-E X|/2 <= sqrt(Var(X))/2`, summing its three binomial
marginals gives the target-action overflow upper bound `b_T`. Consequently,
for every admissible multiple of 20,

```text
V_A(T)-V_R(T) >= 27/200 - 2*a_T - e_0(T) - e_1(T) - b_T.
```

At `T=540`, all binomial-tail terms are evaluated as exact rational
sums. The square-root term is upper-bounded with the rational certificates
`sqrt(99)<199/20` and `sqrt(540)>232379/10000`. Exact integer arithmetic then
certifies

```text
V_A(540)-V_R(540) > 0.00003401568793520436436864842537567899728547.
```

This is a positive all-pressure, all-policy finite-batch theorem at `T=540`;
it is a certificate, not a claim that 540 is the smallest admissible batch
size. The same exact-tail method certifies a lower bound greater than
`0.1138908062645108654518647134002223945491` at `T=1680`, substantially
stronger there than the Hoeffding-only certificate. The verifier is
[`verify_top2_explicit_common_value_bound.py`](../../scripts/verify_top2_explicit_common_value_bound.py).
The registered simulation still uses `T={1680,1800,3360}`; `T=540` is
proved analytically and was not added to that experiment after seeing its
results.

## Connection to the controlled pilot

The companion [pilot protocol](topk_multisaturated_value_protocol_2026-10-17.md)
and [results](topk_multisaturated_value_results_2026-10-17.md) use the same
worlds and capacities. Its numerical common-action search found risk
`459/3080`; the new proof independently brackets the unrestricted value as
`27/200 <= v_* <= 459/3080`. The controlled sample uses
`T={1680,1800,3360}`, at and above the first positive point of the older
Hoeffding-only certificate; it does not simulate the sharper analytic
`T=540` certificate above.

## Proof-audit record and boundaries

The proof was re-read line by line against the declared cost normalization
and Gumbel-Top-2 model. The audit checked: (i) differentiability and strict
convexity of the expected hypersimplex support function on the common-shift
quotient; (ii) coercivity for interior capacity vectors and continuity of
the inverse inclusion map; (iii) the two-world coupling and its three
binomial tail events; (iv) the requested classifier's `1/8` mean margin and
its exact binomial errors; and (v) the factor of `K=2` in the overflow range
and the resulting finite-batch constants. The independent
symbolic verifier
[`verify_top2_explicit_common_value_bound.py`](../../scripts/verify_top2_explicit_common_value_bound.py)
passes the omission-law identities and all ratio-inequality cases. The
controlled reproduction is documented in
[`top2_explicit_value_gap_experiment_results_2026-10-18.md`](top2_explicit_value_gap_experiment_results_2026-10-18.md).

The exact minimizer of `v_*` is not needed for the stated positive theorem;
proving `v_*=459/3080` would only tighten its constant. No minimal positive
batch threshold is claimed; `T=540` is one exact positive certificate. The
arbitrary-`E,K` theorem is separately stated in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md);
this `E=3,K=2` proof does not substitute for that theorem or assert arbitrary
router/controller generality.

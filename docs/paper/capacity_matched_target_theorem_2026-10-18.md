# Capacity-matched targets separate clipping from signal choice

## Question and scope

The existing one-short-capacity population theorem gives a positive overflow
gap for admitted-count feedback when the controller is still targeting a
uniform expert distribution. This note tests the cause of that gap without
changing the router, capacity rule, or controller update: replace the uniform
target by the normalized capacity vector. The result is a theorem about the
existing proportional-pressure model, not a claim that requested counts are
unobservable or that admitted feedback is universally inferior.

## Model

Fix `E>K>=1`, let `p=K/E`, and use iid token affinities with common CDF `F`
and strictly positive bounded density `f`. For the population dynamics,
capacities are fractions of batch size:

```text
c_s = p-r,
c_r = p+r/(E-1)  (for each of the E-1 rivals),
sum_e c_e = K,
0 < r < min(p, (1-p)/(E-1)).
```

At pressure `q=(0,x,...,x)`, let `P(x)` be the probability that the short-
capacity expert is selected by hard Top-K. Exchangeability gives rival
request probability `Q(x)=(K-P(x))/(E-1)`. The function `P` is continuous,
strictly increasing, with `P(0)=p`, `P(-infinity)=0`, and
`P(+infinity)=1`.

Use the canonical independent per-expert admission rule
`A_e=min(R_e,C_e)` and pressure update

```text
q_next = Pi_g(q + eta * (L/(K*T) - mu)),  L in {R,A},
scores = affinity - q.
```

The two targets compared are uniform, `mu^U_e=1/E`, and capacity-matched,
`mu^C_e=c_e/K`. Set `gamma=1`; with general `gamma`, replace `eta` below by
`eta*gamma`.

## Theorem

Let

```text
L_F = ||f||_infinity * (E-1) * binom(E-2,K-1),
0 < eta <= K*(E-1)/(E*L_F).
```

For either requested or admitted feedback with the capacity-matched target,
the population trajectory remains in the symmetric pressure subspace
`q=(0,x_n,...,x_n)` and obeys a scalar recurrence. Let `x_C` be the unique
solution of `P(x_C)=c_s`. Starting from `x_0=0`, both feedback trajectories
converge monotonically to `x_C`. Their per-token overflow is

```text
g(x_n) = |P(x_n)-c_s|,
```

and therefore tends to zero. In contrast, under the uniform target, requested
feedback stays at `x=0` and incurs overflow `r` per token at every round;
admitted feedback follows the previously proved recurrence and converges to
overflow `E*r` per token.

The exact capacity-target recurrences are:

```text
requested: x_next = x + eta*E/[K*(E-1)] * (c_s-P(x)),
admitted:  x_next = x + eta/K * ((c_s-P(x))_+
                                  - (P(x)-c_s)_+/(E-1)).
```

The theorem does not assert equal transient costs for requested and admitted
feedback. Requested feedback moves `E` times as fast on the side `P(x)>c_s`
in this symmetric population model; admitted feedback has a different slope
after crossing the capacity boundary. The theorem also does not cover finite-
batch infinite-horizon behavior, non-symmetric random pressure fluctuations,
or an optimal policy class.

**Matched-target signal-order corollary.** Under the same gain condition,
both trajectories start at `x_0=0>x_C` and remain in `[x_C,0]`. On this
interval `P(x)>=c_s`, so the requested increment is exactly `E` times the
admitted increment evaluated at the same state. Both scalar update maps are
nondecreasing and fix `x_C`; induction gives
`x_n^R <= x_n^A` for every `n`, strictly for `n>=1`. Since overflow
`P(x)-c_s` is increasing on this interval, requested-feedback population
overflow is no greater than admitted-feedback overflow at every round, with
strict inequality after the first update. Thus the requested direct update
has lower cumulative overflow for every horizon `H>=2` in this
capacity-matched family. This compares the two specified update rules, not
their optimal policy classes.

## Proof

### Population response

For fixed `x`, the short expert's inclusion event is that at most `K-1` of
the `E-1` iid shifted rivals outrank it. Conditioning on its affinity gives

```text
P(x) = integral G_(E,K)(F(y+x)) dF(y),
G_(E,K)(u) = sum_(j=0)^(K-1) binom(E-1,j)(1-u)^j*u^(E-1-j).
```

Differentiation under the integral yields `0<P'(x)<=L_F`. Since `P` ranges
strictly from zero to one and `0<c_s<1`, `x_C` exists uniquely. Also
`x_C<0`, because `P(0)=p>p-r=c_s`.

### Requested feedback, capacity target

The relative-pressure increment `x_next-x` is the rival pressure increment
minus the short expert's. Substituting `Q=(K-P)/(E-1)` and
`mu^C_s=c_s/K`, `mu^C_r=c_r/K` gives

```text
eta/K * ((Q-c_r)-(P-c_s))
  = eta*E/[K*(E-1)] * (c_s-P).
```

Thus the map has derivative
`1-eta*E*P'(x)/(K*(E-1))`, which lies in `[0,1]` under the stated gain
condition. It fixes `x_C`, moves every `x>x_C` downward and every
`x<x_C` upward, and cannot cross the fixed point in one step. Starting from
zero, its iterates decrease monotonically to `x_C`.

### Admitted feedback, capacity target

The expected admitted fractions are
`min(P,c_s)` for the short expert and `min(Q,c_r)` for each rival. Hence

```text
x_next-x = eta/K * ((min(Q,c_r)-c_r) - (min(P,c_s)-c_s)).
```

Mass conservation gives `c_r-Q=(P-c_s)/(E-1)`. Splitting at `P=c_s`
reduces the update to the displayed positive-part recurrence. Its derivative
is `1-eta*P'(x)/K` on the `P<c_s` side and
`1-eta*P'(x)/(K*(E-1))` on the `P>c_s` side. The common gain bound makes
both derivatives nonnegative. Each side points toward `x_C`, so the
trajectory from zero decreases monotonically without crossing `x_C` and
converges to it.

### Overflow and the uniform-target comparison

When `P>=c_s`, the short expert is the only expert above capacity and its
excess is `P-c_s`. When `P<=c_s`, every rival is above capacity by
`(c_s-P)/(E-1)`, giving total excess `c_s-P`. Thus `g(x)=|P(x)-c_s|`.
At the capacity-target equilibrium, this is zero.

Under the uniform target, requested feedback at `x=0` has request fraction
`p` for every expert, so its update is zero and overflow remains
`p-c_s=r`. The admitted-feedback uniform-target recurrence and its limit
`E*r` are exactly those of the existing long-run theorem; no new conclusion
about that recurrence is assumed here. This comparison identifies target
misspecification as sufficient to produce the prior positive gap. It does
not exclude additional effects from the observation channel in other
families.

## Extension: target-by-signal theorem for `m` low-capacity experts

The same symmetric argument extends beyond one short expert. This statement
uses the notation of the existing
[`multiple-low-capacity theorem`](topk_multilow_population_overflow_theorem_2026-10-17.md)
and retains its Top-K router, per-expert clipping, and proportional update.

Let `n=E-m`, `p=K/E`, `h_-=max(K-m,0)/n`, and
`h_+=min(K,n)/n`. Choose

```text
0 < r < min(p-h_-, (1-p)*n/m),
c_L = p-r,        c_H = p + m*r/n.
```

There are `m` low-capacity experts with fraction `c_L` and `n` high-capacity
experts with fraction `c_H`; their total capacity is `K`. On the symmetric
pressure line `q_L=0, q_H=x`, write `h(x)` for the inclusion probability of
each high expert and `ell(x)=(K-n*h(x))/m` for each low expert. Under the
theorem's common iid affinity assumptions, `h` is strictly decreasing from
`h_+` to `h_-`, with `h(0)=p`. The strict margins imply that the two roots

```text
h(x_C)=c_H,     h(x_U)=c_L
```

exist uniquely and satisfy `x_C<0<x_U`. Define
`L_h=sup_{x in [x_C,x_U]} |h'(x)|`; it is finite, and for standard Gumbel
affinities `L_h <= m/e`. If

```text
0 < eta <= m*K/(E*L_h),
```

then the following four-arm population result holds under the unchanged
controller update `q_next=Pi_g(q+eta*(load/(K*T)-mu))`:

1. With the **uniform target**, requested feedback stays at `x=0` and has
   overflow `m*r` per round. Admitted feedback follows
   `x_next=x+eta*(h(x)-c_L)/K`, converges monotonically to `x_U`, and has
   long-run overflow `E*r` per round. Thus its long-run excess over the
   requested arm is exactly `(E-m)*r`.
2. With the **capacity-matched target** `mu_L=c_L/K, mu_H=c_H/K`, the
   requested and admitted recurrences are respectively
   `x_next=x+eta*E/(m*K)*(h(x)-c_H)` and
   `x_next=x+eta/K*(h(x)-c_H)`. Both converge monotonically from zero to
   `x_C`, where population overflow is zero.
3. For the capacity-matched target, requested pressure is no greater than
   admitted pressure at every round and is strictly lower after the first
   update. Since overflow on this interval is `n*(c_H-h(x))`, requested
   feedback has strictly lower cumulative population overflow for every
   horizon `H>=2`. Its relative-pressure step is exactly `E/m` times the
   admitted step at a shared state in `[x_C,0]`.

**Proof.** Symmetry gives `m*ell+n*h=K`. The given strict margins put
`c_L` strictly between `h_-` and `p`, and `c_H` strictly between `p` and
`h_+`: when `n>=K`, use `r<p-h_-<=p` to get `c_H<K/n=h_+`; when `n<K`,
the second margin gives `c_H<1=h_+`. Monotonicity and continuity of `h`
therefore give the two roots with the stated signs.

On `[x_C,0]`, `h<=c_H` and `ell>=c_L`, so the high group is below capacity
and the low group is clipped. The admitted feedback difference between a
high and low coordinate is `(h-c_H)/K`. For requested feedback, the same
difference is
`[(h-c_H)-(ell-c_L)]/K = E(h-c_H)/(m*K)`, using the mass identity and
`c_L+n*c_H/m=K/m`. This gives the two matched-target recurrences. On
`[0,x_U]`, the same clipping pattern holds; the uniform-target admitted
recurrence follows because the common target cancels in the high-minus-low
difference. The derivative bound and the gain condition make each scalar
update map nondecreasing with slope in `[0,1]`; each map points toward its
fixed point and cannot cross it. This proves monotone convergence.

At zero pressure, requested load is uniform, giving overflow `m*r`.
Under the uniform target it therefore does not move. For admitted feedback,
the high-minus-low update is `eta*(h-c_L)/K`; at its root the total overflow
is `n*(c_H-c_L)=E*r`. Under the capacity target, total overflow along the
trajectory is `m*(ell-c_L)=n*(c_H-h)`, which vanishes at `x_C`.

Finally, on `[x_C,0]` both matched-target maps are nondecreasing and fix
`x_C`; at a common state above `x_C`, the requested update is `E/m>1` times
the admitted update toward the fixed point. Induction gives
`x_t^R<=x_t^A`, strictly for `t>=1`. Since `h` decreases in `x`, the
requested arm has no larger overflow, strictly smaller after the first
update. `\square`

This extension is a population theorem. The finite-batch experiment below
was run for `m=1`; the existing multi-low experiment tests the uniform-target
arm across multiple `m`. A paired finite-batch factorial experiment over
multiple `m` is still required before describing this generalized
target-by-signal interaction as experimentally validated.

## Claim boundary

This result is a falsification check on the broad claim that saturation alone
removes admitted feedback's control authority: on the stated one-saturated-
expert trajectory, a capacity-matched target lets the admitted controller
converge to zero population overflow. It does not create a Top-K-specific
separation from adaptive testing. For each fixed finite affinity instance,
the outcome-map benchmark can still reproduce its trajectory. A conference
claim must not present this theorem as resolving that reduction.

The reduction attack is stronger than the finite-instance observation: the
one-dimensional convergence proof itself only uses a strictly increasing
response curve `P` with limits zero and one and a derivative upper bound.
Those are generic monotone-plant assumptions; the proof does not use a
Top-K-specific root-arrangement or token-consistency property. Thus this
theorem is a useful diagnosis and exact MoE realization, but is not yet the
load-bearing Top-K theorem needed for the paper's novelty claim. This
boundary matters because projected integral control and anti-windup for
saturated feedback systems are established control topics; see Hauswirth,
Dörfler, and Teel, [*Anti-Windup Approximations of Oblique Projected
Dynamics for Feedback-based Optimization*](https://arxiv.org/abs/2003.00478).
In MoE balancing, `phi`-Balancing already derives population-level load
objectives and mirror-descent updates; see the [ICML 2026 paper](https://proceedings.mlr.press/v306/chen26br.html).
These are scope neighbors, not claims that either source proves this exact
capacity-clipped recurrence.

The paired finite-batch protocol is in
[`capacity_matched_target_experiment_protocol_2026-10-18.md`](capacity_matched_target_experiment_protocol_2026-10-18.md).

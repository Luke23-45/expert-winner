# Exact one-shot requested-telemetry break-even in the Top-1 E-world family

## Theorem

Fix integers `N>=2`, `s>=1`, and `C>=2s`. Use the existing canonical
identical-block Top-1 E-world construction with `N` regular experts and one
sink, `E=N+1`, `K=1`, `T=NC+s`, uniform prior on the `N` worlds, and
capacities

```text
C_e=C       for each regular expert e,
C_sink=C-s.
```

Use the common initial pressure `q_0=0`, unrestricted subsequent pressure
movement, and overflow `J=||R-A||_1` as the per-round cost. Let `h` be the
number of rounds after the common initial round. At `q_0`, the request vector
in world `i` is `R^i=C*1_N+s*e_i` on regular coordinates, while every world
has the same admitted vector `A^i=C*1_N` and initial overflow `s`.

Let `V_A(h,N)` be the minimum expected post-initial cumulative overflow over
all causal admitted-feedback policies. Then

```text
V_A(h,N) = s * min(h, N-1).
```

Conditional on buying requested telemetry, the total overflow-plus-price is

```text
V_buy^kappa(h,N) = s + kappa.
```

If purchase is optional, skipping it gives the admitted-only optimum, while
buying reveals the world and permits zero future overflow. Thus the optimal
value with the buy/no-buy choice is

```text
V_optional^kappa(h,N)
  = min{s + s*min(h,N-1), s + kappa}
  = s + min{s*min(h,N-1), kappa}.
```

The common initial overflow `s` is included in both alternatives. Therefore
the exact break-even price for this family is

```text
kappa_star(h,N) = s * min(h, N-1).
```

Buying strictly improves on skipping when `kappa < kappa_star`, ties at
equality, and is not worthwhile when `kappa > kappa_star`. At `h=0`,
`kappa_star=0`: a free request observation ties with skipping, and any positive
price makes purchase suboptimal.

## Proof

The request vector at `q_0` identifies `i` from its unique regular coordinate
equal to `C+s`; the admitted vector is identical in every world. After a
requested observation, a zero-overflow pressure for the known world is
reachable because movement is unrestricted. This proves the requested-value
formula.

For admitted feedback, the existing all-pressure Top-1 action-reduction
lemma says that every pressure is weakly dominated by either waiting at the
common-output state (cost `s`) or a canonical subset probe. A probe of a
subset of `b` candidate worlds has the exact inside/outside costs

```text
c_in(1)=0,
c_in(b)=L+(b-2)C       for b>=2,
c_out(b)=L+(b-1)C,
```

where `L=s+C-C_sink=2s`. A singleton probe tests one candidate: it costs
zero if correct and `2s` if incorrect. A probe of size `b>=2` satisfies,
using `C>=2s`,

```text
c_in(b)  >= 2s(b-1),
c_out(b) >= 2sb.
```

The exact Bellman recurrence is

```text
V_0(n)=0,  V_h(1)=0,
V_h(n)=min( s+V_{h-1}(n),
             min_{1<=b<=n} [ b/n*c_in(b)
                +(n-b)/n*(c_out(b)+V_{h-1}(n-b)) ] ),
```

with the outside term omitted when `b=n`.

We prove `V_h(n)=s*min(h,n-1)` by induction on `h`.

For the upper bound, waiting for `h` rounds costs `sh`; this suffices when
`h<=n-1`. When `h>=n-1`, test `n-1` singleton candidates in a fixed order.
Under the uniform prior, the expected number of false tests is `(n-1)/2`,
each costing `2s`; the correct test and all later known-world rounds cost
zero. This gives `s(n-1)`.

For the lower bound, a wait action obeys the induction hypothesis directly.
For a singleton query and `h<=n-1`, its Bellman value is at least

```text
(n-1)/n * (2s+s(h-1))
= s(n-1)(h+1)/n
>= s h,
```

because `h<=n-1`. For `h>=n-1`, it is exactly bounded below by `s(n-1)`.

Now take a probe of size `2<=b<n`, and set `r=n-b`. Its immediate expected
cost is at least `2s*b*(n-1)/n`. If `h<=r`, the continuation lower bound is
`s(h-1)` on the outside branch, so the total is at least

```text
s/n * [2b(n-1)+r(h-1)] >= s h,
```

where the inequality follows from `b>=2` and `h<=r=n-b`. If `h>r`, the
outside continuation is at least `s(r-1)`; combining it with the immediate
cost gives

```text
s/n * [2b(n-1)+r(r-1)] = s(n-1) + s*b*(b-1)/n
>= s(n-1).
```

When `b=n`, all worlds are tested separately at inside cost
`c_in(n)>=2s(n-1)`, which is no smaller than the claimed value. This proves
the lower bound for every subset probe and hence, by the exact action
reduction, for every causal admitted policy. Randomization cannot improve a
Bellman minimum. The two bounds agree, proving the theorem.

## Interpretation and reduction boundary

This is a concrete, closed-form version of Professor Report 1's costed-
observation suggestion, built on the existing Top-1 clipping and feedback
model. It turns the already proved E-world probe cost into an explicit
one-shot requested-telemetry threshold for every `N`, every `h`, and the
stated parameter regime.

The theorem does **not** establish new value beyond the corresponding
costed membership-testing problem: the E-world action reduction gives that
same testing problem and the same Bellman recurrence. It is an exact MoE
family theorem, not a separation from general adaptive testing. The price
`kappa` is an abstract overflow-equivalent penalty, not measured latency,
energy, or collective cost. See the preregistered exact audit in
[`eworld_costed_observation_protocol_2026-10-17.md`](eworld_costed_observation_protocol_2026-10-17.md)
and its [results](eworld_costed_observation_results_2026-10-17.md).

The reduction places the result in costed adaptive decision-tree work, where
tests are selected sequentially and their costs may depend on outcomes; see
[Cicalese, Laber, and Saettler](https://arxiv.org/abs/1309.2796) and the
[value-dependent test-cost model of Saettler, Laber, and Cicalese](https://arxiv.org/abs/1406.3655).
These are scope neighbors, not a line-by-line prior-proof comparison. The
theorem's defensible mathematical content is the Top-1 pressure-to-subset-test
reduction, its capacity-derived outcome costs, and the resulting closed-form
value for this family. This exact threshold alone does not clear the
top-conference novelty gate.

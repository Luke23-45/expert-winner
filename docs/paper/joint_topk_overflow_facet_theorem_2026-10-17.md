# Joint overflow and facet theorem for the canonical Top-K clipping model

## Result

This statement joins two established properties of the same canonical model:
the admitted-versus-requested two-step overflow gap and the non-potentiality
of the admitted feedback field at a regular Top-K facet. Admission remains
per-expert clipping, `A_e=min(R_e,C_e)`.

Fix `E>=3`, `1<=K<E`, and write `p=K/E`. Draw one `T x E` affinity matrix
with iid `Uniform[0,1]` entries and reuse it for both routing steps. Set
`q_0=0`, `gamma=1`, uniform target `mu_e=1/E`, zero leak, and exact-total
capacities

```text
C_1/T = p-r,
C_e/T = p+r/(E-1),  e=2,...,E,
```

along a sequence of batch sizes for which these capacities are integers,
where `0<r<min(p,1-p)`. At step zero, update once using either requested
load `R_0` or clipped admitted load `A_0`, with the canonical proportional
rule

```text
q_1^L = Pi_g(eta * (L_0/(K*T)-mu)),  L in {R,A}.
```

For arm `L in {R,A}` and step `s in {0,1}`, define
`J_s^L=sum_e max(R_{s,e}^L-C_e,0)`. Let
`D_T=(J_0^A+J_1^A-J_0^R-J_1^R)/T`, the admitted-feedback arm's two-step
overflow minus the requested-feedback arm's two-step overflow, normalized
by batch size. For fixed `eta>0`, let `d=eta*r/K` and assume `0<d<1`.
Define

```text
Phi_(E,K)(d)
  = d + integral_d^1 sum_(j=0)^(K-1)
        binom(E-1,j) (1-y)^j y^(E-1-j) dy.
```

Then

```text
D_T -> Phi_(E,K)(d)-K/E > 0 in probability.
```

Moreover, with probability tending to one, the same affinity matrix has a
regular Top-K routing facet at which the canonical admitted feedback field
has a nonzero tangential jump. Consequently,

```text
Pr{ D_T>0 and the admitted field has a regular mismatched facet } -> 1.
```

This is a co-occurrence theorem. It does not assert that the facet mismatch
causes the overflow gap.

## Proof

At zero pressure, exchangeability and the law of large numbers give
`R_{0,e}/T -> p` for each expert. Thus the step-zero requested normalized
error tends to zero. The clipped admitted error tends to
`(-r/K,0,...,0)`. After gauge projection, the limiting pressures are
`q_1^R=0` and `q_1^A=(0,d,...,d)`.

At the admitted pressure, expert 1 is selected with probability
`Phi_(E,K)(d)`. Since `Phi_(E,K)(0)=K/E` and

```text
Phi'_(E,K)(d)
 = Pr{ Binomial(E-1,1-d) >= K } > 0,  0<d<1,
```

the probability is strictly greater than `p`. The other experts are
exchangeable and each has inclusion probability
`(K-Phi_(E,K)(d))/(E-1)<p`. The rival capacities exceed `p`, while the
short expert's capacity is `p-r`. Under requested feedback, the limiting
pressure remains zero and every expert's request fraction is `p`. Therefore
the limiting two-step overflow difference is exactly
`Phi_(E,K)(d)-p`. The step-zero overflow is shared between arms and cancels
from `D_T`; the entire limit comes from the step-one overflow difference.

To obtain convergence in probability, apply the uniform law of large numbers
to the finite-VC class of Top-K winner indicators indexed by pressure in a
compact neighborhood of the limiting pressures. This permits substitution
of the random empirical step-one pressures into the empirical request
fractions. The population winner probabilities are continuous because the
affinity law is continuous and hence has zero probability of a score tie.
The limiting loads are strictly separated from the relevant capacity
thresholds: the short expert is above `p-r` under both arms, and every rival
is below its capacity. Clipping and overflow are therefore continuous at
the limiting loads, giving the asserted convergence in probability. In
particular, the probability that `D_T>0` tends to one.

The unconditioned random-facet theorem for iid continuous affinities applies
to this same exact-total capacity profile: `p-r<p<p+r/(E-1)` and the
distinguished pair can be chosen as expert 1 and any rival. It states that
the probability of at least one regular facet with unequal admitted source
and destination changes tends to one. Let this facet event be `F_T` and the
positive-gap event be `G_T`. No independence is needed:

```text
Pr(F_T and G_T) >= 1-Pr(F_T^c)-Pr(G_T^c) -> 1.
```

This proves same-sample co-occurrence. It does not identify a causal path
from local field geometry to the two-step cost difference. `□`

## Relationship to the preceding results

The overflow limit is the probability-in-limit strengthening of
[`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md).
The facet event is the one-short/equal-rival specialization of
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).
The synthesis uses their common assumptions; it introduces no new admission
map, feedback law, or observation-cost model.

## Claim boundary

The theorem proves a positive two-step gap for the two specified proportional
feedback laws, not superiority over every causal controller. The facet
statement is structural; co-occurrence does not prove mediation or improve
the overflow bound. Neither result establishes a trained-model quality gain,
a measured communication price for requested telemetry, or separation from
an exact finite-instance outcome-map benchmark. Those questions remain
separate gates for the broader paper claim.

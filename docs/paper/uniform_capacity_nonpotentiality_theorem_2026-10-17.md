# Uniform-capacity non-potentiality under iid Top-K affinities

**Status:** analytic asymptotic theorem; finite synthetic audit is specified separately.
**Model:** original hard Top-K router, independent per-expert clipping, and gauge quotient. No device-capacity or score-ranked admission variant is introduced.

## Statement

Fix `E >= 3`, `1 <= K < E`, and integer-feasible batch sizes `T` for which
`C = K*T/E` is an integer. Let the entries of the `T x E` affinity matrix be
iid `Uniform[0,1]`, route each row by hard Top-K on `a_e - gamma*q_e` for a
fixed `gamma > 0`, and use uniform per-expert capacities `C_e=C`. Define the
admitted field on the pressure quotient by

```text
g_A(q) = P_0(K*T*mu - A(q)),    A_e(q) = min(R_e(q), C).
```

Let `F_T` be the number of distinct regular routing facets at which one
request moves from a source expert whose pre-exchange request count is above
capacity to a destination expert whose pre-exchange request count is below
capacity, with the facet pressure within `T^(-3/4)/gamma` (in pairwise
pressure difference) of zero. Then

1. `P(F_T >= c_(E,K) * T^(1/4)) -> 1` for an explicit constant
   `c_(E,K)>0` given below;
2. each counted facet has unequal admitted changes `(d_i,d_j)=(0,1)` and
   therefore a nonzero tangential jump; and
3. the full admitted field is not a continuous cellwise-affine potential,
   hence not a convex subgradient field on the full quotient, with
   probability tending to one.

The exponent `1/4` is the rate of this proof construction, not a claim that
it is optimal. The result is about full random affinity matrices with
**uniform exact-total** capacity. The previously proved `Theta(sqrt(T))`
construction for macroscopically heterogeneous capacities remains stronger
in its own regime and is not replaced by this theorem.

## Proof

Write `p=K/E`, `B=binom(E,2)`, and

```text
c0 = (1/6) * binom(E-2,K-1) * (5/12)^(E-2).
```

All constants below depend only on fixed `E,K`. Use
`epsilon=T^(-3/4)` and `w=T^(1/3)`.

### A. A request-count pair has a robust over/under margin

At zero pressure, each row selects a uniform `K`-subset, independently across
rows. Thus `R_e(0) ~ Binomial(T,p)`, `sum_e R_e(0)=KT=EC`, and the maximum
point probability of each marginal is `O_p(T^(-1/2))`.

If no pair `(i,j)` satisfies
`R_i(0) >= C+w` and `R_j(0) <= C-w`, then every coordinate deviation
`R_e(0)-C` has absolute value at most `Ew`: otherwise the zero-sum identity
forces an opposite-sign coordinate beyond `w`. In particular,

```text
P(no such pair) <= P(|R_1(0)-C| <= E*w) = O_(E,K)(T^(-1/6)),
```

by the binomial anti-concentration bound and `w/sqrt(T)=T^(-1/6)`.

### B. Every directed expert pair has many nearby regular Top-K facets

Fix an ordered pair `(i,j)`. For token `t`, put
`M_t=(a_(t,i)+a_(t,j))/2` and `D_t=a_(t,i)-a_(t,j)`. Call row `t` a
candidate for the directed exchange `i -> j` if

```text
5/12 <= M_t <= 7/12,
0 < D_t <= epsilon,
exactly K-1 of the other E-2 affinities in row t exceed M_t.
```

The joint density of `(M_t,D_t)` is one on this rectangle. Conditional on
`M_t`, the final event has probability
`binom(E-2,K-1)*(1-M_t)^(K-1)*M_t^(E-K-1)`, at least
`binom(E-2,K-1)*(5/12)^(E-2)`. Therefore a row is a candidate with
probability at least `c0*epsilon`; candidate indicators are independent
across rows. A Chernoff bound gives at least
`(c0/2)*T^(1/4)` candidates for this ordered pair except with probability
`exp(-c0*T^(1/4)/8)`.

For each candidate, set the pressure difference so the token's `i` and `j`
scores tie at `M_t`; take the other pressure coordinates equal. The resulting
pressure class is within `epsilon/gamma` in the `i-j` score-difference
coordinate of zero. The candidate token has exactly `K-1` experts above the
tie, so crossing this hyperplane exchanges `i` for `j`. Under continuous
affinities, all other tokens are strict at this pressure almost surely, so
the facet is regular. Candidate values `D_t` are distinct almost surely,
so these are distinct parallel facets.

### C. Most nearby candidates preserve the zero-pressure over/under pair

At a candidate pressure, each score moves by at most `epsilon/2`. A filler
row's Top-K set can change only if one of its `B` affinity pairs is within
`epsilon` of a tie. By a union bound, the probability is at most
`2B*epsilon`. Conditional on the candidate row, filler rows remain
independent; the number `Z_t` of changed filler routes is stochastically
bounded by `Binomial(T-1,2B*epsilon)`, whose mean is at most
`2B*T^(1/4)`.

Since `w/2=T^(1/3)/2` grows faster than this mean, a binomial Chernoff bound
gives

```text
P(Z_t > w/2 | row t is a candidate) <= delta_T,
delta_T = (4*e*B*T^(-1/12))^(T^(1/3)/2) -> 0,
```

for sufficiently large `T` (where the base is below one). The expected
number of bad candidates for a fixed ordered pair is at most `delta_T` times
its expected candidate count. Markov's inequality shows that, with
probability tending to one, at least `(c0/4)*T^(1/4)` candidates for that
pair have `Z_t <= w/2`. A union bound applies to the finite set of ordered
pairs.

On the event in part A, choose an over-capacity source `i` and an
under-capacity destination `j`. For each good candidate of this ordered
pair, the one-sided request counts at its facet differ from the zero-pressure
counts by at most `Z_t`; the distinguished token requests `i` on the minus
side. Thus the source remains above `C` and the destination below `C`:

```text
d_i = min(R_i^-,C) - min(R_i^--1,C) = 0,
d_j = min(R_j^-+1,C) - min(R_j^-,C) = 1.
```

The local facet criterion in
[`admitted_field_facet_criterion_2026-10-17.md`](admitted_field_facet_criterion_2026-10-17.md)
then gives a nonzero tangential jump at every such facet. Since at least one
such regular facet exists with probability tending to one, the full field
cannot have a continuous cellwise-affine potential. This proves all three
claims.

## Interpretation and limits

This closes a specific asymptotic gap in the existing structural result:
non-potentiality is not restricted to a planted facet or to heterogeneous
limiting capacities. It occurs with high probability in the full iid
affinity model under uniform exact-total capacity, and this proof finds a
growing number of regular mismatched facets.

It does **not** prove a closed-loop overflow gap, instability, training-loss
change, serving benefit, observation-cost break-even, or separation from a
benchmark that exactly represents finite outcome maps. It also does not say
that a uniformly sampled facet has the same mismatch rate, or that the
`T^(1/4)` lower bound is tight. The controlled experiment is a finite-size
audit; it is not the proof of the asymptotic theorem.

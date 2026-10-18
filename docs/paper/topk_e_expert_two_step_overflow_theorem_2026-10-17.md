# Arbitrary-Top-K two-step overflow theorem under proportional pressure feedback

## Theorem

Fix integers `E>=2` and `1<=K<E`. Use the canonical routing model with
`gamma=1`, target `mu=1/E`, zero pressure leak, and `q_0=0`. Let the entries
of one static `T x E` affinity matrix be iid `Uniform[0,1]`, and reuse that
same matrix at both routing steps. For each feasible batch size, set exact-
total capacities

```text
C_1/T = K/E - r,
C_e/T = K/E + sigma_e,  e=2,...,E,
sum_{e=2}^E sigma_e = r,
sigma_e >= 0,
0 < r < min(K/E, 1-K/E).
```

Assume the displayed capacities are integers along the sequence of batch
sizes. At step zero, compute `R_0`, `A_0=min(R_0,C)`, and the two canonical
updates

```text
q_1^L = Pi_g(eta * (L_0/(K*T) - mu)),   L in {R,A}.
```

For a fixed `eta>0`, put `d=eta*r/K` and assume `0<d<1`. Define

```text
Phi_(E,K)(d)
  = d + integral_d^1 sum_(j=0)^(K-1)
        binom(E-1,j) (1-y)^j y^(E-1-j) dy.
```

Then

```text
lim_(T -> infinity) E[(J_0^A+J_1^A - J_0^R-J_1^R)/T]
  = Phi_(E,K)(d) - K/E  > 0.
```

Here `J_s^L=sum_e max(R_{s,e}^L-C_e,0)`. The limit is independent of the
split `(sigma_2,...,sigma_E)`. The entire limiting gap is generated at step
one; step-zero routes and costs are shared by the two arms. For `K=1`, the
formula reduces to `d-d^E/E`.

## Proof

At zero pressure, exchangeability and the strong law give
`R_{0,e}/T -> K/E` for every expert. Canonical clipping therefore gives
`A_{0,1}/T -> K/E-r` and `A_{0,e}/T -> K/E` for `e>=2`. The requested
normalized error converges to zero. The admitted normalized error converges
to `(-r/K,0,...,0)`. Applying the gauge projection to the update gives

```text
q_1^R -> (0,...,0),
q_1^A -> (0,d,...,d),  d=eta*r/K.
```

At the limiting admitted pressure, expert 1's score is `U_1`; each competing
score is `U_e-d`. Conditional on `U_1=x`, expert 1 is selected in Top-K
exactly when at most `K-1` of the other `E-1` uniform variables exceed
`x+d`. With `y=x+d`, this yields

```text
P(expert 1 selected)
 = d + integral_d^1 P(Binomial(E-1,1-y) <= K-1) dy
 = Phi_(E,K)(d).
```

At `d=0`, symmetry gives `Phi_(E,K)(0)=K/E`. Differentiating the integral
for `0<d<1` gives

```text
Phi'_(E,K)(d)
 = 1 - sum_(j=0)^(K-1) binom(E-1,j)(1-d)^j d^(E-1-j)
 = P(Binomial(E-1,1-d) >= K) > 0,
```

because `K<E` and `d<1`. Thus the gap is strictly positive. The remaining
experts are exchangeable under the admitted pressure and each receives
`(K-Phi_(E,K)(d))/(E-1) < K/E` assignments per token. Their capacities are
at least `K/E`, so their limiting overflow is zero. Expert 1's admitted-arm
overflow fraction is `Phi_(E,K)(d)-(K/E-r)`. Under requested feedback,
the limiting pressure is zero, each expert receives `K/E`, and the only
limiting overflow fraction is `r` at expert 1. Subtraction gives
`Phi_(E,K)(d)-K/E`.

The same affinity matrix drives the first-step update and second-step
routing. This dependence is handled by uniform convergence of the
finite-VC class of Top-K winner indicators on a compact neighborhood of the
limiting pressure. For fixed `E,K`, each selected-subset indicator is a
finite Boolean combination of affine score comparisons, so this class has
finite VC dimension. Its population probabilities are continuous because
the iid affinities have zero probability of a score tie. Hence the random
updated pressures can be substituted into the empirical second-step loads;
bounded convergence then gives convergence of the expected normalized gap.
\(\square\)

## Scope

This is an arbitrary-fixed-`E,K` two-step family theorem within the existing
Top-K, per-expert-clipping, proportional-pressure model. It is not a result
for every causal controller, every affinity law, or a trained model. It does
not assign a physical communication cost to requested counts or defeat the
exact finite-instance outcome-map reduction. The Top-1 special case and its
registered experiment are in
[`top1_e_expert_two_step_overflow_theorem_2026-10-17.md`](top1_e_expert_two_step_overflow_theorem_2026-10-17.md).

## Extension: arbitrary iid continuous affinities

The Uniform[0,1] assumption is needed for the closed-form polynomial
`Phi_(E,K)`, but not for the positive two-step gap. Let `F` be a continuous,
strictly increasing CDF on the real line, and draw every token-expert affinity
iid from `F`. Keep all other assumptions and the same exact-total capacity
profile. Define

```text
G_(E,K)(u)
  = sum_(j=0)^(K-1) binom(E-1,j) (1-u)^j u^(E-1-j),

p_F(d) = integral G_(E,K)(F(x+d)) dF(x).
```

`G_(E,K)(u)` is the probability that at most `K-1` of `E-1` iid draws
exceed a threshold whose CDF value is `u`. The Top-K inclusion probability
of expert 1 after the admitted-feedback pressure shift `(0,d,...,d)` is
exactly `p_F(d)`. At `d=0`, the probability-integral transform gives
`p_F(0)=integral_0^1 G_(E,K)(u)du=K/E`. Since `F(x+d)>F(x)` for every
`x` and `G_(E,K)` is strictly increasing on `(0,1)`,

```text
p_F(d) > K/E  for every d>0.
```

Consequently, for every fixed `E>=2`, `1<=K<E`, every fixed `eta>0`, and
`r` satisfying the existing capacity constraints, the same two-step
argument gives

```text
lim_(T -> infinity) E[(J_0^A+J_1^A-J_0^R-J_1^R)/T]
  = p_F(eta*r/K) - K/E > 0.
```

The proof is unchanged through the first-step law of large numbers and the
pressure limits. At the second step, conditional on expert 1's affinity
being `x`, each of the `E-1` competitors exceeds it with probability
`1-F(x+d)`, giving the displayed integral. The other experts remain
exchangeable and each has inclusion probability `(K-p_F(d))/(E-1)<K/E`,
so none exceeds its capacity fraction. The requested arm's pressure tends
to zero and has limiting overflow fraction `r`. Uniform convergence of the
finite-VC Top-K winner class over the compact set of reachable pressures
handles reuse of the same affinity matrix at both steps. Normalized overflow
is bounded, so convergence in probability also gives convergence of
expectations.

This extension covers standard Gaussian, logistic, and Gumbel affinity
noise, in addition to Uniform affinities. It remains a two-step asymptotic
comparison for the same specified proportional-pressure controller and
per-expert clipping rule; it does not prove universal controller dominance,
optimality over causal policies, a measured telemetry price, or separation
from the exact outcome-map benchmark.

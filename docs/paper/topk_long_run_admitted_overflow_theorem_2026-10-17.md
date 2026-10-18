# Long-run population overflow under admitted feedback: a Top-K theorem

**Status:** analytic theorem for the canonical proportional-pressure update; controlled finite-batch check follows in a separate protocol. It does not replace or broaden the model in `formal.md`.

## Model and assumptions

Fix `E>=2` and `1<=K<E`, write `p=K/E`, and set the uniform target `mu_e=1/E`, `gamma=1`, and `delta=0`. Each token has iid expert affinities from a common distribution with a strictly positive, bounded density `f` on the real line. One static `T x E` affinity matrix is reused at every routing round. Capacities satisfy, along an integer exact-total sequence,

```text
C_1/T -> p-r,
C_e/T -> p+r/(E-1), e=2,...,E,
sum_e C_e = K*T,
0 < r < min(p, (1-p)/(E-1)).
```

The first expert is under-capacitated; all other capacities are equal and above the symmetric request rate. At each batch, route by hard Top-K scores `a_{t,e}-q_e`, admit `A_e=min(R_e,C_e)`, and update the gauge pressure by

```text
q_next = Pi_g(q + eta * (L/(K*T) - mu)),  L in {R,A}.
```
The same affinity matrix is used by both feedback arms. For each finite horizon, take the large-batch limit first; the long-horizon statement below is an iterated limit, not a claim about infinite-horizon behavior at fixed finite `T`.

## Top-K response curve

Let

```text
G_(E,K)(u)
  = sum_(j=0)^(K-1) binom(E-1,j) (1-u)^j u^(E-1-j),

P_F(x) = integral G_(E,K)(F(y+x)) dF(y).
```

At pressure `q=(0,x,...,x)`, `P_F(x)` is the probability that expert 1 is selected in Top-K: conditional on its affinity `y`, at most `K-1` of the `E-1` shifted competitors may exceed it. We have `P_F(0)=p`, `P_F(x)` is strictly increasing, and `P_F(x)->1` as `x->infinity`.

Differentiating under the integral gives

```text
P_F'(x) = integral G'_(E,K)(F(y+x)) f(y+x) dF(y),
G'_(E,K)(u)
  = (E-1) binom(E-2,K-1) (1-u)^(K-1) u^(E-K-1).
```

Thus `0 < P_F'(x) <= L_F`, where
`L_F = ||f||_infinity * (E-1) * binom(E-2,K-1)`.

## Theorem: admitted-feedback equilibrium and overflow gap

Assume

```text
0 < eta <= K*(E-1)/L_F.
```
Let `x_0=0` and define the scalar recurrence

```text
x_(n+1) = x_n + eta/[K*(E-1)] * ((E-1)*r - (P_F(x_n)-p)).
```

For every fixed finite horizon `H`, the expected normalized cumulative-overflow difference on the reused iid affinity batch satisfies

```text
lim_(T -> infinity) E[sum_(n=0)^(H-1) (J_n^A-J_n^R)/T]
  = sum_(n=0)^(H-1) (P_F(x_n)-p).
```
Here `J_n^L=sum_e max(R_(n,e)^L-C_e,0)` for feedback arm `L`.

The sequence `x_n` is nondecreasing, remains in `[0,x_*]`, and converges to the unique finite `x_*` satisfying

```text
P_F(x_*) = p + (E-1)*r < 1.
```
Consequently,

```text
lim_(H -> infinity) (1/H) * lim_(T -> infinity)
    E[sum_(n=0)^(H-1) (J_n^A-J_n^R)/T]
  = (E-1)*r > 0.
```
The requested-feedback population pressure remains `q=0` and its overflow is `r` per token at every round. The admitted-feedback population pressure has relative state `(0,x_n,...,x_n)`. Its per-round overflow is `r + P_F(x_n)-p`; after convergence it is `E*r` per token. At every round after the first, admitted feedback has strictly more overflow in this population limit.

## Proof

At zero pressure, exchangeability gives request probability `p` for every expert. The law of large numbers and the clipping rule imply admitted fractions `p-r` for expert 1 and `p` for every other expert. Therefore the first admitted update has expert-1 component `-eta*r/K` and zero components elsewhere before gauge normalization, producing relative pressure `(0,eta*r/K,...,eta*r/K)`. The requested update converges to zero.

Suppose the admitted pressure has relative form `(0,x,...,x)` with `x>=0`. By symmetry, expert 1 has request probability `P_F(x)` and every other expert has probability `(K-P_F(x))/(E-1)`. Since `P_F(x)>=p`, the short expert is saturated and each other expert is below its capacity. Their admitted fractions are therefore `p-r` and `(K-P_F(x))/(E-1)`. Subtracting the expert-1 pressure increment from a rival's increment gives

```text
eta/K * ((K-P_F(x))/(E-1) - (p-r))
 = eta/[K*(E-1)] * ((E-1)*r - (P_F(x)-p)),
```

which proves the recurrence and preserves the symmetric-rival form.

The root exists uniquely because `P_F` is continuous, strictly increasing from `p` to `1`, while `p+(E-1)r<1`. The update map has derivative
`1-eta*P_F'(x)/(K*(E-1))` in `[0,1]` by the step-size bound. It is nondecreasing, moves every `x<x_*` upward, and maps `[0,x_*]` into itself. Starting at zero, the iterates increase to `x_*`.

At relative pressure `x>=0`, expert 1 overflows by
`P_F(x)-(p-r)=r+P_F(x)-p`. Rival request rates are at most `p`, below their capacities, so they do not overflow. Requested feedback stays at zero pressure in the population model and incurs only the initial shortage `r`. This yields the per-round gap and the fixed-`H` sum.

For the finite-batch limit, for each fixed `H` all reachable pressures lie in a compact set. The Top-K winner-indicator class indexed by pressure has finite VC dimension. Its empirical request fractions therefore converge uniformly over that set to their population probabilities. The admission map is coordinatewise Lipschitz, so the same uniform convergence holds for admitted fractions. Induction over the fixed number of rounds gives convergence of both feedback trajectories and normalized costs to the displayed population recurrences. Costs per token per round are bounded by `K`, so convergence in probability also gives convergence of expectations. Finally, Cesàro convergence of `P_F(x_n)-p` to `(E-1)r` gives the iterated long-horizon limit. □

## Exact Gumbel special case

For `K=1` and standard iid Gumbel affinities, the random-utility identity gives

```text
P_F(x) = exp(x)/(exp(x)+E-1),
P_F'(x) <= 1/4,
```

and the limiting relative pressure is explicit:

```text
x_* = log((E-1)*(1/E+(E-1)*r)/(1-1/E-(E-1)*r)).
```
For this `K=1` special case, it is sufficient to use the sharper Lipschitz bound `1/4` in the step-size condition, giving `eta<=4*(E-1)`. The theorem above also covers all `K` for standard Gumbel; only `P_F` then uses the displayed Top-K inclusion integral.

## Prior-art boundary

The identity that an uncapacitated random-utility choice-probability vector is the gradient of expected surplus is classical (Williams-Daly-Zachary; see Shi, Shum, and Song, *Econometrica* 86(2), 2018, [DOI](https://doi.org/10.3982/ECTA14115738)). The Gumbel Top-1 softmax formula is also standard. The theorem here uses these request probabilities as an input, then analyzes the closed-loop pressure recursion after canonical per-expert clipping. The claim is the explicit admitted-feedback population recurrence and its overflow limit under this capacity family, not a new random-utility identity or a general theorem about potential-based MoE balancing.

## Scope and relation to current results

This result strengthens the existing two-step comparison to an all-finite-horizon population recurrence and an exact long-run average gap, while retaining the same Top-K routing, per-expert clipping, requested/admitted signals, gauge, and proportional update. It is a result for one explicit asymmetric-capacity family and one fixed controller law. It does not say admitted feedback is universally worse, does not establish finite-`T` infinite-horizon convergence, does not optimize over causal policies, does not measure a requested-count communication surcharge, and does not defeat the exact finite-instance polyhedral outcome-map benchmark. The last limitation remains decisive for the current general control-limitation claim.



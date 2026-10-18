# Top-K swapped-saturation value theorem

**Status:** complete proof for the stated population family and one-step
finite-batch value bound. This is a family theorem within the existing
requested/admitted feedback model. It is not a benchmark-separation or
conference-novelty claim.

## 1. Model and assumptions

There are `E>=3` experts and `1<=K<E`. In world `h`, each token independently
draws iid standard Gumbel noise and requests the `K` largest scores
`theta^h_e-q_e+G_e`. Let `R` be the batch request-count vector and
`A_e=min(R_e,C_e)` the canonical per-expert admitted count. The first batch
uses `q=0`; after seeing either full `R` or full `A`, a policy chooses a
pressure for a fresh independent batch. The two worlds have prior probability
`1/2` each.

World 1 swaps the first two coordinates of world 0:

```text
theta^0_1 > theta^0_2,
theta^1_1 = theta^0_2,  theta^1_2 = theta^0_1,
theta^1_j = theta^0_j  (j>=3).
```

Write `p_e=rho^0_e(0)` for the Top-K inclusion probabilities in world 0.
Assume `p_1>p_2`, `p_1,p_2>x`, and choose an exact-total capacity fraction
`c` satisfying

```text
0 < c_1=c_2=x < min(p_1,p_2),
p_j < c_j < 1                    (j=3,...,E),
sum_e c_e=K.
```

By label-swap symmetry, the world-1 inclusion vector swaps `p_1,p_2` and
leaves every `p_j`, `j>=3`, unchanged. For batch sizes `T` for which every
`C_e=T*c_e` is an integer, define normalized realized overflow

```text
J_T = (1/(K*T)) * sum_e (R_e-C_e)_+.
```

For pressure `q`, let `rho^h(q)` be the population Top-K inclusion vector
and define its population overflow cost

```text
L_h(q) = (1/K) * sum_e (rho^h_e(q)-c_e)_+.
```

Let `V_R(T)` and `V_A(T)` be the minimum expected next-batch `J_T` over all
deterministic or randomized one-step policies based on the entire first
batch vector `R` or `A`, respectively. Pressure actions are unrestricted
modulo common shifts. No observation price is included in these values.

## 2. Theorem

Define the population common-action value

```text
v_* = inf_q  (L_0(q)+L_1(q))/2.
```

Then `v_*>0`. Define the saturation and under-capacity margins

```text
m_1=p_1-x,  m_2=p_2-x,
m_j=c_j-p_j  (j>=3),
Delta=p_1-p_2 > 0,
eps_A(T)=sum_{e=1}^E exp(-2*T*m_e^2),
eps_R(T)=exp(-T*Delta^2/2).
```

For every admissible integer batch size `T`,

```text
V_A(T) >= v_* - eps_A(T)/2 - E/(2*K*sqrt(T)),
V_R(T) <= eps_R(T) + E/(2*K*sqrt(T)),
```

and therefore

```text
V_A(T)-V_R(T)
  >= v_* - eps_A(T)/2 - eps_R(T) - E/(K*sqrt(T)).
```

In particular, the optimal requested-signal policy has strictly lower
expected normalized overflow than every admitted-signal policy for all
sufficiently large admissible `T`. If a requested-count observation has an
additive price `kappa` in these same normalized units, the theorem gives the
sufficient break-even condition

```text
kappa < v_* - eps_A(T)/2 - eps_R(T) - E/(K*sqrt(T)),
```

whenever the right-hand side is positive. This is a sufficient bound, not an
exact hardware-cost break-even result.

## 3. Proof

### 3.1 A common pressure cannot match both capacity targets

Let

```text
P_{E,K}={z in [0,1]^E : sum_e z_e=K}
Psi(theta)=E[ max_{z in P_{E,K}} <z,theta+G> ].
```

The support function in this expectation sums the `K` largest coordinates.
It is 1-Lipschitz in Euclidean norm up to the fixed factor `sqrt(K)`, so
`Psi` is finite and differs from the deterministic support function by a
bounded amount. Ties have probability zero. Differentiation under the
expectation gives

```text
nabla Psi(theta)=E[the Top-K indicator vector at theta+G].
```

Every `K`-subset has positive probability under full-support Gumbel noise,
so this gradient lies in `relint(P_{E,K})`.

On the quotient by common shifts, `Psi` is strictly convex. To see this,
take two quotient-distinct score vectors. Their difference has two
coordinates with unequal increments. There is an open set of noise vectors
for which those two experts straddle the Top-K cutoff at the first score
vector and exchange membership at the second, while the other `K-1` winners
and the remaining losers stay separated. The support-function convexity
inequality is strict on this open set, which has positive probability.
Therefore its expectation is strict.

For each `c` in `relint(P_{E,K})`, the function
`Psi(theta)-<c,theta>` is coercive on the quotient: an interior ball around
`c` lies in `P_{E,K}`, so the support-function gap grows linearly with
`||theta||`, while the Gumbel perturbation changes the support function by
at most a finite constant in expectation. Strict convexity and coercivity
give a unique minimizer `theta_c`, with `nabla Psi(theta_c)=c`. The same
coercivity bound is uniform for capacity vectors in a neighborhood of `c`,
which proves continuity of the inverse gradient there. Thus `nabla Psi` is a
homeomorphism from the score quotient onto `relint(P_{E,K})`.

Suppose `v_*=0`. Then a sequence `q_n` would satisfy
`rho^0(q_n)->c` and `rho^1(q_n)->c`, because equal-total vectors obey
`sum_e (z_e-c_e)_+=||z-c||_1/2`. The inverse-gradient continuity just proved
implies both `theta^0-q_n` and `theta^1-q_n` converge in the quotient to the
unique `theta_c`. Subtracting would force `theta^0-theta^1` to be a common
shift. It is a nonzero coordinate swap, a contradiction. Hence `v_*>0`.

### 3.2 Admitted observations become indistinguishable

Couple the two first-batch worlds by swapping the Gumbel coordinates 1 and
2. This gives `R^1=swap(R^0)` exactly and leaves every outside count
`R_j`, `j>=3`, unchanged. On the event

```text
G_T={R_1^0>=T*x, R_2^0>=T*x,
     R_j^0<=T*c_j for every j>=3},
```

both saturated coordinates clip to `T*x` and every other coordinate is
admitted unchanged. Thus `A^0=A^1` on `G_T`. Each marginal count is
binomial. Hoeffding's inequality and a union bound give
`Pr(G_T^c)<=eps_A(T)`. The coupling inequality therefore yields

```text
TV(P^A_0,P^A_1) <= eps_A(T).
```

For any pressure, replacing finite-batch expected overflow by `L_h(q)` has
uniform error at most `E/(2*K*sqrt(T))`: each request marginal is binomial,
and

```text
| E[(R_e-T*c_e)_+]/T - (rho^h_e(q)-c_e)_+ |
  <= E|R_e/T-rho^h_e(q)| <= 1/(2*sqrt(T)).
```

The population loss is in `[0,1]`. Replacing the world-1 admitted-signal
law by the world-0 law changes prior-averaged population risk by at most
`TV(P^A_0,P^A_1)/2`. Under the resulting common observation law, every
possibly randomized policy chooses the same action distribution in both
worlds, whose average population loss is at least `v_*`. This proves the
stated lower bound on `V_A(T)`.

### 3.3 Requested counts identify the world

Use the classifier that selects world 0 when `R_1>R_2`, world 1 when
`R_1<R_2`, and randomizes on a tie. In world 0, each token's difference
`1{expert 1 selected}-1{expert 2 selected}` lies in `[-1,1]` and has mean
`Delta`. Hoeffding gives error at most `eps_R(T)`; symmetry gives the same
bound in world 1.

Because `c` is in the hypersimplex interior, there is a score vector
`theta_c` with inclusion vector `c`. In world `h`, choose
`q^h=theta^h-theta_c` (modulo a common shift). A correctly classified
requested signal therefore selects a zero-population-overflow action. Its
finite-batch expected normalized overflow is at most
`E/(2*K*sqrt(T))`. On a classification error, normalized overflow is at
most one. This proves the upper bound on `V_R(T)`. Subtracting the two
bounds proves the value-gap inequality. `□`

## 4. Nonempty family for every `E,K`

The assumptions are feasible for every `E>=3`, `1<=K<E`. At equal scores,
all inclusion probabilities equal `K/E`. Choose a rational
`delta>0` small enough that

```text
x=K/E-delta > 0,
y=K/E+2*delta/(E-2) < 1.
```

Set `c_1=c_2=x` and `c_j=y` for `j>=3`; these capacities sum to `K`.
Now perturb the first score by a sufficiently small rational positive
amount, leaving all other scores equal. Continuity of Top-K inclusion
probabilities preserves `p_1,p_2>x` and `p_j<y` for every `j>=3`; strict
ordering of the first two inclusion probabilities follows as well: along
the direction `e_1-e_2`, the expected Top-K utility is an even, strictly
convex function around the equal-score point, so its derivative is positive
for a positive score difference. Swapping the first two scores gives the
second world. Choosing `delta` rational makes all capacities integral on
an infinite arithmetic sequence of batch sizes.

This proves a nonempty arbitrary-`E,K` family, not a universal result for
all score/capacity configurations.

## 5. Scope and outstanding evidence

The theorem is about exact Gumbel Top-K population routing, canonical
per-expert clipping, a two-world one-step decision, and normalized overflow.
It does not establish a multi-round control advantage, the exact value
`v_*`, a hardware cost in comparable units, or a separation from
state-constrained adaptive testing / the existing polyhedral outcome-map
benchmark. The fixed-instance reduction remains a required novelty attack.
The controlled experiment is a consistency check on the theorem's
finite-family predictions; it is not a proof of `v_*>0` or a trained-model
result.

## 6. Asymptotic optimal-value corollary

Fix any admissible family instance and let `T` tend to infinity along batch
sizes for which all `T*c_e` are integral. Then

```text
V_A(T) -> v_*,
V_R(T) -> 0,
V_A(T)-V_R(T) -> v_* > 0.
```

These are optimal one-step values over **all** causal policies using the
respective full first-batch count vectors and choosing unrestricted
pressures for the next independent batch. For the exact arbitrary-`E`
Top-1 family in
[`top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md`](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md),
`v_*=1/36`, so the all-policy optimal-value gap converges to exactly
`1/36`.

**Proof.** Overflow is nonnegative, and the requested upper bound in
Theorem 1 tends to zero, so `V_R(T)->0`. The admitted lower bound in
Theorem 1 gives `liminf V_A(T)>=v_*`, since `eps_A(T)->0` and the
finite-batch approximation term vanishes. For any `epsilon>0`, choose a
fixed common pressure `q_epsilon` with population average loss at most
`v_*+epsilon`. The uniform population-to-finite-batch bound in the proof is
at most `E/(2*K*sqrt(T))`, so this action gives
`limsup V_A(T)<=v_*+epsilon`. Let `epsilon` decrease to zero. Then
`V_A(T)->v_*`, and subtracting the requested limit proves the final
identity. `□`

This is an asymptotic value result; the explicit finite-batch bounds and
registered numerical scales are stated separately. The result remains an
instance of a generic censored Bayesian decision problem, as shown in
[`topk_swapped_saturation_reduction_attack_2026-10-17.md`](topk_swapped_saturation_reduction_attack_2026-10-17.md).

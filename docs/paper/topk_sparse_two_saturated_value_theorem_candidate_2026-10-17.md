# Sparse Top-K two-saturation value gap: family theorem candidate

## Claim and status

This extends the two-saturated admitted-versus-requested value construction
to a parameterized family with `K<E`, using the canonical Top-K router,
per-expert clipping `A=min(R,C)`, and the formal pressure action. For every
`K>=2` and `E>=K+2`, the construction has a strictly positive one-step
expected-overflow value gap for all sufficiently large batches. The
positive limiting constant is proved to exist but is not explicitly
evaluated. This is a mathematical family result, not a novelty clearance or
a real-system claim.

## Construction

Partition the experts into a pair `B={1,2}`, one active reference expert
`3`, `K-1` helper experts `H`, and `L=E-K-2` tail experts `U`. For a finite
weight parameter `M` and positive tail weight `tau`, let the two worlds have
Gumbel location weights

```text
world 0: w_1=2, w_2=1;
world 1: w_1=1, w_2=2;
w_3=1 in both worlds;
w_h=M for h in H;
w_u=tau for u in U.
```

Each token independently routes to the `K` highest scores
`log(w_e)-q_e+G_e`, with independent standard Gumbel `G_e`. A pressure
action is an arbitrary vector modulo common shifts.

Choose capacities as follows:

```text
c_h = 1 - 1/(8(K-1)),           h in H;
c_1 = c_2 = 1/8;
S = 0 if L=0, and S=1/16 if L>0;
c_3 = 7/8 - S;
c_u = S/L,                       u in U when L>0.
```

They satisfy `0<c_e<1` and `sum_e c_e=K`. When `M->infinity` and
`tau->0`, all helpers are selected and all tails are excluded with
probability tending to one. The remaining selection is Top-1 over weights
`(2,1,1)` or `(1,2,1)`, so the limiting active inclusion vectors are

```text
world 0: (1/2,1/4,1/4),
world 1: (1/4,1/2,1/4).
```

The capacities therefore have strict margins in the limit: both pair
experts are saturated, expert 3 and the tails are unsaturated, and every
helper is saturated. By continuity, for every fixed `(E,K)` there exist
finite `M` sufficiently large and `tau` sufficiently small for all those
strict inequalities to hold, with `p_1^0-p_1^1>0`. Fix any such finite
choice. All capacities are rational, so take `T` along multiples of their
common denominator.

## Value theorem candidate

Let `p^h` be the one-token Top-K inclusion vector at the initial pressure
`q=0`; by the construction, `p_1^0>p_1^1`, while `p_e^0=p_e^1` for every
`e not in `{1,2}`. Write

```text
L_h(q)=sum_e (rho^h_e(q)-c_e)_+,
v_* = inf_q 1/2*(L_0(q)+L_1(q)),
Delta = p_1^0-p_1^1 > 0,
margin_e = min_h |p_e^h-c_e| > 0.
```

The infimum is over all gauge-fixed pressure actions. Let `V_R(T)` and
`V_A(T)` be the optimal equal-prior expected **realized normalized overflow**
on a fresh independent batch after observing the full first-batch request
vector `R` or admitted vector `A`, respectively. Then `v_*>0` and

```text
V_A(T)-V_R(T)
  >= v_*
     - K * sum_e exp(-2*T*margin_e^2)
     - K * exp(-T*Delta^2/2)
     - E/(2*sqrt(T)).
```

Consequently, requested-count observation has strictly lower optimal
one-step expected overflow for every sufficiently large feasible `T` in
this family. The theorem compares the optimal policies for the stated
one-step experiment; it is not a multi-round or benchmark-separation result.

## Proof

### Lemma: Top-K surplus coordinates pressure by inclusion probabilities

Let `P={x in [0,1]^E:sum x=K}` and work on
`V=R^E/span{1}`. Define

```text
Psi(theta)=E[h_P(theta+G)],   h_P(z)=max_{x in P} x dot z,
```

where `G` has iid standard Gumbel coordinates. Then `Psi` is differentiable
and strictly convex on `V`, and its gradient is a homeomorphism from `V`
onto `relint(P)`.

**Proof.** Ties among the finitely many Top-K subsets have probability zero.
The envelope theorem and dominated convergence yield
`nabla Psi(theta)=E[x*(theta+G)]`, the vector of Top-K inclusion
probabilities. Every Top-K subset has positive probability by full support,
so this vector lies in `relint(P)`.

Take distinct quotient points `theta,theta'`. Their difference is not
constant; choose `i,j` with unequal coordinate differences. Choose a common
set of `K-1` experts among the other `E-2` coordinates. There is an open set
of affinity vectors for which those `K-1` experts remain above the cutoff,
experts `i,j` exchange order between the endpoints, and all remaining
experts stay below the cutoff. The maximizing Top-K subset changes across
the endpoints on this open set. The support-function convexity inequality
is strict there; full support gives the open set positive probability.
Therefore the expectation `Psi` is strictly convex on `V`.

For any `c in relint(P)`, the function `F_c(theta)=Psi(theta)-c dot theta`
is coercive. Indeed, an interior ball of radius `r>0` around `c` in `V`
lies in `P`, so `h_P(theta)-c dot theta>=r||theta||`. Also
`|Psi(theta)-h_P(theta)|<=sqrt(K) E||G||`, by the Lipschitz bound for the
support function. Thus `F_c` has a unique minimizer and
`nabla Psi(theta_c)=c`. This proves surjectivity; strict convexity proves
injectivity.

For continuity of the inverse, if `c_n->c` in `relint(P)`, their interior
ball radii are bounded below for large `n`. The same coercivity estimate is
then uniform for the minimizers of `F_{c_n}`. Since each minimizer's value
is at most `F_{c_n}(0)`, these minimizers are bounded. Every cluster point
maps to `c`; injectivity makes it `theta_c`. Hence the minimizers converge,
proving continuity. `□`

### Step 1: choose a finite-weight plant with the required saturation pattern

As `M->infinity` and `tau->0`, the `K-1` helpers are all selected and the
tails are never selected, except on events whose probability tends to zero.
The active selection becomes Top-1 Gumbel choice over `(2,1,1)` or
`(1,2,1)`, giving the stated limit probabilities. Each desired saturation
or slack inequality has a strict margin at that limit. Continuity of
Plackett-Luce subset probabilities therefore gives finite `M` and positive
`tau` for which all inequalities hold simultaneously. Fix such a finite
choice. Swapping labels 1 and 2 leaves the joint marginal law on every
coordinate outside the pair unchanged and makes `p_1^0>p_1^1`.

### Step 2: every common pressure action has positive population risk

The displayed capacity vector is interior in the Top-K hypersimplex and
has total `K`. By the lemma, each world has a unique quotient pressure
`q^h` with `rho^h(q^h)=c`. If `v_*=0`, there is a sequence of common
pressures `q_n` with both `rho^0(q_n)->c` and `rho^1(q_n)->c`, since
`L_h(q)=0.5||rho^h(q)-c||_1`. The inverse-gradient continuity in the lemma
forces both `theta^0-q_n` and `theta^1-q_n` to converge to the unique point
`theta_c` mapped to `c`. Their difference would converge to zero in the
quotient. But `theta^0-theta^1` has a positive log-weight difference at
coordinate 1, the opposite difference at coordinate 2, and zero elsewhere;
it is not a common shift. Contradiction. Hence `v_*>0`.

### Step 3: the admitted observation law approaches a common law

Let `S=H union {1,2}` and `U'={3} union U`. In each world, the per-token
request indicators are iid across tokens, so each expert count is marginally
binomial. The joint law of the full count vector restricted to `U'` is
identical across worlds: the two categorical Top-K outcome laws are mapped
to each other by swapping only labels 1 and 2. On the event that all
`e in S` are at or above capacity and all `e in U'` are below capacity,
`A_S=C_S` and `A_{U'}=R_{U'}`. Thus both admitted laws couple to the same
reference law with failure probability at most
`epsilon_T=sum_e exp(-2*T*margin_e^2)` by coordinatewise Hoeffding bounds.

For every pressure, normalized overflow is at most `K`; hence replacing
each world-specific admitted law by the reference law changes prior-average
risk by at most `K*epsilon_T`. On the reference law the policy selects the
same action distribution in both worlds, whose population risk is at least
`v_*`. Jensen gives realized expected overflow at least its population
overflow. Therefore

```text
V_A(T) >= v_* - K*epsilon_T.
```

### Step 4: requested counts choose the right pressure

Classify world 0 when `R_1/T` exceeds `(p_1^0+p_1^1)/2`. Hoeffding bounds
the classification error in either world by `exp(-T*Delta^2/2)`. Use the
corresponding target pressure `q^h`. On correct classification, each next
batch marginal is `Binomial(T,c_e)`, so its expected normalized positive
deviation above capacity is at most `1/(2*sqrt(T))`; summing over `E`
experts gives `E/(2*sqrt(T))`. On a classification error, total rejected
mass per token is at most `K`. Thus

```text
V_R(T) <= K*exp(-T*Delta^2/2) + E/(2*sqrt(T)).
```

Subtracting this upper bound from the admitted lower bound proves the
theorem. `□`

## Important proof details to retain

- The admitted reference law uses the **joint** count vector on all
  unsaturated coordinates. Its equality across worlds follows from the
  label-swap symmetry, not from marginal equality alone.
- Capacities must be strictly interior and exact-total. The displayed
  profile is positive and sums to `K`; for each fixed `(E,K)`, choose finite
  `(M,tau)` only after verifying all strict saturation margins.
- `v_*>0` is qualitative. An explicit lower bound depending on `(E,K,M,tau)`
  is still needed for a useful finite-`T` theorem bound.
- The construction embeds a three-active-expert contest inside Top-K. It
  proves a broad family result, but a reviewer may regard the reduction as
  insufficiently Top-K-specific. A sharper theorem should expose a
  quantitative dependence on Top-K geometry that is absent from generic
  censored testing.

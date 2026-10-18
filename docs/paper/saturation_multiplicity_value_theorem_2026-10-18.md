# Saturation multiplicity controls the value of requested-count feedback

## Claim

This theorem combines two already-motivated parts of the formal research
line: (i) the exact count fiber created by `A_e=min(R_e,C_e)` under Top-K mass
conservation, and (ii) the two-world Gumbel-Top-K decision-value construction
in [`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md).
It identifies the relevant saturation transition: a single clipped
coordinate is recoverable from the full admitted vector, while two
simultaneously clipped coordinates can hide an allocation split with
nonvanishing decision value.

## Main theorem: saturation-multiplicity threshold in decision value

Fix `E>=3`, `1<=K<E`, iid standard-Gumbel Top-K requests, two equally likely
static worlds related by swapping experts 1 and 2, exact-total per-expert
capacities, and a fresh-batch overflow decision after the first-batch signal.
The requested and admitted policies have the same pressure action set and
may use any causal decision rule. Write
`kappa_star(T)=V_A(T)-V_R(T)`, the break-even price for observing requested
counts in units of normalized overflow.

For the registered symmetric pair family in this document, the capacity
split has the following sharp threshold:

1. **One persistently saturated expert per world:** if exactly one member of
   the swapped pair is above capacity in each world and all other experts
   have fixed positive slack, then
   `0 <= kappa_star(T) <= epsilon_1(T) -> 0` exponentially, where
   `epsilon_1(T)` is the decoder-failure bound defined below.
2. **Two persistently saturated experts in both worlds:** if both members of
   the swapped pair are above capacity in each world and all remaining
   experts have fixed positive slack, then
   `kappa_star(T) -> v_*(c)>0`, where `v_*(c)` is the unrestricted
   full-pressure common-action population overflow defined below.
3. **Explicit small-skew coefficient:** along the near-critical symmetric
   family, for every fixed `E,K`,
   `kappa_star(T_n,epsilon_n)/epsilon_n -> j_(E,K)(r_c)/K > 0`
   under the joint margin, skew, and batch-size conditions stated below.
   The coefficient `j_(E,K)` is a finite Plackett-Luce prefix sum and also
   equals a weighted flux through Top-K score-switching facets.

The first two claims are the multiplicity dichotomy; the third quantifies
the two-saturation value and its Top-K geometry. Proofs and the explicit
finite-batch all-policy certificate follow. This theorem is about the
value of a one-step signal for a fresh-batch overflow decision. It does not
assert a long-horizon controller advantage, an exact finite-batch
non-identifiability result, or a separation from the broader
adaptive-testing benchmark.

## Quantitative small-skew theorem for the two-saturation value

The general two-saturation theorem proves `v_*(c)>0` but leaves the constant
implicit. The following result gives its exact first-order dependence on a
small world skew for any smooth Gumbel-Top-K family; the `E=3,K=2` instance
below has a rational leading coefficient.

Let `rho(theta)` be the Gumbel-Top-K population inclusion vector, with `theta`
in the score quotient. Fix an interior capacity vector `c` and let `theta_c`
be its unique inverse image, `rho(theta_c)=c`. Fix a baseline score vector
`theta_bar`, a nonzero quotient direction `d`, and worlds
`theta_±(epsilon)=theta_bar±epsilon*d`. Define the common-action population
value under overflow normalized by `K` as

```text
v_*(epsilon) = inf_q (L_+(q,epsilon)+L_-(q,epsilon))/2,
L_±(q,epsilon) = (1/K) sum_e (rho_e(theta_±(epsilon)-q)-c_e)_+.
```

Then, as `epsilon` decreases to zero,

```text
v_*(epsilon) = epsilon * ||D rho(theta_c) d||_1 / (2*K) + o(epsilon).
```

This is a value theorem, not merely the cost at one selected pressure. Its
proof uses the full pressure action set. At `epsilon=0`, the unique zero-cost
action is `q_0=theta_bar-theta_c` modulo common shifts. Evaluating that action
at `epsilon>0` gives the upper bound with the displayed first-order
coefficient, since
`rho(theta_c±epsilon*d)=c±epsilon*D rho(theta_c)d+o(epsilon)`. For the lower
bound, take any `o(epsilon)`-optimal actions `q_epsilon`. The upper bound
implies both routing vectors approach `c`; continuity of the inverse choice
map then gives `q_epsilon -> q_0`. By the triangle inequality,

```text
v(q_epsilon,epsilon)
  >= ||rho(theta_+(epsilon)-q_epsilon)
       - rho(theta_-(epsilon)-q_epsilon)||_1 / (4*K)
  = epsilon * ||D rho(theta_c)d||_1/(2*K) + o(epsilon).
```

The lower and upper bounds match. The coefficient is positive because the
Gumbel-Top-K choice map has a positive-definite Jacobian on the pressure
quotient.

### Exact `E=3,K=2` coefficient with both swapped experts saturated

Set

```text
c=(11/20,11/20,9/10),
theta_c=(log(1/3),log(1/3),0),
theta_bar=(log(2/3),log(2/3),0),
d=(1,-1,0).
```

The capacity target is exact: `rho(theta_c)=c`. At the initial pressure
`q=0`, the baseline inclusion vector is
`rho(theta_bar)=(43/70,43/70,27/35)`. Thus both first experts exceed their
capacities by `9/140`, while expert 3 is below capacity by `9/70`. These
strict margins persist for all sufficiently small `epsilon>0` in both
swapped worlds, so the admitted first-batch observation aliases the worlds
with exponentially high probability as `T` grows.

For weights `(a,b,c_3)`, the probability that expert 1 is omitted by Top-2
is

```text
1-rho_1 = (b*c_3)/(a+b+c_3) * (1/(a+c_3) + 1/(a+b)).
```

Differentiating at `(a,b,c_3)=(1/3,1/3,1)` along
`(a,b)=((1/3)e^epsilon,(1/3)e^-epsilon)` gives
`D rho(theta_c)d=(39/80,-39/80,0)`. Consequently,

```text
v_*(epsilon) = (39/160)*epsilon + o(epsilon).
```

At initial pressure in the two worlds, the request-count contrast has mean

```text
rho_1(theta_+(epsilon))-rho_2(theta_+(epsilon))
  = (159/175)*epsilon + o(epsilon),
```

so the requested-count sign identifies the world with exponentially small
error for each fixed `epsilon>0`. Combining the existing finite-batch
two-saturation theorem with this coefficient gives the iterated limit

```text
lim_(epsilon down to 0) lim_(T to infinity, 20|T)
  (V_A(T,epsilon)-V_R(T,epsilon))/epsilon = 39/160.
```

The limits are ordered: first batch size tends to infinity at fixed positive
skew, then the skew tends to zero. The corresponding price threshold is in
normalized-overflow units. It is not a measured collective latency or energy
price, and the result remains an exact structured instance of censored
Bayesian testing. It strengthens the C2 family theorem; it does not by itself
clear the independent-benchmark novelty gate.

### Capacity-parameterized coefficient for the symmetric Top-2 family

The rational example extends to every interior symmetric exact-total
capacity profile for `E=3,K=2`. Write

```text
c=(c,c,2-2*c),       1/2 < c < 1.
```

For symmetric pair weights `(r,r,1)`, the inclusion probability of either
pair expert is

```text
x(r) = (4*r^2+3*r+1)/(2*(r+1)*(2*r+1)).
```

Its derivative is
`x'(r)=r*(3*r+2)/((r+1)^2*(2*r+1)^2)>0`, so it is strictly increasing
from `1/2` to `1`. The unique target ratio satisfying `x(r_c)=c` is

```text
r_c = ((6*c-3) + sqrt((6*c-3)^2 + 16*(1-c)*(2*c-1)))
      /(8*(1-c)).
```

Choose a baseline ratio `u>r_c`. At zero pressure, both swapped experts
then exceed capacity by `x(u)-c`, while the third expert is under capacity
by `2*(x(u)-c)`. Define the two worlds by weights
`(u*exp(epsilon),u*exp(-epsilon),1)` and
`(u*exp(-epsilon),u*exp(epsilon),1)`. For all sufficiently small positive
`epsilon`, both pair experts remain saturated in both worlds. Define

```text
j(r) = (5*r^2+4*r+1)/(2*(r+1)^2*(2*r+1)).
```

For weights `(w_1,w_2,w_3)`, the probability expert 1 is last (and thus
omitted) is

```text
lambda_1 = w_2*w_3/(w_1+w_2+w_3)
           * (1/(w_1+w_3) + 1/(w_1+w_2)).
```

Substitute `(w_1,w_2,w_3)=(r*exp(epsilon),r*exp(-epsilon),1)` and
differentiate `rho_1=1-lambda_1` at `epsilon=0`; this gives
`d rho_1/d epsilon=j(r)`. By pair symmetry and conservation of total
inclusion mass, the derivative vector is `(j(r),-j(r),0)`. The full-pressure
common-action value therefore has the explicit capacity-dependent expansion

```text
v_*(epsilon;c) = epsilon*j(r_c)/2 + o(epsilon).
```

The initial requested-count contrast in the positive-skew world is
`2*j(u)*epsilon+o(epsilon)`. For fixed `u>r_c`, the request signal identifies
the world exponentially fast in batch size, while the admitted signals can
be coupled to equality except on an exponentially small unsaturation event.
The existing finite-batch two-saturation comparison then gives

```text
lim_(epsilon down to 0) lim_(T to infinity through admissible batch sizes)
    (V_A(T,epsilon;c,u)-V_R(T,epsilon;c,u))/epsilon = j(r_c)/2.
```

Here `c` is rational and admissible `T` satisfy `T*c` and `T*(2-2*c)` both
integer. This makes the small-skew coefficient explicit over the symmetric
`E=3,K=2` capacity family. It remains a family-specific theorem within the
censored-testing formulation. It does not establish a separation from the
broader adaptive-testing benchmark or a measured systems price. The next
subsection gives a uniform finite-`T` inequality and joint slack/skew/batch
limit. A controlled numerical check is recorded in
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md).

### Explicit finite-batch inequality and joint slack/skew limit

Fix rational `c in (1/2,1)` and admissible `T` such that `T*c` and
`T*(2-2*c)` are integers. Let `u>r_c`, `epsilon>0`, and define

```text
m = min{rho_1(log(u)+epsilon,log(u)-epsilon,0)-c,
        rho_2(log(u)+epsilon,log(u)-epsilon,0)-c},
Delta = rho_1(log(u)+epsilon,log(u)-epsilon,0)
        - rho_2(log(u)+epsilon,log(u)-epsilon,0).
```

Assume `m>0` and `Delta>0`. Let `V_R(T)` and `V_A(T)` be the optimal
equal-prior expected normalized overflow on a fresh batch after observing
the first batch's requested or admitted counts, respectively; the common
first-batch cost is excluded. Then every causal admitted policy, including
randomized policies, obeys

```text
V_A(T)-V_R(T)
  >= (1-2*exp(-2*T*m^2))*v_*(epsilon;c)
     - exp(-T*Delta^2/2) - 3/(2*sqrt(T)).
```

The factor `1-2*exp(-2*T*m^2)` may be replaced by its positive part when a
nonvacuous displayed lower bound is desired. To prove the inequality, couple
the two worlds by swapping experts 1 and 2. Unless one of the pair counts
falls below capacity, the admitted observations coincide; Hoeffding and a
union bound give failure probability at most `2*exp(-2*T*m^2)`. For every
common admitted observation, any action has equal-prior population cost at
least `v_*(epsilon;c)`. Uniformly over pressure and world, the difference
between expected finite-batch normalized overflow and population overflow
is at most `E/(2*K*sqrt(T))=3/(4*sqrt(T))`: each request count is a sum of
`T` Bernoulli indicators, and positive-part clipping is 1-Lipschitz.
Therefore `V_A` is at least the common-event mass times `v_*` minus
`3/(4*sqrt(T))`.

For the requested policy, classify by the sign of `R_1-R_2` and move to the
world's target pressure. The per-token difference lies in `[-1,1]` with mean
`Delta`, so the classification error is at most `exp(-T*Delta^2/2)`. At the
target pressure the population overflow is zero, and expected finite-batch
overflow is at most `3/(4*sqrt(T))`. Subtracting the two value bounds gives
the stated inequality.

This yields a joint limit. Fix `c`; take rational `u_n>r_c` with
`delta_n=x(u_n)-c -> 0`, choose `epsilon_n -> 0` with
`epsilon_n/delta_n -> 0`, and let `T_n` be admissible batch sizes satisfying

```text
T_n*delta_n^2 -> infinity,
T_n*epsilon_n^2 / log(1/epsilon_n) -> infinity.
```

Then `m_n/delta_n -> 1`,
`Delta_n/(2*j(r_c)*epsilon_n) -> 1`, all lower-bound errors are
`o(epsilon_n)`, and the common action `q_0=theta_bar-theta_c` gives the
matching upper bound. Hence

```text
(V_A(T_n,epsilon_n;c,u_n)-V_R(T_n,epsilon_n;c,u_n))/epsilon_n
    -> j(r_c)/2.
```

This is an explicit joint slack/skew/batch-size law for the symmetric
`E=3,K=2` family. The exact finite-instance reduction to costed testing
still applies, so the result is not a class-level separation or a real
telemetry-cost result.

### Costed requested-count observation: exact decision rule and finite-batch bracket

Suppose the admitted vector is available at no extra cost and the controller
may buy the requested vector from the same first batch for price `kappa`,
measured in the same normalized-overflow units as the subsequent decision
loss. Let `V_A(T)` and `V_R(T)` be the optimal values defined above, with the
same first-batch cost excluded. Because an `R`-policy can compute
`A=min(R,C)`, requested feedback weakly dominates admitted feedback:
`0 <= V_A(T)-V_R(T)`. The optimal value when telemetry purchase is optional
is exactly

```text
V_optional(T,kappa) = min{V_A(T), kappa + V_R(T)}.
```

Thus the exact break-even price is

```text
kappa_star(T) = V_A(T)-V_R(T).
```

For any `E>=3`, `1<=K<E`, and parameters in the general symmetric-pair
family above, the finite-batch inequality yields the explicit lower
certificate

```text
kappa_star(T) >= max(0,
  (1-2*exp(-2*T*m^2))*v_*(epsilon;c(r_c))
  - exp(-T*Delta^2/2) - E/(K*sqrt(T)) ),
```

where `m` is the minimum positive saturation margin over the two swapped
experts and `Delta` is their requested-count contrast. A simple upper
certificate is

```text
kappa_star(T) <= v_*(epsilon;c(r_c)) + E/(2*K*sqrt(T)).
```

For the upper bound, choose common actions approaching the population
minimizer defining `v_*`; the uniform difference between expected realized
overflow and population overflow is at most `E/(2*K*sqrt(T))`, while
`V_R(T)>=0`. In the joint slack/skew/batch limit already stated, these
certificates imply

```text
kappa_star(T_n)/epsilon_n -> j_(E,K)(r_c)/K.
```

This is the costed-observation statement supported by the mathematical
model. `kappa` is an abstract overflow-equivalent price. The theorem does
not equate it to an all-reduce latency, energy, or training-time cost; those
require a measurement for a named runtime and a precise replace-versus-add
telemetry implementation. The result is also an exact structured instance
of costed adaptive testing, not a benchmark separation claim.

### General symmetric pair formula for arbitrary `E>=3` and `1<=K<E`

The same proof has a finite-sum form for every Top-K size. Let
`w(r)=(r,r,1,...,1)` and define a top-K ordered prefix `pi=(pi_1,...,pi_K)`
under the Plackett-Luce law by

```text
p_w(pi) = product_(l=1..K)
          w_(pi_l) / (sum_(e not in {pi_1,...,pi_(l-1)}) w_e).
```

For `S` the ordered K-tuples that exclude expert 1, define

```text
x_(E,K)(r) = 1 - sum_(pi in S) p_(w(r))(pi),
y_(E,K)(r) = (K-2*x_(E,K)(r))/(E-2).
```

Thus `x` is each of the first two inclusion probabilities and `y` is the
common inclusion probability of every other expert. For rational `r>0`,
these and the capacity vector
`c(r)=(x,x,y,...,y)` are rational and sum to `K`.
The map `x_(E,K)(r)` is strictly increasing: raising both pair logits moves
their utilities upward relative to the other experts, and the full-support
Gumbel law assigns positive probability to pair/tail score crossings at the
Top-K boundary. Hence every rational baseline `u>r_c` has positive pair
margin `x_(E,K)(u)-x_(E,K)(r_c)`.

There is also a finite exact expression for the directional sensitivity. Set
`v=(1,-1,0,...,0)` and, for each `pi in S`, let

```text
s_pi = sum_(l=1..K) [v_(pi_l)
        - (sum_(e not in {pi_1,...,pi_(l-1)}) w_e*v_e)
          /(sum_(e not in {pi_1,...,pi_(l-1)}) w_e)].
j_(E,K)(r) = -sum_(pi in S) p_(w(r))(pi)*s_pi.
```

The expression for `s_pi` is the derivative of `log p_pi` under
`w_1=r*exp(epsilon)`, `w_2=r*exp(-epsilon)`. Hence
`D rho(w(r))*v=(j,-j,0,...,0)`; pair symmetry makes the tail derivatives
zero. This gives a computable rational number `j_(E,K)(r)>0` for every
rational `r>0`, `1<=K<E`.

Because all `E-2` tail weights are equal, the finite sum reduces to a
two-state recurrence. Let `P_(s,h)` be the probability that the first `s`
selections avoid expert 1 and include expert 2 exactly when `h=1`; then
`m=E-2-s+h` tail experts remain and
`D=r*exp(epsilon)+(1-h)*r*exp(-epsilon)+m`. Initialize
`P_(0,0)=1`, `P_(0,1)=0`. For each `s<K`, propagate

```text
P_(s+1,0) += P_(s,0) * m/D,
P_(s+1,1) += P_(s,1) * m/(r*exp(epsilon)+m),
P_(s+1,1) += P_(s,0) * r*exp(-epsilon)/D.
```

Terms with `m=0` are zero. Then
`x_(E,K)(r,epsilon)=1-P_(K,0)-P_(K,1)` and
`j_(E,K)(r) = d x_(E,K)(r,epsilon)/d epsilon at epsilon=0`.
Differentiating the recurrence by the product rule computes `x` and `j`
in `O(K)` arithmetic operations, rather than enumerating all ordered
prefixes. The prefix sum and recurrence are equivalent descriptions; the
controlled audit compares them on the small grid and uses the recurrence for
larger `E`.

Fix a rational target ratio `r_c>0`, capacities `c(r_c)`, and a rational
baseline ratio `u>r_c`. Let `delta=x_(E,K)(u)-x_(E,K)(r_c)>0`; the two
worlds use weights `(u*exp(epsilon),u*exp(-epsilon),1,...,1)` and its pair
swap. At zero pressure the first two experts are above capacity by `delta`,
and all other experts are below capacity by `2*delta/(E-2)`. For sufficiently
small positive skew, both pair experts remain saturated. The common-action
value and request contrast satisfy

```text
v_*(epsilon;c(r_c)) = epsilon*j_(E,K)(r_c)/K + o(epsilon),
Delta(epsilon) = 2*j_(E,K)(u)*epsilon + o(epsilon).
```

For admissible `T` with integer capacities `T*c(r_c)`, put
`m=min(rho_1^+-c_1,rho_2^+-c_2)>0` and
`Delta=rho_1^+-rho_2^+>0`. The same coupling and concentration proof gives
the all-policy finite-batch bound

```text
V_A(T)-V_R(T)
  >= (1-2*exp(-2*T*m^2))*v_*(epsilon;c(r_c))
     - exp(-T*Delta^2/2) - E/(K*sqrt(T)).
```

For any fixed rational `r_c`, take rational `u_n down to r_c` and
`epsilon_n down to 0` with
`epsilon_n/(x(u_n)-x(r_c)) -> 0`. If admissible batch sizes satisfy
`T_n*(x(u_n)-x(r_c))^2 -> infinity` and
`T_n*epsilon_n^2/log(1/epsilon_n) -> infinity`, then

```text
(V_A(T_n)-V_R(T_n))/epsilon_n -> j_(E,K)(r_c)/K.
```

This is now an explicit parameterized C2 value law for every `E,K`, with
the coefficient given by a finite rational sum rather than an unspecified
positive constant. The formula follows from the ordered-prefix
Plackett-Luce probabilities of standard Gumbel-Top-K routing
([Kool et al., JMLR 2020](https://jmlr.org/papers/v21/19-985.html)). The
law remains a structured family inside costed adaptive testing, so it does
not by itself prove a benchmark separation or close the top-conference
novelty gate.

### Root-facet representation of the C2 coefficient

The same coefficient has a geometric representation that connects the C2
value slope to the actual Top-K decision boundaries. Let
`P={x in [0,1]^E: sum(x)=K}` be the hypersimplex, let
`h_P(z)=max_(x in P) x dot z` be its support function, and define

```text
Phi(s)=E[h_P(s+G)],       G_e iid standard Gumbel,
rho(s)=grad Phi(s).
```

Let `F_{E,K}` be the codimension-one walls of the normal fan of `P`. Each
wall separates two adjacent Top-K subsets `S,S'` that differ by exchanging
one selected expert `a` with one unselected expert `b`; its root normal is
`r_F=1_S-1_S'=e_a-e_b`, with Euclidean norm `sqrt(2)`. With `f_G` the joint
Gumbel density, convolution of the distributional Hessian of the piecewise-
linear support function gives

```text
D rho(s)
  = sum_(F in F_{E,K}) (r_F r_F^T / sqrt(2))
      * integral_F f_G(z-s) dH^(E-1)(z).
```

To see the measure identity, `grad h_P` is the constant vertex `1_S` in
each normal-fan chamber. Across a shared facet, its jump is `r_F` in the
normal direction `r_F/||r_F||`; the distributional derivative of this
piecewise-constant gradient therefore contributes
`r_F r_F^T/||r_F||` times Hausdorff measure on that facet. Summing over all
facets gives `D^2 h_P` as a matrix-valued measure. Convolving it with the
smooth joint density of `G` gives the displayed classical Hessian formula.

At the symmetric pair score `s=(log(r),log(r),0,...,0)` and transfer
direction `d=e_1-e_2`, exchange symmetry implies
`D rho(s)d=j_(E,K)(r)d`. Therefore

```text
j_(E,K)(r)
  = (1/(2*sqrt(2))) * sum_(F in F_{E,K)} (r_F dot d)^2
      * integral_F f_G(z-s) dH^(E-1)(z).
```

Only root facets involving experts 1 or 2 contribute. A wall exchanging 1
and 2 receives weight 4 in `(r_F dot d)^2`; a wall exchanging either one
with a third expert receives weight 1; all other walls contribute zero.
Thus `j/K`, the leading requested-observation price in the joint limit, is
an explicitly weighted flux of Gumbel probability density across the
Top-K switching facets. The Plackett-Luce prefix recurrence and this
root-facet formula are two representations of the same coefficient.

This is the precise C2/C3 connection established here: the value coefficient
is built from the type-A root normals of Top-K switching. It does **not** use
the global region-count bound, establish the professor report's unverified
capacity-signature count, or turn a region count into a value theorem. The
connection strengthens the structural interpretation of the C2 theorem but
does not remove the generic costed-testing reduction or establish
conference-level novelty on its own.

### Exact bridge from root-facet value slope to admitted-mean attenuation

Fix `E>=3`, `1<=K<E`, and the symmetric pair score
`s_r=(log(r),log(r),0,...,0)`. Let `d=e_1-e_2`, so
`D rho(s_r)d=j_(E,K)(r)d`. Give experts 1 and 2 the same integer capacity
`C<T`, and write

```text
alpha_T(x) = Pr[Binomial(T-1,x)<C],
x = rho_1(s_r)=rho_2(s_r).
```

For iid tokens, the marginal request counts satisfy
`R_i~Binomial(T,rho_i)`, and
`d E[min(R_i,C)]/d rho_i=T*alpha_T(rho_i)`. Consequently, at the symmetric
score, the derivative of the normalized requested mean contrast is

```text
d/d epsilon [(rho_1(s_r+epsilon*d)-rho_2(s_r+epsilon*d))/K] at 0
  = 2*j_(E,K)(r)/K,
```

while the admitted mean contrast obeys the exact finite-`T` identity

```text
d/d epsilon [(E[A_1]-E[A_2])/(K*T)] at 0
  = 2*alpha_T(x)*j_(E,K)(r)/K
  = alpha_T(x)/(K*sqrt(2))
      * sum_(F in F_{E,K}) (r_F dot d)^2
          * integral_F f_G(z-s_r) dH^(E-1)(z).
```

The last equality substitutes the root-facet formula above. Thus, in this
pair-transfer direction, the exact gain from requested to admitted **mean
signal sensitivity** is `alpha_T(x)`, and the requested coefficient is a
weighted flux over Top-K switching facets. If `C/T -> c<x`, this gain tends
to zero exponentially in `T`; for every finite `T` and `C>=1`, the full
admitted-count law still identifies each marginal request probability from
`Pr[A_i=0]=(1-rho_i)^T`. The statement is therefore a joint C2/C3 theorem
about local mean sensitivity and value slope, not exact finite-sample
non-identifiability, universal controller windup, or a system-cost result.

A controlled deterministic sweep for `E=3,K=2` checks the equality between
the binomial attenuation, the root-facet flux, and direct finite differences
of the clipped expected counts. The registered 72-cell audit spans
`E in {3,4,8}`, representative `K`, three symmetric pair ratios, and three
batch sizes; its maximum absolute slope errors are `9.59e-11` (requested)
and `5.32e-9` (admitted). Every capacity vector has exact total `K*T`, and
every tail expert is strictly below its capacity in the experiment. Protocol,
results, and raw data are recorded in
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md)
and `../../results/topk_small_skew_scaling_2026-10-18/root_facet_clipping_attenuation.csv`.

### Expert-count scaling of the coefficient

The finite-sum coefficient has two distinct large-`E` regimes. Fix pair
weight ratio `r>0`.

**Proportional Top-K.** If `K/E -> alpha` for a fixed `alpha in (0,1)`, then

```text
j_(E,K)(r) -> r*(-log(1-alpha))*(1-alpha)^r,
j_(E,K)(r)/K
  ~ r*(-log(1-alpha))*(1-alpha)^r / (alpha*E).
```

For a proof, represent the Plackett-Luce ranking as increasing independent
exponential clocks with rates equal to the weights. Condition on expert 1's
clock time `t`. Among the `E-2` unit-weight tail experts, the number of
clocks before `t` is `Binomial(E-2,1-exp(-t))`; expert 2 contributes one
additional Bernoulli clock. As `K/E -> alpha`, the Top-K threshold converges
to `t_alpha=-log(1-alpha)`. The derivative of expert 1's inclusion
probability with respect to its own log weight converges to
`r*t_alpha*exp(-r*t_alpha)`. The derivative contribution through expert 2's
threshold indicator is the probability mass at the binomial cutoff and
vanishes as `E` grows. This gives the displayed limit.

**Near-full Top-K.** For `K=E-1`, put `N=E-2` and let
`B(a,b)=Gamma(a)Gamma(b)/Gamma(a+b)` be the beta function. Exponential-race
conditioning gives the exact omitted-expert probability

```text
lambda_1(a,b)=a*(B(a,N+1)-B(a+b,N+1)),
```

when expert 1 has rate `a`, expert 2 has rate `b`, and the `N` tails have
rate 1. Differentiating at `a=b=r` along `a=r*exp(epsilon)` and
`b=r*exp(-epsilon)` yields

```text
j_(E,E-1)(r)
  = r^2*B(r,N+1)*(psi(r+N+1)-psi(r))
    - r*(B(r,N+1)-B(2*r,N+1)),
```

where `psi` is the digamma function. Therefore

```text
j_(E,E-1)(r)/(E-1)
  ~ r*Gamma(r+1)*log(E)/E^(r+1).
```

For `r=1`, the exact simplification is
`j_(E,E-1)(1)=H_(E-1)/(E-1)-1/E`, where `H_n` is the nth harmonic number.
Thus the per-overflow-unit value slope vanishes as `Theta(1/E)` when `K/E`
stays in `(0,1)`, and even faster when `K=E-1`. This is a scaling
prediction of the symmetric Gumbel-Top-K family; it also warns that a
positive information-value gap at fixed `E` need not remain practically
large as expert count grows. The large-`E` numerical audit is recorded with
the controlled experiment results.

## Exact finite-count fiber lemma

Fix a request vector `R in N^E` with `sum_e R_e=K*T`, capacities
`C in N^E`, and admitted counts `A_e=min(R_e,C_e)`. Define

```text
S(A) = {e : A_e=C_e},       d(A)=K*T-sum_e A_e.
```

Then `d(A)=sum_e(R_e-A_e)` is the total rejected assignment count. Every
request vector in the fiber of `A` has `R_e=A_e` for `e not in S(A)` and
`R_e=C_e+x_e` for `e in S(A)`, where `x_e` are nonnegative integers with
`sum_(e in S(A)) x_e=d(A)`. If `d(A)>0`, the fiber cardinality is

```text
binom(d(A)+|S(A)|-1, |S(A)|-1).
```

If `d(A)=0`, the fiber is a singleton (`R=A`). Thus an admitted vector with
at most one capped coordinate always determines the entire request vector.
For `d(A)>0` and `|S(A)|>=2`, it has multiple request preimages. The
dimension of the corresponding continuous allocation simplex is
`|S(A)|-1`.

*Proof.* On unsaturated coordinates `A_e<C_e`, clipping implies `R_e=A_e`.
On saturated coordinates write `R_e=C_e+x_e` with `x_e>=0`. Summing and
using `sum R=K*T` gives the displayed composition constraint. The number of
weak compositions is the stars-and-bars expression. If the total excess is
zero, all `x_e=0`. ∎

## One-saturation value upper bound

Consider a finite two-world decision problem. The first batch gives `R` or
`A`; after observing it, a causal policy selects an action for a fresh batch.
Both policies use the same action set and have loss in `[0,1]`. Let `V_R(T)`
and `V_A(T)` be their optimal prior-averaged losses. Since `A` is a
deterministic function of `R`, `V_R(T)<=V_A(T)`.

Suppose in each world `h` there is one expert `i_h` whose request mean is
above capacity, while every other expert has request mean `p^h_j<C_j/T`.
Write `m^h_j=C_j/T-p^h_j>0` for `j != i_h`. Requests are sums of `T`
independent Top-K inclusion indicators, so Hoeffding gives

```text
Pr_h{R_j >= C_j} <= exp(-2*T*(m^h_j)^2),    j != i_h.
```

The decoder reads all unsaturated coordinates from `A`; if exactly one
coordinate is capped and `d(A)>0`, it assigns all rejected mass to that
coordinate. If `d(A)=0`, it returns `A`. This decoder is exact unless some
expert other than `i_h` is also capped. Therefore, with

```text
epsilon_1(T) = sum_h prior(h) * sum_(j != i_h) exp(-2*T*(m^h_j)^2),
```

the value of requested counts satisfies

```text
0 <= V_A(T)-V_R(T) <= epsilon_1(T).
```

*Proof.* Couple the requested policy and its admitted-signal simulation by
using the decoder above. Their actions and losses agree whenever the decoder
recovers `R`; loss differs by at most one on decoder failure. A failure
requires at least one non-designated coordinate to reach capacity, so the
union bound gives `epsilon_1(T)`. This simulates any requested policy from
the admitted signal up to that risk. Taking infima gives
`V_A<=V_R+epsilon_1`; Blackwell dominance gives `V_R<=V_A`. ∎

The bound needs no Top-K-specific action geometry; Top-K enters through the
mass identity and the independent-token count concentration. It says that
the admitted signal's decision-value loss vanishes exponentially when one
coordinate is the only persistently overloaded expert.

## Two-saturation positive-value construction

Fix `E>=3`, `1<=K<E`, and two worlds whose standard-Gumbel Top-K score
weights are `(w_H,w_L,1,...,1)` and `(w_L,w_H,1,...,1)`, with
`w_H>w_L>0`. Let their inclusion means be

```text
p^0=(p_H,p_L,p_3,...,p_E),
p^1=(p_L,p_H,p_3,...,p_E),
Delta=p_H-p_L>0.
```

Assume the profiles below are in the relative interior of the hypersimplex
`{c in [0,1]^E : sum c=K}`. Use exact-total capacities `C_e=T*c_e` on
admissible integer batch sizes.

**One persistently saturated coordinate per world.** Set

```text
c_1=c_2=p_L+Delta/4,
c_j=p_j+Delta/(2*(E-2)),  j>=3.
```

These capacities sum to `K`. In each world exactly one member of the first
pair is above capacity; the other and all tail experts are below capacity.
The one-saturation bound applies with margins `Delta/4` for the low member
and `Delta/(2*(E-2))` for each tail expert, so `V_A(T)-V_R(T)` tends to zero
exponentially in `T`.

**Two persistently saturated coordinates in both worlds.** More generally,
take any exact-total capacity vector in the hypersimplex interior with
`c_1=c_2=x<p_L` and `c_j>p_j` for every `j>=3`. In each world both members
of the first pair are then above capacity, while all tail experts are below
capacity. The all-pressure common-action theorem in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md)
gives

```text
lim_(T->infinity) (V_A(T)-V_R(T)) = v_*(c) > 0.
```

One explicit profile in this class is

```text
c_1=c_2=p_L-Delta/4,
c_j=p_j+3*Delta/(2*(E-2)),  j>=3.
```

These fractions sum to `K`. The constant `v_*(c)` is the minimum equal-prior
population overflow under a common pressure action. The general Top-K proof
leaves it implicit. An explicit curvature certificate exists for a
neighboring Top-K weight/capacity profile in
[`topk_swapped_saturation_explicit_gap_bound_2026-10-17.md`](topk_swapped_saturation_explicit_gap_bound_2026-10-17.md)
but its tiny numerical constants do not certify the `v_*(c)` for the
capacity profile used in this experiment without redoing that derivation.
For a separate Top-1 family with weights
`(5/4,1,1/(E-2),...,1/(E-2))` and profile `c_1=c_2=1/4`,
`c_j=1/(2(E-2))`, the exact value `v_*=1/36` is proved in
[`top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md`](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md);
neither its weights nor its capacity profile are those used in the controlled
experiment.

The paired construction is an exact within-model comparison: the two worlds,
Top-K law, target action, gauge, observation map, overflow objective, and
total capacity are shared. Only the capacity split changes whether one or
both swapped experts are clipped in each world.

### Explicit finite-batch certificate for `E=3, K=2`

The general two-saturation argument proves `v_*(c)>0` but leaves that
constant implicit. For one concrete Top-2 member of the same theorem family,
the all-pressure analysis in
[`topk_two_saturated_value_theorem_candidate_2026-10-17.md`](topk_two_saturated_value_theorem_candidate_2026-10-17.md)
proves the rational bound

```text
27/200 <= v_* <= 459/3080
```

and the explicit finite-batch all-policy certificate

```text
V_A(T)-V_R(T) >= 27/200
  - 2*(2*exp(-T/450)+exp(-361*T/1800))
  - 2*exp(-T/32) - 3/(2*sqrt(T)).
```

The original Hoeffding bound is rigorously positive at `T=1680`, with exact
rational exponential and square-root inequalities giving a lower certificate
greater than `0.00267814`. A subsequent proof sharpening uses Jensen's
inequality for the admitted-policy lower bound and exact binomial tails for
the coupling and requested classifier. It certifies a positive unrestricted
all-policy gap at `T=540` (`>0.0000340156`) and a stronger lower bound at
`T=1680` (`>0.1138908062`). These are analytic certificates, not a claim
that either batch size is the smallest positive threshold. The accompanying
controlled experiment reports exact finite-count values in a declared
two-target-action class separately from this unrestricted all-policy lower
bound. See
[`top2_explicit_value_gap_experiment_results_2026-10-18.md`](top2_explicit_value_gap_experiment_results_2026-10-18.md).

The controlled one-versus-two-saturation run and its finite-grid limits are
reported in
[`saturation_multiplicity_experiment_results_2026-10-18.md`](saturation_multiplicity_experiment_results_2026-10-18.md).

## Costed requested-count observation corollary

Suppose the decision-maker may either use the admitted signal at no charge,
or pay a price `kappa>=0` in the same normalized-overflow units to obtain the
requested signal. The optimal cost is

```text
V_buy(T,kappa) = min{V_A(T), kappa + V_R(T)},
```

so the exact break-even price is `kappa_star(T)=V_A(T)-V_R(T)`. In the
one-saturation family,

```text
0 <= kappa_star(T) <= epsilon_1(T) -> 0.
```

In the two-saturation family,

```text
kappa_star(T) -> v_*(c) > 0.
```

Thus, for any fixed `kappa<v_*(c)`, purchasing requested counts is optimal
for all sufficiently large admissible batch sizes in the two-saturation
family; any fixed positive price eventually exceeds the value in the
one-saturation family. This is a theorem about an abstract price measured in
the same units as normalized overflow. It does not equate that price to a
collective's latency, energy, or runtime cost. The one-step proof is immediate
from the definition of optimal value and the preceding signal-gap bounds.

## Interpretation and proof boundary

This gives a concrete theorem for the professor's signal-value question:
capacity clipping does not make admitted feedback uniformly uninformative;
the number and identity of simultaneously saturated coordinates matter.
The deterministic fiber lemma is exact, the one-saturation value bound is
finite-sample, and the two-saturation value gap is asymptotically positive
for the stated Gumbel Top-K family.

This theorem does **not** establish a new general theory beyond censored
Bayesian decision-making. The two-world problem is exactly representable as
a finite-alphabet censored Bayesian experiment, and adaptive hypothesis
testing is established prior work. The MoE-specific content is the
Top-K-realizable family and the saturation-multiplicity transition. The
controlled experiment must test that transition across `E,K,T`, report the
finite-bound weakness, and must not be presented as novelty clearance.

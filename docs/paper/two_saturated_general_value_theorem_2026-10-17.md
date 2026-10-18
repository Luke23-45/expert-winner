# General two-saturated-expert value gap under canonical Top-1 clipping

## Model

Fix `E>=3` and rational parameters `a,delta,c,tau_3,...,tau_E,d_3,...,d_E`
satisfying

```text
0 < delta < a,
0 < c < a-delta,
tau_j > 0,
d_j > tau_j,
sum_(j=3)^E tau_j = 1-2a,
sum_(j=3)^E d_j = 1-2c.
```

There are two equally likely static worlds, with Top-1 Gumbel choice
probabilities

```text
p^0=(a,a,tau_3,...,tau_E),
p^1=(a+delta,a-delta,tau_3,...,tau_E).
```

These are realized by scores `log(p^h_e)+G_{t,e}-q_e` with independent
standard Gumbel noise. For feasible batch sizes, take capacities

```text
C/T=(c,c,d_3,...,d_E),     sum_e C_e=T,
A_e=min(R_e,C_e).
```

In both worlds experts 1 and 2 exceed capacity by a fixed positive margin;
every other expert is strictly below capacity. The latent worlds move
request mass between the two saturated experts while keeping their combined
probability and the entire tail distribution fixed.

After observing the first-batch signal `R` or `A`, a policy chooses an
arbitrary gauge-fixed pressure `q` for one fresh iid batch. Define its
population overflow cost

```text
L_h(q)=sum_e [rho^h_e(q)-C_e/T]_+,
rho^h(q)=softmax(log(p^h)-q).
```

Since both probability and capacity vectors sum to one,
`L_h(q)=TV(rho^h(q),C/T)` and `0<=L_h(q)<=1`. Let `V_R^pop(T)` and
`V_A^pop(T)` be the minimum equal-prior expected population cost over all
deterministic or randomized one-step policies based on the full respective
count vector.

## Theorem

Set

```text
lambda = ((a+delta)/a) / ((a-delta)/a) = (a+delta)/(a-delta),
V_* = c*(lambda-1)/(2*(lambda+1)) = c*delta/(2*a),
m_sat = a-delta-c,
m_j = d_j-tau_j,
eps_A(T)=2*exp(-2*T*m_sat^2)+sum_(j=3)^E exp(-2*T*m_j^2),
eps_R(T)=exp(-T*delta^2/2).
```

Then

```text
V_* - eps_A(T) - eps_R(T)
    <= V_A^pop(T)-V_R^pop(T) <= V_*.
```

Consequently,

```text
lim_(T->infinity) V_A^pop(T)=c*delta/(2*a),
lim_(T->infinity) V_R^pop(T)=0,
lim_(T->infinity)(V_A^pop(T)-V_R^pop(T))=c*delta/(2*a)>0.
```

The result holds for every fixed `E>=3` and all parameters satisfying the
displayed strict-margin conditions. Its leading value is independent of the
number and distribution of tail experts once their capacities are above
their common world probabilities and sum to the required exact total.

## Proof

### 1. Admitted observations become indistinguishable

Let `R~Multinomial(T,p^h)` at zero pressure, and define the common reference
vector

```text
Y=(c*T,c*T,R_3,...,R_E).
```

The law of `Y` is the same in both worlds because all tail probabilities
`tau_j` are common. On the event

```text
G={R_1>=c*T, R_2>=c*T, R_j<d_j*T for all j>=3},
```

canonical clipping gives `A=Y`. Hoeffding's inequality and a union bound
give, in either world,

```text
Pr_h(G^c) <= eps_A(T).
```

The coupling inequality therefore gives
`TV(P^A_{h,T},Q_T)<=eps_A(T)` for the common law `Q_T=law(Y)`. In particular,
the two full admitted-vector laws approach one another; this is not an
assertion of exact finite-batch non-identifiability.

### 2. The optimal common-action loss is exactly `V_*`

For a common pressure `q`, write `w=rho^0(q)` and `u=rho^1(q)`. Their
coordinate odds obey

```text
u_1/u_2 = lambda*(w_1/w_2).
```

Let `alpha=TV(w,C/T)` and `beta=TV(u,C/T)`. If either is at least `c`, then
`alpha+beta>=c>c*delta/a`. Otherwise both are below `c`, and the coordinate
bounds implied by total variation give

```text
(c-alpha)/(c+alpha) <= w_1/w_2,
u_1/u_2 <= (c+beta)/(c-beta).
```

Combining with the odds identity and cross-multiplying yields

```text
alpha+beta >= c*(lambda-1)/(lambda+1) = c*delta/a.
```

Thus every common action has equal-prior risk at least `V_*`.

This bound is attained by a pressure `q^0` for which `rho^0(q^0)=C/T`.
Such a finite gauge-fixed pressure exists because all coordinates of `p^0`
and `C/T` are positive. Under world 1, the normalizer remains one:

```text
sum_e (C_e/T)*(p^1_e/p^0_e)
 = c*((a+delta)/a)+c*((a-delta)/a)+sum_(j>=3)d_j
 = 1.
```

The resulting distribution is `(c*(1+delta/a), c*(1-delta/a), d_3,...,d_E)`.
Its only overflow is `c*delta/a` at expert 1, so the equal-prior cost is
exactly `V_*`.

### 3. Finite-batch admitted value

For any admitted-signal policy, replace each world-specific admitted
observation law by the common `Q_T`. The change in equal-prior risk is at
most `eps_A(T)`. Under `Q_T`, the action distribution selected by the policy
is common to both worlds, and every common action has risk at least `V_*`.
Therefore `V_A^pop(T)>=V_*-eps_A(T)`. The constant action `q^0` attains
`V_*` for every observation, so `V_A^pop(T)<=V_*`.

### 4. Requested-signal value

Classify world 1 when `R_1/T>=a+delta/2`. Under either world, Hoeffding's
inequality bounds the classification error by `eps_R(T)`. After classifying,
choose a pressure `q^h` such that `rho^h(q^h)=C/T`; this is possible because
all coordinates are positive. The cost is zero on correct classification
and at most one otherwise. Hence `0<=V_R^pop(T)<=eps_R(T)`. Combining the
admitted and requested bounds proves the theorem. `□`

## Finite-batch realized-overflow corollary

The theorem above uses the population loss `L_h(q)`. The canonical formal
definition instead records realized overflow in a finite batch. The following
corollary transfers the value gap to that objective rather than treating the
two costs as identical.

For an action `q` in world `h`, let `X^{h,q}~Multinomial(T,rho^h(q))` be the
independent fresh-batch request vector and define normalized expected realized
overflow

```text
ell_h,T(q) = (1/T) E[sum_e (X_e^{h,q}-C_e)_+].
```

Let `W_A(T)` and `W_R(T)` be the minimum equal-prior expected `ell` over
one-step policies based on the full admitted or requested vector from the
first batch. Then

```text
V_* - eps_A(T) - U_R(T) <= W_A(T)-W_R(T) <= U_A(T),
```

where the explicit upper bounds are

```text
U_A(T) = 0.5*(ell_0,T(q^0)+ell_1,T(q^0)),
U_R(T) = 0.5*((1-e_0)*ell_0,T(q^0) + e_0*ell_0,T(q^1)
              + e_1*ell_1,T(q^0) + (1-e_1)*ell_1,T(q^1)),
e_0 = Pr[Binomial(T,a) >= ceil(T*(a+delta/2))],
e_1 = Pr[Binomial(T,a+delta) < ceil(T*(a+delta/2))].
```

Here `U_A` is the cost of the constant admitted policy `q^0`; `U_R` is the
cost of the registered requested threshold classifier. Both are computable
from finite binomial sums. For any probability vector `rho`, convexity gives
`ell_h,T(q)>=L_h(q)` by Jensen's inequality. The normalized realized overflow
lies in `[0,1]`, so replacing the admitted observation law by the common
reference law changes risk by at most `eps_A`; this proves
`W_A>=V_*-eps_A`. The requested threshold policy has exactly the displayed
finite-batch value, proving `W_R<=U_R`. Finally `W_A<=U_A` and `W_R>=0`,
which gives the upper gap bound.

For fixed parameters, `U_A(T)->V_*`, `U_R(T)->0`, and `eps_A(T)->0` as
`T->infinity`. Thus the **finite-batch realized-overflow** value gap also
converges to `V_*`. This is the bridge to the canonical finite-count cost;
the earlier population theorem alone should not be described as an exact
finite-batch overflow theorem.

## Interpretation and limits

This is a multi-saturation value theorem for a concrete Top-1/Gumbel family.
It repairs the one-saturated case distinction: when only one coordinate is
clipped, conservation reconstructs the requests; with two clipped
coordinates, a hidden allocation split remains and has a quantitatively
positive decision value in this family.

The closest literature boundary is general censored decision making and
active experiment selection. Abernethy, Amin, and Zhu's
[Threshold Bandits, With and Without Censored Feedback](https://proceedings.neurips.cc/paper_files/paper/2016/hash/0bf727e907c5fc9d5356f11e4c45d613-Abstract.html)
shows that censoring itself is established; its arm/threshold reward model
does not include Top-1 score pressures or per-expert clipping. Verma et al.'s
[Censored Semi-Bandits](https://arxiv.org/abs/1909.01504) studies resource
allocation with threshold-censored feedback, but a different observation and
objective. [Fixed-horizon Active Hypothesis Testing](https://arxiv.org/abs/1911.06912)
already studies adaptive experiment choice to reduce finite-horizon
misclassification, making it a close methodological neighbor to the two-world
signal-value argument. [METRO](https://arxiv.org/abs/2512.09277) is relevant
to the systems price question because it gathers global Top-K information;
its target is activated-expert placement/latency, not admitted-count control.

The exact result here is therefore an MoE-realized value theorem inside the
generic censored-testing family. Its current proof does not establish a
decision-theoretic principle absent from active hypothesis testing, a
requested-side collective price, or a top-conference novelty claim.

The theorem is a special case of censored Bayesian hypothesis testing with
an action-dependent routing realization. It does not by itself establish a
new general control principle, a multi-round Top-K/root-geometry advantage,
a measured telemetry price, or separation from an outcome-map benchmark
that can encode the finite experiment exactly. The equation-level prior-art
comparison and reduction gate remain required.

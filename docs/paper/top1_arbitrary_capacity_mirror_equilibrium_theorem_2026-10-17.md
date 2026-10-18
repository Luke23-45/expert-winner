# Top-1 admitted feedback with arbitrary exact-total capacities

**Scope:** exact population dynamics of the canonical proportional pressure
update for Top-1 Gumbel routing and uniform target. The theorem uses the
existing per-expert clipping model. It does not claim finite-batch
infinite-horizon convergence or a benchmark separation.

## Model

There are `E>=2` experts and a unit request mass. Expert `e` has normalized
capacity `c_e in (0,1)` with `sum_e c_e=1`. For pressure `q`, iid standard
Gumbel affinities and Top-1 selection give

```text
p_e(q)=exp(-q_e)/sum_j exp(-q_j).
```

The population admitted fraction is `a_e(p)=min(p_e,c_e)`. With uniform
target `mu_e=1/E`, no leak, `gamma=1`, and the canonical gauge projection,
the pressure dynamics are

```text
q_next = P0(q + eta*(a(p(q))-1/E)),
P0 = I - 11^T/E.
```

Pressures differing by a common offset are identified. Define the convex
capacity potential on the simplex

```text
W(p) = sum_e integral_0^(p_e) min(s,c_e) ds
     = sum_e { p_e^2/2                         if p_e <= c_e,
               c_e*p_e - c_e^2/2              if p_e >= c_e }.
```

Its gradient is `nabla W(p)=a(p)`. Let `H(p)=sum_e p_e log p_e`, so
`D_H(x,y)=KL(x||y)`.

## Theorem 1: exact mirror-descent representation and convergence

For every interior `p_t`, the pressure update is exactly

```text
p_(t+1) = argmin_{x in Delta_E} { eta * <nabla W(p_t),x>
                                  + KL(x||p_t) }.
```

Moreover, `W` is 1-relatively smooth with respect to negative entropy:

```text
W(y) <= W(x) + <nabla W(x),y-x> + KL(y||x).
```

Consequently, for any minimizer `p*` of `W` and any `0<eta<1`,

```text
W(p_(t+1))-W(p*)
 <= [ KL(p*||p_t)-KL(p*||p_(t+1)) ]/eta
    - (1/eta-1) KL(p_(t+1)||p_t).
```

In particular, `W(p_t)` is nonincreasing and

```text
W(p_N)-W(p*) <= KL(p*||p_0)/(eta*N),    N>=1.
```
Thus the population iterates converge in objective value to the minimizer
set of `W`; every accumulation point is a minimizer. This is a statement for
the exact population update. It does not imply infinite-horizon convergence
for a fixed finite token batch.

### Proof

Since `p=softmax(-q)`, applying the pressure update gives

```text
p_(t+1,e) proportional to p_(t,e)*exp(-eta*a_e(p_t));
```
the uniform target and gauge projection contribute only common factors,
which cancel in the normalization. This is the first-order optimality
condition of the displayed entropic mirror step.

Each scalar summand of `W` has second derivative either zero or one, except
at its continuous first-derivative kink `p_e=c_e`. The entropy summand has
second derivative `1/p_e>=1` on `0<p_e<=1`. Integrating this Hessian
comparison along a segment proves the relative-smoothness inequality.
The standard three-point inequality for the KL mirror step gives

```text
eta*<nabla W(p_t),p_(t+1)-p*>
 <= KL(p*||p_t)-KL(p*||p_(t+1))-KL(p_(t+1)||p_t).
```

Convexity gives `W(p_t)-W(p*) <= <nabla W(p_t),p_t-p*>`. Relative
smoothness from `p_t` to `p_(t+1)` and the mirror-step inequality with
comparison point `p_t` combine with these inequalities to yield

```text
eta*(W(p_(t+1))-W(p*))
 <= KL(p*||p_t)-KL(p*||p_(t+1))-(1-eta)KL(p_(t+1)||p_t).
```

Summing over `t=0,...,N-1`, using nonnegativity of KL, and monotonicity
proves the rate and convergence claims. `W` is continuous on the compact
simplex, so objective convergence implies every limit point belongs to its
minimizer set. `\square`

## Theorem 2: complete equilibrium set and overflow comparison

Let `c_min=min_e c_e`, `S={e:c_e=c_min}`, and `m=|S|`. Since the capacities
sum to one, `c_min<=1/E`. The complete minimizer/equilibrium set is

```text
p_e*=c_min                  for e not in S,
p_e*>=c_min                 for e in S,
sum_(e in S) p_e*=1-(E-m)*c_min.
```

It is nonempty and lies in the interior of the simplex. One canonical
representative chooses equal mass on the minimum-capacity experts:

```text
p_e* = c_min                              if e not in S,
p_e* = [1-(E-m)*c_min]/m                 if e in S,
q_e* = -log(p_e*) + common_offset.
```

At every such equilibrium, all admitted fractions equal `c_min`, so
normalized overflow is

```text
O_A*=1-E*c_min.
```

The requested-feedback uniform-target equilibrium is `p_e=1/E`, with

```text
O_R=sum_e max(1/E-c_e,0).
```

For a nonuniform capacity vector, let `L={e:c_e<1/E}`. Then
`1<=|L|<=E-1` and

```text
O_A*-O_R >= (E-|L|)*(1/E-c_min) >= 1/E-c_min > 0.
```

Thus, in the exact population equilibrium comparison, canonical admitted
feedback strictly increases overflow relative to requested feedback for
every nonuniform positive exact-total capacity profile. The statement
compares equilibria of the specified controller and does not claim that
admitted feedback is worse at every transient time, for every finite batch,
or against every causal policy.

### Proof

At an interior minimizer, the KKT condition is
`min(p_e,c_e)=lambda` for all `e`. For an index with capacity `c_min`, this
implies `lambda<=c_min`. If `lambda<c_min`, every capacity exceeds
`lambda`, forcing `p_e=lambda` for every expert; summing probabilities gives
`lambda=1/E`, contradicting `c_min<=1/E`. Hence `lambda=c_min`, which gives
the displayed minimizer set. Conversely, every vector in that set satisfies
the KKT condition and is a minimizer by convexity. Positivity follows from
`c_min>0`; the equal-mass construction is feasible because
`1-E*c_min>=0`, and its low-group coordinate is strictly below one.

The admitted total at an equilibrium is `E*c_min`, proving `O_A*`. At the
requested equilibrium, the per-coordinate overflow is the positive part
shown. Each term for `e in L` is at most `1/E-c_min`, so
`O_R<=|L|(1/E-c_min)`. Since `O_A*=E(1/E-c_min)`, subtraction proves the
bound. A nonuniform exact-total vector has `c_min<1/E` and at least one
capacity at or above the mean, so `|L|<=E-1`. This proves strict positivity.
\(\square\)

## What is and is not new in this derivation

The potential `W` is the nonatomic congestion potential for the capped cost
`min(p_e,c_e)`, and its entropic mirror-descent convergence follows the
established relative-smoothness framework. Those ingredients alone are not
claimed as new. The MoE-specific statement is the exact identification of
the canonical admitted-count pressure update with this capped-cost mirror
flow, plus the explicit equilibrium overflow comparison under per-expert
capacity clipping. This probability-coordinate potential does not contradict
the existing result that the expected admitted vector field has nonzero
Euclidean curl in pressure coordinates: it is a mirror potential in `p`,
not a scalar Euclidean potential for the `q`-field.

The theorem concerns the large-batch population model. It supplies a
mechanism-level result on arbitrary heterogeneous capacities, but does not
by itself defeat the fixed-instance polyhedral active-testing reduction,
establish a marginal telemetry price, or show trained-model quality gains.

### Primary-source boundary

Rosenthal's original work establishes potential functions for congestion
games ([1973 paper](https://doi.org/10.1007/BF01737559)). Relative-smoothness
mirror-descent convergence is established in the optimization literature;
for example, Aubin-Frankowski, Korba, and Léger prove convergence for
relatively smooth convex objectives under KL mirror descent
([NeurIPS paper](https://papers.nips.cc/paper_files/paper/2022/hash/6e3daaeca6be8579573f69082b2dd58b-Paper-Conference.pdf)). The present derivation
uses these general tools, and novelty must be evaluated at the MoE clipping,
equilibrium, and overflow-comparison statement rather than at the existence
of a potential or mirror-descent convergence.

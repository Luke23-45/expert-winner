# Population overflow theorem with multiple low-capacity experts

**Research line:** the canonical per-expert clipping and proportional pressure
update in `formal.md`. This extends the existing one-low-capacity population
theorem; it does not change the controller or admission rule.

## Statement

Fix `E>=2`, `1<=K<E`, and an integer `m` with `1<=m<E`. Write
`p=K/E`. Each token draws its E affinities iid from one common distribution
with a continuous, strictly positive, bounded density `f`; tokens are independent. It
selects the hard Top-K experts by score `a_e-q_e`. A fixed affinity batch is
reused at every update. Set the uniform target `mu_e=1/E`, `gamma=1`,
`delta=0`, and per-expert admission `A_e=min(R_e,C_e)`.

Let `h_inf=max(K-m,0)/(E-m)`, the limiting inclusion probability of a
particular high expert as the high group is suppressed. Choose `r` with

```text
0 < r < min(p-h_inf, (1-p)*(E-m)/m),
c_low  = p-r,
c_high = p + m*r/(E-m).
```

There are `m` low-capacity experts with limiting capacity fraction `c_low`
and `E-m` high-capacity experts with limiting fraction `c_high`. Thus total
capacity is exactly `K` assignments per token in the large-batch limit;
`h_inf<c_low<p<c_high<1`. For finite batches take an integer sequence with
`m*C_low+(E-m)*C_high=K*T` and the stated capacity fractions converging.

Let `h(x)` denote the one-token inclusion probability of any particular
high-capacity expert when all low experts have pressure zero and all high
experts have pressure `x`:

```text
q(x)=(0,...,0,x,...,x),   # m low, E-m high coordinates
h(x)=Pr[a_high-x is in the Top-K set at q(x)].
```

For this iid continuous-affinity model, `h` is continuously differentiable
and strictly decreasing, `h(0)=p`, and `h(x)->h_inf` as `x->infinity`. In
particular, conditioning on the target high expert's affinity `y`, let
`a` be the number of low experts scoring above `y-x` and `b` the number of
other high experts scoring above `y`. Then

```text
h(x) = integral sum_(a,b>=0, a+b<=K-1)
       BinomPMF(a; m, 1-F(y-x))
       BinomPMF(b; E-m-1, 1-F(y)) f(y) dy.
```

The two binomial counts are conditionally independent. Differentiating the
finite binomial sum under the integral is valid because `f` is continuous
and bounded; every derivative term is dominated by a constant times `f(y)`.
For strict monotonicity, fix `x_1<x_2`. There is positive probability that
exactly `K-1` experts other than the target high expert outrank it at `x_1`,
and that one low expert has affinity in the interval swept by the target
threshold from `y-x_1` to `y-x_2`, with the remaining experts below the
threshold at `x_1`. Strict positivity of `f` makes this event have positive
probability. The target is selected at `x_1` and displaced from the Top-K
set at `x_2`; lowering all high scores cannot reverse any high/high order.
Thus `h(x_2)<h(x_1)`. When `m<K`, the low group eventually occupies `m` of the K
positions and the remaining `K-m` positions are shared symmetrically among
the high experts, giving `h_inf`; when `m>=K`, the high-group probability
tends to zero. Also `|h(x+s)-h(x)|<=m*||f||_infinity*|s|`: inclusion can change
only if at least one of the m low scores lies in the swept interval of
length `|s|` at the target threshold. Thus `L_h=max_{0<=x<=x_*}|h'(x)|` is
finite and bounded by `m*||f||_infinity`. Let `x_*` be the unique solution
of `h(x_*)=c_low`. If `0<eta<=K/L_h`, define

```text
x_0=0,
x_(n+1)=x_n + eta/K * (h(x_n)-c_low).
```

Then the large-batch population limits of the requested and admitted arms
obey:

1. The requested-feedback pressure remains at the zero gauge state and its
   normalized overflow is `m*r` per round.
2. The admitted-feedback pressure remains in the two-group form `q(x_n)`;
   `x_n` increases monotonically to `x_*`.
3. At round `n`, admitted-minus-requested normalized overflow is exactly
   ```text
   Delta_n = (E-m)*(p-h(x_n)).
   ```
   It is zero at the first round and strictly positive at every later round.
4. The long-run per-round gap is
   ```text
   lim_(H->infinity) (1/H) sum_(n=0)^(H-1) Delta_n = (E-m)*r > 0.
   ```
For each fixed finite `H`, the same cumulative normalized gap is the limit
of the expected paired finite-batch gap as `T->infinity` along the integer
capacity sequence.

## Proof

Let `n=E-m`. Symmetry within each group implies that at pressure `q(x)` each
high expert has inclusion probability `h(x)`, and each low expert has

```text
ell(x) = (K-n*h(x))/m.
```

At `x=0`, exchangeability gives `h(0)=ell(0)=p`. Increasing `x` lowers every
high score while leaving low scores fixed. Under a tie-free ranking, the
number of high experts in a token's Top-K set cannot increase when all high
scores are lowered. The positive-probability threshold-crossing argument
above proves strict decrease for the full stated affinity class, not only
for Gumbel affinities. As `x` tends to infinity, low experts occupy
`min(m,K)` of the
Top-K positions with probability one; symmetry among the remaining high
experts gives `h(x)->h_inf`. The capacity condition `h_inf<c_low<p` then
gives a unique finite `x_*`.

For every `x>=0`, `h(x)<=p<c_high`, so each high expert is below its
capacity. Also `ell(x)>=p>c_low`, so each low expert is above its capacity.
Thus the population admitted fractions are exactly `c_low` on the low group
and `h(x)` on the high group.

The canonical update before gauge projection is
`q^+=q+eta*(A/(K*T)-1/E)`. Projection subtracts a common coordinate and
does not change the high-minus-low pressure difference. Therefore

```text
x_(n+1)-x_n
 = eta * (h(x_n)-c_low)/K,
```
which is the stated recurrence. On `[0,x_*]`, its update map has derivative
`1+eta*h'(x)/K` in `[0,1]` under the step-size condition. It maps the
interval into itself and moves each `x<x_*` upward. Hence `x_n` converges
monotonically to `x_*`.

At zero pressure the request fraction of every expert is `p`. Only the `m`
low-capacity experts overflow, by `p-c_low=r` each; requested feedback has
zero population update because the requested vector is uniform. Its
normalized overflow is therefore `m*r` each round.

At `q(x)`, all high experts remain below capacity and all low experts are
clipped. The low group requests `K-n*h(x)` assignments per token and admits
`m*c_low`; the high group has no overflow. Total normalized admitted
overflow is `K-n*h(x)-m*c_low`. Subtracting `m*r`, and using `K=E*p` and
`c_low=p-r`, gives

```text
K-n*h(x)-m*c_low-m*r = n*(p-h(x)).
```

This proves the per-round formula. Since `x_0=0` and `h` is strictly
decreasing, `Delta_0=0` and `Delta_n>0` for `n>=1`. At the fixed point,
`Delta_*=(E-m)*(p-c_low)=(E-m)*r`; Cesaro convergence yields the long-run
average.

Finally, for each fixed horizon, the empirical Top-K inclusion fractions
converge uniformly on the compact interval `[0,x_*]` to their population
probabilities by the finite-dimensional VC uniform law for score
inequalities. Coordinatewise clipping is Lipschitz. Induction over the
fixed number of updates gives convergence of the paired trajectories and
their normalized overflow costs. Costs per token per round are bounded by
`K`, so convergence also holds for expected cumulative costs. This is an
iterated limit: it does not assert infinite-horizon convergence at fixed
finite `T`. `\square`

## Gumbel response computation and limitations

The controlled audit uses standard Gumbel affinities and computes `h(x)`
exactly by dynamic programming over the Plackett-Luce ranking process
induced by Gumbel noise. In that process, each successive expert is selected
proportionally to its remaining exponential weight. Independently, the
general density bound gives `L_h<=m/e` for standard Gumbel, whose density is
bounded by `1/e`; therefore the registered `eta=0.5` satisfies
`eta<=K/L_h` for all tested families. The recurrence and gap are checked
against finite static batches using the actual hard Top-K counts and the
canonical update.

This theorem is a parameterized extension of the one-low-expert result to
any feasible number `1<=m<E` of low experts and common iid affinity laws with positive bounded
density. It is still a symmetric population family with one specified
controller, not a universal ranking over causal policies, a finite-instance
advantage over the polyhedral benchmark, a telemetry-cost break-even, or a
trained-model result. Those are not inferred from this proof or its
experiment.

## Fresh-batch finite-horizon extension

The fixed-batch theorem above reuses one empirical affinity matrix at each
update. The following finite-horizon limit also holds when each update draws
a fresh independent batch. It does not assert convergence as the horizon
grows with fixed batch size.

**Proposition.** Fix `E,K,m`, a finite horizon `H`, the theorem's capacity
fractions, and `eta`. For each batch size `T`, let every round use a fresh
batch of `T` iid affinity vectors from the stated common law. Assume the
integer capacities obey `C_low(T)/T -> c_low` and
`C_high(T)/T -> c_high`. Couple the requested and admitted arms using the
same affinity batch at each round. Then, for either arm, its finite-horizon
pressure path converges in probability to the corresponding deterministic
population path; its expected cumulative overflow divided by `T` converges
to the population cumulative overflow. In particular, the expected paired
admitted-minus-requested gap converges to
`sum_(t=0)^(H-1) (E-m)*(p-h(x_t))`.

*Proof.* Work in the zero-mean pressure subspace. For fixed `H`, all states
of either finite-batch controller lie in a compact ball independent of `T`:
each normalized count coordinate is in `[0,1/K]`, the target is fixed, and
each update has norm bounded by a constant depending only on `E,K,eta`.
For one token, the event that expert `e` is selected by hard Top-K is a
finite Boolean combination of affine score comparisons in `q`. The resulting
class of indicator functions has finite VC dimension. The uniform law of
large numbers therefore gives
`sup_q ||R_T(q)/T - p(q)|| -> 0` in probability on that compact ball, where
`p_e(q)` is the population inclusion probability. The affinity law is
continuous, so ties have probability zero and `p(q)` is continuous.

At each round, the fresh batch is independent of the history. The same
uniform bound thus applies conditionally to the random current pressure.
Since coordinatewise clipping is Lipschitz and `C(T)/T -> c`,
`A_T(q)/T` converges uniformly in probability to `min(p(q),c)`. The update
map is continuous in these normalized counts. Induction over the fixed
number `H` of rounds proves convergence in probability of each pressure
state to its population recursion, for requested and admitted feedback.
Normalized overflow is `sum_e (R_e/T-C_e/T)_+`; it is bounded by `K` and
continuous in the normalized count and capacity vectors. Its finite sum
therefore converges in probability and, by boundedness, in expectation.
Subtracting the two arm limits gives the displayed paired-gap limit. `□`

The static-batch audit and fresh-batch audit answer different questions:
the first checks the empirical deterministic plant; the second checks the
fixed-horizon population limit under independent batches. Neither implies
fixed-`T` infinite-horizon convergence.

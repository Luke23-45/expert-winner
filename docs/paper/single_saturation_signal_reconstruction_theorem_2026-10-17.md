# Exact request reconstruction with at most one saturated expert

## Proposition: the admitted vector is sufficient on a one-saturation fiber

Fix `E,K,T,C` and a mass-conserving requested count vector
`R in Z_{>=0}^E` with `sum_e R_e=K*T`. Let

```text
A_e=min(R_e,C_e),   S(A)={e:A_e=C_e}.
```

If `|S(A)|=0`, then `R=A`. If `S(A)={s}` is a singleton, then the full
requested vector is uniquely determined by `(A,C,K,T)`:

```text
R_e=A_e                    for e != s,
R_s=K*T-sum_(e != s) A_e.
```

In particular, every requested-feedback update in `formal.md`, for any
known target `mu`, can be reproduced exactly from admitted counts on this
regime. The statement is information-theoretic and exact; it does not
assume an affinity distribution or a controller.

**Proof.** If no expert is saturated, `A_e<C_e` for every `e`, so clipping
implies `R_e=A_e`. If exactly expert `s` is saturated, every other coordinate
is unsaturated and hence `R_e=A_e`; mass conservation uniquely supplies the
remaining coordinate. Substitution into the requested update gives exactly
the same next gauge state. `□`

This is a sufficient condition, not a characterization of all singleton
fibers. With two or more saturated coordinates, reconstruction can still be
possible in special cases, but it is not guaranteed by this argument.

## Corollary: capacity-relative control on the one-short iid family

Fix `E>=2`, `1<=K<E`, `p=K/E`, `gamma=1`, zero leak, uniform affinities
with a common strictly positive bounded density `f`, and one static iid
`T x E` affinity matrix. Let exact-total capacities obey

```text
C_1/T -> p-r,
C_e/T -> p+r/(E-1),  e=2,...,E,
0 < r < min(p,(1-p)/(E-1)).
```

Use the **formal capacity-relative requested update**

```text
q_next=Pi_g(q+eta*P_0(R/(K*T)-C/(K*T))).
```

Let `Q(x)` be the population Top-K inclusion probability of expert 1 when
its score is penalized by relative pressure `x>=0` and the other experts
have equal pressure. Then `Q(0)=p`, `Q` is continuous and strictly
decreasing, and `Q(x)->0`. Define `x_*` by `Q(x_*)=p-r`. If

```text
0 < eta*E/(K*(E-1))*sup_(x>=0)|Q'(x)| <= 1,
```

the population capacity-relative recursion is

```text
x_0=0,
x_(n+1)=x_n + eta*E/(K*(E-1))*(Q(x_n)-(p-r)).
```

It increases monotonically to `x_*` without overshoot. Throughout every
finite prefix before the limit, only expert 1 is saturated; all rivals are
strictly below capacity. Therefore admitted counts uniquely reconstruct
requested counts at every state in that prefix. An admitted-only controller
that applies the reconstruction proposition and then the same
capacity-relative update follows exactly the requested capacity-relative
trajectory on that prefix.

The population overflow per token at step `n` is `Q(x_n)-(p-r)`, which
decreases to zero. Its long-run Cesaro average is zero. By contrast, the
formal requested or admitted updates with the **uniform target** `mu=1/E`
are solving a different reference problem: the requested uniform-target
population update stays at zero pressure and retains the short expert's
overflow `r` each round. This contrast diagnoses a target/update mismatch;
it is not evidence that requested telemetry is necessary.

**Proof sketch with details.** At pressure `q=(x,0,...,0)`, the short
expert's request fraction is `Q(x)` and each rival's fraction is
`(K-Q(x))/(E-1)`. While `Q(x)>p-r`, expert 1 is clipped at `p-r`, while
each rival remains below `p+r/(E-1)`. The pressure increment difference
between the short expert and a rival under `R-C` feedback is
`eta*E/[K(E-1)]*(Q(x)-(p-r))`, giving the displayed recursion. The step
condition makes its update map nondecreasing; it fixes `x_*`, maps
`[0,x_*]` into itself, and strictly increases every point below `x_*`.
Thus `x_n` converges to the unique fixed point. The strict inequalities
hold for each finite `n`; the law of large numbers for the finite-VC Top-K
winner class implies that, for every fixed horizon, the corresponding
finite-batch path has exactly one saturated coordinate with probability
tending to one. Apply the proposition inductively to obtain exact
finite-batch trajectory agreement between requested capacity-relative
feedback and admitted-only reconstruction with probability tending to one.
At the population limit all expert request fractions equal their capacities,
so overflow tends to zero; Cesaro convergence gives zero long-run average.
`□`

### Closed-form Top-1 Gumbel instance

For `K=1` and standard iid Gumbel affinities,

```text
Q(x)=1/(1+(E-1)*exp(x)).
```

For `E=4`, `r=1/8`, the capacities are
`C_1/T=1/8` and `C_e/T=7/24` for `e=2,3,4`; the equilibrium is
`x_*=log(7/3)`. Since `sup_(x>=0)|Q'(x)|=3/16`, the displayed sufficient
step condition allows `eta<=4`; the controlled experiment uses `eta=1`.

## Scope

This is a sufficiency theorem on a one-saturated-expert trajectory family.
It does not say admitted counts always identify requests: two or more
saturated coordinates can leave a nontrivial clipping fiber. It also does
not establish universal overflow optimality, a measured collective cost,
trained-model improvement, or separation from a benchmark that copies exact
finite outcome maps. The exact theorem and experiment distinguish
**information loss** from **using the wrong reference target** in the
professor's proposed requested-versus-admitted comparison.

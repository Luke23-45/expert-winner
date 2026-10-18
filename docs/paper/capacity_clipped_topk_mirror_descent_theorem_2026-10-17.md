# Canonical admitted feedback as mirror descent in Top-K probability space

## Claim

This result keeps the canonical score rule, per-expert admission
`A_e=min(R_e,C_e)`, requested/admitted signals, gauge quotient, and pressure
update. It clarifies the geometry of the existing admitted-feedback update;
it does not introduce a controller or an admission variant.

Assume each step uses a fresh batch of `T` iid tokens. At a fixed pressure,
let

```text
p_e(q) = Pr[expert e is selected by one token],  sum_e p_e(q)=K,
m_e(p) = E[min(Binomial(T,p),C_e)].
```

The conditional expected admitted-feedback vector is

```text
epsilon_A(q) = m(p(q))/(K*T) - mu.
```

On the hypersimplex
`P_(E,K)={p in [0,1]^E : sum_e p_e=K}`, define

```text
L_A(p)
  = sum_e integral_0^(p_e) m_e(u)/(K*T) du - <mu,p>.
```

Then `L_A` is convex and
`nabla L_A(p)=epsilon_A(q)` whenever `p=p(q)`. More exactly,

```text
d^2 L_A / dp_e^2
  = Pr[Binomial(T-1,p_e)<C_e] / K >= 0.
```

The expected requested signal is also a convex-potential gradient, for
`L_R(p)=||p||_2^2/(2K)-<mu,p>`.

Now use the canonical pressure update with zero leak,

```text
q_next = Pi_g(q + eta*gamma*epsilon_A(q)).
```

Let `theta` denote the score-location vector modulo common shifts; for
fixed affinity locations, `theta=theta_0-gamma*q`. Let

```text
Psi(theta)
  = E[ max_{S subset [E], |S|=K} sum_{e in S}(theta_e + a_e) ].
```

For a full-support continuous random-utility law such as iid standard
Gumbel, the Top-K inclusion vector is `p=nabla Psi(theta)`, and `Psi` is
strictly convex on the quotient. Write `Psi*` for its convex conjugate on
the hypersimplex. The pressure update is exactly the mirror-descent step

```text
p_next = argmin_{p in P_(E,K)}
          { eta*gamma^2 * <nabla L_A(p_now),p>
            + D_(Psi*)(p,p_now) }.
```

The gauge projection changes `theta_next` only by a common shift, which
does not change `p_next`. With nonzero leak `delta`, this exact mirror-step
identity no longer holds in this form. With a reused fixed affinity batch,
the update is an empirical trajectory, not a fresh-batch stochastic
mirror-descent process.

For `K=1` and standard Gumbel noise,
`Psi(theta)=log(sum_e exp(theta_e))+constant` and
`Psi*(p)=sum_e p_e log(p_e)` on the simplex. The identity reduces to
exponentiated-gradient mirror descent:

```text
p_next,e proportional to p_now,e
                    * exp(-eta*gamma^2*epsilon_A,e).
```

## Proof

For one expert, its per-token inclusion indicator is Bernoulli with
probability `p_e`; independence across tokens gives
`R_e~Binomial(T,p_e)`. For any integer capacity `C_e`, differentiating the
binomial expectation gives

```text
d/dp E[min(Binomial(T,p),C_e)]
  = T*Pr[Binomial(T-1,p)<C_e].
```

Thus each integrand in `L_A` is nondecreasing, and its derivative is the
corresponding expected admitted error coordinate. This proves convexity and
the gradient identity. Dependence between different experts' counts is
irrelevant because the objective and signal use coordinate expectations.

The random-utility surplus `Psi` is convex as an expectation of maxima of
linear functions. With continuous full-support affinities, ties have
probability zero and differentiation under the expectation gives
`nabla Psi(theta)=p(theta)`. Full support gives positive probability to
every Top-K subset, so `Psi` is strictly convex modulo common shifts; its
gradient is invertible between the score quotient and the relative interior
of the hypersimplex. Hence `theta=grad Psi*(p)` modulo constants.

The pressure update implies, modulo a common vector,

```text
theta_next = theta_now - eta*gamma^2*nabla L_A(p_now).
```

The first-order optimality condition for the displayed mirror-descent
problem is

```text
nabla Psi*(p_next)
  = nabla Psi*(p_now) - eta*gamma^2*nabla L_A(p_now) + c*one
```

for a scalar Lagrange multiplier `c` enforcing `sum p=K`. Applying
`nabla Psi` proves the identity. For `K=1` Gumbel noise, the conjugate of
log-sum-exp is negative entropy, yielding the stated exponentiated-gradient
formula. `□`

## Interpretation and limits

The previously proved nonzero curl of the admitted expected field in
Euclidean **pressure coordinates** remains correct. It does not imply that
the canonical dynamics have no potential or no Lyapunov structure: in
inclusion-probability coordinates they are mirror descent on `L_A` under
the random-utility mirror map. Therefore the paper must not present the
pressure-coordinate curl alone as proof of control instability, cycles,
or lack of an optimization objective.

For equal capacities, `L_A` is symmetric across experts and is a particular
convex potential of the expected routing distribution. This falls within
the conceptual scope of the general potential-and-mirror-descent framework
of [`phi`-Balancing](https://proceedings.mlr.press/v306/chen26br.html), which
optimizes a convex potential of expected expert-routing probabilities. The
random-utility surplus foundation is classical; see
[Shi, Shum, and Song (2018)](https://doi.org/10.3982/ECTA14115738). The exact
capacity-induced potential and its clipped-count curvature are the
model-specific calculation here; this theorem alone does not establish
conference-level novelty, a controller-value gap, or a system benefit.

The theorem's fresh-batch/population assumption matters. The existing
fixed-affinity multi-step experiments reuse one affinity matrix, so this
mirror-descent interpretation describes the conditional mean field, not
those exact empirical trajectories. A deterministic identity audit for
the `K=1` Gumbel case is recorded in
[`capacity_clipped_topk_mirror_descent_results_2026-10-17.md`](capacity_clipped_topk_mirror_descent_results_2026-10-17.md).

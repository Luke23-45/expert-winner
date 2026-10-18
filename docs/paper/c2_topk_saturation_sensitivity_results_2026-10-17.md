# Top-K saturation sensitivity: proof and controlled experiment

**Research line:** requested/admitted feedback under the canonical
Top-K router and independent per-expert capacity clipping.
**Status:** exact mean-sensitivity theorem plus a controlled `E=4`,
`K in {1,2}` synthetic audit. This is not a claim of universal windup,
system benefit, or conference-level novelty.

## Result in one sentence

For iid fresh-token batches, independent per-expert clipping multiplies each
expert's requested-mean sensitivity by an exact binomial lower-tail factor;
when expected demand exceeds capacity by a fixed margin, that factor
vanishes exponentially with batch size. Under uniform global shortage, the
existing admitted-count sign update is exactly frozen whenever every expert
is clipped, an event whose probability approaches one in the registered
synthetic family.

## Formal statement and proof

At pressure `q`, let `p_e(q)` be the probability that one token's Top-K set
includes expert `e`, and let `R_e` be the requested count from `T` iid
tokens. Then `R_e ~ Binomial(T,p_e(q))` marginally. For an integer capacity
`1<=C_e<=T`, set `A_e=min(R_e,C_e)` and

```text
alpha_e(p) = Pr[Binomial(T-1,p) < C_e].
```

For the gauge-projected expected requested and admitted fields

```text
F_R(q) = P0(p(q)/K - mu),
F_A(q) = P0(E[A(q)]/(K*T) - mu),
```

at every differentiability point of `p(q)`,

```text
DF_R(q) = (1/K) P0 Dp(q),
DF_A(q) = (1/K) P0 diag(alpha_e(p_e(q))) Dp(q).
```

**Proof.** Write `X=Y+B`, where `Y~Binomial(T-1,p)` and
`B~Bernoulli(p)` are independent. Differentiating a product Bernoulli
expectation one coordinate at a time gives

```text
d/dp E[min(X,C)]
  = T E[min(Y+1,C)-min(Y,C)]
  = T Pr[Y<C].
```

The increment is one exactly when `Y<C`. Thus the derivative of each
expected admitted count with respect to its own request probability is
`T*alpha_e`; its dependence on other experts' probabilities is only through
the router map `p(q)`. The chain rule and normalization by `K*T` give the
admitted Jacobian. The requested identity follows by differentiating
`p(q)/K`. This proof uses only the marginal binomial count law; dependence
between different experts' counts does not affect it. This is the existing
Theorem in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md),
restated here to define the controlled experiment's estimand.

### Uniform-shortage freeze corollary

Let all capacities equal `C_T`, with `C_T/T <= c`, and suppose that at a
fixed pressure every expert has `p_e(q) >= c+epsilon` for some fixed
`epsilon>0`. Then

```text
Pr(R_e < C_T) <= exp(-2*T*epsilon^2),
Pr(A != C_T*1) <= E*exp(-2*T*epsilon^2).
```

The first bound is Hoeffding's inequality for the binomial marginal; the
second is a union bound. Whenever `A=C_T*1`, the admitted sign signal
`sign(mean(A)-A_e)` is exactly zero, so the bias update does not move. For
fresh batches and a trajectory that remains in a region with this margin,
the probability of at least one non-frozen update in `H` rounds is at most
`H*E*exp(-2*T*epsilon^2)`, by conditioning on the history at each round.
This is a high-probability freeze statement for the specified sign update,
not an assertion that every admitted-only controller winds up.

For the same positive-capacity finite-`T` model, the admitted law is not
exactly non-identifying: `Pr(A_e=0)=(1-p_e)^T`. The theorem concerns the
sensitivity of the **mean field**, not the full observation law. At the
capacity boundary `p_e=C_e/T`, exponential vanishing does not follow from
this argument.

## Controlled experiment

The preregistered [protocol](c2_topk_saturation_sensitivity_protocol_2026-10-17.md)
fixes `E=4`, iid standard-Gumbel affinities, `K in {1,2}`,
`T in {60,240,960}`, and five capacity profiles: no clipping, global
shortage, exact boundary, one overloaded expert under exact-total capacity,
and two overloaded experts under exact-total capacity. Expected Top-K
probabilities are computed by exact enumeration of ordered
Plackett–Luce prefixes. Expected clipped counts use exact binomial sums.
Central finite differences of those independently evaluated expected
fields are compared to the theorem's analytic Jacobians. A separate paired
Monte Carlo component samples 4,000 fresh Gumbel batches for each `(K,T)`
and reuses each request batch across the capacity profiles.

### Findings

- All **30 exact cells** passed the registered capacity, probability, and
  Jacobian checks. The largest entrywise error between the analytic admitted
  Jacobian and the central finite difference was `1.10e-8` (tolerance
  `2e-7`). The no-clipping requested/admitted Jacobians agreed, and every
  sampled no-clipping batch had `A=R`.
- Under global shortage, the per-coordinate attenuation decreased from
  `0.1644` to `1.1591e-4` for `K=1`, and from `0.05874` to
  `2.4783e-10` for `K=2`, as `T` rose from 60 to 960.
- At the exact boundary, attenuation did **not** vanish: for `K=1` it rose
  from `0.4801` to `0.4950`; for `K=2` it was `0.5` to numerical precision.
- In the one- and two-overloaded exact-total profiles, only the deliberately
  overloaded coordinates had attenuation tending to zero. Unsaturated
  coordinates tended toward one. This is consistent with the coordinatewise
  theorem; the projected Jacobian norm is not simply the minimum
  attenuation because `P0` mixes rows.
- In the global-shortage Monte Carlo control, the fraction of batches with
  every expert clipped was:

| K | T=60 | T=240 | T=960 |
|---:|---:|---:|---:|
| 1 | 0.4508 [0.4354, 0.4662] | 0.8793 [0.8688, 0.8890] | 0.9993 [0.9978, 0.9997] |
| 2 | 0.8215 [0.8093, 0.8331] | 0.9958 [0.9932, 0.9973] | 1.0000 [0.9990, 1.0000] |

  On every such batch, admitted counts equaled the uniform capacity vector
  and the implemented admitted sign feedback was exactly zero. These are
  Wilson 95% intervals from the registered 4,000-batch Monte Carlo runs.

The machine-readable summary and CSVs are under
[`results/c2_topk_saturation_sensitivity/`](../../results/c2_topk_saturation_sensitivity/).
The runner hash is `916532d98dc1024c757e5105ed9fad52fbc7dca1814f894412a65c54178a009f`;
the exact-grid CSV hash is `2f9f89b2393fd50c9584ac74413e8a3d1ab8cfceec6f963d00f9bb9ef0b7a713`;
the Monte Carlo CSV hash is `578a745dd19aa8cb958c46c031c03e98465e4a0290410c0f5455d25d0358f976`.
Reproduce from the repository root with:

```powershell
python scripts/run_c2_topk_saturation_sensitivity.py
```

## What this supports—and what it does not

This makes the professor's `d E[A]/d theta` idea a correct theorem and
demonstrates its Top-2 extension under the declared Gumbel family. It
corrects the stronger interpretations: finite positive-capacity
observations remain identifying; per-expert score-ranked retention cannot
change `A=min(R,C)`; the sign controller freezes, rather than accumulating
bias, under uniform global saturation; and the result does not show that
requested feedback always improves overflow.

It does **not** establish the professor's proposed extra-collective price.
The audited Megatron path already aggregates a per-expert count vector for
the bias update; replacing its post-drop counts with pre-drop counts may
reuse that reduction. The incremental memory, kernel, and latency cost must
be measured on the exact implementation before assigning a telemetry price.
The result also does not defeat the current finite-instance
outcome-map/adaptive-testing reduction, prove a general Top-K-specific
regret bound, or demonstrate trained-model quality. The attenuation formula
is generic clipped-binomial calculus; the remaining conference-level work is
to prove a quantitative consequence of the Top-K choice geometry and
validate it in the existing capacity-drop system setting without claiming
more than the measurements show.

Primary-source boundaries for that system scope include [DeepSeek-V2's
device-level lowest-affinity dropping](https://arxiv.org/abs/2405.04434),
the [ICLR 2026 capacity-aware inference drop method](https://proceedings.iclr.cc/paper_files/paper/2026/hash/94e845868a9ace4bc239d0c529d32f4c-Abstract-Conference.html),
and [Megatron-Core's routing implementation](https://github.com/NVIDIA/Megatron-LM/blob/main/megatron/core/transformer/moe/token_dispatcher.py).
They describe different admission paths; none alone establishes a
requested-versus-admitted telemetry break-even for the audited controller.

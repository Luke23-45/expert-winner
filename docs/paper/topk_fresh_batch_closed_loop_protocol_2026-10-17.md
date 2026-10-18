# Locked paired synthetic study: static versus fresh affinity batches

## Research question

The existing long-run population theorem takes the batch-size limit at fixed horizon and then takes the long-horizon limit. Its first finite-batch check reused one affinity matrix at every round and showed a large magnitude discrepancy at `H>=4`. This registered follow-up asks whether that discrepancy is specific to reusing a fixed batch, and whether finite-`T` expected-admission dynamics predict closed-loop costs when each round receives fresh iid tokens.

This is a continuation of the canonical formal model: hard Top-K routing on `a-q`, independent per-expert admission `A=min(R,C)`, uniform target, zero leak, and the same proportional pressure update. It introduces no device-capacity, score-ranked-count, or new-controller mechanism.

## Locked design

- Experts `E=4`; `K in {1,2,3}`; iid standard Gumbel affinities; `gamma=1`, `delta=0`, `q_0=0`.
- Exact-total capacities: `C_1/T=K/4-r`, `C_e/T=K/4+r/3` for `e=2,3,4`, with `r=1/48`.
- Batch sizes `T in {2304,9216}`; 12 paired plants per `(K,T)`.
- Gains use the previously registered `eta=0.8*K*(E-1)/L_F`, with `L_F=(1/e)*(E-1)*binom(E-2,K-1)`.
- Horizons `H in {1,2,4,8,16,32,64}`.
- Two temporal regimes: **static** reuses each plant's initial affinity matrix for all rounds; **fresh** draws an independent iid matrix each round. The initial matrix and the first-step outcomes are paired across regimes for each replicate.
- In each regime, requested and admitted feedback arms share the same affinity batch at every round within that paired plant. Feedback equations, tie rule, capacity vector, and initial pressures are identical across regimes.

## Finite-`T` population comparator

For a symmetric relative pressure `q=(0,x,x,x)`, let `p_s(x)` be the exact Gumbel Top-K inclusion probability of the short-capacity expert and `p_r(x)=(K-p_s(x))/3` the inclusion probability of each rival. For `X~Binomial(T,p)`, define `m_T(p,C)=E[min(X,C)]` and `o_T(p,C)=E[(X-C)_+]`. The implemented controller uses the canonical cumulative state update
`q_next=Pi_g(q+eta*(L/(K*T)-mu))`. The deterministic finite-`T`
mean-feedback recurrence is

```text
x_(n+1) = x_n + eta * (m_T(p_r(x_n), C_r)-m_T(p_s(x_n), C_s))/(K*T).
```

Its expected per-batch overflow is

```text
g_T(x) = [o_T(p_s(x),C_s)+3*o_T(p_r(x),C_r)]/T.
```

The primary comparator is the cumulative finite-`T` mean-recursion gap `sum_(n<H) [g_T(x_n)-g_T(0)]`. Also report the iterated population-limit prediction from the existing theorem. The finite-`T` comparator is a deterministic expected-field recursion; because gauge projection and state evolution interact with noise, it is **not** asserted to equal the expected stochastic closed-loop cost.

## Primary outcomes

For each `(regime,K,T,H)`, report paired admitted-minus-requested cumulative overflow per token-batch, its mean and 95% paired t interval, fraction of plants with positive gap, absolute error and ratio to the finite-`T` mean-recursion comparator, and absolute error and ratio to the iterated-limit comparator. Compare static and fresh regimes with paired replicate IDs. Preserve every plant and endpoint; no exclusions.

## Mandatory checks

At every arm and round verify `sum R=K*T`, `R_e<=T`, `A=min(R,C)`, and `sum(R-A)=sum(max(R-C,0))`. The initial overflow must match across arms and across temporal regimes for each replicate. No exact Top-K ties are permitted. Run a no-clipping control with `C_e=T`; requested/admitted trajectories must match exactly. Check that the finite-`T` recurrence starts with zero gap and that its first pressure increment agrees with the exact binomial means. All these checks are reported before interpreting the cost outcome.

## Decision rules

1. If fresh-batch results approach the finite-`T` recurrence substantially better than static-batch results as `T` increases, report fixed-batch reuse as the source of the earlier finite-size mismatch and use fresh-batch dynamics for training-like claims.
2. If neither regime tracks the finite-`T` comparator at registered `T,H`, the finite-`T` mean-field recurrence is insufficient for these horizons; do not claim it predicts stochastic controller cost.
3. If both track the finite-`T` comparator but not the iterated-limit comparator, retain only the finite-`T` prediction over the validated range; do not conflate fixed-`T` and iterated limits.
4. Positive gaps in this one family do not establish universal controller dominance, a costed-telemetry break-even, model-quality benefit, or separation from the independent outcome-map benchmark.

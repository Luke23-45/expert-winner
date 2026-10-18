# Preregistered arbitrary-Top-K two-step overflow experiment

**Status:** fixed before execution. This is the controlled finite-grid check
for [`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md).
It remains within the existing canonical model.

## Primary endpoint

For each paired plant,

```text
G_T = (J_0^A + J_1^A - J_0^R - J_1^R)/T
g_(E,K)(d) = Phi_(E,K)(d) - K/E.
```

Report the paired sample mean, 95% paired-mean `t` interval, asymptotic
formula, absolute error to that formula, fraction of positive individual
paired gaps, and all three arms' mean overflow. No parameter cell is dropped.

## Fixed design

- `E in {3,4,8}` and every `K=1,...,E-1`.
- Let `m=min(K,E-K)` and `r=m/(2E)`. Split the compensating capacity
  equally: `sigma_e=r/(E-1)` for every `e>=2`. This satisfies the theorem's
  strict capacity constraints and makes each capacity integral for all
  registered `T`.
- `d in {1/4,1/2,3/4}` and `eta=d*K/r`, so the population pressure
  displacement is exactly the same three values for every `(E,K)`.
- `T in {3360,6720,13440}` and 50 independent plants per `(E,K,T)`.
  Replicate `n` uses seed `20261031 + 100000*E + 1000*K + 10*T_index+n`,
  with zero-based `T_index` and `n=0,...,49`.
- Affinity entries are iid integers uniform on `{0,...,2^30}`, divided by
  `2^30`. Each exact same matrix is reused across both routing steps, all
  three gains, and all feedback arms. Scores are compared by exact integer
  cross-multiplication; ties at the Top-K boundary use lower expert index.

## Arms and locked checks

Run requested feedback, admitted feedback, and no feedback. At both steps,
assert `sum_e R_e=K*T`, `A=min(R,C)`, and exact overflow accounting. Confirm
identical step-zero overflow across the paired arms. For every registered
`(E,K,T,replicate,d)`, also run requested and admitted feedback with
`C_e=T` for every expert; this no-clipping control must have zero overflow
and identical requested/admitted pressures and routes.

Record exact ties, including any Top-K boundary ties. Do not remove tied
plants. The script must fail immediately on a violated invariant. Rerun the
full script and require byte-identical CSV and summary hashes before
interpreting the study.

## Interpretation boundary

This finite-grid experiment checks the theorem's direction and finite-size
approach for selected `(E,K)` values. It cannot prove the asymptotic limit,
cover all affinity distributions, establish trained-model quality, measure
telemetry cost, or defeat the exact finite-instance outcome-map benchmark.

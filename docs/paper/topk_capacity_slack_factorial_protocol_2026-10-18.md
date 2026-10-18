# Preregistered capacity-slack factorial for the existing Top-K feedback theorem

**Research line:** requested/admitted count feedback under the canonical
Top-K router and independent per-expert clipping. This is an extension of
the theorem and experiment in
[`topk_long_run_admitted_overflow_theorem_2026-10-17.md`](topk_long_run_admitted_overflow_theorem_2026-10-17.md),
not a different admission model or controller.

## Question and theorem-derived prediction

The existing population theorem predicts that with a single under-capacity
expert and equal compensating capacity on the others, the admitted-feedback
arm drifts toward greater overflow while the requested-feedback arm remains
at the initial population state. Its iterated long-run average cumulative
gap is exactly `(E-1)r` overflow assignments per token per round. This
experiment tests the finite-batch trajectory and the predicted dependence on
the shortage `r`, while varying `E`, every nontrivial `K`, affinity law, and
whether batches are reused or resampled.

The primary comparison is each observed paired cumulative gap against the
numerically evaluated population recurrence at the same horizon. The
secondary asymptotic check is whether the horizon-average gap approaches
`(E-1)r` as the registered horizon grows. A positive finite-sample gap alone
does not verify the predicted magnitude.

## Locked design

- `E in {4,8}` and every `K in {1,...,E-1}`.
- Independent, identically distributed affinity coordinates under
  standard Normal, Logistic(0,1), or standard Gumbel laws.
- Exact-total capacities
  `C_1/T=K/E-r`, `C_e/T=K/E+r/(E-1)` for `e>1`.
- For each `(E,K)`, define
  `r_max=min(K/E,(E-K)/(E*(E-1)))`; use `r in {r_max/4,r_max/2}`.
  These are strict interior shortages and make every capacity positive and
  below `T`.
- For each capacity profile, choose batch sizes `T=d*{8,32}`, where `d` is
  the least common denominator of the capacity fractions. Thus all capacities
  are integers and `sum C=K*T`.
- Controller: the existing gauge-projected proportional update,
  `q_next=Pi_g(q+eta*(L/(K*T)-1/E))`, with `L=R` or `A`, zero leak, and
  uniform target. For each `(law,E,K)`, fix
  `eta=0.8*K*(E-1)/L_F` using the theorem's stated density upper bound. Do not
  retune gain by capacity profile, horizon, batch regime, or observed result.
- Use 8 paired replicates per `(law,E,K,r,T,batch_regime)`. The deterministic
  seed depends on `(law,E,K,T,replicate,batch_regime)` but not on `r`, so
  different capacity profiles use common random numbers. Requested and
  admitted arms always receive the same affinity batch at each step.
- Batch regimes are `static` (reuse one affinity matrix at every step) and
  `fresh` (draw a new independent matrix at each step). The theorem's static
  regime is primary; fresh batches are reported separately as an external-
  validity check, not merged into the theorem's estimand.
- Horizons: `H in {1,2,4,8,16,32}`. Preserve all replicate and horizon rows.

## Outcomes and controls

For each plant and horizon, report the paired cumulative overflow difference
`sum_{n<H}(J_n^A-J_n^R)/T`, the horizon-average version, the population
recurrence prediction, absolute prediction error, paired 95% t interval,
and fraction of replicates with positive gap. Report `((E-1)r)` next to the
largest-horizon average, but do not call it attained unless the trajectory
has numerically approached the theorem's fixed point.

At every arm and round, assert request mass `sum R=K*T`, `R_e<=T`,
`A=min(R,C)`, and `sum J=sum(R-A)`. Requested and admitted arms must have
identical initial-state costs. Count exact score ties. A no-clipping
negative control with `C_e=T` must give identical requested/admitted
pressure trajectories and zero overflow. The population response integral
must meet the quadrature error tolerance before any simulation begins.

## Failure criteria and interpretation

Any violated invariant, tie, invalid capacity, unstable theoretical step
size, failed quadrature, or failed no-clipping control invalidates that run.
Report all registered cells, even if the empirical sign or confidence
interval disagrees with the theorem prediction. The theorem is an iterated
large-batch-then-long-horizon statement: this finite grid cannot establish
fixed-`T` infinite-horizon convergence.

This experiment tests robustness and finite-size transfer of the existing
mechanistic result. It does not establish a signal-information advantage:
on the one-short symmetric population trajectory, conservation reconstructs
the clipped coordinate from the admitted rivals. It does not prove a
universal controller ranking, trained-model benefit, implementation cost,
or novelty over censored-feedback/active-testing theory. The multi-saturated
two-world theorem remains the separate signal-value candidate.

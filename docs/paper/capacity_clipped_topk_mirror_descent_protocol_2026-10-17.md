# Exact synthetic audit protocol: pressure update and mirror descent

## Question

Check that the existing canonical proportional admitted update, when
interpreted as its fresh-batch expected update in the Top-1 Gumbel model,
equals the corresponding entropic mirror-descent step in expert
probabilities. This is an algebra/implementation audit of the theorem in
[`capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md`](capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md),
not an empirical controller comparison.

## Locked design

- `E=3`, `K=1`, iid standard Gumbel, `gamma=1`, zero leak, canonical
  `A_e=min(R_e,C_e)`.
- Batch sizes `T in {12,24,60}`.
- Capacity profiles: uniform exact-total `C=(T/3,T/3,T/3)` and
  heterogeneous exact-total `C=(T/6,5T/12,5T/12)`.
- Request-probability profiles: uniform and two fixed nonuniform profiles
  `(1/2,1/3,1/6)` and `(1/6,1/2,1/3)`.
- Targets: uniform and the normalized capacity profile.
- Stepsizes `eta in {1/100,1/20,1/10}`.
- Compute expected admitted errors with exact binomial sums. Compare (a) the
  canonical pressure update followed by Gumbel-softmax routing with (b) the
  closed-form entropic mirror step. Also shift the starting pressure by a
  common constant as a gauge control.

## Pass criteria

1. Every capacity vector is positive, integral, and sums to `T`.
2. Every mean admitted error matches the exact marginal clipped-count sum.
3. The maximum coordinate difference between the two next probability
   vectors is below `2e-14` for every registered cell.
4. Common pressure shifts leave the next probability vector unchanged to
   the same tolerance.
5. The no-clipping control `C=(T,T,T)` matches the requested-signal
   potential-gradient formula.

No Monte Carlo estimates are used. The calculation checks exact expectations
and the floating-point implementation of the update identity. It does not
test convergence, objective decrease at arbitrary step sizes, fresh-batch
noise, or performance on a trained model.

## Reproduction

From the repository root:

```powershell
python scripts/run_capacity_clipped_mirror_descent_audit.py
```

The deterministic cell table and summary are written to
`results/capacity_clipped_mirror_descent_audit/`.

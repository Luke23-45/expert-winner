# Exact synthetic audit protocol: admitted-field curl across finite capacities

## Purpose

Audit the general three-expert Top-1 curl theorem in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md)
without changing the canonical per-expert clipping rule. The experiment
evaluates exact finite-batch expectations; it does not estimate them from a
sample of routing outcomes.

## Locked model and cells

- Three experts, Top-1 routing, iid standard Gumbel affinities, pressure gain
  `gamma=1`, and uniform per-expert integer capacity `C`.
- Main cells: `T=3m`, `C=m`, for every integer `m=1,...,30`. These have
  exact total capacity `3C=T`.
- Main skewed request probability: `p=(1/2,1/3,1/6)`, realized by the
  pressure representative `q=-log(p)` when the Gumbel location vector is
  zero.
- Symmetry control: `p=(1/3,1/3,1/3)` at the same capacities.
- No-clipping control: `C=T` at the main skewed probability vector.
- Orientation control: swap the first and third entries of the main skewed
  probability vector; the signed curl must reverse.

## Primary quantity and pass rules

For each expert, compute the exact clipping derivative
`alpha_e=Pr[Binomial(T-1,p_e)<C]`. The exact quotient curl in directions
`e_1-e_3` and `e_2-e_3` is

```text
Omega = sum_cyclic p_i*alpha_i*(p_j-p_k).
```

All calculations use rational arithmetic. The registered checks are:

1. `Omega` is nonzero at every main skewed cell.
2. `Omega` is exactly zero at every symmetric control.
3. `Omega` is exactly zero in every no-clipping control.
4. The expert-swapped control has curl exactly `-Omega`.
5. Every capacity is positive, integral, and the main exact-total identity
   `3C=T` holds.

These checks audit a fixed interior witness as batch size and capacity grow.
They do not prove the theorem's open-set conclusion, which is established
analytically in the linked theorem, and they do not test a controller's
closed-loop performance.

## Reproduction

From the repository root, run:

```powershell
python scripts/run_top1_curl_capacity_scaling.py
```

The script writes its deterministic CSV and JSON summary under
`results/top1_curl_capacity_scaling/`. No trained model, GPU, random seed, or
Monte Carlo tolerance is involved.

# Robustness audit of the Top-1 requested-versus-admitted delay theorem

**Run date:** 2026-10-17  
**Base revision:** `e1648512e22844f4d8e892577dfc011f83ac307a` (worktree dirty)  
**Evidence class:** exact-rational paired synthetic robustness audit; not a
sample of routers or workloads.

## Result

The existing one-update delay theorem is stable across the full tested
parameter grid and an explicitly certified neighborhood of affinity
matrices. For each of 100 deterministic affinity perturbations, four row
replication factors, and three step sizes, requested feedback reached balance
at batch index 2 with cumulative overflow `2m`; admitted feedback reached it
at index 3 with cumulative overflow `3m`. The difference was exactly `m` in
all 1,200 paired `(perturbation, replication, step-size)` cells.

The exact outcome is the theorem's predicted outcome, not a fitted trend:

| Quantity | Requested feedback | Admitted feedback |
|---|---:|---:|
| First balanced batch index | 2 | 3 |
| Cumulative overflow through first balanced batch | `2m` | `3m` |
| Paired excess overflow |  | `m` |

For each cell, `m` ranges over `{1,2,5,10}` and `eta` over
`{2/25, 9/100, 1/10}`. All calculations used exact rational arithmetic.

## Robustness certificate

The executable independently recomputes all 36 affine winner inequalities
over the six proposed states and the closed interval
`eta in [2/25,1/10]`. The minimum unperturbed margin is exactly `1/300`.
Every perturbed affinity entry differs from its base value by at most
`1/1200`; a winner-minus-competitor margin can therefore decrease by at most
`1/600`. The route sequence remains strict with margin at least `1/600`.
The smallest margin observed across every simulated arm and step was exactly
`1/600`, attaining the certificate.

The analytic inequality proves the same route sequence for every affinity
matrix in the entrywise perturbation box, not only the 100 sampled matrices.
The finite run is an implementation and exact-arithmetic audit of that
uniform bound.

## Professor-suggestion controls

- **Score versus position retention:** both per-expert policies produced
  identical count, pressure, and overflow paths. The selected token identities
  can differ, but each expert retains exactly `min(R_e,C_e)` routes, so the
  admitted-count signal is unchanged.
- **No-clipping control:** at capacity `3m`, requested and admitted signals
  generated identical pressure paths.
- **No-feedback control:** the router remained on the initial saturated
  route pattern across the six-batch horizon.

These checks directly test the proposed score-ranked mechanism under the
formal independent per-expert admission rule. They do not test a coupled
device/group capacity rule.

## Reproducibility and limits

Run `python scripts/run_robust_delay_experiment.py` from the repository root.
The run produced 43,200 step rows, with summary and trajectory hashes:

| Artifact | SHA-256 |
|---|---|
| `summary.json` | `0dbada9e6b23b2f453d95dd6b07ae7eb384a4c2619e6c8b4bd0f92fd5d6e94c3` |
| `trajectories.csv` | `5b7d378693c8eb258fe45d9d3c38ca95721f1c1d46d5106d07b520ed5fa8ffec` |

See the [protocol](closed_loop_delay_robustness_protocol_2026-10-17.md),
[summary](../../results/closed_loop_delay_robustness/summary.json),
[trajectories](../../results/closed_loop_delay_robustness/trajectories.csv),
and [executable](../../scripts/run_robust_delay_experiment.py).

This improves the robustness of one fixed `E=3,K=1` theorem. It does not
generalize to arbitrary `E,K`, prove optimality over all causal admitted
policies, establish a model-quality or deployment effect, or bypass the exact
polyhedral outcome-map representation of each finite instance. The
top-conference-level family/benchmark separation remains open.

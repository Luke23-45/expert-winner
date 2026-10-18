# Results: admitted-sign advantage in the controlled Top-2 family

**Run date:** 2026-10-17  
**Source revision:** `e1648512e22844f4d8e892577dfc011f83ac307a` (worktree dirty)  
**Protocol:** [fixed before execution](top2_signed_bias_separation_protocol_2026-10-17.md)  
**Executable:** [exact-rational runner](../../scripts/run_top2_signed_bias_separation.py)

## Outcome

All 900 paired `(affinity perturbation, replication, gain)` cells passed. In
every cell, admitted feedback first reached global saturation at batch 3,
requested feedback at batch 8, and no feedback did not reach it in the nine
batches. The exact nine-batch cumulative overflow was:

| Feedback | Overflow for replication factor $m$ | For base batch $m=1$ |
|---|---:|---:|
| Admitted counts | $93m$ | 93 |
| Requested counts | $98m$ | 98 |
| No feedback | $99m$ | 99 |

Thus the paired admitted arm saved exactly `5m` overflow assignments versus
requested feedback and `6m` versus no feedback for this fixed horizon and
family. This is an exact mechanism result, not an estimated population
effect.

## Design and checks

- 100 independent deterministic perturbation patterns of the 20 base rows;
  each entry changed by at most `1/1000`.
- Replications `m={1,3,10}`. Affinities and gains are scaled by `1/250`;
  the tested gains are `{0.0009,0.00096,0.001}`, including the canonical
  `bias_gamma=0.001` value.
- Requested, admitted, and no-feedback arms were paired on each plant.
- Score-ranked and position-ranked per-expert retention were paired for each
  arm; their admitted-count, bias, and overflow paths were identical.
- Capacity `20m` per expert served as the no-clipping control; requested and
  admitted state trajectories agreed exactly.
- All routing, signed feedback, bias updates, clipping, and overflow were
  calculated in exact rational arithmetic. The output contains 48,600
  per-batch trajectory rows.

In theorem units, the exact base minimum Top-2 cutoff margin over the compact
gain interval `[9/40,1/4]` is `1/10`. After scaling by `1/250`, the tested
interval is `[9/10000,1/1000]` and the minimum margin is `1/2500`. The
entrywise perturbation can reduce a pairwise margin by at most `1/125000`, so
the analytic lower bound is `49/125000`. The observed minimum margin across
all trajectories was exactly `49/125000`, and every route was strict.

## Reproducibility

The run writes:

- [machine-readable summary](../../results/top2_signed_bias_separation/summary.json)
- [per-batch trajectories](../../results/top2_signed_bias_separation/trajectories.csv)

SHA-256:

| Artifact | Hash |
|---|---|
| `summary.json` | `4cc1f26fa46b37e5f66de0362671604dc50772b65947046dffa3a8a734597e04` |
| `trajectories.csv` | `92ab89a14479639a9f30c96c818f604a03b89fd4961179933f2cb0b3506e6ee7` |

Reproduce from the repository root with:

```powershell
python scripts/run_top2_signed_bias_separation.py
```

## Interpretation boundary

This run audits the theorem and its strict-margin robustness. It does not
show that the result is typical of real MoE routers, that training quality
improves, or that this finite family escapes exact simulation by the general
polyhedral outcome-map benchmark. The proof's value is a controlled,
parameterized positive comparison for the existing signed-bias controller,
alongside the existing negative examples where admitted feedback freezes or
performs worse. It is not a universal controller ranking.

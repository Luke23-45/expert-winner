# Sparse finite-weight Top-2 audit: results

**Protocol:** [controlled protocol](topk_sparse_family_e4_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_sparse_family_e4_pilot.py`](../../scripts/run_topk_sparse_family_e4_pilot.py)  
**Summary:** [`../../results/topk_sparse_family_e4_pilot/summary.json`](../../results/topk_sparse_family_e4_pilot/summary.json)  
**Paired samples:** [`../../results/topk_sparse_family_e4_pilot/paired_plants.csv`](../../results/topk_sparse_family_e4_pilot/paired_plants.csv)

## Exact finite-weight plant

The two Gumbel-Top-2 worlds use weights `(100,2,1,1)` and `(100,1,2,1)`.
Exact enumeration of all 24 Plackett-Luce rankings gives initial inclusion
probabilities

```text
world 0 = (68225/68289, 670/1339, 34183/136578, 34183/136578)
world 1 = (68225/68289, 34183/136578, 670/1339, 34183/136578).
```

Capacities are `(7/8,1/8,1/8,7/8)`, with exact total 2. Experts 0, 1, and
2 are over capacity in both worlds; expert 3 is below capacity and has the
same marginal request probability in both worlds. All capacities are
strictly between zero and one.

Numerically solved target pressures have maximum inclusion residual
`1.36e-13`. Under their matching world, each sends the population inclusion
vector to the capacity vector. The fixed common action `q^0` has equal-prior
population overflow `0.0555074847`; this is a diagnostic feasible action,
not the admitted-optimal value. No feedback has exact initial
population overflow `341291/546312` (`0.6247181098`).

## Paired count-law audit

The runner uses exact Top-2 subset probabilities, couples the two worlds by
sharing the expert-3 request count, and samples each world conditionally on
that count. This gives the correct world-specific multinomial count law and
an exact coupling for the retained unsaturated signal.

| Batch `T` | Equal admitted vectors | Equal requests with no clipping | Request classifier errors |
|---:|---:|---:|---:|
| 1,600 | 500/500 | 0/500 | 0/500 |
| 6,400 | 500/500 | 0/500 | 0/500 |
| 25,600 | 500/500 | 0/500 | 0/500 |

The classifier chooses world 0 when `R_1/T` exceeds the midpoint of the two
exact means. All mass-conservation and canonical-clipping checks passed.
The target-action risk values are calculated from the finite-weight
Plackett-Luce inclusion probabilities, not estimated from the paired
draws. The fixed random seeds and sampling logic are recorded in the runner.

## Interpretation

This finite-weight `E=4,K=2` experiment supports the sparse helper-expert
construction: the admitted signal hid the contested split in every paired
draw at all tested batch sizes, while the requested signal classified the
world in every draw. It is evidence for the family proof candidate, not a
proof of its asymptotic value bound. The positive common-action value
constant is still implicit; the experiment compares the requested policy
only with specified feasible actions, not with an optimized admitted
policy. It also makes no training-quality, measured telemetry-cost, or
benchmark-separation claim.

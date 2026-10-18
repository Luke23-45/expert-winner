# Results: uniform-capacity random-facet audit

**Protocol:** [locked audit](uniform_capacity_random_facet_protocol_2026-10-17.md)

**Theorem:** [uniform-capacity non-potentiality](uniform_capacity_nonpotentiality_theorem_2026-10-17.md)

**Runner:** [`../../scripts/audit_uniform_capacity_random_facets.py`](../../scripts/audit_uniform_capacity_random_facets.py)
**Artifacts:** `../../results/uniform_capacity_random_facets/`

## Results

Every recorded candidate facet was regular and mismatched under uniform
exact-total capacity. The paired no-clipping control had zero mismatches.

| (T) | Plants | Plants with over/under margin pair | Candidate facets | Regular | Mismatched | Satisfy proof's changed-row bound | Plants with ≥1 such facet | No-clip mismatches |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 256 | 400 | 248 | 83 | 83 | 83 | 61 | 57 | 0 |
| 4,096 | 200 | 176 | 119 | 119 | 119 | 102 | 83 | 0 |
| 65,536 | 80 | 79 | 116 | 116 | 116 | 114 | 62 | 0 |
| 1,048,576 | 20 | 20 | 58 | 58 | 58 | 58 | 18 | 0 |

The observed number of candidates per plant was `0.208`, `0.595`, `1.45`,
and `2.90` across the four sizes. At the largest size, all 20 plants had the
robust over/under pair; 18 also had at least one regular facet satisfying
every checked condition in the proof construction, including
`Z <= T^(1/3)/2`. Candidate counts and success fractions are descriptive
finite-sample evidence, not tests of the asymptotic rate or probability-one
limits.

The audit was rerun with the registered seeds and produced the same machine
summary hash on both executions:
`dca4ece74e7587717933ce3e12030119925781247d0e5f943e7e9fd67b2adba1`.
The input is a discrete `2^30`-denominator approximation to iid Uniform
affinities. Candidate detection, pressure scores at the constructed facet,
Top-(K) routes, capacities, and tie checks use exact integer arithmetic.
Facets with any filler-row pairwise score tie on this grid are excluded.

## What this supports

This audit checks the uniform-capacity theorem's own random-plant
construction, including its growing near-zero candidate count, robust
over/under margins, source/destination mismatch, and no-clipping negative
control. It complements the earlier full-arrangement audit, which enumerated
every regular facet in small `E=3,K=1,T=6` plants, and the separate planted-
facet probability experiments. Those experiments have different sampling
schemes and should not be pooled as one prevalence estimate.

It does not prove the theorem, establish a uniform finite-(T) success rate,
sample all directed pairs per plant, measure real-router prevalence, or show
that non-potentiality causes closed-loop performance loss. The broad
finite-outcome benchmark can still encode each finite plant's routing cells
and outputs exactly; this audit does not address that reduction.

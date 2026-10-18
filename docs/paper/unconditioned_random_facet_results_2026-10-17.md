# Unconditioned random-affinity facet audit: results

**Protocol:** [`unconditioned_random_facet_protocol_2026-10-17.md`](unconditioned_random_facet_protocol_2026-10-17.md), fixed before execution.  
**Implementation:** [`audit_unconditioned_random_facets.py`](../../scripts/audit_unconditioned_random_facets.py).  
**Artifacts:** [`summary.json`](../../results/unconditioned_random_facets/summary.json) and [`replicates.csv`](../../results/unconditioned_random_facets/replicates.csv).

## Results

The experiment used 500 paired iid rational-grid affinity plants per batch
size. Every candidate found a regular facet. The no-clipping negative
control had zero mismatches in all 2,083 retained facets.

| T | Candidate found | Regular facets | Mismatches / regular facets | Unconditional regular-mismatch rate | Mean X0/T | Mean X1/T |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 248/500 | 248/248 | 232/248 | 0.464 | 0.4715 | 0.4693 |
| 64 | 367/500 | 367/367 | 367/367 | 0.734 | 0.4962 | 0.4854 |
| 256 | 468/500 | 468/468 | 468/468 | 0.936 | 0.4968 | 0.4973 |
| 1,024 | 500/500 | 500/500 | 500/500 | 1.000 | 0.4995 | 0.4992 |
| 4,096 | 500/500 | 500/500 | 500/500 | 1.000 | 0.5005 | 0.4990 |

Candidate availability increases with `T`; the observed request fractions at
the selected facet approach `1/2`; and all observed regular facets at
`T>=64` were mismatched. This is consistent with the theorem's asymptotic
prediction. The finite-grid experiment is not itself a proof of convergence,
and 500/500 at the largest sizes does not establish a probability of exactly
one.

The script uses a discrete grid of denominator `2^30`, with exact integer
arithmetic for candidate detection, tie checks, routing, and clipping. It
checks that the only tie is the selected token's intended Top-2 boundary tie.
The script passed Python compilation and reran deterministically: the
machine-summary SHA-256 was
`a642bff9840d879f62081eeafea7e36c0627f1b7f07daa5b45bf05eb0acd5290` on both
runs.

## Interpretation

This is a controlled finite-size check of a data-selected regular facet in
the existing per-expert clipping model. It supports the proof's concrete
construction, including exact-total macro-heterogeneous capacities. It does
not sample facets uniformly, establish a prevalence over all routing
facets, demonstrate a closed-loop performance or training-quality effect,
measure observation cost, or separate the result from the finite-outcome
polyhedral benchmark. The exact asymptotic claim and its assumptions are in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).

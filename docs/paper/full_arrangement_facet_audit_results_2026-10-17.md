# Full-arrangement facet audit: exact results

**Protocol:** [`full_arrangement_facet_audit_protocol_2026-10-17.md`](full_arrangement_facet_audit_protocol_2026-10-17.md), written before this run.  
**Implementation:** [`scripts/audit_full_arrangement_facets.py`](../../scripts/audit_full_arrangement_facets.py).  
**Artifacts:** [`summary.json`](../../results/full_arrangement_facets/summary.json) and [`by_seed.csv`](../../results/full_arrangement_facets/by_seed.csv).

## Results

The audit used 40 paired iid rational-affinity plants with (E=3,K=1,T=6).
For each plant it enumerated every distinct pairwise score-tie line and every
open segment of the complete arrangement, then retained every segment where
the one-sided Top-1 request vectors differ. All computations were exact
rational.

| Capacity profile | Regular routing facets | Matched | Mismatched | Pooled mismatch fraction | Plants with a mismatch |
|---|---:|---:|---:|---:|---:|
| No clipping ((6,6,6)) | 4,320 | 4,320 | 0 | 0 | 0/40 |
| Uniform exact total ((2,2,2)) | 4,320 | 1,224 | 3,096 | (43/60) | 40/40 |
| Heterogeneous exact total ((1,2,3)) | 4,320 | 1,193 | 3,127 | (3127/4320) | 40/40 |

Every plant had exactly 108 regular route-changing facet segments. Per-plant
mismatch counts ranged from 65 to 96 of 108 under uniform exact-total
capacity and 68 to 94 of 108 under heterogeneous exact-total capacity. Every
mismatch had a nonzero exact tangential jump; every matched facet had zero
tangential jump. The no-clipping negative control had no mismatches.

The pooled fractions above use **all regular facet segments** as their
denominator. They are not the planted-facet probabilities in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md): that law samples a distinguished facet under a different construction.

## Reproduction and checks

```powershell
python scripts/audit_full_arrangement_facets.py
```

The script asserted that every retained transition was an oriented same-pair
Top-1 exchange; each profile's matched and mismatched counts summed to the
full facet count; the no-clipping control had zero mismatches; and every
mismatch had nonzero tangential component. A second execution produced the
same SHA-256 for `summary.json`:

```text
564AA50CFF4F1156209424C8F5F1791147538DAADF6935E65513A946EB248F73
```

## Interpretation

This removes one sampling ambiguity in the existing local-geometry evidence:
the obstruction is present across the complete finite Top-1 arrangement for
every one of these 40 generated plants, rather than only at a planted facet.
It supports the existing facet criterion in the declared small regime.

It does **not** establish a general probability theorem, a closed-loop cost
or quality consequence, real-router prevalence, a training result, or a
separation from the outcome-map benchmark. In particular, a full finite
arrangement can still be represented by the independent polyhedral
benchmark. The top-conference claim remains open.

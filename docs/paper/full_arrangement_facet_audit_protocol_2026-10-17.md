# Full-arrangement audit of admitted-field facet mismatch

**Status:** preregistered deterministic synthetic protocol; canonical per-expert
admission only.

## Question

The planted-facet law characterizes a facet selected by a construction. This
audit asks a different, finite question: in a fully enumerated hard Top-1
router arrangement, what fraction of all regular route-changing facets have
unequal admitted source and destination changes under canonical per-expert
clipping?

This is supporting evidence for the existing Top-K facet criterion (C3). It
does not modify the model or claim a performance advantage.

## Fixed design

- Router: (E=3, K=1, T=6), score (s_{t,e}=a_{t,e}-q_e), exact rational
  arithmetic, tie-breaking by lower expert index.
- Plants: 40 paired seeds, each an iid exchangeable rational score matrix.
  The same plant and complete arrangement are evaluated under every capacity
  profile.
- Capacity profiles: no effective clipping (C=(6,6,6)); uniform exact-total
  (C=(2,2,2)); heterogeneous exact-total (C=(1,2,3)). Each exact-total
  profile has (sum_e C_e=KT=6).
- Arrangement: enumerate every distinct pairwise score-tie line in the
  two-dimensional pressure quotient; split each line at every intersection
  with a nonparallel tie line; inspect one exact rational point in every open
  segment, including the two unbounded segments.
- Retain a segment as a regular routing facet only when its two exact
  one-sided perturbations change at least one token's Top-1 winner. Same-pair
  simultaneous exchanges count as one facet and use the aggregate exchange
  count (m).

## Recorded quantities and controls

For every seed/profile, record the number of distinct arrangement lines,
candidate open segments, regular route-changing facets, matched facets
((d_i=d_j)), mismatched facets ((d_i\ne d_j)), the maximum exact
nonzero tangential-jump certificate, and the first mismatch witness if one
exists. Define (d_i) as the admitted source decrease and (d_j) as the
admitted destination increase across the oriented facet.

Required exact controls:

1. Every one-sided transition changes requests only by
   (-m e_i+m e_j), with (m\ge1).
2. Every retained no-clipping facet is matched; requested and admitted count
   transitions coincide.
3. Under each clipped profile, every mismatch has a nonzero tangential
   component (P_0(d_i e_i-d_j e_j)) relative to the facet normal
   (P_0(e_i-e_j)).
4. Re-enumerating with the same seed yields byte-identical summaries.

## Interpretation boundary

The denominator is the number of regular route-changing **segments** in the
full affine arrangement, not a measure over pressure space, not a random
router population estimate, and not the planted-facet distribution. The
40-seed aggregate describes only this declared (E=3,K=1,T=6) generator.
The exact facet theorem, not this finite audit, establishes the
potential/non-potential implication. The audit cannot establish a closed-loop
cost gap, trained-model benefit, real-router prevalence, or separation from
the outcome-map benchmark.

## Reproduction

Run `python scripts/audit_full_arrangement_facets.py`. Outputs are written to
`results/full_arrangement_facets/summary.json` and
`results/full_arrangement_facets/by_seed.csv`.

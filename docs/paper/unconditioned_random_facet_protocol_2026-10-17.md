# Controlled audit of the unconditioned random-affinity facet theorem

**Protocol status:** fixed before running the new experiment.  
**Formal model:** hard Top-2 routing with canonical per-expert admission
`A_e=min(R_e,C_e)`.  
**Purpose:** finite-size diagnostic of the theorem in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).

## Question

For an iid affinity matrix rather than a specially planted token, does the
proof's data-selected near-tie construction find a regular Top-K facet whose
source and destination admitted-count changes disagree with probability
increasing toward one as batch size grows?

This tests the declared construction and its proof obligations. It does not
estimate a uniformly random facet, a deployment frequency, a controller
benefit, or novelty against the finite-outcome benchmark.

## Fixed design

- Experts and router: `E=4`, `K=2`, scores `a[t,e]-q[e]` (`gamma=1`),
  deterministic lower-index tie break away from the explicitly audited
  facet.
- Affinities: independent integers uniform on `{0,...,2^30}`, interpreted
  as exact rationals divided by `2^30`. This is a fine-grid approximation
  to iid `Uniform[0,1]`; all candidate tests, facet checks, route counts,
  and capacity arithmetic are exact integer operations.
- Batch sizes: `T in {16,64,256,1024,4096}`. Every size is divisible by
  four and uses `epsilon=T^(-1/2)`.
- Capacities: `C=(T/4,3T/4,T/2,T/2)`. They sum to `KT`; their limiting
  request rates straddle `K/E=1/2` at experts 0 and 1.
- Replicates: 500 independent affinity matrices per batch size, seeds
  `20261017 + 10000*T + replicate_index`.
- Candidate selection: scan rows in index order. A row qualifies when
  `5/12 <= M=(a_0+a_1)/2 <= 7/12`,
  `|a_0-a_1| <= T^(-1/2)`, and exactly one of experts 2 and 3 has affinity
  greater than `M`; equality of either outsider with `M` disqualifies the
  row so the intended rank is strict. The first qualifying row is selected.
- Facet construction: with `D=a_0-a_1`, use pressure
  `q=(D/2,-D/2,0,0)` modulo a common shift. At this pressure the selected
  row's experts 0 and 1 tie at the Top-2 boundary. The implementation checks
  every pair of scores for every other row and records whether the facet is
  regular. Nonregular grid coincidences are not silently counted as regular.
- Facet outcome: route every other row at the exact facet, compute their
  counts `X_0,X_1`, and set
  `d_0=1{X_0<C_0}`, `d_1=1{X_1<C_1}`. Record mismatch iff `d_0 != d_1`.
- Paired negative control: at the same facet and plant, set capacities to
  `(T,T,T,T)`; then both exchanged requests are admitted and mismatch must
  be false.

## Outcomes and validity checks

Record per batch size: candidate-found rate; regular-facet rate among found
candidates; mismatch rate among regular facets; unconditional rate of
regular mismatches (missing/nonregular candidates count as failures for this
quantity); the paired no-clipping mismatch count; and the distributions of
`X_0/T`, `X_1/T`, and selected row index divided by `T`.

The experiment passes its implementation checks only if:

1. every counted candidate has the exact requested rank and exact pair tie;
2. every retained facet has no other score tie in any other row;
3. every retained mismatch is exactly `1{X_0<C_0} != 1{X_1<C_1}`;
4. the no-clipping control has zero mismatches;
5. rerunning with the same seeds produces byte-identical machine summaries.

The theorem predicts candidate-found and regular-mismatch probabilities tend
to one, and `X_0/T,X_1/T` tend to `1/2`. No finite threshold, monotonicity in
`T`, or conference-level novelty is preregistered. The affinity grid is
discrete, so this experiment is numerical support for—not a proof of—the
continuous iid theorem.

## Reproduction

Run `python scripts/audit_unconditioned_random_facets.py`. Results are
written to `results/unconditioned_random_facets/`.

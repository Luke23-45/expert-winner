# Controlled audit: unconditioned iid affinities with uniform exact-total capacity

**Question.** Does the existing high-probability uniform-capacity theorem's
near-zero facet construction appear in finite random plants, with its stated
capacity margins and no-clipping control?

**Theorem under audit:**
[`uniform_capacity_nonpotentiality_theorem_2026-10-17.md`](uniform_capacity_nonpotentiality_theorem_2026-10-17.md).
This protocol tests one data-selected over/under expert pair per plant; it
does not claim to sample a facet uniformly or to verify the asymptotic theorem.

## Locked design

- `E=4`, `K=2`, scores `a[t,e]-q[e]`, `gamma=1`.
- Independent per-expert admission `A_e=min(R_e,C)` with uniform exact-total
  capacity `C=K*T/E=T/2`.
- Affinities are independent integers uniform on `{0,...,2^30}`, interpreted
  as exact rationals on a fixed approximation to `[0,1]`.
- `T in {256,4096,65536,1048576}` with `{400,200,80,20}` independent plants.
  Seed is `20261017+1000*T+replicate`.
- At zero pressure, choose the lexicographically first pair `(i,j)` with
  `R_i-C >= ceil(T^(1/3))` and `R_j-C <= -ceil(T^(1/3))`. If no pair exists,
  record the plant as a margin failure.
- For that directed source/destination pair, scan every token for the
  theorem's candidate conditions: midpoint in `[5/12,7/12]`,
  `0 < a_i-a_j <= T^(-3/4)`, and exactly `K-1` other affinities strictly
  above the midpoint. The thresholds are tested with integer arithmetic on
  the grid.
- At each candidate's exact pair-tie pressure, require no pairwise score tie
  in any filler row before counting the facet as regular. Route fillers by
  stable Top-K, compute the one-sided admitted changes, compare against the
  zero-pressure counts, and record the number of changed filler rows.
- At the same facet, the paired no-clipping control uses `C_e=T`; its two
  admitted changes must match.

## Registered outcomes

Report per batch size: number of plants with a robust over/under pair;
candidate and regular facet counts; mismatch count; number of facets also
satisfying the proof's `Z<=T^(1/3)/2` changed-row bound; and no-clipping
mismatches. These finite sizes are exploratory diagnostics: no monotonicity,
minimum finite-sample success rate, or confirmation of the asymptotic tail
bound is preregistered.

All routing, candidate, capacity, and tie checks use integer arithmetic.
The grid has positive probability of exact ties, unlike the continuous
theorem, so tied candidates are discarded and this discretization limitation
is reported. Reproduce with
[`../../scripts/audit_uniform_capacity_random_facets.py`](../../scripts/audit_uniform_capacity_random_facets.py).

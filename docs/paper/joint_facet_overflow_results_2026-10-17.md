# Results: paired facet and two-step overflow audit

**Registered protocol:** [`joint_facet_overflow_protocol_2026-10-17.md`](joint_facet_overflow_protocol_2026-10-17.md)

**Combined statement:** [`joint_topk_overflow_facet_theorem_2026-10-17.md`](joint_topk_overflow_facet_theorem_2026-10-17.md)

**Runner:** [`../../scripts/run_joint_facet_overflow.py`](../../scripts/run_joint_facet_overflow.py)

## Execution and reproducibility

The locked protocol was executed twice. Both runs produced byte-identical
plant CSVs and summary JSON. The same affinity arrays and seed schedule as
the earlier arbitrary-Top-K overflow experiment were used. All 450
`(T, replicate, d)` gap rows were then compared against that earlier E=4,
K=2 result file: overflow totals and exact normalized gaps matched in every
row. This confirms the joint audit did not change the existing experiment's
routing or control calculation.

| Artifact | SHA-256 |
|---|---|
| Protocol | `c06c6be292475efba7f379dc77da5fdbedc53e0eef4babc7c283c8fda1b54997` |
| Runner | `ed5e32e71860f24b1035856e6d4a28c976a9c439a36558ea50b30828fe324d6b` |
| Paired plant rows | `5d8dc0d2b12ac8db75ae851e31c09d3341b36604678ec849aca4de1ecb127868` |
| Facet plant rows | `a54ebf619f18e3e0913043c882dd2774236e6fe3264038af6a216bc9cdec94c1` |
| Summary | `3ff6ebfb9530a6a81a5ea310dc3d29e7957cd2e8988ae229dafc2fa2ca139702` |

All 150 plants passed the registered audit checks. Every plant had at least
one proof-defined `(0,1)` candidate; all candidates were regular two-way
facets and all had a mismatched admitted-count jump under clipping. Across
the three sizes there were 2,145 such candidates. There were zero ambiguous
candidate pressures, zero failed plants, and zero mismatches in the
no-clipping control. All routing mass, per-expert load, canonical clipping,
overflow accounting, and no-clipping controller invariants passed.
For a crossing from expert `i` to `j`, the exact clipped-count jump check uses
the boundary conditions `R_i^- <= C_i` for a one-count source decrease and
`R_j^- < C_j` for a one-count destination increase; the full jump vector is
asserted against these indicators for every retained facet.

## Paired overflow outcomes

Each cell has 50 paired plants. `D` is the two-step admitted-arm overflow
minus requested-arm overflow, normalized by `T`. The interval is the
registered 95% paired-mean t interval.

| `T` | `d` | Mean `D` | 95% interval | Theorem limit | Plants with `D>0` | Joint event |
|---:|---:|---:|---:|---:|---:|---:|
| 3,360 | 1/4 | 0.237417 | [0.235131, 0.239703] | 0.236328 | 50/50 | 50/50 |
| 3,360 | 1/2 | 0.405435 | [0.401734, 0.409135] | 0.406250 | 50/50 | 50/50 |
| 3,360 | 3/4 | 0.484440 | [0.477472, 0.491409] | 0.486328 | 50/50 | 50/50 |
| 6,720 | 1/4 | 0.237958 | [0.236644, 0.239273] | 0.236328 | 50/50 | 50/50 |
| 6,720 | 1/2 | 0.407256 | [0.404618, 0.409894] | 0.406250 | 50/50 | 50/50 |
| 6,720 | 3/4 | 0.487122 | [0.482234, 0.492010] | 0.486328 | 50/50 | 50/50 |
| 13,440 | 1/4 | 0.237582 | [0.236456, 0.238708] | 0.236328 | 50/50 | 50/50 |
| 13,440 | 1/2 | 0.406795 | [0.404673, 0.408917] | 0.406250 | 50/50 | 50/50 |
| 13,440 | 3/4 | 0.486906 | [0.483540, 0.490273] | 0.486328 | 50/50 | 50/50 |

The joint event means that the *same plant* has both a positive paired
two-step overflow gap and at least one regular mismatched facet. It occurred
in all 450 plant/gain rows; facet presence is shared across the three gains
for each plant. Candidate-facet totals by batch size were 475, 690, and 980
at `T=3,360`, `6,720`, and `13,440`, respectively; all were regular and
mismatched.

## Interpretation and limits

This is a finite-grid controlled audit of co-occurrence under the existing
canonical per-expert clipping model. The exact-grid affinities approximate,
but are not identical to, the theorem's continuous Uniform law. The run
supports the stated asymptotic result and demonstrates that the facet and
overflow phenomena coexist on the same sampled routing systems. It does not
show that the facet mismatch causes the overflow gap, that requested feedback
beats every causal controller, that the observation has a measured
communication cost, or that training quality improves. It also does not
resolve the known reduction to an exact outcome-map/adaptive-testing
benchmark.

Plant-level data are in [`../../results/joint_facet_overflow/plants.csv`](../../results/joint_facet_overflow/plants.csv)
and [`../../results/joint_facet_overflow/facet_plants.csv`](../../results/joint_facet_overflow/facet_plants.csv);
the machine-readable aggregate is [`../../results/joint_facet_overflow/summary.json`](../../results/joint_facet_overflow/summary.json).

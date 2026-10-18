# Controlled synthetic audit of the admitted-field facet theorem

**Status:** completed exploratory experiment; exact arithmetic; not preregistered.  
**Question:** across paired finite Top-$K$ plants, do the observed admitted-field jumps at regular score-arrangement facets obey the capacity-derived potential criterion?  
**Primary target:** the analytic facet criterion in [`admitted_field_facet_criterion_2026-10-17.md`](admitted_field_facet_criterion_2026-10-17.md).

## Claim under examination

Fix a static batch, hard Top-$K$ routing, and independent expert capacities
$A_e(q)=\min(R_e(q),C_e)$. At a regular facet, suppose $m$ token assignments
simultaneously exchange from expert $i$ to expert $j$. If $R^-$ is the request
count vector just before the exchange, define
\[
d_i=\min(R_i^-,C_i)-\min(R_i^- -m,C_i),\qquad
d_j=\min(R_j^-+m,C_j)-\min(R_j^-,C_j).
\]
The admitted error field's jump is
\[
\Delta g_A=P_0(d_i e_i-d_j e_j).
\]
For $E\ge3$, this jump is normal to the routing facet exactly when $d_i=d_j$.
A mismatch produces a local obstruction to a continuous cellwise-affine or
convex potential; matching
every regular facet with $d_i=d_j$ makes the field a convex
piecewise-affine subgradient on open arrangement cells.

The synthetic audit is designed to check the formula and the geometric
consequence on many finite plants. It does not establish the theorem, which
rests on the proof in the linked note.

## Plant generation and paired interventions

- Router: deterministic Top-$2$ over $E=4$ experts, $T=12$ tokens.
- Seeds: `0` through `39`, using Python's `random.Random(seed)` separately
  for every plant; each affinity entry is iid integer uniform on `[-4,4]`.
- Facet proposals: for each token, each of the six unordered expert pairs,
  and 12 draws, construct a rational pressure lying exactly on that token's
  pairwise score-tie hyperplane. Retain only regular codimension-one
  Top-$2$ facets. Coincident same-pair exchanges are retained as one facet
  with their aggregate multiplicity. Facets are deduplicated by expert pair,
  offset, and switching-token set.
- Exactness: pressures and all route comparisons use rational numbers;
  the tie rule is lower expert index, and all side and rectangle evaluations
  are strict. Admission is exactly $A_e=\min(R_e,C_e)$.
- Paired capacity profiles on the same sampled plant/facets:
  - no clipping: `(12,12,12,12)`;
  - exact-total uniform: `(6,6,6,6)`;
  - exact-total heterogeneous: `(2,4,8,10)`;
  - aggregate shortage: `(3,3,3,3)`.

The primary outcome is whether the aggregate source admitted-count decrease
$d_i$ equals the aggregate destination admitted-count increase $d_j$. Exact
secondary checks are (i) whether the computed admitted jump matches the
closed-form formula, (ii) whether matched jumps are exactly parallel to the
facet normal, and (iii) whether every sampled mismatch admits a strict local
rectangle with a nonzero exact line circulation.

## Results

The script found 1,236 sampled regular facets per capacity profile, spanning
all 40 generated plants.

| Capacity profile | Matched facets | Mismatched facets | Mismatch fraction among sampled facets | Mismatches with exact nonzero local circulation |
|---|---:|---:|---:|---:|
| No clipping | 1,236 | 0 | 0% | 0 |
| Exact-total uniform | 308 | 928 | 75.08% | 928 |
| Exact-total heterogeneous | 434 | 802 | 64.89% | 802 |
| Aggregate shortage | 809 | 427 | 34.55% | 427 |

All sampled facets passed the exact admitted-jump formula. Every matched
sample had jump $d_iP_0(e_i-e_j)$. Every mismatch had nonzero tangential jump
and the script found a strict local rectangle with nonzero exact circulation.
The no-clipping arm passed as a negative control: all facets were matched.

## Interpretation and limits

The output supports the **mechanism** in the theorem beyond the earlier
$E=3,K=1$ witness: Top-$2$ finite plants also exhibit the predicted
capacity-dependent facet geometry. The large mismatch rate under the
exact-total uniform profile is a direct counterexample to any intuition that
matching total capacity to total requested slots is enough to preserve a
potential. Local source/destination admission changes, not total capacity
alone, determine the field jump.

The fractions above are not unbiased estimates of all facets or of any
production router. Candidate facets come from the declared generator and
sampling procedure; the complete arrangement was not enumerated. Plants are
small static integer-affinity instances, and no state trajectories, overflow
ranking, learning quality, communication cost, or real-system observability
was measured. The experiment does not overcome the exact polyhedral
active-testing representation of a fixed finite instance and therefore does
not establish a class-level separation or conference-level novelty.

## Prior-art boundary checked

The standard convex-analysis bridge from cyclic monotonicity to convex
subgradients is Rockafellar's result; that theorem is a tool used here, not a
novel contribution ([Rockafellar 1966](https://msp.org/pjm/1966/17-3/pjm-v17-n3-p08-p.pdf)).
The directly relevant MoE neighbor $\phi$-Balancing defines a strictly
convex symmetric potential of the **population mean routing-probability
distribution** and derives EMA/mirror-descent updates from that objective;
the reviewed formulation is not this paper's hard admitted-count field
$P_0(KT\mu-A(q))$ ([ICML 2026 paper](https://proceedings.mlr.press/v306/chen26br.html),
[full paper PDF](https://l-z-chen.github.io/img_pdf/MoE_ICML2026.pdf)).
This distinction is a model boundary, not novelty clearance: both works use
convex-potential language in MoE load balancing, and broader prior-art review
remains necessary before making a novelty claim about the facet theorem.

## Reproduction

From the repository root:

```powershell
python scripts/run_admission_facet_ensemble.py
```

The complete per-facet observations are in
[`results/admission_facet_ensemble/facet_observations.csv`](../../results/admission_facet_ensemble/facet_observations.csv);
the machine-readable aggregate is
[`results/admission_facet_ensemble/summary.json`](../../results/admission_facet_ensemble/summary.json).

# Results: multiple low-capacity experts under Top-K feedback

**Theorem:** [`topk_multilow_population_overflow_theorem_2026-10-17.md`](topk_multilow_population_overflow_theorem_2026-10-17.md)  
**Protocol:** [`topk_multilow_population_overflow_protocol_2026-10-17.md`](topk_multilow_population_overflow_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_multilow_population_overflow.py`](../../scripts/run_topk_multilow_population_overflow.py)

## Result

The finite-batch audit covers all 32 feasible `(E,K,m)` families for
`E in {4,6}`, all three registered batch sizes, 12 paired plants per cell,
and six horizons. At `H=32`, the admitted-minus-requested cumulative
overflow gap is positive in all 1,152 paired plants (384 per batch size).
Two points in the Cartesian grid are excluded because they violate the
theorem's equilibrium-root or capacity-fraction hypotheses; the protocol
states them explicitly.

At the largest batch size, the table reports the mean across 32 families of
the 12-plant paired means and the corresponding exact population prediction.
Coverage counts family-specific 95% paired Student-t intervals that contain
that family's population prediction.

| Horizon | Mean finite-batch gap | Mean population prediction | Family intervals covering prediction |
|---:|---:|---:|---:|
| 1 | 0.000000 | 0.000000 | 32/32 |
| 2 | 0.003567 | 0.003555 | 30/32 |
| 4 | 0.020903 | 0.020773 | 29/32 |
| 8 | 0.092511 | 0.092139 | 29/32 |
| 16 | 0.360614 | 0.359461 | 30/32 |
| 32 | 1.262981 | 1.259891 | 30/32 |

At `H=32`, aggregate results across the eight eligible `(E,K)` pairs and
all eligible `m` values were:

| Batch size | Mean finite-batch gap | Population prediction | Positive paired plants |
|---:|---:|---:|---:|
| 1,440 | 1.271363 | 1.259891 | 384/384 |
| 2,880 | 1.256448 | 1.259891 | 384/384 |
| 5,760 | 1.262981 | 1.259891 | 384/384 |

Across the full 576 family/batch/horizon cells, 552 intervals contain their
population prediction. This is descriptive calibration over the registered
grid, not a confidence guarantee over all affinity laws or parameter values.

## Controls and numerical cross-check

All eight registered exact checks passed:

- capacities are valid integers, exact-total, and lie on the declared sides
  of the mean request rate;
- the exact Gumbel response starts at `K/E`, decreases on the registered
  interval, and meets its equilibrium root within `2e-12`;
- population gaps start at zero, become positive after the first round, and
  converge to `(E-m)r`;
- every finite-batch round conserves `K*T` requests and satisfies the exact
  clipping and overflow identities;
- requested and admitted trajectories agree pathwise in the no-clipping
  negative control.

The Plackett-Luce dynamic program was independently checked against direct
enumeration of ordered prefixes at three `(E,K,m,x)` settings. Maximum
absolute probability difference was `1.11e-16`.

## Reproduction artifacts

- Paired plant/horizon data: [`plant_horizons.csv`](../../results/topk_multilow_population_overflow/plant_horizons.csv)
- Machine-readable summary: [`summary.json`](../../results/topk_multilow_population_overflow/summary.json)
- Runner SHA-256: `b298a58dcbebb99534930983bb5ec01bfd182d5fc777b2948489495800a5ba09`
- Plant/horizon CSV SHA-256: `f1537ed424589bc7926af05c5fd13659ce394a6761f4c9f5591314da74f8bc68`
- An independent full rerun reproduced both hashes exactly.

Reproduce from the repository root with:

```powershell
python scripts/run_topk_multilow_population_overflow.py
```

## Interpretation

This extends the existing one-low-capacity population result to all feasible
numbers of low-capacity experts, including `m<K`, where the high-capacity
group retains a positive inclusion probability at equilibrium. In the
registered static-batch Gumbel grid, the long-run population overflow gap is
`(E-m)r` per round, and the finite-batch trajectories match its quantitative
prediction closely.

It does **not** establish that admitted feedback is generally worse. It is
one symmetric capacity family and one specified controller; other existing
families reverse the ordering. It does not prove optimality over causal
policies, fixed-finite-`T` infinite-horizon behavior, separation from the
polyhedral active-testing benchmark, an observation-cost break-even, or a
trained-model quality gain.

## Prior-work boundary checked for this extension

The closest current population-dynamics neighbor found in this targeted
primary-source check is [*Three Phases of Expert Routing*](https://arxiv.org/abs/2604.04230),
which models routing as a congestion game and studies training-time evolution
of its population equilibrium. Its stated congestion cost is linear in
population load, and its limitations identify hard capacity thresholds as a
nonlinear effect outside that model; it does not state this clipped-admission
overflow recurrence. The ICML 2026 [φ-Balancing paper](https://proceedings.mlr.press/v306/chen26br.html)
directly optimizes a convex potential of expected routing distribution with
mirror descent. It is an important population-level balancing neighbor; the
present mathematical difference is coordinatewise hard capacity clipping
inside the stated pressure dynamics, not a claim that generic population
balancing is new.

This was a targeted boundary check, not a systematic novelty review. The
class-level benchmark-reduction limitation remains in force, so this result
alone does not settle the top-conference contribution.

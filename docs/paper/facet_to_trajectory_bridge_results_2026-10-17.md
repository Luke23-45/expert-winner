# Results: facet-to-trajectory bridge experiment

**Status:** completed; protocol fixed before execution; exact-rational
trajectories. Exploratory mechanism evidence only.

## Question and model

The experiment paired the sampled regular-facet geometry from the existing
40-plant `E=4, K=2, T=12` ensemble with closed-loop trajectories on those same
plants. It used the canonical proportional gauge-pressure controller, not the
separate Megatron-style signed-bias controller:

\[
q^+=\Pi_g\!\left(q+\frac{1}{10}\left(\frac{L}{KT}-\mu\right)\right),
\quad L\in\{R,A\},\quad \mu=(1/4)\mathbf1,
\]

with fixed affinities, initial `q=0`, 120 repeated-batch updates, and exact
per-expert clipping `A_e=min(R_e,C_e)`. It compared requested, admitted, and
no-update arms at four capacity profiles. The complete protocol is
[`facet_to_trajectory_bridge_protocol_2026-10-17.md`](facet_to_trajectory_bridge_protocol_2026-10-17.md).

The primary paired contrast is
`D = cumulative_overflow(admitted) - cumulative_overflow(requested)`: positive
means admitted feedback incurred more overflow. The proposed geometric
predictor is the sampled-facet mismatch fraction already computed for that
plant and capacity. Facets were sampled, not exhaustively enumerated.

## Exact checks

The executable checked all 57,600 per-step arm records with exact rational
arithmetic. Mass conservation, clipping, and overflow identities passed at
every step. The no-clipping requested and admitted trajectories were exactly
equal on all 40 plants. All 40 initially globally saturated uniform-capacity
admitted arms stayed fixed: 39 were in the aggregate-shortage profile and one
in the exact-total uniform profile. Every arm had 120 updates. The affinity
plant hashes and input facet-file hash are in
[`summary.json`](../../results/facet_trajectory_bridge/summary.json).

## Primary results

| Capacity profile | Mean cumulative overflow: requested / admitted / none | `D` mean; median; range | `D<0 / =0 / >0` | Spearman: facet mismatch vs. `D` |
|---|---:|---:|---:|---:|
| No clipping | 0 / 0 / 0 | 0; 0; [0, 0] | 0 / 40 / 0 | undefined (both constant) |
| Exact-total uniform `(6,6,6,6)` | 201.8 / 232.45 / 321 | 30.65; 20; [-2, 141] | 2 / 13 / 25 | -0.243 |
| Exact-total heterogeneous `(2,4,8,10)` | 700.9 / 874.3 / 816 | 173.4; 179; [0, 399] | 0 / 2 / 38 | -0.284 |
| Aggregate shortage `(3,3,3,3)` | 1440.025 / 1440.025 / 1443 | 0; 0; [0, 0] | 0 / 40 / 0 | undefined (`D` constant) |

For the uniform exact-total profile, admitted feedback had lower cumulative
overflow on 2 plants, tied on 13, and had higher overflow on 25. Under
heterogeneous exact-total capacities it tied on 2 and had higher overflow on
38. Under aggregate shortage, the requested and admitted arms tied exactly
on all 40 plants, despite variation in the sampled-facet mismatch fraction.
No feedback was worse on average in the two exact-total profiles, but these
40 hand-generated plants are not a workload population and do not justify
population inference.

## Interpretation

This experiment **does not support using the sampled local facet-mismatch
fraction as a predictor of requested-versus-admitted cumulative overflow**:
the two defined rank correlations are modest and negative, and the
aggregate-shortage condition has varying geometric mismatch but zero paired
cost difference. This does not refute the local facet theorem. It shows that
the theorem's geometric obstruction alone does not determine this finite
closed-loop cost. Capacity regime, visited cells, and the pressure dynamics
also matter.

The observation that admitted feedback loses to requested feedback on most
plants in these two capacity profiles is specific to this proportional
controller, gain, generator, initialization, and horizon. It must not be
transferred to the signed-bias results, which have a different controller and
show the opposite ranking on some exact families. The result does not prove a
general winner, a windup theorem, a real-system effect, a telemetry cost, or a
Top-K advantage over the polyhedral outcome-map benchmark.

## Reproduction and artifacts

Run `python scripts/run_facet_trajectory_bridge.py`. Outputs:

- [`summary.json`](../../results/facet_trajectory_bridge/summary.json)
- [`paired_plants.csv`](../../results/facet_trajectory_bridge/paired_plants.csv)
- [`trajectories.csv`](../../results/facet_trajectory_bridge/trajectories.csv)

The output JSON records the protocol, script, and input SHA-256 digests.

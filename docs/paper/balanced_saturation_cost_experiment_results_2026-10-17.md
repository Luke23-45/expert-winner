# Results: balanced-request saturation cost theorem

**Protocol:** [`balanced_saturation_cost_experiment_protocol_2026-10-17.md`](balanced_saturation_cost_experiment_protocol_2026-10-17.md)  
**Theorem:** [`balanced_saturation_cost_theorem_2026-10-17.md`](balanced_saturation_cost_theorem_2026-10-17.md)  
**Runner:** [`../../scripts/run_balanced_saturation_cost_experiment.py`](../../scripts/run_balanced_saturation_cost_experiment.py)  
**Artifacts:** [`summary.json`](../../results/balanced_saturation_cost/summary.json), [`affinities.csv`](../../results/balanced_saturation_cost/affinities.csv), [`plants.csv`](../../results/balanced_saturation_cost/plants.csv), [`trajectories.csv`](../../results/balanced_saturation_cost/trajectories.csv)

## Exact controlled result

The experiment evaluated 110 rational-affinity plants across 11 `(E,K)`
cells: `E={3,4,5,6}`, with the deduplicated choices
`K={1,floor(E/2),E-1}`, and ten registered plants per cell. Each plant had
exactly balanced initial requests, positive capacities no larger than that
balanced count, aggregate shortage, and a strict capacity gap at the Top-K
cut. The routing, pressure updates, clipping, and costs used
`fractions.Fraction` throughout.

All 110 plants passed every registered exact assertion:

- Requested feedback and no feedback remained at the initial pressure and
  incurred the same aggregate-shortage floor at every state.
- Admitted feedback followed its constant saturated-feedback path through
  the first unsaturated state.
- Every admitted arm exited global saturation by its exact `N_sep` bound.
- The identity `J_A-D=sum_e(C_e-A_e)>=0` held at all 13,345 admitted-arm
  states. It was strict at every first-exit state.
- The cumulative admitted-minus-requested overflow gap became positive by
  the predeclared prefix `N_sep+1` for every plant.
- The requested/admitted no-clipping control matched exactly over the full
  registered horizon.

| `E` | `K` | Plants | First exit `tau` range | Bound `N_sep` range | Cumulative gap by `N_sep+1` | Final cumulative gap |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1 | 10 | 8 | 16 | 24–27 | 24–27 |
| 3 | 2 | 10 | 15–16 | 30–31 | 37–41 | 37–41 |
| 4 | 1 | 10 | 8 | 25 | 89–93 | 89–93 |
| 4 | 2 | 10 | 24 | 73 | 231–253 | 231–253 |
| 4 | 3 | 10 | 24 | 73 | 226–231 | 226–231 |
| 5 | 1 | 10 | 9 | 36 | 239–242 | 239–242 |
| 5 | 2 | 10 | 35 | 141–142 | 884–909 | 884–909 |
| 5 | 4 | 10 | 35 | 141–142 | 534–647 | 534–647 |
| 6 | 1 | 10 | 10 | 49 | 519–527 | 519–527 |
| 6 | 3 | 10 | 96 | 484–485 | 4,913–4,961 | 4,913–4,961 |
| 6 | 5 | 10 | 48 | 241–243 | 1,487–1,511 | 1,487–1,511 |

The first exit was earlier than the conservative all-token bound in all 110
plants. The experiment therefore validates the sign and finite-horizon
consequence but also shows that `N_sep` is loose for this generator. It is
not a test of workload prevalence: the plants are constructed from balanced
K-subset designs. It is an exact implementation audit of the theorem's
quantifiers over a nontrivial finite grid, not statistical evidence about
trained models.

## Scope

This result connects the existing saturation-exit theorem to a cumulative
overflow comparison under a request-balanced initial state. It does not
replace the family theorem proof with the experiment, establish fresh-batch
fixed-`T` behavior, measure a real system, or defeat the exact finite-instance
polyhedral outcome-map benchmark. It therefore strengthens the existing
Top-K feedback result but does not, by itself, clear the top-conference
novelty gate.

## Reproduction record

The final protocol's hypotheses, seeds, parameters, and decision rule were
fixed before the first calculation. After an early run, the summary cell
count and output completeness were corrected: the final archive includes all
five arms and the exact affinity rows. These were artifact-generation fixes;
no plants, parameters, endpoints, or pass criteria were changed. Two final
full executions produced identical artifact hashes. The final run used exact
rational arithmetic and completed all 11 control groups. The hashes are:

| Artifact | SHA-256 |
|---|---|
| Protocol | `33e9411b4e1c2c4f6d840945d6276321874d20956e48e31fea9f4d52ce06cbff` |
| Runner | `d560f480bf3b21e48ef50d3915e4e8d5131b810d691362976d1de0586ebeea61` |
| Summary | `20b9e18df139110251349a2588d2c5256da96012419e26a80b05efa32b97830c` |
| Affinities | `d5888f541a7d006088d4d175342941cbaa895d9995617d98d480bfd5be7e36e4` |
| Plants | `a1f2ee1da832405f8c83b23909e07f9579dadcb41d5bb93040d04f9e3289b4cf` |
| Trajectories | `b61b3be02086cead4120d68fb111f4dfed689c023e036c5988d5cb4c901dcb85` |

An independent artifact audit then read the saved affinity CSV, recomputed
each plant's per-file SHA-256 and initial exact Top-K counts, and verified all
110 plants and 5,100 token rows against `plants.csv` and the summary.

# Results: target × signal under multiple saturated experts

**Question:** does the existing multi-low population theorem's target-by-signal interaction persist in paired finite-batch Top-K routing as the number of low-capacity experts changes?

**Protocol:** [capacity_matched_multiplicity_experiment_protocol_2026-10-18.md](capacity_matched_multiplicity_experiment_protocol_2026-10-18.md)  
**Theorem:** [capacity_matched_target_theorem_2026-10-18.md](capacity_matched_target_theorem_2026-10-18.md)  
**Runner:** [../../scripts/run_capacity_matched_multiplicity_experiment.py](../../scripts/run_capacity_matched_multiplicity_experiment.py)  
**Artifacts:** [../../results/capacity_matched_multiplicity_2026-10-18/](../../results/capacity_matched_multiplicity_2026-10-18/)

## Execution and controls

The locked run used `E=4`, `K=2`, `m={1,2,3}`, `T={2304,9216}`, 12 paired plants per `(m,T)`, horizons through 64, and static and fresh-batch regimes. It produced 5,040 plant-horizon-arm rows, 420 arm cells, and 336 paired contrast cells. All 72 full-trajectory no-clipping controls passed. Every step passed mass conservation, clipping, and overflow-accounting checks; all arms had the same initial cost; no Top-K cutoff ties occurred.

The exact-total capacity vectors at `T=2304` were:

| `m` | Capacity vector | Total |
|---:|---|---:|
| 1 | `(1008,1200,1200,1200)` | `4608` |
| 2 | `(1008,1008,1296,1296)` | `4608` |
| 3 | `(1008,1008,1008,1584)` | `4608` |

The `T=9216` vectors are four times these. The low-capacity fraction is `7/16`; the high-capacity fraction is `1/2 + m/(16(4-m))`.

The population theorem gives exact limiting overflow formulas for this
registered family. Under the uniform target, requested overflow is `m/16`
per round and admitted overflow tends to `E*r=1/4`, so the long-run gap is
`(4-m)/16`. Under the capacity target, both signals converge to zero
population overflow; at a shared state on the trajectory the requested
relative-pressure step is exactly `4/m` times the admitted step. Numerical
Plackett–Luce root solves give:

| `m` | Capacity-target root `x_C` | Uniform-target admitted root `x_U` | Requested/admitted step ratio under capacity target |
|---:|---:|---:|---:|
| 1 | `-0.218109` | `0.647216` | `4` |
| 2 | `-0.322111` | `0.322111` | `2` |
| 3 | `-0.647216` | `0.218109` | `4/3` |

The roots are numerical values from the dynamic-programming response, not
closed-form constants. The exact theorem is the recurrence and convergence
statement in the linked theorem document.

## Primary paired outcomes

At `H=64` in the fresh-batch regime, the paired mean differences in cumulative overflow per `T` were:

| `m` | `T` | Admitted − requested, uniform target | Admitted − requested, capacity target | Capacity-target admitted − no feedback |
|---:|---:|---:|---:|---:|
| 1 | 2304 | `5.888` `[5.857, 5.919]` | `0.801` `[0.768, 0.834]` | `-1.797` `[-1.831, -1.762]` |
| 1 | 9216 | `5.902` `[5.890, 5.914]` | `1.105` `[1.087, 1.123]` | `-1.919` `[-1.938, -1.900]` |
| 2 | 2304 | `5.528` `[5.511, 5.545]` | `0.804` `[0.782, 0.827]` | `-5.257` `[-5.291, -5.223]` |
| 2 | 9216 | `5.533` `[5.527, 5.540]` | `0.975` `[0.960, 0.989]` | `-5.484` `[-5.508, -5.459]` |
| 3 | 2304 | `3.134` `[3.124, 3.144]` | `0.476` `[0.464, 0.489]` | `-9.056` `[-9.124, -8.988]` |
| 3 | 9216 | `3.134` `[3.130, 3.138]` | `0.540` `[0.533, 0.547]` | `-9.271` `[-9.310, -9.231]` |

Entries are paired means with 95% paired-t intervals over 12 plants. For each of the six `(m,T)` cells at this displayed horizon, admitted feedback had higher overflow than requested feedback under both targets in all 12/12 paired seeds. Under the capacity-matched target, admitted feedback beat the no-feedback arm in 12/12 plants. The target-by-signal interaction was negative in every registered fresh-batch cell; at `T=9216,H=64`, its means for `m=1,2,3` were `-4.797`, `-4.558`, and `-2.594`, respectively.

Across **all 72** registered combinations of `(m,T,regime,H≥2)`, the paired admitted-minus-requested contrast was positive in 12/12 plants under each target. This includes both static and fresh regimes and all six nontrivial horizons. The capacity-target admitted arm also beat no feedback in every paired plant for `H≥2`; at `H=1` those arms share the same initial cost, as required by the design.

The paired ordering agrees with the population theorem for the specified direct-update class: capacity matching removes the large uniform-target admitted-feedback penalty, but requested feedback still has lower cumulative overflow. The finite-batch run does **not** show that admitted feedback has lost all control authority; the capacity-target admitted arm substantially beats no feedback.

## Population-prediction check and limitation

For `H=64`, fresh-batch capacity-target arms, the sample means remained above the deterministic population cumulative predictions at both batch sizes. For requested/admitted feedback respectively, the `(mean − population prediction)` differences at `T=9216` were:

| `m` | Requested | Admitted |
|---:|---:|---:|
| 1 | `0.315` | `0.021` |
| 2 | `0.258` | `0.050` |
| 3 | `0.239` | `0.152` |

The requested-arm differences at `T=2304` were larger (`0.763`, `0.620`, `0.578`), consistent with finite-batch effects shrinking with `T`; this two-size trend is not a convergence-rate proof. The 12-seed intervals are intervals for stochastic simulation means, not a confidence statement about the deterministic population theorem. The experiment supports the paired finite-batch ordering on these registered instances, but its 64-step population-magnitude agreement is incomplete, especially for requested capacity-target feedback. That discrepancy must stay visible.

The population predictions are computed from the exact Plackett–Luce dynamic-programming inclusion response and the theorem's scalar recurrences. They are not estimated from the simulated runs. Finite-batch trajectories need not follow the deterministic mean recurrence because pressure is itself stochastic and overflow is nonlinear.

## What this establishes—and what it does not

This validates the same-model target × signal interaction across three saturation multiplicities and two batch sizes. It reinforces the correction that the original large uniform-target gap is partly a target mismatch, while the specified requested-count direct update remains better in this capacity-matched family.

It does not prove a universal windup theorem, an optimal-policy ranking, a measured observation/collective price, real-router prevalence, a trained-model benefit, or a Top-K-specific separation from censored adaptive testing. The last item remains the decisive novelty question for the central paper claim.

## Reproducibility

The runner records protocol, script, and output hashes in `summary.json`:

- protocol SHA-256: `7f4dd1db8b23edbcfdf60e5982f9fbdea83d626582cb810e86329797e7dfa4be`
- runner SHA-256: `596931f5b6282f5985a7e9ea1c059ec5af7ad2b3642ddef84b0246aabb077728`
- raw plants SHA-256: `f93d05e6192dc6fe921c945e28b963fc695923a1c7a8942cda05010fccb5db41`
- cells SHA-256: `a65e1aba515f5a90832f8e0b8d18f927c97672458baf112d47ab788548f52fd7`
- paired contrasts SHA-256: `b620ee62fa5bb6d2c7cb71471f20bc68dff8ebb9f6897d336196ccbe55724548`

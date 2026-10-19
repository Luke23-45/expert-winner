# Central-claim synthetic audit

- Suite: 20261018T132657Z
- Device: cpu
- Runs: 500; trajectory rows: 280100
- Diagnostic protocol overrides: False
- Invariants: PASS

## Checks

- [x] expected_run_count
- [x] unique_run_ids
- [x] protocol_hash_matches_manifest
- [x] source_snapshot_hashes
- [x] run_index_matches_trajectories
- [x] runner_initial_condition_checks
- [x] trajectory_invariants
- [x] saturated_signal_prediction
- [x] boundary_controls
- [x] no_drop_equivalence
- [x] paired_affinity_identity

## Condition summaries

Mean overflow, saturation fraction, and first request-count change are shown separately from load imbalance.

### shortage_c075

| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |
|---|---:|---:|---:|---:|---:|
| requested | 0.0364742 | 512 | 1.0000 | 36/50 | 863.1 |
| admitted | 0.0422656 | 512 | 1.0000 | 0/50 | none |

### shortage_c050

| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |
|---|---:|---:|---:|---:|---:|
| requested | 0.0499595 | 1024 | 1.0000 | 50/50 | 363.9 |
| admitted | 0.129941 | 1024 | 1.0000 | 0/50 | none |

### exact_total_boundary

| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |
|---|---:|---:|---:|---:|---:|
| requested | 0 | 0 | 1.0000 | 0/50 | none |
| admitted | 0 | 0 | 1.0000 | 0/50 | none |

### partial_slack_c1125

| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |
|---|---:|---:|---:|---:|---:|
| requested | 0.196169 | 306.725 | 0.0000 | 50/50 | 127.9 |
| admitted | 0.328476 | 574.29 | 0.0000 | 41/50 | 230.7 |

### no_drop_control

| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |
|---|---:|---:|---:|---:|---:|
| requested | 0.0422656 | 0 | 0.0000 | 0/50 | none |
| admitted | 0.0422656 | 0 | 0.0000 | 0/50 | none |

## Paired shortage results

- shortage_c075: mean admitted-minus-requested TV 0.00579146, 95% seed-bootstrap interval [0.00366969, 0.0081943], requested lower TV in 36/50 seeds.
- shortage_c050: mean admitted-minus-requested TV 0.0799819, 95% seed-bootstrap interval [0.067033, 0.0939562], requested lower TV in 50/50 seeds.

## Interpretation limit

Synthetic mechanism evidence only. These runs do not establish real-data quality, deployed telemetry availability, or universal convergence.
A failed invariant invalidates interpretation until its cause is understood.
A passing suite validates programmed mechanisms under this generator; it does not prove the broader theory or a real-model performance advantage.

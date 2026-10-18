# Capacity-slack factorial: controlled synthetic results

**Protocol:** [registered design](topk_capacity_slack_factorial_protocol_2026-10-18.md)  
**Runner:** [`../../scripts/run_topk_capacity_slack_factorial.py`](../../scripts/run_topk_capacity_slack_factorial.py)  
**Merger:** [`../../scripts/merge_topk_capacity_slack_factorial.py`](../../scripts/merge_topk_capacity_slack_factorial.py)  
**Raw paired trajectories:** [`../../results/topk_capacity_slack_factorial_2026-10-18/paired_plants.csv`](../../results/topk_capacity_slack_factorial_2026-10-18/paired_plants.csv)  
**Cell table:** [`../../results/topk_capacity_slack_factorial_2026-10-18/cells.csv`](../../results/topk_capacity_slack_factorial_2026-10-18/cells.csv)  
**Machine summary:** [`../../results/topk_capacity_slack_factorial_2026-10-18/summary.json`](../../results/topk_capacity_slack_factorial_2026-10-18/summary.json)

## Registered run and checks

The complete grid contains `E={4,8}`, every `K=1,...,E-1`, three
continuous affinity laws, two exact-total capacity shortfalls per `(E,K)`,
two batch sizes, two batch regimes, eight paired replicates, and six
horizons. Both expert-count blocks completed. All 120 law/`E`/`K`/shortfall/
batch-size/regime profiles were retained.

| Check | Result |
|---|---:|
| Paired plant-horizon rows | 11,520 |
| Summary cells | 1,440 |
| Full no-clipping trajectory round controls | 61,440 |
| Exact routing ties | 0 |
| Mass, clipping, overflow, initial-cost, gain, and quadrature checks | All passed |

The runner's vectorized Top-K selector was independently compared with stable
descending sort on integer-valued fixtures: it selected identical experts
and reported identical boundary-tie counts for every `K` at `E=2,...,8`.
SciPy emitted overflow warnings while evaluating extreme Gumbel tail values;
the registered quadrature error checks passed for every evaluated response.
No cell was removed.

## Main result

For the theorem's **static-batch** regime, all cell means are positive from
`H=2` onward, and the aggregated finite-batch means closely follow the
population recurrence:

| Horizon | Mean observed cumulative gap / token | Population prediction | Ratio | Paired 95% intervals covering prediction |
|---:|---:|---:|---:|---:|
| 2 | 0.010649 | 0.010808 | 0.985 | 109/120 |
| 4 | 0.059821 | 0.060945 | 0.982 | 106/120 |
| 8 | 0.246291 | 0.249343 | 0.988 | 113/120 |
| 16 | 0.840303 | 0.844558 | 0.995 | 116/120 |
| 32 | 2.451337 | 2.460473 | 0.996 | 115/120 |

Across the 600 static cells with `H>=2`, 559 paired 95% t intervals contain
the population prediction. At `H>=4`, every registered static cell mean is
positive; at `H>=8`, every static replicate has positive cumulative gap.
These intervals are per-cell summaries from eight paired replicates, not
simultaneous confidence bands.

The theorem's long-run slope is `(E-1)r`; the experiment does **not** show
that slope has been reached by `H=32`. Across registered profiles, the ratio
of the observed horizon-average gap to `(E-1)r` at `H=32` ranges from 0.065
to 0.845 (median 0.416). The correct quantitative comparison at this horizon
is to the finite-horizon population recurrence in the table, not to the
asymptotic slope.

## Fresh-batch check

The fresh-batch regime preserves the direction at later horizons but is more
variable and has lower finite-batch magnitude than the static population
prediction. Mean cumulative gap / token versus the same finite-horizon
population prediction is 0.009388/0.010808 at `H=2`, 0.053769/0.060945 at
`H=4`, 0.226738/0.249343 at `H=8`, 0.787476/0.844558 at `H=16`, and
2.318773/2.460473 at `H=32`. All 120 fresh cell means are positive by
`H>=4`, and every fresh replicate is positive by `H>=8`. However, only
151/600 per-cell 95% t intervals over `H>=2` contain the static population
prediction. Fresh-batch finite-`T` trajectories therefore support the sign
of the mechanism in this grid, but are not a precise magnitude validation
of the static-batch theorem.

At `H=2`, 119 fresh cell means are positive and one is negative. The
negative cell is `E=8,K=7`, Gumbel affinities, the smaller registered
shortage, and `T=12,544`: its eight-replicate mean is `-0.0009168` overflow
assignments per token, with a paired 95% interval
`[-0.001448,-0.000386]`, while the population recurrence predicts
`+0.0020743`. This is a real finite-batch sign reversal in the fresh-batch
regime, which is outside the theorem's primary static-batch setup. By `H=4`
the mean is positive in every fresh cell. The reversal is preserved in the
raw data and should be discussed as a finite-size limitation, not hidden as
noise or described as confirmation of the fresh-batch magnitude.

## Interpretation

The wider controlled sweep supports the existing theorem's finite-horizon
population prediction across both tested expert counts, all tested Top-K
values, three affinity laws, and two capacity-shortage magnitudes. It
strengthens the evidence that the registered admitted proportional update
can increase overflow in this one-short-expert regime. It does not establish
that admitted feedback is universally worse, nor does it test the
two-saturated identification/value theorem's signal-information claim.

The professor's broad “windup” wording remains too strong for these data.
This model's global-saturation result is demand-blind pressure drift for the
heterogeneous exact-total profile, while uniform-capacity saturation can
freeze the signed controller. In the one-short population trajectory, the
hidden request count is reconstructible from conservation; the result is
controller mismatch, not loss of information.

This experiment does not settle top-conference novelty. The exact
finite-instance active-testing reduction still applies; the simulation
validates a declared MoE family and controller, not a separation from a
generic censored-observation decision model. No hardware price, actual
Megatron run, or model-quality outcome was measured. The separate
multi-saturation requested-signal value theorem remains the strongest
candidate for the professor's decision-value question, and its closest
methodological prior art remains active hypothesis testing and censored
data decision theory.

## Reproduction record

Run the two exact expert-count blocks and merge:

```powershell
python scripts/run_topk_capacity_slack_factorial.py --e 4
python scripts/run_topk_capacity_slack_factorial.py --e 8
python scripts/merge_topk_capacity_slack_factorial.py
```

The split is only for execution and output recovery; it does not alter the
registered design or random seeds. The merged result has SHA-256
`4945cf0a4e16ece016f55d4e8fb6f36866cb6f1d0e8281e55140aab32ae0fc56` for
paired rows and
`f4bc2dae27ac49d2d0586f5776f6bb0bf3613df420ea3026eb9938a4851f4bf5` for
the cell table. The complete block hashes and run metadata are in
`summary.json`.

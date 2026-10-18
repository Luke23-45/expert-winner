# Results: arbitrary-Top-K two-step overflow experiment

**Protocol:** [`topk_e_expert_overflow_protocol_2026-10-17.md`](topk_e_expert_overflow_protocol_2026-10-17.md)  
**Theorem:** [`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_e_expert_overflow.py`](../../scripts/run_topk_e_expert_overflow.py)

## Execution and checks

The preregistered design covered all `K=1,...,E-1` for `E in {3,4,8}`,
three fixed population displacements `d`, three batch sizes, and 50 paired
plants per `(E,K,T)`. This produced 5,400 plant/gain rows and 108 endpoint
cells. Every plant used the same affinity matrix across the two routing
steps, all gains, and all controller arms. Scores used exact integer
cross-multiplication and the declared stable lower-index tie rule.

All routing, clipping, overflow, mass, load, and paired-initial-cost
invariants passed. All 5,400 no-clipping controls had zero overflow and
identical requested/admitted routes and updates. There were no exact Top-K
boundary ties. Both full runs produced byte-identical outputs:

| Artifact | SHA-256 |
|---|---|
| Protocol | `b757818ac3688e69f95a9e1dfa912f2ec34df9cd29e70cfa5e84a25354424fb0` |
| Runner | `f448e83c03738ff22a478cc328cb45e6ecd8ba34509dfd009fd5c3e69d5eb927` |
| Paired plant rows | `a14ce00b8a9260315b09e2c3d7e3edcb09c578e6413864c243a08fda1fd69793` |
| Summary | `e084bb35ca3a538694d658e594ff1248a7481eb90a3fccd4ca15b34997b49195` |

The complete 108-cell summary and all plant-level rows are in
[`../../results/topk_e_expert_overflow/summary.json`](../../results/topk_e_expert_overflow/summary.json)
and [`../../results/topk_e_expert_overflow/plants.csv`](../../results/topk_e_expert_overflow/plants.csv).

## Largest batch size: all registered cells

Each row gives the paired mean of `(J_A-J_R)/T`, the 95% paired-mean `t`
interval, the theorem limit, absolute mean error, and fraction of individual
paired gaps that were positive. At `T=13440`, every one of the 36 cells had
50/50 positive paired gaps.

| E | K | d | Mean gap | 95% interval | Theory | Abs. error | Positive pairs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1 | 1/4 | 0.244323 | [0.242623, 0.246023] | 0.244792 | 0.000469 | 1.00 |
| 3 | 1 | 1/2 | 0.457881 | [0.454713, 0.461049] | 0.458333 | 0.000452 | 1.00 |
| 3 | 1 | 3/4 | 0.607939 | [0.602584, 0.613294] | 0.609375 | 0.001436 | 1.00 |
| 3 | 2 | 1/4 | 0.193150 | [0.191627, 0.194673] | 0.192708 | 0.000442 | 1.00 |
| 3 | 2 | 1/2 | 0.293560 | [0.290277, 0.296842] | 0.291667 | 0.001893 | 1.00 |
| 3 | 2 | 3/4 | 0.331810 | [0.326333, 0.337286] | 0.328125 | 0.003685 | 1.00 |
| 4 | 1 | 1/4 | 0.248216 | [0.246231, 0.250201] | 0.249023 | 0.000808 | 1.00 |
| 4 | 1 | 1/2 | 0.483760 | [0.480028, 0.487493] | 0.484375 | 0.000615 | 1.00 |
| 4 | 1 | 3/4 | 0.669018 | [0.662824, 0.675212] | 0.670898 | 0.001881 | 1.00 |
| 4 | 2 | 1/4 | 0.237582 | [0.236456, 0.238708] | 0.236328 | 0.001254 | 1.00 |
| 4 | 2 | 1/2 | 0.406795 | [0.404673, 0.408917] | 0.406250 | 0.000545 | 1.00 |
| 4 | 2 | 3/4 | 0.486906 | [0.483540, 0.490273] | 0.486328 | 0.000578 | 1.00 |
| 4 | 3 | 1/4 | 0.170661 | [0.168800, 0.172521] | 0.170898 | 0.000238 | 1.00 |
| 4 | 3 | 1/2 | 0.233449 | [0.229306, 0.237593] | 0.234375 | 0.000926 | 1.00 |
| 4 | 3 | 3/4 | 0.246292 | [0.239759, 0.252824] | 0.249023 | 0.002732 | 1.00 |
| 8 | 1 | 1/4 | 0.239802 | [0.236634, 0.242970] | 0.249998 | 0.010196 | 1.00 |
| 8 | 1 | 1/2 | 0.455881 | [0.449012, 0.462750] | 0.499512 | 0.043631 | 1.00 |
| 8 | 1 | 3/4 | 0.658900 | [0.649014, 0.668787] | 0.737486 | 0.078586 | 1.00 |
| 8 | 2 | 1/4 | 0.249948 | [0.247663, 0.252233] | 0.249950 | 0.000002 | 1.00 |
| 8 | 2 | 1/2 | 0.489571 | [0.485320, 0.493823] | 0.495117 | 0.005546 | 1.00 |
| 8 | 2 | 3/4 | 0.672238 | [0.666211, 0.678265] | 0.691601 | 0.019363 | 1.00 |
| 8 | 3 | 1/4 | 0.249473 | [0.248090, 0.250856] | 0.249422 | 0.000051 | 1.00 |
| 8 | 3 | 1/2 | 0.477394 | [0.474914, 0.479875] | 0.477051 | 0.000344 | 1.00 |
| 8 | 3 | 3/4 | 0.606924 | [0.603129, 0.610719] | 0.606783 | 0.000141 | 1.00 |
| 8 | 4 | 1/4 | 0.245879 | [0.244784, 0.246975] | 0.246010 | 0.000130 | 1.00 |
| 8 | 4 | 1/2 | 0.430600 | [0.428803, 0.432396] | 0.431641 | 0.001041 | 1.00 |
| 8 | 4 | 3/4 | 0.494028 | [0.491034, 0.497022] | 0.496010 | 0.001982 | 1.00 |
| 8 | 5 | 1/4 | 0.231354 | [0.230301, 0.232408] | 0.231783 | 0.000429 | 1.00 |
| 8 | 5 | 1/2 | 0.351192 | [0.349064, 0.353320] | 0.352051 | 0.000859 | 1.00 |
| 8 | 5 | 3/4 | 0.370984 | [0.367145, 0.374822] | 0.374422 | 0.003438 | 1.00 |
| 8 | 6 | 1/4 | 0.191274 | [0.189928, 0.192620] | 0.191601 | 0.000327 | 1.00 |
| 8 | 6 | 1/2 | 0.239792 | [0.235980, 0.243603] | 0.245117 | 0.005326 | 1.00 |
| 8 | 6 | 3/4 | 0.231557 | [0.225675, 0.237438] | 0.249950 | 0.018394 | 1.00 |
| 8 | 7 | 1/4 | 0.104129 | [0.101319, 0.106940] | 0.112486 | 0.008356 | 1.00 |
| 8 | 7 | 1/2 | 0.094510 | [0.089011, 0.100010] | 0.124512 | 0.030001 | 1.00 |
| 8 | 7 | 3/4 | 0.082140 | [0.075626, 0.088653] | 0.124998 | 0.042858 | 1.00 |

## Finite-size limits

All 108 cell means were positive. Across all 5,400 individual pairs,
5,399 were positive, none were exactly zero, and one was negative
(`E=8,K=7,T=3360,d=3/4`, gap `-1/1120`). At the largest batch size, all
individual pairs were positive; 25 of 36 nominal 95% intervals contained
the asymptotic value. Across all three batch sizes, 69 of 108 intervals
contained it.

At `T=13440`, mean absolute errors averaged `0.00140` for `E=3`,
`0.00106` for `E=4`, and `0.01290` for `E=8`; the largest error was
`0.07859` at `E=8,K=1,d=3/4`. The poor fit is concentrated at edge values
of `K` with larger `eta=d*K/r`: finite-sample requested-count noise is
multiplied by `eta`, while clipping of non-short experts can alter the
admitted update. The theorem takes `T->infinity` with fixed parameters; this
run does not establish that its finite-size approximation is accurate at
`E=8` for the registered batch sizes.

## Conclusion and claim boundary

The analytic theorem establishes a strictly positive asymptotic expected
gap for every fixed `E>=2` and `1<=K<E` under its explicit assumptions. The
controlled finite-grid experiment supports the positive mean across all
registered `(E,K,d,T)` cells and demonstrates reproducibility. It also shows
clear finite-size departures that must remain visible in any presentation.
The synthetic run does not prove the theorem, cover all affinity laws,
compare against every causal controller, price telemetry, demonstrate
trained-model quality, or evade exact finite-instance outcome-map
simulation. This strengthens the existing Top-K formal line; the
class-level novelty gate remains open.

## Independent rerun verification

On 2026-10-17, the checked-in runner was executed again from the research branch. It reproduced the recorded SHA-256 values for the runner, protocol, plant CSV, and summary JSON exactly. The run reported 5,400 paired plant/gain rows, 108 endpoint cells, 5,400 successful no-clipping controls, and all invariants passed. This verifies computational reproducibility of the registered finite-grid audit; it is not additional independent statistical evidence because it uses the same fixed seeds and design.


# Fixed-slice two-step overflow experiment: results

**Protocol:** [`heterogeneous_capacity_two_step_protocol_2026-10-17.md`](heterogeneous_capacity_two_step_protocol_2026-10-17.md), fixed before execution.
**Runner:** [`run_heterogeneous_two_step.py`](../../scripts/run_heterogeneous_two_step.py).
**Artifacts:** [`summary.json`](../../results/heterogeneous_two_step/summary.json) and [`plants.csv`](../../results/heterogeneous_two_step/plants.csv).
**Protocol SHA-256:** `90559566d7b887adca376a833ca6ff51956bfaa809a5a001a96d244929b5079c`.
**Runner SHA-256:** `ae969ff5f9200a9f2ff87c6c77a11d272fe79820c9c89419f7e6e11108abc33b`.
**Summary SHA-256, both executions:** `de69dd0bf91d3d366fddc917a8a7714f89d2899811f4fa4e423cdae399b2fb33`.
**Plant CSV SHA-256, both executions:** `c007bf475f61e626a3727dca596ad101fcb5b9081554d1f1abfc63f9626b3ffe`.

## Design and checks

There are 15,000 paired plant/gain rows: six batch sizes, 500 independent
affinity matrices per size, and five gains. Every matrix is paired across
requested, admitted, and no-feedback arms, reused at both steps, and generated
on the integer grid `0,...,2^30`. The routing-score decisions use exact
integer cross-multiplication. Lower expert index is the declared tie rule.

All registered checks passed: Top-1 mass conservation, `A=min(R,C)`, exact
overflow accounting, equal first-step overflow across paired arms, and 15,000
no-clipping diagnostics with zero overflow and identical requested/admitted
paths. There were no exact score ties in the recorded routing calls. A second
execution reproduced both output files byte-for-byte.

## Primary endpoint

The primary endpoint is the paired two-step normalized overflow gap
`(J0_A + J1_A - J0_R - J1_R)/T`. The theorem's limit at each gain is shown
alongside the observed mean.

| T | eta=1/2 | eta=1 | eta=2 | eta=4 | eta=5 |
|---:|---:|---:|---:|---:|---:|
| 60 | 0.08080 | 0.14463 | 0.23747 | 0.33887 | 0.35833 |
| 120 | 0.07705 | 0.14583 | 0.26748 | 0.41803 | 0.44448 |
| 240 | 0.07422 | 0.14595 | 0.27601 | 0.46762 | 0.51067 |
| 480 | 0.07789 | 0.15438 | 0.29330 | 0.50332 | 0.55582 |
| 960 | 0.07960 | 0.15813 | 0.30167 | 0.52741 | 0.58991 |
| 1,920 | 0.08203 | 0.16233 | 0.31075 | 0.54591 | 0.61486 |
| **Asymptotic limit** | **0.08314** | **0.16512** | **0.32099** | **0.56790** | **0.64043** |

At `T=1,920`, the paired 95% t intervals and the asymptotic limits are:

| eta | Mean gap | 95% t interval | Limit | Positive paired gaps |
|---:|---:|---:|---:|---:|
| 1/2 | 0.08203 | [0.08126, 0.08280] | 0.08314 | 500/500 |
| 1 | 0.16233 | [0.16130, 0.16336] | 0.16512 | 500/500 |
| 2 | 0.31075 | [0.30896, 0.31255] | 0.32099 | 500/500 |
| 4 | 0.54591 | [0.54222, 0.54960] | 0.56790 | 500/500 |
| 5 | 0.61486 | [0.60996, 0.61977] | 0.64043 | 500/500 |

The finite-`T` means remain below the asymptotic limits at the largest tested
batch size. Their distances to the limit are `0.00111, 0.00279, 0.01023,
0.02199, 0.02557` in the displayed gain order. The intervals estimate the
finite-grid finite-`T` means; they are not intervals for the limit. This
experiment supports a positive sign and approach toward the formula, but
does not establish the limit or give a quantitative finite-`T` error bound.

## Interpretation boundary

The result is empirical support for the exact two-step theorem, not its
proof. It tests the specific capacity split `C/T=(1/6,1/2,1/3)` and a
rational approximation to continuous uniform affinities. It does not show
universal superiority, a trained-model or deployment effect, a physical
telemetry price, or a separation from the outcome-map benchmark. The
parameterized follow-up across capacity splits is reported separately in
[`heterogeneous_capacity_family_results_2026-10-17.md`](heterogeneous_capacity_family_results_2026-10-17.md).

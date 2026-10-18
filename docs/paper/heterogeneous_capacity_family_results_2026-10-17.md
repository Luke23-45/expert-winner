# Parameterized two-step overflow experiment: results

**Protocol:** [`heterogeneous_capacity_family_protocol_2026-10-17.md`](heterogeneous_capacity_family_protocol_2026-10-17.md), fixed before execution.
**Runner:** [`run_heterogeneous_family_sweep.py`](../../scripts/run_heterogeneous_family_sweep.py).
**Artifacts:** [`summary.json`](../../results/heterogeneous_family_sweep/summary.json) and [`plants.csv`](../../results/heterogeneous_family_sweep/plants.csv).
**Protocol SHA-256:** `79aee6b28f216a01dd8f82c8c03461a57016a44095974d37a0b1767f4739c861`.
**Runner SHA-256:** `da8093c786064604f1f1e4e776317746a79abd8b09c92fd6c6a6046fd8804fb1`.
**Summary SHA-256, both executions:** `81273ddadbe67a4756e6f79e7ec5465d2521fe38cde0d714ed34be9a05bdf290`.
**Plant CSV SHA-256, both executions:** `52e586978b7945cbcf69feb11c605d7b49e04724a27ce86f0b4b467ff265705a`.

## Execution and integrity

The run contains 36,000 paired plant/parameter rows: five batch sizes,
200 matrices per batch size, three shortage fractions, three capacity
splits, and four gains. The exact-grid runner passed all mass-conservation,
clipping, overflow-accounting, and shared-initial-overflow assertions. The
4,000 registered no-clipping checks had zero overflow and identical R/A
paths. No exact affinity-score ties occurred in any recorded routing call.
The deterministic rerun reproduced the summary and plant CSV byte-for-byte.

## Primary endpoint

The endpoint is the paired two-step normalized overflow difference
`(J0_A + J1_A - J0_R - J1_R)/T`. The theorem predicts the limit
`g(eta,r) = d - d^3/3`, where `d=eta*r`, independent of the capacity split
parameter `s`. The table gives the mean endpoint across all three registered
splits for each `(T,r,eta)`; every individual split remains available with
its 95% t interval in `summary.json`.

| T | r | eta=1/2 | eta=1 | eta=2 | eta=3 |
|---:|---:|---:|---:|---:|---:|
| 120 | 1/12 | 0.03954 | 0.07000 | 0.09550 | 0.10667 |
| 120 | 1/6 | 0.07963 | 0.15275 | 0.27360 | 0.35946 |
| 120 | 1/4 | 0.11761 | 0.23507 | 0.42032 | 0.53374 |
| 240 | 1/12 | 0.03876 | 0.07147 | 0.12003 | 0.15829 |
| 240 | 1/6 | 0.07860 | 0.15140 | 0.28357 | 0.39533 |
| 240 | 1/4 | 0.11788 | 0.23216 | 0.42535 | 0.55323 |
| 480 | 1/12 | 0.03926 | 0.07460 | 0.13849 | 0.19124 |
| 480 | 1/6 | 0.07892 | 0.15632 | 0.29825 | 0.41917 |
| 480 | 1/4 | 0.11963 | 0.23638 | 0.43695 | 0.57666 |
| 960 | 1/12 | 0.04134 | 0.08047 | 0.15295 | 0.21774 |
| 960 | 1/6 | 0.08230 | 0.16230 | 0.30962 | 0.43910 |
| 960 | 1/4 | 0.12297 | 0.24140 | 0.44744 | 0.59352 |
| 1,920 | 1/12 | 0.04047 | 0.08073 | 0.15795 | 0.23113 |
| 1,920 | 1/6 | 0.08202 | 0.16303 | 0.31416 | 0.44671 |
| 1,920 | 1/4 | 0.12323 | 0.24281 | 0.45188 | 0.59861 |
| **Limit** | **1/12** | **0.0416** | **0.0831** | **0.1651** | **0.2448** |
| **Limit** | **1/6** | **0.0831** | **0.1651** | **0.3210** | **0.4583** |
| **Limit** | **1/4** | **0.1243** | **0.2448** | **0.4583** | **0.6094** |

At `T=1,920`, every registered `(r,s,eta)` split cell had positive mean and
all 200 paired plants had positive gaps. Across all 180 cells, the fraction
of plants with a positive gap ranged from 81% to 100%; the minimum occurred
at `T=120`, `r=1/12`, `eta=3`. The small-batch/high-gain deviations are
substantial and are retained in the table. At the largest batch, the maximum
absolute difference between a split-specific mean and its asymptotic limit
was 0.0197. The largest across-split range at fixed `(T,r,eta)` was 0.0194.

The empirical means move toward the formula as `T` increases, with a few
finite-sample nonmonotonicities (notably at the smallest tested gain from
`T=960` to `T=1,920`). Several largest-`T` sampling intervals do not contain
the asymptotic limit. That is not a contradiction: these intervals quantify
the finite-`T` mean across sampled matrices, while the theorem states a
limit, and affinity discretization is an additional finite-grid
approximation. The experiment supports the predicted sign and parameter
dependence; it does not prove asymptotic convergence.

## What this establishes—and does not

The generalized theorem is an analytic result within the canonical formal
model. This sweep stress-tests its `d=eta*r` law over multiple capacities and
tests the predicted invariance to the capacity split. It does not compare
against arbitrary causal controllers, establish universal controller
superiority, measure a physical cost for requested telemetry, prove trained
model quality, or defeat the finite-instance outcome-map reduction. Those
remain separate claims and gates.

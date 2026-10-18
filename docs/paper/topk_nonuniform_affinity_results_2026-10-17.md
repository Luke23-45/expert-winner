# Results: non-Uniform affinity extension check

**Protocol:** [`topk_nonuniform_affinity_protocol_2026-10-17.md`](topk_nonuniform_affinity_protocol_2026-10-17.md)  
**Theorem:** [`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md), arbitrary-iid-affinity extension  
**Runner:** [`../../scripts/run_topk_nonuniform_affinity.py`](../../scripts/run_topk_nonuniform_affinity.py)

## Execution and reproducibility

The locked grid produced 1,440 plant/displacement rows and 48 endpoint cells across four affinity laws, `E=4`, `K={1,2,3}`, `T={2400,9600}`, and `d={1/4,1/2}`. Each cell contains 30 paired plants. All 1,440 no-clipping controls passed; no exact Top-K boundary ties occurred; every registered invariant passed. The population limit was evaluated by one-dimensional adaptive quadrature for Normal, Logistic, and Gumbel laws and compared to the existing closed-form expression for Uniform.

| Artifact | SHA-256 |
|---|---|
| Protocol | `c7fe037263d044c898782bb337e4c8b265360ddee363dd9e1c692530089cd551` |
| Runner | `afa9450d1dbab0ff22e25d75992d93dab95d053573e1ed7e60c34fd31688695c` |
| Plant/displacement rows | `dd694ca425453f819a9d121e1764bbc017028ad7a4f7315902112ad31b5641e7` |
| Summary | `9cf20515c22d7945b4deeaf01ffebc12a85b7c2f5de53c13d6865fcdb70f4776` |

Machine-readable cell results and plant rows are in
[`../../results/topk_nonuniform_affinity/summary.json`](../../results/topk_nonuniform_affinity/summary.json)
and [`../../results/topk_nonuniform_affinity/plants.csv`](../../results/topk_nonuniform_affinity/plants.csv).

An independent rerun reproduced the runner, protocol, plant-row, and
summary hashes above exactly. It again passed all 1,440 no-clipping controls
and every invariant. This checks deterministic reproducibility under the
registered seeds; it is not a second independent sample.

## Outcome

All 48 paired cell means were positive, and all 1,440 individual paired gaps were positive. The 95% paired-mean t intervals contained the asymptotic limit in 44 of 48 cells. By affinity law:

| Affinity law | Positive cell means | Intervals containing limit | Mean absolute finite-size error |
|---|---:|---:|---:|
| Uniform[0,1] | 12/12 | 12/12 | 0.001713 |
| Normal(0,1) | 12/12 | 10/12 | 0.000966 |
| Logistic(0,1) | 12/12 | 11/12 | 0.000438 |
| Standard Gumbel | 12/12 | 11/12 | 0.000955 |

The largest cell-mean absolute error was `0.006528`, at Uniform, `K=1`,
`T=2400`, `d=1/2`; the corresponding mean gap was `0.477847` versus limit
`0.484375`. The largest-`T` Uniform cells reproduce the previously reported
finite-grid experiment's positive direction. Gaussian, Logistic, and Gumbel
results check the distributional extension over this registered grid.

## Claim boundary

This experiment supports the extension's direction for the selected finite
settings; it does not prove the asymptotic theorem. It does not establish
universal requested-feedback superiority, performance against all causal
controllers, trained-model or serving gains, a measured telemetry price, or
separation from the exact finite-instance outcome-map benchmark. The 30
plants per cell are synthetic replications under declared laws, not evidence
about prevalence in real MoE routers.

Reproduce from the repository root with `python scripts/run_topk_nonuniform_affinity.py`.

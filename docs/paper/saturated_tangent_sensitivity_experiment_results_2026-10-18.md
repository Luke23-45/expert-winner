# Results: saturated Top-K probability-transfer sensitivity

**Claim audited:** the directional corollary in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md).
**Protocol:** [`saturated_tangent_sensitivity_experiment_protocol_2026-10-18.md`](saturated_tangent_sensitivity_experiment_protocol_2026-10-18.md).
**Runner:** [`../../scripts/run_saturated_tangent_sensitivity.py`](../../scripts/run_saturated_tangent_sensitivity.py).
**Artifacts:** [`../../results/saturated_tangent_sensitivity_2026-10-18/`](../../results/saturated_tangent_sensitivity_2026-10-18/).

## Results

The run evaluated 27 exact-expectation cells: `E=4`, `K in {1,2,3}`, three
batch sizes from 160 through 640, and three registered capacity regimes.
For the exact-total two-saturated arm, the admitted/requested directional
response ratios were:

| K | T=160 | 320 | 640 |
|---:|---:|---:|---:|
| 1 | 0.05357 | 0.01117 | 0.000631 |
| 2 | 0.05257 | 0.01119 | 0.000727 |
| 3 | 0.01368 | 0.001181 | 0.00001199 |

Every two-saturated ratio was below the theorem's exact upper bound
`max(alpha_1,alpha_2)`. In the one-saturated control, the same `e_1-e_2`
transfer was not supported solely on saturated experts; its response ratio
stayed between `0.411` and `0.484`, rather than tending to zero. All 9
no-clipping controls returned ratio 1 to floating-point precision.

The analytic and direct finite-difference computations agreed: maximum full
Jacobian error was `8.35e-11`; maximum directional derivative error was
`5.68e-10`. Primary response ratios are calculated from the exact chain-rule
directional vectors; finite differences are an independent check, not the
source of the tiny attenuation values. The two-saturated capacity arms all
had exact total capacity `sum C=K*T`, and all request/capacity margin checks
passed.

## Interpretation and limits

This experiment supports the local finite-batch mean-sensitivity corollary
for iid-Gumbel Top-K with `E=4` and `K=1,2,3`. It uses exact Plackett-Luce
probabilities and exact binomial expectations; it is a deterministic
numerical audit, not Monte Carlo evidence. The measured ratio depends on the
chosen probability transfer and routing point, while the theorem provides
the corresponding bound in request-probability coordinates.

It does not prove that admitted counts fail to identify requests, that any
causal admitted policy has worse value, that a controller destabilizes, that
requested feedback improves overflow, or that the effect is novel relative
to generic clipped-signal analysis. It therefore does **not** settle the
class-level benchmark gate or the central conference theorem.

## Reproduction record

`summary.json` records:

- protocol SHA-256: `1e396a4e5826b9848fa22025fb9c08d202af46ef0a481d0793f3f9aecdf3542e`
- runner SHA-256: `af94646fc9fbdfa6b2fde6f68cd86bb82dc78029b51425bf7acca8824c7e94b6`
- cells SHA-256: `abed9c5d8895d30bae4a2322b977ee0041ca0ce6d50f38068a98d5bd793d850f`

Rerun from the repository root with:

```powershell
python scripts/run_saturated_tangent_sensitivity.py
```

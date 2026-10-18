# Results: admitted-field curl for Gumbel Top-K, (K=1,2,3)

**Protocol:** [locked exact-expectation audit](topk_general_k_admission_curl_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_general_k_admission_curl.py`](../../scripts/run_topk_general_k_admission_curl.py)  
**Artifacts:** `../../results/topk_general_k_admission_curl/`

## Outcome

All 27 preregistered cells passed: nine skewed-logit/exact-total-capacity
cells, nine uniform-logit controls, and nine no-clipping controls.

| Check | Observed | Threshold |
|---|---:|---:|
| Skewed, clipped cells with negative nonzero curl | 9/9 | 9/9 |
| Uniform-logit and no-clipping controls with zero curl | 18/18 | 18/18 |
| Maximum direct-vs-chain admitted-Jacobian error | `5.26e-10` | `<2e-7` |
| Maximum direct-vs-chain requested-Jacobian error | `9.11e-12` | `<2e-7` |
| Maximum request-Jacobian symmetry error | `8.33e-11` | `<2e-7` |

| (K) | (T) | (C=KT/E) | Admitted quotient curl |
|---:|---:|---:|---:|
| 1 | 32 | 8 | -0.041230155 |
| 1 | 128 | 32 | -0.045828240 |
| 1 | 512 | 128 | -0.052360319 |
| 2 | 32 | 16 | -0.018032670 |
| 2 | 128 | 64 | -0.018609131 |
| 2 | 512 | 256 | -0.018623791 |
| 3 | 32 | 24 | -0.018934997 |
| 3 | 128 | 96 | -0.019130780 |
| 3 | 512 | 384 | -0.019130794 |

The skewed input gives nonuniform inclusion probabilities for every (K).
As (T) grows, overloaded experts' clipping sensitivities decrease while
underloaded experts' sensitivities approach one; the nonzero curl persists
for all three tested (K) values. The result hash is
`3d4f14ee23c5fde23ad98a9f72c3572e6895668e345552c53099cb51bd7a8be5`.

## Interpretation and boundary

This controlled audit extends the previous (E=3,K=1) exact witness to
(E=4), (K=1,2,3). It verifies, for the preregistered Gumbel-Top-K cells,
that per-expert clipping attenuates the expected request Jacobian coordinate
by coordinate and yields a non-conservative expected admitted field at the
tested skewed pressures. It does **not** prove nonzero curl for every
Top-(K) distribution, every pressure, or every capacity vector. It also
does not show worse overflow, instability, windup, model-quality loss, or a
benefit from paying for requested counts.

The literature boundary remains material. The 2026 ICML paper
[\(\phi\)-Balancing](https://proceedings.mlr.press/v306/chen26br.html)
explicitly optimizes a convex potential of the **expected routing
distribution**. The present calculation studies the Jacobian of the
**expected per-expert admitted counts after clipping**. The experiment does
not contradict the former result and should not be described as showing that
MoE balancing lacks a potential in general. It only shows that this
particular clipped expected-feedback field is non-potential in the registered
cells.

This is one controlled mechanism result within the original research line.
To support the professor report's broader value-of-information/control
claim, a separate theorem still must connect this field property to a
quantitative closed-loop cost gap and account for observation cost. The
present audit supplies neither of those steps.

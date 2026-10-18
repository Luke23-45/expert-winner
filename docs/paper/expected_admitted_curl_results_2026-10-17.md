# Exact finite-batch evaluation of the admitted-field curl

**Formula:** [`expected_admitted_curl_theorem_2026-10-17.md`](expected_admitted_curl_theorem_2026-10-17.md).  
**Evaluator:** [`audit_expected_admitted_curl.py`](../../scripts/audit_expected_admitted_curl.py).  
**Artifact:** [`summary.json`](../../results/expected_admitted_curl/summary.json).

The evaluator sums the binomial probabilities as exact rational numbers. The
table reports the sensitivity factors
`alpha_e=P(Binomial(T-1,pi_e)<C_e)` and the tangent curl divided by
`gamma/lambda` for the fixed witness
`pi=(0.5,0.3,0.2)`, `C/T=(0.4,0.5,0.1)`.

| T | alpha 1 | alpha 2 | alpha 3 | Curl / (gamma/lambda) | No-clipping control |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.253906 | 0.901191 | 0.134218 | -0.063043 | 0 |
| 20 | 0.179642 | 0.967447 | 0.082866 | -0.074773 | 0 |
| 50 | 0.076204 | 0.998349 | 0.021449 | -0.085183 | 0 |
| 100 | 0.021938 | 0.999984 | 0.002670 | -0.088795 | 0 |
| 200 | 0.002228 | 1.000000 | 0.000051 | -0.089887 | 0 |
| 500 | 0.000004 | 1.000000 | < 0.000001 | -0.090000 | 0 |

The exact finite curl approaches the theorem's limit `-9/100`; it is already
nonzero at every evaluated batch size. The no-clipping control is exactly
zero at every size. These are deterministic evaluations of the theorem's
declared synthetic model, not stochastic Monte Carlo estimates or evidence
of a controller-performance advantage.

Reproduce with `python scripts/audit_expected_admitted_curl.py`.

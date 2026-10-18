# Controlled audit: heterogeneous capacity slack at a planted Top-K facet

**Question.** How does unequal capacity slack at the two experts exchanged
across a regular Top-K facet affect the probability that admitted feedback
has a non-potential tangential jump?

**Protocol.** The script
[`run_heterogeneous_facet_slack_audit.py`](../../scripts/run_heterogeneous_facet_slack_audit.py)
uses $E=4$, $K\in\{1,2,3\}$, and $T\in\{32,64,128\}$. For one planted
$i\to j$ exchange, each of the other $T-1$ tokens independently draws a
uniform $K$-subset, exactly the selected-set distribution induced by iid
exchangeable continuous scores at fixed pressure. Capacities at the exchanged
experts are rounded to
\[
(T-1)K/E+z\sqrt{(T-1)(K/E)(1-K/E)},
\]
for slack pairs $z\in\{(0,0),(-1,1),(-1,0),(0,1)\}$. These 36 cells have
an exact rational multinomial probability and 5,000 seeded route-level Monte
Carlo replicates. The audit adds nine exact-total controls with capacity
vector $(pT/2,3pT/2,pT,pT)$, where $p=K/E$; this places the exchanged experts
on opposite sides of the mean request rate while preserving $\sum_e C_e=KT$.

**Result.** All 36 Monte Carlo estimates were within five binomial standard
errors of their exact finite probabilities; the largest deviation was
2.2295 standard errors. At $T=128$, the exact probabilities in the
square-root-slack cells were:

| $K$ | $z_i,z_j=(0,0)$ | $(-1,1)$ | $(-1,0)$ | $(0,1)$ |
|---:|---:|---:|---:|---:|
| 1 | 0.607717 | 0.784609 | 0.546839 | 0.577832 |
| 2 | 0.608618 | 0.770276 | 0.560161 | 0.572073 |
| 3 | 0.596854 | 0.776656 | 0.501365 | 0.613918 |

The corresponding bivariate-normal limits at the target slack pairs are
0.608173, 0.778839, 0.564311, and 0.564311. The finite-$T$ values need not
be close at this batch size: the event uses the strict integer threshold
$X_e<C_e$, and rounding is material when the standard deviation is only a
few counts. The theorem is the asymptotic statement, not a claim that
$T=128$ is already in its limiting regime.

In the exact-total cross-mean controls, the probability approaches one as
predicted by the law-of-large-numbers corollary:

| $K$ | $T=32$ | $T=64$ | $T=128$ |
|---:|---:|---:|---:|
| 1 | 0.917422 | 0.981117 | 0.998868 |
| 2 | 0.996754 | 0.999962 | 0.99999999 |
| 3 | 0.999996 | 0.9999999999 | $1-1.85\times10^{-19}$ |

The displayed values are exact probabilities rounded for readability; for
example, the last is strictly below one despite its decimal rounding.

Exact probabilities, capacities, realized standardized thresholds, seeds,
Monte Carlo errors, and normal-limit values are in
[`summary.json`](../../results/heterogeneous_facet_slack/summary.json).
Reproduce with:

```powershell
python scripts/run_heterogeneous_facet_slack_audit.py
```

This checks the declared conditional planted-facet model. It does not sample
facets uniformly from a full arrangement, infer production prevalence, prove
a controller-performance effect, or defeat the finite-instance outcome-map
reduction. The bivariate-normal expression and law-of-large-numbers
corollary use standard probability tools; no novelty claim is made for those
calculations in isolation.

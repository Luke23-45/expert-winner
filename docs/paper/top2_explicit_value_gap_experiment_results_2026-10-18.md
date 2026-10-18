# Controlled Top-2 experiment: explicit all-policy value-gap certificate

**Theorem:** [Top-2 two-saturated value gap](topk_two_saturated_value_theorem_candidate_2026-10-17.md)  
**Protocol:** [registered experiment protocol](top2_explicit_value_gap_experiment_protocol_2026-10-18.md)  
**Runner:** [`run_top2_explicit_value_gap_experiment.py`](../../scripts/run_top2_explicit_value_gap_experiment.py)  
**Machine output:** [`summary.json`](../../results/top2_explicit_value_gap_2026-10-18/summary.json) and [`cells.csv`](../../results/top2_explicit_value_gap_2026-10-18/cells.csv)

## Question and scope

This run checks finite-batch consequences of the theorem's fixed
`E=3, K=2` two-world construction at the batch sizes where the proved
all-pressure lower-bound expression is positive. It uses the canonical
Gumbel-Top-2 / Plackett-Luce router and coordinatewise capacity clipping.
The connection between Gumbel-Top-k sampling and the Plackett-Luce law is
standard; it is used here to compute the router's exact count law, not as a
novelty claim ([Kool et al., JMLR 2020](https://jmlr.org/papers/volume21/19-985/19-985.pdf)).

The analytic theorem covers arbitrary pressure actions and all policies in
the stated one-step information model. Monte Carlo in this experiment does
**not** test that all-policy statement. It checks the registered classifier,
paired coupling, clipping/mass identities, and finite expected cost formulas.

## Registered configuration

- Worlds: standard-Gumbel Top-2 score weights `(2,1,1)` and `(1,2,1)`,
  equal prior, first-batch pressure zero.
- Capacity fractions: `(11/20, 11/20, 9/10)`; integer capacities are
  `924,924,1512` at `T=1680`, `990,990,1620` at `T=1800`, and
  `1848,1848,3024` at `T=3360`.
- Batch sizes: `T={1680,1800,3360}`. The first-positive designation for
  `T=1680` refers to the original Hoeffding-only lower-bound expression; it
  came from a double-precision scan over multiples of 20, not a certified
  minimal threshold. A sharper exact-tail proof was added later and certifies
  positivity at `T=540` without changing this registered grid.
- Replication: 50,000 paired batches per world and batch size, with the
  registered exact coupling.
- Decision actions: the two target-matching pressures only for the empirical
  Bayes-risk comparison. The theorem's lower bound is separately reported
  for unrestricted pressure policies.

## Results

| `T` | Exact request classifier error, worlds 0 / 1 | Exact admitted sign error | Paired admitted vectors equal | Exact two-action requested value | Exact two-action admitted value | Two-action gap | Original Hoeffding all-policy lower bound |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,680 | `3.31e-37` / `1.05e-26` | 0.498673 | 0.99490 | 0.012601 | 0.155019 | 0.142418 | 0.002752 |
| 1,800 | `9.97e-40` / `1.82e-28` | 0.499018 | 0.99602 | 0.012174 | 0.154892 | 0.142718 | 0.026382 |
| 3,360 | `1.88e-72` / `2.70e-51` | 0.499978 | 0.99984 | 0.008912 | 0.153484 | 0.144572 | 0.106835 |

No request-classification errors appeared in the 50,000 Monte Carlo draws;
the exact tail probabilities above are nonzero. The admitted sign classifier
is near chance because the paired world observations approach the same law.
The exact two-action value gap is not the unrestricted value gap. The last
column is the theorem's analytic lower bound for the unrestricted policy
class, not a simulation estimate.

All registered request-mass, clipping, coupling, and classifier checks
passed. The runner reported the classifier Monte Carlo comparison within five
standard errors for every cell. The run reproduced the recorded hashes:

- `cells.csv`: `a5a2fc411e32282a003c596a4dae74edb7a96a6a13184fedb8d6b83784f1131b`
- `summary.json`: `ca7c5b6950f8355a47a17fdd6dc233cc168d84690dd51bdd0f26abc2466fe8dc`
- runner: `e8cefc2fc81f67c553cbed472d2f40866b8950b6d021756a5cf711684e1b27de`

The independent exact-symbolic verifier also passed. It checked the Top-2
omission formulas, pair-difference identity, `Q >= 1`, and all three cases in
the ratio inequality, certifying the rational bracket
`27/200 <= v_* <= 459/3080` for the common-action value. It now also certifies
strict positivity of the unrestricted all-policy finite-batch lower bound at
`T=1680` using exact rational inequalities: for `x>0`,
`exp(-x) <= (1+x/10000)^(-10000)`, and
`sqrt(1680)>2049/50`. Substitution gives a rigorous bound greater than
`0.0026781420` normalized-overflow units (the bound expression itself is
approximately `0.0027517758`). This certificate is independent of the Monte
Carlo estimate and removes the prior floating-point-only qualification for
the sign of the theorem bound.

The finite-batch proof was subsequently sharpened with Jensen's inequality,
exact rational binomial tails, and a variance bound at the target action. The
same all-pressure, all-policy comparison now has exact-rational positive
certificates at both `T=540` and `T=1680`; at the latter it gives a lower
bound greater than `0.1138908062645108654518647134002223945491`. These are
proof bounds, not Monte Carlo estimates. The experiment's table retains the
original Hoeffding bound values so its recorded results remain unchanged.

## Interpretation

This is controlled evidence for the finite-count and coupling calculations
under the formal model. Combined with the analytic result, it supports a
specific C2 statement: under two simultaneously clipped swapped experts,
the admitted signal's one-step decision value remains bounded away from the
requested signal's value in this Top-2 family. This is an application of
existing costed testing / Bayesian experiment machinery, not a separation
from it: see [Cicalese et al., ICML 2014](https://proceedings.mlr.press/v32/cicalese14.html),
[Saettler et al., Information Processing Letters 2015](https://doi.org/10.1016/j.ipl.2015.02.006),
and the exact embedding recorded in
[`topk_swapped_saturation_reduction_attack_2026-10-17.md`](topk_swapped_saturation_reduction_attack_2026-10-17.md).

The price `kappa` in the theorem is abstract and measured in overflow units.
The theorem does not establish that requested counts cost exactly one
E-vector collective in an implementation. METRO is evidence that a serving
system may pay communication overhead for global routing information, but
its primary paper describes all-gathering token data for global Top-K
placement/routing, which is not the same measurement as reducing a vector of
per-expert request counts ([METRO](https://arxiv.org/abs/2512.09277)). No
latency, energy, or throughput price for the latter is measured here. The
result also does not prove a universal controller windup result, demonstrate
trained-model quality, or resolve the top-conference novelty gate.

Reproduce from the repository root with:

```powershell
python scripts/run_top2_explicit_value_gap_experiment.py
python scripts/verify_top2_explicit_common_value_bound.py
```


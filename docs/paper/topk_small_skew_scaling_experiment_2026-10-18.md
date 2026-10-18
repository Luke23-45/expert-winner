# Controlled audit: Top-K pair-skew value scaling

**Purpose.** Check the explicit symmetric pair-skew coefficient in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md): a finite Plackett-Luce prefix-sum grid for general `E,K`, a population value optimization for the symmetric `E=3,K=2` family, and a paired finite-batch signal check for its rational example.

The runner also contains a preregistered paired price diagnostic for a
restricted decision class: after seeing the requested or admitted vector,
choose between the two pressures that exactly match the capacity target in
one of the swapped worlds. The classifier uses the signed count difference
and randomizes on ties. Its break-even price is in overflow units and applies
only to this declared policy class; it is not the unrestricted theorem's
break-even and not a hardware collective price.

An independent numerical integral over the three type-A switching facets
for `E=3,K=2` also checks the root-facet representation of the same C2
sensitivity coefficient.

The runner additionally checks the finite-batch bridge from the root-facet
Top-K sensitivity to the derivative of clipped admitted counts. For
`E in {3,4,8}`, `K in {1,floor(E/2),E-1}` (deduplicated), `r in {1/3,1,3}`,
and `T in {600,1500,3000}`, it constructs an exact-total integer capacity
profile with the symmetric pair below its request probability and the tail
experts above theirs. The analytic pair sensitivity and binomial attenuation
are compared against central finite differences of the exact binomial-sum
expectation `E[min(Binomial(T,p),C)]`. This is a deterministic audit of
expected values, not a sampled controller trajectory.

**Scope.** This is a controlled synthetic audit of a stated asymptotic
theorem. The population optimization is numerical, not a global certificate;
the finite-batch sections, including the added price diagnostic, are Monte
Carlo. Neither establishes benchmark separation, measured telemetry cost, or
trained-model benefit.

## Fixed protocol

The router is standard-Gumbel Top-2 with three experts, equivalently a
Plackett-Luce ranking. For positive weights `w`, the exact probability that
expert `i` is omitted is

```text
lambda_i = w_j*w_k/(sum(w)) * (1/(w_i+w_k) + 1/(w_i+w_j)),
```

where `{i,j,k}={1,2,3}`. The inclusion probability is `rho_i=1-lambda_i`.
Overflow is `sum_i (rho_i-c_i)_+ / 2`, with exact-total capacity fractions
`sum_i c_i=2`.

For the population check, capacities are `(c,c,2-2c)` for
`c in {0.55,0.65,0.80}`. Baseline pair inclusion is set to `c+m` for
`m in {0.04,0.08}`; this uniquely determines the symmetric baseline weight
ratio `u`. The target ratio `r_c` is defined by `rho_1(r_c,r_c,1)=c`.
The two worlds have weights
`(u*exp(epsilon),u*exp(-epsilon),1)` and
`(u*exp(-epsilon),u*exp(epsilon),1)`, with
`epsilon in {0.04,0.02,0.01,0.005}`. A two-dimensional differential
evolution search minimizes the equal-prior common-action population overflow
over a pressure box centered at the zero-skew target action, with width 3 in
each quotient coordinate. The optimizer is a diagnostic and does not prove
global optimality. We compare its value divided by epsilon to the theorem's
analytic coefficient `j(r_c)/2`.

For the finite-batch check, the fixed rational case is
`c=11/20`, `u=2/3`, and `T in {1000,5000,20000}`. For each
`epsilon in {0.04,0.02,0.01}`, 20,000 standard-seeded multinomial batches are
drawn from the exact three-category omitted-expert law. The requested
diagnostic predicts the world from the sign of `R_1-R_2`. The admitted
diagnostic couples the opposite world by swapping experts 1 and 2 in the
same sampled batch, then measures whether the resulting admitted vectors
match. This is a coupling check; it is not a Bayes-optimal policy comparison.

For the price diagnostic, use the same paired multinomial draws and each
world's target-matching pressure. A wrong target has an exactly computed
population overflow; a correct target has zero population overflow. Estimate
the signed-classifier error separately for each signal, including randomized
ties, and multiply the error-rate difference by the wrong-target overflow.
The reported price is the exact break-even for that two-action classifier
pair, up to Monte Carlo error. It does not optimize over arbitrary pressures
or arbitrary signal policies.

For a joint-limit diagnostic, `c=11/20` and
`T in {20000,160000,1280000}`. The baseline margin and skew follow
`delta=0.5*T^(-1/8)` and `epsilon=T^(-1/3)`. This sequence increasingly
satisfies the theorem's asymptotic scaling conditions. Only the population
common-action value is numerically optimized along this large-batch
sequence; no `T=1,280,000` count Monte Carlo is run.

For the general sensitivity grid, `E=3,...,8`, every `K=1,...,E-1`, and
`r in {1/3,1,3}` are enumerated (81 cells). For each cell the omission
probability is summed over all ordered top-`K` prefixes that exclude expert
1. The derivative `j_(E,K)(r)` is computed by differentiating each prefix
probability analytically through its log probability, then compared with a
central difference using step `1e-4`. A separately coded two-state dynamic
program aggregates the identical tail experts; prefix sum and recurrence
must agree to `1e-11` relative error. The baseline ratio is `u=2r`, which
provides a positive pair saturation margin in every cell.

For the root-facet check, specialize to `E=3,K=2`. A switching wall has two
tied lower scores and the remaining expert above them. Parameterize each wall
by the common tied score `t`; integrate the product Gumbel density times the
remaining expert's survival function over `t`; and combine the three wall
fluxes with the squared root-direction pairings in the Hessian formula.
Compare that result to the independently coded two-state recurrence at
`r in {1/3,1,3}`. This deterministic quadrature checks the coefficient
identity in this case, not the full arrangement-signature count or a value
consequence of that count.

For the clipping-attenuation bridge, use the same symmetric pair scores for
the registered `(E,K,r)` grid. Choose a positive pair overload margin no
larger than `0.05`, and split the remaining exact-total capacity equally
across the `E-2` identical tail experts up to integer rounding. For each
batch size, the pair capacity is rounded down and the remaining integer
capacity is distributed over the tails, so `sum_e C_e=K*T` exactly. Retain
only batch sizes for which every tail capacity fraction is strictly above
its request probability. Compute
`alpha_T=BinomialCDF(C-1;T-1,x)` and the exact clipped-count expectation by
the binomial survival sum. A central difference at score perturbation
`epsilon=2e-5` estimates both requested and admitted pair-contrast slopes.
The acceptance checks are: all capacities are integral and sum to `K*T`,
the tail capacities remain above their inclusion probabilities, and the
finite-difference slopes agree with `2j/K` and `alpha_T*2j/K` to absolute
error below `1e-7`.

To evaluate the coefficient beyond direct enumeration, the two-state
recurrence is also run at `E in {8,16,32,64,128,256,512}`, four representative
`K` values per `E`, and the same three pair ratios (84 cells). This is a
deterministic parameter sweep, not a trained-router experiment.

The fixed seed is `20261018`. The runner is
[`run_topk_small_skew_scaling.py`](../../scripts/run_topk_small_skew_scaling.py).
Raw output is in
[`population_scaling.csv`](../../results/topk_small_skew_scaling_2026-10-18/population_scaling.csv),
[`finite_batch_signal_check.csv`](../../results/topk_small_skew_scaling_2026-10-18/finite_batch_signal_check.csv),
[`priced_decision_class.csv`](../../results/topk_small_skew_scaling_2026-10-18/priced_decision_class.csv),
[`root_facet_sensitivity.csv`](../../results/topk_small_skew_scaling_2026-10-18/root_facet_sensitivity.csv),
[`joint_limit_scaling.csv`](../../results/topk_small_skew_scaling_2026-10-18/joint_limit_scaling.csv),
[`pair_sensitivity_grid.csv`](../../results/topk_small_skew_scaling_2026-10-18/pair_sensitivity_grid.csv),
[`large_pair_sensitivity_grid.csv`](../../results/topk_small_skew_scaling_2026-10-18/large_pair_sensitivity_grid.csv),
and [`summary.json`](../../results/topk_small_skew_scaling_2026-10-18/summary.json).
An independent reproduction on 2026-10-18 reproduced all eight registered
CSV hashes exactly; its runner fingerprint and Python/NumPy/SciPy versions are
recorded in
[`reproduction_manifest.json`](../../results/topk_small_skew_scaling_2026-10-18/reproduction_manifest.json).

## Results

Across 24 population cells, the maximum absolute difference between the
optimized `v_*(epsilon)/epsilon` and the predicted coefficient decreased by
approximately fourfold each time epsilon was halved:

| epsilon | Maximum absolute slope error |
|---:|---:|
| 0.04 | 1.4060e-4 |
| 0.02 | 3.5167e-5 |
| 0.01 | 8.7927e-6 |
| 0.005 | 2.1982e-6 |

The predicted coefficients for the three capacity pairs were respectively
`0.243750`, `0.214788`, and `0.142316`. The approximately quadratic
decrease in slope error is consistent with an `O(epsilon^2)` remainder after
dividing the first-order expansion by epsilon. All 24 numerical optimizers
reported success. This is consistency evidence only: finite search bounds
and optimizer convergence do not certify the infimum over all pressures.

In the finite-batch coupling, the admitted vectors matched in all 20,000
paired samples for every `T>=5000`; at `T=1000`, alias rates were 0.99845,
0.99970, and 0.99990 for epsilon 0.04, 0.02, and 0.01. Request-sign error
rates were:

| epsilon | T=1,000 | T=5,000 | T=20,000 |
|---:|---:|---:|---:|
| 0.04 | 0.09665 | 0.00180 | 0 observed |
| 0.02 | 0.26000 | 0.07480 | 0.00210 |
| 0.01 | 0.38035 | 0.23540 | 0.07245 |

These values show the declared finite-sample tradeoff: the requested sign
becomes informative as `T*epsilon^2` grows, while the swapped admitted
observations remain equal under the coupling when both pair experts hit
capacity. “0 observed” is not zero probability; the 95% Wilson upper bound
for zero errors in 20,000 trials is about `1.92e-4`.

The joint population diagnostic approaches the predicted coefficient while
the baseline margin shrinks:

| T | epsilon / margin | `v_num / epsilon` | predicted coefficient | finite-batch noise bound / epsilon |
|---:|---:|---:|---:|---:|
| 20,000 | 0.2541 | 0.243635 | 0.243750 | 0.2879 |
| 160,000 | 0.1648 | 0.243721 | 0.243750 | 0.2036 |
| 1,280,000 | 0.1068 | 0.243743 | 0.243750 | 0.1440 |

At these points, `T*margin^2` is `420.4`, `2000`, and `9513.7`, while
`T*epsilon^2/log(1/epsilon)` is `8.22`, `13.59`, and `23.16`. The optimizer
diagnostic is consistent with the joint-limit statement. The finite-batch
noise term remains nonnegligible relative to epsilon at these finite values,
so this table does not numerically establish the full value-gap limit.

The general prefix-sum audit had 81 cells. Every computed sensitivity was
positive, every target tail capacity was in `(0,1)`, and the baseline pair
margin was positive. The maximum relative difference between the analytic
derivative and central difference was `7.45e-9`; the largest relative change
between the analytic derivative and the half-step derivative was `1.27e-4`.
The independent two-state recurrence agreed with the prefix sum to maximum
relative error `6.06e-14`.
At `E=3,K=2,r=1/3`, the sum gives `j=39/80` and the value slope `j/K=39/160`,
matching the exact rational derivation.

The larger 84-cell recurrence sweep covers `E` through 512. At `E=512`,
`r=1`, the proportional-`K` sensitivity values are `j=0.215939` for
`K=128` and `j=0.346763` for `K=256`; the limiting values from the theorem
are `0.215762` and `0.346574`. For `K=E-1,r=1`, the normalized quantity
`(j/K)*E^2/log(E)` is `0.9360` at `E=512`, consistent with the limit 1 but
showing a visible finite-size correction. The coefficient `j/K` declines
with `E` in these regimes, so the positive fixed-`E` gap must not be
described as an `E`-uniform constant.

The independent root-facet quadrature matched the prefix recurrence in all
three `E=3,K=2` cells. The maximum relative difference was `1.34e-16`:

| pair ratio `r` | flux through 1–2 facet | flux through 1–3 facet | root-facet `j` | recurrence `j` |
|---:|---:|---:|---:|---:|
| 1/3 | 0.210000 | 0.067500 | 0.487500 | 0.487500 |
| 1 | 0.138889 | 0.138889 | 0.416667 | 0.416667 |
| 3 | 0.066327 | 0.126276 | 0.258929 | 0.258929 |

The 1–3 and 2–3 facet fluxes agree by exchange symmetry. This numerical
identity supports the geometric interpretation of `j`; the
distributional-Hessian derivation is the proof.

The exact-binomial clipping bridge passed all 72 registered cells, including
the strict tail-capacity-above-mean check in every cell. The
maximum absolute errors between analytic slopes and central differences were
`9.59e-11` for requested counts and `5.32e-9` for admitted counts. In the
`E=3,K=2,r=1` profile, the pair attenuation was `0.0052153` at `T=600`,
`2.4867e-5` at `T=1500`, and `4.7144e-9` at
`T=3000`; the independently
computed finite-difference attenuation ratios agreed to the shown precision.
This verifies the finite-`T` derivative composition over the registered
Top-K cells. It does not test adaptive control, prove the theorem, establish
finite-sample non-identifiability, or resolve the independent-benchmark
novelty gate. The added raw output is
[`root_facet_clipping_attenuation.csv`](../../results/topk_small_skew_scaling_2026-10-18/root_facet_clipping_attenuation.csv),
with SHA-256 `025a84ee2b4fcabfa143cd1d58b8e6cb8ea216cc063654a1e146cf2696113a15`.

### Paired requested-telemetry price diagnostic

The added 9-cell diagnostic uses 20,000 paired draws per world and batch
size. For the declared two-target-pressure classifier class, the estimated
requested-versus-admitted value is positive in every cell. At `T=20,000`:

| `epsilon` | Requested error | Admitted error | Break-even price | Paired-cluster Hoeffding 95% interval |
|---:|---:|---:|---:|---:|
| 0.04 | 0 observed | 0.50120 | 0.009773 | [0.009399, 0.010148] |
| 0.02 | 0.00175 | 0.49773 | 0.004838 | [0.004651, 0.005026] |
| 0.01 | 0.07210 | 0.49740 | 0.002074 | [0.001981, 0.002168] |

Prices are in normalized-overflow units. The interval applies Hoeffding's
inequality to the per-paired-plant error-rate difference, whose values lie
in `[-1,1]`; it therefore respects dependence between the two worlds and
between the requested/admitted classifiers. It quantifies Monte Carlo
uncertainty for the declared policies; it does not
cover the unrestricted optimal threshold `kappa_star`. The admitted vectors
matched in every registered sample at `T=20,000`. Zero observed request
errors at `epsilon=0.04` does not imply zero true error. The all-policy
theorem, not this simulation, supplies the unrestricted value guarantee.

The raw CSV digests are:

- `population_scaling.csv`: `039269d53c54fe89f1ee7e2490f705c7a85cb6ee1ac20a5d8eef27b91d917bd4`
- `finite_batch_signal_check.csv`: `67bd765b36bce05fe35ca70e1f0f707616c68909a8437dcb405e9c52c1a6c317`
- `priced_decision_class.csv`: `5a85f7893bb489db34eff3c448e3758ee5bc0d180ad17979d0918f712b432ce3`
- `joint_limit_scaling.csv`: `2c7d49a4020f07c5b0eae773e9f1354661825e88a4a3ba333108972639101afb`
- `pair_sensitivity_grid.csv`: `01db97190ac2017d02e455a6dc78100aced2e9a4f9f24036b3205eef5e372910`
- `root_facet_sensitivity.csv`: `eac989cc0cc921221c91550331ab2745f5e626496fd8d13843ef9b66e734fde6`
- `large_pair_sensitivity_grid.csv`: `6ad94cc54a0c903991ed4fc670dd6df82449eae3614399f71bf35cbb0fce6cb4`

## What this establishes

The experiment is consistent with the explicit pair-skew sensitivity formula
for all enumerated `E,K`, the large-`E` scaling laws, the capacity-dependent value slope proved for the
symmetric `E=3,K=2` Gumbel-Top-2 family, and the finite-batch coupling
mechanism in the named rational instance. It does not
show a class-level advantage over adaptive testing: each fixed finite
experiment remains an exact censored Bayesian experiment. The analytic
finite-batch inequality gives the joint limit for this symmetric family, but
the numerical table does not prove that limit. The Top-K connection is now
proved in the companion saturation-multiplicity theorem: its local value
slope is an explicit Plackett–Luce prefix sum, equivalently a weighted flux
through Top-K switching facets, with large-`E` scaling laws. This closes the
earlier proof obligation to derive a capacity/skew/`K`/`E` law from Top-K
structure. It does not by itself establish novelty or significance relative
to the broader costed-testing benchmark, and it does not measure a real
collective's price. Those are now the unresolved contribution questions;
the arbitrary-capacity common-action constant `v_*(c)` also remains implicit
outside the stated local regime.

## Literature boundary from primary sources

Kumar and Mouchtaki analyze an offline data-driven newsvendor with historical
demand censored by inventory levels; they characterize worst-case regret and
show the value of targeted exploration in that setting. This is the closest
censoring/value neighbor because the observation map is also a capacity
censoring map, but their model is demand/inventory learning rather than a
Top-K choice map with pressure actions. Their result means the generic claim
“censoring creates value for more information” is not novel by itself. See
the [primary paper](https://arxiv.org/abs/2602.16842).

Cicalese, Laber, and Saettler formalize adaptive tests over finite hypotheses
with prior probabilities and test costs, optimizing expected or worst-case
testing cost. The project's fixed two-world requested/admitted experiment
has an exact costed-testing representation, so the present result should be
claimed as an explicit calculation for a structured Gumbel-Top-2 family,
not a new general theory of testing under censoring. Their paper does not
derive the capacity-specific coefficient `j(r_c)/2` or the joint
slack/skew/batch scaling law. See the [ICML primary paper](https://proceedings.mlr.press/v32/cicalese14.html).

Gong and Zhang's ICML 2026 paper studies paid observations in contextual
bandits, jointly charging observation expenditure and regret, and proves a
budget-dependent phase transition. This establishes paid observation as an
active theory area; the present break-even corollary must therefore be
positioned as a Top-K/capacity-specific value calculation, not as a new
general framework for pricing information. Their adversarial contextual
bandit objective and budgeted repeated observation protocol differ from the
single optional requested-count measurement followed by a pressure decision
here. See the [ICML 2026 primary paper](https://proceedings.mlr.press/v306/gong26i.html).

This is a targeted boundary check, not a systematic novelty review. The
measurement cost of requested counts is still not measured in the controlled
experiment or established by these two sources.

## Reproduction

From the repository root:

```powershell
python scripts/run_topk_small_skew_scaling.py
```

The deterministic cell definition, optimizer bounds, seed, multinomial
replicate count, and raw-output paths are fixed in the runner above.

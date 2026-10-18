# Exact arbitrary-E Top-1 swapped-value experiment: results

**Protocol:** [locked design](top1_arbitrary_e_exact_swapped_value_protocol_2026-10-17.md)  
**Theorem:** [exact common-action value](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md)  
**Runner:** [`../../scripts/run_top1_arbitrary_e_exact_swapped_value.py`](../../scripts/run_top1_arbitrary_e_exact_swapped_value.py)  
**Finite-batch bound scan:** [`../../scripts/audit_top1_finite_batch_value_thresholds.py`](../../scripts/audit_top1_finite_batch_value_thresholds.py)  
**Summary:** [`../../results/top1_arbitrary_e_exact_swapped_value/summary.json`](../../results/top1_arbitrary_e_exact_swapped_value/summary.json)  
**Bound thresholds:** [`../../results/top1_arbitrary_e_exact_swapped_value/finite_batch_bound_thresholds.json`](../../results/top1_arbitrary_e_exact_swapped_value/finite_batch_bound_thresholds.json)  
**Paired draws:** [`../../results/top1_arbitrary_e_exact_swapped_value/paired_replicates.csv`](../../results/top1_arbitrary_e_exact_swapped_value/paired_replicates.csv)

## Run and exact checks

The run covers 18 cells: `E={3,4,8,16,32,64}`, three batch sizes per `E`,
and 2,000 paired multinomial first-batch draws per cell. World 1 is the
exact swap of the first two request counts from the world-0 draw. Every
cell passed the request-mass, capacity-mass, and swap checks. The exact
analytic family has `sum C=T`; the simulator converts its rational
probabilities to double precision for NumPy multinomial sampling. Expected
next-batch overflow is computed from binomial marginal tails rather than
from a second Monte Carlo batch.

The registered fixed-action rules use the sign of `R_1-R_2` or
`A_1-A_2`, with ties randomized. A separate exact analysis proves these
rules Bayes-optimal for their respective **full observations** when the
available actions are restricted to the two world-matched target pressures.
This is a post-run characterization of the locked experiment; it does not
claim optimality over arbitrary pressure actions. See
[`top1_arbitrary_e_bayes_value_analysis_2026-10-17.md`](top1_arbitrary_e_bayes_value_analysis_2026-10-17.md).
The analytic common-action optimum `v*=1/36` comes from the theorem proof;
this run does not estimate it.

## Largest tested batch per expert count

| `E` | `T` | Requested error | Admitted error | Paired admitted equality | Requested expected overflow | Admitted expected overflow |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 64 | 0.2113 | 0.4418 | 0.870 | 0.07223 | 0.07709 |
| 4 | 128 | 0.1510 | 0.4683 | 0.932 | 0.06506 | 0.07381 |
| 8 | 384 | 0.0310 | 0.4973 | 0.995 | 0.05246 | 0.07018 |
| 16 | 896 | 0.0060 | 0.5000 | 1.000 | 0.04634 | 0.06806 |
| 32 | 1,920 | 0.0000 | 0.5000 | 1.000 | 0.04276 | 0.06657 |
| 64 | 3,968 | 0.0000 | 0.5000 | 1.000 | 0.04051 | 0.06552 |

At every largest-batch cell, the registered requested classifier has lower
expected next-batch overflow than the admitted classifier; the difference
exceeds twice the sum of their Monte Carlo standard errors. The output also
shows the expected approach toward indistinguishable admitted vectors under
the coupling, while requested counts increasingly identify the swapped
world. These are constructed synthetic results; the table does not establish
production prevalence or general controller dominance.

Exact binomial calculations remove Monte Carlo error from the registered
two-target-action comparison. At the largest registered batch size for each
expert count, the exact no-signal, requested-signal, and admitted-signal
expected normalized overflows are:

| `E` | `T` | No signal | Requested signal | Admitted signal | Requested advantage over admitted |
|---:|---:|---:|---:|---:|---:|
| 3 | 64 | 0.07832244 | 0.07261666 | 0.07707063 | 0.00445398 |
| 4 | 128 | 0.07468273 | 0.06496167 | 0.07381783 | 0.00885616 |
| 8 | 384 | 0.07027979 | 0.05260370 | 0.07017671 | 0.01757301 |
| 16 | 896 | 0.06805819 | 0.04619535 | 0.06805688 | 0.02186154 |
| 32 | 1,920 | 0.06656789 | 0.04276027 | 0.06656789 | 0.02380762 |
| 64 | 3,968 | 0.06551945 | 0.04051226 | 0.06551945 | 0.02500719 |

These are exact count-law expectations evaluated in double precision, for
the two registered target actions only. They are not values optimized over
the continuous pressure space.

The exact `v*=1/36` result also yields an all-policy finite-batch lower bound.
The first analysis used a Chernoff upper bound for requested-count
classification. I replaced that term with the exact binomial error of the
same randomized sign classifier, conditioning on `M=R_1+R_2`. This does not
change the theorem or its policy quantifiers; it sharpens only the explicit
finite-`T` certificate. Exact rational enumeration of the multinomial law
for `E=3`, `T in {4,8,12}` agrees with the binomial formula to below
`6e-17` in absolute error.

The bound remains negative on every originally registered cell; at the
largest tested `T` by `E`, it ranges from approximately `-0.867` to
`-0.0127`. A new floating-point scan over admissible batch sizes finds the
first positive lower bounds at:

| `E` | `T` | Exact-sign error | All-policy gap lower bound |
|---:|---:|---:|---:|
| 3 | 704 | 0.006962 | 0.000129 |
| 4 | 832 | 0.003753 | 0.000027 |
| 8 | 1,356 | 0.000321 | 0.000124 |
| 16 | 2,492 | 0.00000185 | 0.000113 |
| 32 | 4,620 | 1.49e-10 | 0.000178 |
| 64 | 8,556 | 5.00e-18 | 0.000155 |

The exact sums and thresholds are in
[`finite_batch_bound_thresholds.json`](../../results/top1_arbitrary_e_exact_swapped_value/finite_batch_bound_thresholds.json),
generated by [`audit_top1_finite_batch_value_thresholds.py`](../../scripts/audit_top1_finite_batch_value_thresholds.py).
Thresholds and lower bounds are double-precision diagnostics, not
interval-certified minimal values. This closes the finite-size positivity
check for this theorem family; it still does not show a benchmark separation,
measured telemetry cost, or real-system benefit.

## Reproducibility and limits

The runner was rerun after adding exact Bayes-risk and no-signal fields. The
fixed-seed paired CSV remained byte-identical; the summary hash changed to
include the new fields.

| Artifact | SHA-256 |
|---|---|
| Summary JSON | `bb4a21f187869a5ec882ae9890534fc5ba3020b4461ed0e128ae5f6d9e6ab40f` |
| Paired CSV | `6b49721a4c5183db7716ad956998834a88fda21427f2c9575c3066f970e9045` |
| Finite-batch threshold JSON | `168e38b8263f2db1ebfbfae0b8bec84ec818ca7f7d22bfb57cc924e29d2e59c6` |

The symbolic numerator identities and the exact equality action were also
checked with
[`verify_top1_arbitrary_e_value_algebra.py`](../../scripts/verify_top1_arbitrary_e_value_algebra.py).
The Bayes sign-rule argument was separately checked by exact-rational
enumeration for `E=3` and `T in {4,8,12,16}` in
[`verify_top1_bayes_observation_value.py`](../../scripts/verify_top1_bayes_observation_value.py).

No GPU training, model quality, hardware latency, collective count, or
telemetry-cost break-even was measured. The experiment supports the exact
family's predicted signal behavior only. The theorem's one-step problem
still has an exact representation as a generic censored decision problem;
this result does not clear the benchmark-separation gate.

# Exact Bayes value of requested versus admitted counts

**Status:** exact finite-batch analysis for the registered two-world,
two-target-action experiment. This is a post-run characterization of the
locked experiment, not an enlargement of its policy class.

## Setup and scope

Use the two swapped worlds and capacities from
[`top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md`](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md), at a registered
integer batch size `T`. The signal is either the full request vector
`R`, or the full admitted vector `A=min(R,C)`. After observing the signal,
the controller chooses one of exactly two actions: the pressure that makes
the current world's mean request vector equal to `c`, or the corresponding
pressure for the other world. The prior on the worlds is uniform.

This analysis does **not** optimize over arbitrary pressure actions. It
establishes exact optimality within the two registered target-pressure
actions.

## Bayes rule for requested counts

For any request vector `r`, the likelihood ratio is

```text
P_0(R=r) / P_1(R=r) = (5/4)^(r_1-r_2).
```

Therefore the Bayes classifier chooses world 0 when `r_1>r_2`, world 1
when `r_1<r_2`, and randomizes on a tie. This is exactly the registered
requested-count sign rule.

## Bayes rule for admitted counts

The first two capacities are equal. Consider the fiber of the clipping map
over an admitted vector `a`.

- If `a_1>a_2`, every request vector in the fiber has `r_1>r_2`: when
  `a_1<C_1`, both counts are observed exactly; when `a_1=C_1`,
  `r_1>=C_1>r_2=a_2`.
- If `a_1<a_2`, the symmetric statement holds.
- If `a_1=a_2<C_1`, the fiber has `r_1=r_2=a_1`, so the two world
  likelihoods agree term by term.
- If `a_1=a_2=C_1`, the fiber is invariant under swapping `r_1` and
  `r_2`. The two worlds' likelihoods are exchanged by that bijection,
  so their total likelihoods are equal.

The remaining expert probabilities are identical in the two worlds and
their admitted coordinates do not change under the swap. Thus the full
admitted vector's Bayes rule is the sign of `a_1-a_2`, with randomization
on a tie. This is exactly the registered admitted-count sign rule. In
particular, the comparison uses the **full** admitted vector; the other
coordinates do not improve the Bayes decision for this symmetric pair.

## Exact finite-batch values

Let `M=R_1+R_2`. Under world 0,

```text
M ~ Bin(T, 9/13),        R_1 | M=m ~ Bin(m, 5/9).
```

This gives the exact request-classification error by summing
`P(M=m) [P(R_1<m/2 | m) + 0.5 P(R_1=m/2 | m)]`. The admitted error is
the same sum over the regions where clipping leaves `A_1<A_2`, plus half
the tie mass where the admitted pair is equal. The runner evaluates these
finite binomial sums and records both exact expectations and the registered
Monte Carlo audit in
[`../../results/top1_arbitrary_e_exact_swapped_value/summary.json`](../../results/top1_arbitrary_e_exact_swapped_value/summary.json).

Write `r_c` for expected overflow after the correct target action and
`r_w` for expected overflow after the wrong target action. Symmetry makes
these costs the same in either world. For a signal with Bayes error `e`,
its exact expected next-batch overflow in the two-action class is

```text
V(e) = r_c + e (r_w-r_c).
```

In every registered cell `r_w>r_c`; hence the Bayes classifiers above are
also the minimum-overflow policies in the registered two-action class.
The no-signal value in that class is `(r_c+r_w)/2`.

At the largest registered batch size for each `E`, the exact count-law
values are:

| `E` | `T` | No-signal overflow | Requested-signal overflow | Admitted-signal overflow | Requested minus admitted improvement |
|---:|---:|---:|---:|---:|---:|
| 3 | 64 | 0.07832244 | 0.07261666 | 0.07707063 | 0.00445398 |
| 4 | 128 | 0.07468273 | 0.06496167 | 0.07381783 | 0.00885616 |
| 8 | 384 | 0.07027979 | 0.05260370 | 0.07017671 | 0.01757301 |
| 16 | 896 | 0.06805819 | 0.04619535 | 0.06805688 | 0.02186154 |
| 32 | 1,920 | 0.06656789 | 0.04276027 | 0.06656789 | 0.02380762 |
| 64 | 3,968 | 0.06551945 | 0.04051226 | 0.06551945 | 0.02500719 |

These are exact finite-binomial expectations evaluated in double precision;
the Monte Carlo columns in the original results document are independent
simulation checks. Values displayed as zero there are not used here; errors
are retained at full precision in the JSON.

## Interpretation boundary

This closes an ambiguity in the experiment: within the **two target
actions**, the registered full-request and full-admission decision rules
are Bayes-optimal, so their value difference is not caused by a deliberately
weak sign heuristic. It remains a synthetic, finite-batch value-of-signal
result for a constructed two-world family. It does not show optimality over
the continuous pressure space, a multi-round theorem, a hardware or model
quality benefit, or separation from a general adaptive-testing benchmark.

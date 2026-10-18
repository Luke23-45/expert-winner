# Controlled check of the random-facet mismatch theorem

**Status:** completed; exact finite probabilities plus seeded route-level Monte
Carlo.  
**Question:** does direct simulation of the declared planted-facet law agree
with its exact multinomial mismatch probability and the predicted large-$T$
limit?

## Protocol

For each $E=4$, $K\in\{1,2,3\}$, and
$T\in\{8,16,32,64,128\}$, set uniform capacity
$C=KT/E$, so $\sum_e C_e=KT$. Plant one token on a regular $i\to j$ Top-$K$
facet. Simulate the remaining $T-1$ tokens by independently drawing a
uniform $K$-subset of the four experts. This is the exact route law induced
at a fixed pressure by independent continuous exchangeable expert scores;
the simulation operates on those route outcomes directly rather than
generating floating-point scores.

For every configuration, the script independently evaluates the exact
multinomial sum from
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md)
and performs 20,000 independent replicates. The observed event is
\[
\mathbf1\{X_i<C\}\ne\mathbf1\{X_j<C\},
\]
which is exactly the local source/destination mismatch condition. Each
configuration has a fixed seed derived from `20261017`, $K$, and $T$.

## Results

Exact probabilities and empirical proportions are rounded here to five
decimal places. The machine-readable result contains the exact rational
probabilities, seed, standard error, and error measured in standard-error
units for every cell.

| $K$ | $T=8$ exact / MC | $T=16$ exact / MC | $T=32$ exact / MC | $T=64$ exact / MC | $T=128$ exact / MC |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.60083 / 0.59975 | 0.60450 / 0.60130 | 0.60634 / 0.60835 | 0.60726 / 0.60915 | 0.60772 / 0.61045 |
| 2 | 0.61666 / 0.62365 | 0.61201 / 0.61135 | 0.61001 / 0.60705 | 0.60907 / 0.61645 | 0.60862 / 0.61210 |
| 3 | 0.60083 / 0.60355 | 0.60450 / 0.61155 | 0.60634 / 0.60110 | 0.60726 / 0.60800 | 0.60772 / 0.60530 |

The asymptotic prediction for $E=4$ is
$\pi^{-1}\arccos(-1/3)=0.60817345$. The exact finite-$T$ probabilities
approach this value across all three tested $K$ values. Every one of the 15
empirical proportions was within five binomial standard errors of its exact
probability; the largest deviation was 2.14 standard errors.

The theorem also implies an asymptotic expected squared tangential jump of
$((E-2)/(2E))p=0.15204336$ in count units at $E=4$. This quantity is derived
from the exact mismatch probability and the exact local facet geometry; it
was not separately estimated by Monte Carlo.

## Limits

This experiment verifies the finite probability calculation under the
declared route-level sampling law. It does not sample a uniformly random
facet from a complete arrangement, measure real-router facet prevalence,
evaluate pressure trajectories, or compare controller costs. It validates
the random-facet theorem's arithmetic, not its novelty or a control benefit.
The earlier ensemble experiment has a different facet-sampling procedure;
its mismatch percentages are not directly comparable to this conditional
probability.

Reproduce with `python scripts/run_random_facet_mismatch_probability.py`.
Raw results: [`summary.json`](../../results/random_facet_mismatch_probability/summary.json).

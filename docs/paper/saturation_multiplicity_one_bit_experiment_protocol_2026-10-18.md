# Frozen protocol: one-bit decision signal in the saturation-multiplicity family

**Research line:** professor-directed C2 value-of-information result, using the
same swapped-world Gumbel-Top-K model and per-expert clipping as the existing
saturation-multiplicity theorem. This is a preregistered follow-up, not a new
router, controller, admission rule, or paper direction.

**Question.** In the two-world, two-target-pressure decision problem, does
the single bit `Z = 1{R_1 > R_2}` preserve the exact Bayes value of the full
requested-count vector? When both swapped experts saturate, does this bit
recover value lost by admitted counts? The accompanying theorem note states
the finite decision result and the all-pressure asymptotic implication.

## Frozen model and grid

- Standard-Gumbel Top-K, equivalently Plackett-Luce subset sampling, with
  `E in {3,5,7}`, every `K=1,...,E-1`, and world-0 weights
  `(4/3,1,...,1)`. World 1 swaps experts 1 and 2. All tokens are iid.
- Batch sizes are `T=(E-2)*m` for `m in {96,192,384}`.
- For each `(E,K)`, construct the one- and two-saturation capacity profiles
  by the exact rational formulas in the existing saturation-multiplicity
  protocol. Round the common pair capacity to the nearest integer satisfying
  exact total capacity `sum_e C_e=K*T`; split the remaining capacity evenly
  over the `E-2` tail experts. Ties in rounding select the smaller capacity.
- Stop and report a failed cell if any capacity is nonpositive, `C_e>=T`,
  `sum C != K*T`, or the required strict saturated/unsaturated population
  margins fail. Do not change the grid to rescue a failed cell.
- Each signal is observed on the first batch. Its decision chooses between
  the two pressure vectors whose population inclusion vectors equal the
  capacity fractions in the corresponding swapped worlds. The next batch is
  independent and has the same world law. Primary losses are exact expected
  realized normalized overflow, summed over experts and divided by `K*T`.
  Numerically solved target-pressure residuals must be at most `1e-8`; stop
  and retain a failed cell if they exceed that threshold.

## Signals and primary endpoint

For each cell compute exact-count-law Bayes risk for:

1. `A` alone (zero extra message bits);
2. `Z=1{R_1>R_2}` (one fixed-length bit, with equality mapped to 0);
3. full `R`.

The primary endpoint is the `A`-only minus one-bit Bayes value, in normalized
overflow units. Also report the one-bit minus full-`R` difference and the
capacity profile. The theorem predicts the latter difference is exactly zero
for the registered two-action problem. It predicts a strictly positive
one-bit gain wherever the admitted observation loses a decision in the
two-saturation regime; it does not predict monotonicity across batch sizes.

The main grid uses the exact reduced count law, not Monte Carlo. An independent
exact-rational check enumerates all subset-count compositions for `E in
{3,4}`, all `K`, and `T in {2,4,6,8}` (only cells with `T>=K` are retained),
aggregates the complete request-vector distribution, and compares full-`R`
Bayes risk with the one-bit risk. This checks the likelihood-ratio sufficiency
claim independently of the main-grid formula.

## Controls and audit rules

- Check subset probabilities sum to one in both worlds and are exact swaps.
- Check `sum_e R_e=K*T`, exact integer capacity mass, and `A=min(R,C)`.
- Check target actions have equal diagonal risks and equal off-diagonal risks,
  with strictly larger off-diagonal risk.
- Check the exact full-`R` and one-bit Bayes errors agree on the registered
  grid; independently verify the equality by rational enumeration on the
  small grid. Any discrepancy is a failed theorem audit, not a reason to
  alter the statistic or parameters.
- Retain every cell, including any negative or null value gap.
- Do not interpret one bit as one scalar all-reduce, a lower latency, lower
  energy, or a measured implementation cost. The protocol measures decision
  value per bit only.

## Claim boundary

The finite exact result is for a binary swapped-world hypothesis and the
declared two-target action set. The existing all-pressure saturation theorem
provides a separate positive admitted/full-request value gap in the
two-saturation asymptotic regime. The bit's asymptotic sufficiency for that
all-pressure value follows by using it to choose the corresponding target
action and bounding classification and fresh-batch overflow errors.

This experiment does not prove a new general communication principle, defeat
the exact adaptive-testing representation of the finite instance, establish
that a one-bit collective is cheap, or demonstrate a trained-model benefit.
Those claims require distinct evidence and are not inferred here.

## Reproduction

```powershell
python scripts/audit_saturation_multiplicity_one_bit.py
```

The runner writes `results/saturation_multiplicity_one_bit_2026-10-18/` with
the full-grid CSV, exact-rational audit CSV, and a hash-bearing summary.

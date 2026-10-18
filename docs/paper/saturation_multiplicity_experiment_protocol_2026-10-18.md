# Controlled experiment protocol: one versus two saturated experts

**Theorem under test:**
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md).
The experiment stays inside the same Gumbel-Top-K router, exact-total
per-expert capacity rule, two swapped worlds, pressure action set, gauge, and
normalized overflow objective. It changes only the first-pair capacity
level, which changes the number of persistently saturated experts.

## Registered grid

- `E in {3,4,6,8}` and all `K=1,...,E-1`.
- World-0 Gumbel-Top-K weights `(5/4,1,...,1)`; world 1 swaps experts 1
  and 2. Compute every subset probability and inclusion mean exactly as a
  rational Plackett-Luce value.
- Let the first two world-0 inclusion means be `p_H>p_L`, with
  `Delta=p_H-p_L`; all tail inclusion means are equal by symmetry.
- **One-saturation profile:** `c_1=c_2=p_L+Delta/4` and
  `c_j=p_j+Delta/(2*(E-2))` for `j>=3`.
- **Two-saturation profile:** `c_1=c_2=p_L-Delta/4` and
  `c_j=p_j+3*Delta/(2*(E-2))` for `j>=3`.
- Use preregistered moderate batch sizes `T=(E-2)*{64,128,256}`. The target
  pair capacities are rational, but their exact denominators can be very
  large. For each `(E,K,T,profile)`, choose the nearest integer pair capacity
  to the displayed target such that `K*T-2*C_pair` is divisible by `E-2`;
  assign every tail expert the integer capacity
  `(K*T-2*C_pair)/(E-2)`. This preserves exact total capacity and equal tail
  capacities. Stop if the resulting integer profile violates any required
  strict saturation/under-capacity margin or `0<C_e<T`.
- For each cell, compute the world-target pressure actions numerically by
  solving the exact population Top-K inclusion equations; require residual
  at most `1e-8`. The action set for the controlled decision-value check is
  exactly these two target pressures. This restricted experiment is not
  presented as optimizing over all pressure actions.
- Draw 5,000 first-batch count vectors from the exact Gumbel-Top-K subset
  law, using a fixed seed derived from `(E,K,T)`. Generate world 1 by
  swapping the first two counts in each world-0 draw. This coupling gives
  common random numbers and makes the world symmetry exact.

## Primary measurements

For each `(E,K,T,capacity profile)`, record exact finite-batch Bayes
classification errors from the full `R` and `A` vectors using the verified
likelihood-ratio rule, exact expected next-batch overflow of each target
action, and the resulting optimal signal value gap inside the two-action
class. Also report the empirical paired classifier errors, admitted-vector
equality under the world-swap coupling, and the fraction for which the
mass-conservation decoder exactly reconstructs `R` from `A`.

Report the one-saturation finite-`T` Hoeffding decoder-failure upper bound
alongside observed reconstruction. For the two-saturation cells, report the
admitted-law coupling bound and requested classification bound from the
theorem, while clearly marking the `v_*` constant as implicit. Do not claim
that the controlled two-action gap is the unrestricted value `V_A-V_R`.

## Controls and failure rules

Check for every profile that `sum C=K*T`, all capacities are positive and
below `T`, `sum R=K*T`, `A=min(R,C)`, `sum J=sum(R-A)`, and world 1 is the
exact swap of world 0. The world-target risk matrix must have equal diagonal
entries, equal off-diagonal entries, and a strictly larger off-diagonal
entry. The no-clipping control `C_e=T` must satisfy `A=R` for every sampled
count vector. Exact Bayes-error formulas must agree with empirical paired
errors within Monte Carlo uncertainty. Retain all cells, including any
which fail the expected saturation pattern or predicted sign.

This experiment can validate the finite-family saturation-multiplicity
prediction. It cannot prove the theorem, remove the adaptive-testing
reduction, establish a hardware telemetry price, demonstrate trained-model
quality, or establish top-conference novelty by itself.

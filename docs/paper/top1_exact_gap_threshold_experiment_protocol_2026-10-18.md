# Protocol: finite-size check at the Top-1 all-policy certificate threshold

## Question

At batch sizes where the existing exact Top-1 theorem first certifies a
positive all-policy value gap, do paired synthetic observations follow the
theorem's requested/admitted signal predictions? The theorem and exact
finite-size certificate are fixed in
[`top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md`](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md).

## Locked design

- Family: the existing two-world Top-1 Gumbel / categorical family, with
  world-0 probabilities `(5/13, 4/13, 4/(13(E-2)),...)` and world 1 swapping
  the first two coordinates.
- Capacities: `C=(T/4,T/4,T/(2(E-2)),...)`, exact total `T`.
- Expert counts: `E={3,4,8}`.
- Batch sizes: for each `E`, the first admissible `T` at which the
  exact-classifier all-policy lower-bound diagnostic is positive, and twice
  that `T`. Thresholds come from the locked deterministic scan in
  `audit_top1_finite_batch_value_thresholds.py`; the scan uses every
  admissible batch size in order.
- Replications: 50,000 paired draws per cell, fixed seed `20261018+E+T`.
  Draw world 0 once and form its paired world-1 draw by swapping coordinates
  1 and 2. This is the theorem's exact coupling.
- Signals: full `R` and `A=min(R,C)`.
- Classifier: sign of the first-two-coordinate difference, with half loss on
  ties. Exact errors are computed from the binomial conditioning formula;
  Monte Carlo checks the calculation and records paired-signal equality.
- Action-cost check: exact next-batch expected overflow under the two
  world-target pressures is computed from binomial marginals. This gives
  exact two-action-class values, not unrestricted-pressure values.
- The theorem's all-policy finite-batch lower bound is reported from its
  exact inequality separately from the simulated two-action-class gap.

## Controls and exclusions

Every draw must satisfy request mass `T`, admission identity, exact world
swap, and exact capacity mass. The result reports Monte Carlo standard errors
and checks each classifier rate against its exact finite-binomial value.
There is no trained model, hardware-price measurement, or real-router claim.
The experiment does not estimate the unrestricted policy value; the
all-policy conclusion comes only from the theorem proof.

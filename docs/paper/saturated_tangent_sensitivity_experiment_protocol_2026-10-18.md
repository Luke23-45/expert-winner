# Controlled synthetic audit: saturated Top-K probability-transfer directions

## Research question

Audit the new corollary to the exact expected-admission Jacobian theorem:
when two or more experts are strictly overloaded, does a local probability
transfer supported only on those experts remain visible to requested mean
feedback while its admitted mean-feedback derivative is attenuated? The
experiment tests the directional inequality and its stated controls. It does
not test controller trajectories or policy value.

## Locked model and computation

- Four experts with iid standard-Gumbel affinities and hard Gumbel Top-K
  routing, `K in {1,2,3}`.
- Router inclusion probabilities are computed exactly by enumerating all
  `4!` Plackett-Luce rankings; no routing Monte Carlo is used.
- Each batch has `T in {160,320,640}` iid tokens.
- Admission is the canonical independent per-expert clipping rule
  `A_e=min(R_e,C_e)`.
- The expected feedback Jacobians are evaluated from the exact binomial
  identity. Independently, the full expected fields and directional
  derivatives are computed by central finite differences.
- Base logits are `(0.7,0.25,-0.2,-0.75)`. At each `K`, capacities for
  the two-saturated arm are chosen with an exact total `sum C=K*T`, reducing
  the first two capacity fractions by the same positive margin and adding
  that total slack to the remaining experts. The one-saturated control places
  all compensating slack outside expert 1. Capacity rounding uses the
  largest-remainder rule and preserves the integer total exactly.

## Registered arms and direction

1. **Two saturated:** choose `z=e_1-e_2`, supported on the two overloaded
   experts. Compute the unique zero-sum pressure tangent `v` solving
   `Dp(q)v=z`.
2. **One saturated control:** use the same transfer, with only expert 1
   overloaded and expert 2 below capacity. This checks the theorem's
   `m>=2` condition: the transfer is no longer supported entirely on
   saturated experts and should not be driven to zero response by the
   corollary.
3. **No-clipping control:** set every `C_e=T`, so every attenuation factor
   equals one and the admitted and requested directional derivatives must
   match.

For each cell report the pressure tangent norm, each `alpha_e`, the requested
and admitted directional derivative norms, their ratio, and analytic-versus-
finite-difference errors. The theorem predicts an exact upper bound on the
two-saturated response ratio by `max(alpha_1,alpha_2)`.

## Checks and interpretation

- Inclusion probabilities sum to `K`; exact-total clipped arms have
  `sum C=K*T`; all requested overload assignments are verified from the
  realized probability and capacity fractions.
- The computed pressure tangent satisfies `Dp v=z` and has zero-sum gauge.
- The request derivative equals `z/K` within numerical tolerance.
- Both full Jacobians and directional derivatives match central finite
  differences within `2e-6`.
- The primary response ratio is evaluated from the exact chain-rule
  directional vectors `P0 z/K` and `P0 diag(alpha) z/K`; finite differences
  independently audit those derivatives and are not used to resolve
  exponentially tiny ratios below numerical precision.
- Two-saturated cells satisfy the analytic attenuation upper bound; at each
  `K`, the response ratio decreases over the registered batch-size grid.
- No-clipping ratios equal one. The one-saturated control's ratio remains
  above `0.25` on the registered grid.

These are exact-expectation synthetic calculations with numerical derivative
checks, not sampled-run confidence intervals. Passing the audit supports only
the local derivative theorem under this Gumbel Top-K family. It does not
establish finite-law non-identifiability, an all-policy value gap, closed-loop
stability or instability, a hardware price, or a trained-model benefit.

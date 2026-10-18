# Controlled sparse Top-2 finite-weight audit: protocol

## Question

Does the helper-expert construction in the sparse Top-K theorem candidate
survive at finite weights in an `E=4,K=2` Gumbel router while retaining
canonical per-expert clipping?

## Locked plant

- Two worlds use Gumbel-Top-2 base weights `(100,2,1,1)` and `(100,1,2,1)`.
- Capacities are `C/T=(1/8,1/8,7/8,7/8)`, exact total `K=2`.
- At the initial state, experts 1, 2, and 4 should be clipped in both
  worlds; expert 3 is uncapped and has the same marginal law in both worlds.
- Use `T in {1600,6400,25600}` and 500 paired replicates per `T`, with seed
  `2026101702 + 100000*T_index + replicate`.
- Compute Top-2 subset probabilities by exact Plackett-Luce permutation
  enumeration. Couple the first-batch worlds by sharing the count of tokens
  routed to expert 3, then sample each world conditionally on that indicator.
  This makes the observed unsaturated coordinate exactly shared under the
  coupling while preserving each world’s marginal count law.

## Actions and metrics

For each world, solve for a pressure whose population inclusion vector equals
`C/T`; report the residual. The requested classifier chooses world 0 when
`R_1/T` exceeds the midpoint of the two exact initial means, and world 1
otherwise. The admitted diagnostic uses the fixed world-0 target pressure;
it is not labeled an optimal admitted policy. Also report the no-feedback
action.

Primary diagnostics: admitted-vector equality under the coupling, equality
with no clipping, request-classifier error, exact initial and target
inclusion probabilities, exact population overflow of the registered
actions, and all mass/clipping invariants. No seeds or draws are excluded.

## Interpretation boundary

This audit checks one finite-weight member of the broader sparse Top-K
construction. It does not prove the family theorem, globally optimize the
common-action risk, or establish multi-round performance, telemetry cost,
training benefit, or benchmark separation.

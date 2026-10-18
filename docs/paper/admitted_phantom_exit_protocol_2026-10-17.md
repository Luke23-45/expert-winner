# Controlled experiment: exit from global saturation under proportional admitted feedback

**Status:** protocol fixed before the run. This study uses the canonical
proportional gauge-pressure controller `(A)` in `formal_core.md`; it is not
the separate sign-bias controller used in the earlier capacity sweep.

## Question

When the canonical admitted-feedback controller starts globally saturated,
heterogeneous capacity or a non-uniform target can give it a nonzero
constant gauge direction even though it cannot observe current excess demand.
Does the fixed Top-K score arrangement then force a finite exit from global
saturation, and does the exact arrangement-based upper bound predict that
exit?

## Theorem being checked

Use fixed affinities, `delta=0`, `E>K`, positive capacities, and a nonzero
phantom direction

```
v = P_0(C/(K*T) - mu).
```

Assume the `K` smallest coordinates of `v` are separated from the rest by a
strict gap. While globally saturated, `(A)` has constant feedback
`C/(K*T)-mu`; in score-penalty coordinates `p=gamma*q`, its gauge class
therefore follows `p_n = p_0 + n*alpha*v`, where `alpha=eta*gamma^2`.
After a finite, explicit number `N_sep` of updates, every token ranks the
same `K` minimum-slope experts above every other expert. Since all
capacities are positive and `K<E`, at least one expert outside that set has
zero requests, so the controller must have left global saturation by
`N_sep`.

For each token `t`, minimum-slope expert `i`, and outside expert `j`, define

```
theta[t,i,j] = (p_i(0)-p_j(0) - (a[t,i]-a[t,j]))
               / (alpha*(v_j-v_i)).
N_sep = max(0, 1 + max_{t,i,j} floor(theta[t,i,j])).
```

At every integer `n >= N_sep`, each such pair has a strict score ordering
`s[t,i](n) > s[t,j](n)`. The experiment checks the predicted upper bound
and equality of the simulated `(A)` state to the constant-feedback
open-loop state through the first unsaturated state. It does not test
post-exit convergence.

## Fixed synthetic plant and paired arms

- `E=4`, `K=2`, `T=128`; capacities `C=(40,42,43,44)`; target
  `mu=(0.4,0.3,0.2,0.1)`; `eta=0.1`, `gamma=1`, `delta=0`.
- Fixed ring-pair token multiplicities `(40,24,32,32)`, which give initial
  requested counts `(72,64,56,64)` and put every expert at or above its
  capacity.
- Twenty paired affinity perturbations, seeds `0..19`. Every run uses the
  exact same affinity matrix across controller arms. The perturbation is
  rational, deterministic, and too small to change the initial Top-2 pairs.
- Arms: canonical proportional admitted feedback `(A)`, requested feedback
  `(R)`, and no feedback. All start at `q=0`; ties use lower expert index.
- Run each arm through at least `max(120,N_sep+10)` routing states.

## Exact controls and primary endpoint

The primary endpoint is the first state index `tau_A` at which the `(A)` arm
is no longer globally saturated. Required checks:

1. Initial counts, total requested mass, per-expert clipping, and overflow
   accounting are exact.
2. The direction has a strict `K`/`K+1` slope gap and all capacities
   outside the asymptotic Top-K set are positive.
3. The exact open-loop route calculation yields `tau_A <= N_sep`.
4. The simulated `(A)` pressure and request counts match that open-loop
   path at every state through `tau_A`.
5. No-feedback remains at its initial globally saturated state; this is a
   negative control, not a predicted advantage claim.
6. Requested-feedback results are paired descriptive comparisons only; no
   ordering of controller quality is preregistered.

Report each seed's `N_sep`, `tau_A`, first route-change state, requested
feedback exit state, request/admitted vectors, and per-step overflow. Do not
combine these into one score and do not treat the 20 perturbations as a
population sample.

## Interpretation boundary

This experiment tests a finite-time consequence of the existing canonical
`(A)` dynamics under an explicitly stated heterogeneous-capacity/non-uniform
target regime. It does not prove a general admitted-feedback performance
gap, establish a benefit on model quality, validate the professor report's
sign-bias controller claim, or resolve the adaptive-testing reduction.
The uniform-capacity/uniform-target freeze remains the `v=0` boundary case.

## Reproduction

Run `python scripts/run_admitted_saturation_exit.py` from the exploration
worktree. Results are written to `results/admitted_saturation_exit/`.

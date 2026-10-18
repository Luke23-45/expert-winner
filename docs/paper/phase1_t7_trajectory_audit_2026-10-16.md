# T7 trajectory candidate: consistency and proof-obligation audit

**Date:** 2026-10-16  
**Branch:** `feat/research-censored-feedback`  
**Status:** Audit of a proposed construction; no new lower bound is claimed.

## Finding

The proposed T7 paired-world argument in `phase1_h3_direction.md` §3 is
internally inconsistent as written. It asks for identical admitted histories
(`A_t`, with global saturation) while claiming that overflow strictly
increases along the same hidden trajectory. Under the experiment's fixed
token mass, the overflow is exactly determined by the admitted vector, so
these two claims cannot hold together.

This does **not** rule out a value-of-information gap. An informed policy can
choose a world-dependent pressure trajectory, while an admitted policy must
choose actions from its observation history. The finding rules out only the
proposed explanation that overflow compounds *during a common, identical-A
history*.

## Exact identities

For every round, `sum_e R_e = K T`, `A_e = min(R_e, C_e)`, and
`J_e = R_e - A_e`. Therefore

\[
O_t := \sum_e J_{t,e}
    = K T - \sum_e A_{t,e}.
\]

Consequently, if two worlds produce the same admitted vector at round `t`,
they have the same total overflow that round. If their admitted histories are
identical through a prefix, their cumulative overflow over that prefix is
identical as well. This is an observation-cost identity, not a probabilistic
or asymptotic claim.

Under global saturation, `A_t = C`, so

\[
O_t = K T - \sum_e C_e,
\]

which is constant for every round in which global saturation holds. A strict
increase in overflow implies that the admitted vector has changed (in
particular, global saturation has ceased if the prior vector was `C`). Thus
the observation that can reveal a change and the claimed cost increase occur
at the same transition; the increase cannot be hidden inside an unchanged
`A_t=C` observation.

## What T7 does and does not establish

The T7 result in `formal_core.md` is a trajectory statement for the specific
`(A₀)` update under its stated saturation assumptions. Its pressure direction
can move requests toward lower-capacity experts; the empirical v3 runs show
overflow rising after the trajectory leaves global saturation. That is useful
mechanistic evidence about `(A₀)`.

It is not a lower bound against every causal admitted policy. Such a policy
may select a different pressure update, probe a candidate action, observe the
resulting `A`, and then change course. Any G3 theorem must account for this
information-acquisition option and for the pressure-state transition
constraint. A proof about `(A₀)` alone cannot establish that no admitted
policy avoids its trajectory.

## Corrected proof target

Keep T7 as a candidate mechanism or a fixed-controller failure result. Do not
claim that its overflow increase is hidden while `A_t` stays identical. To
obtain a signal-value theorem, formalize a finite-horizon decision problem
with:

1. a specified family/prior of persistent affinity worlds and a common
   initial pressure;
2. the full causal admitted-policy class, including randomized policies;
3. legal pressure increments and their induced Top-K outcome map;
4. per-round cost `K T - sum(A_t)` and the exact admitted observation;
5. the requested-information comparator under the same plant and action
   constraints; and
6. a lower bound that includes every probing strategy, plus a reduction
   comparison against state-constrained adaptive testing.

The relevant gap, if one exists, must come from the cost/information tradeoff:
world-dependent informed actions can have lower cost, while every admitted
policy must either pay for informative actions or accept a quantifiable
decision loss. It cannot come from assigning different overflow costs to
worlds with the same admitted vector.

## Decision

Revise `phase1_h3_direction.md` §3 to mark the original paired-world
compounding story as invalid as written. Preserve the T7 mechanism as a
fixed-controller result. The next mathematical task is a policy-class value
analysis that charges probing explicitly and proves a bound against all
causal admitted policies; run no new sweep until that statement survives the
reduction attack.

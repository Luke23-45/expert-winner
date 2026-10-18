# Exact capacity-phase experiment for the P2f Top-2 family

**Status:** completed exact-rational parameter sweep with cycle certificates;
capacities 11--13 additionally have a continuous-gain interval audit.
This extends the existing P2f family by varying only its uniform per-expert
capacity. It is not a new router model and is not trained-model evidence.

## Question

Does the admitted-feedback advantage in P2f persist as capacity changes, or
does it occur only at the theorem's `C=10m` setting? This is the direct
capacity-regime check suggested by professor report 1, applied to the already
defined Top-2 signed-bias plant.

## Locked plant and controller

Use the same 20-row base affinity multiset as
[`top2_signed_bias_separation_theorem_2026-10-17.md`](top2_signed_bias_separation_theorem_2026-10-17.md):
one row `(0,5,11/10)`, ten rows `(0,101,100)`, and nine rows
`(2,6/5,0)`. Set `E=3`, `K=2`, `T=20`, `b_0=0`, and vary only the uniform
per-expert capacity `C` over every integer from 1 to 19. The gains are the
three exact rationals `9/40`, `6/25`, and `1/4`, all inside the proved P2f
interval `(1/5,11/40)`.

For `L` equal to requested counts `R`, admitted counts `A=min(R,C)`, or no
feedback, use

```text
u_e = sign(mean(L) - L_e)
b_next = P_0(b + alpha*u)
scores = affinity + b
```

Top-2 routing uses lower expert index to resolve exact score ties. The code
therefore omits the *higher* index when the two lowest scores tie. All
arithmetic in the audit is exact (`fractions.Fraction` and integer counts).
The source script is
[`audit_p2f_capacity_phase.py`](../../scripts/audit_p2f_capacity_phase.py);
its machine-readable output is
[`capacity_phase_audit.json`](../../results/top2_signed_bias_separation/capacity_phase_audit.json).

## Cycle certificate and horizon scope

For each of 19 capacities, 3 gains, and 3 feedback arms (171 exact
trajectories), the audit stores the gauge-centered bias state as a tuple of
rational numbers. A repeated state proves the entire future trajectory
repeats, because affinities, tie-breaking, admission, and feedback are
deterministic. Every cell entered an exact state cycle within 2,000 updates;
the longest transient is 446 batches and every eventual period is 1 or 2.
The audit derives cumulative cost at arbitrary horizons from each exact
prefix and cycle. It also combines the three cycle periods to give exact
all-horizon cost-gap profiles, including the average gap added per joint
period. This certifies all horizons for the listed finite capacity/gain grid,
not for every real gain in the P2f interval.

Repeating each row `m` times and scaling capacity to `mC` leaves sign
feedback and bias paths unchanged; counts and every overflow total multiply
by `m`. Thus each exact cell represents that replication family as well.

## Exact eventual mean overflow per batch

The table gives the exact mean overflow over the eventual cycle. The values
are identical for all three gains in the registered grid.

| `C` | Admitted signal | Requested signal | No feedback | Per-batch capacity lower bound |
|---:|---:|---:|---:|---:|
| 1 | 37 | 37 | 37 | 37 |
| 2 | 34 | 69/2 | 34 | 34 |
| 3 | 31 | 32 | 31 | 31 |
| 4 | 28 | 59/2 | 28 | 28 |
| 5 | 25 | 27 | 25 | 25 |
| 6 | 22 | 49/2 | 22 | 22 |
| 7 | 19 | 22 | 19 | 19 |
| 8 | 16 | 39/2 | 16 | 16 |
| 9 | 13 | 17 | 13 | 13 |
| 10 | 10 | 29/2 | 11 | 10 |
| 11 | 13 | 13 | 9 | 7 |
| 12 | 23/2 | 23/2 | 8 | 4 |
| 13 | 10 | 10 | 7 | 1 |
| 14 | 17/2 | 17/2 | 6 | 0 |
| 15 | 7 | 7 | 5 | 0 |
| 16 | 11/2 | 11/2 | 4 | 0 |
| 17 | 4 | 4 | 3 | 0 |
| 18 | 5/2 | 5/2 | 2 | 0 |
| 19 | 1 | 1 | 1 | 0 |

Here the per-batch lower bound is `max(0, 40-3C)`. At `C=1,...,9`,
admitted feedback and no feedback both attain this lower bound on every
batch. At `C=10`, admitted feedback attains the lower bound while the other
two do not. At `C=11,...,18`, both feedback signals have strictly higher
eventual mean overflow than no feedback in this plant. At `C=19`, all three
have the same eventual mean.

## Signal comparisons across all horizons

- **`C=10`:** the existing analytic P2f theorem remains the strong result:
  for every `alpha` in `(1/5,11/40)`, admitted feedback is strictly better
  than requested feedback and no feedback at every horizon `H>=4`.
- **`C=1`:** all three costs agree at every horizon.
- **`C=2,...,9`:** admitted feedback and no feedback have identical
  all-horizon overflow. For the three audited gains, requested feedback has
  a strictly higher cumulative overflow after a finite threshold (the
  threshold is recorded per cell in the JSON).
- **`C=11,...,13` at the three registered gains:** admitted and requested
  feedback have equal eventual average overflow, but their cumulative-cost
  difference changes sign over the trajectory. Neither signal is better at
  every horizon. Both have higher eventual average overflow than no feedback.
- **`C=14,...,19`:** admitted and requested feedback produce identical full
  request paths for each of the three audited gains, so their cumulative
  overflow is identical at every horizon. For `C=14,...,18`, both have
  higher eventual average overflow than no feedback; at `C=19` all three
  cycle means agree.

The all-horizon distinctions above are derived from exact state cycles, not
from extrapolating a finite 100-step window. The open gain interval theorem
at `C=10` remains an analytic result; the three-gain capacity grid for other
capacities is extended only at `C=11,...,13` by the interval audit below.

## Continuous-gain audit at the transition capacities

The three-gain grid above could miss behavior at other gains. To check that,
[`audit_p2f_continuous_gain.py`](../../scripts/audit_p2f_continuous_gain.py)
partitions the entire open interval `alpha in (1/5, 11/40)` at every exact
pairwise score crossing encountered by the closed loop. It separately
simulates each crossing gain with the declared deterministic tie rule. On
each resulting open cell, the route counts and feedback state transitions
are constant; exact repeated states certify the eventual cycle. The audit
does not merge cells across crossing points.

| Capacity | Signal | Open gain cells (cycle-mean overflow) | Isolated crossing gains (cycle-mean overflow) | Max transient / period |
|---:|---|---|---|---:|
| 11 | admitted | 69 cells at 13; 50 at 43/3 | 71 points at 13; 49 at 43/3 | 252 / 3 |
| 11 | requested | 119 cells at 13 | 120 points at 13 | 501 / 2 |
| 12 | admitted | 134 cells at 23/2; 8 at 61/5 | 135 points at 23/2; 8 at 61/5 | 377 / 5 |
| 12 | requested | 119 cells at 23/2 | 120 points at 23/2 | 501 / 2 |
| 13 | admitted | 121 cells at 10 | 122 points at 10 | 498 / 2 |
| 13 | requested | 119 cells at 10 | 120 points at 10 | 501 / 2 |

The point counts include the two interval endpoints for completeness; the
theorem domain is open. For no feedback, the route map is fixed and its exact
mean overflow is 9, 8, and 7 at capacities 11, 12, and 13, respectively.
Therefore, throughout the audited gain interval, admitted feedback's
eventual mean is never lower than requested feedback's at `C=11` or `C=12`;
they tie on some cells and admitted feedback is strictly worse on the rest.
At `C=13`, their means agree throughout. Both feedback signals are strictly
worse than no feedback in eventual mean at all three capacities.

This exact partition refines the three-point phase map but remains a
single-affinity-family result. It explains some gain dependence around the
`C=10` theorem and provides an exact counterexample to any claim that
admitted feedback is generally preferable at nearby capacities. It does
not establish a capacity threshold for other affinity matrices or resolve
the class-level benchmark reduction.

Machine-readable certificates are stored as
`results/top2_signed_bias_separation/continuous_gain_C{11,12,13}_{admitted,requested}.json`.
The capacity-11 admitted result is
`continuous_gain_audit.json`.

## Interpretation for the professor's proposal

This is evidence against a capacity-independent story that requested counts
always improve control, or that admitted-count bias always winds up. In this
single existing Top-2 family, the effect changes sharply with capacity:
the `C=10` admitted-feedback advantage is exact and all-horizon after `H=3`,
adjacent higher capacities lose that strict all-horizon ranking, and at
`C>=14` the two sensors become trajectory-equivalent for the audited gains.
At `C=11,...,18`, feedback can even raise long-run overflow relative to doing
nothing.

This does not give a general capacity threshold for other affinity matrices,
prove a Top-K-specific advantage over the independent polyhedral testing
benchmark, estimate production prevalence, measure requested-telemetry cost,
or establish training-quality benefit. It strengthens the existing mechanism
claim and gives a concrete falsifier for any proposed broader theorem: that
theorem must explain the capacity transition, finite-horizon reversals, and
the no-feedback outcomes without assuming a universal sensor ranking.

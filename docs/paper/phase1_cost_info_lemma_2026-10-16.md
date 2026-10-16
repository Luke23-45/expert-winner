# Cost-versus-information lemma (E=3): finite-partition enumeration

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status:** the score-line arrangement script enumerates 13 pressure-outcome
signatures, including tie strata. Its floating-point finite-case check
supports the lemma for this parameter instance; the paper still needs a
concise hand-checkable case proof.

---

## 1. What the partition reveals

Enumerating all 13 distinct (A¹,A²) signatures over the full (x,y)
plane—including boundary-only outcomes under the lower-index tie rule—
with [`scripts/analyze_e3_exact_partition.py`](../../scripts/analyze_e3_exact_partition.py)
gives the cost pairs summarized below. The script tests every open
winner assignment by a strict-margin linear program, then samples every
vertex and one-dimensional stratum of the exact score-line arrangement.

| informative? | E[c] | (c₁,c₂) | interpretation |
|---|---|---|---|
| No | 20.00 | (20,20) | do nothing; learn nothing |
| Yes | 20.00 | (40,0) or (0,40) | probe; learn perfectly |
| Yes | 40.00 | (40,40) | probe both; learn, but costly |
| No | 40.00 | (40,40) | uninformative but costly |
| Yes | 45.00 | (70,20) or (20,70) | partial probe |
| Yes | 65.00 | (40,90) or (90,40) | bad probe |
| No | 70–90 | (70,70) etc. | very costly, uninformative |

**Finding 1.** min_{(x,y)} E[c] = E_S = 20, attained both by the
uninformative "do nothing" and by the informative probe. The
no-hedging lower bound E[c] ≥ E_S/4 = 5 is **not tight**; the true
minimum is 4× larger.

**Finding 2.** There is **no pressure that is both cheap
(E[c] < E_S) and informative**. Every informative pressure has
E[c] ≥ E_S, with max(c₁,c₂) ≥ 2E_S.

**Finding 3.** The cheapest informative pressures are exactly the
single-world sweet spots: (c₁,c₂) = (2E_S, 0) or (0, 2E_S). They
reveal the world perfectly (A¹ ≠ A²) but cost 2E_S in the wrong
world.

---

## 2. Lemma statement (cost versus information, E=3)

*Lemma.* For the E=3 construction with equal prior, for every
pressure (x,y):
- (a) If A¹(x,y) = A²(x,y) (uninformative), then c₁ = c₂ ≥ E_S and
  the posterior remains (1/2, 1/2).
- (b) If A¹(x,y) ≠ A²(x,y) (informative), then E[c] ≥ E_S and
  max(c₁,c₂) ≥ 2E_S, and the posterior collapses to a point mass.

*Verification of (a) and (b).* The exhaustive arrangement enumerator
checks each of the 13 signatures and enforces the stated inequalities.
This is a reproducible finite-case verification, not a replacement for
the paper proof: the final theorem should include the score inequalities
or a compact exact table that lets a reader check all cells without
trusting code.

*Corollary.* The "cost of one bit of information" (going from
1 bit of uncertainty to 0) is at least E_S in expectation. There
are no cheap informative actions.

---

## 3. Why this does not yet resolve G3

The lemma gives a **one-round** cost-of-information bound. For the
**cumulative** problem with static worlds:
- Round 0: E_S sunk.
- Round 1: pay ≥ E_S (either probe and learn, or don't probe and
  stay blind).
- After an informative pressure is reached, the static world is known and
  that world's zero-overflow action can be held. This ignores the travel
  cost; it applies only when the required action is reachable.

In the one-step-reachable (or unconstrained-action) comparison, the
admitted policy probes once: its total is $2E_S=40$, while the requested
policy pays only the initial $E_S=20$. The resulting cumulative gap is
$E_S$, a one-time learning cost rather than a horizon-growing gap. With the
small-step reach constraint in the companion instance, travel changes the
values: the computer-assisted calculation gives 60 versus 80 for $H\ge4$.
That instance has normalized gap $20/(HKT)$, which also decays as $H$ grows.

**For a horizon-growing gap, one of the following must hold:**
1. The world **changes** over time (Markov switching) — out of
   scope for the current static-world Bellman recursion; requires
   extending (DP-A) with a transition kernel.
2. The **(Reach) constraint binds**: with small B, the controller
   cannot jump to the sweet spot in one step even after learning.
   The number of steps needed to reach a fixed distant pressure grows as B
   shrinks. This is a state-constrained control effect; related constrained
   adaptive-sensing work exists, so MoE-specific novelty remains unproven
   until the exact reduction is completed.
3. The **information decays**: observations become less informative
   over time (not present in the static model).

Direction 2 is the most developed within the current formalization, but its
novelty is not established by the current citations. Constrained adaptive
sensing already studies adaptivity under physically constrained measurement
actions, and finite-horizon POMDP theory already supplies a general
belief-state dynamic-programming framework. The next comparison must state
the exact reduction and identify whether Top-K score cells, clipping, or
the gauge-induced reach metric yield a theorem those abstractions do not
preserve ([Davenport et al., *Constrained adaptive sensing*](https://doi.org/10.1109/TSP.2016.2597130); [Smallwood and Sondik, finite-horizon POMDP control](https://doi.org/10.1287/opre.21.5.1071)).

---

## 4. Relation to the small-step finite-horizon result

The corrected finite-horizon analysis for $B=2.65$ is in
[`phase1_g3_steering_2026-10-16.md`](phase1_g3_steering_2026-10-16.md).
For that instance, $V_R(H)=60$ and $V_A(H)=80$ for $H\ge4$.
The gap is constant in $H$, so it does not establish a horizon-growing
lower bound. A parameterized $B\to0$ result remains open and must optimize
over all causal policies; one-world shortest paths do not establish it.

No large experiment sweep was run. The arrangement check is a deterministic
floating-point finite-case verification, and the companion G3 note gives a
value argument whose
score-cell inequalities still need a hand-checkable proof.

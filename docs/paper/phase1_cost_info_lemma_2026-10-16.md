# Cost-versus-information lemma (E=3): computational characterization

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status:** computational verification + lemma statement; analytic proof
of the strengthened bound is future work.

---

## 1. What the partition reveals

Enumerating all 13 distinct (A¹,A²) cells over the (x,y) pressure
plane (script: `scripts/analyze_e3_partition.py`) gives:

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

*Proof of (a).* Verified computationally over the full partition;
analytic proof by score-cell case analysis is pending.
*Proof of (b).* Same; the (2E_S, 0) structure follows from the
sweet-spot characterization.

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
- Rounds 2+: if probed, cost 0; else ≥ E_S per round.

The optimal policy probes once: total = 2E_S = 40. This is a
**one-time** learning cost, not horizon-growing. The normalized gap
E_S/(4HKT) still decays with H.

**For a horizon-growing gap, one of the following must hold:**
1. The world **changes** over time (Markov switching) — out of
   scope for the current static-world Bellman recursion; requires
   extending (DP-A) with a transition kernel.
2. The **(Reach) constraint binds**: with small B, the controller
   cannot jump to the sweet spot in one step even after learning.
   Each steering step incurs overflow, and the number of steps
   grows as B shrinks. This is MoE-specific (pressure dynamics)
   and not covered by generic adaptive testing.
3. The **information decays**: observations become less informative
   over time (not present in the static model).

Direction 2 is the most promising within the current formalization:
it uses the (Reach) constraint essentially, which neither Golovin
et al. nor Sabato et al. covers.

---

## 4. Next step

Fix small B (violating the §5 assumption B ≥ √2M/(ηγ²)) and
recompute the reachable cells from q₀=0. Characterize the
minimum-step steering cost to each sweet spot, and incorporate it
into (DP-A). If the steering cost is ω(1) as B→0, this yields a
horizon-growing gap driven by pressure dynamics.

No experiments were run; all claims are computational verifications
of the exact partition.

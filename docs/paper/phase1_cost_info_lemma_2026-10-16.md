# Cost-versus-information lemma (E=3): exact score-cell proof

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status:** the fixed-instance lemma below has an exact finite case table;
the parameterized G3 theorem and prior-art reduction remain open.

---

## 1. Model and exact winner regions

Use $C=50$, $E_S=20$, $C_{sink}=30$, $m=1$, $M=3$, and equal prior on
two static worlds. For a pressure $(x,y)$, the four token types have score
vectors

$$
L_1=(1-x,-3-y,0),\quad H_1=(3-x,-3-y,0),\\
L_2=(-3-x,1-y,0),\quad H_2=(-3-x,3-y,0).
$$

Experts are indexed $1,2,3$; ties go to the lower index. The requests are
$R^1=C e_{d_{1H}}+E_S e_{d_{1L}}+C e_{d_{2L}}$ and
$R^2=C e_{d_{1L}}+C e_{d_{2H}}+E_S e_{d_{2L}}$, where $d$ is the winning
expert. Admission is $A^w_e=\min(R^w_e,C_e)$ for capacities
$(C,C,C_{sink})$, and overflow is $c_w=\sum_e(R^w_e-A^w_e)$.

The exact winner conditions (including tie priority) are:

| Token | Winner 1 | Winner 2 | Winner 3 |
|---|---|---|---|
| $L_1$ | $x\le1$, $x-y\le4$ | $y\le-3$, $x-y>4$ | $x>1$, $y>-3$ |
| $H_1$ | $x\le3$, $x-y\le6$ | $y\le-3$, $x-y>6$ | $x>3$, $y>-3$ |
| $L_2$ | $x\le-3$, $x-y\le-4$ | $y\le1$, $x-y>-4$ | $x>-3$, $y>1$ |
| $H_2$ | $x\le-3$, $x-y\le-6$ | $y\le3$, $x-y>-6$ | $x>-3$, $y>3$ |

These conditions partition each token's choices. Their score-equality lines
are exactly $x\in\{-3,1,3\}$, $y\in\{-3,1,3\}$, and
$x-y\in\{-6,-4,4,6\}$. Intersecting the four token conditions gives the
following compatibility table. Here row labels encode $(d_{1L},d_{1H})$;
column labels encode $(d_{2L},d_{2H})$. A check means the four inequalities
have a nonempty intersection; blank entries are inconsistent.

| $(d_{1L},d_{1H})$ | $a=(1,1)$ | $b=(1,2)$ | $c=(2,2)$ | $d=(3,2)$ | $e=(3,3)$ |
|---|---:|---:|---:|---:|---:|
| $A=(1,1)$ | ✓ | ✓ | ✓ | ✓ | ✓ |
| $B=(2,1)$ |  |  | ✓ |  |  |
| $C=(2,2)$ |  |  | ✓ |  |  |
| $D=(3,1)$ |  |  | ✓ | ✓ | ✓ |
| $E=(3,3)$ |  |  | ✓ | ✓ | ✓ |

Thus there are 13 possible winner patterns. The exact rational checker
[`analyze_e3_exact_partition.py`](../../scripts/analyze_e3_exact_partition.py)
independently decomposes all ten lines into their 25 vertices, open line
segments, and open 2-D cells. It verifies these 13 patterns and checks the
costs using integer capacities and exact rational witnesses. The full
outcome table is below; each witness certifies that its row is attainable.

## 2. Complete outcome and cost table

$A^1,A^2$ are admitted-count vectors; $(c_1,c_2)$ are the corresponding
overflows. A signal is informative exactly when $A^1\ne A^2$.

| $(d_{1L},d_{1H},d_{2L},d_{2H})$ | Rational witness $(x,y)$ | $A^1$; $c_1$ | $A^2$; $c_2$ |
|---|---|---|---|
| $(1,1,1,1)$ | $(-6,1)$ | $(50,0,0)$; 70 | $(50,0,0)$; 70 |
| $(1,1,1,2)$ | $(-4,3/2)$ | $(50,0,0)$; 70 | $(50,50,0)$; 20 |
| $(1,1,2,2)$ | $(-5,-3)$ | $(50,50,0)$; 20 | $(50,50,0)$; 20 |
| $(1,1,3,2)$ | $(-2,5/2)$ | $(50,0,30)$; 40 | $(50,50,20)$; 0 |
| $(1,1,3,3)$ | $(0,5)$ | $(50,0,30)$; 40 | $(50,0,30)$; 40 |
| $(2,1,2,2)$ | $(-10,-15)$ | $(50,50,0)$; 20 | $(0,50,0)$; 70 |
| $(2,2,2,2)$ | $(1,-6)$ | $(0,50,0)$; 70 | $(0,50,0)$; 70 |
| $(3,1,2,2)$ | $(3,1)$ | $(50,50,20)$; 0 | $(0,50,30)$; 40 |
| $(3,1,3,2)$ | $(2,2)$ | $(50,0,30)$; 40 | $(0,50,30)$; 40 |
| $(3,1,3,3)$ | $(2,9/2)$ | $(50,0,30)$; 40 | $(0,0,30)$; 90 |
| $(3,3,2,2)$ | $(4,1/2)$ | $(0,50,30)$; 40 | $(0,50,30)$; 40 |
| $(3,3,3,2)$ | $(6,5/2)$ | $(0,0,30)$; 90 | $(0,50,30)$; 40 |
| $(3,3,3,3)$ | $(4,9)$ | $(0,0,30)$; 90 | $(0,0,30)$; 90 |

The table proves the following for **every** pressure:

1. If the admitted observation is uninformative, $A^1=A^2$ and
   $c_1=c_2\ge E_S$.
2. If it is informative, $(c_1+c_2)/2\ge E_S$ and
   $\max(c_1,c_2)\ge2E_S$.
3. Each world’s overflow is either zero or at least $E_S$.

Under equal prior, an informative observation distinguishes the two static
worlds exactly, since the observation is deterministic and the two possible
admitted vectors differ. Therefore the expected stage cost is at least
$E_S$ whenever the pressure is informative; there is no cheaper informative
action. The smallest informative cost pairs are $(2E_S,0)$ and $(0,2E_S)$.

*Proof status.* The winner inequalities and compatibility table provide a
short manual route to verify completeness. The script is an exact-arithmetic
cross-check of the arrangement and tie strata, not the source of the claim.
A paper proof should retain the inequalities and table (or an equivalent
appendix), rather than cite the script as proof.

*Corollary.* In this instance, acquiring the one bit that identifies the
world costs at least $E_S$ in expected stage overflow. This is a fixed-instance
cost-information statement, not a general lower bound for censored feedback.

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
values: the exact fixed-instance calculation gives 60 versus 80 for $H\ge4$.
That instance has normalized gap $20/(HKT)$, which also decays as $H$ grows.

**Candidate mechanisms to investigate for a horizon-growing gap:**
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

No large experiment sweep was run. The arrangement checker uses exact
rational arithmetic; the companion G3 value argument is derived from the
explicit score-cell table and exact reach calculations.

# Phase 1 reduction audit: paired-world lower bound

**Date:** 2026-10-16
**Branch:** `feat/research-censored-feedback`
**Question:** Does the current \(H=2\) overflow-gap theorem contain a lower-bound mechanism beyond censored decision theory, in particular Kumar and Mouchtaki's censored newsvendor?
**Verdict:** The theorem's value-gap argument has an explicit reduction to a two-point censored newsvendor instance. The Top-1/capacity plant realizes the loss table, but the current proof uses no non-reducible dynamic or gauge consequence. Under the stop rule in `conference_roadmap.md` §3, do not position this theorem as the Phase 1 novelty or conference centerpiece.

## 1. Primary-source scope checked

Kumar and Mouchtaki model an offline data-driven inventory decision. Historical
sales are \(S_i^{(k)}=\min(D_i^{(k)},x_k)\), together with the uncensored/stockout
indicator, and a policy maps that history to a scalar future inventory order.
The performance measure is worst-case expected regret against the optimal
expected newsvendor cost under the unknown demand distribution. Their paper
explicitly studies non-identifiability from censored histories and targeted
uncensored observations. See the [arXiv paper, v2 (11 Oct 2026)](https://arxiv.org/abs/2602.16842),
especially its model and regret definition in §2 and its discussion of
indistinguishable unobserved tails in §1.1.

This is not a claim that their paper states the MoE theorem or analyzes MoE
routing. The reduction below identifies the exact information/value-gap
argument shared by the two settings.

## 2. The MoE theorem after removing sunk cost

Let \(f_0(q)=F_\omega(q)\) and \(f_1(q)=F_{\omega'}(q)\) be the Round-1
overflow at a common pressure \(q\). The current Lemma 4 proves

\[
f_0(q)+f_1(q)\ge 40 \quad\text{for every }q\in\mathcal Q.
\]

There are also realizable actions with cost pairs \((0,40)\) and \((40,0)\):
pressure the excess expert in its world-specific sweet spot. The neutral action
has pair \((20,20)\). The Round-0 overflow is 20 in each world, independent of
the action, so it is sunk and cancels in the value difference. Thus the
un-normalized one-decision game after Round 0 has a blind value of 20 and a
requested-informed value of 0. Dividing that gap by the draft's full-horizon
normalizer \(HKT=240\) gives \(1/12\).

## 3. Explicit reduction to a censored newsvendor

Construct a newsvendor with one historical inventory level \(x=1/4\), one
historical demand sample, equal overage and underage costs \(c_o=c_u=80\), and
two possible demand distributions:

| Hidden environment | Future demand distribution | Historical observation |
|---|---|---|
| \(F_0\) | point mass at \(D_0=1/2\) | \(S=1/4\), uncensored flag \(1\{D\le x\}=0\) |
| \(F_1\) | point mass at \(D_1=1\) | \(S=1/4\), uncensored flag \(1\{D\le x\}=0\) |

Both historical records are identical, including the stockout indicator. The
clairvoyant order is \(D_i\) in environment \(F_i\), with zero regret.
Parameterize any order between the demands by

\[
a(\alpha)=D_0+\alpha(D_1-D_0)=\tfrac12+\tfrac12\alpha,
\qquad 0\le\alpha\le1.
\]

Its regret pair is exactly

\[
(R(a(\alpha),F_0),R(a(\alpha),F_1))
= (40\alpha,\,40(1-\alpha)).
\]

Under the equal prior on \(F_0,F_1\), every such order has average regret 20.
The histories are identical, so a policy cannot select a different order in
the two worlds. For every policy, its worst-case regret over all distributions
is at least its worst-case regret over this pair, which is at least the
pair-average 20. The equal-prior policy attains 20, so the restricted pair
game's minimax and Bayes values are exactly 20. Revealing which point-mass
distribution is present reduces regret to zero. Rescaling both newsvendor
cost coefficients scales all regrets and does not change this information
argument.

The mapping also covers every pressure action in the MoE proof, not just the
three illustrative actions. Given its loss pair \((f_0(q),f_1(q))\), define

\[
\alpha(q)=\max\!\left\{0,1-\frac{f_1(q)}{40}\right\}.
\]

Nonnegative losses and \(f_0(q)+f_1(q)\ge40\) imply

\[
40\alpha(q)\le f_0(q),\qquad
40(1-\alpha(q))\le f_1(q).
\]

Thus the two-point newsvendor regret pair is componentwise no larger than the
MoE overflow pair for every common admitted-policy action. For any order
\(a<1/2\), the equal-prior regret is greater than 20; for orders in
\([1/2,1]\), it is exactly 20. Thus 20 is the minimum over all allowed
orders. Conversely, the MoE sweet-spot actions realize the two newsvendor
endpoint loss pairs, and a neutral action realizes the equal-regret value. The lower-bound value is the
same two-state value-of-information obstruction, expressed in overflow units.

This is an explicit reduction of the **value-gap argument** to a simple
censored newsvendor instance. It is not an isomorphism between the entire MoE
plant and every aspect of Kumar and Mouchtaki's model. Their paper's main
contribution is an exact finite-dimensional analysis for a structured class
of offline policies; the reduction here needs only their underlying
censored-history decision setting and the elementary two-point regret
calculation.

## 4. Why the current MoE ingredients do not clear the novelty gate

- **Top-1 and capacities:** they generate the concrete loss pairs. Once the
  pairwise inequality \(f_0+f_1\ge40\) is established, the lower-bound proof
  uses only the two-state decision game above.
- **Pressure dynamics:** at \(H=2\), one update follows the indistinguishable
  observation and only selects the final-round action. There is no repeated
  feedback-state evolution in the theorem.
- **Gauge projection:** it parameterizes which pressure actions are reachable,
  but the gap proof does not show the projection changes the value relative
  to a defined gauge-free plant.
- **Target \(\mu\):** it is uniform and absent from the overflow objective and
  action policy class.
- **Heterogeneous capacity:** the limited sink is essential to this particular
  MoE realization, but the theorem does not establish a result that cannot be
  reproduced by a generic decision loss after the realization is collapsed.

Consequently, this is a useful constructive example and a candidate sanity
check for later theory. Its current novelty claim stops at “an MoE Top-1 plant
realizes this censored two-world decision game.” That alone does not satisfy
Phase 1 requirement 4 as written, which demands that the quantitative gap
depend non-reducibly on Top-K, gauge projection, heterogeneous \(C/\mu\), and
closed-loop state evolution.

## 5. Decision and next theorem target

**Stop the current paired-world theorem as the proposed novelty centerpiece.**
Keep the proof as a correct MoE realization/example; do not spend sweeps or
write the paper around its \(1/12\) gap.

The next theory task is to formulate a result that the reduction above cannot
preserve. The theorem must satisfy all five Phase 1 requirements, including
realizable hard Top-K routing, the declared heterogeneous capacity/target
structure, gauge projection, pressure-state evolution, and a minimal-signal
remedy. As a first discriminator against the present static reduction, use a
multi-round problem \(H\ge3\) where actions change later request observations
and costs. Then make at least one of the following properties quantitative:

1. a sharp \(E_S\), \(K\), or heterogeneous-capacity scaling that is not just a
   rescaling of a two-state loss table;
2. the gauge quotient changing the optimal admitted-feedback policy class or
   achievable value against a precisely defined alternative plant; or
3. a characterized minimal additional statistic of (R) beyond (A) that
   improves the dynamic overflow objective, with its communication cost.

Before proving the larger result, construct an explicit reduction attack for
each candidate. If every candidate still collapses to a static censored
decision/game after conditioning on its information history, apply the
roadmap stop rule and pivot the paper's central question rather than
rebranding the same lower bound. No experiments were run. The existing “no
sweeps until pass/fail criteria” gate remains in force for any replacement
theorem.

# Literature review: adaptive testing boundary for the Phase-1 H≥3 problem

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Purpose:** determine whether the Phase-1 controller problem (exact
Bellman recursion in `phase1_h3_dp_reduction.md`) reduces to a known
adaptive-testing result, and where the boundary lies.

---

## 1. Problem restatement

From `phase1_h3_dp_reduction.md` §4, the admitted-controller problem is
exactly: a hidden hypothesis \(i\in\{1,\dots,N\}\); at each round choose
a pressure \(q\) (a "test") subject to the reachability constraint
(Reach) from the current pressure; observe the admitted vector
\(A^i(q)\) (the "outcome"); pay cost \(c(o)=KT-\mathbf 1^\top o\), which
depends on the observed outcome; update the posterior by consistency.

Three features jointly define the problem:
- (a) **Outcome-dependent costs**: the cost of a test is a function of
  its observed outcome, not known before the test is run.
- (b) **State-constrained test sequence**: which test can follow which
  is constrained by the pressure dynamics (Reach).
- (c) **Cumulative cost**: minimize total overflow over \(H\) rounds,
  not just the cost of identifying the hypothesis.

---

## 2. Golovin, Krause & Ray (arXiv:1010.3091)

*Near-Optimal Bayesian Active Learning with Noisy Observations.*

**What it covers.** Bayesian active learning: adaptively select tests
from a fixed set \(\mathcal T\) to identify a hypothesis \(H\) drawn
from a known prior. Each test \(t\) has a **fixed, known cost**
\(c(t)\). Noiseless case: generalized binary search (GBS) is
\(O(\log n)\)-competitive with the optimal policy (\(n\) = number of
hypotheses), via adaptive submodularity. Noisy case: the EC²
algorithm with competitiveness guarantees. Non-uniform test costs
are handled.

**Why it does not cover our problem.**
- Costs \(c(t)\) are fixed per test and known **before** the test is
  run. Our cost \(c(o)=KT-\mathbf 1^\top o\) depends on the **observed
  outcome**, unknown until after the pressure is applied.
- **Any test can be selected at any time.** There is no constraint on
  the test sequence. Our (Reach) constraint restricts which pressure
  can follow which.
- The objective is pure **hypothesis identification** (drive version
  space to a singleton). Our objective is **cumulative overflow**;
  the controller need not fully identify the world, only route well.

**What survives.** In the noiseless deterministic case, the GBS
competitiveness bound applies to the **identification subproblem**:
with \(N\) worlds and unrestricted test selection, \(O(\log N)\) tests
suffice to identify the hypothesis. This is a valid upper bound on
the *information* cost, but it does not bound the *overflow* cost
of those tests, nor does it account for (Reach).

---

## 3. Sabato, Sarwate & Srebro (arXiv:1306.2347)

*Auditing: Active Learning with Outcome-Dependent Query Costs.*

**What it covers.** Binary classification where the algorithm **pays
only for negative labels** — the cost of a query depends on its
outcome, unknown in advance. Auditing complexity (number of negative
labels) vs active label complexity. Results for thresholds
(auditing complexity 1 vs \(\Theta(\log m)\) active) and rectangles
(\(2d\) vs \(m\)), in realizable and agnostic settings.

**Why it does not cover our problem.**
- Costs are **binary** (0 for positive, 1 for negative). Our cost is a
  **continuous** function \(KT-\mathbf 1^\top o\) of a vector outcome.
- The objective is **classification error** (learn a hypothesis with
  low error). Our objective is **cumulative overflow** over rounds;
  each round's cost is incurred regardless of identification.
- **No state constraints** on the query sequence. Any unlabeled point
  can be queried at any time.
- The hypothesis classes studied (thresholds, rectangles) do not
  include Top-K routing cells.

**What survives.** The *concept* of outcome-dependent query costs is
directly relevant, and the paper demonstrates that auditing
complexity can be strictly better than active label complexity.
But the binary-cost, classification-error setting does not transfer
to cumulative-overflow minimization with continuous vector outcomes.

---

## 4. Search for state-constrained adaptive testing

Searches for "adaptive testing state-dependent test availability,"
"optimal decision tree outcome-dependent cost state constraint," and
related terms returned no paper combining outcome-dependent costs
with state-dependent test availability. The optimal-decision-tree
literature (e.g., recent approximation algorithms) assumes fixed
test costs and unrestricted test selection. The psychometric
"adaptive testing" literature (CAT/IRT) is unrelated.

**Conclusion:** the combination (a)+(b)+(c) — outcome-dependent
costs, state-constrained test sequences, cumulative cost — does not
appear in the surveyed literature as a solved problem.

---

## 5. Reduction boundary (honest assessment)

**What reduces.** The admitted-controller problem is *exactly* an
instance of "adaptive testing with outcome-dependent costs and
state-dependent test availability." If a future theorem about this
*general* problem yields our bound, the contribution is at that
level, not at the MoE level.

**What does not reduce (currently).**
- Neither Golovin et al. nor Sabato et al. covers the combination.
  Citing them as "prior art that already solves it" would be false.
- The (Reach) state constraint has no analogue in either paper.
  Any lower bound that essentially uses (Reach) — e.g., showing that
  pressure-switching limits information-per-overflow — is not
  inherited from these results.

**What remains open (G3).** Whether the Top-K score-cell structure
imposes a *sharp additional* information-cost restriction beyond the
generic constrained-adaptive-testing framework. The cost-versus-
information lemma (user step 3) is the precise missing piece:
for each pressure, bound how much it can reduce uncertainty *per
unit of overflow paid*. Until that lemma is proved, we cannot say
whether the MoE structure adds anything beyond the generic
framework.

---

## 6. Stop condition (from user message, restated)

- If the best lower bound is a standard costly-search bound after
  relabeling pressures as tests → keep as application or pivot.
- If Top-K + (Reach) impose a provable additional restriction →
  that restriction is the candidate contribution.
- Do not run parameter sweeps until the theorem and reduction
  boundary are fixed.

No experiments were run for this review.

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
"metric-constrained active hypothesis testing with action-dependent
costs," and related terms surfaced several adjacent models that must be
compared directly:

- Nitinawarat and Veeravalli study controlled Markovian observations and
  accumulate a general non-uniform control cost up to a sequential stopping
  time. The control is selected from a fixed control set, and its cost is a
  function of the selected control, rather than the realized admitted
  outcome. The paper's guarantees are asymptotic testing results; the stated
  model does not directly encode a continuous pressure state with a
  pressure-dependent reachable-action set and overflow cost
  ([full text](https://arxiv.org/abs/1310.1844), §§3, 5).
- Vaidhiyan and Sundaresan explicitly add switching costs between actions
  to active sequential hypothesis testing. Their total cost combines
  decision delay with switching cost, and their optimality result is in the
  vanishing-error asymptotic regime. This is closer on movement penalties,
  but has a finite action set and does not model a metric-bounded continuous
  state transition or cost determined by the admitted outcome
  ([full text](https://arxiv.org/abs/1505.02358), §§II-A–II-B).
- Li et al. solve finite- and infinite-horizon sequential tests with online
  sensor-usage constraints by introducing sampling costs. Those are usage
  budgets/penalties on selected sensors, not a metric constraint coupling
  the next test to the current pressure state
  ([full text](https://arxiv.org/abs/1601.06447), §§II–III).
- Davenport et al. study adaptive sensing over a finite set of physically
  allowable measurement vectors, for sparse recovery. This constrains which
  tests may be selected but does not state our pressure-transition and
  overflow-cost model ([full text](https://arxiv.org/abs/1506.05889)).

The exact triple—outcome-dependent cumulative overflow, pressure-induced
state-constrained test transitions, and this deterministic Top-K outcome
map—did not appear in the sources reviewed here. This is a bounded search
result, not evidence that the general problem is unstudied or that our
specialization is novel.

---

## 5. Reduction boundary (honest assessment)

**What reduces.** The admitted-controller problem is *exactly* an
instance of "adaptive testing with outcome-dependent costs and
state-dependent test availability." If a future theorem about this
*general* problem yields our bound, the contribution is at that
level, not at the MoE level.

**What does not follow from adjacent prior art.** The papers above do not,
from the models and results checked, directly yield the finite-horizon
probe-versus-wait theorem. The controlled-sensing paper charges selected
control actions; the active-search paper adds switching penalties over a
finite action set; and the sensor-usage paper constrains aggregate use.
None of these formulations, as stated, combines a metric-bounded continuous
pressure transition with overflow determined by the realized admitted
outcome. These model differences do not establish novelty: the exact
instance-matched testing reduction remains valid, and a broader novelty
claim still needs a matched benchmark and an equation-level comparison.

**G3 status (reconciled 2026-10-17).** The fixed E=3 instance has an exact
long-horizon probe-versus-wait bound, but it reduces verbatim to its induced
state-constrained testing system. The canonical E-world family additionally
has the proved pair-separation inequality, but the one class-level go/no-go
assessment did not establish a benchmarked optimal-value separation or a new
general control principle. Current decision: retain these as exact MoE
results; do not claim a general control limitation. See
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md).

---

## 6. Stop condition (from user message, restated)

- If the best lower bound is a standard costly-search bound after
  relabeling pressures as tests → keep as application or pivot.
- If Top-K + (Reach) impose a provable additional restriction →
  that restriction is the candidate contribution.
- Do not run parameter sweeps until the theorem and reduction
  boundary are fixed.

No experiments were run for this review.

# Top-conference roadmap: feedback control for capacity-limited MoE routing

**Date:** 2026-10-16. **Branch:** `feat/paper-feedback-moe-routing`.
**Target:** top-conference paper (NeurIPS/ICML/ICLR tier). Not a workshop comparison.
**Status:** working plan. Theory work precedes any new sweeps.

---

## 1. Where we stand (full reread 2026-10-16)

**Proved [V]:** T1 (exact (R)/(C) equivalence boundary), T2 (exact (A)/(A₀)
boundary), T3 (excess decomposition ε^A = ε^R − J/(KT)), T4 (censoring fiber
F(A) — exact characterization of the knowable), T5 (partial-saturation
signal split), T6 (phantom gradients), T7 (target-blind divergence under
hetero capacity, with directional proof + overflow monotonicity), T8
(leak-freeze closed form + freeze/flip dichotomy), L1 (pre-flip linear
regime, t_flip = ceil(X^ε/η), prospectively verified), P1 (anti-windup
reduction), P2 (bias_integral separate family), P3 (quotient subgradient
structure for requested feedback).

**Open:** O-b (optimal (A,C,μ)-measurable controller — THE capstone),
O-c (principled pattern-signal switch — subsumed by O-b), O-d
(post-divergence recovery), O1 (post-flip cascades — documented as
intractable: as hard as simulation), O2 (η=10 limit cycle — niche),
O3/F3 (attainability — orthogonal to the censoring arc).

**Evidence:** 64 + 93 + 79 synthetic runs (E=8/K=2, deterministic, paired,
pre-registered where load-bearing). Zero trained-model evidence. Toy
trained-router probe is feasibility-only by design.

**Literature position (verified 2026-10-16):** the censoring lane is
unoccupied — zero hits for windup/saturation/censored/dropped in ID
Balancing, φ-Balancing, and the ALF-LB theory paper (independent full-text
searches). Primal-dual theory of ALF-LB is PARTIALLY PREDATED by
2512.03915 — must cite; our part is the capacity-censored extension +
gauge quotient + target dependence + failure conditions. Our Π_g gauge
structure is explicit where theirs is implicit (corrected 2026-10-16:
their dual-objective common-mode invariance holds only for top-1; what
holds is primal translation-invariance + zero-sum-preserving update).

**Premise (corrected):** R is observable in common router designs (GShard
Alg. 1, Switch Fig. 15 — verified from primary text). The paper studies
the restricted-telemetry setting and the comparative question honestly:
which signal controls better under saturation, and what can censored
feedback achieve in principle.

---

## 2. The gap to top-conference, exactly

Three gaps, no more:

**(a) The theory has no capstone.** T1–T8 characterize; none optimizes.
A top-conference theory paper needs a result with bite: an impossibility
result, an optimal controller, or a lower bound. O-b is that result and
it is unsolved.

**(b) Zero trained-model evidence.** The matrix's own rule: TRAINED-LM is
the only tier that can carry a model-quality claim. Blocked on GPU
(zero budget). This half cannot be closed without compute.

**(c) The problem statement is being rewritten.** Must lead with the
theory contribution on honest premises — not a bake-off.

What is NOT a gap: the literature position (lane is ours), the
experimental discipline (paired, pre-registered, honest negatives),
the formal groundwork (proved, verified).

---

## 3. The work plan

### Phase 1 — Theory capstone: optimal censored feedback (O-b)

The single highest-value unsolved problem. Well-posed: T4 gives the
exact fiber geometry; the question is what the best (A,C,μ)-measurable
feedback can achieve on it.

**1a. The lower bound (the "cannot").** Fiber-mates argument, verified
2026-10-16: take S = {1,2} saturated, fiber-mates R = (C_1+E_S, C_2)
and R' = (C_1, C_2+E_S) with E_S the known total excess on S. Both give
the same observation A. Requested feedbacks differ by
(R−R')/(KT) = (E_S/(KT), −E_S/(KT), 0…) on the gauge quotient. Any
measurable ε̂ is identical for both; by triangle inequality,
max over fiber-mates of gauge-L2 error ≥ E_S/(√2·KT). **Theorem to
prove:** no (A,C,μ)-measurable feedback achieves worst-case gauge
error below Ω(E_S/(KT)). The censoring cost scales with saturation
severity — quantitative, not just "information is lost."

**1b. The optimal feedback (the "can").** Minimax over the fiber F(A):
min over measurable ε̂ of max over R ∈ F(A) of gauge error vs ε^R.
Closed form if it exists; otherwise characterize the minimax solution
and give a principled approximation with guarantees.

**1c. O-c as corollary.** The optimal solution dictates exactly when
the saturation-pattern signal helps vs hurts — the principled switch
replacing (AW)'s all-or-nothing freeze.

**1d. Position existing controllers as special cases.** (A) = raw
pattern signal, (AW) = freeze, (A₀) = target-blind variant; the optimal
feedback is the principled interpolation. This turns our honest
negatives into theory: we can say exactly why each fails and what the
best achievable is.

**Success criterion:** theorem(s) + proofs in formal.md stating the
lower bound and the optimal (or minimax-characterized) censored
feedback. This is the paper's centerpiece — the result a reviewer
cites.

**Honesty note:** 1b may not admit a pretty closed form. The lower
bound (1a) plus a characterized minimax solution is still
conference-level. If 1b resists, the paper leads with the lower bound
and the principled approximation — still a "cannot + best-known-can"
arc.

### Phase 2 — Supporting theory

**2a. O-d: post-divergence recovery.** Once (A₀) diverges (T7), can it
recover when saturation breaks? Analyze: recovery condition or proof
of non-recovery under stated assumptions.

**2b. Tighten P3.** The quotient-subgradient structure guarantees
H-convergence, not R → KTμ. Establish exactly what it implies for
loads — or prove the gap is fundamental (attainability).

**Success criterion:** each item solved, or reduced to a precise
conjecture with the obstruction named. No hand-waving.

### Phase 3 — Problem statement and framing

**3a.** Rewrite leading with the theory contribution: "we characterize
what censored feedback can and cannot do" — lower bounds, optimal
feedback, failure conditions. Honest premise throughout (R observable
in common designs; restricted-telemetry setting named where invoked).

**3b.** Related work positions ID Balancing, φ-Balancing, and
2512.03915 explicitly per the 2026-10-16 comparison (claim-by-claim,
dated).

**3c.** Contribution list: (i) censoring fiber + lower bounds (NOVEL),
(ii) optimal censored feedback (NOVEL), (iii) gauge quotient theory
(explicit vs 2512.03915's implicit), (iv) target-dependence + failure
conditions incl. T7 (NOVEL), (v) honest negatives as theory
consequences.

**Success criterion:** the framing is both honest and ambitious — a
reviewer can see the conference-level claim on page one.

### Phase 4 — Synthetic validation of the NEW theory

**4a.** Factorial redesign (reviewer's step 4): target type × capacity
shape × aggregate capacity, matched batches/seeds. Attributes T1's
effects instead of confounding them.

**4b.** Pre-registered predictions from Phase 1 (not the old
mechanics): e.g., the lower bound's E_S-scaling, the optimal
feedback's predicted edge over (A)/(AW) in specified regimes.

**4c.** Sweeps stay stopped until Phase 1 delivers predictions. The
reviewer's gate stands, now with a theory-shaped key.

**Success criterion:** predictions committed to git before runs
execute; verifier extended with row-specific falsification; v1/v2/v3
artifacts untouched.

### Phase 5 — Trained-model evidence

Blocked on GPU (zero budget). S1 spec stays warm. Rule (matrix's own):
no model-quality claim without TRAINED-LM. The paper as submitted
will state this boundary explicitly — a theory paper with synthetic
validation, not a systems paper pretending otherwise. If compute
appears (collaborator, grant), S1 executes per the matrix.

---

## 4. What we will NOT do

- No sweeps until Phase 1 produces predictions that need testing.
  Sweeps without new theory are workshop motion.
- No model-quality claims without TRAINED-LM. Ever.
- No bake-off framing. The controller comparison validates the
  theory; it is not the paper's identity.
- No inflated novelty. The never-claim list (PID framing, centering
  operation, primal-dual-first, persistent load state as a concept)
  stays enforced.
- No claiming what the evidence doesn't support. The reviewer's
  honesty standard and the owner's ambition standard are the same
  standard: exactness.

---

## 5. Sequencing

Phase 1 → Phase 2 → Phase 3 → Phase 4, in that order. Phase 5 is
blocked externally and proceeds in parallel if compute appears.
Phase 3's rewrite can begin once Phase 1's statements are fixed
(theorem statements, not full proofs, suffice for framing).

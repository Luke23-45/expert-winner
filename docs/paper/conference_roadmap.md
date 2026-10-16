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
feedback can achieve on it. **Bar (reviewer 2026-10-16):** worst-case
lower bounds under censored feedback are not themselves new (censored
newsvendor, inventory regret, censored Kalman filtering). The
contribution must be MoE-specific: Top-K discontinuities, gauge
projection, hetero capacities/targets, closed-loop state evolution.
The five requirements below are all mandatory.

**The 5 requirements:**

1. **Controller class + information history.** Formalize the
   observation at step t: (A_t, C, μ, S_t, q_t, history). Define the
   measurable feedback class precisely — what the admitted-only
   controller sees, and what it doesn't.
2. **Comparator + cost.** R-informed controller as comparator. Cost
   stated explicitly: overflow O(R), target violation ‖R/(KT)−μ‖,
   or routing regret — pick one (objectives can conflict; the paper
   says which one it solves).
3. **Quantitative gap.** Worst-case cost gap ≥ X under explicit
   assumptions — not just non-identifiability. Starting point:
   fiber-mates → gauge error ≥ E_S/(√2·KT); must be connected to the
   chosen COST, not just feedback error.
4. **MoE-specific mechanism.** The gap must run through Top-K
   discontinuities, gauge projection Π_g, hetero C/μ, closed-loop
   state evolution. This is what survives comparison with generic
   censored-demand theory.
5. **Remedy + information cost.** Minimal sufficient extra signal.
   A+J = R is sufficient (trivial). A saturation bit alone is
   insufficient (no amount above capacity). Find the minimal signal
   for the stated objective.

**Work items:**

**1a. Formalize (requirements 1–2).** Controller information model,
comparator, loss. Write the definitions before any theorem.

**1b. Lower bound (requirements 3–4).** Fiber-mates argument as the
starting point (verified 2026-10-16: S = {1,2} saturated, R =
(C_1+E_S, C_2) vs R' = (C_1, C_2+E_S), same A, opposite optimal
updates → max gauge-L2 error ≥ E_S/(√2·KT) by triangle inequality).
Strengthen with the MoE mechanism: how the gap propagates through
Top-K switching and pressure dynamics (T7's mechanism is the
prototype).

**1c. REDUCTION ATTACK (mandatory).** Actively try to reduce the bound
to Kumar & Mouchtaki (censored newsvendor), Yang & Shi (inventory
regret), censored Kalman filtering, Tobit. If it reduces with no
MoE-specific remainder → STOP, pivot (do not present as a new
theorem). The novelty lives in requirement 4 or nowhere.

**1d. Remedy (requirement 5).** Minimal sufficient extra signal for
the stated objective. O-c falls out as corollary: the optimal
solution dictates exactly when the saturation-pattern signal helps
vs hurts — the principled switch replacing (AW)'s all-or-nothing
freeze.

**1e. Position existing controllers as special cases.** (A) = raw
pattern signal, (AW) = freeze, (A₀) = target-blind variant; the
optimal feedback is the principled interpolation. This turns our
honest negatives into theory: we can say exactly why each fails and
what the best achievable is.

**Stop conditions (Phase 1):**
- If the bound reduces to known censored-demand/partial-monitoring
  with no MoE-specific consequence → do not present as new; pivot.
- If "optimal feedback" collapses to "observe R" and R is
  obtainable at negligible cost → the remedy claim is weak;
  re-scope as pure theory or investigate another consequence.
- If 1b resists closed form → lower bound + characterized minimax +
  principled approximation still complete ("cannot +
  best-known-can" arc). Not a stop, a scope note.

**Success criterion:** theorem(s) + proofs meeting all 5
requirements, surviving the reduction attack (1c). This is the
paper's centerpiece — the result a reviewer cites.

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

**3b.** Related work positions ID Balancing, φ-Balancing,
2512.03915, Trinity/SMEBU (equation-level), FreeBalance and LAER-MoE
(systems boundary: placement/migration vs feedback control), and the
censored-decision literature (censored newsvendor, inventory regret,
censored Kalman filtering, Tobit) explicitly per the comparison
matrix — with the precise MoE-specific difference stated for each,
not keyword matching.

**3c.** Contribution list: (i) censoring fiber + lower bounds (NOVEL),
(ii) optimal censored feedback (NOVEL), (iii) gauge quotient theory
(explicit vs 2512.03915's implicit), (iv) target-dependence + failure
conditions incl. T7 (NOVEL), (v) honest negatives as theory
consequences.

**Success criterion:** the framing is both honest and ambitious — a
reviewer can see the conference-level claim on page one.

### Phase 4 — Validation in stages (theory decides experiments)

**4a. Small exact cases.** Enumerate controlled examples exposing
missing assumptions; compare observed behavior with the theorem.
(No GPU needed.)

**4b. Real router traces (new).** Instrument a real MoE
implementation before and after capacity enforcement: record R, A,
J, C, the feedback actually used, and the telemetry boundary. Tests
whether the formal model matches real code. Does not prove the
lower bound. (No GPU needed.)

**4c. Factorial synthetic redesign (reviewer's step 4).** Target
type × capacity shape × aggregate capacity, matched batches/seeds.
Attributes T1's effects instead of confounding them. Pre-registered
predictions from Phase 1: the lower bound's E_S-scaling, the
optimal feedback's predicted edge over (A)/(AW) in specified
regimes.

**4d. Controlled interventions (only after theorem + traces
survive).** Test the theorem's predictions in a real router/model
setting. Keep overflow, target error, quality, specialization, and
systems cost distinct — a better load metric alone is not enough.

**Stop conditions (Phase 4):**
- If traces show the assumed admission/censoring regime is absent
  in the intended workload → no deployment claim about it.
- If experiments only reproduce "R beats A" in the synthetic
  harness → does not clear the conference bar; back to Phase 1.

**4e.** Sweeps stay stopped until Phase 1 delivers predictions. The
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

## 6. Branch discipline

- `feat/research-censored-feedback` (this branch): Phase 1–2
  exploration — proofs, negative results, attack notes. Created
  2026-10-16 from the paper branch tip.
- `feat/paper-feedback-moe-routing`: integration target. Promote
  only findings that pass the gates (novelty, theory, reproduction,
  external validity, significance), with proofs/artifacts and
  limitations.
- v1/v2/v3 branches and artifacts: immutable, never touched.
- `main`: merge only when material is reviewed and accepted.

---

## 7. Sequencing

Phase 1 → Phase 2 → Phase 3 → Phase 4, in that order. Phase 5 is
blocked externally and proceeds in parallel if compute appears.
Phase 3's rewrite can begin once Phase 1's theorem statements are
fixed (statements, not full proofs, suffice for framing). The
reduction attack (1c) runs in parallel with 1b from the start —
kill the bound early if it's reducible.

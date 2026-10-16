# Phase 1 H≥3 replacement: research direction and partial results

**Status:** research in progress. NOT a proved theorem.
**Branch:** `feat/research-censored-feedback`.
**Context:** the H=2 lower bound (`phase1_lower_bound_draft.md` v0.3) was
reduced to censored newsvendor (`phase1_reduction_audit_2026-10-16.md`).
Per the roadmap stop rule, the centerpiece needs H≥3 with genuine
multi-round feedback where Top-K, hetero C/μ, gauge, and pressure
dynamics are all load-bearing.

This document records the design space, the most promising direction,
what is proved, and what remains open. It does not claim a complete
H≥3 lower bound.

---

## 1. Why H=2 reduced, and what H≥3 must do differently

The H=2 proof had the structure: one blind observation (A₀), one
pressure decision (q₁), one cost round. Conditioning on the observation
history, it is a static two-state decision game. The Top-K thresholds
and gauge only *instantiated* the loss table; the *argument* was generic.

For H≥3 to survive the same attack, the *proof* — not just the setup —
must essentially use multi-round dynamics. Concretely, after conditioning
on the information history at each round, the remaining problem must
*not* be a static censored decision. This happens when:

- (a) actions change the *informativeness* of future observations
  (active learning / dual control), or
- (b) the hidden parameter *evolves* (tracking), or
- (c) the pressure *state* persists and constrains future actions
  (δ < 1, switching costs).

A mere repetition of the H=2 one-shot gap over H rounds ("H independent
newsvendors") does not satisfy this: it collapses round-by-round.

---

## 2. Primary candidate: E-world probing with Top-K sweet spots

### 2.1 Setup

E experts: 1..E−1 can carry excess, E is a limited sink.
C_e = C for e < E, C_E = C_sink < 2·E_S (sink cannot absorb two
deflections; this is the heterogeneous-capacity structure doing work).
Worlds i = 1..E−1: R_{0,i} = C + E_S, R_{0,e} = C for e < E, e ≠ i,
R_{0,E} = 0. Then A_0 = (C,...,C,0) in *every* world: the admitted
policy is blind to i. T = (E−1)·C + E_S.

Each expert e < E has the H=2 margin structure: E_S low-margin tokens
(deflectable to the sink via a pressure sweet spot
q_e ∈ (m/γ, M/γ]) and high-margin tokens that do not deflect there.
The sweet spots are *mutually exclusive*: pressuring two experts into
their sweet spots overflows the sink (Lemma 4 generalized; the
H=2 case is proved in `phase1_lower_bound_draft.md` Lemma 4).

### 2.2 What is proved: E-world mutual exclusivity (new)

*Lemma (E-world no-hedging).* Fix E−1 worlds i = 1..E−1 and E experts
(E is a sink with C_E = C_sink < C). World i: R_{0,i} = C + E_S,
R_{0,e} = C for e < E, e ≠ i, R_{0,E} = 0; thus A_0 = (C,...,C,0) in
every world. Margin structure: in world i, expert i carries E_S
low-margin tokens (margin m, deflectable to the sink via sweet-spot
pressure q_i ∈ (m/γ, M/γ]); every other expert e < E, e ≠ i, carries
*all* C tokens at low margin m. Then for any fixed pressure q, the set
G(q) = {i : overflow_i(q) < E_S/2} satisfies |G(q)| ≤ 1.

*Proof.* Suppose i ≠ j both lie in G(q). To drive world-i overflow
below E_S/2, q must deflect i's excess: q_i > m/γ. Likewise
q_j > m/γ for world j. But in world i, expert j ≠ i holds C
low-margin tokens; q_j > m/γ deflects all C to the sink, giving
overflow at least (C − C_sink) from the sink alone. Choosing
C_sink < C − E_S/2 makes this ≥ E_S/2, contradicting i ∈ G(q).
Hence |G(q)| ≤ 1. ∎

*Corollary (per-round lower bound).* For fixed q, let J = {e < E :
q_e > m/γ}. If J = ∅, every world incurs overflow E_S (excess
unfixed): average E_S. If J = {j} with q_j in j's sweet spot,
world j has overflow 0 but each world i ≠ j incurs ≥ (C − C_sink)
(sink flooded by j's C deflected tokens) plus its own E_S:
average ≥ [(E−2)(C − C_sink + E_S)]/(E−1). If C − C_sink ≫ E_S,
the minimizer is J = ∅ ("do nothing"), so min_q average ≥ E_S,
and the bound is tight.

The requested policy observes R_0, identifies i, and holds expert i
in its sweet spot: per-round overflow 0 after Round 0. Over H rounds
with per-round blind decisions, the admitted policy's optimal
("do nothing") total is H·E_S vs E_S for the requested policy.

*Why this matters.* The lemma closes gap (G1): mutual exclusivity
holds for E worlds, not just 2, and the *catastrophic* wrong-probe
cost (C − C_sink, not merely E_S) is what forces the admitted policy
to *rationally* stay blind. The Top-K thresholds and the limited
sink are load-bearing: smooth the thresholds and the sweet spots
dissolve; enlarge the sink and hedging becomes safe.

*Limitation.* This is a *per-round* (one-shot) bound repeated over H
rounds. It does not yet establish an *irreducible* multi-round gap:
a strict reductionist may view it as "H copies of an (E−1)-state
static game." The multi-round *learning* analysis (G3) — where the
admitted policy *could* probe but the probing *itself* is the costly
multi-step process — remains the missing piece for full
irreducibility. See §2.3.

### 2.3 What is conjectured: E-world sequential probing lower bound

*Conjecture.* With H ≥ E rounds, any admitted policy π_A incurs
expected cumulative overflow Ω(E·E_S), while a requested policy
achieves O(E_S). The normalized gap is Ω(E_S/(KT)), non-vanishing in H.

*Proof skeleton (incomplete).*
π_R observes R_0, identifies i immediately, and pressures expert i
to its sweet spot from Round 1: total cost E_S (Round 0 sunk).
π_A observes A_0 = (C,...,C,0), blind to i. To find i, it must
*probe*: apply a sweet-spot pressure to a candidate expert j and
observe whether A_t changes (success: sink receives E_S, revealing
j = i; failure: A_t unchanged, ruling out j). By mutual exclusivity,
probes are sequential (one expert per round). Each failed probe
leaves expert i's excess in place, incurring Ω(E_S) overflow that
round. In the worst case over worlds (adversarial ordering), or
Ω(E) expected over a uniform prior, π_A needs Ω(E) probes before
succeeding. Total: Ω(E·E_S) vs O(E_S).

*Gaps in the proof.*
- (G1) CLOSED by the Lemma above (mutual exclusivity for E worlds,
  with catastrophic wrong-probe cost forcing rational blindness).
- (G2) The probing *informativeness* claim (A_t reveals success)
  assumes the sink capacity and margin structure make success/failure
  distinguishable from A_t alone; this needs verification per probe.
  Note: under the Lemma's margin structure, probing is *catastrophic*
  when wrong, so a rational admitted policy does *not* probe — the
  "do nothing" bound above is the operative one, and (G2) is moot
  for the lower bound (it would matter only for an *upper* bound
  via a probing policy).
- (G3) For *full irreducibility* (beyond "H copies of a static
  game"), the multi-round learning analysis remains open: a
  construction where probing is *worthwhile but slow*, so the
  admitted policy *does* learn over rounds and the *rate* of
  learning — governed by Top-K informativeness — determines the
  gap. The current Lemma gives a *valid* H-round lower bound
  (H·E_S vs E_S); whether it *survives* the reduction attack as
  stated is the open question for §2.4.

### 2.4 Reduction attack on E-world probing (preliminary)

*Attack:* "This is multi-armed bandits: E−1 arms, costly pulls,
find the best arm. The Ω(E) lower bound is standard."

*Defense (partial).*
- The *probe* is not an abstract arm pull: it is a *pressure vector*
  to a Top-K sweet spot, subject to *gauge constraints*
  (U_B ⊂ 1^⊥). Realizing "test expert j" as a pressure, and computing
  its cost, requires the MoE dynamics. A bandit reduction would need
  to reproduce the sweet-spot threshold structure.
- The *observation* is not a scalar reward but a *censored load
  vector* A_t = min(R_t, C). Its informativeness (1 bit per probe:
  success/failure) is *derived* from the censoring, not assumed.
- The *mutual exclusivity* (one probe per round) comes from Top-K
  thresholds interacting with sink capacity — not from an exogenous
  "one arm per round" constraint.

*Honest assessment.* The *framework* (search with costly tests) is
generic. The *mechanism* (Top-K probes, censored observations) is
MoE-specific. Whether this clears the novelty gate depends on whether
"MoE-specific instantiation of sequential search" is deemed a
contribution. It is *strictly stronger* than H=2 (multi-round,
scales with E), but a strict reviewer may still see bandits.
**This candidate has non-trivial reduction risk.**

---

## 3. Alternative: T7 divergence over H rounds

Theorem T7 (`formal_core.md`) proves: under (A₀) feedback with
heterogeneous C, pressure diverges in the capacity direction,
and overflow is *non-decreasing* along the divergent trajectory.

*Idea.* Pair two worlds where the T7-divergent pressure direction is
*correct* in one and *harmful* in the other, with identical A_t
(global saturation). Over H rounds, the harmful divergence
*compounds* (overflow strictly increases at each flip, T7 part 2),
while the requested policy applies the corrective pressure.
The gap *grows* with H (not just a one-shot).

*Why it might survive.* The *compounding* is driven by the
*interaction* of pressure dynamics with Top-K flips — a genuinely
dynamical mechanism with no static analogue. The proof must track
the pressure *trajectory*, not just a single decision.

*Status.* Not yet constructed. The key challenge is the same as
H=2: ruling out *all* blind policies, not just (A₀). Requires a
*trajectory* no-hedging lemma.

---

## 4. Alternative: Markov-switching world (tracking)

*Idea.* The hidden excess expert *changes* over time (Markov chain).
π_R observes R_t and tracks perfectly. π_A observes censored A_t
and must *filter* the hidden state. The gap is the *filtering error*
compounded over H rounds.

*Why it might survive.* Filtering from censored observations with
Top-K structure is not a standard bandit problem; it is a POMDP
with MoE-specific observation kernel. The *rate* at which π_A learns
depends on the informativeness of A_t, which is MoE-specific.

*Status.* Not yet constructed. Requires information-theoretic
analysis of the censored observation kernel.

---

## 5. Decision

The E-world probing direction (§2) is the most developed: it has a
proved 2-world core (Lemma 4), a clear E-world generalization path,
and a concrete (if risky) reduction defense. The T7-divergence (§3)
and Markov-switching (§4) directions are less developed but may have
stronger irreducibility.

**Recommendation:** develop the E-world probing lower bound to
completion (close G1–G3), then subject it to the full reduction
attack. If it collapses, pivot to T7-divergence. Do not run
experiments until a replacement theorem survives the attack.

No sweeps were run. No theorem is claimed here.

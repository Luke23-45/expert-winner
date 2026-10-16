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

Use Top-1 routing (\(K=1\)) with E experts: 1..E−1 can carry excess,
and E is a limited sink.
C_e = C for e < E. For a correct probe to fit and a wrong probe to
overload the sink, the construction requires
E_S ≤ C_sink < C−E_S/2 (hence C > 3E_S/2).
The earlier condition C_sink < 2·E_S alone does not imply these facts.
Worlds i = 1..E−1: R_{0,i} = C + E_S, R_{0,e} = C for e < E, e ≠ i,
R_{0,E} = 0. Then A_0 = (C,...,C,0) in *every* world: the admitted
policy is blind to i. T = (E−1)·C + E_S.

Use an explicit token construction. In world i, every regular expert
e < E has C baseline tokens; the baseline margin is M at e=i and m at
e≠i. There are E_S additional low-margin (m) tokens at expert i.
For a token assigned to e, set affinity m or M at e, 0 at the sink E,
and −M at all other regular experts. At q=0 these tokens realize the
stated request counts. A probe of j is the particular pressure state
with q_j−q_E in (m/γ,M/γ] and q_e=q_E for e≠j,E; it moves the low-margin
j tokens, but retains high-margin baseline tokens. These are properties
of those probe states, not yet a proof for every reachable pressure.

### 2.2 E-world mutual exclusivity (proved for the explicit construction)

*Lemma (E-world no-hedging).* Use the explicit construction
in §2.1, integer parameters satisfying its capacity conditions, and a
persistent affinity matrix for each world. For every \(q\in\mathcal Q\),
the set
\(G(q)=\{i:\|J^i(q)\|_1<E_S/2\}\) satisfies \(|G(q)|\le1\).

*Proof.* Fix any pressure q, and let d_e^L(q) be the expert selected by
Top-1 for a token of low-margin type L_e. This destination is the same
in every world because the affinity vector and tie rule are fixed.
Suppose, for contradiction, that two distinct worlds i and j each have
overflow below E_S/2.

In either world there are E−1 baseline groups of C identical tokens.
None can be sent to the sink: that would create sink overflow at least
C−C_sink>E_S/2. No two such groups can be sent to the same regular
expert: that expert would receive at least 2C and overflow by at least
C>E_S/2. Therefore the E−1 baseline groups must go one each to the
E−1 regular experts. The additional E_S-token group also cannot go to a
regular expert, since every regular expert already receives a C-sized
baseline group, which would create overflow E_S>E_S/2. It must go to the
sink. In world i this implies d_i^L(q)=E. But in world j, i≠j, the
baseline group at i is also of type L_i and has size C. At the same q
it must therefore also go to the sink, causing overflow at least
C−C_sink>E_S/2 in world j, a contradiction. Hence |G(q)|≤1. ∎

This proof uses the explicit identical-token-block construction,
Top-1 determinism, and the capacity inequalities. It does not assume
the sink has minimum pressure. It establishes the static all-state
no-hedging lemma (G1), not a sequential value lower bound.

*Restricted-action calculation.* For J=∅, each world has overflow
E_S. For a single specified sweet-spot probe j, world j has overflow
zero; every world i≠j has overflow E_S+(C−C_sink). Under the uniform
prior the probe's average one-round overflow is therefore
\((E−2)(E_S+C−C_sink)/(E−1)\). Thus no-probe is no worse than this
single probe if \((E−2)(C−C_sink) ≥ E_S\). This calculation is only
for the listed actions; it is not a lower bound over arbitrary pressure
vectors, multi-expert actions, or history-dependent policies. Thresholds
are relative (q_e−q_E), not q_e alone.

The requested policy observes R_0, identifies i, and holds expert i
in its sweet spot: per-round overflow 0 after Round 0. Over H rounds
with per-round blind decisions, the no-probe admitted policy costs
H·E_S, versus E_S for the requested policy. This does not establish
that no-probe is optimal for the admitted policy over the horizon.

*Scope of the result.* The lemma closes the static mutual-exclusivity
claim for E worlds, not the sequential lower bound. Its proof is a
capacity and identical-block argument; it does not by itself show that
Top-K thresholds or gauge geometry are essential. Whether the
construction yields a non-reducible control theorem remains open.

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
achieves O(E_S). This would give a cumulative gap Ω(E·E_S) in the
specified parameter regime. Under the document's normalized cost, the
corresponding gap is Ω(E·E_S/(HKT)); it decreases as H grows with fixed
E, so no horizon-independent normalized gap is claimed.

This is not yet a well-posed theorem statement: the constants and
quantifiers must specify how C−C_sink scales with E, E_S, and H, as
well as B, δ, the prior, and the exact policy class. In particular,
H≥E alone does not imply the proposed tradeoff.

*Proof skeleton (incomplete and conditional on unproved claims).*
π_R observes R_0, identifies i immediately, and pressures expert i
to its sweet spot from Round 1: total cost E_S (Round 0 sunk).
π_A observes A_0 = (C,...,C,0), blind to i. In the proposed
single-candidate strategy, it applies a sweet-spot pressure to a
candidate expert j and
read the sink coordinate of A_t (success: it is E_S, revealing j=i;
failure: it is C_sink, ruling out j). If the unproved
no-hedging/action-class claim forces probes to be sequential, they use
one expert per round. Each failed probe
leaves expert i's excess in place, incurring Ω(E_S) overflow that
round. In the worst case over worlds (adversarial ordering), or
Ω(E) expected over a uniform prior, π_A needs Ω(E) probes before
succeeding. Total: Ω(E·E_S) vs O(E_S).

*Gaps in the proof.*
- (G1) CLOSED by the block-counting proof in §2.2 for the explicitly
  constructed affinity worlds and stated capacity regime.
- (G2) Probes can be informative. In the explicit single-probe
  construction with E_S<C_sink, a correct probe produces admitted sink
  load E_S and a wrong probe produces C_sink. This distinguishes the
  probed world from the others using A, so information acquisition must
  be included in the lower-bound analysis.
- (G3) For *full irreducibility* (beyond "H copies of a static
  game"), the multi-round learning analysis remains open: a
  construction where probing is *worthwhile but slow*, so the
  admitted policy *does* learn over rounds and the *rate* of
  learning — governed by Top-K informativeness — determines the
  gap. The current note does **not** prove a lower bound against all
  admitted policies, nor establish the claimed H·E_S versus E_S value
  gap. Whether a corrected theorem survives the reduction attack is
  open; see §2.4.

### 2.4 Exact three-round probe policy: why the horizon matters

Take E=3 and worlds i=1,2, with E_S<C_sink<C−E_S/2. At q=0 both
worlds have A_0=(C,C,0) and overflow E_S. Probe j=1 at the next round.
The explicit token margins above give:

| World | Probe-round requests (1,2,sink) | Admitted sink load | Overflow |
|---|---:|---:|---:|
| i=1 (correct probe) | (C,C,E_S) | E_S | 0 |
| i=2 (wrong probe) | (0,C+E_S,C) | C_sink | E_S+C−C_sink |

**Proposition (exact one-probe upper bound for the admitted value).**
Assume integer capacities and counts with
\(E_S<C_{sink}<C−E_S/2\), \(0<m<M\), \(\delta=0\), persistent
affinities, equal prior on the two worlds, and
\(B\ge\sqrt{2}M/(\eta\gamma^2)\). For any \(H\ge3\), there is a
causal admitted policy with expected cumulative raw overflow exactly
\(E_S+(E_S+C−C_{sink})/2\). It observes only admitted counts.

*Proof.* At round 0 both worlds reveal \(A_0=(C,C,0)\), with raw
overflow \(E_S\). Apply the j=1 probe. The table gives round-1 cost
zero in world 1 and \(E_S+C−C_{sink}\) in world 2. The admitted vectors
are \((C,C,E_S)\) and \((0,C,C_{sink})\), so the policy identifies the
world because \(E_S<C_{sink}\). For \(L\in(m/\gamma,M/\gamma]\), it
reaches \(q_1=Le_1\) from zero with a zero-sum update of norm
\(L\sqrt{2/3}/(\eta\gamma)\), then switches to \(q_2=Le_2\) in world 2
using update \(L(e_2-e_1)/(\eta\gamma)\), whose norm is
\(L\sqrt{2}/(\eta\gamma)\le B\). In world 1 it holds \(q_1\). With
\(\delta=0\), zero subsequent updates preserve the selected pressure;
the chosen sweet spot yields zero overflow for every later round.
Taking the equal-prior expectation gives the stated total. ∎

The no-probe policy costs \(H E_S\). Thus this explicit probe beats
no-probe exactly when
\((H−1)E_S>(E_S+C−C_{sink})/2\). This refutes the unqualified
claim that a costly wrong probe makes an admitted controller stay
blind. It does not characterize the optimal admitted policy, and it
does not provide a lower bound. The normalized gap associated with this
example divides these cumulative costs by (HKT).

This is a correction, not G3's solution. A complete theorem must
optimize over causal policies that trade probe cost, information,
remaining horizon, and pressure switching. Even this exact probe game
still resembles costly search/bandits, so it has not passed the
reduction attack.

### 2.5 Reduction attack on E-world probing (preliminary)

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
MoE-specific. The full-history controller problem and exact value bound
have not been derived, so this candidate is not yet known to be
strictly stronger than H=2. A reviewer may still reduce it to costly
search or bandits.
**This candidate has non-trivial reduction risk.**

**Prior-theory boundary to check.** Bayesian active learning studies
adaptive selection of informative tests, including nonuniform test
costs and noisy or correlated outcomes; costly-bandit work studies
action-dependent observation costs and exploration/exploitation
tradeoffs ([Golovin, Krause & Ray, 2010/2013](https://arxiv.org/abs/1010.3091);
[Schur, Lago & Fiez, UAI 2026](https://proceedings.mlr.press/v337/schur26a.html)).
These sources do not, from their stated models alone, settle whether the
MoE plant reduces to those settings: here pressure induces a Top-K
routing transition, admission clips the resulting vector, and the same
pressure state carries into later rounds. The reduction attack must
formalize that transition and show either an exact reduction or a
quantitative property those models do not preserve. This is a scope
boundary, not a novelty claim.

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

The E-world probing direction (§2) is the most developed. Its static
all-state no-hedging lemma is proved, but the sequential value bound
and novelty reduction remain open. The H=2
construction in `phase1_lower_bound_draft.md` remains a valid MoE
realization of a two-point value gap, but its own reduction audit shows
that it is not a novel centerpiece. The T7-divergence (§3) and
Markov-switching (§4) directions are research hypotheses, not results.

**Recommendation:** develop the E-world probing lower bound to
completion (close G1–G3), then subject it to the full reduction
attack. If it collapses, pivot to T7-divergence. Do not run
experiments until a replacement theorem survives the attack.

No sweeps were run. No theorem is claimed here.

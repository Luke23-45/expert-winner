# Phase 1 H≥3 replacement: research direction and partial results

**Status (reconciled 2026-10-18):** research-direction note with historical conjectures. The fixed
E=3 probe-versus-wait value theorem is now proved separately in
[`phase1_probe_wait_value_theorem_2026-10-16.md`](phase1_probe_wait_value_theorem_2026-10-16.md).
An exact E=4, three-round value theorem over all causal admitted policies is
now documented in
[`phase1_matched_testing_comparator_e4_2026-10-16.md`](phase1_matched_testing_comparator_e4_2026-10-16.md).
The continuous-pressure note gives exact E=4 values at horizons three and
four for every movement radius, plus exact values for every horizon
\(H\ge4\) when \(\beta>1/\sqrt2\). The remaining fixed-instance value domain is
\(H\ge5\), \(\beta\le1/\sqrt2\); these values are not a priority because
they cannot change the fixed-instance benchmark result. A reduction-resistant
novelty claim is not established. The fixed E=3/E=4 results
reduce exactly to
state-constrained adaptive testing. The independent benchmark and the
coarse-matching no-go counterexample are in
[`phase1_benchmark_gate_2026-10-16.md`](phase1_benchmark_gate_2026-10-16.md).
The current E-world family gate, including the all-pressure pair-separation
inequality, finite-horizon all-policy lower bound, and exact E=4
pair-separation audit, is in
[`phase1_eworld_pair_separation_gate_2026-10-16.md`](phase1_eworld_pair_separation_gate_2026-10-16.md).
**Branch:** `feat/research-censored-feedback`.
**Context:** the H=2 lower bound (`phase1_lower_bound_draft.md` v0.3) was
reduced to censored newsvendor (`phase1_reduction_audit_2026-10-16.md`).
Per the roadmap stop rule, the centerpiece needs H≥3 with genuine
multi-round feedback where Top-K, hetero C/μ, gauge, and pressure
dynamics are all load-bearing.

This document records the design space, the most promising direction,
what is proved, and what remains open. The E-world family now has an
all-causal-policy finite-horizon lower bound; extension beyond that family
and novelty beyond adaptive testing remain open.

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
no-hedging lemma (G1), not a sequential value lower bound for the E-world
family. The fixed E=3 sequential value question is handled separately in the
linked probe-versus-wait theorem.

*One-round value corollary.* Let \(N=E-1\) and use the uniform prior on
the N worlds. At round zero all admitted observations are identical,
so the admitted controller chooses a common round-one pressure (couple
its private coins across worlds). By the lemma, at most one world can
have round-one overflow below \(E_S/2\). Therefore its expected
round-one overflow is at least
\((N-1)E_S/(2N)\), and its expected cumulative raw overflow is at least
\(E_S+(N-1)E_S/(2N)\). If the requested controller can reach each
sweet spot in one update, its total is \(E_S\), giving a shared-prior
value gap of at least \((N-1)E_S/(2N)\), provided
\(\delta=0\) and
\(B\ge M\sqrt{1-1/E}/(\eta\gamma^2)\), which suffices to reach any
chosen sweet spot from q_0=0 in one update and hold it thereafter.
This is a one-round gap; after normalization by \(HKT\) it decays as
\(1/H\). It does not close G3.

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
rounds. It does not establish an *irreducible* multi-round gap for the
E-world family:
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

This conjecture is now superseded for the named E-world family by the
finite-horizon bound in
[`eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md`](eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md).
That theorem proves a lower bound of order `min{E_S(H-1),L(N-1)}` up to
constants against every causal randomized admitted policy when the requested
policy can reach a zero-overflow pressure. The older, stronger
`Omega(E*E_S)` conjecture as originally parameterized is not asserted.

The earlier version of this section said the finite-horizon theorem was not
well-posed: the constants and
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
  game"), the multi-round learning analysis for the E-world family remains
  open: a
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

**Update (2026-10-16).** A separate finite-horizon calculation, with its
score-cell costs now stated in a hand-checkable table, gives
$V_R(H)=60$ and $V_A(H)=80$ for one $E=3$, two-world, small-$B$ instance
when $H\ge4$. See
[`phase1_g3_steering_2026-10-16.md`](phase1_g3_steering_2026-10-16.md).
This closes the fixed-instance value calculation. Its gap is
constant in $H$, and the reduction risk remains: this is not the general
all-horizon admitted-value characterization or proof of a Top-K-specific
theory contribution.

**Parameterized update (2026-10-16).** For this same score/capacity instance,
varying only the step budget gives an exact requested value
$V_R(H)=E_S\min\{H,n(B)\}$ and an exact admitted value at the first
reachable horizon; the gap there remains exactly $E_S$, while the normalized
gap vanishes as $B\to0$. See
[phase1_parameterized_small_b_2026-10-16.md](phase1_parameterized_small_b_2026-10-16.md).
Thus changing only the travel radius does not establish a growing signal-value
gap. The next candidate is the trajectory-level T7 construction in §3, with
the reduction attack against all causal admitted policies required from the
start.

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

Theorem T7 (`formal_core.md`) is a fixed-controller trajectory result:
under `(A₀)` feedback and its saturation assumptions, pressure moves in the
capacity direction and overflow is non-decreasing, with a strict increase
possible when saturation breaks.

*Original paired-world idea (rejected as written).* Pair worlds with identical
`A_t=C` histories and claim that overflow compounds while the admitted
controller remains blind. This is impossible: `O_t = K T - sum_e A_{t,e}`,
so identical admitted vectors imply identical stage overflow; moreover,
`A_t=C` makes overflow the constant `K T - sum_e C_e`. Any strict increase
changes `A_t` and is observable at that transition. The exact identity and
scope correction are recorded in
[`phase1_t7_trajectory_audit_2026-10-16.md`](phase1_t7_trajectory_audit_2026-10-16.md).

This does not rule out a value-of-information gap. A requested policy may
choose world-dependent actions with lower cost, while an admitted policy must
trade off probing cost, information, and constrained pressure movement. The
open theorem must quantify that tradeoff against every causal randomized
admitted policy and attack its reduction to state-constrained adaptive
testing. T7 may motivate a fixed-controller failure or a plant mechanism; it
does not itself supply the policy-class lower bound.

*Status.* The proposed hidden-compounding argument is invalid as phrased.
Any replacement must explicitly model informative actions, observations,
costs, and pressure transitions. No gap or novelty claim follows from T7
alone.

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
all-state no-hedging lemma and the canonical-family all-pressure
pair-separation inequality are proved. The E=4 full-pressure value is known
at H=3 and H=4 for all movement radii, and for H≥4 when β>1/√2; values for
H≥5 and β≤1/√2 remain uncomputed but are not the active research gate. The
class-level novelty attempt is documented in
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no-go_2026-10-17.md)
and did not establish a benchmarked control limitation. The
fixed E=3 sequential
result is proved separately in the linked companion note. The H=2
construction in `phase1_lower_bound_draft.md` remains a valid MoE
realization of a two-point value gap, but its own reduction audit shows
that it is not a novel centerpiece. T7 (§3) is a proved fixed-controller
mechanism, but its proposed hidden-compounding paired-world argument is
invalid as written; the replacement policy-class theorem is open.
Markov-switching (§4) remains a research hypothesis.

**Recommendation:** the exact E=3 probe-versus-wait value theorem is now in
[`phase1_probe_wait_value_theorem_2026-10-16.md`](phase1_probe_wait_value_theorem_2026-10-16.md).
The E=4 high-movement three-round value and matched-comparator audit are in
[`phase1_matched_testing_comparator_e4_2026-10-16.md`](phase1_matched_testing_comparator_e4_2026-10-16.md).
The E=3 result covers every causal randomized admitted policy and yields a
raw long-horizon gap of order $1/\beta$; the E=4 result gives an exact
three-round value under a large movement budget. Both transfer to their
induced state-constrained adaptive-testing models, so neither yet supports a
distinct MoE-control impossibility claim. The all-pressure inequality (PS) and its finite-horizon unrestricted-movement
Bellman reduction are now proved in
[`phase1_eworld_pair_separation_gate_2026-10-16.md`](phase1_eworld_pair_separation_gate_2026-10-16.md).
The same note gives exact finite-movement reachability within canonical subset
probes. The exact continuous-pressure Bellman recursion, a short-horizon quiet zone,
the complete E=4 values for H=3 and H=4 at all β, and the E=4 values for
H≥4 and β>1/√2 are in
[`phase1_full_pressure_cell_dp_gate_2026-10-17.md`](phase1_full_pressure_cell_dp_gate_2026-10-17.md).
The E=4 construction also shows that optimizing pressure location inside a
test cell matters under movement constraints. Values for H≥5 and
β≤1/√2 remain uncomputed, but are not the next priority: all such
fixed-instance values transfer exactly to the metric-constrained polyhedral
testing benchmark. The single class-level attempt is now assessed in
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md):
PS is a valid family lemma, but no benchmarked optimal-value separation or
new general control principle follows. The current decision is no-go for the
control-limitation claim; retain these results as exact MoE applications.
The T7 audit (`phase1_t7_trajectory_audit_2026-10-16.md`) rules out hiding
increasing overflow inside an unchanged admitted history. Do not run large
sweeps until that broader theorem and its reduction boundary survive review.

The all-pressure result is specific to the stated
canonical E-world family; it is not a theorem for arbitrary MoE instances.
The fixed E=3 theorem is stated and proved in the linked companion document.

## 6. Status update: finite-horizon all-policy theorem (2026-10-18)

The historical G3 statements above are superseded for the canonical E-world
family by
[`eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md`](eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md).
Combining the proved pair-separation inequality with the all-state
no-hedging lemma gives, for `D=H-1`, an explicit all-causal-policy lower
bound `abD/(a+b(D-1))` on post-initial admitted overflow, where
`a=L(N-1)/2` and `b=E_S/4`. With a one-update reachable zero-overflow
pressure, requested value is exactly the unavoidable initial `E_S`, so this
is a positive shared-prior value gap. The exact rational DP audit covers 156
parameter/horizon cells and passes every bound; see
[`eworld_finite_horizon_lower_bound_results_2026-10-18.md`](eworld_finite_horizon_lower_bound_results_2026-10-18.md).

This closes the finite-horizon all-policy proof gap for the stated family.
It does **not** close the conference novelty gate: the fixed family has an
exact outcome-cost adaptive-testing representation, and the prior-art
comparison for the new quantitative theorem remains to be completed. The
older comments that called G3 open refer to the state before this update.

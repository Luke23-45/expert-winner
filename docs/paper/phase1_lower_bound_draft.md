# Phase 1 lower bound: draft theorem (v0.3)

**Status:** the MoE construction and value-gap proof are retained; the reduction audit finds that the lower-bound argument reduces to a two-point censored newsvendor game. It does not clear the novelty gate in `conference_roadmap.md`.
**Branch:** `feat/research-censored-feedback`.
**Depends on:** `phase1_controller_model.md` (v0.3) for policy classes,
comparator, and cost definitions. Uses the implemented dynamics
\(q^{+} = \Pi_g((1-\delta)q + \eta\gamma\varepsilon)\).

This document proves a quantitative shared-distribution value gap between
requested-observation and admitted-observation policies on a paired
environment. It does **not** claim a robust minimax value gap (see the
remark after the theorem). No experiments were run; the predictions in §7
are falsifiable and precede any sweep.

---

## 1. Fixed assumptions

| Symbol | Value / range | Role |
|---|---|---|
| \(E\) | \(3\) | experts |
| \(K\) | \(1\) | top-1 routing |
| \(T\) | \(120\) | tokens per round |
| \(C\) | \((50,50,30)\) | capacity; expert 3 is a limited sink |
| \(\mu\) | \((1/3,1/3,1/3)\) | target (fixed; not used by the overflow cost) |
| \(q_0\) | \(0\) | initial pressure |
| \(\delta\) | \(0\) | no leak (the construction uses \(H=2\); \(\delta\) is irrelevant from \(q_0=0\)) |
| \(H\) | \(2\) | horizon: one observation round, one cost round |
| \(\gamma>0,\ \eta>0\) | fixed | shared dynamics parameters |
| tie rule | lower expert index wins equal scores | resolves threshold equalities below |
| \(0 < m < M\) | affinity margins | two threshold levels; affinity bound \(M_{\text{bound}} = 2M\) |
| \(B \ge B_0\) | action bound | \(B_0 = M\sqrt{2/3}/(\eta\gamma^2)\); §4 derives it |
| \(\nu\) | uniform on \(\{\omega,\omega'\}\) | hard distribution over the paired worlds below |

Both policy classes \(\Pi_R(B),\Pi_A(B)\) are as defined in
`phase1_controller_model.md`: causal, possibly randomized, shared update set
\(U_B = \{\varepsilon \in \mathbf{1}^\perp : \|\varepsilon\|_2 \le B\}\),
shared tie-breaking, coupled coins in paired arguments.
The cost is normalized cumulative overflow
\(O_H(\pi;\omega) = \frac{1}{HKT}\sum_{t=0}^{H-1}\|J_t\|_1\).

The affinity bound is
\(\max_{t,i,e,e'}|a_{t,i,e}-a_{t,i,e'}| \le 2M =: M_{\text{bound}}\);
all affinities below respect it.

---

## 2. Construction: paired worlds

Both worlds are **oblivious** (affinity sequences fixed in advance, not
adaptive) and **persistent** (same affinities every round). \(T=120\).

**World \(\omega\).** Round-\(t\) affinities \(a_t = a_0\) for all \(t\):

- 20 tokens: \(a_{i} = (+m,\,-M,\,0)\). Want expert 1 (low margin \(m\));
  second choice expert 3.
- 50 tokens: \(a_{i} = (+M,\,-M,\,0)\). Want expert 1 (high margin \(M\));
  second choice expert 3.
- 50 tokens: \(a_{i} = (-M,\,+m,\,0)\). Want expert 2 (low margin \(m\));
  second choice expert 3.

**World \(\omega'\).** Round-\(t\) affinities \(a'_t = a'_0\) for all \(t\):

- 20 tokens: \(a'_{i} = (-M,\,+m,\,0)\). Want expert 2 (low margin);
  second choice expert 3.
- 50 tokens: \(a'_{i} = (-M,\,+M,\,0)\). Want expert 2 (high margin);
  second choice expert 3.
- 50 tokens: \(a'_{i} = (+m,\,-M,\,0)\). Want expert 1 (low margin \(m\));
  second choice expert 3.

### Lemma 1 (Round-0 requests and admission).

At \(q_0 = 0\) with the shared tie-breaking rule:

- In \(\omega\): \(R_0 = (70,50,0)\), hence \(A_0 = (\min(70,50),\min(50,50),0)
  = (50,50,0)\) and \(J_0 = (20,0,0)\), \(\|J_0\|_1 = 20\).
- In \(\omega'\): \(R'_0 = (50,70,0)\), hence \(A'_0 = (50,50,0)\) and
  \(J'_0 = (0,20,0)\), \(\|J'_0\|_1 = 20\).

*Proof.* At \(q_0=0\) scores equal affinities. In \(\omega\):
\(s_i = (m,-M,0)\) has unique argmax expert 1 (\(m > 0 > -M\));
\(s_i = (M,-M,0)\) has unique argmax expert 1;
\(s_i = (-M,m,0)\) has unique argmax expert 2 (\(m > 0 > -M\)).
Counts: \(70,50,0\). Admission truncates at \(C=(50,50,30)\).
The \(\omega'\) case is symmetric. ∎

**Corollary (admitted-policy blindness).**
\(A_0 = A'_0 = (50,50,0)\). Both worlds saturate experts \(\{1,2\}\).
Any \(\pi_A \in \Pi_A(B)\) observes the identical Round-0 history in both
worlds, so (with coupled coins) it selects the identical
\(\varepsilon_0^A\) and reaches the identical \(q_1^A\) in both worlds.
The total Round-0 overflow \(\|J_0\|_1 = 20\) is exactly observed
(\(= KT - \sum_e A_{0,e}\)), but its allocation — 20 on expert 1 vs 20 on
expert 2 — is censored.

### Lemma 2 (Top-K realizability).

The request vectors \(R_0=(70,50,0)\) and \(R'_0=(50,70,0)\) are realized
by the stated Top-K router at \(q_0=0\) (Lemma 1, explicit affinities).
For Round 1, no request vector is prescribed: \(R_1\) is whatever the
Top-K router produces from \((a_0, q_1)\). The flip analysis in §3
computes it exactly from the affinities, so every visited
\((\text{affinities}, \text{pressure})\) pair is realizable by
construction. The affinity bound \(M_{\text{bound}} = 2M\) holds:
\(\max|a_{i,e}-a_{i,e'}| = 2M\) (high-margin tokens).

---

## 3. Pressure-to-overflow map (the MoE mechanism)

Fix \(\omega\). First consider a gauge representative with \(q_3=0\).
Round-1 scores are
\(s_{i,e} = a_{i,e} - \gamma q_e\). Flips occur at Top-K thresholds:

- 20 low-margin tokens (want 1): flip \(1\to3\) iff \(q_1 > m/\gamma\).
- 50 high-margin tokens (want 1): flip \(1\to3\) iff \(q_1 > M/\gamma\).
- 50 tokens (want 2, low margin \(m\)): flip \(2\to3\) iff \(q_2 > m/\gamma\).
  (They never flip \(2\to1\): \(s_{i,1} = -\gamma q_1 \le 0 = s_{i,3}\)
  whenever expert 1 does not beat expert 3.)

Let \(x = \mathbf{1}\{q_1 > m/\gamma\}\), \(y = \mathbf{1}\{q_1 > M/\gamma\}\),
\(z = \mathbf{1}\{q_2 > m/\gamma\}\) (so \(y=1 \Rightarrow x=1\)).
Then

\[
R_1 = \bigl(70-20x-50y,\; 50-50z,\; 20x+50y+50z\bigr)
\]

and with \(C=(50,50,30)\),

\[
\,f_\omega(q_1,q_2) := \|J_1\|_1
   = [20-20x-50y]_+ + [20x+50y+50z-30]_+\,  \tag{1}
\]

(the middle term \([50-50z-50]_+ = 0\)).
The **sweet spot** \(m/\gamma < q_1 \le M/\gamma,\ q_2 \le m/\gamma\)
gives \(x=1,y=0,z=0\), hence \(R_1=(50,50,20)\) and \(f_\omega = 0\):
exactly the 20 excess tokens are deflected to the sink, which has room
(\(20 \le 30\)).

By the symmetric construction,
\(f_{\omega'}(q_1,q_2) = f_\omega(q_2,q_1)\).

The formula above is stated for \(q_3=0\), not for every gauge state.
For any \(q\in\mathcal Q\), define relative pressures
\(u=\gamma(q_1-q_3)\) and \(v=\gamma(q_2-q_3)\). Routing is invariant
to common shifts, so its scores are equivalent to
\((a_1-u,a_2-v,a_3)\). The relative pressures \(u,v\) can be negative;
Lemma 4 covers those states directly rather than assuming they have a
nonnegative representative with \(q_3=0\).

### Lemma 3 (Tailored policies achieve zero Round-1 overflow).

Assume \(B \ge B_0 := M\sqrt{2/3}/(\eta\gamma^2)\).
There exist \(\pi_R \in \Pi_R(B)\) with

\[
\|J_1\|_1 = 0 \quad \text{in } \omega
\quad\text{and}\quad
\|J_1\|_1 = 0 \quad \text{in } \omega'.
\]

*Proof.* \(\pi_R\) observes \(R_0=(70,50,0)\), identifies \(\omega\)
(\(R'_0=(50,70,0)\) is the only alternative under \(\nu\)), and knows
\(\nu\) (hence the margin structure). It selects
\(\varepsilon_0\) with \(\Pi_g(\eta\gamma\varepsilon_0) = (L,0,0)\) for
any \(L \in (m/\gamma, M/\gamma]\).
Such an \(\varepsilon_0\) exists in \(U_B\):
take \(\varepsilon_0 = \frac{L}{3\eta\gamma}(2,-1,-1) \in \mathbf{1}^\perp\);
then \(\eta\gamma\varepsilon_0 = (\tfrac{2L}{3},-\tfrac{L}{3},-\tfrac{L}{3})\),
\(\Pi_g\) gives \((L,0,0)\), and
\(\|\varepsilon_0\|_2 = \frac{L\sqrt{2/3}}{\eta\gamma}
  \le \frac{M\sqrt{2/3}}{\eta\gamma^2} = B_0 \le B\).
By (1) with \(x=1,y=0,z=0\): \(f_\omega = 0\).
The \(\omega'\) case is symmetric (pressure expert 2). ∎

Hence \(V_R(2;\nu) \le \frac{20 + 0}{2\cdot 120} = \frac{1}{12}\):
Round 0 contributes \(\|J_0\|_1 = 20\) (sunk), Round 1 contributes \(0\),
normalized by \(HKT = 240\).

### Lemma 4 (No single pressure hedges both worlds).

For a reachable gauge state \(q\in\mathcal Q\), define
\(F_\omega(q):=\|J_1^\omega(q)\|_1\) and
\(F_{\omega'}(q):=\|J_1^{\omega'}(q)\|_1\), using the same state in
both environments.

For **every reachable gauge state** \(q\in\mathcal Q\),

\[
F_\omega(q) + F_{\omega'}(q) \;\ge\; 40,
\]

i.e. the average Round-1 overflow under any single admitted-policy
pressure is at least \(20\).

*Proof.* Put \(u=\gamma(q_1-q_3)\) and \(v=\gamma(q_2-q_3)\).
These relative pressures determine routing and may be negative. Split the
plane into four regions.

1. If \(u\le m\) and \(v\le m\), each token's intended expert has score
   at least zero. The lower-index tie rule sends equality to expert 1 or
   2 rather than the sink. Thus, in either world all 120 requests go to
   experts 1 and 2. Since their combined capacity is 100, each world has
   overflow at least 20.
2. If \(u>m\) and \(v\le m\), consider \(\omega'\). Its 70 tokens
   intended for expert 2 still choose expert 2: their scores are
   \(m-v\ge0\) or \(M-v>0\), and expert 1 scores below zero for those
   token types. The 50 low-margin expert-1 tokens have expert-1 score
   \(m-u<0\), so they choose either expert 2 or the sink. If they choose
   expert 2, it receives at least 120 requests and overflows by at least
   70. If they choose the sink, expert 2 overflows by 20 and the sink's
   50 requests overflow its capacity by 20. Hence \(F_{\omega'}(q)\ge40\).
3. The case \(u\le m\) and \(v>m\) is symmetric: in \(\omega\),
   either expert 1 receives at least 120 requests or experts 1 and 3
   each overflow by at least 20. Hence \(F_\omega(q)\ge40\).
4. If \(u>m\) and \(v>m\), then \(q_1>q_3\) and \(q_2>q_3\).
   Because \(q\in\mathcal Q\) has minimum coordinate zero, \(q_3=0\).
   Formula (1) applies. Classifying \(u,v\) into \((m,M]\) and
   \((M,\infty)\), the overflow pairs \((F_\omega,F_{\omega'})\) are
   \((40,40)\), \((40,90)\), \((90,40)\), and \((90,90)\), respectively.
   Their sums are at least 80.

The first three cases give a pairwise sum of at least 40, and the last
case gives at least 80. These cases cover all relative pressures, proving
the claim. ∎
**Remark (MoE realization of a paired-world cost conflict).**
The mutual exclusivity of the sweet spots runs through three
MoE-specific elements:
(a) **Hard Top-K thresholds** — this exact piecewise-constant payoff
calculation uses hard Top-1 routing. It does not establish that an
analogous lower bound vanishes under a smooth router.
(b) **Limited sink** — \(C_3 = 30 < 40 = 20+20\) is what makes hedging
harmful rather than safe; it is the heterogeneous-capacity structure
(T7) doing quantitative work.
(c) **Margin heterogeneity** (\(m < M\)) — the censoring hides not only
*which* expert has the excess but the *margin structure* that determines
how much pressure is safe. \(A_0=(50,50,0)\) reveals neither.

This construction does not yet establish that the gauge projection is
essential: routing depends only on pressure differences, and the proof
uses the projection to select a canonical state representative. A
gauge-free comparison needs a precisely defined alternative plant and
action set, followed by a proof that the value changes. Likewise, \(\mu\)
is uniform and does not affect this overflow objective or the arbitrary
feedback policy class. The result is not a target-dependent theorem.

---

## 4. The action bound \(B_0\)

Lemma 3 requires reaching \(q_1 = (L,0,0)\) with
\(L \in (m/\gamma, M/\gamma]\). The derivation in Lemma 3 gives
\(\|\varepsilon_0\|_2 = L\sqrt{2/3}/(\eta\gamma) \le
M\sqrt{2/3}/(\eta\gamma^2) =: B_0\).
\(B_0\) is **not** tuned to manufacture the gap:
it is the norm cost of the gauge-quotient action that the tailored
policy needs, computed from the dynamics. Any \(B \ge B_0\) works;
larger \(B\) does not help \(\pi_A\) (Lemma 4 holds for all \(q\),
hence all \(B\)).

---

## 5. Theorem (shared-distribution value gap)

Under the assumptions of §1, with \(\nu\) uniform on \(\{\omega,\omega'\}\),

\[
\;\Delta_2(\nu) \;=\; V_A(2;\nu) - V_R(2;\nu) \;\ge\; \frac{1}{12}\;
\]

in normalized overflow units.

*Proof.*
\(V_R(2;\nu) \le \frac{1}{12}\) by Lemma 3
(\(\frac{20+0}{240}\) per world).
For any \(\pi_A \in \Pi_A(B)\) (possibly randomized, coins \(\xi\) coupled
across worlds): it selects \(q_1^A = q_1^A(\xi)\), one pressure per coin
realization, for both worlds (Corollary to Lemma 1). Its expected cost is
\(\mathbb{E}_{\omega''\sim\nu}\mathbb{E}_{\xi}
   \frac{20 + f_{\omega''}(q_1^A(\xi))}{240}\).
For each fixed \(\xi\), Lemma 4 gives
\(f_{\omega}(q_1^A(\xi)) + f_{\omega'}(q_1^A(\xi)) \ge 40\);
taking \(\mathbb{E}_\xi\) preserves the bound. Hence the
\(\nu\)-expected cost is \(\ge \frac{20 + 20}{240} = \frac{1}{6}\).
Taking \(\inf_{\pi_A}\): \(V_A(2;\nu) \ge \frac{1}{6}\).
Subtract: \(\Delta_2(\nu) \ge \frac{1}{6} - \frac{1}{12} = \frac{1}{12}\). ∎

### Worst-case paired-policy guarantee (exact quantifiers)

Let \(\pi_A^\nu, \pi_R^\nu\) be \(\varepsilon\)-optimal for
\(V_A(2;\nu), V_R(2;\nu)\) (\(\varepsilon \ge 0\)), with coupled coins.
Then

\[
\sup_{\omega''\in\{\omega,\omega'\}}
\Bigl[\bar O_2(\pi_A^\nu;\omega'') - \bar O_2(\pi_R^\nu;\omega'')\Bigr]
\;\ge\; \frac{1}{12} - \varepsilon .
\]

*Proof.* The expected difference under \(\nu\) is at least
\(V_A - (V_R + \varepsilon) \ge \frac{1}{12} - \varepsilon\);
a supremum over \(\operatorname{supp}\nu\) is at least its average.
Both policies are fixed causal maps; each bracket compares them on the
same affinity sequence. ∎

### Remark: What this theorem does not claim

This does **not** establish
\(\inf_{\pi_A}\sup_{\omega} - \inf_{\pi_R}\sup_{\omega} > 0\)
(a robust minimax value gap with separately optimized worst cases).
The guarantee is the worst-case *paired-policy* advantage derived from
the shared hard distribution, exactly as scoped in
`phase1_controller_model.md` §3. The two worlds are fixed and oblivious;
no adaptive environment is considered.

---

## 6. Reduction audit (completed for this theorem; 2026-10-16)

The paired-world value-gap argument has an explicit reduction to a
two-point censored newsvendor decision. The two environments can have
identical historical sales and stockout indicators while their clairvoyant
orders differ. The resulting equal-prior regret game has endpoint loss
pairs \((0,40)\), \((40,0)\), and blind value 20. Lemma 4 supplies the same
pairwise loss lower bound for every common admitted-policy pressure; the
MoE sweet spots attain the same endpoint values. The round-0 overflow is
common sunk cost and cancels from the value difference.

The explicit construction, cost scaling, history mapping, and limitations
are in [`phase1_reduction_audit_2026-10-16.md`](phase1_reduction_audit_2026-10-16.md).
The primary source is Kumar and Mouchtaki, [*What is the Value of Censored
Data?*](https://arxiv.org/abs/2602.16842), whose model maps censored
historical demand observations to a future inventory action and evaluates
regret against the known-distribution optimum.

**Decision:** this theorem remains a valid MoE realization of the game,
but its value-gap proof does not survive the roadmap's reduction attack as
a new centerpiece. Its hard Top-1 routing and heterogeneous capacities
generate the loss table; after that, the lower bound is a generic binary
value-of-information argument. At \(H=2\), the pressure update selects one
final-round action and does not establish a repeated closed-loop effect.
The gauge projection is not shown to be essential, and uniform \(\mu\) is
not load-bearing. Do not claim those as contributions of this theorem.

Other cited partial-monitoring, censored-bandit, and queueing papers remain
related-work obligations, but they are not needed to reach this stop
decision: the primary reduction target already absorbs the current gap
argument. Follow the roadmap stop rule and develop a different theorem
before running experiments.

---

## 7. Falsifiable predictions (pre-registered, no runs yet)

The theorem predicts, for the synthetic harness extended with a limited
sink and two margin levels:

1. **Sweet-spot existence:** with \(q_3=0\) and the other expert's
   pressure \(\le m/\gamma\), an \(R\)-informed controller that pressures
   the excess expert to \(q \in (m/\gamma, M/\gamma]\) achieves zero
   Round-1 overflow; pressure \(\le m/\gamma\) leaves baseline overflow
   20, and pressure \(>M/\gamma\) gives overflow at least 40.
2. **Hedging harm:** an \(A\)-informed controller that pressures both
   saturated experts into their sweet spots incurs **more** overflow
   than pressuring one (Lemma 4, region "sweet × sweet": 40 vs 20).
3. **Gap scale:** the \(R\)-vs-\(A\) normalized overflow gap is bounded
   away from zero independently of \(B\) (for \(B \ge B_0\)); increasing
   \(B\) does not close it.

These are testable in the existing harness (new affinity/margin
config + sink capacity). **No sweeps until these are written as
pass/fail criteria** — this section is the first half; the criteria
are the second half and belong in the experiment plan, not here.

---

## Appendix A. Literature sweep summary (2026-10-16)

Five search angles, full details in the sweep report:
**Kumar–Mouchtaki reduction:** explicit for the current gap argument (see
§6 and the audit document). **Other related work:** Mon-MDPs 2402.06819
(indistinguishable-set formalism); Bengs & Hüllermeier 2011.00813 (censored-bandit
lower-bound structure); Chadaga & Modiano 2609.28219
(partial-observation load balancing, algorithmic only); Zubeldia 1807.02882
(memory-bounded LB lower bound, different mechanism); Ledford & Regli
2605.27076 (threshold-bandit censoring, upper bounds only); queue-regret
2005.05206 (unknown service rates, not censored observations).
**Explicit no-hit angles:** partial monitoring + switching dynamics;
Top-K/argmax routing + lower bound + censoring; value-of-information lower
bound in closed-loop control; min-structure feedback + LB lower bound;
gauge/translation-invariance + lower bounds.
The source sweep did not establish novelty. The explicit reduction in §6
shows that the current value-gap argument is already captured by a simple
two-point censored newsvendor instance.

# Prior-Art Comparison, 2026-10-16: feedback load control for MoE routing

**Date:** 2026-10-16. **Branch:** `feat/paper-feedback-moe-routing`.
**Purpose:** the reviewer's step 1 — a dated claim-by-claim comparison of the
papers the v3 literature review missed (φ-Balancing, arXiv:2605.15403; and
"A Theoretical Framework for Auxiliary-Loss-Free Load Balancing",
arXiv:2512.03915) against ID Balancing (arXiv:2609.39137), DeepSeek
loss-free balancing (arXiv:2408.15664), and our methods. Columns follow the
reviewer's requested schema: state update | feedback signal |
capacity/admission model | target | theory | model scale |
quality/efficiency evidence.

**Evidence labels:** `[VERIFIED-PRIMARY]` = I read the paper's full text in
this pass (PDF via arXiv, pdftotext). `[VERIFIED-ABSTRACT]` = abstract only.
`[SECONDARY]` = reputable third-party/impl notes. `[NOT FOUND]` = searched,
nothing located. `[SYNTHESIS]` = my inference from established results, not a
literature claim. Claims marked `(v3)` were verified in the earlier v3 deep
review and are re-stated, not re-verified, unless noted.

**How the two new papers were read:** full PDFs downloaded 2026-10-16 and
converted with pdftotext (φ-Balancing: 2173 lines; 2512.03915: 3854 lines).
Full-text term searches were run for: windup, saturation, censored, dropped,
"token drop", "capacity constraint", "non-uniform", "expert capacity",
overflow, admission, censor. Hit counts are reported with context below.

---

## 1. Full-text censoring-term search results (the load-bearing check)

**φ-Balancing (2605.15403):** windup 0, saturation 0, censored 0, dropped 0,
"token drop" 0, "capacity constraint" 0, non-uniform 0, overflow 0.
"expert capacity" 2 — both about *model* capacity ("vast expert capacity",
"capacity violations" = MaxVio_global, a balance metric defined as deviation
of the global mean routing distribution from uniform, Appendix A — not token
drops) `[VERIFIED-PRIMARY]`.

**2512.03915:** windup 0, saturation 0, censored 0, dropped 0, "token drop" 0,
"capacity constraint" 0, non-uniform 0, "expert capacity" 0, overflow 0,
admission 0, censor 0 `[VERIFIED-PRIMARY]`.

**ID Balancing (2609.39137):** verified in the earlier pass and re-confirmed
2026-10-16 via fresh PDF download + pdftotext: windup 0, saturation 0,
dropped 0, censor 0; "capacity" 7 hits, all about *model* capacity
("model capacity grows", "using the capacity of larger, sparser MoE models"),
never per-expert capacity constraints `[VERIFIED-PRIMARY]`.

**Result:** none of the three papers analyzes what capacity saturation does
to the feedback signal. The censoring lane is unoccupied.

---

## 2. Claim-by-claim comparison table

### ID Balancing — Jin et al. (Qwen Team, Alibaba), arXiv:2609.39137 (Sept 2026)

| column | fact |
|---|---|
| state update | Per-expert bias `b_i`; integral–derivative controller: magnitude-aware integral `K_i·e_i` + worsening-gated derivative `K_d·g_i·Δe_i` with `g_i = 1[e_prev·Δe > 0]`; zero-mean re-centering after each update, justified explicitly because "adding the same constant to every expert bias leaves the score ranking and the selected set unchanged" `[VERIFIED-PRIMARY]` (§2.2–§3) |
| feedback signal | `e_i = (nbar − n_i)/nbar`, `n_i` = "number of tokens assigned to expert i" — post-assignment hard counts `[VERIFIED-PRIMARY]` (§2.2) |
| capacity/admission model | none modeled; no dropping, no censoring analysis (term search above) `[VERIFIED-PRIMARY]` |
| target | uniform `nbar` (mean load) `[VERIFIED-PRIMARY]` |
| theory | PID taxonomy: unifies DeepSeek's method as fixed-step *integral* control and Kimi K3's quantile balancing as generalized *proportional* control; proposes the ID (integral–derivative) controller. No convergence/regret theorems located `[VERIFIED-PRIMARY]` |
| model scale | Top-10/Top-5/Top-3 over 768 experts; 18.9B→69.9B params; 120B tokens `(v3)` `[VERIFIED-PRIMARY]` |
| quality/efficiency evidence | competitive LM loss at trained scale `(v3)` `[VERIFIED-PRIMARY]` |

### φ-Balancing — Chen et al. (UT Austin / Northwestern), arXiv:2605.15403 (May 2026), ICML 2026

| column | fact |
|---|---|
| state update | Dual price `q_{t+1} ← ∇φ(m_{t+1})` where `m_{t+1} ← (1−η)m_t + ηp_t` is an EMA of batch routing distributions; strictly convex symmetric differentiable potential `φ` (best: negative entropy). Acts **through the loss**, not routing scores: `L_aux = Σ_e ∇φ(m)_e·p_e`, model updated with `∇L_task + α·E·L_aux`, stop-gradient on `m` `[VERIFIED-PRIMARY]` (Alg. 1, §3.1, eq. 12) |
| feedback signal | `p_t` = batch-mean **soft** routing probabilities `p(x;θ) = softmax(W_r x)` — explicitly NOT hard dispatch counts: "our method relies solely on the dual variable `q`, which tracks the history of the soft routing probabilities… avoiding the instability associated with discrete routing decisions" `[VERIFIED-PRIMARY]` (§3.1) |
| capacity/admission model | none — no per-expert capacity, no dropping, no censoring analysis (term search §1) `[VERIFIED-PRIMARY]` |
| target | uniform (symmetric `φ`, population-level uniform utilization) `[VERIFIED-PRIMARY]` (§3) |
| theory | Fenchel duality → min-max → online mirror descent yields the EMA closed form (Beck & Teboulle 2003; Rockafellar Thm 26.5 — classical results, Appendix B). No regret bound; no closed-loop convergence theorem for routing `[VERIFIED-PRIMARY]` |
| model scale | Gemma MoE pretraining on C4, top-2, 111M–986M active params, E ∈ {8,…,128}, granularity sweep G ∈ {2,…,32}; downstream fine-tuning on Moonlight-16B-A3B-Instruct `[VERIFIED-PRIMARY]` (§4) |
| quality/efficiency evidence | lower validation loss than Switch-style (ST-MoE) and loss-free baselines across scales; downstream wins on Math500, LiveBench, HumanEval, BBH `[VERIFIED-PRIMARY]` (§4) |

### A Theoretical Framework for Auxiliary-Loss-Free Load Balancing — Han & Zhong (Chicago Booth), arXiv:2512.03915 (Dec 2025, v3 Apr 2026)

| column | fact |
|---|---|
| state update | Single-shot primal-dual on the assignment LP: primal `x_ik = 1{k ∈ TopK(γ_ik + p_k)}`; dual `p_k ← p_k + ε_k(L − A_k)`, `A_k = Σ_i x_ik` (assigned load). DeepSeek's deployed rule is the sign version `p_k ← p_k ∓ u` (`u = 0.001`), quoted in their §1.3 `[VERIFIED-PRIMARY]` (§2.2, eq. 7–8) |
| feedback signal | `A_k` = assigned load per batch vs target `L`; no dropping exists in the model, so assigned = admitted `[VERIFIED-PRIMARY]` (§2) |
| capacity/admission model | none — the primal is an exact-balance assignment IP (`Σ_i x_ik = L`, `L = KT/E` with exact divisibility assumed); no capacity constraints, no censoring (term search §1) `[VERIFIED-PRIMARY]` |
| target | uniform `L = KT/E` `[VERIFIED-PRIMARY]` (§2.1) |
| theory | **Yes — the strongest theory among comparators:** monotonic Lagrangian-improvement condition (Thm 1), overloaded→underloaded preference rule (Thm 5), approximate-balance band-stability (Thm 9), strong convexity of the expected dual objective (§5.6) → logarithmic expected regret bound (Thm 17) `[VERIFIED-PRIMARY]` |
| model scale | 1B-parameter DeepSeekMoE experiments (validation load imbalance + validation loss) `[VERIFIED-PRIMARY]` (abstract, §3, Fig. 2) |
| quality/efficiency evidence | 1B DeepSeekMoE training curves: imbalance (avg load deviation from `L`) and validation loss `[VERIFIED-PRIMARY]` |

### DeepSeek loss-free balancing — Wang et al., arXiv:2408.15664 (2024)

| column | fact |
|---|---|
| state update | `b_i ← b_i − u` if load > `L`; `b_i + u` if load < `L` (`u = 0.001`); bias added to scores before top-K, selection-only, treated as constant in backprop `[VERIFIED-PRIMARY]` (via 2512.03915 §1.3 quotation); `[VERIFIED-ABSTRACT]` for the original |
| feedback signal | per-expert assigned load vs `L` `[VERIFIED-ABSTRACT]` |
| capacity/admission model | none in the method; deployed in dropless training `[VERIFIED-ABSTRACT]`; `[SYNTHESIS]` the assigned/admitted distinction is invisible there |
| target | uniform `L` `[VERIFIED-ABSTRACT]` |
| theory | none in the original (heuristic); 2512.03915 now supplies the primal-dual theory (row above) |
| model scale | 1B–3B DeepSeekMoE (Wang et al. 2024) `[VERIFIED-PRIMARY]` (via 2512 §1.3); deployed at 671B/37B in DeepSeek-V3 `(v3)` `[SECONDARY]` |
| quality/efficiency evidence | empirical benefits on 1B–3B models; at-scale deployment in V3 training `(v3)` |

### Our methods (formulas read from `src/moe_control/controllers/base.py`, 2026-10-16 — never from memory)

| method | feedback `ε` (code) |
|---|---|
| `(R)` requested (`RequestedFeedback`) | `R/(KT) − μ`; runner `q⁺ = Π_g((1−δ)q + ηγε)` |
| `(A)` admitted (`AdmittedFeedback`) | `A/(KT) − μ`, canonical admission `A = min(R,C)` |
| `(A₀)` admitted_centered (`AdmittedCenteredFeedback`) | `P₀(A/(KT))` |
| `(C)` capacity_relative (`CapacityRelativeFeedback`) | `P₀(R/(KT) − C/(KT))` |
| `(AW)` admitted_antiwindup (`AdmittedAntiwindupFeedback`) | `P₀(g)`; `g_e = A_e/(KT) − μ_e` on unsaturated `U`, unsaturated mean on saturated `S`; `ε = 0` if `S` = all experts |
| `(bias)` bias_integral (`BiasIntegralFeedback`) | `b ← b + bias_gamma·sign(A − mean(A))`; bias added to scores with sign +1, selection-only |

Our columns: capacity/admission model = **explicit** per-expert `C`, canonical admission, dropped `J = [R−C]_+`; target = general `μ` (uniform and non-uniform studied); theory = `docs/paper/formal_core.md` T1–T8, L1 (equivalences, censoring fiber, phantom gradients, hetero-divergence theorem, leak-freeze closed form, t_flip law); scale = synthetic E=8/K=2 CPU (64+93+79 deterministic runs) + toy trained-router feasibility probe only; quality evidence = **none at LM scale** (stated as the open bar).

---

## 3. Per-paper novelty verdicts

### ID Balancing — no change to existing verdicts
Does not threaten the censoring lane (verified zero treatment, §1). It predates, as already recorded: the PID framing (never claim), magnitude-aware updates (never claim), and the zero-mean-centering *operation* (never claim; only the quotient theory is ours). Our lane — what saturation does to the *observation* — is untouched.

### φ-Balancing — NEW assessment (was not in the v3 review)
**Does not threaten the censoring lane** (zero hits, §1; it deliberately avoids hard dispatch statistics altogether, using soft probabilities). Two honest positionings required:
1. Its dual price `q = ∇φ(m)` **is** a persistent per-expert load-error state — the closest non-bias-controller analogue of a "pressure state" in the literature. It is loss-actuated (via `L_aux`), not routing-actuated, and has no gauge/zero-sum structure (mirror descent on the dual, not a projected feedback loop). Verdict: does not predate our gauge-quotient theory (vi), but must be cited as adjacent stateful-load-tracking prior art. Add to the never-claim list: "persistent per-expert load state" as a concept.
2. It is an **aux-loss method**, not a feedback controller on routing scores — a different mechanism family from both our pressure controllers and the deployed bias controllers. Its population-vs-minibatch argument (Jensen gap, eq. 8) is orthogonal to our censoring argument.

### 2512.03915 — NEW assessment; the most theoretically adjacent paper
**Does not threaten the censoring lane** (zero hits, §1 — its model cannot express capacity, dropping, or censoring). But it **partially predates the "primal-dual/subgradient theory of feedback load balancing" framing**: it casts ALF-LB as single-shot primal-dual on the assignment LP, with monotonicity, band-stability, and regret guarantees. Honest split:
- Theirs: primal-dual theory of the *uncensored* bias update; dual variables unconstrained; uniform target; guarantees about convergence-to-balance.
- Ours: gauge-quotient theory (`R^E/span{1}`, `Π_g`, quotient subgradient of the hard Top-K potential); the *censored* observation regime (T3–T7); target dependence; explicit failure conditions under saturation.
- What we must do: **cite 2512.03915 as the primal-dual theory of ALF-LB** and scope our P3-adjacent claims as the capacity-censored + gauge extension. Add to the never-claim list: "first (sub)gradient/primal-dual theory of feedback load balancing."
- Note a genuine mathematical adjacency the paper should acknowledge [corrected 2026-10-16 after direct verification against their LP (4) and dual: the "common-mode invariance of their dual objective" does NOT hold for top-K with K>1 — shifting all (y_i,p_k) by c changes the objective by c·T·(1−K), vanishing only for top-1]: what does hold is (i) their primal assignment `x_ik = 1{k ∈ TopK(γ_ik + p_k)}` is invariant to common-mode shifts of `p_k` (top-K is translation-invariant), so the dual's common mode never affects the primal trajectory; and (ii) their uniform-step dual update preserves `Σ_k p_k` exactly, since `Σ_k(L − A_k) = LE − KT = 0` by exact balance. I.e., their scheme implicitly evolves on the quotient `R^E/span{1}` — the same gauge quotient as ours — but unnamed and unexploited: no projection operator, no quotient dynamics analysis. Our `Π_g` makes the gauge structure explicit and load-bearing (equivalences T1/T2, quotient subgradient P3). Adjacent, not the same — cite, don't ignore.

### DeepSeek loss-free — no change
Heuristic, no theory of its own, no censoring analysis. 2512.03915 is now its theory reference; cite both together.

---

## 4. What changed vs `novelty_outline.md` §1 (2026-10-11)

- **(i) requested-vs-admitted axis:** candidate, not cleared. Neither of these two papers names the axis, but that limited search is not a novelty proof.
- **(ii) censoring formalization:** candidate claims need separate audits. The clipping fiber is a generic censoring object; the current Phase 1 gap reduces to a two-point censored-newsvendor game (see `phase1_reduction_audit_2026-10-16.md`). The independent saturation-dynamics results are not adjudicated by that reduction.
- **(iii) target-aware vs target-blind:** candidate, not cleared. Both papers use uniform targets, but this does not establish priority against the wider load-balancing and control literature.
- **(iv) t_flip law:** unchanged — CLASSICAL mechanism, ours as verified law.
- **(v) anti-windup:** unchanged — CLASSICAL mechanism, honest negative result.
- **(vi) gauge-projection formulation:** verdict stays PARTIALLY PREDATED, must-cite list grows — add φ-Balancing's dual price `q = ∇φ(m)` as adjacent stateful-load-tracking prior art (loss-actuated, no gauge structure). The claimed-novel part remains exactly the quotient formal theory.
- **NEW (vii): primal-dual theory of feedback load balancing** — PARTIALLY PREDATED by 2512.03915 (single-shot primal-dual, monotonicity, band-stability, log regret, for the uncensored uniform-target case). Our claimed-novel part: the capacity-censored extension, gauge quotient structure, target dependence, and failure conditions. Never claim "first primal-dual/subgradient theory of feedback load balancing."
- **Never-claim list additions:** (a) "persistent per-expert load state" as a concept (φ-Balancing's dual price); (b) "first (sub)gradient/primal-dual theory of feedback load balancing" (2512.03915).

---

## 5. Censored-decision prior art + systems boundary (2026-10-16, exploration branch)

Full-text reads (PDF via arXiv, pdftotext) on the exploration branch.
Every claim [VERIFIED-PRIMARY] unless noted. Independently spot-checked
by the owner against the PDFs.

### 5.1 Kumar & Mouchtaki, "What is the Value of Censored Data?" (2602.16842)

Data-driven newsvendor under censored demand. Signal: historical sales
`x_i = min(D_i, I_i)` (demand censored by past inventory levels).
Decision: ONE inventory quantity, chosen offline — one-shot, no
dynamics, no persistent state. Objective: worst-case expected regret
`sup_F E[c(a,F) − opt(F)]` with overage/underage costs. Thm 1: exact
finite-dimensional characterization of worst-case regret for
piecewise-separable policies. Key line (verified verbatim): "distributions
with different unobserved tails remain indistinguishable" → irreducible
regret from passive censored data; targeted uncensored observations cut
worst-case regret ~23.5% (1 sample) to ~61% (5 samples) at n=50.

**Boundary:** closest structural neighbor to our lower-bound *shape*
(censoring → identification set → decision regret → extra information
helps). The current Phase 1 draft has an (H=2) plant, but only one
post-observation action affects its final-round cost. The explicit
reduction in `phase1_reduction_audit_2026-10-16.md` maps its two-world
overflow loss pairs to a two-point newsvendor regret game with identical
censored histories. Therefore the present draft's gap argument does not
clear roadmap §3, item 1c as a new result. Top-1/capacity structure
realizes the loss table, but the proof's value gap is the generic binary
information-value gap. A later result must show a quantitative dynamic,
gauge, or signal-structure property that this reduction fails to preserve.

### 5.2 "Kalman Filtering With Censored Measurements" (2002.08597)

Tobit Type I censored 1-D measurements; recursive Bayesian estimation
of a hidden multidimensional state under first-order Markov + Gaussian
assumptions. No controller, no feedback loop, no decision.

**Boundary:** farthest of the four from our setting. Pure estimation
under strong distributional assumptions vs our worst-case control with
no distributional assumptions over the fiber. Cite to pre-empt "why
not just estimate R" — not a threat.

### 5.3 Trinity / SMEBU (2602.17004) — equation-level

Update (exact, must cite): `v_i = (n̄ − n_i)/n̄` (Eq 23, assigned
counts); `ṽ_i = tanh(κ·v_i)` (Eq 24); `Δb_i = λ·ṽ_i` (Eq 25); centering
`Δb_i −= (1/N_r)Σ_j Δb_j` (Eq 26); momentum `m_i = β·m_i +
(1−β)·Δb_i` (Eq 27); `b_i += m_i` (Eq 28); hyperparameters λ = 5×10⁻⁴,
β = 0.5, κ = 2 (verified verbatim). Rationale: tanh as continuous
relaxation of the sign operator ("can never fully settle" near
convergence), momentum as noise dampening. **Zero hits** on
censored/windup/capacity-constraint/dropped (verified); the one
"saturation" is tanh saturation speed. No capacity, no censoring, no
feedback-information analysis.

**Boundary:** direct prior art for *stable, stateful expert-bias
control*. We must distinguish our contribution from generic
momentum/damping/centering: their centering (Eq 26) is a heuristic
zero-mean; our Π_g is a gauge-quotient theory (routing depends only on
pressure differences; proved equivalences T1/T2; quotient subgradient
P3). Never claim "persistent per-expert state" as a concept (already
on the never-claim list). The censoring lane is untouched.

### 5.4 LAER-MoE (2602.11686) — planner, equation-level

Signal: `R` = routing matrix (token→expert assignments from the
router); `expert_load = R.sum(axis=0)`; `C` = capacity; N devices, E
experts. Decision: expert→device placement (greedy descending-by-load),
replica allocation, `lite_routing(R, A, N, E, C)` dispatcher, time-cost
search over layouts. Objective: minimize training step time (systems).
**Zero hits** on censored/saturation/windup (verified); the planner
consumes R directly — observed, never censored. No persistent
control state; per-iteration heuristic planner.

**Boundary (qualified per reviewer):** LAER co-optimizes placement and
routing from observed routing counts — it does dispatch tokens to
replicas, so "doesn't touch routing" would be too broad. But it
analyzes neither persistent pressure-state feedback dynamics nor an
admitted-only censoring model. Its "routing" is per-iteration
assignment given placement, not closed-loop control driven by a
censored signal.
**Notation warning:** their R (routing matrix) and C (device/token
capacity) are different objects from our R_e (per-expert requested
load) and C_e — do not let symbols collide in prose.

### 5.5 FreeBalance (2608.14205) — confirmed boundary

Pre-routing workload prediction (frozen router on earlier hidden
state) → expert swap planning → inference latency. The actual router
makes final assignments. Contribution is prediction + placement;
**not** a persistent feedback controller driven by censored admitted
counts. (Assessment from abstract + method; full-text read deferred —
structural boundary confirmed.)

### 5.6 State-constrained sensing and finite-horizon partial observability

Smallwood & Sondik (1973) formulate finite-horizon control with a hidden
finite-state process and partial observations; their value-function result
and dynamic-programming method make belief-state control an established
general comparator `[VERIFIED-PRIMARY: abstract]`
([Operations Research DOI](https://doi.org/10.1287/opre.21.5.1071)).
Davenport et al. (2016) study adaptive sensing when measurement vectors
must satisfy physical constraints, and analyze both limits and benefits of
adaptivity in that setting `[VERIFIED-PRIMARY: full text]`
([IEEE TSP DOI](https://doi.org/10.1109/TSP.2016.2597130)).
These are not the same MoE plant: the former is a general partial-observation
control framework, and the latter is constrained linear sensing/estimation.
They do, however, invalidate any broad assertion that sequential information
gathering under state/action constraints is itself new.

**Required reduction test:** express the MoE construction as a finite-horizon
belief-state control problem with pressure as the physical state, reachable
pressure changes as the action constraint, Top-K plus admission as the
observation kernel, and overflow as the stage cost. Then identify a theorem
or invariant—such as the exact Top-K score-cell arrangement, clipping map, or
gauge-induced reach metric—that is not preserved by the strongest relevant
abstract model. Until that separation is proved, the E=3 calculation is a
model-specific instance of constrained adaptive control, not evidence of a
new general theory.

### 5.7 What this changes

- **Reduction outcome:** the current paired-world Phase 1 gap reduces to
  a two-point censored newsvendor regret game. Keep it as an MoE
  realization/example, not as the novel lower-bound centerpiece. The full
  mapping is in `phase1_reduction_audit_2026-10-16.md`.
- **Next novelty gate:** any replacement theorem must identify and prove
  the quantitative property that survives both the static two-state
  reduction and the state-constrained sensing / belief-control comparison
  above (for example a multi-round state-transition effect, a
  gauge-dependent value difference, or a minimal-signal characterization).
  Merely adding MoE terminology or parameters does not pass this gate.
- **Yang & Shi 2023** (POMS, DOI 10.1111/poms.13824): journal paper,
  full text not verified — accept reviewer's characterization
  (regret under censored demand, inventory control) pending direct
  read. Same boundary shape as K&M expected.

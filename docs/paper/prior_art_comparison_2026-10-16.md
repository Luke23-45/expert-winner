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
- Note a genuine mathematical adjacency the paper should acknowledge: their dual has an (unnamed, unexploited) common-mode invariance (adding `c` to all `p_k` and `y_i` leaves objective and constraints unchanged since `KT = LE`); their update is already zero-sum-preserving. Our `Π_g` makes the gauge structure explicit and load-bearing. Adjacent, not the same — cite, don't ignore.

### DeepSeek loss-free — no change
Heuristic, no theory of its own, no censoring analysis. 2512.03915 is now its theory reference; cite both together.

---

## 4. What changed vs `novelty_outline.md` §1 (2026-10-11)

- **(i) requested-vs-admitted axis:** unchanged — NOVEL. Neither new paper names the axis (φ-Balancing sidesteps hard counts entirely; 2512 has no censoring).
- **(ii) censoring formalization:** unchanged — NOVEL. Verified zero hits in both new papers.
- **(iii) target-aware vs target-blind:** unchanged — NOVEL. Both new papers use uniform targets only.
- **(iv) t_flip law:** unchanged — CLASSICAL mechanism, ours as verified law.
- **(v) anti-windup:** unchanged — CLASSICAL mechanism, honest negative result.
- **(vi) gauge-projection formulation:** verdict stays PARTIALLY PREDATED, must-cite list grows — add φ-Balancing's dual price `q = ∇φ(m)` as adjacent stateful-load-tracking prior art (loss-actuated, no gauge structure). The claimed-novel part remains exactly the quotient formal theory.
- **NEW (vii): primal-dual theory of feedback load balancing** — PARTIALLY PREDATED by 2512.03915 (single-shot primal-dual, monotonicity, band-stability, log regret, for the uncensored uniform-target case). Our claimed-novel part: the capacity-censored extension, gauge quotient structure, target dependence, and failure conditions. Never claim "first primal-dual/subgradient theory of feedback load balancing."
- **Never-claim list additions:** (a) "persistent per-expert load state" as a concept (φ-Balancing's dual price); (b) "first (sub)gradient/primal-dual theory of feedback load balancing" (2512.03915).

# Novelty Outline: Feedback Control for Capacity-Limited MoE Routing

**Author role:** literature analyst. **Date:** 2026-10-11.
**Branch:** `feat/paper-feedback-moe-routing`.
**Evidence labels:** `[VERIFIED-PRIMARY]` (I read the paper text on arXiv in this pass),
`[VERIFIED-ABSTRACT]`, `[SECONDARY]` (third-party summary — provisional),
`[GRAY]` (non-arXiv — lead only), `[SYNTHESIS]` (my inference from established results —
not a literature claim), `[NOT FOUND]` (searched, nothing located).
Claims marked with `(v3)` were verified in `docs/literature_review/moe_routing_load_balancing_v3_deep.md`
and are re-stated here, not re-verified, unless noted.

**Central constraint (owner's directive):** the paper's novelty rests on the formal
treatment of CENSORED OBSERVATIONS, TARGET DEPENDENCE, CAPACITY, and LIMITS OF
FEEDBACK — explicitly NOT on introducing feedback control to MoE routing.
Four deployed at-scale bias controllers now exist (DeepSeek 2024, SMEBU/Trinity 2026,
Kimi K3 Quantile Balancing 2026, ID Balancing 2026). Every one of them feeds back
post-assignment counts against a uniform target and says nothing about what happens
to the feedback signal under capacity saturation. That gap — what the controller
observes, not that it controls — is the paper.

---

## 1. Per-candidate-contribution novelty verdicts

Verdict scale: **NOVEL** (no prior art found; ours to claim) /
**CLASSICAL** (mechanism is textbook canon — cite it, claim only the instantiation) /
**PRIOR ART** (a specific paper already does it — cite it, do not claim) /
**PARTIALLY PREDATED** (some layer is prior art; the rest may be novel — split it honestly).

### (i) Requested-vs-admitted as a design axis under saturation — NOVEL

No prior art found for the distinction as a load-balancing design axis.
Classical dispatch-time feedback (power-of-two-choices, JIQ, backpressure) uses
exclusively admitted-state signals — queue backlogs, idle tokens, outstanding
connections `(v3, [NOT FOUND] after direct search)`. All four deployed MoE bias
controllers feed back post-assignment token counts:
DeepSeek's loss-free update uses per-expert load vs mean `[VERIFIED-ABSTRACT]`(2408.15664);
SMEBU's normalized violation `v_i = (nbar − n_i)/nbar` is computed on assigned counts
`[VERIFIED-PRIMARY]` (2602.17004 §2.3); ID Balancing's error `e_i = (nbar − n_i)/nbar`
uses `n_i` = "number of tokens assigned to expert i" `[VERIFIED-PRIMARY]` (2609.39137 §2.2);
Kimi K3's quantile target assigns `q = mK/E` tokens per expert from the batch score
distribution `[SECONDARY]` (K3 tech report via ID Balancing §2.3).
ID Balancing unifies these in PID terms without ever naming the requested/admitted
axis — full-text search of the paper finds no "windup", "saturation", "dropped",
or capacity-constraint treatment of the feedback signal `[VERIFIED-PRIMARY]`.
The v3 review's classical search found no sensor-side telling of saturation anywhere:
the anti-windup canon always tells the story from the actuator side (the control
signal saturates; the integrator doesn't know). Ours is the sensor-side dual (the
feedback signal saturates; the integrator sees a constant). The math is dual;
the MoE instantiation — GShard/Switch-style capacity clipping censoring the load
observation — appears in no paper found.

### (ii) Censoring formalization (A=C reveals only R≥C) — NOVEL

The formal results — information-loss proposition (`min{R_e,C_e}` constant on
`[C_e,∞)`, so excess demand is invisible), sign-reversal corollary
(`ε^R_e > 0` while `ε^A_e < 0`), and the saturation-freeze theorem
(global saturation → admitted feedback is common-mode → `q^+ = (1−δ)q`, no relative
corrective dynamics) — have no prior art located. Classical anti-windup
(Fertik & Ross 1967; Hanus et al. 1987; Åström & Hägglund 2006; Caparroz et al.
2026 review) treats actuator saturation, never a censored load observation.
Adjacent but different: RED (Floyd & Jacobson 1993) acts on a pre-saturation queue
statistic, but as a drop policy, not as the tap point of a controller's feedback
`(v3, [SECONDARY])`. `[SYNTHESIS]` Why nobody noticed: modern large-scale training
is largely dropless (SimBal §6 explicitly trains dropless models `[VERIFIED-PRIMARY]`),
so in training, assigned counts coincide with requested counts and the
admitted/requested distinction is invisible. It becomes visible exactly under hard
per-expert capacity — i.e., our formalization predicts when and how the deployed
controllers' feedback degrades, a regime none of them analyzes.

### (iii) Target-aware vs target-blind distinction; failure under non-uniform μ — NOVEL

All deployed controllers use uniform targets (`nbar` = mean load in ID Balancing
Eq. 3 and SMEBU Eq. 23; `q = mK/E` in Kimi K3). None analyzes non-uniform targets
or target dependence `[VERIFIED-PRIMARY]` for ID Balancing (no "non-uniform" hit);
`[NOT FOUND]` for the rest. Our formal doc proves `(A)` ≡ `(A_0)` on the gauge
quotient *only* under uniform target + uniform capacity, and T1 measures the
breakdown outside that regime: target-blind `(A_0) = P_0(A/(KT))` equalizes the
censored admitted load, ignoring both target and capacity. The distinction itself
and its measured consequence are ours to claim.

### (iv) The t_flip(η) = ceil(X/η) pre-flip law — CLASSICAL (mechanism); our instantiation measured

Verdict follows the v3 review: a discrete integrator accumulating a constant error
to a fixed threshold in time ∝ 1/η is textbook (Åström & Hägglund 2006).
What is ours: the exact pre-flip statement for gauge-projected pressure dynamics —
`q_t = t·η·γ·(eps − min(eps))` with the gauge min-shift canceling in score
differences, the per-seed invariant `η·t_flip = X_seed` (not the number 35.2),
and the prospective verification (predictions committed before the runs; 14/14
exact). Present it as a verified law demonstrating determinism and protocol
fidelity, never as a theoretical discovery about MoE routing. The mildly
interesting part — the discrete Top-K selector behaving like a threshold on
accumulated pressure, i.e. gain-linearity through a discrete plant — is our
measurement, not prior art `(v3, [SYNTHESIS])`.

### (v) Anti-windup-by-conditional-integration for admitted feedback — CLASSICAL (mechanism); MoE instantiation novel; honest NEGATIVE result

The mechanism is the classical conditioning technique: Hanus, Kinnaert &
Henrotte, "Conditioning technique, a general anti-windup and bumpless transfer
method," *Automatica* 23(6), 729–739, 1987 `(v3, existence verified via reference
lists)`. Our `admitted_antiwindup` (freeze saturated coordinates at the
unsaturated mean before the zero-sum projection; full freeze under global
saturation) is conditional-integration-inspired and faithfully implemented
(unit tests pass). It is NOT ID Balancing's gated derivative — theirs activates
on worsening imbalance (`1[e_prev·Δe > 0]`), a condition on error dynamics, not
on saturation state; different mechanism, different problem `[VERIFIED-PRIMARY]`.
**The experimental verdict is negative and must stay negative:** it never beats
requested / admitted / bias_integral on any rebalancing metric (V3-T2); it
refuses the censored signal while admitted exploits the signal's ordinal content
(saturated = at least as loaded as unsaturated). Its unambiguous win is the
T1 phantom-vs-freeze dissociation: under fully-censored heterogeneous saturation,
admitted builds 1.48 units of windup state from zero current-demand information
while antiwindup builds exactly 0. Claim the dissociation and the limit
("prevents miscalibration but cannot recover information censoring destroys"),
never an improvement.

### (vi) Gauge-projection formulation of the controller state — PARTIALLY PREDATED (changed vs v3)

**This verdict changed against the v3 review, which rated gauge projection
APPEARS NOVEL without knowledge of ID Balancing.** The *operation* — removing the
common-mode component of the controller state because it does not change routing
— is prior art at trained 768-expert scale: ID Balancing re-centers the bias to
zero mean after each update, explicitly because "adding the same constant to every
expert bias leaves the score ranking and the selected set unchanged"
`[VERIFIED-PRIMARY]` (2609.39137 §3, "Zero-mean centering step"); SMEBU centers its
update (`Δb_i − mean(Δb)`) `[VERIFIED-PRIMARY]` (2602.17004 Eq. 26); Kimi K3
mean-centers the bias `[SECONDARY]`. (DeepSeek's fixed-step sign update does *not*
preserve zero-mean — ID Balancing notes the drift explicitly — so gauge-fixing is
novel relative to DeepSeek 2024 only.)
What **appears novel** is the *formal quotient theory*: the gauge quotient
`R^E/span{1}`, the canonical nonnegative representative `Q`, the boundary
re-entry lemma, requested feedback as a quotient subgradient step of a convex
hard Top-K potential (with the corrected `τ/K` smooth normalization), and the
capacity-dual gauge reduction (`Σ_e C_e = KT` ⟺ exact quotient dual descent).
ID Balancing's centering is a one-paragraph engineering step, not a dynamics
theory. Split the claim exactly this way in the paper: operation → cite
ID Balancing/SMEBU; quotient formal theory → ours. Also cite the adjacent
classical canon honestly: Hanus et al. 1987 conditioning keeps controller state
consistent with a feasible set but recomputes a realizable *reference* rather
than projecting the *state* — adjacent, not the same.

### (vii) The hetero-divergence failure regime — NOVEL (measured; framing-constrained)

T1 §2.3: under heterogeneous capacity, target-blind `(A_0)` is actively
destructive — viol 0.0576 → 0.4106–0.4126, overflow 512 → 1065–1072
(aggregate shortage is only 512), saturation fraction collapsing to 0.35–0.37;
e.g. expert 7 (capacity 66) driven to 938 requests. No prior art found; no
deployed controller is target-blind, so none could have reported it.
**Framing constraint:** `(A_0)` is our own construct. This is a measured failure
mode of a target-blind variant, not an indictment of any deployed controller.
Present it as the empirical cost of discarding the target — the complement of
(iii) — and as the reason the paper's formalism tracks the target explicitly.

---

## 2. What we must cite (verified)

**Direct prior art — deployed feedback controllers (the "we do not introduce feedback" wall):**
- Wang et al., "Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts,"
  arXiv:2408.15664 (2024) `[VERIFIED-ABSTRACT]` — per-expert bias before top-K,
  `b_i ← b_i ∓ γ` on sign of load error, selection-only (no interference gradients);
  validated to 3B params / 200B tokens. Our `bias_integral` is a faithful replication.
- DeepSeek-AI, "DeepSeek-V3 Technical Report," arXiv:2412.19437 (2024)
  `(v3, report excerpts)` — deploys the bias controller at 671B/37B with γ=0.001
  plus a complementary sequence-wise aux loss (α=0.0001) for within-sequence imbalance.
  (γ schedule "0.001 for 14.3T tokens then 0" is `[SECONDARY]` — reimplementation notes only.)
- Singh et al. (Arcee AI / Prime Intellect / DatologyAI), "Arcee Trinity Large
  Technical Report," arXiv:2602.17004 (2026) `[VERIFIED-PRIMARY]` — 400B total /
  13B active, sigmoid routing, Muon, 17T tokens, zero loss spikes; introduces SMEBU
  (Soft-clamped Momentum Expert Bias Updates): normalized violation
  `v_i = (nbar − n_i)/nbar`, `tanh(κ·v_i)` soft-clamped magnitude-aware update,
  zero-mean-centered update, momentum buffer (`m_i = β·m_i + (1−β)·Δb_i`;
  λ=5e-4, β=0.5, κ=2) — introduced because the sign operator oscillates and "can
  never fully settle" near a fixed ideal bias; plus a sequence-wise aux loss.
  Independent industry confirmation that sign-based updates chatter at scale.
- Jin et al. (Qwen Team, Alibaba), "ID Balancing: Stable Training of Extremely
  Sparse MoE via PID-Based Load Control," arXiv:2609.39137 (2026)
  `[VERIFIED-PRIMARY]` — unifies DeepSeek's method as fixed-step *integral* control
  and Kimi K3's Quantile Balancing as generalized *proportional* control; proposes
  an *integral–derivative* controller (magnitude-aware integral `K_i·e_i` +
  worsening-gated derivative `K_d·g_i·Δe_i`, `g_i = 1[e_prev·Δe > 0]`, zero-mean
  re-centering); evaluated Top-10/Top-5/Top-3 over 768 experts, 18.9B→69.9B params,
  120B tokens, with competitive LM loss. **The explicit PID-framing prior art.**
- Kimi Team, "Kimi K3 Technical Report," Moonshot AI (July 2026)
  `[SECONDARY]` (report excerpts via search; mechanism confirmed via ID Balancing
  §2.3 `[VERIFIED-PRIMARY]`) — Quantile Balancing: sets each expert's bias from the
  router-score quantile matching target load `q = mK/E` (uniform), using the
  (K+1)-th largest biased score as cutoff; mean-centers the bias. The
  "generalized proportional" member of the family. (The "exact coordinate
  minimization of the balanced-assignment LP dual" derivation is `[GRAY]` —
  community summary of Appendix C — do not cite as fact.)

**Balance-metric-vs-model-quality caution (the "synthetic balance ≠ quality" wall):**
- Omi, Sen & Farhadi, "Load Balancing Mixture of Experts with Similarity
  Preserving Routers" (SimBal), arXiv:2506.14038 (2025; v2 11 Oct 2025)
  `[VERIFIED-PRIMARY]` — Table 4 re-verified in this pass: MoE-M perplexity
  13.685 (SimBal) vs 14.086 (LBL); MoE-L 8.304 vs 8.517; 5-seed MoE-M stats
  (LBL 14.051±0.026, SimBal 13.691±0.039); Min PES 0.0044 vs 0.0255 (MoE-M);
  downstream mean 45.19% vs 43.28%; 36% fewer tokens to same loss. Core argument:
  imposing uniformity makes experts acquire redundant knowledge. **Also cite
  SimBal §6's limitation:** "we do not investigate how token dropping might affect
  the performance of our balancing mechanism" — token dropping under capacity is
  explicitly their open direction; it is our lane.
- Kapusuzoglu et al., "When Load-Balancing Goes Too Far," arXiv:2609.04453 (2026)
  `(v3, primary text)` — over-dispersed routing: per-token routing entropy
  (90.8% vs 74.3% of max) separates homogenized from specialized balance.
- Lee et al. (NAVER), "Router Prior Bias," arXiv:2609.08115 (2026)
  `(v3, primary text)` — re-imposed uniformity degrades post-training (45.77 → 31.91).
- Mouzouni, "Three Phases of Expert Routing," arXiv:2604.04230 (2026)
  `(v3, abstract)` — late training deliberately trades balance for quality
  (γ_eff 27→9); a fixed uniform setpoint fights the relaxation phase.
- Wu et al., "Relax Within, Balance Across" (ReBA), arXiv:2608.00574 (2026)
  `(v3, abstract)` — balance metrics are definition-dependent (mixed vs
  per-modality); balance is a diagnostic, never the objective.
- DeepSeekMoE (Dai et al. 2024) knowledge hybridity/redundancy; DynMoE (Guo et al.,
  ICLR 2025) arguing against uniform-frequency targets `(v2, verified)`.

**Classical control canon (cite for mechanisms, claim only instantiations):**
- Hanus, Kinnaert & Henrotte, "Conditioning technique, a general anti-windup and
  bumpless transfer method," *Automatica* 23(6), 729–739, 1987 `(v3, existence
  verified)` — conditional integration / conditioning.
- Fertik & Ross, "Direct digital control algorithm with antiwindup feature,"
  *ISA Transactions* 6, 317–328, 1967 `(v3)` — back-calculation.
- Åström & Hägglund, *Advanced PID Control*, ISA, 2005/2006 `(v3, bibliographic)` —
  clamping, back-calculation, gain scheduling, relay feedback (limit cycles from
  sign nonlinearities — the classical explanation of bias-integrator chatter).
- Kothare, Campo, Morari & Nett, "A unified framework for the study of antiwindup
  designs," *Automatica* 30, 1869–1883, 1994 `(v3)` — most schemes are special
  cases of one architecture.
- Ioannou & Sun, *Robust Adaptive Control*, Prentice-Hall, 1996 `(v3)` —
  σ-modification / leaky integrator: leak buys boundedness at the price of a
  steady-state dead zone (our `requested_leaky` adversarial-init failure is the
  textbook tradeoff re-instantiated).
- Caparroz, Soltesz, Hägglund & Guzmán, "Anti-Windup in PID Control: Review,
  Analysis, and New Tuning Directions," arXiv:2606.01959 (2026) `(v3, abstract)` —
  the 2026 state of the taxonomy; none of its schemes operates on a projected
  pressure state or distinguishes pre- vs post-saturation error signals.

**Classical load balancing (the "everyone uses admitted-state" evidence):**
- Mitzenmacher, "The Power of Two Choices in Randomized Load Balancing,"
  *IEEE TPDS* 12(10), 1094–1104, 2001 `(v3, DOI verified)` — feedback is sampled
  queue length (admitted, unfinished work).
- Lu et al., "Join-Idle-Queue," *NSDI* 2011 `(v3, abstract)` — feedback is idleness
  (spare admitted capacity).
- Tassiulas & Ephremides, "Stability Properties of Constrained Queueing Systems…,"
  *IEEE TAC* 37(12), 1936–1948, 1992 `(v3)` — backpressure routes on queue-backlog
  differences (admitted minus served).
- Hellerstein, Diao, Parekh & Tilbury, *Feedback Control of Computing Systems*,
  Wiley, 2004 `(v3, ToC verified; §1.6.5 "Load Balancing")` — the control-in-computing
  tradition regulates *admission* (how much work enters); our controller is the
  inverse (admission is the plant; the controller routes). The two literatures
  have not met.

**MoE routing canon for related work** `(v2, verified)`: Shazeer et al. 2017
(noisy top-k + two aux losses); GShard (Lepikhin et al. 2021 — hard expert
capacity, overflow tokens dropped via residual); Switch (Fedus et al. 2022 —
`α·N·Σ f_i·P_i`, capacity factor); Hash Layers (Roller et al. 2021 — the
fixed-random baseline any learned controller must beat); BASE (Lewis et al. 2021 —
auction assignment, open-loop per-batch); Expert Choice (Zhou et al. 2022 —
perfect balance by construction, awkward for autoregressive decoding);
StableMoE (Dai et al. 2022 — routing fluctuation statistics 40.9%/29.1%/15.4%);
ST-MoE (Zoph et al. 2022 — z-loss); Clark et al. 2022 (Sinkhorn — the closest
literature analogue to projecting, but it projects the *assignment matrix*
per batch, not a persistent controller state); DeepSeekMoE (Dai et al. 2024);
ReMoE (Wang et al., ICLR 2025); DynMoE (Guo et al., ICLR 2025).

**Adjacent 2026 (cite honestly, know the boundary):**
- Qiu et al., "HERO-MoE: Historical Expert ROuting with Scale-Preserving Fusion,"
  arXiv:2609.32581 (2026) `[VERIFIED-ABSTRACT]` — reuses detached dense routing
  distributions from preceding layers as cross-depth priors (8B/0.5B-active,
  100B tokens, loss 1.6393→1.6184). Stateful routing exists, but it is a
  feedforward prior across depth, not a load-error feedback loop across steps —
  no error signal, no saturation treatment. Cite as the honesty boundary on
  "stateful."
- DTop-p MoE, arXiv:2512.13996 `[SECONDARY]` (search snippet; not read) — a PI
  controller stabilizing the *number of activated experts* (sparsity) via the
  top-p threshold. Feedback control applied to MoE routing, but to a different
  loop variable; no load-error signal, no censoring analysis. Verify before citing.

---

## 3. What we must NEVER claim

1. **Never claim to introduce feedback control to MoE routing.** Four deployed
   at-scale controllers predate us: DeepSeek's sign-integral bias (2024),
   SMEBU's tanh-momentum update (Trinity, 400B, 2026), Kimi K3's quantile-proportional
   update (2026), ID Balancing's integral–derivative controller (768 experts, 2026).
2. **Never claim the PID framing.** ID Balancing (arXiv:2609.39137, Sept 2026)
   explicitly unifies the family as incomplete PID controllers, with trained
   results. Our paper cites it as prior art, not as a springboard we invented.
3. **Never claim magnitude-aware error scaling.** ID Balancing's `K_i·e_i` and
   SMEBU's `tanh(κ·v_i)` both scale corrections with error magnitude. Ours is the
   leaky pressure + projection design, not magnitude-awareness.
4. **Never claim bias/pressure centering.** ID Balancing, SMEBU, and Kimi K3 all
   zero-mean-center the bias or its update. Claim only the quotient formal theory
   (vi), never the operation.
5. **Never claim synthetic balance implies model quality.** SimBal's LBL baseline,
   Kapusuzoglu's over-dispersion, Lee et al.'s post-training degradation, and
   Mouzouni's relaxation phase all show uniformity-imposing balance can coexist
   with — or cause — worse models. Every synthetic result must carry the SimBal
   caution; the toy trained-router probe is feasibility only, never evidence.
6. **Never claim the anti-windup controller improves rebalancing.** The verdict is
   negative: it prevents miscalibration (phantom 1.48 vs exact 0) but cannot
   recover censored information, and admitted's exploitation of ordinal signal
   content beats it. Present the dissociation, not a triumph.
7. **Never present the t_flip law as a discovery.** It is textbook integrator
   scaling; "35.2" is seed-17-specific. Present as a verified law (protocol
   fidelity), not a finding.
8. **Never let (A_0)'s divergence indict deployed controllers.** `(A_0)` is our
   construct; deployed controllers are target-aware (uniform). The failure mode
   bounds target-blind designs, nothing else.
9. **Never claim the uniform-μ setpoint is the right target.** The field is moving
   away from uniform setpoints (SimBal, DynMoE, Mouzouni, ReBA, RPB). Our uniform
   target is the simplest setpoint, stated with the explicit caveat that the
   evidence favors non-uniform targets; the requested/admitted/windup analysis is
   orthogonal to the setpoint choice and survives it.
10. **Never claim trained-model evidence.** All closed-loop results are synthetic
    (E=8/K=2, CPU, fixed affinities). The bar for belief — a small LM at matched
    FLOPs reporting validation perplexity — is beyond this VM and is stated as
    future work, not implied.
11. **Never repeat v2's "exactly one deployed feedback controller" claim** without
    a time stamp. As of 2026 there are at least four (DeepSeek, SMEBU, Kimi K3,
    ID Balancing). Position against the family.
12. **Never cite the v3 review's HERO-MoE arXiv ID (2602.11184).** That ID is
    KBVQ-MoE, a quantization paper — the v3 review's citation was wrong. The real
    HERO-MoE is arXiv:2609.32581.

---

## 4. Positioning paragraph (2–3 sentences)

Feedback control of MoE expert load is a deployed, industrially mature idea:
DeepSeek's sign-integral bias (2024), Arcee's tanh-momentum SMEBU (2026), Kimi K3's
quantile-proportional update (2026), and ID Balancing's PID unification at
768-expert scale (2026) all steer loads with per-step controllers — but every one
of them feeds back post-assignment counts against a uniform target, with no
account of what capacity saturation does to the observation itself. This paper
supplies that missing layer: a formal theory of censored load observations for
capacity-limited routing — the requested-vs-admitted feedback distinction, a
proved saturation-freeze theorem with its sensor-side windup analysis, the
target-dependence of centered feedback including a measured hetero-divergence
failure regime, and a conditional-integration anti-windup design whose honest
negative verdict delineates exactly what feedback can and cannot recover once
the signal is censored.

---

## 5. Open questions / unverified items

1. **v3 review correction (done in this pass):** the v3 review cited HERO-MoE as
   arXiv:2602.11184 — wrong; that ID is KBVQ-MoE (quantization). Correct citation:
   Qiu et al., arXiv:2609.32581 (26 Sep 2026) `[VERIFIED-ABSTRACT]`. It is
   cross-depth routing priors, not load-error feedback — no threat to the
   novelty claims, but the v3 review's "top follow-up read" framing is retired.
2. **(vi) verdict changed vs v3:** gauge-projection-as-operation is prior art
   (ID Balancing §3 zero-mean centering, SMEBU Eq. 26, Kimi K3). Only the quotient
   formal theory remains claimed-novel. The paper must split these explicitly.
3. **Kimi K3 "balanced-assignment LP dual" derivation** (Appendix C, "exact
   coordinate minimization") is `[GRAY]` — community summary only. Do not cite
   the LP-duality claim as fact; cite the mechanism (quantile target + centering)
   via ID Balancing §2.3 `[VERIFIED-PRIMARY]`.
4. **DTop-p MoE** (arXiv:2512.13996, PI control for sparsity) is `[SECONDARY]`
   (search snippet only). Read before citing; it is adjacent (different loop
   variable), not a threat.
5. **DeepSeek-V3 γ schedule** (0.001 for 14.3T tokens, then 0) and any deadband
   details are `[SECONDARY]` (reimplementation notes). The report primary-verified
   facts are: bias controller deployed at 671B/37B + sequence-wise aux loss
   α=0.0001.
6. **SimBal SEU 0.997** (near-perfect per-batch balance of the LBL baseline) was
   `(v3, primary excerpts)`; in this pass I re-verified Table 4 (perplexity, PES,
   downstream) from the v2 full text but not the SEU figure. Treat the SEU number
   as v3-verified, not independently re-verified here.
7. **"No deployed controller discusses censoring":** verified by full-text search
   for ID Balancing (no windup/saturation/dropped/capacity-feedback) and by
   section read for SMEBU; DeepSeek 2024 re-checked at abstract level only.
   A full-text pass of Wang et al. 2024 for capacity/drop discussion would
   strengthen this — flagged as a pre-submission check.
8. **Jianlin Su's "Quantile Load Balancing"** (2026, Chinese-language MoE blog
   series Part 6, cited in a gray replication essay) `[NOT FOUND]` as a formal
   paper — unverified lead, do not cite.
9. **Akhtar 2026** (small-scale ALF-vs-AL study, GitHub-hosted PDF) remains
   `[GRAY]` — single small-scale study, not evidence.
10. **Toy trained-router probe** (`v3_notes/trained_router_smoke.py`) is
    feasibility only (17.7 s, 3 conditions × 300 steps) — must not be cited as
    trained-model evidence. The belief-grade experiment (small LM, matched FLOPs,
    validation perplexity, multiple seeds, per-token routing entropy alongside
    load histograms) is future work requiring a GPU cluster.
11. **No convergence result** beyond the pre-flip theorem: post-flip cascades,
    the η ≤ 3.0 clean basin, and the η = 10 limit cycle remain empirical
    finite-horizon description. The paper must not imply otherwise.
12. **(A_0) ≡ (A) gauge-equivalence** holds only under uniform target + uniform
    capacity (proved); the fragility outside that regime is the finding, not a
    general indictment — keep the regime qualifier attached to every mention.

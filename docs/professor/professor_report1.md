I'll start by being explicit about one hard constraint, then do the real work.

**Constraint I cannot work around:** the paths you cite (`C:/Users/Hellx/...`) are on your local machine. My tools are web search and web fetch only — I cannot read your repository, re-run your verifiers, or inspect your ledger. So everything below is built from (a) the summary you just gave me, treated as your attested ground truth, and (b) external literature I will actually verify. Where I cannot verify something, I will say so rather than paper over it.

Let me verify the external claims first.


# Senior-Researcher Assessment: MoE Phase-1 Censored-Feedback Program

## 0. Scope and provenance of this analysis (read first)

**What I could not do.** The paths you cite (`C:/Users/Hellx/Documents/Papers/mvb/moe-phase1-censored-feedback/...`) are on your local machine. I have no filesystem access. Every statement below about *your repository* is taken from your summary and is **unverified by me**. I have not re-derived your proofs, inspected your simulator, or confirmed the 236-run inventory.

**What I did do.** I ran a live literature review (5 search rounds, 4 primary-source extractions) against the public record, current to October 2026. That review **changes three entries in your assessment table** and **opens a fourth research option you did not list**. Those changes are the highest-value content below.

**Error discipline.** Section 6 is an explicit uncertainty ledger. Anything I could not verify is listed there rather than smoothed over.

---

## 1. What your assessment actually means

Translated out of hedged audit language, your assessment says four things:

**(a) You diagnosed a claim-architecture failure, not a results failure.** The theory and the experiments were being sold as one contribution ("censored feedback is a real limitation, and our controller fixes it"). Neither half supports the other. The synthetic runs do not validate the theorem; the theorem does not predict a system benefit. Bundling them produced a package where a reviewer who disproves either half disproves the paper.

**(b) Your "no-go" result is a benchmark-design artifact, and you correctly identified the mechanism.** B1 is *constructed* to reproduce a finite MoE instance's actions, outcomes, costs, and movement constraints exactly. Value equality against an instance-matched copy is a tautology, not a discovery. This is the classic **over-strong-comparator** error: you built an oracle that already contains the answer, then "proved" the oracle matches. The finding is real but it is a statement about your benchmark, not about control.

**(c) Your motivating premise was over-claimed and you caught it.** "Real MoE systems can only observe admitted counts" is false as a blanket statement. But — and this is the part your assessment understates — **it is not false everywhere**. Section 2 shows the premise survives, in a narrower and much more useful form.

**(d) Your corrected recommendation is right, and its ordering is right.** "Claim correction and separation before new experiments" is correct because any experiment run under a broken claim architecture produces un-publishable evidence regardless of outcome. You are fixing the instrument before collecting more data. That is the correct senior move.

**What your assessment does NOT mean, and you should resist reading it as meaning:**
- It does not mean the research is finished. You already say this; hold the line.
- It does not mean the theory is wrong. It means the theory's *target* was mis-chosen.
- It does not mean the synthetic results are worthless. A regime-dependent mechanism finding in a controlled simulator is a legitimate result — it is simply a *mechanism* paper, not a *benefit* paper.
- It does not license a fourth open-ended exploration. Your own recommendation forbids that, correctly.

**The one thing your assessment is missing:** you framed the fork as *theory vs. method*. The literature says there is a third axis that dominates both — **observation cost**, not observation impossibility. That reframe rescues the premise, makes the theory non-trivial, and makes the experiment cheap. Details in §2.6 and §3.

---

## 2. Literature review

### 2.1 Corrections and upgrades to your evidence table

These are findings from primary sources that **contradict or materially sharpen** your assessment.

**Correction 1 — "DeepSeek does not drop tokens" is version-specific, and V2 is the faithful comparator target.**

DeepSeek-V3 is indeed dropless: *"DeepSeek-V3 does not drop any tokens during training. In addition, we also implement specific deployment strategies to ensure inference load balance, so DeepSeek-V3 also does not drop tokens during inference."* [[115]]

But **DeepSeek-V2 dropped tokens, by design, at device granularity, selected by lowest affinity score**:

> *"we introduce a device-level token-dropping strategy during training. This approach first computes the average computational budget for each device, which means that the capacity factor for each device is equivalent to 1.0. Then, inspired by Riquelme et al. (2021), we drop tokens with the lowest affinity scores on each device until reaching the computational budget. In addition, we ensure that the tokens belonging to approximately 10% of the training sequences will never be dropped."* [[110]][[114]]

**Consequence for your baseline claim.** You wrote that the simulator's bias controller has "DeepSeek-style update form and gain, but a modified observation path under simulated drops," and that this distinction needs to be explicit. That is right, but it undersells the problem. The published record contains **no system that combines a V3-style γ-bias sign update with V2-style device-level dropping**. V2 used three auxiliary losses (ExpBal, DevBal, CommBal), not bias updates [[110]]; the bias mechanism came later, from Loss-Free Balancing (Wang/Dai et al., arXiv 2408.15664) [[163]], and was adopted in V3 [[115]]. Your baseline is therefore a **constructed hybrid**, not a modified DeepSeek. Say so plainly, and either (i) justify the hybrid as the natural composition, or (ii) implement the actual V2 mechanism as a second comparator.

**Correction 2 — the censoring is not "clipping." It is score-biased truncation, and that is a much stronger and more interesting mechanism.**

Both V2 (*"drop tokens with the lowest affinity scores"*) [[110]] and Megatron-Core (`--moe-token-drop-policy` with default `probs`) [[395]] drop by **lowest routing score**, not arbitrarily. This means:

> The admitted count for expert *i* is not `min(R_i, C)`. It is a **downward-biased, score-truncated** statistic whose bias is largest exactly for experts whose requests are low-affinity.

That has a sharp, testable control consequence which I believe is your paper:

- A γ-sign bias controller driven by admitted counts sees expert *i* as *underloaded* precisely when *i*'s marginal requests were the low-score ones that got dropped.
- Underloaded → bias increases → *i* enters more tokens' Top-K → but those tokens still have low raw affinity → they are still first to be dropped → admitted count does not rise → bias increases again.
- **This is integrator windup driven by censoring.** Under global saturation, admitted counts pin at capacity for every expert and carry *zero* information about relative demand, so the controller loses controllability entirely.

Your synthetic finding — *"admitted feedback freezes under the stated global-saturation/uniform setup, while requested feedback can move the routing state"* — is, on my reading, an empirical observation of exactly this. You currently describe it as a regime-dependent mechanism in your simulator. It is better described as **saturation-induced loss of identifiability in censored load feedback**, which is a family-level statement, and which is the thing your Phase-1 theory should have been targeting.

**Correction 3 — the observability premise is not dead. It is mis-scoped, and three current, published, code-available settings instantiate it.**

| Setting | Requested ≠ admitted? | Source | Status |
|---|---|---|---|
| DeepSeek-V3 training/inference | **No** — dropless; inference balance via redundant experts + statistics collected online, adjusted ~every 10 min | [[115]][[328]] | Deployed |
| MegaBlocks / dropless MoE | **No** — block-sparse formulation avoids dropping entirely | [[45]][[47]] | Published |
| Expert Choice routing | **No** expert overflow; failure mode inverts (a token may be picked by none) | [[55]][[62]] | Published |
| **Switch / GShard / ViT-MoE token-choice with capacity factor** | **Yes** — surplus tokens dropped; token-choice needs 2×–8× overprovisioning to avoid it | [[54]][[38]][[383]] | Published, in production frameworks |
| **DeepSeek-V2 training** | **Yes** — device-level, lowest-affinity-first, 10% of sequences protected | [[110]] | Published |
| **Capacity-Aware Token Drop (inference)** | **Yes, deliberately** — enforces per-expert ceilings by discarding excess tokens; 30% speedup at 0.9% degradation on OLMoE; Expanded Drop gives 1.85× on Mixtral-8×7B-Instruct | [[92]][[93]] | **ICLR 2026, code released** |
| **Megatron-Core today** | **Yes, configurable** — `--moe-expert-capacity-factor`, `--moe-pad-expert-input-to-capacity`, `--moe-token-drop-policy {probs,position}` | [[395]] | Shipping framework |

So the correct premise statement is:

> ~~"Real MoE systems can only observe admitted counts."~~
> **"There exist published, deployed, and code-available MoE regimes — capacity-factor training, device-level dropping, and capacity-aware inference — in which requested and admitted expert counts differ, and in which the difference is a score-biased truncation rather than a random sample. In dropless regimes the two coincide and the distinction is vacuous."**

That version is defensible, cited, and *narrow enough to be true*. It also tells you exactly which experimental regime you must use (see §4).

**Correction 4 — the binding constraint in current systems work is observation COST, not observation impossibility. This is the strongest reframe available to you.**

The 2025–2026 systems literature has converged on explicitly pricing the load-information channel:

- **METRO** (arXiv 2512.09277, Dec 2025) balances *activated experts per GPU* rather than token counts, and *"employs a novel allGather scheme to gather global top-k knowledge, which has minimal overhead compared to conventional allToAll."* Evaluated against **EPLB** on vLLM over 8×A100 plus a proprietary 8–16×B200 simulator; 11–22% decode-latency reduction, up to 4.11× decode throughput at fixed SLO. [[11]][[15]]
  → **METRO pays for global requested-side (top-k) information and justifies the price.** That is your research question, answered affirmatively by someone else, without a theory of when the price is worth it.
- **Demons in the Detail** (arXiv 2501.11873, Qwen; 67 citations) shows existing frameworks compute `f_i` within a micro-batch and average across parallel groups, making the load-balancing loss *"almost at the sequence level"*; they *"introduce an extra communication step to synchronize f_i across micro-batches"* and get large gains up to 42.8B parameters / 400B tokens. [[101]][[103]]
  → **Direct published precedent that the observation scope of load statistics is a first-order design variable with a communication price.** This is your closest related work and you must cite and differentiate from it.
- **Libra** (ICLR 2026) is explicitly *"aimed at balancing the 'effectiveness' of load balancing and the 'overhead of the mechanism itself'"*. [[132]][[299]][[305]]
- **ReaLB** (arXiv 2604.19503) advertises *"zero scheduling overhead."* [[303]]
- **DeepSeek-V3 production inference** runs a periodic, statistics-driven control loop: high-load experts *"are detected based on statistics collected during the online deployment and are adjusted periodically (e.g., every 10 minutes)"*, then rearranged into redundant-expert placements. [[115]][[328]][[336]]

**This is where your active-testing / costed-measurement machinery finally earns its place.** Not as "you cannot observe requested counts," but as "observing requested counts costs one extra collective of an *E*-vector per step; here is the break-even as a function of capacity slack, *E*, *K*, and load skew." That is a quantitative family-level theorem, it uses your Top-K structure, and it lands squarely in an active research genre.

**Correction 5 — your problem has a 70-year-old canonical name, and citing it will do more for your credibility than any amount of MoE related-work.**

The ITU Teletraffic Engineering Handbook states the premise exactly:

> *"The offered traffic is a theoretical value and it cannot be measured. It is only possible to estimate the offered traffic from the carried traffic."* [[338]]

Offered load *a*, carried load *a(1−B)*, Erlang-B blocking *B* [[74]][[337]]. Your "requested vs admitted" is **offered vs carried**. Your saturation-freezing finding is the classical fact that carried load saturates at capacity and stops being informative about offered load. Positioning the work inside teletraffic + partial monitoring, rather than only inside MoE, (i) makes the problem look principled rather than ad hoc, (ii) supplies ready-made estimators and identifiability language, and (iii) immediately explains why your instance-matched B1 benchmark failed: an Erlang-B oracle that knows the offered load is not an interesting comparator.

### 2.2 Track A — MoE routing, capacity, and load balancing (the application layer)

| Sub-area | Key sources | Bearing on your project |
|---|---|---|
| Capacity-factor token-choice & dropping | GShard/Switch [[38]][[54]], NeMo [[383]], Megatron-Core [[395]] | Your regime must be a dropping regime; dropless regimes give a guaranteed null |
| Dropless alternatives | MegaBlocks [[45]][[47]], Expert Choice [[55]], MaxScore (min-cost max-flow + SoftTopk, removes the capacity constraint) [[1]] | These are the P1 counterexamples; also your "why not just remove the constraint?" reviewer objection — MaxScore answers it and shows constrained vs unconstrained is a live tradeoff |
| Aux-loss-free bias control (your controller class) | Loss-Free Balancing arXiv 2408.15664 [[163]][[196]]; DeepSeek-V3 §3.3 [[115]]; Megatron-Core `--moe-router-enable-expert-bias --moe-router-bias-update-rate 1e-3` [[395]] | **The controller is now a framework flag. Zero novelty in the controller itself.** Novelty must be in the *observation* it consumes |
| Observation-scope of load statistics | Demons in the Detail [[101]]; Megatron-Core `aux_loss` (micro-batch) vs `seq_aux_loss` vs `global_aux_loss` (global across ranks) [[395]]; Qwen3 global-batch LBL [[420]] | Your "requested vs admitted" axis is *orthogonal* to and composable with the "local vs global" axis. Megatron-Core exposes both. This is a 2×2 you can actually run |
| Inference-side capacity enforcement | Capacity-Aware Token Drop / Expanded Drop, ICLR 2026, code released [[92]][[93]] | The single best real-system host for a serving-track paper |
| Expert placement / replication control | EPLB [[327]][[328]][[336]], Libra [[132]], EasyBalance (ICML 2026) [[308]][[309]], METRO [[11]], MoEShard (EuroSys'25) [[244]], FineMoE (EuroSys'26) [[246]], Pre-gated MoE [[250]] | Crowded and well-funded. Do not enter with a placement algorithm. Enter with an *observation/information* result they can all consume |
| Pseudo-balance critique | Memory-Aware Routing (OpenReview KTVW33GNRU) [[417]]; Advancing Expert Specialization (NeurIPS 2025) [[368]]; Similarity-constraint balancing [[366]] | Reviewers now expect specialization metrics (e.g., KED) alongside load CV, and expect quantified overhead (MAR reports +0.3 GB, +0.8 ms) [[417]] |
| Benchmarks/testbeds as contributions | MoE-Inference-Bench [[173]], MoE Routing Testbed [[413]][[418]], Capacity-Aware-MoE code [[93]] | Precedent exists for a testbed paper — but only if it is faithful to a real stack or explicitly scoped as a controlled abstraction |
| Surveys to cite | MoE in LLMs (arXiv 2507.11181, 48 cites) [[318]]; comprehensive MoE survey [[346]]; **Load Balancing for LLM Inference Serving: A Control and Learning Oriented Survey** (SSRN, 18 Jun 2026) [[387]] | See §2.6 — the last one is your closest framing competitor |

### 2.3 Track B — Censored / partial feedback (the theory layer)

- **Censored bandits.** *Threshold Bandits, With and Without Censored Feedback* (NeurIPS 2016) establishes that censoring changes regret character [[84]]; Guinet's MIT thesis *Bandit Problems under Censored Feedback* is the systematic treatment [[83]][[90]]; *Censored Semi-Bandits* [[88]]; *MAB with Censored Consumption of Resources* [[86]]; *Cost of Structural Learning under Censored Feedback* (arXiv 2605.27076, May 2026) [[85]]; online algorithm selection under censored feedback (AAAI 2022) [[81]].
  → **Implication:** "censored feedback makes learning harder" is *not novel by itself*. Your novelty must be the **structured, endogenous, score-biased** censoring induced by Top-K routing plus capacity — the censoring mechanism depends on the learner's own action. That is a genuine departure from iid censoring and is where a theorem can live.
- **Partial monitoring.** Bartók–Pál–Szepesvári give a full classification of finite partial-monitoring games with minimax regret characterizations [[222]][[221]]; adversarial classification [[226]]; linear partial monitoring [[227]]; recent unified treatment of partial-feedback online learning (arXiv 2601.21462, 2026) [[154]]; graph-feedback information-capacity bounds [[155]][[89]].
  → **Implication:** your setting is a partial-monitoring game where the feedback function is *state-dependent and saturating*. Slotting it into the Bartók taxonomy is a concrete, checkable first theorem step and would immediately tell you whether a non-trivial separation is even possible.
- **Top-K combinatorial bandits.** Top-K subset bandits [[146]][[147]], top-*k* with full-bandit feedback and matching lower bounds [[150]], route-constrained combinatorial bandits (2026) [[149]].
  → Your `Σ_i R_i = K·N` coupling is exactly the structure these papers exploit. Use them, don't reinvent.
- **Load balancing with partial/stale information.** Power-of-two-choices: *"only small amounts of queue length information can be extremely useful"* [[259]][[263]]; partial-information variants explicitly *"reduc[e] the amount of information to be retrieved"* [[266]]; stale information causes herding [[260]].
  → Gives you the shape of the positive result: a *little* requested-side information may suffice, so the VoI curve is likely steep-then-flat, and the interesting theorem is where the knee is.

### 2.4 Track C — Costed observation / value of information (the missing layer you already own)

- **Classical sensor scheduling & measurement design.** Mehra (1976), *optimization of measurement schedules and sensor designs for linear dynamic systems* [[411]]; Williams, *Information-Theoretic Sensor Management* as constrained optimization [[408]]; sensor scheduling for linear systems [[409]]; event-based scheduling trade-offs [[410]]; robust optimal sensor configuration by maximizing expected VoI as cost–benefit analysis [[407]]; computation–communication trade-offs in sensor scheduling (arXiv 1911.05859) [[404]].
- **VoI in networked control.** Age-of-Information vs Value-of-Information scheduling for networked control [[358]]; VoI in wireless sensor networks [[360]]; VoI in sequential decision making under POMDPs [[231]][[234]][[230]].
- **Costed evaluation.** Active Testing: Sample-Efficient Model Evaluation (ICML 2021) [[182]][[183]]; actively testing while learning (NeurIPS 2023) [[191]]; active learning for cost-sensitive classification (COAL, ICML 2017) [[137]].

→ **This is your existing "costed active testing" asset, and it maps cleanly onto the MoE problem:** the measurement is the requested-count vector, its price is one collective, and the decision is the bias/placement update. Nobody in the MoE literature is writing this down as a VoI problem. METRO just pays the price and reports the bill [[11]]; Libra reports the trade-off empirically [[132]]. **A break-even theorem would be cited by all of them.**

### 2.5 Novelty status

**Appears unclaimed (weak evidence, limited search):** the specific framing of MoE load-balancing feedback as an offered-vs-carried / censored-observation problem, and any break-even or VoI characterization of requested-side routing telemetry. My targeted queries for `"censored" expert load feedback mixture of experts`, and `MoE routing "requested" versus "admitted" token counts observability` returned no on-topic hits — the returned results were noise (survival-analysis censoring, unrelated infrastructure docs) [[279]]–[[288]][[384]][[385]]. **This is not a systematic review and is not novelty clearance.**

**Claimed and adjacent (must differentiate):**
1. **METRO** — already gathers global top-k knowledge via allGather and prices it against allToAll [[11]]. Threat: high for the *empirical* claim "global requested info helps." Mitigation: your contribution must be *when and why*, i.e., the theorem + break-even, not the demonstration.
2. **Demons in the Detail** — already shows observation scope (micro-batch vs global) changes outcomes, and pays an extra sync [[101]]. Threat: high for the *scope* axis. Mitigation: your axis is requested-vs-admitted (censoring), which is orthogonal; run the 2×2 and report the interaction.
3. **Capacity-Aware Token Drop** — already drops tokens at inference and measures quality/latency [[92]]. Threat: moderate. Mitigation: they treat dropping as a *mechanism*; you treat it as an *observation channel*.
4. **Loss-Free Balancing / DeepSeek-V3 bias** — the controller is prior art and a framework flag [[163]][[115]][[395]]. Threat: fatal if the controller is your claim. Mitigation: never claim the controller.
5. **Load Balancing for LLM Inference Serving: A Control and Learning Oriented Survey** (43 pp., SSRN, 18 Jun 2026) — codes prior work by *"imbalance source, **observable signals**, control knobs, assumptions, limitations, and evaluation evidence"* and introduces a *"state–action–constraint abstraction"* [[387]]. Threat: **this is your framing, published as a survey, four months ago.** Mitigation: cite it as the framing you instantiate; your contribution is the formal identifiability/VoI result it lists as an assumption column, not a theorem.

### 2.6 Residual scooping risk I could not close

A search snippet from the SSRN survey [[387]] surfaced the sentence: *"This suggests that controllers must be designed to remain stable under censored or delayed telemetry, rather than assuming full-state feedback."* My full-text extraction returned **only the abstract page** and did not contain that passage — the extractor could not reach the 43-page body.

**This is the single highest-priority manual action in this plan.** If that sentence is in the survey's open-directions section, your framing is already flagged as an open problem by a Manchester/Loughborough/Southeast group — which is *good* for significance and *bad* for being first. Read the PDF before committing to a title. I am flagging it as unverified rather than assuming either way.

---

## 3. Full combination analysis

### 3.1 Dimension definitions

**Premise states (P)** — what is actually true about requested-vs-admitted observability:

| | Statement | Verified status |
|---|---|---|
| **P1** | Censoring is nominal: production MoE is dropless, so requested ≡ admitted | **True for** DeepSeek-V3 [[115]], MegaBlocks [[45]], Expert Choice [[55]] |
| **P2** | Censoring is real in capacity-factor *training* | **True.** Switch/GShard token-choice [[38]][[54]], DeepSeek-V2 device-level lowest-affinity drop [[110]], Megatron-Core `--moe-token-drop-policy` [[395]], NeMo [[383]] |
| **P3** | Censoring is real in capacity-aware *inference* | **True.** Capacity-Aware Token Drop, ICLR 2026, code released [[92]][[93]] |
| **P4** | The binding constraint is the **cost** of requested-side observation (extra collective), not its impossibility | **True.** METRO allGather [[11]], Demons-in-the-Detail extra sync [[101]], Libra overhead-vs-effectiveness [[132]], ReaLB zero-overhead claim [[303]] |

**Honest global premise state: ¬P1 ∧ P2 ∧ P3 ∧ P4.** Your docs asserted P1-universality (false); your corrected assessment swung to "premise unsupported" (over-corrected). The truth is that the premise holds in a *bounded, citable, code-available* region — and in that region it is a **cost** question, not an **impossibility** question.

**Claim types (C):**

| | Claim |
|---|---|
| C1 | General control limitation / no-go theorem (current Phase-1 ambition) |
| C2 | Value-of-information / identifiability-regret separation with priced observation |
| C3 | Structural Top-K characterization (root-arrangement signature bound) |
| C4 | Exact benchmark reduction / representation equivalence (current B1) |
| C5 | Controller improves a **real trained MoE** (training track) |
| C6 | Controller improves a **real MoE serving system** (inference track) |
| C7 | Measurement/characterization audit: what MoE stacks actually observe, and what scope costs |
| C8 | Benchmark / simulator / testbed contribution |
| C9 | Negative or limitation result (premise correction) |

### 3.2 The 36-cell viability matrix (C × P)

Legend: ✅ viable · ⚠️ conditional · ❌ dead · — not applicable

| Claim | P1 (dropless) | P2 (cap-factor training) | P3 (cap-aware inference) | P4 (cost-bound) |
|---|---|---|---|---|
| **C1** No-go / general limitation | ❌ Limitation about a hypothetical; no gap exists | ⚠️ Must survive *score-biased* truncation; your B1 comparator is too strong to serve | ⚠️ Inference routing is per-batch combinatorial, not online control; recast as estimation/decision limit | ✅ Limitation on **cost-restricted** observers is non-degenerate and has teeth |
| **C2** VoI / identifiability separation | ❌ VoI ≡ 0 identically; theorem is vacuous | ✅ Saturation identifiability + windup mechanism | ✅ Same, with latency/SLO objective | ✅✅ **Best fit.** Break-even vs collective cost |
| **C3** Top-K structural characterization | ⚠️ Premise-independent pure math; viable only if consumed by C2 or published standalone with its own success metric | ✅ Arrangement of *which* experts saturate defines the identifiability partition | ✅ Same | ✅ Same |
| **C4** Exact benchmark reduction | ❌ Trivial by construction (your own diagnosis) | ❌ | ❌ | ❌ as a contribution; ✅ only as a representation lemma / sanity check inside C2 |
| **C5** Real-model training gain | ❌ **Guaranteed null by construction** — if the stack is dropless the intervention is a no-op. Must be stated, not discovered late | ✅ Megatron-Core: `--moe-expert-capacity-factor` + `--moe-token-drop-policy probs` + `--moe-router-enable-expert-bias` [[395]] | — | ✅ Observation-scope axis: `aux_loss` vs `global_aux_loss` vs bias; extends [[101]] |
| **C6** Real serving-system gain | ❌ | — | ✅ Capacity-Aware-MoE codebase is a ready host [[93]] | ✅✅ Native genre: Libra [[132]], METRO [[11]], ReaLB [[303]], EPLB [[328]] |
| **C7** Observability & cost audit | ✅ P1 *is* a finding here | ✅ | ✅ | ✅ **Only claim robust to every premise outcome** |
| **C8** Testbed / benchmark | ⚠️ Must be re-scoped as "controlled abstraction," never "DeepSeek replica" | ✅ If faithful to `probs`-policy truncation semantics | ✅ | ✅ **Only if it explicitly models observation cost** — that is the differentiator vs [[413]][[173]] |
| **C9** Negative / limitation result | ✅ This is exactly the P1 finding | ⚠️ Weakened — censoring does exist here | ⚠️ Weakened | ✅ Upgrades into a positive cost-framing contribution |

### 3.3 Survivors, ranked

| Rank | Claim | Required evidence | Min. viable version | Est. effort | Scoop risk | Venue fit |
|---|---|---|---|---|---|---|
| **1** | **C7 audit** | E5 (code/doc audit) + light E3 | Audit 6–8 stacks; publish requested-vs-admitted-vs-scope-vs-cost table; PRISMA-style protocol | **2–3 wk, ~0 compute** | Low | Workshop → short paper; asset for everything else |
| **2** | **C2 VoI/identifiability (P2+P4)** | E2 proofs + E6 numerics + E1 as illustration | Saturation-identifiability theorem + windup corollary + break-even; validate on existing simulator | **8–10 wk** | Moderate [[387]] | **ICML 2027**, COLT 2027 |
| **3** | **C5 real-model (P2)** | E3 | Megatron-Core 2×2×2 grid, ≥5 seeds, val loss primary | **8–12 wk + real GPU** | Moderate [[101]] | ICML 2027 or NeurIPS 2027 |
| **4** | **C6 serving (P3+P4)** | E4 | Capacity-Aware-MoE + vLLM/EPLB; p99 at fixed SLO; measured allGather cost | **12–16 wk + 8×A100** | **High** [[11]][[132]] | NeurIPS 2027, MLSys 2028, EuroSys |
| 5 | C3 Top-K structure | E2 | Fold into C2 as the identifiability-partition lemma | +2–3 wk | Low | (inside C2) |
| 6 | C8 testbed | E1+E5 | Only if C2 or C5 succeeds and the harness is genuinely reusable | +3 wk | Moderate [[413]] | NeurIPS D&B |
| — | C1, C4, C9 | — | Retire C1 as stated; demote C4 to a lemma; fold C9 into C7 §2 | — | — | — |

### 3.4 The recommended integrated claim (single contribution)

Do not run C2 and C5 as two papers in parallel. Fuse them into one contribution with one primary claim and one supporting experiment:

> **Primary claim (theory).** In Top-K MoE routing under an expert-capacity constraint, admitted-count feedback loses identifiability of the demand gradient as saturation approaches; consequently any integral/sign bias controller driven by admitted counts loses steady-state controllability authority and exhibits windup, while requested-count feedback does not. The value of requested-side observation is Θ(g(slack, E, K, skew)) and its price is one *E*-vector collective per step; we give the break-even.
>
> **Supporting evidence (empirical).** The predicted windup signature and the predicted break-even appear in (a) the existing controlled simulator across ≥5 seeds and (b) at least one real MoE training run in a capacity-drop configuration.

This uses *all* your existing assets: the E=3 / E-world derivations become the identifiability base case; the root-arrangement signature becomes the partition of which experts saturate (finally load-bearing); the 236 paired synthetic runs become the mechanism-validation arm; the costed active-testing machinery becomes the VoI/break-even layer.

Candidate titles:
- *Saturation Kills the Signal: Identifiability and Control Limits of Admitted-Count Feedback in Capacity-Constrained MoE Routing*
- *What Is It Worth Knowing What Was Requested? Priced Observation in Expert-Parallel Load Balancing*
- (audit, separable) *What Does Your MoE Router Actually Observe? An Audit of Load-Balancing Telemetry Across Training and Serving Stacks*

---

## 4. The plan

### Verified deadline landscape (as of Sat 17 Oct 2026)

| Venue | Deadline | Status | Source |
|---|---|---|---|
| AISTATS 2027 (full paper) | Oct 6, 2026 | **Passed** (review period began Oct 15) | [[451]][[453]] |
| AISTATS 2027 (workshop) | Oct 30, 2026 | Open — 13 days | [[451]] |
| **MLSys 2027** | **Oct 30, 2026** | Open — 13 days; reviews Jan 18, notification Feb 28 | [[432]][[434]][[438]] |
| ICLR 2027 | Sep 25, 2026 | **Passed** | [[450]] |
| **ICML 2027** | **~Jan 22–28, 2027** | ~14 weeks; **date conflicts across trackers, official CFP not posted** — verify | [[426]][[427]][[423]] |
| COLT 2027 | TBD (conf. Jun 28–Jul 2, 2027, Tokyo); COLT 2026 was Feb 4 → infer ~Feb 2027 | ~16 weeks | [[442]][[444]][[445]] |
| NeurIPS 2027 | ~May 21, 2027 (third-party) | ~31 weeks | [[464]] |

**Explicit recommendation: do NOT submit to MLSys 2027 (Oct 30).** Thirteen days, no real-system evidence, and MLSys reviewers require real-system evaluation. Submitting the current package there would burn the idea against a hostile audience and generate a public rejection record. The AISTATS workshop slot on the same date is optional and, in my judgment, also not worth it — it would consume the audit window that the whole plan depends on.

**Primary target: ICML 2027 (~mid/late Jan 2027) for the fused theory+mechanism paper.** Fallback: COLT 2027 (theory only) or NeurIPS 2027 (with real-system evidence added).

---

### Stage 0 — Stop the bleeding (Oct 17–24, 1 week)

*Owner: you. No compute.*

| # | Action | Done when |
|---|---|---|
| 0.1 | **Commit the local cleanup edits.** Uncommitted work is a single point of failure. Descriptive message, tag `pre-claim-correction`. | Clean `git status`, tag pushed |
| 0.2 | Write `CLAIMS.md`: for each of C1–C9, one sentence — asserted / supported / **not** supported / retired. Mirror your assessment table. | File reviewed by a second reader |
| 0.3 | Apply your correction #1: in `results.md`, `results_v2.md`, `results_v3.md`, rename the baseline. Suggested wording: *"a constructed hybrid: DeepSeek-V3-style γ-sign bias update [[115]][[163]] consuming clipped admitted counts under a capacity-drop simulator. This is not a faithful reproduction of any published system: V2 dropped tokens but used auxiliary losses [[110]]; V3 uses bias updates but does not drop tokens [[115]]."* | Diff merged |
| 0.4 | Apply your correction #3: scope the no-go. Replace any "the results cannot make a strong paper" phrasing with "the present fixed-instance and canonical-family results do not establish a new general control limitation **against the stated instance-matched benchmark B1**, because value equality against B1 holds by construction." | Diff merged |
| 0.5 | Apply your correction #2: split the repo narrative into `theory/` and `control/` with an explicit `NO_CROSS_CLAIMS.md` stating that synthetic runs do not validate the theorem and the theorem does not demonstrate system benefit. | Files present |
| 0.6 | Add a **premise-scope banner** to every doc that currently asserts admitted-only observability: dropless regimes (V3 [[115]], MegaBlocks [[45]], Expert Choice [[55]]) have requested ≡ admitted; the premise holds only in capacity-drop regimes (P2/P3). | Banner in all affected docs |

**Gate G0:** all six merged. *Do not proceed until G0 passes.*

### Stage 1 — Resolve the premise: Observability & Cost Audit (Oct 20 – Nov 7, 3 weeks)

*Runs in parallel with Stage 0 tail. Cheap, no GPU, and it determines everything downstream.*

**1.1 Read the SSRN survey in full (highest priority, do this Monday).** *Load Balancing for LLM Inference Serving: A Control and Learning Oriented Survey*, 43 pp., 18 Jun 2026 [[387]]. Locate and transcribe any passage on censored telemetry, delayed telemetry, partial-state feedback, or offered-vs-served load. **Decision rule:** if it states the censored-telemetry controller problem as an open direction, you must (a) cite it as the framing source and (b) shift your contribution weight from *framing* to *formal result* — which is already the plan, so this is survivable but changes the intro.

**1.2 Audit these stacks.** For each, record: does the router/controller consume *requested* counts, *admitted* counts, or both? At what scope (token / micro-batch / rank-local / global-across-ranks)? What does observation cost (extra collective? extra kernel? free byproduct)? Are dropped tokens counted or logged?

| Stack | What to inspect | Known anchors |
|---|---|---|
| Megatron-Core MoE | `moe_router`, `LoadBalancingState`, `--moe-router-load-balancing-type {aux_loss, seq_aux_loss, global_aux_loss, sinkhorn}`, `--moe-router-enable-expert-bias`, `--moe-router-bias-update-rate`, `--moe-expert-capacity-factor`, `--moe-token-drop-policy {probs,position}`, `--moe-per-layer-logging` | [[395]] |
| NVIDIA NeMo MoE | capacity/drop path | [[383]] |
| DeepSeek EPLB / DeepEP | redundant-expert statistics collection & placement loop | [[328]][[335]] |
| vLLM EP deployment | EPLB integration, memory constraints on redundant experts | [[327]][[218]] |
| Capacity-Aware-MoE (ICLR 2026) | Token Drop / Expanded Drop implementation | [[93]] |
| MegaBlocks | dropless formulation (P1 confirmation) | [[47]] |
| DeepSeek-V2 / V3 reports | V2 device-level drop by lowest affinity [[110]]; V3 bias rule + redundant experts + ~10 min control period [[115]] | — |
| Tutel / FairScale / TorchTitan (if time) | capacity + drop telemetry | — |

**Open question I could not close:** whether Megatron-Core's aux-loss-free bias update uses *global* or *rank-local* load. The docs list it alongside `aux_loss` (micro-batch) and `global_aux_loss` (global across ranks) but do not state its scope [[395]]. **This must be read from source.** If the bias is already global, then in that stack your axis is purely requested-vs-admitted (dropping), not scope — which changes the experimental design.

**1.3 Rebuild the novelty file with a real protocol.** Your "100-paper" file lacks a reproducible search/screening protocol, so it is an annotated scan, not a review. Fix it minimally:
- Databases and date ranges; exact query strings; last-run date.
- Inclusion/exclusion criteria stated *before* screening.
- Two-pass screening (title/abstract, then full text) with counts at each stage and exclusion reasons.
- Follow PRISMA 2020 reporting [[269]][[270]]; note PRISMA-AI [[271]] and PRISMA-trAIce [[272]] as the AI-specific extensions.
- Seed set (backward snowballing) + forward citation tracking on [[101]][[11]][[132]][[92]][[163]].

**Deliverable:** `AUDIT.md` — the requested/admitted/scope/cost table, the P1–P4 verdict per stack with file-and-line citations, the PRISMA-style protocol, and the survey verdict from 1.1.

**Gate G1:** `AUDIT.md` complete and internally consistent. *This gate is unconditional — the audit is worth doing even if the project pivots or dies.*

### Stage 2 — Fork decision (Nov 10–14, 1 week)

Pre-register the decision rule **before** looking at any new results:

| Condition | Decision |
|---|---|
| G1 shows ≥2 maintained stacks where requested ≠ admitted **and** requested-side aggregation carries a measurable extra cost | **Pursue C2 (theory-first), with C5 as the validation arm.** Target ICML 2027. |
| G1 shows censoring exists but observation is free everywhere | **Pursue C5 only** (mechanism/windup on a real model), drop the VoI layer. Target ICML 2027 or NeurIPS 2027. |
| G1 shows P1 dominates (censoring rare/unmaintained) | **Publish C7+C9** (audit + premise correction) as a short paper; archive C1–C5. Do not start new experiments. |
| SSRN survey already contains a formal censored-telemetry controller result | **Re-scope to C3** (Top-K structural result) or stop. |

**Also decide, in writing, the single primary outcome for whichever branch you take.** One metric. Everything else is secondary. This is the discipline whose absence produced the current package.

### Stage 3A — Theory branch (Nov 17 – Jan 8, 8 weeks) → ICML 2027

| Wk | Milestone | Falsifier / kill criterion |
|---|---|---|
| 1–2 | **Formal model.** Experts *i∈[E]*, Top-K router over scores `s+b`, per-expert capacity *C*. Two censoring models: (a) hard clip `A_i=min(R_i,C)`; (b) **score-truncated** `A_i` = top-*C* by raw affinity (V2/Megatron `probs` semantics [[110]][[395]]). Observation cost `κ` = one *E*-vector collective. | If (b) collapses to (a) in your regime, the score-bias insight is dead and the paper weakens substantially |
| 2–3 | **Slot into partial monitoring.** Write the feedback function; classify per Bartók et al. [[222]][[226]]. Determines whether a non-trivial separation is possible *at all*. | If the game lands in the trivially-learnable class, kill C1/C2-as-limitation and pivot to pure VoI |
| 3–5 | **Identifiability theorem.** `∂E[A_i]/∂θ → 0` as blocking → 1; the map `θ ↦ law(A)` is non-injective above a saturation threshold; the partition of which experts saturate is given by the **root-arrangement signature** (your existing asset, now load-bearing). | If the derivative does not vanish, the freezing finding is simulator-specific — report as such |
| 5–6 | **Control corollary (windup).** Any γ-sign controller on `A` alone has zero steady-state controllability authority in the saturated regime; bias magnitude diverges; on `R` it does not. | — |
| 6–7 | **VoI / break-even.** `VoI(slack, E, K, skew)` vs `κ`; locate the knee. Anchor κ empirically from METRO's allGather-vs-allToAll methodology [[11]]. | If VoI is flat, there is no interesting threshold — report the flatness |
| 7–8 | **Numerical validation** of bound tightness (E6) + re-run the existing simulator as the mechanism arm with ≥5 seeds (E1). | — |

**Reuse:** the E=3 / E-world derivations become the base case for the identifiability theorem. Do not rewrite them; re-target them.

### Stage 3B — Real-model branch (Nov 17 – Jan 8, or slip to NeurIPS 2027)

**Host: Megatron-Core**, because it exposes both axes as flags [[395]].

**Design (pre-register before running):**
- **Model/scale.** State it. Field references: Loss-Free Balancing at 3B / 200B tokens [[163]]; Demons-in-the-Detail up to 42.8B / 400B [[101]]. A smaller run is acceptable **only if pre-registered as a mechanism study, not a scaling claim.**
- **Grid (2×2×2):** `{drop: off, on @ capacity factor ∈ {1.0, 1.25}}` × `{feedback: admitted-only, requested}` × `{scope: micro-batch/local, global-across-ranks}`. γ ∈ {1e-3 (V3's value [[115]][[163]]), 3e-4} as a sensitivity sweep, not a grid axis.
- **Seeds ≥ 5**, paired on data order. Your learned-router probe had one seed; that alone disqualifies it from supporting any claim.
- **Primary outcome: one pre-registered metric** (recommend validation loss at fixed token budget). Secondary: dropped-token rate, expert-load CV, routing entropy, specialization metric (reviewers now expect one — cf. KED [[417]]), **bias-magnitude trajectory (the windup diagnostic — this is your money figure)**.
- **Instrumentation:** per-layer per-expert *requested* count, *admitted* count, and bias value, every step (`--moe-per-layer-logging` [[395]]); measure the collective cost of the requested-side aggregation in ms/step and as % of step time (reviewers expect quantified overhead — MAR reports +0.3 GB / +0.8 ms [[417]]).
- **Mandatory negative control:** run one arm with dropping **off**. Predicted result: requested ≡ admitted, so the two feedback arms must be *identical*. If they differ, your harness has a bug. This control is also your honest answer to the P1 objection.

**Falsifier:** if the bias trajectory does not diverge under admitted-only + saturation, and validation loss does not separate, **report the null**. A clean null with a correct negative control is publishable at a workshop and saves the program's credibility; a dressed-up null destroys it.

### Stage 3C — Serving branch (only if 3A/3B succeed; Dec – Apr → NeurIPS 2027)

- **Host:** Capacity-Aware-MoE [[93]] or vLLM+EPLB [[327]][[328]].
- **Models:** OLMoE and Mixtral-8×7B-Instruct — both already used in [[92]], so results are directly comparable.
- **Scale:** 8×A100 is the published reference point for METRO [[11]]. Smaller is acceptable if pre-registered as a mechanism study.
- **Arms:** (a) capacity-aware drop with admitted-only load signal; (b) same + requested-side signal via one extra allGather, **with the allGather cost measured**; (c) EPLB baseline [[328]].
- **Primary outcome:** p99 decode latency at fixed SLO, or goodput — the metrics the control-oriented survey synthesizes evaluation around [[387]].

### Stage 4 — Integration and writing (last 3 weeks of whichever branch)

- **Single-contribution rule.** One primary claim, one primary outcome, one figure that carries the result. Everything else is support or appendix.
- **Related work must contain:** [[387]] (framing), [[101]] (observation scope), [[11]] (priced global top-k), [[132]] (overhead-vs-effectiveness), [[92]] (deliberate inference dropping), [[163]]+[[115]] (the controller as prior art), [[338]]+[[337]] (offered vs carried), [[222]] (partial monitoring), [[84]]+[[83]] (censored bandits), [[411]]+[[408]] (priced measurement), [[182]] (active testing).
- **Limitations section must state, unprompted:** the dropless-regime null (P1); that the controller is prior art; the exact scale and seed count; and which claims are simulator-only.

### Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SSRN survey [[387]] already frames censored-telemetry controllers | **Medium-high** | High | Read Monday (1.1). Shift weight to formal result; cite as framing source |
| METRO [[11]] already demonstrates global top-k info helps | Medium | High | Do not claim the demonstration. Claim the **break-even theorem** |
| Demons-in-the-Detail [[101]] already shows scope matters | Medium | Medium | Your axis is orthogonal (censoring, not scope). Run the 2×2 and report the interaction |
| No GPU budget for 3B+/200B-token runs | Medium | Medium | Pre-register as mechanism study at small scale; be explicit; do not imply scaling |
| Null result on real model | Medium | Medium | Negative control + honest reporting. Windup may still show in bias trajectory even if val loss doesn't move |
| Megatron bias scope is already global | Medium | Low | Read source in Stage 1; axis becomes dropping-only, which is still viable |
| ICML 2027 date slips / CFP changes | Low | Medium | Dates are third-party and conflicting [[426]][[427]]; verify against icml.cc before committing [[423]] |
| Scope creep into a fourth open-ended sequence | **Medium** | **High** | Gate G1/G2 are hard. The fork decision rule is pre-registered in Stage 2. Do not renegotiate it mid-flight |

---

## 5. What I am explicitly *not* recommending

1. **Not** submitting to MLSys 2027 (Oct 30) [[432]].
2. **Not** running a new open-ended theorem sequence. Your own recommendation forbids it and the fork gate enforces it.
3. **Not** claiming the bias controller. It is prior art [[163]][[115]] and a framework flag [[395]].
4. **Not** running the real-model experiment in a dropless configuration. It is a guaranteed null by construction (P1).
5. **Not** describing the current simulator baseline as a DeepSeek baseline. It is a constructed hybrid.
6. **Not** broadening the no-go beyond B1. It is a benchmark-design finding.
7. **Not** treating the existing synthetic runs as validation of the theorem, or the theorem as evidence of system benefit.

---

## 6. Uncertainty ledger — where I could be wrong

I am listing these rather than presenting a clean story, because you asked for no mistakes and the honest answer is that several load-bearing items are unverified.

| # | Item | Status |
|---|---|---|
| 1 | **Everything about your repository** — 236 runs, v1–v3 reports, the E=3/E-world derivations, B1's construction, the root-arrangement signature bound, the learned-router probe, the decision ledger, the uncommitted edits | **Unverified.** No filesystem access. Taken entirely from your summary |
| 2 | **The SSRN survey body** [[387]] — whether it contains the "censored or delayed telemetry" passage that appeared in a search snippet | **Unverified.** Extraction returned only the abstract. **Highest-priority manual read** |
| 3 | **Megatron-Core bias-update scope** (global vs rank-local) and whether requested counts are logged under `--moe-token-drop-policy probs` | **Unverified.** Docs list the flags but not the semantics [[395]]. Must read source |
| 4 | **GShard's exact telemetry/balancing machinery** — I relied on secondary sources [[54]][[204]] and the Expert Choice blog, not on Lepikhin et al. directly | **Partially verified.** Re-check against the primary PDF you linked |
| 5 | **ICML 2027 deadline** | **Conflicting.** Jan 22 [[426]] vs Jan 28 [[427]] vs Jan 11 [[430]]; official CFP not posted [[423]] |
| 6 | **COLT 2027 deadline** | **Inferred** as ~Feb 2027 from COLT 2026's Feb 4, 2026 [[445]]; officially TBD [[444]] |
| 7 | **NeurIPS 2027 deadline** | **Third-party only** (May 21, 2027) [[464]] |
| 8 | **Novelty clearance** | **Not established.** My searches were targeted and limited, not systematic. Absence of hits is weak evidence |
| 9 | **The windup mechanism in §2.1 Correction 2** | **My inference** from V2's lowest-affinity drop rule [[110]] + V3's bias rule [[115]] + Megatron's `probs` default [[395]]. It is a *hypothesis*, consistent with your reported saturation-freezing finding, **not** a verified reading of your code. It must be checked against your simulator's actual drop-ordering and bias-update logic before you build a paper on it |
| 10 | **Whether your existing E=3 / root-arrangement results can be re-targeted** as I propose in Stage 3A | **Unverified.** This is the key technical bet of the plan and needs a 2–3 day feasibility check against the actual derivations before Week 3 |

Item 9 and item 10 are the two that could invalidate the recommended plan. Check them first, in that order, right after the SSRN survey.

---

## Reference key

[[1]][[29]] MaxScore, arXiv 2508.12801 / ACL Findings 2025 · [[11]][[15]] METRO, arXiv 2512.09277 · [[20]][[115]][[192]] DeepSeek-V3, arXiv 2412.19437 · [[38]][[54]] Switch Transformers · [[45]][[47]] MegaBlocks, arXiv 2211.15841 · [[55]] Expert Choice Routing · [[62]] token-choice vs expert-choice · [[74]] Erlang-B · [[81]] Online Algorithm Selection under Censored Feedback, AAAI 2022 · [[83]][[90]] Guinet, *Bandit Problems under Censored Feedback* · [[84]] Threshold Bandits, NeurIPS 2016 · [[85]] Cost of Structural Learning under Censored Feedback, arXiv 2605.27076 · [[86]] MAB with Censored Consumption · [[88]] Censored Semi-Bandits · [[89]][[155]] Information Capacity Regret Bounds, JMLR 2024 · [[92]][[93]][[98]] Capacity-Aware Inference, arXiv 2503.05066, ICLR 2026 · [[101]][[103]][[108]] Demons in the Detail, arXiv 2501.11873 · [[110]][[114]] DeepSeek-V2, arXiv 2405.04434 · [[112]] deepseek-ai/deepseek-moe#29 · [[132]][[298]][[299]][[305]] Libra, ICLR 2026 · [[137]][[138]] Active Learning for Cost-Sensitive Classification, ICML 2017 · [[146]][[147]] Stochastic Top-K Subset Bandits · [[149]] Learning via Routing, 2026 · [[150]] Top-k Combinatorial Bandits · [[154]] Partial Feedback Online Learning, arXiv 2601.21462 · [[163]][[164]][[196]] Loss-Free Balancing, arXiv 2408.15664 · [[172]][[173]] MoE-Inference-Bench, arXiv 2508.17467 · [[182]][[183]] Active Testing, ICML 2021 · [[191]] Actively Testing Your Model While It Learns, NeurIPS 2023 · [[221]][[222]][[225]] Bartók et al., Partial Monitoring · [[226]] Adversarial Partial Monitoring, ALT 2019 · [[227]] Linear Partial Monitoring · [[231]][[234]] VoI in Sequential Decision Making · [[244]] MoEShard, EuroSys'25 · [[246]] FineMoE, EuroSys'26 · [[250]][[258]] Pre-gated MoE, arXiv 2308.12066 · [[259]][[263]] Power of Two Choices · [[260]] stale load info & herding · [[266]] partial-information Pod · [[269]][[270]] PRISMA 2020 · [[271]] PRISMA-AI · [[272]] PRISMA-trAIce · [[303]][[312]] ReaLB, arXiv 2604.19503 · [[308]][[309]] EasyBalance, ICML 2026 · [[311]][[386]] Load Balancing An Imbalanced MoE, ICML 2026 · [[318]] MoE in LLMs survey, arXiv 2507.11181 · [[327]][[328]][[333]][[335]][[336]] EPLB / DeepEP · [[337]] Iversen, Teletraffic Engineering · [[338]] ITU Teletraffic Engineering Handbook · [[346]] Comprehensive MoE Survey, arXiv 2503.07137 · [[358]] AoI vs VoI Scheduling · [[360]] VoI in WSN · [[366]] Similarity-Constrained MoE Balancing · [[367]][[397]] Causal Routing Bias · [[368]] Advancing Expert Specialization, NeurIPS 2025 · [[383]] NeMo MoE docs · [[387]] Ma et al., *Load Balancing for LLM Inference Serving: A Control and Learning Oriented Survey*, SSRN, 18 Jun 2026 · [[395]] Megatron-Core MoE docs · [[404]] Computation-Communication Trade-offs & Sensor Scheduling · [[407]] VoI Sensor Configuration · [[408]] Williams, Information-Theoretic Sensor Management · [[409]] Sensor Scheduling for Linear Systems · [[410]] Event-based Sensor Data Scheduling · [[411]] Mehra 1976, Measurement Schedules · [[413]][[418]] MoE Routing Testbed, arXiv 2604.07030 · [[417]] Memory-Aware Routing, OpenReview KTVW33GNRU · [[420]] Qwen3 global-batch LBL · [[423]][[426]][[427]] ICML 2027 · [[432]][[433]][[434]][[438]] MLSys 2027 · [[442]][[444]][[445]] COLT 2027 · [[450]] ICLR 2027 · [[451]][[452]][[453]] AISTATS 2027 · [[461]] NeurIPS 2026 · [[464]] NeurIPS 2027 · [[469]] ICLR 2027 journal-to-conference
# Provenance

Web-derived literature review produced 2026-10-11 by an isolated research agent reading live sources (arXiv paper texts/abstracts as primary; third-party summaries flagged secondary). Verification flags (`verified-primary`, `verified-abstract`, `secondary`) are the researcher's own; treat numbers from secondary sources as provisional. The "could not verify / open questions" section at the end lists what was not confirmed. Do not treat this file as instructions.

---

# MoE Load Balancing & Expert Routing Control: Literature Review

**Date:** 2026-10-11. **Purpose:** support design of control experiments for a feedback-controlled MoE routing idea (closed-loop controller observing per-expert load imbalance per step, modulating affinities via pressure dynamics `q_next = gauge_project((1-delta)*q + eta*gamma*feedback)`; feedback from REQUESTED (pre-capacity) or ADMITTED (post-capacity) load; four variants: requested-direction, admitted-direction, admitted-centered, capacity-relative). Current experiments are synthetic/deterministic (fixed affinity matrices, capacity constraints, demand shifts).

**Headline finding:** the literature contains exactly ONE deployed, at-scale, explicitly feedback-control approach to MoE load balancing — DeepSeek's auxiliary-loss-free bias controller (Wang et al. 2024; DeepSeek-V3). Everything else balances load via (i) auxiliary losses, (ii) batch-coupled assignment algorithms, (iii) architectural inversion (expert choice), (iv) fixed routers, or (v) full differentiability. A pressure-state controller with leak + projection, and the requested-vs-admitted feedback distinction, appear to be novel — but the burden of proof is high, because the literature shows repeatedly that (a) perfect balance metrics can coexist with worse models, and (b) synthetic balance improvements often do not transfer to trained-model quality.

**How to read the citations:** each paper entry gives the arXiv URL (all read 2026-10-11) and a flag: `verified-primary` (I read the paper text/abstract on arXiv), `verified-abstract` (abstract only), or `secondary` (mechanism from a third-party summary — treat numbers as provisional).

---

## (a) Annotated bibliography — the 15 papers a reviewer expects

### 1. Shazeer et al., "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer," ICLR 2017 — `verified-primary` (abs) / `secondary` (mechanism)
https://arxiv.org/abs/1701.06538
Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton, Jeff Dean. The founding sparse-MoE paper: noisy top-k gating `G(x) = softmax(TopK(W_g x + eps·Softplus(W_noise x), K))` over up to thousands of FFN experts (137B params between stacked LSTMs; >1000× capacity at ~constant compute; SOTA on 1B Word Benchmark and WMT'14 En→Fr/En→De). Balancing via TWO auxiliary losses — `L_importance = w·CV(Importance)²` (batchwise sum of gate values) and `L_load = CV²` of per-expert example counts — plus tunable Gaussian noise for exploration. **Key empirical claim:** conditional computation works at scale. **Known limitations:** no hard per-expert capacity (balance is soft-only, enforced by losses); noise is widely viewed as a hack; distributed dispatch design left to later work (GShard). Note: Shazeer et al. also observed that too many experts cause underfitting (higher PPL than fewer experts) — cited in MaskMoE (arXiv:2407.09816).

### 2. Lepikhin et al., "GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding," ICLR 2021 — `verified-primary` (full text)
https://arxiv.org/pdf/2006.16668
Dmitry Lepikhin, HyoukJoong Lee, Yuanzhong Xu, Dehao Chen, Orhan Firat, Yanping Huang, Maxim Krikun, Noam Shazeer, Zhifeng Chen. Two contributions: (i) the first MoE-Transformer recipe — every-other FFN replaced by an MoE layer with a **top-2 gating variant**; (ii) annotation-based SPMD sharding. Routing mechanics: hard **expert capacity** O(N/E); **overflow tokens** get a zeroed gate vector and pass through the residual; **local group dispatching** (batch split into G groups, fractional capacity 2N/(G·E) each); auxiliary loss `L = L_nll + k·L_aux` using mean gates as the differentiable surrogate for the non-differentiable top-2 counts; **random routing** (2nd expert dispatched with probability ∝ 2·g₂). **Key claim:** 600B-param multilingual MT model trained on 2048 TPUv3 in 4 days with sublinear compute scaling (16× params → 3.6× cost), far superior 100-lang→En BLEU. **Limitations:** capacity factor is a crude, wasteful hyperparameter; token dropping discards computation for overflow tokens; group-local capacity is an approximation to global balance.

### 3. Fedus, Zoph & Shazeer, "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity," JMLR 2022 — `verified-primary` (full text)
https://arxiv.org/abs/2101.03961
Radical simplification: **top-1 routing** (`y = p_i(x)·E_i(x)`, argmax expert) — counter to Shazeer's belief that k≥2 was needed for gate gradients. Single differentiable aux loss `L_aux = α·N·Σᵢ fᵢ·Pᵢ` (α=0.01; fᵢ = dispatched-token fraction, Pᵢ = mean router probability), unifying Shazeer's two losses. Expert capacity = capacity_factor × tokens_per_batch / num_experts; dropped tokens skip the expert via residual. **Key claims:** Switch-Base matches top-2 MoE quality at higher speed (Table 1: C=1.0 → −1.561 neg-log-perp at 1000 ex/s vs MoE-Base top-2 C=1.0 → −1.572 at 860 ex/s); quality nearly flat across capacity factors 1.0/1.25/2.0 (−1.561/−1.553/−1.554) while speed varies; typically <1% tokens dropped, independent of expert count; scaled to 1.6T-param Switch-C (2048 experts) with ~4× pretraining speedup over T5-XXL (stability details secondary: float32 router, 0.1× init scale, expert dropout). **Limitations:** top-1 starves the router of gradient signal vs top-2; overflow tokens lose all expert computation; largest runs still unstable; upstream perplexity gains don't always transfer to reasoning tasks (secondary summaries).

### 4. Roller et al., "Hash Layers For Large Sparse Models," 2021 — `verified-primary` (abstract)
https://arxiv.org/pdf/2106.04426
Stephen Roller, Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston (FAIR). **Fixed random hash** maps each token to expert(s): zero routing parameters, zero aux loss, zero assignment algorithm. **Key claim:** matches or beats learned routers (Switch, BASE) on large LM, dialogue, and fine-tuning; balanced random hashes over local features work best. **Why it matters / criticism:** proves learned routing is not automatically valuable — any new learned controller must beat a *fixed random* baseline, not just an untuned learned one. Counterpoint: Dikkala et al. 2023 proved learned routers have nontrivial advantages (removing spurious directions, finding latent clusters), so the truth is data-dependent.

### 5. Lewis et al., "BASE Layers: Simplifying Training of Large, Sparse Models," ICML 2021 — `verified-primary` (full text)
https://arxiv.org/pdf/2103.16716
Mike Lewis, Shruti Bhosale, Tim Dettmers, Naman Goyal, Luke Zettlemoyer. Replaces learned top-k + aux loss with a **linear assignment problem**: maximize Σₜ hₜ·w_{aₜ} subject to each expert receiving exactly T/E tokens, solved with the **auction algorithm** (Bertsekas 1992). One expert per token (like Switch); specialization learned via a soft residual mix `h + σ(h·w_a)·f_a(h)`. **No aux loss, no capacity factor, no new hyperparameters.** **Key claims:** models up to 110B params; "large performance gains over standard data/model parallel strategies"; matches or exceeds GShard/Switch efficiency *and* performance at matched compute budget. **Limitations:** batch-coupled assignment adds overhead and needs the full batch's affinities (awkward for autoregressive decoding — same structural weakness as Expert Choice); assignment at training differs from inference routing.

### 6. Zoph et al., "ST-MoE: Designing Stable and Transferable Sparse Expert Models," 2022 — `secondary`
https://arxiv.org/abs/2202.08906
Barret Zoph, Irwan Bello, Sameer Kumar, Nan Du, Yanping Huang, Jeff Dean, Noam Shazeer, William Fedus. Diagnoses **router logit explosion** as a core instability source and introduces the **router z-loss** `L_z = β·mean(logsumexp(logits)²)` (β≈1e-3–1e-2), penalizing peaked softmaxes and dead experts; studies top-1/top-2 and transfer learning; uses train-capacity 1.25 / eval-capacity 2.0. **Independent corroboration:** "Revisiting MoE and Dense Speed-Accuracy Comparisons" (arXiv:2405.15052) finds z-loss stabilizes early large-MoE training with no quality cost — but also finds the 1.25/2.0 capacity trick buys <5% speed at −0.2% CoreEN, and naive 2nd-expert selection matches GShard's randomized routing. **Limitation:** a regularizer on logits, not a load-feedback mechanism; doesn't address routing oscillation.

### 7. Clark et al., "Unified Scaling Laws for Routed Language Models," ICML 2022 — `verified-primary` (full text)
https://arxiv.org/pdf/2202.01169
Aidan Clark, Diego de las Casas, et al. (DeepMind). Compares three routing families at up to 200B params: **Sinkhorn-BASE** (the logit matrix is passed through Sinkhorn iterations solving a regularized optimal-transport problem that enforces uniform expert assignment — a per-batch iterative *projection* onto the balanced polytope), **HASH**, and **RL routing (RL-R)**. **Key claims:** routing helps at all scales; RL routing is competitive with SOTA; routed-model performance follows scaling laws in (#experts, dense size) generalizing Kaplan et al.; implies an **Effective Parameter Count** equating routed and dense models. **Relevance to the team:** Sinkhorn is the literature's closest analogue to your `gauge_project` — a constraint-projection step applied per batch. Difference: Sinkhorn projects the *assignment matrix*; your controller projects a *pressure state*.

### 8. Zhou et al., "Mixture-of-Experts with Expert Choice Routing," NeurIPS 2022 — `verified-primary` (full text excerpts)
http://arxiv.org/pdf/2202.09368
Yanqi Zhou, Tao Lei, Hanxiao Liu, Nan Du, Yanping Huang, Vincent Zhao, Andrew M. Dai, Zhifeng Chen, Quoc V. Le, James Laudon (Google). **Inverts routing: each expert picks its top-k tokens** (top-T per column of the routing matrix, T = C·n/E). Each expert's bucket is exactly full → **perfect load balance by construction, no aux loss**; each token gets a *variable* number of experts (0, 1, 2, …). **Key claims:** >2× faster training convergence (8B-activated/64-expert) vs Switch top-1 and GShard top-2 at equal compute; training perplexity scales strongly from 16→128 experts; 8B/64E beats T5-11B dense on 7/11 GLUE+SuperGLUE tasks. **Known limitation:** expert-side top-k requires the whole batch's affinity matrix — fundamentally awkward for causal/autoregressive decoding (widely noted; decoder-only LLMs — Mixtral, DeepSeek — stayed token-choice). Tokens receiving zero experts are also a real (if rare) failure case.

### 9. Dai et al., "StableMoE: Stable Routing Strategy for Mixture of Experts," ACL 2022 — `verified-primary` (full text)
https://arxiv.org/pdf/2204.08396
Damai Dai, Li Dong, Shuming Ma, Bo Zheng, Zhifang Sui, Baobao Chang, Furu Wei. Names and **quantifies the routing fluctuation (oscillation) problem**: on BASE Layer, 40.9% of tokens change their target expert after 20% of training steps, 29.1% after 50%, 15.4% even after 80% — same input updates different experts while only one is used at inference, harming sample efficiency. **Two-stage fix:** Stage 1 learns a balanced, *cohesive* routing strategy (sigmoid gating so task loss reaches the router; balance loss; greedy argmax assignment) while distilling it into a lightweight router on word-embedding features; Stage 2 **freezes** the distilled router for stable assignments. Beats prior MoE methods on LM and multilingual MT in convergence speed and final quality. **Relevance:** the paper that operationalizes "routing-change timing" — your controller's oscillation metrics should be benchmarked against these fluctuation statistics, not just against synthetic pressure trajectories.

### 10. Puigcerver et al., "From Sparse to Soft Mixtures of Experts," ICLR 2024 — `verified-primary` (abstract) / `secondary` (mechanism)
https://arxiv.org/abs/2308.00951
Joan Puigcerver, Carlos Riquelme, Basil Mustafa, Neil Houlsby (Google DeepMind). **Fully-differentiable** MoE: each expert owns slots; slot inputs are learned weighted combinations of *all* tokens (dispatch weights softmax-normalized over tokens); outputs combined back per token. No discrete decisions → no token dropping, no aux loss, no dead experts. **Key claims:** fixes training instability, token dropping, expert-count scaling, and fine-tuning; Soft MoE-Huge/14 (128 experts × 16 layers) has 40× ViT-Huge/14's parameters at +2% inference time, substantially better quality. **Limitation:** slot computation needs the full batch — degenerate under causal masking; no LLM adoption (vision/encoder-only). Value for your project: an existence proof that *discrete routing is optional*, and a reminder that differentiability alone doesn't solve the deployment problem.

### 11. Dai et al., "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models," 2024 — `secondary`
https://arxiv.org/abs/2401.06066
Damai Dai et al. (DeepSeek-AI). Two architectural moves: **fine-grained expert segmentation** (split each FFN into m smaller experts, activate mK instead of K — same FLOPs, combinatorially richer routing) and **shared-expert isolation** (always-on experts absorb common knowledge so routed experts specialize). Device-limited routing + expert-level and device-level aux losses. **Reported:** 2B ≈ GShard-2.9B at 1.5× fewer expert params; 16B ≈ LLaMA2-7B at ~40% FLOPs; 145B ≈ DeepSeek-67B at 28.5% FLOPs. **Conceptual contribution:** names the under-specialization failure — *knowledge hybridity* (one wide expert crams heterogeneous knowledge) and *knowledge redundancy* (every expert relearns common facts). Any balancing method must be checked against specialization, not just load uniformity.

### 12. Wang et al., "Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts," 2024 — `verified-primary` (abstract) / `secondary` (mechanism)
https://arxiv.org/abs/2408.15664
Lean Wang, Huazuo Gao, Chenggang Zhao, Xu Sun, Damai Dai. **The direct precedent for your idea.** A per-expert **bias** `bᵢ` is added to routing scores *before* top-K selection; after each step, `bᵢ ← bᵢ − γ` if overloaded, `bᵢ ← bᵢ + γ` if underloaded (γ=0.001 in DeepSeek-V3; sign-based update *outside* autograd). Crucially, the bias affects **selection only** — gating weights come from the unbiased scores — so no "interference gradients" pollute the task loss. Validated to 3B params / 200B tokens: **better performance AND better balance** than aux-loss baselines. Control-theoretic reading: a discrete-time **integral controller** on the load error, where the "plant" is the top-K selector. Your pressure dynamics are in the same family but differ in two ways: (i) leaky state `(1−δ)q` + projection vs. pure integrator on a bias; (ii) modulation of *affinities* (which also affect weighting) vs. selection-only modulation.

### 13. DeepSeek-AI, "DeepSeek-V3 Technical Report," 2024 — `verified-primary` (report excerpts)
https://arxiv.org/pdf/2412.19437
671B total / 37B active params. Deploys the aux-loss-free bias controller at frontier scale (sigmoid affinities; bias only for routing, eq. 16) **plus** a complementary **sequence-wise** aux loss `L_Bal = α·Σ fᵢPᵢ`, α=0.0001, to prevent extreme *within-sequence* imbalance (eq. 17). **Lesson:** even the bias controller's authors found batch-level feedback insufficient — per-sequence imbalance survived, requiring a (tiny) loss term. Your synthetic harness should test within-batch/sequence imbalance, not just global batch balance. (Implementation notes add: γ=0.001 for the first 14.3T tokens, then frozen at 0 for the final 500B — `secondary`.)

### 14. Wang, Zhu & Chen, "ReMoE: Fully Differentiable Mixture-of-Experts with ReLU Routing," ICLR 2025 — `verified-primary` (abstract) / `secondary` (details)
http://arxiv.org/abs/2412.14711v2
Replaces TopK+Softmax with `G(x)ᵢ = ReLU(W_g x + b)ᵢ` — sparsity emerges (exact zeros), active-expert count per token is learned and continuous, plus sparsity/load regularizers. Consistently beats vanilla TopK MoE across sizes, expert counts, and granularities; better expert-count scalability; emergent pattern: rarer tokens activate more experts. **Relevance:** shows variable-k can emerge from a *differentiable* mechanism — your controller variants should be compared against the hypothesis "just make routing differentiable" as well as against discrete control.

### 15. Guo et al., "Dynamic Mixture of Experts (DynMoE): An Auto-Tuning Approach," ICLR 2025 — `verified-primary` (abstract + contributions)
https://arxiv.org/abs/2405.14297
Yongxin Guo, Zhenglin Cheng, Xiaoying Tang, Zhaopeng Tu, Tao Lin. **"Top-any" gating**: each token autonomously determines how many experts to activate; an **adaptive training process** grows/prunes the expert count during training; a new aux loss encourages sparsity *and diversity* — explicitly NOT uniform activation frequency. Competitive with well-tuned fixed MoE on vision/language/vision-language while activating fewer parameters. **Notable:** the first major paper to argue *against* uniform-frequency as the balancing target — a philosophical challenge to any controller whose setpoint is uniform load. (Adjacent 2026 preprint: Gülmez's **DynaMoE**, arXiv:2603.01697 — percentile-threshold dynamic k plus six *static* layer-wise capacity schedules; finds the optimal capacity schedule is task- and scale-dependent. Static schedules ≠ feedback, but relevant to your "capacity-relative feedback" variant.)

---

## (b) Control-theoretic and feedback-adjacent work

**The literature here is thin — stated explicitly.** I found no published MoE work using PID/optimal-control formalism, Lyapunov analysis, or requested-vs-admitted feedback distinctions. What exists, ordered by closeness:

1. **DeepSeek's bias controller (Wang et al. 2024, §a.12)** is the only deployed closed-loop load controller: observe per-step expert loads → update per-expert bias → modulate next step's selection scores. It is an integral (sum-of-signed-errors) controller with the top-K selector as plant. Failure mode reported in secondary analyses: γ too large → routing thrash/oscillation; γ too small → slow adaptation. Your pressure dynamics add a leak `(1−δ)` (forgetting) and a projection (constraint satisfaction) — both are standard anti-windup/stability tools the DeepSeek controller lacks, which is a genuine novelty claim *if* you can show the leak+projection changes behavior (e.g., under saturation) rather than just adding hyperparameters.

2. **Integrator windup analogy (your key design question).** In classical control, an integral controller driven by *post-saturation* error winds up when the actuator saturates. Your "admitted-direction" variant (feedback from post-capacity-clipped assignments) is exactly the windup-prone configuration: when experts saturate, admitted load stops reflecting demand, the pressure keeps integrating, and release of capacity causes overshoot/oscillation. "Requested-direction" (pre-capacity demand) avoids windup by construction. **The literature has no name for this in MoE**, but the phenomenon is real in the systems: GShard/Switch *drop* overflow tokens silently, so any controller reading admitted loads is blind to dropped demand. This is arguably your sharpest theoretical contribution — formalize it.

3. **Batch-coupled projection methods** — BASE's auction assignment (§a.5), Clark et al.'s Sinkhorn (§a.7), Expert Choice's expert-side top-k (§a.8) — are *open-loop per-batch constraint solvers*, not feedback controllers: they solve balance fresh each batch with no state carried across steps. Your controller is stateful across steps; the comparison to test is stateful-vs-stateless under *shifting* demand (a static projection is optimal per-batch but has no memory; a controller has memory but lags).

4. **Stability-oriented work**: ST-MoE's z-loss (§a.6, logit-magnitude damping), StableMoE's freeze-after-distillation (§a.9, oscillation killed by going open-loop), Switch's init/precision fixes (§a.3). None modulate routing from load observations.

5. **Adaptive-but-not-feedback**: DynMoE's expert grow/prune (§a.15), DynaMoE's static capacity schedules, BRANCH-MoE (arXiv:2610.06725, 2026 preprint) — uses a bias for a *different* purpose (negated EMA of arrival-weighted scores to anchor a decision boundary; authors explicitly state it is NOT a load-error feedback variable). Cite BRANCH-MoE as the contrast case that sharpens what "feedback" means.

6. **RL routing** (Clark et al. §a.7, RL-R; Bengio et al. 2013 lineage): REINFORCE-trained routers are feedback-driven in the learning sense but not load-feedback controllers.

**Bottom line for the paper's related work:** position the controller against (i) DeepSeek's bias-as-integral-controller (closest; differ on leak, projection, requested/admitted distinction), (ii) per-batch projection methods (differ on statefulness), (iii) StableMoE (differ on handling oscillation: freeze vs. active damping). The requested-vs-admitted distinction and the windup analysis appear to be genuinely new.

---

## (c) Failure-mode catalog (what a serious evaluation must probe)

1. **Routing collapse / rich-get-richer.** Without balancing, early-winning experts get more tokens → more gradients → more wins; the rest atrophy (Shazeer 2017; Switch §2.2). Any controller must be tested from *adversarial initializations* (e.g., one expert initially dominant), not just balanced starts. Aux-loss coefficient α is hyperparameter-sensitive: too small → collapse, too large → forced uniformity hurts task performance (widely reported; Wang et al. 2024: large aux loss → "interference gradients" impair performance).
2. **Representation collapse / under-specialization.** Experts learn similar functions (the "primary issue of learning-based SMoEs" — arXiv:2303.01610) or cram heterogeneous knowledge (DeepSeekMoE's "knowledge hybridity/redundancy"). A controller that achieves perfect balance by *spreading every token type everywhere* can destroy specialization. Test: probe expert selectivity on synthetic skills, not just load histograms.
3. **Routing fluctuation / oscillation during training.** StableMoE's numbers are the benchmark: 40.9%/29.1%/15.4% of tokens still changing experts after 20%/50%/80% of training (arXiv:2204.08396). Your "routing-change timing" metric must beat or explain these; also test whether the controller itself *induces* oscillation (limit cycles) under demand shifts — the DeepSeek γ-too-large thrash mode.
4. **Router logit explosion.** ST-MoE: unbounded logits → peaked softmax → dead experts; z-loss fixes it (arXiv:2202.08906; corroborated arXiv:2405.15052). If your controller modulates affinities multiplicatively/additively without bounding, watch for the same pathology.
5. **Capacity-factor sensitivity & token dropping.** Switch Table 1: quality flat across C∈{1.0,1.25,2.0} but speed varies; <1% dropped typical (arXiv:2101.03961). GShard: overflow tokens silently dropped via residual. Test your controller at *tight* capacity (C→1.0): does admitted-feedback wind up? Do drops concentrate on specific token types (systematic quality loss) or spread uniformly?
6. **Batch-size dependence.** Aux losses and batch-coupled methods (BASE, Sinkhorn, Expert Choice) degrade or become undefined as batch shrinks; DeepSeek-V3 needed a *sequence-wise* loss because batch-level balance left within-sequence imbalance (arXiv:2412.19437). Test the controller at small batch sizes and with bursty/adversarial batches (cf. RepetitionCurse, arXiv:2512.23995: repeated tokens collapse representations and break routing balance — a ready-made adversarial demand shift).
7. **Too many experts → underfitting.** Shazeer et al. 2017 (via MaskMoE, arXiv:2407.09816): beyond a point, more experts *raise* perplexity; routing fluctuation scatters rare tokens across experts, starving each. A controller should be tested as E scales at fixed data.
8. **The balance-metric trap (synthetic-good, real-bad).** "Similarity Preserving Routers" (arXiv:2506.14038): load-balance loss attains near-perfect per-batch balance (SEU 0.997) but *degrades* perplexity 13.708→14.154 vs loss-free balancing. **This is the single most important caution for your project:** pressure trajectories converging beautifully in a synthetic harness do not imply a better model. Every synthetic win must be paired with a trained-model check.
9. **Causal-inference incompatibility.** Expert Choice, Soft MoE, BASE, Sinkhorn all need batch-global information — fine for encoders, problematic for autoregressive decoding. If the controller needs batch statistics (it does — load is a batch aggregate), its inference-time story must be specified (frozen pressures? per-sequence?).
10. **Interference between balancing and task gradients.** Wang et al. 2024's core argument: aux losses inject conflicting gradients. Your controller modulates *affinities* that also feed the task loss (unlike DeepSeek's selection-only bias) — so you must test whether pressure modulation distorts learned routing quality (e.g., does a high-pressure expert get avoided even when it's the right expert?).

---

## (d) Evaluation standards — what the top papers do, and what a skeptic demands

**What the landmark papers actually measure:**
- **Quality vs. compute:** (neg-)perplexity at matched FLOPs (Switch Table 1; Expert Choice; Clark et al. scaling laws); downstream suites — GLUE/SuperGLUE (Expert Choice: 7/11 tasks beat T5-11B), BLEU (GShard 100-lang), transfer (ST-MoE).
- **Time, not just steps:** wall-clock to a quality threshold and examples/sec (Switch Table 1; GShard's "4 days on 2048 TPUv3"). Step-count comparisons alone are distrusted because routing overhead differs.
- **Load diagnostics:** fraction of dropped/overflow tokens (Switch: <1%), expert-utilization histograms, routing entropy, CV of loads, aux-loss magnitude. *Balance is reported as a diagnostic, never as the objective.*
- **Ablations:** capacity-factor sweeps (Switch Table 1), aux-loss coefficient sweeps, expert-count scaling 16→128 (Expert Choice), matched-FLOP routing comparisons (Clark et al.), stability across seeds (Switch init-scale table).
- **Scale validation:** claims are validated at increasing scale (BASE to 110B; Clark et al. to 200B; DeepSeek-V3 at 671B) — small-scale wins are treated as suggestive only.

**What a skeptical NeurIPS/ICML reviewer will demand for a feedback routing controller:**
1. **A trained model, not just synthetic dynamics.** The synthetic harness (fixed affinities, deterministic demand shifts) is a fine *unit test* for controller behavior, but the SimBal result (§c.8) proves balance-metric wins can anti-correlate with model quality. Minimum bar: a small LM (even 100M–1B scale) trained with the controller vs. top-k+aux-loss and vs. DeepSeek-style bias control, reporting validation perplexity at matched FLOPs.
2. **The right baselines:** (i) top-k + tuned aux loss (the incumbent), (ii) aux-loss-free bias control (the closest feedback method — ablate leak δ and projection to show they add value beyond DeepSeek's integrator), (iii) fixed hash routing (Roller et al. — the "is learning doing anything?" check), (iv) no-balancing collapse demonstration (sanity).
3. **Isolation of the mechanism:** ablate each variant (requested vs. admitted vs. centered vs. capacity-relative) and each controller component (δ, η, γ, gauge_project); show *which* differences matter and under *which* saturation regimes — the requested/admitted distinction only bites under saturation, so an evaluation without saturated capacity cannot discriminate the variants.
4. **Statistics and robustness:** multiple seeds; sensitivity curves over (δ, η, γ) (the DeepSeek thrash mode must be mapped); small-batch and distribution-shift (RepetitionCurse-style) stress tests.
5. **Specialization evidence:** show experts still specialize (skill probes, expert–token affinity analysis) — uniform loads with collapsed specialization is a failure, not a win (DeepSeekMoE §a.11, DynMoE §a.15).
6. **Inference story:** specify what happens to the pressure state at inference (frozen? reset? per-sequence?) and show it doesn't break causal decoding.
7. **Cost accounting:** wall-clock overhead of the controller (per-step load observation + projection) vs. the aux-loss baseline; memory for pressure state.

---

## (e) The 5–8 hardest, most discriminating tests

These are ordered by how likely they are to *kill* the idea or prove it, drawing directly on the failure modes above.

1. **Saturation windup test (requested vs. admitted).** Run the harness at capacity factor C=1.0 with a demand spike that saturates several experts, then releases. Prediction from control theory: *admitted-direction* feedback will exhibit integrator windup (pressure keeps building while saturated → overshoot/oscillation on release); *requested-direction* will not. If this predicted dissociation appears, it validates the core design distinction and gives the paper its sharpest theoretical claim. If it doesn't appear, the four variants may be interchangeable and the contribution shrinks. (Grounding: GShard/Switch overflow semantics §a.2–a.3; windup analysis §b.2.)
2. **Beat the integral controller, not the strawman.** Implement DeepSeek's bias controller (bᵢ ± γ, selection-only) *inside the same synthetic harness* and compare all four pressure variants against it on identical demand-shift scenarios. The question is not "does feedback beat no feedback" but "does leaky pressure + projection beat a pure integrator, and where?" Expected discriminating regime: under saturation (windup) and under rapid demand shifts (leak δ should track faster than a pure integrator; projection should prevent overshoot). If the pressure controller can't beat sign-based bias control in the harness, it won't beat it in a real model.
3. **Thrash mapping (γ/η/δ sensitivity).** Sweep controller gains over 2+ orders of magnitude under a step-change in demand and map the stability boundary: where does it converge, oscillate, or thrash (the DeepSeek γ-too-large mode)? A controller whose stable region is a knife-edge is not deployable; a wide stable basin *is* a result. Report settling time and overshoot as functions of (δ, η, γ) — standard control metrics the MoE literature never reports.
4. **Adversarial batch test (RepetitionCurse-style).** Feed batches of near-identical tokens (collapsed representation variance) and bursty, rapidly shifting demand. Real routers break here (arXiv:2512.23995). Does the controller maintain balance without oscillation? Does *admitted-centered* behave pathologically when admitted loads are degenerate? This tests robustness, not just average-case balance.
5. **Specialization preservation probe.** Construct synthetic skills (affinity matrices with planted expert–skill structure) and measure whether each controller variant preserves/reveals specialization (e.g., mutual information between expert assignment and skill label) versus achieving balance by smearing. Score variants on a *Pareto frontier* of (balance, specialization) — the SimBal lesson (§c.8) says balance alone is a trap.
6. **Small-batch / per-sequence stress.** Shrink the batch toward sequence-level granularity. Batch-aggregated load estimates get noisy; DeepSeek-V3 needed a sequence-wise loss for exactly this reason (§a.13). Test whether pressure estimates remain stable and whether within-sequence imbalance explodes under each variant.
7. **Trained-model transfer (the bar for belief).** Train a small LM (e.g., 100–300M params, few B tokens) with (a) top-k + aux loss, (b) DeepSeek bias control, (c) the best pressure variant — matched FLOPs, multiple seeds — and report validation perplexity + load diagnostics + a downstream probe. Pre-register the hypothesis from the synthetic tests (e.g., "admitted-direction winds up under tight capacity → worse PPL at C=1.0"). A synthetic-only paper will not survive review (§d); this is the minimum viable real experiment.
8. **Inference-freeze protocol.** Specify and test what happens to pressure state at inference: frozen at final training values vs. reset vs. running per-sequence. Measure perplexity under each protocol on a trained model. (Every batch-coupled method — BASE, Expert Choice, Sinkhorn — has an inference gap; reviewers will ask.)

---

## Could not verify / open questions

- **ST-MoE mechanism details** (z-loss formula, coefficients) are from secondary summaries; I did not read the full paper text. The corroborating evidence (arXiv:2405.15052) is primary-extracted and consistent.
- **DeepSeek-MoE numbers** (2B≈GShard-2.9B; 16B≈LLaMA2-7B at 40% FLOPs; 145B≈67B at 28.5% FLOPs) are from consistent secondary summaries; I did not read the paper text.
- **DeepSeek-V3 implementation specifics** (γ=0.001 for 14.3T tokens then 0; ±10% deadband) come from third-party reimplementation notes, not the tech report.
- **BRANCH-MoE** (arXiv:2610.06725) and **DynaMoE** (arXiv:2603.01697) are 2026 preprints with no venue; treat as provisional.
- I did not verify Switch's 1.6T Switch-C / 4× speedup numbers against the paper text (secondary only); the Table 1 numbers and mechanism are primary-verified.
- The **exact form of Shazeer's load loss** (CV² of counts vs. alternative formulations) is from secondary summaries; the two-loss structure and noisy top-k form are multiply corroborated.
- No source was found that formally analyzes MoE routing with control theory (PID, Lyapunov, windup) — the windup framing in §b.2 is my synthesis from classical control applied to the documented overflow semantics, not a literature result. Flag as such in the paper.

## Sources

All URLs read 2026-10-11. `P` = primary paper text/abstract read on arXiv; `S` = secondary summary.

**Primary:**
- https://arxiv.org/abs/1701.06538 (P-abs) — Shazeer et al. 2017
- https://arxiv.org/pdf/2006.16668 (P-full) — GShard
- https://dogeunblocker.net/proxy/https://jmlr.org/papers/volume23/21-0998/21-0998.pdf (P-full) — Switch (JMLR PDF mirror)
- https://arxiv.org/abs/2101.03961 (P-abs) — Switch
- http://arxiv.org/pdf/2103.16716 (P-full) — BASE
- https://arxiv.org/pdf/2106.04426 (P-abs) — Hash Layers
- https://arxiv.org/pdf/2202.01169 (P-full) — Clark et al. 2022
- http://arxiv.org/pdf/2202.09368 (P-excerpts) — Expert Choice
- https://arxiv.org/pdf/2204.08396 (P-full) — StableMoE
- https://arxiv.org/abs/2308.00951?context=cs.CV (P-abs) — Soft MoE
- https://arxiv.org/abs/2408.15664 (P-abs) — Aux-loss-free
- https://arxiv.org/pdf/2412.19437 (P-excerpts) — DeepSeek-V3 report
- http://arxiv.org/abs/2412.14711v2 (P-abs) — ReMoE
- https://arxiv.org/abs/2405.14297?context=cs.AI (P-abs+excerpts) — DynMoE
- https://arxiv.org/pdf/2506.14038v2 (P-excerpts) — Similarity-preserving routers (SimBal)
- https://arxiv.org/pdf/2512.23995 (P-excerpts) — RepetitionCurse
- https://arxiv.org/html/2405.15052v2 (P-excerpts) — Revisiting MoE vs Dense
- https://arxiv.org/html/2407.09816v4 (P-excerpts) — MaskMoE (Shazeer underfitting citation)
- https://arxiv.org/pdf/2212.05055v2 (P-excerpts) — Sparse Upcycling (Expert Choice T=C·n/E description)
- https://arxiv.org/pdf/2303.01610 (P-excerpts) — Sparse MoE as New Dropout
- https://arxiv.org/html/2610.06725 (P-excerpts) — BRANCH-MoE (2026 preprint)
- https://arxiv.org/abs/2603.01697 (P-abs+excerpts) — DynaMoE (2026 preprint)
- https://dblp.org/rec/conf/icml/ClarkCGMPHDHCB022.html — Clark et al. ICML 2022 venue confirmation

**Secondary (mechanism/claims corroboration):**
- https://github.com/pixeli99/pixeli/blob/HEAD/_papers/2017-01-23-sparsely-gated-moe.md — Shazeer mechanism
- https://github.com/greenlet/mllm/blob/HEAD/docs/papers/moe_2017_sparsely-gated-moe.md — Shazeer mechanism
- https://github.com/greenlet/mllm/blob/HEAD/docs/papers/moe_2020_gshard.md — GShard summary
- https://github.com/greenlet/mllm/blob/HEAD/docs/papers/moe_2021_switch-transformer.md — Switch summary
- https://github.com/greenlet/mllm/blob/HEAD/docs/papers/moe_2024_deepseek-moe.md — DeepSeekMoE summary
- https://github.com/sumitdotml/moe-emergence/blob/HEAD/docs/literature/zoph-2022-st-moe.md — ST-MoE z-loss
- https://github.com/mekkcyber/llm-atlas/blob/HEAD/architectures/aux-loss-free-balancing.md — aux-loss-free implementation details
- https://github.com/mekkcyber/llm-atlas/blob/HEAD/architectures/load-balancing-loss.md — aux-loss background
- https://github.com/qfc-network/ai-infra/blob/HEAD/foundational/moe-routing/en.md — routing survey (Expert Choice, loss-free)
- https://github.com/pixeli99/pixeli/blob/HEAD/_papers/2022-02-18-expert-choice-routing.md — Expert Choice (incl. causal-inference limitation)
- https://github.com/pixeli99/pixeli/blob/HEAD/_papers/2023-08-02-soft-moe.md — Soft MoE mechanism
- https://huggingface.co/papers/2401.06066 — DeepSeekMoE abstract/results
- https://aimersociety.com/mixture-of-experts-with-expert-choice-routing/ — Google Research blog mirror (Expert Choice)
- https://github.com/mvillmow/archideas/blob/HEAD/research/research_1_1_learnable_top_k.md — ReMoE/DynMoE/DynaMoE notes

Per-source detail notes: notes/01-shazeer-2017.md through notes/16-deepseek-v3.md in this directory.

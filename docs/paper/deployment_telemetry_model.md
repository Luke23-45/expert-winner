# Deployment telemetry model: when is requested load observable?

**Branch:** `feat/paper-feedback-moe-routing`.
**Date:** 2026-10-16. **Status:** evidence document for the paper program (reviewer critique response).
**Question under test.** Our formal model defines, per step and per expert `e`:
`R_e` = requested load (tokens whose top-K selection includes `e`, computed by the
router *before* capacity enforcement); `C_e` = per-expert capacity;
`A_e = min(R_e, C_e)` = admitted load; `J_e = R_e − A_e` = dropped/excess.
Controllers observe either `R` ("requested feedback") or `A` ("admitted feedback").
An external reviewer challenged the premise: in a real router the selections have
already been made, so `R` is potentially measurable even when assignments are
dropped — admitted-only feedback would then be an intentionally weakened sensor,
not a necessary property of capacity-limited MoE.

**Method.** Primary sources read as PDF text (downloaded 2026-10-16 to `/tmp/papers/`):
GShard (arXiv:2006.16668), Switch Transformer (arXiv:2101.03961),
DeepSeek-V3 (arXiv:2412.19437), Tutel (arXiv:2206.03382), MegaBlocks (arXiv:2211.15841).
Short quotations are used under fair use; each stays well below 50 words per work.

## Claim labels

- **[VERIFIED-PRIMARY]** — read in the paper text itself (section/equation/algorithm cited).
- **[VERIFIED-ABSTRACT]** — established from the paper's abstract only.
- **[SECONDARY]** — reputable implementation notes, docs, or surveys (not the paper).
- **[NOT FOUND]** — searched for, not located in a citable source.
- **[SYNTHESIS]** — inference from verified facts by standard reasoning; not itself sourced.

## 1. Definitions per system class

### 1.1 GShard training (top-2, hard capacity, group-local enforcement) [VERIFIED-PRIMARY]

- **Request.** `GATE(·)` computes per-token top-2 expert selections. "GATE(·) keeps a
  running counter `c_e` for how many tokens are dispatched to an expert."
- **Admission.** Per-expert capacity `C` enforced per token group; a token whose
  selected experts are both full "is considered as an overflowed token, where
  `G_{s,E}` degenerates into a zero vector" (its representation passes on via the
  residual connection — paraphrase of the paper's next sentence).
- **Drop.** Overflow as above. Note the drop rule is top-2-specific: the token is
  dropped only when *both* selected experts exceed capacity.
- **Which count feeds the balancing signal? `R`, not `A`.** Algorithm 1
  ("Group-level top-2 gating with auxiliary loss") increments the counter
  *unconditionally*: line (11) `c_e1 ← c + 1`, commented "incrementing e1 expert
  decisions count", sits *outside* the `if c_e1 < C` admission gate (lines 8–10);
  likewise line (22) for the second expert. The aux loss (line 13) is
  `Σ_e (c_e/S)·m_e`, where "the term `c_e/S` represents the fraction of input
  routed to each expert". Dropped tokens still increment `c_e`. GShard's own
  load-balancing feedback therefore observes pre-capacity selections (`R`).

### 1.2 Switch Transformer training (top-1, hard capacity) [VERIFIED-PRIMARY]

- **Request.** Per-token argmax expert selection (`expert index`).
- **Admission.** `expert capacity = (tokens per batch / number of experts) × capacity
  factor` (Eq. 3). "If too many tokens are routed to an expert (referred to later
  as dropped tokens), computation is skipped and the token representation is passed
  directly to the next layer through the residual connection." Typical drop rate
  reported as < 1%.
- **Drop.** Tokens beyond capacity: computation skipped, residual passthrough.
- **Which count feeds the balancing signal? `R`, not `A`.** The aux loss is
  `loss = α·N·Σ_i f_i·P_i` (Eq. 4), "where `f_i` is the fraction of tokens
  dispatched to expert i", `f_i = (1/T)·Σ_x 1{argmax p(x) = i}` (Eq. 5) — the
  indicator is on the router's argmax decision, i.e. the pre-drop assignment.
  The paper's own Mesh-TensorFlow router pseudocode (Fig. 15) computes
  `aux loss = load balance loss(router probs, expert mask)` on the expert mask
  *before* the capacity-enforcement line `expert mask *= mtf.less(position in
  expert, expert capacity)`. The mask that continues to dispatch is the
  post-capacity one; the loss sees the pre-capacity one. [SYNTHESIS] The word
  "dispatched" in the `f_i` definition therefore means "router-assigned", not
  "post-capacity-admitted".

### 1.3 DeepSeek-V3 training (auxiliary-loss-free) [VERIFIED-PRIMARY]

- **Request.** Top-`K_r` selection on bias-adjusted affinities `s_{i,t} + b_i` (Eq. 16).
- **Admission / drop.** None: "DeepSeek-V3 does not drop any tokens during
  training." Hence `R_e = A_e` identically and the pre/post distinction is vacuous.
- **Balancing signal.** Per-expert bias `b_i`: "During training, we keep monitoring
  the expert load on the whole batch of each training step", then "we will decrease
  the bias term by γ if its corresponding expert is overloaded, and increase it by
  γ if its corresponding expert is underloaded". **Ambiguity flagged:** the paper
  does not define "expert load" more precisely than "actual expert load" versus
  "theoretically balanced expert load" (ablation section); whether the implementation
  counts routed tokens per expert per batch is not stated in the text. Because
  nothing is dropped, any token-count-based load equals both `R` and `A`.
  The complementary sequence-wise loss uses `f_i` on top-K assignments (Eq. 18),
  again pre-drop = post-drop.

### 1.4 DeepSeek-V3 inference (redundant experts) [VERIFIED-PRIMARY]

- **Drop.** None: the paper states specific deployment strategies keep inference load
  balanced, "so DeepSeek-V3 also does not drop tokens during inference"
  (paraphrase). `R_e = A_e`; distinction vacuous.
- **Balancing signal.** "The high-load experts are detected based on statistics
  collected during the online deployment and are adjusted periodically" (e.g. every
  10 minutes); experts are then rearranged/duplicated across GPUs. The controller
  observes served expert loads — which equal requested loads since nothing drops.

### 1.5 Tutel (dynamic capacity) [VERIFIED-PRIMARY]

- With `capacity_setting = 0`, "TUTEL automatically adapts the capacity factor to the
  minimum value that does not drop any tokens at each iteration." Computing that
  minimum requires the maximum per-expert *request* count — i.e. Tutel's control
  loop observes global pre-drop `R` (at least its per-expert max). This is a
  deployed system whose balancing controller provably consumes `R`, not `A`.

### 1.6 MegaBlocks dropless MoE (dMoE) [VERIFIED-PRIMARY]

- The paper contrasts the "prevalent, token dropping formulation" ("If the number of
  tokens assigned to an expert exceeds its capacity, extra tokens are dropped")
  with its own block-sparse formulation: "We use this formulation to train
  dropless-MoEs (dMoEs)." No drops ⇒ `R_e = A_e`; the distinction is vacuous.
- [SECONDARY] The same dropless lineage (permute → grouped GEMM → un-permute, no
  capacity truncation) is what vLLM/SGLang fused-MoE inference kernels implement;
  no token dropping occurs in those serving paths.

## 2. Where `R` is computed, and who can observe global `R` vs global `A`

### 2.1 Switch-style SPMD training

Per device (core), the router computes logits → top-1 → one-hot expert mask on its
local token shard: local `R^d` is available on every device *before any collective*.
The aux loss then does `density_1 = reduce_mean(expert mask, dim=tokens per core)`
→ shape `[num cores, num experts]`, and the final `reduce_mean` over cores ×
experts — a cross-device reduction of **pre-drop** selection counts
[VERIFIED-PRIMARY, Fig. 14 pseudocode]. So:

- **Global `R`** is observed by the training framework (it is literally an input to
  the scalar loss). Any controller colocated with the training loop that reads the
  same per-device counters observes global `R`.
- **Global `A`** (post-capacity admissions summed over devices) is *not* aggregated
  anywhere in the published loop [SYNTHESIS from the pseudocode: the post-capacity
  mask feeds dispatch/combine tensors; no reduction of post-capacity counts is
  shown]. Ironically, in Switch it is global `A`, not global `R`, that goes
  unobserved.

### 2.2 GShard-style training

Gating and the `c_e` counters are per token-group (groups processed in parallel
across devices); the per-group aux loss terms sum into the total loss, so global
`R` is aggregated by the existing loss machinery [VERIFIED-PRIMARY]. Global `A`
would require a separate reduction of post-capacity counts that the paper does not
describe [SYNTHESIS].

### 2.3 Expert-parallel all-to-all dispatch (Tutel/DeepSpeed-style)

[VERIFIED-PRIMARY, Tutel] "it runs a gating function … that determines the
destination GPU of each input token in the following all-to-all collective
communication (All-to-All). After the All-to-All (called dispatch), each GPU runs
their own expert". Consequences:

- **After dispatch, each expert's device observes exactly what it received**: its
  local share of global `A` (post-capacity admissions, if drops were applied before
  dispatch) — or, in dropless systems, its share of `R` (with `R = A`).
- **Both global `R` and global `A` are per-device-local quantities.** Making
  either of them global requires one cross-device collective: an all-reduce (or
  reduce) of an `E`-element integer vector per MoE layer per step —
  `8·E` bytes (≈ 2 KB for `E = 256`) [SYNTHESIS]. Against the dispatch all-to-all
  itself (`T·K·d` activation elements, routinely hundreds of MB), this is ~5
  orders of magnitude smaller: pure noise.
- **Is any existing system doing that? Yes.** Switch/GShard aggregate global
  pre-drop counts through the aux-loss reduction (no *extra* collective beyond the
  loss scalar the optimizer already needs); DeepSeek-V3's bias update monitors
  "expert load on the whole batch"; Tutel's dynamic-capacity mode needs the global
  pre-drop max. No verified system was found whose balancing controller is
  restricted to `A`.

## 3. Verdict per architecture class

| Architecture class | Drops? | Balancing signal observes | Global `R` observable? | Admitted-only holds? |
|---|---|---|---|---|
| Training, hard capacity + dropping (GShard/Switch-style) | Yes | **Pre-drop** selections (`c_e`, `f_i`) | **Yes** — aggregated by existing aux-loss reduction | **No** |
| Training, dropless (MegaBlocks dMoE; Tutel `capacity_setting=0`) | No | n/a (`R = A`) | Vacuous | **No** (distinction vacuous) |
| Training, aux-loss-free, no dropping (DeepSeek-V3) | No | Whole-batch expert load; `R = A` | Vacuous | **No** (distinction vacuous) |
| Inference/serving, dropless (DeepSeek-V3; vLLM/SGLang fused MoE) | No | Online deployment load statistics; `R = A` | Vacuous | **No** (distinction vacuous) |
| Hypothetical: capacity + drops, controller sensor downstream of drop point with no router-counter access and no added collective | Yes | `A` only | No (by stipulation) | **Yes — the only class where it holds** |

## 4. The system model under which censored-observation (admitted-only) analysis is load-bearing

Admitted-only observation is load-bearing **iff all three** hold [SYNTHESIS]:

1. The system enforces hard per-expert capacity **with** token dropping (`R ≠ A`
   on saturated steps — the GShard/Switch regime, not the DeepSeek-V3/MegaBlocks
   regime);
2. the controller's sensor sits **downstream of the drop point** (e.g. it reads
   per-expert executed-token counters from serving telemetry, post-hoc execution
   logs, or a monitoring endpoint) **and** has no access to the router's
   pre-drop selection counters; and
3. no cross-device collective is added to recover global `R` (the ~2 KB
   all-reduce is declined for engineering, not physical, reasons).

That is a **telemetry/instrumentation restriction**, not an architectural
necessity: the router necessarily computes the top-K selection on every device
before dispatch, so `R^d` exists locally everywhere; globalizing it costs one
negligible all-reduce, and the flagship training systems already perform that
aggregation inside their balancing machinery. [NOT FOUND] No primary source was
located showing a real, deployed MoE system's balancing controller actually
operating under conditions (1)–(3).

## 5. What changes in our problem statement

1. **The premise "R is unobservable in capacity-limited MoE" is false and must be
   retracted.** In GShard and Switch the system's own balancing feedback observes
   pre-drop `R`; in DeepSeek-V3, MegaBlocks, Tutel-dropless, and dropless serving,
   nothing is dropped so `R = A`. Stated plainly as the task requires: `R` is
   observable in most real systems we checked.
2. **The honest framing becomes a design question, not an observability claim:**
   "which signal — requested load `R` or admitted load `A` — yields better
   closed-loop control under saturation?" Our controller comparison (requested- vs
   admitted-feedback) is then an ablation over *sensor choice*, where admitted
   feedback is the degraded/weakened sensor and requested feedback is the
   full-information baseline.
3. **The censored-observation analysis is retained, re-scoped.** The leak-freeze,
   divergence, and `t_flip` results still characterize the *information content*
   of `A` vs `R`. They are load-bearing (a) as a robustness analysis — how much
   control performance is lost if a deployment is forced onto `A` (telemetry-
   restricted serving, log-only post-hoc settings); and (b) as the exact
   characterization of what the weakened sensor can and cannot see. They are not
   load-bearing as a claim about what real routers can measure.
4. **Must-never-claim additions for the paper:** never claim "real routers cannot
   observe requested load"; never claim "admitted-only feedback is a necessary
   property of capacity-limited MoE"; never imply the GShard/Switch aux losses
   observe post-drop admissions (both observe pre-drop selections — verified
   above). Any sentence of the form "in practice only `A` is available" must name
   the concrete telemetry restriction (Section 4, conditions 1–3) or be cut.

## 6. What could not be verified / open questions

- **[NOT FOUND]** A production inference system with hard capacity dropping whose
  balancing controller is restricted to `A`-only observation. Searched; the
  systems found either do not drop (DeepSeek-V3 inference, vLLM/SGLang fused MoE
  [SECONDARY]) or expose pre-drop counts.
- **[NOT FOUND]** SGLang's EPLB (expert-parallel load balancer): confirmed to
  exist as a serving-time rebalancer [SECONDARY], but which quantity it observes
  (requested vs served loads) was not verified from a primary source.
- **[NOT FOUND]** DeepSpeed-MoE's aux-loss counter definition (pre- vs post-drop)
  from DeepSpeed's own source; not read as primary. (Not required for the
  verdict: GShard/Switch primaries already settle the training question.)
- **Ambiguity on record:** DeepSeek-V3 never defines "expert load" precisely
  (Section 1.3); the vacuous-`R=A` conclusion does not depend on the definition.
- **Scope note:** Switch's published router pseudocode is explicitly the
  non-model-parallel version; cross-device capacity enforcement at full
  expert-parallel scale is not detailed in the paper, so the global-`A`
  non-observation claim (Section 2.1) rests on the published loop only.

## Sources

- GShard: Lepikhin et al., arXiv:2006.16668 — gating/capacity (Sec. 2),
  Algorithm 1 (group-level top-2 gating with auxiliary loss).
- Switch Transformer: Fedus, Zoph & Shazeer, arXiv:2101.03961 — expert capacity
  & dropped tokens (Sec. 2.2, Eq. 3), aux loss (Eqs. 4–6), router pseudocode
  (Figs. 14–15, Appendix F).
- DeepSeek-V3: DeepSeek-AI et al., arXiv:2412.19437 — aux-loss-free bias update
  (Sec. 2.1.2, Eqs. 16–20), "No Token-Dropping", inference deployment strategy
  with redundant experts (Sec. 4.2).
- Tutel: Hwang et al., arXiv:2206.03382 — all-to-all dispatch/combine (Sec. 2),
  dynamic capacity factor (Sec. 4.1).
- MegaBlocks: Gale et al., arXiv:2211.15841 — token-dropping formulation vs
  dropless dMoE (Fig. 1, Sec. 1).
- PDFs read 2026-10-16: `/tmp/papers/{gshard,switch,dsv3,tutel,megablocks}.txt`
  (pdftotext of the arXiv PDFs above).

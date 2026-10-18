# Literature boundary for the Top-K swapped-saturation result

**Search status:** targeted primary-source check on 2026-10-17, not a
systematic survey or novelty clearance.

## What the checked sources establish

### Censored data and value of information

Kumar and Mouchtaki's *What is the Value of Censored Data? An Exact Analysis
for the Data-driven Newsvendor* studies offline censored sales, computes
worst-case regret over demand distributions consistent with the censoring,
and analyzes how targeted exploration at high inventory levels changes the
guarantee. This is the closest checked mathematical neighbor to the general
shape of the present result: a latent state is obscured by capacity censoring,
and a more informative observation can improve a subsequent decision.

The present theorem is an exact Gumbel-Top-K construction with an
action-dependent overflow objective and a clipped vector signal. That
application difference alone does not prove a new decision-theoretic
principle. The proof's use of two hypotheses, a coupling of censored signals,
and the value of a more informative signal must be compared directly with
censored-data and active-testing results before novelty is asserted.

Primary source: Kumar and Mouchtaki, arXiv:2602.16842,
<https://arxiv.org/abs/2602.16842>.

### Capacity-drop semantics in MoE systems

DeepSeek-V2 describes device-level dropping of low-affinity routes, but its
expert-balance term counts tokens that select each expert (Eq. 24), and its
device/communication balance terms are likewise defined from router
selections (Eqs. 27 and 30). The paper presents token dropping separately.
It therefore supports the existence of a score-ranked admission mechanism;
it does not establish that V2 controls from post-drop admitted counts.

In NVIDIA Megatron-Core at pinned commit `36731ac`, per-expert
`moe_token_drop_policy=probs` keeps the capacity-limited routes for each
expert before the routing map is accumulated for the expert-bias update.
Ranking determines which tokens survive, but the resulting count remains
`A_e=min(R_e,C_e)`. The canonical count model is therefore a reasonable
count-level abstraction for that pinned configuration. Its existing
global-batch count reduction also means requested feedback might replace the
reduced vector rather than require an additional collective; a marginal
price must be measured in the actual implementation.

Primary sources: DeepSeek-V2, arXiv:2405.04434,
<https://arxiv.org/abs/2405.04434>; NVIDIA source pinned to
`36731acc3f0dac859ee7369bdc3a6af58bac546c`,
<https://github.com/NVIDIA/Megatron-LM/tree/36731acc3f0dac859ee7369bdc3a6af58bac546c>.
The local source-level analysis and exact call order are documented in
[`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md).

### Observation scope and hardware cost

*Demons in the Detail* studies micro-batch versus global-batch load-balancing
statistics and adds cross-micro-batch synchronization. It makes aggregation
scope a real systems variable, but it does not compare requested to
post-capacity admitted counts.

METRO gathers global top-K routing knowledge as part of its serving
algorithm and reports low overhead relative to conventional all-to-all.
TEMPO (arXiv:2608.13057) reports fusing dispatch with count collection into
one in-graph kernel and eliminating additional critical-path kernels and
collectives in its evaluated configuration. These papers do not answer the
present value theorem, but they rule out assigning a generic fixed price to
requested telemetry without measuring a concrete path.

Primary sources: Qiu et al., arXiv:2501.11873,
<https://arxiv.org/abs/2501.11873>; Yu et al., METRO,
arXiv:2512.09277, <https://arxiv.org/abs/2512.09277>; Li et al., TEMPO,
arXiv:2608.13057, <https://arxiv.org/abs/2608.13057>.

## Implications for claim wording

The evidence supports these statements:

1. The mathematical result is about the exact per-expert clipping map
   `A=min(R,C)` and a specified two-world Gumbel-Top-K family.
2. Score-ranked retention within a per-expert capacity changes admitted
   token identities but not the admitted count vector.
3. Device-level score-ranked dropping is a different, coupled admission
   model and must not be substituted for the canonical per-expert model
   without changing the theorem.
4. The theorem proves an optimal one-step signal-value gap in its family;
   it does not establish a multi-round control limitation, a production
   telemetry restriction, a measured hardware break-even, or novelty over
   generic censored-data/active-testing theory.

The next novelty gate is a theorem-level reduction comparison against a
benchmark defined independently of this MoE family. If the result transfers
unchanged, retain it as an exact MoE application and do not label it a new
general control principle. Any observation-cost claim also requires a
measured replacement-versus-addition comparison on a specified runtime.

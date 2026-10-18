# Reconciliation of professor report 1 and controlled experiment

**Status:** source audit, mathematical correction, and controlled synthetic
follow-ups; no trained-model result is reported here. The only real-system
evidence is a source-level Megatron code-path audit, not a run.
**Purpose:** test the professor report's score-truncation / windup mechanism
against the existing canonical count model, while preserving the current
Phase-1 theorem boundary.

## Decision question

The current project studies requested expert counts `R`, admitted expert
counts `A`, and pressure feedback under hard capacity. Professor report 1
proposes that score-ranked dropping can create a stronger feedback pathology
than count clipping and suggests a real-model study. Before training or
changing the paper claim, test the precise mathematical point on which that
proposal depends:

> Does changing *which routes* are dropped change the expert-count feedback
> signal under per-expert capacity, and if not, does a distinct group/device
> capacity rule create the proposed effect?

This experiment combines the existing MoE model with the report's suggestion.
It is not a replacement theory program, a claim about any named production
system, or evidence of model-quality improvement.

## Exact result for the existing count model

Let `S_e` be the multiset of routes requested to expert `e`, with
`|S_e| = R_e`. Suppose expert `e` admits exactly the highest-ranked
`min(R_e, C_e)` routes under any fixed score or order rule. Then

\[
 A_e = |\mathrm{admit}(S_e)| = \min(R_e,C_e).
\]

The choice of admitted token identities can depend on scores; the admitted
**count** cannot. Thus score-ranked and position-ranked dropping with the
same per-expert capacity produce the same `A` vector for a fixed request
matrix. This is precisely the count abstraction implemented by
[`CanonicalCapacityPolicy`](../../src/moe_control/capacity/per_expert.py).

Under global saturation and uniform capacities, `A_e=C` for every expert.
The existing sign-bias controller compares each `A_e` to their mean, so every
feedback coordinate is zero. Its bias does not wind up in that regime; it
freezes. This follows from the implemented
[`BiasIntegralFeedback`](../../src/moe_control/controllers/base.py) and the
formal saturation-freeze theorem in
[`formal.md`](../../docs/formal_definitions/formal.md).

The professor report's score-biased explanation therefore does not explain
the existing simulator's global-saturation/uniform-capacity result. A
different admission granularity is required for score ordering to alter
per-expert admitted counts.

### Exact separation between per-expert and device-level admission

The count invariance above is a theorem, not an assumption about a particular
drop order. For each expert (e), let (S_e) be its requested routes and let
(D_e\subseteq S_e) be the routes admitted by a per-expert policy. If the
policy fills every available slot whenever a request exists, then

\[
|D_e|=\min(|S_e|,C_e)=\min(R_e,C_e).
\]

The route scores can change *which* elements of (D_e) are retained, but
cannot change this cardinality. Consequently, rank-based dropping within
independent expert capacities does not create a new admitted-count feedback
map. A model that admits fewer than this number needs an additional explicit
constraint or rejection rule.

A shared device budget does produce a different count map. Minimal example:
two experts share one device with budget (B=1); two Top-1 tokens request
different experts, so (R=(1,1)). If their requested-route scores are
respectively (2) for expert 1 and (1) for expert 2, global score-ranked
admission gives (A=(1,0)). If the two scores are (1) and (2), while
keeping each token's selected expert unchanged, admission gives (A=(0,1)).
The request-count vector is identical but the admitted-count vector changes.
This is the minimum kind of coupling required for the report's score-ranked
count claim.

The source literature supports these as distinct mechanisms, not one shared
mechanism. DeepSeek-V2 describes a **device-level** computational budget and
dropping the lowest-affinity routes on each device; it also protects routes
from approximately 10% of training sequences. The paper separately defines
its expert-balancing signal from token expert selections, so it does not
establish an admitted-count controller. In Megatron-Core at pinned commit
[`36731ac`](https://github.com/NVIDIA/Megatron-LM/tree/36731acc3f0dac859ee7369bdc3a6af58bac546c),
[`apply_router_token_dropping`](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/moe_utils.py#L1065-L1128)
computes a capacity and applies `topk(...,
dim=0)` to each expert column of the routing-probability matrix for the
`probs` policy; the `position` policy also masks per expert. The resulting
admitted count is therefore `min(R_e,C_e)` for each expert (when padding is
not counted as real assignments). Critically, the pinned
[`TopKRouter.routing`](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/router.py#L1100-L1215)
calls the capacity drop before `_apply_expert_bias`; that method accumulates
the resulting routing map into `local_tokens_per_expert`. At global-batch
finalization,
[`get_updated_expert_bias`](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/moe_utils.py#L1245-L1281)
all-reduces those counts and applies the sign of the deviation from the
expert-count mean. Therefore, when the capacity-factor and expert-bias
options are enabled together, this pinned Megatron path **does implement the
formal model's admitted-count sign controller with per-expert clipping**.
This is the real-system configuration to study for the existing formal line;
it is not the V2 device-level mechanism. The count identity still holds:
`probs` ranking changes admitted token identities, not `A_e`.

DeepSeek-V2's device-level drop plus an admitted-count sign controller would
remain a constructed hybrid, because V2's balancing losses use router
selection statistics. The professor report has, however, identified a
genuine real-system setting in Megatron for the existing per-expert model.
The distinction matters: do not use V2's device-drop semantics to explain
Megatron's per-expert admitted counts, and do not say that no maintained
stack combines capacity dropping with bias feedback.

This distinction also limits the current synthetic pilot: its grouped-capacity
arm tests the necessary shared-budget mechanism, but it does not implement
DeepSeek-V2's device-limited Top-K, protected-sequence rule, or its training
controller. It establishes behavior only for the declared group-capacity
abstraction.

### What the proposed integrated theorem would still have to prove

The report's proposed primary claim combines four logically separate claims:

1. the chosen real-system admission rule makes (A) lose information about
   the requested-load error;
2. that loss is caused by a Top-K-specific endogenous score/admission
   geometry, rather than by generic finite-alphabet partial feedback;
3. every controller in a precisely stated class using only (A) has a
   quantitative performance or controllability limitation, while an
   (R)-observer avoids it;
4. the value difference exceeds an explicitly measured marginal cost for
   collecting (R).

There is an exact finite-sample distinction the theorem must preserve. If
tokens are iid at a fixed pressure and expert `e` is requested with
probability `pi_e(q)`, then its marginal request count is
`R_e ~ Binomial(T,pi_e(q))`. For any positive capacity `C_e>=1`,
`P(A_e=0)=P(R_e=0)=(1-pi_e(q))^T`; hence the exact law of `A_e=min(R_e,C_e)`
still identifies `pi_e(q)` at every finite `T`. Also,
\[
\frac{d}{d\pi}\,\mathbb E[\min\{\mathrm{Binomial}(T,\pi),C_e\}]
=T\Pr\{\mathrm{Binomial}(T-1,\pi)<C_e\}.
\]
The admitted-load sensitivity is therefore the requested-load sensitivity
times the exact attenuation factor
`Pr{Binomial(T-1,pi_e(q))<C_e}`. When `pi_e(q)` exceeds `C_e/(T-1)` by a
fixed positive margin, this factor decays exponentially in `T` by a
Chernoff/Hoeffding bound. This proves asymptotic sensitivity loss in that
stochastic model, not exact finite-`T` non-injectivity. Exact
non-injectivity can hold for deterministic fibers or a limiting experiment,
but the report must define which one; it cannot assert that
`theta -> law(A)` is non-injective for finite iid binomial counts without
additional assumptions. The clipping attenuation formula is generic. The
Top-K-specific part still has to come from a proved property of
`q -> pi(q)` or its Jacobian, and the result must survive the benchmark
reduction.

The current formal saturation-freeze theorem proves a narrower exact fact:
with **uniform per-expert capacities**, **global saturation**, the specified
admitted-count sign feedback, and gauge-quotient dynamics, admitted feedback
has zero relative update. It proves a freeze, not a diverging-bias windup
theorem. The E-world results prove family-specific information/overflow
inequalities and probe-versus-wait values, but the current class-level audit
shows those fixed experiments are represented exactly by the existing
metric-constrained polyhedral testing benchmark. Neither result proves items
2–4 above.

Replacing per-expert admission with the report's device-level score rule
does not, by itself, defeat the fixed-instance reduction principle. For a
finite static batch, each router decision compares finitely many affine
pressured scores; each device drop decision compares finitely many route
scores (raw-affinity scores are constant in pressure, and pressured scores
are affine if that is the chosen rule). With a fixed tie rule, these
comparisons induce a finite polyhedral partition on which the complete
requested/admitted/overflow output is constant. The current B1 definition is
specifically clipping-based, so it does **not** directly contain a coupled
device-cap admission map. Its general outcome-map extension, B1-out, is
defined and reduced in
[`phase1_benchmark_gate_2026-10-16.md`](phase1_benchmark_gate_2026-10-16.md).
That extension exactly encodes each fixed instance. A possible contribution
would still need a quantitative *family-level* statement about the
restricted Top-K/device-drop class that does not transfer unchanged to the
independently defined benchmark. This is the same novelty obligation already
identified in the Phase-1 reduction audit, now applied to the professor's
admission mechanism.

The DeepSeek-V2 paper does provide a relevant *admission mechanism*: each
token is restricted to experts on at most (M) selected devices, and each
device then drops low-affinity routes to meet its computational budget. It
does **not** provide the proposed admitted-feedback controller: its balancing
losses use expert-selection and device-selection quantities defined from
router selections. Thus coupling that device drop rule to the paper's
admitted-count sign controller remains an explicit hybrid intervention.
That is a legitimate controlled model to analyze, but it must be called a
hybrid and cannot inherit V2's training results as evidence for the feedback
premise.

Nor can the observation price be set to “one extra (E)-vector collective”
by definition. In the pinned Megatron bias path, an (E)-count vector is
already all-reduced to update the bias from post-drop counts. A requested-
count controller could potentially replace the locally accumulated
post-drop counts with pre-drop counts and reuse that same reduction; measuring
both signals simultaneously would require keeping/reducing both vectors.
Which implementation is compared changes the marginal cost. A costed
observation theorem must specify whether requested feedback **replaces** or
is **added to** the existing telemetry, then benchmark that exact path. The
report's Θ(…) value formula is currently a placeholder, not a theorem: its
function, comparator, controller class, observation protocol, and cost units
have not been fixed in the current formal documents.

**Pinned-source consequence, checked directly at commit
`36731acc3f0dac859ee7369bdc3a6af58bac546c`:** `TopKRouter.routing` calls
`apply_router_token_dropping` before `_apply_expert_bias`; in the ordinary
non-padded capacity path (`moe_pad_expert_input_to_capacity=False`), the
latter counts the post-drop routing map into a per-layer `int64[E]` buffer.
At global-batch
finalization, the per-layer vectors are stacked and passed to
`get_updated_expert_bias`, which performs one all-reduce over the existing
TP×CP×DP group. An R-only variant can count the pre-drop Top-K map into that
same buffer instead. Under an unchanged layer set, dtype, reduction group,
and update cadence, this replacement adds **zero all-reduce calls and zero
all-reduced count elements** by construction. This is a source-level
communication-count statement, not a measured latency statement: the local
counting kernel, memory traffic, overlap, and end-to-end step time still need
measurement. A simultaneous A-versus-R comparison may retain both vectors
and therefore has a different cost. Consequently, the break-even theorem
must charge the measured replacement overhead (which may be near zero), not
assume the price of an extra collective.

Accordingly, the rigorous state of the work is: the canonical per-expert
count model and its fixed-family theorems are proved within their stated
scopes, and a pinned Megatron path instantiates admitted-count bias feedback
under capacity dropping. DeepSeek-V2 supplies a distinct device-level
score-drop mechanism whose controller uses pre-drop selection statistics.
The report's stronger score-rank-induced *count* bias is false for independent
per-expert caps. A general admitted-feedback windup theorem, a class-level
Top-K separation, and a measurement-cost break-even remain unproved. The
paired synthetic pilot checks the per-expert identity and a separate
group-capacity abstraction; it is not a reproduction of either system and
does not close those theorem obligations.

## Controlled experiment

### Synthetic routing plant

Use a deterministic, seeded batch of token-expert scores. Add a pressure bias
to scores for selection only; select stable Top-K routes and retain each
selected route's score. Use identical batches and initial pressure for every
condition in a paired run.

Implement two admission policies:

1. **Per-expert capacity (existing model).** Each expert retains up to `C_e`
   of its requested routes. Run both score-ranked and position-ranked token
   selection. For a fixed request matrix, both must yield the same admitted
   count vector `A=min(R,C)` even though admitted token identities may differ.
2. **Group/device capacity (new synthetic policy).** Partition experts into
   fixed groups. Each group admits up to `B_g` of its requested routes,
   retaining the highest-affinity routes within that group. Report admitted
   counts per expert, aggregate group overflow, and the exact tie rule. This
   is a score-ranked group-capacity abstraction motivated by DeepSeek-V2's
   device-level dropping; it is **not** a faithful DeepSeek-V2 reproduction.

Keep the expert groups, capacities, token scores, Top-K, targets, and pressure
update fixed across paired conditions. Include a demand-shift condition only
after the stationary cases are characterized.

### Feedback conditions

For each admission policy compare:

- requested-count sign feedback `R`;
- admitted-count sign feedback `A`;
- no-feedback control;
- oracle feedback computed from the true requested counts, reported only as
  an upper-bound diagnostic.

The `A` controller is an intentional sensor ablation when the simulated
system exposes `R`. Do not describe it as the default behavior of a real
router without source evidence.

### Factorial controls

Evaluate these cases in order:

| Case | Admission | Capacity state | Required result |
|---|---|---|---|
| Negative control | None | `R=A` | Requested- and admitted-feedback trajectories match exactly |
| Count-model replication | Per-expert | All experts saturated, uniform `C` | `A=C`; sign-bias feedback is zero; no bias drift |
| Order-only intervention | Per-expert | Same `R`, scores, and `C`; vary only which excess routes survive | `A` is invariant; count-feedback trajectories match exactly |
| Partial saturation | Per-expert | Mix saturated and unsaturated experts | Quantify information loss only on saturated coordinates |
| Group-capacity mechanism | Group/device | Some groups saturated; score ranking varies within group | Determine whether `A` contains rank-dependent signal and whether the proposed feedback effect appears |
| Heterogeneous capacity | Both policies | Nonuniform capacities/group budgets | Separate demand feedback from capacity-induced feedback |

The first three cases are exact controls, not statistical hypotheses. Any
failure is an implementation or accounting error and must be resolved before
interpreting later cases.

### Outcomes and analysis

Primary mechanistic outcomes:

- per-expert and per-group request/admission vectors;
- fraction of route requests rejected and which token routes are rejected;
- bias/pressure norm and signed drift while capacity remains saturated;
- cumulative overflow and request-target mismatch, reported separately;
- time to leave saturation and time to recover after a demand shift.

Do not combine these into a weighted score. For each paired seed publish the
full trajectory and aggregate paired differences with uncertainty intervals.
The exact negative controls should be reported as exact equality checks.

Use a small exhaustive toy configuration first to enumerate all score-order
patterns and verify the admission invariants. Then run a larger seeded
synthetic sweep to estimate how often the group-capacity effect appears over
the declared score and capacity distributions. State the distribution,
generator, seed list, number of cases, and all exclusions before examining
the sweep. This is a controlled synthetic mechanism study; it does not
validate trained-model quality or prove production prevalence.

## Interpretation gates

1. **If per-expert score-ranked admission preserves `A=min(R,C)` and the
   uniform-saturation controller freezes**, retire the report's windup
   explanation for the existing model. Keep the current theorem unchanged.
2. **If group/device admission changes the result**, state the result only for
   that separately defined group-capacity model. Do not transfer it to the
   existing per-expert theorem or call it DeepSeek-V2 behavior without
   matching the paper's routing, protected-sequence, and loss details.
3. **A top-conference contribution is not established by this experiment.**
   It becomes a candidate contribution only if a theorem explains the
   observed effect for a parameterized Top-K family, survives comparison to
   an independently specified testing/control benchmark, and the effect
   matters under a measured real-system objective.

## Source and claim boundaries

- DeepSeek-V2 describes device-level dropping of lowest-affinity routes and
  three auxiliary balancing losses. Its expert-balance term defines load by
  the number of tokens selecting each expert, while the drop policy is
  described separately later in the report. Thus the paper does not support
  treating V2's balancing signal as admitted-only; it is not evidence that
  the V2 controller operates on the post-drop count vector:
  [technical report](https://arxiv.org/abs/2405.04434).
- DeepSeek-V3 states that it does not drop tokens during training or
  inference: [technical report](https://arxiv.org/abs/2412.19437).
- At Megatron-Core commit
  [`36731ac`](https://github.com/NVIDIA/Megatron-LM/tree/36731acc3f0dac859ee7369bdc3a6af58bac546c),
  the supported `moe_expert_capacity_factor` and expert-bias path can be
  enabled together. `TopKRouter.routing` applies token dropping before it
  calls `_apply_expert_bias`; the latter accumulates the post-drop map.
  Global-batch finalization all-reduces those counts and applies the sign
  update. Its count-level signal is therefore the canonical admitted vector
  `A=min(R,C)`, even though the `probs` rule changes which tokens are retained.
  See the pinned
  [router](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/router.py#L1100-L1215),
  [drop utility](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/moe_utils.py#L1065-L1128),
  [bias update](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/transformer/moe/moe_utils.py#L1245-L1281),
  and [global-batch finalizer](https://github.com/NVIDIA/Megatron-LM/blob/36731acc3f0dac859ee7369bdc3a6af58bac546c/megatron/core/distributed/finalize_model_grads.py#L377-L415).
- The pinned Megatron bias update already all-reduces one E-count vector.
  Replacing admitted counts with requested counts may reuse that collective;
  measuring both signals together may require an additional vector. A
  marginal communication-cost claim therefore requires an implementation
  comparison and measurement, not just the nominal size of an E-vector.
- Existing Phase-1 value-gap results remain exact results for their stated
  models. The current research decision record still says they do not
  establish a Top-K-specific advantage over the exact active-testing
  representation: [`conference_roadmap.md`](conference_roadmap.md).

## Exact corollary from the existing Top-1 family

The all-pressure pair-separation lemma also gives an exact identification-cost
bound. For any causal admitted-feedback policy with a uniform prior on `N`
worlds, telescoping the posterior support size yields expected cumulative
overflow at least `L(N-1)/2` if the policy must identify the world with
probability one. Under unrestricted movement, sequential singleton probes
attain this bound. The proof and its scope are recorded in
[`phase1_eworld_pair_separation_gate_2026-10-16.md`](phase1_eworld_pair_separation_gate_2026-10-16.md).

This is the cleanest exact family theorem currently available from the work.
It is an identification-constrained objective, not the original
unconstrained overflow-control objective, and it remains an adaptive-testing
result for a Top-1-realizable family. It does not resolve the current
benchmark-reduction objection or establish a top-conference novelty claim.

## Pilot execution and result

The standalone implementation is
[`run_admission_geometry_synthetic.py`](../../scripts/run_admission_geometry_synthetic.py).
It ran on CPU for 20 paired seeds, 120 steps per arm, with one fixed Top-2
ring-pair demand family. Its per-expert capacity 24 matches Megatron-Core's
capacity formula at capacity factor 0.75 for `T=128`, `K=2`, `E=8`; its
mean-centered sign update is gauge-equivalent to Megatron's global sign
update. This is a count-level mechanism match only: the script uses fixed
synthetic affinities and does not run Megatron, autograd, or token-specific
expert learning. It wrote
[`summary.json`](../../results/admission_geometry/summary.json) and
[`trajectories.csv`](../../results/admission_geometry/trajectories.csv).
I independently reran the paired CPU experiment on 2026-10-17. All four
exact-control checks passed again, and the regenerated summary SHA-256 was
`bea8cdb34284cfdb5acd198c6527b6070dc59e4689c589f272566754e6716f54`.
The three principal controls passed:

- per-expert score-ranked and position-ranked dropping produced identical
  request, admitted-count, feedback, and bias trajectories;
- in the per-expert fully saturated uniform-capacity arm, admitted feedback
  stayed zero and bias stayed zero for all 120 steps;
- in the dropless arm, requested and admitted feedback trajectories matched.
- the exact two-token shared-device example kept `R=(1,1)` fixed but changed
  `A` from `(1,0)` to `(0,1)` when only the route-score ordering changed.

The group-capacity result depended on the drop rule. At step 120, averaged
over the 20 constructed seeds:

| Group admission / feedback | Mean request deviation from uniform | Mean admitted deviation | Mean overflow | Mean bias L2 |
|---|---:|---:|---:|---:|
| position / requested | 30.9 | 30.1 | 32.00 | 4.659 |
| position / admitted | 29.6 | 27.4 | 32.00 | 5.326 |
| position / no update | 32.0 | 30.8 | 32.00 | 0 |
| score / requested | 30.9 | 30.7 | 32.00 | 4.659 |
| score / admitted | 57.3 | 40.5 | 34.25 | 4.813 |
| score / no update | 32.0 | 32.9 | 32.00 | 0 |

The standard errors are not a basis for population-level inference: the 20
seeds perturb route scores around the same hand-constructed ring family, and
the score-drop/admitted-feedback arm has high between-seed variation. The
pilot shows that a *group-capacity* rule can make admitted-count feedback
depend on which routes survive, and that its effect can reverse with the
drop rule in this construction. It does not establish general windup,
real-system frequency, or a Top-K advantage over the active-testing
benchmark.

The score-ranked group arm's final request deviation (57.3) exceeds the
requested-feedback arm (30.9), while the position-ranked admitted arm is
slightly better than its requested-feedback arm on the reported final
imbalance. That split is evidence against a rule-independent windup story,
not evidence for a universal controller ranking. The group mechanism remains
an explicitly synthetic abstraction, not DeepSeek-V2 or Megatron-Core.

## Status and continuation criterion

This pilot resolves one narrow but load-bearing question: score-ranked
selection within independent per-expert caps cannot alter expert admitted
counts; group-level capacity is a materially different observation model.
The subsequent four-capacity experiment is documented in
[`capacity_regime_sweep_results_2026-10-17.md`](capacity_regime_sweep_results_2026-10-17.md).
It uses the Megatron-style signed expert-bias controller, not the proportional
gauge-pressure `(A)` update in `formal.md`. Its post-run cumulative-overflow
diagnostic shows a regime-specific result: at `C=28`, admitted feedback
enters a globally saturated absorbing state in all 20 seeds and has lower
cumulative overflow than both requested feedback and no feedback; at `C=32`
and `C=36`, it has higher cumulative overflow than no feedback in all seeds.
The cumulative endpoint was computed from saved trajectories after the run,
so it is exploratory, not preregistered. The canonical pressure theorem
remains unchanged.

The source-pinned mapping is now completed for the audited Megatron-Core path:
its configured per-expert capacity drop followed by expert-bias accumulation
uses the post-drop count vector, so this is an actual implementation path for
the admitted-count signal under per-expert clipping. It is not the same
controller dynamics as the proportional gauge-pressure family in the formal
core. This does not make requested telemetry costly: the same E-count
all-reduce is already used by the bias update, so a replacement of admitted
counts by requested counts may reuse it.

Before any training run, there must be a theorem that predicts signal value
from the instance rather than presenting isolated examples. A concrete
two-sided result is now proved for the existing signed-bias/per-expert-clipping
model: admitted feedback strictly wins on the parameterized P2f Top-2 family,
while requested feedback strictly wins on a uniform-capacity `E=8,K=2` family
at `H=120` by 531 overflow assignments. The uniform witness has strict Top-2
margins, an open affinity neighborhood, and an exact-rational perturbation
audit. A separate heterogeneous `E=4,K=2` witness gives a smaller requested-
feedback advantage at `H=34`. See
[`bidirectional_bias_comparison_theorem_2026-10-17.md`](bidirectional_bias_comparison_theorem_2026-10-17.md)
and
[`bidirectional_bias_controlled_synthetic_experiment_2026-10-17.md`](bidirectional_bias_controlled_synthetic_experiment_2026-10-17.md).
This proves non-dominance, not the requested predictive condition or a
class-level separation from the outcome-cost testing benchmark. The next
proof must characterize sufficient conditions for the sign and size of the
overflow difference and survive that benchmark attack. Training still does
not follow from the fixed-plant sweep: it must measure an objective such as
validation loss, with the requested/admitted telemetry path and marginal
cost matched to the pinned implementation.

To connect the result back to the canonical proportional pressure law, the
same `E=8,K=2,T=128,C=32` fixture was audited with exact rational arithmetic
under `q^+=P_g(q+eta*gamma*(L/(KT)-mu))`, `delta=0`. At `eta=1`, requested
feedback gives overflow 1,874 versus 1,920 for admitted and no feedback; at
`eta=1/100,1/10,1/2`, all three arms give 1,920. An exact route-arrangement
calculation certifies the requested-better gap on
`(18944223025711/18945312500000,
38087479892954599/38085937500000000)`. A second exact Top-1 witness gives
admitted overflow 18 versus requested 23 on `E=3,K=1,T=3,C=(1,1,1)`,
`H=12`, for every `eta>3`; no feedback has overflow 12 there. Together these
form a two-sided non-dominance theorem for the canonical proportional
controller, recorded in
[`canonical_pressure_two_sided_comparison_2026-10-17.md`](canonical_pressure_two_sided_comparison_2026-10-17.md).
It remains a pair of constructive witnesses, not a predictive criterion for
new router instances or a Top-K advantage over the polyhedral testing
benchmark. This proportional-pressure result is separate from the signed-bias
theorem.

## Mathematical audit of the report's integrated C2 claim

The report's proposed claim is not a theorem statement that follows from the
current formal model. The checks below use the existing deterministic
finite-batch Top-K plant and the stated signed-bias update.

### 1. The proposed derivative needs a probability model

For a fixed finite affinity batch and deterministic tie rule, each request
vector `R(q)` is constant on every open cell of the finite score-tie
arrangement. Since `A(q)=min(R(q),C)`, the admitted vector is also constant
on each open cell. Consequently, for a deterministic scalar parameter
`theta` that changes scores continuously, `A_i(theta)` has derivative zero
where the routing cell is unchanged and is discontinuous/undefined at a
cell boundary. There is no nontrivial classical limit
`d E[A_i]/d theta -> 0` in this deterministic formalization: the expectation
and the law that defines it have not been specified.

A smoothed statement could be studied after defining, for example, a
probability distribution over token scores or router noise, the dependence
of that distribution on `theta`, the order of expectation and capacity
clipping, and the blocking/slack parameter. Those choices change the claim;
they are not implicit in the current definition. The exact deterministic
replacement already supported here is a fiber statement: when `R_e >= C_e`,
`A_e=C_e` does not distinguish different excess requests at that coordinate.
That is T4 in `formal.md`, not a derivative theorem.

### 2. Global saturation does not always mean windup

For the signed-bias update `b^+ = P_0(b + alpha*sign(mean(A)-A))`:

- with uniform capacities and global saturation, `A=C*1`, so the update is
  exactly zero and the bias freezes;
- with heterogeneous capacities and global saturation, `A=C` is constant
  but nonuniform, so the update is a constant capacity-determined vector
  until routing changes. This is demand-blind drift, not evidence that the
  controller has zero routing authority;
- after routing changes, the controller may leave saturation, so a claim of
  unbounded bias growth requires proof that the saturated state persists.

Thus “any admitted-count integral/sign controller exhibits windup under
saturation” conflates a uniform-capacity freeze with heterogeneous-capacity
phantom drift. The two regimes have different updates and different claims.

There is also a terminology issue. Classical integrator windup concerns an
integrator continuing to accumulate error while the actuator output is
saturated, often producing excessive stored controller state and delayed
recovery when the actuator leaves saturation (see the primary control-paper
discussion in ["Integrator Windup and How to Avoid It"](https://doi.org/10.23919/ACC.1989.4790464)).
Here the hard clip is in the *observed count*, not a bound on the bias
actuator. Under uniform capacities and global saturation, this specific
admitted-sign controller has zero update, so it freezes. Under heterogeneous
capacities it can apply constant demand-blind drift, but the finite-exit
theorem bounds a single saturated episode when its slope-gap condition holds.
Until an unbounded-state/recovery-delay criterion is stated and proved for
the MoE dynamics, use “saturation freeze” or “demand-blind drift”; “windup”
should be labeled an analogy, not presented as an established theorem.

### 3. Requested-count feedback is not guaranteed to avoid drift or loss

The requested signal removes the clipping ambiguity at the current batch,
but that does not establish bounded bias, convergence, or lower overflow for
every static Top-K batch. The exact comparison results already in
`formal_core.md` are conditional: P2c is a non-hitting boundary case, P2d is
a positive two-expert margin family, P2e characterizes the scalar dynamics,
and P2f is a finite-horizon Top-2 family where admitted feedback wins.
They do not support a universal ranking. A universal statement that the
requested controller “does not wind up” must therefore be removed unless a
controller class, target, tie rule, and boundedness criterion are added and
proved.

### 4. The requested-observation price is implementation-dependent

The pinned Megatron-Core path already reduces an expert-count vector for the
bias update. A requested-count variant may compute the vector before dropping
and reuse that collective instead of adding a second vector reduction.
Logging both signals simultaneously may cost more, but replacing one signal
with the other need not. The relevant cost comparison is therefore:

1. keep the existing admitted-count reduction;
2. replace it with pre-drop requested counts;
3. collect both vectors;

and measure each path under the same parallel layout. “One extra E-vector
collective per step” is not a valid default price. The source-pinned call
path and its limitations are documented above and in the linked NVIDIA
Megatron-Core source files.

### Decision for the paper and controlled experiment

Keep the paper's router, capacities, clipping map, and feedback comparison
as the object of study. Do not substitute the report's ambiguous
score-truncated count map: rank-based retention within each independent
expert cap leaves `A=min(R,C)` unchanged. The separate group/device pilot is
an explicitly different admission model and remains a mechanism control,
not the main paper model.

The strongest structural result now combines the exact necessary-and-
sufficient regular-facet criterion with a high-probability theorem for an
entirely iid affinity matrix under macro-heterogeneous exact-total
capacities. The proof selects the first row satisfying a near-tie condition,
handles the resulting conditioning on all other rows, and uses the pressure
gain `gamma` in the facet construction. A preregistered exact-grid audit
used 500 paired plants at each `T in {16,64,256,1024,4096}`. Candidate rates
were `.496,.734,.936,1,1`; every candidate was regular; mismatch rates
among regular facets were `.935,1,1,1,1`; mean counts for the exchanged
experts approached `T/2`; and the paired no-clipping control had zero
mismatches. This finite-grid audit supports the construction but does not
prove the limit or sample facets uniformly. The separate planted-facet exact
probability audit remains a different conditional experiment; its values
must not be conflated with the new unconditioned experiment.

This gives a concrete, proved structural result in the existing
per-expert-clipping line. It is not yet the requested top-conference
capstone: it does not establish a closed-loop performance gap, a priced
observation break-even, or a training-quality gain, and the finite outcome
map admits an exact polyhedral representation. No training claim should be
inferred from the facet experiment.

**Status of the report's named C3 asset.** Professor Report 1 defines C3 as a
root-arrangement signature bound and calls that an existing asset. The
near-tie result now proves a high-probability lower bound of
`b_{E,K}*sqrt(T)/2` on a proof-defined subset of distinct, regular,
capacity-mismatched facets. It still does not count all arrangement regions,
give a capacity-signature partition bound, or prove the report's specific
claimed signature result. A repository-wide search of the main, v3-review,
and exploration worktrees found the phrase only in the professor report
itself; it found no theorem, implementation, or artifact proving that
specific signature bound. Treat the claimed existing asset as unverified
until its signature is defined and its bound is located or proved. The
current many-facet theorem is a distinct proved result in the same canonical
model; see [`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md)
and the complete-candidate audit in
[`many_facet_random_affinity_results_2026-10-17.md`](many_facet_random_affinity_results_2026-10-17.md).

**Closer primary-source result located (2026-10-18).** The full score-tie
arrangement for a batch of `T` token-affinity vectors is exactly a union of
`T` translated copies of the type-A braid arrangement: its hyperplanes are
`q_e-q_f=(a_{t,e}-a_{t,f})/gamma`. With independent expert affinities
having densities, every nongenericity condition is a proper linear equality
in a jointly absolutely continuous translation vector, so the translations
are generic almost surely. Delcroix-Oger, Laplante-
Anfossi, Pilaud, and Stoeckl give the exact region count for this multiple-
braid arrangement in Theorem 2.21 of *Cellular Diagonals of Permutahedra*
([arXiv:2308.12119](https://arxiv.org/abs/2308.12119)):
`E! [z^E] exp(sum_{j>=1} FC(T,j) z^j/j)`, where
`FC(T,j)=binom(T*j,j)/((T-1)*j+1)`. Every per-token full ranking is constant
inside one such region; Top-K subsets, request counts, and clipped admitted
counts are successive coarsenings. Thus the known multiple-braid formula
already upper-bounds the number of request/admission signatures. For
`E=4,T=1,2,3,4`, the exact full-ranking region counts are `24,149,472,1089`,
whereas the existing forest-polynomial upper bound is `38,201,586,1289`.

This closes the generic *region-count* part of C3 against the literature; it
does not establish the professor report's specific capacity-signature bound,
which needs an exact definition and may count a coarser or different object.
More importantly, neither the known region count nor a stronger count by
itself yields a value-of-requested-signal theorem. To support C2, the proof
must connect the capacity-labeled coarsening to a quantitative overflow/value
bound that does not follow unchanged from the corresponding generic
costed-testing formulation. No such bridge is currently proved.

**Correction to the professor report's count-level wording.** Its claim
that score-ranked retention makes the *per-expert admitted count* differ
from `min(R_e,C_e)` is false when each expert independently admits up to
`C_e` of its own requests: the retained token identities can change, but the
count remains `min(R_e,C_e)`. Score order can affect downstream token-level
loss. Aggregate admitted counts change under score ranking only with a
coupled rule such as a shared device-level budget; that is a different
admission map and must be modeled separately. The Megatron per-expert path
and the distinct device-level case are documented above.

### Follow-up: does the local facet obstruction predict closed-loop cost?

To connect the structural theorem to the feedback-control question without
changing the model, the preregistered protocol
[`facet_to_trajectory_bridge_protocol_2026-10-17.md`](facet_to_trajectory_bridge_protocol_2026-10-17.md)
paired the same 40 `E=4,K=2,T=12` affinity plants and sampled-facet records
with 120-step exact-rational trajectories under the canonical proportional
pressure law. It compared requested, admitted, and no-update arms across
no-clipping, exact-total uniform, exact-total heterogeneous, and aggregate-
shortage capacities. This is distinct from the Megatron-style signed-bias
controller and from the grouped-capacity pilot above.

The no-clipping equality and all count/overflow identities passed. Under
uniform exact-total capacity, mean cumulative overflow was 201.8 for requested
feedback, 232.45 for admitted, and 321 for no update; admitted feedback had
higher overflow than requested on 25/40 plants, lower on 2, and tied on 13.
Under heterogeneous exact-total capacity, the corresponding means were
700.9, 874.3, and 816; admitted feedback had higher overflow than requested
on 38/40 plants and tied on 2. Under aggregate shortage, requested and
admitted cumulative costs tied exactly on all 40 plants. The sampled facet-
mismatch fraction had descriptive Spearman correlations of `-0.243` and
`-0.284` with `D = overflow_admitted - overflow_requested` in the two
exact-total profiles; in aggregate shortage that geometry fraction varied
while `D` was identically zero.

This closes one specific bridge attempt: the fraction of sampled mismatched
facets is not a useful stand-alone predictor of closed-loop overflow on this
design. It does not invalidate the exact facet theorem; it shows that a local
non-potentiality certificate does not by itself determine trajectory cost.
The experiment therefore does not license the report's broad windup or
universal signal-value claims. The reproducible results and full trajectories
are in
[`facet_to_trajectory_bridge_results_2026-10-17.md`](facet_to_trajectory_bridge_results_2026-10-17.md)
and `results/facet_trajectory_bridge/`.

### Follow-up: exact route split from rejected-load accumulation

The bridge experiment made it possible to state and check the exact
common-prefix recurrence in
[`rejected_load_route_divergence_identity_2026-10-17.md`](rejected_load_route_divergence_identity_2026-10-17.md):
while requested and admitted routes agree, their pairwise relative-pressure
separation is the discounted cumulative difference in rejected counts
`J=R-A`. The first route split occurs when that separation reaches a
selected/unselected Top-K score margin. Exact rational auditing checked every
expert-pair identity through each shared prefix for all 160 plant/capacity
pairs; every split had the required nonpositive-margin witness.

The first split occurred by state 119 in 28/40 uniform exact-total plants,
38/40 heterogeneous exact-total plants, and 34/40 aggregate-shortage plants;
none split without clipping. The post-hoc cost join is informative but not a
causal test: in uniform exact-total capacity the no-split plants all tied in
cost, while split plants had both signs of cost difference; in heterogeneous
exact-total capacity every split plant had lower requested-controller
overflow in this particular generator; in aggregate shortage all plants
tied in overflow even when routes split. The last case is a direct exact
warning: when all experts remain saturated, aggregate overflow is fixed at
`KT-sum(C)` regardless of where requests go.

This gives an exact necessary mechanism for route divergence, but not a
post-divergence cost theorem. A proof of the remaining performance claim must
track the visited Top-K cells together with the capacity-feasible allocation;
neither a sampled facet count nor a first-split time alone predicts the
overflow ranking. Full results and per-plant data are in
[`rejected_load_route_divergence_results_2026-10-17.md`](rejected_load_route_divergence_results_2026-10-17.md)
and `results/rejected_load_first_divergence/`.

The integrated C2 proposal still does not follow from the existing formal
definition. Its implementation premise also needs correction: the pinned
Megatron-Core route applies per-expert token dropping before its expert-bias
count accumulation, so its admitted count is `min(R_e,C_e)`, but the same
count reduction is already part of the bias update. Computing requested
counts before dropping may replace that vector rather than add another
all-reduce. The DeepSeek-V2 paper's device-level drop is a distinct coupled
admission mechanism and its balancing statistics are defined on selections;
the synthetic group-capacity arm must remain labelled an abstraction.

**Current scientific spine:** keep the established deterministic Top-K,
per-expert clipping, and pressure/bias comparisons together, while keeping
the two controller laws separate. The exact structural theorem is the
regular-facet criterion for when admitted feedback is or is not a convex
subgradient field. Its controlled facet experiment verifies the local
mechanism; the bridge experiment shows that sampled local non-potentiality
does not by itself predict overflow. The performance comparisons give
genuine two-sided non-dominance for particular parameterized families. The
new Corollary T6c below supplies an exact cost consequence for one
request-balanced, aggregate-shortage family. These results still do not
establish a value/complexity separation from the independent
polyhedral-outcome-map benchmark or a measured system benefit. The
top-conference claim is therefore not yet proved; the remaining gate is to
show a quantitative family property that survives the benchmark comparison,
or to measure a real-system objective that the formal result predicts.

### Exact cost corollary from the existing saturation-exit line

The canonical proportional model now has a parameterized all-horizon cost
corollary in
[`balanced_saturation_cost_theorem_2026-10-17.md`](balanced_saturation_cost_theorem_2026-10-17.md).
It fixes the original per-expert clipping rule, uniform target, and gauge
pressure update. If initial Top-K requests are balanced and every positive
capacity is at most that count, requested feedback and no feedback remain at
the aggregate-shortage overflow floor. If the Kth and (K+1)st capacities
have a strict gap, admitted feedback has a constant saturated direction and
must exit by an explicit score-arrangement bound; after exit its overflow is
strictly above the floor. The exact controlled audit spans 110 plants in 11
`(E,K)` cells and checks every state and no-clipping control; results are in
[`balanced_saturation_cost_experiment_results_2026-10-17.md`](balanced_saturation_cost_experiment_results_2026-10-17.md).

This is a proved cost consequence for a structured Top-K family, not the
professor report's score-rank mechanism, not a general value-of-information
claim, and not a separation from the polyhedral benchmark. The latter
remains a real gate for the paper's novelty claim.

## Exact costed-observation integration

The existing E-world family now has an exact one-time requested-observation
break-even theorem; this uses the same Top-1 construction and admitted
pair-separation work, rather than changing the admission model. For
`E_S=s`, `C_sink=C-s`, `C>=2s`, uniform prior, and unrestricted movement, the
exact admitted-feedback value over `h` post-initial rounds is
`s*min(h,N-1)`. A single requested vector at the initial pressure identifies
the world. Buying costs `s+kappa`; skipping costs
`s+s*min(h,N-1)`, so the optional buy/no-buy value is
`s+min(kappa,s*min(h,N-1))` and the break-even is
`kappa*=s*min(h,N-1)` overflow-equivalent units. The proof covers every
integer `N>=2`; an exact rational Bellman audit checked 171 `(N,s,C)` cells,
29,583 DP values, and 8,892 buy/no-buy comparisons. See
[`eworld_costed_observation_value_theorem_2026-10-17.md`](eworld_costed_observation_value_theorem_2026-10-17.md),
the [audit protocol](eworld_costed_observation_protocol_2026-10-17.md), and
[`results/eworld_costed_observation/summary.json`](../../results/eworld_costed_observation/summary.json).

This gives the professor's C2 suggestion a precise mathematical instance,
but it does not finish the top-conference claim. The paid measurement is
one-shot because the hidden world is static and identified by the first
request vector; `kappa` is not a measured collective/latency cost. Moreover,
the family reduces exactly to the same costed subset-testing Bellman problem,
so the theorem is an exact Top-1 application rather than a separation from
general adaptive testing. The outstanding paper-level requirement remains a
quantitative Top-K family result beyond that reduction, together with a
measured marginal telemetry cost if the systems claim depends on one.

### Full-arrangement check of the existing facet result

To test whether the planted-facet result depended on conditioning on one
selected facet, a separate exact audit enumerated every regular route-changing
segment of the complete pressure arrangement for 40 paired iid rational
`E=3,K=1,T=6` plants. Under canonical per-expert clipping, all 40 plants had
at least one mismatched facet. The pooled mismatch fractions were `43/60`
for uniform exact-total capacity and `3127/4320` for heterogeneous
exact-total capacity; the no-clipping control had zero mismatches. Every
mismatch had a nonzero exact tangential jump, and every matched facet had
zero tangential jump. The deterministic summary reproduced byte-for-byte.

This strengthens the *structural validation* of C3 by using the complete
finite arrangement rather than a planted or sampled subset of facets. It does
not create a closed-loop performance result: the controlled trajectory work
already shows that facet mismatch alone does not predict overflow ordering.
It also remains an instance-level result that the exact outcome-map benchmark
can encode. Protocol, results, and machine-readable output are in
[`full_arrangement_facet_audit_protocol_2026-10-17.md`](full_arrangement_facet_audit_protocol_2026-10-17.md),
[`full_arrangement_facet_audit_results_2026-10-17.md`](full_arrangement_facet_audit_results_2026-10-17.md),
and [`summary.json`](../../results/full_arrangement_facets/summary.json).

## Addendum: original-model cost theorem and controlled validation

Follow-up work remained inside the existing canonical definitions; it did
not replace them with the report's costed-observation proposal. The new
two-step theorem proves that, for an explicit parameterized iid Top-1 family
with one under-capacity expert and exact total capacity, the expected
normalized overflow gap between admitted and requested **proportional
pressure feedback** converges to
\[
d-d^3/3>0,\qquad d=\eta r<1.
\]
The result is independent of how the remaining capacity is split between
the other experts. It uses the original feedback equations and overflow
objective, and the proof accounts for reusing the same affinity matrix at
both steps. See
[`heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`](heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md).

Two preregistered paired exact-grid experiments tested the fixed example and
the capacity/gain family. They use the same static affinity matrix across
feedback arms, exact integer score comparisons, mass/clipping/overflow
invariants, and no-clipping negative controls. Their finite-size estimates
show positive paired gaps at every registered cell at the largest batch
size; small-batch/high-gain cells deviate materially from the asymptotic
formula and remain reported. Protocols, data, and outputs are linked from
[`heterogeneous_capacity_two_step_results_2026-10-17.md`](heterogeneous_capacity_two_step_results_2026-10-17.md)
and [`heterogeneous_capacity_family_results_2026-10-17.md`](heterogeneous_capacity_family_results_2026-10-17.md).

This is a concrete cost consequence within the existing MoE formal model,
not a result about the price of collecting requested counts. It does not
establish a gain against arbitrary causal controllers or evade the exact
outcome-map benchmark, so it does not close the conference-level novelty
gate or justify a trained-model claim. The useful professor-report guidance
applied here was to define one primary outcome, pair the arms on identical
inputs, preregister all tested cells, use negative controls, and keep
mechanism evidence separate from deployment claims.

## Addendum: fixed-`E` generalization and registered controlled run

The preceding E=3 asymptotic cost theorem now has a proved extension to every
fixed `E>=2` within the same canonical model. For `K=1`, uniform target,
zero leak, `q_0=0`, iid static `U[0,1]` affinities, and exact-total capacity
with expert 1 short by fraction `r`, the two-step normalized expected
admitted-minus-requested overflow tends to
`d-d^E/E`, where `d=eta*r<1`. The result is independent of the split of the
remaining capacity. The proof is in
[`top1_e_expert_two_step_overflow_theorem_2026-10-17.md`](top1_e_expert_two_step_overflow_theorem_2026-10-17.md)
and is summarized in section 11 of `formal_core.md`.

The protocol fixed `E={3,4,8,16}`, `d={1/4,1/2,3/4}`,
`T={3360,6720,13440}`, 100 paired plants per `(E,T)`, exact integer score
comparisons, the same matrix across both routing steps and all arms, and
no-clipping controls. The runner was executed twice; both outputs were
byte-identical. All 3,600 paired gaps were positive, all 3,600 no-clipping
checks and all routing/admission/overflow invariants passed, and no exact ties
occurred.

The finite-size check is not uniformly close to the limit: at `T=13440`,
the largest absolute mean error is `0.00305` for `E=4`, `0.06688` for `E=8`,
and `0.22666` for `E=16`. For `E=16`, the per-other-expert capacity slack
`1/480` is about the standard deviation of its empirical Top-1 fraction at
this batch size. Therefore the positive sign is supported by every registered
pair, but the magnitude convergence is not demonstrated at `E=8,16` by this
run. See the complete table, hashes, and caveat in
[`top1_e_expert_overflow_results_2026-10-17.md`](top1_e_expert_overflow_results_2026-10-17.md),
with raw rows in `results/top1_e_expert_overflow/`.

This is a continuation of the existing canonical per-expert-clipping line,
not the report's distinct device-level token-drop model and not its priced
telemetry theorem. It strengthens the proved family-level cost consequence;
it does not establish a trained-model gain or evade exact finite-instance
outcome-map simulation. The class-level conference novelty gate remains
unresolved.

## Addendum: arbitrary Top-K extension and controlled experiment

The two-step overflow theorem has now been extended from `K=1` to every
fixed `E>=2` and `1<=K<E`, without changing the formal model or the research
question. Under the same iid static uniform affinity law, exact-total
per-expert clipping, uniform target, zero leak, and canonical proportional
pressure update, its limit is `Phi_(E,K)(d)-K/E>0`, where `d=eta*r/K` and
`Phi` is the exact Top-K inclusion probability for the capacity-short
expert. The Top-1 formula `d-d^E/E` follows as `K=1`. The derivation and
conditions are in
[`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md).

The preregistered paired experiment covers every `K` at `E={3,4,8}` and
three displacements and batch sizes, with 50 paired plants per `(E,K,T)`.
It produced 5,400 rows, passed 5,400 no-clipping controls and all invariants,
and reproduced byte-identically on rerun. All 108 cell means are positive;
5,399/5,400 individual gaps are positive. The finite-size agreement is not
uniform: only 69/108 nominal 95% intervals across all batch sizes contain the
asymptotic value, and the largest-batch `E=8` edge-`K` cells still deviate
materially. Full tables, hashes, and raw outputs are recorded in
[`topk_e_expert_overflow_results_2026-10-17.md`](topk_e_expert_overflow_results_2026-10-17.md)
and `results/topk_e_expert_overflow/`.

This is a controlled synthetic experiment on the existing formal line, not
a new admission model or the report's hypothesized windup/price theorem. It
broadens the proved family consequence to general Top-K. The finite-instance
and finite-grid outcome maps still embed in the polyhedral testing benchmark,
so this result does not prove the desired class-level top-conference
separation. It is not evidence for trained-model quality, and it does not
justify starting training without a separate quality hypothesis and
preregistered primary metric.

## Addendum: primary-source literature check and exact paper claim boundary

This addendum checks the report's proposed value-of-information framing
against primary sources available on 2026-10-17. It does not change the
canonical routing model or replace any result above.

### What the literature check changes

The generic phrase “value of censored feedback in resource allocation” is
not an available novelty claim. Montanari et al. study online budget
allocation with censored rewards, prove a regret lower bound, and give
algorithms for known and changing budgets ([arXiv:2602.06565](https://arxiv.org/abs/2602.06565)).
Kumar and Mouchtaki give an exact finite-dimensional analysis of worst-case
regret under censored demand and show how targeted exploration can improve
guarantees ([arXiv:2602.16842, revised 2026-10-11](https://arxiv.org/abs/2602.16842)).
Hssaine and Sinclair characterize when censoring permits vanishing regret and
derive an irreducible information-loss bound otherwise
([arXiv:2412.01763](https://arxiv.org/abs/2412.01763)). Qin, Simchi-Levi, and
Zhu further distinguish learning a policy from valuing its cost in multistage
censored inventory control ([arXiv:2609.37380](https://arxiv.org/abs/2609.37380)).
These works do not analyze Top-K routing with gauge pressure or its exact
admitted-feedback dynamics, but they make a generic censoring/VoI framing
insufficient. A claim must name and prove the MoE-specific theorem beyond
that established structure.

Recent MoE work also changes how telemetry cost must be treated. Exact
Quantile Balancing computes global expert quantiles using two all-reduces of
256-bin counts per expert, while Load-Error Injection feeds local hard-load
errors into router-score gradients ([Neitemeier et al.,
arXiv:2609.28053](https://arxiv.org/abs/2609.28053)). The paper describes this
communication as independent of token count and reports training results at
7.5B model scale. Loss-Free Balancing already updates selection biases from
recent expert loads ([Wang et al., arXiv:2408.15664](https://arxiv.org/abs/2408.15664)).
Therefore, neither “bias-based load control” nor “global count collection
costs one extra E-vector collective” is a safe novelty or cost premise. The
marginal cost must be measured for a named implementation and specify whether
requested counts replace or supplement existing reductions.

Least-Loaded Expert Parallelism is another relevant boundary: it dynamically
reroutes overloaded experts and their parameters at the device/placement
level, with an empirical systems objective ([ICML 2026 paper](https://proceedings.mlr.press/v306/nguyen26m.html)).
It does not analyze the requested/admitted feedback field or the pressure
recurrence here. It is adjacent systems work, not evidence for the current
theorem.

### The exact theorem and experiment currently supported

The strongest single closed-loop result already present in this research line
is the all-horizon population theorem in
[`topk_long_run_admitted_overflow_theorem_2026-10-17.md`](topk_long_run_admitted_overflow_theorem_2026-10-17.md).
For fixed `E>=2`, `1<=K<E`, iid continuous affinities with a positive bounded
density, uniform target, exact-total per-expert capacities with one expert
short by fraction `r` and equal compensating slack on the others, and the
canonical proportional pressure update, it proves:

1. Requested feedback stays at the symmetric population pressure and incurs
   normalized overflow `r` per round.
2. Admitted feedback follows the explicit one-dimensional Top-K response
   recurrence
   `x[n+1]=x[n]+eta/[K(E-1)]*((E-1)r-(P_F(x[n])-K/E))`.
3. Under the stated step-size bound, the recurrence converges to the unique
   `x*` satisfying `P_F(x*)=K/E+(E-1)r`.
4. In the iterated limit `T -> infinity` first and then `H -> infinity`, the
   admitted-minus-requested cumulative overflow per round converges to
   `(E-1)r>0`.

This is a concrete Top-K/gauge closed-loop theorem with a quantitative
family-level consequence. It is not the report's universal statement about
all integral/sign controllers. It does not compare optimal policies, prove a
generic value-of-information theorem, or show that a real model's task
quality improves. The precise asymptotic order of limits is part of the
claim; do not call it a fixed-finite-batch infinite-horizon theorem.

### Critical distinction: this theorem is not an information-loss example

On the theorem's symmetric trajectory, write `p=K/E`. For every relative
pressure `q=(0,x,...,x)` with `x>=0`, the short expert's request fraction
satisfies `p_s(x)>=p`, while each rival's request fraction satisfies
`p_r(x)=(K-p_s(x))/(E-1)<=p`. The capacities are
`c_s=p-r` and `c_r=p+r/(E-1)`. Thus the short expert is saturated, but every
rival is strictly below capacity in the population model:

```text
A_s/T = c_s,
A_e/T = R_e/T = p_r(x) < c_r,  e=2,...,E.
```

Because `sum_e R_e=K*T`, the rival counts recover the saturated coordinate:
`R_s=K*T-sum_{e=2}^E A_e`. The map from the full requested vector to the
admitted vector is therefore injective on this trajectory. For fixed positive
slack `r+r/(E-1)`, the probability that any rival exceeds capacity also
vanishes exponentially in `T` under iid sampling. The excess-overflow
theorem consequently does **not** demonstrate an irreducible loss of
requested-load information, nor that requested telemetry is necessary.
It demonstrates a different mechanism: the specified controller feeds raw
admitted fractions into a uniform-target update instead of reconstructing
the request vector from the available admitted counts and conservation law.
The controller is miscalibrated for this heterogeneous-capacity objective;
the observation channel is sufficient on the theorem's population
trajectory.

This separates two candidate claims that must not be merged. The
one-short-capacity population theorem is an exact **controller-mismatch and
overflow** result. The separate two-saturated-expert theorem is the project's
actual **information-channel** result, but it has a two-world Top-1 model,
an explicit policy class, and a generic censored-testing reduction risk.
The professor report's proposed sequence “identifiability loss, therefore
any integral/sign controller loses authority” is not proved by the
one-short theorem.

The locked controlled experiment in
[`topk_long_run_admitted_overflow_protocol_2026-10-17.md`](topk_long_run_admitted_overflow_protocol_2026-10-17.md)
was rerun on 2026-10-17. It evaluates `E=4`, `K=1,2,3`, Normal/Logistic/Gumbel
affinities, `T=2304,9216`, 12 paired static affinity plants per law/K/T, and
`H=1,2,4,8,16,32,64`. The rerun reports 1,512 plant-horizon rows, 126 cells,
216 no-clipping controls, zero ties, all invariants passed, and positive cell
means in all 108 nonzero-horizon cells. The registered artifacts reproduced
their recorded hashes:

| Artifact | SHA-256 |
|---|---|
| Runner | `0d0543100ea7af988c12332a6491b97eae1caeb36dd36661c86bb21a30dbeb08` |
| Protocol | `4540e0d0c7023dc6dfa08cb11533e9f963a9dcc4a32c9e39ff26955b4f892b5b` |
| Plant rows | `eb4e0397e6bf4261cffd1ec79a11d901da2d3d498a69cd4ee331956d52e37971` |
| Summary | `7cc7cf167e5db038cfe0fc856adc0ded5e524627d68f7d6d4af2d49ddf4d0433` |

The experiment is a reproducibility check and finite-grid support for the
population recurrence. It does not expand the affinity laws, horizons, or
controller class beyond the preregistered grid, and it does not remove the
exact finite-outcome-map reduction.

The separately registered fresh-batch-versus-static study was also rerun.
Its 1,008 rows, 84 cells, 144 full-trajectory no-clipping controls, and all
invariants pass, with zero ties; the runner, protocol, and result hashes
match `results/topk_fresh_batch_closed_loop/summary.json`. Fresh batches
track the finite-`T` mean-feedback recurrence more closely on average than
static reuse (mean absolute cell error `0.0175` versus `0.0400`), while the
nominal intervals cover it in only 20/42 and 16/42 cells, respectively. The
fresh-batch cumulative gap is lower than the paired static gap in 35/42
registered `(K,T,H)` comparisons and remains positive on average. This
supports a stochastic fresh-batch mechanism effect in the registered grid;
it does not prove a fixed-`T` infinite-horizon result, a model-quality gain,
or a measured observation cost. The fresh-batch protocol and full results
remain separate at
[`topk_fresh_batch_closed_loop_protocol_2026-10-17.md`](topk_fresh_batch_closed_loop_protocol_2026-10-17.md)
and [`topk_fresh_batch_closed_loop_results_2026-10-17.md`](topk_fresh_batch_closed_loop_results_2026-10-17.md).

### Consequence for the report's proposed integrated C2 claim

The professor report's broad formula “value is `Theta(g(slack,E,K,skew))`
minus one E-vector collective per step” is not proved by the theorem above,
the costed two-world result, or this experiment. It has no established
function `g`, universally valid comparator, measured cost unit, or general
controller class in the current evidence. The exact two-world one-step
value theorem and the E-world probe theorem are legitimate additional
results, but each has its own finite family, decision class, cost convention,
and reduction boundary; they cannot be merged into a family-wide formula by
assertion.

Accordingly, the grounded research package is: (i) retain the closed-loop
Top-K population theorem and its controlled synthetic validation as the
primary formal/mechanistic result under its exact assumptions; (ii) use the
expected-Jacobian attenuation/curl and costed-observation theorems as separate
supporting results with their explicit scopes; and (iii) make no conference
novelty or real-training-benefit claim until the targeted comparison with
random-utility, censored-feedback, MoE balancing, and adaptive-testing theory
is completed at the theorem's exact boundary and the class-level benchmark
issue is addressed. This consolidates the existing research line; it does
not introduce a new model or propose an additional open-ended direction.


## New theorem and exact synthetic audit

The sensitivity calculation proposed in the professor report is now stated
for the unchanged canonical model in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md).
For iid tokens and `A_e=min(R_e,C_e)`, the derivative of the expected
admitted fraction is the requested Top-K probability derivative multiplied
coordinatewise by
`Pr[Binomial(T-1,p_e)<C_e]`. Above the capacity fraction this factor tends
to zero exponentially as batch size increases. At every finite `T` and
positive capacity, however, the law still identifies the request probability
through `Pr[A_e=0]=(1-p_e)^T`; the exact claim is weak mean sensitivity, not
finite-sample non-identifiability.

For `E=3,K=1`, iid standard Gumbel affinities, `T=6`, and uniform exact-total
capacities `C_e=2`, the expected admitted field has exact quotient curl
`-29/2187` at request probabilities `(1/2,1/3,1/6)`. The locked 72-cell
numerical audit matched analytic Jacobians to maximum error `2.38e-10`, with
all uniform-state and no-clipping controls passing. This is an expected-field
mechanism result, not a closed-loop cost or model-quality result. Its exact
protocol, outputs, and runner are linked from the theorem document.

The targeted source review also supports a boundary on the report's proposed
measurement price. ALF-LB primal-dual analysis already exists for the
uncensored assignment setting ([Han and Zhong](https://arxiv.org/abs/2512.03915));
METRO uses global Top-K information for a distinct serving-routing objective
([METRO](https://arxiv.org/abs/2512.09277)). Neither establishes a generic
marginal cost of one additional count collective. In the pinned Megatron path
discussed above, requested counts may replace counts already reduced for the
bias update, so the cost must come from a measured implementation comparison.
The new theorem does not claim this price or a top-conference novelty result.

## Addendum: two-saturated-expert information and finite-size control study

The report's identifiability suggestion has also been tested in a two-world
Top-1 Gumbel-Max family with two saturated experts, so conservation of total
Top-1 requests cannot reveal one hidden saturated coordinate from the others.
The exact theorem in
[`two_saturated_expert_information_and_control_theorem_2026-10-17.md`](two_saturated_expert_information_and_control_theorem_2026-10-17.md)
proves that the full admitted-vector laws become asymptotically
indistinguishable while request-vector laws become distinguishable, and gives
an exact asymptotic two-batch overflow comparison for the canonical
proportional pressure update. It also proves an optimal one-step
decision-value result over all gauge-fixed pressure actions: requested
feedback's Bayes-optimal overflow tends to zero, while admitted feedback's
tends to exactly `1/32` in normalized overflow units. This assumes a static
two-world prior, no movement constraint, and no cost for acquiring either
signal; `1/32` is not a measured system cost. Exact finite-law evaluation
also proves that the optimal requested-versus-admitted value gap is at least
`0.018498060` at `T=320` and `0.029782371` at `T=640`, in the same normalized
units.

The finite-size controller ordering crosses: exact enumeration of all
multinomial first-batch count vectors shows admitted feedback has lower
expected overflow at `T=40,80`; requested feedback wins in both worlds at
`T=320,640`; at `T=160` the worlds have opposite, very small differences.
This rules out describing the result as “requested always wins.” It is a
concrete result in the existing formal line and directly addresses the
professor's signal-identification and decision-value proposal. The optimal
one-step value theorem is stronger than the preceding comparison of the
fixed proportional updates, but remains a two-world Top-1 result. It still
does not prove the report's universal windup claim, distinguish Top-K from
generic censored multinomial testing, beat the independent outcome-map
benchmark, price telemetry in system units, or establish model-quality
benefit. The full exact expectations,
paired Monte Carlo check, output hash, and interpretation are recorded in
[`two_saturated_expert_indistinguishability_results_2026-10-17.md`](two_saturated_expert_indistinguishability_results_2026-10-17.md).

The two-saturated experiment was also rerun in this review. The exact-law
table is unchanged; the machine-readable result SHA-256 is
`9cc5ef62cc8fc39f7cbefec873d611e3f0ec4c20d1a3747c00595d44e1fb320e`. At
`T=320` and `640`, respectively, the enumerated finite-state lower bounds on
the all-admitted-policy value gap are `0.018498060` and `0.029782371` in
normalized overflow units. The fixed-update comparison still crosses: at
`T=40` and `80` admitted has lower expected second-batch overflow in both
worlds; at `T=320` and `640` requested has lower expected overflow in both.
This checked rerun supports the exact two-world theorem and also preserves
the finite-size caveat; it does not turn that family into an all-controller,
all-horizon, system-cost, or benchmark-separation result.

## Independent rerun and primary-source comparison (2026-10-17)

I reran the two locked expected-field experiments from this checkout after
reviewing the underlying equations:

| Run | Controlled synthetic model and result | What it verifies |
|---|---|---|
| `python scripts/run_topk_expected_admission_jacobian.py` | Top-1 Gumbel-Max; 72 registered cells over three request-probability profiles, six batch sizes, and four capacity ratios. All checks passed; maximum analytic-Jacobian/central-difference error `2.3761e-10`; exact witness curl `-29/2187`; 18 no-clipping and 24 uniform-state zero-curl controls passed. Grid SHA-256 `00e21f496e352e793ffa4be79b076b8e45c1990f8fdbb1dc949856017bec3e09`. | Finite-batch attenuation identity and its Top-1 quotient-curl consequence for the declared expected field. |
| `python scripts/run_topk_general_k_admission_curl.py` | Gumbel Top-K with `E=4`, `K∈{1,2,3}`, `T∈{32,128,512}`; 27 registered cells. All checks passed; maximum admitted-Jacobian error `5.2563e-10`; all 9 skewed/clipped cells had nonzero curl and all 18 symmetry/no-clipping controls had zero curl. Result SHA-256 `3d4f14ee23c5fde23ad98a9f72c3572e6895668e345552c53099cb51bd7a8be5`. | The same clipping/Jacobian mechanism is present for `K>1` in this finite controlled grid; it is not a general nonzero-curl theorem for every Top-K law or capacity profile. |

These are exact-expectation synthetic audits with finite-difference checks,
not Monte Carlo runs and not closed-loop performance measurements. Their
protocols, equations, and output files remain the authorities for details:
[`topk_expected_admission_jacobian_protocol_2026-10-17.md`](topk_expected_admission_jacobian_protocol_2026-10-17.md),
[`topk_expected_admission_jacobian_results_2026-10-17.md`](topk_expected_admission_jacobian_results_2026-10-17.md),
[`topk_general_k_admission_curl_protocol_2026-10-17.md`](topk_general_k_admission_curl_protocol_2026-10-17.md),
and [`topk_general_k_admission_curl_results_2026-10-17.md`](topk_general_k_admission_curl_results_2026-10-17.md).

The primary-text comparison bounds the theorem's claim. The [φ-Balancing
paper](https://arxiv.org/abs/2605.15403), §3 and Algorithm 1, constructs a
population objective from expected pre-selection routing probabilities and
uses mirror descent; it does not analyze the expected *hard admitted-count*
field after `A_e=min(R_e,C_e)`. The [Loss-Free Balancing
paper](https://arxiv.org/abs/2408.15664), Eq. (3) and Algorithm 1, updates
pre-Top-K score biases from observed assigned-token counts; its stated
algorithm does not define the capacity-clipped signal map in the canonical
model. Those are close and mandatory comparisons, not evidence that the
clipped-field result is novel. In particular, the present theorem is not a
claim that all MoE balancing fields lack potentials.

The concrete statement carried forward from the professor's sensitivity
suggestion is therefore: **under iid token affinities and canonical
per-expert admission, clipping multiplies each expected admitted-load
sensitivity by an exact binomial factor; in explicit Top-K/Gumbel instances,
the resulting quotient field has nonzero curl.** This remains the original
requested-versus-admitted/capacity model. It is a structural theorem, not the
report's broader claim about every integral/sign controller, an
information-theoretic impossibility at finite batch size, a priced collective,
or a real-model gain. The existing closed-loop overflow theorems and
controlled runs remain separate evidence; their controller and capacity
conditions must accompany every result.

The full conference-level gate is still open: connect this structural
mechanism to a robust closed-loop value or system-level result that survives
the exact finite-instance outcome-map comparison, and measure the actual
incremental cost of replacing versus adding the signal in a pinned runtime.
The current results do not prove that gate has been passed.

## Same-plant synthesis of the canonical facet and overflow results

To make the professor suggestions serve the model already being studied, I
paired two established results without adopting a new admission mechanism:
the exact two-step requested-versus-admitted overflow comparison and the
unconditioned random-facet theorem. The joint theorem is in
[`joint_topk_overflow_facet_theorem_2026-10-17.md`](joint_topk_overflow_facet_theorem_2026-10-17.md).
It strengthens the specified two-step result to convergence in probability
of the normalized gap, then combines that event with the regular
non-potential-facet event using a union bound. The conclusion is same-sample
co-occurrence with probability tending to one, not causal mediation.

The locked exact-grid experiment used `E=4`, `K=2`, one-short/equal-rival
exact-total capacities, 50 paired plants at each `T∈{3360,6720,13440}`, and
`d∈{1/4,1/2,3/4}`. All 150 plants had a regular mismatched facet; all 450
plant/gain rows had positive normalized overflow gap and the joint event.
There were 2,145 regular mismatched candidate facets, zero ambiguous
facets, and zero mismatches in the no-clipping control. All 450 overflow
totals exactly match the preceding arbitrary-Top-K experiment on the same
seeds. Two executions of the final runner produced identical hashes.

This is evidence for the combined canonical-model theorem and a check that
the professor's structural suggestion is compatible with the existing
formal definitions. It does **not** validate the report's proposed
score-truncated admission model, universal integral-controller windup,
collective price, real-model gain, or top-conference novelty. In particular,
rank-based removal under independent per-expert caps still has admitted
count `min(R_e,C_e)`; a device-level shared budget would be a different
admission map and needs its own formal comparison. Protocol, full plant data,
facet rows, and hashes are recorded in
[`joint_facet_overflow_results_2026-10-17.md`](joint_facet_overflow_results_2026-10-17.md)
and `results/joint_facet_overflow/`.

## Request sufficiency and target correction in the one-short family

The uniform-target overflow comparison above must not be interpreted as
evidence that requested counts are necessary in this family. Exact
mass-conserving clipping implies that if at most one coordinate of `A` is at
capacity, then `(A,C,K,T)` uniquely determines `R`: unsaturated coordinates
equal their requests, and the remaining request count follows from
`sum_e R_e=K*T`. The proposition and its dynamic population corollary are in
[`single_saturation_signal_reconstruction_theorem_2026-10-17.md`](single_saturation_signal_reconstruction_theorem_2026-10-17.md).

The corollary studies the already-defined formal capacity-relative update
`P_0((R-C)/(K*T))`. On the one-short iid family, it moves pressure toward
the capacity proportions and the population overflow tends to zero. An
admitted-only controller that first reconstructs `R` follows exactly the
same requested-capacity trajectory whenever only one expert is saturated.
That isolates two different effects: the admitted observation loses request
allocation only on multi-saturated fibers; using the uniform target despite
heterogeneous capacities is a separate controller-target mismatch.

The locked finite experiment used Top-1, `E=4`, Gumbel affinities, exact-total
capacities `(T/8,7T/24,7T/24,7T/24)`, `eta=1`, eight updates, and 50 paired
static plants at each `T=2304,9216`. All 100 plants remained in the
one-saturated regime for all eight steps. The reconstruction recovered
every requested vector, and the admitted-reconstructed capacity-relative
arm matched requested capacity-relative pressure and routing exactly on
every step. Mean cumulative overflow per token was `0.496` for both
capacity-relative arms, versus `0.998` for requested uniform-target and
`1.644` for admitted uniform-target at `T=2304`; the `T=9216` values were
`0.496`, `1.001`, and `1.646`. Direct use of admitted counts in the
capacity-relative formula gave `0.807` and `0.816`, respectively, slower
than reconstruct-then-update. All no-clipping controls and count identities
passed; no ties or reconstruction fallbacks occurred.

This corrects the interpretation of the earlier overflow result, not its
arithmetic: its gap is real for its uniform-target update, but it is not an
irreducible information gap in the one-short family. It remains open whether
the professor's proposed multi-saturated regimes have a useful value of
requested telemetry after target correction and after exact reduction to
the outcome-map benchmark. The protocol, runner, complete records, and hashes
are in [`capacity_relative_reconstruction_experiment_results_2026-10-17.md`](capacity_relative_reconstruction_experiment_results_2026-10-17.md)
and `results/capacity_relative_reconstruction/`.

## Finite-batch two-saturation value result

The professor's identifiability/value-of-requested-telemetry suggestion now
has a second, broader-in-`E` exact result in the existing stochastic
Top-1/Gumbel model. Two saturated experts exchange probability mass while
their total probability and all tail probabilities remain fixed. Under
canonical independent per-expert clipping, the complete admitted-vector laws
become asymptotically indistinguishable, while a requested-count threshold
identifies the world. The proof gives the asymptotic normalized population
value gap `c*delta/(2a)` for every fixed `E>=3` under explicit strict margins.

I corrected an important objective mismatch before recording the result:
the first theorem statement used population overflow, whereas the canonical
formal model measures realized finite-batch overflow. The theorem now has a
separate finite-batch corollary. Jensen's inequality lower-bounds every
admitted policy by its population cost; the admitted-signal coupling changes
risk by at most the explicit `eps_A(T)`; and a requested threshold policy's
finite-batch cost is computed exactly from binomial tails. This yields a
positive optimal-value lower bound in 17 of the 18 registered cells. The
remaining cell (`E=8`, `delta=0.04`, `T=4800`) is inconclusive because its
lower bound is negative.

The controlled audit covers `E={3,4,8}`, `delta={0.04,0.08,0.12}`,
`T={4800,19200}`, and 2,000 paired draws per cell. Across 36,000 paired draws
(72,000 world-specific first-batch request vectors), all registered
saturation events held; all 36,000 coupled world pairs had identical
admitted vectors. The finite
second-batch overflow expectations use exact binomial positive-part sums,
independently checked against direct PMF summation for 27 small cases. The
runner and results are
[`run_two_saturated_general_value.py`](../../scripts/run_two_saturated_general_value.py),
[`two_saturated_general_value_protocol_2026-10-17.md`](two_saturated_general_value_protocol_2026-10-17.md),
and [`two_saturated_general_value_results_2026-10-17.md`](two_saturated_general_value_results_2026-10-17.md).

An invalid first execution was discarded: its NumPy multinomial call omitted
the pair category of mass `0.8`, which caused the residual probability to be
assigned to the final tail category. The corrected sampler includes the pair
category explicitly; two consecutive corrected runs have identical CSV and
summary hashes. This correction is recorded in the result report.

The external-theory audit keeps the claim bounded. Censored bandits and
censored semi-bandits establish that generic censoring/resource-allocation
problems are prior work; fixed-horizon active hypothesis testing is the
closest methodological neighbor for the two-world signal-value proof. METRO
shows a real MoE system paying for global Top-K information for a different
serving objective. These sources establish scope boundaries, not novelty
clearance. This result is still a Top-1, one-step MoE application; it does not
establish the professor report's universal windup claim, a multi-round
Top-K/gauge separation, measured collective price, trained-model benefit, or
the top-conference gate.

## Controlled one-versus-two-saturation experiment (2026-10-18)

To test the professor report's identifiability/value suggestion on the same
formal model, the two-world Gumbel-Top-K construction was rerun with paired
capacity profiles that create one versus two persistently saturated experts
per world. The registered grid covers `E={3,4,6,8}`, every `K=1,...,E-1`,
three batch sizes per `(E,K)`, and 5,000 paired draws per cell. Exact finite-
count Bayes risks were calculated for the same two world-target pressure
actions; simulation only checked those formulas and the coupling events.

Across 51 matched batch-size comparisons, the two-action value gap was larger
in the two-saturation profile every time. The mean exact gap was `0.00162`
with one saturated expert and `0.00693` with two. The requested Bayes error
averaged `0.0428` in both profiles; admitted Bayes error averaged `0.1213`
and `0.4068`, respectively. All mass/clipping/swap/target-solver controls
passed, and every Monte Carlo error check was within four standard errors.
The locked protocol, runner, exact cell data, and limitations are in
[`saturation_multiplicity_experiment_results_2026-10-18.md`](saturation_multiplicity_experiment_results_2026-10-18.md).

This supports the finite-grid saturation-multiplicity mechanism in the
professor's C2 direction. The theorem's one-saturation decoder bound and
two-saturation coupling bound are both numerically vacuous over this grid,
so the experiment does not empirically establish the asymptotic theorem.
The finite decision class has only two target pressures, and the entire
instance remains an exact censored Bayesian experiment. It does not settle
novelty against adaptive testing, assign a hardware price to requested
counts, validate a real router, or establish the top-conference claim.

## Explicit all-pressure Top-2 C2 result (2026-10-18)

The fixed Top-2 value theorem now has an explicit all-pressure certificate,
separate from the restricted two-action results above. For `E=3,K=2`, base
weights `(2,1,1)` and `(1,2,1)`, and exact-total capacity fractions
`(11/20,11/20,9/10)`, the analytic proof establishes
`27/200 <= v_* <= 459/3080` and a finite-batch lower bound on
`V_A(T)-V_R(T)` against all one-step policies using the full signal. Its
first-positive multiple-of-20 threshold was found by a double-precision
scan at `T=1680`; the threshold is not interval-certified. The proof audit
checked the Top-2 omission formulas and rational inequalities symbolically.

The controlled run at `T=1680,1800,3360` reproduced its CSV and summary
hashes. It found exact admitted sign-classification error near `1/2`, paired
admitted-vector equality from `0.99490` to `0.99984`, and exact value gaps
`0.14242` to `0.14457` **within the registered two-target-action class**.
The analytic all-policy lower bounds at those sizes are respectively
`0.00275`, `0.02638`, and `0.10684`; the experiment does not estimate the
all-policy values or prove the theorem. The runnable protocol and results are
[`top2_explicit_value_gap_experiment_protocol_2026-10-18.md`](top2_explicit_value_gap_experiment_protocol_2026-10-18.md)
and [`top2_explicit_value_gap_experiment_results_2026-10-18.md`](top2_explicit_value_gap_experiment_results_2026-10-18.md).

This closes the concrete C2 proof obligation for that stated family and
strengthens the professor's saturation-multiplicity proposal. It does not
prove the broader gradient/windup statement, measure a collective's price,
or resolve the exact reduction to outcome-costed adaptive testing. The
conference-level claim remains open for that precise reason; this result is
not evidence to relabel the no-go as a go.

## Update: target × signal factorial over saturation multiplicity (2026-10-18)

The existing multi-low population theorem was audited against its four
recurrences and then checked in a paired finite-batch factorial with
`E=4,K=2,m={1,2,3}`, exact-total capacities, two batch sizes, 12 paired
seeds, static/fresh batches, and horizons through 64. The locked run produced
5,040 plant rows, 420 arm cells, and 336 paired contrasts; all 72 no-clipping
controls passed and no routing ties occurred. Protocol, code, hashes, tables,
and population-prediction deviations are in
[`capacity_matched_multiplicity_experiment_results_2026-10-18.md`](capacity_matched_multiplicity_experiment_results_2026-10-18.md).

Across all 72 registered `(m,T,regime,H>=2)` comparisons, requested feedback
had lower cumulative overflow than admitted feedback in all 12/12 paired
seeds under both uniform and capacity-matched targets. Capacity-target
admitted feedback also beat no feedback in every paired plant for `H>=2`;
the arms share initial cost at `H=1`. Thus the large
uniform-target penalty is not evidence that admitted feedback has no control
authority: matching the target substantially improves that arm, while the
requested signal retains an advantage for the specified direct update. At
`H=64`, finite-batch capacity-target overflow remains above the population
recurrence, especially for requested feedback; that discrepancy is recorded
and is not treated as a finite-batch confidence claim.

This closes the same-model finite-batch check for the multi-low target ×
signal extension, not the central paper theorem. It does not establish a
universal windup claim, optimal-policy value gap, measured telemetry cost,
real-system benefit, or separation from outcome-costed adaptive testing. The
top-conference novelty gate remains open; this experiment does not change the
existing no-go decision for the general control-limitation claim.

## Primary-source boundary check (2026-10-18)

The targeted source check confirms the current novelty boundary. Kumar and
Mouchtaki's censored-newsvendor paper studies finite-sample worst-case regret
from sales `min(demand, inventory)` and shows that targeted uncensored
observations can improve guarantees; it is a close censored-information/value
neighbor, but its static inventory-learning model does not establish the
MoE pressure or Top-K result
([primary paper](https://arxiv.org/abs/2602.16842)). Cicalese, Laber, and
Saettler study adaptive decision trees with costs and Bayesian or worst-case
objectives; the project's one-shot E-world telemetry threshold reduces to
such a testing problem, so the threshold alone is not a distinct general
control principle
([primary paper](https://arxiv.org/abs/1309.2796),
[outcome-dependent testing costs](https://doi.org/10.1016/j.ipl.2015.02.006)).

The nearest MoE equation-level neighbors are also consequential. φ-Balancing
optimizes a potential of population routing probabilities by mirror descent
([ICML 2026 paper](https://proceedings.mlr.press/v306/chen26br.html)); it does
not analyze the post-capacity field `A=min(R,C)`. Qiu et al. report an extra
synchronization step to compute global-batch load-balancing statistics
([ACL 2025 paper](https://aclanthology.org/2025.acl-long.249/)). METRO gathers
global Top-K knowledge for a serving routing/placement objective
([paper](https://arxiv.org/abs/2512.09277)). Neither source measures the
marginal hardware cost of replacing an admitted-count vector with a requested-
count vector in the same controller and execution stack. Therefore “one
extra E-vector collective” remains an implementation hypothesis, not an
established price. These sources bound the claim; this targeted check is not
systematic novelty clearance.

## Follow-up: explicit C2 coefficient and joint finite-batch limit (2026-10-18)

The C2 proof has since been sharpened on the same line. For symmetric pair-
target capacities it now gives the exact small-skew coefficient
`j_(E,K)(r_c)/K` for every `E>=3` and `1<=K<E`, using an explicit finite sum
over Plackett-Luce top-K prefixes. It also gives an all-policy finite-batch
inequality and a joint capacity-margin/skew/batch-size limit. The exact
`E=3,K=2` member recovers `39/160`. This directly addresses the report's
request for a quantitative value law; it does not alter the problem
statement or claim a new general control theory. See
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md).

The controlled check covers an 81-cell `(E,K)` sensitivity grid, 24
population optimizer cells, 9 paired finite-batch cells, and a 3-cell
joint-scaling sequence. Its derivative audit matches central differences to
`7.45e-9` relative error; population slope ratios approach the theorem's
coefficient; mirrored admitted vectors alias at high batch size. The
optimizer is not a global proof certificate, and Monte Carlo does not
validate an all-policy theorem. Full code and data are in
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md).

**Unchanged central gate:** this is still a structured finite experiment
inside costed censored testing. The generalized Top-K/gauge consequence that
survives the independent benchmark remains unproved, and no same-stack
requested-count acquisition cost has been measured. This addition is progress
on the professor's C2 suggestion, not completion of the integrated C2/C3
top-conference theorem.

## Reproduced paired analysis of the synthetic admission pilot (2026-10-18)

I reran [`run_admission_geometry_synthetic.py`](../../scripts/run_admission_geometry_synthetic.py)
from a temporary working directory. The newly generated `summary.json` and
`trajectories.csv` match the archived artifacts byte-for-byte. The standalone
analysis [`analyze_admission_geometry.py`](../../scripts/analyze_admission_geometry.py)
rechecked request mass, dropped-route accounting, `A_e=min(R_e,C_e)`, the
per-expert score-versus-position equality, and the dropless `R=A` negative
control before computing paired summaries. Its machine-readable output is
[`analysis_summary.json`](../../results/admission_geometry/analysis_summary.json).

### Per-expert cap: this plant does not support requested-signal superiority

The plant has `E=8`, `K=2`, `T=128`, `C_e=24`, and 120 updates. Each batch
requests 256 routes; aggregate per-expert capacity is 192, so the exact
minimum possible dropped-route count is 64. Twenty seeds vary small affinity
noise around the same fixed ring-pair multiplicities. This is one structured
plant family, not 20 independent workload samples.

| Feedback | Mean cumulative dropped routes over 120 batches | Mean request-count L1 imbalance over time | Globally saturated batch fraction | First unsaturated step |
|---|---:|---:|---:|---:|
| No update | 7,680 | 32.000 | 1.000 | Not observed |
| Admitted count | 7,680 | 32.000 | 1.000 | Not observed |
| Requested count | 7,867.9 | 33.875 | 0.813 | 76 in every seed |

Requested minus no-update cumulative overflow was `+187.9` dropped routes on
average (paired 95% t interval `[159.98, 215.82]`), positive in all 20 seeds.
Time-averaged request imbalance was higher by `1.875` (paired 95% t interval
`[1.044, 2.706]`; positive in 17/20 seeds). Final-batch imbalance was not
reliably lower: the paired mean difference was `-1.1` with interval
`[-5.64, 3.44]`. The final-step mean of 30.9 versus 32.0 is not evidence of a
repeatable balancing improvement.

The admitted arm stayed at zero bias because every expert remained saturated
and its admitted vector stayed exactly `(24,...,24)`. It attained the
aggregate overflow floor throughout. This is a concrete counterexample to a
blanket assertion that replacing admitted counts with requested counts
improves the chosen overflow objective for this sign controller. It does not
show admitted feedback is generally superior: this is a static batch, one
hand-designed route-pair template, and fixed gain and horizon. The intervals
summarize the seeded small-noise generator only; they do not estimate
prevalence over MoE models or training workloads.

Changing only score-ranked versus position-ranked retention under independent
per-expert caps produced identical `R`, `A`, feedback, and bias trajectories
at every recorded step, as the identity `A_e=min(R_e,C_e)` requires.

### Coupled group-capacity arm: rank order matters only in the constructed hybrid

With two four-expert groups and a shared budget of 112 assignments per group,
the score-ranked and position-ranked policies differ under admitted feedback:
mean cumulative dropped routes were `4,007.8` and `3,850.5`, respectively.
The paired score-minus-position difference was `+157.3` (95% t interval
`[93.29, 221.31]`; positive in 18/20 seeds). Under requested feedback and no
feedback, the two drop orders had identical cumulative overflow in all paired
seeds because those controllers do not use admitted counts to update bias.

This shows that rank-dependent admitted-count feedback can matter when
admission couples experts through a shared budget. The group-capacity rule is
a synthetic hybrid, not a faithful implementation of DeepSeek-V2 or
Megatron-Core; the result cannot be transferred to either system. Again,
these intervals are descriptive for the narrow generator. The pilot does not
measure the requested-count signal's hardware cost.

### Consequence for the central theorem

The reproduced experiment narrows the empirical claim: signal quality alone
does not order the two specified sign controllers, and admission granularity
changes the mechanism. The exact signed-bias saturation theorem remains a
valid conditional result, but it does not predict this pilot's requested
controller outcome because the pilot starts from imbalanced request counts,
uses one fixed affinity batch, and compares particular update rules. This
pilot does not support a general requested-feedback advantage.

**The concrete mathematical centerpiece on the existing professor-directed
C2 line is now the saturation-multiplicity value theorem**, not the signed-
bias pilot. For the canonical iid Gumbel Top-K router with exact-total
per-expert clipping, it compares optimal one-step policies over all pressure
actions: one clipped coordinate per world has vanishing requested-signal
value as batch size grows; two swapped clipped coordinates have strictly
positive limiting value. Near the symmetric capacity boundary, the value
slope is the explicit finite Plackett-Luce prefix coefficient
`j_(E,K)(r_c)/K`, with a Top-K switching-facet representation and large-`E`
scaling laws. For `E=3,K=2`, the all-pressure common-action value has the
rational certificate `27/200 <= v_* <= 459/3080`. A sharpened exact-tail
all-policy proof is positive at `T=540` and exceeds `0.11389` at `T=1680`.

The controlled Top-2 experiment was rerun on 2026-10-18. Its cell and summary
hashes match the recorded values. At `T={1680,1800,3360}`, the original
Hoeffding analytic all-policy lower bounds are respectively `0.002752`,
`0.026382`, and `0.106835` normalized-overflow units. The exact two-target-action gaps are
`0.142418`, `0.142718`, and `0.144572`; those are empirical finite-class
values, not estimates of the unrestricted optimum. This is direct controlled
evidence for the theorem's finite-count and coupling calculations, while the
analytic inequalities supply the all-policy conclusion. Subsequent exact
binomial-tail arithmetic gives a stronger all-policy lower bound
`>0.1138908062` at `T=1680`; it also certifies positivity at `T=540`
(`>0.0000340156`). The latter is a proof-only batch size, not part of the
registered experiment. The experiment's recorded data and hashes are
unchanged.

That theorem settles a **specific, family-level C2 signal-value claim** under
its stated information model, loss, and action class. It does not settle the
professor report's broader integrated proposal about device-level score
truncation, universal closed-loop windup, or a measured observation-cost
break-even in a named training stack. Nor does its exact embedding in
costed censored testing establish a general control-theory separation. The
remaining paper-level question is whether the Top-K-specific coefficient,
its scaling, and the saturation-multiplicity transition yield a contribution
of sufficient novelty and consequence against the closest primary
literature. The current evidence supports a concrete theorem and a controlled
synthetic experiment; it does not by itself certify acceptance at a top
conference or a real-model quality benefit.

## Addendum: one-bit decision signal on the existing C2 line (2026-10-18)

The C2 result now has a decision-specific minimal-signal corollary in
[`saturation_multiplicity_one_bit_value_theorem_2026-10-18.md`](saturation_multiplicity_one_bit_value_theorem_2026-10-18.md).
For the same symmetric swapped-world Gumbel-Top-K family and two target
actions, the sign bit `1{R_1>R_2}` has exactly the full-request Bayes value at
every finite batch size. The proof is an explicit likelihood-ratio identity
for the request vector. Combining this with the already-proved all-pressure
two-saturation value gap shows that one bit is asymptotically sufficient and
zero additional bits (admitted counts alone) are not, in this named family.
This sharpens the professor's C2 value-of-information proposal; it is not a
generic new sufficiency theorem and does not itself clear the benchmark gate.

The result was checked on a newly frozen exact-count grid with weight ratio
`4/3`, `E={3,5,7}`, every `K<E`, three batch sizes, and both saturation
profiles: 72/72 one-bit/full-request values agreed, and admitted-only value
was strictly worse in all 36 two-saturation cells. A separate exact-rational
enumeration checked the complete request-vector likelihood ratio and Bayes
risk equality in 19 small cells. Protocol, output, and scope limits are in
[`saturation_multiplicity_one_bit_experiment_results_2026-10-18.md`](saturation_multiplicity_one_bit_experiment_results_2026-10-18.md).

### Correction to the proposed score-truncation observation mechanism

The professor report's statement that Megatron's `probs` drop order makes
the **per-expert admitted-count vector** a score-biased estimate of demand
does not hold for independent per-expert capacities. Megatron-Core documents
capacity as a per-expert limit and says `probs` drops the lowest-probability
routes within each expert
([capacity/drop behavior](https://github.com/llm-jp/Megatron-LM/blob/main/megatron/core/transformer/moe/README.md#L271-L279),
[drop-policy definitions](https://github.com/llm-jp/Megatron-LM/blob/main/megatron/core/transformer/moe/README.md#L391-L394)).
If expert `e` receives `R_e` routes and retains up to its own capacity `C_e`,
then its admitted count remains exactly `A_e=min(R_e,C_e)` regardless of
which routes are kept. The score ranking changes *token identity*, not the
count observation. This is the same count map studied by the clipping
theorems. This statement is for actual dispatched assignments with
`pad_to_capacity=False`: the implementation chooses up to `C_e` indices per
expert and intersects that mask with the original routing map. In the padded
case, the map contains padding entries and must not be mistaken for actual
admitted-token counts. The exact implementation is visible in
[Megatron-Core `apply_router_token_dropping`](https://github.com/NVIDIA/Megatron-LM/blob/main/megatron/core/transformer/moe/moe_utils.py#L1003-L1035).

Score-ranked retention can alter `A` counts when admission couples experts
through a shared device budget. That is a different observation kernel and
must be analyzed as such; the project's group-capacity synthetic pilot is
not by itself evidence about Megatron-Core or DeepSeek-V2. Therefore the
professor report's proposed score-biased-count extension is not validated by
the current per-expert C2 model. A faithful device-level theorem/experiment
would require implementing the exact public admission rule and comparing
requested, pre-drop, post-drop, and token-identity signals separately.

Finally, the one-bit theorem measures **payload size**, not aggregation cost.
Even computing `R_1-R_2` across distributed ranks may need a synchronized
reduction; the experiment makes no latency claim. No same-stack requested
signal surcharge has been measured.

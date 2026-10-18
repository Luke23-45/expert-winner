# Research decision record: capacity-limited MoE feedback

**As of:** 2026-10-18
**Branch:** `feat/research-censored-feedback`
**Purpose:** current research status and the single decision gate for a top-conference claim.

This file supersedes the earlier phase-by-phase roadmap. The prior sequence
assumed that an optimal censored-feedback theorem was still the active
capstone and described the literature lane as unoccupied. Subsequent reduction
audits invalidate both assumptions. The dated documents linked below retain
the detailed derivations and historical reasoning; this file is the current
decision source.

## Current decision

**Do not claim a new general control limitation or a top-conference theory
contribution from the current Phase-1 value-gap results.** They are valid
MoE-realized results, but their finite-instance Bellman problems transfer
exactly to metric-constrained polyhedral active testing. The fixed-instance
novelty route is closed.

**C2 theorem status, updated 2026-10-18:** the requested-versus-admitted
one-step value question now has a proved, all-pressure finite-batch result
for a concrete `E=3,K=2` Gumbel-Top-2 family with two clipped experts. The
common-action value has the exact rational bracket
`27/200 <= v_* <= 459/3080`; its explicit all-policy finite-batch lower
bound has a sharper exact-binomial certificate positive at `T=540` and a
lower bound greater than `0.11389` at `T=1680`. The
broader swapped-world theorem proves asymptotic positive value for every
`E>=3, 1<=K<E` under its strict capacity margins. A separate controlled
experiment covers 102 `(E,K,T,profile)` cells for the one- versus
two-saturation mechanism, and a three-size Top-2 replication checks the
finite-count and coupling calculations. These results make the C2
mathematical claim concrete; they do **not** prove the professor report's
full integrated claim (gradient attenuation plus universal windup plus
measured collective break-even), nor do they overcome the exact
outcome-costed adaptive-testing reduction. The current no-go for a
conference-level novelty claim therefore remains unchanged. See
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md),
[`topk_two_saturated_value_theorem_candidate_2026-10-17.md`](topk_two_saturated_value_theorem_candidate_2026-10-17.md),
and [`top2_explicit_value_gap_experiment_results_2026-10-18.md`](top2_explicit_value_gap_experiment_results_2026-10-18.md).

An exact cost corollary has now been added to the existing saturation-exit
line: from a request-balanced initial state with aggregate shortage, the
requested and no-feedback arms remain at the overflow floor, while admitted
feedback exits that floor by a finite Top-K arrangement bound under a strict
capacity-order condition. Its 110-plant exact-rational audit is recorded in
[`balanced_saturation_cost_experiment_results_2026-10-17.md`](balanced_saturation_cost_experiment_results_2026-10-17.md).
This strengthens the existing model result; it does not change the
instance-level benchmark reduction or clear the top-conference gate.

**Signed-bias follow-up, 2026-10-18:** the same finite-exit argument now has
an exact cumulative-overflow corollary for the signed admitted-count update
used by Megatron-Core. From exactly balanced initial requests, positive
capacities no larger than the balanced count, aggregate shortage, and a
strict gap in the signed capacity-feedback slopes at the Top-$K$ cut,
requested feedback and no update remain at the aggregate-overflow floor;
admitted feedback is never below it and is strictly above it after its first
unsaturated state. The explicit arrangement bound gives a finite horizon for
that strict gap. An exact rational grid audit passed all 63 cells over
`E={3,4,5,6,8}`, every `1<=K<E`, and three gains; two complete runs matched.
See [`signed_bias_saturation_exit_theorem_2026-10-17.md`](signed_bias_saturation_exit_theorem_2026-10-17.md)
and [`signed_bias_balanced_cost_2026-10-18/`](../../results/signed_bias_balanced_cost_2026-10-18/).
This is the most direct proved link to the professor's controller suggestion
so far. Its initial-balance and static-plant assumptions are substantive; it
does not prove a typical-training-workload effect or clear the benchmark and
runtime-impact gates.

The pinned Megatron source audit also shows that an R-only counter can replace
the post-drop E-count vector in the same existing all-reduce, under the
ordinary non-padded capacity path. Thus the added collective count and payload
are zero by construction; the local counting and end-to-end runtime overhead
remain unmeasured. This corrects the proposed “one extra collective” price
assumption. The current machine has CPU-only PyTorch, so no GPU latency claim
was measured here.

One parameterized Top-1 result remains worth preserving as a candidate
structural result: for the canonical identical-block E-world family and the
stated capacity regime, every pressure action pays at least
`(L/2) × expected support reduction` in overflow. Its proof uses the common
hub / three-class winner structure forced by Top-1 score comparisons. A
telescoping corollary gives a tight `L(N−1)/2` cumulative-overflow bound when
the policy is required to identify one of N worlds. This is a genuine family
statement, not merely an E=4 enumeration. The corollary changes the objective
to exact identification; it does not solve the original unconstrained
finite-horizon overflow-control problem or clear novelty against adaptive
testing. Treat it as a **candidate family theorem**, not a cleared
top-conference contribution.

The class-level go/no-go attempt is recorded in
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md).
Its outcome is **NO-GO for the control-limitation claim on present evidence**.
The four-capacity mechanism sweep below does not change that verdict: it is
one synthetic plant and supplies no independent-benchmark separation. The
claim can be reconsidered only after a theorem gives a quantitative
family-level value or complexity result tied to Top-K/root-arrangement
structure and compares it against an independently fixed benchmark in a way
that does not follow by copying the same outcome maps and metric.

## Evidence status

Use [`phase1_research_status_2026-10-17.md`](phase1_research_status_2026-10-17.md)
as the claim ledger. In brief:

- **Analytically proved:** the fixed E=3 long-horizon probe-versus-wait
  bounds for all causal randomized admitted policies; the canonical E-world
  pair-separation inequality and its exact-identification cost corollary
  under their explicit assumptions; unrestricted action reduction to subset
  probes for that family; the exact costed one-shot requested-observation
  value `s*min(h,N-1)` in the parameterized E-world regime; and the stated
  E=4 finite-horizon results. The one-shot telemetry price is abstract, and
  the E-world Bellman problem still reduces to costed subset testing.
- **Exactly audited, finite scope:** rational arrangement signatures,
  support partitions, and Bellman certificates for the documented E=4
  instances. These audits corroborate finite cases; they do not prove the
  all-pressure family theorem.
- **Exploratory diagnostics:** finite-grid Bellman values. Grids can miss
  narrow cells and are not continuous-pressure certificates.
- **Not established:** a Top-K-specific advantage in optimal value against
  an independent class-level active-testing benchmark; a new general
  censored-control lower bound; trained-model or real-router validation.

- **Stronger C3-aligned facet theorem in the existing formal model:** under
  iid continuous affinities and any fixed nonuniform exact-total capacity
  limit, the admitted field is non-potential with probability tending to one.
  A many-facet corollary gives at least `b_EK*sqrt(T)/2` distinct regular
  mismatched facets except with an explicit vanishing failure bound. The
  controlled exact-grid audit counts every proof-defined candidate
  facet in 500 `E=4,K=2` plants at each of four batch sizes; the mean mismatch
  count grows from `1.334` to `10.664`, with zero no-clipping mismatches and a
  deterministic rerun hash. See
  [`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md),
  [`many_facet_random_affinity_protocol_2026-10-17.md`](many_facet_random_affinity_protocol_2026-10-17.md),
  and [`many_facet_random_affinity_results_2026-10-17.md`](many_facet_random_affinity_results_2026-10-17.md).
  This gives a lower bound on a proof-defined subset, not a count of all
  root-arrangement signatures; the specific bound claimed as an existing
  asset in Professor Report 1 remains unverified. Region counting for
  braid-arrangement deformations is established mathematics. More directly,
  the token score-tie arrangement is a generic multiple-braid arrangement
  almost surely, whose exact region count is already given by Delcroix-Oger
  et al., *Cellular Diagonals of Permutahedra* (Theorem 2.21,
  [arXiv:2308.12119](https://arxiv.org/abs/2308.12119)). Request/admission
  signatures are coarsenings of those cells. Thus a bare root-arrangement
  region count is not a novelty claim; any capacity-signature refinement
  must be defined and shown to add a quantitative value consequence. This theorem does not
  change the no-go for a control-limitation claim: it supplies no
  controller-value gap, measured observation price, or separation from the
  outcome-map benchmark.

- **Uniform-capacity extension of the C3 structural result:** with iid
  `Uniform[0,1]` affinities and uniform exact-total capacities, the admitted
  field is non-potential with probability tending to one; the proof constructs
  at least `c_(E,K)*T^(1/4)` distinct nearby regular mismatched facets with
  high probability. A directly aligned `E=4,K=2` exact-grid audit covers
  `T=256` through `1,048,576`; all 376 retained candidates were regular and
  mismatched, all 18 no-clipping controls were zero, and the rerun summary
  hash matched. This removes the earlier dependence on a planted token or
  macroscopically heterogeneous capacity for the existence result. The
  finite audit tests one selected cross-mean pair per plant and is not
  evidence about a uniformly sampled facet or real-router prevalence. It
  does not change the no-go for the control-limitation claim. See
  [`uniform_capacity_nonpotentiality_theorem_2026-10-17.md`](uniform_capacity_nonpotentiality_theorem_2026-10-17.md),
  [`uniform_capacity_random_facet_protocol_2026-10-17.md`](uniform_capacity_random_facet_protocol_2026-10-17.md),
  and [`uniform_capacity_random_facet_results_2026-10-17.md`](uniform_capacity_random_facet_results_2026-10-17.md).

  **Coordinate qualification:** these non-potentiality claims concern
  Euclidean integrability of the admitted vector field in pressure
  coordinates. For fresh iid batches, the same expected update is mirror
  descent on a separable convex objective in Top-K inclusion-probability
  space. See
  [`capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md`](capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md).
  Thus facet mismatch is a structural property, not by itself evidence of
  instability, cycles, or absence of an optimization objective.

The 100-entry literature document is a **preliminary annotated scan**, not a
systematic review: it does not preserve the query strings, dates, screening
rules, or inclusion/exclusion log needed to reproduce such a protocol.
Individual primary-source reads remain useful, but the count of references is
not evidence of exhaustive coverage or novelty.

## Research boundary and decision rule

The benchmark note defines B0 and the independently described metric-
constrained polyhedral benchmark B1. It proves that every finite Top-K
instance can be simulated exactly in B1 by retaining its pressure metric,
arrangement outcomes, clipping, and costs. Therefore no **instance-level**
value gap from that benchmark is possible. The canonical E-world lemma is
narrower and more structured, but it has not yet yielded a benchmarked
optimal-value separation or a result beyond known costed adaptive-testing
tools.

The bounded Phase-1 theorem attempt is complete and produced a no-go for the
present control-limitation claim. This record does not open another research
queue. Reopen the question only if a materially new theorem target is
proposed; before proof work begins, specify:

1. A parameterized family (including its prior, capacities, affinity
   restrictions, horizon, and movement regime).
2. A benchmark and comparator fixed independently of that family, with a
   precise quantifier (worst case, average case, or minimax).
3. A quantitative conclusion—value, regret, information-cost, or complexity—
   whose dependence on Top-K/root-arrangement structure is explicit.
4. A reduction attack showing whether the statement follows unchanged from
   general metric-constrained polyhedral testing, decision-tree,
   active-sensing, or outcome-dependent-test-cost results.

**Stop rule:** if the theorem is preserved unchanged by that reduction, stop
the control-limitation claim. Retain the exact MoE realization and present it
as an application of active testing/control theory. Do not rename a general
testing result as MoE-specific.

## Empirical and paper decisions

One paired synthetic admission-geometry pilot and one bounded four-capacity
sweep have been run to test the professor report's score-drop mechanism;
exact controls and limitations are recorded in
[`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md)
and [`capacity_regime_sweep_results_2026-10-17.md`](capacity_regime_sweep_results_2026-10-17.md).
It shows that per-expert score-ranked dropping leaves count feedback
unchanged, while the separate grouped-capacity abstraction is
drop-rule-dependent. An exact two-token Top-1 example also verifies that a
shared device budget can change `A` at fixed `R`. The primary-source check
separates DeepSeek-V2's device-level drop mechanism (with selection-based
balance losses) from Megatron-Core's per-expert capacity path. At pinned
Megatron commit `36731ac`, the configured capacity-plus-expert-bias path
accumulates post-drop counts, so it instantiates the existing formal
admitted-count controller with `A=min(R,C)`. `probs` ranking changes route
identities, not these per-expert counts. B1's original clipping form does not
directly cover shared-device admission; B1-out represents each fixed
raw-affinity-ranked shared-capacity instance exactly, so that extension still
needs a family-level theorem beyond general polyhedral testing. The
experiments supply no real-router or model-quality evidence. The capacity
sweep's strongest positive case is partial saturation at `C=28`: all 20
admitted-feedback trajectories enter an absorbing global-saturation state at
steps 77–84, then attain per-batch minimum overflow `KT-EC=32`. The post-run
cumulative-overflow diagnostic is lower than both requested and no-feedback
arms in all 20 seeds. At `C=32` and `C=36`, cumulative overflow under admitted
feedback is higher than no feedback in every seed. That remains an exploratory
result for its registered plant family; do not generalize it to a capacity
phase theorem. The exact signed-bias finite-exit and cumulative-overflow
theorem proved elsewhere has different explicit hypotheses (balanced initial
requests, static batch, aggregate shortage, and a strict capacity-slope gap)
and does not certify the `C=28` sweep's broader parameter behavior. See
[`signed_bias_saturation_exit_theorem_2026-10-17.md`](signed_bias_saturation_exit_theorem_2026-10-17.md).

The exact two-expert theory is in `formal_core.md`: P2e characterizes the
admitted-sign controller for every static `E=2,K=1` affinity batch by its
count-threshold interval and invariant pressure lattice; P2d gives a
parameterized positive comparison; P2c gives a non-hitting counterexample.
The exploration branch now also has P2f, an exact `E=3,K=2` finite-horizon
family where admitted signed-bias feedback beats requested feedback and no
feedback, with a strict gain interval and a paired perturbation audit. Its
finite-instance benchmark attack is recorded in
[`top2_signed_bias_benchmark_reduction_2026-10-17.md`](top2_signed_bias_benchmark_reduction_2026-10-17.md): B1-out reproduces every trajectory and all three overflow totals exactly.

An exact capacity-phase extension varies the uniform per-expert capacity
over `C=1,...,19` on this same P2f affinity family. Across 57 capacity/gain
cells and all three signals, repeated rational gauge states certify the
all-horizon cost trajectories. At the three registered gains, for
`C=11,...,13`, admitted and requested feedback have equal cycle-average
overflow but their cumulative order changes with horizon; at the three
registered gains and `C=14,...,19`, the two feedback signals induce identical
request paths. A
continuous-gain refinement at `C=11,...,13` finds admitted feedback never
has lower eventual mean overflow than requested feedback, and both signals
are worse than no feedback throughout the interval. At `C=11,...,18`, both
feedback signals have higher eventual mean overflow than no feedback on the
registered grid. Full results are in
[`p2f_exact_capacity_phase_experiment_2026-10-17.md`](p2f_exact_capacity_phase_experiment_2026-10-17.md).

Two-sided exact comparisons now exist for both controller laws, with the
definitions kept separate. For signed expert bias, P2f gives an admitted-
better family and strict-margin uniform-capacity and heterogeneous
requested-better witnesses give the reverse ranking. For the canonical
proportional pressure law in `formal.md`, exact `E=3,K=1` and `E=8,K=2`
witnesses also give opposite rankings under uniform exact-total capacity;
the open step-size and affinity neighborhoods are recorded in
[`canonical_pressure_two_sided_comparison_2026-10-17.md`](canonical_pressure_two_sided_comparison_2026-10-17.md).
This closes the claim that one signal universally minimizes overflow for
either specified controller. It does not predict the winner from a new plant,
and it does not alter the benchmark-reduction verdict: B1-out can still copy
each finite instance's outcome map.

The new arbitrary-fixed-`E,K` extension gives a positive two-step cost
comparison **within the canonical proportional-pressure model**. For every
fixed `E>=2` and `1<=K<E`, under a parameterized iid Top-K family with
exact-total heterogeneous capacities, the normalized expected overflow gap
is `Phi_(E,K)(d)-K/E>0`, where `d=eta*r/K<1` and `r` is the shortfall of
one expert. Its proof is in
[`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md).
The preregistered experiment, exact-grid runner, and results are in
[`topk_e_expert_overflow_protocol_2026-10-17.md`](topk_e_expert_overflow_protocol_2026-10-17.md),
[`../../scripts/run_topk_e_expert_overflow.py`](../../scripts/run_topk_e_expert_overflow.py),
and [`topk_e_expert_overflow_results_2026-10-17.md`](topk_e_expert_overflow_results_2026-10-17.md).
The `K=1` expression `d-d^E/E` is a special case. The experiment supports
positive means across all registered cells, but has finite-size departures
at `E=8`. This is progress within the existing formal line; it is not the
professor report's priced-telemetry theorem, does not compare against every
causal policy, and does not survive exact finite-instance B1-out reduction
as a new general information principle. The top-conference class-level gate
therefore remains open.

A subsequent theorem strengthens the same formal model from two steps to
all fixed finite horizons in the population limit. Under iid affinities with
positive bounded density and the stated one-short/equal-rival-capacity family,
admitted proportional feedback follows an explicit scalar pressure recurrence
and has iterated long-run average overflow gap `(E-1)r`; requested feedback
stays at the symmetric population pressure. A runner audit then found that an
earlier finite-batch helper reset pressure instead of applying the specified
cumulative update. That invalidated the earlier reported magnitude failure.
The corrected static-batch run has aggregate mean/prediction ratio `.998` at
`H=64`, with 119/126 nominal intervals covering the population prediction.
A paired fresh-batch run (same initial plant; iid batches thereafter) finds
lower cumulative gaps than static reuse in 35/42 cells and is closer on
average to the finite-`T` mean recurrence. The correction and both protocols
and results are recorded in the two `topk_*long_run*` and
`topk_fresh_batch_closed_loop*` documents. This resolves the prior empirical
magnitude objection over the tested grid, but not fixed-`T` infinite-horizon
convergence or the exact outcome-map benchmark reduction. The remaining
conference gate is the class-level result: a quantitative Top-K consequence
that does not follow unchanged from encoding the same finite outcomes in the
independent benchmark.

The conference gate therefore remains open only to a genuinely class-level
result: fix an independently specified outcome-cost testing benchmark and
family quantifier first, then prove a quantitative consequence of Top-K
structure that does not follow unchanged from copying the outcome maps. If
the reduction preserves the proposed statement, stop the control-limitation
claim and keep the exact MoE comparisons as applications. Do not start
training on these synthetic overflow results. Training becomes relevant only
after a separate system-quality claim is specified and the signal path is
verified against an actual implementation.

The integration branch remains a separate target. Promote material only
after proof review, benchmark comparison, reproducible evidence, and a clear
claim boundary. The current record supports preserving the formal results;
it does not support saying that a top-conference contribution is complete or
that acceptance-level novelty has been established.

## Professor Report 1: independent candidate audit (2026-10-17)

The proposed C2 arc—value of requested telemetry versus its measurement
cost—fits the existing requested/admitted question, but the report's claimed
cost model is not yet supported by the audited implementation. At the pinned
Megatron-Core path above, the bias update already reduces an expert-count
vector. Replacing post-drop counts with pre-drop requested counts can use that
same reduction; it is not justified to charge an additional full-vector
collective without profiling a concrete implementation. The existing exact
E-world result has a valid abstract break-even in overflow units, but its DP
reduces exactly to costed subset testing and its `kappa` is not a measured
system cost. It is not a theorem that requested telemetry is worth an extra
collective.

The primary-source comparison supports these boundaries:

- DeepSeek-V2 does use device-level lowest-affinity route dropping, but its
  expert-balance loss is computed from tokens selected by the router. The
  paper does not instantiate an admitted-count sign controller. Device-level
  drop plus admitted-count feedback would be a constructed hybrid.
- `phi`-Balancing already studies convex potentials of expected routing
  distributions and derives mirror-descent updates. Our capacity-clipped
  expected objective is a precise model-specific extension; the existence of
  a potential or mirror-descent representation is not itself a novelty
  claim.
- METRO gathers global top-k information to optimize activated-expert load
  for serving. This establishes that communication-backed routing information
  can be useful for a different objective. It does not measure the marginal
  cost or value of substituting requested counts for admitted counts in the
  audited training controller.
- Demons in the Detail pays for synchronization of global-batch selection
  statistics to change the scope of a load-balancing loss. That is close
  evidence that statistics scope can carry a communication cost, but it is
  not capacity-censored feedback or an admitted-versus-requested controller.

These boundaries are checked against the primary texts: [DeepSeek-V2,
§§2.2.3–2.2.4](https://arxiv.org/html/2405.04434), [\(\phi\)-Balancing,
ICML 2026](https://proceedings.mlr.press/v306/chen26br.html), [METRO,
arXiv:2512.09277](https://arxiv.org/abs/2512.09277), and [Demons in the
Detail](https://arxiv.org/abs/2501.11873). The costed-testing reduction is
also established prior art; see the [PMLR decision-tree treatment](https://proceedings.mlr.press/v32/cicalese14.html)
and [value-dependent testing-cost model](https://doi.org/10.1016/j.ipl.2015.02.006).
This is a targeted source check, not a systematic novelty review.

The requested synthetic controls were rerun from the current exploration
checkout with Python 3.14.5 and CPU PyTorch 2.12.0. The admission-geometry
experiment again passed all four exact controls over 20 paired seeds and 120
steps: per-expert score-ranked and position-ranked retention give identical
count and pressure trajectories; uniform globally saturated admitted-sign
feedback freezes; the dropless requested/admitted trajectories coincide; and
a two-token shared-device example changes `A` at fixed `R` only under the
separate shared-capacity rule. The summary SHA-256 is
`bea8cdb34284cfdb5acd198c6527b6070dc59e4689c589f272566754e6716f54`.
The exact-rational E-world audit also passed all 29,583 Bellman checks in 171
parameter cells. These reruns validate the declared synthetic calculations;
they do not establish production prevalence, measured telemetry cost, model
quality, or a benchmark separation.

The paired trajectory reanalysis of the admission-geometry pilot now also
shows that, on its per-expert-capacity static plant, requested-sign feedback
has **higher** 120-step cumulative overflow than admitted feedback and no
update: paired mean difference `+187.9` dropped routes, positive in all 20
seeded perturbations (descriptive paired 95% t interval `[159.98,215.82]`).
It also raises time-averaged request imbalance. The run therefore supports no
general requested-signal superiority claim. In the separate synthetic
group-capacity hybrid, score-ranked versus position-ranked admission changes
cumulative overflow only under admitted feedback; this is not a reproduction
of a deployed stack. The full paired summary is in
[`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md)
and [`analysis_summary.json`](../../results/admission_geometry/analysis_summary.json).

**Next gate for the existing research line:** keep the canonical per-expert
model and make one measured marginal-cost/value comparison in the audited
implementation. Compare `A` and `R` as alternative inputs to the same count
reduction, record the actual incremental kernel, memory, and latency cost,
and pair that cost with a prespecified system outcome. If the marginal cost is
negligible, C2's priced-observation claim does not apply to this path; pursue
the controller's system-level effect only if a theorem predicts the regime
and a paired real-model experiment can test it. Do not substitute the
DeepSeek-V2 device-drop hybrid for this experiment, and do not begin training
on the synthetic overflow result alone. The experiment's decisive controls,
primary metric, and falsifier must be fixed before any model run.

## Update: arbitrary-Top-K two-world result (2026-10-17)

The same requested/admitted question now has a proved arbitrary-`E,K`
two-world family result under Gumbel Top-K and the canonical per-expert
clipping rule. It supplies an explicit finite-`T` inequality in terms of a
strictly positive but implicit population constant `v_*`; it does not yet
give a useful closed-form lower bound for that constant. The accompanying
controlled synthetic audit has 33 `(E,K,T)` cells, 2,000 coupled draws per
cell, exact rational Top-K subset probabilities converted to double for
sampling, binomial-tail overflow calculations, and byte-identical outputs
on rerun. A post-run proof establishes that the registered sign rules are
Bayes-optimal from the full requested/admitted count vectors within the two
world-target actions, with exact finite-batch values added for all 33 cells.
This does not optimize over all pressures, and the experiment measures no
hardware price. Details are in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md),
the paired [protocol](topk_swapped_saturation_value_protocol_2026-10-17.md),
the [results](topk_swapped_saturation_value_results_2026-10-17.md), and the
[exact Bayes analysis](topk_swapped_saturation_bayes_value_analysis_2026-10-17.md).

The benchmark attack for this result is complete: at every finite `T`, it
is exactly an instance of a general two-state censored Bayesian experiment.
Consequently, it improves the scope of the MoE application but does not
clear the class-level novelty gate. The related source and novelty boundary
are in
[`topk_swapped_saturation_reduction_attack_2026-10-17.md`](topk_swapped_saturation_reduction_attack_2026-10-17.md)
and
[`topk_swapped_saturation_literature_boundary_2026-10-17.md`](topk_swapped_saturation_literature_boundary_2026-10-17.md).
**Superseding update (2026-10-18):** the saturation-multiplicity theorem now
proves an explicit local small-skew coefficient `j_(E,K)(r_c)/K`, identifies
it with a weighted Top-K switching-facet flux, and derives large-`E` scaling
in proportional-`K` and `K=E-1` regimes. This closes the earlier *missing
explicit family-scaling law* item. It does not make the unrestricted
common-action constant `v_*` explicit for arbitrary capacities, defeat the
exact embedding in the censored Bayesian benchmark, or establish that the
coefficient is important enough for a top-conference paper. A system-value
claim still needs measured benefit and actual marginal telemetry cost. No
training claim follows from this synthetic experiment. See
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md).

## Update: decision-theoretic constraint on signal ranking (2026-10-17)

Under the canonical per-expert model, `A=min(R,C)` is a deterministic
function of `R`. An unrestricted requested-observation policy can therefore
compute `A` and emulate every admitted-observation policy. With equal
observation costs, the optimal requested policy cannot have greater task
cost than the optimal admitted policy. This is Blackwell's ordering applied
to this map, not a new theorem. The Top-2 result where the direct admitted
sign update wins compares two specific update rules and remains valid; a
requested observer can reproduce the admitted rule by clipping internally.

This rules out a universal optimal-value advantage for admitted feedback.
The consistent conference target within the existing requested/admitted
line is a costed comparison: quantify requested feedback's value for a
prespecified controller class and compare it to the measured marginal cost
of replacing the input to the existing count reduction. The audited
Megatron path already reduces one count vector, so an added-collective cost
is not assumed. The formal consequence and policy scope are in
[`feedback_information_dominance_and_costed_value_2026-10-17.md`](feedback_information_dominance_and_costed_value_2026-10-17.md).
No such system value/cost comparison is complete; the current environment
has CPU-only PyTorch, and the synthetic results do not substitute for it.

## Update: capacity-matched target falsification and experiment (2026-10-18)

The one-short-capacity family has now been analyzed with the same Top-K,
per-expert clipping, and proportional pressure update, but with a second
target `mu=C/(K*T)` paired against the original uniform target. The new
population theorem proves that both requested- and admitted-feedback
trajectories converge to the capacity-matched routing distribution and
zero overflow under an explicit common gain bound. This is a counterexample
to a blanket assertion that admitted feedback necessarily loses all control
authority as saturation occurs. It also isolates the existing uniform-target
overflow theorem as a target-mismatch result; it does not prove that the
observation channel is irrelevant in other families.

The locked experiment covers `E=4`, `K={1,2,3}`, `T={2304,9216}`, 12 paired
plants, horizons through 64, and static/fresh affinity regimes. All registered
invariants and 72 no-clipping controls pass with zero ties, and the rerun
reproduces all artifact hashes. At `T=9216,H=64` in the fresh regime,
capacity-target admitted feedback beats no feedback in all 36 paired plants
(12 for each `K`), while requested feedback still has lower cumulative
overflow than admitted feedback in every registered seed. The finite-`T`
mean-field interval coverage is 62/84 capacity-target cells; the population
limit magnitudes are not uniformly supported at this finite horizon. Full
tables and limits are in
[`capacity_matched_target_experiment_results_2026-10-18.md`](capacity_matched_target_experiment_results_2026-10-18.md).

This strengthens the existing controller-mismatch analysis but does not
clear the conference gate: it is a constructed family, has no measured
telemetry price or model-quality result, and every fixed finite outcome map
still embeds into B1. Do not reinterpret it as the professor report's
requested-count value-of-information theorem. The admissible paper claim must
keep target choice, observation choice, and system cost as separate axes.

The proof audit also found that this new scalar convergence argument uses
only a strictly increasing bounded-slope response curve; its proof does not
use a Top-K-specific arrangement constraint. It is therefore not, by itself,
the missing class-level Top-K contribution. This scope limit is recorded in
the theorem note, together with anti-windup and `phi`-Balancing as prior-art
neighbors.

## Update: capacity-slack factorial on the same closed-loop theorem (2026-10-18)

The existing long-run population theorem's controlled finite-batch check has
been extended over `E={4,8}`, every `K<E`, three affinity laws, two shortage
magnitudes, two batch sizes, and static/fresh batch regimes. All 120
registered profiles passed the routing, capacity, overflow, no-clipping, and
quadrature checks. Static-batch results track the finite-horizon population
recurrence closely through `H=32`; all static cell means are positive after
the shared initial-cost round. Fresh-batch results have positive means in
all cells by `H=4`, but one registered `E=8,K=7` small-shortage cell has a
negative two-round mean with a 95% paired interval below zero, opposite the
large-batch population prediction. It is outside the theorem's primary
static-batch setup and is retained as a finite-size limitation. Full design,
raw outputs, and results are in
[`topk_capacity_slack_factorial_protocol_2026-10-18.md`](topk_capacity_slack_factorial_protocol_2026-10-18.md)
and [`topk_capacity_slack_factorial_results_2026-10-18.md`](topk_capacity_slack_factorial_results_2026-10-18.md).

This broadens the controlled mechanism evidence without changing the
class-level decision: the single-short-expert population trajectory has
request reconstruction by conservation, so it is not the requested-signal
identification theorem; the finite-instance active-testing reduction,
absence of measured telemetry cost, and lack of trained-model outcome remain
unresolved for a top-conference claim.

## Update: saturation multiplicity and all-K controlled check (2026-10-18)

The existing two-world C2 line now has a parameterized saturation-multiplicity
theorem in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md):
with one persistently saturated expert per world, the admitted signal's
one-step value loss is bounded by an exponentially decaying decoding-failure
probability; with two persistently saturated experts, the all-policy
one-step gap converges to a strictly positive common-action value `v_*` for
the stated Gumbel-Top-K family. This is the strongest direct theorem so far
matching the professor's information-value proposal. It is a static two-world
decision theorem, not a multi-round controller/windup theorem, and its general
`v_*` is implicit for general `K`. A separate Top-1 weight/capacity family
has exact value `1/36`; it is not the parameter profile used in this
experiment. Its costed-observation corollary says the break-even price tends
to zero with one saturated expert and to `v_*` with two; the price is
measured in normalized overflow, not hardware time or energy.

The registered experiment compares one versus two saturated experts across
`E={3,4,6,8}`, every `K<E`, and 51 matched `(E,K,T)` cells. The exact value
gap in the two-target-action class was larger with two saturated experts in
all 51 comparisons. The all-policy asymptotic theorem's finite-size
Hoeffding bounds are vacuous at the tested batch sizes, and the experiment
does not optimize the unrestricted pressure action or measure signal cost.
See
[`saturation_multiplicity_experiment_results_2026-10-18.md`](saturation_multiplicity_experiment_results_2026-10-18.md).

The current decision therefore remains **no-go for a general control-
limitation claim**: the fixed finite decision problem embeds exactly in the
broader censored Bayesian benchmark. The local Top-K coefficient and its
scaling law are now proved, so the earlier “missing explicit `(E,K)` bound”
objection is closed; whether that structured result is sufficiently novel
and consequential remains unestablished. A top-conference claim is therefore
not supported yet, though the reduction alone does not rule it out. Costed decision
trees and value-of-information methods are established neighboring frameworks
([Cicalese et al., ICML 2014](https://proceedings.mlr.press/v32/cicalese14.html),
[Chen et al., UAI 2017](https://proceedings.mlr.press/r15/chen17a.html)). The
recent censored-feedback work also jointly studies structural identification
and communication cost, though in a threshold-activated multi-agent bandit
model rather than MoE routing ([Ledford and Regli, 2026](https://arxiv.org/abs/2605.27076)).
In MoE itself, global-batch load balancing has paid an extra synchronization
step ([Qiu et al., ACL 2025](https://aclanthology.org/2025.acl-long.249/)),
and METRO gathers global Top-K information for its serving objective
([Yu et al., 2025](https://arxiv.org/abs/2512.09277)). These are close
boundaries, not proofs that the present theorem is already known. The
remaining publication test is to assess the precise coefficient and its
scaling against the closest specific results, and establish why that
structured law matters; alternatively, a systems claim requires a named-
system measurement of benefit against actual marginal observation cost.
The existing synthetic experiments establish mechanism-level behavior, not
either of those contribution tests.

## Update: exact finite-size certificate for the existing Top-1 signal theorem (2026-10-18)

For the existing arbitrary-`E` Top-1 swapped family, the request-classifier
term in the all-policy finite-batch inequality has been sharpened from a
Chernoff bound to its exact conditional-binomial error. This changes no
model, theorem quantifier, or benchmark comparison. The resulting explicit
certificate is positive at admissible `T=704,832,1356,2492,4620,8556` for
`E=3,4,8,16,32,64`, respectively; these threshold scans use double-precision
binomial tails and are not interval-certified. A paired controlled run at
the first-positive thresholds for `E={3,4,8}` and at twice those sizes
matches the exact signal errors and clipping coupling in all six cells. The
proof, threshold audit, protocol, and raw results are linked from
[`top1_exact_gap_threshold_experiment_results_2026-10-18.md`](top1_exact_gap_threshold_experiment_results_2026-10-18.md).

This concretely strengthens the professor-aligned value-of-requested-signal
result: it now has an explicit positive finite-batch lower bound against all
one-step admitted policies in this stated Top-1 family. It remains a static
two-world censored-decision theorem with an exact adaptive-testing
representation. It does not prove the professor report's broader
multi-round windup claim, price a collective in hardware units, or clear the
top-conference novelty gate. The current decision is still no-go for those
broader claims on present evidence.

## Update: multi-low target × signal validation (2026-10-18)

A paired finite-batch factorial has now checked the existing target-by-signal
population extension for `m={1,2,3}` low-capacity experts under `E=4,K=2`,
two batch sizes, static and fresh batches, and horizons through 64. Requested
feedback had lower overflow than admitted feedback in all paired plants for
both targets at every registered `H>=2`; capacity-target admitted feedback
also beat no feedback in every plant. The results and finite-batch/population
discrepancies are recorded in
[`capacity_matched_multiplicity_experiment_results_2026-10-18.md`](capacity_matched_multiplicity_experiment_results_2026-10-18.md).

This confirms the same-model target × signal effect across the registered
saturation multiplicities. It does not satisfy the independent-benchmark
gate or measure a telemetry price, so the decision above remains unchanged:
the central top-conference theorem is not settled by this experiment.

## Update: explicit pair-skew value law and joint limit (2026-10-18)

The existing saturation-multiplicity C2 theorem now has an explicit
pair-skew coefficient for every `E>=3` and `1<=K<E`, expressed as a finite
sum over Plackett-Luce ordered prefixes. For rational symmetric pair-target
capacities, the small-skew common-action value is
`epsilon*j_(E,K)(r_c)/K+o(epsilon)`. The same note proves an all-policy
finite-batch inequality and a joint limit as baseline capacity margin, world
skew, and batch size vary. This sharpens the professor's requested C2
value-versus-slack analysis; it does not change the research objective or
create another track.

The controlled numerical audit used 81 finite-sum sensitivity cells over
`E=3,...,8`, every `K<E`, and three pair-weight ratios; analytic derivatives
matched central differences to relative error at most `7.45e-9`. It also
used 24 population optimizer cells, 9 finite-batch cells with 20,000 paired
draws each, and 3 population cells in the joint-limit scaling sequence.
Population slope error fell from `1.4060e-4` at `epsilon=0.04` to
`2.1982e-6` at `epsilon=0.005`; the joint sequence's `v_num/epsilon`
approached `0.243750` for the `E=3,K=2,c=0.55` case. The optimizer is not a
global certificate, and experiments do not prove the theorem. Full protocol,
raw data, code, and limits are in
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md).

**The central top-conference theorem remains unsettled.** The explicit
small-skew sensitivity law for general `(E,K)` is now derived and numerically
audited in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md)
and
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md).
That closes the earlier coefficient-derivation task; it does **not** close
the novelty gate. Each fixed finite experiment still embeds exactly in the
costed censored-testing benchmark, and the sensitivity law is currently a
structured instance of that benchmark. The remaining theorem task is to
define the broader state-constrained benchmark independently and prove a
quantitative Top-K/gauge restriction or separation that cannot be obtained
unchanged in that benchmark. No requested-count collective price has been
measured, so no systems-cost claim follows. If the benchmark comparison
produces no such structural result, stop claiming a new general control
limitation and present the result as an exact MoE application of
costed-testing theory.

## C2/C3 progress update: explicit price threshold (2026-10-18)

The same general symmetric-pair Top-K theorem now states the exact optional
purchase rule `V_optional=min(V_A,kappa+V_R)` and defines the unrestricted
break-even `kappa_star=V_A-V_R`. Its all-policy finite-batch value bound
gives an explicit lower certificate and the small-skew limit
`kappa_star/epsilon -> j_(E,K)(r_c)/K`. The statement remains in normalized
overflow units; no runtime price is inferred. The paired synthetic audit
adds a finite-batch break-even estimate for a declared two-target-pressure
classifier class and does not estimate the unrestricted threshold.

The C2/C3 coefficient bridge is now explicit. The root-facet Hessian identity
expresses `j_(E,K)(r)` as weighted probability flux through Top-K switching
facets; the exact finite-batch admitted-mean contrast derivative is the same
root-facet coefficient multiplied by
`alpha_T(x)=Pr[Binomial(T-1,x)<C]`. The added 72-cell exact-binomial audit
covers `E={3,4,8}`, representative `K`, three pair ratios, and three batch
sizes. It matches the analytic requested/admitted slopes to maximum absolute
errors `9.59e-11` and `5.32e-9`, respectively, with exact-total capacities
and strict tail under-capacity in every cell. This closes the coefficient-
derivation and sensitivity-audit task; it does not connect the total number
of capacity-labeled arrangement signatures to a stronger `kappa_star` bound.

The literature check also verified that paid observations already have
active theory, including contextual-bandit regret with observation charges
and phase transitions ([Gong and Zhang, ICML 2026](https://proceedings.mlr.press/v306/gong26i.html)),
while adaptive decision-tree testing with paid tests is established
([Cicalese et al., ICML 2014](https://proceedings.mlr.press/v32/cicalese14.html)).
Accordingly, C2's candidate contribution remains the exact Top-K/capacity
family law, not a general paid-information framework. C3's multiple-braid
region count is known. Root-facet quadrature matched the independent
recurrence to `1.34e-16` in three `E=3,K=2` cells, and the 72-cell check
validates the finite-batch clipping attenuation composition. These checks do
not use C3's total capacity-signature count to sharpen the family value
bound. A new primary source also changes how the observation-cost premise
must be handled: Exact Quantile Balancing recovers a global MoE score-margin
quantile with two 256-bin all-reduces per layer, a communication volume
independent of token count ([Neitemeier et al., arXiv:2609.28053](https://arxiv.org/html/2609.28053)).
It has no capacity-clipped requested/admitted count model, so it does not
preempt the theorem; it does show that a marginal “extra collective” cost
cannot be assumed. The incremental cost must be measured against the selected
implementation's existing aggregation path.

**Decision remains unchanged:** the family theorem is mathematically proved
within its assumptions, but the top-conference contribution is not settled.
The fixed-instance value problem embeds exactly in costed adaptive testing;
the present work has not proved a class-level Top-K/gauge separation or
measured a real-system benefit and telemetry surcharge. The next gate is
therefore not another parameter sweep or another re-derivation of the C2/C3
coefficient. It is one independent-benchmark comparison of a genuinely
family-level quantitative claim, paired with a measured marginal signal cost
in a named router. If the benchmark reproduces the claim unchanged and the
named stack has no useful signal/value tradeoff, this contribution is not
supported as a top-conference paper in its present form; do not relabel the
same fixed-instance theorem as a general control limitation.

## C2 addendum: one-bit value-preserving signal (2026-10-18)

The existing C2 family now has a decision-specific signal-compression result:
in the symmetric two-world Gumbel-Top-K model, `Z=1{R_1>R_2}` exactly
preserves full-`R` Bayes value for the two target actions at every finite
batch size. Combining this with the proved all-pressure two-saturation gap
shows that one bit is asymptotically sufficient to recover the full-request
value, while zero additional bits are not. A task-loss break-even price for
this bit converges to the existing `v_*`; the price is not a hardware cost.

The frozen exact-count experiment used a held-out weight ratio `4/3`,
`E={3,5,7}`, all `K<E`, three batch sizes, and the existing one/two saturation
profiles. All 72 full-request and one-bit values matched; the bit strictly
improved on admitted-only value in all 36 two-saturation cells. Independent
exact-rational request-vector enumeration confirmed the likelihood-ratio
identity on 19 small cells. See
[`saturation_multiplicity_one_bit_value_theorem_2026-10-18.md`](saturation_multiplicity_one_bit_value_theorem_2026-10-18.md)
and
[`saturation_multiplicity_one_bit_experiment_results_2026-10-18.md`](saturation_multiplicity_one_bit_experiment_results_2026-10-18.md).

This is an integration result for C2, not a replacement research direction.
Binary likelihood-ratio compression is classical, and the fixed experiment
still has the exact adaptive-testing representation. The result does not
change the current top-conference no-go absent a benchmark-separating theorem
or measured system benefit.

### Admission-model correction from primary implementation documentation

Megatron-Core documents a capacity limit **per expert** and a `probs` policy
that retains the highest-probability routes within each expert. Under that
independent-capacity rule and without padding, the admitted count is still
exactly `A_e=min(R_e,C_e)`; the score policy changes which tokens survive,
not the per-expert count signal. The implementation selects at most `C_e`
indices per expert and intersects that mask with the routing map; padded map
entries must not be counted as dispatched tokens. See the official
[implementation](https://github.com/NVIDIA/Megatron-LM/blob/main/megatron/core/transformer/moe/moe_utils.py#L1003-L1035) and
[token-drop documentation](https://github.com/llm-jp/Megatron-LM/blob/main/megatron/core/transformer/moe/README.md#L271-L279),
[policy definitions](https://github.com/llm-jp/Megatron-LM/blob/main/megatron/core/transformer/moe/README.md#L391-L394).
Score-order-induced changes to admitted counts require a genuinely coupled
device/group budget and a separately specified admission kernel. The
professor report's score-biased-count mechanism therefore cannot be inferred
from the per-expert C2 model. The one-bit result measures payload size only;
it does not establish the communication cost of computing or reducing that
bit.

## C2 local-rank sharpening (2026-10-18)

The expected-admission Jacobian result now has an exact saturation-multiplicity
rank corollary. In requested-response coordinates, the local operator is
`P_0 diag(alpha)|_{1^perp}`. At finite batch size all attenuation factors are
positive, so the mean-response Jacobian retains full quotient rank. In the
strict-capacity limit, saturating `m>=1` coordinates leaves rank `E-m`: one
saturated coordinate causes no rank loss by conservation, and each additional
saturated coordinate removes one direction. The proof and scope are in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md).

The exact-expectation audit covers 36 cells (`E=4`, all `K<E`, three batch
sizes, and `m=0,1,2,3`). Every finite rank, limiting rank, and saturated-
subspace singular-value check passed; the largest analytic-versus-finite-
difference Jacobian error was `5.59e-10`. Results and raw data are in
[`saturation_rank_threshold_results_2026-10-18.md`](saturation_rank_threshold_results_2026-10-18.md)
and `results/saturation_rank_threshold_2026-10-18/`.

This sharpens the professor's C2 sensitivity statement but is still a local
mean-channel theorem. It does not establish finite-law non-identifiability,
closed-loop value, a class-level benchmark separation, or measured system
benefit. It therefore does not change the conference go/no-go gate above.

The main C2 decision-value theorem is now stated as one threshold result in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md): one persistently saturated expert per world gives exponentially vanishing requested-signal value; two swapped experts persistently saturated give positive limiting value, with the explicit small-skew coefficient `j_(E,K)(r_c)/K`. Its finite-batch proof covers every causal policy for the stated two-world, one-decision problem. This settles the **mathematical C2 statement under those assumptions**. It does not settle the paper-level novelty question: the result remains representable as an instance of the broader censored-testing benchmark, and no real-system benefit or marginal telemetry cost has been measured.

The independent benchmark audit in [`phase1_benchmark_gate_2026-10-16.md`](phase1_benchmark_gate_2026-10-16.md), Propositions 2–3, now makes the reduction explicit for the stochastic C2 experiment and proves that its first-order common-action value expansion is generic for smooth invertible choice maps. Thus the candidate Top-K content is the explicit Plackett–Luce coefficient and its scaling; whether that evaluation is novel and consequential remains unestablished. No new experiment sweep changes this benchmark conclusion.

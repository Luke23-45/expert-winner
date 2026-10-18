# Phase-1 research status and evidence ledger

**As of:** 2026-10-18
**Branch:** `feat/research-censored-feedback`
**Authority:** current status ledger for the exploratory Phase-1 documents. It does not supersede their proofs; it reconciles their claims and evidence levels.

## Decision in one paragraph

The fixed-instance control results are documented and should be frozen as
exploratory MoE applications. The canonical E-world Top-1 family also has a
proved one-step information-cost inequality under explicit assumptions, but
no result currently establishes a top-conference-level control limitation
against an independent benchmark. Every finite Top-K instance admits an
exact metric-constrained polyhedral active-testing simulation, so fixed-
instance value comparisons cannot provide that separation. The single
class-level attempt and its no-go verdict are in
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md).
The 2026-10-18 saturation-multiplicity theorem now proves a requested-signal
value transition for a parameterized standard-Gumbel Top-K family, and its
`E=3,K=2` member has an explicit rational all-pressure certificate and
finite-batch all-policy lower bound. This materially completes the C2
mathematical result within the declared family; it does not overturn the
benchmark/no-go conclusion stated above.
An exact two-sided comparison has also been established for the signed
expert-bias controller under canonical per-expert clipping. Admitted feedback
wins on the P2f family, while requested feedback wins on a strict-margin
uniform-capacity `E=8,K=2` family at `H=120` by 531 overflow assignments; a
separate heterogeneous witness gives a smaller gap at `H=34`. This is robust
non-dominance, not yet a predictive family-level criterion or benchmark
separation. A separate exact two-sided result now applies to the canonical
proportional pressure dynamics as written in `formal.md`: an `E=3,K=1` witness
has admitted overflow 18 versus requested 23 for every `eta>3`, while the
`E=8,K=2` witness has requested overflow 1,874 versus admitted 1,920 near
`eta=1`. This corrects the earlier status that treated the proportional
cross-check as one-directional.

The canonical proportional-controller line now also has Corollary T6c: for
balanced initial requests, uniform target, aggregate shortage, and a strict
capacity-order gap, requested feedback and no feedback stay at the aggregate
overflow floor, while admitted feedback exits that floor by the T6a
arrangement bound. An exact controlled audit checks this implication in 110
plants across 11 `(E,K)` cells. This strengthens the existing feedback
result; it does not change the finite-instance polyhedral benchmark
reduction. See
[`balanced_saturation_cost_theorem_2026-10-17.md`](balanced_saturation_cost_theorem_2026-10-17.md)
and
[`balanced_saturation_cost_experiment_results_2026-10-17.md`](balanced_saturation_cost_experiment_results_2026-10-17.md).

The arbitrary-fixed-`E,K` two-step expected-overflow theorem now has an
extension from Uniform affinities to any iid affinity law with a continuous,
strictly increasing CDF; the Uniform law retains its closed-form expression,
while general laws use an explicit one-dimensional inclusion-probability
integral. A paired controlled check covers Uniform, Gaussian, Logistic, and
Gumbel laws at `E=4`, all `K=1,2,3`, two batch sizes, and two displacements:
all 48 cell means and all 1,440 plant-level paired gaps are positive, and the
exact no-clipping controls pass. This strengthens the original-model theorem;
it does not change the class-level no-go because finite-instance outcome maps
still reproduce these values.


A further all-finite-horizon population theorem characterizes the same
admitted-pressure controller for this one-short, equal-rival-capacity family:
under a proved small-step condition its relative pressure converges to the
unique state where every expert's admitted fraction equals the short expert's
capacity, and its iterated long-run average overflow gap is `(E-1)r`. The
corrected static-batch experiment tracks the population cumulative prediction
closely through `H=64`: 119/126 registered nominal intervals cover it, and
aggregate means are within 0.2% at `H=64`. A paired fresh-batch study finds
smaller cumulative gaps than static reuse in 35/42 cells, while its cell means
remain close to the exact finite-`T` expected-field recurrence. Both runners
now implement the cumulative `q_next=Pi_g(q+eta*feedback)` update. A previous
runner version omitted `q` and its finite-batch report was invalid; the
superseding correction is documented in the results file. Neither study
proves fixed-`T` infinite-horizon convergence or a class-level benchmark
separation.

**Interpretation correction:** on this theorem's symmetric population
trajectory, only the short-capacity expert is saturated and all rivals are
below capacity. Since `sum_e R_e=K*T`, the admitted rival counts reconstruct
the short expert's request exactly. This one-short-family result is therefore
a controller-mismatch theorem, not an information-loss or requested-telemetry
necessity result. The separate two-saturated-expert theorem is the relevant
information-channel construction. See the explicit derivation in
[`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md).

A new one-step expected-field result remains inside the original per-expert
clipping model: for iid token affinities at fixed pressure,
`D E[A/(K*T)] = diag(alpha) Dp/K`, with
`alpha_e=Pr(Binomial(T-1,p_e)<C_e)`. It proves asymptotic mean-sensitivity
attenuation above capacity but explicitly does not claim finite-sample
non-identifiability. An exact `E=3,K=1` Gumbel witness has nonzero quotient
curl `-29/2187` under uniform exact-total capacities. The locked 72-cell exact
numerical audit matches analytic Jacobians to at most `2.38e-10`; all
symmetric and no-clipping controls pass. This is a precise bridge from the
professor's sensitivity suggestion to the existing formal model, not a
closed-loop value result or a novelty clearance. See
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md),
its [protocol](topk_expected_admission_jacobian_protocol_2026-10-17.md),
[results](topk_expected_admission_jacobian_results_2026-10-17.md), and
[`../../scripts/run_topk_expected_admission_jacobian.py`](../../scripts/run_topk_expected_admission_jacobian.py).

A controlled exact-expectation follow-up now checks the same theorem at
`E=4`, `K=1,2,3`, with Gumbel-Top-K routing and uniform exact-total
per-expert capacities. Across nine skewed/clipped cells the quotient curl is
nonzero; all 18 uniform-routing and no-clipping controls are zero. The
direct expected-field Jacobian matches the clipping chain rule to at most
`5.26e-10`. This extends the controlled mechanism check to `K>1`, but does
not strengthen the theorem's generality or establish a controller-value,
training-quality, or observation-cost result. See
[`topk_general_k_admission_curl_protocol_2026-10-17.md`](topk_general_k_admission_curl_protocol_2026-10-17.md),
[`topk_general_k_admission_curl_results_2026-10-17.md`](topk_general_k_admission_curl_results_2026-10-17.md),
and [`../../scripts/run_topk_general_k_admission_curl.py`](../../scripts/run_topk_general_k_admission_curl.py).

An exact algebraic corollary now characterizes the quotient-curl zero set for
the existing `E=3,K=1,T=6,C=(2,2,2)` iid-Gumbel instance: the curl is nonzero
exactly when all three request probabilities differ. The proof factors the
curl and bounds its symmetric factor strictly below zero, so the field has no
potential on any open region of the pressure quotient for this instance. A
deterministic exact-rational grid audit checked the factorization and zero-set
criterion at 37,579 interior points; reruns produced identical SHA-256
`4638236f879186605ee2ceb28a4143894c11e5d77c6991f2d2c9c7aab87879fc`.
This strengthens a structural statement already in the original stochastic
clipping/Top-K model. It does not show cyclic trajectories, worse overflow,
controller-value separation, or a top-conference novelty result. Details:
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md),
[`expected_admitted_curl_genericity_results_2026-10-17.md`](expected_admitted_curl_genericity_results_2026-10-17.md),
and [`../../scripts/audit_expected_admitted_generic_curl.py`](../../scripts/audit_expected_admitted_generic_curl.py).

The uniform-capacity random-facet theorem now has a directly aligned finite
audit: `E=4,K=2`, iid rational-grid affinities, uniform exact-total
capacities, and the theorem's `T^(-3/4)` candidate window. At `T=1,048,576`,
all 20 plants had the robust over/under pair, 18 had at least one regular
mismatched facet satisfying the proof's changed-row bound, and the paired
no-clipping control had zero mismatches. Across all 700 plants at the four
registered sizes, all 376 retained candidates were regular and mismatched.
This is finite-grid evidence for the construction, not proof of its
asymptotic probability or rate. It checks one data-selected cross-mean pair
per plant, not all directions or real-router prevalence. See
[`uniform_capacity_random_facet_protocol_2026-10-17.md`](uniform_capacity_random_facet_protocol_2026-10-17.md),
[`uniform_capacity_random_facet_results_2026-10-17.md`](uniform_capacity_random_facet_results_2026-10-17.md),
and [`../../scripts/audit_uniform_capacity_random_facets.py`](../../scripts/audit_uniform_capacity_random_facets.py).

## Claim ledger

| Claim / artifact | Evidence class | What is established | What it does not establish |
|---|---|---|---|
| Swapped-saturation requested/admitted value theorem | Analytic proof for standard-Gumbel Top-K, exact-total per-expert clipping, two swapped static worlds | For every `E>=3, 1<=K<E`, strict feasible margins give `V_A(T)-V_R(T) -> v_*(c)>0`; with one persistently capped expert per world, the signal-value gap instead vanishes exponentially. The corresponding abstract one-step purchase price has the same gap in overflow units. | Exact finite-size useful constants for arbitrary `(E,K,c)`; measured collective cost; controller windup; multi-round or independent-benchmark separation. See [`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md) and [`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md). |
| Explicit finite-batch Top-2 all-policy value gap | Analytic proof plus symbolic rational-algebra verifier; controlled paired simulation at three batch sizes | For `E=3,K=2`, weights `(2,1,1)/(1,2,1)`, and `c=(11/20,11/20,9/10)`, `27/200<=v_*<=459/3080`. The original Hoeffding bound is positive at `T=1680`; the sharper exact-binomial all-policy certificate is positive at `T=540` and exceeds `0.11389` at `T=1680`. The registered simulation remains at `T={1680,1800,3360}` and reproduces the finite-count/coupling quantities. | `v_*` is not solved exactly; no minimal positive threshold is claimed; simulated two-action values are not unrestricted values; no system price or novelty clearance. See [`topk_two_saturated_value_theorem_candidate_2026-10-17.md`](topk_two_saturated_value_theorem_candidate_2026-10-17.md) and [`top2_explicit_value_gap_experiment_results_2026-10-18.md`](top2_explicit_value_gap_experiment_results_2026-10-18.md). |
| E=3 probe-versus-wait theorem | Analytic proof, fixed two-world instance | Bounds for all causal randomized admitted policies, including the stated movement/probe costs and horizon condition; raw long-horizon gap scales as `1/β` for this instance | A Top-K-specific separation; the same induced state-constrained test model preserves the theorem and its values |
| T4a one-batch Top-K count-fiber theorem | Analytic proof using Gale–Ryser | With per-expert clipping, every count vector in the bounded fiber is Top-K-realizable at one fixed pressure when affinity matrices may vary; the fiber size is an exact bounded-composition coefficient | Realizability of the entire fiber under one fixed affinity batch as pressure varies; any multi-round root-arrangement or value result; novelty beyond generic clipping/active testing |
| T4b minimum exact signal for requested-update emulation | Analytic injectivity/counting proof plus exhaustive exact audit for `E=2,3,4,8,16,32` | On a fixed `(A,C)` fiber, distinct mass-conserving `R` vectors yield distinct next gauge states under requested feedback; a zero-error message reproducing that update needs at least `ceil(log2|F(A)|)` fixed-length bits; `P_0(J)` is sufficient; all listed Top-1 family checks pass | Minimum signal for an overflow-optimal/redesigned controller; communication latency or system cost; a new generic information-theory principle; a multi-round or family-level separation from adaptive testing |
| T4c unit-capacity Top-1 shortage family | Analytic corollary from T4a/T4b and stars-and-bars; exact enumeration for `E∈{2,3,4,8}`, `D∈{1,2,3,4}` | For `K=1`, `T=E+D`, `C=1`, `A=1`, exact zero-error requested-update message length is `ceil(log2 binomial(E+D-1,D))`; the new controlled audit enumerates 611 Top-1-realizable worlds in 16 groups and verifies the formula and injectivity for every world | Novelty of the generic composition-count/coding argument; physical telemetry cost; a performance-optimal signal; multi-round separation |
| Cost sensitivity on two exact Top-2 signal witnesses | Exact arithmetic from the existing P2f all-horizon theorem and uniform-capacity 120-step fixture | Under an explicitly hypothetical per-update surcharge `κ` measured in overflow-equivalent units, P2f admits no nonnegative break-even for requested feedback; the requested-better fixture beats all three fixed arms only for `κ<1/60` | Measured system cost, an optimal-policy value-of-information theorem, a predictive family criterion, or separation from the outcome-map benchmark; see [`costed_signal_two_witness_analysis_2026-10-17.md`](costed_signal_two_witness_analysis_2026-10-17.md) |
| Small-step E=3 analysis | Analytic proof plus parameterization | First-reachable-horizon gap is constant; distinct long-horizon raw gap grows as `1/β` under its stated horizon condition | Uniform positive normalized gap for arbitrary longer horizons; generality over E/K/capacity families |
| E-world pair-separation inequality (PS) and exact-identification corollary | Analytic family proof | For the canonical identical-block Top-1 family and `E_S ≤ C_sink < C − E_S/2`, every pressure's expected overflow lower-bounds `(L/2)Δ`, where `L=E_S+C−C_sink` and `Δ` is expected support reduction; telescoping gives cumulative overflow at least `L(N−1)/2` for policies required to identify all N worlds, tight under unrestricted singleton probing | Generality to arbitrary MoEs; the unconstrained finite-horizon overflow optimum; novelty against decision-tree/test-cost results |
| Costed one-shot requested observation on the E-world family | All-integer Bellman proof plus exact rational subset-probe audit | For `E_S=s`, `C_sink=C-s`, `C≥2s`, uniform prior, and unrestricted movement, admitted optimum after `h` rounds is `s·min(h,N−1)`; buying costs `s+κ`, skipping costs `s+s·min(h,N−1)`, so the optional value is `s+min(κ,s·min(h,N−1))` and `κ*=s·min(h,N−1)`. The audit covers 171 parameter cells, 29,583 DP values, and 8,892 exact buy/no-buy comparisons | Physical telemetry price; multi-round paid-observation policies; separation from generic membership testing/active testing; see [`eworld_costed_observation_value_theorem_2026-10-17.md`](eworld_costed_observation_value_theorem_2026-10-17.md) |
| Signed admitted-bias Top-1 theorems P2c–P2e | Analytic proofs in `formal_core.md`; exact integer audit for P2d over 4,800 capacity/horizon pairs | P2e gives the complete scalar dynamics and exact lattice criterion for reaching the capacity-optimal absorbing interval for every static two-expert Top-1 affinity batch; P2d gives an explicit parameterized family where admitted sign feedback beats requested sign feedback and no update in cumulative overflow; P2c gives a homogeneous-preference non-hitting counterexample | Generalization to E>2 or K>1; a class-level advantage over generic polyhedral/adaptive testing; trained-model or production benefit |
| P2f Top-2 signed-bias all-horizon comparison and perturbation audit | Analytic strict route-sequence proof for every row replication and gain `alpha in (1/5,11/40)`; exact-rational paired experiment on 100 perturbed plants, three replication factors, three gains, score/position drop-order controls, and a no-clipping control; exact-rational horizon audit through `H=100` | For the parameterized `E=3,K=2,T=20m,C=10m` family, admitted feedback enters global saturation at batch 3, requested feedback at batch 8, and no feedback not within nine batches. Exact nine-batch overflow is `93m`, `98m`, and `99m`; the analytic corollary proves admitted feedback strictly lower cumulative overflow than requested and no feedback for every `H≥4` (with stated exact/lower-bound gaps). Common score/gain scaling by `1/250` puts the compact test interval at `[0.0009,0.001]`; the base cutoff margin is `1/2500`, and entrywise perturbations of at most `1/250000` preserve a margin of at least `49/125000`. | A deliberately structured finite family, not a broad router population; no universal controller ranking, quality/deployment claim, uniform positive normalized gap, or separation from the finite-instance polyhedral benchmark. See `top2_signed_bias_separation_theorem_2026-10-17.md`, `top2_signed_bias_separation_protocol_2026-10-17.md`, `top2_signed_bias_separation_results_2026-10-17.md`, and `top2_all_horizon_results_2026-10-17.md` |
| P2f exact capacity-phase extension | Exact rational sweep over all integer `C=1,...,19`, three gains in the proved P2f interval, and all three feedback arms; exact repeated gauge-state cycle certificate for each of 171 cells, giving all-horizon costs and gap profiles; three-row replication scales every cost by `m` | The `C=10` strict admitted advantage is special: at `C=1` all signals tie in overflow; at `C=2,...,9` admitted and no-feedback attain the capacity lower bound while requested feedback has larger cycle-average overflow; at `C=11,...,13`, admitted/requested cycle averages tie but cumulative differences change sign **at the three registered gains**; at `C=14,...,19` request paths under admitted and requested feedback coincide for all three audited gains. At `C=11,...,18`, both feedback arms have higher eventual mean overflow than no feedback | Does not establish a general continuous-gain capacity phase diagram, generalize to other affinity families, or prove benchmark separation or model-quality benefit. The continuous refinement at `C=11,...,13` is separately recorded in the next row. See `p2f_exact_capacity_phase_experiment_2026-10-17.md` and `scripts/audit_p2f_capacity_phase.py` |
| P2f continuous-gain refinement at `C=11,...,13` | Exact rational partition of the full open gain interval at all closed-loop score crossings, plus exact simulation of every crossing point; exact repeated-state cycles on every open cell and singleton | Confirms that for this fixture admitted feedback never beats requested feedback in eventual mean at `C=11,12` (ties on some gain cells and is worse on the rest), ties requested feedback throughout at `C=13`, and is strictly worse than no feedback throughout all three capacities. At `C=11` admitted cycle means are `13` or `43/3`; at `C=12`, `23/2` or `61/5`; at `C=13`, `10`. Requested means are respectively `13`, `23/2`, and `10` throughout. | Exact continuation of one fixed affinity family, not a general gain/capacity theorem or benchmark separation. See `p2f_exact_capacity_phase_experiment_2026-10-17.md`, `scripts/audit_p2f_continuous_gain.py`, and the `continuous_gain_C*` JSON certificates |
| Two-sided signed-bias signal comparison | Exact constructive proof from P2f plus two requested-better Top-2 witnesses; exact-rational audits, including a 120-step uniform-capacity witness with strict-margin neighborhood, perturbations, and row replication | Under the same per-expert clipping and signed-bias controller class, neither requested nor admitted feedback universally minimizes finite-horizon overflow: P2f gives a strict admitted advantage for every `H≥4`; an `E=8,K=2,C=32` uniform-capacity family gives a requested advantage of `531m` at `H=120` under row replication `m≥1`; the smaller heterogeneous witness gives `2m` at `H=34` | Does not predict the ranking from general instance parameters, separate from the polyhedral testing benchmark, price telemetry, or establish trained-model benefit. See `bidirectional_bias_comparison_theorem_2026-10-17.md`, `bidirectional_bias_controlled_synthetic_experiment_2026-10-17.md`, `scripts/audit_uniform_cap_requested_better.py`, and `scripts/audit_bidirectional_bias_comparison.py` |
| Canonical proportional-pressure two-sided comparison | Exact rational constructive theorem with two strict-margin witnesses; exact step-size path certificates, open affinity neighborhoods, and replication checks | With uniform exact-total capacities and `delta=0`, the `E=3,K=1,T=3` plant gives admitted overflow 18 versus requested 23 for `H=12` and every `eta>3`; the `E=8,K=2,T=128` plant gives requested overflow 1,874 versus admitted 1,920 for `H=120` on an exact open interval around `eta=1`. Thus neither signal universally dominates the other in the canonical proportional model | Does not predict the winning signal from a new plant, beat no feedback in every witness, separate from the independent polyhedral-testing benchmark, price telemetry, or establish trained-model benefit. See `canonical_pressure_two_sided_comparison_2026-10-17.md`, `bidirectional_bias_controlled_synthetic_experiment_2026-10-17.md`, and both `audit_canonical_pressure_*` scripts |
| Arbitrary-fixed-`E` Top-1 two-step overflow theorem and controlled audit | Analytic asymptotic proof for every fixed `E>=2`; paired exact-grid experiment rerun byte-identically | With `K=1`, uniform target, zero leak, iid static uniform affinities, and one expert short by fraction `r`, admitted-minus-requested normalized expected two-step overflow tends to `d-d^E/E>0`, `d=eta*r<1`; the limit is independent of the split of remaining exact-total capacity. The experiment covers `E={3,4,8,16}`, three `d` values, three `T` values, 100 paired plants per `(E,T)`: all 3,600 paired gaps positive; all invariants and 3,600 no-clipping checks pass; output hashes reproduce | Does not prove `K>1`, arbitrary-policy superiority, finite-size convergence at the largest E (large deviations remain at `E=8,16`), physical telemetry cost, trained-model benefit, or separation from exact outcome-map testing. See `top1_e_expert_two_step_overflow_theorem_2026-10-17.md`, `top1_e_expert_overflow_protocol_2026-10-17.md`, and `top1_e_expert_overflow_results_2026-10-17.md` |
| Arbitrary-fixed-`E,K` Top-K two-step overflow theorem and affinity-law extension | Analytic asymptotic proof for every fixed `E>=2, 1<=K<E` under iid Uniform affinities, extended to iid laws with continuous strictly increasing CDF; paired controlled experiments rerun byte-identically | Under uniform target, zero leak, and one expert short by fraction `r`, the expected normalized two-step gap is `Phi_(E,K)(d)-K/E>0` for Uniform affinities, and `p_F(d)-K/E>0` for general `F`, where `d=eta*r/K<1` and `p_F(d)=integral G_(E,K)(F(x+d))dF(x)`. The original Uniform experiment covers `E={3,4,8}`, all `K`, three `d`, three `T`, and 50 paired plants per `(E,K,T)`: all 108 cell means positive; 5,399/5,400 individual pairs positive. The added distribution check covers four affinity laws, `E=4`, all `K`, two `T`, two `d`, and 30 paired plants per law/K/T: all 48 cell means and 1,440 individual gaps positive; all 1,440 no-clipping controls pass. | Does not establish accurate finite-size magnitude in every Uniform cell (only 69/108 nominal intervals cover that limit), `K=E`, arbitrary-policy superiority, physical telemetry cost, trained-model benefit, or separation from exact outcome-map testing. See `topk_e_expert_two_step_overflow_theorem_2026-10-17.md`, both `topk_*affinity*` protocol/results documents, and the corresponding runner scripts. |
| Two-world, two-saturated-expert information/control theorem | Exact integer-weight enumeration of full request/admitted laws plus paired multinomial controlled study (20,000 first-batch samples/world/T; T=40,80,160,320,640); rerun at `eta=15 log(2)` | Along `p0=(.4,.4,.2)`, `p1=(.5,.3,.2)`, and `C/T=(.25,.25,.5)`, exact `TV(R)` rises .5263→.9958 while exact `TV(A)` falls .1804→.0022; requested/admitted equal-prior Bayes errors approach 0 and .5, respectively. Theorem 2 gives asymptotic fixed-update costs `1/6` and `.18266432` versus admitted `.20400314`; Theorem 3 optimizes over all one-step gauge-fixed pressures and gives exact asymptotic Bayes values `V_R→0`, `V_A→1/32`, hence a signal value gap `1/32` in normalized overflow units; full finite-law evaluation lower-bounds the optimal gap by `.018498060` at `T=320` and `.029782371` at `T=640`. The finite study shows a crossover: admitted feedback has significantly lower overflow at T=40,80; requested wins in both worlds by T=320,640; at T=160 one cell is tied within uncertainty. | This is a fixed Top-1 multinomial family and generic clipping mechanism; finite-T admitted laws remain distinguishable; no universal controller/windup theorem, Top-K-specific separation from censored-testing theory or B1-out, system cost, trained-model benefit, or novelty clearance. See `two_saturated_expert_information_and_control_theorem_2026-10-17.md`, `two_saturated_expert_indistinguishability_results_2026-10-17.md`, and `scripts/run_two_saturated_expert_indistinguishability.py` |
| Long-run population overflow under admitted Top-K feedback | Analytic scalar-recurrence proof for every fixed `E>=2, 1<=K<E` under iid affinities with positive bounded density and the stated capacity profile; corrected paired static-batch experiment and separate paired fresh-batch experiment | For every fixed `H`, the `T->infinity` expected cumulative gap equals `sum_(n<H)(P_F(x_n)-K/E)`; its iterated long-run average is `(E-1)r>0`. With the corrected cumulative update, static-batch aggregate means track the prediction through `H=64` (119/126 intervals cover; aggregate ratio .998 at H=64). Fresh batches are closer than static reuse to the finite-`T` mean recurrence in mean absolute error (.0175 vs .0400) but have wider cell intervals; fresh-minus-static is negative in 35/42 paired cells. Only the short-capacity expert is saturated on the symmetric population trajectory, so conservation reconstructs its request from the admitted rivals; this is controller mismatch, not information loss. | Neither experiment proves fixed-`T` infinite-horizon convergence, a nonasymptotic joint bound, universal signal dominance, measured observation cost, model-quality benefit, or separation from exact outcome-map testing. The earlier finite-batch report used an incorrect reset update and is superseded. See theorem, protocol, corrected results, fresh-batch protocol/results, and runners. |
| Capacity-slack factorial extension of the long-run theorem | Paired controlled synthetic sweep over `E={4,8}`, all `K<E`, three affinity laws, two shortage magnitudes, two batch sizes, static/fresh regimes, eight replicates, and six horizons; exact invariants and population recurrence evaluated cellwise | 11,520 plant-horizon rows and 1,440 cells; all 61,440 no-clipping round controls pass, zero ties. In static cells, every mean is positive for `H>=2`, aggregate gaps track the finite-horizon population recurrence within 0.4–1.8% through `H=32`, and 559/600 per-cell intervals cover the prediction for `H>=2`. Fresh cells are positive by `H>=4`, but the `E=8,K=7`, Gumbel, low-shortage cell has a significant negative gap at `H=2`, opposite the population prediction. | Expands finite-grid robustness only; does not change the theorem's iterated limit, imply the asymptotic slope is reached by `H=32`, establish fixed-`T` infinite-horizon behavior, or separate from censored decision theory. This one-short profile remains reconstructible from admitted counts and mass conservation. See [`topk_capacity_slack_factorial_protocol_2026-10-18.md`](topk_capacity_slack_factorial_protocol_2026-10-18.md), [`topk_capacity_slack_factorial_results_2026-10-18.md`](topk_capacity_slack_factorial_results_2026-10-18.md), and the runner/merger. |
| E-world unrestricted action reduction | Analytic family proof | For the stated E-world family without movement constraints, pressure actions are weakly dominated by subset probes with the same information partition and no greater worldwise cost; gives a finite subset Bellman recursion | Exact reduction under finite movement budgets, except the separately stated fixed-representative/high-movement cases |
| E=4 arrangement and support checks | Exact rational finite audit | Enumerates the documented finite signatures/maps/supports and checks the claimed finite-instance inequalities/certificates | Proof for continuous pressures at arbitrary E or parameters; independent validation of every analytic proof step |
| Random planted-facet mismatch under heterogeneous capacity slack | Exact finite multinomial formula, bivariate-CLT limit, and cross-mean LLN corollary; controlled audit at `E=4`, `K=1,2,3`, `T=32,64,128`, four square-root slack pairs plus exact-total cross-mean profiles, 5,000 replicates/cell | The asymptotic non-potentiality probability is `Φ(z_i)+Φ(z_j)−2Φ₂(z_i,z_j;−1/(E−1))`; when the two limiting capacities straddle `K/E`, mismatch tends to one. All 45 Monte Carlo cells were within 5 standard errors of their exact finite probabilities | Uniform sampling of facets from complete arrangements; production prevalence; closed-loop performance or benchmark separation; novelty of the standard Gaussian/LLN calculations. See `random_facet_nonpotentiality_theorem_2026-10-17.md`, `heterogeneous_facet_slack_results_2026-10-17.md`, and `scripts/run_heterogeneous_facet_slack_audit.py` |
| T6c signed admitted-bias finite saturation-exit theorem | Analytic bound from Top-K score-slope separation; exact-rational audit on the base plant and 20 entrywise-perturbed plants at three gains | For a static plant, each globally saturated episode has constant admitted sign slope. A strict gap at the Top-K slope boundary implies exit by the explicit score-margin bound. Base example exits at state 500 against bound 501; all 60 perturbation/gain cells exit within their computed bounds | No exit guarantee when the slope gap condition fails; no bound on repeated episodes or total bias; exit can produce poor routing; no universal cost ranking or separation from the finite-instance polyhedral benchmark. See `signed_bias_saturation_exit_theorem_2026-10-17.md`, `signed_bias_saturation_exit_results_2026-10-17.md`, and `scripts/audit_signed_bias_saturation_exit.py` |
| E=4 full-pressure values for H=3/H=4 and high movement H≥4 | Analytic finite-instance proof with exact finite Bellman certificate | The values and movement thresholds stated in the dated full-pressure note | Values for all H and all movement radii; a benchmark separation |
| E=3/E=4 grid Bellman output | Finite-grid diagnostic | Behavior on the listed grids; useful for discovering candidate policies/cells | Continuous-state optimum or theorem; grids can omit narrow useful regions |
| Phase-1 pytest suite | Behavioral checks, sampled-grid diagnostics, and selected helper-consistency checks | Concrete routing, admission, reachability, and sampled-grid behavior are exercised; weak tautological and arithmetic-only placeholders identified in review were removed or replaced | The suite has not been run after this cleanup and does not verify the analytic theorems; sampled grids do not certify continuous pressure space, and newer PS/long-horizon/continuous E=4 results are not covered by theorem-verification tests |
| Exact-rational audit scripts | Finite-instance research audit | Enumerate the documented E=4 arrangement/support cases and compute exact rational outputs | They print violations/results rather than acting as fail-fast CI theorem verifiers; their finite scope does not certify the general proof |
| B0/B1 benchmark results | Formal reduction and construction | B0 contains each fixed instance; B1 exactly simulates every finite static-affinity Top-K experiment through its pressure metric, arrangement labels, clipping, and loss | A useful universal theorem for an independently constrained family of root arrangements; B1 is intentionally broad |
| B1-out extension for coupled admission | Exact arrangement representation proof | A fixed finite Top-K instance with raw-affinity-ranked per-expert or shared-device admission is exactly simulable by a finite polyhedral outcome map while preserving the metric, information histories, and overflow costs | Any family-level theorem beyond general polyhedral active testing; nonlinear cross-token drop rankings without a separate boundary proof |
| Synthetic routing runs (v1/v2/v3) | Reproducible synthetic experiments, separate from Phase-1 theorem audits | Behavior of the specified synthetic harness and controllers under the reported seeds/settings | Real-router prevalence, trained-model quality, deployment benefit, or proof of the Phase-1 lower bound |
| Admission-geometry pilot (20 paired seeds, 120 steps/arm) | Controlled synthetic mechanism experiment; exact control assertions plus finite seeded trajectories | Per-expert score-ranked vs position-ranked admission has identical count-feedback trajectories; globally saturated uniform per-expert admitted-sign feedback freezes; an exact two-token Top-1 case changes `A` at fixed `R` under a shared device slot; the declared grouped-capacity abstraction produces drop-rule-dependent outcomes | General windup; production prevalence; trained-model quality; a Top-K advantage over the active-testing benchmark |
| Capacity-regime sweep (20 paired score perturbations; `C=24,28,32,36`; 120 updates/arm) | Controlled synthetic mechanism experiment with six exact invariants; post-hoc exact rational replay of all three `C=28` arms against the float64 CSV; corrected cumulative audit removes duplicate score/position rows | At `C=24`, admitted feedback freezes; at `C=28`, admitted feedback reaches absorbing global saturation in all 20 seeds and has lower `H=120` cumulative overflow than requested and no feedback in every seed; its exact paired advantage persists in an entrywise affinity neighborhood around each seed plant. At `C=32,36`, admitted feedback has higher cumulative overflow than no feedback in all 20 seeds; per-expert score-vs-position invariance and saturated-set bias-gap invariance hold. Exact replay shows the 20 seeds share the request path through state 75, first change at 76, then have distinct paths and reach global saturation at states 77--84. Corrected audit shows requested feedback at `C=32` has lower cumulative overflow in 3/20 seeds (the previous duplicated-row diagnostic incorrectly said 0/20). | General benefit outside this fixed ring plant; a universal winner among feedback signals; trained-model quality; a family-level theorem or novelty over adaptive testing. See `capacity_regime_sweep_results_2026-10-17.md`, `scripts/audit_capacity28_all_signal_replay.py`, `scripts/audit_capacity_sweep_cumulative.py`, and `scripts/audit_capacity28_exact_replay.py` |
| T6a/T6b proportional-controller exit theorems and exact audit (20 paired rational perturbations) | Analytic proofs plus exact-rational finite implementation audit; T6b was derived after the T6a protocol run | T6a gives global arrangement bound `N_sep`; T6b refines it using a maximum-slope expert's capacity slack and token exit-order statistics. In the registered plant, all 20 runs exit at state 9; `N_sep=30` while the post-run T6b bound is 9. Requested-feedback exit is 11; no feedback remains frozen | Overflow/performance advantage; population or trained-model effect; family-level separation from polyhedral adaptive testing; conference-level novelty on its own |
| T6b varied-plant diagnostic (100 exact `E=4,K=2,T=8` plants) | Post-run deterministic exact-rational property audit; not preregistered and not a proof | Observed exit `<= N_e* <= N_sep` in all 100 generated plants; the T6b bound is tight in 92 | No inference to larger routers or workload populations; no novelty separation or model-quality result |
| Admitted-field cyclic-monotonicity counterexamples | Two exact-rational Top-1 constructions and fail-fast scripts; fixed affinity batches, strict quotient states, and exact replication families for `E=3` and `E=4` | For every integer `m>=1`, the `E=3,K=1,T=3m,C=(m,m,m)` family has admitted cyclic sum `2m/3` (constant `2/9` per token); the `E=4,K=1,T=4m,C=(m,m,m,m)` family has admitted cyclic sum `733m/2000` (constant `733/8000` per token). Both have `sum(C)=KT`, uniform targets, and strict routes robust to a nonzero affinity perturbation radius. Requested-field cycle sums are negative in both witnesses | Constructed Top-1 families only: no divergence, worse overflow theorem, general `E,K` classification, or benchmark separation. See `admitted_feedback_noncyclicity_2026-10-17.md` and `admitted_feedback_noncyclicity_e4_2026-10-17.md` |
| Admitted-field facet criterion and E=4 Top-2 ensemble audit | Analytic regular-facet characterization including simultaneous same-pair exchanges; exact-rational local audits on a seeded paired synthetic ensemble | At a regular facet where `m` routes exchange `i -> j`, the admitted jump is `P0(d_i e_i-d_j e_j)`, where `d_i=min(R_i^-,C_i)-min(R_i^--m,C_i)` and `d_j=min(R_j^-+m,C_j)-min(R_j^-,C_j)`. For `E>=3`, a continuous cellwise-affine potential exists on open cells exactly when `d_i=d_j` at every regular facet; any mismatch rules out a convex subgradient potential. In 40 generated `E=4,K=2,T=12` plants, 4,944 paired sampled facets were checked across four capacity profiles; no-clipping matched 1,236/1,236, while exact-total uniform, exact-total heterogeneous, and shortage profiles had 928/1,236, 802/1,236, and 427/1,236 mismatches respectively, each with an exact local circulation witness | Sampled facets only, not complete arrangement enumeration or router prevalence; no closed-loop performance consequence, trained-model benefit, or separation from a benchmark reproducing the same outcome map. See `admitted_field_facet_criterion_2026-10-17.md`, `admitted_facet_ensemble_experiment_2026-10-17.md`, and `scripts/run_admission_facet_ensemble.py` |
| Facet-to-trajectory bridge experiment | Protocol fixed before run; exact-rational 120-step paired trajectories on the same 40 `E=4,K=2,T=12` plants as the sampled-facet audit | No-clipping R/A trajectories are identical; for the canonical proportional pressure law, mean cumulative overflow (requested/admitted/none) is `201.8/232.45/321` under uniform exact-total capacity and `700.9/874.3/816` under heterogeneous exact-total capacity; requested and admitted costs tie on all 40 aggregate-shortage plants. Geometry-mismatch vs. admitted-minus-requested overflow Spearman correlations are `-0.243` and `-0.284` for the two exact-total profiles | These sampled facet mismatch rates do not predict the trajectory cost in a strong or causal sense; one small integer-affinity generator, one gain/initial state/horizon, and no population inference, training, measured telemetry cost, or benchmark separation. It also uses proportional pressure, not the distinct signed-bias controller. See `facet_to_trajectory_bridge_protocol_2026-10-17.md`, `facet_to_trajectory_bridge_results_2026-10-17.md`, and `scripts/run_facet_trajectory_bridge.py` |
| Common-prefix rejected-load route-divergence identity and audit | Analytic recurrence plus exact-rational check across 160 paired plant/capacity runs; post-hoc cost join | While requested/admitted routes agree, pairwise pressure separation equals the discounted cumulative difference in rejected-load coordinates. Every observed first split has a nonpositive requested selected/unselected Top-K margin witness. Split by state 119: 0/40 no-clipping, 28/40 uniform exact-total, 38/40 heterogeneous exact-total, 34/40 aggregate-shortage. In the shortage case, all 34 route-split plants still have identical 120-step overflow because the aggregate shortage is fixed whenever all experts are saturated | Route divergence alone does not determine overflow ranking or Top-K-specific benchmark separation. The cost join is post-hoc, on the same small generator and fixed controller parameters. The identity is a prefix theorem, not a post-split value theorem. See `rejected_load_route_divergence_identity_2026-10-17.md`, `rejected_load_route_divergence_results_2026-10-17.md`, and `scripts/audit_rejected_load_first_divergence.py` |
| Planted-facet exact mismatch probability under exchangeable Top-K | Finite exact multinomial probability theorem plus bivariate-CLT limit; route-level Monte Carlo check | For a planted regular `i -> j` facet with uniform exact-total `C=KT/E`, and `T-1` independent exchangeable continuous-score tokens, `p_{E,K,T}=Pr[1{X_i<C} != 1{X_j<C}]` has an exact four-category multinomial sum. For fixed `E>=3,K`, as feasible `T` grows, it tends to `arccos(-1/(E-1))/pi`, independent of `K`; for `E=4` the limit is `0.60817345`. The count-unit expected squared tangential jump tends to `0.15204336` at `E=4`. The `E=4`, `K=1,2,3`, `T=8,16,32,64,128` simulation matched the exact probabilities within 2.14 Monte Carlo standard errors at worst | Conditional planted-facet law only, not uniformly sampled full-router facets; multinomial/CLT tools are standard, and this is not a performance theorem or novelty clearance. See `random_facet_nonpotentiality_theorem_2026-10-17.md`, `admitted_random_facet_probability_experiment_2026-10-17.md`, and `scripts/run_random_facet_mismatch_probability.py` |
| Paired E=4 Top-2 facet-family dynamics audit | Exact-rational controlled synthetic trajectories; 40 shared affinity plants, three feedback arms, four capacity profiles, 80 updates | No-clipping requested/admitted trajectories are identical at all steps. On exact-total uniform capacities, admitted feedback has mean cumulative overflow 13.35 above requested (20 worse, 18 ties, 2 better); on exact-total heterogeneous capacities, 93.575 above (36 worse, 4 ties); under aggregate shortage, their cumulative overflow ties on all 40 seeds. The ordering therefore depends on the capacity regime and is not universal | One small integer-affinity generator, one gain, one initial pressure and fixed horizon; outcome experiment does not prove non-cyclicality causes the ranking, establish a general controller winner, price telemetry, or defeat the finite-instance outcome-map reduction. See `admitted_facet_dynamics_experiment_2026-10-17.md` and `scripts/run_admission_facet_dynamics.py` |
| High-probability global non-potentiality under macroscopic capacity heterogeneity | Analytic corollary combining the regular-facet criterion with a law-of-large-numbers argument under one deliberately planted regular Top-K facet | For fixed `E>=3`, `K<E`, exact-total capacities with `C_e(T)/T -> c_e` and nonuniform limit, choose `c_i<K/E<c_j`; at the planted `i -> j` facet the source/destination admitted changes mismatch with probability tending to one, so the full admitted field is non-potential with probability tending to one. Exact finite cross-mean audit: 9 `E=4` cells all match the theorem and MC check; complete E3 arrangements separately have mismatches in all 40 plants | The distinguished token in the asymptotic theorem is constructed, not drawn from an unconditioned router population; no closed-loop consequence, cost/value gap, or separation from the outcome-map benchmark. See `random_facet_nonpotentiality_theorem_2026-10-17.md`, `heterogeneous_facet_slack_results_2026-10-17.md`, and `full_arrangement_facet_audit_results_2026-10-17.md` |
| Unconditioned iid-affinity high-probability facet theorem and many-facet corollary | Analytic proof with explicit failure bounds plus two preregistered exact-rational-grid audits | Under iid continuous affinities and any fixed nonuniform exact-total capacity limit, the admitted field is non-potential with probability tending to one. The strengthening proves that at least `b_EK*sqrt(T)/2` distinct regular candidate facets have mismatched admitted changes, except with probability at most `exp(-b_EK sqrt(T)/8)+(4/3)sqrt(T)exp(-Delta^2*T/8)` for all sufficiently large `T`, where `b_EK=(1/3)binom(E-2,K-1)(5/12)^(E-2)` and `Delta=min(K/E-c_i,c_j-K/E)>0`. In the fixed `E=4,K=2` audit, 500 plants per `T in {64,256,1024,4096}` had mean mismatched-facet counts `1.334,2.726,5.332,10.664`, respectively; every retained candidate facet mismatched, no-clipping mismatches were zero, and 497/500 plants met the integerized theorem threshold at `T=4096`. The deterministic rerun matched the same summary hash | The audits use a finite affinity grid and a proof-defined candidate rule; they do not sample all facets uniformly or estimate the fraction of all facets that mismatch. Structural non-potentiality still gives no closed-loop cost gap, observation break-even, training benefit, or separation from the finite-outcome benchmark. See `random_facet_nonpotentiality_theorem_2026-10-17.md`, `many_facet_random_affinity_protocol_2026-10-17.md`, and `many_facet_random_affinity_results_2026-10-17.md` |
| Stochastic expected admitted-field curl under Top-1 Gumbel routing | Exact binomial sensitivity identity and exact finite-rational evaluation | Under iid Top-1 Gumbel routing, `D_q E[A/T]=diag(alpha)D_q pi`, with `alpha_e=P(Binomial(T-1,pi_e)<C_e)`. For `pi=(1/2,3/10,1/5)` and exact-total heterogeneous capacity fractions `(2/5,1/2,1/10)`, the tangent curl converges to `-9 gamma/(100 lambda)`. Exact finite evaluations at `T=10,20,50,100,200,500` are nonzero and approach the limit; the no-clipping control is exactly zero | Stochastic Top-1/Gumbel model only; clipping attenuation itself is generic, and no controller-value gap, telemetry cost, real-router gain, or separation from B1-out is proved. For positive capacities, the finite law of `A_e` still identifies its request probability via `P(A_e=0)=(1-pi_e)^T`; the result is sensitivity loss, not exact finite-law non-identifiability. See `expected_admitted_curl_theorem_2026-10-17.md` and `expected_admitted_curl_results_2026-10-17.md` |
| Full-arrangement E3 Top-1 facet audit | Preregistered exact-rational enumeration of every regular route-changing segment in each complete pressure arrangement; 40 paired iid rational plants | For each plant, all 108 route-changing facets were enumerated. Under uniform exact-total capacity, 3,096/4,320 pooled facets mismatch (43/60), with at least one mismatch in all 40 plants; under heterogeneous exact-total capacity, 3,127/4,320 mismatch, again in all 40. No-clipping has 0/4,320 mismatches. Every mismatch has a nonzero tangential jump; exact rerun SHA matches | Small `E=3,K=1,T=6` declared generator only; not a probability theorem, full-workload prevalence estimate, closed-loop consequence, or benchmark separation. See `full_arrangement_facet_audit_protocol_2026-10-17.md`, `full_arrangement_facet_audit_results_2026-10-17.md`, and `scripts/audit_full_arrangement_facets.py` |
| Non-cyclic field trajectory follow-up | Exact-rational deterministic audit; paired requested/admitted arms across four witness initial states and four step sizes, 100 updates per arm | At `eta=1/10`, admitted has higher cumulative overflow from all four initial states; at `eta=1/2`, ordering varies by initial state; at `eta=1,2`, admitted has higher overflow from all four. All 32 trajectories are tie-free. This confirms that potential geometry alone does not fix performance ordering | One plant and four initial states/step sizes; not a seed-based population study, convergence theorem, or controller ranking. See `admitted_noncyclicity_trajectory_results_2026-10-17.md` |
| Fixed-family one-update delay theorem | Analytic state recursion plus exact-rational audit of all 36 routing inequalities | In the `E=3,K=1` plant from `q0=(0,2,3)`, for every `eta in (7/100,21/200)`, requested feedback reaches zero overflow after two saturated steps and admitted feedback after three. Exact replication gives cumulative overflow `2m` versus `3m` for `T=3m`, `C=(m,m,m)` | One fixed affinity family and initial state; not a minimax statement over admitted policies, a general `E,K` theorem, or a benchmark separation. See `closed_loop_admission_delay_theorem_2026-10-17.md` and `scripts/audit_closed_loop_admission_delay.py` |
| Robust fixed-family delay corollary and paired perturbation audit | Exact uniform margin argument plus exact-rational experiment: 100 affinity perturbations, 4 row-replication factors, 3 step sizes, requested/admitted/no-feedback, score/position retention, and a no-clipping control | On `eta in [2/25,1/10]`, all 36 baseline route inequalities have minimum margin `1/300`; entrywise affinity perturbations of at most `1/1200` preserve every route with margin at least `1/600`. All 1,200 paired cells reproduced balance at step 2 vs 3 and cumulative overflow `2m` vs `3m`; score/position count paths and dropless requested/admitted paths matched exactly | The same fixed `E=3,K=1` family, not a sample of routers; no arbitrary-`E,K` theorem, policy optimality, model-quality result, or separation from the finite-instance polyhedral benchmark. See `closed_loop_delay_robustness_protocol_2026-10-17.md`, `closed_loop_delay_robustness_results_2026-10-17.md`, and `scripts/run_robust_delay_experiment.py` |
| Professor-report mechanism/source audit | DeepSeek-V2 primary text plus Megatron-Core source pinned to `36731ac`; exact admission-count identity and call-order audit | DeepSeek-V2 has device-level score-ranked dropping but defines balancing signals from router selections; Megatron applies per-expert dropping before accumulating `local_tokens_per_expert` for its expert-bias update, so its configured capacity+bias path uses admitted counts with `A=min(R,C)`; B1-out represents the fixed raw-affinity-ranked device-cap instance exactly | That V2 uses admitted-count control; that score-ranked per-expert drops change `A`; a marginal requested-telemetry cost or family-level advantage over B1-out |
| Literature notes / 100-entry file | Preliminary annotated scan plus selected primary-text checks | Identified relevant neighbors and explicit reduction risks; the 100-entry document distinguishes 55 search-supported citations from 45 standard references | Systematic-review completeness, exhaustive novelty, or reproducibility of the whole search protocol |

## Addendum: arbitrary-capacity Top-1 mirror equilibrium

A broader population theorem now treats every positive exact-total
heterogeneous capacity vector for canonical Top-1 Gumbel routing. In
probability coordinates, the admitted pressure update is exactly entropic
mirror descent on the convex potential
`W(p)=sum_e integral_0^{p_e} min(s,c_e) ds`. Relative smoothness with respect
to negative entropy yields a global `O(1/N)` objective-gap bound for
`0<eta<1`. The minimizer set has every admitted fraction equal to the
minimum capacity fraction `c_min`, and its equilibrium overflow exceeds the
requested uniform-target overflow by at least `1/E-c_min` for every
nonuniform profile. This explains why nonzero Euclidean curl in pressure
coordinates does not rule out a mirror potential in probability
coordinates.

The controlled audit covers 288 heterogeneous capacity profiles, three
step sizes, 1,024 population updates per step size, and 4,096 fresh finite
batches at each predicted equilibrium. The mirror-step identity, one-step
inequality, objective bound, equilibrium identities, and batch mass
controls all pass. The related potential-game and KL mirror-descent tools
are established prior art; novelty is limited to the exact MoE clipping
specialization and overflow consequence. This still does not defeat the
fixed-instance polyhedral-testing reduction or establish a telemetry-cost
or model-quality gain. See
[`top1_arbitrary_capacity_mirror_equilibrium_theorem_2026-10-17.md`](top1_arbitrary_capacity_mirror_equilibrium_theorem_2026-10-17.md),
its protocol/results documents, and the runner.

## Addendum: multi-low-capacity population extension

A new theorem extends the one-short-expert population result to `m` equally
low-capacity experts and `E-m` equally high-capacity experts, for every
feasible `1<=m<E` and `1<=K<E`. Under the canonical hard Top-K router,
per-expert clipping, uniform target, proportional pressure update, and iid
continuous positive bounded affinity density, the two-group pressure
trajectory obeys an explicit scalar recurrence. The admitted-minus-requested
population overflow gap converges to `(E-m)r` per round. This includes
`m<K`, where high experts retain nonzero selection probability at
equilibrium.

The controlled static-batch Gumbel audit covers all 32 feasible grid points
for `E in {4,6}`, every `K`, and low-group sizes `m`, over three batch sizes,
12 paired plants per cell, and `H<=32`. All exact controls pass; at `H=32`
all 1,152 paired plants have positive admitted-minus-requested cumulative
overflow, and a second full run reproduces both runner and data hashes. This
strengthens the canonical population-theorem line, but remains one symmetric
capacity family and one specified controller. It does not overcome the
fixed-instance polyhedral active-testing reduction or establish a
top-conference novelty claim. Full proof, protocol, results, and artifacts
are in [`topk_multilow_population_overflow_theorem_2026-10-17.md`](topk_multilow_population_overflow_theorem_2026-10-17.md),
[`topk_multilow_population_overflow_protocol_2026-10-17.md`](topk_multilow_population_overflow_protocol_2026-10-17.md),
and [`topk_multilow_population_overflow_results_2026-10-17.md`](topk_multilow_population_overflow_results_2026-10-17.md).

## Open, invalidated, and uncomputed items

- **Open research claim:** a quantitative family-level result beyond the
  exact polyhedral active-testing representation. The class-level attempt
  did not establish one. P2c–P2e add an exact two-expert Top-1 signed-bias
  characterization and counterexamples, but their finite threshold maps
  transfer unchanged to the independent testing benchmark. The current
  decision remains no-go for the general control-limitation claim.
- **Open fixed-instance calculations:** E=4 values for \(H\ge5\) and
  \(\beta\le1/\sqrt2\), plus continuous-pressure finite-movement details
  outside the proved regimes. These are optional application calculations,
  not the active novelty gate.
- **Invalidated as phrased:** the proposed T7 hidden-overflow-compounding
  paired-world argument. See
  [`phase1_t7_trajectory_audit_2026-10-16.md`](phase1_t7_trajectory_audit_2026-10-16.md).
- **Conjectural / not established:** Markov-switching extensions and a
  minimum-sufficient-signal theorem for optimizing control. T4b establishes
  only the minimum zero-error signal for emulating one next requested-feedback
  gauge update over a fixed clipping fiber.
- **Not run:** broad theorem-family sweeps, trained-model experiments, or
  real-router trace collection. The admission-geometry pilot, four-capacity
  signed-bias sweep, exact-rational T6a/T6b proportional-controller audit,
  and post-run T6b varied-plant diagnostic are
  distinct experiments; their controls and limitations are documented in
  [`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md),
  [`capacity_regime_sweep_results_2026-10-17.md`](capacity_regime_sweep_results_2026-10-17.md),
  and [`admitted_phantom_exit_results_2026-10-17.md`](admitted_phantom_exit_results_2026-10-17.md).

## Addendum: request reconstruction and target correction

**Proved:** if at most one admitted coordinate is at capacity, mass
conservation and the known capacity vector recover the entire request vector
exactly. Therefore the earlier one-short uniform-target overflow gap is not
an information-theoretic request-versus-admitted gap in that family.

**Population result:** under the already-formalized capacity-relative update
`P_0((R-C)/(K*T))`, the one-short symmetric iid family converges to its
capacity proportions with zero long-run population overflow. An
admitted-only controller that reconstructs requests follows the same path
on every fixed finite horizon with probability tending to one. The exact
statement and proof are in
[`single_saturation_signal_reconstruction_theorem_2026-10-17.md`](single_saturation_signal_reconstruction_theorem_2026-10-17.md).

**Controlled evidence:** the `E=4,K=1` standard-Gumbel experiment used 100
paired static plants, `T=2304,9216`, and eight steps. All plants remained in
the one-saturated regime; reconstructed admitted and requested
capacity-relative trajectories matched exactly. Cumulative overflow per
token was approximately `0.496` for those two arms, compared with `1.00`
for requested uniform-target and `1.64` for admitted uniform-target. Direct
admitted capacity-relative updates gave `0.81`. Full paired results and
hashes are in
[`capacity_relative_reconstruction_experiment_results_2026-10-17.md`](capacity_relative_reconstruction_experiment_results_2026-10-17.md).

**Interpretation:** this is a concrete correction to the professor
candidate's broad telemetry-value argument. It identifies a regime where
there is no signal loss, and it shows why the target must be matched to the
heterogeneous capacities. It does not resolve the multiple-saturated case,
prove a universal controller result, measure system cost, or pass the
outcome-map benchmark gate. The top-conference novelty question therefore
remains open; this result does not justify claiming it is solved.

## Status corrections to older notes

1. [`phase1_g3_steering_2026-10-16.md`](phase1_g3_steering_2026-10-16.md)
   has a stale opening status. The small-step parameterization and separate
   long-horizon probe-versus-wait theorem are no longer open. The remaining
   issue is not that theorem's proof; it is the lack of a result beyond its
   exact constrained-testing representation.
2. [`phase1_parameterized_small_b_2026-10-16.md`](phase1_parameterized_small_b_2026-10-16.md)
   must distinguish the constant first-reachable-horizon gap from the
   `1/β` raw long-horizon gap. Both are now described in §4; neither is a
   benchmark separation.
3. [`phase1_full_pressure_cell_dp_gate_2026-10-17.md`](phase1_full_pressure_cell_dp_gate_2026-10-17.md)
   documents valid fixed-instance open values, but its old numbered
   “research gate” is superseded. Filling H≥5 small-movement entries is not
   the current novelty gate.
4. [`conference_roadmap.md`](conference_roadmap.md) is now the concise
   current decision source; its earlier phase sequence and “literature lane
   is ours” framing are retired.

## Literature-method qualification

The file [`phase1_100paper_survey_2026-10-16.md`](phase1_100paper_survey_2026-10-16.md)
does not preserve exact query strings, search dates per query, screening
rules, or an inclusion/exclusion log. It must therefore be described as a
**preliminary annotated scan**, not a systematic survey. The 55/45 reference
count is bibliographic bookkeeping, not an estimate of field coverage.

Selected primary-source boundaries relevant to the reduction attack:

- Cicalese, Laber, and Saettler study decision trees optimizing worst and
  expected testing cost and use pair-separation reasoning:
  [PMLR paper](https://proceedings.mlr.press/v32/cicalese14.pdf).
- Saettler, Laber, and Cicalese explicitly study outcome/value-dependent
  test costs in decision trees:
  [Information Processing Letters / DOI](https://doi.org/10.1016/j.ipl.2015.02.006).
- Atanasov et al. study active M-ary hypothesis testing with sensor-motion
  costs and belief-state planning:
  [ICRA 2013 paper](https://natanaso.github.io/ref/Atanasov_Sankaran_ActiveObjectRecognition_ICRA13.pdf).
- Gupta, Nagarajan, and Ravi study optimal decision trees and adaptive TSP;
  their adaptive-TSP formulation explicitly models switching costs between
  tests in a metric space:
  [Mathematics of Operations Research (2017)](https://doi.org/10.1287/moor.2016.0831).
- Papadopoulos et al. analyze invariant sets and limit cycles for a
  quantized discrete-time integrator used in computing systems. This is a
  close control-theory neighbor for the lattice and two-cycle behavior in
  P2c–P2e, although its quantization/disturbance model and objective differ
  from Top-1 capacity admission:
  [arXiv:1701.07482](https://arxiv.org/abs/1701.07482).
- Loss-Free Balancing already uses an expert-wise additive bias updated by
  `sign(mean_count − expert_count)` from preceding-batch assignment counts.
  Thus the signed controller in P2a–P2e is established controller prior art;
  the candidate result is only about its interaction with capacity-clipped
  counts and Top-1 threshold geometry:
  [Wang et al., arXiv:2408.15664](https://arxiv.org/abs/2408.15664).
- Kiselev analyzes adaptive softmax MoE load dynamics via a two-expert
  reinforcement/decay mean-field ODE, derives its scalar gradient potential,
  and proves pitchfork/fold regimes with hysteresis. This makes generic
  claims about feedback-induced MoE bifurcation, hysteresis, or potential
  dynamics unsafe. The model uses smooth softmax probabilities without the
  hard Top-K plus per-expert clipping map studied here:
  [Kiselev, arXiv:2605.29121](https://arxiv.org/abs/2605.29121).
- $\phi$-Balancing is a direct convex-potential MoE neighbor: its formal
  objective is a strictly convex symmetric potential applied to the
  population-mean routing-probability vector, with an EMA/mirror-descent
  construction ([ICML 2026 paper](https://proceedings.mlr.press/v306/chen26br.html),
  [full paper PDF](https://l-z-chen.github.io/img_pdf/MoE_ICML2026.pdf),
  §§2.1 and 3.1, equations 3–12). The present facet theorem instead studies
  when a fixed-batch hard Top-$K$ field after per-expert clipping,
  $P_0(KT\mu-A(q))$, is or is not a convex subgradient. This is a precise
  model/objective distinction, not evidence that the theorem is novel; the
  overlap in convex-potential framing requires discussion and broader review.

These sources are close model components, not identical formulations of our
overflow objective. The quantized-integrator paper makes lattice/limit-cycle
analysis unsafe as a novelty claim by itself; Loss-Free Balancing makes the
signed bias controller itself prior art. The adaptive-TSP result adds
another established movement/switching-cost neighbor. They make generic
pair-separation, outcome-dependent test cost, or moving-test Bellman structure
unsafe as novelty claims by themselves. The comparison is a scoped
primary-source check, not an exhaustive review.

## What can be said now

- **Safe:** “We prove exact results for specified MoE routing plants and
  identify their exact adaptive-testing representations.”
- **Safe with scope:** “For a canonical parameterized Top-1 family, pressure
  actions obey a proved overflow-versus-information inequality.” State the
  family and assumptions every time.
- **Safe with scope:** “Under the canonical proportional pressure update,
  an iid continuous Top-1 family with one expert under-capacitated by fraction
  `r` has a two-step expected overflow gap `d - d^3/3` between admitted and
  requested feedback, where `d=ηr<1`; the limit is independent of the exact
  split of the remaining capacity across the other two experts.” The theorem
  and two exact-grid controlled experiments are documented in
  `heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`,
  `heterogeneous_capacity_two_step_results_2026-10-17.md`, and
  `heterogeneous_capacity_family_results_2026-10-17.md`. This is a
  parameterized two-step family theorem, not a universal controller ranking
  or a class-level benchmark separation.
- **Safe with scope:** “For every fixed `E>=2` and `1<=K<E`, under the
  stated proportional-pressure, exact-total-capacity family, the two-step
  asymptotic overflow gap is positive for iid affinities from any continuous,
  strictly increasing CDF: it equals `p_F(eta*r/K)-K/E`, with `p_F` given by
  the Top-K inclusion integral.” The Uniform case has the closed form already
  recorded in the theorem. This remains a two-step family result, not a
  universal ranking, cost theorem, or benchmark separation. See
  `topk_e_expert_two_step_overflow_theorem_2026-10-17.md` and the non-Uniform
  affinity protocol/results.
- **Safe with scope:** “Over a fixed clipping fiber, exact emulation of the
  requested controller's next gauge update requires identifying the request
  vector; the minimum message alphabet has size `|F(A)|`.” This is a
  one-step zero-error statement, not an overflow-optimal telemetry claim.
- **Safe with scope:** “For a static Top-K plant with a simple score
  arrangement, a mismatched source/destination admission transition at a
  regular facet rules out a convex potential for admitted feedback; matching
  every such transition is sufficient for a convex piecewise-affine potential
  on the open cells.” This is a structural potential criterion, not a
  performance or benchmark-separation theorem.
- **Safe with scope:** “For one explicit parameterized, replicated
  `E=3,K=2` family and nine-batch horizon, the existing signed admitted-bias
  update has lower overflow than the same requested-count update and no
  update.” The exact totals are `93m/98m/99m`; this is a family result for
  that affinity pattern, not a universal ranking or a benchmark separation.
- **Not supported:** “Admitted feedback has a new general control-theoretic
  limitation,” “the censoring lane is unoccupied,” or “the current results
  establish top-conference novelty.”
- **Not supported empirically:** claims about trained-model quality or how
  often a real router operates in the modeled telemetry regime.

No test suite was run after the test cleanup. The two-step theorem proof was
strengthened to handle the dependence created by reusing the same affinity
matrix at both routing steps; paired exact-grid experiments were rerun
deterministically, with byte-identical summary and plant-level files. Recent
research audits include
the T6a/T6b exact-rational work, T4b minimal-signal family audit, admitted
non-cyclicality checks, the regular-facet obstruction check, and the exact
closed-loop delay audit. None is a trained-model or real-router experiment;
the closed-loop theorem remains a fixed Top-1 family result and not a
benchmark separation.

## Addendum: finite-batch two-saturation value bound

The general two-saturated Top-1/Gumbel theorem now has a corrected,
reproducible controlled experiment. The theorem was clarified to distinguish
its population-overflow value from the canonical realized finite-batch
overflow. A Jensen/coupling corollary now gives a finite-batch value-gap lower
bound against every admitted one-step policy, and an exact upper bound from a
registered requested threshold policy; both use normalized realized overflow
on an independent fresh batch. See
[`two_saturated_general_value_theorem_2026-10-17.md`](two_saturated_general_value_theorem_2026-10-17.md).

The corrected count-law audit covers `E={3,4,8}`, three skew levels, two
batch sizes, and 2,000 paired replications per cell. It retains the canonical
`A=min(R,C)` map, has zero failures of the registered saturation event, and
has identical admitted vectors in all 36,000 common-tail coupled draws. The
finite-batch optimal value gap is certified positive by the theorem bounds in
17/18 cells; the remaining lower bound is negative and inconclusive. One
invalid initial execution was discarded after detecting that the sampler
omitted the pair-probability category; the fixed sampler and all outputs are
recorded in
[`two_saturated_general_value_results_2026-10-17.md`](two_saturated_general_value_results_2026-10-17.md).

This advances the professor's requested/admitted value analysis within the
original per-expert clipping model. It is still Top-1, one-step, and a
two-world application of censored Bayesian testing. It does not prove a
multi-round Top-K/gauge separation from the broader adaptive-testing
benchmark, a measured collective break-even, or model-level benefit; the
top-conference gate remains open.

## Addendum: Top-2 multi-saturation extension attempt

A controlled `E=3,K=2` Gumbel-Top-2 pilot now studies the same two-saturated
signal-value mechanism under the canonical `A=min(R,C)` map and pressure
action. It uses worlds with initial inclusion vectors
`(5/6,7/12,7/12)` and `(7/12,5/6,7/12)`, exact-total capacities
`(11/20,11/20,9/10)`, and 1,500 paired draws across three batch sizes.
Clipped admitted vectors were equal in 1,498/1,500 pairs at `T=1,800` and
all pairs at the two larger sizes; requested classification had zero errors;
the no-clipping request vectors were never equal. Exact target pressures,
the no-feedback risk, and the fixed-action cost are reported separately.
See the [protocol](topk_multisaturated_value_protocol_2026-10-17.md) and
[results](topk_multisaturated_value_results_2026-10-17.md).

The proof candidate now includes a quotient-level strict-convexity and
inverse-gradient argument and establishes a **strictly positive**, but not
yet explicitly lower-bounded, one-step expected-overflow value gap against
every common pressure action in this Top-2 family. It also proves the exact
interval `0 < v_* <= 459/3080`; a bounded numerical search attained the upper
endpoint, but did not prove equality. The lemma still needs independent
technical review, and an explicit lower bound or global optimization proof
is still required before promotion to the formal core. This is a Top-2
extension attempt; it does not
establish arbitrary-`K` generality, benchmark separation, real-system cost,
or model-quality gains. See
[`topk_two_saturated_value_theorem_candidate_2026-10-17.md`](topk_two_saturated_value_theorem_candidate_2026-10-17.md).

## Addendum: general finite-capacity curl result and exact scale audit

The professor-aligned expected-admission sensitivity result now has an
analytic extension beyond the single `(T,C)=(6,2)` witness. For three
experts, Top-1 Gumbel routing, common capacity `1<=C<T`, and any batch size
`T>=2`, the expected admitted feedback field has nonzero quotient curl on a
dense open subset of pressure space and has no scalar potential on any
nonempty open set. The proof reduces the curl to a determinant built from
`g(p)=p Pr[Binomial(T-1,p)<C]`; its boundary limit is
`y(1-y)(alpha(y)-alpha(1-y))`, which is nonzero because the binomial CDF
`alpha` is strictly decreasing. No-clipping (`C=T`) and symmetric-pressure
cases remain exact zero-curl controls. The theorem is in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md).

The locked exact synthetic audit covers 30 exact-total cells `T=3C`, from
`(3,1)` through `(90,30)`, at a fixed skewed request vector. All 30 curls
were nonzero with the same sign; all 30 symmetry controls and all 30
no-clipping controls were exactly zero; all 30 expert-swap checks reversed
the sign. Two runs produced byte-identical results. This validates the
registered calculations, while the general open-set statement rests on the
proof, not the finite grid. Protocol, executable, and hashes are in
[`top1_curl_capacity_scaling_protocol_2026-10-17.md`](top1_curl_capacity_scaling_protocol_2026-10-17.md),
[`run_top1_curl_capacity_scaling.py`](../../scripts/run_top1_curl_capacity_scaling.py),
and [`top1_curl_capacity_scaling_results_2026-10-17.md`](top1_curl_capacity_scaling_results_2026-10-17.md).

This strengthens the structural result in the original clipping model. It
does not close the separate class-level benchmark reduction or establish
closed-loop performance, real-system cost, model-quality benefit, or
top-conference novelty.

## Addendum: coordinate-aware potential for admitted feedback

A further geometric check materially qualifies the pressure-coordinate curl
result. Under the unchanged `A_e=min(R_e,C_e)` model and fresh iid batches,
the expected admitted error is the gradient of a separable convex objective
in the Top-K one-token inclusion vector. Its coordinate curvature is the
exact clipping attenuation
`Pr[Binomial(T-1,p_e)<C_e]/K`. With zero leak, the formal pressure update
`q_next=Pi_g(q+eta*gamma*epsilon_A)` is exactly mirror descent on that
objective under the convex conjugate of the Top-K random-utility surplus;
for Top-1 Gumbel it is ordinary entropy mirror descent. Therefore the
previous nonzero-curl theorem remains true in Euclidean pressure coordinates,
but it must not be interpreted as absence of a potential for the dynamics,
as instability, or as evidence of cycles. The exact identity and proof are
in
[`capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md`](capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md).

The exact synthetic audit covered 162 Top-1 cells across batch sizes,
uniform and heterogeneous capacities, target choices, and step sizes. The
pressure implementation and entropy mirror update agreed with maximum
probability error zero; common-shift gauge error was at most `1.33e-15`.
The run reproduced byte-for-byte. This audit is an implementation check,
not a convergence or model-quality experiment. Its protocol, executable,
and results are in
[`capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md`](capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md),
[`run_capacity_clipped_mirror_descent_audit.py`](../../scripts/run_capacity_clipped_mirror_descent_audit.py),
and [`capacity_clipped_topk_mirror_descent_results_2026-10-17.md`](capacity_clipped_topk_mirror_descent_results_2026-10-17.md).

This is a necessary framing correction. Because `phi`-Balancing already
develops convex objectives and mirror descent over expected MoE routing
distributions, this identity alone does not establish novelty. Any paper
claim must isolate the clipped-capacity-specific objective or a consequence
that prior potential-based balancing results do not already imply.

## Addendum: arbitrary-Top-K two-world signal-value theorem and controlled audit

The earlier `E=3,K=2` two-saturated value candidate has now been extended to
an arbitrary-`E,K` family. The construction swaps two favored expert scores,
sets equal exact-total caps below both swapped experts' request rates, and
sets every other cap above its unchanged request rate. A random-utility
surplus homeomorphism proves that no single pressure can match the capacity
target in both worlds, giving an implicit but strictly positive population
common-action value `v_*>0`. A coupling bound makes the full admitted-count
laws converge in total variation, while a requested-count sign test
identifies the world. The resulting one-step finite-batch bounds and all
assumptions are recorded in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md).

The preregistered-style controlled audit covers 33 `(E,K,T)` cells for
`E={3,4,6,8}`, three `K` values per `E`, and 2,000 paired first-batch draws
per cell from exact Plackett-Luce subset laws. World 1 is generated by
swapping the first two request counts. The admitted pair matched in 70.05%–
100% of draws across the grid, versus 0%–10.5% with clipping disabled. At
the largest tested batch size in each `(E,K)` family, requested-classifier
error was 0%–6.825%, admitted-classifier error 49.2%–50.0%, and requested
classifier expected overflow was lower in all 11 families. Target actions
were solved to residual at most `8.25e-13`; an independent exact ordered-
prefix enumeration matched the subset dynamic program for every registered
`(E,K)` pair. The paired raw draws reproduced byte-for-byte after the
post-run analysis was added. That analysis proves the sign rules are Bayes-
optimal from the full `R` and full `A` signals, respectively, for this
equal-outside-weight family; therefore they are minimum-overflow decisions
within the two target-pressure actions in all 33 cells. Exact values are
reported alongside the simulation; the requested action has lower exact
expected overflow in all 33 cells, with minimum gap `0.00081113` at
`(E,K,T)=(3,1,16)`. This does not optimize over all pressures, estimate
`v_*`, or measure hardware cost. See the [protocol](topk_swapped_saturation_value_protocol_2026-10-17.md),
[results](topk_swapped_saturation_value_results_2026-10-17.md),
[Bayes analysis](topk_swapped_saturation_bayes_value_analysis_2026-10-17.md),
and [`run_topk_swapped_saturation_value.py`](../../scripts/run_topk_swapped_saturation_value.py).

Combining the arbitrary-Top-K finite-batch theorem with the exact Top-1
constant gives an all-policy one-step limit for the latter family:
`V_A(T)->1/36`, `V_R(T)->0`, and `V_A(T)-V_R(T)->1/36`, with unrestricted
pressure actions for the next fresh batch. This closes the asymptotic
optimal-value statement for the exact Top-1 instance family; it does not
extend to multi-round control or escape the exact generic censored-decision
reduction. The corollary is recorded in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md).

The exact reduction attack is also complete: at every finite `T`, the
theorem is a member of the general two-state censored Bayesian experiment
class with finite request/alarm alphabets, the same clipping channel, and
the same action losses. It therefore does not establish a control-theoretic
separation from generic active testing. The targeted literature check
records Kumar–Mouchtaki's censored-news-vendor result and the relevant MoE
systems boundaries in
[`topk_swapped_saturation_literature_boundary_2026-10-17.md`](topk_swapped_saturation_literature_boundary_2026-10-17.md);
the formal reduction is in
[`topk_swapped_saturation_reduction_attack_2026-10-17.md`](topk_swapped_saturation_reduction_attack_2026-10-17.md).

**Decision:** keep this as the strongest current arbitrary-Top-K
signal-value theorem, not as a finalized top-conference claim. The proof has
now been given an explicit facet-curvature lower bound on a rational
subfamily; its computed constants are too small to make the finite-batch
guarantee positive at practical batch sizes. The numerical evaluation is not
interval-certified. The controlled experiment is not real-system evidence,
and the generic active-testing reduction absorbs the one-step value
statement. The unresolved top-conference requirement is a quantitative
Top-K-specific consequence that survives that benchmark, or a measured
system result using the marginal cost of replacing versus adding
requested-count telemetry. Do not infer an extra collective cost: on the
pinned Megatron path, the existing bias update already reduces a count
vector. Do not reinterpret score-ranked per-expert drops as a different
count observation: they preserve `A=min(R,C)`.

The explicit-bound derivation, assumptions, and limitations are recorded in
[`topk_swapped_saturation_explicit_gap_bound_2026-10-17.md`](topk_swapped_saturation_explicit_gap_bound_2026-10-17.md).
Its deterministic diagnostic is
[`audit_topk_swapped_saturation_explicit_bound.py`](../../scripts/audit_topk_swapped_saturation_explicit_bound.py),
with output in
[`summary.json`](../../results/topk_swapped_saturation_explicit_bound/summary.json).

### Exact common-action value for a Top-1 family

A sharper result now replaces the facet-bound constant for a designated
Top-1 family: for every `E>=3`, a three-category aggregation plus a
four-region algebraic certificate proves the exact common-action value
`v_*=1/36`. The lower bound uses total-variation contraction under
aggregation; a symmetric pressure attains equality in the full E-expert
system. The full proof is in
[`top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md`](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md).

The controlled synthetic audit covers 18 cells (`E={3,4,8,16,32,64}`, three
batch sizes, 2,000 paired draws per cell). At the largest batch in every E
cell, the requested-count sign classifier has lower expected next-batch
overflow than the admitted-count sign classifier by more than twice the sum
of their Monte Carlo standard errors; admitted coupled vectors become equal
in 87%–100% of draws. See the [protocol](top1_arbitrary_e_exact_swapped_value_protocol_2026-10-17.md),
[results](top1_arbitrary_e_exact_swapped_value_results_2026-10-17.md), and
[runner](../../scripts/run_top1_arbitrary_e_exact_swapped_value.py). The
four sign-region polynomial identities and equality action pass an exact
symbolic check in
[`verify_top1_arbitrary_e_value_algebra.py`](../../scripts/verify_top1_arbitrary_e_value_algebra.py).

This exact value theorem is stronger than the previous implicit-constant
statement for its Top-1 family, but it remains a one-step two-world
censored-decision result. The generic adaptive-testing reduction still
applies; the experiment does not measure systems cost or establish the
top-conference novelty gate. Substituting `1/36` into the finite-batch
coupling bound gives an explicit all-policy value-gap inequality. Jensen's
inequality removes the population-to-finite loss penalty from the admitted
lower bound; the requested upper bound uses the exact target-action binomial
overflow and the exact error of the requested-count sign classifier. This
replaces the earlier, looser Chernoff term. The bound is negative at every
batch in the controlled run; a double-precision scan finds positive values
from `T=704` at `E=3` to `T=8,556` at `E=64`. These numerical thresholds are
not interval-certified. The registered-classifier experiment must not be
described as verifying a positive all-policy finite-batch guarantee.
The separate paired synthetic check at the first-positive thresholds and at
twice those batch sizes is recorded in
[`top1_exact_gap_threshold_experiment_results_2026-10-18.md`](top1_exact_gap_threshold_experiment_results_2026-10-18.md).
All six cells passed the routing/clipping controls and classifier Monte
Carlo checks. This validates the signal and coupling calculations; the
all-policy conclusion still comes from the proof, not from simulation.

### Exact Bayes characterization of the registered Top-1 experiment

The sign rules used in the arbitrary-E Top-1 controlled experiment have
now been characterized exactly. Under the uniform two-world prior,
`R_1-R_2` is sufficient for the Bayes decision from the full request vector;
the sign of `A_1-A_2` is also Bayes-optimal from the full admitted vector.
The latter follows because equal first-two capacities make each clipping
fiber either sign-preserving or invariant under swapping the first two
counts. For the two registered target-pressure actions, the rules are also
minimum-overflow decisions in every registered cell because the wrong-target
action has strictly greater expected overflow.

Exact binomial sums now report the no-signal and two-signal policy values,
without Monte Carlo error, for the registered 18-cell experiment. At the
largest tested batch, the requested-versus-admitted exact overflow gap grows
from `0.00445` (`E=3`) to `0.02501` (`E=64`). This closes the concern that
the experiment compared an optimal requested decision with a deliberately
weak admitted heuristic **within this two-action class**. It does not
optimize over all pressures, remove the generic censored-testing reduction,
or establish a top-conference contribution. The proof and exact table are
in [`top1_arbitrary_e_bayes_value_analysis_2026-10-17.md`](top1_arbitrary_e_bayes_value_analysis_2026-10-17.md);
the exact-rational small-batch audit is
[`verify_top1_bayes_observation_value.py`](../../scripts/verify_top1_bayes_observation_value.py).

### Decision-theoretic constraint on the signal comparison

Under the canonical observation map `A=min(R,C)`, an unrestricted `R`
observer can compute `A` and reproduce any `A`-causal policy. Therefore,
without a differential observation cost or an explicit policy-class
restriction, the optimal requested-observation value cannot be worse than
the optimal admitted-observation value. This is the standard Blackwell
ordering applied to the project's deterministic clipping map, not a novel
MoE theorem. It explains why the Top-2 direct-update result (where one
specific update rule does better on `A`) does not contradict the optimal
signal-value comparison. A costed signal comparison is meaningful only
after its marginal implementation cost is defined. The proof and research
boundary are recorded in
[`feedback_information_dominance_and_costed_value_2026-10-17.md`](feedback_information_dominance_and_costed_value_2026-10-17.md).

### 2026-10-18: capacity-matched target check

The existing one-short-capacity population theorem was extended without
changing its router, clipping rule, or proportional controller: replace the
uniform target by `mu=C/(K*T)`. Under the explicit gain bound, both requested
and admitted population recurrences converge monotonically to the unique
pressure at which requests equal capacities, with overflow tending to zero.
The locked paired experiment ran the four signal-by-target arms plus
no-feedback for `E=4`, `K={1,2,3}`, two batch sizes, 12 seeds, seven horizons,
and static/fresh affinity regimes. All invariants and no-clipping controls
passed, with zero ties and byte-identical rerun artifacts.

At the largest fresh-batch cells (`T=9216,H=64`), capacity-target admitted
feedback reduced cumulative overflow relative to no feedback in every paired
seed, but its cumulative overflow remained above capacity-target requested
feedback. For the capacity-target finite-`T` mean recurrence, interval
coverage was 62/84 cells at `T=9216`; the population-limit cumulative
magnitudes are not uniformly validated at this finite horizon. This supports
the target-mismatch diagnosis in this constructed family; it does not
establish a signal-information theorem, hardware cost, trained-model gain, or
the benchmark separation required for a top-conference novelty claim. See
[`capacity_matched_target_theorem_2026-10-18.md`](capacity_matched_target_theorem_2026-10-18.md),
its [locked protocol](capacity_matched_target_experiment_protocol_2026-10-18.md),
and [results](capacity_matched_target_experiment_results_2026-10-18.md).

### 2026-10-18: multi-low target factorial and C3 literature audit

The same target-by-signal population theorem was checked for `E=4,K=2` and
`m={1,2,3}` low-capacity experts in a second locked paired experiment. It
covered two batch sizes, 12 seeds, static/fresh batches, four signal-target
arms, no-feedback, and horizons through 64. All mass/clipping/no-clipping
controls passed and no ties occurred. Requested feedback had lower cumulative
overflow than admitted feedback for all 72 registered `(m,T,regime,H>=2)`
cells in all 12/12 paired seeds under both targets. Capacity-target admitted
feedback also beat no feedback at each `H>=2`; the arms have identical initial
cost at `H=1`. Population-magnitude mismatch remains material at 64 steps,
especially for requested feedback, and is reported. See
[`capacity_matched_multiplicity_experiment_results_2026-10-18.md`](capacity_matched_multiplicity_experiment_results_2026-10-18.md).

The C3 search found an exact prior for the general score-arrangement region
count. A batch of `T` token score-tie systems is a union of `T` translated
type-A braid arrangements; with independent affinity coordinates having
density, the translations are generic almost surely. Delcroix-Oger et al.,
Theorem 2.21 of *Cellular Diagonals of Permutahedra*, enumerate the regions
exactly ([arXiv:2308.12119](https://arxiv.org/abs/2308.12119)). The full
request and admitted signatures are coarsenings of these ranking regions.
Consequently, the earlier forest-polynomial bound is valid but weaker than
the known region count. A capacity-labeled coarsening may still be distinct,
but no quantitative overflow/value consequence of it is currently proved.

**Current theorem gate unchanged:** these results complete additional
same-model claims and their synthetic checks. They do not deliver the
professor report's integrated C2/C3 theorem (explicit information value as a
function of capacity slack, `E,K`, plus a defensible marginal observation
price), nor a Top-K-specific result beyond the independent costed-testing
benchmark. The top-conference central theorem remains unsettled.

## Update: symmetric Top-2 small-skew theorem and audit (2026-10-18)

On the existing C2 line, the saturation-multiplicity theorem now has an
explicit pair-skew coefficient for symmetric pair-target capacities for
every `E>=3` and `1<=K<E`, as a finite sum over ordered Plackett-Luce
prefixes. It also has an all-policy finite-batch inequality and a joint
capacity-margin/skew/batch limit. The proof and assumptions are in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md).
The controlled numerical audit is in
[`topk_small_skew_scaling_experiment_2026-10-18.md`](topk_small_skew_scaling_experiment_2026-10-18.md),
with a fixed-seed runner and raw CSVs.

The `E=3,K=2` exact derivatives were independently checked symbolically. The
general prefix-sum sensitivity was checked in 81 cells (`E=3,...,8`, all
`K<E`, three pair ratios) against central differences, with maximum relative
error `7.45e-9`. Across 24 population optimizer cells, the value-per-skew
numerical error decreased quadratically as skew was halved; finite-batch
paired draws showed the requested sign becoming informative while mirrored
admitted vectors aliased under the declared coupling. This supports, but
does not prove, the analytic claims. Differential evolution is not a global
certificate, and Monte Carlo is not the proof of the all-policy bound.

The result answers the professor's C2 request for an explicit capacity- and
`(E,K)`-dependent value coefficient within the symmetric pair-skew family. It does
**not** settle the top-conference central theorem: fixed instances still
reduce exactly to costed censored testing; a useful Top-K-specific
class-level consequence beyond that benchmark has not been proved; and the
marginal cost of obtaining requested counts has not been measured. The
remaining task is still the same C2/C3 theorem gate, not a new research
direction.

## Reproduced mechanism-pilot analysis (2026-10-18)

The existing 20-seed static admission-geometry pilot was rerun from a temporary
directory; its summary and trajectory CSV matched the archived artifacts
byte-for-byte. A new analysis script verified per-expert clipping, route-mass
accounting, the score/position count-invariance control, and the dropless
`R=A` control. In the per-expert-cap arm, requested-sign feedback increased
120-step cumulative drops by 187.9 on average versus both admitted feedback
and no update (paired 95% t interval `[159.98,215.82]`, positive in all 20
seeded perturbations); its time-averaged request-count imbalance also
increased. The admitted/no-update arms remained at the aggregate overflow
floor. This is a counterexample to a blanket requested-signal advantage for
that controller and cost, not a population claim. In the separate constructed
group-capacity hybrid, score-ranked versus position-ranked dropping changed
cumulative overflow only under admitted feedback; this does not reproduce
DeepSeek-V2 or Megatron-Core. Full limits and paired tables are recorded in
[`professor_report1_reconciliation_and_experiment.md`](professor_report1_reconciliation_and_experiment.md)
and machine-readable output is in
[`../../results/admission_geometry/analysis_summary.json`](../../results/admission_geometry/analysis_summary.json).
This experiment does not alter the C2 result or the independent-benchmark
no-go.

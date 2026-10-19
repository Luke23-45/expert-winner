# Real-workload benchmark protocol for requested versus admitted MoE feedback

**Status:** research protocol for implementation and preregistration; no real-data result is claimed here.
**Implementation status:** planning only; the clean-room v1 code has not been started.
**Repository branch inspected:** `feat/control-experiment-v3-utmost`.
**Related implementation:** [`experiments/megatron_feedback/README.md`](../../../experiments/megatron_feedback/README.md), [`protocol.yaml`](../../../experiments/megatron_feedback/protocol.yaml), `run_matrix.py`, `adapter.py`, and `analyze.py`.
**Formal mechanism:** [`central_theorem.md`](../../notes/central_theorem.md).
**Protocol version:** 1.0, 2026-10-19.

This protocol converts the project's saturation mechanism into two linked empirical studies: a real-router observation/replay study and a controlled real-data training study. It specifies what each study can establish, how to compare methods fairly, and what evidence is required before making a practical claim. It is a plan, not evidence that the planned experiments have run or succeeded.

## 1. Research question and claim boundary

The central mathematical result is conditional: with uniform capacities and target, per-expert clipping, and all experts saturated under aggregate shortage, admitted counts contain no relative load-error signal. With zero pressure decay, the formal gauge-pressure controller cannot change relative pressure. Requested counts retain the centered request imbalance. The theorem is an exact statement about that model and its specified update.

The real-workload question is:

> In a real Top-(K) MoE router that drops tokens at per-expert capacity, how often does saturation censor the request-allocation signal, and what are the effects of controlling with pre-drop requests versus post-drop admissions on routing, language-model quality, and system cost?

The benchmark must keep four claims distinct:

1. **Mechanism prevalence:** whether the theorem's conditions occur in naturally configured real workloads.
2. **Controller effect:** whether changing only the observed count signal changes routing or training outcomes in a specified MoE implementation.
3. **System effect:** whether any quality/load benefit is worth the measurement and runtime cost in that implementation.
4. **Theory novelty:** whether the mathematical result gives something beyond the costed censored/adaptive-testing benchmark. Experiments cannot settle this comparison by themselves.

Do not infer universal superiority of requested feedback, deployment unobservability, or lower total overflow from the freeze theorem. Under persistent global saturation, total overflow is fixed by aggregate capacity shortage; the possible effect is on its distribution and on subsequent routing state.

## 2. Keep the formal controller and Megatron controller separate

This is a load-bearing experimental distinction.

The formal note uses the gauge update

\[
q^+=\Pi_g\big((1-\delta)q+\eta\gamma\,\varepsilon\big),
\qquad s_{t,e}=a_{t,e}-\gamma q_e.
\]

The current Megatron adapter updates additive expert bias with a **signed count error** (global count or averaged rank-local signs), using Megatron's bias-update rate. That is an implementation-specific controller. It can test whether the requested-versus-admitted signal distinction has practical consequences under Megatron's native bias-control mechanism, but its trajectories are not the exact linear gauge dynamics of the theorem.

Therefore report two tracks, with different labels:

| Track | Router/controller | What it tests | Allowed interpretation |
|---|---|---|---|
| A. Formal-mechanism replay | Fixed real router scores/logits, exact deterministic Top-\(K\), canonical per-expert capacity accounting, and the formal gauge update | Whether the proved signal/dynamics mechanism is visible on real router score distributions and real token batches | Real-logit mechanism validation; not a language-model training or quality claim |
| B. Megatron training benchmark | Pinned Megatron router and its native signed expert-bias update, replacing only the update's count input with requested or admitted counts | Whether the signal choice changes the behavior of this training stack under matched training | A result about this pinned Megatron implementation and protocol; not a proof of the exact formal update |

Track A should replay saved logits or router scores from a real pretrained MoE checkpoint over a fixed, documented text set. It should preserve the formal score equation and update exactly, rather than importing the Megatron sign rule. Track B uses the existing adapter and must be described as a signed-bias signal ablation. If resources require sequencing, complete and validate Track A first, then run Track B; do not merge their outcomes into one claim.

For each track, log the actual pre-drop routing map and post-drop map. Do not assume the framework's names or counters equal the paper's \(R\) and \(A\); validate the map-level definitions in the pinned source and in the runtime telemetry. Under ordinary independent per-expert capacity, the count relation is expected to be \(A_e=\min(R_e,C_e)\), but the experiment must verify this for the selected dispatcher, padding, and drop policy.

## 3. Preregistered hypotheses and estimands

### H1 — Real-workload condition prevalence

Measure the fraction of router-layer × update-step observations that satisfy each condition:

- at least one expert is capacity-clipped;
- at least two experts are capacity-clipped;
- every expert in the relevant balancing group is saturated;
- aggregate capacity is below the number of offered assignments;
- zero assignments are dropped (the no-censoring regime).

Report both the fraction of steps and the fraction of token assignments affected. Define the balancing group (layer, expert-parallel group, data-parallel aggregation group, and update interval) before counting. Never describe a single saturated expert as global saturation.

### H2 — Signal and controller response

For each matched initial seed, data order, and workload, compare requested- and admitted-feedback arms. Primary mechanism outcomes are:

- controller-state difference and update direction;
- requested/admitted per-expert count distributions;
- request-load imbalance (TV from target, coefficient of variation, max-to-mean ratio);
- dropped assignments, drop rate, and per-expert overflow;
- saturation incidence and duration;
- routing-map disagreement and fraction of tokens whose selected experts change.

The primary comparison must use a **global count signal** so it tests the same population-level observation as the formal result. Rank-local signs averaged across ranks are a different controller; report them as a separately labeled secondary factor.

### H3 — Training quality and efficiency

In Track B, the primary training outcome is validation next-token negative log-likelihood at a fixed number of training tokens seen. Select the final token budget before the full comparison. The primary contrast is requested-feedback minus admitted-feedback at the predeclared scarcity condition. Lower NLL is better. Report its paired effect and uncertainty across independent seeds.

Secondary outcomes: held-out validation NLL across the training curve; downstream task scores selected before training; training loss and instability; overflow/drop rate; request-load imbalance; tokens/sec and optimizer-step time; peak allocated GPU memory; controller/telemetry time; communication operations and bytes; and failed/rolled-back runs. Report quality and system metrics separately; do not combine them into an arbitrary weighted score.

### H4 — No-drop negative control

With capacity dropping disabled and otherwise matched inputs, pre-drop and post-drop maps must be identical. The requested/admitted signal arms must then produce identical count inputs and, for an identical deterministic update implementation, identical controller trajectories. If this check fails, the telemetry adapter or experimental pairing is invalid and the paper profile must not be interpreted.

## 4. Experimental platform and data

### 4.1 Pinned training stack

Use the existing pinned Megatron-LM revision and adapter guard documented in `experiments/megatron_feedback/README.md`. Record the exact Megatron commit, the adapter and compatibility-patch hashes, Python/PyTorch/CUDA/NCCL versions, GPU model and topology, driver, all launch arguments, and git state. Do not silently upgrade the source or change the dispatcher between arms. The first adapter validation should keep router fusion and CUDA graphs disabled; only add optimized paths after the same telemetry and negative-control checks pass.

The inspected code profile is an 8-expert, Top-2, 12-layer model with hidden size 768 and sequence length 2048. Treat that as the **controlled initial training model**, not as evidence of frontier-scale behavior. Report parameter count, active parameters/token, FLOPs/token estimate, effective batch, sequence length, and total tokens. A larger model/parallel topology is the replication/scale study after the controlled experiment is stable.

### 4.2 Real training corpus

Use a public, licensed, versioned corpus suitable for pretraining; FineWeb or FineWeb-Edu is a candidate because its dataset and curation are documented. Freeze a specific dataset revision/snapshot and shard list. Record license, download source, preprocessing code/version, tokenizer files and hash, exact train/validation/test split, deduplication policy, document/token counts, and a manifest hash. The training and validation streams must be disjoint at the document level. Keep the tokenizer, sequence packing, and batch order identical within each paired seed.

The current launcher accepts explicit preprocessed data and tokenizer arguments. Do not use mock data in a result table, and do not use a sample called “real data” without a reproducible fingerprint. If a held-out broad-domain fit benchmark such as Paloma is added, pin its version, report domains separately and aggregate using the benchmark's declared procedure; check overlap with training data and label any non-decontaminated evaluation as diagnostic.

The corpus is not itself the benchmark. The benchmark is the complete model, data, routing, capacity, controller, budget, evaluation, and statistical protocol recorded here.

### 4.3 Token and compute budget

Do not use the example `--steps 5000` as a research justification. First run a small baseline-only pilot on the actual hardware to measure tokens/sec, memory, validation cadence, and seed-to-seed validation variation. From the available compute allocation, set a fixed token budget and checkpoint schedule that all treatment arms can complete. Record this decision before opening treatment comparisons. Keep the primary comparisons token-matched; separately report wall-clock and accelerator-hours because the controllers may have different costs.

Use the same initialization seed and saved initial weights for each paired arm, the same pretokenized batch sequence, optimizer and schedule, global batch, and exact number of tokens. Training trajectories naturally diverge after the controllers route differently; do not force later RNG states to match. Record all run failures and exclude no run based on outcome. If a run is excluded for a predeclared technical failure, rerun its entire matched seed block and preserve the failed artifacts.

## 5. Capacity design: natural operating points plus a theorem-aligned stress condition

The existing `protocol.yaml` factors are `disabled`, 1.0, and 1.25. These are useful no-drop/ordinary-capacity controls, but they do **not** include aggregate shortage below nominal assignment demand. The central theorem's strict-shortage regime therefore is not represented by that current capacity grid.

Use this capacity set, after verifying that the pinned Megatron path supports each value and records its realized integer capacities:

| Condition | Role | Interpretation |
|---|---|---|
| Dropping disabled | Mandatory negative control | Requested and admitted maps should coincide; feedback-signal contrast is null by construction |
| Capacity factor 1.25 | Slack operating point | Tests censoring when capacity is generously provisioned; report observed drops, do not assume zero |
| Capacity factor 1.0 | Nominal operating point | Realistic reference point; actual saturation/drop incidence is measured |
| Capacity factor 0.75 | Controlled scarcity stress | Creates aggregate capacity below nominal assignment demand; tests the theorem-aligned mechanism under stress, not a claim that this is a universal production setting |

The first full protocol should use per-expert capacity and the pinned `probs` token-drop policy, without padding. Record actual `C_e` and the exact selected-map transformation for every layer/update. Capacity factor is not identical to the theorem's uniform integer ratio \(c=EC/(KT)\) because frameworks may round capacity and apply group-specific token counts; compute realized \(c\) from the actual batch and report it.

Analyze the theorem's exact condition as an observed stratum, not as an assumption inferred from capacity factor. Report results for all steps and separately for (i) all experts saturated, (ii) partial saturation, and (iii) no drops. The conditioning event is measured from pre-update counts and must not be selected based on outcome.

## 6. Baselines and factorial design

### 6.1 Required baselines

All baselines use the same architecture, score function, capacity/drop policy, data order, seed pairing, optimizer, training tokens, and execution flags unless the baseline definition requires otherwise.

| Arm | Balancing mechanism | Purpose |
|---|---|---|
| No balancing | No auxiliary load loss and no bias update | Measures unconstrained router behavior and drop/quality reference |
| Standard auxiliary load-balancing loss | Megatron's documented auxiliary-loss router with coefficient fixed from the pilot and then frozen | Represents the loss-based balancing family |
| Native admitted-count bias update | Unmodified pinned Megatron expert-bias controller | Current system reference and relevant admitted-count policy |
| Matched admitted-feedback bias | Same adapter/update rate as requested arm, but input counts are post-drop admissions | Primary signal ablation control |
| Matched requested-feedback bias | Same adapter/update rate as admitted arm, but input counts are pre-drop requests | Primary signal intervention |

The matched requested/admitted pair isolates the feedback signal. The native bias controller measures how the adapter's instrumentation/wiring compares with stock framework behavior. The auxiliary-loss method is a distinct family, not a signal-only ablation. Do not call any one method “the standard” across all MoE implementations; state the exact implementation and configuration.

### 6.2 Core versus secondary factors

Primary signal comparison: global requested versus global admitted counts, same signed-bias update, and same predeclared update rate. The primary efficacy condition is the declared 0.75 scarcity stress cell; 1.0 and 1.25 are secondary operating-point replications, and dropping-disabled is the negative control. Report the complete capacity-by-controller interaction rather than pooling the four conditions into one number.

Secondary comparison: rank-local signed actions averaged to synchronized bias versus global-count update. This changes the information aggregation and controller law, so do not pool it into the primary requested/admitted estimate.

Initial full matrix using the current launcher structure:

- 4 capacity conditions × 5 required arms × 5 seeds = 100 primary/global runs.
- If local-scope requested and admitted variants are retained: add 4 capacity conditions × 2 feedback signals × 5 seeds = 40 secondary runs, for 140 total.

This is a design count, not a compute commitment. If the budget is smaller, preserve the paired requested/admitted arms and the no-drop control first; reduce secondary scope arms before reducing the primary comparison's seed count or dropping its capacity conditions. Use a pre-run pilot to estimate seed variance and set the final sample size to detect the predeclared minimum practically important NLL difference. Five seeds are the current protocol's starting design, not proof of adequate power.

### 6.3 Hyperparameter fairness

Do not select the requested arm's update rate on the test/validation results and then hold the admitted arm to a different search budget. Use a small, predeclared grid of shared rates for both signal arms; use the same number of pilot runs and the same selection rule. Choose the auxiliary-loss coefficient with its own declared pilot because it is a different method. Freeze all selected values before the final seed block. Report the full pilot range and selected value.

The formal controller and signed-bias controller have different parameterizations; never transfer an \(\eta\) or bias-rate value between them as though they were equal. For Track A, declare \(\eta,\gamma,\delta\) and use the formal equations. For Track B, declare Megatron's signed update rate and report it separately.

## 7. Run sequence and launch gates

### Gate 0 — Freeze data and paper protocol

Create and hash the data/tokenizer manifest; fix the exact Megatron SHA, model configuration, capacity set, controller definitions, evaluation split, token budget, seed list, primary outcome, and analysis script hash. Publish this preregistration internally before treatment results are inspected.

### Gate 1 — Source and telemetry audit

For the pinned revision, verify with source references that requested counts are counted before token dropping, admitted counts after dropping, and global update counts use the intended process group. Verify the selected `probs` drop policy, non-padding assumption, and whether the requested histogram reuses or adds a collective. Instrument and compare the actual local maps against recorded counts on a tiny batch. Compute whether requested and admitted count reduction replaces an existing reduction or adds communication; do not assume either.

### Gate 2 — Mock-data GPU wiring smoke

Run the existing one-GPU smoke and matched drop-off arms. This is a software/wiring gate only. Require no analyzer violations, exact requested/admitted equality in the no-drop pair, valid count mass/capacity constraints, identical resolved flags, and successful validation-log parsing. Mock data cannot enter the scientific results.

### Gate 3 — Real-data baseline pilot

Run only a short no-balancing and native-baseline pilot on the frozen real corpus. Confirm input pipeline, train/validation separation, token accounting, stable loss, correct evaluation split, usable logging, and a feasible fixed token budget. This pilot is not used for final efficacy claims.

### Gate 4 — Real-router prevalence/replay

Capture pre-drop scores/routes and post-drop routes on a public pretrained MoE checkpoint or the real-data baseline model. First report natural-capacity incidence. Then perform the formal Track-A replay on the same saved scores with fixed batches and the formal update. This provides the cleanest test of the theorem on realistic score geometry without confounding it with parameter learning.

### Gate 5 — Paired training benchmark

Run the frozen matrix, paired by seed and token stream. Save complete logs and telemetry. No mid-run changes to flags, controller, evaluation, or exclusion rules. Do not stop a run because its metrics look unfavorable.

### Gate 6 — Replication/scale

Only after gates 0–5 pass, repeat the primary comparison at a larger model or expert-parallel topology. Keep the same measurement definitions and report when the topology changes the count-aggregation group. This is required before making claims about scaling behavior; it is not needed to prove the finite formal theorem.

## 8. Statistical analysis and reporting

The experimental unit for training quality is an independent training seed/run, not a step, layer, token, or expert. Use paired seed-level differences. Report each seed's value, mean paired effect, standard deviation, and a 95% interval calculated over independent seeds (paired bootstrap or a predeclared paired model). Do not compute confidence intervals by treating correlated steps or tokens as independent samples.

Primary training estimand at each preregistered capacity condition:

\[
\Delta_{\mathrm{NLL}} = \mathrm{NLL}_{\mathrm{requested}} - \mathrm{NLL}_{\mathrm{admitted}}
\]

at the same final seen-token budget. Negative values favor requested feedback. Report the estimate and interval; do not equate statistical significance with practical importance. State a practical effect threshold before training based on the pilot and project objective. If the interval includes both meaningful benefit and harm, the study is inconclusive at its current power.

For mechanism outcomes, aggregate within each run first, then compare matched run-level summaries. Show time series and distributions in addition to averages, because the theorem predicts a state-dependent freeze rather than a constant average effect. Report all capacity strata, all seeds, all failed runs, and all registered baselines. Keep the following evidence classes separate in figures/tables:

- theorem proof;
- exact formal-controller replay;
- real-data router telemetry;
- end-to-end training quality;
- system runtime and communication.

## 9. Required telemetry, metrics, and artifacts

### Per layer × update record

Record step and tokens seen; layer ID; process-group/topology IDs; pre-drop request vector \(R\); post-drop admitted vector \(A\); realized capacity vector \(C\); dropped vector \(J=R-A\); pressure or bias before/after; controller input and update direction; total requested/admitted/dropped assignments; all-expert and per-expert saturation flags; router score function; capacity/drop policy; and whether counts are rank-local or globally reduced. Retain counts exactly; normalized views can be derived offline.

### Per run

Record seed; initial checkpoint hash; data/tokenizer manifest hash; consumed token count; full resolved config and command; source and adapter hashes; framework and hardware versions; run start/end; training/validation curves; throughput and per-step timings; peak memory; profiler traces for representative warm steady-state intervals; communication operation counts/bytes where available; checkpoint hashes; run exit status; and analysis code hash.

Write immutable run directories. Derive summary tables and plots only from saved artifacts through versioned analysis code. Keep test data separate from tuning and validation. Never overwrite a prior run or hand-edit reported values.

## 10. Go/no-go interpretation rules

| Observation | Correct interpretation / next decision |
|---|---|
| No-drop negative control fails | Stop; fix telemetry, pairing, or controller implementation before interpreting any comparison |
| Natural workload has almost no drops/saturation | The mechanism is mathematically valid but rare in that operating regime; report that fact. Use the predeclared scarcity stress condition to test the mechanism, but do not call it typical behavior |
| Saturation occurs and admitted feedback freezes/loses allocation information in Track A | Supports real-logit relevance of the formal mechanism under the observed condition; does not establish training quality benefit |
| Requested feedback reduces imbalance but not NLL or throughput | Establishes a load metric effect only; do not claim model or system improvement |
| Requested feedback improves NLL but materially increases time/cost | Report the quality-cost tradeoff; claim practical benefit only if a predeclared value criterion is met |
| Requested feedback improves quality at matched tokens with acceptable measured cost, across paired seeds and a replication | Supports a scoped practical claim for the tested model/data/router regime; broader deployment claims still require broader systems evidence |
| No meaningful requested/admitted difference in naturally occurring conditions | Limits practical relevance in those conditions; does not refute the conditional theorem |
| Results vary by capacity or workload | Treat capacity/workload as effect modifiers and report them; do not average away the interaction |

The theoretical benchmark-comparison gate remains separate: a strong real-data result improves empirical significance, but it does not by itself prove that the family theorem is new relative to costed adaptive testing. Conversely, a benchmark reduction does not invalidate a practically useful measured result.

## 11. Known gaps in the current implementation plan

The inspected code already provides a pinned Megatron adapter, a mock-data smoke profile, requested/admitted telemetry, validation parsing, and a real-data launcher. The following changes are required before calling the existing `paper` profile this benchmark:

1. **Add the theorem-aligned capacity stress cell.** Current factors are `disabled`, 1.0, and 1.25; add 0.75 (after verifying capacity rounding and that the pinned implementation accepts it). Keep ordinary operating points and no-drop control.
2. **Document controller mismatch.** Existing training arms use signed bias updates, not the formal linear gauge update. Label them as a Megatron signal ablation. Add Track A formal-controller replay if claiming real-score validation of the theorem itself.
3. **Make global signal comparison primary.** Keep local-scope averaged signs as secondary and report them separately.
4. **Freeze compute budget from a baseline pilot.** The README's 5,000-step command is illustrative; steps/tokens, evaluation checkpoints, seeds, and power must be justified and recorded before full runs.
5. **Add instrumentation overhead profiling.** Compare native admitted baseline, adapter admitted, and adapter requested under the same no-drop and drop-enabled conditions; isolate hook/logging overhead from count-collection cost and training noise.
6. **Use a real, fingerprinted corpus and fixed tokenizer/split.** The mock smoke is never evidence. Add overlap checks for external evaluation sets.
7. **Reconcile formal-update parameter notation.** The code and paper formal core use \(\eta\gamma\), while the canonical `formal.md` generic update omits explicit \(\gamma\). This is harmless to the common-mode freeze conclusion, but normalize the notation before quantitative step-size comparisons.

The launcher currently expands the three capacity levels into 105 runs for five seeds (21 cells/seed). Adding 0.75 yields 140 runs if local-scope secondary arms are retained (28 cells/seed). Update the run-count documentation and artifact schemas together; do not assume the old count remains correct.

## 12. Online sources checked for this protocol

- [Switch Transformers, JMLR](https://jmlr.org/papers/volume23/21-0998/21-0998.pdf): capacity, token overflow, and auxiliary load-balancing formulation.
- [NVIDIA Megatron Core MoE documentation](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/features/moe.html): current capacity, router bias, auxiliary loss, and token-drop configuration surface. The study pins a source revision separately because these docs evolve.
- [Megatron Core router API](https://docs.nvidia.com/megatron-core/developer-guide/latest/apidocs/core/core.transformer.moe.router.html): router ordering and distinction between scores, routing maps, and optional dropping.
- [Loss-Free Balancing](https://arxiv.org/abs/2408.15664) and [DeepSeek-V3 technical report](https://arxiv.org/abs/2412.19437): count-driven expert-bias balancing is established prior art and should be included as a system baseline, not claimed as the project's invention.
- [FineWeb](https://arxiv.org/abs/2406.17557): candidate documented public pretraining corpus; the exact dataset revision and license still need to be frozen in the experiment manifest.
- [Paloma](https://arxiv.org/abs/2312.10523): candidate broad-domain language-model-fit evaluation; use its versioned protocol and report domain-level results if selected.

These sources motivate the benchmark ingredients. They do not certify the experimental setup or prove that a proposed outcome will occur. The protocol is the project's preregistered design; the pinned code, actual telemetry, and run artifacts determine whether each requirement was met.

## 13. Clean-room implementation architecture

The experiment runner must be a new, versioned implementation. Do not extend the exploratory `experiments/megatron_feedback` launcher, import `moe_control` into the training adapter, or copy old generated results into the new run tree. Those artifacts remain valuable historical evidence, but the new benchmark must have one source of truth for its protocol, command construction, telemetry schema, and analysis.

Use a dedicated namespace such as `experiments/real_workload_v1/` with these boundaries:

```text
experiments/real_workload_v1/
├── README.md                    # operator guide and claim boundaries
├── protocol.py                  # typed source of truth for factors and constants
├── schemas/                     # manifest and telemetry schema documentation
├── src/real_workload_bench/
│   ├── protocol.py              # load, type-check, validate, and hash protocol
│   ├── data_manifest.py         # verify dataset/tokenizer files and split identity
│   ├── plan.py                  # deterministic matrix expansion; no training side effects
│   ├── preflight.py             # source/runtime/GPU/data checks before run allocation
│   ├── adapters/
│   │   ├── formal_replay.py     # exact q, gamma, gauge, and Top-K replay contract
│   │   └── megatron_<sha>.py    # one explicit adapter for one pinned Megatron revision
│   ├── telemetry.py             # versioned local-rank JSONL/parquet event schema
│   ├── launcher.py              # argv-only subprocess launch and immutable artifacts
│   └── analysis.py              # paired-seed metrics, intervals, and report generation
├── configs/                     # dataset/model/hardware-specific non-secret manifests
└── runs/                        # generated, append-only and git-ignored
```

The typed `protocol.py` is the only place that defines the factor matrix and scientific constants for v1. The run planner validates it and refuses invalid capacity values, duplicate arm/seed keys, or mismatched primary signal arms. Generate a `plan.json` before any run; it contains every cell, seed, protocol hash, pinned source hash, data-manifest hash, and expected output identity. The matrix is deterministic and can be reviewed without GPUs. Execution consumes that saved plan rather than rebuilding a possibly changed matrix.

### 13.1 Run safety and provenance

- Every run gets a unique immutable ID derived from protocol version, cell, seed, data fingerprint, and code revision; collisions fail closed.
- Create the run directory atomically and write `RUNNING` state only after all preflight checks pass. On exit, record `SUCCEEDED` or `FAILED`, exit code, timestamps, and the last log offset. Never overwrite or silently resume a partial run.
- Store commands as structured argv arrays, not shell strings. Reject semantic overrides that conflict with the protocol (model, data split, router score, capacity, token budget, controller, or seed).
- Save resolved config, data manifest, environment manifest, source hashes, adapter hash, protocol hash, hardware topology, and analysis hash into each run.
- A changed source SHA, dirty framework tree, mismatched tokenizer, or changed dataset shard list invalidates the plan unless a new protocol version is created.
- Keep credentials, signed URLs, and private filesystem paths out of public manifests. Store only portable dataset identifiers, file hashes, and redacted path metadata.

### 13.2 Data path and memory discipline

Preprocess and tokenize the corpus once, before treatment runs. Store tokenized shards in a documented, immutable format with per-shard checksums and a manifest containing document IDs or stable hashes, split membership, token counts, tokenizer revision, and preprocessing version. Validate no document crosses train/validation/test. Use the same shard order for paired seeds and store the exact sampling permutation/seed. Do not tokenize separately inside each arm.

Keep the hot training path unchanged except for the controller signal and required count capture. Do not copy full logits, routing maps, or token IDs to CPU every step. Derive per-expert counts on device from the existing routing maps, emit compact integer vectors, and write rank-local asynchronous records. No diagnostic all-reduce is permitted on every step unless that collective is part of the declared controller; aggregate diagnostic telemetry offline. Bound any writer queue and apply backpressure explicitly rather than allowing unbounded host-memory growth.

### 13.3 Performance and optimization protocol

Correctness comes before optimization. First validate the eager, unfused path. Then benchmark three code paths on identical fixed batches after warmup: native controller, instrumented admitted controller, and instrumented requested controller. Use the same hardware placement, dispatch policy, number of warmup iterations, synchronization boundaries, and profiler settings. Repeat timing blocks and report median plus dispersion; do not compare a profiled treatment with an unprofiled baseline.

Report instrumentation overhead separately from the controller's marginal signal cost. Measure router forward time, count extraction time, communication operations and bytes, bias update time, MoE layer time, total optimizer-step time, tokens/sec, and peak memory. Include both local-rank and global-count variants only as distinct controllers. State whether requested counts reuse an existing collective or add any; verify it against the pinned source and a communication trace.

After semantic parity is established, re-enable the deployment-relevant fused router/dispatch path and CUDA graphs if the target stack uses them. Re-run the no-drop equality check and map-level count checks on that optimized path. Record compiler/kernel settings and benchmark both optimized and reference execution. Do not report speedups obtained only by changing precision, batch size, graph capture, or dispatcher between arms.

### 13.4 Analysis and result integrity

The analyzer accepts only complete run directories whose protocol, data, model, and adapter hashes match the saved plan. It verifies expected run cardinality, paired seed coverage, complete validation checkpoints, and telemetry invariants before estimating effects. It emits a machine-readable claim table linking every plotted/table value to input run IDs and code version. Missing runs are shown as missing; they are never silently dropped from a paired comparison.

Before data collection, freeze the primary contrast, evaluation checkpoint, seed count, practical effect threshold, interval method, and treatment of failed runs. Keep pilot data labeled as pilot and exclude it from final inferential results if it was used to choose hyperparameters or budget. No test-set metric may select a controller or tune its rate.

### 13.5 Implementation completion gate

Do not launch the real-data matrix until the new implementation can, from a clean checkout:

1. validate the protocol and reject malformed or conflicting configs;
2. produce the same reviewed run plan on repeated invocations;
3. verify data/tokenizer manifests and pinned source hashes before allocating a run;
4. pass the no-drop requested/admitted identity check;
5. emit complete per-rank request/admission/capacity telemetry without diagnostic collectives;
6. reproduce an analysis summary from saved artifacts alone; and
7. quantify instrumentation overhead on fixed batches.

These are acceptance criteria for implementation, not results already achieved. The existing exploratory runner may inform the source audit, but it does not satisfy this clean-room completion gate by itself.

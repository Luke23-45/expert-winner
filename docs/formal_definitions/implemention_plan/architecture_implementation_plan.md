# Architecture and implementation plan

**Status:** proposed design; no experiment code has been implemented yet
**Scope:** a reproducible control experiment for the formal definitions in [`../formal.md`](../formal.md)
**Repository state observed:** this repository currently contains the formal document but no experiment package or established Python tooling. This plan therefore proposes a clean initial structure rather than fitting an existing runtime.

## 1. Objective and research framing

The first implementation should isolate the formal claim that capacity admission can censor requested demand. Under global saturation, admitted counts are fixed at capacity, so admitted-load feedback cannot distinguish excess-demand patterns. Requested-load feedback still observes the pre-capacity request counts.

The experiment is a **closed-loop routing control study**, not initially a language-model training comparison. Its core question is whether the two feedback sources cause the predicted difference in relative pressure and requested-load response while saturation holds. Full model training, downstream quality, performance benchmarking, and an exhaustive baseline study belong to later phases.

This distinction matters for research positioning. Switch Transformers describe finite expert capacity, token overflow, and auxiliary balancing losses. Loss-Free Balancing already adjusts expert score biases before Top-K using observed assignment counts, so the general idea of count-driven router feedback is established. A 2025 theoretical preprint interprets that method through a primal-dual lens, and a September 30, 2026 preprint frames recent balancing approaches as incomplete PID controllers. The experiment should therefore make its contribution specific to **requested versus censored admitted feedback under saturation**, rather than claiming that per-expert feedback control is itself new. The recent PID paper is an early preprint and should be reviewed again before publication.

Sources: [Switch Transformers](https://jmlr.org/papers/volume23/21-0998/21-0998.pdf), [Loss-Free Balancing](https://arxiv.org/html/2408.15664), [theoretical framework for Loss-Free Balancing](https://arxiv.org/abs/2512.03915), and [ID Balancing, submitted September 30, 2026](https://arxiv.org/abs/2609.39137).

## 2. Architecture decisions

### 2.1 Keep the control loop independent of model training

Implement routing, capacity accounting, controller updates, and metrics as ordinary Python/PyTorch components. The first synthetic and cached-logit experiments need no optimizer, autograd graph, or Lightning `Trainer`. Keep the controller state as an explicit pressure tensor and update it under `torch.no_grad()`.

Use PyTorch tensors for affinity scores, Top-K masks/counts, capacity vectors, and pressure updates. Keep arithmetic in floating point where the theory uses normalized counts, and counts/capacities in integer tensors. Make dtype and device conversion explicit at component boundaries.

### 2.2 Use Lightning at the training boundary

Use `lightning.pytorch` when a later phase trains a router or MoE model. Put training-specific logic in a `LightningModule` and data preparation in a `LightningDataModule`; have those call into the same routing/controller package used by the synthetic experiment. Do not put the formal routing update inside Lightning hooks.

Lightning’s `Trainer` provides seeding and deterministic-mode controls; Lightning Fabric is an option if future work needs a lower-level custom distributed loop. For this project, start with plain PyTorch for the control runner and add the Lightning dependency only when the model-training phase begins. This keeps the primary experiment small while preserving a supported path to training. See the [Lightning Trainer documentation](https://lightning.ai/docs/pytorch/stable/common/trainer.html) and [Fabric overview](https://lightning.ai/docs/fabric/latest/index.html).

### 2.3 Use composable YAML with typed configuration

Use Hydra config groups in YAML to combine independent choices such as scenario, capacity regime, controller, and runtime. Define a matching Python structured configuration/dataclass schema and validate the fully composed configuration before a run starts. This gives researchers readable configs and keeps invalid combinations out of the numerical core. Hydra supports config composition and multirun sweeps; retain the fully resolved config for every run. See [Hydra’s configuration composition](https://hydra.cc/docs/intro/), [Defaults List](https://hydra.cc/docs/advanced/defaults_list/), and [multirun](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/).

Do not encode experimental data or generated affinity matrices in YAML. YAML stores small declarative parameters; scenarios generate or load tensor data from deterministic seeds and versioned data files.

### 2.4 Use a `src/` package, explicit interfaces, and a small dependency set

Use a Python package under `src/` with a `pyproject.toml` and a lockfile. Pin exact resolved versions for each published result. Keep dependencies purposeful: PyTorch for tensor operations, Hydra/OmegaConf for configuration, pytest for tests, and Lightning only for later training. Add analysis or artifact dependencies when a concrete output format requires them, rather than coupling the controller to a tracking service.

## 3. Proposed repository layout

The following is the proposed code layout for a later implementation. This document-only change does not create these source files.

```text
moe/
├── pyproject.toml
├── uv.lock                         # exact reproducible environment
├── configs/
│   ├── config.yaml                 # experiment composition and defaults
│   ├── scenario/
│   │   ├── stationary_synthetic.yaml
│   │   ├── shifted_synthetic.yaml
│   │   └── cached_logits.yaml      # later frozen-router input
│   ├── controller/
│   │   ├── requested.yaml
│   │   ├── admitted.yaml
│   │   ├── admitted_centered.yaml
│   │   └── capacity_relative.yaml
│   ├── capacity/
│   │   ├── shortage.yaml
│   │   ├── exact_total.yaml
│   │   └── slack.yaml
│   └── runtime/
│       ├── cpu.yaml
│       └── cuda.yaml
├── src/moe_control/
│   ├── __init__.py
│   ├── config.py                   # typed schemas and cross-field validation
│   ├── contracts.py                # immutable inputs/outputs and protocols
│   ├── routing/
│   │   ├── topk.py                 # pressured scores and deterministic Top-K
│   │   └── observations.py          # request counts and routing records
│   ├── capacity/
│   │   ├── base.py                 # admission protocol
│   │   └── per_expert.py           # canonical A_e=min(R_e,C_e) rule
│   ├── controllers/
│   │   ├── base.py                 # feedback-controller protocol
│   │   ├── requested.py
│   │   ├── admitted.py
│   │   ├── admitted_centered.py
│   │   └── capacity_relative.py
│   ├── dynamics/
│   │   └── gauge.py                # gauge projection and pressure transition
│   ├── scenarios/
│   │   ├── base.py                 # affinity-source protocol
│   │   ├── synthetic.py
│   │   ├── demand_shift.py
│   │   └── cached_logits.py         # later real-router adapter
│   ├── metrics.py                  # pure metric functions and schemas
│   ├── runner.py                   # one explicit, ordered control loop
│   ├── artifacts.py                # manifests and append-only outputs
│   ├── reproducibility.py           # seeds, device, and deterministic options
│   ├── cli.py                       # Hydra entry point
│   └── training/                   # later phase only
│       ├── lightning_module.py
│       └── data_module.py
├── tests/
│   ├── unit/
│   ├── properties/
│   └── integration/
├── scripts/
│   └── summarize_runs.py
└── results/                         # generated; ignored by version control
```

Keep the experiment package in the `moe` repository root. Keep this architecture document in `docs/formal_definitions/implemention_plan/`; later experiment-specific protocol and results documents can live beside it without mixing raw outputs into the formal-definition folder.

## 4. Component responsibilities and boundaries

| Component | Owns | Must not own |
|---|---|---|
| `Scenario` / `AffinitySource` | Produces a batch of raw affinities and optional time-varying changes from a seed | Capacity or controller semantics |
| Router | Forms scores as affinity minus gamma times pressure, selects exactly K distinct experts per token, and returns selected indicators plus requested counts R | Admission decisions or pressure updates |
| CapacityPolicy | Computes admitted counts A and rejected counts J from requests and capacity | Changing requested routes or feedback values |
| FeedbackController | Computes a feedback vector from an immutable observation containing R, A, C, mu, K, and T | Mutating pressure state or selecting experts |
| PressureDynamics | Applies step size, optional decay, and gauge normalization to q | Reading logits or inventing a feedback signal |
| `Metrics` | Computes descriptive values from a completed pre-update observation | Changing routing, counts, or control state |
| `ExperimentRunner` | Calls the components in a single documented sequence and records each step | Embedding controller-specific equations inline |
| `ArtifactWriter` | Saves resolved config, run metadata, step metrics, and summaries | Becoming a second source of experimental configuration |

Use small protocols/abstract base classes for the scenario, router, capacity policy, feedback controller, and artifact writer. Pass explicit immutable records between them. A new controller should require a new controller implementation and config group, not a fork of the runner.

## 5. Exact iteration contract

One iteration must follow this order to avoid off-by-one ambiguity:

1. Read current pressure q_k and current affinity batch a_k.
2. Compute pressured scores s_k = a_k - gamma * q_k.
3. Select Top-K experts and compute pre-capacity requested counts R_k.
4. Apply the configured capacity policy to obtain A_k and J_k.
5. Build an immutable observation from R_k, A_k, C, mu, K, and T.
6. Compute the controller feedback epsilon_k.
7. Apply the exact pressure transition, including configured decay and gauge normalization, to produce q_(k+1).
8. Compute and write metrics for step k, storing pressure before and after the update.
9. Advance the scenario and begin the next step.

The default transition should match the document: q_next = gauge_project((1 - delta) * q + eta * epsilon). Keep eta, gamma, and delta separate in configuration and artifacts, even when a sweep uses the effective scale eta * gamma. This makes the score penalty and update scale inspectable.

For the initial synthetic study, implement the canonical count admission (A_e = min(R_e, C_e)) exactly. Do not silently turn it into a token-order policy. If later model execution needs a concrete accepted-token mask, add a separate token-level admission adapter and document how its ordering maps back to the formal count rule.

## 6. Typed contracts and configuration

Define typed configuration objects for:

- **Experiment:** name, protocol version, number of control steps, output root.
- **Problem:** expert count E, routing width K, token count T, target vector mu, and score scale gamma.
- **Scenario:** scenario name, seed, skew specification, shift step/size if present, affinity dtype/device.
- **Capacity:** per-expert integer capacity vector or a checked capacity-factor construction; policy name.
- **Controller:** controller name, step size η, pressure decay δ, and controller-specific options.
- **Runtime:** CPU/CUDA selection, deterministic setting, precision, and optional batch size.
- **Artifacts:** output format and whether full per-step routing masks are retained.

Validate before execution: 1 <= K <= E; T > 0; capacity vector length equals E; capacities are nonnegative integers; mu lies on the simplex; and scenario tensors have compatible shapes. Warn prominently when total capacity differs from K * T, because this changes whether the capacity dual interpretation in the formal document applies.

Use an explicit small YAML config as the human interface. An illustrative composition could be:

```yaml
defaults:
  - scenario: stationary_synthetic
  - capacity: shortage
  - controller: requested
  - runtime: cpu
  - _self_

experiment:
  name: saturation_signal_test
  steps: 500
  seed: 17

problem:
  experts: 8
  top_k: 2
  tokens: 1024
  score_gain: 1.0

controller:
  step_size: 0.05
  pressure_decay: 0.0
```

Treat this as a schema example, not a final tuned protocol. Store the resolved configuration (including all defaults and CLI overrides) with every run.

## 7. Determinism and scientific traceability

Hard Top-K makes ties scientifically consequential. PyTorch documents that `torch.topk` does not guarantee stable indices for tied values. Use a deterministic lexicographic tie rule—such as stable descending sort with expert index as the secondary ordering—or an equivalent explicitly tested selection function. The stable sort preserves the order of equal elements; define expert order in the contract. See the [PyTorch `topk` documentation](https://docs.pytorch.org/docs/stable/generated/torch.topk.html) and [`torch.sort(stable=True)` documentation](https://docs.pytorch.org/docs/stable/generated/torch.sort.html).

For each run:

- Seed Python, NumPy (if used), and PyTorch generators explicitly; seed DataLoader workers in later training runs.
- Offer a deterministic mode using PyTorch deterministic algorithms. Fail loudly if an operation cannot meet the requested determinism instead of silently falling back. PyTorch notes that deterministic behavior also depends on the full software/hardware setup, so record both.
- Record the git commit, clean/dirty state, resolved config, Python/PyTorch/Lightning versions, CUDA/runtime versions, device name, seed, scenario/data identifiers, and protocol version.
- Keep experimental outputs append-only and tie each output row to a unique `run_id` and `step`.

PyTorch explicitly cautions that deterministic-algorithm mode alone does not guarantee whole-application reproducibility. The implementation must combine deterministic selection, explicit seeding, version capture, and fixed scenario generation. ([PyTorch deterministic algorithms](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html); [Lightning reproducibility guidance](https://lightning.ai/docs/pytorch/stable/common/trainer.html#reproducibility))

## 8. Output and artifact contract

Create one output directory per run, for example:

```text
results/runs/<run_id>/
├── config.resolved.yaml
├── manifest.json
├── metrics.parquet
├── summary.json
└── affinity_reference.json        # generator parameters/hash, not necessarily full tensor
```

`metrics.parquet` should contain one row per step and fields with explicit units/names, including `step`, `controller`, `scenario`, `seed`, `pressure_before`, `pressure_after`, `requested_counts`, `admitted_counts`, `overflow_counts`, `requested_max_vio`, `requested_cv`, `total_overflow`, and `all_experts_saturated`. If arrays in a tabular row become awkward, store scalar per-expert columns or a sidecar tensor file with schema/version metadata. Save only aggregate data by default; make full token-level masks an opt-in artifact to control storage.

Generate publication tables and plots from saved run artifacts using separate analysis scripts. Never copy final values manually into paper tables. Raw runs are immutable; rerunning a config creates a new run ID rather than overwriting prior results.

## 9. Verification plan

These checks are design requirements for implementation, not claims that tests have already been run.

### Unit checks

- The router returns exactly K unique selected experts per token.
- Requested counts conserve mass: sum_e R_e = K * T, and each R_e <= T.
- Capacity satisfies A_e = min(R_e, C_e), 0 <= A_e <= R_e, and J_e = R_e - A_e.
- Gauge projection returns nonnegative pressure with minimum zero and is invariant to adding a common scalar to its input.
- Requested feedback sums to zero; centered feedback sums to zero within floating-point tolerance.
- Stable tie-breaking produces the documented expert ordering on CPU and CUDA.

### Equation-level regression checks

- Under verified global saturation with uniform capacities, admitted feedback is common-mode and produces no relative pressure change when delta = 0.
- In the same saturated state, requested feedback uses R rather than A and responds to the requested imbalance.
- For uniform capacities and uniform target, requested and capacity-relative feedback produce equivalent gauge updates.
- With uniform target, admitted and admitted-centered feedback produce equivalent gauge updates.
- At c = 1, global saturation implies R_e = C_e = K * T / E for every expert.

### Integration and property checks

- Run a short experiment end to end from a saved YAML config and verify the resolved config and metadata are present.
- Reload the saved metrics and reproduce the summary statistics from the raw rows.
- Test the same generated scenario twice with the same seed and deterministic mode; exact routing and metrics should match on the same software/hardware stack.
- Check invalid configurations fail before expensive execution with a specific validation error.

Use `pytest` for ordinary checks and property-based tests for conservation/gauge invariants where helpful. Treat empirical convergence of the hard Top-K update as an outcome, not a unit-test invariant; the formal document does not prove global convergence.

## 10. Implementation phases and exit criteria

### Phase 0 — Protocol freeze

Agree on the control question, exact iteration order, scenario construction, saturation conditions, metrics, seeds, and the meaning of capacity shortage. Exit when the protocol can be implemented from this document without making hidden choices.

### Phase 1 — Minimal deterministic core

Implement typed config, stable Top-K, canonical capacity accounting, gauge dynamics, requested/admitted controllers, runner, metrics, and artifact writer. Begin on CPU and keep the sample sizes small.

**Exit:** equation-level checks pass; same seed gives the same trace on the target environment; all invariants and metadata are observable.

### Phase 2 — Saturation and boundary experiment

Run shortage, exact-total, and slack capacities with fixed synthetic affinities. Confirm and report whether all-expert saturation holds at each step. Add the demand-shift run. Select step size through a predeclared small sweep, not per-controller hand tuning.

**Exit:** raw per-step data, configs, and run manifests exist for each paired seed; claims are conditioned on verified saturation; no assertion of overflow reduction is made for the fully saturated aggregate-shortage interval.

### Phase 3 — Frozen real-router validation

Add a cached-logit scenario from a fixed pretrained/frozen router. Do not train the router during this stage. Preserve batch boundaries and update controller state only after the batch that generated the counts, consistent with the historical-feedback interpretation in Loss-Free Balancing.

**Exit:** the signal-censoring finding either reproduces on realistic logits or the reason it does not is characterized by the data and capacity regime.

### Phase 4 — Training integration

Add Lightning modules only when evaluating learned-model quality or training dynamics. Reuse router, capacity, controller, and metrics contracts. Avoid a second implementation of the controller inside training code.

**Exit:** training and control-only paths agree on routed/admitted counts given the same logits, pressure, capacities, and tie policy.

## 11. Risks and engineering responses

| Risk | Response |
|---|---|
| Unstable Top-K ties obscure the controller effect | Fix tie order explicitly, record it, and include tied-score regression cases. |
| A controller-specific runner changes the experiment semantics | Keep one shared runner and inject the feedback controller through an interface. |
| Shortage is misreported as a solvable drop-rate problem | Report aggregate capacity shortage and separate it from avoidable imbalance/overflow; interpret full-saturation results as a signal observability/control test. |
| Hard Top-K creates oscillation | Log time series and settling/cycling behavior; do not encode convergence as a required test. |
| Step-size tuning favors one feedback signal | Select from a common predeclared range and report the sweep; log eta and gamma separately. |
| Lightning adds lifecycle complexity to a small routing loop | Keep it out of the core dependency path until model training is in scope. |
| Results cannot be regenerated after code/config changes | Save resolved config, version manifest, seed, scenario identity, protocol version, and immutable run outputs. |

## 12. Deferred decisions

The following decisions belong in the later detailed experimental protocol/baseline study:

- Final synthetic affinity distribution and how its skew parameter is calibrated.
- The complete baseline set and equal-tuning budget for each baseline.
- Statistical power, final seed count, and inferential procedure.
- Whether to include a particular pretrained MoE router and dataset for frozen-logit validation.
- Whether paper artifacts use Parquet, CSV, or both, based on the final analysis stack.
- Training-scale architecture, compute budget, and language-model quality evaluation.

This keeps the architecture extensible while avoiding premature commitment to an incomplete baseline study.

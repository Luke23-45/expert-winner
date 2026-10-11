# expert-winner

Research notes and implementation planning for capacity-constrained sparse Mixture-of-Experts routing.

## Current contents

- [`docs/formal_definitions/formal.md`](docs/formal_definitions/formal.md): formal model and corrected theoretical claims.
- [`docs/formal_definitions/implemention_plan/architecture_implementation_plan.md`](docs/formal_definitions/implemention_plan/architecture_implementation_plan.md): proposed modular architecture and staged experiment plan.

The initial study is implemented as a deterministic control experiment comparing requested-load and admitted-load feedback under capacity saturation (see below).

## Control experiment (`src/moe_control`)

The initial deterministic closed-loop routing experiment is implemented as the
`moe_control` Python package, following the architecture plan above. It
compares requested-load feedback against admitted-load feedback under capacity
saturation, using gauge-normalized pressure dynamics on synthetic Top-K routing
(E=8, K=2, T=1024, uniform target). The routing/control core is plain PyTorch;
Lightning is intentionally absent until the model-training phase.

### Install

```bash
pip install -e .
# torch CPU is sufficient; for CUDA builds install torch with CUDA support first
```

### Run

From the repository root:

```bash
# Shortage/saturation, uniform C=192, requested-load feedback
python -m moe_control.cli scenario=shortage capacity=shortage controller=requested

# Exact-total boundary, uniform C=256, admitted-load feedback
python -m moe_control.cli scenario=exact_total capacity=exact_total controller=admitted

# Slack capacity, uniform C=288, capacity-relative feedback
python -m moe_control.cli scenario=slack capacity=slack controller=capacity_relative

# Demand shift at step 250 (pressure state preserved), shortage capacity
python -m moe_control.cli scenario=demand_shift capacity=shortage controller=requested
```

Available choices: `scenario` in {`shortage`, `exact_total`, `slack`, `demand_shift`};
`capacity` in {`shortage`, `exact_total`, `slack`}; `controller` in {`requested`,
`admitted`, `admitted_centered`, `capacity_relative`}; `runtime` in {`cpu`, `cuda`}.
Any value can be overridden, e.g. `experiment.steps=200 experiment.seed=42
controller.step_size=0.02`.

Paired sweep over all four controllers on one scenario (same affinity batch
for every controller, since the batch is a pure function of the scenario seed):

```bash
python -m moe_control.cli scenario=shortage capacity=shortage \
  controller=requested,admitted,admitted_centered,capacity_relative --multirun
```

Or via the installed console script: `moe-control scenario=slack ...`.

### Outputs

Every execution writes one immutable run directory (never overwritten;
a fresh run ID is minted each time):
```text
results/runs/<run_id>/
├── config.resolved.yaml     # fully composed Hydra configuration
├── manifest.json            # git commit, versions, device, seed, protocol
├── metrics.parquet          # one row per step (counts, overflow, pressures)
├── summary.json             # aggregate statistics for the run
└── affinity_reference.json  # generator parameters + content hash
```

Generated outputs live under `results/` and are git-ignored.

### Results

The full experiment (64 runs: 4 scenarios x 4 controllers x 3 seeds at 500
steps, plus a shared step-size sweep in the shortage regime at 2000 steps) is
documented in [`docs/control_experiment_results/results.md`](docs/control_experiment_results/results.md),
with the published run artifacts committed alongside it in
`docs/control_experiment_results/runs/`. Regenerate the tables and verify the
headline findings from the artifacts with
`python scripts/summarize_runs.py --runs-dir docs/control_experiment_results/runs`
and `python scripts/verify_findings.py --runs-dir docs/control_experiment_results/runs`.

### Scientific notes

- Under uniform capacity and uniform target, `requested` and
  `capacity_relative` produce identical feedback, and `admitted` and
  `admitted_centered` define the same gauge dynamics (they differ only by a
  common-mode component the gauge projection removes). The run manifest
  records this equivalence; equivalent variants are not independent findings.
- In the fully saturated aggregate-shortage regime, total overflow is fixed
  by the aggregate capacity shortage, so overflow reduction must not be
  attributed to a controller there. Overflow and requested-load balance are
  reported as separate metrics.
- Convergence or cycling of the pressure dynamics is an empirical outcome;
  the formal document does not prove global convergence.

# Pre-data central-claim audit

This suite checks the implemented mechanism in the formal claim using the
repository's existing deterministic Top-K router, canonical admission rule,
feedback controllers, and gauge pressure update. It is paired by seed and
affinity tensor. It is synthetic evidence only; it cannot establish a real
language-model validation-NLL improvement or telemetry properties of deployed
systems.

## Run

From the repository root, run the production synthetic suite on CPU:

```bash
uv run python experiments/central_claim/run_suite.py --device cpu
```

This simulator uses small per-step tensors, so GPU launch overhead may exceed
the compute. CUDA remains available as an explicit option if you benchmark it
on your machine:

```bash
uv run python experiments/central_claim/run_suite.py --device cuda
```

The default protocol is 50 paired seeds over five conditions (500 runs).
Artifacts are created in a unique timestamped directory under
experiments/central_claim/results/. The script refuses to overwrite an
existing suite directory. Do not use --seed-count or --step-limit for the
protocol run; these switches are only for diagnostic smoke runs and are marked
in the manifest.

After the suite finishes, analyze that exact output directory:

```bash
uv run python experiments/central_claim/analyze_suite.py experiments/central_claim/results/<suite-id>
```

The analyzer exits nonzero if any preregistered invariant or pairing check
fails. Inspect report.md, claim_audit.json, and paired_effects.csv; retain
the immutable raw trajectories, run index, protocol snapshot, and manifest.

## Conditions and interpretation

| Condition | Purpose |
|---|---|
| shortage_c075 | Primary globally saturated aggregate-shortage dynamics |
| shortage_c050 | More severe shortage sensitivity |
| exact_total_boundary | Balanced c = 1 boundary control |
| partial_slack_c1125 | Mixed saturated/unsaturated boundary control |
| no_drop_control | Requested/admitted equivalence when no request is rejected |

The central check is structural: under uniform capacity and global saturation
with aggregate shortage, admitted feedback is common-mode, so gauge projection
keeps the pressure state at zero; requested feedback contains the centered
request imbalance. Total overflow and requested-load balance are reported as
separate quantities. Lower overflow is not predicted during persistent global
saturation because aggregate shortage fixes its total.

The first-change metric is the first step where the aggregate request-count
vector differs from its initial value; it does not track individual token
assignments. The seed-bootstrap interval describes variability only under the declared
synthetic profile generator. A favorable time-mean total-variation comparison
is not a theorem, is not evidence of generalization, and is not a substitute
for the later real-data training experiment. The suite does not resolve the
separate open question of a theorem that separates MoE Top-K/gauge structure
from a broad adaptive-testing benchmark.

## Operational notes

- Default execution uses CPU; pass --device cuda to require CUDA explicitly.
- Deterministic algorithms are enabled and unsupported deterministic
  operations fail loudly.
- The manifest records protocol SHA-256, per-file source hashes and a matching
  source snapshot, Git commit/status, Python and PyTorch versions, device, and
  whether diagnostic overrides were used.
- If an invariant fails, treat the suite as invalid. Diagnose and document the
  cause before changing the protocol or rerunning; never silently discard a
  seed.

# Megatron-Core feedback experiment

This is a separate real-model training track. It does not modify the existing
synthetic `moe_control` package or its published run artifacts.

## What the implementation does

`adapter.py` hooks Megatron-Core's `TopKRouter` and the global-batch expert-bias
update. In requested-feedback runs, it counts the map before capacity dropping
and uses those counts in place of post-drop counts. In admitted-feedback runs,
it consumes Megatron's existing post-drop counter and does not compute the extra
pre-drop histogram. Drop-off feedback runs capture both maps, which must agree:

- `requested`: use the pre-drop assignment counts;
- `admitted`: use the post-drop assignment counts;
- `none`: no bias controller and no auxiliary balance loss;
- `aux_loss`: use Megatron's standard auxiliary load-balancing loss.

`scope=global` all-reduces the selected count vector before the sign update.
`scope=local` computes the sign update on each rank's local counts, then averages
the update directions so replicated bias state remains synchronized. The local
and global scopes are deliberately distinct control laws. They are not described
as a communication-free local controller.

The adapter is guarded to Megatron-LM commit
`62c063f2b731b57b1c2031b2b4f4c6a769271ccb` (2026-10-18). The version guard is
intentional: this code hooks framework internals, not a stable plugin API. The
official [router implementation](https://github.com/NVIDIA/Megatron-LM/blob/62c063f2b731b57b1c2031b2b4f4c6a769271ccb/megatron/core/transformer/moe/router.py)
applies token dropping before accumulating its expert-bias counts. Its
[finalization path](https://github.com/NVIDIA/Megatron-LM/blob/62c063f2b731b57b1c2031b2b4f4c6a769271ccb/megatron/core/distributed/finalize_model_grads.py)
updates that state once per global batch; the [drop transform](https://github.com/NVIDIA/Megatron-LM/blob/62c063f2b731b57b1c2031b2b4f4c6a769271ccb/megatron/core/transformer/moe/moe_utils.py)
supports `probs` and `position` policies. This experiment pins `probs` and
derives requested/admitted count vectors from the actual pre/post maps; it does
not treat token composition as interchangeable.

## Run the wiring check first

Run this only on a Linux NVIDIA-GPU machine where the pinned Megatron checkout
and its CUDA/PyTorch dependencies are installed. Check the visible GPU count
before choosing `--nproc-per-node`; each worker requires one visible GPU. The
smoke profile uses generated mock data and a small 2-layer model; it checks the
adapter and the required no-drop equivalence, not language-model quality or the
paper's research claims. The pinned Megatron version rejects expert bias with
its default softmax router score, so the protocol fixes the score function to
sigmoid across every arm, including the auxiliary-loss baseline.

```bash
git -C /path/to/Megatron-LM checkout 62c063f2b731b57b1c2031b2b4f4c6a769271ccb
python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'visible GPUs:', torch.cuda.device_count()); assert torch.cuda.is_available() and torch.cuda.device_count() >= 1"
python experiments/megatron_feedback/run_matrix.py \
  --megatron-root /path/to/Megatron-LM \
  --output-root "$PWD/experiments/megatron_feedback/runs/smoke_gpu1" \
  --nproc-per-node 1 --device-ids 0 \
  --profile smoke --steps 20 --execute && \
python experiments/megatron_feedback/analyze.py \
  experiments/megatron_feedback/runs/smoke_gpu1
```

The analysis command runs only if training succeeds (`&&`). If you have more
visible GPUs, increase both `--nproc-per-node` and the number of IDs in
`--device-ids` to match. If Megatron is installed in a different Python
environment, invoke both commands with that environment's Python executable.
The adapter rejects any checkout whose Git SHA differs from the pinned one.

`telemetry_checks.json` must have no violations and must report one matched
drop-off pair. With dropping disabled, requested and admitted assignments and
the global-scope controller trajectories must match for the same seed. Do not
start the paper profile if this check fails.

## Real-data profile

The paper profile is deliberately not launched until the data, tokenizer, GPU
allocation, and training budget are set. It uses the protocol's 8-expert, Top-2,
12-layer configuration and expands into 105 runs (five paired seeds, three
capacity settings, no-balance and auxiliary-loss controls, the unmodified native
admitted-bias reference, and requested/admitted feedback under local/global
scope). Set the step budget before examining outcomes. Provide
Megatron's preprocessed data and tokenizer arguments explicitly:

```bash
python experiments/megatron_feedback/run_matrix.py \
  --megatron-root /path/to/Megatron-LM \
  --output-root "$PWD/experiments/megatron_feedback/runs/paper" \
  --nproc-per-node 8 --device-ids 0,1,2,3,4,5,6,7 \
  --profile paper --data-mode real --steps 5000 \
  --data-fingerprint SHA256_OF_DATA_AND_TOKENIZER_MANIFEST --execute \
  --megatron-arg=--data-path --megatron-arg=/data/preprocessed/train_prefix \
  --megatron-arg=--split --megatron-arg=949,50,1 \
  --megatron-arg=--tokenizer-type --megatron-arg=HuggingFaceTokenizer \
  --megatron-arg=--tokenizer-model --megatron-arg=/data/tokenizer
```

The 5000-step value is an example command value, not a justified statistical or
compute budget. Select and record the budget before the full run. Add
`--save-checkpoints` only after estimating the storage required for all runs.
Real data
requires a fixed train/validation split and identical data arguments across all
cells. Keep tokenizer and data preprocessing/cache paths fixed. The generated
run manifest stores the exact command and adapter/protocol hashes.

## Outputs and analysis

Each run is written once under the chosen output root and contains `cell.json`,
`manifest.json`, `command.txt`, `stdout.log`, and rank-local
`telemetry/*.jsonl` for the adapter's requested/admitted feedback arms. Add `--save-checkpoints` to save a final
checkpoint for every run; plan storage before enabling it. The telemetry writer
does not add a reduction collective; global diagnostics are reconstructed by
summing rank-local counts offline. The native-admitted reference runs the
unmodified Megatron update with the adapter disabled, so its step-time
comparison estimates framework-hook/logging overhead. `analyze.py` checks
`admitted <= requested` where requested telemetry is collected, drop-off
equality, top-k assignment-count divisibility, and paired
requested/admitted trajectories in the mandatory negative control.

The pre-registered primary outcome is validation negative log-likelihood at a
fixed seen-token budget. The secondary outcomes and control conditions are in
[`protocol.yaml`](protocol.yaml). Megatron stdout is retained as the source for
training/validation loss and throughput. The adapter's instrumentation and
Python hooks may affect throughput; quantify that overhead before using timing
as a result. Do not interpret the mock-data smoke run as empirical evidence.

## Important implementation boundaries

- The source experiment uses Megatron's own token drop map and `probs` drop
  ordering. It does not reimplement model dispatch in this repository.
- The all-reduce group follows the pinned framework's existing TP×DP×CP update
  group. Expert-parallel behavior must match the selected topology.
- The local-scope update averages rank-local sign actions to preserve identical
  replicated biases. This is an explicitly defined distributed controller, not
  a claim that independent per-rank bias states are valid.
- First validation must use the default non-fused, non-CUDA-graph router path.
  Re-enable those optimizations only after the hooks are verified against that
  code path.
- The first run is the smoke command above. The full profile needs an agreed
  dataset/tokenizer, available GPU topology, and a predeclared token/step budget.

#!/usr/bin/env bash
# v2 hardened control-experiment matrix (protocol 0.2.0).
#
# Run from the repository root with the venv active:
#   bash scripts/run_v2_matrix.sh
#
# Writes immutable run directories under docs/control_experiment_results/v2_runs/.
# Does NOT touch docs/control_experiment_results/runs/ (v1 artifacts frozen).
#
# Inventory: 93 runs
#   head-to-head: 5 scenarios x 7 controllers x seeds {17, 23} = 70
#   thrash mapping: 9 pressure-eta + 7 bias-gamma (shortage) +
#                   7 bias-gamma (exact_total, uncensored) = 23
set -euo pipefail

OUT=docs/control_experiment_results/v2_runs
CTLS="requested,admitted,admitted_centered,capacity_relative,bias_integral,requested_leaky,requested_no_projection"
PY=.venv/bin/python

run() { $PY -m moe_control.cli experiment.output_root=$OUT experiment.protocol_version=0.2.0 "$@"; }

# --- head-to-head matrix -------------------------------------------------
for sd in 17 23; do
  run scenario=saturation_windup capacity=windup_tight controller="$CTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1200 --multirun
  run scenario=adversarial_init capacity=shortage controller="$CTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 --multirun
  run scenario=adversarial_batches capacity=exact_total controller="$CTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1000 --multirun
  run scenario=specialization_probe capacity=shortage controller="$CTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 --multirun
  run scenario=small_batch capacity=small_shortage controller="$CTLS" \
      experiment.seed=$sd scenario.seed=$sd problem.tokens=64 experiment.steps=800 --multirun
done

# --- thrash mapping: pressure eta sweep (3+ orders of magnitude) --------
for eta in 0.001 0.003 0.01 0.03 0.1 0.3 1.0 3.0 10.0; do
  run scenario=demand_shift capacity=shortage controller=requested \
      controller.step_size=$eta experiment.steps=1000 experiment.name=thrash_eta_sweep
done

# --- thrash mapping: bias gamma sweep (2+ orders of magnitude) -----------
# On shortage the bias controller is censored by global saturation, so the
# informative sweep uses exact_total capacity (partial saturation only).
for bg in 0.0001 0.0003 0.001 0.003 0.01 0.03 0.1; do
  run scenario=demand_shift capacity=shortage controller=bias_integral \
      controller.bias_gamma=$bg experiment.steps=1000 experiment.name=thrash_gamma_sweep
  run scenario=demand_shift capacity=exact_total controller=bias_integral \
      controller.bias_gamma=$bg experiment.steps=1000 experiment.name=thrash_gamma_sweep_exact
done

echo "v2 matrix complete: $(ls $OUT | wc -l) run directories in $OUT"

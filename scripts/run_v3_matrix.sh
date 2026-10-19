#!/usr/bin/env bash
# v3 "utmost version" control-experiment matrix (protocol 0.3.0).
#
# Run from the repository root with the venv active:
#   bash scripts/run_v3_matrix.sh
#
# Writes new runs under ignored results/reproductions/v3_runs/.
# The archived v1/v2/v3 artifacts under docs/research_history/ remain unchanged.
#
# Inventory: 79 runs
#   T1 non-uniform target: 2 capacity regimes x 6 controllers x seeds {17,23,42} = 36
#   T2 anti-windup on v2 scenarios: 5 scenarios x seeds {17,23} = 10
#   T3 dedicated re-verification fresh runs = 11
#     - flip-invariant: shortage x requested x etas {0.05,0.1,0.2,0.4} x seeds {23,42} = 8
#     - freeze retest: shortage x {requested,admitted} x seed 99 = 2
#     - requested_leaky adversarial_init x seed 42 = 1
#   T4 theorem prospective check: shortage x requested x etas {0.15,0.3} x seed 17 = 2
#   T5 DeepSeek head-to-head extension: 2 controllers x 5 scenarios x seeds {42,99} = 20
set -euo pipefail

OUT=results/reproductions/v3_runs
PY=.venv/bin/python
# Feasible integer-count explicit target: K*T*mu = [384,352,320,288,256,224,128,96].
MU="problem.target=explicit problem.target_weights=[0.1875,0.171875,0.15625,0.140625,0.125,0.109375,0.0625,0.046875]"

run() { $PY -m moe_control.cli experiment.output_root=$OUT experiment.protocol_version=0.3.0 "$@"; }

# --- T1: non-uniform target x heterogeneous capacity -----------------------
T1CTLS="requested,admitted,admitted_centered,capacity_relative,admitted_antiwindup,bias_integral"
for sd in 17 23 42; do
  for cap in hetero_balanced hetero_shortage; do
    run scenario=nonuniform_target capacity=$cap controller="$T1CTLS" \
        experiment.seed=$sd scenario.seed=$sd experiment.steps=800 \
        experiment.name=nonuniform_target_test $MU --multirun
  done
done

# --- T2: anti-windup controller on the v2 hardened scenarios ----------------
for sd in 17 23; do
  run scenario=saturation_windup capacity=windup_tight controller=admitted_antiwindup \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1200 \
      experiment.name=antiwindup_probe
  run scenario=adversarial_init capacity=shortage controller=admitted_antiwindup \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 \
      experiment.name=antiwindup_probe
  run scenario=adversarial_batches capacity=exact_total controller=admitted_antiwindup \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1000 \
      experiment.name=antiwindup_probe
  run scenario=specialization_probe capacity=shortage controller=admitted_antiwindup \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 \
      experiment.name=antiwindup_probe
  run scenario=small_batch capacity=small_shortage controller=admitted_antiwindup \
      experiment.seed=$sd scenario.seed=$sd problem.tokens=64 experiment.steps=800 \
      experiment.name=antiwindup_probe
done

# --- T3: dedicated re-verification (fresh runs) -----------------------------
# flip-invariant across seeds: shortage x requested x 4 etas x seeds {23,42}
for sd in 23 42; do
  for eta in 0.05 0.1 0.2 0.4; do
    run scenario=shortage capacity=shortage controller=requested \
        controller.step_size=$eta experiment.seed=$sd scenario.seed=$sd \
        experiment.steps=1200 experiment.name=flip_invariant_test
  done
done
# freeze retest at a fresh seed (paired requested/admitted)
for ctl in requested admitted; do
  run scenario=shortage capacity=shortage controller=$ctl \
      experiment.seed=99 scenario.seed=99 experiment.steps=500 \
      experiment.name=freeze_retest
done
# requested_leaky adversarial_init failure at a fresh seed
run scenario=adversarial_init capacity=shortage controller=requested_leaky \
    experiment.seed=42 scenario.seed=42 experiment.steps=800 \
    experiment.name=leaky_retest

# --- T4: theorem prospective check (predict first, then run) ----------------
# Predicted eta*t_flip from the affinity tensor is recorded in
# docs/research_history/control_experiment_results/v3_notes/eta_flip_theorem.md BEFORE these
# runs execute; the verifier checks the observed first-flip steps against it.
for eta in 0.15 0.3; do
  run scenario=shortage capacity=shortage controller=requested \
      controller.step_size=$eta experiment.seed=17 scenario.seed=17 \
      experiment.steps=1200 experiment.name=flip_theorem_prospective
done

# --- T5: DeepSeek head-to-head extension (seeds 42, 99; v2 has 17, 23) -------
H2HCTLS="requested,bias_integral"
for sd in 42 99; do
  run scenario=saturation_windup capacity=windup_tight controller="$H2HCTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1200 \
      experiment.name=deepseek_headtohead --multirun
  run scenario=adversarial_init capacity=shortage controller="$H2HCTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 \
      experiment.name=deepseek_headtohead --multirun
  run scenario=adversarial_batches capacity=exact_total controller="$H2HCTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=1000 \
      experiment.name=deepseek_headtohead --multirun
  run scenario=specialization_probe capacity=shortage controller="$H2HCTLS" \
      experiment.seed=$sd scenario.seed=$sd experiment.steps=800 \
      experiment.name=deepseek_headtohead --multirun
  run scenario=small_batch capacity=small_shortage controller="$H2HCTLS" \
      experiment.seed=$sd scenario.seed=$sd problem.tokens=64 experiment.steps=800 \
      experiment.name=deepseek_headtohead --multirun
done

echo "v3 matrix complete: $(ls $OUT | wc -l) run directories in $OUT"

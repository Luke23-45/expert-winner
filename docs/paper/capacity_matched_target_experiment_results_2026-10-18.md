# Results: capacity-matched target versus uniform target

**Theorem:** [`capacity_matched_target_theorem_2026-10-18.md`](capacity_matched_target_theorem_2026-10-18.md)  
**Locked protocol:** [`capacity_matched_target_experiment_protocol_2026-10-18.md`](capacity_matched_target_experiment_protocol_2026-10-18.md)  
**Runner:** [`../../scripts/run_capacity_matched_target_experiment.py`](../../scripts/run_capacity_matched_target_experiment.py)  
**Artifacts:** [`../../results/capacity_matched_target_2026-10-18/`](../../results/capacity_matched_target_2026-10-18/)

## Execution and controls

The run used `E=4`, `K={1,2,3}`, `T={2304,9216}`, 12 paired plants per
`(K,T)`, horizons through 64, and both static-batch and fresh-batch regimes.
It produced 5,040 plant-horizon-arm rows, 420 arm cells, and 336 paired
contrast cells. All 72 no-clipping full-trajectory controls passed. All
mass-conservation, clipping, overflow-accounting, and initial-cost checks
passed; there were zero Top-K cutoff ties. The protocol and output hashes
are in `summary.json`.

## Main registered comparison

At `T=9216`, `H=64`, fresh-batch regime, the paired cumulative overflow
results (overflow assignments divided by `T`, accumulated over 64 steps)
were:

| K | Uniform target, requested | Uniform target, admitted | Capacity target, requested | Capacity target, admitted | No feedback |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.362 [1.356, 1.368] | 3.764 [3.750, 3.779] | 0.545 [0.526, 0.563] | 0.696 [0.678, 0.713] | 1.342 [1.326, 1.358] |
| 2 | 1.374 [1.365, 1.382] | 3.403 [3.387, 3.419] | 0.623 [0.603, 0.643] | 0.797 [0.783, 0.810] | 1.372 [1.347, 1.397] |
| 3 | 1.364 [1.359, 1.369] | 4.046 [4.038, 4.055] | 0.540 [0.524, 0.556] | 0.640 [0.629, 0.650] | 1.365 [1.339, 1.390] |

Intervals are 95% t intervals across the 12 arm replicates; they are
marginal arm intervals, not paired-difference intervals. The registered
paired-contrast table is the appropriate comparison:

- With a uniform target, admitted feedback had higher cumulative overflow
  than requested feedback in every replicate for all three `K` values; the
  paired mean gaps were `2.402`, `2.030`, and `2.682`.
- With a capacity-matched target, admitted feedback still had higher
  cumulative overflow than requested feedback in this fixed update class;
  the paired gaps fell to `0.151`, `0.174`, and `0.100`, with requested
  feedback lower in all 12/12 seeds for each `K`.
- Capacity-target admitted feedback had lower cumulative overflow than
  no-feedback in all 12 paired plants for every `K`; mean paired changes
  were `-0.646`, `-0.575`, and `-0.725`.
- The target-by-signal interaction was negative for all three `K` values
  (`-2.251`, `-1.856`, `-2.583`), consistent with the theorem's diagnosis
  that the large admitted-versus-requested gap in the uniform-target family
  depends strongly on target mismatch.

The matched-target population corollary proves requested-feedback overflow
is no greater than admitted-feedback overflow at every round for this direct
update class. The fresh-batch finite experiment has the same ordering in all
12/12 seeds for every `K`; this is empirical confirmation for the registered
batch sizes, not a proof about finite-batch stochastic trajectories.

Full cell and contrast tables are in `cells.csv` and `contrasts.csv`.

## Check against the dynamics

The registered finite-`T` symmetric mean-feedback recurrence's 95% cell
interval covered the simulated mean in 62/84 capacity-target cells for
`T=9216`, across both temporal regimes and all registered horizons. At
`H=64` in the fresh regime it covered 4/6 capacity-target signal/`K` cells;
both `K=3` cells missed. This is not uniform coverage and must remain visible
in any paper. Fresh-batch capacity-target means at `H=64` were close to that
finite-`T` recurrence for `K=1,2` and modestly above it for `K=3`.

The population-limit recurrence predicts lower cumulative overflow than the
finite-`T` recurrence over this finite horizon. It is the iterated population
theorem, not the finite-`T` stochastic trajectory; the discrepancy is
especially large for capacity-target requested feedback. The experiment
therefore supports the finite-`T` mean-field comparator more directly than
the population-limit magnitudes at `H=64`. It does **not** verify a
fixed-batch-size infinite-horizon limit.

## Interpretation

The experiment supports a specific correction to the original story: in
this one-short-capacity family, the severe admitted-feedback overflow under
the uniform target is not evidence that admitted counts have lost all
control authority. Replacing the uniform target with `C/(K*T)` substantially
reduces overflow under admitted feedback and beats no feedback in the
registered finite-batch runs. Requested feedback remains better than
admitted feedback within the same proportional update class, as expected
from its strictly richer observation.

This is a target-sensitivity and controller-mismatch result in a constructed
synthetic family. It is not a measured telemetry-cost result, a trained-model
gain, evidence of production prevalence, an optimal-policy comparison, or a
separation from adaptive testing. Every finite affinity plant still has the
exact outcome-map reduction documented in the benchmark gate. The theorem
and experiment sharpen the existing research line but do not close the
top-conference novelty gate.

## Reproducibility

The run summary is `../../results/capacity_matched_target_2026-10-18/summary.json`.
It records:

- protocol SHA-256: `1dd730249ddd497df9f09ef5c27ea2dba776b0b245822358ab02add6a97add00`
- runner SHA-256: `d9ceecf2d5688510979f1723b64ef3067494625de6f238267b561d3829a1e806`
- plant rows SHA-256: `02eb3f130f274e02c77fee84bbb650b5a41e435a3ddbab62ccd5cf7599e3346d`
- cell summary SHA-256: `c11438b7cf340cebd990c4ebf4e02d7808b63f488f0f1652fca4852e128852aa`
- contrast summary SHA-256: `13f479c530d9f5366834504efc8c431ba8234764f97e26c87dab7b2b22be149f`

# Results: admitted-only reconstruction with a capacity-relative target

**Theorem:** [`single_saturation_signal_reconstruction_theorem_2026-10-17.md`](single_saturation_signal_reconstruction_theorem_2026-10-17.md)

**Locked protocol:** [`capacity_relative_reconstruction_experiment_protocol_2026-10-17.md`](capacity_relative_reconstruction_experiment_protocol_2026-10-17.md)

**Runner:** [`../../scripts/run_capacity_relative_reconstruction.py`](../../scripts/run_capacity_relative_reconstruction.py)

## Reproducibility and invariant checks

The run used the fixed protocol: Top-1, four experts, iid standard Gumbel
affinities, 50 paired static plants at each `T in {2304,9216}`, exact-total
capacities `(T/8,7T/24,7T/24,7T/24)`, `eta=1`, and eight routing/update
steps. All 100 plants had exactly one observed saturated coordinate at every
step. The admitted-only reconstruction recovered the request vector exactly
on every step. Its capacity-relative pressures and routes matched the
requested-capacity arm exactly on all 100 plants. No fallback was needed;
there were no score ties. All 100 no-clipping controls and all mass,
load-bound, clipping, and overflow identities passed.

| Artifact | SHA-256 |
|---|---|
| Protocol | `a218f5bfbed4ff27b751d1593d5d8bfdc9dcaad3df3e7ef4afde29c581bb5f45` |
| Runner | `497048be60c1b397ddff3f960d13ecda26000bc476b2aa24c327d223e6fdd110` |
| Plant rows | `5eadcabe854c987c049b17e8b3b4974643d5114adab8085cd48155290cab8f9b` |
| Step rows | `a46f7d31810702c7dbd61bbcd76d08b885df1efc4824c599e145d317100a118a` |
| Summary | `f91282bba79c6e17c4f865db4f711647b1e62b8545765215b3610b63106b5225` |

The complete records are in [`../../results/capacity_relative_reconstruction/plants.csv`](../../results/capacity_relative_reconstruction/plants.csv),
[`../../results/capacity_relative_reconstruction/steps.csv`](../../results/capacity_relative_reconstruction/steps.csv),
and [`../../results/capacity_relative_reconstruction/summary.json`](../../results/capacity_relative_reconstruction/summary.json).

## Eight-step cumulative overflow

Overflow is summed over the eight routing rounds and divided by `T`. Each
cell reports 50 plants and a paired-mean 95% t interval. The population
reference is the exact Gumbel Top-1 recurrence in the protocol.

| `T` | Controller | Mean cumulative overflow / `T` | 95% interval | Population reference |
|---:|---|---:|---:|---:|
| 2,304 | Requested, uniform target | 0.997682 | [0.988409, 1.006955] | 1.000000 |
| 2,304 | Admitted, uniform target | 1.643950 | [1.627896, 1.660003] | 1.642688 |
| 2,304 | Requested, capacity-relative | 0.495686 | [0.486944, 0.504428] | 0.496526 |
| 2,304 | Admitted, capacity-relative, direct | 0.807422 | [0.791464, 0.823379] | 0.814562 |
| 2,304 | Admitted, reconstructed, capacity-relative | 0.495686 | [0.486944, 0.504428] | 0.496526 |
| 9,216 | Requested, uniform target | 1.001452 | [0.996210, 1.006694] | 1.000000 |
| 9,216 | Admitted, uniform target | 1.646261 | [1.636608, 1.655913] | 1.642688 |
| 9,216 | Requested, capacity-relative | 0.495753 | [0.490789, 0.500717] | 0.496526 |
| 9,216 | Admitted, capacity-relative, direct | 0.815924 | [0.806712, 0.825137] | 0.814562 |
| 9,216 | Admitted, reconstructed, capacity-relative | 0.495753 | [0.490789, 0.500717] | 0.496526 |

For each T, the reconstructed admitted arm and requested capacity-relative
arm have exactly equal cumulative costs on every seed. Relative to requested
uniform-target feedback, capacity-relative feedback reduces cumulative
overflow by paired means `0.501997` (`T=2304`, 95% CI `[0.495970,0.508023]`)
and `0.505699` (`T=9216`, CI `[0.503048,0.508350]`). Relative to direct
admitted capacity-relative feedback, reconstruction reduces it by `0.311736`
(`[0.302423,0.321049]`) and `0.320171` (`[0.315118,0.325224]`). Each paired
difference is positive on all 50 seeds at both batch sizes.

## What this establishes

This is direct evidence that the earlier positive overflow gap under a
uniform target does not, by itself, establish that requested telemetry is
needed in the one-short family. With the formal capacity-relative target,
admitted counts determine the full request vector whenever at most one
coordinate is clipped; using that reconstruction exactly reproduces the
requested-capacity controller without a separate request-count signal. The
experiment also shows that applying the capacity-relative formula directly
to clipped counts is slower than reconstructing first, though both beat the
uniform-target arms in this registered design.

This remains a fixed-horizon static-batch synthetic audit and a theorem for
one specific symmetric population family. It does not prove the
reconstruction condition in regimes with multiple saturated experts, a
universal overflow-optimal policy, a physical system gain, or separation
from the finite outcome-map benchmark. The relevant distinction is now
explicit: multiple-saturation fibers can hide request allocation; a
one-saturation family does not, and a mismatched uniform target can create
an apparent signal advantage even when admitted telemetry is sufficient.

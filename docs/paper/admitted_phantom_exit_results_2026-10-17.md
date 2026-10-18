# Exact synthetic audit: admitted-feedback exit from global saturation

**Run date:** 2026-10-17  
**Branch/base revision:** `feat/research-censored-feedback`, `e1648512e22844f4d8e892577dfc011f83ac307a`  
**Protocol:** [admitted_phantom_exit_protocol_2026-10-17.md](admitted_phantom_exit_protocol_2026-10-17.md)  
**Executable:** [`scripts/run_admitted_saturation_exit.py`](../../scripts/run_admitted_saturation_exit.py)  
**Artifacts:** [`summary.json`](../../results/admitted_saturation_exit/summary.json), [`trajectories.csv`](../../results/admitted_saturation_exit/trajectories.csv)

The post-run T6b diagnostic uses [`scripts/audit_t6b_randomized_small.py`](../../scripts/audit_t6b_randomized_small.py) and writes [`t6b_property_audit.json`](../../results/admitted_saturation_exit/t6b_property_audit.json). It is kept separate from the preregistered T6a protocol.

## Question and formal result

The pre-run protocol checks Theorem T6a in [`formal_core.md`](formal_core.md): with fixed affinities and positive per-expert capacities, the canonical proportional admitted controller `(A)` has a constant nonzero gauge direction while every expert is saturated. If the `K` smallest coordinates of

\[
v=P_0\!\left(C/(KT)-\mu\right)
\]

are strictly separated from the remaining coordinates, their pressure penalties eventually dominate every token's affinity differences. At that point all tokens select those `K` experts, so some positive-capacity expert outside that set receives no requests and global saturation must have ended. T6a gives an explicit conservative upper bound `N_sep` using tokenwise pairwise score-crossing thresholds.

The T6a proof is deterministic and covers any fixed affinity matrix satisfying its assumptions. The pre-run protocol checks its arithmetic and trajectory implementation at one finite parameter point across 20 paired rational score perturbations. After inspecting that run, T6b was derived as a sharper capacity-slack refinement; it is post-run theory and its checks below are explicitly exploratory rather than pre-registered. Neither experiment is the proof: the analytic arguments are.

## Fixed protocol

- `E=4`, `K=2`, `T=128`.
- `C=(40,42,43,44)` and `mu=(2/5,3/10,1/5,1/10)`.
- `eta=1/10`, `gamma=1`, `delta=0`, and `q_0=0`.
- Ring-pair multiplicities `(40,24,32,32)` yield initial requests `(72,64,56,64)`, so every expert begins saturated.
- Twenty deterministic rational affinity perturbations, seeds `0..19`; each seed's same affinity batch is paired across admitted feedback `(A)`, requested feedback `(R)`, and no feedback.
- State, score, routing, clipping, and accounting calculations use exact `Fraction` arithmetic.

The protocol and implementation hashes are recorded in `summary.json`. The artifact hashes from this rerun are:

| Artifact | SHA-256 |
|---|---|
| `summary.json` | `846fd0476224126a68637461d02d1ada7e55e5b8fefcd35f1d383797e37fa04b` |
| `trajectories.csv` | `6ca82732576d3ac3418cbe6b7d4ddf43ca199f329be4b67cc18ca298360bac64` |

The original protocol hash is `d09385d2fba0a7bf9b1af1836faeedb2a5d6d8ff658abe509ab118a7996a059c`; the post-run-refined script hash is `ffa22986fc06193b3a6f9d8990f11ce5c904f3b398dd66dfdc7b85765210eacb`.

## Results

All 20 runs had the same exact event indices:

| Quantity | State index |
|---|---:|
| Conservative T6a bound `N_sep` | 30 |
| T6b capacity-slack order-statistic bound `N_e*` | 9 |
| Predicted first exit from the open-loop saturated trajectory | 9 |
| Observed first exit under admitted feedback `(A)` | 9 |
| First route change under `(A)` | 9 |
| First exit under requested feedback `(R)` | 11 |
| First exit under no feedback | None in the run horizon |

At the admitted arm's exit state, total overflow was 99. This is a state-specific value, not a cumulative advantage claim. The gap `9 < 30` shows that the all-token common-Top-K sufficient condition is conservative for this plant: saturation breaks before all tokens have converged to the asymptotic minimum-slope set.

For this plant, initial global saturation admits all `sum(C)=169` available
slots, so overflow is `KT-sum(C)=87`, the per-batch lower bound. At exit,
overflow rises to 99 in every seed. This follows structurally: with fixed
`sum(R)=KT`, any unsaturated expert makes `sum(A)<sum(C)`, hence
`sum(J)=KT-sum(A)>KT-sum(C)`. Thus T6b proves an exit event, and in this
shortage regime that event leaves the minimum-overflow set; it is not evidence
that the controller improves overflow.

For each seed, the T6b witness is the maximum-slope expert `e*=3`, with 64 initial requests and capacity 44. Therefore 21 of its initially routed tokens must leave before its count is strictly below capacity. The `21`st token-leaving threshold is state 9, exactly where global saturation first fails in the simulated admitted arm. This tighter result uses per-token Top-K order events and capacity slack, not the sufficient event that every token has converged to the same set.

All six exact checks recorded by the executable passed for every seed:

1. Initial global saturation.
2. Strict `K`/`K+1` slope separation and positive capacities.
3. The predicted open-loop exit is finite and observed exit occurs by `N_sep`.
4. The admitted-controller route counts and pressure state match the exact constant-feedback open-loop path through the first unsaturated state.
5. The no-feedback arm stays at its initial saturated state.
6. Requested mass conservation, canonical clipping, and overflow accounting hold at every state.

The protocol's separate requested-feedback arm is retained as paired
descriptive context only; the protocol prespecified no ranking of controller
quality.

The four **post-run T6b audit checks** also passed for every seed: each order-statistic bound is finite; observed exit is no later than the bound; the bound is no larger than `N_sep`; and the registered plant's bound equals the observed exit state. Equality is an outcome for this plant, not a general equality theorem.

### Separate post-run finite-family diagnostic

To check the order-statistic derivation beyond the registered plant, a separate deterministic generator produced 100 small `E=4, K=2, T=8` plants with varying rational targets, positive capacities, and exact affinity perturbations. The generator retained only initially globally saturated cases with a strict `K`/`K+1` slope gap. Exact rational routing verified `observed exit <= N_e* <= N_sep` in all 100 cases; `N_e*` equaled the observed exit in 92. Across these cases, `N_e*` ranged from 26 to 792 and `N_sep` from 36 to 2,829.

This is a post-run property audit, not a preregistered confirmation, statistical sample, or proof. The 100 plants are small variants generated by one script, and all use `E=4, K=2, T=8`. Full parameters and per-case outcomes are in the JSON artifact. Its SHA-256 is `0c44f32c82bbadafef70c9dfd834b5827e6a04343f1784778b72682f37bb5dbd`; the generator script SHA-256 is `cf838f0ff2a7d6b2e9379e3d8115f718bec1b78d67b8a1be5ba0b08e169ed616`.

## What this establishes—and what it does not

**Established:** T6a's finite-time exit theorem and T6b's capacity-slack order-statistic refinement under their stated fixed-affinity assumptions, plus an exact-rational implementation audit of one constructed plant. The plant tests the formal proportional controller `(A)`, not the separate signed `bias_integral` controller.

**Not established:** that `(A)` has lower overflow than `(R)`; that leaving global saturation improves cumulative overflow, training loss, or serving quality; that the result is typical across MoE workloads; that the theorem separates Top-K from general adaptive testing; or that this is a top-conference-level contribution on its own. The 20 perturbations are paired perturbations of one designed plant, not independent workload samples.

The event ordering `(A)` at 9 versus `(R)` at 11 is descriptive only. Since post-exit paths and objective tradeoffs are not covered by T6a, it must not be presented as an admitted-feedback performance win.

## Literature/source check relevant to the model

The primary DeepSeek-V2 paper describes a **device-level** computational budget and drops low-affinity routes to meet it ([§2.2.4](https://arxiv.org/abs/2405.04434)); its expert-balance statistic is based on the number of tokens selecting each expert ([Eqs. 23–25](https://arxiv.org/abs/2405.04434)). This supports a device-coupled dropping mechanism, but not the claim that DeepSeek-V2 runs an admitted-count controller.

The pinned Megatron-Core audit recorded in [the professor-report reconciliation](professor_report1_reconciliation_and_experiment.md) is a closer instantiation of the existing per-expert model: capacity dropping is applied per expert, so `A_e=min(R_e,C_e)`; the retention ranking changes token identities, not admitted counts. The current official API also describes token dropping as an optional step in its TopKRouter workflow ([Megatron Core router API](https://docs.nvidia.com/megatron-core/developer-guide/latest/apidocs/core/core.transformer.moe.router.html)).

Therefore, this experiment retains the canonical per-expert clipping map. It does not silently substitute the device-level DeepSeek-V2 mechanism or assert that score-ranked per-expert retention changes count feedback.

## Research implication

T6a is a valid scoped theorem, but it does not close the open benchmark-reduction issue in the current research status. Its finite arrangement/event-time conclusion is exactly computable from piecewise-constant Top-K outcomes, and the project has established exact polyhedral active-testing representations for fixed plants. A conference-level claim still needs a family-level quantitative statement that uses Top-K/gauge restrictions and does not transfer unchanged to that benchmark. Do not start model training on this result alone.

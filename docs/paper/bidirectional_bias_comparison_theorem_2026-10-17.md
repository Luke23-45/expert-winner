# Two-sided overflow comparison for requested- and admitted-count bias feedback

**Status:** exact constructive theorem plus an exact-rational controlled audit.
This is a result for the existing per-expert clipping model and the signed
expert-bias controller. It is not a result for the proportional gauge-pressure
controller in `formal.md`.

## Main statement

There is no universal cumulative-overflow ordering between requested-count and
admitted-count signed-bias feedback, even with the same deterministic Top-K
router, fixed affinities, canonical per-expert admission
`A_e=min(R_e,C_e)`, zero initial bias, and a common positive step size. Both
strict rankings occur on parameterized replicated families with strict Top-K
cutoff margins:

1. The existing Top-2 family in Theorem P2f of
   [`formal_core.md`](formal_core.md) has admitted feedback strictly below
   requested feedback in cumulative overflow for every horizon `H>=4` and
   every `alpha in (1/5,11/40)`.
2. The uniform-capacity family below has requested feedback strictly below
   admitted feedback at horizon `H=120`, with a strict gap of `531m` for
   every integer row-replication factor `m>=1`. The gap holds throughout an
   entrywise open neighborhood of its affinity matrix.

This disproves any claim that either signal universally dominates the other
for overflow under this controller/model class. It does not yet characterize
which signal wins from instance parameters, prove a class-level control
limitation, or assign a system cost to collecting either signal.

## Uniform-capacity requested-better family

Use `E=8`, `K=2`, `T=128`, uniform capacity `C_e=32`, step size
`alpha=1/40`, zero initial bias, and horizon `H=120`. Scores are
`a_{t,e}+b_e`; routing selects the top two, breaking exact ties by lower
expert index. The feedback and gauge-centered signed update are exactly those
defined in the next section. The fixed 128-by-8 affinity matrix is stored as
exact decimal rationals in
[`uniform_capacity_seed5_affinities.csv`](fixtures/uniform_capacity_seed5_affinities.csv).
Its SHA-256 is
`b7cb4002f5aa7a0ddc384fbacaa7617ca744534e5a2bcb0987bfc1ab2c43bc2d`.
It was generated from the existing ring-pair synthetic family with edge
counts `(30,8,22,10,26,6,18,8)`, CPU float64 noise in `[0,0.02)`, seed 5,
then rationalized by each value's round-trip decimal representation. The
checked-in matrix, not a fresh RNG draw, is authoritative for the exact
result.

The exact-rational trajectory gives:

| Feedback | Cumulative overflow over 120 batches | Minimum Top-2 cutoff margin |
|---|---:|---:|
| Admitted | 2,449 | `542933344799/10000000000000000` |
| Requested | 1,918 | `114112300983/2500000000000000` |
| None | 1,920 | `37806719560039579/10000000000000000` |

All routes are strict for all 120 states, and no arm reaches global
saturation. Requested feedback therefore saves exactly 531 overflow
assignments relative to admitted feedback, and 2 relative to no feedback.
The path margins give an open robustness radius: every entrywise perturbation
of magnitude at most `1/100000` changes a pairwise score difference by at most
`1/50000`, less than the minimum margin of either controlled arm. By
induction, the 120-step routes, counts, feedback, and overflow remain fixed.
Ten exact-rational perturbation trials pass. Explicit row-replication checks
at `m=1,2` give overflow `2449m` (admitted), `1918m` (requested), and `1920m`
(none); the same replication argument proves these identities for every
integer `m>=1`.

Reproduce with
[`audit_uniform_cap_requested_better.py`](../../scripts/audit_uniform_cap_requested_better.py).
The exact result and source hashes are in
[`uniform_cap_requested_better.json`](../../results/bidirectional_bias_comparison/uniform_cap_requested_better.json).

## Additional heterogeneous-capacity witness

The independent `E=4`, `K=2`, `T=8`, `C=(1,2,3,3)` construction below is a
second requested-better witness at `H=34`: it has the exact gap `2m` and a
larger sampled perturbation audit. It is retained as a compact hand-readable
example; the uniform-capacity construction above is the stronger evidence
that non-dominance does not depend on heterogeneous capacities.

### Definitions for the heterogeneous witness

Take `E=4`, `K=2`, `T=8`, capacities `C=(1,2,3,3)`, gain `gamma=1/100`,
and zero initial bias. The eight affinity rows are the following exact
rational numbers (the displayed decimals are terminating rationals):

```text
( 0.819180,  1.028240,  0.056863, -0.175017)
( 1.160296,  0.072379, -0.139075,  1.158428)
(-0.002522,  1.170735,  0.186723,  0.836694)
( 0.022639,  1.145491, -0.166813,  0.971930)
( 0.040438,  0.897060,  0.196673,  0.937628)
( 0.015482,  0.153365,  0.812693,  0.913671)
( 0.187260, -0.087490,  0.845061,  0.929071)
(-0.097150,  0.118014,  0.859227,  0.800792)
```

At batch `n`, route each row to its two largest `a_{t,e}+b_e` scores, with
lower expert index winning any exact tie. Set `L=R` for requested feedback and
`L=A` for admitted feedback, and update

```text
u_e = sign(mean(L) - L_e)
b_{n+1} = P_0(b_n + gamma*u),
```

where `P_0` subtracts the coordinate mean. Per-batch overflow is
`J_n=sum_e(R_{n,e}-A_{n,e})`.

For replication factor `m`, repeat every affinity row `m` times and use
capacities `mC`. The bias gain and initial bias are unchanged.

### Exact trajectory and overflow

Under both feedback signals the initial requests are `R_0=(2,4,3,7)`, so
the initial state is globally saturated and incurs overflow `7`. Under
admitted feedback, states `n=0,...,32` retain this request vector. At state
`n=33`, requests become `(3,5,1,7)`, with admitted counts `(1,2,1,3)` and
overflow `9`. Hence

```text
J_34(admitted) = 33*7 + 9 = 240.
```

Under requested feedback, state `n=33` has requests `(2,4,4,6)`, still
globally saturated, and overflow remains `7`. The first unsaturated state is
`n=46`, outside the `H=34` comparison. Thus

```text
J_34(requested) = 34*7 = 238.
```

With no feedback the initial request vector persists, so `J_34(none)=238`.
For replication factor `m`, all request/admission counts and overflow values
scale by `m`, while the sign updates and bias path are unchanged. Therefore

```text
J_34(admitted)=240m,  J_34(requested)=238m,  J_34(none)=238m.
```

In particular, requested feedback saves exactly `2m` overflow assignments
against admitted feedback on this family. The conclusion is an exact
finite-horizon statement, not an asymptotic average-cost claim.

### Strict-margin robustness

The minimum Top-2 cutoff margin over states `0,...,33` is exactly
`21/31250` for the admitted arm and `9971/1000000` for the requested arm.
Therefore both route paths remain unchanged under any entrywise affinity
perturbation of magnitude at most `1/10000`: each pairwise score difference
changes by at most `2/10000`, which is strictly less than `21/31250`. By
induction, unchanged routes imply unchanged counts, sign feedback, and bias;
so the overflow gap `2m` persists throughout that open neighborhood. This
argument does not rely on a tie-breaking event.

The executable exact-rational audit additionally samples 100 deterministic
entrywise perturbations from `{-1/10000,0,1/10000}` and verifies identical
34-step paths and costs. It checks replication factors `m={1,2,5,10}`.

## Proof of the two-sided conclusion

The uniform-capacity construction gives
`J_120(requested)<J_120(admitted)`; the heterogeneous witness also gives
`J_34(requested)<J_34(admitted)`. The existing Theorem P2f gives
`J_H(admitted)<J_H(requested)` for every `H>=4` on its replicated Top-2
family. These are all admissible instances of the stated controller and
per-expert clipping model. A universal ranking in either direction would
contradict one of the two strict inequalities. This proves the non-dominance
statement, including within uniform-capacity instances.

The first construction and its all-horizon proof are recorded in
[`top2_signed_bias_separation_theorem_2026-10-17.md`](top2_signed_bias_separation_theorem_2026-10-17.md).
The uniform-capacity construction is reproducible with
[`audit_uniform_cap_requested_better.py`](../../scripts/audit_uniform_cap_requested_better.py)
and its exact affinity fixture. The heterogeneous construction is
reproducible with
[`audit_bidirectional_bias_comparison.py`](../../scripts/audit_bidirectional_bias_comparison.py);
its machine-readable output is
[`strict_requested_better_witness.json`](../../results/bidirectional_bias_comparison/strict_requested_better_witness.json).

## Interpretation for the professor's proposed candidate

The result makes a precise part of the professor's value-of-information
proposal testable: requested counts do not have a uniformly positive overflow
value against admitted counts, and admitted counts are not uniformly
beneficial either. Therefore the proposed direction must be conditional on
capacity regime and router instance; it cannot claim a universal requested
signal advantage. Theorem P2f and this theorem supply opposite exact
mechanisms in the existing model.

The theorem does **not** prove that this signal choice has positive net value
after measurement or communication costs. The pinned Megatron-Core path
already reduces expert-count telemetry to update its bias, so replacing the
post-drop vector with a pre-drop vector may reuse that collective; an
additional cost is implementation-dependent. Nor does this theorem establish
validation-loss improvement on a trained model.

The score-ordering variant in the professor report also needs a careful
boundary: retaining the top `C_e` routes independently for each expert
changes admitted token identities but always gives count
`A_e=min(R_e,C_e)`. A score-dependent change in the admitted-count vector
requires coupled admission, such as a shared device/group budget. That is a
different model, and the existing group-capacity pilot is an ablation rather
than evidence for the per-expert theorem.

## Paper-level gate

This is a concrete theorem, but by itself it is not yet the final
top-conference contribution. It proves sign-indefinite value for two
parameterized constructions, not a predictive criterion for which signal
wins over a broad family. The remaining research target is to derive
checkable structural conditions on the Top-K affinity arrangement, capacities,
and gain that predict the sign and size of the overflow difference, and to
show that the resulting family-level statement is not simply the general
finite-outcome polyhedral testing reduction. A trained-model experiment should
follow only if that theorem target and the measured marginal telemetry cost
survive those checks.

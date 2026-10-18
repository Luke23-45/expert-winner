# Results: arbitrary-expert Top-1 two-step overflow experiment

**Protocol:** [`top1_e_expert_overflow_protocol_2026-10-17.md`](top1_e_expert_overflow_protocol_2026-10-17.md)  
**Theorem:** [`top1_e_expert_two_step_overflow_theorem_2026-10-17.md`](top1_e_expert_two_step_overflow_theorem_2026-10-17.md)  
**Runner:** [`../../scripts/run_top1_e_expert_overflow.py`](../../scripts/run_top1_e_expert_overflow.py)

## Registered study and execution integrity

The preregistered design varied `E in {3,4,8,16}`, `d in {1/4,1/2,3/4}`,
and `T in {3360,6720,13440}`, with 100 paired affinity matrices in each
`(E,T)` cell. It ran requested, admitted, and no-feedback arms on the same
static matrix, using exact integer score comparisons and the declared
lowest-index tie rule. No parameters or cells were changed after seeing the
outcomes.

The run produced 3,600 plant/gain rows across 36 endpoint cells and 3,600
no-clipping diagnostics. Every registered invariant passed: requested mass
was `T`; admitted counts equaled `min(R,C)`; overflow accounting was exact;
step-zero paired costs agreed; and requested/admitted no-clipping routes and
costs agreed. There were zero exact ties. Every one of the 3,600 paired
plant/gain gaps was strictly positive.

The script was run twice from the checked-in protocol. Both runs produced
byte-identical output:

| Artifact | SHA-256 |
|---|---|
| Protocol | `0506ddbb2a4c7b7012568c9eee32d15b492c7354ad6c286e63eab42f2d4a88cb` |
| Runner | `cabe75119fcff11377411bd9ab25694d9a4c95b7f860198c4bd6981e13e8b19a` |
| Paired plant rows | `fe155751dfd6df793f354ef82675ce11f5603c2aa1c9401f143072feec6a9fb2` |
| Summary | `8d61f58c11a76b7a4019750aaf47e12eb76a0175652987054879e392ad1827e9` |

Machine-readable per-plant and per-cell data are in
[`../../results/top1_e_expert_overflow/plants.csv`](../../results/top1_e_expert_overflow/plants.csv)
and [`../../results/top1_e_expert_overflow/summary.json`](../../results/top1_e_expert_overflow/summary.json).

## Largest registered batch size

Each row reports the paired mean of `(J_A-J_R)/T`, its 95% paired-mean `t`
interval, and the theorem limit `d-d^E/E`. All 100/100 paired gaps were
positive in every row.

| E | d | Mean gap | 95% interval | Theorem limit | Absolute deviation |
|---:|---:|---:|---:|---:|---:|
| 3 | 1/4 | 0.245432 | [0.244263, 0.246600] | 0.244792 | 0.000640 |
| 3 | 1/2 | 0.459268 | [0.456940, 0.461596] | 0.458333 | 0.000935 |
| 3 | 3/4 | 0.610953 | [0.606984, 0.614922] | 0.609375 | 0.001578 |
| 4 | 1/4 | 0.248557 | [0.247093, 0.250020] | 0.249023 | 0.000467 |
| 4 | 1/2 | 0.484197 | [0.481437, 0.486957] | 0.484375 | 0.000178 |
| 4 | 3/4 | 0.667851 | [0.663539, 0.672163] | 0.670898 | 0.003047 |
| 8 | 1/4 | 0.242400 | [0.240376, 0.244423] | 0.249998 | 0.007599 |
| 8 | 1/2 | 0.463375 | [0.459589, 0.467161] | 0.499512 | 0.036137 |
| 8 | 3/4 | 0.670611 | [0.664949, 0.676273] | 0.737486 | 0.066875 |
| 16 | 1/4 | 0.181162 | [0.177723, 0.184602] | 0.250000 | 0.068838 |
| 16 | 1/2 | 0.346118 | [0.340139, 0.352096] | 0.499999 | 0.153881 |
| 16 | 3/4 | 0.522715 | [0.514357, 0.531073] | 0.749374 | 0.226659 |

## Finite-size interpretation

The direction of the paired effect is robust on this design, but the
largest-batch means for `E=8` and especially `E=16` are not close to the
asymptotic values. The equal-split extra capacity of each non-short expert is
`sigma=1/(2E(E-1))`. At `E=16`, this is `1/480 ≈ 0.002083` of the batch,
approximately the standard deviation of a uniform expert's empirical
Top-1 fraction at `T=13440` (`sqrt((1/16)(15/16)/13440) ≈ 0.00209`). Thus
finite batches frequently place non-short experts on the clipping boundary;
the population proof's limiting step-zero clipping pattern is not yet a good
finite-size approximation at that setting. Increasing `T` should reduce
this sampling effect, but this experiment did not test larger batches.

For `E=3,4`, the finite estimates are close to the limit. For `E=8,16`, the
theorem's strict positive sign is supported by all registered paired runs,
but the experiment does not numerically validate the limiting magnitude at
the tested `T`. The asymptotic proof, not this finite sample, establishes the
limit.

## Claim boundary

This is controlled evidence for the stated two-step, iid-affinity, Top-1
family under the existing proportional-pressure update and canonical
per-expert clipping. It does not compare against every causal controller,
cover `K>1`, measure telemetry latency, establish trained-model quality, or
separate the finite family from its exact outcome-map representation in the
polyhedral active-testing benchmark. It advances the existing formal line;
it does not close the paper's class-level novelty gate.

# Exact audit of the minimum signal for requested-update emulation

**Run date:** 2026-10-17  
**Protocol:** [minimal_signal_audit_2026-10-17.md](minimal_signal_audit_2026-10-17.md)  
**Executable:** [`scripts/audit_minimal_signal_family.py`](../../scripts/audit_minimal_signal_family.py)  
**Output:** [`summary.json`](../../results/minimal_signal_audit/summary.json)  
**Theorem:** T4b in [`formal_core.md`](formal_core.md)

## Exact finding

For `E ∈ {2,3,4,8,16,32}`, set `K=1`, `T=E+1`, `C_e=1`, `mu_e=1/E`, and observe `A_e=1` for every expert. The feasible clipping fiber contains exactly `E` requests, `R^(i)=1+e_i`. Each is realized by a one-hot-affinity Top-1 batch. All worlds have the same admitted feedback and therefore the same admitted next gauge state. The requested controller's next gauge state is instead `e_i/(E+1)`, distinct for each overloaded expert.

| Experts `E` | Fiber size | Distinct requested next states | Admitted next states | Minimum fixed-length bits |
|---:|---:|---:|---:|---:|
| 2 | 2 | 2 | 1 | 1 |
| 3 | 3 | 3 | 1 | 2 |
| 4 | 4 | 4 | 1 | 2 |
| 8 | 8 | 8 | 1 | 3 |
| 16 | 16 | 16 | 1 | 4 |
| 32 | 32 | 32 | 1 | 5 |

All eight exact checks passed across every family: Top-1 realizability, identical admitted observations, exact fiber size, distinct requested updates, identical admitted update, injective `P_0(J)`, tight message alphabet size, and mass/clipping identities. The script hashes itself and the fixed protocol in the JSON artifact.

## Interpretation

This confirms the exact scope of T4b: to reproduce the **requested controller's next gauge update with zero error** over the full one-batch clipping fiber, a telemetry message must identify the request vector. In the `D=1` family above, that message only needs to identify the overloaded expert, so its information lower bound is `ceil(log2 E)` bits. The centered rejected-load signal `P_0(J)` is sufficient.

The analytic extension T4c in `formal_core.md` covers `D≥1`: for `K=1`,
`T=E+D`, unit capacities, and `A=1`, the fiber size is
`binomial(E+D-1,D)`. The original audit reported here checked `D=1` only.
The later controlled enumeration now covers `E∈{2,3,4,8}` and
`D∈{1,2,3,4}`; see [`minimal_signal_multioverflow_results_2026-10-17.md`](minimal_signal_multioverflow_results_2026-10-17.md)
and its exact machine-readable artifact.

It does **not** show that this is the minimum signal for an overflow-optimal or otherwise redesigned controller. The bit-count argument is a generic injective-encoding bound; the MoE-specific content is the exact clipping fiber, its Top-1 realizability, and the requested gauge-update map. It remains a one-batch result, and no physical collective or latency was measured. It therefore closes the formal “exact signal to emulate `(R)`” question, not the paper's family-level separation from state-constrained adaptive testing.

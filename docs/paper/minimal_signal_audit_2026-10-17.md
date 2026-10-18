# Controlled exact audit: minimum signal to reproduce the requested update

**Status:** protocol fixed before executing the audit. This tests the one-batch exact-emulation claim in T4b; it is not a control-performance or model-quality experiment.

## Question

When multiple Top-1 request vectors produce the same admitted vector, how many distinct messages must an exact telemetry signal carry to reproduce the requested controller's next gauge state? The theorem predicts that every request vector in the clipping fiber produces a distinct requested next state, and that the exact message count equals the fiber cardinality.

## Fixed parameter family

For each `E ∈ {2,3,4,8,16,32}`:

- `K=1`, `T=E+1`, `C_e=1` for every expert, and `mu_e=1/E`.
- The observed admitted vector is `A=(1,…,1)`.
- There are `E` hidden request worlds indexed by `i`. World `i` assigns one token to each expert and one additional token to expert `i`, yielding `R^(i)=1+e_i`.
- Each world is realized by a one-hot-affinity Top-1 batch at `q_0=0`; the same routing is used to construct the request and admitted counts.
- `eta=gamma=1`, `delta=0`; all arithmetic, updates, and comparisons use exact rational values.

## Arms and controls

Compare the requested update computed from `R^(i)` with the admitted-only update computed from the common `A`. For each `E`, exhaustively enumerate all `E` worlds and check:

1. Every affinity batch realizes its declared Top-1 request vector.
2. Every world yields the same `A`, while `R^(i)` and `P_0(J^(i))` are distinct.
3. Requested feedback produces `E` distinct next gauge states; admitted feedback produces one common next state.
4. The clipping-fiber cardinality is exactly `E`, and an exact zero-error message needs at least `ceil(log2 E)` worst-case fixed-length bits; the index `i` achieves that alphabet size.
5. Mass conservation and `A_e=min(R_e,C_e)` hold in every world.

## Interpretation boundary

The endpoint is exact one-step behavioral emulation of the requested proportional controller, not the minimum telemetry for an overflow-optimal policy. The bit count is a worst-case information lower bound, not a measurement of collective latency or network bytes. The result is a finite family check of T4b; the theorem proof, not the enumeration, supports the general fiber statement. The generic counting argument is not claimed as a new communication-complexity principle.

## Reproduction

Run `python scripts/audit_minimal_signal_family.py` from the exploration worktree root. The script writes `results/minimal_signal_audit/summary.json` with each world and every exact control.

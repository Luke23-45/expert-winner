# Exact synthetic audit: pressure update equals entropy mirror descent

**Run date:** 2026-10-17. Two executions of the locked deterministic audit
produced byte-identical output.

## Results

The exact-binomial experiment covered 162 cells: three batch sizes, three
capacity profiles, three request-probability profiles, two targets, and
three step sizes. The model was `E=3,K=1`, iid standard Gumbel, zero leak,
and canonical per-expert clipping.

- Across all cells, the next probabilities computed by the canonical
  gauge-pressure update and by the closed-form entropy mirror step agreed
  exactly in the reported floating-point arithmetic (maximum difference
  `0.0`).
- Adding a common constant to the initial pressure changed the next
  probabilities by at most `1.33e-15`.
- All 54 no-clipping controls matched the requested-signal potential
  formula.
- Every registered capacity-integrality and exact-total check passed.
- The CSV SHA-256 is
  `deaeb4b786220884dfbf01633cd1f83db3892aa767574a9baec0be5462e5efa3`;
  the summary SHA-256 is
  `476eeb5829a0792c60d3be527bd7d5099566cbc04e88696d203faf11914e6e23`.
  Protocol SHA-256:
  `b5fc895915aa726abb855c98540d0b7d7739d86d639f682f2863c1366730c32f`;
  runner SHA-256:
  `edd84de2367d59d5e853fa3d56e078f40ff9b1ce37637fde3210c612218e9424`.

The complete records are
[`../../results/capacity_clipped_mirror_descent_audit/mirror_step_cells.csv`](../../results/capacity_clipped_mirror_descent_audit/mirror_step_cells.csv)
and
[`../../results/capacity_clipped_mirror_descent_audit/summary.json`](../../results/capacity_clipped_mirror_descent_audit/summary.json).
The theorem, protocol, and runner are
[`capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md`](capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md),
[`capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md`](capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md),
and [`run_capacity_clipped_mirror_descent_audit.py`](../../scripts/run_capacity_clipped_mirror_descent_audit.py).

## Interpretation

This verifies the `K=1` implementation identity for expected fresh-batch
feedback. It does not test the general `K>1` conjugate computation, prove
objective decrease for the tested step sizes, establish convergence, or
validate fixed-affinity trajectories as stochastic mirror descent. The
general `K` statement is proved analytically in the theorem document.

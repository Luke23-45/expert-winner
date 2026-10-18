# Exact synthetic audit: Top-1 admitted-field curl across capacity scale

**Status:** two-run deterministic exact-rational audit, 2026-10-17. This
checks a general analytic theorem in the unchanged canonical per-expert
clipping model. It is not training evidence or a controller-performance
comparison.

## Registered experiment

The protocol fixes three-expert Top-1 routing with iid standard Gumbel
affinities, `gamma=1`, and equal capacities. It tests the exact-total family
`T=3m`, `C=m`, `m=1,...,30`, at request probabilities
`(1/2,1/3,1/6)`. For each cell, the binomial clipping sensitivities and the
quotient curl are evaluated with exact rational arithmetic. The controls are
uniform request probabilities, no clipping (`C=T`), and swapping experts 1
and 3.

## Results

- All 30 exact-total skewed cells had nonzero curl, with the registered
  orientation negative. The value was `-1/108` at `(T,C)=(3,1)` and
  approximately `-0.0266209015` at `(90,30)`.
- All 30 uniform-probability controls had exactly zero curl.
- All 30 no-clipping controls had exactly zero curl.
- All 30 expert-swap controls exactly reversed the signed curl.
- Two executions produced byte-identical CSV data. Its SHA-256 is
  `6937acf53d484e5cb489f322fa3a2fffd473794bda7b8aceafcf4ddc527ebe9b`.

The machine-readable summary is
[`../../results/top1_curl_capacity_scaling/summary.json`](../../results/top1_curl_capacity_scaling/summary.json),
and all 120 cell/control rows are in
[`../../results/top1_curl_capacity_scaling/curl_cells.csv`](../../results/top1_curl_capacity_scaling/curl_cells.csv).
The summary SHA-256 is
`167f998b54c48d519cb40476dd0e5a046289257a51c5cc772465841590ef0711`.
The protocol SHA-256 is
`e1d0b01ef84d155e7f41b3646fd0a3867f74622d1f9e89d91874eda68f87a3ac`, and
the final runner SHA-256 is
`e4fdc5b17dd4c9ceac803a7bf1eb5f4a29dfc90613e52b7dc57c4d2e0d66aa10`.

## Interpretation

The experiment confirms the exact curl formula and its symmetry controls over
the registered capacity scale. The open-set non-potentiality conclusion for
every `T>=2, 1<=C<T` comes from the analytic proof in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md),
not from observing 30 nonzero cells. The finding remains structural: it does
not prove closed-loop instability, universal overflow harm, a system-level
measurement cost, or a separation from the exact outcome-map benchmark.

The protocol and executable are
[`top1_curl_capacity_scaling_protocol_2026-10-17.md`](top1_curl_capacity_scaling_protocol_2026-10-17.md)
and [`run_top1_curl_capacity_scaling.py`](../../scripts/run_top1_curl_capacity_scaling.py).

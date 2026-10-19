# Current central result

## Established result

[theorem.md](theorem.md) proves an exact conditional mechanism for the specified Top-K routing model: when every expert is saturated under uniform capacities and a uniform target, canonical per-expert clipping makes the admitted-feedback vector common-mode. Gauge normalization removes that component. With zero pressure decay, admitted feedback leaves relative pressure unchanged; with a fixed affinity batch and deterministic tie rule, the routing remains invariant. Requested feedback retains the centered requested-load imbalance.

The theorem's assumptions and conclusions are part of the result. It does not establish that requested feedback always improves routing, reduces aggregate overflow, improves language-model quality, or is unavailable in deployed routers.

## Empirical evidence

The paired 500-run synthetic audit is preserved at [evidence/20261018T132657Z/](evidence/20261018T132657Z/). It ran on CPU and uses the deterministic simulator. The bundle includes the protocol, manifest, source snapshot, run index, paired effects, audit output, report, and compressed trajectories. [`SHA256SUMS.txt`](evidence/20261018T132657Z/SHA256SUMS.txt) records hashes for all 29 files copied from the original ignored output bundle. Its findings corroborate load-imbalance effects for the declared generator; they are not trained-model or real-workload evidence.

## Canonical sources and next study

- Mathematical definitions: [../formal_definitions/formal.md](../formal_definitions/formal.md).
- Theorem and audit interpretation: [theorem.md](theorem.md).
- Planned real-workload benchmark: [../implementation_plan/real_workload_benchmark_protocol.md](../implementation_plan/real_workload_benchmark_protocol.md).
- Previous experiment versions and research drafts: [../research_history/README.md](../research_history/README.md).

The class-level separation from state-constrained adaptive-testing theory remains unresolved. The real-workload plan is the next empirical stage; it does not resolve that theoretical question by itself.

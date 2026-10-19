# Expert Winner: capacity-constrained MoE routing

This repository studies how capacity admission affects feedback control in sparse Mixture-of-Experts (MoE) routing. The current established result is the conditional saturation-freeze mechanism stated in [docs/central_claim/theorem.md](docs/central_claim/theorem.md), with canonical model definitions in [docs/formal_definitions/formal.md](docs/formal_definitions/formal.md).

## Research status

- The theorem is exact under its stated uniform-capacity, uniform-target, global-saturation, canonical-clipping, and pressure-dynamics assumptions.
- The synthetic corroboration is a deterministic CPU simulator study. Its tracked artifacts and provenance are in [docs/central_claim/evidence/20261018T132657Z/](docs/central_claim/evidence/20261018T132657Z/).
- This evidence does not establish language-model quality gains, behavior on real router traces, universal superiority of requested feedback, deployment telemetry limits, or a separation from adaptive-testing theory.
- The real-workload study is planned in [docs/implementation_plan/real_workload_benchmark_protocol.md](docs/implementation_plan/real_workload_benchmark_protocol.md); the existence of this protocol does not mean the study has run.

## Document map

- [docs/central_claim/README.md](docs/central_claim/README.md): current result, evidence, and claim boundaries.
- [docs/central_claim/theorem.md](docs/central_claim/theorem.md): statement, assumptions, proof, and synthetic corroboration.
- [docs/formal_definitions/formal.md](docs/formal_definitions/formal.md): canonical mathematical model and definitions.
- [docs/implementation_plan/real_workload_benchmark_protocol.md](docs/implementation_plan/real_workload_benchmark_protocol.md): planned real-router and training benchmark design.
- [docs/research_history/README.md](docs/research_history/README.md): archived experiment versions, literature reviews, feedback, and superseded drafts.

The synthetic controller implementation remains in `src/moe_control/`. Earlier v1-v3 reports and their run artifacts are retained under `docs/research_history/` for audit and reproducibility.

# Benchmark attack on the Top-2 signed-bias theorem

## Question

Does P2f's exact admitted-versus-requested overflow difference establish a
value gap over the independently defined polyhedral outcome benchmark B1 or
B1-out?

## Answer: no, at the finite-instance level

Fix any replication factor `m`, any affinity perturbation matrix, any gain
`alpha`, and the nine-batch horizon. The resulting router has finitely many
pairwise Top-2 score-tie hyperplanes in its gauge state. These divide the
state space into finitely many cells on which requested counts `R` are
constant. Per-expert admission then gives the fixed output `A=min(R,C)` and
the same overflow on each cell.

Assign each cell's exact `(R,A)` pair as its outcome label in B1-out. The
requested and admitted observers receive the same signals as in the MoE
experiment. The sign update is a deterministic function of that signal, so
the next bias state is the same; representing the bias score `a+b` by the
gauge state `q=-b` (up to the positive score scale) preserves all Top-2
rankings and trajectories. Every policy/arm history and every batch overflow
therefore agrees pathwise. In particular, the exact nine-batch totals
`93m/98m/99m` are reproduced by the benchmark instance.

This is an application of the exact finite-instance embedding in
[`phase1_benchmark_gate_2026-10-16.md`](phase1_benchmark_gate_2026-10-16.md),
including Proposition 4's B1-out extension. P2f is a valid Top-2 family
mechanism theorem, but it is not a strict value separation from its exact
outcome-map copy. The same argument applies to each fixed perturbed plant and
each fixed horizon; no benchmark novelty follows from the 100-run audit.

## Consequence for the paper claim

Keep P2f as a proved positive Top-2 case alongside the known Top-1 positive
and negative results. Do not use it alone to claim a new general control
limitation, an information-cost break-even, or top-conference novelty. A
stronger claim would need a family-level value or complexity theorem compared
against a benchmark fixed independently of the family, and an explicit proof
that the relevant quantitative dependence does not transfer by copying the
same finite outcome maps. This result does not supply that proof.

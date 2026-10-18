# Robustness protocol for the requested-versus-admitted Top-1 delay theorem

**Purpose:** verify a nonzero robustness neighborhood of the existing exact
one-update delay result, including the professor report's score-ranked versus
position-ranked per-expert drop suggestion. This protocol does not introduce
a new controller, admission model, observation-cost objective, or training
claim.

## Mathematical target fixed before the run

The base plant, target, and update are those in
[`closed_loop_admission_delay_theorem_2026-10-17.md`](closed_loop_admission_delay_theorem_2026-10-17.md):
`E=3`, `K=1`, uniform target, `q0=(0,2,3)`, static affinities, unit per-expert
capacity at base scale, zero leak, and minimum-coordinate gauge projection.
For every `eta` in `(7/100,21/200)`, requested feedback reaches the balanced
count vector after two saturated batches; admitted feedback takes three.
Replicating every affinity row `m` times makes the cumulative overflow to
balance `2m` and `3m`, respectively.

The robustness calculation is new and exact. Restrict to the closed interval
`eta in [2/25,1/10]`. Evaluate all 36 winner-versus-competitor inequalities
along the six proposed states (initial, two requested updates, and three
admitted updates). Their minimum baseline margin over this compact interval
is `1/300`. Perturbing every affinity entry by at most `1/1200` changes any
winner-minus-competitor score margin by at most `1/600`, leaving a strict
margin of at least `1/600`. Therefore every such perturbed plant follows the
same route sequence throughout the stated step-size interval. This gives an
open affinity neighborhood, not merely the exact duplicated base matrix.

## Paired controlled synthetic design

- Generate 100 deterministic rational affinity perturbations. Each entry is
  independently chosen from `{-1/1200, 0, +1/1200}`.
- Pair requested, admitted, and no-feedback signals on each same perturbed
  plant, step size, and row-replication factor.
- Use replication factors `m in {1,2,5,10}` and step sizes
  `{2/25, 9/100, 1/10}`.
- For admitted feedback, compare score-ranked and position-ranked retention
  under independent per-expert capacities. Record token identities and the
  resulting admitted counts.
- Use capacity `3m` as a no-clipping negative control. Requested and admitted
  pressure paths must then agree exactly.
- Use exact rational arithmetic for scores, route margins, feedback, pressure
  updates, overflow, and event times. The fixed horizon is six batches, long
  enough to observe the balance event and its absorbing continuation.

## Outcomes and pass conditions

The primary outcomes are first balanced-batch index and cumulative overflow
up to that batch. The pre-stated pass conditions are:

1. Requested feedback balances at batch index 2 and has cumulative overflow
   `2m`.
2. Admitted feedback balances at batch index 3 and has cumulative overflow
   `3m`.
3. The paired difference is exactly `m` for every perturbation, step size,
   and replication factor.
4. Score-ranked and position-ranked per-expert retention have identical
   requested/admitted count and pressure trajectories.
5. In the no-clipping control, requested and admitted trajectories are
   identical.
6. Every observed winner margin is at least the certified lower bound
   `1/300 - 2/1200 = 1/600` and therefore remains strictly positive.

These checks audit the theorem's implementation and robustness arithmetic;
they are not independent-router samples and do not provide statistical
generalization evidence.

## Interpretation boundary

This experiment strengthens the existing requested-versus-admitted Top-1
mechanism result. It does not establish optimality over all admitted
controllers, a general `E,K` theorem, a real-system frequency claim, a
training-quality gain, or a separation from the exact polyhedral outcome-map
benchmark. Per-expert score ranking is included as a control because it
changes retained token identities but, when each expert fills its own slots,
cannot change `A_e=min(R_e,C_e)`. Coupled device/group capacity is a separate
admission model and is not silently substituted here.

## Reproduction

From the repository root:

```powershell
python scripts/run_robust_delay_experiment.py
```

The executable writes `results/closed_loop_delay_robustness/summary.json` and
`trajectories.csv`. The summary records source revision and protocol/script
hashes.

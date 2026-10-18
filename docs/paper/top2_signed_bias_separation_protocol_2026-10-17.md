# Controlled experiment: admitted-sign Top-2 transient advantage

**Research line:** requested versus admitted feedback under hard Top-K and
per-expert capacity.  
**Controller:** the existing signed expert-bias update, not the proportional
pressure update.  
**Primary endpoint:** cumulative overflow over a fixed nine-batch horizon.

## Exact family fixed before simulation

Use `E=3`, `K=2`, `T=20m`, uniform capacity `C=10m`, and replicate the
following 20 affinity rows `m` times:

- one row `(0, 5, 11/10)`;
- ten rows `(0, 101, 100)`;
- nine rows `(2, 6/5, 0)`.

The Top-2 router omits the lowest-scoring expert; all initial cutoff
comparisons are strict. At zero bias the request counts are
`R=(9m,20m,11m)`, so the admitted counts are `A=(9m,10m,10m)`. The total
requested slots are `40m` and total capacity is `30m`; the per-batch minimum
possible overflow is therefore `10m`.

The update is `b⁺ = P0(b + alpha * sign(mean(L)-L))`, with `L=R`, `A`, or
zero. The controller's score is affinity plus bias, as in the signed
expert-bias formulation. Scale all theorem affinities and gains by `1/250`;
this preserves every route and event time while placing the gain grid at
`{0.0009,0.00096,0.001}`, including the canonical `bias_gamma=0.001` value.
This compact interval is contained in the scaled theorem interval
`(0.0008,0.0011)`.

## Paired perturbation design

- Generate 100 deterministic rational affinity perturbations. Every entry is
  independently shifted by one of `{-1/1000,0,+1/1000}`.
- Pair admitted, requested, and no-feedback arms on every perturbed matrix,
  replication factor `m in {1,3,10}`, and step size
  `alpha in {9/10000,3/3125,1/1000}`.
- For each arm, pair score-ranked and position-ranked retention within the
  independent per-expert capacity slots. Record actual retained token IDs
  and admitted counts.
- Run a no-clipping negative control with capacity `20m` per expert. Since
  `A=R`, requested and admitted states must agree exactly.
- Use exact rational scores, routes, feedback, bias updates, count vectors,
  and overflow. Run exactly nine batches; no parameter is tuned after
  observing outcomes.

## Registered predictions and pass conditions

For every perturbation, `m`, and `eta`:

1. Admitted feedback has `R=(9,20,11)m` for batches 0–2, then
   `R=(10,20,10)m` for batches 3–8. Its first globally saturated batch is 3
   and its nine-batch cumulative overflow is `93m`.
2. Requested feedback has `R=(9,20,11)m` for batches 0–2, alternates between
   `(9,11,20)m` and `(9,20,11)m` for batches 3–7, and reaches
   `(10,20,10)m` at batch 8. Its cumulative overflow is `98m`.
3. No feedback retains `(9,20,11)m` for all nine batches and accumulates
   overflow `99m`.
4. Score-ranked versus position-ranked retention has identical count and
   bias paths under independent per-expert caps.
5. The no-clipping requested and admitted paths are identical.
6. Every Top-2 cutoff remains strict. After the common `1/250` score scaling,
   the exact base family has minimum cutoff margin `1/2500` over the
   registered compact gain interval; the perturbation can reduce a pairwise
   margin by at most `1/125000`.

## Why this experiment is controlled

It pairs all controller arms on the same fixed affinity plant, varies only
the signal used by the same signed update, includes no-feedback and dropless
negative controls, and fixes the horizon, objective, step-size grid, and
perturbation rule in advance. The perturbations audit a proved strict-margin
neighborhood; they are not independent workload samples. Report raw exact
counts and overflow without combining them with a weighted score.

## Reproduction and boundary

Run `python scripts/run_top2_signed_bias_separation.py`. The script writes the
machine-readable summary and all trajectories to
`results/top2_signed_bias_separation/`.

This is a parameterized, replicated `E=3,K=2` mechanism theorem and a
controlled exact synthetic audit. It does not establish a general controller
ranking, trained-model quality improvement, deployment prevalence, or a
separation from an outcome-map benchmark that reproduces each finite plant.

# Paired synthetic dynamics following the facet audit

**Status:** completed exploratory experiment; exact finite trajectories.  
**Question:** does the admitted-field potential obstruction by itself order overflow outcomes under the existing pressure dynamics?  
**This is a follow-up experiment, not a theorem test.** The facet theorem is local geometry; it does not predict the global trajectory ranking.

## Protocol

The study reuses the 40 seeded $E=4,K=2,T=12$ integer-affinity plants
(`iid Uniform[-4,4]`) from the facet ensemble. For each seed and each of the
same four capacity profiles, it runs three paired arms from the same initial
state $q_0=0$:

1. requested-count feedback $R$;
2. admitted-count feedback $A=\min(R,C)$;
3. no-feedback control.

Every arm uses the formal gauge update with $\gamma=1$, $\delta=0$,
$\eta=1/10$, uniform target $\mu_e=1/E$, and minimum-coordinate gauge
projection. The horizon is fixed at 80 steps. The primary metric is total
overflow accumulated over those 80 steps,
\[
\sum_{t=0}^{79}\sum_e (R_{t,e}-A_{t,e}).
\]
All scores, routing comparisons, feedback updates, and pressures are exact
rational calculations. Arms share the same affinity matrix within each seed;
each controller evolves its own pressure trajectory. The no-clipping
negative control checks the entire requested/admitted trajectory equality at
every seed and every step, not just the final metric.

## Outcomes

Values below are per-run 80-step cumulative overflow averaged over 40 paired
seeds. Paired differences are arm minus requested feedback.

| Capacity profile | Requested mean | Admitted mean | No-feedback mean | Admitted minus requested (mean; median; wins/ties/losses) | No feedback minus requested (mean; median; wins/ties/losses) |
|---|---:|---:|---:|---|---|
| No clipping | 0 | 0 | 0 | $0$; $0$; 0 / 40 / 0 | $0$; $0$; 0 / 40 / 0 |
| Exact-total uniform | $2943/20=147.15$ | $321/2=160.50$ | 214 | $267/20=13.35$; $1/2$; 20 / 18 / 2 | $1337/20=66.85$; 79; 30 / 9 / 1 |
| Exact-total heterogeneous | $2333/5=466.60$ | $22407/40=560.175$ | 544 | $3743/40=93.575$; 99; 36 / 4 / 0 | $387/5=77.40$; 79; 32 / 8 / 0 |
| Aggregate shortage | $38401/40=960.025$ | $38401/40=960.025$ | 962 | $0$; $0$; 0 / 40 / 0 | $79/40=1.975$; 0; 1 / 39 / 0 |

Here “wins / ties / losses” counts how often the comparison arm has greater,
equal, or lower cumulative overflow than requested feedback. The term
“win” therefore means worse overflow for the comparison arm. Medians are
exact; for 40 paired runs the median is the average of observations 20 and
21. The complete per-seed differences are in `summary.json`.

Under the exact-total uniform profile, admitted feedback has higher average
overflow but is not uniformly worse: it is worse on 20 seeds, ties on 18,
and is better on 2. Under the heterogeneous exact-total profile it is worse
on 36 and ties on 4. Under aggregate shortage, the two feedback arms have
equal cumulative overflow on all 40 seeds, despite their requested routes
and feedback signals sometimes differing step by step. This is a concrete
warning against inferring performance from local field geometry or from the
mere existence of clipping.

The no-clipping arm is a valid negative control: requested and admitted
feedback produce identical routes, counts, pressure, and zero overflow at
every step. The result is exactly what $A=R$ requires.

## Interpretation

This experiment gives a deterministic paired mechanism check, not a
population-level performance claim. The observed mean ordering in the two
exact-total capacity profiles is promising evidence that the signal
difference can matter on these plants, but the uniform profile already
contains counterexamples to a universal per-instance ordering. The
heterogeneous profile's ordering is a result for this generator, these
capacities, the chosen gain, and 80 steps only. Neither outcome establishes
that non-cyclicality causes worse control, or that a requested-count
collective is worth its implementation cost.

This does **not** close the class-level benchmark issue. Every finite static
plant's trajectory remains exactly reproducible by the polyhedral
outcome-map benchmark already described in the research status. No training,
router traces, communication profiling, or quality metric was collected.
Thus this is an additional controlled synthetic result on the existing
research line, not the final proof of a broad Top-$K$ limitation or a
conference-ready contribution.

## Reproduction

Run from the repository root:

```powershell
python scripts/run_admission_facet_dynamics.py
```

The exact per-seed and per-step outputs are in
[`results/admission_facet_dynamics/summary.json`](../../results/admission_facet_dynamics/summary.json),
[`results/admission_facet_dynamics/run_metrics.csv`](../../results/admission_facet_dynamics/run_metrics.csv),
and `step_metrics.csv`.

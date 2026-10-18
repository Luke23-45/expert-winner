# Controlled trajectory follow-up for the non-cyclic admitted field

**Evidence class:** deterministic exact-rational finite-horizon audit on one
fixed synthetic Top-1 plant. This is a mechanism check, not a population
experiment.

## Question and protocol

The cyclic-monotonicity counterexample establishes a geometric difference
between requested and admitted fields. It does not imply that admitted-feedback
pressure trajectories have higher overflow. This follow-up checks whether the
four-state witness yields a consistent trajectory advantage for either
controller.

The plant, affinity rows, capacities, target, and Top-1 rule are exactly those
in [`admitted_feedback_noncyclicity_2026-10-17.md`](admitted_feedback_noncyclicity_2026-10-17.md).
Both arms use the same fixed batch on every update. There are no random seeds.

| Design item | Setting |
|---|---|
| Initial pressures | All four witness states, represented with minimum coordinate zero |
| Feedback arms | Requested: $R/T-\mu$; admitted: $A/T-\mu$ |
| Update | $q^+=\Pi_g(q+\eta\varepsilon)$, with $\gamma=1$ and $\delta=0$ |
| Step sizes | $\eta\in\{1/10,1/2,1,2\}$ |
| Horizon | 100 updates per arm and initial state |
| Gauge projection | Subtract the coordinate minimum after each update |
| Tie handling | Lowest expert index; no ties occurred in any run |
| Primary measure | Cumulative rejected assignments $\sum_{t=0}^{99}(\sum_e R_{t,e}-\sum_e A_{t,e})$ |
| Secondary measure | First exact repeat, if reached by the horizon |

The custom audit script uses rational arithmetic and asserts the reported
overflow totals and absence of ties:

```powershell
python scripts/run_admitted_noncyclicity_trajectory_audit.py
```

## Results

Each cell below is cumulative overflow over 100 updates. $\Delta$ is admitted
minus requested, so positive values favor requested feedback on this finite
comparison and negative values favor admitted feedback.

| $\eta$ | Start $(-3,-1)$: R / A ($\Delta$) | Start $(-2,-2)$: R / A ($\Delta$) | Start $(3,1)$: R / A ($\Delta$) | Start $(-3,4)$: R / A ($\Delta$) |
|---:|---:|---:|---:|---:|
| $1/10$ | 2 / 3 (+1) | 17 / 33 (+16) | 93 / 106 (+13) | 63 / 99 (+36) |
| $1/2$ | 100 / 1 (-99) | 100 / 7 (-93) | 19 / 39 (+20) | 14 / 21 (+7) |
| $1$ | 100 / 144 (+44) | 100 / 140 (+40) | 101 / 141 (+40) | 103 / 146 (+43) |
| $2$ | 100 / 147 (+47) | 100 / 145 (+45) | 101 / 146 (+45) | 104 / 148 (+44) |

The finite comparison does **not** produce a controller that wins across the
tested settings. At $\eta=1/10$, requested feedback has lower cumulative
overflow from all four starts. At $\eta=1/2$, admitted feedback has lower
overflow from the first two starts and higher overflow from the other two. At
$\eta=1$ and $2$, requested feedback has lower overflow from all four starts.
Some trajectories enter exact period-one or period-two cycles; one admitted
trajectory at $\eta=1/10$ did not repeat within 100 updates. The script records
the repeat details.

One exact signal is stronger than this parameter grid: from the first witness
state, the requested controller reaches balance two saturated steps earlier
for every $\eta\in(7/100,21/200)$, with an exact replicated-family overflow
gap. The derivation is in
[`closed_loop_admission_delay_theorem_2026-10-17.md`](closed_loop_admission_delay_theorem_2026-10-17.md).

## Interpretation

This is evidence that the non-cyclic admitted field is **not by itself** a
performance theorem: trajectory outcomes depend on step size and initial
pressure. The positive cycle rules out a convex-potential representation for
the admitted field on the constructed family, but it does not imply universal
instability or higher overflow. The result remains a structural lemma and a
small controlled mechanism study; it does not establish a class-level
Top-$K$/gauge separation from adaptive testing or a trained-model benefit.

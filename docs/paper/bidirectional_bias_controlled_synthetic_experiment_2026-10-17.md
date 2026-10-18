# Controlled synthetic comparison of requested- and admitted-count feedback

**Status:** completed exact-rational controlled mechanism audit. It combines
an analytic all-horizon admitted-better family with two exact requested-better
witnesses, one of which has uniform capacities. This is a retrospective
controlled experiment, not a preregistered confirmatory study and not trained-
model evidence.

## Question

Does requested-count feedback always reduce overflow relative to admitted-count
feedback, or does the ranking depend on the fixed Top-K affinity/capacity
instance? The experiment also checks the professor report's suggestion that
score-ranked dropping itself changes admitted expert counts under independent
per-expert capacities.

## Locked mechanics and outcomes

All three plants use the same signed expert-bias rule:

```text
u_e = sign(mean(L) - L_e)
b_next = P_0(b + gamma*u)
scores = affinities + b
```

Here `L` is requested count `R`, admitted count `A`, or zero update (no
feedback); `P_0` removes the common bias mode. Admission is independently
per-expert, `A_e=min(R_e,C_e)`. The primary outcome is cumulative rejected
assignments `sum_t sum_e(R_{t,e}-A_{t,e})`; request imbalance, bias magnitude,
and saturation entry are mechanism diagnostics. This controller is the
signed-bias family, not the proportional pressure update in `formal.md`.

The exact baselines are requested feedback, admitted feedback, no feedback,
and a no-clipping control where `A=R`. Per-expert score-ranked and
position-ranked retention are paired admission-order controls. They must
produce identical admitted-count and controller paths whenever the request
matrix is fixed.

## Plant 1: admitted feedback wins

The fixed parameterized Top-2 family from Theorem P2f has `E=3`, `K=2`,
`T=20m`, uniform capacities `C=10m`, and replicates `m` times the three
affinity rows described in
[`top2_signed_bias_separation_theorem_2026-10-17.md`](top2_signed_bias_separation_theorem_2026-10-17.md).
The theorem applies to every gain `alpha in (1/5,11/40)` and gives an
all-horizon ranking after batch 3. Its exact-rational robustness audit uses
100 seeded entrywise affinity perturbations, `m={1,3,10}`, three gains in a
compact certified interval, both score- and position-ranked per-expert
retention, plus a no-clipping control. All 900 paired cells pass. At nine
batches the overflows are `93m` admitted, `98m` requested, and `99m` no
feedback. The selected routing paths have strict cutoff margins throughout.

Reproduction: `python scripts/run_top2_signed_bias_separation.py`. The run
record is `results/top2_signed_bias_separation/summary.json`; it records
source revision `e1648512e22844f4d8e892577dfc011f83ac307a`, script SHA-256
`938e47a82728f40e16138594f5a10d7c2f7fb385618f2cc586fa32fa08b8ab8e`, and
900 exact paired cells.

## Plant 2: requested feedback wins with uniform capacities

The stronger requested-better witness is a fixed, reproducible uniform-
capacity plant. It uses `E=8`, `K=2`, `T=128`, `C_e=32`, gain `1/40`, zero
initial bias, and `H=120`. The authoritative 128-by-8 affinity matrix is
checked in as exact decimal rationals at
[`uniform_capacity_seed5_affinities.csv`](fixtures/uniform_capacity_seed5_affinities.csv)
(SHA-256 `b7cb4002f5aa7a0ddc384fbacaa7617ca744534e5a2bcb0987bfc1ab2c43bc2d`).
It was generated from the ring-pair family with edge counts
`(30,8,22,10,26,6,18,8)`, CPU float64 noise in `[0,0.02)`, and seed 5; the
checked-in rational matrix, rather than a platform-dependent future RNG draw,
defines the exact theorem witness. Ties are broken by lower expert index.

| Controller | Cumulative overflow over 120 batches | Minimum Top-2 cutoff margin |
|---|---:|---:|
| Admitted feedback | 2,449 | `542933344799/10000000000000000` |
| Requested feedback | 1,918 | `114112300983/2500000000000000` |
| No feedback | 1,920 | `37806719560039579/10000000000000000` |

Every route is strict over the full horizon. No arm reaches global
saturation; five experts are saturated initially. Requested feedback lowers
overflow by exactly 531 assignments relative to admitted feedback and by 2
relative to no feedback. This is a finite-horizon result for this declared
plant, not a claim that requested feedback is generally better.

The exact minimum controlled-arm margin is greater than `1/50000`. Therefore
any entrywise affinity perturbation of magnitude at most `1/100000` changes a
pairwise score difference by at most `1/50000` and preserves all controlled
routes by induction. Ten exact-rational perturbation trials also preserved
the paths and costs. Replication checks at `m=1,2` give
`(2449m,1918m,1920m)` for admitted, requested, and no feedback; repeating each
row `m` times and scaling capacities by `m` proves this identity for every
integer `m>=1`.

Reproduce with `python scripts/audit_uniform_cap_requested_better.py`. The
exact output is
[`uniform_cap_requested_better.json`](../../results/bidirectional_bias_comparison/uniform_cap_requested_better.json).
The script uses `fractions.Fraction` for routing, feedback, and accumulated
costs; its current SHA-256 is
`880671a7e5f236d0313193dd55e991910d0420d76725d00fc91ffc57495719f4`.

## Plant 3: additional heterogeneous requested-better witness

An independent compact witness is fully specified and proved in
[`bidirectional_bias_comparison_theorem_2026-10-17.md`](bidirectional_bias_comparison_theorem_2026-10-17.md).
It uses `E=4`, `K=2`, `T=8`, `C=(1,2,3,3)`, gain `1/100`, and the displayed
eight-row rational affinity matrix. For horizon `H=34`:

| Controller | Cumulative overflow | First unsaturated state | Minimum Top-2 cutoff margin, states 0–33 |
|---|---:|---:|---:|
| Admitted feedback | 240 | 33 | `21/31250` |
| Requested feedback | 238 | 46 | `9971/1000000` |
| No feedback | 238 | never | strictly positive on this horizon |

This is an exact two-assignment requested-feedback advantage. On replication
factor `m`, counts and costs scale by `m`, while the bias and routing paths are
unchanged, giving `240m` versus `238m` versus `238m`.

The minimum margin across both controlled arms and all 34 compared states is
`21/31250`. Any entrywise affinity perturbation with absolute value at most
`1/10000` changes each pairwise score gap by at most `1/5000`, so the selected
Top-2 sets stay fixed. Inductively, the feedback and bias trajectories stay
fixed too. The script sampled 100 deterministic perturbation matrices from
`{-1/10000,0,1/10000}` using seed `20261017`; all 100 retained both paths and
the exact overflow totals. Replication checks at `m={1,2,5,10}` also pass.

Reproduction: `python scripts/audit_bidirectional_bias_comparison.py`. The
machine-readable result is
`results/bidirectional_bias_comparison/strict_requested_better_witness.json`.
All arithmetic in this audit uses `fractions.Fraction`. Script SHA-256:
`af3abfcc13683ae62b61562d86cf3a218788229c196a25cb2d6715f3f4e52b94`.

## Canonical proportional-pressure comparison

The professor's integrated candidate uses a signed expert-bias update, while
the canonical formal definition uses proportional gauge-pressure feedback.
To avoid transferring a signed-bias result to different dynamics, the exact
same `E=8,K=2,T=128,C=32,H=120` affinity fixture was separately run under the
formal update

```text
q_next = P_g(q + eta*gamma*(L/(K*T) - mu)),   delta=0
scores = affinity - gamma*q
```

with `gamma=1`, uniform `mu`, and `eta` in `{1/100,1/10,1/2,1}`. Arithmetic,
Top-2 selection, clipping, and overflow accumulation are exact rational. All
routes are strict over the full trajectory grid. The cumulative overflow is:

| `eta` | Admitted feedback | Requested feedback | No feedback |
|---:|---:|---:|---:|
| `1/100` | 1,920 | 1,920 | 1,920 |
| `1/10` | 1,920 | 1,920 | 1,920 |
| `1/2` | 1,920 | 1,920 | 1,920 |
| `1` | 1,920 | 1,874 | 1,920 |

The dropless negative control gives identical requested- and admitted-pressure
paths at every `eta`. At `eta=1`, requested feedback reduces overflow by 46 on
this single fixed plant. At the three smaller gains, all three arms have the
same overflow. This demonstrates that the controller law and step size affect
the observed comparison; this one plant alone does not prove a universal
advantage for requested feedback. The signed-bias two-sided theorem above
remains separate from the proportional pressure controller.

The requested and admitted route paths at `eta=1` are certified unchanged on
the exact open interval
`(18944223025711/18945312500000,
38087479892954599/38085937500000000)`. This is approximately
`(0.99994249,1.00004050)`. On that entire interval, the requested-pressure
arm retains the 46-assignment overflow advantage. The certificate intersects
the selected-versus-unselected affine score inequalities along both complete
120-step paths (184,320 inequalities per arm); an exact midpoint run also
reproduces both paths and costs. This is a local step-size robustness theorem
for one fixture, not a parameterized capacity/affinity-family theorem.
At `eta=1`, the exact minimum controlled-arm cutoff margin is
`47149144803/2500000000000000`. Thus every entrywise affinity perturbation of
magnitude at most `1/1000000` preserves both trajectories, since it changes
any pairwise gap by at most `1/500000`; the audit also checks six perturbed
signal/plant cells exactly.

The opposite ranking holds under the same canonical pressure law on a strict
`E=3,K=1,T=3,C=(1,1,1)` plant with affinity rows
`(0,0,1),(0,0,1),(0,1,0)`, `gamma=1`, and `H=12`: for every `eta>3`,
admitted feedback has overflow 18 and requested feedback 23. No feedback has
overflow 12 on this witness, so the comparison does not say that admitted
feedback beats doing nothing. At `eta=4`, the routes have minimum cutoff
margin `1/3`; the ranking survives every entrywise affinity perturbation with
magnitude strictly less than `1/6`. See the exact constructive statement
and proof in
[`canonical_pressure_two_sided_comparison_2026-10-17.md`](canonical_pressure_two_sided_comparison_2026-10-17.md).
Together with the `E=8` requested-better witness, this proves that neither
signal universally dominates the other for the canonical proportional
pressure controller under uniform exact-total capacities.

Reproduce with
[`audit_canonical_pressure_uniform_fixture.py`](../../scripts/audit_canonical_pressure_uniform_fixture.py).
The exact output is
[`canonical_pressure_uniform_fixture.json`](../../results/bidirectional_bias_comparison/canonical_pressure_uniform_fixture.json);
the script SHA-256 is
`0899cf9e0e78b792adac889988e311a6797b00ab48344b875e2fae712904673c`.

## Exact controls for the professor's score-drop suggestion

For each expert `e`, let `S_e` be its requested routes and let an independent
per-expert policy admit the highest-ranked `min(|S_e|,C_e)` routes. Then,
regardless of route score order,

```text
|admit(S_e)| = min(|S_e|, C_e), hence A_e=min(R_e,C_e).
```

The score- versus position-ranked runs in Plant 1 verify this at trajectory
level. Therefore the report's score-ranked dropping cannot change *expert
admitted counts* under independent per-expert capacity. A shared device/group
budget can make the count vector depend on route ordering, but that is a
separate admission map and is not part of either theorem above.

The no-clipping control checks the complementary identity: when `A=R`, the
requested and admitted feedback paths coincide exactly. The full-saturation
uniform-capacity control is also included in the earlier
[`capacity_regime_sweep_results_2026-10-17.md`](capacity_regime_sweep_results_2026-10-17.md):
the admitted sign update freezes when `A=C*1`.

## What this controlled evidence establishes

Together, Plant 1 and the uniform-capacity Plant 2 establish a rigorous,
robust **two-sided** result:
neither requested nor admitted sign feedback universally minimizes finite-
horizon overflow in the declared Top-K/per-expert-clipping class. The
ordering can reverse without ties and persists under open-set perturbations.
The result makes the professor's value-of-information question conditional:
the decision value of the signal depends on the plant, capacity regime,
controller, and horizon.

The perturbation trials are robustness checks inside known margin regions,
not random samples from a population of routers. The examples do not
identify a predictive condition for which signal wins, establish production
prevalence, price the signal, or show a validation-loss or serving benefit.
The canonical proportional-pressure comparison now has two exact opposite-
ranking witnesses, as stated in
[`canonical_pressure_two_sided_comparison_2026-10-17.md`](canonical_pressure_two_sided_comparison_2026-10-17.md).
It still has no predictive family criterion or separation from the
polyhedral testing benchmark.
The per-expert score-ordering identity rejects the report's proposed
score-order count mechanism for this model; device-level score dropping is a
different hybrid model and is not used to support these results.

## Relevance to the professor's integrated candidate

These are the exact controlled synthetic results to complete before any
training study. They establish opposite strict overflow rankings separately
for the canonical proportional-pressure controller and the professor's
signed-bias controller, so neither controller admits a universal signal
ordering under the stated per-expert clipping model. They also establish that
score selection alone does not alter `A` under independent per-expert caps.
The open research question is a predictive condition for signal selection,
not whether either feedback signal universally wins.

The next theorem needed for a conference-level paper is a checkable condition
on the Top-K score arrangement, capacities, gain, and horizon that predicts
the sign and magnitude of
`J_H(admitted)-J_H(requested)`. It must be compared to the independent
finite-outcome testing benchmark already in the Phase-1 reduction audit. If
the condition transfers unchanged to that benchmark, it is not a new
Top-K-specific control theorem. The system-cost term must be measured on the
actual implementation; source inspection shows that replacing one expert
count vector with another may reuse an existing collective, so an extra
collective cannot be presumed.

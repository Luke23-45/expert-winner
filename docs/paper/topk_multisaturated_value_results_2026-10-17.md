# Top-2 multi-saturation pilot: results and proof status

**Protocol:** [fixed pilot protocol](topk_multisaturated_value_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_multisaturated_value_pilot.py`](../../scripts/run_topk_multisaturated_value_pilot.py)  
**Machine-readable output:** [`../../results/topk_multisaturated_value_pilot/summary.json`](../../results/topk_multisaturated_value_pilot/summary.json)  
**Paired samples:** [`../../results/topk_multisaturated_value_pilot/paired_plants.csv`](../../results/topk_multisaturated_value_pilot/paired_plants.csv)

## Exact population construction

For Gumbel-Top-2 with base weights `(2,1,1)` and `(1,2,1)`, enumerating the
six Plackett-Luce rankings gives the initial inclusion vectors

```text
world 0: (5/6, 7/12, 7/12)
world 1: (7/12, 5/6, 7/12).
```

The capacity vector is `(11/20,11/20,9/10)`, with exact total `K=2`. Thus
experts 1 and 2 are both overloaded in both worlds, while expert 3 is
under-capacity. The worlds only exchange load between the two saturated
experts; expert 3 has the same request distribution in both worlds.

The target-matched pressures have exact gauge representatives

```text
q^0=(log 6, log 3, 0),    q^1=(log 3, log 6, 0).
```

They produce the target inclusion vector in their respective worlds. Using
the wrong world's pressure yields overflow `459/1540`; therefore using one
fixed target pressure across the equally likely worlds has risk
`459/3080 = 0.1490259740...`. This is an exact feasible common-action risk,
not a proof that it is the minimum over all common pressures.

The runner now verifies the zero-pressure world probabilities, target
inclusion vector, cross-world inclusion vector, no-feedback cost, and fixed
common-action cost by exact enumeration of the six Plackett-Luce rankings
with rational arithmetic. The data-generation and finite-batch rates remain
Monte Carlo draws from the exact omitted-expert multinomial law.
The no-feedback action `q=0` has exact equal-prior population overflow
`19/60 = 0.3166666667...`.

## Controlled sample results

The run used 500 paired draws at each of `T=1,800`, `7,200`, and `28,800`.
Each world-specific request count was sampled from the exact Top-2
Plackett-Luce omitted-expert multinomial law. The coupling shares the
omitted-expert-3 count. No clipping was applied in the negative control.

| `T` | Identical clipped admitted vectors | Identical requests with no clipping | Requested classifier errors |
|---:|---:|---:|---:|
| 1,800 | 498/500 | 0/500 | 0/500 |
| 7,200 | 500/500 | 0/500 | 0/500 |
| 28,800 | 500/500 | 0/500 | 0/500 |

The classifier chooses world 0 when `R_1/T > 17/24` and world 1 otherwise.
Its selected target-matched action had mean population overflow below
`4e-16` in every cell; the fixed common action `q^0` had population risk
`0.1490259740...` in every cell. The no-feedback baseline had population
risk `0.3166666667...`. Action risks are calculated from the exact
Plackett-Luce population probabilities, not estimated from simulation
draws. All request-mass and `A=min(R,C)` checks passed. The runner, protocol,
CSV, and summary hashes reproduced byte-for-byte across two runs:

| Artifact | SHA-256 |
|---|---|
| Runner | `adb4951fb8188c328f91914da2122172bc8f1d43e63408741e1463c5cc8bca35` |
| Protocol | `3d0289396ce1dedba6e424d5f5012c73c1bf42eef3e1e358f30fb2f8f3601498` |
| Paired samples | `8a8ac7958e770950f3f68bd99ee0c8aa603f2b601d085a20b50ce2dee7543875` |
| Summary | `da34291ad6bc4a12f15c73c96db3d7980e9c54185e7621b4ad426e84b4dc5fd2` |

## What this establishes

This is evidence that the **mechanism** in the canonical two-saturated
Top-1 construction is not confined to Top-1: in one nondegenerate Top-2
Gumbel plant, clipping hides the split between two overloaded experts,
whereas requested counts identify which target-matched pressure to use.
The exact feasible common action incurs positive risk, and the numerical
search over `q_1,q_2 in [-8,8]` found the same risk. The search is not a
global-optimality certificate.

## What remains unproved

This pilot does **not** prove a Top-2 value-of-information theorem. In
particular, it does not lower-bound the risk of every common pressure action
or every admitted-signal policy, nor does it quantify the finite-`T`
admitted-law total-variation error. A requested policy beating one fixed
admitted diagnostic is not an optimal-policy value gap. The next proof
obligation is to establish a positive lower bound on

```text
inf_q  1/2 * (L_0(q) + L_1(q))
```

for this Top-2 world pair, then combine it with an explicit concentration
bound for the full admitted observation. If that lower bound cannot be
proved, the Top-2 extension remains an experiment-only lead and the proved
Top-1 theorem remains the formal value result.

This does not resolve the benchmark-reduction or literature-novelty gates;
it is a focused extension attempt within the existing formal definition.

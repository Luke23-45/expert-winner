# Exact cost sensitivity of the existing two-sided signal witnesses

## Purpose

Professor Report 1 proposes comparing the value of requested-count feedback
with the cost of obtaining it. The existing experiments already establish
opposite overflow rankings for requested and admitted feedback. This note
converts those exact outcomes into a transparent sensitivity calculation;
it does not assume a measured system cost.

Define a hypothetical incremental charge `kappa >= 0` for using requested
counts on each of `H` updates, in units commensurate with one overflowed
assignment. For the fixed controller arms, let

```text
L_R(kappa) = J_R + H*kappa,
L_A        = J_A,
L_none     = J_none.
```

This is a post hoc price sensitivity, not an optimal-policy value-of-
information calculation. The conversion from latency, communication bytes,
or energy to overflow-equivalent units is deliberately left unspecified.

## Exact paired witnesses

Both input result sets were regenerated with exact-rational audit scripts on
2026-10-17.

| Fixed Top-K witness | Horizon | `J_A` | `J_R` | `J_none` | `kappa` range where requested beats admitted | Range where requested beats both |
|---|---:|---:|---:|---:|---:|---:|
| P2f replicated `E=3, K=2` family, `m=1` | `H>=4` | `10H+3` | `>=10H+8` for `H>=9`; exact through `H=8` | `11H` | none for `kappa>=0` | none |
| Uniform-capacity ring-pair fixture, `E=8, K=2, T=128, C=32` | `120` | `2449` | `1918` | `1920` | `0<=kappa<177/40` | `0<=kappa<1/60` |

For the first row, the proved formulas imply

```text
L_R(kappa) - L_A >= 5 + H*kappa > 0,  H>=9.
```

Thus admitted feedback beats requested feedback on this exact family for
every nonnegative requested-signal surcharge. For the second row,

```text
L_R(kappa) - L_A    = -531 + 120*kappa,
L_R(kappa) - L_none =   -2 + 120*kappa.
```

Requested feedback beats admitted feedback below `kappa=177/40`, but beats
all three fixed arms only below `kappa=1/60`. The no-feedback comparison is
the binding one in that fixture.

For row replication `m`, all overflow differences in each construction scale
by `m`; the price term scales by `H*kappa`. Therefore the threshold against
the fixed baseline scales linearly with `m` if `kappa` remains a fixed
per-update charge. This is a mathematical sensitivity statement, not a
claim that real telemetry cost is independent of batch size.

## Experimental status and limits

- Exact Top-2 routing, count clipping, signs, and overflow were checked by
  [`audit_uniform_cap_requested_better.py`](../../scripts/audit_uniform_cap_requested_better.py)
  and [`audit_top2_all_horizons.py`](../../scripts/audit_top2_all_horizons.py).
- P2f's analytic route proof establishes its all-horizon bound; exact
  rational audits cover registered replication/gain cells through `H=100`.
- These are two fixed families under the same declared signed-bias controller
  and per-expert clipping model. They establish signal non-dominance, not a
  predictive capacity/gain criterion for arbitrary affinity matrices.
- No physical value of `kappa` is measured. In the pinned Megatron-Core path,
  the expert-bias update already reduces an expert-count vector; whether
  switching its contents from post-drop to pre-drop counts adds any collective
  or latency must be established by profiling that implementation.
- The exact finite outcome-map benchmark can reproduce either fixed witness.
  This sensitivity calculation therefore does not defeat the existing
  class-level reduction and does not establish a top-conference contribution.

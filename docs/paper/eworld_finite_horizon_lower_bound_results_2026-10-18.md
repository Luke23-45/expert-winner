# Exact DP results: finite-horizon E-world lower bound

**Theorem audited:** [`eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md`](eworld_finite_horizon_all_policy_gap_theorem_2026-10-18.md).
**Protocol:** [`eworld_finite_horizon_lower_bound_protocol_2026-10-18.md`](eworld_finite_horizon_lower_bound_protocol_2026-10-18.md).
**Runner:** [`../../scripts/audit_eworld_finite_horizon_lower_bound.py`](../../scripts/audit_eworld_finite_horizon_lower_bound.py).
**Exact data:** [`../../results/eworld_finite_horizon_lower_bound_2026-10-18/`](../../results/eworld_finite_horizon_lower_bound_2026-10-18/).

## Audit outcome

The audit checked 156 combinations of four valid capacity triples,
`N=2,...,7`, and post-initial horizon `D=1,...,N+2`. All exact rational DP
values were at least the theorem's lower bound; all 156 bounds also exceeded
the stated half-minimum simplification. The exact DP optimizes over every
subset-probe action and causal continuation under unrestricted movement,
which equals the full pressure value for this family by the existing
all-pressure action-dominance proof.

For the reference parameters `(C,E_S,C_sink)=(50,20,30)` at `D=N-1`:

| N | Exact post-initial DP value | Theorem lower bound | Bound / DP |
|---:|---:|---:|---:|
| 2 | 20 | 5 | 0.250 |
| 3 | 40 | 80/9 | 0.222 |
| 4 | 60 | 90/7 | 0.214 |
| 5 | 80 | 320/19 | 0.211 |
| 6 | 100 | 125/6 | 0.208 |
| 7 | 120 | 720/29 | 0.207 |

Across the whole grid, the lower-bound-to-DP ratio ranged from `0.2069` to
`0.6154`. The singleton-probe upper bound `L(N-1)/2` was attained in 69 of
the 96 cells with `D>=N-1`; it was not asserted as universally optimal.

## What this verifies

This is an exact arithmetic check that the new all-policy bound is consistent
with the exact optimum of the unrestricted E-world instance over the declared
grid. The proof itself covers all `N`, all permitted integer parameters, and
all causal admitted policies under its assumptions; the grid does not extend
that proof. The experiment does not compare against a different benchmark,
clear the adaptive-testing novelty question, or validate a hardware or model
quality effect.

## Reproduction hashes

- protocol SHA-256: `0d49c9c6458f850ba148eb04904317937546adee027f44de8c3b75796d62c1d8`
- runner SHA-256: `1af2a8bb58546d799ce64f27ccdf49855c05b88edf1d20063b2fd0a5048c85a0`
- Bellman source SHA-256: `9884cccba530d2091d7dacf18c3968f743b68e8e98cf80bc906eca1c0710b108`
- cells SHA-256: `d55d133df477921aa28701a08c0ab6f8cbfe6d370e6ecd5740ed08e8831f008c`

Rerun from the repository root with:

```powershell
python scripts/audit_eworld_finite_horizon_lower_bound.py
```

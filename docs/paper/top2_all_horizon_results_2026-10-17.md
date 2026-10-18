# Exact-rational all-horizon audit for the Top-2 signed-bias family

**Question.** Does the exact finite-horizon P2f advantage persist at every
horizon, or only through the originally registered nine batches?

**Method.** `scripts/audit_top2_all_horizons.py` reuses the audited exact
Top-2 routing, sign-feedback, and gauge-centering functions from the P2f
runner. It simulates admitted, requested, and no-feedback arms with Python
`Fraction` arithmetic for every horizon from 1 through 100. The audit pairs
three replication factors (`m=1,3,10`) with three gains
(`9/40,6/25,1/4`) in theorem units, for nine trajectories per controller.
These gains are points in the theorem's open interval `(1/5,11/40)`.

**Assertions checked in every cell.** Admitted overflow equals `11Hm` for
`H≤2` and `10Hm+3m` for `H≥3`; no-feedback overflow equals `11Hm`; requested
overflow equals `11Hm` through `H=8`; for `H≥9`, requested overflow is at
least `10Hm+8m`. The audit also checks that all three arms tie through
`H=3` and admitted feedback is strictly lower than the other two for every
`H=4,…,100`.

**Result: PASS.** All nine exact-rational cells satisfy every assertion at
all 100 horizons. Selected cumulative costs for `m=1` and gain `6/25` are:

| Horizon | Admitted | Requested | No feedback |
|---:|---:|---:|---:|
| 3 | 33 | 33 | 33 |
| 4 | 43 | 44 | 44 |
| 8 | 83 | 88 | 88 |
| 9 | 93 | 98 | 99 |
| 20 | 203 | 208 | 220 |
| 100 | 1003 | 1008 | 1100 |

The machine-readable output is
[`all_horizon_audit.json`](../../results/top2_signed_bias_separation/all_horizon_audit.json).
Reproduce from the repository root with:

```powershell
python scripts/audit_top2_all_horizons.py
```

This is a deterministic audit of one parameterized family, not evidence that
the ranking is typical across MoE routers. The proof only gives a fixed
additive lower bound against requested feedback after batch 8; it does not
give a positive asymptotic *normalized* gap. It establishes no controller
class separation, trained-model benefit, or escape from the finite-instance
outcome-map benchmark.

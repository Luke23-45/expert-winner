# Results: exact rank threshold under saturated Top-K feedback

**Theorem:** [`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md), exact local-rank corollary.
**Protocol:** [`saturation_rank_threshold_experiment_2026-10-18.md`](saturation_rank_threshold_experiment_2026-10-18.md)
**Runner:** [`../../scripts/run_saturation_rank_threshold_experiment.py`](../../scripts/run_saturation_rank_threshold_experiment.py)
**Artifacts:** [`../../results/saturation_rank_threshold_2026-10-18/`](../../results/saturation_rank_threshold_2026-10-18/)

## Result

The deterministic exact-expectation audit covered 36 cells: `E=4`, all
`K in {1,2,3}`, `T in {160,320,640}`, and saturation multiplicities
`m in {0,1,2,3}`. All finite relative Jacobians had full quotient rank 3;
all 36 limiting ranks matched `3` for `m=0` and `4-m` for `m>=1`; and all
cells met the singular-value bound requiring at least `m-1` singular values
no larger than the largest saturated-coordinate attenuation. The maximum
absolute difference between the analytic and finite-difference requested,
admitted, and relative Jacobians was `5.59e-10`.

For `K=2`, the smallest relative singular value illustrates the threshold:

| Saturated experts `m` | `T=160` | `T=320` | `T=640` | Limiting rank |
|---:|---:|---:|---:|---:|
| 0 | 1.0000 | 1.0000 | 1.0000 | 3 |
| 1 | 0.2073 | 0.1998 | 0.2142 | 3 |
| 2 | 0.05194 | 0.01081 | 0.000681 | 2 |
| 3 | 0.04899 | 0.01075 | 0.000557 | 1 |

With one saturated expert, its attenuation reached `3.22e-4` at `T=640`,
while the smallest relative singular value remained `0.2142`: the missing
single coordinate is recoverable from the mass-conservation constraint. With
two or three saturated experts, respectively one or two singular values
shrank with the clipped response. The limiting rank falls by exactly `m-1`.
The `m=0` no-clipping control had all three singular values equal to one.

These are deterministic numerical checks of the theorem, not a proof. The
proof is the linear-algebra argument in the linked corollary; the experiment
checks its numerical realization for the registered Gumbel-Top-K grid.

## Claim boundary

The result sharpens the professor’s sensitivity-loss suggestion: the
asymptotic local **mean-response** rank loss is exactly determined by
saturation multiplicity, with no exact rank loss at finite `T`. It does not
show that the full finite-batch admitted-count law is non-identifying, that
any controller has a long-run performance gap, or that this result separates
from generic clipped-signal/adaptive-testing theory. It therefore does not
settle the top-conference benchmark gate.

## Reproduction record

The run summary records:

- Protocol SHA-256: `966462942412592ecc74775cd617b853690d92404a3dacbd42977758cfd19ce3`
- Runner SHA-256: `4fb828a9663834a39f4322e2e2a069497a8940dd4c305d0160b38e20796098cf`
- Cell CSV SHA-256: `ab74383a6df6ae4fef4393f46b2d2193a394a0bf3767a14a4d29adfba6be7521`

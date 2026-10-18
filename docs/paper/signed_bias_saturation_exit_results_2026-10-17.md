# Exact audit of signed-bias saturation exit

The executable
[`audit_signed_bias_saturation_exit.py`](../../scripts/audit_signed_bias_saturation_exit.py)
checks the finite-exit theorem and its exact plant using rational arithmetic.

## Base plant

For all three gains, the admitted arm preserves the initial saturated route
counts until state $N-1$, then exits at state $N-1$ under the fixed lower-index
tie rule. The theorem's strict upper bound is one state larger:

| $\gamma$ | Theorem bound $N$ | Actual exit $\tau$ | Admitted overflow at exit | Requested exit | Requested overflow at exit |
|---:|---:|---:|---:|---:|---:|
| $1/1000$ | 501 | 500 | 13 | 500 | 10 |
| $1/500$ | 251 | 250 | 13 | 250 | 10 |
| $1/100$ | 51 | 50 | 13 | 50 | 10 |

At each exit, the admitted controller routes every token to experts 1 and 2;
the requested controller routes across experts 1, 2, and 3. The controllers
are paired on the same fixed affinity matrix, capacities, initial bias, and
step size. These base-plant outcomes occur at Top-2 cutoff ties and depend on
the declared lower-index tie rule; they are not an open-set performance
separation.

## Perturbation audit

Twenty deterministic affinity perturbations were generated with seed range
`20261018`–`20261037`; each entry independently receives noise
$-1/100$, $0$, or $1/100$. For each plant, all three gains above were run,
for 60 paired cells total. Exact assertions verify:

- all plants begin at $R=(2,4,3,7)$ and $A=C=(1,2,3,3)$;
- the admitted slope gap condition holds;
- the first admitted unsaturated state is no later than the theorem bound.

**Result: PASS in all 60 cells.** Admitted exit indices range from 49 to 505;
the corresponding theorem bounds range from 51 to 511. Exit overflow varies
across the perturbations, so the audit does not claim a uniform cost ordering.
In the paired requested arm, 29 cells exited saturation within the 10,000
state observation window and 31 remained saturated through that window. Of
the 29 cells where both arms exited, admitted exit overflow was higher in 9,
equal in 10, and lower in 10. This is a finite diagnostic only; no
requested-feedback exit theorem or robust cost ranking is claimed.

The full rational records are in
[`summary.json`](../../results/signed_bias_saturation_exit/summary.json).
Reproduce from the repository root with:

```powershell
python scripts/audit_signed_bias_saturation_exit.py
```

The audit checks the theorem on this family and its stated perturbations; it
does not prove the theorem itself, which is established analytically in
[`signed_bias_saturation_exit_theorem_2026-10-17.md`](signed_bias_saturation_exit_theorem_2026-10-17.md).

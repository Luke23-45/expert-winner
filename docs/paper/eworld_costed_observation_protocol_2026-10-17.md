# Costed E-world observation: exact DP audit protocol

## Question

For the existing Top-1 E-world family, what is the exact finite-horizon
overflow value when the controller observes admitted counts, and what
one-time price for a requested-count observation is justified by that value?
This audit uses the existing unrestricted-movement subset-probe reduction;
it does not introduce a new admission rule or controller.

## Fixed parameter grid

Enumerate every combination of:

- number of regular worlds `N=2,...,20` (plus the sink expert);
- extra overload mass `s in {1,2,5}`;
- regular-expert capacity `C in {2s,3s,5s}`;
- post-initial horizon `h=0,...,N+1` (the common initial batch is separate).

Set `C_sink=C-s`, `E=N+1`, `K=1`, `T=NC+s`, uniform prior on the `N`
worlds, zero initial pressure, and no movement restriction. These choices
satisfy the existing E-world capacity conditions and give
`L=s+C-C_sink=2s`.

## Exact recurrence and controls

Use rational arithmetic in the exact Bellman recursion already derived for
the E-world family. At posterior support size `n`, a wait action costs `s`
and leaves the support unchanged. A subset probe of size `b` has the existing
exact inside/outside overflow costs:

```text
c_in(1)=0
c_in(b)=L+(b-2)C,  b>=2
c_out(b)=L+(b-1)C.
```

The script must verify, for every grid cell, that the exact DP value equals
`s * min(h, N-1)` for the `h` post-initial rounds. It must also verify the
optional buy/no-buy value. The admitted-only option costs
`s + s*min(h,N-1)` including the initial overflow; buying the one-time
requested observation costs `s+kappa`, since it identifies the world and the
known-world controller then holds a zero-overflow pressure. The optional
minimum is therefore `s+min(kappa,s*min(h,N-1))`, with break-even
`kappa_star=s*min(h,N-1)`. At `h=0`, `kappa_star=0` and a free observation
ties with skipping.

All DP values and comparisons are exact `Fraction` calculations. There are
no random seeds, tunable parameters, or statistical generalization claims.

## Claim boundary

The grid checks a theorem candidate over a finite parameter range; the proof
must separately establish the formula for all admissible integers. The
one-time price is a mathematical penalty in overflow units. It is not a
measured communication/latency cost. This family remains an exact active-
testing instance, so the audit cannot establish separation from the general
outcome-map benchmark.

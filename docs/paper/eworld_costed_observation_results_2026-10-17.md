# Exact E-world costed-observation DP audit: results

**Theorem:** [exact one-shot break-even theorem](eworld_costed_observation_value_theorem_2026-10-17.md)  
**Protocol:** [fixed audit protocol](eworld_costed_observation_protocol_2026-10-17.md)  
**Executable:** [`audit_eworld_costed_observation.py`](../../scripts/audit_eworld_costed_observation.py)  
**Artifact:** [`summary.json`](../../results/eworld_costed_observation/summary.json)

The exact-rational subset-probe Bellman audit passed all 171 parameter cells:

- `N=2,...,20` regular worlds;
- excess overload `s in {1,2,5}`;
- regular capacity `C in {2s,3s,5s}`, with `C_sink=C-s`;
- every support size `n=1,...,N` and post-initial horizon `h=0,...,N+1`.

All 29,583 Bellman values matched

```text
V_h(n)=s*min(h,n-1).
```

The same audit verified that the initial requested vectors are distinct by
world, the admitted vector is common, and the one-time price threshold equals
the admitted value at every checked horizon. It also checked 8,892 exact
buy/no-buy comparisons at four prices per horizon against
`s+min(kappa,s*min(h,N-1))`, including the zero-horizon, zero-price tie. This
is a finite exact audit of the theorem and recurrence; the all-integer result
rests on the analytic proof in the theorem document.

The experiment supports the professor's costed-observation suggestion in
the existing Top-1 family. It does not measure a system cost. Because the
all-pressure reduction yields the same subset-probe Bellman recursion, these
results remain an exact MoE application of adaptive testing, not a separation
from it.

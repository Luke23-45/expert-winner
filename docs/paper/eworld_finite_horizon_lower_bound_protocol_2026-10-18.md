# Exact DP audit protocol: finite-horizon E-world lower bound

## Question

Does the closed-form all-policy lower bound (FH-LB) hold against the exact
unrestricted-movement value of the canonical Top-1 E-world family, across
multiple world counts, capacities, and finite horizons? The DP minimizes over
all subset probes and all causal follow-on policies. The existing
all-pressure action-dominance proof makes this the exact unrestricted-pressure
value for the family.

## Registered calculation

- World counts: `N in {2,3,4,5,6,7}`.
- Capacity triples `(C,E_S,C_sink)`:
  `(50,20,30)`, `(45,20,30)`, `(55,20,30)`, `(100,20,20)`.
- Post-initial horizons: `D in {1,...,N+2}`.
- For each cell, compute the exact rational subset-probe Bellman value
  `V_D(N)` and compare it with
  `G_D=abD/(a+b(D-1))`, where
  `a=(E_S+C-C_sink)(N-1)/2` and `b=E_S/4`.
- Also verify the scale bound
  `G_D >= (1/2)*min(a,bD)` exactly in rational arithmetic.

The DP starts after the common initial round, so the comparison is between
post-initial values. No Monte Carlo or confidence intervals are involved.
The theorem's lower bound itself covers movement-constrained policies too;
the unrestricted DP is used here as an exact value audit.

## Required checks

1. All parameter rows satisfy `E_S<=C_sink<C-E_S/2` and `a>b`.
2. Every exact DP value is at least the rational FH-LB.
3. Every rational FH-LB is at least the displayed half-minimum bound.
4. For `D>=N-1`, record whether the singleton-probe upper bound
   `a=L(N-1)/2` is attained by the DP; do not assert equality unless the
   computed Bellman values establish it.
5. Preserve exact fractions in the output CSV and summary; decimals are for
   readability only.

This audit checks the theorem against the exact policy optimum in this
unrestricted E-world instance. It does not establish literature novelty,
generalize beyond the family, or show separation from an abstract adaptive-
testing benchmark that retains the same outcome and cost maps.

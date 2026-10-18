# Preregistered full-support-affinity check for the arbitrary-Top-K theorem extension

**Question.** Does the same paired two-step overflow gap persist for iid Gaussian, logistic, and Gumbel affinities under the canonical Top-K/per-expert-clipping/proportional-pressure model? Uniform[0,1] is included as a compatibility control for the existing closed-form theorem.

**Primary endpoint.** For each plant and displacement `d`, record `G_T=(J_0^A+J_1^A-J_0^R-J_1^R)/T`. The theoretical large-batch limit is `p_F(d)-K/E`, where `p_F(d)=integral G_(E,K)(F(x+d)) dF(x)` and `G_(E,K)(u)=sum_(j=0)^(K-1) binom(E-1,j)(1-u)^j u^(E-1-j)`. Uniform[0,1] uses the existing exact `Phi_(E,K)(d)-K/E` formula. Numerical quadrature settings and method are recorded by the runner.

**Locked grid.** `E=4`, `K in {1,2,3}`, `T in {2400,9600}`, `d in {1/4,1/2}`, affinity laws `{Uniform[0,1], Normal(0,1), Logistic(0,1), standard Gumbel}` and 30 independent plants per `(law,K,T)`. Capacities use `r=min(K/E,1-K/E)/2`, `C_1/T=K/E-r`, and `C_e/T=K/E+r/(E-1)` for `e=2,3,4`; all are integral for both T values and sum exactly to `KT`. Set `eta=d*K/r`, `gamma=1`, `delta=0`, `mu_e=1/E`, and `q_0=0`.

Each plant samples one `T x E` affinity matrix and reuses it for both routing steps, both feedback arms, both displacement values, and the no-feedback control. Routing uses stable score sorting with lower expert index as the tie rule. Step 0 computes `R_0`, `A_0=min(R_0,C)`, and overflow; each feedback arm then makes exactly one canonical update from either `R_0` or `A_0`, routes step 1 on the same affinity matrix, and records two-step overflow. No-feedback remains at `q=0`.

**Required controls and invariants.** Assert `sum R=KT`, `A=min(R,C)`, `sum J=sum(R-A)`, and equal step-0 overflow across paired arms. For each plant and displacement, repeat requested/admitted arms with `C_e=T` and require identical pressures/routes and zero overflow. Report exact score ties, paired means, sample standard deviations, and two-sided 95% paired-mean t intervals; do not drop ties or plants. Do not interpret repeated fixed-seed execution as new statistical evidence.

**Interpretation boundary.** The registered experiment is a finite-sample check of the stated asymptotic family theorem over selected score laws and parameters. It cannot prove the theorem, establish a universal controller ranking, show trained-model or serving gains, price telemetry, or evade exact finite-instance outcome-map representation.

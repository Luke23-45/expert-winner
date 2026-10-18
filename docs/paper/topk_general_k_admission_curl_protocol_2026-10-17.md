# Controlled exact-expectation audit: admitted-field curl for Gumbel Top-K

**Question.** Does the existing clipping-attenuation/curl theorem remain visible
for Top-(K) values (K>1), under the same per-expert capacity rule and
gauge quotient?

**This is an extension of the current formal model.** It changes neither the
admission rule nor the controller. It tests the one-step expected-field
consequence for (E=4), (Kin\{1,2,3}).

## Locked synthetic model

- Four experts; every token has an independent standard-Gumbel perturbation
  added to the fixed logits, then selects its top (K) experts.
- Pressure enters the logits as `logit_e - q_e`; set `gamma=1`.
- Independent per-expert admission is exactly `A_e=min(R_e,C)`.
- Use uniform exact-total capacities `C=K*T/4`, with
  `T in {32,128,512}`.
- The skewed logit vector is `(1.2, 0.35, -0.4, -1.0)`. Two controls use
  uniform logits and, separately, no clipping (`C=T`).
- Evaluate at `q=0` and on the pressure quotient. The reported curl uses
  tangent directions `u=e1-e4`, `v=e2-e4` and is
  `u^T D F_A v - v^T D F_A u`.

## Evaluation and checks

Gumbel-Top-K rankings have the Plackett-Luce sequential-order law; this is the
standard Gumbel-Top-K sampling-without-replacement identity
([Kool, van Hoof, and Welling](https://arxiv.org/abs/1903.06059)). The runner
enumerates all `4!` rankings to obtain exact-in-expectation inclusion
probabilities, then evaluates each marginal clipped-count expectation using
the finite Binomial sum. It computes the pressure Jacobian of the inclusion
probabilities and checks the identity

\[
 D F_A(q)=\frac1K P_0\,\operatorname{diag}(\alpha_e)\,D p(q),
 \qquad
 \alpha_e=\Pr\{\operatorname{Binomial}(T-1,p_e)<C\}.
\]

The primary outcome is admitted-field quotient curl. The chain-rule Jacobian
is checked against a central finite difference of the directly evaluated
expected admitted field. Requested-field curl, symmetry, and no-clipping
controls are reported separately.

## Preregistered pass criteria

1. Requested-field curl has magnitude below `2e-7` in every cell.
2. Direct versus chain-rule admitted Jacobian max error is below `2e-7`.
3. The request-probability Jacobian is symmetric to `2e-7`.
4. Each skewed, clipped cell has a nonzero negative curl with magnitude above
   `1e-5`.
5. Both uniform-logit and no-clipping controls have curl below `2e-7`.

This is a deterministic exact-expectation computation (floating-point
evaluation of finite sums), not a Monte Carlo estimate and not a closed-loop
training experiment. The frozen executable is
[`../../scripts/run_topk_general_k_admission_curl.py`](../../scripts/run_topk_general_k_admission_curl.py).

# Expected admitted-field sensitivity and curl for Top-1 routing

**Status:** exact derivation under a declared stochastic extension of the
canonical per-expert admission rule.  
**Admission:** `A_e=min(R_e,C_e)`.  
**Purpose:** make the sensitivity and potential claims in the C2 direction
precise without changing the per-batch routing/admission definition.

## Model

There are `E` experts and `T` iid tokens. The token scores are
`s_{t,e}(q)=theta_e+G_{t,e}-gamma*q_e`, where `G_{t,e}` are independent
Gumbel random variables with scale `lambda>0`; each token requests its
highest-scoring expert (`K=1`). The pressure is interpreted modulo common
shifts. Each expert has an integer per-batch capacity `C_e` and the batch
uses the canonical admission count `A_e=min(R_e,C_e)`.

The Gumbel-max identity gives
\[
\pi_e(q):=\Pr\{e\text{ is requested by one token}}
=\frac{\exp((\theta_e-\gamma q_e)/\lambda)}
       {\sum_j\exp((\theta_j-\gamma q_j)/\lambda)}.
\]
Independence across tokens implies the marginal count law
`R_e(q)~Binomial(T,pi_e(q))`. Counts for different experts are dependent,
but the coordinate expectations and derivatives below require only these
marginal laws.

## Exact clipped-count sensitivity

For `0<=C<=T`, define
\[
h_{T,C}(p)=\mathbb E[\min\{X,C\}],\qquad X\sim\operatorname{Binomial}(T,p).
\]
Then
\[
h'_{T,C}(p)
=T\Pr\{Y<C\},\qquad Y\sim\operatorname{Binomial}(T-1,p).
\]

**Proof.** Write `X` as a sum of `T` iid Bernoulli variables. For any
function `g` on the integers,
\[
\frac{d}{dp}\mathbb E[g(X)]
=T\mathbb E[g(Y+1)-g(Y)],\qquad
Y\sim\operatorname{Binomial}(T-1,p).
\]
For `g(x)=min(x,C)`, the finite difference is one exactly when `Y<C` and
zero otherwise. This proves the identity. `\square`

Define
\[
\bar a_e(q)=\frac{\mathbb E[A_e(q)]}{T}
=\frac{h_{T,C_e}(\pi_e(q))}{T},\qquad
\alpha_e(q)=\Pr\{\operatorname{Binomial}(T-1,\pi_e(q))<C_e\}.
\]
The chain rule gives the exact Jacobian
\[
D_q\bar a(q)=\operatorname{diag}(\alpha(q))D_q\pi(q).
\]
The requested-load expectation is `E[R_e/T]=pi_e`, so `alpha_e` is the
coordinatewise ratio between admitted and requested sensitivity. In
particular, the admitted sensitivity is small when expert `e` is saturated
with high probability.

This is not exact finite-sample non-identifiability. If `C_e>=1`, then
`Pr(A_e=0)=(1-pi_e)^T`, so the exact law of `A_e` identifies `pi_e` at every
finite `T`. What vanishes under saturation is the derivative of the expected
clipped count. A statistical estimation lower bound would require a
separate observation model and is not claimed here.

## Exact-total heterogeneous-capacity witness

Take `E=3`, `K=1`, `q=0`, and
\[
\pi=(1/2,3/10,1/5),\qquad
\theta_e=\lambda\log\pi_e,
\qquad
C(T)=(2T/5,T/2,T/10),
\]
for integers `T` divisible by ten. The capacities are integer and satisfy
`sum_e C_e=T=KT`. The capacity fractions are respectively below, above, and
below the request probabilities. Therefore, as `T` grows,
\[
\alpha_1\to0,\qquad \alpha_2\to1,\qquad \alpha_3\to0.
\]

For the softmax request probabilities,
\[
J:=D_q\pi(0)
=-\frac{\gamma}{\lambda}
  (\operatorname{diag}(\pi)-\pi\pi^T),
\]
which is symmetric. On the pressure quotient test the normalized admitted
field's derivative using the tangent vectors
`x=e_1-e_3` and `y=e_2-e_3`. Its antisymmetric part is
\[
\begin{aligned}
\mathcal C_T
&=x^T D_q\bar a(0)y-y^T D_q\bar a(0)x\\
&=(\alpha_1-\alpha_2)J_{12}
 +(\alpha_3-\alpha_1)J_{13}
 +(\alpha_2-\alpha_3)J_{23}.
\end{aligned}
\]
Since `J_12=(3/20)(gamma/lambda)`,
`J_13=(1/10)(gamma/lambda)`, and
`J_23=(3/50)(gamma/lambda)`,
\[
\lim_{T\to\infty}\mathcal C_T
=\left(-\frac3{20}+\frac3{50}\right)\frac{\gamma}{\lambda}
=-\frac9{100}\frac{\gamma}{\lambda}\ne0.
\]
The projection `P_0` onto the pressure quotient does not change this test:
`x,y` are tangent, so their inner products with `P_0D_q\bar a P_0` equal
those with `D_q\bar a`. Thus the expected admitted field has nonzero local
curl and cannot be the gradient of a scalar potential for all sufficiently
large `T`. With no clipping (`C_e=T`), every `alpha_e=1`, the Jacobian is
`J`, and this curl is exactly zero.

The exact finite-binomial values and their deterministic evaluation are in
[`expected_admitted_curl_results_2026-10-17.md`](expected_admitted_curl_results_2026-10-17.md)
and [`audit_expected_admitted_curl.py`](../../scripts/audit_expected_admitted_curl.py).

## Scope and literature boundary

This is a stochastic expectation result for Top-1 with independent Gumbel
scores and heterogeneous exact-total per-expert capacities. It is not a
performance or regret theorem for a feedback controller, does not measure
the cost of requested telemetry, and does not separate the exact finite
outcome map from the polyhedral benchmark. The binomial attenuation identity
is generic to clipping independent Bernoulli counts; the Top-1 contribution
here is the explicit request-probability Jacobian and its pressure-quotient
curl after expert-dependent clipping.

This setting differs from [\(\phi\)-Balancing](https://proceedings.mlr.press/v306/chen26br.html),
which designs a convex population-level objective over expected routing
probabilities, and from the [mean-field congestion-game model](https://arxiv.org/abs/2604.04230),
which gives a potential for its population equilibrium. Here the object is
the expected *admitted count vector* after per-expert clipping. These
distinctions bound the claim; they do not establish novelty.

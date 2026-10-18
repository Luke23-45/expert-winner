# Capacity attenuation and curl of expected admitted Top-K feedback

**Status:** proved one-step theorem for the existing per-expert clipping model; exact numerical audit is separate. This is not a change to the canonical admission rule and is not a closed-loop performance or conference-novelty claim.

## Model

Fix a pressure vector `q`. Each of `T` tokens independently draws a continuous affinity vector `a_t` from one common law and requests the hard Top-K set under scores `a_{t,e}-gamma*q_e`. Let

\[
p_e(q)=\Pr\{e\text{ is selected for one token at pressure }q\},\qquad \sum_e p_e(q)=K.
\]

Then the per-expert request count has marginal law `R_e(q) ~ Binomial(T,p_e(q))`. Different experts' counts are dependent, but that dependence is not needed below. Per-expert admission remains the canonical rule `A_e=min(R_e,C_e)`, where `1<=C_e<=T` is an integer. Define

\[
m_e(q)=\mathbb E[A_e(q)],\quad
\alpha_e(p)=\Pr\{\operatorname{Binomial}(T-1,p)<C_e\}.
\]

Let `P_0=I-11^T/E`. The expected admitted feedback field on the routing quotient is

\[
F_A(q)=P_0\left(\frac{m(q)}{KT}-\mu\right).
\]
The corresponding expected requested field is `F_R(q)=P_0(p(q)/K-mu)`.

## Theorem: exact clipping attenuation

At every pressure where `p(q)` is differentiable,

\[
\boxed{\quad
D F_A(q)=\frac1K P_0\,\operatorname{diag}(\alpha_e(p_e(q)))\,D p(q),
\qquad
D F_R(q)=\frac1K P_0 Dp(q).
\quad}
\]

Thus each admitted coordinate's local sensitivity to changes in its own request probability is exactly multiplied by the probability that one fewer token requests it than its capacity. This is an exact finite-`T` identity, not an asymptotic approximation.

For a sequence of capacities `C_e(T)/T -> c_e` and a fixed probability `p`:

- if `p<c_e`, then `alpha_e(p)->1`;
- if `p>c_e`, then `alpha_e(p)->0` exponentially fast in `T`;
- at `p=c_e`, the limit depends on the second-order placement of `C_e(T)` and is not determined by the ratio alone.

In particular, overload does **not** make the finite-`T` law of `A_e` non-identifying: for `C_e>=1`, `Pr(A_e=0)=(1-p_e)^T`, so the marginal distribution still identifies `p_e`. The theorem establishes attenuation of the derivative of the **mean signal**, with exponentially weak sensitivity above capacity; it does not establish exact finite-sample non-identifiability.

### Proof

For `X~Binomial(T,p)`, write `X=Y+B`, where `Y~Binomial(T-1,p)`, `B~Bernoulli(p)`, independently. Differentiating the expectation of a function of independent Bernoulli variables one coordinate at a time gives

\[
\frac{d}{dp}\mathbb E[\min(X,C)]
=T\,\mathbb E[\min(Y+1,C)-\min(Y,C)]
=T\Pr(Y<C).
\]

The increment in brackets is one exactly when `Y<C`, and zero otherwise. Hence `Dm_e/Dp_e=T alpha_e(p_e)`. Each marginal `m_e` depends only on `p_e`; applying the chain rule and dividing by `KT` gives the first Jacobian. The requested formula follows directly from its definition. The asymptotic statements follow from binomial concentration on either side of the capacity fraction; strict separation `|p-c_e|>0` gives an exponential Chernoff bound. Finally, `A_e=0` iff `R_e=0` for positive capacity, proving the stated finite-`T` identification fact.

## Corollary: dimension of saturated mean-sensitivity loss

This corollary makes the clipping identity directional while retaining the
Top-K pressure geometry. Let `J(q)=Dp(q)` and assume that its restriction
from the pressure quotient `R^E/span{1}` to the probability tangent space
`1^perp` is an isomorphism. This regularity holds for iid standard-Gumbel
Top-K routing whenever `1<=K<E`: if
\[
 \Phi(s)=\mathbb E\left[\max_{|S|=K}\sum_{e\in S}(s_e+G_e)\right],
 \qquad G_e\ \text{iid standard Gumbel},
\]
then `p(s)=nabla Phi(s)`. To verify strict curvature, write
`h(x)=max_{|S|=K} x^T 1_S`, so `Phi` is the convolution of `h` with the
strictly positive smooth joint Gumbel density `f_G`. For each codimension-one
wall `F` between adjacent maximizing subsets `S,S'`, put
`d_F=1_S-1_{S'}`. The distributional Hessian of this piecewise-linear
support function, convolved with `f_G`, gives
\[
 v^T\nabla^2\Phi(s)v
 =\sum_F \frac{(d_F^T v)^2}{\|d_F\|_2}
     \int_F f_G(x-s)\,d\mathcal H^{E-1}(x).
\]
Every coefficient is positive: each wall has a relatively open portion and
the Gumbel density is positive everywhere. For every pair `i,j`, adjacent
sets differing by `1_i-1_j` exist because `1<=K<E`. Hence the sum can vanish
only if `v_i=v_j` for every pair, i.e. if `v` is a common-shift direction.
It is strictly positive on `1^perp`. With `s=-gamma*q`, `J(q)` is negative
definite and invertible on the pressure quotient.

Let `S` be any set of `m>=2` experts, and suppose
`alpha_e(p_e(q))<=a` for every `e in S`, where `0<=a<=1`. Define the
`(m-1)`-dimensional probability-transfer space
\[
 U_S=\{z\in\mathbb R^E: z_e=0\ (e\notin S),\ \mathbf1^Tz=0\}.
\]
For every `z in U_S`, regularity gives a unique pressure-quotient direction
`v` satisfying `J(q)v=z`. Then
\[
 D F_R(q)v=\frac{z}{K},\qquad
 \|D F_A(q)v\|_2
 =\frac1K\|P_0\operatorname{diag}(\alpha)z\|_2
 \le a\frac{\|z\|_2}{K}
 =a\|D F_R(q)v\|_2.
\]
Consequently, the pressure quotient contains an `(m-1)`-dimensional
subspace of local directions on which the admitted **mean-field** response
is at most an `a` fraction of the requested response, measured in the
induced request-probability displacement. For `z=e_i-e_j` with `i,j in S`,
the requested response has norm `sqrt(2)/K`, whereas the admitted response
is at most `a*sqrt(2)/K`.

If `C_e(T)/T -> c_e < p_e(q)` for every `e in S`, then each such `alpha_e`
vanishes exponentially in `T`; the relative sensitivity bound therefore
does too. The condition `m>=2` is essential to this construction: with one
saturated coordinate, no nonzero zero-sum request perturbation can be
supported only on that coordinate. This explains why a single saturated
expert does not provide a local transfer direction that is attenuated in
every participating coordinate.

The result concerns the derivative of the expected signal at a fixed
pressure. It is not a statement about exact finite-batch observation laws,
adaptive policy values, closed-loop stability, overflow improvement, or
telemetry cost. The attenuation inequality after the local invertibility
step is a generic clipped-signal chain rule; this corollary alone does not
survive the project's generic outcome-cost benchmark as a distinct value or
control theorem. The additional numerical audit is specified in
[`saturated_tangent_sensitivity_experiment_protocol_2026-10-18.md`](saturated_tangent_sensitivity_experiment_protocol_2026-10-18.md)
and reported in
[`saturated_tangent_sensitivity_experiment_results_2026-10-18.md`](saturated_tangent_sensitivity_experiment_results_2026-10-18.md).

### Corollary: exact local-rank threshold and number of lost directions

The preceding directional statement has an exact rank counterpart. Let
`Q=1^perp` be both the pressure quotient and the request-probability tangent
space, with its Euclidean norm. Assume `J=Dp(q)|_Q:Q->Q` is invertible, as it
is for iid standard-Gumbel Top-K when `1<=K<E`. Define the requested and
admitted mean-feedback Jacobians, restricted to `Q`, by

```text
B_R = (1/K) J,
B_A = (1/K) P_0 diag(alpha) J.
```

The response of admitted feedback measured in requested-response
coordinates is therefore the operator

```text
L_T = B_A B_R^(-1) = P_0 diag(alpha)|_Q.
```

For every finite `T` with `1<=C_e<=T` and `0<p_e(q)<1`, all
`alpha_e(p_e(q))>0`, and `rank(B_A)=E-1`.

Now consider a limiting attenuation vector with `alpha_e -> 0` for the
strictly saturated set `S`, `|S|=m`, and `alpha_e -> a_e>0` for every
`e` outside `S`. Then

```text
rank(L_limit) = rank(B_A,limit) = E-m       if m>=1,
rank(L_limit) = E-1                       if m=0.
```

Thus exactly `m-1` quotient directions are lost when at least one coordinate
saturates; one saturated expert causes no rank loss, while each additional
saturated expert removes one independent local response direction. In the
usual strict-capacity limit, `C_e(T)/T -> c_e` with `p_e>c_e` on `S` and
`p_e<c_e` off `S`, the `m-1` vanishing singular values of `L_T` vanish
exponentially in `T`; the other `E-m` singular values converge to positive
limits. For any finite batch, the response remains full rank, so this is
asymptotic loss of conditioning and limiting rank, not exact finite-sample
non-identifiability.

**Proof.** For finite `T`, suppose `z in Q` and `L_T z=0`. Then
`diag(alpha)z=lambda*1` for some scalar `lambda`. Since every `alpha_e>0`,
`z_e=lambda/alpha_e`; the constraint `sum_e z_e=0` gives
`lambda*sum_e 1/alpha_e=0`, hence `lambda=0` and `z=0`. This proves full
rank. In the limit, coordinates in `S` have zero attenuation and the
remaining attenuations are positive. If `m>=1`, `P_0 diag(a)z=0` implies
`diag(a)z=lambda*1`; any coordinate in `S` forces `lambda=0`. Therefore
`z_e=0` off `S`, and the kernel is exactly
`{z: supp(z) subset S, sum_e z_e=0}`, of dimension `m-1`. Rank-nullity on
the `(E-1)`-dimensional space `Q` gives `E-m`. If `m=0`, the same finite
rank argument applies with all limiting attenuations positive. The singular
value statement follows from continuity of singular values under matrix
convergence. Exponential convergence of saturated attenuations follows from
the binomial tail bound in the preceding theorem.

If `alpha_e<=a` for all `e in S`, the operator restricted to
`U_S={z in Q:supp(z) subset S}` satisfies
`||L_T z||_2<=a||z||_2`. Since `dim(U_S)=m-1`, the min-max principle gives at
least `m-1` singular values of `L_T` no larger than `a`. This finite-batch
bound identifies the disappearing subspace before taking the limit. `\square`

This is a rank statement about the local **mean** feedback channel in
requested-response coordinates. It does not imply a policy-value separation
from an arbitrary outcome-map benchmark: the full finite instance remains
representable there. A controlled exact-expectation singular-spectrum audit
is recorded in
[`saturation_rank_threshold_experiment_2026-10-18.md`](saturation_rank_threshold_experiment_2026-10-18.md).

## Top-K geometry and a nonzero quotient curl

For continuous affinities, define the expected Top-K surplus

\[
\Psi(q)=\mathbb E\left[\max_{|S|=K}\sum_{e\in S}(a_e-\gamma q_e)\right].
\]
At differentiability points, `nabla Psi(q)=-gamma*p(q)`. Since `Psi` is convex, `Dp(q)` is a symmetric negative-semidefinite Hessian up to the positive factor `gamma`. Requested feedback therefore has a symmetric Jacobian on the quotient. Admitted feedback instead left-scales this Top-K Hessian by expert-specific attenuation factors before projecting.

For any symmetric matrix `H=Dp(q)`, set `B=diag(alpha)H`. For distinct `i,j` and reference coordinate `E`, the antisymmetric part of the admitted Jacobian on quotient directions `u=e_i-e_E`, `v=e_j-e_E` is

\[
\Omega_{ij}
:=u^T DF_A(q)v-v^T DF_A(q)u
=\frac1K\left[(\alpha_i-\alpha_j)H_{ij}
-(\alpha_i-\alpha_E)H_{iE}
+(\alpha_j-\alpha_E)H_{jE}\right].
\]
A nonzero `Omega_ij` rules out a differentiable scalar potential for the projected expected admitted field in any neighborhood of that point. Unequal attenuation alone is not sufficient: the Top-K cross-derivatives and the quotient projection both matter. The displayed expression is the exact criterion to evaluate.

### Exact Top-1 witness

Take `E=3`, `K=1`, iid standard Gumbel affinities, `T=6`, and equal exact-total capacities `C_1=C_2=C_3=2`. Gumbel-max gives `p(q)=softmax(-q)`. Choose a pressure representative for

\[
p=(1/2,1/3,1/6),\quad q=(-\log(1/2),-\log(1/3),-\log(1/6))+c\one
\]
for any common shift `c`. Here

\[
(\alpha_1,\alpha_2,\alpha_3)
=\left(\frac3{16},\frac{112}{243},\frac{3125}{3888}\right),
\quad
H_{ij}=p_i p_j\ (i\ne j),
\]
so the quotient curl in directions `e_1-e_3`, `e_2-e_3` is exactly

\[
\Omega_{12}=-\frac{29}{2187}\ne0.
\]
Therefore the expected admitted feedback field is not a quotient gradient even with uniform per-expert capacities and exact total capacity. With no clipping (`C_e=T`), every `alpha_e=1` and the curl is zero. At the uniform pressure, symmetry likewise gives equal `alpha_e` and zero curl. These are falsifiable controls, not assumptions used to force the result.

### Exact genericity result for this finite Top-1 instance

The witness above extends to an exact characterization over the entire
interior of the three-expert request simplex. Fix `E=3`, `K=1`, `T=6`,
`C=(2,2,2)`, iid standard Gumbel noise, and `gamma=1`. Write
`x=p_1`, `y=p_2`, `z=p_3`, so `x+y+z=1` and `x,y,z>0`. The exact clipping
sensitivity is

```text
alpha(p) = Pr[Binomial(5,p)<2] = (1-p)^4(1+4p).
```

For the quotient directions `u=e_1-e_3` and `v=e_2-e_3`, direct
factorization gives

```text
Omega(x,y,z)
  = xy(alpha(x)-alpha(y))
    -xz(alpha(x)-alpha(z))
    +yz(alpha(y)-alpha(z))
  = (x-y)(y-z)(x-z) Q(x,y,z),
Q = 4 s_2^2 - 2 s_2 - 7 s_3 - 1,
s_2 = xy+yz+zx,  s_3 = xyz.
```

Since `0 <= s_2 <= 1/3`, convexity of `4t^2-2t-1` implies
`4s_2^2-2s_2-1 <= -1`; also `s_3>=0`. Therefore `Q<=-1<0`. It follows
that the curl vanishes exactly when at least two request probabilities are
equal, and is nonzero whenever `x,y,z` are pairwise distinct. The softmax
map from the two-dimensional pressure quotient to the simplex interior is a
diffeomorphism, so every open pressure region contains points with nonzero
curl. Thus this expected admitted field has no scalar potential on any
nonempty open region of the quotient. This is stronger than a single-point
witness, but remains a theorem for the stated `E=3,K=1,T=6,C=2` stochastic
instance; it is not a general all-`E,K,T,C` theorem or a controller-value
result.

The exact rational grid audit in
[`expected_admitted_curl_genericity_results_2026-10-17.md`](expected_admitted_curl_genericity_results_2026-10-17.md)
checks the factorization and this zero-set characterization at 37,579
interior rational points. It is a reproducible algebra audit, not evidence
that replaces the proof.

### General finite-capacity extension for three-expert Top-1

The local non-potentiality statement does not depend on the particular
`T=6,C=2` witness. Fix `E=3`, `K=1`, iid standard Gumbel affinities,
`gamma>0`, a common integer capacity `C` at all three experts, and `T>=2`.
If `1<=C<T`, the expected admitted feedback field has nonzero quotient
curl on a dense open subset of the pressure quotient. In particular, it
has no scalar potential on any nonempty open set. This includes the
exact-total-capacity sequence `T=3C`.

Write `p=(x,y,z)` for the one-token request probabilities, so
`x+y+z=1`, and set

```text
alpha(p) = Pr[Binomial(T-1,p)<C],
g(p) = p*alpha(p).
```

The softmax choice Jacobian has off-diagonal entries
`H_ij=gamma*p_i*p_j`. The antisymmetric derivative on quotient directions
`e_1-e_3` and `e_2-e_3` is therefore

```text
Omega(x,y,z)
  = gamma * [g(x)*(y-z) + g(y)*(z-x) + g(z)*(x-y)].
```

The bracket is a polynomial in `x,y` after substituting `z=1-x-y`, hence
real analytic on the simplex interior. It is not identically zero: its
continuous boundary value at `x=0`, `z=1-y`, is

```text
Omega(0,y,1-y)/gamma
  = y*(1-y) * (alpha(y)-alpha(1-y)).
```

For `1<=C<T`, the binomial-CDF derivative is

```text
alpha'(p)
  = -(T-1)*binomial(T-2,C-1)
       * p^(C-1) * (1-p)^(T-C-1) < 0,  0<p<1.
```

Thus for any `y` strictly between zero and one-half, this boundary value
is nonzero. If the analytic curl vanished on any open subset of the
simplex interior, it would vanish identically there and throughout the
connected interior, contradicting the boundary limit. Its zero set
consequently has empty interior. The softmax map is a diffeomorphism from
the pressure quotient onto the simplex interior, so the same dense-open
non-potentiality statement holds in pressure coordinates.

The endpoints are controls: for `C=T`, `alpha=1`, all three coordinates
have equal attenuation and the curl vanishes; at the symmetric request
point `p=(1/3,1/3,1/3)`, permutation symmetry also forces zero curl even
when `C<T`. This theorem is structural and stochastic: it does not imply
that the proportional controller is unstable or that admitted feedback is
always worse. The exact finite-capacity audit is recorded in
[`top1_curl_capacity_scaling_results_2026-10-17.md`](top1_curl_capacity_scaling_results_2026-10-17.md).

## Interpretation and boundary

This result joins the project's existing ingredients without changing them: Top-K requested probabilities, iid token batches, per-expert clipping, and the same gauge quotient. It gives a finite-batch analytic form for how clipping transforms the requested-feedback Jacobian and an explicit expected-field curl witness. The binomial attenuation identity itself is a generic property of clipping and is not claimed as novel in isolation; the model-specific consequence comes from its composition with the Top-K choice Jacobian and quotient geometry.

The curl is computed in Euclidean **pressure coordinates**. It does not by
itself imply that the canonical expected update lacks a potential in its
natural choice-probability geometry. In fact, for fresh iid batches the
expected update is mirror descent on a separable convex, capacity-dependent
objective over Top-K inclusion probabilities; see
[`capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md`](capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md).
Accordingly, the curl result is a coordinate-specific structural fact, not
evidence of instability or nonconvergence.

It does **not** prove that admitted feedback is always worse, that the finite-`T` admitted observation law is non-identifying, that every admitted-only controller winds up, that paying for requested counts is worthwhile, or that a production router incurs an extra collective. Those require separate claims and evidence. It also does not evade the existing fixed-instance outcome-map reduction by itself. The immediate paper-level test is whether this quotient-curl/attenuation statement yields a family-level quantitative consequence not already implied by generic clipped-gradient or censored-observation theory.


## Literature boundary checked for this result

The requested-field potential step uses the standard envelope/choice-probability relation; the Top-K maximum is the envelope over fixed-cardinality subsets. Shi, Shum, and Song study cyclic monotonicity for multinomial random-utility choice probabilities, which is the closest mathematical foundation for that uncensored geometry ([Econometrica article](https://doi.org/10.3982/ECTA14115738)). The present calculation does not claim that convex-envelope identity as new.

The closest MoE controller theory found in this targeted check casts auxiliary-loss-free balancing as a primal-dual method and proves monotonicity and approximate balancing for an uncensored assignment model ([Han and Zhong, arXiv:2512.03915](https://arxiv.org/abs/2512.03915)). METRO explicitly gathers global Top-K knowledge for a serving-time routing/placement objective ([METRO, arXiv:2512.09277](https://arxiv.org/abs/2512.09277)); this is evidence that requested-side information can be used, but not evidence for a universal extra-collective price or this admitted-feedback field. Capacity-Aware Inference instead studies deterministic per-expert ceilings and token dropping at inference ([ICLR 2026 paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/94e845868a9ace4bc239d0c529d32f4c-Abstract-Conference.html)).

Targeted online searches for the exact composition “Top-K request-choice Jacobian × binomial per-expert clipping attenuation × gauge-projected curl” did not surface a matching MoE result. This is a bounded search, not a systematic review or proof of novelty. The derivative of a clipped binomial mean is elementary and generic; a paper claim would need to show that the Top-K quotient consequence supports a nontrivial family-level control result beyond generic censored-gradient analysis and beyond the project's finite outcome-map benchmark.

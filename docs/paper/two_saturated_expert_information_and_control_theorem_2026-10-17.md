# Two saturated experts: admitted-count indistinguishability and a two-batch control gap

**Status:** exact theorem for a parameterized batch-size sequence in the
canonical Top-1, per-expert clipping model; paired synthetic audit completed.
This replaces a false claim of exact finite-sample non-identifiability with a
quantitative statement about asymptotic indistinguishability. It is not a
universal controller theorem or a novelty clearance.

## Model

There are three experts, `K=1`, and `T` iid tokens, with `T` a positive
multiple of 20. Under latent world `h in {0,1}`, token requests are iid
categorical with

```text
p^0 = (2/5, 2/5, 1/5),
p^1 = (1/2, 3/10, 1/5).
```

Equivalently, route by Top-1 over `log(p^h_e) + G_{t,e} - q_e`, with
independent standard Gumbel noise. Thus `R ~ Multinomial(T,p^h)` at pressure
`q=0`. Set exact-total capacities

```text
C = (T/4, T/4, T/2),       sum_e C_e = T,
A_e = min(R_e,C_e).
```

Both worlds overload experts 1 and 2 and leave expert 3 below capacity. They
have the same total request probability on the saturated pair, `p_1+p_2=4/5`,
but a different split. This is the first dimension of ambiguity left after
mass conservation: a single saturated coordinate could be recovered from
the other two counts, while two saturated coordinates can trade requests.

## Theorem 1: the full admitted vector becomes asymptotically uninformative

Let `P_h^R` and `P_h^A` be the one-batch laws of `R` and `A` in world `h`.
Define a reference law `Q_T` by

```text
Y = (T/4, T/4, Z),       Z ~ Binomial(T,1/5).
```

Then

```text
TV(P_0^A, Q_T) <= eps_0(T)
TV(P_1^A, Q_T) <= eps_1(T),
```

where

```text
eps_0(T) = 2 exp(-9T/200) + exp(-9T/50),
eps_1(T) =   exp(-T/8) + exp(-T/200) + exp(-9T/50).
```

Consequently,

```text
TV(P_0^A,P_1^A) <= eps_0(T)+eps_1(T) -> 0.
```

For equal prior probability on the two worlds, every classifier based on the
entire admitted vector has Bayes error at least
`(1-eps_0(T)-eps_1(T))/2`, which tends to `1/2`.

By contrast, classifying world 1 when `R_1/T >= 0.45` has error at most
`exp(-T/200)` in each world by Hoeffding's inequality. Hence

```text
TV(P_0^R,P_1^R) >= 1 - 2 exp(-T/200) -> 1,
```

and the equal-prior Bayes error from requested counts tends to zero.

### Proof

Couple `A` and `Y` using the same request vector in each world. They are
identical on

```text
G = {R_1 >= T/4, R_2 >= T/4, R_3 < T/2}.
```

On `G`, both overloaded experts report their caps and expert 3 reports its
exact count. Its marginal law is `Binomial(T,1/5)` in both worlds, so the
reference law `Q_T` is common. The coupling inequality gives
`TV(P_h^A,Q_T) <= P_h(G^c)`. Applying Hoeffding separately to the three
threshold failures yields the displayed `eps_h` bounds. The triangle
inequality proves the admitted-vector bound.

For requested counts, the first marginal is binomial with parameter `2/5`
under `h=0` and `1/2` under `h=1`. The threshold `0.45` is exactly 0.05 from
both means, so each classification error is at most
`exp(-2T(0.05)^2)=exp(-T/200)`. The total-variation and Bayes-error bounds
follow.

This is **not** exact finite-`T` non-identifiability. It proves that the two
full admitted-vector laws approach each other exponentially under the stated
capacity margins, despite the finite laws remaining distinguishable.

### Consequence for one pressure update

Use the formal proportional update with `q_0=0`, `delta=0`, `gamma=1`,
uniform target `mu=(1/3,1/3,1/3)`, and any `eta>0`:

```text
q_1 = Pi_g(eta * (signal/T - mu)),       signal in {R,A}.
```

The requested update is injective on the request-count simplex: if two
updates coincide, the pre-projection vectors differ by a common-mode vector;
their difference has zero sum because both request vectors sum to `T`, so
that common mode is zero and the two request vectors are equal. Therefore
`TV(law(q_1^R|h=0),law(q_1^R|h=1)) = TV(P_0^R,P_1^R)`. The admitted update is a
deterministic function of `A`, so data processing gives
`TV(law(q_1^A|h=0),law(q_1^A|h=1)) <= TV(P_0^A,P_1^A)`. The pressure-state
separation therefore tends to one for requested feedback and zero for
admitted feedback in this one-step experiment.

## Theorem 2: exact population two-batch overflow comparison

Keep the same two worlds and capacities, and set

```text
eta = 15 log(2).
```

After the first batch, update once from requested counts, admitted counts, or
no feedback, then route a fresh iid batch in the same world. Let the primary
cost be normalized second-batch overflow

```text
O(p,C/T) = sum_e max(p_e - C_e/T, 0).
```

As `T -> infinity` through multiples of 20, the expected second-batch costs
converge to:

| World | Requested feedback | Admitted feedback | No update |
|---|---:|---:|---:|
| `h=0` | `1/6` | `(2^(5/4)-1)/(2(1+2^(5/4)))` | `3/10` |
| `h=1` | `(32 sqrt(2)+9)/(4(32 sqrt(2)+29))` | `(2^(5/4)-1)/(2(1+2^(5/4)))` | `3/10` |

The admitted value is about `0.20400314`; requested values are about
`0.16666667` and `0.18266432`. Both requested values are strictly lower than admitted and no
update. Thus requested feedback has strictly lower two-batch cumulative
overflow than both admitted feedback and no update in both worlds in this
specified family. The first-batch cost is the same across the three arms and
worlds (`3/10`), so adding it preserves the ordering.

### Proof

The law of large numbers gives `R/T -> p^h` and
`A/T -> min(p^h,C/T)=(1/4,1/4,1/5)` in both worlds. The pressure update and
softmax choice probabilities are continuous, so the second-batch population
loads converge to those generated by the limiting pressure.

For requested feedback, the common target cancels from softmax ratios, giving
`p'_e proportional to p^h_e 2^{-15p^h_e}`. Direct substitution yields

```text
h=0: p' = (1/6, 1/6, 2/3),
h=1: p' = (r_1/Z, r_2/Z, 1/Z),
     r_1 = 5/(32 sqrt(2)), r_2 = 3/(4 sqrt(2)), Z = 1+r_1+r_2.
```

Their overflow costs are `1/6` and
`(32 sqrt(2)+9)/(4(32 sqrt(2)+29))`. For admitted feedback,
the two worlds have the same limiting observed vector, hence the same
pressure update. Relative to expert 3, the updated weights of experts 1 and
2 are each multiplied by \(d=2^{-3/4}\), because
\(\eta(1/4-1/5)=(3/4)\log 2\). Their combined post-update probability is
\(4d/(1+4d)=2^{5/4}/(1+2^{5/4})\). Since \(d>1/2\), each of the first two
expert probabilities exceeds `1/4`, while expert 3 remains below `1/2`.
Subtracting the two active capacities gives the displayed admitted cost. No update leaves
the original overload `(.4-.25)+(.4-.25)=.3` in `h=0` and
`(.5-.25)+(.3-.25)=.3` in `h=1`. For `h=0`, the requested cost `1/6` is
below the admitted cost because \(2^{5/4}>2\), and
\((x-1)/(2(1+x))\) is increasing for \(x>0\). For `h=1`, let
\(r=2^{1/4}\). Common-denominator algebra gives
\[
O_A-O_R^{h=1}=
\frac{64r^3+98r-96r^2-67}
{4(29+32r^2+58r+64r^3)}>0.
\]
For a rational positivity certificate, \(1.1892<r<1.1893\), since the
fourth powers of these rational endpoints bracket 2. The numerator is
increasing for \(r>1\), as its derivative is \(192r(r-1)+98>0\), and at
`r=1.1892` it equals `10454849509/488281250 > 0`. Both requested costs are
also below `3/10`.

## Theorem 3: optimal one-step value of the observation channel

The previous theorem compares the three specified proportional-update rules.
We can also compare the **best** post-observation pressure policy under each
signal, in a one-step decision problem with no movement constraint. This is a
different controller class and is stated separately.

Let \(\mathcal Q=\{q\in\mathbb R_+^3:\min_e q_e=0\}\). After observing
either the full request vector \(R\) or the admitted vector \(A\) from the
first batch, a policy chooses any \(q\in\mathcal Q\). In world \(h\), the
next-batch route probabilities and cost are
\[
\rho^h(q)=\operatorname{softmax}(\log p^h-q),\qquad
L_h(q)=\sum_{e=1}^3[\rho^h_e(q)-c_e]_+,
\quad c=(1/4,1/4,1/2).
\]
For \(S\in\{R,A\}\), define the equal-prior optimal expected overflow
\[
V_S(T)=\inf_{\pi_S}\frac12\sum_{h=0}^1
\mathbb E_{Y\sim P^S_{h,T}}[L_h(\pi_S(Y))],
\]
where \(\pi_S\) ranges over all deterministic or randomized maps from the
observed signal to \(\mathcal Q\). Then
\[
\lim_{T\to\infty}V_A(T)=\frac1{32},\qquad
\lim_{T\to\infty}V_R(T)=0,
\qquad
\lim_{T\to\infty}(V_A(T)-V_R(T))=\frac1{32}.
\]

More explicitly, with \(\epsilon_A(T)=\epsilon_0(T)+\epsilon_1(T)\) from
Theorem 1 and \(\epsilon_R(T)=e^{-T/200}\),
\[
\frac1{32}-\frac{\epsilon_A(T)}2-\epsilon_R(T)
\le V_A(T)-V_R(T)\le\frac1{32}.
\]

### Proof

For any common pressure \(q\), put \(w=\rho^0(q)\) and \(u=\rho^1(q)\).
Since \(p^1/p^0=(5/4,3/4,1)\) coordinatewise,
\[
\frac{u_1}{u_2}=\frac53\frac{w_1}{w_2}.
\]
Write \(a=\operatorname{TV}(w,c)\) and
\(b=\operatorname{TV}(u,c)\). Overflow equals total variation from \(c\),
because both vectors have unit mass. If \(a\ge1/4\) or \(b\ge1/4\),
then \(a+b\ge1/16\). Otherwise, coordinatewise deviation is bounded by
total variation, so
\[
\frac53\frac{1/4-a}{1/4+a}
\le \frac{u_1}{u_2}
=\frac53\frac{w_1}{w_2}
\le \frac{1/4+b}{1/4-b}.
\]
Cross-multiplication gives \(a+b-ab\ge1/16\), hence
\(a+b\ge1/16\). Thus every common action has equal-prior cost at least
\(1/32\). Equality is attained by \(q^*=(\log4,\log4,0)\): it gives
\(\rho^0(q^*)=c\) and
\(\rho^1(q^*)=(5/16,3/16,1/2)\), whose overflow is \(1/16\).

For a policy using \(A\), let
\(\bar P_T=(P^A_{0,T}+P^A_{1,T})/2\). Replacing each world-specific
observation law by \(\bar P_T\) changes its equal-prior risk by at most
\(\operatorname{TV}(P^A_{0,T},P^A_{1,T})/2\), since \(0\le L_h\le1\).
Under the common law, the policy only randomizes over common actions, each
with risk at least \(1/32\). Theorem 1 therefore gives
\[
1/32-\epsilon_A(T)/2\le V_A(T)\le1/32,
\]
where the upper bound uses the constant action \(q^*\).

For requested feedback, classify \(h=1\) iff \(R_1/T\ge0.45\), then
choose \(q^1=(\log5,\log3,0)\) if classified as world 1 and \(q^0=q^*\)
otherwise. Each action routes exactly at \(c\) in its matching world, and
the classifier error is at most \(e^{-T/200}\) in either world. Since
\(L_h(q)\le1\), this gives \(0\le V_R(T)\le e^{-T/200}\). Combining the
bounds proves the claim. \(\square\)

### Finite-batch optimal-value certificate

The proof yields the sharper computable bound
\[
V_A(T)-V_R(T)\ge
\frac1{32}-\frac12\operatorname{TV}(P^A_{0,T},P^A_{1,T})-r_T,
\]
where the exact risk of the requested threshold-and-balance policy is
\[
r_T=\frac12\left[
\frac9{124}\Pr_{0}\{R_1\ge .45T\}
+\frac1{16}\Pr_{1}\{R_1<.45T\}
\right].
\]
Both terms are evaluated by the full integer-weight count-law enumeration.
This lower bound is positive at `T=320` and `T=640`, respectively
`0.018498060` and `0.029782371`. Thus, at those two batch sizes, the
requested observation has a proved strictly positive advantage even after
comparing an explicit request-informed policy against **every** admitted-
observation policy in the unrestricted one-step pressure class. The
finite-size certificate does not assert that advantage at smaller `T`.

If requested observation is assigned a surcharge \(\kappa\) in the same
normalized overflow units while admitted observation is free, this model's
asymptotic break-even is exactly \(\kappa^*=1/32\). This is a decision-value
benchmark, **not** a measured communication or latency cost. The action
class here is all gauge-fixed pressures, not the single proportional update
used in Theorem 2.

## Exact finite experiment

[`../../scripts/run_two_saturated_expert_indistinguishability.py`](../../scripts/run_two_saturated_expert_indistinguishability.py)
enumerates the complete request and admitted multinomial laws with integer
weights, so the reported total-variation distances and Bayes errors are
exact. For each finite `T` and world it also enumerates every first-batch
multinomial count vector to compute the finite-`T` expected second-batch
population overflow without Monte Carlo sampling error (float64 log weights
and population costs). Separately, it runs 20,000 paired multinomial plants
per world and batch size as a sampling check. The first-batch count vector is
shared across requested/admitted/no-update arms; the reported second-batch
overflow is evaluated from the exact Gumbel-Max population probabilities
under the resulting pressure. This isolates controller feedback from
second-batch sampling noise.

Results are in
[`two_saturated_expert_indistinguishability_results_2026-10-17.md`](two_saturated_expert_indistinguishability_results_2026-10-17.md)
and the machine-readable file
[`../../results/two_saturated_expert_indistinguishability/results.json`](../../results/two_saturated_expert_indistinguishability/results.json).

## Relation to the professor report and prior work

This supplies the report's saturation/identifiability mechanism in a form
compatible with the existing formal definition. It uses **two** saturated
experts so that Top-1 mass conservation does not recover the hidden split.
It does not change per-expert admission, invoke score-ranked dropping, or
claim finite-sample equality of observation laws. The two-batch theorem is
for the existing proportional-pressure law, not every integral/sign
controller, and does not assign a system measurement cost.

Gumbel-Max/Top-k is an established routing construction; censored-feedback
learning and censored multinomial response models are also established
areas. The current theorem must therefore be treated as an exact MoE
realization and candidate mechanism result, not as novelty clearance. A
top-conference claim still needs a reduction audit against censored
multinomial/active-testing results and a family-level consequence beyond
finite outcome-map copying. Relevant primary sources include [Kool et al.,
Gumbel-Top-k](https://proceedings.mlr.press/v97/kool19a.html) and the 2026
[IJCAI work on censored-feedback structural learning](https://www.ijcai.org/proceedings/2026/495).

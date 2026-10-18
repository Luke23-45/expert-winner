# Capacity-clipped Top-K fields: planted mismatch law and unconditioned non-potentiality

**Evidence class:** finite exact probability theorem plus a multivariate-CLT
limit; checked by an exact-sum/Monte-Carlo controlled synthetic experiment.  
**Scope:** a planted regular local facet, not a uniformly sampled facet from a
whole router arrangement.

## Construction

Fix $E\ge3$, $1\le K<E$, and $T$ such that
$C=KT/E$ is an integer. Use uniform per-expert capacity $C$, so the total
capacity equals the number $KT$ of requested slots.

At $q=0$, plant one distinguished token with exactly $K-1$ experts strictly
above a tie between experts $i$ and $j$, and all remaining experts strictly
below that tie. Thus the token changes its Top-$K$ set by the single exchange
$i\to j$ across a regular codimension-one facet. Give each of the other
$T-1$ tokens independent, identically distributed continuous scores across
experts, independent across tokens. Exchangeability and absence of ties imply
that every other token's selected $K$-subset is uniform over the
$\binom EK$ possibilities. Their joint distribution is independent of the
planted token and its facet.

Let $X_i,X_j$ be the numbers of the other $T-1$ tokens selecting $i,j$,
respectively. Just before the planted exchange,
$R_i^-=X_i+1$ and $R_j^-=X_j$. For $A_e=\min(R_e,C)$, the source admitted
decrease and destination admitted increase are
\[
d_i=\mathbf1\{X_i<C\},\qquad d_j=\mathbf1\{X_j<C\}.
\]
For $E\ge3$, the facet theorem says this local field jump is compatible with
a convex potential exactly when $d_i=d_j$. Therefore the probability that
this planted facet is non-potential is
\[
p_{E,K,T}=\Pr\!\left[\mathbf1\{X_i<C\}\ne\mathbf1\{X_j<C\}\right].
\]

## Exact finite-$T$ formula

For one other token, the number of $K$-subsets containing both fixed experts,
exactly one specified expert, or neither is respectively
\[
m_{11}=\binom{E-2}{K-2},\qquad
m_{10}=\binom{E-2}{K-1},\qquad
m_{00}=\binom{E-2}{K},
\]
with out-of-range binomial coefficients equal to zero. Write
$n=T-1$ and $M=\binom EK$. For nonnegative integers
$a+b+c+d=n$, represent counts of other-token outcomes that select only $i$,
only $j$, both, or neither. Then
\[
\boxed{
p_{E,K,T}=
\frac1{M^n}
\sum_{a+b+c+d=n}
\frac{n!}{a!b!c!d!}
m_{10}^{a+b}m_{11}^{c}m_{00}^{d}
\mathbf1\!\left\{(a+c<C)\mathbin{\mathrm{xor}}(b+c<C)\right\}.
}
\]
This is an exact rational number. It is a conditional planted-facet
probability: it does not claim that all facets in a random full arrangement
have this sampling distribution.

## Large-batch limit

For each other token, the indicators of selecting $i$ and $j$ have mean
$K/E$, variance $K(E-K)/E^2$, and correlation $-1/(E-1)$. Thus the bivariate
central limit theorem gives a centered normal limit with that correlation.
The threshold $C-1$ differs from the mean $(T-1)K/E$ by the bounded constant
$K/E-1$. After standardization, this offset tends to zero. For a centered
bivariate normal pair with correlation $\rho$, the probability of opposite
signs is $\arccos(\rho)/\pi$. Hence, along integer-feasible $T\to\infty$,
\[
\boxed{
\lim_{T\to\infty}p_{E,K,T}
=\frac1\pi\arccos\!\left(-\frac1{E-1}\right).
}
\]
For fixed $E$, this limit is independent of $K$. At $E=4$ it is approximately
$0.60817$. It lies strictly between $1/2$ and $1$ for each $E\ge3$ and tends
to $1/2$ as $E\to\infty$.

For a single exchange, a mismatch means $(d_i,d_j)=(1,0)$ or $(0,1)$.
Projecting the field jump onto the tangent space of the facet gives the exact
size
\[
\left\|\operatorname{Proj}_{n^\perp}\Delta g_A\right\|^2
=\frac{E-2}{2E},\qquad n=P_0(e_i-e_j).
\]
Consequently the expected squared tangential jump under the planted-facet
law is exactly $p_{E,K,T}(E-2)/(2E)$, converging to
\[
\frac{E-2}{2E\pi}\arccos\!\left(-\frac1{E-1}\right).
\]

## Heterogeneous-capacity slack limit

The same planted-facet law admits a two-threshold extension. Keep the score
sampling model above, but allow capacities $C_i(n),C_j(n)$ for the exchanged
experts to differ. Let $p=K/E$, $\sigma^2=p(1-p)$, and suppose, as
$n=T-1\to\infty$,
\[
C_i(n)=np+z_i\sigma\sqrt n+O(1),\qquad
C_j(n)=np+z_j\sigma\sqrt n+O(1),
\]
for fixed real $z_i,z_j$. The planted exchange gives
$d_i=\mathbf1\{X_i<C_i(n)\}$ and
$d_j=\mathbf1\{X_j<C_j(n)\}$. Since the standardized pair
$(X_i,X_j)$ converges to a unit-variance bivariate normal with correlation
$\rho=-1/(E-1)$, the mismatch probability converges to
\[
\boxed{p_E(z_i,z_j)=\Phi(z_i)+\Phi(z_j)
-2\Phi_2(z_i,z_j; -1/(E-1)).}
\]
Here $\Phi_2(x,y;\rho)=\Pr(Z_i\le x,Z_j\le y)$ for a standard bivariate
normal pair of correlation $\rho$. Capacity rounding and the strict integer
inequalities shift the standardized thresholds by only $O(n^{-1/2})$. The
expected squared tangential field jump therefore converges to
\[
p_E(z_i,z_j)\frac{E-2}{2E}.
\]
Setting $z_i=z_j=0$ recovers the equal-capacity limit above. Unequal slacks
change the probability quantitatively; the expression is a bivariate-normal
threshold probability, so the CLT and that probability identity are standard
ingredients, not a novelty claim by themselves.

There is also a simpler linear-slack corollary. Suppose
$C_i(n)/n\to c_i$ and $C_j(n)/n\to c_j$, with neither limit equal to
$p=K/E$. By the law of large numbers, $X_i/n,X_j/n\to p$ in probability.
Thus
\[
\Pr(d_i\ne d_j)\longrightarrow
\begin{cases}
1,&(c_i-p)(c_j-p)<0,\\
0,&(c_i-p)(c_j-p)>0.
\end{cases}
\]
When the pair's limiting capacities straddle the mean requested load, the
planted facet is therefore non-potential with probability tending to one.
If the full capacity profile also satisfies $\sum_e C_e(n)=KT$ and has a
nonuniform limiting profile, at least one expert lies below and one above
$p$; choosing that cross-profile pair gives this high-probability local
obstruction under the planted-facet law. This is a local geometry statement,
not a claim about the fraction of all arrangement facets or closed-loop
performance.

### Global non-potentiality under macroscopic capacity heterogeneity

The local statement gives a global obstruction for the entire pressure field.
Fix $E\ge3$ and $1\le K<E$. For each feasible $T$, take capacities
$C(T)\in\mathbb N_0^E$ with exact total capacity
\[
\sum_{e=1}^E C_e(T)=KT,
\]
and assume the normalized capacities converge, $C_e(T)/T\to c_e$. Suppose
the limiting profile is nonuniform. Since $\sum_e c_e=K$, there are experts
$i,j$ with
\[
c_i<K/E<c_j.
\]
Construct one distinguished token whose score vector at $q=0$ has exactly
$K-1$ experts strictly above a tie between $i$ and $j$, with all other
experts strictly below. Let the remaining $T-1$ score rows be independent,
exchangeable, continuous across experts and independent across tokens.

**Theorem.** Under this construction, with probability tending to one as
$T\to\infty$, the full admitted field
$g_A(q)=P_0(KT\mu-A(q))$, with $A_e(q)=\min(R_e(q),C_e(T))$, has no continuous
cellwise-affine potential on the pressure quotient. In particular, it is
not a convex subgradient field on the full quotient.

**Proof.** The distinguished tie is a regular routing facet almost surely:
all other score differences at $q=0$ are nonzero with probability one, and
there are finitely many tokens, so a sufficiently small neighborhood avoids
their tie hyperplanes. Let $X_e$ count selections of expert $e$ by the other
$T-1$ tokens. Each marginal count is a sum of iid Bernoulli variables with
mean $(T-1)K/E$, hence $X_e/T\to K/E$ in probability. On the minus side of
the facet the distinguished token selects $i$; on the plus side it selects
$j$. Therefore the source and destination admitted-count changes are
\[
d_i=\mathbf1\{X_i<C_i(T)\},\qquad
d_j=\mathbf1\{X_j<C_j(T)\}.
\]
Because $c_i<K/E<c_j$, the law of large numbers gives
$\Pr(d_i=0)\to1$ and $\Pr(d_j=1)\to1$; thus
$\Pr(d_i\ne d_j)\to1$. The facet criterion then says that this regular
facet's admitted-field jump has a nonzero tangential component and rules out
a continuous cellwise-affine potential. Since this one facet belongs to the
full arrangement, the same event rules out a convex subgradient field for
the full pressure quotient. $\square$

On the mismatched event above, $(d_i,d_j)=(0,1)$, and the squared norm of
the jump projected tangent to the facet is $(E-2)/(2E)$. Thus the expected
squared tangential jump at this planted facet converges to that positive
constant. This probability statement is over the random filler-token scores;
the distinguished token is deliberately constructed to expose a regular
facet. The following result removes that planted-token assumption for an iid
Uniform affinity model.

The controlled `cross_mean_exact_total` audit uses exact-total capacities
with exchanged experts at one half and three halves of the mean requested
load. Its nine exact finite-probability cells for `E=4`, `K in {1,2,3}`, and
`T in {32,64,128}` approach one as predicted; the paired 5,000-replicate
estimates all fall within five binomial standard errors of their exact
values. Separately, the full-arrangement audit enumerates all 108 regular
facets in each of 40 `E=3,K=1,T=6` iid rational plants and finds at least one
mismatch in every clipped plant. These validate different scopes: the first
checks the planted-facet probability law; the second samples complete finite
arrangements. See
[`heterogeneous_facet_slack_results_2026-10-17.md`](heterogeneous_facet_slack_results_2026-10-17.md)
and [`full_arrangement_facet_audit_results_2026-10-17.md`](full_arrangement_facet_audit_results_2026-10-17.md).

### Unconditioned random-affinity theorem

Fix (E\ge3), (1\le K<E), and let all entries of the (T\times E)
affinity matrix be iid (operatorname{Unif}[0,1]). For each (T), let
integer capacities satisfy
\[
\sum_e C_e(T)=KT,\qquad C_e(T)/T\longrightarrow c_e,
\]
where the limit is nonuniform. Define (p=K/E). Then at least one pair
(i,j) satisfies (c_i<p<c_j).

**Theorem.** Under the iid affinity model, the probability that the full
admitted field has at least one regular facet with unequal source and
destination admitted-count changes tends to one as (T\to\infty). Thus the
field is non-potential with probability tending to one.

**Proof.** Fix a cross-mean pair (i,j) with (c_i<p<c_j), and let
\(\epsilon_T=T^{-1/2}\). For token (t), write
\(D_t=a_{t,i}-a_{t,j}\) and
\(M_t=(a_{t,i}+a_{t,j})/2\). Consider the event that

1. (M_t\in[5/12,7/12]) and (|D_t|\le\epsilon_T); and
2. exactly (K-1) of the other (E-2) affinities in row (t) exceed (M_t).

For all sufficiently large (T), the first event has probability
\(\epsilon_T/3\). Conditional on (M_t\in[5/12,7/12]), the second has
probability
\[
\binom{E-2}{K-1}(1-M_t)^{K-1}M_t^{E-K-1},
\]
which is bounded below by a positive constant depending only on (E,K).
Thus each row satisfies both conditions with probability at least
\(b_{E,K}\epsilon_T\) for some (b_{E,K}>0). The rows are independent and
\(T\epsilon_T=\sqrt T\to\infty\), so with probability tending to one at
least one such token exists. Choose the lowest-index one.

For the code convention (score `a_{t,e}-\gamma q_e`), choose the
representative
\[
q_i=D_t/(2\gamma),\qquad q_j=-D_t/(2\gamma),\qquad
q_k=0\quad(k\notin\{i,j\}),
\]
then add a common constant if needed to use the nonnegative gauge
representative. The common shift changes no routing decision. The selected
token's two scores are both exactly `M_t`, while every other expert's score
is its raw affinity; condition 2 therefore places the tie exactly at ranks
`K,K+1`. Conditional on the selected row and selected index, each other row
has an absolutely continuous conditional law (the rows before it are
conditioned on `B_t^c`). Thus with probability one no other token has any
score tie at this pressure. This is a regular facet of the complete routing
arrangement. The factor `1/gamma` is essential unless `gamma=1`.

The selected row is the first row satisfying the rare event, so the other
rows are not all unconditionally iid after conditioning on its index. The
following bound handles that selection. Let `B_t` be the candidate event
and `r_T=Pr(B_t)=Theta(epsilon_T)`. Conditional on the selected index
`tau=m`, rows before `m` are independent with law conditioned on `B_t^c`,
row `m` has law conditioned on `B_m`, and rows after `m` retain their
original law. For each expert `e`, its zero-pressure request indicator
`Y_{t,e}` has unconditional mean `p=K/E` by exchangeability, and
\[
\left|\mathbb E[Y_{t,e}\mid B_t^c]-p\right|
\le \frac{r_T}{1-r_T}=O(\epsilon_T).
\]
Thus, uniformly in `m`, the conditional mean of the total zero-pressure
request count differs from `Tp` by only `O(T epsilon_T)+O(1)=o(T)`, and
its conditional variance is at most `T/4`. Chebyshev's inequality gives
`X_e(0)/T -> p` in probability, uniformly over the selected index.

At the constructed pressure, each score changes from its zero-pressure
value by at most `epsilon_T/2` (up to a common shift). Hence a filler row's
Top-K set can change only if some pair of its raw scores differs by at most
`epsilon_T`. For a fixed pair of iid uniforms this event has probability at
most `2 epsilon_T`; a union bound over the fixed `binom(E,2)` pairs gives
probability `O(epsilon_T)` per row. The same bound holds for rows
conditioned on `B_t^c`, up to the factor `1/(1-r_T)`. Conditional on
`tau=m`, the expected number of changed filler rows is therefore
`O(T epsilon_T)=o(T)`, uniformly in `m`. Markov's inequality shows that
their fraction is `o_p(1)`. Consequently the filler counts `X_e` at the
selected facet also satisfy `X_e/T -> p` in probability.
Across the facet, the distinguished token moves (i\to j), so
\[
d_i=\mathbf1\{X_i<C_i(T)\},\qquad
d_j=\mathbf1\{X_j<C_j(T)\}.
\]
The strict capacity limits imply (d_i\to0) and (d_j\to1) in
probability. Hence this regular facet is mismatched with probability tending
to one. By the local facet criterion, it rules out a potential for the full
field on that event. \(\square\)

### Quantitative tail bound

The same proof gives an explicit asymptotic tail rate. Let
\[
\Delta:=\min\{p-c_i,\ c_j-p\}>0,
\qquad
b_{E,K}:=\frac{1}{3}\binom{E-2}{K-1}\left(\frac{5}{12}\right)^{E-2}.
\]
For all sufficiently large (T), depending on (E,K,Delta) and the capacity
convergence sequence,
\[
\Pr\{\text{no regular mismatched facet exists}\}
\le \exp(-b_{E,K}\sqrt T)
   +5\exp\left(-\frac{\Delta^2 T}{32}\right).
\]

Indeed, the candidate probability (r_T) obeys
(r_T\ge b_{E,K}/\sqrt T) and (r_T\le 1/(3\sqrt T)); hence the probability
of no candidate is at most the first term. Conditional on the selected
index (tau=m), the zero-pressure request indicator for any fixed expert is
a sum of independent Bernoulli variables. Its mean differs from (Tp) by at
most (T r_T/(1-r_T)+1), and its variance is at most (T/4). For sufficiently
large (T), this mean shift is at most (T Delta/8). Hoeffding's inequality
and a union bound for the two exchanged experts then bound failure of the
zero-pressure count concentration event by
(4\exp(-Delta^2 T/32)).

For any filler row, a route can change under the constructed pressure only
if some raw affinity pair differs by at most (epsilon_T). Conditional on
(tau=m), the probability of this event for each filler row is at most
(2\binom E2 epsilon_T/(1-r_T)). For sufficiently large (T), this is at
most (Delta/8). Hoeffding's inequality bounds the probability that more
than (Delta T/4) filler rows are near a tie by
(\exp(-Delta^2 T/32)). On the complementary event, the two exchanged
experts' request fractions at the facet lie within (Delta/2) of (p).
Because (C_i(T)/T\to c_i<p-Delta/2) and
(C_j(T)/T\to c_j>p+Delta/2), their admitted changes are exactly (0,1)
for sufficiently large (T). The regularity failure probability is zero
under the continuous affinity law. Summing the three failure bounds gives
the display.

This theorem uses an **unconditioned iid affinity matrix** and one
data-selected regular facet; it does not claim that a uniformly selected
facet mismatches, nor does it quantify the fraction of mismatched facets.
The result is structural. It still does not imply a closed-loop cost gap,
training-quality effect, or separation from a benchmark that reproduces the
same finite outcome map.

### Many-facet strengthening

The same construction yields more than existence of one obstructing facet.
Fix the same cross-mean pair $(i,j)$ and let $B_t$ be the candidate event in
the preceding proof with $\epsilon_T=T^{-1/2}$. Define
\[
N_T=\sum_{t=1}^T\mathbf1\{B_t\}.
\]
The candidate rows are independent. For all sufficiently large $T$,
\[
b_{E,K}T^{-1/2}\le \Pr(B_t)\le (3\sqrt T)^{-1},
\]
so $\mathbb E[N_T]\ge b_{E,K}\sqrt T$ and a Chernoff bound gives
\[
\Pr\{N_T< b_{E,K}\sqrt T/2\}
\le \exp(-b_{E,K}\sqrt T/8).
\]

For each candidate row $t$, construct its pressure $q^{(t)}$ as above.
Conditional on that row, the other $T-1$ rows remain iid. Every score
coordinate changes from its zero-pressure value by at most $\epsilon_T/2$.
A filler row's Top-$K$ set can therefore change only if two of its raw
affinities differ by at most $\epsilon_T$. Under iid $\operatorname{Unif}[0,1]$
affinities, a union bound over expert pairs gives probability at most
$2\binom E2\epsilon_T$. Thus each filler expert-inclusion probability
differs from $p=K/E$ by at most this amount. For sufficiently large $T$, the
mean count of either exchanged expert among the fillers is within
$\Delta T/4$ of $pT$, where
\[
\Delta=\min\{p-c_i,c_j-p\}>0.
\]
Hoeffding's inequality then bounds the conditional probability that either
count leaves the $\Delta T/2$ neighborhood of $pT$ by
$4\exp(-\Delta^2T/8)$. On the complementary event, the lower-capacity
source is saturated and the higher-capacity destination is unsaturated,
so this candidate facet has the mismatched admission indicators $(0,1)$.

The event that a specified candidate row is bad depends on that row and the
independent filler rows; a union bound over candidate rows, using
$\Pr(B_t)\le1/(3\sqrt T)$, gives
\[
\Pr\{\text{some candidate facet is not mismatched}\}
\le \frac43\sqrt T\exp(-\Delta^2T/8).
\]
Under continuous affinities, all candidate facets are regular and pairwise
distinct almost surely: conditional on a candidate row, any other row has
zero probability of a score tie at its constructed pressure, and two
independent candidate rows have equal $a_{t,i}-a_{t,j}$ with probability
zero. Therefore, with probability at least
\[
1-\exp(-b_{E,K}\sqrt T/8)
 -\frac43\sqrt T\exp(-\Delta^2T/8),
\]
the full arrangement contains at least $b_{E,K}\sqrt T/2$ distinct regular
facets whose admitted-field jumps have nonzero tangential components. Each
such jump has squared tangent norm $(E-2)/(2E)$.

This strengthening follows from the same explicit candidate construction;
it does not assert a positive fraction of all facets. The controlled audit
in [`many_facet_random_affinity_protocol_2026-10-17.md`](many_facet_random_affinity_protocol_2026-10-17.md)
counts all candidate facets and checks the $\sqrt T$ lower-growth
prediction. Its finite rational grid is evidence for the construction, not
a replacement for this probability proof.

For finite $n$, let $a,b,c,d$ count the other tokens selecting only $i$,
only $j$, both, and neither, respectively. The exact probability is
\[
\frac{1}{\binom EK^n}
\sum_{a+b+c+d=n}\frac{n!}{a!b!c!d!}
\binom{E-2}{K-1}^{a+b}
\binom{E-2}{K-2}^{c}
\binom{E-2}{K}^{d}
\mathbf1\{(a+c<C_i)\mathbin{\mathrm{xor}}(b+c<C_j)\},
\]
with out-of-range binomial coefficients set to zero. This follows from the
same four-category multinomial count as the equal-capacity formula.

The exact finite sum and route-level Monte Carlo for unequal capacity slacks
are recorded in
[`heterogeneous_facet_slack_results_2026-10-17.md`](heterogeneous_facet_slack_results_2026-10-17.md).
This gives a scale-aware local measure of non-integrability in the
count-valued field. The pressure-update signal normalized by $KT$ has this
quantity divided by $(KT)^2$.

### Proof details

The exact sum follows by grouping the $n$ independent uniform $K$-subsets
into the four categories above; each category has the displayed number of
underlying subsets. The mismatch indicator is precisely the exclusive-or
condition in the sum.

For the limit, the covariance between the two inclusion indicators is
\[
\frac{K(K-1)}{E(E-1)}-\frac{K^2}{E^2}
=-\frac{K(E-K)}{E^2(E-1)},
\]
so the correlation is $-1/(E-1)$. Since $E\ge3$ and $1\le K<E$, the
limiting covariance matrix is nondegenerate. The multivariate CLT and
continuity of the opposite-sign event at the origin yield the stated
probability. This proves the distributional claim for the declared
construction; it does not use an empirical estimate.

## Controlled synthetic check

[`scripts/run_random_facet_mismatch_probability.py`](../../scripts/run_random_facet_mismatch_probability.py)
evaluates the exact finite sum and simulates the same planted-facet
distribution for $E=4$, $K\in\{1,2,3\}$, and
$T\in\{8,16,32,64,128\}$, with 20,000 independent replicates per cell.
Every Monte Carlo estimate was within five binomial standard errors of the
exact value; see
[`admitted_random_facet_probability_experiment_2026-10-17.md`](admitted_random_facet_probability_experiment_2026-10-17.md)
and the machine-readable
[`summary.json`](../../results/random_facet_mismatch_probability/summary.json).

The separate 40-plant facet ensemble in
[`admitted_facet_ensemble_experiment_2026-10-17.md`](admitted_facet_ensemble_experiment_2026-10-17.md)
is not a validation of this conditional sampling law: it samples candidate
facets under a different procedure. Its mismatch percentages must not be
compared numerically to $p_{E,K,T}$ as if they used the same facet distribution.

## Literature boundary and reduction risk

The proof uses elementary multinomial counting and a standard bivariate CLT;
these probability tools are not new. Convex-potential equivalence through
cyclic monotonicity is classical ([Rockafellar 1966](https://msp.org/pjm/1966/17-3/pjm-v17-n3-p08-p.pdf)).
The router's score-tie hyperplanes have equations
\[
q_i-q_j=(a_{t,i}-a_{t,j})/\gamma,
\]
so their normals are the roots $e_i-e_j$ of type $A_{E-1}$. Counting
regions of braid-arrangement deformations is an established subject; for
example, [Athanasiadis and Linusson](https://arxiv.org/abs/math/9702224)
count regions of the Shi arrangement, and
[Bernardi](https://arxiv.org/abs/1604.06554) studies region counts and
bijections for deformations of the braid arrangement. Those
results do not directly give the capacity-labeled mismatch count here: the
router offsets are arbitrary real affinity differences with cross-pair
dependencies, and the theorem counts a specified family of regular facets
whose admitted changes violate the potential jump condition. The root
directions or a generic arrangement-region upper bound alone are not a
novelty claim.
The MoE neighbor $\phi$-Balancing has a different population-probability
objective ([ICML 2026 paper](https://proceedings.mlr.press/v306/chen26br.html)),
but its existence makes broad claims about “potential methods for MoE”
untenable. Finite-outcome cyclic monotonicity also appears in allocation and
choice theory, for example [Kushnir and Lokutsievskiy 2021](https://doi.org/10.3982/TE4305).

The present theorem quantifies local clipping-induced non-potentiality for a
specified random Top-$K$ facet distribution. It is not a closed-loop value
gap, a telemetry break-even, or a training result. Because the exact
finite-instance outcome map can still be represented by the paper's broad
polyhedral benchmark, this theorem alone does not close the benchmark
reduction or establish top-conference novelty. Its value is a proved
family-level structural rate that can be combined with a further result only
if that result survives the same reduction and prior-art checks.

A targeted search for the exact combination of MoE hard Top-$K$ routing,
per-expert clipping, and cyclic-monotonicity analysis did not surface a direct
match. That search was not systematic and does not establish novelty. The
finite-outcome allocation literature is close enough that the proof must be
positioned as a specific capacity-clipping result rather than as a new
cyclic-monotonicity framework.

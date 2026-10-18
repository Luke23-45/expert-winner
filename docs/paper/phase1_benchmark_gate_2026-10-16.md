# Independent benchmark gate for the admitted-feedback value gap

**Date:** 2026-10-16  
**Branch:** `feat/research-censored-feedback`  
**Status:** the broad and polyhedral benchmarks are defined; a coarse-
statistics impossibility result and an exact Top-K-to-polyhedral simulation
are proved; no fixed-instance separation is possible in these classes.

## 1. Question and research decision

The fixed-instance results in
[`phase1_probe_wait_value_theorem_2026-10-16.md`](phase1_probe_wait_value_theorem_2026-10-16.md)
and
[`phase1_matched_testing_comparator_e4_2026-10-16.md`](phase1_matched_testing_comparator_e4_2026-10-16.md)
are valid value results, but their Bellman recursions transfer unchanged to
state-constrained adaptive testing when the same outcome maps are supplied.
The benchmark question is therefore not whether a generic model can encode
the instance—it can—but whether a useful, independently specified model
preserves enough constraints to support a nontrivial theorem without simply
copying the MoE pressure-cell graph.

This note fixes that broad model, proves why matching only common scalar
descriptors is inadequate, and identifies what extra structural statement a
Top-K result would have to establish. The outcome is deliberately a research
gate, not a novelty claim.

## 2. Benchmark B0: metric-constrained mass-conserving admission control

Define a finite-horizon abstract experiment by
\[
\mathfrak B=(\mathcal W,b,\mathcal Q,d,\beta,q_0,E,K,T,C,
                 R,\mathsf{H}),
\]
where:

- \(\mathcal W\) is a finite static hidden-world set with prior \(b\);
- \((\mathcal Q,d)\) is a metric action/state space, with initial state
  \(q_0\), and actions must satisfy \(d(q_t,q_{t+1})\le\beta\);
- \(R^w(q)\in\mathbb Z_{\ge0}^E\) is a world- and action-dependent
  request vector satisfying \(\mathbf1^\top R^w(q)=KT\);
- admission and loss are fixed, not chosen by the policy:
  \[
  A^w_e(q)=\min\{R^w_e(q),C_e\},\qquad
  \ell(A)=KT-\mathbf1^\top A;
  \]
- the requested policy sees \(R^w(q_t)\), while the admitted policy sees
  \(A^w(q_t)\); both know \(C\), share the same state, movement, prior,
  horizon, and causal-policy rules.

The objective is expected cumulative loss
\(\mathbb E_b\sum_{t=0}^{H-1}\ell(A^w(q_t))\). B0 is specified without
experts, logits, Top-K, or a router. It retains the exact mass-conservation,
clipping, overflow, and movement facts relevant to the signal comparison.

### Proposition 1 — exact embedding and no value separation at the instance level

Every finite static-affinity MoE instance with a fixed capacity vector embeds
in B0 by setting
\[
R^w(q)=\operatorname{TopKCounts}(a^w-\gamma q),
\]
using the gauge-quotient pressure metric for \(d\), and retaining its exact
affinity-dependent request map. The two policy classes, histories, losses,
reachable trajectories, and Bellman values are then identical. Therefore a
fixed-instance inequality about \(V_A-V_R\) transfers to B0 with the same
constant whenever its proof uses only the B0 axioms. This proposition is a
reduction statement, not a claim that B0 is a new literature model.

*Proof.* The map from a MoE pressure to its request vector is, by
construction, one admissible B0 outcome map. Admission is the same coordinate
clip; the metric transition relation is the same gauge-projected reach set;
and the loss is the same overflow identity. Thus each causal policy has the
same action/outcome history and pathwise cost in both descriptions. Taking
expectations and infima preserves equality. \(\square\)

### Proposition 2 — exact reduction of the stochastic C2 value comparison

The two-world, one-observation C2 problem in
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md)
is exactly a finite Bayesian observation-and-action experiment. Define the
benchmark independently of a router by
\[
\mathfrak D=(\mathcal W,b,\mathcal Y_R,P_R,\phi,\mathcal Q,\ell),
\]
where \(\mathcal W\) is the hidden-world set and prior, \(\mathcal Y_R\) is
the requested-signal alphabet, \(P_R(\cdot\mid w)\) is its observation
channel, \(\phi:\mathcal Y_R\to\mathcal Y_A\) is a deterministic coarsening,
\(\mathcal Q\) is the action set, and \(\ell(w,q)\) is the expected
post-observation decision loss. A policy receives either \(Y_R\) or
\(Y_A=\phi(Y_R)\), then chooses an action (randomization is allowed). Let
\(V_R^{\mathfrak D}\) and \(V_A^{\mathfrak D}\) be the two minimum Bayes
risks.

For the C2 instance, take \(\mathcal W=\{0,1\}\), the equal prior,
\(\mathcal Y_R=\{r\in\mathbb Z_{\ge0}^E:\mathbf1^Tr=KT\}\), and
\(P_R(\cdot\mid h)\) equal to the first-batch Top-K request-count law at its
fixed initial pressure in world \(h\). Set
\(\phi(r)=\min(r,C)\), \(\mathcal Q\) equal to the full gauge-fixed
pressure space, and \(\ell(h,q)\) equal to expected normalized overflow in
the independent fresh batch. Then
\[
V_R^{\mathfrak D}=V_R(T),\qquad V_A^{\mathfrak D}=V_A(T)
\]
exactly, for every finite \(T\). The equality includes randomized policies
and the full pressure action space; it is not an asymptotic approximation.

*Proof.* A policy in either description is a stochastic kernel from its
observed signal alphabet to \(\mathcal Q\). The prior, signal law, coarsening,
action set, and conditional loss agree term by term. Thus the policy kernels
are identical and each has the same Bayes risk; taking infima proves both
equalities. \(\square\)

This is an exact reduction, not a claim that the MoE model is uninteresting.
It shows that the current finite-instance value gap cannot separate itself
from a general costed-observation benchmark by value alone. Any distinct
result must quantify a property of the *family* of Top-K channels that the
benchmark does not simply encode as its observation kernel.

### Proposition 3 — the local small-skew value expansion is generic

Let \(\rho:\mathbb R^{E-1}\to\operatorname{relint}(\Delta_{E,K})\) be a
continuously differentiable bijection with continuously differentiable
inverse, where
\(\Delta_{E,K}=\{x\in[0,1]^E:\mathbf1^Tx=K\}\). Fix an interior target
\(c=\rho(\theta_c)\), a baseline \(\bar\theta\), and a direction \(d\).
For two worlds \(\theta_\pm(\epsilon)=\bar\theta\pm\epsilon d\), define
\[
v_*(\epsilon)=\inf_q\frac{1}{4K}\sum_{s\in\{+,-\}}
 \left\|\rho(\theta_s(\epsilon)-q)-c\right\|_1.
\]
If the zero-cost common action at \(\epsilon=0\) is unique, as follows from
injectivity of \(\rho\), then
\[
v_*(\epsilon)=\frac{\epsilon}{2K}
\left\|D\rho(\theta_c)d\right\|_1+o(\epsilon).
\]

*Proof.* Set \(q_0=\bar\theta-\theta_c\). Evaluating at \(q_0\) and using
Fréchet differentiability gives the upper bound with the displayed leading
term. For the lower bound, choose \(o(\epsilon)\)-optimal actions
\(q_\epsilon\). The upper bound forces both nonnegative overflow costs to
vanish, and exact mass conservation makes each cost equal to one half of
the corresponding \(L^1\) distance from \(c\). Hence both routing vectors
converge to \(c\); continuity of \(\rho^{-1}\) gives
\(q_\epsilon\to q_0\). The triangle inequality yields
\[
v_*(\epsilon)\ge \frac{1}{4K}
\left\|\rho(\theta_+(\epsilon)-q_\epsilon)-
             \rho(\theta_-(\epsilon)-q_\epsilon)\right\|_1
=\frac{\epsilon}{2K}\left\|D\rho(\theta_c)d\right\|_1+o(\epsilon).
\]
The bounds match. \(\square\)

This expansion is not Top-K-specific. In the current theorem, Top-K enters
when its Plackett-Luce choice map is substituted to compute
\(D\rho(\theta_c)d\), including the prefix-sum and switching-facet
representations. Therefore the general local expansion cannot be presented
as the structural novelty; the remaining claim to assess is whether the
explicit Top-K coefficient and its \((E,K,c)\)-scaling are new and
consequential against existing random-utility and active-testing theory.
For the exact \(E=3,K=2\) instance, the derivative is
\((39/80,-39/80,0)\), so its L1 norm is \(39/40\) and the generic formula
gives \((39/40)/(2K)=39/160\), matching the theorem's coefficient. This
calculation establishes the normalization consistency; it does not by itself
prove the finite-batch requested-versus-admitted value limit, which also
requires the separate signal-identification and clipping-coupling bounds in
the C2 theorem.

## 3. Why coarse matching cannot give the desired benchmark theorem

The following counterexample holds fixed more than just the number of
worlds: it uses the E=4 instance's \(K,T,C\), prior, action metric and
movement budget, initial admitted observation, and mass-conserving integer
request vectors. It changes only the action-to-request map, which B0 leaves
unrestricted.

Take three equally likely worlds, \(K=1,T=170\),
\(C=(50,50,50,30)\), and use relative pressure coordinates
\(x_e=\gamma(q_e-q_4)\), \(e=1,2,3\), with
\[
d(x,x')^2=(x-x')^\top\left(I-\tfrac14\mathbf1\mathbf1^\top\right)(x-x').
\]
Take \(q_0=0\), \(q_1=(a,0,0)\) for \(a=1+\varepsilon\),
\(0<\varepsilon<2\), and the E=4 high-movement condition
\(\beta\ge\sqrt2a\); then \(q_1\) is reachable from \(q_0\). At \(q_0\),
set the world-specific request vectors to
\[
R^1(q_0)=(70,50,50,0),\quad
R^2(q_0)=(50,70,50,0),\quad
R^3(q_0)=(50,50,70,0),
\]
so every world has the same admitted vector
\[
A^w(q_0)=(50,50,50,0),
\]
making the admitted observation initially identical and the first-round
overflow 20. At \(q_1\), set the requests equal to these distinct,
capacity-feasible vectors:
\[
R^1(q_1)=(50,50,50,20),\quad
R^2(q_1)=(50,50,49,21),\quad
R^3(q_1)=(50,49,50,21).
\]
Each has total mass 170, each is within \(C\), and hence each has zero
overflow; each also identifies the world. In contrast, the requested vector
at \(q_0\) can be made world-identifying while preserving its common admitted
vector. Thus both regimes pay exactly the unavoidable 20 and then incur zero
additional overflow: \(V_A(H)=V_R(H)=20\) for \(H\ge2\).

This proves that **there is no positive admitted-versus-requested gap
guaranteed by the coarse descriptors alone**, even when those descriptors
include the exact capacity vector, batch mass, movement metric/radius,
initial admitted alias, outcome alphabet, and loss identity. It does not
refute the E=3/E=4 MoE results; this request map is intentionally not claimed
to be Top-K-realizable. It pinpoints the missing assumption: a benchmark must
constrain how outcomes vary with the action.

## 4. Literature boundary from primary sources

The literature supports two separate benchmark axes; neither alone is the
whole B0 model.

1. **Costed adaptive information acquisition.** Naghshvar and Javidi use
dynamic programming to bound optimal total cost in active sequential
hypothesis testing. Javdani et al. study Bayesian active learning for
decision-making, where tests are selected to place the remaining hypotheses
inside a common decision region. Vaidhiyan and Sundaresan explicitly include
action-switching costs in active search. These are direct conceptual
neighbors for belief updates and costed information acquisition, but their
stated models do not supply B0's arbitrary metric-constrained action state
plus clipping-derived outcome loss
([Naghshvar and Javidi](https://arxiv.org/abs/1203.4626),
[Javdani et al.](https://proceedings.mlr.press/v33/javdani14.html),
[Vaidhiyan and Sundaresan](https://arxiv.org/abs/1505.02358)).
2. **Geometric query structure.** Kane, Lovett, and Moran study linear
decision trees for point location in hyperplane arrangements; Hopkins et al.
study point location and active learning of halfspaces. These establish
substantial prior art on adaptive queries constrained by hyperplane
geometry. Their query-complexity objectives do not charge overflow on each
visited state or constrain successive query locations by a gauge metric
([Kane et al., ICALP 2018](https://doi.org/10.4230/LIPIcs.ICALP.2018.82),
[Hopkins et al.](https://arxiv.org/abs/2004.11380)).
3. **Metric movement.** Koren, Livni, and Mansour study metric movement costs
in non-stochastic bandits and give minimax-regret guarantees. That is direct
prior art for movement-sensitive action selection, but it uses an online
bandit regret objective rather than deterministic hidden-world observations
with admission-derived outcome costs ([paper](https://arxiv.org/abs/1710.08997)).

For Top-1, score changes occur on \(q_e-q_f=a_{i,e}-a_{i,f}\). Thus each
token induces a translate of the type-A braid arrangement; a batch gives a
union of such translated arrangements, followed by count aggregation and
capacity clipping. The offsets within each token's comparisons are
consistent because they arise from one affinity vector. This is more
structured than an arbitrary affine arrangement. Region-counting results
for braid-arrangement deformations are relevant geometric tools, but they
count cells, not the minimum overflow cost of a movement-constrained adaptive
policy ([Bernardi, *Deformations of the braid arrangement and trees*](https://doi.org/10.1016/j.aim.2018.07.020),
[Zaslavsky, *Facing Up to Arrangements*](https://doi.org/10.1090/memo/0154)).

### Lemma 2 — the Top-1/gauge arrangement restriction

Fix one token with affinity vector \(a_i\). Its expert-\(e\) score is
\(a_{i,e}-\gamma q_e\). Experts \(e\) and \(f\) tie exactly on
\[
\gamma(q_e-q_f)=a_{i,e}-a_{i,f}.
\]
In the quotient by common-mode pressure, each boundary normal is the root
\(e_e-e_f\) of type \(A_{E-1}\), hence is orthogonal to the gauge direction
\(\mathbf1\). For three experts, the offsets obey the token-consistency
identity
\[
(a_{i,e}-a_{i,f})+(a_{i,f}-a_{i,g})=a_{i,e}-a_{i,g};
\]
the pairwise hyperplanes for one token cannot be positioned independently.
The same pairwise score comparisons determine the complete ranking and
therefore Top-K membership for any K. Aggregating token winners and clipping
by C then maps these cells to admitted-count outcomes.

*Proof.* Subtract the two pressure-adjusted scores. The common-mode
component of q cancels, leaving the displayed equality. Every boundary
normal has coordinate sum zero, and the offset identity follows by
cancellation of the affinity terms. Top-K selects the first K experts in
this same pairwise ordering. \(\square\)

This is a genuine Top-K/gauge **structural restriction** relative to an
arbitrary arrangement: normals and within-token offsets are constrained.
It is not yet a quantitative value restriction. The E=4 theorem does not
derive a lower bound from Lemma 2 that could not be proved in a generic
metric-constrained polyhedral experiment.

### Corollary 2.1 — a root-matroid upper bound on one-round signatures

Let \(d=E-1\), let \(N\) be the number of distinct token/world affinity
vectors in a fixed round, and let \(F_E(z)\) be the forest polynomial of
the complete graph on E vertices:
\[
F_E(z)=\sum_{F\text{ a forest of }K_E}z^{|F|}.
\]
The number of distinct joint request signatures
\((R^w(q))_{w\in\mathcal W}\) achievable as q ranges over the gauge
quotient is at most \(F_E(N)\). For a general arrangement of
\(M=N\binom E2\) hyperplanes in dimension d, the corresponding chamber
bound is \(\sum_{k=0}^{d}\binom Mk\). In particular, for E=4,
\[
F_4(N)=1+6N+15N^2+16N^3,
\]
whereas the unrestricted arrangement bound is
\(1+6N+\binom{6N}{2}+\binom{6N}{3}\).

*Proof.* The normals are the incidence roots \(e_e-e_f\) of edges of
\(K_E\). A set of these roots is linearly independent exactly when its
edges form a forest. There are at most N parallel copies of each root
direction, one per token/world affinity vector. The deletion-restriction
recurrence for arrangement regions bounds the number of chambers by the
number of independent subfamilies of normals; choosing a k-edge forest
and one of at most N copies for each edge gives \(F_E(N)\). The standard
general-position upper bound gives the comparator expression for M
unrestricted hyperplanes. Finally, a pressure on one or more tie hyperplanes
has the same deterministic lower-index tie-broken winner pattern as a
sufficiently small common perturbation that favors lower expert indices:
replace q_e by q_e+\epsilon e/\gamma, then gauge-normalize. Because the
number of scores is finite, choose \(\epsilon\) small enough to preserve
all strict comparisons. Thus boundary tie outcomes add no request
signatures beyond the full-dimensional chambers. \(\square\)

**Literature correction (2026-10-18).** For independent affinity coordinates
with densities, the genericity conditions hold almost surely, and the
arrangement is precisely the union of `N` generically translated copies of
the type-A braid arrangement. Delcroix-Oger et al. give its exact region
count in Theorem 2.21 of *Cellular Diagonals of Permutahedra*
([arXiv:2308.12119](https://arxiv.org/abs/2308.12119)). Their formula is
`E! [z^E] exp(sum_{j>=1} FC(N,j) z^j/j)`, with
`FC(N,j)=binom(N*j,j)/((N-1)*j+1)`. Since complete per-token rankings are
constant on those regions and request-count signatures are coarsenings, that
known formula directly bounds the signatures counted here. The forest
polynomial above remains a valid but weaker elementary bound; it should not
be presented as a new region-count theorem. The potential additional object
is a capacity-labeled quotient of these regions, and its value relevance is
still unproved.

This corollary quantifies a combinatorial restriction on pressure-induced
tests, and the existing E=4 exact checker gives 51 feasible winner
signatures (45 distinct admitted cost maps) for its particular six affinity
types. At \(N=6,E=4\), the root bound is 4033 signatures, while 36 unrestricted
hyperplanes have the general-position bound 7807. The exact instance's 51
signatures show how loose both bounds are for this construction. More
importantly, the bound counts possible signatures without charging their
overflow or accounting for which partitions are reachable at low cost. It
is therefore not yet a control value lower bound. Region-counting theory
already treats deformations of braid arrangements; this corollary is a
convenient bound for our root-normal multiset, not a novelty claim in
arrangement enumeration.

**Literature conclusion:** the well-studied pieces are adaptive costed
testing, metric or switching costs, and hyperplane point location. This
search does not establish that their intersection is unoccupied. It does
establish that a novelty claim cannot rest on any one ingredient or on a
generic Bellman recursion. The contribution must be a proved property of the
Top-K score-arrangement subclass and overflow labels.

## 5. Benchmark B1: metric-constrained polyhedral active testing

Define B1, the **metric-constrained polyhedral active-testing** benchmark,
independently of MoE as follows. It has a finite static hypothesis set and
prior, a metric action space with a per-step movement radius, and for each
hypothesis and round a piecewise-constant outcome map over the faces of a
finite affine-hyperplane arrangement. The output belongs to a declared finite
loss alphabet and the loss is a fixed bounded function of that output. The
requested/admitted comparison can be represented by paired outputs
\((R,A)\) with the deterministic clipping relation and mass constraint from
B0. Dimension, horizon, prior, movement radius, arrangement-size budget,
loss alphabet, and initial common admitted observation are explicit
parameters. Arrangement faces include boundary/tie strata, not only full-
dimensional open cells.

### Proposition 4 — every finite Top-K instance is exactly simulable in B1

Fix a finite set of hidden affinity sequences and a finite horizon. In
relative pressure coordinates, for every round \(t\), world \(w\), token
\(i\), and expert pair \(e<f\), include the score-tie hyperplane
\[
\mathcal H_{t,w,i,e,f}
 =\{q:(a^w_{t,i,e}-a^w_{t,i,f})-
                  \gamma(q_e-q_f)=0\}.
\]
On every sign-vector face of the union arrangement, all pairwise score
orders for every token and world are fixed. Deterministic tie-breaking
therefore fixes every Top-K set, the request-count vector, the clipped
admitted vector, and overflow. Label each face with those exact outputs.
Use the MoE gauge-quotient metric and movement radius as B1's metric action
space. This reproduces every causal history, feasible transition, pathwise
cost, and Bellman value exactly, for both information regimes. The number of
hyperplanes is at most
\(|\mathcal W|HT\binom E2\), before duplicate planes are removed.

*Proof.* The pairwise sign vector fixes each token's total expert ordering,
including equalities resolved by the shared tie rule. Summing the resulting
Top-K indicators fixes \(R\); clipping fixes \(A\) and its cost. The same
pressure points and metric transitions are retained, so the policy trees
and their path costs coincide. \(\square\)

**Consequence:** the E=3 and E=4 fixed-instance value theorems have exact B1
simulations. A strict difference in optimal value between one such MoE
instance and its B1 simulation is mathematically impossible: the simulation
is the same experiment with a different description. The simulation resolves
the current fixed-instance benchmark gate in the negative. This is stronger
than a similarity argument based on literature; it is an exact reduction.

### Proposition 5 — extension to coupled, score-ranked admission

B1 as defined above uses coordinate clipping and therefore does not directly
contain a shared device-capacity admission rule. To compare that rule without
changing assumptions silently, define B1-out by replacing the clipping
equation with a fixed cell-output map
\[
o_{w,t}(q)=(R^w_t(q),A^w_t(q))\in\mathcal O,
\]
where \(\mathcal O\) is a finite alphabet of integer vector pairs satisfying
\(\mathbf 1^\top R=KT\), \(0\leq A\leq R\), and the experiment's declared
fixed overflow loss. The requested observer receives \(R\), the admitted
observer receives \(A\); the prior, action metric, movement constraint,
horizon, and causal-policy definitions are unchanged. B1-out is a general
finite polyhedral outcome experiment, not a MoE-specific admission model.

Every fixed finite-horizon static-affinity Top-K instance with deterministic
per-expert or shared-device admission ranked by **raw route affinity** embeds
exactly in B1-out. For every token and expert pair, include the affine
router-score tie plane. Raw-affinity drop priorities are fixed within a
world, so their ranking is constant; once the router arrangement fixes the
requested routes, the fixed admission rule fixes all admitted routes. If a
different model ranks routes by scores that vary affinely with pressure, add
the pairwise admission-priority tie planes too. On each resulting arrangement
face, the fixed tie rules determine all requested routes, all admitted
routes, and hence \((R,A)\) and the overflow loss. Assign this pair as the
face's output label and retain the exact gauge metric and transitions. The
policy histories and pathwise costs then coincide, so the Bellman values are
identical. A policy that ranks by cross-token softmax probabilities is not
covered by the affine-plane statement without a separate boundary-geometry
proof.

This proposition is an exact **instance representation**. It does not say
that the coupled-capacity map is coordinate clipping, and it does not establish
a family-level theorem or a contribution beyond polyhedral active testing.
Any comparison of the professor's device-drop extension must use B1-out (or
another benchmark fixed independently of the MoE family), rather than claim
that the original clipping-only B1 already models it.

There remains a different, class-level question: can the token-consistent
root-arrangement subclass admit a sharp family theorem that is not implied
by known guarantees for general metric-constrained polyhedral testing? That
question cannot be answered by comparing one instance to its exact B1
copy. Any new comparison must declare a family quantifier (for example,
worst-case over a precisely specified family), constrain the affinity,
capacity, and initial-alias conditions before construction, and prove a
root-geometry-dependent extremal result. Merely noting that its normals are
restricted is not that result.

The E=4 exact audit remains an exact value result for one instance. It is not
a family-level separation from B1. Do not run empirical sweeps for this
static fixed-instance novelty route; the simulation has already shown that
benchmark cannot separate it.

## 6. Current decision

- **Proved:** B0 exactly contains the MoE instance-level value problem.
- **Proved:** coarse scalar matching in B0 is insufficient; a mass-conserving
  abstract plant can make the admitted and requested values equal.
- **Proved:** every finite-horizon finite-affinity Top-K experiment is a B1
  polyhedral experiment with the same value; fixed-instance separation from
  B1 is impossible.
- **Proved:** Top-K's one-round pressure arrangement has root-system normals;
  its number of joint request signatures obeys the forest-polynomial bound.
- **Literature-grounded:** costed active testing and geometric point location
  are both established research areas; arrangement cell counts alone do not
  yield the required costed-control theorem.
- **Open:** a class-level extremal result for the token-consistent
  root-arrangement subclass, with an explicit family quantifier and a
  nontrivial comparison theorem against general metric-constrained
  polyhedral testing.
- **Current paper guidance:** stop the fixed-instance MPAT-separation route.
  Keep the exact MoE value theorem as an application. Reopen this lane only
  for a class-level theorem whose quantitative conclusion depends on the
  root-arrangement constraints.

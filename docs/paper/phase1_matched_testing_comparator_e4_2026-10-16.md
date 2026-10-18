# Matched testing comparator and E=4 Top-1 probe audit

**Date:** 2026-10-16  
**Branch:** `feat/research-censored-feedback`  
**Status:** exact matched comparator plus an exact E=4, all-causal-policy
three-round value theorem at high movement budget; no novelty claim beyond
state-constrained adaptive testing.

## 1. Decision this note is meant to support

The fixed E=3 probe-versus-wait theorem is an exact result for an MoE
instance, but its proof is preserved by the state-constrained testing
reduction. The next question is whether increasing the expert count produces
a quantitative Top-K/gauge fact that is stronger than the corresponding
generic testing statement.

This note defines the strongest instance-matched comparator and works out an
E=4 candidate-probe family exactly. The calculation confirms that the
candidate probes form an ordinary noiseless adaptive-search problem. It does
not show that these probes are optimal among all pressures, nor that the
result separates from generic testing. That is a useful negative checkpoint:
the E=4 construction alone is not yet the desired contribution.

## 2. Exact matched state-constrained testing comparator

For a finite static hidden environment set \(\mathcal W\), prior \(b_0\),
state space \(S\), and horizon \(H\), define a deterministic testing
instance by:

- a state transition relation \(\mathcal R_t(s)\subseteq S\);
- an outcome map \(g_t:\mathcal W\times S\to\mathcal O\);
- an observed-outcome cost \(\ell_t:\mathcal O\to\mathbb R_{\ge0}\);
- an initial state \(s_0\).

A policy observes \(o_t=g_t(w,s_t)\), updates its posterior, and selects
\(s_{t+1}\in\mathcal R_t(s_t)\). Its objective is
\(\mathbb E[\sum_{t=0}^{H-1}\ell_t(o_t)]\). The Bellman state is
\((b_t,s_t)\). This includes randomized causal policies; randomization
cannot lower the infimum of expected cost over the available actions.

For the MoE controller, take \(S=\mathcal Q\), \(g_t(w,q)=A^w_t(q)\),
\(\ell_t(o)=KT-\mathbf1^\top o\), and \(\mathcal R_t(q)\) equal to the
exact gauge-projected feasible pressure set from (Reach) in
[`phase1_h3_dp_reduction.md`](phase1_h3_dp_reduction.md). These choices
produce the same posterior updates, feasible policies, path costs, and
therefore the same Bellman recursion and optimal value, round by round.
This is an exact equivalence by construction, not an approximation.

Consequently, **no theorem about one fixed MoE instance can separate its
value from this fully instance-matched comparator**. A meaningful
MoE-specific theorem must instead compare a *family* of realizable Top-K
testing systems against a broader benchmark defined without copying their
exact outcome maps. That benchmark must be specified before claiming a
separation. At minimum it must state what is matched: hidden-world count and
prior, state dimension and metric, movement radius, number of outcomes,
loss range, initial indistinguishability, and what information is free.
Matching the entire pressure-cell outcome/cost graph collapses the comparison
to an identity.

## 3. E=4, K=1 construction

Use three regular experts and one sink:

\[
E=4,\quad K=1,\quad C_1=C_2=C_3=50,\quad C_4=30,\quad
E_S=20,\quad T=3C+E_S=170.
\]

There are three equally likely static worlds \(i\in\{1,2,3\}\). In world
\(i\), the batch consists of a \(C\)-token high-margin block \(H_i\), a
\(C\)-token low-margin block \(L_e\) for each regular expert \(e\ne i\),
and an additional \(E_S\)-token low-margin block \(L_i\). A low block for
expert \(e\) has affinities 1 at expert \(e\), 0 at the sink, and -3 at the
other regular experts. The high block \(H_i\) has affinity 3 at \(i\), 0
at the sink, and -3 at other regular experts. Pressure-adjusted score is
affinity minus pressure; ties go to the lower expert index.

At \(q_0=0\), each block routes to its named regular expert. Thus
\(R^i_0\) has \(C+E_S=70\) requests at expert \(i\), \(C=50\) at each
other regular expert, and zero at the sink. Every world yields the same
admitted vector
\[
A^i_0=(50,50,50,0),\qquad \|J^i_0\|_1=20.
\]
The requested vector identifies \(i\); the admitted vector does not.

### Candidate pressure and exact response

Write \(x_e=\gamma(q_e-q_4)\) for \(e=1,2,3\). For candidate \(j\),
choose
\[
x^{(j)}_j=1+\varepsilon,\quad x^{(j)}_e=0\ (e\ne j),
\qquad 0<\varepsilon<2.
\]
Then \(L_j\) routes to the sink because its score at \(j\) is
\(-\varepsilon<0\) and its sink score is zero; \(H_j\) still routes to
\(j\), since its score there is \(2-\varepsilon>0\). Every other low
block remains at its named regular expert.

- If \(i=j\), the excess low block moves to the sink, which admits all 20
  tokens. The admitted vector is \((50,50,50,20)\) and overflow is zero.
- If \(i\ne j\), the baseline \(C\)-block \(L_j\) moves to the sink,
  causing sink overflow \(C-C_4=20\); the excess block \(L_i\) remains
  on top of the high block at expert \(i\), causing another 20 overflow.
  Total overflow is 40, and the admitted vector has zero at coordinate \(j\),
  50 at the other regular coordinates, and 30 at the sink.

Hence this pressure is an exact test of \(i=j\) against \(i\ne j\):
success identifies the world, while failure eliminates only \(j\). Under
the uniform prior, its *immediate expected overflow* is
\[
\frac13\,0+\frac23\,40=\frac{80}{3}>20,
\]
whereas holding at \(q_0\) costs 20 and reveals nothing. The candidate test
is informative but myopically more expensive than waiting.

### Reachability and candidate-only policy value

The gauge-invariant pressure metric is
\[
d(x,x')^2=(x-x')^\top\left(I-\frac14\mathbf1\mathbf1^\top\right)(x-x').
\]
For \(a=1+\varepsilon\), the origin-to-candidate distance is
\(d(0,x^{(j)})=\sqrt3a/2\), and the distance between distinct candidate
pressures is \(\sqrt2a\). Thus if
\(\beta=\eta\gamma^2B\ge\sqrt2a\), the initial move and every candidate
switch are feasible when \(\delta=0\). The parameter \(\varepsilon\) can be
arbitrarily small, so any fixed \(\beta>\sqrt2\) allows such a choice.

With this reach budget, test candidates 1 and 2 in order. Stop after a
success; after two failures the remaining world is known. Across the three
equally likely worlds, expected probe overflow is 40, so cumulative cost is
60 including the initial round. The exact all-policy result is established
in §4 below; this candidate sequence attains it for \(H\ge3\).

The policy and calculation are reproduced by a generic adaptive-testing
model with three hypotheses and two candidate tests. They are an E=4 MoE
realization, but not an E=4 Top-K separation.

The same candidate-only calculation extends to \(N=E-1\ge2\) regular
experts and one sink, under \(0<E_S\le C_{sink}<C\) and the same margins.
Let
\(L=E_S+C-C_{sink}\). Each failed candidate probe costs \(L\), the correct
candidate costs zero, and a uniform prior gives \((N-1)/2\) expected failed
probes when testing \(N-1\) candidates and inferring the last after all
failures. For \(\beta\ge\sqrt2(1+\varepsilon)\) and \(H\ge N+1\), this
specific policy has value
\[
V_A(H)\le E_S+\frac{N-1}{2}\left(E_S+C-C_{sink}\right).
\]
This is an upper bound from one chosen policy, not the optimal admitted
value. Its \(\Theta(E)\) scaling is the standard linear-search cost for
noiseless singleton tests; it does not by itself establish an MoE-specific
scaling law.

## 4. Exact E=4 three-round value from the full pressure partition

The six token types \((L_1,L_2,L_3,H_1,H_2,H_3)\) induce at most 36
pairwise score-equality planes in the three-dimensional relative-pressure
space. We enumerate all \(4^6=4096\) joint winner assignments and test each
assignment's exact strict/non-strict score inequalities by rational
Fourier-Motzkin elimination. This includes tie strata under lower-index
priority. The finite-case audit is
[`scripts/analyze_e4_exact_partition.py`](../../scripts/analyze_e4_exact_partition.py):
51 assignments are feasible and they induce 45 distinct joint
observation/cost maps. The script is a reproducible exact-arithmetic check;
the score inequalities and this finite reduction must still be presented in
the paper.

Across these maps, 42 have no zero-overflow world, three have exactly one,
and none have two or more. The minimum informative expected current cost
under the full prior is exactly \(80/3\); under each two-world uniform
posterior it is 20. These are exact one-stage properties of this finite
construction, not yet family-level information bounds.

The resulting Bellman certificate for one or two remaining rounds is:

| Current posterior support | Minimum one-round expected overflow |
|---|---:|
| One world | 0 |
| Any two worlds, uniform on the pair | 20 |
| All three worlds, uniform | 20 |

For the full three-world prior and two rounds remaining, the first pressure
can induce only these partition shapes. The exact minimum immediate costs
and their Bellman continuation bounds are:

| Observation partition at first pressure | Minimum immediate expected cost | Minimum expected one-round continuation | Total lower bound |
|---|---:|---:|---:|
| One block of size 3 (uninformative) | 20 | 20 | 40 |
| One singleton and one pair | \(80/3\) | \((2/3)20=40/3\) | 40 |
| Three singleton blocks | \(170/3\) | 0 | \(170/3\) |

The minimum singleton/pair immediate cost is attained by the candidate
outcome-cost pattern \((0,40,40)\), up to permutation. The pair branch keeps
two equally likely worlds and costs at least 20 in the final round; the
singleton branch costs at least zero. The table therefore gives an
unrestricted-transition lower bound of 40 for the last two rounds from the
full prior. It is valid for the physical controller because removing the
pressure-reach constraint can only lower the optimal cost.

**Proposition (E=4 value, high movement budget).** Under the construction in
§3, \(\delta=0\), equal prior, and
\(\beta=\eta\gamma^2B\ge\sqrt2(1+\varepsilon)\) for some
\(0<\varepsilon<2\),
\[
V_A(1)=20,\qquad V_A(2)=40,\qquad V_A(H)=60\quad(H\ge3),
\]
while \(V_R(H)=20\) for all \(H\ge2\).

*Proof.* At round zero every world has the same admitted vector and overflow
20. For a single remaining round under the full prior, the minimum possible
expected overflow over all pressures is 20; under any two-world uniform
posterior it is also 20, and under a known world it is zero. The two-round
Bellman lower bound in the preceding table is 40. Adding the unavoidable
round-zero cost proves \(V_A(H)\ge60\) for every \(H\ge3\), since costs are
nonnegative. This lower bound optimizes over every causal policy: its first
observation induces one of the enumerated partitions, and the continuation
is bounded below for the resulting posterior. Randomization cannot improve
the finite Bellman infimum.

For achievability, use candidate tests 1 and 2 as above. They require at most
two informative rounds and have expected overflow 40; after both tests the
world is known. The stated \(\beta\) makes the origin-to-candidate and
candidate-to-candidate moves feasible. Thus total cost is 60 for \(H=3\),
and the known safe candidate pressure can be reached by the next round and
held for \(H>3\), with no additional overflow. Requested feedback sees the
world at round zero and moves directly to its safe pressure, giving cost 20.
\(\square\)

The E=4 result is an exact policy-class value theorem, but the reduction to
state-constrained adaptive testing remains exact. It does **not** establish
that Top-K/gauge control has a limitation absent from that comparator.

## 5. What is established and what remains the discriminator

Established here:

1. The fully matched state-constrained testing comparator has exactly the
   MoE value by definition of its state, transitions, observations, and costs.
2. The E=4 full pressure partition gives a minimum informative one-round
   cost of \(80/3\) under the uniform three-world prior and supports the
   exact high-movement, three-round value \(V_A=60\).
3. The candidate-only policy attains that value; the requested value is 20.

Not established:

- a separation from a non-MoE testing/control benchmark;
- a general dependence on \(E\), \(K\), or heterogeneous capacities.

The next proof attempt should define a nontrivial, pre-registered generic
benchmark that is weaker than copying the MoE cell graph but strong enough to
avoid arbitrary free information. Then derive a Top-K realizability theorem
for the family of partitions/costs it permits. A candidate avenue is to
characterize the pressure cells induced by affine token scores: each change
in a token's Top-1 choice occurs on a pairwise score-equality hyperplane, so
the realizable tests are a structured polyhedral family. Hyperplane
arrangement theory counts faces from their intersection structure, but a
cell-count bound alone is not an information-per-overflow or value theorem.
Zaslavsky's face-count formulas are a geometric tool, not by themselves the
missing control result ([Zaslavsky, *Facing Up to Arrangements*](https://doi.org/10.1090/memo/0154)).

The closest sequential-testing neighbors reviewed here establish that
dynamic-programming bounds for adaptive information acquisition, and
accumulated control costs, are already standard theory: Naghshvar and Javidi
derive lower bounds on optimal total cost for active sequential hypothesis
testing; Nitinawarat and Veeravalli allow controlled Markov observations and
non-uniform accumulated control costs; Vaidhiyan and Sundaresan add action-
switching costs to active search. Their stated objectives and guarantees
focus on sequential testing and asymptotic reliability/error regimes, rather
than this exact finite-horizon overflow objective with gauge-metric movement
constraints. These papers are close conceptual neighbors, not evidence of a
novelty gap. A formal comparison must state the precise restriction that
remains after the generic state-constrained testing reduction
([Naghshvar and Javidi](https://arxiv.org/abs/1203.4626),
[Nitinawarat and Veeravalli](https://arxiv.org/abs/1310.1844),
[Vaidhiyan and Sundaresan](https://arxiv.org/abs/1505.02358)). They do not
remove the need to define the finite-horizon movement-constrained comparator
precisely.
([Vaidhiyan and Sundaresan](https://arxiv.org/abs/1505.02358),
[Nitinawarat and Veeravalli](https://arxiv.org/abs/1310.1844)).

**Decision:** do not promote the E=4 candidate calculation as the main
theorem. Continue only if the next stage proves a family-level restriction
on Top-K realizable tests and compares it against a benchmark fixed before
seeing the resulting bound. Otherwise reframe the current results as an
exact MoE application of state-constrained adaptive testing.

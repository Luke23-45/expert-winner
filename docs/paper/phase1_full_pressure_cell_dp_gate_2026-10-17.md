# Full-pressure finite-movement Bellman model: exact state and reduction gate

**Date:** 2026-10-17  
**Branch:** `feat/research-censored-feedback`  
**Status (reconciled 2026-10-17):** exact finite-horizon recursion, a
short-horizon quiet-zone theorem, and the complete E=4 values at horizons
three and four are established for every movement radius. For horizons
\(H\ge4\), the exact E=4 value is also established when
\(\beta>1/\sqrt2\). Other fixed-instance values remain open, but computing
them is not the current research gate: any finite instance has an exact
metric-constrained polyhedral testing representation. The current class-level
decision is in [`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md).

## 1. Why a cell-distance graph is not an exact controller state

At fixed pressure, Top-K routing and capacity clipping are constant on each
face of the joint score arrangement. It is tempting to replace each face by a
node and connect two nodes when their minimum distance is at most the step
radius. That graph is not an exact finite-movement model. Two pressures in one
face have the same current observation and overflow, but their reachable
balls can intersect different future faces. The exact state must retain the
pressure coordinate, not only its face label.

This matters for the proposed next computation: pairwise face distances can
provide reachability summaries, but cannot by themselves support a Bellman
recursion unless an additional theorem proves that a representative pressure
is sufficient for every posterior and horizon. No such theorem is currently
available.

## 2. Joint arrangement and labels

Fix a finite horizon, finite static world set \(\mathcal W\), and finite
token batches. Work in the gauge quotient
\(\mathcal Q=\mathbb R^E/\mathrm{span}\{\mathbf1\}\), with its induced
Euclidean metric. For every world \(w\), round \(t\), token \(i\), and
expert pair \(e<f\), include the score-tie hyperplane

$$
\gamma(q_e-q_f)=a^w_{t,i,e}-a^w_{t,i,f}.
$$

The common refinement of these hyperplanes partitions \(\mathcal Q\) into
relatively open arrangement faces \(\mathcal F\), including lower-dimensional
tie faces. The signs and equalities on a face determine every token's score
ordering. With the specified deterministic tie rule, they therefore
determine, for each \((w,t)\),

$$
g^A_{w,t}(F)=A^w_t(q),\qquad
c_{w,t}(F)=KT-\mathbf1^\top g^A_{w,t}(F),
\qquad q\in F.
$$

These labels are constant on the entire face. Faces with identical output
labels cannot generally be merged for movement planning: their geometric
locations and reachable sets can differ. A union is usable only if its
geometry is retained as a possibly disconnected set.

## 3. A finite-movement quiet-zone theorem

For the canonical Top-1 construction in the E-world notes, take zero initial
pressure, regular-expert low margin \(m>0\), high margin \(M>m\), and sink
index \(E=N+1\). In score coordinates

$$
x_e=\gamma(q_e-q_{E}),\qquad e=1,\ldots,N,
$$

the gauge metric is \(d(x,x')^2=(x-x')^TG(x-x')\), where
\(G=I-\mathbf1\mathbf1^T/(N+1)\) and \(G^{-1}=I+\mathbf1\mathbf1^T\).
The nearest winner-changing score boundary to the origin is the low-block
own-expert/sink tie \(x_e=m\). Its distance is

$$
\operatorname{dist}_d(0,\{x_e=m\})
=\frac{m}{\sqrt{e_e^TG^{-1}e_e}}
=\frac{m}{\sqrt2}.
\tag{QZ}
$$

Every other boundary that can change a token's winner is farther away: a
high block ties its own expert with the sink at \(x_e=M\), while own-versus-
other-regular ties have offsets at least \(M+m\). The tie at \(x_e=m\) is
still won by the regular expert because its index is below the sink's. Thus
the closed ball of radius \(m/\sqrt2\) around zero has exactly the same token
winners as at zero.

**Proposition (short-horizon no-information regime).** Under \(\delta=0\),
per-step gauge movement radius \(\beta=\eta\gamma^2B\), and horizon \(H\),
if

$$
(H-1)\beta\le\frac{m}{\sqrt2},
\tag{QZ-H}
$$

then every feasible pressure in every stage lies in the quiet zone. The
request and admitted vectors therefore equal their zero-pressure values in
every world and round. Both the requested- and admitted-feedback policy
classes have cumulative overflow exactly \(H E_S\).

*Proof.* Each transition has gauge distance at most \(\beta\), so the
triangle inequality gives \(d(0,q_t)\le t\beta\). Condition (QZ-H) keeps
all routed states through \(t=H-1\) in the closed quiet zone. The initial
construction has overflow \(E_S\) in every world, and its requests remain
unchanged. Hence no policy in either information regime can change any
stage's overflow. \(\square\)

This proposition gives an exact boundary regime, not a growing signal-value
gap. At the threshold itself, the tie rule matters: the low-block/sink tie
does not change the winner, so the conclusion includes equality in (QZ-H).

## 4. E=4 finite-movement value certificate

The fixed E=4 construction in
[`phase1_matched_testing_comparator_e4_2026-10-16.md`](phase1_matched_testing_comparator_e4_2026-10-16.md)
has an exact unrestricted-movement admitted value of 60 for every \(H\ge3\).
The following pressure sequence attains that lower bound at substantially
smaller movement radii than the canonical subset representatives require.

### Exact three-round values for every movement radius

Let \(\rho=1/\sqrt2\). For the E=4 construction,

$$
V_A(3)=60\quad\text{for every }\beta\ge0,
\qquad
V_R(3)=
\begin{cases}
60,&0\le\beta\le\rho/2,\\
40,&\rho/2<\beta\le\rho,\\
20,&\beta>\rho.
\end{cases}
\tag{E4-H3}
$$

For the admitted lower bound, the initial round costs 20. The E=4
all-pressure certificate in the matched-comparator note gives the exact
unrestricted-transition two-round Bellman lower bound of 40 from the full
prior. This bound accounts for every first observation partition: an
uninformative action costs at least 20 now and leaves a full-prior
one-round value of at least 20; a singleton/pair split has immediate
expected cost at least $80/3$, followed by pair-branch continuation of at
least $(2/3)20$; a fully identifying action costs at least $170/3$
immediately. The minimum of these cases is 40. Removing movement
constraints can only lower the value, so the bound applies to every
movement-constrained admitted policy. Adding the unavoidable initial cost
gives 60. The zero-pressure policy attains 60 over three rounds.

For requested feedback, the initial request reveals the world and costs 20.
The quiet-zone proposition shows that zero overflow is impossible at a
pressure within distance \(\rho\) of zero, and every positive overflow in
this construction is at least 20: every block size and capacity is a
multiple of 10, and the smallest positive overload is either
\(50+20-50=20\) at a regular expert or \(50-30=20\) at the sink. If
\(\beta\le\rho/2\), the pressure at
round 2 is within distance \(2\beta\le\rho\), so both remaining stages
cost at least 20; staying at zero attains 60. If
\(\rho/2<\beta\le\rho\), choose a world-specific zero-overflow point
arbitrarily close to distance \(\rho\), move halfway to it at round 1,
then reach it at round 2. The midpoint is in the quiet zone, so this costs
20 at round 1 and zero at round 2; the lower bound of 20 at round 1 makes
the value exactly 40. If \(\beta>\rho\), a zero-overflow point is reachable
in one step, giving value 20, the unavoidable initial cost. At \(\beta=\rho\)
the zero-overflow boundary is not attained, which is why equality belongs
to the middle case.

### Exact four-round values for every movement radius

For the same E=4 construction, the full four-round values are

$$
V_A(4)=
\begin{cases}
80,&0\le\beta\le\rho,\\
60,&\beta>\rho,
\end{cases}
\qquad
V_R(4)=
\begin{cases}
80,&0\le\beta\le\rho/3,\\
60,&\rho/3<\beta\le\rho/2,\\
40,&\rho/2<\beta\le\rho,\\
20,&\beta>\rho.
\end{cases}
\tag{E4-H4}
$$

*Proof for requested feedback.* The initial round costs 20 and reveals the
world. A zero-overflow pressure has distance strictly greater than \(\rho\)
from zero, while every nonzero overflow costs at least 20. After \(j\)
updates, pressure is at distance at most \(j\beta\). Thus the earliest
possible zero-overflow round is the least \(j\in\{1,2,3\}\) with
\(j\beta>\rho\). Before that round each stage costs at least 20. If no such
\(j\) exists, all three post-initial stages cost at least 20. These bounds
are attained: choose a world-specific zero-overflow point at distance
arbitrarily close to \(\rho\), and traverse the straight segment in \(j\)
equal moves. By minimality of \(j\), all earlier points on this segment lie
inside the quiet zone; hold at the endpoint afterward. This gives the stated
piecewise value, including the strict thresholds at \(j\beta=\rho\).

*Proof for admitted feedback.* At the initial pressure, the admitted
observation is identical in all worlds. If \(\beta\le\rho\), the next
pressure remains in the closed quiet zone, so that round also costs 20 and
reveals no information. Relaxing the movement constraint for the two
remaining rounds gives the unrestricted-transition full-prior Bellman
lower bound 40 from the exact partition certificate in the matched-
comparator note. Including the first two costs gives a lower bound of 80,
attained by staying at zero pressure. If \(\beta>\rho\), the two-probe
policy from the high-movement proposition costs 60 over the initial round
and the first two probes, then holds the identified world's safe pressure.
The same unrestricted-transition certificate gives a lower bound of 60,
so equality follows. \(\square\)

Let \(m=1\), \(M=3\), and for each regular expert \(i\in\{1,2,3\}\)
define \(p_i\) in score-offset coordinates by setting its own coordinate to
\(1+\epsilon\) and the other two regular coordinates to \(1/2\). The sink
coordinate is zero. For \(p_1=(1+\epsilon,1/2,1/2)\),

$$
d(0,p_1)^2=\frac12+\epsilon+\frac34\epsilon^2,
\qquad
d(p_i,p_j)^2=\frac{(1+2\epsilon)^2}{2}\quad(i\ne j).
\tag{E4-M}
$$

Thus for every \(\beta>1/\sqrt2\), choose \(\epsilon>0\) small enough
that both the initial move to \(p_i\) and every switch between distinct
\(p_i\)'s are feasible.

**Proposition.** In the E=4 instance with \((C_1,C_2,C_3,C_4)=(50,50,50,30)\),
\(E_S=20\), \(K=1\), \(T=170\), \(\delta=0\), and uniform prior,

$$
V_A(H)=60,\qquad V_R(H)=20,
\qquad H\ge3,\quad \beta>1/\sqrt2.
\tag{E4-V}
$$

At the first post-initial round, route at \(p_1\). World 1 gives admitted
vector \((50,50,50,20)\) and zero overflow. Worlds 2 and 3 share admitted
vector \((0,50,50,30)\), each with overflow 40. If the observation identifies
world 1, hold \(p_1\). On the remaining pair, route at \(p_2\): world 2
has zero overflow, while world 3 has admitted vector \((50,0,50,30)\) and
overflow 40. This identifies the world; hold the corresponding \(p_i\)
thereafter, moving from \(p_2\) to \(p_3\) only in world 3. The expected
post-initial overflow is

$$
\frac{80}{3}+\frac23\cdot20=40,
$$

so total expected overflow is 60. The unrestricted Bellman certificate in
the matched-comparator note gives \(V_A(H)\ge60\), proving equality.
Requested feedback identifies the world at the initial round and reaches
its zero-overflow \(p_i\) next, so its value is 20.

The points \(p_i\) lie in the same routing cells as the canonical singleton
probe representatives \((1+\epsilon,0,0)\) and their permutations. Those
canonical representatives have origin distance \((1+\epsilon)\sqrt3/2\),
whereas (E4-M) approaches \(1/\sqrt2\). This is a concrete example of why a
cell label is not a movement state: pressure placement within the same
outcome cell changes which future tests are reachable. It is an exact
geometric refinement of the MoE instance, not a separation from the
continuous metric-constrained polyhedral testing benchmark.

**Fixed-representative comparison.** In the E=4 case, every nonempty fixed
canonical representative \(x(P)=a(\mathbf1_P,0)\), \(a>1\), has origin
distance at least \(a\sqrt3/2>\sqrt3/2\). Therefore, for

$$
\frac1{\sqrt2}<\beta<\frac{\sqrt3}{2},
\tag{E4-B}
$$

the controller restricted to those fixed representatives cannot leave
\(P=\varnothing\) from the initial state. Its admitted value is \(20H\).
The continuous-pressure policy above has value 60 for \(H\ge3\), so for
\(H\ge4\) it strictly improves on that fixed-representative restriction.
This is a within-cell placement effect, not a stronger information
partition: each \(p_i\) induces the same singleton-test outcome partition
as its canonical representative. Consequently, it is an ablation result
about retaining the continuous action location, not a separation from
adaptive testing that allows continuous metric test locations.

## 5. Exact continuous-state Bellman recursion

Let \(b\in\Delta(\mathcal W)\) be the posterior immediately before routing
at round \(t\), and let \(q\in F\) be the current pressure. For each
admitted output \(o\), define

$$
p_{t,o}(b,F)=\sum_{w:g^A_{w,t}(F)=o}b_w,
\qquad
b^{t,o}_w=\frac{b_w\mathbf1\{g^A_{w,t}(F)=o\}}{p_{t,o}(b,F)}.
$$

The exact next-pressure feasible set is

$$
\mathcal R(q)=\left\{q'\in\mathcal Q:
\left\|P_0\left(q'-(1-\delta)q\right)\right\|_2
\le\eta\gamma B\right\}.
$$

With \(V_H(b,q)=0\), the optimal admitted-feedback value satisfies

$$
V_t(b,q)=\sum_{o:p_{t,o}>0}p_{t,o}(b,F)
\left[
KT-\mathbf1^\top o+
\inf_{q'\in\mathcal R(q)}V_{t+1}(b^{t,o},q')
\right].
\tag{FC-DP}
$$

The infimum is taken separately after each observation because the controller
may select its next pressure from the observed output. Equivalently, inside
each infimum one may decompose the feasible set by destination face:

$$
\mathcal R(q)=\bigcup_{F'\in\mathcal F}(F'\cap\mathcal R(q)).
$$

The continuous point \(q'\) must remain in the value-function argument.
This equation is the existing belief-pressure dynamic program specialized
using the fact that the router outcome map is piecewise constant. It handles
all causal deterministic policies; randomized policies cannot improve an
expected-cost infimum. Tie faces are included, so the deterministic tie rule
is part of the labeled arrangement, not a measure-zero omission.

## 6. What this establishes and what remains to compute

The arrangement makes the finite-world routing problem piecewise constant,
but does not make its movement-constrained control problem a finite graph.
An exact numerical solution for a specified \(\beta\) would need to optimize
over the intersections \(F'\cap\mathcal R(q)\) while preserving the
continuous \(q\) coordinate. A minimum-distance matrix between faces is
insufficient: it records whether *some* pair of pressures can transition,
not which next faces are reachable from the actual pressure selected by the
policy.

This full-pressure problem still has an exact reduction to
metric-constrained polyhedral active testing: use the same gauge action
space, arrangement faces, output labels, costs, and transition relation.
Thus solving (FC-DP) for one fixed MoE instance gives an exact MoE
application/value calculation, not a separation from that benchmark. The
existing exact Top-K-to-polyhedral simulation applies without discretizing
pressure.

### Status of the former fixed-instance gate

The earlier proposed gate—searching for a noncanonical E=4 pressure that
beats the fixed subset-probe representatives—was a valid instance-analysis
question, but it is **not** a novelty gate. Even an exact solution of this
continuous-state Bellman problem would be an exact value calculation for one
instance and would transfer to B1 by the same pressure space, arrangement
labels, metric, transition relation, and costs. Its result could be retained
as an application, but cannot establish a control-limitation separation.

Accordingly, do not spend the next research effort filling the remaining
H≥5/small-movement table or refining grids for this instance. The one
class-level go/no-go attempt and its decision are recorded in
[`phase1_class_level_go_no_go_2026-10-17.md`](phase1_class_level_go_no_go_2026-10-17.md).
No parameter sweep, approximation, or experiment was run for this note.

## 7. Literature boundary

Movement-constrained active hypothesis testing predates this project.
Atanasov et al. formulate active M-ary testing for a mobile depth sensor,
include physical movement and observation costs, and solve a belief-state
planning problem ([ICRA 2013 paper](https://natanaso.github.io/ref/Atanasov_Sankaran_ActiveObjectRecognition_ICRA13.pdf)).
Their observation model is viewpoint-dependent and noisy, and their terminal
loss is classification loss; those differences leave room for an exact
capacity-clipping/overflow analysis, but do not make the generic moving-test
Bellman structure new. Metric movement also appears in online learning under
different feedback and regret objectives ([Koren, Livni, and Mansour, COLT
2017](https://proceedings.mlr.press/v65/koren17a.html)). These are scope
neighbors; novelty requires the family-level quantitative distinction in
item 3 above.

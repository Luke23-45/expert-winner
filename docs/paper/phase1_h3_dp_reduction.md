# Phase 1: finite-horizon controller DP and reduction audit

**Status:** exact model reduction and bounds for a finite static-world
problem; no new lower bound claimed.
**Branch:** feat/research-censored-feedback.
**Companion:** [phase1_h3_direction.md](phase1_h3_direction.md).
**Purpose:** make the H≥3 controller problem explicit enough to test
whether its proposed contribution survives reduction to active
hypothesis testing with outcome-dependent costs.

---

## 1. Scope and assumptions

Fix a finite set of hidden, static environments
\(\mathcal W=\{1,\dots,N\}\) with prior \(b\in\Delta^{N-1}\).
Environment \(i\) is a fixed affinity sequence
\(\omega_i=(a^i_0,\dots,a^i_{H-1})\); it is selected once and does not
adapt to the controller. Capacities \(C\), target \(\mu\), and plant
parameters \((K,T,\eta,\gamma,\delta,B)\) are known. At round \(t\),
the gauge-fixed pressure is \(q_t\in\mathcal Q\), and the router and
admission produce

\[
R^i_t(q_t),\qquad A^i_t(q_t)=\min(R^i_t(q_t),C),\qquad
J^i_t(q_t)=R^i_t(q_t)-A^i_t(q_t).
\]

The admitted controller observes \(A_t\), knows the prior, and may use
the full history. Its update is
\(\epsilon_t\in U_B=\{\epsilon\in\mathbf1^\perp:\|\epsilon\|_2\le B\}\),
with
\[
F(q,\epsilon)=\Pi_g((1-\delta)q+\eta\gamma\epsilon).
\]
The objective is raw cumulative overflow
\(\sum_{t=0}^{H-1}\|J_t\|_1\); normalization by \(HKT\) can be applied
after solving the finite-horizon problem.

Static environments are intentional here. If affinities evolve
stochastically or adversarially, the hidden state and transition kernel
must be added; the recursion below does not cover that extension.

## 2. Exact belief-state Bellman recursion

Let \(b\) be the posterior over environments immediately before the
current batch is routed, and let \(q\) be the current pressure. At
round \(t\), define the deterministic admitted observation map
\[
g^A_{i,t}(q)=A^i_t(q)
\]
and immediate overflow
\[
c_{i,t}(q)=\|J^i_t(q)\|_1
=KT-\mathbf1^\top g^A_{i,t}(q).
\]
The last identity follows from \(\mathbf1^\top R=KT\); thus the
current scalar cost is known from the admitted vector even though the
expert-wise rejected-load allocation is not.

For an admitted observation \(o\), define its probability and posterior
at time \(t\) by
\[
p^A_{t,o}(b,q)=\sum_{i:g^A_{i,t}(q)=o}b_i,\qquad
b^{A,t,o}_i=
\frac{b_i\mathbf1\{g^A_{i,t}(q)=o\}}{p^A_{t,o}(b,q)}
\quad\text{when }p^A_{t,o}(b,q)>0.
\]
The posterior is a version-space update: under deterministic fixed
worlds it removes exactly the hypotheses inconsistent with the
observed admitted vector.

Let \(V^A_t(b,q)\) be the optimal expected overflow from rounds \(t\)
through \(H-1\), with terminal value \(V^A_H(b,q)=0\). The recursion is
\[
V^A_t(b,q)=
\sum_{o:p^A_{t,o}(b,q)>0}p^A_{t,o}(b,q)\left[
KT-\mathbf1^\top o+
\inf_{\epsilon\in U_B}
V^A_{t+1}\!\left(b^{A,t,o},F(q,\epsilon)\right)
\right],
\quad t=H-1,\ldots,0.
\tag{DP-A}
\]
The infimum is inside the observation sum because the controller sees
\(o\) before choosing its update. In this static finite-world model,
\((b,q)\) is sufficient: the posterior contains all information in the
admitted observation history about the hidden environment, while \(q\)
is the plant state needed for future feasibility and routing. Private
randomization cannot improve the infimum of expected cost over pure
actions; if an infimum is not attained, the equation is interpreted as
an infimum over admissible policies.

For requested feedback, define \(g^R_{i,t}(q)=R^i_t(q)\), and define
\[
p^R_{t,r}(b,q)=\sum_{i:g^R_{i,t}(q)=r}b_i,\qquad
b^{R,t,r}_i=
\frac{b_i\mathbf1\{g^R_{i,t}(q)=r\}}{p^R_{t,r}(b,q)}
\quad\text{when }p^R_{t,r}(b,q)>0.
\]
Then
\[
V^R_t(b,q)=
\sum_{r:p^R_{t,r}(b,q)>0}p^R_{t,r}(b,q)\left[
KT-\mathbf1^\top\min(r,C)+
\inf_{\epsilon\in U_B}
V^R_{t+1}\!\left(b^{R,t,r},F(q,\epsilon)\right)
\right],
\quad V^R_H=0.
\tag{DP-R}
\]
The minimum is coordinatewise. Comparing (DP-A) and (DP-R) isolates
information: plant, action set, physical cost, and initial condition
stay fixed. In (DP-R), current cost is computed from the observed
request vector and known capacity; it is not \(KT-\mathbf1^\top r\),
which would incorrectly be zero.

## 3. Pressure-update feasibility as a state constraint

The gauge projection can be removed from the action constraint exactly.
For \(q,q'\in\mathcal Q\), there exists an update
\(\epsilon\in U_B\) satisfying \(q'=F(q,\epsilon)\) if and only if
\[
\left\|P_0\!\left(q'-(1-\delta)q\right)\right\|_2
\le \eta\gamma B,
\tag{Reach}
\]
where \(P_0(x)=x-\operatorname{mean}(x)\mathbf1\).

*Proof.* Since \(q'=\Pi_g(z)\), \(P_0(q')=P_0(z)\). Hence any feasible
update must satisfy
\[
P_0(q')=(1-\delta)P_0(q)+\eta\gamma\epsilon,
\]
which gives (Reach) because \(P_0(\epsilon)=\epsilon\). Conversely, if
(Reach) holds, set
\(\epsilon=[P_0(q')-(1-\delta)P_0(q)]/(\eta\gamma)\). It lies in
\(\mathbf1^\perp\), obeys the norm bound, and the two vectors
\((1-\delta)q+\eta\gamma\epsilon\) and \(q'\) differ only by a common
mode. Their gauge projections are therefore equal. \(\square\)

Thus the pressure process is not an unconstrained sequence of tests:
the allowed next test pressure depends on the current pressure through
(Reach). This state constraint is the precise dynamical remainder that
must be retained in any reduction or novelty argument.

## 4. Exact connection to adaptive testing

For fixed static worlds, a pressure state \(q\) is a test:

| Control model | Adaptive-testing interpretation |
|---|---|
| Hidden affinity world \(i\) | Unknown hypothesis \(i\) |
| Choose pressure \(q\) through a feasible update | Select an available test |
| Observe \(A^i(q)\) | Observe the test outcome |
| Pay \(KT-\mathbf1^\top A^i(q)\) | Outcome-dependent test cost |
| Update posterior by consistency | Eliminate inconsistent hypotheses |
| Reachability constraint (Reach) | State-dependent constraint on the next test |

The cost is a function of the observed outcome, not an unobserved
penalty: \(c(o)=KT-\mathbf1^\top o\). This makes the probe construction
a deterministic adaptive-testing problem with outcome-dependent test
costs and a pressure-induced constraint on the test sequence. The
general active-learning literature already treats adaptive test
selection and nonuniform costs; outcome-dependent query costs have
also been studied explicitly. Relevant primary sources include
[Golovin, Krause & Ray, *Near-Optimal Bayesian Active Learning with
Noisy Observations*](https://arxiv.org/abs/1010.3091) and
[Sabato, Sarwate & Srebro, *Auditing: Active Learning with
Outcome-Dependent Query Costs*](https://arxiv.org/abs/1306.2347).

This is an exact modeling connection, not a claim that those papers
already solve (DP-A). A reduction attack has to ask whether the
pressure-constrained test family and its outcome/cost maps admit a
known reduction, and whether a proposed theorem uses a property that
survives no such reduction. Merely deriving a search lower bound for
the E-world probe example is not enough.

### 4.1 Exact all-pressure observation map for the E=3 construction

For \(E=3,K=1\), write the gauge-invariant relative pressures as
\[
x=\gamma(q_1-q_3),\qquad y=\gamma(q_2-q_3).
\]
Every \((x,y)\in\mathbb R^2\) corresponds to one gauge-fixed
\(q\in\mathcal Q\), so this parameterization covers every pressure
state. Let \(d_{1L},d_{1H},d_{2L},d_{2H}\in\{1,2,3\}\) be the
deterministic winning expert, with lower expert index winning ties,
for the following score triples after subtracting the common sink
pressure:
\[
\begin{array}{c|c}
\text{token type}&\text{scores for experts }(1,2,3)\\ \hline
L_1&(m-x,\ -M-y,\ 0)\\
H_1&(M-x,\ -M-y,\ 0)\\
L_2&(-M-x,\ m-y,\ 0)\\
H_2&(-M-x,\ M-y,\ 0).
\end{array}
\tag{Scores}
\]
Here \(L_e\) is a low-margin token with preferred expert \(e\);
\(H_e\) is the high-margin baseline token. The full request vectors at
every pressure—not just the intended probes—are exactly
\[
R^1(x,y)=C e_{d_{1H}}+E_S e_{d_{1L}}+C e_{d_{2L}},
\qquad
R^2(x,y)=C e_{d_{1L}}+C e_{d_{2H}}+E_S e_{d_{2L}},
\tag{Requests}
\]
where \(e_j\) is the \(j\)-th standard basis vector. Admission and cost
then follow by
\[
A^i(x,y)=\min\{R^i(x,y),(C,C,C_{\rm sink})\},\qquad
c_i(x,y)=2C+E_S-\mathbf1^\top A^i(x,y).
\tag{Observed outcome}
\]

The observation map is piecewise constant. Its cell boundaries are
contained in the pairwise score-equality lines
\[
x=m,\ x=M,\ x=-M;\quad y=-M,\ y=m,\ y=M;
\quad x-y=m+M,\ x-y=2M;\quad
y-x=m+M,\ y-x=2M.
\tag{Cells}
\]
The score triples and fixed tie priority define behavior on the
boundaries exactly. Equations (Scores)–(Observed outcome) therefore
give a finite, exact partition of the full pressure plane into test
outcomes and costs. To obtain the action-feasible partition at a
particular round, intersect these cells with the reachable pressure
set generated by (Reach) from \(q_0\).

In centered coordinates \(u=P_0(q)\), routing uses
\(x=\gamma(u_1-u_3)\), \(y=\gamma(u_2-u_3)\), and the reachable-state
transition is the Euclidean ball constraint
\[
\|u'-(1-\delta)u\|_2\le\eta\gamma B,\qquad \mathbf1^\top u'=0.
\]
This is equivalent to (Reach), with the gauge-fixed pressure recovered
as \(q'=u'-\min_e u'_e\,\mathbf1\). Thus all-pressure observation
cells and bounded-update reachability are both explicit for E=3.

## 5. Three-round instance: bounds, not a lower bound

Use \(E=3,K=1\), capacities \((C,C,C_{\rm sink})\), batch size
\(T=2C+E_S\), two equally likely static worlds, \(q_0=0\), and the
explicit token affinities in §2.1 of the companion note. Assume
\[
E_S<C_{\rm sink}<C-E_S/2,\quad
0<m<M,\quad \delta=0,\quad
B\ge\frac{\sqrt2M}{\eta\gamma^2}.
\]
At round zero the requested counts are \((C+E_S,C,0)\) and
\((C,C+E_S,0)\), respectively, while both worlds yield
\(A_0=(C,C,0)\). The unavoidable first-round overflow is \(E_S\).

The requested policy sees \(R_0\), identifies the world, and reaches
the corresponding sweet spot before round one. For the equal prior and
initial state \(q_0=0\), its value is
\[
V^R(H)=E_S\qquad(H\ge2).
\]
The equality follows because the first-round cost is fixed at \(E_S\)
and all later costs can be zero.

The admitted policy has at least the same value and at most the cost of
either the no-probe or one-probe policy. The one-probe policy and its
exact expected raw cost are proved in
[phase1_h3_direction.md](phase1_h3_direction.md):
\[
E_S+\frac{E_S+C-C_{\rm sink}}2\qquad(H\ge3).
\]
Writing \(V^A(H)\) for the admitted value from \(q_0=0\), the rigorous
bounds currently established for this instance
are
\[
E_S\le V^A(H)\le
\min\!\left\{H E_S,\ E_S+\frac{E_S+C-C_{\rm sink}}2\right\}.
\tag{Bounds}
\]
No equality or lower bound beyond \(V^A(H)\ge V^R(H)\) is established.
In particular, (Bounds) does not prove the conjectured
\(\Omega(E E_S)\) lower bound for the E-world family.

## 6. What would count as a surviving MoE theorem

The Bellman equation makes the missing result precise. A viable
theorem must give a sharp property of the induced test-control system
that is not inherited from a generic adaptive-testing theorem. Examples
of possible load-bearing properties (all still open) are:

1. A characterization of which hypothesis partitions
   \(i\mapsto A^i(q)\) can be implemented under (Reach), tied to Top-K
   score cells and heterogeneous capacities.
2. A tight value bound showing how gauge geometry or pressure
   switching limits information-per-overflow in a way not captured by
   generic outcome-dependent-cost test complexity.
3. A matching optimal strategy and lower bound for the MoE-induced
   test family, with a demonstrated separation from the best bound for
   the unrestricted test problem.

If the desired result follows unchanged after replacing each pressure
state by an abstract test with the same outcome, cost, and transition
graph, then the contribution is a constrained adaptive-testing result
with an MoE application. That may still be publishable, but it is not
evidence for the stronger claim that Top-K/gauge dynamics create a
distinct control-theoretic limitation.

## 7. Next proof task

The full \(E=3\) observation partition and pressure reachability are now
explicit in §4.1. Next solve (DP-A) or obtain certified upper/lower
bounds for small \((H,B,\delta)\) regimes, using the exact test cells
and transitions. Then use the resulting test tree to attack the
reduction:

- If every useful observation tree is equivalent to outcome-dependent
  adaptive testing with the same cost and state constraint, state that
  theorem at the right level and stop claiming a new generic lower
  bound.
- If Top-K and gauge impose a sharp additional restriction, isolate it
  as a lemma first, then prove the value gap from that lemma.
- Do not run parameter sweeps as evidence for the theorem until the
  theorem statement and reduction boundary are fixed.

No experiments were run for this note.

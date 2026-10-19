\documentclass{article}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{geometry}

\geometry{margin=1in}

\newtheorem{theorem}{Theorem}
\newtheorem{proposition}{Proposition}
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}
\newtheorem{remark}{Remark}

\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\one}{\mathbf{1}}
\newcommand{\TopK}{\operatorname{TopK}}
\newcommand{\sgn}{\operatorname{sign}}
\newcommand{\Proj}{\Pi}
\newcommand{\gproj}{\Pi_{\mathrm{g}}}
\newcommand{\relu}[1]{\left[#1\right]_{+}}

\title{
Requested-Demand Feedback for Capacity-Constrained Sparse Routing:\\
Corrected Formal Theory on the Gauge Quotient
}

\author{}
\date{}

\begin{document}

\maketitle

\section{Objects and notation}

Let there be
\[
E \in \mathbb{N}
\]
routed experts and let each token make
\[
K \in \{1,\dots,E\}
\]
routing requests. Consider a batch of
\[
T \in \mathbb{N}
\]
tokens. Write
\[
[E] := \{1,\dots,E\},
\qquad
\one \in \R^E
\]
for the all-ones vector.

For token \(t \in \{1,\dots,T\}\), let
\[
a_t \in \R^E
\]
be the raw affinity vector. Let
\[
q \in \R_+^E
\]
be the pressure vector and let
\[
\gamma > 0
\]
be a scalar pressure gain. The pressured score is
\[
s_{t,e}(q)
=
a_{t,e} - \gamma q_e.
\]

For a score vector \(s \in \R^E\), define the hard Top-\(K\) set-valued map
\[
\TopK_K(s)
:=
\arg\max_{\substack{S \subseteq [E] \\ |S| = K}}
\sum_{e \in S} s_e.
\]
A tie-breaking rule selects one element of \(\TopK_K(s)\). All statements below hold for any fixed tie-breaking rule; at ties, any active Top-\(K\) subset gives a valid subgradient.

For token \(t\), let
\[
I_t(q) \in \TopK_K(s_t(q))
\]
be the selected set. Define the requested indicator
\[
r_{t,e}(q)
:=
\mathbf{1}\{e \in I_t(q)\}.
\]
Then
\[
\sum_{e=1}^E r_{t,e}(q) = K.
\]

The batch requested load is
\[
R_e(q)
:=
\sum_{t=1}^T r_{t,e}(q),
\qquad
e \in [E].
\]
It satisfies the conservation law
\[
\sum_{e=1}^E R_e(q)
=
K T.
\]

Let
\[
C \in \mathbb{N}_0^E,
\qquad
\mathbb{N}_0 := \{0,1,2,\dots\}
\]
be integer expert capacities. Under canonical slot-wise capacity admission,
\[
A_e(q)
:=
\min\{R_e(q), C_e\},
\]
and the rejected load is
\[
J_e(q)
:=
R_e(q) - A_e(q)
=
\relu{R_e(q) - C_e}.
\]
More generally, any admission rule satisfying
\[
A_e(q) \le R_e(q),
\qquad
A_e(q) \le C_e
\]
only strengthens the censoring statements below.

Let
\[
\mu \in \Delta^{E-1}
:=
\left\{
p \in \R_+^E : \sum_{e=1}^E p_e = 1
\right\}
\]
be the target requested distribution. The uniform target is
\[
\mu_e = \frac{1}{E}.
\]

Since each token can request a given expert at most once,
\[
R_e(q) \le T,
\qquad
\frac{R_e(q)}{K T} \le \frac{1}{K}.
\]
Hence any exactly matched requested target must satisfy the necessary bound
\[
\mu_e \le \frac{1}{K}.
\]
For exact matching on a finite batch, one also needs \(K T\mu_e\in\mathbb{N}_0\) for every \(e\). The uniform target satisfies the coordinate bound because \(K \le E\). These conditions are necessary, but do not guarantee that a particular finite batch and fixed affinity matrix can realize \(\mu\) under hard Top-\(K\) routing.

\section{Gauge quotient and nonnegative pressure dynamics}

Because the score vector is invariant under common shifts of \(q\),
\[
\TopK_K(a_t - \gamma(q + c\one))
=
\TopK_K(a_t - \gamma q),
\qquad
\forall c \in \R,
\]
the pressure state is naturally defined on the quotient space
\[
\R^E / \operatorname{span}\{\one\}.
\]

We use the canonical nonnegative gauge representative
\[
\mathcal{Q}
:=
\left\{
q \in \R_+^E : \min_{e} q_e = 0
\right\}.
\]
Define the gauge projection
\[
\gproj : \R^E \to \mathcal{Q},
\qquad
\gproj(z)
:=
z - \left(\min_{i} z_i\right)\one.
\]
This map satisfies
\[
\gproj(z + c\one)
=
\gproj(z),
\qquad
\forall c \in \R.
\]

\begin{remark}
The map \(\gproj\) is not the Euclidean projection onto the nonconvex set \(\mathcal{Q}\). It is the canonical gauge representative used because routing depends only on pressure differences. The nonnegative boundary is represented by the faces
\[
\{q \in \mathcal{Q} : q_e = 0\}.
\]
Thus the update is a step on the gauge quotient followed by gauge normalization, not Euclidean projection onto a convex feasible set.
\end{remark}

Let
\[
\delta \in [0,1)
\]
be an optional pressure decay and let
\[
\eta > 0
\]
be the step size. Given a feedback signal
\[
\varepsilon(q) \in \R^E,
\]
the gauge-quotient pressure dynamics are
\[
q^{+}
=
\gproj\!\left(
(1-\delta)q + \eta\gamma\,\varepsilon(q)
\right).
\]
Since \(\gproj(z+c\one)=\gproj(z)\), adding any common-mode component to \(\varepsilon(q)\) leaves this update unchanged. Equivalently, the gauge dynamics depend only on the centered component of the feedback.

\begin{lemma}[Boundary exit and re-entry]
Let
\[
z_e := (1-\delta)q_e + \eta\gamma\,\varepsilon_e(q),
\qquad
m := \min_j z_j.
\]
Then
\[
q_e^{+}
=
z_e - m.
\]
Hence
\[
q_e^{+} > 0
\iff
z_e > m,
\]
and
\[
q_e^{+} = 0
\iff
z_e = m.
\]
In particular, an expert at the boundary, \(q_e = 0\), re-enters with positive pressure if and only if
\[
\eta\gamma\,\varepsilon_e(q)
>
\min_j\left((1-\delta)q_j + \eta\gamma\,\varepsilon_j(q)\right).
\]
\end{lemma}

\begin{proof}
By definition,
\[
\gproj(z)
=
z - m\one.
\]
Thus
\[
q_e^{+}
=
z_e - m.
\]
Since \(m = \min_j z_j\), we have \(q_e^{+} \ge 0\) for all \(e\), and \(q_e^{+} = 0\) exactly when \(z_e = m\). The re-entry condition follows by substituting \(q_e = 0\).
\end{proof}

\section{Requested and admitted feedback signals}

Define the requested-demand feedback error
\[
\varepsilon^{\mathrm{R}}_e(q)
:=
\frac{R_e(q)}{K T}
-
\mu_e.
\]
Define the admitted-load feedback error
\[
\varepsilon^{\mathrm{A}}_e(q)
:=
\frac{A_e(q)}{K T}
-
\mu_e.
\]

\begin{proposition}[Mass conservation and mass loss]
For every \(q\),
\[
\sum_{e=1}^E \varepsilon^{\mathrm{R}}_e(q)
=
0.
\]
For admitted feedback,
\[
\sum_{e=1}^E \varepsilon^{\mathrm{A}}_e(q)
=
\frac{\sum_{e=1}^E A_e(q)}{K T}
-
1
\le 0.
\]
If any requested assignment is rejected, then
\[
\sum_{e=1}^E \varepsilon^{\mathrm{A}}_e(q)
<
0.
\]
\end{proposition}

\begin{proof}
Since \(\sum_e R_e = K T\) and \(\sum_e \mu_e = 1\),
\[
\sum_e \varepsilon^{\mathrm{R}}_e
=
\frac{K T}{K T}
-
1
=
0.
\]
Similarly,
\[
\sum_e \varepsilon^{\mathrm{A}}_e
=
\frac{\sum_e A_e}{K T}
-
1.
\]
Because \(A_e \le R_e\) and \(\sum_e R_e = K T\),
\[
\sum_e A_e \le K T.
\]
The inequality is strict if any assignment is rejected.
\end{proof}

\section{Absolute reflected dynamics and no interior equilibrium}

Before passing to the gauge quotient, consider the absolute reflected update on the nonnegative orthant:
\[
\widehat{U}_{\varepsilon}(q)
:=
\relu{(1-\delta)q + \eta\gamma\,\varepsilon(q)}.
\]

\begin{proposition}[No interior fixed point under admitted feedback]
Suppose \(q \in \R_{++}^E\) is a fixed point of
\[
q
=
\relu{(1-\delta)q + \eta\gamma\,\varepsilon(q)}.
\]
Then
\[
\delta q_e
=
\eta\gamma\,\varepsilon_e(q),
\qquad
e \in [E].
\]
Consequently,
\[
\delta \sum_{e=1}^E q_e
=
\eta\gamma \sum_{e=1}^E \varepsilon_e(q).
\]
If \(\varepsilon = \varepsilon^{\mathrm{A}}\) and any assignment is rejected, then
\[
\sum_e \varepsilon^{\mathrm{A}}_e(q) < 0,
\]
which is impossible because \(q_e > 0\) and \(\delta \ge 0\). Hence there is no strictly positive fixed point under admitted-load feedback whenever rejection occurs.
\end{proposition}

\begin{proof}
If \(q_e > 0\), the ReLU is inactive at coordinate \(e\), so
\[
q_e
=
(1-\delta)q_e + \eta\gamma \varepsilon_e(q).
\]
Thus
\[
\delta q_e
=
\eta\gamma \varepsilon_e(q).
\]
Summing over \(e\) gives
\[
\delta \sum_e q_e
=
\eta\gamma \sum_e \varepsilon_e(q).
\]
The left-hand side is nonnegative. Under admitted feedback with rejection,
\[
\sum_e \varepsilon^{\mathrm{A}}_e(q) < 0,
\]
a contradiction.
\end{proof}

\begin{remark}
This theorem is correct for the absolute reflected dynamics without gauge fixing. However, routing depends only on the gauge class of \(q\). Therefore the more important question is whether admitted feedback fails after quotienting out the common mode. The next section resolves that question.
\end{remark}

\section{Failure of admitted feedback in relative gauge dynamics}

The negative total mass of \(\varepsilon^{\mathrm{A}}\) is removed by the gauge projection. Therefore the relevant failure cannot be only negative total mass. The correct failure is loss of demand information under capacity saturation.

Assume uniform capacities
\[
C_e = c \frac{K T}{E},
\qquad
c > 0,
\]
with \(c K T/E \in \mathbb{N}_0\), and uniform target
\[
\mu_e = \frac{1}{E}.
\]

\begin{theorem}[Saturation freeze under admitted feedback]
Suppose every expert is saturated:
\[
R_e(q) \ge C_e,
\qquad
\forall e.
\]
Then necessarily \(c\le1\). If \(c=1\), then \(R_e(q)=C_e=K T/E\) for every expert, so the requested load is already balanced. The nontrivial saturation-freeze case is therefore \(c<1\).
Then under canonical admission,
\[
A_e(q) = C_e,
\qquad
\forall e.
\]
Therefore
\[
\varepsilon^{\mathrm{A}}_e(q)
=
\frac{C_e}{K T}
-
\frac{1}{E}
=
\frac{c-1}{E},
\qquad
\forall e.
\]
Thus \(\varepsilon^{\mathrm{A}}(q)\) is a constant vector. The gauge update becomes
\[
q^{+}
=
\gproj\!\left(
(1-\delta)q + \eta\gamma \frac{c-1}{E}\one
\right)
=
(1-\delta)q.
\]
Hence:
\begin{enumerate}
\item if \(\delta = 0\), admitted feedback induces no relative pressure change;
\item if \(\delta > 0\), each update scales the existing relative pressure by \(1-\delta\); if global saturation persists, the pressure converges geometrically to zero.
\end{enumerate}
While global saturation persists, admitted-load feedback cannot correct an imbalance in requested demand.
\end{theorem}

\begin{proof}
Summing \(R_e(q)\ge C_e=c K T/E\) over \(e\) gives \(K T\ge c K T\), hence \(c\le1\). If \(c=1\), then the nonnegative values \(R_e(q)-C_e\) have zero sum, so each is zero.

Since \(R_e \ge C_e\), canonical admission gives
\[
A_e = \min\{R_e,C_e\} = C_e.
\]
With uniform capacity,
\[
\frac{A_e}{K T}
=
\frac{c}{E}.
\]
Therefore
\[
\varepsilon^{\mathrm{A}}_e
=
\frac{c}{E}
-
\frac{1}{E}
=
\frac{c-1}{E}.
\]
Let
\[
\alpha := \frac{c-1}{E}.
\]
Then
\[
(1-\delta)q + \eta\gamma \varepsilon^{\mathrm{A}}
=
(1-\delta)q + \eta\gamma \alpha \one.
\]
Because \(q \in \mathcal{Q}\), \(\min_e q_e = 0\), so
\[
\min_e\left((1-\delta)q_e + \eta\gamma \alpha\right)
=
\eta\gamma \alpha.
\]
Applying the gauge projection,
\[
q^{+}
=
(1-\delta)q + \eta\gamma\alpha\one - \eta\gamma\alpha\one
=
(1-\delta)q.
\]
The conclusions follow.
\end{proof}

\begin{proposition}[Information loss under saturation]
Under canonical admission,
\[
A_e(q)
=
\min\{R_e(q), C_e\}.
\]
Therefore, for any two requested load vectors \(R\) and \(\widetilde R\) satisfying
\[
\min\{R_e,C_e\}
=
\min\{\widetilde R_e,C_e\},
\qquad
\forall e,
\]
the admitted feedback signals coincide:
\[
\varepsilon^{\mathrm{A}}(R)
=
\varepsilon^{\mathrm{A}}(\widetilde R).
\]
In particular, on the saturated region
\[
R_e \ge C_e,
\]
the admitted feedback coordinate
\[
\varepsilon^{\mathrm{A}}_e
=
\frac{C_e}{K T}
-
\mu_e
\]
is independent of the actual requested load \(R_e\). Thus excess demand
\[
R_e - C_e
\]
is invisible to admitted-load feedback.
\end{proposition}

\begin{proof}
The map
\[
R_e \mapsto A_e = \min\{R_e,C_e\}
\]
is constant on \([C_e,\infty)\). Therefore any two requested loads that differ only by increasing already-saturated coordinates produce the same admitted load and hence the same admitted feedback.
\end{proof}

\begin{corollary}[Sign reversal under censoring]
Suppose for some expert \(e\),
\[
\frac{R_e(q)}{K T} > \mu_e,
\]
but
\[
\frac{A_e(q)}{K T} < \mu_e.
\]
Then
\[
\varepsilon^{\mathrm{R}}_e(q) > 0,
\qquad
\varepsilon^{\mathrm{A}}_e(q) < 0.
\]
Thus requested feedback correctly increases pressure on an over-demanded expert, while admitted feedback decreases it.
\end{corollary}

\begin{proof}
Immediate from the definitions of \(\varepsilon^{\mathrm{R}}\) and \(\varepsilon^{\mathrm{A}}\).
\end{proof}

\section{Requested Top-\(K\) feedback as a convex subgradient}

We now show that requested Top-\(K\) feedback is not a heuristic. It is a subgradient of a convex Top-\(K\) potential.

For each token \(t\), define the hard Top-\(K\) potential
\[
\Phi_t(q)
:=
\frac{1}{K}
\max_{\substack{S \subseteq [E] \\ |S| = K}}
\sum_{e \in S}
\left(
a_{t,e} - \gamma q_e
\right).
\]
Define the batch potential
\[
H(q)
:=
\gamma \mu^{\top} q
+
\frac{1}{T}
\sum_{t=1}^T
\Phi_t(q).
\]

\begin{proposition}[Hard Top-\(K\) subgradient]
For each token \(t\), if \(I_t(q)\) is a selected Top-\(K\) set, then
\[
-\frac{\gamma}{K} r_t(q)
\in
\partial \Phi_t(q).
\]
Therefore
\[
\gamma
\left(
\mu
-
\frac{R(q)}{K T}
\right)
\in
\partial H(q).
\]
Consequently, the equivalence-class update
\[
[q]^+
=
\left[q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\mu
\right)
\right]
\]
is a quotient subgradient step for \(H\). Its canonical nonnegative representative is
\[
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\mu
\right)
\right)
\]
obtained by gauge normalization.
\end{proposition}

\begin{proof}
For fixed \(t\), the function
\[
q
\mapsto
\frac{1}{K}
\sum_{e \in S}
(a_{t,e} - \gamma q_e)
\]
is affine for each subset \(S\). The maximum of affine functions is convex. If \(I_t(q)\) is an active maximizer, then a subgradient of \(\Phi_t\) at \(q\) is
\[
\nabla_q
\left[
\frac{1}{K}
\sum_{e \in I_t(q)}
(a_{t,e} - \gamma q_e)
\right]
=
-\frac{\gamma}{K} r_t(q).
\]
Averaging over tokens gives
\[
\partial
\left[
\frac{1}{T}
\sum_t \Phi_t(q)
\right]
\ni
-\frac{\gamma}{K T} R(q).
\]
The linear term contributes \(\gamma \mu\). Hence
\[
\partial H(q)
\ni
\gamma \mu
-
\gamma \frac{R(q)}{K T}.
\]
Subgradient descent uses
\[
q
\mapsto
q
-
\eta
\left[
\gamma \mu
-
\gamma \frac{R(q)}{K T}
\right]
=
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\mu
\right).
\]
Applying the gauge projection gives the stated update.
\end{proof}

\begin{proposition}[Gauge invariance of the hard potential]
For every \(c \in \R\),
\[
H(q + c\one)
=
H(q).
\]
Thus \(H\) is well-defined on the gauge quotient.
\end{proposition}

\begin{proof}
The linear term changes by
\[
\gamma \mu^{\top}(q + c\one)
=
\gamma \mu^{\top}q
+
\gamma c
\sum_e \mu_e
=
\gamma \mu^{\top}q
+
\gamma c.
\]
For each token,
\[
\Phi_t(q+c\one)
=
\frac{1}{K}
\max_{|S|=K}
\sum_{e \in S}
(a_{t,e} - \gamma q_e - \gamma c)
=
\Phi_t(q)
-
\gamma c,
\]
because \(|S|=K\). Therefore the token-average potential changes by \(-\gamma c\), canceling the linear term.
\end{proof}

\section{Smooth Top-\(K\) potential with correct factor-\(K\) normalization}

For theoretical analysis, define the smooth Top-\(K\) partition function
\[
Z_{t,K}(s)
:=
\sum_{\substack{S \subseteq [E] \\ |S| = K}}
\exp\!\left(
\frac{1}{\tau}
\sum_{e \in S} s_e
\right),
\qquad
\tau > 0.
\]
Define
\[
\Phi_{t,\tau}(q)
:=
\frac{\tau}{K}
\log Z_{t,K}(a_t - \gamma q).
\]
Define the smooth batch potential
\[
H_{\tau}(q)
:=
\gamma \mu^{\top}q
+
\frac{1}{T}
\sum_{t=1}^T
\Phi_{t,\tau}(q).
\]

For each token, define the Gibbs distribution over Top-\(K\) subsets:
\[
p_{t,\tau}(S;q)
:=
\frac{
\exp\!\left(
\frac{1}{\tau}
\sum_{e \in S}
(a_{t,e} - \gamma q_e)
\right)
}{
Z_{t,K}(a_t - \gamma q)
}.
\]
Define the inclusion probabilities
\[
d_{t,e}(q)
:=
\sum_{\substack{S \ni e}} p_{t,\tau}(S;q),
\]
and the normalized smooth demand
\[
\bar d_e(q)
:=
\frac{1}{T K}
\sum_{t=1}^T d_{t,e}(q).
\]
Since each subset has cardinality \(K\),
\[
\sum_{e=1}^E d_{t,e}(q) = K,
\]
and therefore
\[
\sum_{e=1}^E \bar d_e(q) = 1.
\]

\begin{proposition}[Smooth Top-\(K\) gradient]
The smooth potential \(H_{\tau}\) is convex and differentiable. Its gradient is
\[
\nabla H_{\tau}(q)
=
\gamma
\left(
\mu
-
\bar d(q)
\right).
\]
Hence the gauge-projected gradient update is
\[
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\left(
\bar d(q)
-
\mu
\right)
\right).
\]
Moreover,
\[
\Phi_{t,\tau}(q)
\to
\Phi_t(q)
\quad
\text{as }
\tau \to 0,
\]
so the smooth potentials converge pointwise to the hard Top-\(K\) potential. Away from Top-\(K\) ties, their gradients converge to the gradient associated with the unique selected subset. At ties, the limiting smooth gradients are elements of the hard subdifferential and need not coincide with the subgradient selected by an arbitrary fixed tie-breaking rule.
\end{proposition}

\begin{proof}
For fixed \(t\),
\[
\frac{\partial}{\partial q_e}
\log Z_{t,K}(a_t - \gamma q)
=
-\frac{\gamma}{\tau}
d_{t,e}(q).
\]
Therefore
\[
\frac{\partial}{\partial q_e}
\Phi_{t,\tau}(q)
=
\frac{\tau}{K}
\left(
-\frac{\gamma}{\tau}
d_{t,e}(q)
\right)
=
-\frac{\gamma}{K}
d_{t,e}(q).
\]
Averaging over tokens,
\[
\frac{\partial}{\partial q_e}
\left[
\frac{1}{T}
\sum_t \Phi_{t,\tau}(q)
\right]
=
-\gamma
\left[
\frac{1}{T K}
\sum_t d_{t,e}(q)
\right]
=
-\gamma \bar d_e(q).
\]
Adding the linear term gives
\[
\nabla H_{\tau}(q)
=
\gamma \mu
-
\gamma \bar d(q).
\]
Convexity follows because \(\log\sum \exp(\cdot)\) is convex and composition with an affine map preserves convexity. The zero-temperature limit follows from the standard identity
\[
\lim_{\tau \to 0}
\tau \log \sum_i e^{f_i/\tau}
=
\max_i f_i.
\]
The factor \(1/K\) ensures that the limiting potential is the average Top-\(K\) score and that the normalized demand sums to one.
For each token, the Gibbs distribution concentrates on the active maximizing subsets as \(\tau\to0\). If the maximizer is unique, this gives the stated gradient limit. At a tie, the limiting gradient is a convex combination of gradients of active affine pieces, and hence belongs to the hard subdifferential.
\end{proof}

\section{Capacity-constrained objective and gauge reduction}

We now derive the capacity-constrained dual objective. Consider the assignment problem
\[
\max_x \sum_{t=1}^T\sum_{e=1}^E a_{t,e}x_{t,e}
\]
subject to the per-token Top-\(K\) budgets and expert capacities. In the binary formulation,
\[
x_{t,e} \in \{0,1\},
\qquad
\sum_{e=1}^E x_{t,e} = K.
\]
The capacity constraints are
\[
\sum_{t=1}^T x_{t,e} \le C_e.
\]
The same Lagrangian dual function results if the binary token constraints are replaced by their fractional relaxation \(0\le x_{t,e}\le1\), \(\sum_e x_{t,e}=K\), since a linear function over this per-token polytope attains its maximum at a binary Top-\(K\) indicator.

A necessary condition for admitting all \(K T\) requested slots is
\[
\sum_{e=1}^E C_e \ge K T.
\]
This condition is not sufficient in general, because each token must use \(K\) distinct experts. If the condition fails, the hard-capacity assignment problem is infeasible and the pressure controller can only represent relative scarcity; aggregate shortage must be reported separately.

Introduce nonnegative dual variables \(\gamma q_e\) for the capacity constraints. The scaled Lagrangian dual function is
\[
\mathcal{L}_C(q)
:=
\gamma
\sum_{e=1}^E
\frac{C_e}{K T}
q_e
+
\frac{1}{K T}
\sum_{t=1}^T
\max_{\substack{S \subseteq [E] \\ |S| = K}}
\sum_{e \in S}
\left(
a_{t,e}
-
\gamma q_e
\right).
\]

\begin{proposition}[Capacity dual subgradient]
A subgradient of \(\mathcal{L}_C\) is
\[
\partial \mathcal{L}_C(q)
\ni
\gamma
\left(
\frac{C}{K T}
-
\frac{R(q)}{K T}
\right).
\]
The dual function is minimized over \(q\in\R_+^E\). The usual coordinatewise projected subgradient step is
\[
\widehat q^{+}
=
\relu{\left(
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right)
\right)}.
\]
The gauge controller instead uses the relative update
\[
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right)
\right).
\]
This is an exact quotient subgradient-descent step when \(\sum_e C_e=K T\), in which case \(\mathcal{L}_C\) is gauge-invariant. When \(\sum_e C_e\ne K T\), the gauge update removes a common-mode component that affects \(\mathcal{L}_C\); it is then a gauge-centered relative controller, not descent on the full dual objective.
\end{proposition}

\begin{proof}
The first term has gradient
\[
\gamma \frac{C_e}{K T}.
\]
For the second term, by the same Top-\(K\) subgradient argument as above,
\[
\partial_{q_e}
\left[
\frac{1}{K T}
\sum_t
\max_{|S|=K}
\sum_{j \in S}
(a_{t,j} - \gamma q_j)
\right]
\ni
-\gamma \frac{R_e(q)}{K T}.
\]
Adding the two terms gives the result.
\end{proof}

Routing is invariant under common shifts of \(q\), so the relative controller uses only the quotient component of the capacity feedback. Let
\[
P_0 : \R^E \to \one^{\perp}
\]
be the zero-sum projection:
\[
P_0 x
:=
x
-
\left(
\frac{1}{E}
\sum_{e=1}^E x_e
\right)
\one.
\]
Define the gauge-relative capacity feedback
\[
\varepsilon^{\mathrm{C}}(q)
:=
P_0
\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right).
\]
The quotient capacity update is
\[
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\varepsilon^{\mathrm{C}}(q)
\right).
\]

\begin{proposition}[Uniform capacities reduce to requested balance]
Assume uniform capacities
\[
C_e = c \frac{K T}{E}.
\]
Then
\[
\varepsilon^{\mathrm{C}}(q)
=
\frac{R(q)}{K T}
-
\frac{1}{E}\one.
\]
Thus, for uniform capacities, the gauge-centered capacity direction is exactly the requested-balance direction with target \(\mu_e = 1/E\). It is an exact quotient dual-descent direction when \(c=1\), for which \(\sum_e C_e=K T\).
\end{proposition}

\begin{proof}
Let
\[
x_e
=
\frac{R_e(q)}{K T}
-
\frac{c}{E}.
\]
Then
\[
\frac{1}{E}
\sum_e x_e
=
\frac{1}{E}
\left(
\sum_e \frac{R_e(q)}{K T}
-
\sum_e \frac{c}{E}
\right)
=
\frac{1}{E}
(1 - c).
\]
Therefore
\[
P_0 x_e
=
\frac{R_e(q)}{K T}
-
\frac{c}{E}
-
\frac{1-c}{E}
=
\frac{R_e(q)}{K T}
-
\frac{1}{E}.
\]
\end{proof}

\begin{remark}
If \(\sum_e C_e = K T\), then \(\mathcal{L}_C\) is gauge-invariant without quotient projection. If \(\sum_e C_e \ne K T\), the common mode corresponds to aggregate capacity mismatch. The relative pressure controller observes only the quotient component, so the signed mismatch \(\sum_e C_e-K T\) must be tracked separately. Under canonical admission, total rejected mass
\[
\sum_e J_e(q)
=
\sum_e \relu{R_e(q) - C_e}
\]
records realized assignment rejection; it does not measure aggregate capacity surplus.
\end{remark}

\section{Overflow minimization}

For uniform capacities
\[
C_e = C,
\]
define the total overflow
\[
\mathcal{O}(R)
:=
\sum_{e=1}^E \relu{R_e - C}.
\]

\begin{proposition}[Balanced requested load minimizes overflow]
Among nonnegative real requested-load vectors with fixed total load
\[
\sum_{e=1}^E R_e = K T.
\]
The function
\[
R
\mapsto
\mathcal{O}(R)
\]
is Schur-convex. Therefore it is minimized by the balanced requested load
\[
R_e = \frac{K T}{E},
\qquad
e \in [E].
\]
\end{proposition}

\begin{proof}
Let
\[
\phi(x) := \relu{x - C}.
\]
The function \(\phi\) is convex. The sum
\[
\sum_e \phi(R_e)
\]
is symmetric and convex, hence Schur-convex. The balanced vector
\[
\left(\frac{K T}{E},\dots,\frac{K T}{E}\right)
\]
is majorized by every other vector with the same sum. By Karamata's inequality,
\[
\mathcal{O}\!\left(\frac{K T}{E}\one\right)
\le
\mathcal{O}(R).
\]
\end{proof}

\begin{corollary}
Under uniform capacities, balanced requested load minimizes total overflow among relaxed load vectors with fixed total mass. This is a static optimality statement; it does not by itself prove that the hard Top-\(K\) pressure dynamics converge to a balanced load. If the dynamics do converge to a balanced requested load, that load attains the minimum overflow.
\end{corollary}

\section{Exact experimental update rules}

The theory defines four exact experimental controller variants.

Let
\[
q \in \mathcal{Q}
\]
be the current gauge-fixed pressure. Let
\[
R(q)
\]
be the pre-capacity requested Top-\(K\) count and let
\[
A(q)
\]
be the post-capacity admitted count.

Define:

\[
\boxed{
\textbf{(R) Requested feedback:}
\qquad
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\mu
\right)
\right).
}
\]

\[
\boxed{
\textbf{(A) Admitted feedback:}
\qquad
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
\left(
\frac{A(q)}{K T}
-
\mu
\right)
\right).
}
\]

\[
\boxed{
\textbf{(A\(_0\)) Admitted feedback with common mode removed:}
\qquad
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
P_0
\left(
\frac{A(q)}{K T}
\right)
\right).
}
\]

\[
\boxed{
\textbf{(C) Capacity-relative requested feedback:}
\qquad
q^{+}
=
\gproj\!\left(
q
+
\eta \gamma
P_0
\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right)
\right).
}
\]

For uniform capacities and uniform target \(\mu_e = 1/E\), variants \((R)\) and \((C)\) coincide on the gauge quotient.
For uniform \(\mu\), variants \((A)\) and \((A_0)\) also define the same gauge dynamics: their feedback vectors differ only by a common-mode component, which \(\gproj\) removes.

\section{Corrected scientific claims}

The corrected formal claims are as follows.

\begin{enumerate}
\item
Requested load satisfies the conservation law
\[
\sum_e R_e = K T.
\]
It also satisfies
\[
0\le R_e\le T,
\qquad
0\le \frac{R_e}{K T}\le \frac{1}{K}.
\]
Thus any exactly matched requested target must satisfy \(\mu_e\le 1/K\) and, on a finite batch, \(K T\mu_e\in\mathbb{N}_0\). These necessary conditions are not generally sufficient for hard Top-\(K\) attainability.
Admitted load satisfies
\[
\sum_e A_e \le K T,
\]
with strict inequality under rejection.

\item
In absolute reflected dynamics without gauge fixing, admitted feedback with rejection admits no strictly positive fixed point.

\item
On the gauge quotient, negative total mass is not the core failure. The core failure is saturation-induced information loss:
\[
R_e \ge C_e
\implies
A_e = C_e,
\]
so admitted feedback cannot distinguish different levels of excess demand.

\item
Under uniform capacities \(C_e=c K T/E\), global saturation requires \(c\le1\). If \(c=1\), global saturation implies balanced requested load. For \(c<1\), while global saturation persists, admitted feedback is constant modulo the gauge and induces no relative corrective dynamics. With decay, pressure contracts geometrically toward zero while saturation persists.

\item
Requested Top-\(K\) feedback is a valid quotient subgradient step for a convex hard Top-\(K\) potential, followed by gauge normalization. The smooth Top-\(K\) potential requires the normalization \(\tau/K\), so that the normalized inclusion probabilities sum to one and the zero-temperature limit matches the hard Top-\(K\) average potential.

\item
The capacity-constrained Lagrangian dual function is minimized by dual descent. When \(\sum_e C_e=K T\), it is gauge-invariant and the quotient capacity update is an exact quotient dual-descent step. When \(\sum_e C_e\ne K T\), gauge normalization removes a common-mode component that affects the full dual objective, so the relative update is not descent on that objective. For uniform capacities, its centered capacity direction reduces exactly to
\[
\frac{R(q)}{K T}
-
\frac{1}{E}\one.
\]

\item
Under uniform capacities, balanced requested load minimizes total overflow among relaxed nonnegative load vectors with fixed total mass. This is a static result and does not by itself prove convergence of the hard Top-\(K\) dynamics.
\end{enumerate}

\end{document}

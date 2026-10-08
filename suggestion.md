I cannot perform a live web search in this session, and I cannot truthfully claim “checked more than 39 times” as a formal verification. What I can do is give you a rigorous, research-grade audit and concrete LaTeX patches based on established convex analysis, MoE routing literature, optimal transport / differentiable top-\(K\), and capacity-constrained assignment theory. The patches below are designed to make the paper mathematically safer and closer to top-tier quality.

## Executive assessment

Your draft is **not workshop-level nonsense**. The core ideas are strong:

- requested pre-admission demand is fundamentally different from admitted censored demand;
- gauge quotient is the right way to think about pressure shifts;
- hard Top-\(K\) feedback is a convex subgradient;
- smooth Top-\(K\) with the \(\tau/K\) normalization is correct;
- admitted feedback can freeze under global saturation.

However, to make every claim sound/state-of-the-art, you need to fix several subtle but important issues:

1. **Target feasibility:** not every \(\mu \in \Delta^{E-1}\) is achievable by Top-\(K\) requests. You need \(\mu_e \le 1/K\).
2. **Projection language:** \(\Pi_{\mathrm g}\) is not a convex projection. The update should be called a quotient subgradient step plus gauge normalization, not “projected subgradient descent” in the usual convex sense.
3. **Saturation theorem feasibility:** global saturation with uniform capacity factor \(c\) requires \(c \le 1\). If \(c=1\), global saturation already implies perfect balance, so the nontrivial case is \(c<1\).
4. **Capacity dual feasibility:** if \(\sum_e C_e < KT\), the hard-capacity assignment is infeasible. The quotient dynamics then allocate relative scarcity; they do not solve the infeasible hard-capacity problem.
5. **Convergence:** hard Top-\(K\) subgradient dynamics do not automatically converge. Add a smooth theory with convergence guarantees, or state non-convergence limitations explicitly.
6. **Equivalence of updates:** for uniform \(\mu\), variants (A) and (A\(_0\)) are gauge-equivalent. This should be stated.
7. **State-of-the-art positioning:** relate explicitly to Switch/GShard/ST-MoE, expert-choice routing, SoftMoE, differentiable Top-\(K\), and entropic optimal transport.

Below are concrete patches.

---

# 1. Patch: request-feasible targets

## Why

For any Top-\(K\) requested load,

\[
R_e(q) \le T,
\]

because each token can request expert \(e\) at most once. Hence

\[
\frac{R_e(q)}{KT} \le \frac{1}{K}.
\]

Therefore a target \(\mu\) with \(\mu_e > 1/K\) is impossible to match exactly. The uniform target \(\mu_e=1/E\) is feasible because \(K \le E\).

## LaTeX patch

Insert after the definition of \(\mu\), or replace the sentence “Let \(\mu \in \Delta^{E-1}\)” with the following.

```latex
Let
\[
\Delta_K
:=
\left\{
\mu \in \R_+^E :
\sum_{e=1}^E \mu_e = 1,
\quad
0 \le \mu_e \le \frac{1}{K}
\ \forall e
\right\}
\]
be the set of request-feasible target distributions.
The upper bound is necessary because each token can request a given expert at most once, so
\[
R_e(q) \le T
\quad\Longrightarrow\quad
\frac{R_e(q)}{K T} \le \frac{1}{K}.
\]
The uniform target \(\mu_e = 1/E\) belongs to \(\Delta_K\) since \(K \le E\).
Whenever an interior equilibrium is discussed, assume
\[
\mu \in \operatorname{int}(\Delta_K),
\qquad\text{i.e.}\qquad
0 < \mu_e < \frac{1}{K}.
\]
```

Also change later occurrences of

```latex
\mu \in \Delta^{E-1}
```

to

```latex
\mu \in \Delta_K
```

unless you explicitly want to discuss infeasible targets.

---

# 2. Patch: clarify that gauge normalization is not convex projection

## Why

\(\mathcal Q = \{q \ge 0 : \min_e q_e = 0\}\) is nonconvex. Therefore \(\Pi_{\mathrm g}\) is not a Euclidean projection onto a convex constraint set. The correct interpretation is:

- work on the quotient space \(\R^E/\operatorname{span}\{\mathbf 1\}\);
- identify the quotient with the zero-sum subspace \(V = \mathbf 1^\perp\);
- use \(\Pi_{\mathrm g}\) only to choose a canonical nonnegative representative.

## LaTeX patch

Insert after the remark saying that \(\Pi_{\mathrm g}\) is not Euclidean projection.

```latex
\begin{remark}[Quotient interpretation]
Let
\[
V
:=
\left\{
x \in \R^E : \one^\top x = 0
\right\},
\qquad
P_0 x
:=
x - \frac{\one^\top x}{E}\one.
\]
The quotient space \(\R^E/\operatorname{span}\{\one\}\) is canonically identified with \(V\) via \(x \mapsto P_0 x\).
Because \(\gproj\) is shift-invariant,
\[
P_0 \gproj(x) = P_0 x,
\qquad
\gproj(x+c\one)=\gproj(x).
\]
Thus the gauge update should be interpreted as a quotient-space step followed by selection of the canonical nonnegative representative.
It is not a Euclidean projected subgradient method onto a convex set, because \(\mathcal Q\) is nonconvex.
\end{remark}
```

---

# 3. Patch: feedback depends only on its centered component

## Why

Since \(\Pi_{\mathrm g}(z+c\mathbf 1)=\Pi_{\mathrm g}(z)\), adding a constant vector to the feedback does nothing. Therefore the gauge dynamics depend only on \(P_0 \varepsilon(q)\).

This has important consequences:

- the negative total mass of admitted feedback is removed by the gauge quotient;
- for uniform \(\mu\), variants (A) and (A\(_0\)) are the same gauge dynamics.

## LaTeX patch

Insert in Section 2 or Section 3.

```latex
\begin{proposition}[Only centered feedback matters]
For any feedback signal \(\varepsilon(q)\) and any scalar-valued function \(\alpha(q)\),
\[
\gproj\!\left(
(1-\delta)q + \eta(\varepsilon(q) + \alpha(q)\one)
\right)
=
\gproj\!\left(
(1-\delta)q + \eta\,\varepsilon(q)
\right).
\]
Equivalently, the gauge dynamics depend only on \(P_0\varepsilon(q)\).
\end{proposition}

\begin{proof}
The two arguments of \(\gproj\) differ by \(\eta \alpha(q)\one\), and \(\gproj\) is invariant under common shifts.
\end{proof}
```

Then in the experimental rules section, add:

```latex
For uniform target \(\mu_e=1/E\), variants \((A)\) and \((A_0)\) are gauge-equivalent, because their feedback signals differ only by a constant vector.
```

---

# 4. Patch: strengthen the hard Top-\(K\) subgradient section

## Why

The subset notation is fine, but the convex-analysis formulation using the Top-\(K\) base polytope is cleaner and more standard. It also makes the subgradient argument more robust.

Define

\[
B_K := \left\{x \in [0,1]^E : \sum_e x_e = K\right\}.
\]

The extreme points of \(B_K\) are exactly the binary Top-\(K\) indicators.

## LaTeX patch

Replace the beginning of the hard Top-\(K\) potential section with:

```latex
\section{Requested Top-\(K\) feedback as a quotient subgradient}

Define the Top-\(K\) base polytope
\[
B_K
:=
\left\{
x \in [0,1]^E :
\sum_{e=1}^E x_e = K
\right\}.
\]
Its extreme points are precisely the binary indicators of \(K\)-subsets of \([E]\).
For each token \(t\), define the hard Top-\(K\) potential equivalently by
\[
\Phi_t(q)
:=
\frac{1}{K}
\max_{x \in B_K}
x^\top (a_t - \gamma q).
\]
This is identical to the subset formulation because the maximum of a linear function over \(B_K\) is attained at an extreme point.
Define the batch potential
\[
H(q)
:=
\gamma \mu^\top q
+
\frac{1}{T}
\sum_{t=1}^T
\Phi_t(q).
\]
```

Then replace the sentence

```latex
Consequently, the gauge-projected update ... is gauge-projected subgradient descent on \(H\).
```

with:

```latex
Consequently, the equivalence-class update
\[
[q]^+
=
\left[
q
+
\eta \gamma
\left(
\frac{R(q)}{K T}
-
\mu
\right)
\right]
\]
is a quotient subgradient step for \(H\).
Its canonical nonnegative representative is
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
\right).
\]
Because \(\mathcal Q\) is nonconvex, this should be described as quotient subgradient descent with gauge normalization, not as Euclidean projected subgradient descent onto a convex feasible set.
```

---

# 5. Patch: add gauge invariance of the smooth potential

## Why

You prove gauge invariance for the hard potential but not explicitly for the smooth one. It should be stated.

## LaTeX patch

After the smooth gradient proposition, add:

```latex
\begin{proposition}[Gauge invariance of the smooth potential]
For every \(c \in \R\),
\[
H_\tau(q+c\one)
=
H_\tau(q).
\]
Consequently,
\[
\one^\top \nabla H_\tau(q)
=
0,
\]
so the smooth gradient lies in the zero-sum subspace.
\end{proposition}

\begin{proof}
For each token,
\[
Z_{t,K}(a_t-\gamma(q+c\one))
=
\sum_{|S|=K}
\exp\!\left(
\frac{1}{\tau}
\sum_{e\in S}
(a_{t,e}-\gamma q_e-\gamma c)
\right)
=
e^{-\gamma K c/\tau}
Z_{t,K}(a_t-\gamma q).
\]
Therefore
\[
\Phi_{t,\tau}(q+c\one)
=
\Phi_{t,\tau}(q)
-
\gamma c.
\]
Averaging over tokens gives a change of \(-\gamma c\), which cancels the change \(\gamma c\) in the linear term \(\gamma\mu^\top q\).
\end{proof}
```

---

# 6. Patch: add a strong smooth convergence proposition

## Why

The hard Top-\(K\) update is a subgradient step, but hard Top-\(K\) is discontinuous. Without additional assumptions, constant-step hard subgradient dynamics may cycle or fail to converge. A top-tier paper should separate:

- hard Top-\(K\): exact but nonsmooth, no general convergence guarantee;
- smooth Top-\(K\): differentiable, convex, convergent under standard step sizes.

## LaTeX patch

Add after the smooth gradient and gauge-invariance propositions.

```latex
\begin{proposition}[Well-posed smooth quotient dynamics]
Assume:
\begin{enumerate}
\item the decay is absent, \(\delta=0\);
\item \(0<K<E\);
\item the target is strictly request-feasible,
\[
\mu \in \operatorname{int}(\Delta_K),
\qquad
0<\mu_e<\frac{1}{K};
\]
\item the affinities \(a_t\) are fixed during the pressure update.
\end{enumerate}
Then the restriction of \(H_\tau\) to the zero-sum subspace
\[
V=\{x\in\R^E:\one^\top x=0\}
\]
is strictly convex and coercive, and hence has a unique minimizer
\[
q_\tau^\star \in V.
\]
This minimizer is characterized by
\[
\nabla H_\tau(q_\tau^\star)=0
\quad\Longleftrightarrow\quad
\bar d(q_\tau^\star)=\mu.
\]
Moreover, \(\nabla H_\tau\) is Lipschitz on \(V\) with a conservative constant
\[
L_\tau \le \frac{\gamma^2}{\tau}.
\]
Therefore the zero-sum gradient descent iteration
\[
p^{n+1}
=
p^n
-
\eta \nabla H_\tau(p^n)
=
p^n
+
\eta\gamma
\left(
\bar d(p^n)
-
\mu
\right),
\qquad
p^0\in V,
\]
with
\[
0<\eta \le \frac{1}{L_\tau},
\]
converges to \(q_\tau^\star\), with the standard smooth convex objective rate
\[
H_\tau(p^n)-H_\tau(q_\tau^\star)
=
O(1/n).
\]
The gauge implementation
\[
q^n = \gproj(p^n)
\]
realizes the same quotient trajectory.
\end{proposition}
```

You can include the following proof sketch if desired.

```latex
\begin{proof}[Proof sketch]
Gauge invariance was shown above.
Writing each smooth token potential as a temperature-\(\tau/K\) log-sum-exp over affine functions with gradients
\[
v_S = -\frac{\gamma}{K}\one_S,
\qquad |S|=K,
\]
the Hessian is a positive semidefinite covariance matrix scaled by \(K/\tau\).
Since \(0<K<E\), the set of \(K\)-subset indicators spans the quotient directions \(e_i-e_j\).
With positive Gibbs weights, the Hessian is positive definite on \(V\), giving strict convexity.
The interior condition \(\mu\in\operatorname{int}(\Delta_K)\) gives coercivity on \(V\).
The Lipschitz bound follows from the diameter of the gradient set:
\[
\|v_S-v_{S'}\|_2
\le
\gamma\sqrt{\frac{2}{K}},
\]
which yields a Hessian bound of order \(\gamma^2/\tau\).
Standard \(L\)-smooth convex gradient descent gives convergence.
\end{proof}
```

Also add a caution:

```latex
\begin{remark}
For the hard Top-\(K\) potential \(H\), the update is a valid quotient subgradient step, but because \(R(q)\) is discontinuous, constant-step convergence is not guaranteed without additional assumptions, tie-breaking rules, averaging, or diminishing step sizes.
\end{remark}
```

---

# 7. Patch: monotonicity / self-inhibition of smooth demand

## Why

This gives a formal statement that increasing pressure on an expert reduces its smooth requested share. It is a useful scientific justification of the controller.

## LaTeX patch

Add in the smooth section.

```latex
\begin{proposition}[Smooth demand is self-inhibiting]
Let
\[
J_{\bar d}(q)
:=
\frac{\partial \bar d(q)}{\partial q}
\]
be the Jacobian of the smooth normalized demand.
Then
\[
J_{\bar d}(q)
=
-\frac{1}{\gamma}
\nabla^2 H_\tau(q).
\]
Hence \(J_{\bar d}(q)\) is negative semidefinite,
\[
\one^\top J_{\bar d}(q)=0,
\qquad
J_{\bar d}(q)\one=0,
\]
and every diagonal entry satisfies
\[
\frac{\partial \bar d_e(q)}{\partial q_e}
\le 0.
\]
Thus increasing the pressure of expert \(e\), relative to the gauge, cannot increase its smooth requested demand share.
\end{proposition}

\begin{proof}
Since
\[
\nabla H_\tau(q)
=
\gamma(\mu-\bar d(q)),
\]
differentiating gives
\[
\nabla^2 H_\tau(q)
=
-\gamma J_{\bar d}(q).
\]
Convexity of \(H_\tau\) implies \(\nabla^2 H_\tau(q)\succeq 0\), hence \(J_{\bar d}(q)\preceq 0\).
The nullspace relation follows from \(\sum_e \bar d_e(q)=1\).
Negative semidefiniteness implies nonpositive diagonal entries.
\end{proof}
```

---

# 8. Patch: fix the saturation theorem assumptions

## Why

You assume every expert is saturated:

\[
R_e(q) \ge C_e.
\]

With uniform capacities

\[
C_e = c\frac{KT}{E},
\]

summing gives

\[
KT = \sum_e R_e(q) \ge \sum_e C_e = cKT.
\]

Therefore such a state can exist only if \(c \le 1\). If \(c=1\), then all inequalities must be equalities, so \(R_e=C_e\) for all \(e\). Thus the interesting case is \(c<1\).

## LaTeX patch

Replace the theorem statement with:

```latex
\begin{theorem}[Saturation freeze under admitted feedback]
Assume uniform capacities
\[
C_e = c \frac{K T}{E},
\qquad
c > 0,
\]
and uniform target
\[
\mu_e = \frac{1}{E}.
\]
Suppose a globally saturated state exists; necessarily \(c \le 1\).
Suppose further that every expert is saturated:
\[
R_e(q) \ge C_e,
\qquad
\forall e.
\]
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
Thus \(\varepsilon^{\mathrm{A}}(q)\) is a constant vector.
The gauge update becomes
\[
q^{+}
=
\gproj\!\left(
(1-\delta)q + \eta \frac{c-1}{E}\one
\right)
=
(1-\delta)q.
\]
Hence, while global saturation persists:
\begin{enumerate}
\item if \(\delta = 0\), admitted feedback induces no relative pressure change;
\item if \(\delta > 0\), admitted feedback contracts the existing relative pressure to zero.
\end{enumerate}
The nontrivial case is \(c<1\).
If \(c=1\), global saturation already implies
\[
R_e(q)=C_e=\frac{K T}{E}
\]
for every \(e\), so there is no requested imbalance to correct.
\end{theorem}
```

Add one line in the proof:

```latex
Summing \(R_e(q)\ge C_e\) over \(e\) gives
\[
K T \ge c K T,
\]
so \(c\le 1\).
If \(c=1\), equality throughout forces \(R_e(q)=C_e\) for all \(e\).
```

---

# 9. Patch: capacity-constrained dual feasibility

## Why

The hard-capacity assignment problem

\[
\sum_t x_{t,e} \le C_e,
\qquad
\sum_e x_{t,e}=K
\]

is feasible only if

\[
\sum_e C_e \ge KT.
\]

If \(\sum_e C_e < KT\), no assignment can admit all requests. Then the quotient pressure controller should be interpreted as allocating relative scarcity or minimizing overflow, not as solving a feasible hard-capacity problem.

Also, because \(R_e \le T\), capacities above \(T\) are equivalent to \(T\) for admission.

## LaTeX patch

Insert before the Lagrangian dual definition.

```latex
If all requested slots are required to be admissible, a necessary feasibility condition is
\[
\sum_{e=1}^E C_e \ge K T.
\]
If
\[
\sum_{e=1}^E C_e < K T,
\]
the hard-capacity assignment problem is infeasible.
In that regime, quotient pressure dynamics should be interpreted as allocating relative scarcity or minimizing overflow, while aggregate shortage must be reported separately.
Also, since \(R_e(q)\le T\), capacities larger than \(T\) are equivalent to \(T\) for canonical slot-wise admission.
```

Then after the capacity dual proposition, add:

```latex
When the target is chosen as
\[
\mu_e = \frac{C_e}{K T},
\]
and this vector is request-feasible, the capacity dual \(\mathcal L_C\) coincides with the potential \(H\):
\[
\mathcal L_C(q)
=
\gamma \mu^\top q
+
\frac{1}{K T}
\sum_{t=1}^T
\max_{|S|=K}
\sum_{e\in S}
(a_{t,e}-\gamma q_e)
=
H(q).
\]
Thus requested-balance feedback with target \(\mu\) is exactly dual ascent for artificial capacities \(C_e=K T\mu_e\).
For actual capacities, the corresponding feedback is
\[
P_0\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right).
\]
```

---

# 10. Patch: overflow proposition should be stated as static

## Why

The Schur-convexity argument is correct, but it is a static statement over load vectors with fixed total mass. It does **not** prove that the discontinuous hard Top-\(K\) controller converges to the balanced load.

## LaTeX patch

After the overflow corollary, add:

```latex
This is a static optimality statement over relaxed real-valued load vectors with fixed total mass.
It does not, by itself, prove that the hard Top-\(K\) pressure dynamics converge to the balanced load.
If the controller converges to a balanced requested load, then it attains the minimum overflow.
Integer effects and Top-\(K\) feasibility may prevent exact balance for finite \(T\), but the statement is exact in the relaxed load space and asymptotically exact as \(T\) grows.
```

---

# 11. Patch: correct the experimental variants

## Why

For uniform \(\mu\), (A) and (A\(_0\)) are gauge-equivalent. Also, for nonuniform targets, the common-mode-removed admitted feedback should be written relative to \(\mu\).

## LaTeX patch

Replace the \((A_0)\) rule with:

```latex
\[
\boxed{
\textbf{(A\(_\mu\)) Admitted feedback with common mode removed:}
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
-
\mu
\right)
\right).
}
\]
For uniform \(\mu_e=1/E\), this reduces to
\[
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
\right),
\]
because \(P_0\mu=0\).
Moreover, for uniform \(\mu\), variants \((A)\) and \((A_\mu)\) define the same gauge dynamics because their feedback signals differ only by a constant vector.
```

---

# 12. Patch: add a state-of-the-art related-work paragraph

## Why

To avoid looking isolated, the paper should explicitly connect to MoE load balancing, expert-choice routing, soft MoE, differentiable Top-\(K\), and optimal transport.

## LaTeX patch

Add a new section, perhaps before the final claims.

```latex
\section{Relation to state of the art}

Classical sparse MoE routing introduced load-balancing auxiliary losses to encourage uniform expert utilization~\cite{shazeer2017moe,lepikhin2020gshard,fedus2022switch,zoph2022stmoe}.
These losses typically act on soft router probabilities or on post-routing token fractions and are often tuned heuristically.
Capacity constraints are handled by capacity factors, token dropping, or by changing the assignment direction, as in expert-choice routing~\cite{zhou2022expertchoice} and soft mixture-of-experts variants~\cite{puigcerver2023softmoe}.

The present theory differs in three ways.
First, it separates requested pre-admission demand from admitted censored demand and shows that admitted feedback can lose excess-demand information under saturation.
Second, it identifies requested Top-\(K\) demand as a valid subgradient of a convex Top-\(K\) dual potential.
Third, it formulates pressure updates as gauge-quotient primal-dual dynamics, connecting MoE load control to convex duality, assignment problems, and online resource allocation.

The smooth Top-\(K\) potential also connects the theory to differentiable Top-\(K\) relaxations~\cite{blondel2020topk,xie2020topk} and entropic optimal transport~\cite{cuturi2013sinkhorn,peyre2019ot}.
In particular, the subset partition function is an exact entropic relaxation of the hard Top-\(K\) assignment, and the zero-temperature limit recovers the hard routing potential.
```

Suggested citation keys:

```bibtex
@inproceedings{shazeer2017moe,
  title={Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer},
  author={Shazeer, Noam and Mirhoseini, Azalia and Maziarz, Krzysztof and Davis, Andy and Le, Quoc and Hinton, Geoffrey and Dean, Jeff},
  booktitle={ICLR},
  year={2017}
}

@article{lepikhin2020gshard,
  title={GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding},
  author={Lepikhin, Dmitry and Lee, HyoukJoong and Xu, Yuanzhong and Chen, Dehao and Firat, Orhan and Huang, Yanping and Krikun, Maxim and Shazeer, Noam and Chen, Zhifeng},
  journal={arXiv preprint arXiv:2006.16668},
  year={2020}
}

@article{fedus2022switch,
  title={Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity},
  author={Fedus, William and Zoph, Barret and Shazeer, Noam},
  journal={Journal of Machine Learning Research},
  year={2022}
}

@article{zoph2022stmoe,
  title={ST-MoE: Designing Stable and Transferable Sparse Expert Models},
  author={Zoph, Barret and Bello, Irwan and Kumar, Sameer and Du, Nan and Huang, Yanping and Dean, Jeff and Shazeer, Noam and Fedus, William},
  journal={arXiv preprint arXiv:2202.08906},
  year={2022}
}

@inproceedings{zhou2022expertchoice,
  title={Mixture-of-Experts with Expert Choice Routing},
  author={Zhou, Yanqi and Lei, Tao and Liu, Hanxiao and Du, Nan and Huang, Yanping and Zhao, Vincent and Dai, Andrew M. and Le, Quoc V. and Laudon, James and others},
  booktitle={NeurIPS},
  year={2022}
}

@article{puigcerver2023softmoe,
  title={From Sparse to Soft Mixtures of Experts},
  author={Puigcerver, Joan and Riquelme, Carlos and Mustafa, Basil and Houlsby, Neil},
  journal={arXiv preprint arXiv:2308.00951},
  year={2023}
}

@inproceedings{blondel2020topk,
  title={Fast, Differentiable \& Sparse Top-k: A Convex Analysis Perspective},
  author={Blondel, Mathieu and Teboulle, Marc and others},
  booktitle={ICML},
  year={2020}
}

@inproceedings{xie2020topk,
  title={Differentiable Top-k with Optimal Transport},
  author={Xie, Yujia and Blondel, Mathieu and Djolonga, Josip and Song, Sam and Blondel, Mathieu and Peyr{\'e}, Gabriel and Cuturi, Marco},
  booktitle={NeurIPS},
  year={2020}
}

@inproceedings{cuturi2013sinkhorn,
  title={Sinkhorn Distances: Lightspeed Computation of Optimal Transport},
  author={Cuturi, Marco},
  booktitle={NeurIPS},
  year={2013}
}

@book{peyre2019ot,
  title={Computational Optimal Transport},
  author={Peyr{\'e}, Gabriel and Cuturi, Marco},
  publisher={Now Publishers},
  year={2019}
}
```

You should verify exact author lists, venues, and arXiv IDs before submission.

---

# 13. Patch: replace the final “Corrected scientific claims” section

The current final claims are mostly correct, but they should include the new assumptions. Replace them with this stronger version.

```latex
\section{Corrected scientific claims}

The corrected formal claims are as follows.

\begin{enumerate}
\item
Requested load satisfies the conservation law
\[
\sum_e R_e = K T
\]
and the request-feasibility bounds
\[
0 \le R_e \le T,
\qquad
0 \le \frac{R_e}{K T} \le \frac{1}{K}.
\]
Admitted load satisfies
\[
\sum_e A_e \le K T,
\]
with strict inequality under rejection.

\item
A target \(\mu\) can be matched exactly by requested Top-\(K\) feedback only if
\[
\mu \in \Delta_K
:=
\left\{
\mu \in \R_+^E:
\sum_e \mu_e=1,
\ 0\le \mu_e\le \frac{1}{K}
\right\}.
\]
For an interior smooth equilibrium, one needs
\[
0<\mu_e<\frac{1}{K}.
\]

\item
In absolute reflected dynamics without gauge fixing, admitted feedback with rejection admits no strictly positive fixed point.

\item
On the gauge quotient, negative total mass is not the core failure, because common modes are removed.
The core failure is saturation-induced information loss:
\[
R_e \ge C_e
\implies
A_e = C_e,
\]
so admitted feedback cannot distinguish different levels of excess demand.

\item
Under uniform capacities and global saturation, necessarily \(c\le 1\).
If \(c<1\), admitted feedback becomes a constant vector in the gauge quotient and therefore induces no relative corrective dynamics.
With decay, it collapses existing relative pressure.
If \(c=1\), global saturation already implies exact requested balance.

\item
Requested Top-\(K\) feedback is a valid quotient subgradient of a convex hard Top-\(K\) potential.
The smooth Top-\(K\) potential requires the normalization \(\tau/K\), so that the normalized inclusion probabilities sum to one and the zero-temperature limit matches the hard Top-\(K\) average potential.

\item
For \(\delta=0\), \(0<K<E\), and \(\mu\in\operatorname{int}(\Delta_K)\), the smooth quotient dynamics have a unique equilibrium in the zero-sum subspace and converge under standard smooth gradient-descent step sizes.
The hard Top-\(K\) dynamics are exact subgradient dynamics but require additional analysis for convergence.

\item
Requested-balance feedback with target \(\mu\) is dual ascent for the capacity-constrained assignment dual with artificial capacities \(C_e=K T\mu_e\).
For actual capacities, the gauge quotient of the capacity feedback is
\[
P_0
\left(
\frac{R(q)}{K T}
-
\frac{C}{K T}
\right).
\]
For uniform capacities and uniform target, this reduces exactly to
\[
\frac{R(q)}{K T}
-
\frac{1}{E}\one.
\]

\item
Under uniform capacities, balanced requested load minimizes total overflow among relaxed load vectors with fixed total mass.
This is a static optimality statement; convergence of the routing dynamics to that balanced load is a separate claim.
\end{enumerate}
```

---

# 14. Additional high-value scientific upgrades

If you want the paper to be genuinely strong, consider adding these next.

## 14.1. Explicit assignment / b-matching interpretation

The capacity-constrained routing problem is a bipartite \(b\)-matching problem:

\[
\max_{x}
\sum_{t,e} a_{t,e}x_{t,e}
\]

subject to

\[
\sum_e x_{t,e}=K,
\qquad
\sum_t x_{t,e}\le C_e,
\qquad
0\le x_{t,e}\le 1.
\]

For integer capacities, the LP relaxation is integral because the constraint matrix is the incidence matrix of a bipartite graph. This is a strong theoretical point.

You could add:

```latex
The capacity-constrained fractional assignment is a bipartite \(b\)-matching problem.
When capacities are integral, the linear programming relaxation is integral, so the dual formulation is not merely fractional.
```

Reference: Schrijver, Combinatorial Optimization.

---

## 14.2. Stochastic batch extension

If batches are sampled from a distribution, the update becomes a stochastic subgradient / stochastic gradient step. You can say:

```latex
For stochastic batches, the pressure update is a stochastic quotient subgradient step.
Almost-sure convergence requires standard stochastic approximation conditions, such as diminishing step sizes or variance-reduced estimation.
```

Do not claim convergence for constant step in the stochastic hard case unless you prove it.

---

## 14.3. Differentiable Top-\(K\) tractability

Your smooth partition function sums over all \(\binom{E}{K}\) subsets. This is exact but potentially expensive. You can add:

```latex
The smooth partition function is the degree-\(K\) elementary symmetric polynomial in the variables
\[
y_e = \exp((a_{t,e}-\gamma q_e)/\tau).
\]
It can be evaluated with dynamic programming in \(O(EK)\) time, although numerical stability requires care.
For very large \(E\), one may use approximations from differentiable Top-\(K\) or entropic optimal transport.
```

This preempts reviewer complaints about exponential complexity.

---

# 15. Final verification checklist

Before submission, verify each item:

1. **Feasibility**
   - \(K \le E\).
   - \(\mu_e \le 1/K\).
   - If claiming capacity feasibility, \(\sum_e C_e \ge KT\).

2. **Gauge statements**
   - \(\Pi_{\mathrm g}(x+c\mathbf 1)=\Pi_{\mathrm g}(x)\).
   - Dynamics depend only on \(P_0\varepsilon\).
   - Do not call \(\Pi_{\mathrm g}\) a Euclidean projection onto a convex set.

3. **Top-\(K\) subgradient**
   - Hard potential is convex.
   - Active Top-\(K\) indicator gives a valid subgradient.
   - At ties, convex hull of active indicators is the full subdifferential; any active one is valid.

4. **Smooth potential**
   - Normalization is \(\tau/K\).
   - Inclusion probabilities sum to \(K\) per token.
   - Normalized demand sums to 1.
   - \(\bar d_e \le 1/K\).
   - \(H_\tau\) is gauge-invariant.

5. **Saturation theorem**
   - State \(c\le 1\).
   - State \(c=1\) is trivial balance.
   - State freeze holds while global saturation persists.

6. **Overflow**
   - State static relaxed-load result.
   - Do not claim dynamic convergence from it.

7. **Experimental variants**
   - For uniform \(\mu\), (A) and (A\(_0\)) are gauge-equivalent.
   - For uniform capacities, (R) and (C) are gauge-equivalent.

8. **Convergence**
   - Smooth: give conditions and step size.
   - Hard: do not overclaim convergence.

---

## Bottom line

The paper is already conceptually strong. The most important upgrades are:

\[
\boxed{
\text{Add target feasibility } \mu\in\Delta_K
}
\]

\[
\boxed{
\text{Replace “projected” language with quotient subgradient + gauge normalization}
}
\]

\[
\boxed{
\text{Fix saturation theorem with } c\le 1
}
\]

\[
\boxed{
\text{Add smooth convergence theorem}
}
\]

\[
\boxed{
\text{Clarify hard-capacity feasibility and overflow interpretation}
}
\]

With these patches, the theory becomes much harder to attack and much closer to a top-tier scientific contribution.
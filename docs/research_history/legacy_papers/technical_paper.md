# Saturation Kills the Signal: Controllability Loss Under Censored Load Feedback in Capacity-Constrained Sparse MoE Routing

---

## Abstract

Sparse Mixture-of-Experts (MoE) models with Top-$K$ token-choice routing under expert-capacity constraints must balance expert utilization through a load-feedback controller. In every deployed capacity-factor framework — Switch Transformer, GShard, Megatron-Core, DeepSeek-V2 — the observable load signal is the *admitted* count $A_e = \min(R_e, C_e)$, not the *requested* count $R_e$, because tokens exceeding capacity are dropped before the count is formed. We prove that this censoring induces a structural loss of controllability: under expert saturation ($R_e \geq C_e$), admitted feedback degenerates to a constant vector on the gauge quotient, any integral controller consuming it — including the DeepSeek-V3 bias-sign update — loses corrective authority, and excess demand becomes provably invisible. In contrast, we show that requested-count feedback $R_e$ is a valid subgradient of a convex Top-$K$ potential whose smooth relaxation is strictly convex on the quotient space with guaranteed $O(1/n)$ convergence. The separation is not a tuning deficiency: it is a structural consequence of the $\min(\cdot, C_e)$ censoring operator applied to a conservation-law-constrained signal. We verify these results across 236 paired deterministic experiments spanning four capacity regimes, seven controller variants, non-uniform targets, heterogeneous capacities, and adversarial demand conditions. A closed-form first-flip-step theorem $t_\text{flip}(\eta) = \lceil X/\eta \rceil$ yields 14/14 exact predictions, including two committed prospectively before execution.

---

## 1. Introduction

### 1.1 The problem

Large-scale Mixture-of-Experts models (Shazeer et al., 2017; Lepikhin et al., 2020; Fedus et al., 2022) route each token to $K$ of $E$ experts via a Top-$K$ selection on learned affinity scores. When expert capacity is bounded — either by a capacity factor during training (Switch, GShard, ST-MoE) or by a capacity-aware drop policy at inference (Hwang et al., ICLR 2026) — tokens exceeding an expert's capacity are rejected. The system must then balance load across experts to minimize rejection while preserving routing quality.

Every deployed capacity-factor system uses some form of load-feedback controller: auxiliary losses on token fractions (Shazeer et al., 2017; Fedus et al., 2022; Zoph et al., 2022), bias-sign updates on admitted counts (Wang and Dai et al., 2024; DeepSeek-V3), or capacity-relative adjustments (Megatron-Core). In all of these, the load signal available to the controller is the *admitted* count — the number of tokens actually processed — not the *requested* count — the number of tokens that selected the expert before capacity enforcement.

This distinction is the subject of this paper.

### 1.2 The observation

The map $R_e \mapsto A_e = \min(R_e, C_e)$ is flat on $[C_e, \infty)$. Under expert saturation, admitted counts report the capacity ceiling, not the actual demand. A controller consuming only admitted counts therefore receives a signal that carries zero information about excess demand precisely when excess demand is most severe.

This is not a new phenomenon in engineering. In teletraffic theory, the distinction between *offered load* and *carried load* is foundational: "The offered traffic is a theoretical value and it cannot be measured. It is only possible to estimate the offered traffic from the carried traffic" (ITU Teletraffic Engineering Handbook). The Erlang-B blocking model captures exactly the saturation at which carried load ceases to be informative about offered load. Our contribution is the formal instantiation of this principle in MoE routing, where the censoring is *endogenous* — it depends on the controller's own pressure state through the Top-$K$ selection — and where the gauge-quotient structure of the pressure space creates additional subtleties.

### 1.3 Contribution

We make one contribution with three components:

1. **Negative result (Theorems 1–2).** Under global expert saturation with uniform capacities $C_e = cKT/E$ and $c < 1$, admitted-load feedback is a constant vector on the gauge quotient and induces zero relative corrective dynamics. More generally, the admitted feedback coordinate for any saturated expert is independent of the actual requested load $R_e$, so excess demand $R_e - C_e$ is invisible. Any integral controller driven by admitted counts — including the DeepSeek-V3 $\gamma$-sign bias update — loses steady-state controllability authority.

2. **Positive result (Propositions 3–6).** Requested Top-$K$ feedback is a valid quotient subgradient of a convex hard Top-$K$ potential $H(q)$. Its smooth relaxation $H_\tau(q)$ is strictly convex and coercive on the zero-sum subspace with Lipschitz gradient $L_\tau \leq \gamma^2/\tau$, and gradient descent converges at rate $O(1/n)$. Smooth demand is self-inhibiting: increasing pressure on expert $e$ cannot increase its demand share.

3. **Experimental separation (236 runs).** Across three protocol versions, four capacity regimes, seven controller variants, non-uniform targets, heterogeneous capacities, and adversarial demand, requested-count feedback rebalances load while admitted-count feedback is frozen under saturation. A closed-form first-flip-step theorem yields 14/14 exact predictions. Head-to-head against a DeepSeek-style bias controller: requested-direction wins 16/20 paired comparisons across 4 seeds and 5 scenarios.

### 1.4 Scope and non-claims

This paper characterizes the *feedback signal*, not the *controller*. The gauge-quotient subgradient update is standard convex optimization; we do not claim algorithmic novelty. The bias controller is prior art (Wang and Dai et al., 2024) and a framework flag (Megatron-Core `--moe-router-enable-expert-bias`). All experiments are synthetic and deterministic; we make no claim about downstream model quality, following the SimBal caution that load-balance metrics can anti-correlate with perplexity (Huang et al., 2024). In dropless systems (DeepSeek-V3 in production, MegaBlocks, Expert Choice routing), requested and admitted counts coincide and our results are vacuously true. The contribution applies specifically to *capacity-constrained regimes where tokens are dropped*.

---

## 2. Formal Setup

### 2.1 Objects and notation

Let $E \in \mathbb{N}$ be the number of experts, $K \in \{1, \ldots, E\}$ the per-token routing fan-out, and $T \in \mathbb{N}$ the batch size. For token $t$, let $a_t \in \mathbb{R}^E$ be the raw affinity vector and $q \in \mathbb{R}_+^E$ the pressure vector with pressure gain $\gamma > 0$. The pressured score is

$$s_{t,e}(q) = a_{t,e} - \gamma q_e.$$

The hard Top-$K$ set-valued map is

$$\text{TopK}_K(s) := \arg\max_{\substack{S \subseteq [E] \\ |S| = K}} \sum_{e \in S} s_e.$$

For token $t$, let $I_t(q) \in \text{TopK}_K(s_t(q))$ be the selected set under a fixed tie-breaking rule. Define the requested indicator $r_{t,e}(q) := \mathbf{1}\{e \in I_t(q)\}$, so $\sum_e r_{t,e}(q) = K$. The batch requested load is

$$R_e(q) := \sum_{t=1}^T r_{t,e}(q), \qquad \sum_{e=1}^E R_e(q) = KT.$$

### 2.2 Capacity and admission

Let $C \in \mathbb{N}_0^E$ be expert capacities. Under canonical slot-wise admission,

$$A_e(q) := \min\{R_e(q), C_e\}, \qquad J_e(q) := [R_e(q) - C_e]_+.$$

### 2.3 Request-feasible targets

Since each token can request a given expert at most once, $R_e(q) \leq T$, hence $R_e(q)/(KT) \leq 1/K$. Define the set of request-feasible target distributions:

$$\Delta_K := \left\{\mu \in \mathbb{R}_+^E : \sum_{e=1}^E \mu_e = 1, \quad 0 \leq \mu_e \leq \frac{1}{K} \ \forall e\right\}.$$

The uniform target $\mu_e = 1/E$ belongs to $\Delta_K$ since $K \leq E$. For interior smooth equilibria, we require $\mu \in \text{int}(\Delta_K)$, i.e., $0 < \mu_e < 1/K$.

### 2.4 Gauge quotient

Because $\text{TopK}_K(a_t - \gamma(q + c\mathbf{1})) = \text{TopK}_K(a_t - \gamma q)$ for all $c \in \mathbb{R}$, the pressure state is naturally defined on $\mathbb{R}^E / \text{span}\{\mathbf{1}\}$. We use the canonical nonnegative gauge representative:

$$\mathcal{Q} := \{q \in \mathbb{R}_+^E : \min_e q_e = 0\}.$$

The gauge projection is

$$\Pi_{\mathrm{g}}(z) := z - (\min_i z_i)\mathbf{1}.$$

This map satisfies $\Pi_{\mathrm{g}}(z + c\mathbf{1}) = \Pi_{\mathrm{g}}(z)$ for all $c \in \mathbb{R}$.

> **Remark 1 (Quotient interpretation).** The map $\Pi_{\mathrm{g}}$ is not the Euclidean projection onto the nonconvex set $\mathcal{Q}$. It is the canonical gauge representative. The quotient space $\mathbb{R}^E/\text{span}\{\mathbf{1}\}$ is identified with the zero-sum subspace $V = \{x \in \mathbb{R}^E : \mathbf{1}^\top x = 0\}$ via the centering projection $P_0 x := x - (\mathbf{1}^\top x / E)\mathbf{1}$. The gauge update is a quotient-space step followed by selection of the canonical nonnegative representative, not Euclidean projected subgradient descent onto a convex set.

### 2.5 Pressure dynamics

Let $\delta \in [0,1)$ be optional pressure decay and $\eta > 0$ the step size. Given feedback $\varepsilon(q) \in \mathbb{R}^E$, the gauge-quotient pressure dynamics are:

$$q^+ = \Pi_{\mathrm{g}}\!\left((1-\delta)q + \eta\,\varepsilon(q)\right).$$

Since $\Pi_{\mathrm{g}}(z + c\mathbf{1}) = \Pi_{\mathrm{g}}(z)$, adding any common-mode component to $\varepsilon(q)$ leaves this update unchanged. The gauge dynamics depend only on the centered component $P_0\,\varepsilon(q)$.

### 2.6 Feedback signals

The requested-demand feedback error and the admitted-load feedback error are defined respectively as:

$$\varepsilon^{\mathrm{R}}_e(q) := \frac{R_e(q)}{KT} - \mu_e, \qquad \varepsilon^{\mathrm{A}}_e(q) := \frac{A_e(q)}{KT} - \mu_e.$$

**Proposition 1 (Mass conservation and mass loss).** For every $q$:

$$\sum_{e=1}^E \varepsilon^{\mathrm{R}}_e(q) = 0.$$

For admitted feedback:

$$\sum_{e=1}^E \varepsilon^{\mathrm{A}}_e(q) = \frac{\sum_e A_e(q)}{KT} - 1 \leq 0,$$

with strict inequality if any requested assignment is rejected.

*Proof.* Immediate from $\sum_e R_e = KT$, $\sum_e \mu_e = 1$, and $A_e \leq R_e$. $\square$

---

## 3. The Negative Result: Controllability Loss Under Censored Feedback

### 3.1 Saturation freeze

**Theorem 1 (Saturation freeze under admitted feedback).** Assume uniform capacities $C_e = cKT/E$ with $c > 0$, and uniform target $\mu_e = 1/E$. Suppose every expert is saturated: $R_e(q) \geq C_e$ for all $e$. Then necessarily $c \leq 1$. Under canonical admission, $A_e(q) = C_e$ for all $e$, and

$$\varepsilon^{\mathrm{A}}_e(q) = \frac{c-1}{E}, \qquad \forall e.$$

This is a constant vector. The gauge update becomes

$$q^+ = \Pi_{\mathrm{g}}\!\left((1-\delta)q + \eta\frac{c-1}{E}\mathbf{1}\right) = (1-\delta)q.$$

Hence, while global saturation persists:

1. If $\delta = 0$: admitted feedback induces **no relative pressure change**.
2. If $\delta > 0$: each update scales the existing relative pressure by $(1-\delta)$; pressure converges geometrically to zero.

The nontrivial case is $c < 1$. If $c = 1$, global saturation already implies $R_e = C_e = KT/E$ for every expert, so the requested load is already balanced and there is no imbalance to correct.

*Proof.* Summing $R_e(q) \geq C_e = cKT/E$ over $e$ gives $KT \geq cKT$, hence $c \leq 1$. If $c = 1$, then $R_e - C_e \geq 0$ sum to zero, so each is zero. For $c \leq 1$ with $R_e \geq C_e$: $A_e = \min\{R_e, C_e\} = C_e$. Hence $A_e/(KT) = c/E$ and $\varepsilon^{\mathrm{A}}_e = c/E - 1/E = (c-1)/E$. Let $\alpha = (c-1)/E$. Then $(1-\delta)q + \eta\alpha\mathbf{1}$ has minimum $\eta\alpha$ (since $q \in \mathcal{Q}$ implies $\min_e q_e = 0$). The gauge projection subtracts this minimum: $q^+ = (1-\delta)q + \eta\alpha\mathbf{1} - \eta\alpha\mathbf{1} = (1-\delta)q$. $\square$

### 3.2 Information loss

**Theorem 2 (Information loss under saturation).** Under canonical admission, for any two requested-load vectors $R$ and $\widetilde{R}$ satisfying $\min\{R_e, C_e\} = \min\{\widetilde{R}_e, C_e\}$ for all $e$, the admitted feedback signals coincide: $\varepsilon^{\mathrm{A}}(R) = \varepsilon^{\mathrm{A}}(\widetilde{R})$. In particular, on the saturated region $R_e \geq C_e$, the admitted feedback coordinate $\varepsilon^{\mathrm{A}}_e = C_e/(KT) - \mu_e$ is independent of $R_e$. Excess demand $R_e - C_e$ is invisible to admitted-load feedback.

*Proof.* The map $R_e \mapsto \min\{R_e, C_e\}$ is constant on $[C_e, \infty)$. $\square$

**Corollary 1 (Sign reversal under censoring).** If $R_e(q)/(KT) > \mu_e$ but $A_e(q)/(KT) < \mu_e$ for some expert $e$, then $\varepsilon^{\mathrm{R}}_e(q) > 0$ (correctly signals over-demand) while $\varepsilon^{\mathrm{A}}_e(q) < 0$ (incorrectly signals under-demand). Admitted feedback would *decrease* pressure on an over-demanded expert.

### 3.3 Implications for deployed controllers

**Corollary 2 (DeepSeek-V3 bias controller under saturation).** The DeepSeek-V3 bias-sign update (Wang and Dai et al., 2024) is

$$b_e \leftarrow b_e + \gamma \cdot \text{sign}(A_e - \text{mean}(A)),$$

which updates from admitted counts. Under global saturation with uniform capacity, $A_e = C_e$ for all $e$, so $\text{sign}(A_e - \text{mean}(A)) = 0$ for all $e$. The bias update halts. More generally, any integral controller of the form $q^+ = f(q, A(q))$ that depends on admitted counts only through $A_e = \min(R_e, C_e)$ loses corrective authority on saturated experts, because the map $R_e \mapsto A_e$ is flat on $[C_e, \infty)$.

### 3.4 No interior equilibrium in absolute dynamics

**Proposition 2.** In absolute reflected dynamics $q = [(1-\delta)q + \eta\varepsilon^{\mathrm{A}}(q)]_+$ without gauge fixing, there is no strictly positive fixed point under admitted feedback whenever rejection occurs. (The proof follows from summing the fixed-point equation: $\delta\sum_e q_e = \eta\sum_e \varepsilon^{\mathrm{A}}_e < 0$, contradicting $q_e > 0$.)

> **Remark 2.** On the gauge quotient, the failure is not negative total mass (which the gauge projection removes) but *saturation-induced information loss*: the censored signal $A_e = C_e$ carries no information about the magnitude of excess demand $R_e - C_e$.

---

## 4. The Positive Result: Convex Structure of Requested Feedback

### 4.1 Hard Top-$K$ potential

For each token $t$, define the hard Top-$K$ potential:

$$\Phi_t(q) := \frac{1}{K} \max_{\substack{S \subseteq [E] \\ |S| = K}} \sum_{e \in S} (a_{t,e} - \gamma q_e).$$

Define the batch potential:

$$H(q) := \gamma\mu^\top q + \frac{1}{T}\sum_{t=1}^T \Phi_t(q).$$

**Proposition 3 (Hard Top-$K$ subgradient).** For each token $t$, if $I_t(q)$ is a selected Top-$K$ set, then $-(\gamma/K)r_t(q) \in \partial\Phi_t(q)$. Therefore

$$\gamma\left(\mu - \frac{R(q)}{KT}\right) \in \partial H(q).$$

The equivalence-class update $[q]^+ = [q + \eta\gamma(R(q)/(KT) - \mu)]$ is a quotient subgradient step for $H$. Its canonical nonnegative representative is

$$q^+ = \Pi_{\mathrm{g}}\!\left(q + \eta\gamma\left(\frac{R(q)}{KT} - \mu\right)\right).$$

*Proof.* Each $\Phi_t$ is the maximum of affine functions (one per $K$-subset), hence convex. The gradient of the active affine piece at $I_t(q)$ is $-(\gamma/K)r_t(q)$, which is a valid subgradient at the maximum. Averaging over tokens and adding the linear term $\gamma\mu$ gives the batch subgradient. $\square$

**Proposition 4 (Gauge invariance).** For every $c \in \mathbb{R}$: $H(q + c\mathbf{1}) = H(q)$. Thus $H$ is well-defined on the gauge quotient.

*Proof.* The linear term changes by $\gamma c$. Each $\Phi_t$ changes by $-\gamma c$ (each subset has cardinality $K$). They cancel. $\square$

### 4.2 Smooth Top-$K$ potential

Define the smooth Top-$K$ partition function:

$$Z_{t,K}(s) := \sum_{\substack{S \subseteq [E] \\ |S| = K}} \exp\!\left(\frac{1}{\tau}\sum_{e \in S} s_e\right), \qquad \tau > 0,$$

and the smooth token potential:

$$\Phi_{t,\tau}(q) := \frac{\tau}{K}\log Z_{t,K}(a_t - \gamma q).$$

The normalization $\tau/K$ is essential: it ensures that the Gibbs inclusion probabilities

$$d_{t,e}(q) := \sum_{S \ni e} p_{t,\tau}(S; q), \qquad p_{t,\tau}(S; q) := \frac{\exp\!\left(\frac{1}{\tau}\sum_{e \in S}(a_{t,e} - \gamma q_e)\right)}{Z_{t,K}(a_t - \gamma q)},$$

satisfy $\sum_e d_{t,e}(q) = K$ (each subset has cardinality $K$), so that the normalized smooth demand

$$\bar{d}_e(q) := \frac{1}{TK}\sum_{t=1}^T d_{t,e}(q)$$

satisfies $\sum_e \bar{d}_e(q) = 1$ and $\bar{d}_e(q) \leq 1/K$.

The smooth batch potential is $H_\tau(q) := \gamma\mu^\top q + (1/T)\sum_t \Phi_{t,\tau}(q)$.

**Proposition 5 (Smooth gradient and convergence).** $H_\tau$ is convex and differentiable with

$$\nabla H_\tau(q) = \gamma(\mu - \bar{d}(q)).$$

It is gauge-invariant: $H_\tau(q + c\mathbf{1}) = H_\tau(q)$. For $\delta = 0$, $0 < K < E$, and $\mu \in \text{int}(\Delta_K)$, the restriction of $H_\tau$ to the zero-sum subspace $V = \{x \in \mathbb{R}^E : \mathbf{1}^\top x = 0\}$ is strictly convex and coercive, with unique minimizer $q_\tau^\star \in V$ characterized by $\bar{d}(q_\tau^\star) = \mu$. The gradient is Lipschitz on $V$ with constant $L_\tau \leq \gamma^2/\tau$. Gradient descent with step size $0 < \eta \leq 1/L_\tau$ converges at rate $O(1/n)$.

*Proof sketch.* Gauge invariance: the partition function satisfies $Z_{t,K}(a_t - \gamma(q + c\mathbf{1})) = e^{-\gamma Kc/\tau} Z_{t,K}(a_t - \gamma q)$, so $\Phi_{t,\tau}$ changes by $-\gamma c$, canceling the linear term. Strict convexity on $V$: the Hessian is a positive semidefinite covariance matrix scaled by $K/\tau$; since $0 < K < E$, the $K$-subset indicators span the quotient directions $e_i - e_j$, and with positive Gibbs weights the Hessian is positive definite on $V$. The interior condition on $\mu$ gives coercivity. The Lipschitz bound follows from the gradient-set diameter: $\|v_S - v_{S'}\|_2 \leq \gamma\sqrt{2/K}$, yielding a Hessian bound of order $\gamma^2/\tau$. $\square$

**Proposition 6 (Self-inhibition of smooth demand).** The Jacobian of smooth demand satisfies

$$J_{\bar{d}}(q) = -\frac{1}{\gamma}\nabla^2 H_\tau(q) \preceq 0.$$

Every diagonal entry satisfies $\partial\bar{d}_e/\partial q_e \leq 0$: increasing the pressure of expert $e$ cannot increase its smooth demand share.

*Proof.* Since $\nabla H_\tau = \gamma(\mu - \bar{d})$, differentiating gives $\nabla^2 H_\tau = -\gamma J_{\bar{d}}$. Convexity implies $\nabla^2 H_\tau \succeq 0$, hence $J_{\bar{d}} \preceq 0$. Negative semidefiniteness implies nonpositive diagonal entries. $\square$

### 4.3 Zero-temperature limit and the hard subgradient

$\Phi_{t,\tau}(q) \to \Phi_t(q)$ as $\tau \to 0$ (standard log-sum-exp identity). Away from Top-$K$ ties, the smooth gradient converges to the hard subgradient. At ties, the limiting smooth gradient belongs to the convex hull of active indicators, hence to the hard subdifferential. This connects the smooth convergence theory to the hard Top-$K$ dynamics: for small enough $\tau$, the smooth dynamics approximate the hard ones with provable convergence.

> **Remark 3 (Hard convergence is open).** For the hard Top-$K$ potential $H$, the update is a valid quotient subgradient step, but because $R(q)$ is discontinuous (a Top-$K$ flip changes $R$ by $\pm 1$), constant-step convergence is not guaranteed without additional assumptions. Our experiments observe convergence in a wide step-size basin ($\eta \in [0.1, 3.0]$) and a limit cycle at $\eta = 10$. We do not claim convergence; we report empirical behavior.

### 4.4 Capacity dual and the connection between targets and capacities

The capacity-constrained assignment problem — $\max_x \sum_{t,e} a_{t,e} x_{t,e}$ subject to $\sum_e x_{t,e} = K$ and $\sum_t x_{t,e} \leq C_e$ — yields the Lagrangian dual function

$$\mathcal{L}_C(q) = \gamma\sum_e \frac{C_e}{KT}q_e + \frac{1}{KT}\sum_t \max_{|S|=K} \sum_{e \in S}(a_{t,e} - \gamma q_e).$$

When the target is chosen as $\mu_e = C_e/(KT)$ and this vector is request-feasible, the capacity dual $\mathcal{L}_C$ coincides with the potential $H$. Thus requested-balance feedback with target $\mu$ is exactly dual ascent for artificial capacities $C_e = KT\mu_e$. For uniform capacities and uniform target, the gauge-centered capacity direction reduces exactly to $R(q)/(KT) - (1/E)\mathbf{1}$.

### 4.5 Overflow minimization

**Proposition 7.** For uniform capacities $C_e = C$, the total overflow $\mathcal{O}(R) = \sum_e [R_e - C]_+$ is Schur-convex. Among nonnegative real load vectors with $\sum_e R_e = KT$, it is minimized by the balanced load $R_e = KT/E$.

This is a *static* optimality statement over relaxed load vectors. It does not prove that the hard Top-$K$ dynamics converge to balanced load. If they do, that load attains the minimum overflow.

---

## 5. Experimental Update Rules

The theory defines four exact controller variants. Let $q \in \mathcal{Q}$ be the current pressure, $R(q)$ the requested count, $A(q)$ the admitted count.

**(R) Requested feedback:**
$$q^+ = \Pi_{\mathrm{g}}\!\left(q + \eta\gamma\left(\frac{R(q)}{KT} - \mu\right)\right)$$

**(A) Admitted feedback:**
$$q^+ = \Pi_{\mathrm{g}}\!\left(q + \eta\gamma\left(\frac{A(q)}{KT} - \mu\right)\right)$$

**(A₀) Admitted with common mode removed:**
$$q^+ = \Pi_{\mathrm{g}}\!\left(q + \eta\gamma P_0\!\left(\frac{A(q)}{KT}\right)\right)$$

**(C) Capacity-relative requested feedback:**
$$q^+ = \Pi_{\mathrm{g}}\!\left(q + \eta\gamma P_0\!\left(\frac{R(q)}{KT} - \frac{C}{KT}\right)\right)$$

For uniform capacities and uniform target $\mu_e = 1/E$: (R) and (C) are gauge-equivalent. For uniform $\mu$: (A) and (A₀) define the same gauge dynamics (their feedback differs by a constant vector). These equivalences break under non-uniform targets or heterogeneous capacities (Section 7.3).

---

## 6. The First-Flip-Step Theorem

In the pre-flip linear regime ($\delta = 0$, requested feedback, $R$ constant because no Top-$K$ selection has yet changed), pressure grows as

$$q_n = n\eta\gamma(\varepsilon - \min_e \varepsilon_e)\cdot\mathbf{e}$$

where $\varepsilon = R/(KT) - \mu$ (by induction; the gauge min-shift cancels in score differences). The first Top-$K$ flip over the batch occurs at

$$t_{\text{flip}}(\eta) = \left\lceil \frac{X}{\eta} \right\rceil, \qquad X = \min_{i,e,e'} \frac{a_{i,e} - a_{i,e'}}{\gamma^2(\varepsilon_e - \varepsilon_{e'})}$$

a pure function of the affinity tensor and step-0 counts — no dynamics simulated.

**Verification.** Predictions committed to git *before* prospective runs. All 14 predictions exact ($|\text{error}| = 0$):

| Seed | $X$ | $\eta = 0.05$ | $0.1$ | $0.15$ | $0.2$ | $0.3$ | $0.4$ |
|------|------|------|------|------|------|------|------|
| 17 | 35.115 | 703 | 352 | **235** | 176 | **118** | 88 |
| 23 | 34.622 | 693 | 347 | 231 | 174 | 116 | 87 |
| 42 | 36.457 | 730 | 365 | 244 | 183 | 122 | 92 |

(Bold = prospective predictions; all matched exactly.)

The seed-independent invariant is $\eta \cdot t_{\text{flip}} = X_{\text{seed}}$. The previously reported "$\eta \times \text{step} \approx 35.2$" is seed-17-specific. Uniform capacity is not required (capacity never enters pre-flip requested-feedback dynamics).

---

## 7. Experimental Verification

### 7.1 Protocol

All experiments use $E = 8$, $K = 2$, deterministic mode, CPU. Three protocol versions:

| Version | Runs | Design |
|---------|------|--------|
| v1 (0.1.0) | 64 | 4 scenarios × 4 controllers × 3 seeds + step-size sweep |
| v2 (0.2.0) | 93 | 5 scenarios × 7 controllers × 2 seeds + sensitivity sweeps |
| v3 (0.3.0) | 79 | Non-uniform targets, heterogeneous capacities, anti-windup, DeepSeek head-to-head, theorem verification |
| **Total** | **236** | All paired (affinity SHA-256 hashes identical within groups) |

Every scenario/controller/seed combination ran on the identical affinity batch. Verified by content-hash matching across controllers.

### 7.2 Core result: saturation freeze confirmed exactly

**Shortage regime** ($C = 192$, $c = 0.75$, aggregate shortage $KT - \sum C = 512$).

Initial loads: $R = [300, 300, 270, 270, 240, 240, 214, 214]$ (every expert above capacity).

| Controller | Pressure range (final) | Violation $0 \to 2000$ | First routing change |
|------------|----------------------|----------------------|---------------------|
| Requested | 1.82 | 0.0215 → 0.0000 | Step 352 ($\eta = 0.1$) |
| Admitted | 0.00 | 0.0215 → 0.0215 | **Never** |

Under admitted feedback, the per-step feedback vector is the constant $-0.03125 = (c-1)/E$ on every coordinate, exactly as Theorem 1 predicts. The gauge update removes the common mode and pressure stays $[0]^8$ for all 2000 steps at every step size tested ($\eta \in \{0.05, 0.1, 0.2, 0.4\}$). No step size rescues admitted feedback.

Under requested feedback at $\eta \geq 0.1$, load balances exactly ($R = [256]^8$, violation 0.0000) while global saturation persists ($R_e \geq 192$ at every step). At $\eta = 0.05$, the 2000-step horizon yields violation 0.0068 (still improving).

This result replicates across three seeds (17, 23, 42) with quantitative consistency.

**Exact-total boundary** ($C = 256$, $c = 1.0$): Global saturation implies $R_e = C_e = KT/E$ for all $e$. All controllers produce zero feedback, zero pressure, zero violation. The degenerate case identified by the theory.

**Slack regime** ($C = 288$, aggregate surplus 256):

| Controller | Violation $0 \to 500$ | Overflow $0 \to 500$ | First routing change |
|------------|---------------------|---------------------|---------------------|
| Requested | 0.0449 → 0.0215 | 128 → 24 | Step 344 |
| Admitted | 0.0449 → 0.0444 | 128 → 125 | Step 488 |

Requested feedback cuts overflow by 81% (128 → 24); admitted feedback cuts it by 2.3% (128 → 125). Admitted feedback understates excess on the two most overloaded experts by a factor of ~2.6× ($A_e = 288$ vs. $R_e = 340$).

### 7.3 Non-uniform targets and heterogeneous capacities (v3)

With explicit target $KT\mu = [384, 352, 320, 288, 256, 224, 128, 96]$ and heterogeneous-shortage capacities $C = [300, 270, 240, 210, 180, 150, 120, 66]$ (sum 1536, $c = 0.75$):

- **Admitted feedback integrates a phantom gradient.** Under global saturation (fraction 1.00), the admitted controller integrates $P_0(C/(KT) - \mu)$: pressure moves on 799/799 consecutive saturated steps, building range 1.484 over 800 steps while routing stays frozen (violation constant at 0.0576). This is 1.48 units of pressure state built from a signal containing zero current-demand information.

- **(A₀) diverges under heterogeneous capacity.** The admitted-centered variant, gauge-equivalent to (A) only under uniform target, is actively destructive here: violation $0.0576 \to 0.41$, overflow $512 \to 1065$, expert 7 (capacity 66) driven to 938 requests. The v1 gauge equivalence is fragile.

- **Requested feedback gets closest.** Final violation 0.0088 (within 18 tokens of target), all 3 seeds, both regimes.

### 7.4 Saturation windup scenario (v2)

Demand spike on steps 400–800 saturating experts 0–3 at capacity $C = 256$:

| Controller | Violation at spike end | Post-release overshoot | Final violation |
|------------|----------------------|----------------------|----------------|
| Requested | 0.0215 | +0.046 | 0.0068 |
| Admitted | 0.1245 | +0.040 | 0.0063 |
| Bias (DeepSeek-style) | 0.1655 | −0.0005 | 0.0010 |

During the spike, requested-direction rebalances fully (violation 0.0215) while admitted-direction stalls at 0.12 and the bias controller stalls at 0.166. Post-release transients are bounded (overshoot < 0.05) for all controllers.

### 7.5 DeepSeek head-to-head (v2 + v3, 4 seeds)

Requested vs. bias_integral (DeepSeek-V3-style $\gamma$-sign update on admitted counts, $\gamma = 0.001$) across 5 scenarios × 4 seeds = 20 paired comparisons:

| Scenario | Requested (mean) | Bias (mean) | Winner |
|----------|-----------------|-------------|--------|
| saturation_windup | 0.0067 | 0.0015 | Bias 4-0 |
| adversarial_init | 0.0215 | 0.1653 | Requested 4-0 |
| adversarial_batches | 0.0323 | 0.3746 | Requested 4-0 |
| specialization_probe | 0.0112 | 0.0693 | Requested 4-0 |
| small_batch | 0.0117 | 0.0234 | Requested 4-0 |

Requested wins 16/20 paired comparisons. The 4 bias wins are on saturation_windup final violation — reported honestly. The bias controller's advantage on that specific metric is genuine (it accumulates no state during the spike, so it has no post-release overshoot), but its spike-end violation is ~8× worse.

### 7.6 Stability: thrash mapping

Step-size sensitivity for the requested-direction controller ($\eta$ over 4 orders of magnitude):

| $\eta$ | Behavior | Final violation | Tail oscillations |
|--------|----------|----------------|-------------------|
| 0.001 – 0.03 | Inert | 0.0215 | 0 |
| 0.1 – 3.0 | **Converged (clean)** | 0.0005 – 0.0078 | **0** |
| 10.0 | Limit cycle | 0.0215 | 143 |

The pressure controller has a wide clean basin spanning 1.5 orders of magnitude with zero tail oscillation. The bias controller chatters (132–198 tail direction changes) at every working gain.

### 7.7 Ablation findings

- **Pressure decay ($\delta = 0.05$) can be fatal.** The leak caps pressure at $(\eta\gamma/\delta)|\varepsilon|$. In the adversarial_init scenario, the ceiling is 0.467 but diversion requires $q_0 > 1.0$; the controller never diverts a single token ($R_0 = 1024$ unchanged at step 799).

- **Gauge projection is numerical hygiene.** Without it, routing is bit-identical in 9/10 cases; in the 10th, common-mode drift (−0.7) causes single-token flips at float32 Top-$K$ boundaries. No scientific conclusion changes, but the projection does real work.

- **Anti-windup controller (conditional integration) is honest but limited.** Prevents windup (builds exactly 0 state vs. admitted's 1.48 units under heterogeneous saturation), but cannot recover the information censoring destroys — trades under-correction for no-correction. Never beats requested on any rebalancing metric.

---

## 8. Related Work

### 8.1 MoE load balancing

Sparse MoE routing was introduced by Shazeer et al. (2017) with auxiliary load-balancing losses. Capacity-factor token dropping appeared in GShard (Lepikhin et al., 2020) and Switch Transformer (Fedus et al., 2022), with refinements in ST-MoE (Zoph et al., 2022). Expert-Choice routing (Zhou et al., 2022) inverts the assignment direction; Soft MoE (Puigcerver et al., 2023) removes sparsity. Aux-loss-free bias control was introduced by Wang and Dai et al. (2024) and adopted in DeepSeek-V3. Observation-scope effects were characterized by "Demons in the Detail" (Qwen, 2025), which showed that micro-batch vs. global load statistics is a first-order design variable. Our axis — requested vs. admitted (censoring) — is orthogonal to and composable with the scope axis.

**Our contribution relative to this literature:** We characterize the *feedback signal*, not the *controller*. The controller is prior art. The signal characterization — that admitted counts lose identifiability under saturation while requested counts are convex subgradients — is the contribution.

### 8.2 Teletraffic theory

The offered-vs-carried distinction is classical in teletraffic engineering: carried load saturates at capacity and stops being informative about offered load (ITU Handbook; Iversen, 2015). Our saturation-freeze theorem (Theorem 1) is the MoE-routing instantiation of this principle. The connection has not previously been drawn.

### 8.3 Censored feedback in online learning

Censored bandits (Abernethy et al., NeurIPS 2016; Guinet, MIT thesis) establish that censoring changes regret character. Our setting differs in two ways: (1) the censoring is *endogenous* — it depends on the controller's own state through $R_e \geq C_e$; and (2) it is *score-biased* — in DeepSeek-V2 and Megatron-Core, dropped tokens are selected by lowest affinity score, making the admitted count a downward-biased, score-truncated statistic whose bias is largest for experts whose marginal requests have low affinity.

### 8.4 Differentiable Top-$K$ and optimal transport

The smooth Top-$K$ partition function is the degree-$K$ elementary symmetric polynomial in the variables $y_e = \exp((a_{t,e} - \gamma q_e)/\tau)$, computable by dynamic programming in $O(EK)$ time. This connects to differentiable Top-$K$ (Blondel and Teboulle, ICML 2020; Xie et al., NeurIPS 2020) and entropic optimal transport (Cuturi, NeurIPS 2013; Peyré and Cuturi, 2019). The subset partition function is an exact entropic relaxation of the hard Top-$K$ assignment.

### 8.5 Systems-level observation cost

METRO (2025) gathers global top-$K$ knowledge via allGather and prices it against allToAll; Libra (ICLR 2026) explicitly balances overhead vs. effectiveness; Capacity-Aware Token Drop (ICLR 2026) enforces per-expert ceilings at inference. Our formal characterization of *when* the requested-side signal is worth its observation cost complements these empirical tradeoffs.

---

## 9. Limitations

1. **Synthetic only.** All 236 runs use synthetic affinities, $E = 8$, $K = 2$, CPU. Nothing here implies the pressure controller trains a better model. The SimBal caution (Huang et al., 2024) — that near-perfect load balance can anti-correlate with perplexity — applies directly.

2. **No trained-model evaluation.** The minimum bar for belief is a small LM trained under capacity-drop conditions, reporting validation perplexity. We have not crossed that bar.

3. **No convergence proof for hard Top-$K$.** The smooth convergence proposition applies to $H_\tau$ with $\tau > 0$. For the hard potential $H$ ($\tau = 0$), the subgradient dynamics may cycle under constant step size. Our experiments observe convergence in a wide basin ($\eta \in [0.1, 3.0]$) and a limit cycle at $\eta = 10$.

4. **Premise scope.** In dropless systems (DeepSeek-V3 production, MegaBlocks, Expert Choice routing), requested ≡ admitted and our results are vacuously true. The contribution applies to capacity-constrained regimes where tokens are dropped.

5. **Three to four seeds per condition.** Seed-dependence was observed (adversarial_batches: requested seed 17 at 0.1250, seeds 23/42/99 at 0.0005–0.0024). Seed-averaged claims are weak.

6. **The controller is not novel.** The gauge-quotient subgradient update is standard convex optimization. The DeepSeek bias controller is prior art. Our contribution is the feedback-signal characterization, not the algorithm.

---

## 10. Conclusion

We have established a formal separation between requested-count and admitted-count feedback signals in capacity-constrained sparse MoE routing:

- **Admitted-count feedback** loses controllability under expert saturation. The censoring operator $\min(R_e, C_e)$ destroys excess-demand information; under global saturation with uniform capacity, the feedback degenerates to a constant vector on the gauge quotient; any integral controller consuming it — including deployed bias-sign updates — cannot correct load imbalance.

- **Requested-count feedback** has clean convex optimization structure. It is a subgradient of a gauge-invariant Top-$K$ potential; its smooth relaxation is strictly convex with provable convergence; smooth demand is self-inhibiting.

- **The separation is verified** across 236 paired deterministic experiments, with 14/14 exact first-flip-step predictions including prospective ones.

The observation has been available since capacity-factor routing was introduced in 2020. It has not been formally characterized. We expect the result to be directly useful to designers of load-balancing controllers in capacity-constrained MoE training (Megatron-Core, NeMo) and capacity-aware inference (Capacity-Aware Token Drop, EPLB), and to connect to the broader question of when the observation cost of requested-side telemetry is justified.

---

## References

- Abernethy, J. et al. (2016). Threshold bandits, with and without censored feedback. *NeurIPS*.
- Blondel, M. and Teboulle, M. (2020). Fast, differentiable and sparse Top-$K$: a convex analysis perspective. *ICML*.
- Cuturi, M. (2013). Sinkhorn distances: Lightspeed computation of optimal transport. *NeurIPS*.
- DeepSeek-AI (2024). DeepSeek-V2: A strong, economical, and efficient Mixture-of-Experts language model. arXiv:2405.04434.
- DeepSeek-AI (2024). DeepSeek-V3 technical report. arXiv:2412.19437.
- Fedus, W., Zoph, B., and Shazeer, N. (2022). Switch Transformers: Scaling to trillion parameter models with simple and efficient sparsity. *JMLR*.
- Guinet, G. (2020). Bandit problems under censored feedback. MIT thesis.
- Huang, Y. et al. (2024). Towards understanding the importance of load balance in MoE models (SimBal). arXiv.
- Hwang, R. et al. (2026). Capacity-aware token drop for efficient MoE inference. *ICLR*.
- ITU. Teletraffic Engineering Handbook.
- Iversen, V. B. (2015). Teletraffic Engineering and Network Planning.
- Lepikhin, D. et al. (2020). GShard: Scaling giant models with conditional computation and automatic sharding. arXiv:2006.16668.
- Ma, H. et al. (2026). Load balancing for LLM inference serving: A control and learning oriented survey. SSRN.
- Peyré, G. and Cuturi, M. (2019). *Computational Optimal Transport*. Now Publishers.
- Puigcerver, J. et al. (2023). From sparse to soft mixtures of experts. arXiv:2308.00951.
- Shazeer, N. et al. (2017). Outrageously large neural networks: The sparsely-gated Mixture-of-Experts layer. *ICLR*.
- Wang, Y., Dai, D. et al. (2024). Auxiliary-loss-free load balancing strategy for Mixture-of-Experts. arXiv:2408.15664.
- Xie, Y. et al. (2020). Differentiable Top-$K$ with optimal transport. *NeurIPS*.
- Zhou, Y. et al. (2022). Mixture-of-Experts with Expert Choice routing. *NeurIPS*.
- Zoph, B. et al. (2022). ST-MoE: Designing stable and transferable sparse expert models. arXiv:2202.08906.
- NVIDIA (2026). Megatron-Core MoE documentation. GitHub.
- Chen, L. et al. (2025). METRO: Minimize expert-level token routing overhead for efficient MoE inference. arXiv:2512.09277.
- Liu, Z. et al. (2025). Demons in the detail: On the intricacies of MoE load balancing. arXiv:2501.11873.
- Li, J. et al. (2026). Libra: Balancing the effectiveness and overhead for MoE load balancing. *ICLR*.

---

*Appendix: Reproducibility.* All 236 runs are committed with full provenance (config, manifest with git commit, metrics, affinity reference). Reproduce with `python -m moe_control.cli` from the repository root. Verify with `scripts/verify_findings.py` (all checks pass across v1/v2/v3 suites).

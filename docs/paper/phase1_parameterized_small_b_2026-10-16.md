# Small-step parameterization: exact value boundary for the E=3 instance

**Date:** 2026-10-16
**Branch:** feat/research-censored-feedback
**Status (reconciled 2026-10-17):** proved for the fixed E=3 score/capacity instance while varying only the pressure-step budget. The first-reachable-horizon gap is constant, while the separate sufficiently-long-horizon raw gap grows as \(1/\beta\), as §4 and the linked all-policy theorem state. Both results reduce exactly to the induced state-constrained testing problem; neither establishes a MoE-specific novelty claim. See the [current research ledger](phase1_research_status_2026-10-17.md).

## 1. Question and scope

The previous fixed-step example had $V_R(H)=60$ and $V_A(H)=80$ for
$H\ge4$. The proposed next attack was to send the pressure budget to zero
and let the time to reach informative routing cells grow. This note works out
what that scaling actually proves.

Keep the exact instance from
[phase1_cost_info_lemma_2026-10-16.md](phase1_cost_info_lemma_2026-10-16.md):

- $C=50,\ E_S=20,\ C_{\rm sink}=30,\ m=1,\ M=3$, with two static worlds and equal prior;
- $K=1,\ T=2C+E_S,\ q_0=0,\ \delta=0,\ \gamma=1,\ \eta=0.1$;
- requested feedback observes $R_t$, admitted feedback observes $A_t$;
- both policies use the same gauge-projected plant and overflow objective.

Only $B$ varies. Define the score-coordinate step radius

$$
\beta=\eta\gamma^2B=\eta B,
\qquad
d((x,y),(x',y'))=
\sqrt{\frac23\left(\Delta x^2-\Delta x\Delta y+\Delta y^2\right)},
\qquad
d_*=\frac1{\sqrt2}.
$$

The exact reach condition is $d((x_t,y_t),(x_{t+1},y_{t+1}))\le\beta$.
Let

$$
n(\beta)=\left\lfloor\frac{d_*}{\beta}\right\rfloor+1.
$$

The strict $+1$ is necessary: the nearest zero-overflow cells have an
infimum distance $d_*$, but their threshold boundary is assigned to the
lower-index expert and is not itself a zero-overflow point.

## 2. Geometry and cost facts used

The exact winner/cost table in the companion lemma gives these facts for all
pressures:

1. On the closed square $[-1,1]^2$, both worlds have the same admitted vector and each has overflow $E_S$.
2. Every positive per-world overflow is at least $E_S$.
3. At every pressure, equal-prior expected overflow is at least $E_S$.
4. Each world has a zero-overflow region. World 1 has such points arbitrarily close to $(1,1/2)$, and world 2 has the symmetric points arbitrarily close to $(1/2,1)$.
5. Any point outside the closed square has distance at least $d_*$ from the origin in metric $d$. Indeed, for $|x|\ge1$, $x^2-xy+y^2\ge3x^2/4\ge3/4$, with equality at $y=x/2$; the $y$-case is symmetric. The closest points of the square boundary are $(1,1/2)$ and $(1/2,1)$.

Therefore every pressure reachable in at most $\lfloor d_*/\beta\rfloor$
updates remains in the closed square. No admitted observation can distinguish the
worlds there, and no zero-overflow action is there.

## 3. Theorem: exact requested value and the first-horizon gap

**Theorem.** For every $\beta>0$ and integer horizon $H\ge1$, the
requested-feedback value is

$$
V_R(H)=E_S\min\{H,n(\beta)\}.
\tag{1}
$$
For the admitted-feedback value,

$$
V_A(H)=H E_S \quad (1\le H\le n(\beta)),
\tag{2}
$$
and

$$
V_A(n(\beta)+1)=(n(\beta)+1)E_S.
\tag{3}
$$
Consequently, the values agree for $H\le n(\beta)$, and at the first horizon
that permits a zero-overflow action the value gap is exactly

$$
V_A(n+1)-V_R(n+1)=E_S.
\tag{4}
$$
For all longer horizons, the proved bound is only

$$
V_A(H)-V_R(H)\ge E_S \qquad(H\ge n+1),
\tag{5}
$$
not a growing-gap claim.

### Proof

For $t\le n-1=\lfloor d_*/\beta\rfloor$, any trajectory from the origin
satisfies $d((0,0),(x_t,y_t))\le t\beta\le d_*$. The geometry above
places it in the closed square, where both worlds incur exactly $E_S$.
Thus no policy can pay less than $E_S$ on the first
$\min\{H,n\}$ rounds.

For the requested-policy upper bound, fix $\varepsilon>0$ small enough that
the point $z_1=(1+\varepsilon,1/2)$ is within distance $n\beta$ of the
origin and that the point reached after $n-1$ equal substeps is still inside
the closed square. Such an epsilon exists: the endpoint distance tends to
$d_*$ as $\varepsilon\downarrow0$, while
$(n-1)d_*/n<d_*$. Divide the straight segment to $z_1$ into $n$ equal
steps. Each step is feasible, the first $n-1$ visited states lie in the
closed square, and the endpoint is a zero-overflow point in world 1.
World 2 uses the symmetric endpoint $z_2=(1/2,1+\varepsilon)$.
Requested feedback identifies the world at the initial observation $R_0$,
so it selects the matching path and then holds the zero-overflow pressure.
This costs exactly $nE_S$ when $H\ge n+1$, and matches the lower bound.
If $H\le n$, staying at the origin costs $HE_S$. This proves (1).

For admitted feedback and $H\le n$, every visited pressure is in the closed
square, so every round costs $E_S$ and the observation remains common. This
proves (2). At horizon $n+1$, the first $n$ rounds still cost $E_S$ in
both worlds. The round-$n$ pressure is selected from a common history. If its
admitted vector is common, that round costs $E_S$. If it differs between
worlds, the exact cost-information lemma gives equal-prior expected overflow
at least $E_S$. Hence $V_A(n+1)\ge(n+1)E_S$, and holding the origin
attains that value. This proves (3). For $H>n+1$, the same prefix lower bound
holds, while requested feedback can hold its zero-overflow pressure, giving
(5). $\square$

## 4. What the parameterization does—and does not—show

As $B\downarrow0$, $n(\beta)=\Theta(1/B)$. The requested value grows as
$\Theta(E_S/B)$ when the horizon is long enough. The **exact gap at the
first reachable horizon remains the constant $E_S$**. At that particular
horizon, the paper's $1/(HKT)$ normalization makes the gap
$E_S/((n+1)KT)=\Theta(B)$, which vanishes as the step budget shrinks.

That first-horizon fact does not settle long horizons. The separate
probe-versus-wait theorem now gives, for the same fixed E=3 family and
sufficiently long horizons,
$V_A(H)=E_S\sqrt{2/3}/\beta+O(E_S)$ and
$V_R(H)=E_S/(\sqrt2\,\beta)+O(E_S)$. Thus the **raw long-horizon gap does
grow as $1/\beta$**; it is not the constant first-horizon gap. See
[`phase1_probe_wait_value_theorem_2026-10-16.md`](phase1_probe_wait_value_theorem_2026-10-16.md)
for the explicit policy-class lower bound and horizon condition. At the
sufficient horizon scale in that theorem, its lower bound also gives a positive
limiting normalized gap of about `0.00779` for the stated `E_S=20`, `K=1`,
`T=120` instance. That normalized statement requires `H=Theta(1/beta)`;
it does not hold uniformly for horizons that grow faster. This remains an
exact result for a specific constrained-testing instance, not yet a
Top-K/gauge result beyond that abstraction.

## 5. Reduction attack and literature boundary

For this two-world static instance, the admitted controller's exact state is
the pair (belief over the two worlds, pressure). A pressure is a deterministic
test; its admitted vector is the outcome; overflow is the outcome-dependent
test cost; and $d\le\beta$ is a movement constraint between tests. Replacing
the pressure coordinates by the corresponding test state and retaining the
same outcome, cost, and transition relation leaves the Bellman recursion and
all values unchanged. The small-$B$ theorem above uses precisely that
reachability/cost map; it has no additional claim that survives this exact
state-constrained adaptive-testing representation.

The closest cited frameworks are not exact prior solutions. Davenport et al.
study adaptively selected linear measurements whose rows belong to a finite
physically constrained set; the paper does not state this continuous movement-
constrained, outcome-costed finite-horizon control problem. Agnetis et al.
study deadline-constrained testing/search with costly tests, but their model
does not supply this pressure-induced transition geometry or overflow outcome
map. These are scope neighbors; neither establishes novelty for our
specialization. [Davenport et al., *Constrained adaptive sensing*](https://arxiv.org/abs/1506.05889),
[Agnetis et al., *Time-critical testing and search problems*](https://arxiv.org/abs/2101.05473).

**Reduction verdict:** the parameterized latency theorem is a valid exact
control result and MoE realization. It fails the current conference novelty
gate as a standalone centerpiece: its proof reduces to a two-hypothesis
state-constrained testing game with the same metric, tests, outcomes, and
costs. A distinct contribution would need a theorem showing a sharp property
of realizable Top-K score cells or the gauge metric that is stronger than the
corresponding abstract movement-constrained testing bound. No such separation
is proved here.

## 6. Next mathematical discriminator

The fixed E=3 family now has a long-horizon all-policy value sandwich, not
just a first-horizon result. Its raw gap scales as $1/\beta$ under the
explicit horizon condition, but its proof is preserved exactly by the
state-constrained adaptive-testing reduction. Do not present this as a
distinct MoE impossibility theorem.

The remaining discriminator is to generalize the geometric coefficient to
a parameterized family in $E$, $K$, or heterogeneous capacities and prove a
sharp Top-K/gauge structural statement that is not just the same induced
test metric restated. If that generalization reduces unchanged to existing
constrained sensing/testing theory, re-scope this result as an application
or stop this novelty lane. The T7 hidden-overflow-compounding proposal is
separately invalid as written; see
[`phase1_t7_trajectory_audit_2026-10-16.md`](phase1_t7_trajectory_audit_2026-10-16.md).

No experiment or parameter sweep was run for this proof.

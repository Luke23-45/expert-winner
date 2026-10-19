# Saturation-freeze theorem for the central-claim synthetic audit

> **Status and relation to the broader project.** This note states the exact
> uniform-capacity, uniform-target freeze result exercised by the synthetic
> central-claim audit on `feat/control-experiment-v3-utmost`. It is a proved
> mechanism theorem, not a claim that the full paper's top-conference theorem
> or novelty case is settled. The separate `feat/research-censored-feedback`
> branch contains the later saturation-multiplicity decision-value theorem;
> its research-status document says the class-level separation from the
> adaptive-testing benchmark remains unproved. Keep those results and claims
> distinct.

## Research claim

Under canonical per-expert admission, uniform expert capacities, a uniform
requested-load target, and global saturation with aggregate capacity shortage,
admitted-count feedback has no relative component on the pressure gauge
quotient. The admitted controller therefore cannot change relative pressure
while this regime holds. With zero pressure decay, it leaves pressure exactly
unchanged; on a fixed affinity batch, the resulting Top-K requests and
saturation state remain unchanged. Requested-count feedback, by contrast,
retains the centered requested-load error. This is a signal and control-dynamics
separation; it is not a universal performance guarantee.

The statement below is the theorem to cite for the project's central
mechanism. The multi-seed synthetic results that exercise it are reported
separately in [Empirical corroboration](#empirical-corroboration).

## Model and assumptions

There are \(E\ge2\) experts, \(T\ge1\) tokens, and a Top-\(K\) router with
\(1\le K<E\). For a fixed affinity batch and pressure vector
\(q\in\mathbb R^E\), the router chooses exactly \(K\) experts per token from
scores

\[
s_{t,e}(q)=a_{t,e}-\gamma q_e,\qquad \gamma>0,
\]

using a fixed deterministic tie rule. Let (R_e(q)) be the resulting number
of requests to expert (e). Thus

\[
\sum_{e=1}^E R_e(q)=KT.
\]

Each expert has the same integer capacity

\[
C_e=C=c\frac{KT}{E},
\]

and the target requested-load distribution is uniform, \(\mu_e=1/E\).
Admission and rejection are

\[
A_e(q)=\min\{R_e(q),C\},\qquad J_e(q)=R_e(q)-A_e(q).
\]

Pressure is represented in the canonical gauge

\[
\mathcal Q=\{q\in\mathbb R_+^E:\min_e q_e=0\},\qquad
\Pi_g(z)=z-(\min_e z_e)\mathbf 1.
\]

The two feedback vectors are

\[
\varepsilon^R(q)=\frac{R(q)}{KT}-\mu,
\qquad
\varepsilon^A(q)=\frac{A(q)}{KT}-\mu.
\]

The implementation's pressure update is

\[
q^+=\Pi_g\!\left((1-\delta)q+\alpha\varepsilon(q)\right),
\qquad \alpha=\eta\gamma>0,\quad 0\le\delta<1.
\]

Here \(\eta\) is the controller step size and \(\gamma\) is the score
pressure gain. The theorem uses their product \(\alpha\), so the conclusion
does not depend on how this positive scalar is parameterized.

## Theorem: admitted-feedback saturation freeze

**Theorem 1 (Saturation freeze and retained requested signal).** Suppose that
at a state \(q\), every expert is saturated:

\[
R_e(q)\ge C\quad\text{for every }e,
\]

and that \(0<c<1\). Then:

1. **Admitted feedback is common-mode.** Canonical admission gives
   \(A_e(q)=C\), and therefore
   \[
   \varepsilon^A(q)=\frac{c-1}{E}\mathbf 1,
   \qquad P_0\varepsilon^A(q)=0,
   \]
   where \(P_0x=x-(E^{-1}\sum_e x_e)\mathbf 1\) is the centering
   projection.

2. **The admitted pressure dynamics have no relative correction.** For any
   \(q\in\mathcal Q\),
   \[
   q^+=(1-\delta)q.
   \]
   In particular, when \(\delta=0\), \(q^+=q\). If the affinity batch is
   fixed and the same deterministic tie rule is used, the routing is then
   unchanged. Since its initial request vector remains globally saturated,
   this is an invariant frozen trajectory for the admitted controller.
   When \(\delta>0\), relative pressure contracts by \(1-\delta\); exact
   pressure freeze is not claimed.

3. **Requested feedback retains the imbalance signal.** Its entries sum to
   zero, and
   \[
   P_0\varepsilon^R(q)=\varepsilon^R(q).
   \]
   Thus, whenever \(R(q)\ne(KT/E)\mathbf 1\), requested feedback has a
   nonzero gauge-relevant component. It preserves the direction and magnitude
   of the current requested-load deviation from the uniform target.

The theorem guarantees this signal distinction and the admitted controller's
relative-pressure behavior. It does **not** by itself guarantee that requested
feedback changes a Top-K assignment at a particular step, decreases imbalance
on every trajectory, or reduces aggregate overflow.

### Proof

Summing the saturation inequalities gives

\[
KT=\sum_e R_e(q)\ge EC=cKT,
\]

so global saturation requires \(c\le1\). The theorem assumes the nontrivial
shortage case \(c<1\). For every expert, \(R_e(q)\ge C\), hence
\(A_e(q)=\min\{R_e(q),C\}=C\). Consequently

\[
\varepsilon^A_e(q)=\frac{C}{KT}-\frac1E
                 =\frac{c-1}{E},
\]

which is independent of \(e\). Since \(q\in\mathcal Q\), its minimum
coordinate is zero. The minimum coordinate of
\((1-\delta)q+\alpha(c-1)\mathbf1/E\) is therefore
\(\alpha(c-1)/E\). Applying \(\Pi_g\) subtracts this common value and
leaves \((1-\delta)q\), proving parts 1 and 2. With \(\delta=0\), the
pressure vector is unchanged; fixed affinities and deterministic routing then
produce the same request vector at the next step, so global saturation and
the same conclusion persist by induction. Finally,

\[
\sum_e\varepsilon^R_e(q)
=\frac{\sum_eR_e(q)}{KT}-\sum_e\mu_e=1-1=0.
\]

Thus \(P_0\varepsilon^R=\varepsilon^R\), and it is nonzero exactly when
the request vector is not uniform. \(\square\)

## Direct information consequence

The control result follows from a more general property of the admission
map. For known capacity \(C_e\), every saturated coordinate reports only
\(A_e=C_e\), regardless of how far \(R_e\) exceeds capacity. In particular,
for any two feasible request vectors \(R,\widetilde R\) with

\[
\min(R_e,C_e)=\min(\widetilde R_e,C_e)\quad\text{for all }e,
\]

the admitted vectors, and hence admitted feedback vectors for a fixed target,
are identical. The total rejected mass is recoverable from conservation,

\[
\sum_eJ_e=KT-\sum_eA_e,
\]

but its allocation across saturated experts is not. This identity is why the
theorem concerns the *relative allocation signal*, not ignorance of the total
amount rejected.

## Empirical corroboration

The pre-data synthetic audit used the production simulator, paired requested
and admitted controllers on identical affinity batches, and 50 seeds per
condition. All preregistered audit checks passed for suite
`20261018T132657Z` (500 runs total). In the two globally saturated shortage
conditions, admitted pressure remained at zero for every run; requested
feedback changed the aggregate request-count vector in 36/50 runs at
\(c=0.75\) and 50/50 at \(c=0.50\).

The time-mean total-variation (TV) results were:

| Capacity ratio | Requested mean TV | Admitted mean TV | Paired admitted-minus-requested TV (95% seed-bootstrap interval) | Mean overflow, requested / admitted |
|---:|---:|---:|---:|---:|
| \(c=0.75\) | 0.0364742 | 0.0422656 | 0.00579146 [0.00366969, 0.00819430] | 512 / 512 |
| \(c=0.50\) | 0.0499595 | 0.1299410 | 0.07998194 [0.06703305, 0.09395621] | 1024 / 1024 |

Positive paired differences favor requested feedback on this metric. These
intervals quantify variation over the declared synthetic generator only. The
overflow values are equal within each pair because total overflow is fixed at
\(KT-EC\) while every expert remains saturated. The experiment therefore
corroborates a conditional load-imbalance result; it does not demonstrate
overflow reduction.

Audit artifacts: `outputs/central_claim/results/20261018T132657Z/`, including
`report.md`, `claim_audit.json`, `manifest.json`, paired effects, and compressed
trajectories. The run was CPU-executed; it exercises the same deterministic
simulator logic and is not a trained-model result.

## Scope of the theorem

The established result is strong and exact within its assumptions:

- uniform capacity and uniform target;
- canonical per-expert clipping admission;
- global saturation with aggregate shortage;
- gauge-normalized pressure dynamics;
- exact freeze requires zero pressure decay; and
- the trajectory invariance conclusion additionally assumes a fixed affinity
  batch and deterministic tie-breaking.

Heterogeneous capacities, non-uniform targets, partial saturation, stochastic
or changing affinity batches, learned language-model quality, and deployment
telemetry are not covered by Theorem 1. They have separate analyses or require
separate evidence. In particular, this theorem does not claim that deployed
routers cannot observe requested counts.

The theorem establishes the saturation-induced control mechanism. The paired
synthetic study shows that this mechanism can coincide with lower requested-
load imbalance under the declared shortage workloads. Whether a broader
Top-K/gauge theorem gives a separation from state-constrained adaptive-testing
benchmarks remains a distinct theoretical question; this document does not
claim to settle it.

## Implementation convention to preserve

The current implementation in `src/moe_control/dynamics/gauge.py` uses
\(\eta\gamma\) in the pressure update, matching the paper's formal core.
The current `docs/formal_definitions/formal.md` writes the generic update with
\(\eta\) and no explicit \(\gamma\). For the zero-versus-common-mode result
above, this is only a positive rescaling and does not change the conclusion.
For quantitative flip-time statements or comparisons at a fixed numeric
\(\eta\), the convention must be reconciled explicitly; do not transfer
constants between those parameterizations without converting
\(\eta_{\mathrm{effective}}=\eta\gamma\).

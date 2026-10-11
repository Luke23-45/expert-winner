# Formal core: feedback control for capacity-limited MoE routing

**Branch:** `feat/paper-feedback-moe-routing` (based at v3 tip `787ae71`).
**Date:** 2026-10-11. **Status:** working theory document for the paper program.
**Companion documents:** `docs/formal_definitions/formal.md` (canonical
definitions, LaTeX — authoritative where the two overlap);
`docs/control_experiment_results/v3_notes/eta_flip_theorem.md` (proved
`t_flip` theorem); `src/moe_control/controllers/base.py` (exact controller
formulas — every formula below verified against code, never from memory).

## Reading guide: claim labels

Every substantive claim carries one label. No label = definition or
immediate algebra.

- **[V]** — proved in this document, proved in `formal.md`, or verified
  against frozen v1/v2 artifacts by the verifier suite. Treat as fact.
- **[S2]** — synthetic evidence from the verified v1/v2 suites
  (deterministic, CPU, E=8/K=2). Empirical, not proved.
- **[S3]** — synthetic evidence from the **exploratory** v3 suite
  (`results_v3.md` is a draft). Empirical and provisional — do not cite
  as established.
- **[I]** — qualified inference: follows from verified facts by standard
  reasoning, but not directly proved or run.
- **[O]** — open problem / obstruction: stated so the gap is explicit.

**Global scope note.** All dynamical claims are about *synthetic*
closed-loop experiments (E=8, K=2, T=1024, CPU, deterministic). Nothing
here is trained-model evidence. The program's only trained-router artifact
(the v3 toy feasibility probe) is explicitly not belief-grade and is not
used to support any theorem below.

## 0. Canonical model

**Router.** `E` experts, top-`K` routing, batch of `T` tokens. Token `t`
has affinity vector `a_t ∈ R^E`. Controller state (pressure) `q ∈ R_+^E`
with gauge fixing `min_e q_e = 0`. Pressured scores (score_sign = −1 in
all v1–v3 runs):

```
s_{t,e}(q) = a_{t,e} − γ q_e,   γ > 0.
```

`TopK_K(s)` is the hard top-K argmax set-valued map (fixed tie-breaking
rule; all statements hold for any fixed rule). `I_t(q) ∈ TopK_K(s_t(q))`
is the selected set, `r_{t,e}(q) = 1{e ∈ I_t(q)}`, and the **requested
load** is `R_e(q) = Σ_t r_{t,e}(q)`, satisfying the conservation law
`Σ_e R_e = KT` and `0 ≤ R_e ≤ T`.

**Capacity and admission.** Capacity vector `C ∈ N_0^E`. Canonical
admission `A_e(q) = min(R_e(q), C_e)` coordinatewise; rejected load
`J_e(q) = R_e(q) − A_e(q) = [R_e(q) − C_e]_+ ≥ 0`. Hence `Σ_e A_e ≤ KT`,
strict under any rejection.

**Target.** `μ ∈ Δ^{E−1}` (probability vector), the target *requested*
distribution. Uniform target: `μ_e = 1/E`.

**Projections.** Gauge projection `Π_g(z) = z − min_i(z_i)·1` (canonical
nonnegative representative of the gauge class; routing depends only on
pressure differences). Zero-sum projection `P_0(z) = z − mean(z)·1`.

**Pressure update (runner, verified in
`src/moe_control/dynamics/gauge.py`).** For feedback vector `ε = ε(q)`:

```
q⁺ = Π_g( (1−δ) q + η γ ε ),   η > 0, δ ∈ [0,1).
```

`Π_g` removes any common-mode component of `ε`: the gauge dynamics depend
only on the centered part of the feedback **[V]** (`formal.md`, §2).

**Controller feedback vectors (verified against
`src/moe_control/controllers/base.py`).** With `KT` = `top_k · tokens`:

| name | code class | feedback `ε` |
|---|---|---|
| `(R)` requested | `RequestedFeedback` | `R/(KT) − μ` |
| `(A)` admitted | `AdmittedFeedback` | `A/(KT) − μ` |
| `(A₀)` admitted_centered | `AdmittedCenteredFeedback` | `P_0(A/(KT))` |
| `(C)` capacity_relative | `CapacityRelativeFeedback` | `P_0(R/(KT) − C/(KT))` |
| `(AW)` admitted_antiwindup | `AdmittedAntiwindupFeedback` | `P_0(g)`; `g_e = A_e/(KT) − μ_e` on unsaturated `U`, `g_e = mean_U(A/(KT) − μ)` on saturated `S`; `ε = 0` if `S` = all experts |
| `(bias)` bias_integral | `BiasIntegralFeedback` | `bias_gamma · σ`, `σ_e = sign(A_e − mean(A)) ∈ {−1,0,1}`; separate bias state `b` (not gauge-projected), added to scores with sign +1, update `b ← b + ε` exactly (η=1, δ=0, identity projection) |

Saturation in `(AW)` is tested as `R_e ≥ C_e` (equivalent to `A_e = C_e`
under canonical admission — see Theorem T4).

---

## 1. Part (a): exact equivalences between controller variants

**Theorem T1 (requested vs capacity-relative) [V].**
For every `q`,
```
ε^R − ε^C = P_0(C/(KT)) − P_0(μ)        (exact vector identity)
```
Hence the gauge dynamics of `(R)` and `(C)` coincide **iff**
`P_0(C/(KT)) = P_0(μ)`, i.e. iff `C/(KT) − μ` is common-mode.

*Proof.* `ε^C = P_0(R/(KT) − C/(KT)) = P_0(R/(KT)) − P_0(C/(KT))` by
linearity, and `P_0(R/(KT)) = R/(KT) − (1/E)1` since `Σ_e R_e/(KT) = 1`.
With `ε^R = R/(KT) − μ`, subtraction gives
`ε^R − ε^C = P_0(C/(KT)) − (μ − (1/E)1) = P_0(C/(KT)) − P_0(μ)`.
The difference is a fixed vector; `Π_g` kills exactly its common-mode
part, so gauge-equivalence holds iff `P_0` of the difference is zero. ∎

*Corollaries.*
- Uniform `C = c·(KT/E)·1` **and** uniform `μ`: both `P_0` terms vanish,
  so `ε^R = ε^C` **as vectors** (stronger than gauge-equivalence). This
  is the exact coincidence the code's `gauge_equivalence_classes`
  asserts — and the theorem shows uniform+uniform is sufficient but the
  precise condition is `P_0(C/(KT)) = P_0(μ)`.
- Uniform `C` alone: `ε^C = R/(KT) − (1/E)1` — the capacity-relative
  controller is **μ-blind**; it always steers toward uniform balance on
  the gauge quotient. It coincides with `(R)` iff `μ` is uniform. This
  is exactly the T1 hetero_balanced split **[S3]**: `capacity_relative`
  (viol 0.052) targets uniform while `requested` (viol 0.0088) targets
  the non-uniform `μ`.
- Role of uniform `C`: uniformity of `C` zeroes `P_0(C/(KT))`, removing
  the capacity-heterogeneity term; non-uniform `C` makes `(C)` steer
  toward requested load *proportional to capacity* (`R/(KT) ∝ C/(KT)`
  direction), which differs from `(R)` whenever `μ` is not
  capacity-proportional.

**Theorem T2 (admitted vs admitted_centered) [V].**
For every `q`,
```
ε^A − ε^{A0} = (mean(A/(KT)) − 1/E)·1  −  P_0(μ).
```
Hence the gauge dynamics of `(A)` and `(A₀)` coincide **iff** `μ` is
uniform (`P_0(μ) = 0`). If `μ` is non-uniform they differ on the gauge
quotient by exactly `−P_0(μ)`.

*Proof.* `ε^{A0} = A/(KT) − mean(A/(KT))·1`, `ε^A = A/(KT) − μ`;
subtract and split `μ = P_0(μ) + (1/E)1`. The first term is
common-mode, killed by `Π_g`. ∎

Role of uniform `μ`: it is *necessary and sufficient* for the
gauge-equivalence the code documents. Outside uniform `μ`, `(A₀)`
optimizes equalization of admitted load while `(A)` optimizes balance
toward `μ` — different objectives, not different implementations of one.

**Theorem T3 (excess decomposition: admitted vs requested) [V].**
For every `q`, coordinatewise,
```
ε^A(q) = ε^R(q) − J(q)/(KT),    J = [R − C]_+ ≥ 0.
```
In words: admitted feedback equals requested feedback *minus the
per-coordinate censored excess*, normalized. On the gauge quotient they
coincide iff `P_0(J) = 0`, i.e. iff the excess `R_e − C_e` is identical
across all saturated experts.

*Proof.* `A = R − J` coordinatewise under canonical admission. ∎

Sharp edge case **[I]**: censoring is harmless on the gauge quotient
exactly when excess demand is uniform across experts — otherwise the
centered excess `P_0(J/(KT))` is the precise distortion admitted
feedback suffers relative to requested feedback.

**Proposition P1 (anti-windup reduction) [V]** (code docstring +
`scripts/check_antiwindup_unit.py`).
- `S = ∅` (nothing saturated): `(AW)`'s gauge update is bit-identical
  to `(A)`'s, because `P_0(g)` and `g` differ by a common-mode vector
  that `Π_g` removes.
- Global saturation (`S` = all experts): `(AW)` returns `ε = 0`
  (full integrator freeze), while `(A)`/`(A₀)` integrate the phantom
  gradients of Theorem T6.
- Partial saturation: `(AW)` gives saturated coordinates exactly `0`
  relative feedback (frozen at the unsaturated mean before `P_0`).

**Proposition P2 (bias_integral is a separate family) [V]** (from code).
`(bias)` carries a bias state, not a gauge-fixed pressure; its feedback
`bias_gamma·sign(A − mean(A))` is ordinal-only (magnitude-blind). It is
never gauge-equivalent to any pressure controller. Under global
saturation its feedback is the constant demand-blind vector
`bias_gamma·sign(C − mean(C))` — the sign-quantized analogue of the
`(A₀)` phantom (Theorem T7).

**Regime table: where the published variants coincide / diverge [V]**
(✓ = same gauge dynamics; ✗ = differ):

| regime | (R) vs (C) | (A) vs (A₀) | (R) vs (A) | (AW) vs (A) |
|---|---|---|---|---|
| uniform C, uniform μ | ✓ identical vectors (T1) | ✓ gauge (T2) | ✓ iff `J = 0` (T3) | ✓ iff `S = ∅` (P1) |
| uniform C, non-uniform μ | ✗ differ by `P_0(μ)` (T1) | ✗ differ by `P_0(μ)` (T2) | differ by `J/(KT)` (T3) | ✓ iff `S = ∅`; ✗ under saturation |
| hetero C, uniform μ | ✗ differ by `P_0(C/(KT))` (T1) | ✓ gauge (T2) | differ by `J/(KT)` (T3) | ✓ iff `S = ∅`; ✗ under saturation |
| hetero C, non-uniform μ (v3 T1) | ✗ | ✗ | ✗ | ✗ (except `S = ∅`) |

The code's `gauge_equivalence_classes` asserts the first row only; the
theorems above give the exact boundaries. `requested_leaky` and
`requested_no_projection` share the `(R)` feedback vector exactly and
differ only in dynamics (leak / projection) — separate scientific
comparisons, not duplicate findings **[V]** (code comment).

**[O-a]** No open problem: the equivalence boundaries are closed. The
live question is which side of each boundary the deployment regime sits
on — the v1/v2 uniform+uniform regime made `(R)=(C)` and `(A)=(A₀)`
*look* like four controllers; T1 shows that was a degenerate regime.

---

## 2. Part (b): information analysis — what saturation censors

**Theorem T4 (censoring fiber) [V].** Fix an observed admitted vector
`A` with known `C` (`Σ_e A_e ≤ KT`, `A_e ≤ C_e`). Let
`S = {e : A_e = C_e}` (saturated pattern) and `U` its complement. The
set of requested loads consistent with the observation is
```
F(A) = { R ∈ N_0^E : R_e = A_e ∀e ∈ U,  R_e ≥ C_e ∀e ∈ S,
         Σ_{e∈S} R_e = KT − Σ_{e∈U} A_e }.
```
That is: on unsaturated coordinates the observation reveals `R`
*exactly*; on saturated coordinates it reveals only the ordinal fact
`R_e ≥ C_e`. The lost information is exactly the position of the excess
vector `J|_S = (R − C)|_S` inside an `(|S|−1)`-simplex.

*Proof.* `A_e = min(R_e, C_e) = C_e ⇔ R_e ≥ C_e`; `A_e < C_e ⇔ R_e = A_e`.
The mass constraint fixes the simplex. ∎

**What is kept [V]:** the saturation pattern `S` itself (exactly
observable from `(A, C)` — no access to `R` needed), the exact requested
counts on `U`, and the known constants `C`, `μ`.
**What is lost [V]:** the magnitudes of excess `R_e − C_e` on `S`
(including the boundary distinction "exactly at cap" vs "strictly
over").

**Corollary C1 (sign reversal) [V]** (`formal.md`). If
`R_e/(KT) > μ_e` but `A_e/(KT) < μ_e`, then `ε^R_e > 0 > ε^A_e`:
requested feedback correctly raises pressure on an over-demanded
expert while admitted feedback lowers it.

**Remark: the saturation pattern is the ordinal content [I].** The v3
report's "admitted exploits ordinal information that AW discards" is
precisely this: `(A)`'s update on `S` is a function of the *pattern*
`S` plus the known `(C, μ)` (Theorem T5 below), while `(AW)` maps `S`
to relative zero. The pattern is binary per coordinate — that is the
entire ordinal content of the censored signal. (On `U` the signal is
not ordinal but exact — see T5.)

**[O-b]** Information-theoretic: `F(A)` characterizes what *any*
controller observing only `(A, C, μ)` can know. The optimal
partially-observed controller for this censoring (dual control /
belief over the fiber) is unformulated. `(AW)` (conditional
integration) is one heuristic; the v3 verdict shows it trades
under-correction for no-correction **[S3]** — whether any
`(A,C,μ)`-measurable feedback can do strictly better is open.

---

## 3. Part (c): partial saturation

**Theorem T5 (partial-saturation signal split) [V].** Let `S, U` be as
in T4. Then coordinatewise
```
ε^A_e = ε^R_e            for e ∈ U   (exact requested deviation),
ε^A_e = C_e/(KT) − μ_e   for e ∈ S   (demand-blind; known constants only).
```

*Proof.* On `U`, `A_e = R_e`. On `S`, `A_e = C_e`. ∎

Consequences **[V]**:
- Everything admitted feedback gets *right* under partial saturation
  comes from `U`, where it equals the requested deviation exactly.
- All distortion is supported on `S` and equals `−J_e/(KT)` there (T3).
- The gauge-relevant difference between `(A)` and `(AW)` is supported
  on `S`: `(A)` applies the pattern-dependent signal `C_e/(KT) − μ_e`
  on `S`; `(AW)` applies exactly `0` relative. Hence admitted's
  rebalancing edge over `(AW)` (e.g. saturation_windup spike-end
  0.1245/0.1191 vs 0.1680 **[S3]**) equals the control value of the
  saturation *pattern* `S` — and its windup failures (T6, T7) are the
  price: under global saturation the pattern is vacuous (`S` = all)
  and the `S`-signal becomes pure phantom.

**[O-c]** When does the `S`-signal help vs hurt? Helped in
saturation_windup (partial, transient) **[S3]**; hurt under persistent
global saturation (T6/T7). A principled switch — use the pattern signal
only when the pattern is informative — is unformulated; `(AW)`'s
all-or-nothing freeze is the current placeholder.

---

## 4. Part (d): target-aware vs target-blind — the role of `μ`

**Theorem T6 (phantom gradients under global saturation) [V].**
Assume global saturation persists (`R_e ≥ C_e ∀e`, so `A = C`), any
`δ`. Then while it persists:
```
(A):   ε^A = C/(KT) − μ            → gauge direction P_0(C/(KT) − μ),
(A₀):  ε^{A0} = P_0(C/(KT))        → gauge direction P_0(C/(KT)),
(AW):  ε = 0.
```
All three are *independent of the current requested load `R`* —
`P_0(C/(KT) − μ)` still encodes the target `μ` (target-aware,
demand-blind: pure windup), while `P_0(C/(KT))` encodes neither `R`
nor `μ` (fully blind).

*Proof.* `A = C` under global saturation; substitute into the feedback
formulas; `Π_g` removes the common mode. `(AW)` returns `0` by
construction (P1). ∎

Load-bearing distinction (corrected after external review — getting
this wrong is the cardinal sin of this track): under full saturation
the admitted signal is `P_0(C/(KT) − μ)`; it **cannot** recover the
current excess `R − C`, but its update **can** depend on the known `C`
and `μ`. The failure is information loss (T4), not a wrong formula.

**Theorem T7 (target-blind divergence under heterogeneous capacity)
[V].** Assume global saturation persists on `[0, t)`, `δ = 0`,
`q_0 = 0`, controller `(A₀)`. Then the feedback `φ = P_0(C/(KT))` is
constant and demand-blind, pressure grows linearly
`q_t = t·ηγ·(φ − min(φ)·1)` (Lemma L1 below), and:

1. *(directional)* The first routing flip in the batch (if any) moves
   one request from an expert of strictly larger capacity to one of
   strictly smaller capacity (up to measure-zero exact ties).
2. *(overflow monotonicity)* While global saturation persists, total
   overflow `O(R) = Σ_e [R_e − C_e]_+` is non-decreasing along the
   trajectory, strictly increasing at any flip whose donor is exactly
   at capacity.

*Proof.* (1) At `t = 0`, `q = 0` so scores are affinities; `e` in the
top-2 and `e'` out gives `a_{i,e} ≥ a_{i,e'}`. A flip `e → e'` needs
`γ(q_e(t) − q_e'(t)) > a_{i,e} − a_{i,e'} ≥ 0`, while
`q_e(t) − q_e'(t) = tηγ(φ_e − φ_e')`; hence `φ_e > φ_e'`, i.e.
`C_e > C_e'`. (2) One flip: `R_e ↦ R_e − 1`, `R_e' ↦ R_e' + 1`;
under saturation `ΔO = −1{R_e > C_e} + 1 ≥ 0`, strict iff
`R_e = C_e`. ∎

*Empirical instance* **[S3]** (v3 T1, hetero_shortage, all 3 seeds):
`(A₀)` viol 0.0576 → 0.41, overflow 512 → 1065–1072, saturation
fraction → 0.35–0.37, final `R` e.g. `[146, 143, 135, 135, 88, 238,
225, 938]` (seed 17): expert 7 (`C_7 = 66`, the minimum-capacity
expert, hence `φ_7 = min φ` and `q_7 ≡ 0`) absorbs the flood to 938
requests. Mechanism per T7: pressure rises fastest on the
highest-capacity experts, scores there fall, demand flees *down* the
capacity gradient — the opposite of the overflow-minimizing direction.
On hetero_balanced it is worse than no control (viol → 0.088–0.091,
overflow 122 → 314–316) **[S3]**.

**[O-d]** Post-divergence recovery: once saturation breaks, does
`(A₀)` recover? v3 shows no recovery within 800 steps (viol stays
≈0.41) **[S3]** — unproved whether recovery is slow or impossible.

---

## 5. Part (e): stability, convergence, and explicit failure conditions

### 5.1 Requested feedback: what stability means here

**Proposition P3 [V]** (`formal.md`, §7). The gauge-class update
`[q]⁺ = [q + ηγ(R/(KT) − μ)]` is a quotient subgradient step for the
convex hard Top-K potential
`H(q) = γμᵀq + (1/T)Σ_t Φ_t(q)`; `Π_g` only selects the nonnegative
representative (`H` is gauge-invariant, so subgradients agree on gauge
classes).

*Stability reading* **[I]** (classical convex analysis, not proved
in-repo): quotient subgradient descent on convex `H` converges in
objective with diminishing steps (`η_t → 0`, `Ση_t = ∞`); with constant
`η` it converges at best to an `O(η)`-neighborhood of the optimum.
`H`-convergence does **not** imply `R → KTμ`: the residual floor is the
attainability gap (whether `KTμ` is hard-Top-K-realizable on the given
affinity batch — T1's 18-token gap is unattributed between
attainability, horizon, and step size **[S3]**).

*Failure conditions for requested feedback* **[V]**:
- **(F1) Leak freeze** (Theorem T8 below): `δ > 0` caps pressure;
  if the cap sits below every flippable affinity margin, no token ever
  moves. Instance **[S2]**: `requested_leaky` (η=0.05, δ=0.05) on
  adversarial_init — `R_0 = 1024` frozen, viol 0.3750 (v2 §6; v3 C3
  re-verified at seed 42).
- **(F2) Step-size overshoot**: η = 10 limit cycle (tail pressure range
  0.0991) vs clean convergence at η ≤ 3.0 **[S2]** — consistent with
  constant-step subgradient dynamics on a nonsmooth potential (see
  obstruction O2); no contraction argument can rule it out.
- **(F3) Attainability**: exact `R = KTμ` may be unrealizable
  (`formal.md` necessary conditions `μ_e ≤ 1/K`, `KTμ_e ∈ N_0` are not
  sufficient) — a floor no controller in this family can cross **[O]**.

### 5.2 Failure conditions for admitted-family feedback

- **(F4) Saturation freeze (uniform C, global saturation) [V]**
  (`formal.md`, §5): `ε^A = ((c−1)/E)·1` is pure common-mode → `Π_g`
  kills it → with `δ = 0` no relative pressure change; with `δ > 0`
  pressure contracts geometrically to 0 while saturation persists.
  Instance **[S2]**: v1 admitted feedback exactly −0.03125, pressure
  `[0]*8` (v3 C1 re-verified on frozen artifacts + fresh seed-99
  retest).
- **(F5) Phantom windup (hetero C, global saturation) [V]** (T6):
  `(A)` integrates the demand-blind `P_0(C/(KT) − μ)` — 1.48 units of
  pressure over 800 frozen-routing steps **[S3]** (§2.2: the
  phantom-vs-freeze dissociation).
- **(F6) Target-blind divergence [V]** (T7): `(A₀)` under hetero `C`
  actively increases overflow (512 → 1065+) **[S3]**.
- **(F7) Anti-windup freeze [V]** (P1 + code): `(AW)` returns exactly
  `0` under global saturation — windup-proof but correction-proof;
  adversarial_init frozen at viol 0.3750 with `R_0 = 1024` unchanged
  **[S3]**. The honest verdict stands: conditional integration cannot
  recover information censoring destroys.
- **(F8) Projection is load-bearing numerically [S2]**: routing depends
  only on the gauge class, so identity vs gauge projection give
  identical routing in exact arithmetic; v2's `requested_no_projection`
  was bit-identical in 9/10 pairs, with 46/1000 near-tie flips from
  float32 common-mode drift (−0.7) in the 10th — numerical hygiene, not
  bookkeeping.

### 5.3 Leak-freeze theorem (new)

**Theorem T8 (leaky pressure ceiling and flip dichotomy) [V].**
Assume `δ > 0`, `q_0 = 0`, and feedback `ε` constant on `[0, t)`
(e.g. requested feedback before the first routing change). Then
exactly
```
q_t = (1 − (1−δ)^t) · (ηγ/δ) · (ε − min(ε)·1).
```
Let `m_{i,e,e'} = a_{i,e} − a_{i,e'}` be affinity margins. Then:
- **Freeze:** if `(ηγ²/δ)(ε_e − ε_e') ≤ m_{i,e,e'}` for every
  candidate triple (`ε_e > ε_e'`), **no routing flip ever occurs**
  (the asymptotic pressure gap cannot cross any margin).
- **Flip:** otherwise the first flip is the smallest `t ≥ 1` with
  `(1 − (1−δ)^t)(ηγ²/δ)(ε_e − ε_e') > m_{i,e,e'}` for some triple
  (closed form via logarithms).

*Proof.* Induction: with `v = ε − min(ε)·1 ≥ 0`, guess
`q_t = c_t·v`, `c_t = (1 − (1−δ)^t)ηγ/δ`; then
`(1−δ)q_t + ηγε = c_{t+1}v + ηγmin(ε)·1`, whose minimum coordinate is
`ηγmin(ε)`, so `Π_g` gives `c_{t+1}v`. Score gaps
`γ(q_e(t) − q_e'(t)) = γc_t(v_e − v_e')` increase monotonically to
`(ηγ²/δ)(ε_e − ε_e')`; a flip needs the gap to exceed the margin.
If the limit is below every margin, no finite `t` flips (induction on
"No flip through t−1 ⇒ ε constant through t−1 ⇒ formula holds at
t ⇒ no flip at t"); else the first crossing time is finite. ∎

This formalizes v2 §6's "provably stuck" reading of `requested_leaky`
(ceiling `(ηγ/δ)|ε|`, here with the gauge-centering the code's
informal `q* = (ηγ/δ)ε` omits) **[S2]**.

---

## 6. Extending the `t_flip` theorem: what generalizes, what resists

**Lemma L1 (general pre-flip linear regime) [V].** Assume `δ = 0`,
`q_0 = 0`, and the feedback vector `ε` is constant on `[0, t)`. Then
`q_t = t·ηγ·(ε − min(ε)·1)` (same induction as
`eta_flip_theorem.md`; the gauge min-shift is common-mode and cancels
in score differences).

*Where it applies* **[V]**: to **every** pressure controller —
`(R)`, `(C)`, `(A)`, `(A₀)`, `(AW)` — whenever its feedback is
constant pre-flip. For `(A)`/`(A₀)` under saturation, `A = C` is
constant while saturation persists, so the lemma holds with
`ε = C/(KT) − μ` (resp. `P_0(C/(KT))`) — under uniform C + uniform μ
this gives `ε` common-mode, i.e. `q_t ≡ 0`: the saturation-freeze
theorem F4 is the `t_flip` lemma's degenerate case. Non-uniform `μ`
and non-uniform `C` need no new proof: they enter only through `ε`
(the note's assumption 7 — capacity never enters pre-flip
requested dynamics — was already the general statement).

*First-flip formula* **[V]**: with `X^ε = min_{i,e,e': ε_e>ε_e'}
(a_{i,e} − a_{i,e'})/(γ²(ε_e − ε_e'))`, the first routing change over
the batch is at `t_flip = ceil(X^ε/η)`. Precision: this is the first
*routing* change; a flip that leaves `ε` invariant (e.g. a
saturated→saturated token move under admitted feedback) extends the
linear regime — after any flip, constancy of `ε` must be re-checked
before re-applying.

*Leaky extension* **[V]** (Theorem T8): with `δ > 0` the linear regime
becomes the closed-form saturating curve above, with an exact
freeze/flip dichotomy — the `t_flip` theorem's honest `δ > 0`
generalization.

*Bias-integral analogue* **[V]** (from code): with constant sign
vector `σ = sign(A − mean(A))` (constant `A` pre-flip), the
unprojected bias drifts linearly `b_t = t·bias_gamma·σ` (runner uses
η=1, δ=0, identity projection), and the first selection flip is
`t^b_flip = ceil(X^b)` with
`X^b = min_{σ_e'>σ_e} (a_{i,e} − a_{i,e'})/(bias_gamma·(σ_e' − σ_e))`
(scores use `+b`). Same proof structure, sign `+1` coupling.

**Where proof resists — named obstructions:**

- **[O1] Post-flip cascades.** After a flip changes `ε`, the system is
  a piecewise-constant vector field switching on the Top-K arrangement
  — a combinatorial partition of the gauge quotient with up to
  `C(E,K)^T` cells. Predicting flip `k+1` needs the new `ε` and new
  `X^ε`, both computable *from the post-flip state*; but the *sequence*
  is the orbit itself — no closed form, because the switching map
  (pressure → routing → feedback) has no tractable composition or
  inverse. There is also no known strictly-decreasing Lyapunov function
  through flips at constant η (`H` is convex with subgradient steps on
  the quotient, but constant-step subgradient descent on nonsmooth `H`
  is not monotone). Predicting cascades without simulating is as hard
  as simulating.
- **[O2] The η = 10 limit cycle.** The hard Top-K subgradient is
  discontinuous (not Lipschitz), so no contraction argument applies;
  classical theory gives at best `O(η)`-neighborhood convergence for
  constant-step subgradient on nonsmooth convex `H` **[I]**. The
  observed tail range 0.0991 at η = 10 vs clean basins at η ≤ 3.0
  **[S2]** is consistent with this — but *proving* the cycle (or its
  exact η-boundary) needs a cycle analysis of the specific switching
  system, which is open.
- **[O3] Attainability.** For which `(a, μ)` does hard Top-K realize
  `R = KTμ`? The 18-token T1 gap is unattributed **[S3]**; the formal
  necessary conditions are not sufficient (`formal.md` §1).

---

## 7. Per-theorem open problems (consolidated)

| # | status |
|---|---|
| O-a (equivalences) | closed — boundaries exact |
| O-b (censoring) | optimal `(A,C,μ)`-measurable controller unformulated; lower bounds open |
| O-c (partial saturation) | principled use/abandon of the pattern signal `S` unformulated |
| O-d (target-blind divergence) | post-divergence recovery: slow or impossible? |
| F3/O3 (attainability) | which `(a,μ)` admit `R = KTμ` under hard Top-K; T1 gap unattributed |
| O1 (cascades) | no closed form; as hard as simulation; no Lyapunov through flips |
| O2 (large-η cycles) | cycle analysis of the switching system open |

## 8. What this document does not claim

- No convergence of any controller to `R = KTμ` is proved beyond the
  pre-flip linear regime (L1/T8) and the quotient-subgradient structure
  (P3, whose guarantees are about the potential `H`, not the load).
- Post-flip behavior, the η ≤ 3.0 clean basin, and the η = 10 limit
  cycle remain empirical **[S2]**; §6 names exactly why.
- All dynamics are synthetic; the v3 trained-router probe is
  feasibility-only and supports nothing here.
- v3 numbers cited as **[S3]** come from a draft report on an
  exploratory suite — provisional by the owner's own constraint.

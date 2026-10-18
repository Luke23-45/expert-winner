# Formal core: feedback control for capacity-limited MoE routing

**Working branch:** `feat/research-censored-feedback` (integration target:
`feat/paper-feedback-moe-routing`). **Date:** 2026-10-17.
**Status:** working theory document for the paper program.
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

**Global scope note.** The dynamical claims below are either exact
mathematical statements under their individually stated models and
assumptions or results from synthetic closed-loop experiments. Experiment
settings differ by section; do not transfer a result outside its stated
controller, capacity, affinity, and horizon conditions. Nothing here is
trained-model evidence. The program's only trained-router artifact (the v3
toy feasibility probe) is explicitly not belief-grade and is not used to
support any theorem below.

The separate signed-bias controller `(bias)` is also evaluated in the
exploration branch's capacity-regime synthetic sweep (E=8, K=2, T=128).
That sweep uses a gauge-centered representation of the bias state and is
equivalent to an uncentered signed update for routing as long as there is no
coordinatewise clipping or other non-gauge-invariant operation. Its results
must not be attributed to the proportional pressure controllers `(R)` or
`(A)`.

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
| `(bias)` bias_integral | `BiasIntegralFeedback` | `bias_gamma · u`, `u_e = sign(mean(A) − A_e) ∈ {−1,0,1}`; separate bias state `b` (not gauge-projected), added to scores with sign +1, update `b ← b + ε` exactly (η=1, δ=0, identity projection) |

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
`bias_gamma·sign(mean(A) − A)` is ordinal-only (magnitude-blind). It is
never gauge-equivalent to any pressure controller. Under global
saturation its feedback is the constant demand-blind vector
`bias_gamma·sign(mean(C) − C)` — the sign-quantized analogue of the
`(A₀)` phantom (Theorem T7).

**Proposition P2a (saturated-set invariance for signed bias) [V].** Assume
uniform per-expert capacity `C`, canonical admission `A_e=min(R_e,C)`, and
the signed bias update with the bias maintained in the zero-mean gauge
`b∈1^⊥`:
```
u_e = sign(mean(A) − A_e),
b⁺ = P_0(b + αu),   α > 0.
```
At any step, let `S={e:R_e≥C}`. For every `e,f∈S`,
```
b⁺_e − b⁺_f = b_e − b_f.
```
If `S=[E]`, then `A=C·1`, `u=0`, and `b⁺=b`: the complete update freezes.
If a common leakage factor `λ` is added as `b⁺=P_0(λb+αu)`, then
`b⁺_e−b⁺_f=λ(b_e−b_f)` for all `e,f∈S`.

*Proof.* For `e∈S`, canonical admission and uniform capacity give
`A_e=C`, hence all such coordinates have the same update
`u_e=sign(mean(A)−C)`. The zero-mean projection subtracts the same scalar
from every coordinate, so it cancels in any pairwise difference. With
leakage, the old difference is multiplied by `λ`. Under global saturation,
all admitted counts equal `C`, so `mean(A)=C`, `u=0`, and the no-leak update
leaves `b` unchanged. ∎

This proposition is a property of the signed-bias family only. It proves
neither divergence nor a general closed-loop failure under partial
saturation: it says that the controller cannot change relative bias gaps
within the currently saturated set in that step. The four-capacity ring
sweep in the exploration branch checks the pairwise-gap identity
numerically; it is not the proof of the identity.

**Corollary P2b (global saturation is absorbing and batch-overflow optimal)
[V].** Assume a fixed affinity batch, deterministic Top-K tie-breaking,
uniform capacity `C`, canonical per-expert admission, `EC≤KT`, and the
zero-mean signed-bias update in P2a. If at time `t` every expert is
saturated, then for every `s≥t` the bias and request vector remain fixed,
and per-step overflow equals `KT−EC`. Moreover, no state or controller can
have lower one-step overflow under the same per-expert capacities.

*Proof.* At global saturation, `A=C·1`, so `u=0`; as `b∈1^⊥`, P2a gives
`b⁺=b`. Fixed affinities and deterministic routing therefore reproduce the
same request vector, which is still globally saturated. Induction gives
absorption. Its overflow is `Σ_e(R_e−C)=KT−EC`. For any request vector,
`Σ_e A_e≤EC`, hence `Σ_e J_e=KT−Σ_e A_e≥KT−EC`; thus the absorbing
state attains the per-step lower bound. ∎

P2b is a conditional attainment theorem, not a hitting-time theorem: it
does not establish that the controller reaches global saturation from an
arbitrary initial state. The `C=28` ring experiment supplies a finite-plant
hitting observation only; its class-level extension and comparison to
adaptive testing remain open.

**Proposition P2c (homogeneous Top-1 obstruction to universal hitting)
[V].** Let `E=2`, `K=1`, and let all `T` tokens have the same affinity gap
`d=a_1-a_2>0`. Use deterministic Top-1 routing, tie-breaking in favor of
expert 1, uniform integer capacity `0<C<T/2`, and start at `b_0=0`. Under
the signed-bias update in P2a, every batch routes all tokens to exactly one
expert. The process never enters the globally saturated set
`R_1≥C,R_2≥C`. Moreover, requested-count and admitted-count sign feedback
produce identical bias and routing trajectories, each with per-step overflow
`T-C`.

Writing `y_t=d+b_{t,1}-b_{t,2}`, the exact recurrence is
```
y_{t+1} = y_t - 2α,  if y_t ≥ 0,
y_{t+1} = y_t + 2α,  if y_t < 0.
```
After finitely many steps it enters a two-cycle `{r, r-2α}` for the unique
`r∈[0,2α)` congruent to `d` modulo `2α`.

*Proof.* If `y_t≥0`, all tokens request expert 1 (including the tie by the
specified rule), giving `R=(T,0)` and `A=(C,0)`. Since `T>C>0`, both count
vectors have positive deviation on coordinate 1 and negative deviation on
coordinate 2 relative to their means. Thus both signals give `u=(-1,+1)`,
and their difference update is `-2α`. If `y_t<0`, all tokens request expert
2, so `R=(0,T)`, `A=(0,C)`, both signals give `u=(+1,-1)`, and the
difference update is `+2α`. This proves the recurrence and equality of the
requested/admitted trajectories by induction. The map moves toward zero in
increments of `2α` until it reaches `{r,r-2α}`, which is invariant. At each
step one expert receives zero requests, so global saturation is impossible;
the one occupied expert admits `C` and overflow is `T-C`. ∎

P2c is a boundary case, not a performance lower bound: identical token
affinities make split routing infeasible under the shared deterministic
Top-1 bias. It shows that a theorem claiming global-saturation hitting or a
strict admitted-versus-requested sign-feedback advantage for every Top-1
family is false. A positive family theorem needs explicit affinity diversity
or other reachability assumptions.

**Proposition P2d (exact capacity-optimality advantage on a margin family)
[V].** For every integer `C≥3`, let `E=2`, `K=1`, `T=2C+2`, and use uniform
capacity `C`. All tokens have one of four affinity gaps
`d_t=a_{t,1}-a_{t,2}` with multiplicities:
```
d_t/α =  1 : C−2 tokens,
d_t/α =  3 : 3 tokens,
d_t/α =  5 : C−1 tokens,
d_t/α = −1 : 2 tokens,
```
where `α>0` is the signed-bias update rate. Start at `b_0=0`, use Top-1
with expert 1 winning ties, and update by P2a. Let `J_H` be cumulative
overflow over `H≥1` routing rounds. Then
```
J_H(admitted) = C + 2(H−1),
J_H(requested) = C + 2 ceil((H−1)/2) + 3 floor((H−1)/2),
J_H(no update) = H C.
```
Thus admitted feedback attains the per-round capacity lower bound `2` after
one update, beats requested sign feedback by `floor((H−1)/2)`, and beats no
update by `(H−1)(C−2)`. The admitted controller reaches global saturation
after one update and remains there; requested feedback cycles between request
loads `(C+2,C)` and `(C−1,C+3)`.

*Proof.* Write `x=b_1-b_2`. A token routes to expert 1 exactly when
`d_t+x≥0`. At `x=0`, `R=(2C,2)`. Both the requested and admitted count
signals have signs `(-1,+1)` because `C≥3`, so the first update gives
`x=-2α`. There, exactly the 3-token and `(C−1)`-token positive-margin groups
route to expert 1, so `R=(C+2,C)` and `A=(C,C)`. Admitted feedback is zero
and fixes the bias. The resulting per-round overflow is `2=KT-2C`, the
lower bound from total capacity.

Requested feedback at `x=-2α` still has signs `(-1,+1)`, because the
requested load is `(C+2,C)` and its mean is `C+1`; hence `x=-4α`. At that
point only the `(C−1)`-token group routes to expert 1, giving
`R=(C−1,C+3)`. Requested feedback reverses to `(+1,-1)`, returning to
`x=-2α`. The two states therefore repeat, with overflow `2` and `3`.
Without updates, `x=0` persists and overflow is `C` each round. Summing the
initial round and these subsequent per-round costs gives the formulas. ∎

This is an exact parameterized Top-1 controller comparison with a real
capacity-optimality gap. It remains a deliberately structured, fixed-affinity
family, and its finite outcomes have an exact polyhedral active-testing
representation. It does not by itself establish novelty over adaptive
testing or a top-conference contribution. Its value here is to provide a
positive theorem with explicit affinity-diversity conditions alongside the
negative boundary P2c; any broader claim must generalize these conditions and
survive the benchmark reduction.

**Theorem P2e (complete one-dimensional admitted-sign dynamics) [V].** Let
`E=2`, `K=1`, `T` be fixed, `0<C<T/2`, affinities be static, and ties be
resolved deterministically in favor of expert 1. Let
`d_t=a_{t,1}-a_{t,2}` and `x=b_1-b_2`; define the monotone request-count
function
```
r(x) = #{t : d_t+x ≥ 0},
```
and the capacity-feasible interval
```
G_C = {x : C ≤ r(x) ≤ T−C}.
```
For the signed admitted-count update `u_e=sign(mean(A)−A_e)` with update
rate `α>0`, the scalar state obeys exactly
```
x⁺ = x+2α,  if r(x)<C,
x⁺ = x,     if C≤r(x)≤T−C,
x⁺ = x−2α,  if r(x)>T−C.
```
Consequently, on the invariant lattice `L=x_0+2α Z`, the controller reaches
`G_C` if and only if `L∩G_C` is nonempty. On reaching it, the state is fixed
and every subsequent batch has overflow `T−2C`, which is the minimum
possible under total capacity `2C`. If `L∩G_C=∅`, the orbit eventually
alternates between adjacent lattice points with request counts below `C` and
above `T−C`.

For comparison, the requested-count sign update obeys
```
x⁺ = x+2α, if r(x)<T/2,
x⁺ = x,    if r(x)=T/2,
x⁺ = x−2α, if r(x)>T/2.
```
Thus admitted feedback stops at the first capacity-feasible lattice point,
whereas requested feedback continues toward exact request balance. They
coincide outside `G_C` until the first entry; inside `G_C`, only the admitted
controller is guaranteed to stop. This gives an exact finite-horizon
trajectory characterization for the static two-expert Top-1 family.

*Proof.* Since all token scores depend on the scalar difference `x`, the
number routed to expert 1 is the nondecreasing threshold count `r(x)`.
If `r<C`, then `A=(r,C)`, so the admitted sign is `(+1,−1)` and `x` rises
by `2α`. If `r>T−C`, then `A=(C,T-r)`, so the sign is `(−1,+1)` and `x`
falls by `2α`. If `C≤r≤T−C`, then `A=(C,C)`, the sign is zero, and `x`
does not move. Thus the dynamics move one lattice point at a time toward
the interval `G_C`, stop on it, or—if no lattice point lies in the interval—
alternate across it. In `G_C`, total admitted count is `2C`, so overflow is
`T−2C`; for every state `sum(A)≤2C`, giving the matching lower bound. For
requested feedback, the same calculation with `R=(r,T-r)` changes sign at
`r=T/2` and gives the second recurrence. ∎

P2d is an explicit instance of P2e where `L∩G_C` is hit after one update,
while requested feedback leaves that set and incurs a two-cycle. P2c is a
case where `G_C` is unreachable on the state lattice, so neither the
absorption guarantee nor a strict admitted-feedback advantage applies.
Although P2e characterizes an entire static Top-1 family, the model is
one-dimensional and its finite threshold map is representable by the
independent polyhedral testing benchmark. Novelty beyond that benchmark is
still unestablished.

**Theorem P2f (a Top-2 admitted-sign all-horizon comparison) [V].** For every
integer `m≥1`, take `E=3`, `K=2`, `T=20m`, uniform capacity `C=10m`, and
replicate `m` times each row of the base affinity multiset
`(0,5,11/10)` once, `(0,101,100)` ten times, and `(2,6/5,0)` nine times.
Start from zero bias, use Top-2 with score `a+b`, and apply the signed update
`b⁺=P0(b+α sign(mean(L)−L))`, where `L=A` or `R`. For every
`α∈(1/5,11/40)`, admitted feedback first reaches global saturation at batch
3; requested feedback first reaches it at batch 8; no feedback does not
reach it in the first nine batches. Over those same nine batches,
`J_9(A)=93m`, `J_9(R)=98m`, and `J_9(none)=99m`. Hence admitted feedback
saves `5m` overflow assignments against requested feedback and `6m` against
no feedback over nine batches. More generally, all arms tie through horizons
`H≤3`; for every `H≥4`, admitted feedback has strictly lower cumulative
overflow than both requested feedback and no feedback. Its gap versus no
feedback is exactly `(H−3)m`; its gap versus requested feedback is exactly
`(H−3)m` for `4≤H≤8` and at least `5m` for `H≥9`. The exact proof and the
paired strict-margin perturbation audit are in
[`top2_signed_bias_separation_theorem_2026-10-17.md`](top2_signed_bias_separation_theorem_2026-10-17.md)
and
[`top2_signed_bias_separation_results_2026-10-17.md`](top2_signed_bias_separation_results_2026-10-17.md).
This is a fixed-family Top-2 result for the signed expert-bias
controller, not the proportional pressure controller. The all-horizon
extension is specific to this fixed family and does not imply a uniform
positive normalized gap as `H→∞`, a universal signal ranking, or defeat the exact polyhedral outcome-map
representation of finite instances. Commonly scaling all affinities and the
update rate by `1/250` leaves the route sequence unchanged and places the
registered compact gain interval at `[0.0009,0.001]`, including the
canonical `bias_gamma=0.001` value. The exact-rational horizon audit through
`H=100` is reported in
[`top2_all_horizon_results_2026-10-17.md`](top2_all_horizon_results_2026-10-17.md).

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
F(A) = { R ∈ {0,…,T}^E : R_e = A_e ∀e ∈ U,
         C_e ≤ R_e ≤ T ∀e ∈ S,
         Σ_{e∈S} R_e = KT − Σ_{e∈U} A_e }.
```
That is: on unsaturated coordinates the observation reveals `R`
*exactly*; on saturated coordinates it reveals only the ordinal fact
`R_e ≥ C_e`. The feasible fiber is a bounded integer slice of a simplex:
the bounds `R_e ≤ T` follow from Top-K's per-token no-duplicate rule.

*Proof.* `A_e = min(R_e, C_e) = C_e ⇔ R_e ≥ C_e`; `A_e < C_e ⇔ R_e = A_e`.
The mass constraint fixes the simplex. ∎

**What is kept [V]:** the saturation pattern `S` itself (exactly
observable from `(A, C)` — no access to `R` needed), the exact requested
counts on `U`, and the known constants `C`, `μ`.
**What is lost [V]:** the allocation of excess `R_e − C_e` across `S`
(including the boundary distinction "exactly at cap" vs "strictly
over"). The total excess is fixed by mass conservation; its feasible
coordinate values are bounded above by `T − C_e`.

**Theorem T4a (one-batch Top-K realizability and exact fiber size) [V].**
Fix integers `E ≥ K ≥ 1`, `T ≥ 1`, capacities `C_e ≥ 0`, and a feasible
admitted-count vector `A` under `A_e = min(R_e,C_e)`. Let
`S = {e : A_e = C_e}` and let `U` be the remaining experts, and define
`D = KT − Σ_{e∈U} A_e − Σ_{e∈S} C_e`. Then every integer vector in
`F(A)` is realizable as the requested-count vector of a Top-K assignment
for some affinity matrix at pressure `q=0`. Consequently, the exact
number of requested-count vectors compatible with `A` is
```
             [x^D]  ∏_{e∈S} (1 + x + … + x^(T−C_e)),
```
with the coefficient interpreted as zero when `D < 0` or
`D > Σ_{e∈S}(T−C_e)`.

*Proof.* Necessity of `F(A)` follows from T4 and `0 ≤ R_e ≤ T`. For
sufficiency, take any `R ∈ F(A)`. It has `0 ≤ R_e ≤ T` and
`Σ_e R_e = KT`. By the [Gale–Ryser criterion](https://doi.org/10.4153/cjm-1957-044-3)
for a zero-one matrix with prescribed row and column sums, there is a
`T × E` incidence matrix with
every row sum `K` and column sums `R`: for each `j ≤ K`, the sum of the
largest `j` column sums is at most `jT`, since each `R_e ≤ T`; for
`j > K`, that sum is at most the total `KT`. These are all the Gale–Ryser
inequalities for row sums `(K,…,K)`. Interpret row `t`'s ones as the
`K` experts selected by token `t`. At `q=0`, set affinity to `1` on those
experts and `0` on the others. Since exactly `K` entries equal `1`, hard
Top-K selects precisely that row's ones (for any fixed tie rule). This
realizes `R`. Finally, for each `e ∈ S`, write `R_e=C_e+d_e`; then
`0 ≤ d_e ≤ T−C_e` and `Σ_{e∈S} d_e=D`. The generating-function
coefficient counts exactly these integer allocations. ∎

This is a **one-batch, across-affinity-matrices** statement. It does not
say that one fixed affinity batch realizes every member of the fiber as
pressure varies. Thus it quantifies the static clipping ambiguity but
does not settle the multi-round root-arrangement or controller-value
questions. One-batch Top-K count feasibility alone adds no restriction
beyond total mass and `R_e ≤ T`; a stronger *MoE-specific novelty* result
must use fixed-affinity dynamics, cross-token score geometry, or a non-count
objective.

**Theorem T4b (minimum exact signal for the requested gauge update) [V].**
Fix an admitted observation `(A,C)` with nonempty fiber `F(A)` from T4 and
assume `eta*gamma > 0`. The known quantities at the controller include
`q`, `mu`, `A`, `C`, `K`, and `T`. Consider any extra deterministic message
`Z` computed from the hidden request vector `R` that must let the controller
reproduce exactly the next gauge state of the requested-feedback update
```
q_R^+ = Pi_g((1-delta)q + eta*gamma*(R/(K*T) - mu))
```
for every `R ∈ F(A)`. Then `Z` must be injective on `F(A)`. Consequently,
the message alphabet must contain at least `|F(A)|` symbols, requiring at
least `ceil(log2 |F(A)|)` worst-case fixed-length bits. This bound is
attainable by sending an index of `R` in `F(A)`. Equivalently, the centered
rejected-load vector `P_0(J)`, `J=R-A`, is a sufficient signal; given the
known total `sum(J)=K*T-sum(A)`, it uniquely determines `J` and hence the
requested update.

By T4a, every member of `F(A)` is realizable by a Top-K assignment at one
fixed pressure when the affinity matrix may vary. Therefore this minimum
alphabet bound is tight for the one-batch family of Top-K plants consistent
with `(A,C)`. It does not assert that every fiber member is realizable under
one fixed affinity matrix as pressure varies, that this is the minimum
signal for overflow-optimal control, or that the bit bound is new as a
generic communication-complexity principle.

*Proof.* For any two requests `R,R' ∈ F(A)`, the two pre-projection update
vectors differ by `eta*gamma*(R-R')/(K*T)`. The gauge projection identifies
two vectors exactly when their difference is common-mode. Since both
requests have the same total `K*T`, a common-mode difference between them
must be zero. Hence distinct `R,R'` produce distinct next gauge states for
every fixed `q`; a message that merges them cannot reproduce both updates.
Thus `Z` must be injective, giving the alphabet lower bound by counting.
For sufficiency, an index transmits the full request member. Alternatively,
on the fiber the total rejected load is fixed. If two rejected vectors have
the same `P_0(J)`, their difference is common-mode, and equality of their
known totals forces the difference to be zero. So `P_0(J)` reconstructs
`J` and recovers `R=A+J`. ∎

For example, with `K=1`, `T=E+1`, `C=1` per expert, and `A=1` per expert,
the fiber consists of the `E` vectors `R=1+e_i`. Exact reproduction of the
requested gauge update therefore requires `ceil(log2 E)` bits in the
worst case. The exact synthetic check is specified in
[`minimal_signal_audit_2026-10-17.md`](minimal_signal_audit_2026-10-17.md),
with its output recorded in
[`minimal_signal_results_2026-10-17.md`](minimal_signal_results_2026-10-17.md).

**Corollary T4c (exact signal alphabet in a uniform Top-1 shortage family)
[V].** Let `K=1`, `C_e=1`, `T=E+D` for integers `E≥2`, `D≥1`, and observe
`A_e=1` for all experts. Then the clipping fiber has
```
|F(A)| = binomial(E + D - 1, D),
```
so the minimum fixed-length message reproducing the requested gauge update
has `ceil(log2 binomial(E+D-1,D))` bits. In particular, for `D/E → rho > 0`,
the bit count is
```
E*((1+rho)*log2(1+rho) - rho*log2(rho)) + O(log E).
```

*Proof.* Write `R_e=1+d_e`. The fiber constraints reduce to nonnegative
integers `d_e` summing to `D`. Since `d_e≤D≤T-1`, the per-expert bound
`R_e≤T` is inactive. Stars and bars gives the binomial cardinality, and T4b
gives the exact message count. The asymptotic expression follows from
Stirling's formula. T4a realizes every such request vector by a Top-1
affinity batch, but does not assert realization by a single fixed batch. ∎

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

**Theorem T6a (finite exit from saturation under a strict phantom slope
gap) [V].** Let `E>K≥1`, `delta=0`, fixed affinities `a[t,e]`, positive
integer capacities `C_e`, and initial pressure `q_0` be globally
saturated under the canonical per-expert rule. Run the canonical
proportional admitted controller `(A)`. Define
```
h = C/(K*T) − mu,     v = P_0(h),     alpha = eta*gamma^2,
p_0 = gamma*q_0.
```
Assume `v ≠ 0` and the `K`th and `(K+1)`st smallest coordinates of `v`
are strictly separated. Let `M` be the `K` experts with the smallest
coordinates of `v`. For every token `t`, `i ∈ M`, and `j ∉ M`, set
```
theta[t,i,j] = (p_0[i] − p_0[j] − (a[t,i] − a[t,j]))
               / (alpha*(v[j] − v[i])),
N_sep = max(0, 1 + max_{t,i,j} floor(theta[t,i,j])).
```
Then the first state index `tau` at which global saturation fails is
finite and satisfies `tau ≤ N_sep`.

*Proof.* While a state is globally saturated, `A=C`, so the feedback is
the constant `h`. Gauge projection removes its common mode, hence in the
score-penalty quotient the update is translation by `alpha*v`. By
induction, as long as saturation has not failed, the state at index `n`
has the same score differences as `p_0+n*alpha*v`.

For `i∈M` and `j∉M`, strict separation gives `v[j]−v[i]>0`, and their
score difference along this line is
```
s[t,i](n) − s[t,j](n)
 = a[t,i] − a[t,j] − p_0[i] + p_0[j]
   + n*alpha*(v[j] − v[i]).
```
By the definition of `N_sep`, this difference is strictly positive for
every such pair and every token at all integer `n≥N_sep`. Thus every
token's Top-K set at `N_sep` is exactly `M`. Every expert outside `M`
then has requested count zero; because its capacity is positive, global
saturation fails at that state. If the actual trajectory left saturation
earlier, the claimed bound already holds; otherwise its state agrees with
the saturated open-loop line through `N_sep`, so it must leave by then.
∎

The theorem supplies an exact arrangement-based upper bound, not a
controller-performance guarantee. It excludes the uniform-capacity,
uniform-target freeze because that case has `v=0`; it says nothing about
post-exit recovery or whether the resulting overflow is better than
requested feedback or no feedback. The controlled check is specified in
[`admitted_phantom_exit_protocol_2026-10-17.md`](admitted_phantom_exit_protocol_2026-10-17.md).

**Theorem T6b (capacity-slack order-statistic exit bound) [V].** Under the
assumptions of T6a, fix the router's deterministic total tie order. Choose an
expert `e*` maximizing `v_e`; the strict `K`/`K+1` gap implies that at least
`K` experts have strictly smaller `v` coordinates. Consider the linear
score-penalty path `p_n = p_0 + n*alpha*v`, which equals the actual path as
long as global saturation persists. For each token `t` and expert `j != e*`,
let `n[t,j]` be the first integer `n >= 0` at which `j` ranks ahead of `e*`
for token `t` on this path, including the fixed tie order; set `n[t,j]=+inf`
if it never does. Let `ell[t]` be the `K`th smallest of these `E-1`
thresholds. Let
```
m = R_e*(q_0) - C_e* + 1,
N_e* = the m-th smallest ell[t] over tokens t routed to e* at q_0.
```
Then `N_e*` is finite and the first state index `tau` at which global
saturation fails satisfies
```
tau <= N_e* <= N_sep.
```

For lower-index-wins ties, the thresholds are explicit. Write
`d_j=alpha*(v_e* - v_j) >= 0` and
`theta[t,j]=(p_0[j]-p_0[e*]-(a[t,j]-a[t,e*]))/d_j` when `d_j>0`.
If `j<e*`, then `n[t,j]=max(0,ceil(theta[t,j]))`; if `j>e*`, then
`n[t,j]=max(0,floor(theta[t,j])+1)`. When `d_j=0`, set `n[t,j]=0` if
`j` already ranks ahead at state zero and `+inf` otherwise.

*Proof.* On the linear path, every score difference
`s[t,j](n)-s[t,e*](n)` has slope
`alpha*(v_e* - v_j) >= 0`. With a fixed tie order, an expert's rank relative
to `e*` therefore cannot change from ahead to behind. Thus the number of
experts ahead of `e*` for any token is nondecreasing, and a token not routed
to `e*` initially cannot later start routing to it. Once `K` experts rank
ahead, that token no longer routes to `e*`. At `n=ell[t]`, at least `K`
experts do so. The strict slope gap gives at least `K` experts in `M` with
strictly smaller slope than `e*`, so every such token has finite `ell[t]`.
By `N_e*`, at least `m` of the initially routed tokens have left `e*`, and
none have entered; hence the linear-path count is at most
`R_e*(q_0)-m=C_e*-1`. If the actual dynamics have not already left global
saturation, their state agrees with the linear path through that index and
this count forces exit. Finally, T6a's `N_sep` makes every token select only
`M`, so in particular all initially routed tokens to `e*` have left; it
therefore bounds the same order statistic. ∎

The bound is capacity-aware: it depends on the number of initial requests
above `e*`'s capacity and the earliest score-order events needed to remove
that excess. It remains an event-time result for one fixed plant, not an
overflow-performance comparison or a separation from the polyhedral
active-testing benchmark. The exact-rational audit is recorded in
[`admitted_phantom_exit_results_2026-10-17.md`](admitted_phantom_exit_results_2026-10-17.md).

**Corollary T6c (strict overflow cost after admitted-feedback saturation
exit).** Assume the canonical proportional controller `(A)`, `delta=0`,
uniform target `mu_e=1/E`, `q_0=0`, and integer `n=KT/E`. Suppose the initial
strict Top-K request counts are `R_e(q_0)=n`, all capacities satisfy
`0<C_e<=n`, and their sorted values obey `C_(K)<C_(K+1)`. Let `tau` be the
first state at which the admitted-feedback trajectory is not globally
saturated, and let `N_sep` be the T6a score-arrangement bound. Define the
aggregate-shortage floor `D=KT-sum_e C_e>0`. Then requested feedback and no
feedback remain at `q_0` and incur overflow `D` at every state; admitted
feedback exits by `tau<=N_sep`; and at every state of its trajectory

```text
J_A(t)-D = sum_e(C_e-A_e(q_t)) >= 0.
```

This is strict at the first unsaturated state. Hence admitted feedback has
strictly greater cumulative overflow than requested feedback and no feedback
at every horizon `H>tau`, in particular for all `H>N_sep`.

*Proof.* The initial balanced request makes the requested update zero; no
feedback also holds `q_0`. Since `C_e<=n`, both stay globally saturated and
have overflow `D`. While admitted feedback is saturated, its signal equals
the constant vector `C`; the capacity gap puts the K smallest coordinates
of `P_0(C/(KT)-mu)` strictly below the others. T6a therefore gives
`tau<=N_sep`. For any Top-K request vector, `sum_e R_e=KT` and
`A_e=min(R_e,C_e)`, so `J=KT-sum_e A_e` and
`J-D=sum_e(C_e-A_e)`. This quantity is nonnegative and is positive whenever
some expert is unsaturated. Summing over states proves the claim. □

The expanded statement, assumptions, and exact controlled audit are in
[`balanced_saturation_cost_theorem_2026-10-17.md`](balanced_saturation_cost_theorem_2026-10-17.md)
and [`balanced_saturation_cost_experiment_results_2026-10-17.md`](balanced_saturation_cost_experiment_results_2026-10-17.md).

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

*Bias-integral analogue* **[V]** (from code): while the admitted count
vector is constant, define `σ = sign(A − mean(A))`. The implementation
returns `u = −σ`, so the unprojected bias drifts as
`b_t = b_0 − t·bias_gamma·σ` (scores use `+b`). For a token whose
initially selected expert `w` is above the Top-K boundary and an initially
unselected expert `l` is below it, their score gap is
`d_{w,l}(t) = a_{i,w} + b_{0,w} − a_{i,l} − b_{0,l}
− t·bias_gamma·(σ_w − σ_l)`. A crossing can occur only when
`σ_w > σ_l`. The exact first integer routing-change time is the minimum,
over tokens and such selected/unselected pairs, of the smallest integer
`n ≥ 1` for which `d_{w,l}(n) < 0`, or `d_{w,l}(n) = 0` and the fixed
tie rule selects `l` over `w`. This strict/tie-aware definition is needed:
`ceil(d_{w,l}(0)/(bias_gamma·(σ_w−σ_l)))` alone can return a boundary
contact at which the router has not yet changed its selection. Before that
first change, the feedback is constant and the linear bias formula is exact.

**Theorem T6c (finite exit from global saturation for signed admitted bias)
[V].** For a static affinity batch with positive capacities, the signed
admitted-bias controller has constant slope
`u=sign(mean(C)−C)` throughout any globally saturated episode. If the
`K`th-largest and `(K+1)`st-largest coordinates of `u` are strictly
separated, let `M` be the top-`K` slope experts and set
```
N = max_{t,i∈M,j∉M} max(0, floor((a[t,j]+b[0,j]−a[t,i]−b[0,i]) /
                                 (bias_gamma*(u_i−u_j))) + 1).
```
Then the episode's first unsaturated state occurs by index `N`: if
saturation persisted, the bias would be `b[0]+n*bias_gamma*u`, and at `N`
every token strictly selects only `M`, leaving all positive-capacity experts
outside `M` unrequested. Full assumptions, proof, and exact controlled audit
are in
[`signed_bias_saturation_exit_theorem_2026-10-17.md`](signed_bias_saturation_exit_theorem_2026-10-17.md)
and
[`signed_bias_saturation_exit_results_2026-10-17.md`](signed_bias_saturation_exit_results_2026-10-17.md).
This bounds one uninterrupted episode only; it does not rule out repeated
saturation, bound long-run bias, or rank controllers by total cost.

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

## 9. Capacity clipping and potential geometry [V]

This section records the existing C3 structural line in the canonical
per-expert model. It does not change the controller definitions above.

Fix a static batch and a regular Top-K arrangement facet across which (m)
token-routes move from expert (i) to expert (j). Write the requested
count vectors on the two sides as

```text
R+ = R− − m e_i + m e_j.
```

Under canonical admission (A_e=min(R_e,C_e)), define the source decrease
and destination increase

```text
d_i = min(R−_i,C_i) − min(R−_i−m,C_i)
d_j = min(R−_j+m,C_j) − min(R−_j,C_j).
```

The admitted feedback field is (g_A=P_0(KT\mu-A)), so its facet jump is

```text
g_A+ − g_A− = P_0(d_i e_i − d_j e_j).
```

For (E\ge3), a mismatch (d_i\ne d_j) gives the jump a component
tangent to the Top-K facet. A continuous potential affine on the adjacent
routing cells would require the gradient jump to be normal to their common
facet; therefore a single mismatch rules out such a potential, including a
convex subgradient potential. Conversely, if every regular facet matches,
the jumps are nonnegative multiples of their facet normals, and the field on
open cells is the gradient of a convex piecewise-affine potential. The exact
criterion, including simultaneous exchanges and the (E=2) case, is proved
in [`admitted_field_facet_criterion_2026-10-17.md`](admitted_field_facet_criterion_2026-10-17.md).

### High-probability corollary for exact-total heterogeneous capacities [V]

Fix (E\ge3), (1\le K<E), and a sequence of integer capacities with
\(\sum_e C_e(T)=KT\) and limits (C_e(T)/T\to c_e). Assume the limiting
profile is nonuniform. Then (sum_e c_e=K), so there are (i,j) with
\(c_i<K/E<c_j).

Construct one distinguished token with a regular facet at (q=0) exchanging
(i\to j): exactly (K-1) experts score above the (i,j) tie, and the
remaining experts score below it. Let all other (T-1) affinity rows be iid,
exchangeable, and continuous across experts. At (q=0), each filler token
selects expert (e) with probability (K/E). If (X_e) is its aggregate
count, the law of large numbers gives (X_e/T\to K/E) in probability.

At the distinguished facet,

```text
d_i = 1{X_i < C_i(T)},    d_j = 1{X_j < C_j(T)}.
```

Thus (\Pr(d_i=0)\to1), (\Pr(d_j=1)\to1), and
\(\Pr(d_i\ne d_j)\to1\). By the facet criterion, the entire admitted field
is non-potential with probability tending to one. On this event, the squared
tangential jump is \((E-2)/(2E)\) in count units. Full assumptions and the
proof are in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).

### Unconditioned iid-affinity version [V]

The construction can be made from an entirely iid affinity matrix rather
than inserting a distinguished token. For fixed `E>=3`, `1<=K<E`, and a
nonuniform exact-total capacity limit `C_e(T)/T -> c_e`, choose experts with
`c_i<K/E<c_j`. Among `T` iid uniform-affinity rows, with probability tending
to one there is a row whose `i,j` affinity gap is at most `T^(-1/2)`, whose
midpoint lies in `[5/12,7/12]`, and for which exactly `K-1` other experts
score above that midpoint. Select the first such row and set
`q_i-q_j=(a_i-a_j)/gamma`, centered so the tied pair has zero average
pressure relative to other experts. This creates a regular Top-K facet with
probability one under the continuous model. Conditioning on the selected
row changes the other rows' zero-pressure request means by only
`O(T^(-1/2))`; the pressure perturbation changes only `o_p(T)` filler
routes. Thus the two exchanged experts' other-token request fractions both
converge to `K/E`. The cross-mean capacities then imply `d_i -> 0` and
`d_j -> 1` in probability, so the full admitted field is non-potential with
probability tending to one.

Writing `Delta=min(K/E-c_i,c_j-K/E)>0`, the proof gives, for all sufficiently
large `T`, a failure bound
`exp(-b_{E,K} sqrt(T)) + 5 exp(-Delta^2 T/32)`, where
`b_{E,K}=binom(E-2,K-1)(5/12)^(E-2)/3`. Thus the rate depends explicitly on
the capacity-straddling margin and on the fixed router dimensions.

The full conditioning and concentration proof is in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).
The finite-size, exact-rational-grid check is in
[`unconditioned_random_facet_results_2026-10-17.md`](unconditioned_random_facet_results_2026-10-17.md).

The same construction gives a multiplicity bound without selecting only the
first candidate. Let `B_t` be the proof-defined near-tie/rank event for row
`t` and `N_T=sum_t 1{B_t}`. The events are independent and
`P(B_t)>=b_{E,K}/sqrt(T)`. For each candidate, conditional on that row, its
other rows remain iid, and the chance that either exchanged request count
fails to straddle its capacity is at most
`4 exp(-Delta^2*T/8)` for all sufficiently large `T`. A union bound and a
Chernoff bound therefore give at least `b_{E,K} sqrt(T)/2` distinct regular
mismatched facets except with probability at most
\[
\exp(-b_{E,K}\sqrt T/8)
+\frac43\sqrt T\exp(-\Delta^2T/8).
\]
The facets are distinct almost surely under continuous affinities. The
preregistered exact-grid audit counts every candidate and observes mean
mismatch counts `1.334, 2.726, 5.332, 10.664` for `T=64,256,1024,4096`
respectively, with zero no-clipping mismatches. Protocol, results, and
plant-level data are in
[`many_facet_random_affinity_protocol_2026-10-17.md`](many_facet_random_affinity_protocol_2026-10-17.md),
[`many_facet_random_affinity_results_2026-10-17.md`](many_facet_random_affinity_results_2026-10-17.md),
and `results/many_random_facets/plants.csv`. This counts a
proof-defined subset, not all facets or their overall fraction.

### Expected admitted-field curl under a stochastic Top-1 router [V]

This gives a smooth expectation-level version of the same per-expert clipping
mechanism. Assume `K=1`, iid tokens, and raw scores
`a_{t,e}=theta_e+G_{t,e}`, where `G_{t,e}` are independent Gumbel random
variables with scale `lambda>0`. At pressure `q`, the request probability is
`pi_e(q)=softmax((theta-gamma*q)/lambda)_e`; therefore
`R_e(q)~Binomial(T,pi_e(q))` marginally. For
`h_{T,C}(p)=E[min{Binomial(T,p),C}]`,
\[
h'_{T,C}(p)=T\Pr\{\operatorname{Binomial}(T-1,p)<C\}.
\]
Writing `alpha_e(q)=Pr{Binomial(T-1,pi_e(q))<C_e}`, the Jacobian of the
normalized expected admitted-count vector is exactly
\[
D_q\left(E[A(q)]/T\right)=\operatorname{diag}(\alpha(q))D_q\pi(q).
\]
With no clipping, every `alpha_e=1` and `D_q pi` is symmetric. With
heterogeneous clipping, expert-specific attenuation can make the projected
Jacobian nonsymmetric on the gauge quotient.

An explicit asymptotic witness takes `E=3`,
`pi(0)=(1/2,3/10,1/5)`,
`C(T)=(2T/5,T/2,T/10)` for multiples of ten, and `theta_e=lambda log(pi_e(0))`.
The capacities sum to `T`, while the admitted-response factors converge to
`alpha(0)=(0,1,0)`. For tangent directions
`x=e_1-e_3` and `y=e_2-e_3`, the antisymmetric derivative is
\[
\lim_{T\to\infty}\left[x^T D_q(E[A]/T)y-y^T D_q(E[A]/T)x\right]
=-\frac{9\gamma}{100\lambda}\ne0.
\]
Thus the expected admitted feedback is not locally the gradient of any
scalar potential on the pressure quotient for all sufficiently large `T`.
The exact finite formula, proof, and numerical evaluation are recorded in
[`expected_admitted_curl_theorem_2026-10-17.md`](expected_admitted_curl_theorem_2026-10-17.md).

This statement is a structural response result, not a controller-value
comparison. Its attenuation factor is the generic derivative of a clipped
binomial count; the Top-1 softmax geometry supplies `D_q pi`. It does not by
itself establish a value-of-information break-even, a real-router gain, or
separation from the outcome-map benchmark.

**Boundary.** Non-potentiality does not imply instability, worse overflow,
or a training benefit. It also does not defeat the exact outcome-map
benchmark, which can represent every finite arrangement. The
complete-arrangement experiment in
[`full_arrangement_facet_audit_results_2026-10-17.md`](full_arrangement_facet_audit_results_2026-10-17.md)
is finite synthetic support for this structural line, not a performance
result. Cyclic monotonicity as a test for convex-gradient structure is
classical; MoE potential-based balancing is also prior art. For example,
[\(\phi\)-Balancing](https://proceedings.mlr.press/v306/chen26br.html)
optimizes a population-level potential of expected routing probabilities,
whereas this result concerns a fixed-batch hard Top-K count field after
per-expert clipping. Mouzouni's [mean-field congestion-game analysis of MoE
routing](https://arxiv.org/abs/2604.04230) likewise gives a Rosenthal
potential for a population equilibrium and interprets the balance-quality
tradeoff through that potential; it does not analyze the finite-batch
admitted-count field after clipping. These are scope distinctions, not
novelty clearance. The cyclic-monotonicity criterion itself is classical,
and the remaining paper-level test is whether the clipped Top-K structure
produces a result that survives the exact outcome-map benchmark. [Maximum
Score Routing](https://arxiv.org/abs/2508.12801) is another capacity-aware
neighbor, but it solves a batch assignment problem using min-cost maximum
flow and a SoftTopk operator; it does not study the pressure-state feedback
field considered here. This distinction also does not clear novelty.

## 10. Two-step overflow consequence under the canonical pressure law [V]

The exact asymptotic result is stated and proved in
[`heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`](heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md).
For $E=3$, $K=1$, uniform target, $\gamma=1$, zero leak, and static iid
continuous affinities, take exact-total capacities
\[
C/T=(1/3-r,\;1/3+\sigma,\;1/3+r-\sigma),\qquad 0<r<1/3,\quad 0\le\sigma\le r.
\]
For every fixed $\eta>0$ with $d=\eta r<1$, the expected two-step overflow
gap between admitted and requested proportional pressure feedback satisfies
\[
\lim_{T\to\infty}\frac{1}{T}\mathbb{E}
[(J_0^A+J_1^A)-(J_0^R+J_1^R)]=d-d^3/3>0,
\]
along batch sizes making all capacities integral. The limit is independent of
the split parameter $s$. The gain is created entirely by the second routing
step; step-zero costs are paired and identical. The limit is independent of
the split parameter $\sigma$. The proof handles reuse of
the same affinity matrix at both steps via uniform convergence of the
finite-VC Top-1 winner class, rather than assuming independence between the
random updated pressure and the second-step assignments.

Two controlled exact-grid experiments are recorded in
[`heterogeneous_capacity_two_step_results_2026-10-17.md`](heterogeneous_capacity_two_step_results_2026-10-17.md)
and [`heterogeneous_capacity_family_results_2026-10-17.md`](heterogeneous_capacity_family_results_2026-10-17.md).
The first tests the original $r=\sigma=1/6$ slice; the second sweeps three $r$
values, three capacity splits, four gains, and five batch sizes. Both use
paired static affinity matrices and exact integer score comparisons. These
finite experiments support but do not prove the theorem.

**Boundary.** This is a two-step expected overflow comparison for a stated
iid Top-1 family and the canonical proportional update. It is not a theorem
for every causal controller or every affinity distribution, does not measure
the cost of collecting requested counts, does not imply trained-model quality,
and does not defeat the exact outcome-map benchmark. It adds a direct cost
consequence inside the existing formal model; it does not close the
class-level novelty gate.

## 11. Arbitrary fixed expert count: two-step Top-1 overflow consequence [V]

The preceding three-expert formula extends to every fixed `E>=2`, without
changing the routing law, controller, clipping rule, or cost. Let `K=1`,
`gamma=1`, `mu=1/E`, `delta=0`, `q_0=0`, and draw one static affinity matrix
with iid `U[0,1]` entries, reused at both routing steps. Set exact-total
capacities to
\[
C_1/T=1/E-r,\qquad C_e/T=1/E+\sigma_e\ (e\ge2),
\qquad 0<r<1/E,\quad \sigma_e\ge0,\quad\sum_{e=2}^E\sigma_e=r.
\]
For any fixed `eta>0` with `d=eta*r<1`, the expected paired overflow gap
satisfies
\[
\lim_{T\to\infty}\frac1T\mathbb E[(J_0^A+J_1^A)-(J_0^R+J_1^R)]
=d-\frac{d^E}{E}>0.
\]
The limit is independent of how the compensating capacity `r` is split
among experts `2,...,E`. The second-step population request probability of
the short-capacity expert under admitted feedback is
\[
p_1(d)=\int_0^1\min(1,x+d)^{E-1}\,dx
=1/E+d-d^E/E;
\]
the requested update tends to zero, and its second-step overflow remains
the original shortage fraction `r`. The common-batch dependence is handled
by uniform convergence of the finite-VC Top-1 winner class, as detailed in
the proof.

The full assumptions and proof are in
[`top1_e_expert_two_step_overflow_theorem_2026-10-17.md`](top1_e_expert_two_step_overflow_theorem_2026-10-17.md).
The preregistered finite-grid experiment is in
[`top1_e_expert_overflow_protocol_2026-10-17.md`](top1_e_expert_overflow_protocol_2026-10-17.md),
with its results in
[`top1_e_expert_overflow_results_2026-10-17.md`](top1_e_expert_overflow_results_2026-10-17.md).
It supports positive paired gaps across its registered cells, while showing
substantial finite-size deviation from the asymptotic magnitude at `E=8,16`.

**Boundary.** This extends the MoE family result in expert count, but remains
Top-1, two-step, and specific to iid continuous affinities with the stated
capacity pattern. It is not an optimal-policy or telemetry-price theorem and
does not escape exact finite-instance outcome-map simulation. It strengthens
the original-model cost consequence, not the class-level novelty claim.

## 12. Arbitrary fixed Top-K: two-step overflow consequence [V]

The same two-step construction extends to every fixed `E>=2` and
`1<=K<E`. Keep `gamma=1`, uniform target, zero leak, `q_0=0`, and the same
iid uniform affinity matrix at both steps. Choose exact-total capacities
`C_1/T=K/E-r`, `C_e/T=K/E+sigma_e` for `e>=2`, with
`sum_{e>=2} sigma_e=r` and `0<r<min(K/E,1-K/E)`. Under the canonical update
`q_1^L=Pi_g(eta*(L_0/(K*T)-mu))`, set `d=eta*r/K` and require `0<d<1`.
Then
\[
\lim_{T\to\infty}\frac1T\mathbb E[(J_0^A+J_1^A)-(J_0^R+J_1^R)]
=\Phi_{E,K}(d)-K/E>0,
\]
where
\[
\Phi_{E,K}(d)=d+\int_d^1\sum_{j=0}^{K-1}
\binom{E-1}{j}(1-y)^j y^{E-1-j}\,dy.
\]
This is the Top-K inclusion probability of the short-capacity expert after
the admitted-feedback pressure shift. `Phi(0)=K/E` and
`Phi'(d)=Pr[Binomial(E-1,1-d)>=K]>0`. The Top-1 result in section 11 is the
special case `K=1`, for which the gap is `d-d^E/E`.

The complete proof, exact rational evaluation, preregistered design, and
finite-size results are in
[`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md),
[`topk_e_expert_overflow_protocol_2026-10-17.md`](topk_e_expert_overflow_protocol_2026-10-17.md),
and [`topk_e_expert_overflow_results_2026-10-17.md`](topk_e_expert_overflow_results_2026-10-17.md).

The Uniform affinity assumption is not necessary for positivity. If the
common iid affinity law has a continuous, strictly increasing CDF `F`, replace
the Uniform inclusion formula by
`p_F(d)=integral G_(E,K)(F(x+d)) dF(x)`, where
`G_(E,K)(u)=sum_(j=0)^(K-1) binom(E-1,j)(1-u)^j u^(E-1-j)`. Strict
monotonicity gives `p_F(d)>K/E` for every `d>0`; hence the same two-step limit
is `p_F(d)-K/E>0`. The full derivation and paired Uniform/Gaussian/Logistic/
Gumbel controlled check are documented in
[`topk_e_expert_two_step_overflow_theorem_2026-10-17.md`](topk_e_expert_two_step_overflow_theorem_2026-10-17.md),
[`topk_nonuniform_affinity_protocol_2026-10-17.md`](topk_nonuniform_affinity_protocol_2026-10-17.md),
and [`topk_nonuniform_affinity_results_2026-10-17.md`](topk_nonuniform_affinity_results_2026-10-17.md).

**Boundary.** The theorem is a fixed-family asymptotic expected cost
comparison for two steps, not an all-policy guarantee or a telemetry-price
result. The registered experiments support its positive direction but have
finite-size deviations. The theorem does not escape exact finite-instance
outcome-map simulation or establish the class-level conference claim.

## 13. Long-run population overflow under admitted feedback [V]

For the canonical proportional update, uniform target, zero leak, and exact-
total capacities `C_1/T->K/E-r`, `C_e/T->K/E+r/(E-1)` for `e>=2`, the
large-batch population dynamics reduce to a scalar relative pressure `x_n`
when token affinities are iid from a common positive bounded density. The
admitted-feedback recurrence is

```text
x_(n+1)=x_n + eta/[K*(E-1)] * ((E-1)*r-(P_F(x_n)-K/E)),
```

where `P_F(x)` is the Top-K inclusion probability of the short expert when
all rivals have pressure `x`. Under
`eta<=K*(E-1)/(||f||_infinity*(E-1)*binom(E-2,K-1))`, this state converges to
the unique root `P_F(x_*)=K/E+(E-1)r`, while requested feedback stays at zero
population pressure. For every fixed finite `H`, the iterated large-batch
cumulative overflow gap is `sum_(n<H)(P_F(x_n)-K/E)`; taking `H->infinity`
after `T->infinity` gives average gap `(E-1)r` per token per batch. The proof,
protocol, and finite-batch audit are in
[`topk_long_run_admitted_overflow_theorem_2026-10-17.md`](topk_long_run_admitted_overflow_theorem_2026-10-17.md),
[`topk_long_run_admitted_overflow_protocol_2026-10-17.md`](topk_long_run_admitted_overflow_protocol_2026-10-17.md),
and [`topk_long_run_admitted_overflow_results_2026-10-17.md`](topk_long_run_admitted_overflow_results_2026-10-17.md).

**Finite-batch evidence and boundary.** The corrected static-batch runner
implements the cumulative pressure update and its paired means track the
population prediction through `H=64` (119/126 nominal intervals cover it;
the aggregate `H=64` ratio is .998). A separate fresh-batch experiment
compares resampling with static reuse and reports both against the exact
finite-`T` mean-feedback recurrence. The earlier finite-batch report was
invalid because its update helper reset pressure each round; the corrected
results supersede it. These experiments support the theorem over the
registered grid but do not prove fixed-`T` infinite-horizon convergence or a
joint nonasymptotic bound. The result still does not establish universal
signal dominance or class-level benchmark separation. See
[`topk_long_run_admitted_overflow_results_2026-10-17.md`](topk_long_run_admitted_overflow_results_2026-10-17.md)
and [`topk_fresh_batch_closed_loop_results_2026-10-17.md`](topk_fresh_batch_closed_loop_results_2026-10-17.md).


## 14. Capacity attenuation of the expected admitted Top-K field [V]

For iid token affinity vectors at a fixed pressure, let `p_e(q)` be expert
`e`'s one-token Top-K inclusion probability. Its requested count has marginal
law `Binomial(T,p_e(q))`, so under the canonical per-expert rule
`A_e=min(R_e,C_e)`,

```text
alpha_e(q) = Pr[Binomial(T-1,p_e(q)) < C_e]
D P0(E[A/(K*T)-mu]) = (1/K) P0 diag(alpha(q)) Dp(q).
```

This is an exact finite-batch derivative identity. When `C_e/T -> c_e`, the
attenuation tends to one for `p_e<c_e` and to zero exponentially for
`p_e>c_e`; the boundary case needs a second-order capacity specification.
For positive capacity the finite-`T` marginal law remains identifying because
`Pr[A_e=0]=(1-p_e)^T`; the theorem is about mean-signal sensitivity, not exact
non-identifiability.

Under iid standard Gumbel Top-1 affinities with `E=3`, `T=6`, and uniform
exact-total capacities `C_e=2`, at choice probabilities
`p=(1/2,1/3,1/6)` the quotient curl of expected admitted feedback in directions
`e1-e3` and `e2-e3` is exactly `-29/2187`. The no-clipping and symmetric-state
controls have zero curl. The exact proof and 72-cell deterministic numerical
audit are in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md),
its [protocol](topk_expected_admission_jacobian_protocol_2026-10-17.md),
[results](topk_expected_admission_jacobian_results_2026-10-17.md), and
[`../../scripts/run_topk_expected_admission_jacobian.py`](../../scripts/run_topk_expected_admission_jacobian.py).

**Boundary.** This is a one-step expected-field theorem for iid tokens and
per-expert clipping. It does not establish finite-batch closed-loop benefit,
universal controller failure, information-theoretic non-identifiability,
telemetry price, or separation from the outcome-map benchmark. Clipping
attenuation is generic; whether its Top-K quotient-curl consequence yields a
new family-level theorem beyond prior clipped-feedback theory is still open.

## 15. Request sufficiency under at most one saturated expert [V]

Let `R in Z_{>=0}^E` satisfy `sum_e R_e=K*T`, and let
`A_e=min(R_e,C_e)`. If no coordinate is at capacity, `R=A`. If exactly one
coordinate `s` is at capacity, then the request vector is still exactly
recoverable from admitted telemetry and known capacities:

```text
R_e=A_e                           for e != s,
R_s=K*T-sum_(e != s) A_e.
```

Thus every requested-feedback update, for any known target, can be exactly
emulated by an admitted-only controller on this regime. The proof is direct:
all unsaturated coordinates are unmodified by clipping, and Top-K request
mass conservation determines the remaining coordinate. This is a sufficient
condition; multiple coordinates at capacity may or may not leave ambiguity.

### Capacity-relative one-short family

Fix `E>=2`, `1<=K<E`, `p=K/E`, iid affinities with a common continuous
strictly positive bounded density, `gamma=1`, zero leak, and exact-total
capacities with fractions

```text
C_1/T -> p-r,
C_e/T -> p+r/(E-1),  e=2,...,E,
0<r<min(p,(1-p)/(E-1)).
```

Let `Q(x)` denote expert 1's population Top-K selection probability when
its score is penalized by `x` relative to the other experts. It decreases
continuously from `p` to zero. Under the formal capacity-relative requested
update `P_0((R-C)/(K*T))`, the population pressure difference
`x=q_1-q_e` for any rival follows

```text
x_(n+1)=x_n+eta*E/[K*(E-1)]*(Q(x_n)-(p-r)),  x_0=0.
```

If `eta*E/[K*(E-1)] * sup_(x>=0)|Q'(x)| <= 1`, the sequence increases
without overshooting the unique root `Q(x_*)=p-r`. Until the root, expert 1
alone is saturated and every rival is strictly below capacity. The admitted
vector therefore recovers the full requested vector at every state in any
fixed finite prefix, and an admitted-only reconstructed controller follows
the same capacity-relative pressure path exactly. Population overflow
decreases to zero, hence its long-run Cesaro average is zero.

For `K=1` and standard Gumbel affinities,
`Q(x)=1/(1+(E-1)exp(x))`. In the controlled `E=4,r=1/8` instance,
`x_*=log(7/3)` and `eta=1` satisfies the sufficient step bound. The exact
proof and eight-step paired static-batch experiment are in
[`single_saturation_signal_reconstruction_theorem_2026-10-17.md`](single_saturation_signal_reconstruction_theorem_2026-10-17.md),
[`capacity_relative_reconstruction_experiment_protocol_2026-10-17.md`](capacity_relative_reconstruction_experiment_protocol_2026-10-17.md),
and [`capacity_relative_reconstruction_experiment_results_2026-10-17.md`](capacity_relative_reconstruction_experiment_results_2026-10-17.md).

**Boundary.** The positive overflow gap under the earlier uniform-target
updates is real for those update laws, but it is not an irreducible
information gap in this one-short family. This result separates
multi-saturation censoring from target mismatch; it does not establish a
universal optimal policy, physical telemetry price, trained-model benefit,
or separation from the exact outcome-map benchmark.

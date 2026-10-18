# Finite-horizon all-policy gap for the Top-1 E-world family

**Status:** proof derived from the existing all-pressure pair-separation
inequality and the existing all-state no-hedging lemma; its exact-DP audit
passed on 156 parameter/horizon cells. This is a theorem for the stated Top-1
family, not a general Top-K theorem or a novelty claim beyond adaptive testing.

## Model and prior results used

Use the canonical static E-world construction in
[`phase1_h3_direction.md`](phase1_h3_direction.md), with `N>=2` regular
experts and one sink, `K=1`, batch size `T=NC+E_S`, uniform prior over the
`N` worlds, initial pressure `q_0=0`, and capacities `C` on each regular
expert and `C_sink` on the sink. Assume
\[
 E_S\le C_{sink}<C-E_S/2,
 \qquad L=E_S+C-C_{sink}.
\]
Both information regimes use the same gauge-projected pressure dynamics,
same bounded zero-sum update set, and same cumulative raw overflow cost.
The first round is common to the admitted policy and costs exactly `E_S`.

Two established facts are used:

1. **Pair-separation cost (PS).** For every pressure `q` and every
   consistent support `U` with its uniform posterior,
   \[
   \mathbb E[J(q,W)\mid W\in U]\ge
   \frac L2\left(|U|-\frac1{|U|}\sum_{B\in\mathcal P_q(U)}|B|^2\right),
   \]
   where `P_q(U)` is the partition induced by the admitted count vector.
   The proof is in
   [`phase1_eworld_pair_separation_gate_2026-10-16.md`](phase1_eworld_pair_separation_gate_2026-10-16.md).
2. **No hedging.** At every pressure, at most one world has overflow
   strictly below `E_S/2`. This is the all-pressure block-counting lemma in
   [`phase1_h3_direction.md`](phase1_h3_direction.md).

## Theorem

Let `H>=2` costed rounds, and define the number of post-initial rounds
`D=H-1` and constants
\[
 a=\frac{L(N-1)}2,\qquad b=\frac{E_S}4.
\]
For every causal randomized admitted-feedback policy, even with unrestricted
pressure movement,
\[
 V_A(H)\ge E_S+\frac{abD}{a+b(D-1)}.
 \tag{1}
\]
This lower bound also holds for any smaller reachable pressure-action set.
If `delta=0` and the shared update budget satisfies
\[
 B\ge\frac{M\sqrt{1-1/(N+1)}}{\eta\gamma^2},
 \tag{2}
\]
the requested-feedback controller can identify the world from `R_0`, reach
its zero-overflow pressure in one update, and hold it. Hence
`V_R(H)=E_S` and
\[
 V_A(H)-V_R(H)\ge\frac{abD}{a+b(D-1)}
 \ge\frac12\min\left\{\frac{L(N-1)}2,
                           \frac{E_S(H-1)}4\right\}>0.
 \tag{3}
\]

For fixed `L/E_S` satisfying the capacity assumptions, (3) is
`Omega(min{E_S H,LN})` up to absolute constants. The bound saturates with
the number of worlds at fixed `N`; it makes no unbounded-in-horizon claim.

## Proof against every causal admitted policy

Condition on the policy's private random seed and current admitted history.
The posterior is uniform over the consistent world support because the prior
is uniform and observations are deterministic for a fixed pressure. Averaging
over private randomization at the end gives the same bounds for randomized
policies.

At the start of the `D` post-initial rounds the support has size `N`. Let
`U_t` denote the support before the `t`th such action. For any chosen
pressure, the expected next support size is
\[
 \mathbb E[|U_{t+1}|\mid U_t,q_t]
 =\frac1{|U_t|}\sum_{B\in\mathcal P_{q_t}(U_t)}|B|^2.
\]
Thus (PS), summed conditionally over all `D` actions, telescopes to
\[
 \mathbb E\sum_{t=1}^{D}J_t
 \ge\frac L2\left(N-\mathbb E|U_{D+1}|\right).
 \tag{4}
\]
Let `tau` be the number of actions up to and including the first one that
leaves a singleton support, or `+infinity` if this does not happen by the
horizon. Put `p=Pr(tau<=D)`. The terminal support is one on that event and
at most `N` otherwise, so (4) implies
\[
 \mathbb E\sum_{t=1}^{D}J_t\ge\frac L2p(N-1)=ap.
 \tag{5}
\]

Before each of the `min(tau,D)` actions the support is nonsingleton. The
no-hedging lemma implies that at least `|U_t|-1` of its worlds have
overflow at least `E_S/2`; averaging under the uniform posterior gives
conditional expected overflow at least
\[
 \frac{|U_t|-1}{|U_t|}\frac{E_S}{2}\ge\frac{E_S}{4}=b.
\]
The event that support is nonsingleton before an action is determined by
past observations. Therefore
\[
 \mathbb E\sum_{t=1}^{D}J_t
 \ge b\,\mathbb E[\min(tau,D)]
 \ge b\bigl(p+(1-p)D\bigr)
 =b\bigl(D-(D-1)p\bigr).
 \tag{6}
\]

Combining (5) and (6), every policy has post-initial cost at least
`max{ap,b(D-(D-1)p)}`. Since the assumptions imply
`a>=L/2>3E_S/4>b`, minimizing this maximum over `0<=p<=1` occurs where
the two affine terms meet, at
\[
 p_* = \frac{bD}{a+b(D-1)}\in[0,1].
\]
The common value is `abD/(a+b(D-1))`, proving (1). For (3), use
\[
 \frac{abD}{a+b(D-1)}
 \ge\frac{abD}{a+bD}
 \ge\frac12\min\{a,bD\}.
\]

For the requested upper bound, the initial requested vector identifies the
world. A pressure with relative shift strictly between the low and high
affinity margins sends the extra low-margin block to the sink while retaining
the high-margin baseline block. Its centered pressure norm is less than
`M sqrt(1-1/(N+1))/gamma`; (2) makes the corresponding zero-sum update
feasible. All requests then fit capacity. With `delta=0`, zero later updates
hold this pressure and incur zero additional overflow. Thus the requested
value is exactly the unavoidable initial `E_S`. \(\square\)

## What this settles and what it does not

This proves the missing **finite-horizon, all-causal-policy lower bound** for
the explicit realizable Top-1 E-world family. The proof does not assume that
the admitted controller must identify the world: it interpolates between
policies that keep uncertainty and pay repeatedly, and policies that acquire
information and pay for it. It also explicitly includes arbitrary private
randomization.

It does not prove a general result for `K>1`, arbitrary affinities, changing
worlds, or the broad controller class in the paper's full model. The fixed
E-world system still has an exact outcome-cost adaptive-testing
representation, and pair-separation/test-cost arguments have substantial
prior art. Therefore this closes the G3 proof gap for the named family, but
does not by itself close the **conference novelty** gate. That requires an
equation-level literature assessment of this exact finite-horizon bound and
a demonstration that the Top-1 realizability constraint yields a result not
captured by the relevant adaptive-testing theory.

An exact DP validation is specified in
[`eworld_finite_horizon_lower_bound_protocol_2026-10-18.md`](eworld_finite_horizon_lower_bound_protocol_2026-10-18.md)
and reported in
[`eworld_finite_horizon_lower_bound_results_2026-10-18.md`](eworld_finite_horizon_lower_bound_results_2026-10-18.md).

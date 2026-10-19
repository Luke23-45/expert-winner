# The eta x first-flip-step invariant, derived (v3 T4)

**Status:** theorem proved for the stated assumptions; verified against the
v1 sweep artifacts (exact match on all four etas at seed 17) and
**predicted prospectively** for seeds 23/42 and etas 0.15/0.3 below --
those runs had not executed when this note was committed.

## Setup

Shortage scenario: E=8, K=2, T=1024, uniform capacity, uniform target
mu = 1/8, requested controller, delta = 0, gamma = 1, step size eta.
Affinity tensor `a` (float32 in runs); pressure `q_0 = 0`.

## Lemma (pre-flip linear pressure growth)

Let `R` be the requested counts and `eps = R/(K*T) - mu`. As long as no
routing change has occurred, `R` (hence `eps`) is constant across steps,
and the pressure evolves as

    q_t = t * eta * gamma * (eps - min(eps))

*Proof.* By induction. `q_0 = 0`. The update is
`q_{t+1} = Pi_g(q_t + eta*gamma*eps)` with `Pi_g(z) = z - min(z)*1`.
`eps` is exactly zero-sum (`sum R/(KT) - sum mu = 1 - 1 = 0`).
Assume `q_t = t*eta*gamma*(eps - m)`, `m = min(eps)`. Then
`q_t + eta*gamma*eps = eta*gamma*((t+1)*eps - t*m)`, whose minimum
coordinate is `eta*gamma*((t+1)*m - t*m) = eta*gamma*m` (attained where
`eps_e = m`). Subtracting it gives `(t+1)*eta*gamma*(eps - m)`. QED.

Crucially, the gauge min-shift `-min(eps)` is a **common-mode** constant:
it cancels in every score difference, so routing sees only
`q_e(t) - q_e'(t) = t*eta*gamma*(eps_e - eps_e')`.

## Theorem (first-flip time)

For token `i` with pre-flip top-2 experts `{e1, e2}`, pressured scores are
`s_{i,e}(t) = a_{i,e} - gamma*q_e(t)` (score_sign = -1). The token's top-2
set first changes at the smallest integer `t >= 1` with

    gamma^2 * t * eta * (eps_e - eps_e') >= a_{i,e} - a_{i,e'}

for some `e in {e1,e2}`, `e' not in {e1,e2}` with `eps_e > eps_e'`.
Hence, with

    X = min_{i,e,e'} (a_{i,e} - a_{i,e'}) / (gamma^2 * (eps_e - eps_e')),

the first routing-change step over the whole batch is

    t_flip(eta) = ceil(X / eta),   i.e.   eta * t_flip in [X, X + eta).

`R` changes if and only if some token's top-2 set changes (counts are
selection sums), so the first count change coincides with the first
top-2 flip. `X` is a pure function of the affinity tensor and the
step-0 counts -- no dynamics need to be simulated.

## Assumptions and limits (read before citing)

1. **delta = 0.** A leak breaks the linear growth (pressure would
   asymptote to `(eta*gamma/delta)*eps` instead).
2. **Requested feedback with R constant pre-flip.** True by definition of
   "first" flip; the feedback is then exactly constant. Does not apply to
   admitted feedback (censored) or bias_integral (state-dependent sign).
3. **gamma^2 scaling explicit.** The derivation keeps gamma symbolic; the
   numeric predictions below use gamma = 1.
4. **Exact arithmetic vs float32.** The proof is in real arithmetic. Runs
   compute scores in float32 (`affinity.float32 - gamma*q.float32`) while
   `X` above was computed in float64. Near the argmin boundary this can
   shift the observed flip by ~1 step; the verifier therefore allows
   `|t_obs - ceil(X/eta)| <= 2` rather than exact equality. (Empirically
   the v1 seed-17 observations matched `ceil(X/eta)` exactly.)
5. **Tie rule.** Exact score ties have measure zero under continuous
   noise; the deterministic stable-sort tie rule does not affect the
   argmin.
6. **"35.2" is seed-17-specific.** `X` depends on the affinity tensor:
   X = 35.115 (seed 17), 34.622 (seed 23), 36.457 (seed 42). The
   seed-independent invariant is `eta * t_flip = X_seed`, not the number
   35.2. The v1 report's "35.2" was seed 17's `X` rounded.
7. **Uniform capacity is not actually needed** -- capacity never enters
   the pre-flip requested-feedback dynamics. The theorem holds for any
   capacity vector (and any target), as long as no routing change has
   yet occurred.

## Predictions (committed before the prospective runs executed)

Computed by `v3_notes/predict_flip_time.py` from the regenerated affinity
tensors (pure functions of the scenario seeds; no run artifacts used).

| seed | X       | eta=0.05 | eta=0.1 | eta=0.15 | eta=0.2 | eta=0.3 | eta=0.4 |
|------|---------|----------|---------|----------|---------|---------|---------|
| 17   | 35.1151 | 703      | 352     | **235**  | 176     | **118** | 88      |
| 23   | 34.6217 | 693      | 347     | 231      | 174     | 116     | 87      |
| 42   | 36.4574 | 730      | 365     | 244      | 183     | 122     | 92      |

Bold = prospective (no run existed when predicted): seed-17 etas 0.15/0.3
(`flip_theorem_prospective` runs); the rest are verified by the
`flip_invariant_test` runs (seeds 23/42, etas 0.05-0.4).

## Verification against v1 (pre-existing artifacts)

v1 sweep (`runs/`, seed 17, 2000 steps): observed first-flip steps
703 / 352 / 176 / 88 at etas 0.05 / 0.1 / 0.2 / 0.4 -- **exact match**
with `ceil(X/eta)` for X = 35.115089. The argmin triple is token 192,
expert 1 (eps = 0.021484) vs expert 7 (eps = -0.020508), margin 1.474559:
a group-0 token whose second-favorite expert is overtaken by the
least-pressured expert once the pressure gap crosses its affinity margin.

## Where a proof was NOT achieved

No convergence result is claimed: the theorem covers only the linear
pre-flip regime. What happens after the first flip (cascades, settling,
the eta <= 3.0 clean basin, the eta = 10 limit cycle) remains empirical.
The theorem also does not cover the small_batch regime (T=64 changes the
affinity tensor, hence X) or non-requested controllers.

# Controlled Top-K saturation-sensitivity experiment

**Status:** protocol fixed before this run. This experiment extends the
existing capacity-attenuation theorem in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md).
It stays within the canonical Top-K and independent per-expert clipping
model. It does not test score-ranked shared-device admission.

## Question

Does the exact clipping factor in the expected admitted-feedback Jacobian
continue to predict the requested-versus-admitted sensitivity gap for
Top-K (`K>1`), heterogeneous saturation patterns, and increasing batch
size? Under global capacity shortage, how often does the realized admitted
sign signal freeze exactly because every expert is clipped?

## Fixed model

- Four experts, `K in {1,2}`, `T in {60,240,960}`.
- Independent standard-Gumbel affinity coordinates per token; scores are
  `a[t,e] - q[e]`, with unit score gain. This produces the Plackett-Luce
  ranking induced by the Gumbel Top-K router.
- Pressure state is evaluated at `q=0`. Expected Top-K inclusion
  probabilities are computed by exact enumeration of ordered Plackett-Luce
  prefixes, not Monte Carlo.
- Admission is always `A_e=min(R_e,C_e)`.
- The feedback field uses `P_0=I-11^T/E`, uniform target `mu_e=1/E`, and
  the existing requested/admitted definitions.
- The exact binomial factor is
  `alpha_e=Pr[Binomial(T-1,p_e)<C_e]`.

## Locked capacity profiles

For each `(K,T)`, run these five profiles:

1. **No clipping:** `C_e=T` for every expert.
2. **Global shortage:** `C_e=(4/5)KT/E` for every expert. The capacity
   total is `0.8KT`; under the symmetric state, every expected expert load
   exceeds capacity by 20% of its mean.
3. **Boundary:** `C_e=KT/E` for every expert (exact total, and
   `C_e/T=p_e(0)`). This distinguishes strict overload from the boundary.
4. **One overloaded expert:** expert 0 receives `0.8KT/E`; the remaining
   three capacities divide the residual equally. Total capacity is `KT`.
5. **Two overloaded experts:** experts 0 and 1 each receive `0.8KT/E`;
   experts 2 and 3 divide the residual equally. Total capacity is `KT`.

All capacities are integers for the registered grid. Capacity profiles are
fixed before evaluating results.

## Exact primary measurements

For every cell, compute the exact `p(q)` from all ordered length-`K`
Plackett-Luce prefixes, then evaluate the analytic requested and admitted
Jacobians from the theorem. Independently compute both expected feedback
fields at `q +/- h e_j`, with `h=1e-4`, and form central finite-difference
Jacobians.

Record:

- `p`, `C`, and each coordinate attenuation `alpha_e`;
- maximum entrywise difference between analytic and finite-difference
  Jacobians for both sensors;
- quotient Frobenius norms of the two Jacobians and their ratio;
- the maximum violation of
  `DF_A=(1/K)P_0 diag(alpha) Dp`.

## Paired fresh-batch control

For each `(K,T)`, generate 4,000 iid Gumbel batches once and reuse the same
requests across all five capacity profiles. For the global-shortage profile,
record the fraction for which every expert satisfies `R_e>=C_e`, hence
`A=C` and the admitted sign feedback is exactly zero. Report a 95% Wilson
interval for that event. For the no-clipping profile, verify pathwise that
`A=R` on every sampled batch.

The Monte Carlo component is a finite-sample implementation control. The
analytic Jacobian and binomial attenuation are the primary mechanism result;
do not infer novelty or production prevalence from the Monte Carlo rates.

## Predictions and failure criteria

1. The analytic Jacobian identity and independent finite differences agree
   within `2e-7` in every cell.
2. In no-clipping cells, every `alpha_e=1` up to numerical precision and
   the requested/admitted Jacobians agree.
3. At the exact boundary, the attenuation remains nonzero and approaches
   the central-limit boundary value; it is not reported as exponentially
   vanishing.
4. In the one- and two-overloaded profiles, only the overloaded rows have
   attenuation tending toward zero as `T` grows; unsaturated rows tend
   toward one.
5. In the global-shortage profile, the probability of `A=C` increases with
   `T`; whenever `A=C`, the admitted sign update is exactly zero.
6. Any failure of the formula, mass conservation, integer-capacity
   conditions, no-clipping identity, or exact-zero feedback on `A=C`
   invalidates the implementation and must be resolved before interpretation.

## Claim boundary

This experiment tests a correct, quantitatively specified version of the
professor's proposed sensitivity mechanism in the existing formal model.
It does not prove exact finite-`T` non-identifiability, that every admitted
controller winds up, that requested feedback always improves overflow, that
requested telemetry costs an extra collective, or that this result escapes
generic clipped-count/censored-observation theory. The exact count law is
still identifying for positive capacity at finite `T`; the theorem concerns
the derivative of its mean. A top-conference claim still needs a distinct
Top-K family consequence and evidence from a faithful system path.

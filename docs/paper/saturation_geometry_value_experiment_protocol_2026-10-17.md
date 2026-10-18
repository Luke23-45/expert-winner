# Exact controlled audit: saturation geometry and decision value

## Question

Does the number of simultaneously saturated experts distinguish a regime in
which admitted counts preserve the request signal from one in which they lose
decision-relevant information, under the same Top-1 request worlds?

This audit combines two existing formal facts: a single saturated coordinate
is reconstructible from mass conservation, while the two-saturated Top-1
family has a positive asymptotic value gap. It does not introduce another
router, admission rule, controller, or paper claim.

## Locked synthetic design

Use `E=3`, `K=1`, equal-prior static worlds

```text
p0 = (0.40, 0.40, 0.20)
p1 = (0.46, 0.34, 0.20)
```

These are exact Top-1 Gumbel-Max choice laws for logits `log(p_h)` at zero
pressure. Use the same two worlds in both arms and change only the exact-total
capacity assignment:

```text
one-saturated regime: C/T = (0.25, 0.50, 0.25)
two-saturated regime: C/T = (0.25, 0.25, 0.50)
```

For both regimes, `T in {40, 80, 160, 320, 640, 1280}`. Every capacity is integral.
Requests have their exact multinomial law; admitted counts are always
`A_e=min(R_e,C_e)`. Enumerate all integer compositions of T exactly; do not
use Monte Carlo estimates for the primary endpoint.

## Primary endpoint and registered policy class

After the first batch, select one of two fixed pressures `q^h` satisfying
`softmax(log(p_h)-q^h)=C/T`. Route an independent fresh batch in the same
world. The loss is exact expected realized normalized overflow
`E[sum_e (X_e-C_e)_+]/T` for that next batch.

For each signal (`R`, `A`, the compressed augmentation `(A,R_1)`, or the
single requested coordinate `R_1`), compute its exact equal-prior Bayes value over the registered two-action set
`{q^0,q^1}` by summing the multinomial probability of every observation and
selecting the lower conditional expected loss. This is an exact optimum
**within the two registered target pressures**; it is not represented as the
optimum over all possible pressure vectors.

## Predictions and controls

1. In the one-saturated regime, the high-probability event that no more than
   one expert reaches capacity makes A sufficient to reconstruct R exactly.
   The admitted/requested value difference in the registered action set
   should approach zero as T grows. Record the exact probability of this
   sufficient event and all three signal values.
2. In the two-saturated regime, experts 1 and 2 are both above capacity in
   both worlds, while expert 3 is below capacity. The exact admitted laws
   should approach one another, while requested observations separate the
   worlds. The two-saturated theorem predicts an asymptotic population value
   gap `c*delta/(2a) = 0.01875`; report the finite realized-overflow values
   separately and do not equate them with the population limit.
3. In the two-saturated regime, transmitting just the raw count `R_1` in
   addition to A should reconstruct the full request vector whenever expert 3
   is below capacity: A reveals `R_3`, and mass conservation then recovers
   `R_2`. Record the exact event probability and the value of `(A,R_1)`.
   This is a registered one-counter sufficiency diagnostic, not a claim that
   this is a universally minimum-cost telemetry encoding.
4. `R_1` alone is an exploratory compressed-signal arm. Compare the exact
   Bayes action selected from `R_1` with the action selected from full `R`.
   If those actions agree throughout the support, report that finite-family
   decision sufficiency as an observed result, not as a theorem unless a
   separate likelihood-ratio proof is supplied.
5. Requested counts are the positive-information control. A target-matched
   action in its matching world is the zero-population-overflow control;
   finite-batch sampling overflow is reported separately.
6. Check probability normalization, mass conservation, exact clipping, and
   exact-total capacities in every enumerated row.

## Analysis amendment

The first exact execution found equality between the Bayes values from full
`R` and `(A,R_1)` in every registered cell. Only after observing that result,
`R_1` alone was added as an exploratory arm to test whether the action rule
itself is a function of one count. This adaptive follow-up is post hoc; it is
not described as preregistered evidence. A confirmatory run would need a
separately frozen protocol and fresh parameters or seeds.

## Interpretation limits

This exact finite-count audit tests the predicted saturation-geometry change
for one declared two-world Top-1 family and a two-action controller class. It
does not prove the asymptotic theorem, establish a value gap for every
pressure policy, measure communication cost, validate a production stack,
establish training quality, or defeat the exact polyhedral outcome-map
benchmark. Those are separate claims and are not inferred from this audit.

## Reproduction

Run `python scripts/audit_saturation_geometry_value.py` from the repository
root. The runner writes the full finite-horizon values and checks under
`results/saturation_geometry_value/`.

# Controlled experiment: Top-1 clipped-load mirror equilibrium

## Question

For arbitrary heterogeneous positive exact-total capacities, does the
canonical Top-1 admitted-feedback population update exhibit the predicted
entropic mirror-descent decrease, converge at the stated objective-rate
bound, and approach the analytically characterized overflow equilibrium?
Separately, do fresh finite Gumbel batches at the predicted equilibrium
agree with the exact finite-binomial expectations?

## Locked population audit

- Router and target: Top-1, iid standard Gumbel affinities,
  `p=softmax(-q)`, uniform target, `gamma=1`, `delta=0`.
- Admission: independent per-expert caps `A_e=min(R_e,C_e)`.
- Exact-total integer capacities: `sum(C)=T`, `1<=C_e<T`.
- `E in {3,4,6,8}`, `T in {256,1024,4096}`, 24 deterministic seeded
  nonuniform capacity profiles per `(E,T)`.
- Profile generator: draw `Dirichlet(12*1_E)`; use largest-remainder
  rounding to sum exactly to T. Reject only zero-coordinate or uniform
  rounded vectors, as specified before sampling.
- Initial pressure: `q_0=0`, hence requested probabilities are uniform.
- Pressure steps: `eta in {0.1,0.5,0.9}`; horizon 1,024. Record at
  `N={1,2,4,8,16,32,64,128,256,512,1024}`.
- For every profile, construct the theorem's equal-minimum-capacity
  equilibrium `p*`, and independently compute the potential `W`, objective
  gap, KL distance, and overflow at all checkpoints.

## Locked finite-batch audit

At each profile's analytic equilibrium `p*`, draw 4,096 independent fresh
Top-1 batches for each `(E,T)` profile. Since iid Gumbel Top-1 has exact
softmax choice probabilities, sample the request vector from
`Multinomial(T,p*)`; this is distributionally identical to explicitly
sampling T Gumbel score vectors and routing them. Use the same sampled
request vectors for all admission and overflow summaries within a profile.

For each expert, compute exact finite-T expected admitted fraction from its
binomial marginal. Compute exact expected overflow by summing the same
binomial marginal. Report Monte Carlo means and 95% intervals next to these
exact values. The MC interval is descriptive and is not used to accept or
reject the theorem.

## Exact controls

1. Every capacity vector is positive, integer, nonuniform, and sums to T.
2. The constructed `p*` is interior, sums to one, and satisfies
   `min(p*_e,c_e)=c_min` coordinatewise within `1e-12`.
3. The pressure update and entropic mirror-step closed form agree within
   `1e-12` at every population step.
4. The one-step mirror-descent inequality holds at every population update;
   `W` never increases beyond `1e-12`; at each checkpoint,
   `W(p_N)-W(p*) <= KL(p*||p_0)/(eta*N)+1e-10`.
5. Exact equilibrium overflow equals `1-E*c_min`; requested equilibrium
   overflow equals `sum(max(1/E-c_e,0))`; the theorem's strict lower bound
   holds for every nonuniform profile.
6. Finite-batch request mass, clipping, and overflow identities hold for all
   Monte Carlo batches. Use Wilson/Student intervals only as descriptive
   summaries; do not discard profiles for disagreement.

The protocol tests the exact population theorem and finite-sample observation
law. It does not test a trained MoE, real hardware cost, another controller,
or fixed-finite-T infinite-horizon convergence.

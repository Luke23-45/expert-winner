# Locked experiment: two-saturated Top-1 value gap across E and skew

**Question.** Does the generalized exact value theorem hold across expert
counts and world-skew levels in the canonical Top-1 Gumbel/per-expert
clipping model, and do the common-tail coupling and requested classifier
behave as predicted?

## Design fixed before execution

- Expert counts `E in {3,4,8}`, `K=1`.
- Latent worlds `p0=(0.4,0.4,tail)` and
  `p1=(0.4+delta,0.4-delta,tail)`, with
  `delta in {0.04,0.08,0.12}` and tail probability `0.2` split equally over
  experts `3,...,E`.
- Exact-total capacity fractions `c=(0.25,0.25,tail-cap)`, with remaining
  `0.50` split equally over the tail experts. Every T is divisible so all
  capacities and displayed probabilities are integral when multiplied by T.
- `T in {4800,19200}` and 2,000 paired replications per `(E,delta,T)`.
- Sample the exact Top-1 Gumbel-Max count law by drawing one multinomial over
  the `E-2` shared tail categories **and one explicit pair category of mass
  `0.8`**. Reuse the tail counts in both coupled worlds, then split the pair
  count with each world's conditional binomial probability. This is
  distributionally identical to routing independent `log(p_e)+G_e` scores
  and gives an explicit coupling for the theorem. The pair category must be
  explicit: passing only the tail probabilities to NumPy's multinomial
  routine assigns the residual probability mass to the final category.

## Registered policies and metrics

- **Admitted constant action:** always choose `q^0`, the pressure that routes
  world 0 exactly to capacity. Its equal-prior population value is the
  theorem's exact `V_* = c*delta/(2a)`.
- **Requested classifier:** classify world 1 iff `R_1/T >= a+delta/2`, then
  choose the corresponding world-specific pressure `q^h` that routes to
  capacity. Record classifier error and realized population overflow risk.
- **Admitted simple classifier:** classify world 1 iff `A_1>A_2`; on ties,
  use a registered fair coin. Apply `q^h` accordingly. This is a diagnostic
  policy, not asserted optimal.
- **World-informed target-matched action:** choose `q^h` with the latent world
  available. Its population overflow is zero, but its realized finite-batch
  overflow is not zero because fresh multinomial counts fluctuate around
  capacity. Report that finite-batch noise floor separately.

For every paired replication, record whether each world satisfies the
two-saturated/no-tail-clipping event and whether their admitted vectors are
identical under the common-tail coupling. Compare empirical failure and
classifier rates against the theorem's explicit Hoeffding bounds. Report all
cell counts, means, and 95% binomial intervals; retain all replications.
Alongside population costs, compute exact expected realized overflow for a
fresh multinomial batch using the binomial identity
`E[(X-C)_+]=T*p*Pr[Bin(T-1,p)>=C]-C*Pr[Bin(T,p)>=C+1]` for each expert.
Use exact binomial tails for the registered requested threshold classifier;
this yields finite-batch upper bounds on each controller's optimal value.

## Invariants and interpretation limits

Assert each request vector sums to T, `A=min(R,C)`, and each pressure
realizes its claimed population distribution up to floating-point tolerance.
The admission identity and common-tail distribution are checked for every
cell. This count-law experiment is an exact stochastic realization of the
Top-1 Gumbel model, not a training run.

The experiment checks the theorem over the registered grid. It does not
prove its asymptotic bounds, establish a multi-round advantage over all
causal controllers, measure telemetry or collective cost, establish
quality/performance gains in a trained model, or separate the finite
experiment from a generic censored-hypothesis-testing benchmark.

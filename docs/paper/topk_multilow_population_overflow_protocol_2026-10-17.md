# Controlled experiment protocol: multiple low-capacity experts

## Question

Does the existing one-low-capacity population overflow theorem extend, with
its predicted quantitative gap, to several symmetrically low-capacity
experts under the same Top-K router, per-expert clipping, and proportional
pressure update?

## Locked design

- Router: hard Top-K on iid standard Gumbel affinities, score `a-q`.
- Admission: independent per-expert capacity, `A_e=min(R_e,C_e)`.
- Feedback arms: requested `R`, admitted `A`, and no-update diagnostic.
- Update: `q_next=P0(q+eta*(signal/(K*T)-1/E))`; no decay, `gamma=1`.
- Static-batch primary design: each affinity matrix is reused in every
  update and is paired across arms.
- Families: all `E in {4,6}`, all `K in {1,...,E-1}`, and all
  `m in {1,...,E-1}` satisfying the theorem's strict feasibility conditions
  for the fixed margin below. This is 32 families. Two grid points are
  excluded by the stated hypotheses: `(6,5,1)` has high-group limiting
  request fraction `(K-m)/(E-m)=0.8 > c_low=0.79167`, while `(6,5,5)` has
  `c_high=1.04167`. The former has no finite equilibrium of the claimed
  form; the latter violates the capacity-fraction constraint. These
  exclusions are by theorem hypotheses, not observed outcomes.
- Capacity margin: `r=1/(4E)`, with fractions `c_low=K/E-r` and
  `c_high=K/E+m*r/(E-m)`. The grid satisfies
  `max(K-m,0)/(E-m)<c_low` and `c_high<1`. Batch sizes
  `T={1440,2880,5760}` make every registered capacity integer and exact-total.
- Paired plants: 12 independent seeds per family and batch size; seed is
  `20261017 + 100000*family_index + 1000*T_index + replicate`.
- Horizon checkpoints: `H={1,2,4,8,16,32}`. Fixed step size `eta=0.5`.
- The population response `h(x)` is computed by exact Plackett-Luce dynamic
  programming. Predicted population recurrence and overflow gaps use no
  finite-batch outputs.

## Primary outcomes

For each paired plant and checkpoint, record cumulative overflow per token
under requested and admitted feedback, their paired difference, the
population prediction, and the group pressure separation. Report all plant
rows and paired means with 95% Student-t intervals. Keep request imbalance
and overflow separate; do not construct a weighted score.

## Required exact controls

1. Every sampled round has `sum(R)=K*T`, `A=min(R,C)`, and
   `sum(max(R-C,0))=K*T-sum(A)`.
2. The analytic capacity vectors are integer, valid, and sum to `K*T`.
3. The exact Gumbel response has `h(0)=K/E`, decreases on the registered
   pressure interval, and the bisection root satisfies `h(x*)=c_low`.
4. Population predictions satisfy `Delta_0=0`, `Delta_n>0` for `n>0`, and
   approach `(E-m)*r` per round.
5. A separate no-clipping negative control verifies pathwise equality of
   requested- and admitted-feedback trajectories.

## Interpretation fixed in advance

Agreement supports the finite-batch consequence of the stated population
theorem on this Gumbel grid. It does not establish fixed-`T` infinite-horizon
convergence, universal controller superiority, all affinity laws, an
independent benchmark separation, measured systems cost, or model-quality
improvement. A failed exact control invalidates the run; a failed
population comparison must be reported and investigated rather than
excluded.

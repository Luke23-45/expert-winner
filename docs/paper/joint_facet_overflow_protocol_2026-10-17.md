# Joint facet and overflow experiment protocol

**Status:** locked before this experiment is run. This is a paired audit of
two existing results in the canonical requested/admitted model; it does not
change the routing, admission, or controller definitions.

## Question

For the one-short, equal-rival-capacity family in the arbitrary-Top-K
two-step theorem, do the *same sampled affinity plants* exhibit both (a) a
regular Top-K facet where per-expert clipping makes the admitted field
non-potential and (b) a positive two-step overflow gap for admitted versus
requested proportional feedback? This tests co-occurrence on the theorem's
family. It does not test whether facet non-potentiality causes the overflow
gap.

## Locked plant and controller design

- `E=4`, `K=2`; short expert `i=0`, fixed cross-mean pair `(i,j)=(0,1)`.
- `T in {3360, 6720, 13440}` and 50 paired plants at each size.
- Generate each plant using seed
  `20261031 + 100000*E + 1000*K + 10*T_index + replicate`, matching the
  existing `topk_e_expert_overflow` controlled run. Affinities are iid
  integers in `{0,...,2^30}` divided by `2^30`; exact integer score
  comparisons are used. This is a fine-grid approximation to the theorem's
  continuous Uniform law, not the proof of that law.
- Use exact-total capacities `C_0/T=1/4`, `C_e/T=7/12` for `e=1,2,3`.
  These are the theorem's profile with `r=1/4` and `sum_e C_e=KT`.
- Reuse each same affinity matrix at both routing steps and across requested,
  admitted, and no-update arms. For `d in {1/4,1/2,3/4}`, set
  `eta=8*d`, so `d=eta*r/K` as in the theorem.
- Update after step zero by
  `q_1=Pi_g(eta*(signal/(K*T)-mu))`, with `mu=(1/E,...,1/E)`.
- Primary control outcome: paired normalized two-step overflow gap
  `D=(J_0^A+J_1^A-J_0^R-J_1^R)/T`.

## Facet audit

For every token row, test the proof-defined candidate condition for the fixed
pair `(0,1)`: its midpoint affinity is in `[5/12,7/12]`, the absolute pair
difference is at most `T^(-1/2)`, and exactly `K-1` of the other experts
score above that midpoint. At its constructed pressure, retain a candidate
only if exactly the distinguished token has a Top-K boundary tie and a small
two-sided pressure perturbation changes only its selection, from expert 0 to
expert 1. Compute the admitted count jump from the two exact routings. A
candidate is a mismatch when its source and destination admitted-count
changes differ; by the facet criterion this is a nonzero tangential jump.

Record candidate, regular-candidate, and mismatched-facet counts per plant.
The probability theorem predicts that the cross-mean profile has at least
one mismatch with probability tending to one. The experiment also reruns the
same facet check with no clipping (`C_e=T` for every expert); this control
must have zero mismatches. Any nonzero no-clipping mismatch, tie ambiguity,
or failed mass/clipping/overflow invariant invalidates that plant's audit.

## Registered summaries and interpretation

For each `T,d`, report mean and 95% paired-mean interval for `D`, fraction
of plants with `D>0`, fraction with at least one regular mismatched facet,
and fraction with both events. Compare mean `D` with the exact limit
`Phi_(4,2)(d)-1/2`. Report all individual plant rows, including failures;
do not drop any seed or change the threshold after seeing results.

The joint probability theorem predicts convergence of both events to one;
finite-grid results are supporting evidence only. This audit does not
establish causality between a local curl and control cost, performance under
trained routers, telemetry cost, or separation from the polyhedral
active-testing benchmark.

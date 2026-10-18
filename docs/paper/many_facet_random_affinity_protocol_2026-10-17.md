# Controlled audit of the many-facet strengthening

**Protocol status:** fixed before execution.  
**Research line:** canonical deterministic Top-$K$ with per-expert clipping.  
**Theorem under audit:** the many-facet strengthening in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).

## Question

For iid affinity plants, does the explicit candidate construction produce an
increasing number of distinct, regular Top-$K$ facets whose admitted-count
field jump has a nonzero tangent component, with observed growth compatible
with the theorem's $\Omega(\sqrt T)$ lower bound? This audit checks the
candidate-count strengthening; it does not sample all facets uniformly.

## Fixed design

- Experts $E=4$, Top-$K$ with $K=2$; exchanged experts are fixed as $i=0$,
  $j=1$ before generating any plant.
- Batch sizes $T\in\{64,256,1024,4096\}$, each divisible by four.
- Capacities are $(T/4,3T/4,T/2,T/2)$, with exact total $KT$ and strict
  limiting cross-mean pair $(c_0,c_1)=(1/4,3/4)$.
- Affinities are iid integer draws from $\{0,\ldots,2^{30}\}$, interpreted
  as exact rationals with denominator $2^{30}$. Seeds are
  `20261018 + 10000*T + replicate`, for 500 replicate plants per $T$.
- For **every** row $t$, test the fixed proof event: midpoint
  $M_t=(a_{t,0}+a_{t,1})/2$ lies in $[5/12,7/12]$; pair gap
  $|a_{t,0}-a_{t,1}|\le T^{-1/2}$; and exactly one of experts 2 and 3 has
  affinity strictly above $M_t$. On the finite grid, exclude candidates
  with any additional tie in the selected row; this has probability zero
  under the theorem's continuous model. All predicates use integer
  arithmetic.
- For each candidate row, form its exact tie pressure
  $q_0=(a_{t,0}-a_{t,1})/(2\gamma)$,
  $q_1=-(a_{t,0}-a_{t,1})/(2\gamma)$, $q_2=q_3=0$, with $\gamma=1$.
  Evaluate every token's scores at that **same candidate pressure**. Check
  the intended token is tied at ranks 2 and 3, no other row has any score
  tie, and no other candidate pressure duplicates this facet.
- Count the other $T-1$ rows' Top-2 requests exactly. The facet is a
  capacity-mismatch witness iff
  $(X_0<C_0)\ne(X_1<C_1)$. Record the exact tangent-jump indicator and
  squared norm; for a mismatch the theorem predicts $(E-2)/(2E)=1/4$.

## Controls and invariants

1. **No-clipping negative control:** set every capacity to $T$. Since each
   filler count is at most $T-1$, both exchange indicators equal one and no
   candidate may have a tangential mismatch.
2. **Mass conservation:** every filler row requests exactly two experts.
3. **Admission identity:** per expert and every candidate,
   $A_e=\min(R_e,C_e)$; retention order cannot alter this count.
4. **Regularity:** a candidate with a second token tie is recorded as
   nonregular, never counted as a theorem witness.
5. **Facet uniqueness:** candidates with equal tie pressure are recorded as
   duplicates and counted once at most; their shared arrangement face is
   not counted as multiple facets.
6. **Deterministic replay:** fixed seed mapping, exact integer scoring, and
   byte-identical summary hash on rerun.

## Primary reported quantities

For each $T$, report the mean, median, range, and plant-level values for:

- candidate rows;
- distinct regular candidate facets;
- distinct regular mismatched facets;
- fraction of candidate facets that are regular and mismatched;
- number of plants meeting the integerized lower threshold
  $N_{\rm mismatch}\ge\lceil b_{4,2}\sqrt T/2\rceil$;
- no-clipping mismatches;
- mean $X_0/T$ and $X_1/T$ at candidate facets.

The theorem's constant is fixed in advance:
\[
b_{4,2}=\frac13\binom{2}{1}(5/12)^2=25/216.
\]
No threshold or candidate rule may be adjusted after examining results.

## Interpretation boundary

The experiment can expose implementation errors, show finite-size behavior
of the explicit proof construction, and test whether the predicted
$\sqrt T$ candidate count is visible at these sizes. It cannot prove the
asymptotic theorem, estimate the fraction of **all** arrangement facets
that mismatch, establish controller performance or overflow improvement,
validate a training-quality claim, or establish novelty against the
polyhedral outcome-map benchmark. Those are separate claims and are not
outcomes of this protocol.

## Execution

Run `python scripts/audit_many_random_facets.py` from the repository root.
The script writes `results/many_random_facets/summary.json` and
`results/many_random_facets/plants.csv`. Preserve both outputs and record
the source and protocol hashes in the results report.

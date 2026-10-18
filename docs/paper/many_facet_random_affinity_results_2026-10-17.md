# Many-facet random-affinity audit: results

**Protocol:** [`many_facet_random_affinity_protocol_2026-10-17.md`](many_facet_random_affinity_protocol_2026-10-17.md), fixed before this run.  
**Implementation:** [`audit_many_random_facets.py`](../../scripts/audit_many_random_facets.py).  
**Artifacts:** [`summary.json`](../../results/many_random_facets/summary.json) and [`plants.csv`](../../results/many_random_facets/plants.csv).  
**Summary SHA-256:** `c7538bed086ea36e8df37eb4d7fa5a6179056625e96398997938cf3d018f5fee`.  
**Plant CSV SHA-256:** `03ff328554e7051b6264ee661ec0f1a8b0d5f77892fd1463c8f11264abd14791`.  
**Protocol SHA-256:** `f2d9c65f0438aab1d9a347aff208c7d9cfc27f5eb318b08c13e2d93033c5e8a0`.  
**Script SHA-256:** `7b9eb32734b4250aee8a3904d8ed2a283c9fbcb3a7e652f76ec56177725b7cb0`.
The full experiment was executed twice; both runs produced the same summary
SHA-256. The current plant-level CSV contains all 2,000 replicate records.

## Results

The audit used 500 paired rational-grid affinity plants at each batch size.
For every plant, it enumerated **all** rows meeting the preregistered
candidate condition and tested the corresponding candidate pressures against
the full batch. The capacity fractions were $(1/4,3/4,1/2,1/2)$, with experts
0 and 1 the fixed below-mean/above-mean pair. Across all 2,000 plants it
checked 10,028 distinct candidate facets; every one was regular and every one
was mismatched under clipping.

| $T$ | Mean candidate facets | Mean mismatched facets | Mean mismatches / $\sqrt T$ | Plants meeting $\lceil b_{4,2}\sqrt T/2\rceil$ | No-clipping mismatches |
|---:|---:|---:|---:|---:|---:|
| 64 | 1.334 | 1.334 | 0.16675 | 367/500 | 0 |
| 256 | 2.726 | 2.726 | 0.17038 | 468/500 | 0 |
| 1,024 | 5.332 | 5.332 | 0.16663 | 488/500 | 0 |
| 4,096 | 10.664 | 10.664 | 0.16663 | 497/500 | 0 |

Every retained regular candidate facet mismatched under clipping. At
$T=4096$, each plant had between 3 and 21 distinct regular mismatched
candidate facets, versus the theorem's integerized lower threshold of 4.
The mean filler request fractions for experts 0 and 1 were respectively
`0.49998` and `0.49946`, approaching the common Top-2 mean $K/E=1/2$.

The empirical mean candidate count divided by $\sqrt T$ stays near
`0.167`, consistent with the proof's $\Theta(\sqrt T)$ candidate scale.
The explicit lower-bound constant is $b_{4,2}/2=25/432\approx0.05787$;
the preregistered plant-level lower-count criterion was met by 497/500
plants at $T=4096$. Finite-grid observations support the construction; they
do not prove the asymptotic probability statement. The analytic failure
bound can be loose at these finite sizes and was not treated as a prediction
of exact plant-level coverage.

## Controls and interpretation

The exact integer-grid run verified the intended rank-2/rank-3 tie, checked
that every counted facet is regular in the complete finite arrangement,
deduplicated pressures, conserved the $2(T-1)$ filler request mass, and
checked $A_e=\min(R_e,C_e)$. The no-clipping control produced zero
mismatches in all plants. No route-outcome or controller-performance metric
was used to select candidates.

This is stronger finite-size support than the previous first-candidate audit:
it counts multiple distinct facets per plant and tests the predicted
$\sqrt T$ growth. It still does not estimate the fraction of **all** facets
that mismatch; the candidates follow a proof-defined selection rule. It
also says nothing about cumulative overflow, convergence, training loss,
telemetry cost, or separation from an outcome-map benchmark. The exact
asymptotic conclusion remains the theorem in
[`random_facet_nonpotentiality_theorem_2026-10-17.md`](random_facet_nonpotentiality_theorem_2026-10-17.md).

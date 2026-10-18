# Results: arbitrary-capacity Top-1 mirror equilibrium

**Theorem:** [`top1_arbitrary_capacity_mirror_equilibrium_theorem_2026-10-17.md`](top1_arbitrary_capacity_mirror_equilibrium_theorem_2026-10-17.md)  
**Protocol:** [`top1_arbitrary_capacity_mirror_equilibrium_protocol_2026-10-17.md`](top1_arbitrary_capacity_mirror_equilibrium_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_top1_arbitrary_capacity_mirror_equilibrium.py`](../../scripts/run_top1_arbitrary_capacity_mirror_equilibrium.py)

## Population dynamics

The exact population audit covers 288 nonuniform exact-total capacity
profiles (`E={3,4,6,8}`, `T={256,1024,4096}`, 24 profiles per cell), three
step sizes, 1,024 updates, and 9,504 saved profile/step rows. Every profile
satisfied the exact equilibrium construction and overflow lower bound. At
every simulated update, the pressure update matched its entropic mirror-step
form; the one-step mirror-descent inequality, nonincrease of the capped-load
potential, and all checkpoint objective-rate bounds passed.

At update 1,024:

| Step size | Mean potential gap over profiles | Maximum potential gap | Maximum overflow error from equilibrium |
|---:|---:|---:|---:|
| 0.1 | 0.00007280 | 0.00088451 | 0.046782 |
| 0.5 | 0.00000187 | 0.00012780 | 0.006992 |
| 0.9 | 0.0000000433 | 0.00001245 | 0.003325 |

The theorem bounds the **potential gap**, not the overflow error. The larger
finite-horizon overflow residual at `eta=0.1` is therefore reported
separately and should not be presented as a violation of the theorem.

Across the 288 profiles, the exact population equilibrium overflow exceeded
the requested uniform-target equilibrium overflow by between `0.007487` and
`0.485352` assignments per token. The theorem's profile-wise lower bound
`1/E-c_min` was positive for every nonuniform profile and passed exactly in
all audits.

## Fresh finite-batch check at the predicted equilibrium

At each profile's analytic equilibrium, 4,096 fresh multinomial Top-1
request batches were drawn. This is distributionally identical to routing
iid Gumbel token scores at the fixed equilibrium pressure. All request-mass,
clipping, and overflow identities passed. The Monte Carlo 95% intervals for
overflow contained their exact finite-`T` binomial-marginal expectations in
266/288 profiles (92.4%); the intervals were not used to accept or reject
the theorem.

| Batch size | Intervals covering exact finite-`T` expectation | Mean exact finite-`T` overflow | Mean population-limit overflow |
|---:|---:|---:|---:|
| 256 | 91/96 | 0.302464 | 0.299601 |
| 1,024 | 87/96 | 0.297368 | 0.296733 |
| 4,096 | 88/96 | 0.295041 | 0.294884 |

The small finite-`T` differences from the population overflow arise because
counts fluctuate around capacity thresholds. This check is evidence for the
declared finite-batch sampling law, not an infinite-horizon finite-batch
claim.

## Reproduction artifacts

- Population trajectories: [`population_trajectories.csv`](../../results/top1_arbitrary_capacity_mirror_equilibrium/population_trajectories.csv)
- Finite-batch results: [`finite_batch_equilibrium.csv`](../../results/top1_arbitrary_capacity_mirror_equilibrium/finite_batch_equilibrium.csv)
- Generated profiles: [`capacity_profiles.json`](../../results/top1_arbitrary_capacity_mirror_equilibrium/capacity_profiles.json)
- Summary: [`summary.json`](../../results/top1_arbitrary_capacity_mirror_equilibrium/summary.json)
- Runner SHA-256: `4ba9ebe5a41bbfa861a2c9a7befd0aba2aa2dfca10c1c237d21676c31c1a53a9`
- Population CSV SHA-256: `d4ebdc580605db26bb246696ae854f0052bb8fa1c23e1a4eecefa05de582d4c2`
- Finite-batch CSV SHA-256: `f7ca4688cdeda8f4ba01dd93d9b90606b2269cc6d676b2c6ab03422390caffbf`
- Capacity-profile JSON SHA-256: `88ddd69e2278319e1153008199c7ee423cac69ae19ff9978c40a46168c8ae0d0`

Reproduce from the repository root with:

```powershell
python scripts/run_top1_arbitrary_capacity_mirror_equilibrium.py
```

## Interpretation and prior-art boundary

The controlled result supports the exact population theorem under arbitrary
heterogeneous positive exact-total capacities. The admitted-count update is
mirror descent on the separable capped-load potential in probability
coordinates, and every population equilibrium has admitted fraction equal
to the minimum capacity fraction. This implies a strict equilibrium
overflow penalty relative to the requested uniform-target state whenever
capacities are nonuniform.

The potential and mirror-descent convergence are applications of established
ideas: Rosenthal's congestion-game potential and relative-smoothness KL
mirror descent ([Rosenthal, 1973](https://doi.org/10.1007/BF01737559);
[Aubin-Frankowski et al., NeurIPS](https://papers.nips.cc/paper_files/paper/2022/hash/6e3daaeca6be8579573f69082b2dd58b-Paper-Conference.pdf)). The candidate contribution is the exact Top-1
Gumbel/capacity-clipping identification and its overflow comparison, not the
generic optimization method. This remains a targeted novelty boundary, not
a systematic search or a conference-novelty verdict.

The result does not establish a separation from the fixed-instance
polyhedral active-testing benchmark, a telemetry-cost break-even, or a
trained-model quality gain. It proves convergence for the exact **population
update**, not for a fixed finite batch over an infinite horizon.

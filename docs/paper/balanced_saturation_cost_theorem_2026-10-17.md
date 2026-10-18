# Exact cost consequence of admitted-feedback saturation drift

**Status:** theorem/corollary in the canonical Top-K, per-expert clipping,
proportional gauge-pressure model. The statement combines the existing
constant-feedback exit argument with an exact aggregate-overflow identity.
It does not change the controller or admission rule.

## Model

Fix integers `E>K>=1`, `T`, and `n=KT/E` with `n` an integer. Fix positive
integer capacities satisfying

```text
0 < C_e <= n for every e,
C_(K) < C_(K+1),
```

where capacities are sorted in nondecreasing order. Let `S` be the `K`
experts with the smallest capacities. Use a fixed affinity matrix, strict
Top-K routing at `q_0=0`, and assume its initial request counts are balanced:
`R_e(q_0)=n` for every expert. The target is uniform, `mu_e=1/E`; the
admission map is `A_e=min(R_e,C_e)`; the pressure update has zero leak:

```text
q_next = Pi_g(q + eta*gamma*(L/(K*T) - mu)),   eta,gamma > 0,
scores = affinity - gamma*q.
```

Compare admitted feedback `L=A` against requested feedback `L=R` and no
feedback. Overflow is `J(q)=sum_e (R_e(q)-C_e)_+`.

## Theorem: nonnegative all-horizon gap, strict after a certified exit

Let

```text
D = K*T - sum_e C_e > 0.
```

Let `tau` be the first state index at which the admitted-feedback trajectory
is not globally saturated. Define

```text
v = P_0(C/(K*T) - mu),   alpha = eta*gamma^2,
theta[t,i,j] =
  (-(a[t,i]-a[t,j])) / (alpha*(v_j-v_i)),  i in S, j not in S,
N_sep = max(0, 1 + max_(t,i,j) floor(theta[t,i,j])).
```

The strict capacity gap makes `v_j-v_i>0` for every `i in S, j not in S`.
Then:

1. Requested feedback and no feedback remain at `q_0` and incur exactly `D`
   overflow at every batch.
2. Admitted feedback remains on the open-loop constant-feedback trajectory
   until it exits global saturation, and `tau <= N_sep < infinity`.
3. At every state of the admitted-feedback trajectory,

   ```text
   J_A(t) - D = sum_e (C_e - A_e(q_t)) >= 0.
   ```

   The difference is zero exactly when all experts are saturated. It is
   strictly positive at the first unsaturated state and thereafter whenever
   the admitted trajectory is unsaturated.
4. Therefore, for every horizon `H`,

   ```text
   sum_(t=0)^(H-1) J_A(t)
       >= sum_(t=0)^(H-1) J_R(t)
        = sum_(t=0)^(H-1) J_none(t),
   ```

   with strict inequality whenever `H > tau`. In particular, the strict
   requested-versus-admitted cumulative-overflow gap is certified for every
   `H > N_sep`.

The result is uniform over all fixed affinity matrices satisfying the stated
initial balanced-count and strict-routing conditions. The bound depends on
the actual Top-K score margins and the capacity-induced slope gap; it is not
a claim for arbitrary affinity matrices or arbitrary targets.

## Proof

At `q_0`, `R/(KT)=mu`, so the requested update is zero. The no-feedback
update is also zero. Since `C_e<=n=R_e(q_0)`, both trajectories remain at
`q_0` with `A=C`, and their per-batch overflow is
`sum_e(n-C_e)=KT-sum_e C_e=D`.

While the admitted trajectory is globally saturated, `A=C`; hence its
feedback is constant. In score-penalty coordinates `p=gamma*q`, gauge
projection only changes the common mode, and the relative state evolves as
`p_t = p_0 + t*alpha*v`. Since `v` has the same strict coordinate ordering
as `C`, every expert in `S` has smaller pressure slope than every expert
outside `S`. For each token, the displayed `N_sep` makes every expert in
`S` strictly outrank every expert outside `S`. If global saturation had not
already failed, that state would route every token to `S`; because `E>K`
and every outside capacity is positive, an outside expert would have zero
requests and saturation would fail. Thus `tau<=N_sep`.

For any request vector with `sum_e R_e=KT`,

```text
J = sum_e(R_e-C_e)_+
  = KT - sum_e min(R_e,C_e)
  = KT - sum_e A_e.
```

Therefore `J-D=sum_e C_e-sum_e A_e=sum_e(C_e-A_e)>=0`. Equality holds
exactly when `A=C`, i.e. every expert is saturated. At the first unsaturated
state, at least one term `C_e-A_e` is positive. Summing over states proves
the all-horizon comparison and its strictness condition. □

## Relation to the existing results and claim boundary

The finite-exit component is the existing canonical proportional-controller
arrangement theorem T6a in [`formal_core.md`](formal_core.md). The new step is
the exact aggregate-overflow identity, which turns that exit into a strict
cost consequence when the requested controller is stationary at a balanced
initial state. This statement does **not** use T7: T7 concerns the separate
signed expert-bias controller.

This is a **Top-K class theorem**, not an instance-level separation from the
polyhedral benchmark: every fixed finite affinity plant still has an exact
piecewise-constant outcome-map representation. It does not prove that the
phenomenon is typical in trained models, that it holds for fresh iid batches
at fixed `T`, or that requested telemetry has a net system benefit. Those
remain separate publication gates.

### Benchmark attack

The strict-exit conclusion does not hold for unrestricted B1 outcome maps.
For the same initial request vector `R=n*1` and capacities `C`, let a B1
plant return the constant request label `R(q)=n*1` at every pressure and
define `A(q)=min(R(q),C)=C`. This is a valid one-cell piecewise-constant
outcome map with mass-conserving requests and the same deterministic clipping
and overflow cost. The requested and no-feedback arms stay at `q_0`; the
admitted arm's pressure moves, but the constant outcome map never changes,
so all three arms incur exactly `D` at every horizon. Thus B1 does not imply
T6c's strict-exit result. The load-bearing assumption is the Top-K
score-consistent arrangement, which forces the low-capacity experts to
eventually win every token under the saturated constant drift.

This is a **class-structure comparison**, not a performance separation:
B1 can also copy any one fixed Top-K plant exactly and therefore reproduce
its value. The new corollary says that the specified Top-K family has a
uniform finite-exit/cost property that arbitrary polyhedral maps need not
have; it does not show that Top-K achieves lower optimal value than B1 or
clear novelty against the broader control/active-testing literature.

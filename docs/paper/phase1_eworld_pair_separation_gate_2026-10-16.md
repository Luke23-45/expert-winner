# E-world family gate: pair-separation cost and finite-movement reduction

**Date:** 2026-10-16  
**Branch:** `feat/research-censored-feedback`  
**Status:** the all-pressure pair-separation inequality is proved for the
canonical Top-1 E-world family under the stated capacity conditions. With
unrestricted movement, every pressure action is dominated by a subset-probe
test, giving an exact finite-horizon Bellman recursion. This is not a
novelty claim; the decision-tree reduction remains a serious boundary. The
subset-probe transition geometry is now exact for finite movement budgets;
below the all-subset diameter threshold, this does not yet characterize the
full pressure optimum.

## 1. Research question for this phase

The earlier E-world construction proves that one pressure cannot give
sub- $E_S/2$ overflow in two worlds. That one-shot fact is too weak for the
proposed growing gap: it does not say how much overflow an action must pay
when it separates many hypotheses, and it does not itself charge uncertainty
left at a finite horizon.

The one-step information-cost inequality is now proved. Let the posterior be
uniform on a consistent world set $\mathcal U$ of size $u$. A pressure
$q$ partitions $S$ into admitted-observation blocks $B\in\mathcal P_q(S)$.
The expected reduction in support size is

$$
\Delta_q(\mathcal U)=u-\frac1u\sum_{B\in\mathcal P_q(\mathcal U)}|B|^2.
$$

For the canonical E-world parameters define

$$
L=E_S+C-C_{\rm sink},
$$

the overflow of a wrong single-candidate probe. The proposed all-pressure
lemma is

$$
\mathbb E[\|J(q,W)\|_1\mid W\in\mathcal U]
\;\ge\;\frac L2\,\Delta_q(\mathcal U)
\qquad\text{for every pressure }q\text{ and every nonempty }\mathcal U.
\tag{PS}
$$

This is a Top-1-derived bound on the information a pressure action reveals.
It is stronger than the existing no-hedging lemma, but it is **not by itself**
a finite-horizon value theorem: a policy can leave hypotheses unresolved at
the horizon. The exact unrestricted-movement Bellman recursion below accounts
for both probing cost and waiting with uncertainty.

## 2. What the finite exact checks establish

The reproducible command is:

```powershell
python scripts/audit_eworld_pair_separation.py
```

The E=4 part reuses the exact rational Fourier-Motzkin arrangement audit in
[`analyze_e4_exact_partition.py`](../../scripts/analyze_e4_exact_partition.py).
It enumerates every feasible joint winner signature for the six token types,
deduplicates to 45 admitted observation/cost maps, and checks (PS) on all 7
nonempty posterior supports for every map: 315 exact rational checks. At the
reference parameters $E_S=20,C=50,C_{\rm sink}=30$, there are no violations.
The smallest slack is zero for partition shapes $(1,1)$ and $(2,1)$; the
singleton-plus-pair equality is attained by the canonical single-candidate
probe. The all-singleton partition has strictly positive slack in this
instance.

This exact E=4 enumeration is a check on the general proof below. By itself,
the enumeration would not prove (PS) for continuous pressure at other E or
other integer parameters.

## 3. All-pressure proof

Let the sink be expert $s=N+1$. Write the pressure-relative advantage of
regular expert $e$ over the sink as

$$
z_e=-\gamma(q_e-q_s),\qquad U=\max_{e\le N}z_e,
$$

and let $r$ be the lowest-index maximizer of $z_e$. Relative to the sink, a
low token $L_e$ has scores $m+z_e$ at $e$, $0$ at $s$, and $-M+z_f$ at every
other regular expert $f$. A high token $H_e$ changes only its own score, from
$m+z_e$ to $M+z_e$.

If $U<M$, every non-own regular score is strictly below the sink. Thus the
winner pair (low destination, high destination) for each $e$ is one of
$(e,e)$, $(s,e)$, or $(s,s)$. If $U\ge M$, expert $r$ beats or tie-breaks ahead
of the sink. For each $e\ne r$, every non-own regular competitor is no better
than $r$; raising the own score from $m+z_e$ to $M+z_e$ can therefore only
change the winner from $r$ to $e$. Expert $r$ wins both token types. Thus in
either case there is a **common hub** $h$ (the sink or one regular expert)
such that every regular expert has exactly one of these destination pairs:

| class | low block destination $d_e$ | high block destination $h_e$ |
|---|---|---|
| $P$ | $e$ | $e$ |
| $Q$ | $h$ | $e$ |
| $Z$ | $h$ | $h$ |

The tie rule is covered: when $U=M$, the maximizing regular expert has a
lower index than the sink and is the hub; ties between the own expert and hub
still give one of the three listed pairs. If the hub is regular, it is in
class $P$. Put $k=|Q\cup Z|$ and $b=|Q|$.

For world $i$, the exact request vector is

$$
R^i=C\sum_{e=1}^N\mathbf e_{d_e}
      +C(\mathbf e_{h_i}-\mathbf e_{d_i})
      +E_S\mathbf e_{d_i}.
\tag{R}
$$

It starts with the common low-block request, replaces world $i$'s baseline
block by its high-block destination, and adds the extra low block. Formula
(R) is valid whether the hub is the sink or a regular expert.

The induced admitted partition has a simple form: each world $i\in Q$ has a
distinct admitted vector (its regular coordinate $i$ is filled), while all
worlds outside $Q$ share one admitted vector. For the sink hub, a $Q$ world
has regular experts in $P\cup\{i\}$ filled and sink load
$(k-1)C+E_S$; every non-$Q$ world has regular set $P$ filled and its sink is
saturated. For a regular hub, a $Q$ world has $P\cup\{h,i\}$ filled, and a
non-$Q$ world has $P\cup\{h\}$ filled; the sink is unused. These patterns
also cover $k=1$ and the deterministic tie rule.

The per-world overflow is:

| hub | world type | overflow $J_i$ |
|---|---|---:|
| sink | $k=0$ | $E_S$ for every world |
| sink | $i\in Q$, $k\ge1$ | $\max\{0,(k-1)C+E_S-C_{\rm sink}\}$ |
| sink | $i\notin Q$, $k\ge1$ | $L+(k-1)C$ |
| regular | $k=0$ | $E_S$ for every world |
| regular | $i\in Q$, $k\ge1$ | $(k-1)C+E_S$ |
| regular | $i\notin Q$, $k\ge1$ | $kC+E_S$ |

The assumptions $E_S\le C_{\rm sink}<C-E_S/2$ imply
$0<L=E_S+C-C_{\rm sink}\le C$. For either hub and $k\ge1$, the $Q$-world
cost is at least $(k-1)L$ and every non-$Q$ world costs at least $kL$. For
the sink hub this uses $E_S\le C_{\rm sink}$ when $k=1$; for $k\ge2$ the
positive part equals $L+(k-2)C$. For the regular hub it follows from
$C\ge L$.

Now take any nonempty consistent support $\mathcal U$. Let
$x=|\mathcal U\cap Q|$ and $y=|\mathcal U\setminus Q|$. The number of
unordered world pairs separated by the admitted observation is

$$
P_q(\mathcal U)=\binom{x}{2}+xy.
$$

For $k\ge1$, summing the cost bounds gives

$$
\sum_{i\in\mathcal U}J_i
\ge L((k-1)x+ky)
=L P_q(\mathcal U)
+L\left[\frac{x(2k-x-1)}2+y(k-x)\right]
\ge L P_q(\mathcal U),
$$

because $x\le |Q|\le k$. When $k=0$, no pair is separated and the
inequality is trivial. Finally,

$$
\Delta_q(\mathcal U)=\frac{2P_q(\mathcal U)}{u}.
$$

Dividing the summed inequality by $u$ proves (PS). This covers every
pressure, the gauge quotient, every posterior support, and the deterministic
tie rule. It is specific to this identical-block E-world construction and
capacity regime; it is not a theorem for arbitrary MoE instances.

### Corollary: exact-identification overflow lower bound

Consider any causal admitted-feedback policy on this family, with the uniform
prior over $N$ worlds. Let $\mathcal U_t$ be the set of worlds consistent
with its admitted-observation history after round $t$. Conditional on a
history, the posterior is uniform on $\mathcal U_t$: observations are
deterministic functions of the world and chosen pressure, and the policy's
private randomness is independent of the world. For a chosen pressure $q_t$,
the support-size reduction satisfies

$$
\mathbb E[|\mathcal U_t|-|\mathcal U_{t+1}|
  \mid \mathcal H_t,q_t]
=\Delta_{q_t}(\mathcal U_t).
$$

Applying (PS) conditionally and summing for $t=0,\ldots,H-1$ gives

$$
\mathbb E\!\left[\sum_{t=0}^{H-1}\|J(q_t,W)\|_1\right]
\ge \frac L2\left(N-\mathbb E|\mathcal U_H|\right).
\tag{ID-LB}
$$

In particular, if the policy identifies the world with probability one by
round $H$, then $\mathbb E|\mathcal U_H|=1$ and cumulative overflow is at
least $L(N-1)/2$. This lower bound holds for every causal randomized policy;
conditioning on its private random seed gives the deterministic case and
averaging preserves the inequality. If the experiment includes a separate
initial blind round at $q_0$, add that round's fixed overflow $E_S$ to the
bound for the subsequent identification phase.

With unrestricted movement and at least $N-1$ informative rounds, the bound
is attained by testing singleton subsets in a fixed order and inferring the
last untested world after $N-1$ failures. A false singleton test costs $L$,
and the correct test costs zero. Under the uniform prior, the expected number
of false tests is $(N-1)/2$. Thus the minimum expected overflow **among
policies required to identify the world** is exactly $L(N-1)/2$ after the
initial blind round, or $E_S+L(N-1)/2$ when that round is included.

This is an exact finite-family information-cost theorem derived from the
Top-1 pressure partition. It does not solve the original unconstrained
cumulative-overflow objective, because that objective does not require
identification; nor does it escape the generic adaptive-testing reduction.
The result is therefore a concrete theorem about this MoE family, but not by
itself the missing top-conference novelty separation.

## 4. Canonical subset probes and exact all-pressure reduction

Take $N=E-1$ regular experts and one sink. In world $i$, there is a size-$C$
baseline block per regular expert, with margin $M$ at expert $i$ and $m$ at
the others, plus $E_S$ extra margin-$m$ tokens at $i$. Assume

$$
E_S\le C_{\rm sink}<C-E_S/2.
$$

For a subset $P\subseteq[N]$, use the pressure with relative score offset in
$(m,M)$ at coordinates in $P$ and zero elsewhere. In world $i\in P$, the
high-margin block survives at $i$ and the admitted vector identifies $i$;
in world $i\notin P$, every coordinate in $P$ is depleted and the outcome
keeps all worlds outside $P$ together. Write $p=|P|$. The raw overflow is

$$
J_i(P)=
\begin{cases}
\max\{0,(p-1)C+E_S-C_{\rm sink}\},&i\in P,\\
E_S+pC-C_{\rm sink},&i\notin P.
\end{cases}
$$

For $P=\varnothing$ every world has the common observation and cost $E_S$.
For a singleton $P=\{j\}$, world $j$ has zero probe overflow and every other
world pays $L=E_S+C-C_{\rm sink}$. Thus sequential singleton probing costs
$L(N-1)/2$ in expectation under the uniform prior if enough rounds are
available to identify the last remaining world.

The all-pressure proof also gives an action reduction when movement is
unrestricted. If $Q=\varnothing$, the pressure gives no information and its
per-world overflow is at least $E_S$, so zero pressure weakly dominates it.
If $b=|Q|\ge1$, the canonical subset pressure with exactly $P=Q$ has the same
outcome partition and no larger cost in any world. For a sink hub, this
follows by replacing $k\ge b$ with $b$. For a regular hub and $b\ge2$, the
original costs exceed the canonical costs by $(k-b)C+C_{\rm sink}$; for
$b=1$, the same dominance follows from nonnegative probe cost and
$kC+E_S\ge L$. Thus, with no action-transition restriction, the full
continuous pressure set reduces exactly to subset-probe tests. This
replacement need not be reachable under a finite pressure-step budget.

Let $V_h(n)$ be the minimum expected remaining overflow with $h$ rounds and a
uniform posterior on $n$ worlds. Set $V_0(n)=V_h(0)=V_h(1)=0$. The exact
Bellman recursion is

$$
V_h(n)=\min\left\{
E_S+V_{h-1}(n),
\min_{1\le b\le n}\left[
\frac b n c_{\rm in}(b)
+\frac{n-b}{n}\left(c_{\rm out}(b)+V_{h-1}(n-b)\right)
\right]\right\},
$$

where $c_{\rm in}(1)=0$, $c_{\rm in}(b)=L+(b-2)C$ for $b\ge2$, and
$c_{\rm out}(b)=L+(b-1)C$. Waiting incurs $E_S$ and leaves the posterior
unchanged. A probe of $b$ candidates identifies the world if it lies in the
subset; otherwise it leaves a uniform posterior on $n-b$ worlds. Hence the
admitted value over a total horizon $H$ is $E_S+V_{H-1}(N)$. If the requested
policy can reach and hold each correct singleton probe after the initial
round, its value is $E_S$.

The exact Bellman dynamic program in the audit script allows every subset
action and every causal policy. By the action reduction, it also gives the
all-pressure value in the unrestricted-movement regime. At $H=N$ post-initial
rounds, for the parameter rows $E_S/C/C_{\rm sink}=$
$20/50/30$, $20/45/30$, $20/55/30$, and $20/100/20$, the values for
$N=2,\ldots,7$ are respectively:

| $E_S/C/C_{\rm sink}$ | exact post-initial values at $N=2,\ldots,7$ |
|---|---|
| $20/50/30$ | $20,40,60,80,100,120$ |
| $20/45/30$ | $17.5,35,52.5,70,87.5,105$ |
| $20/55/30$ | $22.5,45,67.5,90,112.5,135$ |
| $20/100/20$ | $40,60,80,100,120,140$ |

These are exact all-pressure values in the unrestricted-movement regime,
because of the pointwise action domination above. They do not establish a
new control limitation: the resulting Bellman problem is itself a
finite-horizon decision tree with outcome-dependent costs.

## 5. Finite-movement geometry of the canonical probes

The unrestricted action reduction does not automatically survive a movement
constraint. This section gives exact reachability within the canonical
subset-probe family and the exact diameter threshold at which the
unrestricted Bellman value is attainable by physical pressures.

Represent a canonical test of subset \(P\subseteq[N]\) by the relative
score-offset vector

$$
x(P)=a(\mathbf1_P,0)\in\mathbb R^{N+1},\qquad m<a<M,
$$

where the final coordinate is the sink. The gauge-invariant metric between
two such states is

$$
d(P,Q)^2=\left\|P_0\left(x(P)-x(Q)\right)\right\|_2^2
=a^2\left(r+s-\frac{(r-s)^2}{N+1}\right),
\tag{M1}
$$

where \(r=|P\setminus Q|\) and \(s=|Q\setminus P|\). For \(\delta=0\),
the transition \(P\to Q\) is feasible in one pressure update exactly when
the right side of (M1) is at most \(\beta^2\). From the initial zero
pressure (the empty subset),

$$
d(\varnothing,P)^2=a^2\left(|P|-\frac{|P|^2}{N+1}\right).
\tag{M2}
$$

These formulas distinguish three thresholds:

- The chosen fixed canonical representative of a singleton probe is
  reachable from zero iff \(\beta\ge a\sqrt{N/(N+1)}\). This is not the
  distance to the full singleton-test cell: the E=4 note dated 2026-10-17
  gives a point in that same cell approaching distance \(1/\sqrt2\).
- Switching between two distinct singleton probes costs exactly
  \(a\sqrt2\), independent of \(N\).
- Every canonical subset state is reachable from every other in one update
  iff
  $$
  \beta\ge a\sqrt{\max_{0\le d\le N}
    \left(d-\frac{\sigma_d^2}{N+1}\right)},\qquad
  \sigma_d=\begin{cases}0&d\text{ even},\\1&d\text{ odd.}\end{cases}
  \tag{M3}
  $$
  The maximum is attained at \(d=N\): it is \(N\) for even \(N\), and
  \(N-1/(N+1)\) for odd \(N\).

For (M3), write \(d=r+s\). At fixed \(d\), the smallest possible
\(|r-s|\) is zero for even \(d\) and one for odd \(d\). The largest
squared distance at that symmetric-difference size is therefore the
expression in (M3). It increases with \(d\) on \(0\le d\le N\), so the
maximum occurs at \(d=N\). This is the exact diameter threshold for the
chosen canonical representatives, sharpening the sufficient bound
\(a\sqrt N\).

For any finite \(\beta\), the policy class restricted to the **fixed
canonical representatives** \(x(P)=a(\mathbf1_P,0)\) has an exact Bellman
recursion on posterior support \(U\) and current representative \(P\):

$$
W_h(U,P)=\frac1{|U|}\sum_{i\in U}J_i(P)
+\sum_{B\in\mathcal P_P(U)}\frac{|B|}{|U|}
  \min_{Q:\,d(P,Q)\le\beta}W_{h-1}(B,Q),\qquad W_0=0,
\tag{M4}
$$

where \(\mathcal P_P(U)\) is the admitted-observation partition under
representative \(P\), and \(d\) is (M1). The minimum is inside the block sum
because the next probe may depend on the observed block. The initial state
is \(P=\varnothing\), so the first test incurs no additional movement;
each later transition must satisfy (M1). This is exact only for the stated
fixed-representative restriction. Allowing any pressure point inside a
singleton-test cell changes the reachability problem, as the E4 construction
in [`phase1_full_pressure_cell_dp_gate_2026-10-17.md`](phase1_full_pressure_cell_dp_gate_2026-10-17.md)
demonstrates.

When (M3) holds, every transition between fixed canonical representatives is
feasible. The
pointwise action-domination theorem from Section 4 then gives both sides:
the unrestricted all-pressure value is a lower bound on the movement-limited
physical value, while an optimal unrestricted subset-probe tree is physically
reachable. Therefore the all-pressure Bellman value in Section 4 is also the
exact physical value in this high-movement regime. Below (M3), domination
alone proves no value equality: the canonical replacement may be outside the
reachable ball even when the original pressure is reachable.

This movement calculation remains an exact instance-level reduction to a
metric-constrained test tree. It does not separate MoE control from metric-
constrained adaptive testing.

## 6. Prior-art boundary and novelty gate

The immediate reduction attack is substantial. Cicalese, Laber, and
Saettler's decision-tree framework uses pair-separation cost as a lower-bound
tool; a companion paper by Saettler, Laber, and Cicalese explicitly studies
tests whose costs depend on their outcomes. Here a pressure is a test, its
outcome is $A$, and overflow is exactly the outcome function
$KT-\mathbf1^\top A$. Our $Δ_q(S)$ is the expected number of remaining
hypotheses eliminated, equivalently the uniform-prior mass of separated
ordered pairs divided by $s$. Therefore even a proof of (PS) is not
automatically a new decision-tree principle. The static-world, unrestricted-
movement case is a bounded-depth decision tree with outcome-dependent cost;
the gauge movement budget adds a transition constraint between tests, which
must be compared separately. If the MoE theorem is exactly recovered by that
induced state-constrained test system, the right claim is an exact MoE
realization, not a new general control limitation.

Primary sources: Cicalese, Laber, and Saettler, “Diagnosis determination:
decision trees optimizing simultaneously worst and expected testing cost,”
PMLR 32 (2014), especially its pair-count potential and separation-cost lower
bound ([paper PDF](https://proceedings.mlr.press/v32/cicalese14.pdf)); and
Saettler, Laber, and Cicalese, “Approximating decision trees with value-
dependent testing costs,” *Information Processing Letters* 115 (2015)
([DOI page](https://doi.org/10.1016/j.ipl.2015.02.006)). The papers' models
and objectives are not identical to our finite-horizon,
movement-constrained overflow control problem. The overlap is substantial
enough that any novelty claim around (PS) must be stated as a structural
property derived from Top-1 realizability, then tested against that broader
decision-tree benchmark rather than claimed from pair separation itself.

Movement-constrained active hypothesis testing is also established outside
decision-tree theory. Atanasov et al. formulate active M-ary hypothesis
testing for a mobile depth sensor, include physical movement and observation
costs, and solve a belief-state planning problem by dynamic programming
([ICRA 2013 paper](https://natanaso.github.io/ref/Atanasov_Sankaran_ActiveObjectRecognition_ICRA13.pdf)).
This rules out presenting the generic combination “adaptive testing plus a
moving action state” as new. Their observation model and decision loss differ
from ours: they use viewpoint-dependent noisy detections and classification
loss, while this E-world model uses deterministic Top-1 requests, capacity
clipping, and overflow. That difference is a candidate application boundary,
not yet a theorem-level separation. Metric movement in online learning is
another adjacent literature, with different information and regret models
([Koren, Livni, and Mansour, COLT 2017](https://proceedings.mlr.press/v65/koren17a.html)).

## 7. Next gate and stop conditions

1. **Complete:** the pointwise action domination is proved, and the exact
   unrestricted Bellman recurrence is stated. The E=4 all-pressure audit
   agrees with the recurrence on its checked cases.
2. **Complete for canonical probes:** (M1)–(M4) give exact finite-movement
   reachability and values within the subset-probe class. **Open for all
   pressures below (M3):** the exact state remains continuous pressure within
   each arrangement face; a face-to-face minimum-distance table is not an
   exact Bellman state. The recursion and the required strict comparison with
   canonical probes are recorded in
   [`phase1_full_pressure_cell_dp_gate_2026-10-17.md`](phase1_full_pressure_cell_dp_gate_2026-10-17.md).
3. Compare that full cell-state problem with metric-constrained
   polyhedral/adaptive testing. The current finite-horizon Top-K experiment
   has an exact polyhedral simulation, so a fixed-instance novelty claim is
   impossible by construction. A new claim requires a family-level theorem
   that the independent benchmark cannot preserve.
4. Stop the “new control limitation” claim if the full continuous-pressure
   Bellman problem transfers unchanged to the independent benchmark. Keep the
   all-pressure result as an exact structured MoE application unless a
   separate family-level Top-K/gauge separation is proved.

No experiment sweep, neural-model training run, or claim of conference-level
novelty is made in this phase.

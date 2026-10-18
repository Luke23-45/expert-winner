# G3 steering analysis: finite-horizon value calculation

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status (reconciled 2026-10-17):** the fixed E=3 calculation, its
small-\(B\) first-reachable-horizon result, and the separate long-horizon
probe-versus-wait theorem are documented in this note and its linked
companion. Those mathematical results are no longer open. They remain exact
MoE realizations of a state-constrained adaptive-testing problem; a
Top-K/gauge result beyond that representation is not established. See the
[current research ledger](phase1_research_status_2026-10-17.md).

This note supersedes the earlier heuristic that estimated the admitted cost
as approximately (1.5) times an open-loop steering cost. That estimate was
not a policy lower bound and omitted observation-dependent branching. The
original grid scripts also used an inexact circular reachability test; that
test has been corrected. The reproducible finite-grid Bellman diagnostic is
[`analyze_e3_grid_dp.py`](../../scripts/analyze_e3_grid_dp.py); its values are
not continuous-space certificates.

## 1. Exact pressure geometry

Let $u=P_0(q)$, $x=\gamma(u_1-u_3)$, and
$y=\gamma(u_2-u_3)$. With $\delta=0$,

$$
\|u'-u\|_2^2=\frac{2}{3\gamma^2}
\left((\Delta x)^2-\Delta x\Delta y+(\Delta y)^2\right).
$$

To see the metric, the centered difference is
$(3\gamma)^{-1}(2\Delta x-\Delta y,\,2\Delta y-\Delta x,\,-\Delta x-\Delta y)$;
squaring its coordinates gives the displayed identity. The update permits
this centered norm to be at most $r=\eta\gamma B$, so the exact reach set is
the following ellipse in score-difference coordinates:

$$
(\Delta x)^2-\Delta x\Delta y+(\Delta y)^2
\le \frac32(\eta\gamma^2B)^2.
\tag{Reach-xy}
$$

The previous scripts checked Euclidean distance against a circular bound.
That circle allowed some infeasible edges. Both steering scripts now check
`Reach-xy`; their discretized shortest paths are still exploratory and are
not policy-value bounds. The score-arrangement enumerator now uses exact
rational arithmetic for line intersections, tie strata, costs, and the
displayed reach witnesses. The separate finite-grid Bellman diagnostic
remains a numerical check only.

## 2. Finite-horizon value calculation for the documented $E=3$ instance

Use $C=50$, $E_S=20$, $C_{sink}=30$, $m=1$, $M=3$,
$\eta=0.1$, $\gamma=1$, $B=2.65$, and $\delta=0$. Thus the
pressure-step radius in the original centered-pressure norm is
$r=\eta\gamma B=0.265$. The prior is uniform over the two static worlds,
and $q_0=0$. The objective is raw cumulative overflow.

The exact winner inequalities and 13-row outcome table are proved in
[`phase1_cost_info_lemma_2026-10-16.md`](phase1_cost_info_lemma_2026-10-16.md).
The rational checker [`analyze_e3_exact_partition.py`](../../scripts/analyze_e3_exact_partition.py)
independently validates the line arrangement, including tie strata.
Across the enumerated signatures:

- every uninformative pressure has equal world costs, each at least 20;
- every informative pressure has equal-prior expected overflow at least 20;
- in each world, every nonzero overflow value is at least 20.

For $|x|,|y|\le1$, the four token types retain their origin winners:
$(d_{1L},d_{1H},d_{2L},d_{2H})=(1,1,2,2)$ in one-based expert indices.
Thus $A^1=A^2=(C,C,0)$ and both worlds have overflow $E_S$ throughout this
closed square. Consequently, any informative state or zero-overflow state
must satisfy $|x|>1$ or $|y|>1$. For fixed $x$, the quadratic form
$Q(x,y)=x^2-xy+y^2$ is minimized at $y=x/2$, where $Q=3x^2/4$; by symmetry
the same holds with $x,y$ exchanged. Its infimum outside that square is
therefore $3/4$, corresponding to centered-pressure distance
$\sqrt{2Q/3}=1/\sqrt{2}$. Since $2r=0.53<1/\sqrt{2}$, no policy can
reach an informative or zero-overflow pressure in fewer than three updates.

### Requested-feedback value

For world 1, take the pressure sequence in $(x,y)$ coordinates

$$
(0,0),\quad (1.01/3,0.505/3),\quad (2(1.01/3),2(0.505/3)),\quad
(1.01,0.505).
$$

Each update has centered-pressure norm $0.2381<0.265$. The first three
visited pressures cost 20 in world 1; the last has zero overflow. World 2 uses the symmetric sequence. The distance argument and the
complete winner/cost table in the companion lemma give the matching lower
bound. Consequently,

$$
V_R(H)=60\qquad(H\ge 3).
$$

### Admitted-feedback value

The first informative pressure cannot occur before the fourth visited
pressure (three updates). Before that, the observation is shared by both
worlds. The complete cell table shows that each of those first four rounds
has expected cost at least 20, whether its observation is informative or not.
Hence $V_A(H)\ge80$ for $H\ge4$.

For an attaining policy, use the common pressure sequence

$$
(0,0),\quad (1.01/3,0.3),\quad (2(1.01/3),0.6),\quad (1.01,0.9).
$$

The first three updates have centered-pressure norm $0.2613<0.265$. The
first three round costs are 20 in each world. At the fourth pressure the
admitted vectors differ: world 1 costs 0 and world 2 costs 40, so the
observation identifies the world. In the fifth round, world 1 holds its
pressure; world 2 moves to $(0.99,1.01)$, a feasible step of norm
0.0990, where its overflow is zero. Later rounds hold the selected
zero-overflow pressure. Thus

$$
V_A(H)=80\qquad(H\ge4),\qquad
V_A(H)-V_R(H)=20\qquad(H\ge4).
$$

At $H=3$, neither policy can reach an informative pressure and both values
are 60. This exact instance **does not produce a horizon-growing raw gap**. It
proves a finite signal-value gap for the stated plant and prior; it does not
close the parameterized G3 problem or establish irreducibility relative to
constrained adaptive testing.

## 3. Finite-grid Bellman computation and its limits

[`analyze_e3_grid_dp.py`](../../scripts/analyze_e3_grid_dp.py) computes the
optimal finite-horizon values on a pressure lattice. Its transitions use the
exact `Reach-xy` ellipse, and its Bellman update allows the policy to branch
on admitted observations. For $B=2.65$, extent 6, the grid results were:

| Grid points per axis | Spacing | (H=4): requested / admitted | (H=5): requested / admitted |
|---:|---:|---:|---:|
| 61 | 0.20 | 80 / 80 | 100 / 100 |
| 121 | 0.10 | 80 / 80 | 80 / 100 |
| 241 | 0.05 | 60 / 80 | 60 / 90 |

These are exact values **for their respective finite action grids**, not
certified values for continuous pressure. The non-monotone refinement is a
warning that coarse grids miss narrow useful cells; the $H=5$, $n=241$
admitted value of 90 misses the explicit continuous-pressure policy of cost
80 above. Do not use the lattice table as a continuous-space result. The fixed-instance
value claim rests on the analytic reach argument and the explicit winner/cost
table in the companion lemma, not on the lattice values.

## 4. Long-horizon update and remaining open questions

The admitted value beyond the first reachable horizon is now bounded by the
analytic all-policy theorem in
[`phase1_probe_wait_value_theorem_2026-10-16.md`](phase1_probe_wait_value_theorem_2026-10-16.md).
For sufficiently long horizons,

$$
E_S\frac{\sqrt{2/3}}{\beta}\le V_A(H)
\le E_S\left(\left\lceil\frac{\sqrt{2/3}}{\beta}\right\rceil+2\right),
\qquad \beta=\eta\gamma^2B,
$$

while $V_R(H)=E_S(\lfloor1/(\sqrt2\beta)\rfloor+1)$. The raw value gap
therefore grows as
$E_S(\sqrt{2/3}-1/\sqrt2)/\beta+O(E_S)$; this is distinct from the
constant $E_S$ gap at the first reachable horizon. The lower bound covers
all causal randomized admitted policies and explicitly charges the probe and
post-probe travel.

At the theorem's sufficient horizon scale $H=\Theta(1/\beta)$, the lower
bound also yields a positive limiting normalized gap; for the stated
parameters it is at least approximately `0.00779`. This does not imply a
positive normalized gap for horizons growing faster than that scale.

The exact abstraction remains constrained adaptive testing with the same
score-cell outcomes, outcome-dependent costs, and gauge-induced transition
metric. The theorem is therefore an exact MoE specialization, not yet a
separation from generic constrained-testing theory. The open research gate
is a parameterized $E$/$K$/$C$ result with a quantitative Top-K/gauge
property that survives the reduction attack. The T7 hidden-compounding
paired-world proposal is invalid as phrased; see
[`phase1_t7_trajectory_audit_2026-10-16.md`](phase1_t7_trajectory_audit_2026-10-16.md).

No large parameter sweep or trained-model experiment was run.

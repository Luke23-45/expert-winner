# G3 steering analysis: finite-horizon value calculation

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status:** computer-assisted value calculation for one (E=3), two-world
parameter instance. Its hand-checkable score-cell proof, general small-(B)
scaling, and reduction attack remain open.

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
not policy-value bounds. The score-arrangement enumerator uses floating-point
LP and intersection calculations, so its output is a reproducible
computer-assisted check, not a rational-arithmetic certificate.

## 2. Finite-horizon value calculation for the documented $E=3$ instance

Use $C=50$, $E_S=20$, $C_{sink}=30$, $m=1$, $M=3$,
$\eta=0.1$, $\gamma=1$, $B=2.65$, and $\delta=0$. Thus the
pressure-step radius in the original centered-pressure norm is
$r=\eta\gamma B=0.265$. The prior is uniform over the two static worlds,
and $q_0=0$. The objective is raw cumulative overflow.

A score-line arrangement enumeration gives 13 pressure-outcome signatures,
including lower-dimensional tie strata. The finite-case verification uses
floating-point LP and intersection calculations; it is not a standalone
formal proof. The reproducible
enumerator is [`analyze_e3_exact_partition.py`](../../scripts/analyze_e3_exact_partition.py).
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
enumerated cell-cost table give the matching lower bound, subject to the
proof gap stated above. Consequently,

$$
V_R(H)=60\qquad(H\ge 3).
$$

### Admitted-feedback value

The first informative pressure cannot occur before the fourth visited
pressure (three updates). Before that, the observation is shared by both
worlds. The enumerated cell-cost check indicates that each of those first
four rounds has expected cost at least 20, whether its observation is
informative or not; this inequality still needs a hand-checkable cell proof.
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
are 60. This exact instance **does not produce a horizon-growing raw gap**.
It demonstrates a finite signal-value gap for the stated plant and prior;
it does not close the general G3 problem or establish that the result is
irreducible relative to constrained adaptive testing.

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
80 above. Do not use the lattice table as a continuous-space result. The instance
value claim rests on the analytic reach argument and the enumerated cell
inequalities; those inequalities still need a hand-checkable proof before
this becomes a paper-ready theorem.

## 4. What remains open

1. Derive a theorem for a parameterized small-$B$ regime, with explicit
   $H(B)$, capacities, margins, and prior. Do not call a $B$-dependent
   transient “horizon-growing” unless the theorem proves that scaling.
2. Prove a matching lower bound for every causal randomized admitted policy
   in that regime; an open-loop Dijkstra path is not sufficient.
3. Compare the theorem to a general state-constrained adaptive-testing or
   belief-state control model. The $E=3$ result alone is an instance, not
   evidence that Top-K/gauge geometry yields a new general theory.
4. If the lower bound reduces to a constrained testing instance, state that
   honestly. A stronger MoE claim needs a property of the score-cell geometry
   or reachability metric that the abstract model does not preserve.

No large parameter sweep or trained-model experiment was run.

# E=4 exact witness for admitted-field non-cyclic-monotonicity

This note gives an independent higher-dimensional witness for the structural
counterexample in
[`admitted_feedback_noncyclicity_2026-10-17.md`](admitted_feedback_noncyclicity_2026-10-17.md).
It remains inside the existing hard per-expert clipping model.

## Exact plant

Set $E=4$, $K=1$, $T=4$, $C=(1,1,1,1)$, and
$\mu=(1/4,1/4,1/4,1/4)$. Thus $\sum_e C_e=KT$. Let $\gamma=1$ and use the
following rational affinity rows:

$$
A=\begin{pmatrix}
157/125 & 191/100 & 7617/1000 & 1657/500\\
13/50 & 3131/500 & 3273/500 & 6587/1000\\
4253/1000 & 3437/500 & 6103/1000 & 487/500\\
1533/500 & 377/125 & 1373/1000 & 7297/1000
\end{pmatrix}.
$$

Use quotient coordinates $p=(q_1-q_4,q_2-q_4,q_3-q_4)$ and chart
representative $q=(p_1,p_2,p_3,0)$. At the five listed states, every Top-1
selection is strict.

| $i$ | Quotient point $p_i$ | $R(p_i)$ | $A(p_i)=\min(R,C)$ | $P_0(KT\mu-A)$, first three coordinates | Minimum score margin |
|---:|---|---|---|---|---:|
| 0 | $(-2501/1000,-3043/1000,-1579/500)$ | $(0,1,2,1)$ | $(0,1,1,1)$ | $(3/4,-1/4,-1/4)$ | $399/1000$ |
| 1 | $(133/40,457/1000,-97/125)$ | $(0,0,3,1)$ | $(0,0,1,1)$ | $(1/2,1/2,-1/2)$ | $231/500$ |
| 2 | $(-79/200,347/200,-3657/1000)$ | $(0,0,3,1)$ | $(0,0,1,1)$ | $(1/2,1/2,-1/2)$ | $2267/1000$ |
| 3 | $(-533/500,417/250,1097/500)$ | $(1,0,1,2)$ | $(1,0,1,1)$ | $(-1/4,3/4,-1/4)$ | $113/1000$ |
| 4 | $(-517/1000,33/25,3853/1000)$ | $(0,1,1,2)$ | $(0,1,1,1)$ | $(3/4,-1/4,-1/4)$ | $9/20$ |

The routes are evaluated from the one fixed affinity batch at each pressure;
there are no ties. Adding a common constant to a chart representative gives
its nonnegative, minimum-zero pressure representative and does not change any
route.

## Exact cyclic-monotonicity violation

For the order $p_0,p_1,p_2,p_3,p_4,p_0$, exact rational arithmetic gives
$$
\sum_{i=0}^{4}\langle P_0(KT\mu-A(p_i)),p_{i+1}-p_i\rangle
=\frac{733}{2000}>0.
$$
This violates the necessary cyclic-monotonicity condition for subgradients of
a convex function. On the same cycle, the requested field gives
$$
\sum_{i=0}^{4}\langle P_0(KT\mu-R(p_i)),p_{i+1}-p_i\rangle
=-\frac{1001}{125}<0.
$$
As in the $E=3$ witness, this proves that no convex potential can have the
admitted field as a subgradient at all these states; it does not establish a
closed-loop performance claim.

## Replica family and audit

For any integer $m\ge1$, repeat each affinity row $m$ times and set
$T=4m$, $C=(m,m,m,m)$. The five route patterns and score margins are
unchanged, the centered fields scale by $m$, and the admitted cyclic sum is
$733m/2000$, or $733/8000$ per token. The exact script checks $m=1,2,5$ and
asserts these identities:

```powershell
python scripts/audit_admitted_noncyclicity_e4.py
```

The minimum score margin is $113/1000$, so any entrywise affinity perturbation
smaller than $113/2000$ preserves every listed route and the violation.

The convex-analysis implication uses the necessary direction of Rockafellar's
cyclic-monotonicity characterization; see the original
[1966 paper](https://msp.org/pjm/1966/17-3/pjm-v17-n3-p08-p.pdf). No novelty
claim is made for that general theorem.

## Scope

This gives strict, capacity-balanced counterexample families at both $E=3$
and $E=4$, with nonzero violation per token. It does not yet characterize all
Top-K instances, give an $E$-uniform lower bound, establish instability or
overflow regret, or separate from the general polyhedral adaptive-testing
benchmark. Those remain the relevant broader research questions.

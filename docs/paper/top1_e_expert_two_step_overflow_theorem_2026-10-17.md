# Arbitrary-expert Top-1 two-step overflow theorem

This strengthens the $E=3$ result in
[`heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md`](heterogeneous_capacity_two_step_overflow_theorem_2026-10-17.md)
without changing its controller, admission rule, or overflow objective.

## Theorem

Fix any integer $E\ge2$. Use the canonical pressure model with $K=1$,
$\gamma=1$, uniform target $\mu=\mathbf1/E$, zero leak, and $q_0=0$.
Affinities are iid $U[0,1]$ and the same static $T\times E$ affinity matrix
is used for both routing steps. Fix rational capacities
\[
\frac{C_1(T)}{T}=\frac1E-r,\qquad
\frac{C_e(T)}{T}=\frac1E+\sigma_e\quad(e=2,\ldots,E),
\]
where $0<r<1/E$, $\sigma_e\ge0$, and $\sum_{e=2}^{E}\sigma_e=r$.
Take $T\to\infty$ through values for which all capacities are integers.
For requested or admitted feedback, update once by the canonical rule
\[
q_1^L=\Pi_g\!\left(\eta\left(L_0/T-\mu\right)\right),
\qquad L\in\{R,A\},
\]
then route the same batch at $q_1^L$. Let $J_s^L$ be the total overflow at
step $s$ under that signal's pressure trajectory.

For every fixed $\eta>0$ with $d=\eta r<1$,
\[
\boxed{\lim_{T\to\infty}\frac1T
\mathbb E\!\left[(J_0^A+J_1^A)-(J_0^R+J_1^R)\right]
=d-\frac{d^E}{E}>0.}
\]
The limit depends on the capacity vector only through the under-capacity
amount $r$ and expert count $E$; it is independent of the split
$(\sigma_2,\ldots,\sigma_E)$. The first-step cost is identical in the
paired arms; the entire limiting difference is generated on step two. A
no-feedback arm, which holds $q=0$, has the same limiting two-step cost as
requested feedback.

## Proof

At $q_0=0$, exchangeability and the strong law give
$R_0/T\to\mathbf1/E$ almost surely. Hence
$A_0/T\to(1/E-r,1/E,\ldots,1/E)$. The requested update tends to zero. The
admitted error tends to $(-r,0,\ldots,0)$, so after gauge projection its
pressure tends to $(0,d,\ldots,d)$, where $d=\eta r$.

At this limiting admitted pressure, expert 1 wins exactly when its uniform
score $U_1$ exceeds every shifted competitor $U_e-d$. Its population
probability is
\[
p_1^{(E)}(d)=\int_0^1\min\{1,x+d\}^{E-1}\,dx
=\frac1E+d-\frac{d^E}{E}.
\]
The other experts are symmetric and each has probability
$(1-p_1^{(E)}(d))/(E-1)<1/E$. Their capacities are at least $1/E$, so their
limiting overflow is zero. Expert 1's admitted-arm overflow fraction is
$p_1^{(E)}(d)-(1/E-r)$. Under requested feedback, the limiting route
probabilities remain uniform and only expert 1 overflows, by fraction $r$.
Subtracting gives $p_1^{(E)}(d)-1/E=d-d^E/E$.

For the shared-batch two-step argument, $q_1^L$ converges almost surely by
the first-step strong law and continuity of clipping and gauge projection.
For fixed $E$, the Top-1 winner sets indexed by pressure form a finite-VC
class: each expert's winning region is an intersection of $E-1$ affine
score-comparison half-spaces. The empirical winner proportions therefore
converge uniformly on a compact neighborhood of the limiting pressure. The
population proportions are continuous there because the iid continuous
affinities have zero tie probability. This uniform law handles the fact that
$q_1^L$ is computed from the same affinity matrix used on step two. Thus the
normalized paired cost gap converges almost surely to the displayed value.
It is bounded, so its expectation converges as well. \(\square\)

## Scope

This is an exact family-level performance consequence of the existing
canonical Top-1 clipping and pressure equations. It does not prove a ranking
for arbitrary causal policies, other affinity laws, $K>1$, trained models,
or telemetry cost. Each finite affinity instance remains exactly
representable by the project's outcome-map benchmark; this theorem alone is
not a class-level separation from that benchmark. The registered expert-
count experiment is in
[`top1_e_expert_overflow_protocol_2026-10-17.md`](top1_e_expert_overflow_protocol_2026-10-17.md).

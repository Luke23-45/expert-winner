# Exact common-action value for an arbitrary-E Top-1 swapped family

**Status:** exact one-step population theorem with a complete lower-bound
certificate. It is a Top-1 family result, not a multi-round theorem or a
separation from generic censored active testing.

## Model

Fix `E>=3`, let `n=E-2`, and set `K=1`. There are two equally likely
static worlds. In world 0, the Top-1 Gumbel score weights are

```text
(5/4, 1, 1/n, ..., 1/n),
```

and world 1 swaps the first two weights. The exact target/admission
fractions are

```text
c_1=c_2=1/4,       c_j=1/(2n)  (j=3,...,E).
```

They sum to one. Equivalently, `c` is the Top-1 inclusion vector at target
weights `(1/2,1/2,1/n,...,1/n)`. Requests are iid over the batch; admission
is the canonical per-expert clip `A_e=min(R_e,C_e)`. The one-step population
overflow at pressure `q` in world `h` is

```text
L_h(q)=sum_e (rho^h_e(q)-c_e)_+ = TV(rho^h(q),c).
```

The common-action value is `v*=inf_q (L_0(q)+L_1(q))/2`, with unrestricted
pressure modulo common shifts.

At the initial pressure, world-0 inclusion probabilities are
`p_1=5/13`, `p_2=4/13`, and `p_j=4/(13n)` for `j>=3`. Thus both first
experts are strictly saturated relative to `c`, while every other expert
is strictly below capacity. World 1 swaps the first two probabilities.

## Theorem

For every `E>=3` in this family,

```text
v*=1/36.
```

Consequently, the optimal common pressure has population overflow at least
`1/36`, while a world-aware pressure can set `rho=c` and attain zero
population overflow.

## Proof

### 1. Reduce any pressure to three aggregate categories

Aggregate experts `3,...,E` into one category `o`. Total variation
contracts under aggregation, so for either world

```text
TV(rho^h(q),c) >= TV((rho^h_1,rho^h_2,rho^h_o),(1/4,1/4,1/2)).
```

For any common pressure, define positive numbers
`X=exp(-q_1)/z`, `Y=exp(-q_2)/z`, where
`z=(1/n)*sum_{j>=3} exp(-q_j)>0`. The two aggregate routing vectors are

```text
p^0=(rX,Y,1)/(1+rX+Y),
p^1=(X,rY,1)/(1+X+rY),       r=5/4.
```

Write their coordinates as `p^h_i`, and put
`d_0=1+rX+Y`, `d_1=1+X+rY`,
`A=1-rX-Y`, and `B=1-X-rY`. Since
`TV(p,c)=(1/2)*sum_i |p_i-c_i|`, the triangle inequality coordinatewise
gives

```text
TV(p^0,c)+TV(p^1,c)
 >= 1/2 * S,
S=|p^0_1-p^1_1|+|p^0_2-p^1_2|
  +|p^0_3-1/2|+|p^1_3-1/2|.
```

Direct substitution yields

```text
S = (r-1)*(X+Y+2*(r+1)*X*Y)/(d_0*d_1)
    + |A|/(2*d_0) + |B|/(2*d_1).
```

For `r=5/4`, on each sign region of `(A,B)`, subtracting `1/9` and
putting the result over the positive denominator
`9*(4+5X+4Y)*(4+4X+5Y)` gives these numerators:

```text
A>=0, B>=0:   -8*(25X^2+31XY+25Y^2-16)
A>=0, B<=0:   -20X^2+121XY-36X-20Y^2+36Y-16
A<=0, B>=0:   the preceding mixed polynomial with X,Y exchanged
A<=0, B<=0:    10*(16X^2+49XY+16Y^2-16).
```

Each numerator is nonnegative on its sign region:

1. For `A,B>=0`, `(X,Y)` lies in the polygon with vertices
   `(0,0),(4/5,0),(4/9,4/9),(0,4/5)`. The quadratic
   `25X^2+31XY+25Y^2` is convex and equals at most `16` at every vertex,
   hence throughout the polygon.
2. For `A,B<=0`, set `s=X+Y`. The constraints imply `s>=8/9`. If `s>=1`,
   `16X^2+49XY+16Y^2=16s^2+17XY>=16`. If `8/9<=s<=1`, both constraints
   imply `X,Y>=4(1-s)`, so
   `XY>=4(1-s)(5s-4)`. Therefore the same quadratic is at least
   `16s^2+68(1-s)(5s-4)`, a concave function of `s` equal to `16` at both
   interval endpoints and hence at least `16` throughout.
3. In the mixed region `A>=0,B<=0`, the feasible set has
   `0<=X<=4/9` and `4(1-X)/5<=Y<=1-5X/4`. The mixed numerator is concave
   in `Y`, so its minimum for fixed `X` is at an interval endpoint. At
   `Y=1-5X/4` it equals `-(45/2)X(9X-4)>=0`; at
   `Y=4(1-X)/5` it equals `-(72/5)X(9X-4)>=0`. The other mixed region is
   symmetric.

Thus `S>=1/9`, so the common-action population risk is at least
`(TV(p^0,c)+TV(p^1,c))/2 >= 1/36`. Aggregation cannot increase this lower
bound, so it holds for every pressure in the original E-expert system.

### 2. Attain the lower bound

Choose equal pressure on experts 1 and 2, equal pressure on all outside
experts, and `X=Y=4/9`. Then

```text
p^0=(5/18,4/18,1/2),
p^1=(4/18,5/18,1/2)
```

in the three-category aggregation. Assigning the outside mass uniformly
gives each outside expert probability `1/(2n)`, exactly its capacity.
Both world losses are `1/36`; hence `v*<=1/36`. Combined with the lower
bound, `v*=1/36`. `□`

## Claim boundary

This exact constant resolves the common-action optimization for one
arbitrary-E Top-1 family. It does not prove a multi-round lower bound, a
universal controller ranking, a telemetry-cost break-even, or a separation
from the general two-world censored decision / adaptive-testing benchmark.
The exact finite-batch experiment is specified separately; it audits the
signal and overflow predictions, not the benchmark novelty claim.

## Finite-batch signal-value corollary

The exact population value can be substituted into the finite-batch
requested/admitted theorem in
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md).
For this family, with `n=E-2`, the exact world-0 inclusion probabilities
and target fractions are

```text
p_1=5/13, p_2=4/13, p_j=4/(13n) for j>=3,
c_1=c_2=1/4, c_j=1/(2n) for j>=3, Delta=p_1-p_2=1/13.
```

For every integer `T` such that `T/4` and `T/(2n)` are integers, define
the coupling error and request-classification error bounds

```text
eps_A(T)=Pr[Bin(T,5/13)<T/4]+Pr[Bin(T,4/13)<T/4],
eps_R(T)=sum_{m=0}^T Pr[M=m] * e_m,
M ~ Bin(T,9/13),
e_m=Pr[Bin(m,5/9)<m/2]
    + (1/2)*1{m even}*Pr[Bin(m,5/9)=m/2].
```

For `eps_A`, couple the worlds by swapping the first two experts' Gumbel
coordinates. Outside counts then agree exactly, including when a tail expert
is itself clipped. When both first experts saturate, their admitted counts
are equal under the coupling, so the full admitted vectors agree. The
displayed union bound is the probability that at least one of those two
experts fails to saturate. For `eps_R`, condition on
`M=R_1+R_2`. Under world 0, `M~Bin(T,9/13)` and
`R_1|M~Bin(M,5/9)`. The displayed expression is exactly the error
probability of the randomized sign rule that chooses world 0 when
`R_1>R_2`, world 1 when `R_1<R_2`, and flips a fair coin on a tie. By
symmetry it is the same in world 1. The Chernoff bound
`eps_R(T) <= (4*(1+sqrt(5))/13)^T` is a simpler, looser alternative.

Let `b_T` be the expected normalized overflow of the world-aware target
pressure on a fresh batch:

```text
b_T = sum_e [ c_e*Pr[Bin(T-1,c_e)>=C_e]
              - c_e*Pr[Bin(T,c_e)>C_e] ],  C_e=T*c_e.
```

Convexity of each positive-part loss gives finite-batch expected overflow
at any pressure at least its population overflow (Jensen). Therefore the
admitted-policy lower bound needs no `O(E/sqrt(T))` approximation term.
For the requested policy, a correct sign decision costs exactly `b_T`; an
incorrect decision costs at most one.

Then the optimal one-step finite-batch values, over all causal policies
using the respective first-batch count vector, obey

```text
V_A(T) >= 1/36 - eps_A(T)/2,
V_R(T) <= b_T + eps_R(T),
V_A(T)-V_R(T) >= 1/36 - eps_A(T)/2 - eps_R(T) - b_T.
```

The first two inequalities are uniform over all admitted and requested
policies, respectively; the requested upper bound uses the sign classifier
and the two world-specific target pressures. They imply a strictly positive
finite-batch optimal-value gap for each fixed `E` at sufficiently large
admissible `T`. They are not a system-cost result and retain the exact
generic censored-decision reduction.

For scale only, a floating-point scan of the bound using the exact
`eps_R(T)` sum gives the following first positive admissible batch sizes on
the displayed E grid. These are diagnostics, not interval-certified
minimal-threshold claims:

| `E` | Capacity denominator `lcm(4,2(E-2))` | First numerically positive admissible `T` |
|---:|---:|---:|
| 3 | 4 | 704 |
| 4 | 4 | 832 |
| 8 | 12 | 1,356 |
| 16 | 28 | 2,492 |
| 32 | 60 | 4,620 |
| 64 | 124 | 8,556 |

These threshold evaluations use floating-point binomial tails and are
diagnostics, not interval-certified minimal thresholds. The registered
count-law experiment uses smaller batches; its classifier comparison is
positive, but the theorem's all-policy finite-batch lower bound is not
positive on those registered cells. This distinction is recorded in the
results document. The scan is reproducible with
[`audit_top1_finite_batch_value_thresholds.py`](../../scripts/audit_top1_finite_batch_value_thresholds.py);
its saved output is
[`finite_batch_bound_thresholds.json`](../../results/top1_arbitrary_e_exact_swapped_value/finite_batch_bound_thresholds.json).

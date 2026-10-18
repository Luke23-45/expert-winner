# Exact Bayes value for the arbitrary-Top-K swapped-pair experiment

**Status:** exact observation-optimality proof for the registered swapped
family and exact finite-batch values for the two registered target-pressure
actions. This is a post-run characterization of the experiment. It does
not optimize over the full continuous pressure space or defeat the generic
censored-testing reduction.

## Setup

There are `E>=3` experts and `1<=K<E`. Under world 0, every token requests
the unordered Gumbel-Top-K subset from Plackett-Luce weights
`(5/4,1,1,...,1)`. World 1 swaps the first two weights. The first two
capacities are equal, `C_1=C_2=C`; all other capacities are fixed and the
admitted signal is the full vector `A_e=min(R_e,C_e)`. This is the first
batch at the registered initial pressure `q=0`, so all outside experts have
equal scores. Each of `T` tokens routes independently. The prior over worlds
is uniform.

The two available next-batch actions are the world-0 target pressure and the
world-1 target pressure, each chosen to make the corresponding world's
population inclusion vector equal the capacity fraction `c`. The no-signal
policy chooses between these two actions without observing the first batch.

## Theorem 1: requested-count likelihood is determined by `R_1-R_2`

Let `S` be an unordered Top-K subset. Partition subsets into four types:
both first experts selected, neither selected, expert 1 only, or expert 2
only. Since all experts `3,...,E` have equal weights, permutation symmetry
makes every set of the same type have equal probability in world 0. The
number of sets of type “expert 1 only” and “expert 2 only” is the same,
`binom(E-2,K-1)`. Write their per-subset probabilities as `u` and `v`.
The strict inclusion ordering `rho^0_1>rho^0_2` follows from symmetry and
strict convexity of the Gumbel-Top-K random-utility surplus along the
`e_1-e_2` score direction, as proved in §3.1 of the
[population theorem](topk_swapped_saturation_value_theorem_2026-10-17.md).
It implies `u>v`: the
contribution of the one-only subsets to `rho^0_1-rho^0_2` is
`binom(E-2,K-1)(u-v)`, while both/neither subsets contribute zero.

Let `tau` swap labels 1 and 2. The world construction gives
`P_1(S)=P_0(tau(S))`. Thus the single-token likelihood ratio is `u/v` for
each expert-1-only subset, `v/u` for each expert-2-only subset, and 1 for
the both/neither types. For an ordered sequence of token subsets
`S_1,...,S_T`,

```text
P_0(S_1,...,S_T) / P_1(S_1,...,S_T)
  = (u/v)^(R_1-R_2).
```

Therefore the full requested-count vector `R` is sufficient for the binary
world decision, and its Bayes rule is: choose world 0 if `R_1>R_2`, choose
world 1 if `R_1<R_2`, and randomize on a tie. This holds for every `E,K`
in the stated equal-outside-weight family.

## Theorem 2: the full admitted vector has the same Bayes decision

The full admitted vector, not just its first two coordinates, is observed.
For any admitted vector `a` with `a_1>a_2`, every request vector in its
clipping fiber has `r_1>r_2`: the higher admitted count is below the common
cap, so it equals its request count, while the lower count cannot exceed
it. By Theorem 1, every request vector in this fiber favors world 0. The
case `a_1<a_2` is symmetric.

If `a_1=a_2<C`, every request vector in the fiber has `r_1=r_2`, so its
world likelihoods are equal. If `a_1=a_2=C`, the full clipping fiber is
invariant under `tau`, including its fixed other coordinates; `P_1(r)=
P_0(tau(r))` then makes the total likelihoods of the two worlds equal.
Hence the full-vector Bayes rule is the sign of `A_1-A_2`, with a
randomized tie. The other admitted coordinates do not improve the Bayes
decision for this family.

## Exact finite-batch error sums

For one token under world 0, define

```text
Z = 1{expert 1 selected} - 1{expert 2 selected} in {-1,0,+1},
p_+ = P(Z=+1),  p_- = P(Z=-1),
p_b = P(both experts selected),  p_0 = P(neither selected).
```

Here `p_+>p_->0` and `p_++p_-+p_b+p_0=1`. Let `M` be the number of
tokens with `Z!=0`. Then

```text
M ~ Bin(T,p_++p_-),
N_+ | M=m ~ Bin(m,p_+/(p_++p_-)),
N_b | M=m ~ Bin(T-m,p_b/(p_b+p_0)),
```

where `N_b` is the number of neutral tokens selecting both experts. Given
`M`, `N_+` and `N_b` are independent. The request Bayes error is the sum of
`P(M=m)` times

```text
P(N_+ < m/2 | M=m) + 0.5*P(N_+=m/2 | M=m).
```

For admitted feedback, put `N_-=m-N_+`, and define `B=N_b`. The
conditional error for a pair `(n_+,n_-)` is

```text
g(n_+,n_-) = P(B < C-n_+) + 0.5*P(B >= C-n_+)   if n_+ < n_-,
              0.5                                      if n_+ = n_-,
              0.5*P(B >= C-n_-)                     if n_+ > n_-.
```

The first line accounts for a preserved wrong sign below capacity and a tie
when both first experts clip to `C`. The last line counts only such a
clipped tie as an error. Summing `g` over the two conditional binomials gives
the exact admitted Bayes error. The implementation evaluates these finite
binomial sums and stores both errors and risks in
[`summary.json`](../../results/topk_swapped_saturation_value/summary.json).

## Exact decision values and scope

Let `L_c` be the expected normalized overflow after choosing the target
pressure for the true world, and `L_w` the expected overflow after choosing
the other target pressure. World-swap symmetry gives the same `L_c,L_w`
under either world. In every registered cell `L_w>L_c`. Therefore, within
the two-target-action class, a signal with Bayes error `e` has exact value

```text
V(e)=L_c + e*(L_w-L_c),
```

and the Bayes rules above minimize expected overflow in that class. The
no-signal value is `(L_c+L_w)/2`. The exact values appear beside the Monte
Carlo audit in the 33-cell result file.

The exact-rational verifier checks the Plackett-Luce one-only subset orbits
for every `K` at `E={3,4,6,8}` and compares the binomial formulas with
brute-force category-count enumeration in five `(E,K,T)` profiles. Its
finite-grid checks support the implementation; the proofs above establish
the stated family result. These values do not optimize over all pressures,
prove a new general theory of censored experiments, measure hardware cost,
or establish a system-quality gain. The finite-instance experiment remains
exactly encodable as a generic censored Bayesian decision problem.

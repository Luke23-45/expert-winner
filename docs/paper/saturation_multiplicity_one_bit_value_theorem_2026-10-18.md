# One-bit decision sufficiency for the saturation-multiplicity theorem

**Status:** exact finite theorem for the declared two-target decision problem,
plus an all-pressure asymptotic corollary from the existing
[`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md).
The controlled exact-count audit is frozen in
[`saturation_multiplicity_one_bit_experiment_protocol_2026-10-18.md`](saturation_multiplicity_one_bit_experiment_protocol_2026-10-18.md).

## Model

There are `E>=3` experts and `1<=K<E`. Each token independently chooses its
Top-K subset using standard-Gumbel perturbations, equivalently a
Plackett-Luce ranking with positive weights. In world `+`, expert 1 has weight
`u`, expert 2 has weight `v`, and all other experts have a common weight `w`;
assume `u>v>0`. Also assume each subset containing expert 1 but not 2 has
strictly greater probability in world `+` than its swapped counterpart
containing expert 2 but not 1. This strict pair-subset ordering follows from
Plackett-Luce Top-K monotonicity for positive weights with `u>v`. World `-`
swaps `u` and `v`. A batch contains `T` tokens.
Write `R_e` for the number of requests to expert `e`, and let

```text
D = R_1 - R_2
Z = 1{D > 0}.
```

The target actions `q+` and `q-` are the swapped pressure vectors whose
population inclusion vectors equal the exact-total capacity fractions in
their corresponding worlds. Assume equal prior on the two worlds and that
the two target actions have equal correct-world risk `ell_c` and equal
wrong-world risk `ell_w`, with `ell_w > ell_c`. This equality follows from
the stated pair symmetry whenever the capacities are symmetric in experts 1
and 2 and the tail capacities are invariant under the swap.

## Theorem 1 — exact one-bit Bayes value in the two-action problem

For every finite `T`, under the assumptions above, the full requested-count
vector `R` and the single bit `Z` have exactly the same Bayes value for
choosing between `q+` and `q-`. The same is true of the joint signal `(A,Z)`
for any deterministic admission map `A=f(R)`:

```text
V_R^(2-action) = V_(A,Z)^(2-action)
                = ell_c + e_R(T) * (ell_w - ell_c),
```

where `e_R(T)` is the equal-prior Bayes classification error from `R` and is
also the error from `Z`. Thus one bit is sufficient to preserve the full
requested-vector value in this decision problem. If the admitted-only value
is strictly larger, zero additional bits are insufficient and one bit is
minimal among fixed-length messages.

### Proof

For a single token, partition its selected set into four categories: it
contains expert 1 but not 2; it contains expert 2 but not 1; it contains both;
or it contains neither. Because all tail weights are equal, every size-`K`
subset in the first category has the same probability in world `+`; call
that probability `a` per subset. Its swapped subset has probability `b` per
subset, with `a>b>0`. The two probabilities exchange in world `-`. Each
subset in the both/neither categories is invariant under swapping worlds.

For an ordered batch of selected subsets, let `N+` and `N-` be the counts of
the first and second categories. Its likelihood ratio is

```text
P(batch | +) / P(batch | -) = (a/b)^(N+ - N-).
```

Every ordered batch yielding the same request vector has the same difference
`N+ - N- = R_1-R_2 = D`. Summing the batch probabilities over that fiber
therefore gives the same likelihood ratio for the aggregate request vector:

```text
P(R=r | +) / P(R=r | -) = (a/b)^(r_1-r_2).
```

With equal priors and equal correct/wrong action losses, the Bayes action is
`q+` exactly when `D>0`, and `q-` when `D<0`; either action is Bayes-optimal
at `D=0`. This decision is a function of the bit `Z`, so `Z` attains the
full-`R` Bayes value. Since `Z` is recoverable from `R` and `(A,Z)` contains
`Z`, the Blackwell risk ordering gives
`V_R <= V_(A,Z) <= V_Z`; equality follows. If `A` alone has strictly larger
Bayes risk, a constant extra message cannot attain the full-`R` value, while
the one-bit message does. ∎

This is **decision-specific sufficiency** for a binary symmetric action
problem. It is not Blackwell sufficiency for every possible loss, not exact
reconstruction of `R`, and not enough to reproduce the requested pressure
update (Theorem T4b requires an injective message on the clipping fiber).

## Corollary 2 — one bit is asymptotically necessary and sufficient for value

Use the strict two-saturation conditions from the existing all-pressure
theorem: both swapped experts have a positive population overload margin in
both worlds, every tail expert has a positive under-capacity margin, and the
pair separation `u>v` is fixed. Assume the exact-total admissible batch-size
sequence of that theorem.

There is a one-bit policy that sends `Z` and chooses the corresponding target
pressure. Let `Delta = E_+[X] > 0`, where a token contributes `X=+1` if it
selects expert 1 but not 2, `X=-1` if it selects expert 2 but not 1, and zero
otherwise. Then `D` is the sum of `T` iid variables in `[-1,1]` with mean
`Delta` in world `+` and `-Delta` in world `-`. Hoeffding's inequality gives
`Pr(error) <= exp(-T*Delta^2/2)` for the bit decoder.

At its matching target pressure the population overflow is zero. For a fresh
batch, the normalized expected overflow is at most `E/(2*K*sqrt(T))`, by
coordinatewise variance bounds and 1-Lipschitz positive-part clipping.
Since normalized overflow is at most one, the one-bit policy obeys

```text
0 <= V_(A,Z)(T) - V_R(T)
   <= V_(Z,target)(T)
   <= E/(2*K*sqrt(T)) + exp(-T*Delta^2/2) -> 0.
```

The first inequality uses that full `R` is at least as informative as
`(A,Z)`. The existing saturation-multiplicity theorem supplies
`V_A(T)-V_R(T) -> v_*>0` under its strict two-saturation assumptions.
Consequently a zero-bit message (admitted counts alone) fails to recover the
requested-feedback value asymptotically, while one bit suffices. In this
precisely defined value sense, the minimum extra fixed-length message is one
bit. This is not a finite-`T` equality for the unrestricted continuous
pressure-action problem; the finite exact equality above is for the declared
two-target action set.

### Costed-observation consequence

Suppose the controller can either retain `A` alone or purchase the one-bit
message `Z` at price `kappa` measured in the same normalized-overflow units.
The optimal optional-observation value is

```text
V_optional(T,kappa) = min{V_A(T), kappa + V_(A,Z)(T)}.
```

Its break-even price is `kappa_1*(T)=V_A(T)-V_(A,Z)(T)`. By the asymptotic
one-bit sufficiency just proved and the existing two-saturation theorem,

```text
kappa_1*(T) -> v_* > 0.
```

Thus the same positive asymptotic decision value can be captured by a
one-bit payload in this family; the full `E`-count request vector is not
needed for this decision. Under one saturation, the existing reconstruction
theorem gives `V_A-V_R -> 0`, and information ordering gives
`0 <= V_A-V_(A,Z) <= V_A-V_R`, so the one-bit break-even tends to zero.
This is a price in task-loss units, **not** a hardware price. It does not
estimate the cost of computing or globally reducing `R_1-R_2`.

For the fixed two-action problem, the corresponding exact finite-`T`
break-even is
`(e_A(T)-e_R(T))*(ell_w-ell_c)`. The machine-checked held-out audit is in
[`saturation_multiplicity_one_bit_experiment_results_2026-10-18.md`](saturation_multiplicity_one_bit_experiment_results_2026-10-18.md).

## Relation to the professor's C2/C3 proposal and prior theory

This makes the “minimum additional information” part of the existing C2
value-of-information line concrete: full requested telemetry may carry more
information than this binary decision needs. The pair contrast is generated
by the Top-K request law; the coefficient and saturation transition remain
those proved in the existing Top-K theorem. However, compressing a binary
Bayes decision to its likelihood-ratio sign is classical statistical
decision theory, not a new generic information theorem. Blackwell's
comparison-of-experiments framework is the appropriate boundary
([Blackwell, *Comparison of Experiments*, 1951](https://digicoll.lib.berkeley.edu/record/112749/files/math_s2_article-08.pdf)).
The claim here is an exact MoE-family instantiation and its connection to the
Top-K saturation-value law. This does not defeat the project's exact
adaptive-testing representation and does not, by itself, establish
top-conference novelty.

One communicated bit is a payload bound only. Computing and globally
aggregating `R_1-R_2` may still require synchronization; no latency, bandwidth,
energy, or end-to-end system cost is inferred. The separate experiment uses
exact count laws and does not train a model.

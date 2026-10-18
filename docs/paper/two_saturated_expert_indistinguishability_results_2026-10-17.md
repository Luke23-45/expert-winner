# Two-saturated-expert experiment results

**Status:** exact one-batch law enumeration and a paired synthetic study were
rerun from the checked-in script on 2026-10-17. This is an asymptotic,
fixed-family mechanism result under canonical per-expert clipping; it is not a
universal controller theorem, real-system result, or novelty clearance.

## Locked design

The model, seed, and outcomes are specified in
[`two_saturated_expert_information_and_control_theorem_2026-10-17.md`](two_saturated_expert_information_and_control_theorem_2026-10-17.md)
and implemented by
[`run_two_saturated_expert_indistinguishability.py`](../../scripts/run_two_saturated_expert_indistinguishability.py).
There are three experts, Top-1 Gumbel-Max routing, two latent categorical
worlds `p0=(0.4,0.4,0.2)` and `p1=(0.5,0.3,0.2)`, exact-total capacities
`C/T=(0.25,0.25,0.5)`, and canonical admission `A=min(R,C)`. The experiment
uses `eta=15 log(2)`, uniform target, and a fresh second batch in the same
world. The primary outcome is normalized second-batch *population* overflow
after the first-batch update. Each row uses 20,000 first-batch multinomial
draws per world; requested, admitted, and no-update arms share the same draw.
Second-batch sampling noise is absent because the cost is evaluated from the
exact Gumbel-Max population probabilities at each updated pressure.

## Exact one-batch information results

The full request and admitted laws are enumerated with integer multinomial
weights. `TV_R` and `TV_A` are their exact total-variation distances between
the two worlds; Bayes error assumes equal prior probabilities.

| T | `TV_R` | `TV_A` | Request Bayes error | Admitted Bayes error |
|---:|---:|---:|---:|---:|
| 40 | 0.526326 | 0.180353 | 0.236837 | 0.409823 |
| 80 | 0.688757 | 0.133562 | 0.155622 | 0.433219 |
| 160 | 0.847683 | 0.069214 | 0.076159 | 0.465393 |
| 320 | 0.957011 | 0.020641 | 0.021494 | 0.489680 |
| 640 | 0.995787 | 0.002203 | 0.002106 | 0.498898 |

This is **asymptotic indistinguishability**, not equality of finite-sample
admitted laws. At every listed finite `T`, `TV_A>0`. The exact theorem bounds
`TV_A` above by exponentially small coupling-failure probabilities and
proves `TV_R -> 1` while `TV_A -> 0` along this family.

## Full finite-state expectation of second-batch population overflow

For each `T` and world, the runner enumerates every possible first-batch
multinomial count vector and sums its probability times the resulting
second-batch population overflow. The expectation has no first-batch Monte
Carlo error; log probabilities and softmax costs are evaluated in float64.
The 20,000-draw paired simulation remains as an independent sampling check.
`A-R` is the exact-enumeration admitted-minus-requested expected cost.

| T | World | Requested | Admitted | No update | Exact `A-R` |
|---:|:---:|---:|---:|---:|---:|
| 40 | 0 | 0.243492889 | 0.199847883 | 0.300000000 | -0.043645006 |
| 40 | 1 | 0.267505008 | 0.216156750 | 0.300000000 | -0.051348259 |
| 80 | 0 | 0.200435902 | 0.197370285 | 0.300000000 | -0.003065618 |
| 80 | 1 | 0.230254436 | 0.208831594 | 0.300000000 | -0.021422842 |
| 160 | 0 | 0.175310057 | 0.199664825 | 0.300000000 | 0.024354768 |
| 160 | 1 | 0.205900586 | 0.205837660 | 0.300000000 | -0.000062926 |
| 320 | 0 | 0.164731917 | 0.201742594 | 0.300000000 | 0.037010677 |
| 320 | 1 | 0.191456989 | 0.204487945 | 0.300000000 | 0.013030957 |
| 640 | 0 | 0.162729390 | 0.202863481 | 0.300000000 | 0.040134092 |
| 640 | 1 | 0.184469100 | 0.203891540 | 0.300000000 | 0.019422440 |

The asymptotic theorem predicts requested feedback has lower overflow in both
worlds, with limits `1/6` versus `0.20400314` in world 0 and `0.18266432`
versus `0.20400314` in world 1. Exact finite-state expectations show a
crossover: admitted feedback is better at `T=40` and `T=80`; at `T=160`, the
requested advantage is `0.02435` in world 0 while admitted is better by only
`0.000063` in world 1; requested feedback is better in both worlds at `T=320`
and `T=640`. The paired 20,000-draw estimates have the same sign in all ten
cells. This crossover is part of the result and rules out presenting
“requested always wins” as an empirical finding.

## Separate optimal-policy theorem

The companion theorem also solves the **asymptotic one-step decision problem**
over all gauge-fixed pressure actions, not just the three fixed update rules
in the table. In the admitted-only channel, the best common pressure has
equal-prior overflow exactly `1/32`; in the requested channel, a threshold
classifier followed by the world-specific balancing pressure has cost tending
to zero. Thus the asymptotic optimal signal value is `1/32` normalized
overflow units. This is proved using the exact observation-law TV bounds and
an odds-ratio lower bound on the best common action. It assumes no movement
constraint and does not assign a real communication cost to the request
signal. The exact finite-law enumeration also certifies finite-T bounds on
the best-policy gap:

| T | Lower bound on `V_A` | Upper bound on `V_R` | Lower bound on `V_A−V_R` | Upper bound on `V_A−V_R` |
|---:|---:|---:|---:|---:|
| 40 | 0 | 0.018016095 | -0.018016095 | 0.031250000 |
| 80 | 0 | 0.012586043 | -0.012586043 | 0.031250000 |
| 160 | 0 | 0.006911956 | -0.006911956 | 0.031250000 |
| 320 | 0.020929691 | 0.002431631 | 0.018498060 | 0.031250000 |
| 640 | 0.030148290 | 0.000365919 | 0.029782371 | 0.031250000 |

The lower bound on `V_A` uses the exact total-variation distance of the two
admitted laws; the upper bound on `V_R` uses the exact risk of the
threshold-and-balance policy. The positive gap lower bounds at `T=320,640`
compare one explicit requested policy against every admitted-only policy in
the one-step action class. The table earlier evaluates only the fixed
proportional updates.

## Interpretation and limits

The controlled experiment verifies that, for this two-world family, the
information gap grows with batch size and the asymptotic pressure update can
make use of the requested split. It also shows that the finite-horizon
controller comparison depends on batch size: the informative signal can
initially produce a worse action under the fixed gain, even though it wins
asymptotically in the specified family. The separate optimal-policy theorem
and finite-T certificates establish value of the observation channel under
the declared unrestricted one-step action class; they do not imply that the
fixed proportional controller is optimal.

The result does not establish windup for every admitted-feedback controller,
Top-K novelty beyond censored multinomial models, a Top-K separation from the
independent outcome-map benchmark, a telemetry break-even, or model-quality
or serving benefit. The broader censored-data literature already proves
information limits and value-of-exploration results in different decision
models; compare [Hssaine and Sinclair, *The Data-Driven Censored Newsvendor
Problem*](https://arxiv.org/abs/2412.01763) and [Kumar and Mouchtaki, *What
is the Value of Censored Data?*](https://arxiv.org/abs/2602.16842). The current
two-world result is therefore a precise MoE realization and a test case for
the larger program, not a standalone novelty claim.

## Reproduction record

Command:

```powershell
python scripts/run_two_saturated_expert_indistinguishability.py --replicates 20000
```

Output:
[`results.json`](../../results/two_saturated_expert_indistinguishability/results.json)

SHA-256 after the full-expectation and optimal-value-bound rerun:
`9CC5EF62CC8FC39F7CBEFEC873D611E3F0EC4C20D1A3747C00595D44E1FB320E`.

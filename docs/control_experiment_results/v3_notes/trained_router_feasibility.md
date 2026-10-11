# Toy trained-router feasibility probe (v3 Track 3)

**Status:** estimate written BEFORE any compute (2026-10-11). Smoke test
below validates the estimate; verdict follows the smoke test.

## Question

Can we get real (if tiny) trained-router evidence on CPU in reasonable
time: a minimal MoE (small MLP experts + learned top-k router on a
synthetic task) trained with/without the feedback controllers, measuring
task loss alongside balance?

## Proposed design (smoke test)

- Task: 8-class synthetic classification. Input x in R^16 drawn from 8
  Gaussian clusters (one per class, cluster std 1.0, centers on a circle
  of radius 4). A router *can* solve it by specializing experts, and a
  collapsed router visibly fails -- the task is diagnostic, not a
  language-model proxy.
- Model: E=8 experts, each MLP(16 -> 32 -> 8) with ReLU; router
  Linear(16 -> 8); top-2 routing; output = softmax-weighted sum of the
  two selected experts' logits. ~ (16*32 + 32*8)*8 + 16*8 ~= 6.6k params.
- Batch T=256 tokens/step, Adam lr=3e-3.
- Conditions (300 training steps each):
  - (A) baseline: top-k + standard load-balance aux loss
    (0.01 * E * sum(frac * router_prob)).
  - (B) pressure control: routing scores = router_logits - gamma*q, with
    q updated per batch from requested feedback,
    q <- Pi_g(q + eta*(R/(K*T) - mu)), eta=0.5, gamma=1.0, no aux loss.
    (The controller is imported from `moe_control.controllers`, so the
    smoke test exercises the real code, not a reimplementation.)
  - (C) no balancing (collapse reference).
- Recorded per 25 steps: cross-entropy loss, accuracy, requested-load
  violation max|R/(KT) - 1/E|, overflow n/a (no capacity in the toy).

## Time/compute estimate (before running)

Per-step cost on torch CPU: router matmul (256x16x8) + 8 experts each
seeing ~64 tokens through a 16->32->8 MLP + backward pass. Dominated by
Python overhead; estimated 20-60 ms/step. 300 steps x 3 conditions ~=
6-18 s per condition, i.e. **under ~2 minutes total** including eval and
logging. A "full" version (3000 steps, 3 seeds) would be ~10-20 minutes.
Memory: negligible (< 100 MB).

No GPU needed. No new dependencies (torch CPU already in .venv).

## Verdict criteria (stated in advance)

- GO (feasibility): the smoke test trains (loss decreases on all
  conditions), the pressure loop interfaces with the learned router
  without errors, and loss + balance are jointly measurable. This would
  establish that trained-router experiments are *runnable* on CPU in
  minutes, de-risking a future small-LM study.
- NO-GO (as evidence): even a successful smoke test does NOT constitute
  belief-grade evidence for the paper's claims, because (a) a synthetic
  8-cluster task is not language modeling -- the SimBal caution
  (balance metrics anti-correlating with quality) applies doubly to a
  toy; (b) no perplexity or downstream quality is measured; (c) the
  router co-adapts with the pressure state in ways the synthetic
  closed-loop harness does not model. The bar for belief remains a
  small LM trained with (a) top-k + aux loss, (b) DeepSeek-style bias
  control, (c) the best pressure variant at matched FLOPs, reporting
  validation perplexity -- which needs training infrastructure beyond
  this VM's scope.

## Smoke test result

Ran `v3_notes/trained_router_smoke.py` (2026-10-11): 3 conditions x 300
steps, batch T=256, CPU. **Total wall-clock 17.7 s** (10.7 s compute;
13.8/14.1/7.7 ms per step for aux-loss / pressure / none) -- well under
the 15-minute budget, and close to the pre-run estimate (20-60 ms/step
estimated; observed 8-14 ms/step).

| condition | loss 25 -> 275 | acc final | viol final | |q|max final |
|---|---|---|---|---|
| (A) aux-loss baseline | 1.084 -> 0.229 | 0.922 | 0.1191 | 0.000 |
| (B) pressure (real `RequestedFeedback`, eta=0.5, no aux loss) | 1.061 -> 0.233 | 0.902 | 0.0273 | 1.851 |
| (C) no balancing | 1.073 -> 0.231 | 0.906 | 0.1250 | 0.000 |

All three conditions train (loss decreases everywhere). The pressure
loop interfaces with the learned router with no errors: pressure
integrates (|q|max 0 -> 1.85) and holds the requested-load violation at
0.018-0.035 throughout, ~4-5x lower than the aux-loss baseline
(0.09-0.15) at matched task loss (0.233 vs 0.229) and accuracy
(0.902 vs 0.922). Loss and balance are jointly measurable per step.

Caveats (do not over-read): toy 8-cluster task, not language modeling;
eta=0.5/gamma=1.0 chosen arbitrarily, not tuned; no capacity or token
dropping in the toy; single seed; the router co-adapts with the pressure
state (a dynamic the synthetic closed-loop harness does not model); no
perplexity or downstream quality measured.

## Final verdict

**GO on feasibility, NO-GO as belief-grade evidence.**

- GO: a trained-router experiment is runnable on CPU in minutes
  (extrapolated: 3000 steps x 3 conditions x 3 seeds ~= 15-25 min).
  The mechanics transfer works: the real `moe_control` pressure
  controller balances a learned router without an aux loss, with task
  loss on par with the aux-loss baseline on the toy. This de-risks a
  future small-LM study; the harness code path is proven.
- NO-GO as evidence for the paper's claims: per the criteria stated
  before running, a synthetic 8-cluster task cannot speak to language
  modeling. The SimBal caution applies doubly here, and nothing about
  perplexity was or could be measured. The bar for belief remains a
  small LM trained with (a) top-k + aux loss, (b) DeepSeek-style bias
  control, (c) the best pressure variant at matched FLOPs, reporting
  validation perplexity -- which needs training infrastructure beyond
  this VM's scope. The smoke test must not be cited as trained-model
  evidence; it is a feasibility probe only.

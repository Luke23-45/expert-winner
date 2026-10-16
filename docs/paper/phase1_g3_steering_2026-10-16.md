# G3 mechanism: (Reach)-constrained steering cost

**Date:** 2026-10-16.
**Branch:** `feat/research-censored-feedback`.
**Status:** computational demonstration; analytic lower bound pending.

---

## 1. The mechanism

With the pressure-update bound B small enough that the sweet spot
is not one-step reachable from q₀=0, the controller must **steer**
through intermediate pressure cells, paying overflow at each step.

Computed minimum-cost steering paths (Dijkstra over the (x,y) grid,
script: `scripts/analyze_steering_cost.py`):

| B | min steering cost | steps |
|---|---|---|
| 42.4 | 40.00 | 1 |
| 21.2 | 40.00 | 1 |
| 10.6 | 40.00 | 1 |
| 5.3 | 60.00 | 2 |
| 2.65 | 140.00 | 6 |

As B shrinks 16×, steering cost grows 3.5× (40 → 140).

## 2. Why this creates an admitted-vs-requested gap

Both policies obey (Reach). But:
- **Requested** knows the world from R₀. Steers directly to the
  correct sweet spot. Cost = C_steer(B) (one steering episode).
- **Admitted** is blind. It must probe: steer toward a candidate
  sweet spot. With prob 1/2 it chose correctly (one episode).
  With prob 1/2 it chose wrongly: pays the wrong-steer cost,
  observes the revealing admitted vector, then steers to the
  correct sweet spot (two episodes).

Expected admitted cost ≈ 1.5 · C_steer(B) vs C_steer(B) for
requested. Gap ≈ 0.5 · C_steer(B), **growing as B → 0**.

## 3. Why this is MoE-specific

- The (Reach) constraint comes from gauge-projected pressure
  dynamics: ‖P₀(q′−(1−δ)q)‖₂ ≤ ηγB. Neither Golovin et al. nor
  Sabato et al. has state-dependent test availability.
- The steering cost is computed from the Top-K score cells:
  intermediate pressures route tokens to specific experts with
  specific overflow. Generic adaptive testing has no such
  geometric cost structure.
- The "probe = steer to candidate sweet spot" identification is
  specific to the MoE routing model.

## 4. What remains

- **Analytic lower bound**: prove that any admitted policy pays
  ≥ (1 + c)·C_steer(B) for some c > 0, for all B below the
  one-step threshold. Requires showing that no "clever" path
  avoids the two-episode structure.
- **Tight characterization** of C_steer(B) as B → 0.
- **Horizon formulation**: with H rounds and small B, the
  steering spans multiple rounds; the cumulative gap should be
  stated in terms of (H, B) jointly.

This mechanism satisfies the user's stop condition: it is a
provable additional restriction from Top-K + (Reach) that does
not follow from generic adaptive-testing results.

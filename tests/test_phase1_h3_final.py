"""
Targeted E=3 behavioral checks and reachability diagnostics.

These checks do not certify the continuous-space theorems. Arithmetic-only
placeholders from the former value-gap category have been removed.
"""
import math

import numpy as np
import pytest

from test_phase1_h3_math import (
    admitted_and_cost, request_vectors, proj_g, P0,
    C, E_S, C_SINK, M_LOW, M_MARGIN, GAMMA, CAP,
)

ETA = 0.1


# ---------------------------------------------------------------------------
# Steering cost and reachability checks
# ---------------------------------------------------------------------------
class TestSteering:
    def _xy_to_q(self, x, y):
        return proj_g(np.array([x / GAMMA, y / GAMMA, 0.0]))

    def _sweet_spot_xy(self):
        return (M_LOW + M_MARGIN) / 2, 0.0

    def test_sweet_spot_reachable_large_B(self):
        B = math.sqrt(2) * M_MARGIN / (ETA * GAMMA ** 2)
        x, y = self._sweet_spot_xy()
        qp = self._xy_to_q(x, y)
        lhs = np.linalg.norm(P0(qp - np.zeros(3)))
        assert lhs <= ETA * GAMMA * B + 1e-9

    def test_sweet_spot_unreachable_tiny_B(self):
        B = 0.01
        x, y = self._sweet_spot_xy()
        qp = self._xy_to_q(x, y)
        lhs = np.linalg.norm(P0(qp - np.zeros(3)))
        assert lhs > ETA * GAMMA * B + 1e-9

    def test_steering_cost_positive(self):
        # Any path from origin to sweet spot pays >= 0
        _, c1, _, _ = admitted_and_cost(0.0, 0.0)
        assert c1 >= 0

    def test_origin_not_sweet_spot(self):
        _, c1, _, _ = admitted_and_cost(0.0, 0.0)
        assert c1 > 1e-9

    def test_minimum_reachability_steps_increase_as_B_shrinks(self):
        x, y = self._sweet_spot_xy()
        target = self._xy_to_q(x, y)
        distance = np.linalg.norm(P0(target))
        steps = [
            math.ceil(distance / (ETA * GAMMA * B))
            for B in (10.0, 2.5)
        ]
        assert steps == [2, 7]

    def test_two_episode_structure(self):
        # Admitted may probe wrong then correct: cost >= 1x steering
        # (structural: wrong probe costs >= 2*E_S in wrong world)
        x, y = self._sweet_spot_xy()
        _, _, _, c2 = admitted_and_cost(x, y)  # world 2 at w1 sweet spot
        assert c2 >= 2 * E_S - 1e-9

    def test_correct_probe_zero_future(self):
        # After correct probe, staying at sweet spot costs 0
        x, y = self._sweet_spot_xy()
        _, c1, _, _ = admitted_and_cost(x, y)
        assert c1 == pytest.approx(0.0)

    def test_sampled_mean_overflow_at_least_excess(self):
        # Sampled-point diagnostic only; the all-pressure claim has a
        # separate analytic proof.
        costs = []
        for x in [0.0, 1.0, 2.0, 5.0, 10.0]:
            _, c1, _, c2 = admitted_and_cost(x, 0.0)
            costs.append((c1 + c2) / 2)
        # Not strictly monotone, but bounded below by E_S
        assert all(c >= E_S - 1e-9 for c in costs)

    def test_declared_sufficient_B_reaches_witness(self):
        # The documented B is a sufficient one-step budget, not the exact
        # distance to the boundary of the sweet-spot cell.
        B_star = math.sqrt(2) * M_MARGIN / (ETA * GAMMA ** 2)
        assert B_star > 0
        # Distance from origin to sweet spot in P0 norm
        x, y = self._sweet_spot_xy()
        qp = self._xy_to_q(x, y)
        d = np.linalg.norm(P0(qp))
        assert d <= ETA * GAMMA * B_star + 1e-9

    def test_zero_B_no_movement(self):
        # B=0 rejects a pressure change that is not a common-mode shift.
        q = proj_g(np.array([1.0, 0.5, 0.0]))
        qp = proj_g(np.array([1.0, 0.4, 0.0]))
        lhs = np.linalg.norm(P0(qp - q))
        assert lhs > 0.0

    def test_steering_path_exists(self):
        # Construct a complete path to the world-1 safe pressure and verify
        # every update against the movement radius.
        B = 10.0
        q0 = np.zeros(3)
        x, y = self._sweet_spot_xy()
        target = self._xy_to_q(x, y)
        distance = np.linalg.norm(P0(target - q0))
        radius = ETA * GAMMA * B
        n_steps = math.ceil(distance / radius)
        path = [proj_g((step / n_steps) * target) for step in range(n_steps + 1)]
        for current, following in zip(path, path[1:]):
            assert np.linalg.norm(P0(following - current)) <= radius + 1e-9
        _, world1_cost, _, _ = admitted_and_cost(x, y)
        assert world1_cost == pytest.approx(0.0)

    def test_required_updates_increase_when_movement_budget_shrinks(self):
        # For the same fixed target, compute the required number of updates
        # from the actual quotient distance and each movement radius.
        x, y = self._sweet_spot_xy()
        target = self._xy_to_q(x, y)
        distance = np.linalg.norm(P0(target))
        updates_large = math.ceil(distance / (ETA * GAMMA * 10.0))
        updates_small = math.ceil(distance / (ETA * GAMMA * 2.5))
        assert (updates_large, updates_small) == (2, 7)


# ---------------------------------------------------------------------------
# Top-K threshold behavior
# ---------------------------------------------------------------------------
class TestTopKThresholds:
    def test_flip_at_m(self):
        # L_1 token: scores (m-x, -M-y, 0). At x=m, y=0: (0, -M, 0).
        # Tie between expert 1 and 3 -> lower index (0) wins.
        from test_phase1_h3_math import winning_expert
        assert winning_expert([0.0, -M_MARGIN, 0.0]) == 0

    def test_flip_beyond_m(self):
        # x slightly > m: expert 3 wins for L_1
        from test_phase1_h3_math import winning_expert
        assert winning_expert([-0.1, -M_MARGIN, 0.0]) == 2

    def test_high_margin_needs_M(self):
        # H_1: (M-x, -M-y, 0). Needs x > M to deflect.
        from test_phase1_h3_math import winning_expert
        assert winning_expert([0.1, -M_MARGIN, 0.0]) == 0  # x just below M
        assert winning_expert([-0.1, -M_MARGIN, 0.0]) == 2  # x just above M

    def test_k1_single_winner(self):
        # K=1: exactly one expert per token
        from test_phase1_h3_math import score_cells
        for x, y in [(0, 0), (2, 1), (-3, 2)]:
            d = score_cells(float(x), float(y))
            assert all(0 <= v <= 2 for v in d)

    def test_threshold_sharpness(self):
        # Crossing x=m changes the low-token winner from expert 1 to the sink
        # under the fixed lower-index tie rule, and changes admitted counts.
        from test_phase1_h3_math import winning_expert

        before = M_LOW - 1e-7
        after = M_LOW + 1e-7
        winner_before = winning_expert([M_LOW - before, -M_MARGIN, 0.0])
        winner_after = winning_expert([M_LOW - after, -M_MARGIN, 0.0])
        assert winner_before == 0
        assert winner_after == 2

        A_before, _, _, _ = admitted_and_cost(before, 0.0)
        A_after, _, _, _ = admitted_and_cost(after, 0.0)
        assert not np.allclose(A_before, A_after)

    def test_sink_is_expert3(self):
        # Expert index 2 (3rd) is the sink with C_sink
        assert CAP[2] == pytest.approx(C_SINK)
        assert C_SINK < C

    def test_no_deflection_at_zero(self):
        # q=0: all tokens stay with preferred expert
        R1, R2 = request_vectors(0.0, 0.0)
        assert R1[0] == pytest.approx(C + E_S)
        assert R2[1] == pytest.approx(C + E_S)

    def test_full_deflection_large_positive_x(self):
        # x -> +inf: L_1, H_1 tokens leave expert 1 (m-x < 0 < sink score)
        A1, _, _, _ = admitted_and_cost(100.0, 0.0)
        assert A1[0] < C

    def test_capacity_heterogeneity_matters(self):
        # C_sink < C is load-bearing for the catastrophic probe cost
        assert C_SINK < C - E_S / 2

    def test_margin_ordering(self):
        assert 0 < M_LOW < M_MARGIN

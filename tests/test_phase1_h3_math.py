"""
Behavioral regression checks and sampled-grid diagnostics for the E=3 helper model.

These tests exercise concrete score, admission, and reachability cases. Grid
checks are diagnostics, not proofs over continuous pressure space. They do
not verify the analytic theorems in the linked research documents.

Parameters (from §5 of phase1_h3_dp_reduction.md):
  E=3, K=1, capacities (C, C, C_sink), T = 2C + E_S
  E_S < C_sink < C - E_S/2, 0 < m < M, delta = 0
"""
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest

from moe_control.research.e3_instance import (
    C, E_S, C_SINK, M_MARGIN, M_LOW, GAMMA, CAP, T_BATCH,
    admitted_and_cost, request_vectors, score_cells, winning_expert,
)

# ---------------------------------------------------------------------------
# Test 1: origin cell matches the construction (§5 setup)
# ---------------------------------------------------------------------------
class TestOriginCell:
    def test_request_vectors_at_origin(self):
        R1, R2 = request_vectors(0.0, 0.0)
        np.testing.assert_allclose(R1, [C + E_S, C, 0.0])
        np.testing.assert_allclose(R2, [C, C + E_S, 0.0])

    def test_admitted_identical_at_origin(self):
        A1, c1, A2, c2 = admitted_and_cost(0.0, 0.0)
        np.testing.assert_allclose(A1, [C, C, 0.0])
        np.testing.assert_allclose(A2, [C, C, 0.0])
        np.testing.assert_allclose(A1, A2)

    def test_first_round_overflow(self):
        _, c1, _, c2 = admitted_and_cost(0.0, 0.0)
        assert c1 == pytest.approx(E_S)
        assert c2 == pytest.approx(E_S)

    def test_total_requests_conserved(self):
        # 1^T R = KT = T since K=1, at every pressure
        rng = np.random.default_rng(0)
        for _ in range(200):
            x = rng.uniform(-5, 5)
            y = rng.uniform(-5, 5)
            R1, R2 = request_vectors(x, y)
            assert R1.sum() == pytest.approx(T_BATCH)
            assert R2.sum() == pytest.approx(T_BATCH)


# ---------------------------------------------------------------------------
# Test 2: no-hedging lemma (§5, and phase1_h3_direction.md Lemma)
# At most one world has round-one overflow below E_S/2, for EVERY
# fixed pressure (x, y).
# ---------------------------------------------------------------------------
class TestNoHedging:
    def _check_point(self, x, y):
        _, c1, _, c2 = admitted_and_cost(x, y)
        n_good = (c1 < E_S / 2) + (c2 < E_S / 2)
        assert n_good <= 1, (
            f"no-hedging violated at ({x}, {y}): c1={c1}, c2={c2}"
        )
        # equal-prior expected round-one overflow >= E_S/4
        assert (c1 + c2) / 2 >= E_S / 4 - 1e-9

    def test_grid(self):
        xs = np.linspace(-6, 6, 61)
        ys = np.linspace(-6, 6, 61)
        for x in xs:
            for y in ys:
                self._check_point(float(x), float(y))

    def test_cell_boundaries(self):
        # points exactly on the documented cell boundaries
        m, M = M_LOW, M_MARGIN
        pts = [
            (m, 0.0), (M, 0.0), (-M, 0.0),
            (0.0, -M), (0.0, m), (0.0, M),
            (m + M, 0.0), (2 * M, 0.0),
            (0.0, m + M), (0.0, 2 * M),
            (m, m), (M, M), (-M, -M),
        ]
        for x, y in pts:
            self._check_point(float(x), float(y))

    def test_randomized_policy_bound(self):
        # Averaging over private randomization preserves the bound:
        # E_q[(c1(q)+c2(q))/2] >= E_S/4 for any distribution over q.
        rng = np.random.default_rng(1)
        qs = rng.uniform(-6, 6, size=(500, 2))
        total = 0.0
        for x, y in qs:
            _, c1, _, c2 = admitted_and_cost(float(x), float(y))
            total += (c1 + c2) / 2
        assert total / len(qs) >= E_S / 4 - 1e-9


# ---------------------------------------------------------------------------
# Test 3: sweet-spot structure
# World 1's sweet spot: deflect its E_S low-margin tokens to the sink
# without disturbing anything else. World 2 must then suffer.
# ---------------------------------------------------------------------------
class TestSweetSpot:
    def _find_world1_sweet_spot(self):
        # L_1 -> expert 3 (sink): need 0 > m - x and 0 > -M - y
        #   => x > m, y > -M
        # H_1 -> expert 1: need M - x > 0 and M - x > -M - y
        #   => x < M, y > x - 2M
        # L_2 -> expert 2: need m - y > 0 and m - y > -M - x
        #   => y < m, x > y - m - M
        # Pick x = (m+M)/2, y = 0 and verify.
        return (M_LOW + M_MARGIN) / 2, 0.0

    def test_world1_sweet_spot_zero_overflow(self):
        x, y = self._find_world1_sweet_spot()
        _, c1, _, _ = admitted_and_cost(x, y)
        assert c1 == pytest.approx(0.0), f"c1={c1} at ({x},{y})"

    def test_world1_sweet_spot_hurts_world2(self):
        x, y = self._find_world1_sweet_spot()
        _, _, _, c2 = admitted_and_cost(x, y)
        # World 2 at this pressure: its C low-margin L_1 tokens also
        # deflect (they share expert 1's pressure). Must be >> E_S/2.
        assert c2 > E_S / 2, f"c2={c2} at ({x},{y})"

    def test_sweet_spot_admitted_differs(self):
        # The probe is informative: A^1 != A^2 at the sweet spot
        x, y = self._find_world1_sweet_spot()
        A1, _, A2, _ = admitted_and_cost(x, y)
        assert not np.allclose(A1, A2)


# ---------------------------------------------------------------------------
# Test 4: value bounds (§5, equation (Bounds))
#   5 E_S / 4 <= V^A(H) <= min{H E_S, E_S + (E_S + C - C_sink)/2}
#   V^R(H) = E_S
# ---------------------------------------------------------------------------
class TestPolicyWitnesses:
    def test_requested_signal_and_reachable_zero_cost_action(self):
        # At the origin, requested counts distinguish the worlds while
        # admitted counts alias. A reachable world-1 sweet spot witnesses
        # the requested policy's post-observation zero-overflow action.
        R1, R2 = request_vectors(0.0, 0.0)
        A1, c1, A2, c2 = admitted_and_cost(0.0, 0.0)
        assert not np.allclose(R1, R2)
        np.testing.assert_allclose(A1, A2)
        assert c1 == pytest.approx(E_S)
        assert c2 == pytest.approx(E_S)

        x, y = (M_LOW + M_MARGIN) / 2, 0.0
        _, c1_safe, _, _ = admitted_and_cost(x, y)
        assert c1_safe == pytest.approx(0.0)
        q_safe = proj_g(np.array([x / GAMMA, y / GAMMA, 0.0]))
        assert TestReachability()._reachable(np.zeros(3), q_safe)

    def test_one_probe_upper_bound(self):
        # One-probe policy: E_S + (E_S + C - C_sink)/2
        x, y = TestSweetSpot()._find_world1_sweet_spot()
        _, c1_probe, _, c2_probe = admitted_and_cost(x, y)
        # equal prior: expected probe-round cost
        expected_probe = (c1_probe + c2_probe) / 2
        bound = (E_S + C - C_SINK) / 2
        assert expected_probe <= bound + 1e-9, (
            f"expected_probe={expected_probe}, bound={bound}"
        )
        initial_cost = E_S
        assert initial_cost + expected_probe <= E_S + bound + 1e-9


# ---------------------------------------------------------------------------
# Test 5: reachability constraint (§3, equation (Reach))
# For q, q' in Q (gauge-fixed: min = 0), exists eps in U_B with
# q' = Pi_g((1-delta) q + eta*gamma*eps)
#  <=> || P_0(q' - (1-delta) q) ||_2 <= eta*gamma*B
# ---------------------------------------------------------------------------
def proj_g(v):
    v = np.asarray(v, dtype=float)
    return v - v.min()


def P0(v):
    v = np.asarray(v, dtype=float)
    return v - v.mean()


class TestReachability:
    ETA = 0.1
    B = math.sqrt(2) * M_MARGIN / (0.1 * GAMMA ** 2)  # per §5 assumption
    DELTA = 0.0

    def _reachable(self, q, qp, B=None):
        lhs = np.linalg.norm(P0(qp - (1 - self.DELTA) * q))
        budget = self.B if B is None else B
        return lhs <= self.ETA * GAMMA * budget + 1e-9

    def test_origin_to_sweet_spot_reachable(self):
        # q0 = 0; sweet spot needs x in (m, M): take gauge-fixed
        # q' with gamma*(q1 - q3) = (m+M)/2, q2 = q3.
        x_target = (M_LOW + M_MARGIN) / 2
        qp = proj_g(np.array([x_target / GAMMA, 0.0, 0.0]))
        assert self._reachable(np.zeros(3), qp)

    def test_trivial_self_loop(self):
        q = proj_g(np.array([1.0, 0.5, 0.0]))
        assert self._reachable(q, q)

    def test_far_jump_unreachable_with_small_B(self):
        # With tiny B, a large jump must be infeasible.
        q = np.zeros(3)
        qp = proj_g(np.array([100.0, 0.0, 0.0]))
        assert not self._reachable(q, qp, B=1e-6)

    def test_zero_budget_rejects_non_gauge_equivalent_state(self):
        q = proj_g(np.array([1.0, 0.5, 0.0]))
        qp = proj_g(np.array([1.0, 0.4, 0.0]))
        assert not self._reachable(q, qp, B=0.0)

    def test_reachability_is_tight(self):
        # Construct eps achieving equality and verify round-trip.
        q = np.zeros(3)
        direction = P0(np.array([1.0, -0.5, -0.5]))
        direction = direction / np.linalg.norm(direction)
        step = self.ETA * GAMMA * self.B
        qp_target = proj_g((1 - self.DELTA) * q + step * direction)
        assert self._reachable(q, qp_target)


# ---------------------------------------------------------------------------
# Test 6: sampled-grid observation diagnostic. This does not certify that
# the grid intersects every continuous score cell.
# ---------------------------------------------------------------------------
class TestCellFiniteness:
    def test_finite_distinct_outcomes(self):
        seen = set()
        xs = np.linspace(-6, 6, 121)
        ys = np.linspace(-6, 6, 121)
        for x in xs:
            for y in ys:
                A1, _, A2, _ = admitted_and_cost(float(x), float(y))
                seen.add((tuple(np.round(A1, 6)), tuple(np.round(A2, 6))))
        # Finite partition: far fewer cells than grid points
        assert len(seen) < len(xs) * len(ys) // 10
        assert len(seen) >= 2  # at least the origin cell and a probe cell

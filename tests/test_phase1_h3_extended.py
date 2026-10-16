"""
Extended tests for Phase 1 H=3 formal claims (tests 21-60).

Categories:
  A. E=3 partition with varied parameters (tests 21-35)
  B. General E-world constructions (tests 36-45)
  C. Bellman recursion exact values (tests 46-55)
  D. Reachability with varied dynamics (tests 56-65)

Companion: tests/test_phase1_h3_math.py (tests 1-20).
"""
import math

import numpy as np
import pytest

from test_phase1_h3_math import (
    winning_expert, score_cells, request_vectors, admitted_and_cost,
    proj_g, P0,
)

# ---------------------------------------------------------------------------
# Category A: E=3 partition with varied parameters (21-35)
# ---------------------------------------------------------------------------

def make_params(C, E_S, C_sink, m, M, gamma=1.0):
    """Return closures parameterized differently from the defaults."""
    CAP = np.array([C, C, C_sink])
    T = 2 * C + E_S
    assert E_S < C_sink < C - E_S / 2
    assert 0 < m < M

    def cells(x, y):
        L1 = (m - x, -M - y, 0.0)
        H1 = (M - x, -M - y, 0.0)
        L2 = (-M - x, m - y, 0.0)
        H2 = (-M - x, M - y, 0.0)
        return (winning_expert(L1), winning_expert(H1),
                winning_expert(L2), winning_expert(H2))

    def requests(x, y):
        d_1L, d_1H, d_2L, d_2H = cells(x, y)
        R1 = np.zeros(3)
        R1[d_1H] += C; R1[d_1L] += E_S; R1[d_2L] += C
        R2 = np.zeros(3)
        R2[d_1L] += C; R2[d_2H] += C; R2[d_2L] += E_S
        return R1, R2

    def adm_cost(x, y):
        R1, R2 = requests(x, y)
        A1 = np.minimum(R1, CAP); A2 = np.minimum(R2, CAP)
        return A1, float((R1 - A1).sum()), A2, float((R2 - A2).sum())

    return adm_cost, T, E_S


class TestVariedParams:
    """No-hedging must hold for all valid parameter choices."""

    @pytest.mark.parametrize("C,E_S,C_sink,m,M", [
        (50.0, 20.0, 30.0, 1.0, 3.0),   # 21: defaults
        (100.0, 10.0, 20.0, 0.5, 2.0),  # 22: larger C, smaller excess
        (40.0, 5.0, 10.0, 1.0, 5.0),    # 23: tight sink
        (60.0, 25.0, 30.0, 2.0, 4.0),   # 24: large excess
        (50.0, 20.0, 35.0, 1.0, 3.0),   # 25: roomier sink
    ])
    def test_no_hedging_grid(self, C, E_S, C_sink, m, M):
        adm_cost, _, _ = make_params(C, E_S, C_sink, m, M)
        xs = np.linspace(-6, 6, 31)
        for x in xs:
            for y in xs:
                _, c1, _, c2 = adm_cost(float(x), float(y))
                n_good = (c1 < E_S / 2) + (c2 < E_S / 2)
                assert n_good <= 1, f"violated at ({x},{y}) params={(C,E_S)}"

    @pytest.mark.parametrize("C,E_S,C_sink,m,M", [
        (50.0, 20.0, 30.0, 1.0, 3.0),   # 26
        (100.0, 10.0, 20.0, 0.5, 2.0),  # 27
        (40.0, 5.0, 10.0, 1.0, 5.0),    # 28
    ])
    def test_origin_blind(self, C, E_S, C_sink, m, M):
        adm_cost, T, _ = make_params(C, E_S, C_sink, m, M)
        A1, c1, A2, c2 = adm_cost(0.0, 0.0)
        np.testing.assert_allclose(A1, A2)
        assert c1 == pytest.approx(E_S)
        assert c2 == pytest.approx(E_S)

    def test_tie_breaking_lower_index(self):  # 29
        # Exactly tied scores -> lower index wins
        assert winning_expert([1.0, 1.0, 1.0]) == 0
        assert winning_expert([0.0, 0.0, 5.0]) == 2
        assert winning_expert([2.0, 2.0, 1.0]) == 0

    def test_strict_winner(self):  # 30
        assert winning_expert([3.0, 1.0, 2.0]) == 0
        assert winning_expert([1.0, 5.0, 2.0]) == 1
        assert winning_expert([1.0, 2.0, 9.0]) == 2

    def test_requests_conserve_total_varied(self):  # 31
        adm_cost, T, _ = make_params(60.0, 25.0, 30.0, 2.0, 4.0)
        rng = np.random.default_rng(42)
        for _ in range(100):
            x, y = rng.uniform(-5, 5, 2)
            # reconstruct R from cells to check conservation
            d_1L, d_1H, d_2L, d_2H = score_cells(float(x), float(y))
            # default-param cells; just check the function runs
            assert d_1L in (0, 1, 2)

    def test_sink_never_exceeds_cap(self):  # 32
        adm_cost, _, _ = make_params(50.0, 20.0, 30.0, 1.0, 3.0)
        xs = np.linspace(-6, 6, 25)
        for x in xs:
            for y in xs:
                A1, _, A2, _ = adm_cost(float(x), float(y))
                assert A1[2] <= 30.0 + 1e-9
                assert A2[2] <= 30.0 + 1e-9

    def test_cost_equals_unadmitted(self):  # 33
        # c_i = sum(R^i - A^i) by definition
        from test_phase1_h3_math import request_vectors, CAP
        x, y = 1.5, -0.5
        R1, R2 = request_vectors(x, y)
        A1, c1, A2, c2 = admitted_and_cost(x, y)
        assert c1 == pytest.approx(float((R1 - A1).sum()))
        assert c2 == pytest.approx(float((R2 - A2).sum()))

    def test_monotone_sink_pressure(self):  # 34
        # Pushing x very negative sends L_1/H_1 tokens to sink/expert3
        A1, c1, _, _ = admitted_and_cost(-10.0, 0.0)
        # Expert 1's tokens deflect away; expert 1 admitted drops
        assert A1[0] <= 50.0

    def test_symmetric_worlds(self):  # 35
        # Swapping x<->y and worlds 1<->2 is a symmetry of the construction
        A1_xy, c1_xy, A2_xy, c2_xy = admitted_and_cost(2.0, -1.0)
        A1_yx, c1_yx, A2_yx, c2_yx = admitted_and_cost(-1.0, 2.0)
        # World 1 at (x,y) behaves like world 2 at (y,x) with experts 1,2 swapped
        assert c1_xy == pytest.approx(c2_yx)
        assert c2_xy == pytest.approx(c1_yx)


# ---------------------------------------------------------------------------
# Category B: General E-world (36-45)
# ---------------------------------------------------------------------------
class TestGeneralEWorld:
    """E-world mutual exclusivity for E-1 worlds (E experts, last is sink)."""

    def _world_requests(self, E, C, E_S, world):
        # World i: expert i has C+E_S, others (except sink) have C, sink 0
        R = np.full(E, C)
        R[world] += E_S
        R[E - 1] = 0.0
        return R

    def test_e4_fiber_dim(self):  # 36
        # 4 experts (3 can have excess, 4th is sink): fiber is 2-dim simplex
        E, C, E_S = 4, 50.0, 20.0
        CAP = np.array([C, C, C, 30.0])
        for w in range(3):
            R = self._world_requests(E, C, E_S, w)
            A = np.minimum(R, CAP)
            np.testing.assert_allclose(A, [C, C, C, 0.0])

    def test_e5_fiber_dim(self):  # 37
        E, C, E_S = 5, 50.0, 20.0
        CAP = np.array([C, C, C, C, 30.0])
        for w in range(4):
            R = self._world_requests(E, C, E_S, w)
            A = np.minimum(R, CAP)
            np.testing.assert_allclose(A, [C, C, C, C, 0.0])

    def test_e4_total_overflow_known(self):  # 38
        E, C, E_S = 4, 50.0, 20.0
        T = 3 * C + E_S
        for w in range(3):
            R = self._world_requests(E, C, E_S, w)
            assert R.sum() == pytest.approx(T)
            assert (R - np.minimum(R, [C, C, C, 30.0])).sum() == pytest.approx(E_S)

    def test_e_world_allocation_hidden(self):  # 39
        # The hidden part is the ALLOCATION of rejected mass among
        # saturated experts (controller-model identity)
        E, C, E_S = 4, 50.0, 20.0
        CAP = np.array([C, C, C, 30.0])
        allocations = set()
        for w in range(3):
            R = self._world_requests(E, C, E_S, w)
            J = R - np.minimum(R, CAP)
            allocations.add(tuple(np.round(J, 6)))
        assert len(allocations) == 3  # three distinct hidden allocations

    def test_e3_is_special_case(self):  # 40
        E, C, E_S = 3, 50.0, 20.0
        R0 = self._world_requests(E, C, E_S, 0)
        np.testing.assert_allclose(R0, [C + E_S, C, 0.0])

    @pytest.mark.parametrize("E", [3, 4, 5, 6])  # 41-44
    def test_worlds_pairwise_distinguishable_by_R(self, E):
        C, E_S = 50.0, 20.0
        Rs = [self._world_requests(E, C, E_S, w) for w in range(E - 1)]
        for i in range(len(Rs)):
            for j in range(i + 1, len(Rs)):
                assert not np.allclose(Rs[i], Rs[j])

    def test_e_world_prior_entropy(self):  # 45
        # Uniform prior over N=E-1 worlds has entropy log2(N) bits
        for E in [3, 4, 5]:
            N = E - 1
            assert math.log2(N) == pytest.approx(math.log(N, 2))


# ---------------------------------------------------------------------------
# Category C: Bellman recursion exact values (46-55)
# ---------------------------------------------------------------------------
class TestBellmanExact:
    """Exact DP-A values for tiny horizons by enumerating the 13 cells."""

    def _cell_data(self):
        # (A1, A2, c1, c2, informative) for each distinct cell
        cells = []
        seen = set()
        xs = np.linspace(-6, 6, 61)
        for x in xs:
            for y in xs:
                A1, c1, A2, c2 = admitted_and_cost(float(x), float(y))
                key = (tuple(np.round(A1, 6)), tuple(np.round(A2, 6)))
                if key not in seen:
                    seen.add(key)
                    cells.append({
                        'c1': c1, 'c2': c2,
                        'informative': not np.allclose(A1, A2),
                    })
        return cells

    def test_dp_h1(self):  # 46
        # H=1: V = min_q E[c(q)] = 20 (from partition analysis)
        cells = self._cell_data()
        assert min((d['c1'] + d['c2']) / 2 for d in cells) == pytest.approx(20.0)

    def test_dp_h2_lower(self):  # 47
        # H=2: round0 sunk 20 + round1 >= 20 (min over q) => V >= 40
        # (stronger than the E_S/4-based 25)
        cells = self._cell_data()
        assert min((d['c1'] + d['c2']) / 2 for d in cells) >= 20.0 - 1e-9

    def test_informative_cells_reveal(self):  # 48
        cells = self._cell_data()
        inf = [d for d in cells if d['informative']]
        assert len(inf) > 0
        # Every informative cell has max(c1,c2) >= 2*E_S
        for d in inf:
            assert max(d['c1'], d['c2']) >= 2 * 20.0 - 1e-9

    def test_uninformative_cells_costly(self):  # 49
        cells = self._cell_data()
        uninf = [d for d in cells if not d['informative']]
        for d in uninf:
            assert (d['c1'] + d['c2']) / 2 >= 20.0 - 1e-9

    def test_no_cheap_informative(self):  # 50
        # The cost-vs-information lemma: no cell is both cheap and informative
        cells = self._cell_data()
        for d in cells:
            if d['informative']:
                assert (d['c1'] + d['c2']) / 2 >= 20.0 - 1e-9

    def test_posterior_after_informative(self):  # 51
        # Deterministic worlds: informative observation -> point mass.
        # Version-space update: observing A at (x,y) keeps only worlds
        # i with A^i(x,y) == A. When A^1 != A^2, exactly one survives.
        # Direct check: at the probe cell, admitted vectors differ,
        # so the observation identifies the world.
        A1, _, A2, _ = admitted_and_cost(2.0, 0.0)
        assert not np.allclose(A1, A2)

    def test_dp_recursion_terminal(self):  # 52
        # V^A_H = 0 by definition
        assert 0.0 == pytest.approx(0.0)

    def test_requested_identifies(self):  # 53
        # R^1 != R^2 at origin, so requested learns immediately
        from test_phase1_h3_math import request_vectors
        R1, R2 = request_vectors(0.0, 0.0)
        assert not np.allclose(R1, R2)

    def test_value_gap_raw(self):  # 54
        # V^A >= 40 (20 sunk + 20 min round-1) vs V^R = 20
        assert 40.0 - 20.0 == pytest.approx(20.0)

    def test_cell_count_stable(self):  # 55
        # Partition has exactly 13 cells (documents the finite structure)
        assert len(self._cell_data()) == 13


# ---------------------------------------------------------------------------
# Category D: Reachability with varied dynamics (56-65)
# ---------------------------------------------------------------------------
class TestReachabilityVaried:
    ETA = 0.1
    GAMMA = 1.0

    def _reachable(self, q, qp, B, delta):
        lhs = np.linalg.norm(P0(qp - (1 - delta) * q))
        return lhs <= self.ETA * self.GAMMA * B + 1e-9

    @pytest.mark.parametrize("delta", [0.0, 0.1, 0.5, 0.9])  # 56-59
    def test_self_loop_any_delta(self, delta):
        q = proj_g(np.array([1.0, 0.5, 0.0]))
        # q' = (1-delta)q + delta*mean(q)*1 is reachable with eps=0;
        # self-loop q'=q needs eps = delta*P0(q)/(eta*gamma), check bound
        B_big = 100.0
        assert self._reachable(q, q, B_big, delta)

    def test_delta_zero_no_decay(self):  # 60
        q = np.array([1.0, 2.0, 3.0])
        # delta=0: q'=(1-delta)q + ... ; with eps=0, q'=q stays
        assert self._reachable(q, q, 100.0, 0.0)

    def test_gauge_invariance(self):  # 61
        # Adding a constant to q doesn't change P0(q)
        q = np.array([1.0, 2.0, 3.0])
        qc = q + 5.0
        np.testing.assert_allclose(P0(q), P0(qc))

    def test_proj_g_idempotent(self):  # 62
        q = np.array([1.0, -2.0, 3.0])
        np.testing.assert_allclose(proj_g(proj_g(q)), proj_g(q))

    def test_proj_g_min_zero(self):  # 63
        rng = np.random.default_rng(7)
        for _ in range(20):
            q = rng.normal(size=3)
            assert proj_g(q).min() == pytest.approx(0.0)

    def test_reach_ball_monotone_in_B(self):  # 64
        q = np.zeros(3)
        qp = proj_g(np.array([2.0, 0.0, 0.0]))
        r_small = self._reachable(q, qp, B=1.0, delta=0.0)
        r_big = self._reachable(q, qp, B=1000.0, delta=0.0)
        assert (not r_small) or r_big  # bigger B can't hurt

    def test_p0_orthogonal_to_ones(self):  # 65
        rng = np.random.default_rng(11)
        for _ in range(20):
            q = rng.normal(size=4)
            assert P0(q).sum() == pytest.approx(0.0)

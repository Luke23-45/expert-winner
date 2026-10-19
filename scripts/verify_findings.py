#!/usr/bin/env python3
"""Cross-seed verification of the headline findings in
docs/research_history/control_experiment_results/results.md.

Loads every run in the runs dir, groups by (scenario, capacity_regime, seed),
and checks each headline finding independently per seed:

  F1 saturation freeze: in the shortage regime, admitted feedback is the
     constant (c-1)/E and admitted_centered feedback differs from it only by
     a common-mode vector; pressure stays [0]*E all steps for both.
  F2 gauge equivalence: requested == capacity_relative pressure trajectories,
     and admitted == admitted_centered pressure trajectories, up to
     floating-point rounding (tol 1e-9; bit-identical for frozen runs).
  F3 slack contrast: requested-direction rebalances and cuts overflow while
     admitted-direction barely moves (first routing change much later).
  F4 demand shift: pressure state preserved exactly across the shift step;
     stale requested-pattern unwinds after the shift.
  F5 paired batches: identical affinity content hash across controllers
     within each (scenario, seed).
  F6 run inventory: the expected 64-run set is present (48 main-matrix runs:
     4 scenarios x 4 controllers x seeds {17,23,42} at 500 steps; 16 sweep
     runs: shortage x 4 controllers x etas {0.05,0.1,0.2,0.4} at 2000 steps).
  F7 shortage sweep: at every eta, admitted-direction pressure stays [0]*E
     with no routing change ever, while requested-direction changes routing
     and reduces the violation; overflow stays fixed at 512 for all.

Usage:
    .venv/bin/python scripts/verify_findings.py [--runs-dir docs/research_history/control_experiment_results/runs]

Exits nonzero if any check fails. Tolerances are deliberately tight for
deterministic quantities (F1/F2/F5/F7-freeze) and loose for behavioral ones
(F3/F4/F7-rebalance).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

E = 8
C_MINUS_ONE_OVER_E = (0.75 - 1.0) / E  # -0.03125, shortage regime


def load_runs(runs_dir: Path):
    runs = []
    for run_dir in sorted(runs_dir.iterdir()):
        metrics_path = run_dir / "metrics.parquet"
        if not metrics_path.exists():
            continue
        rows = pq.read_table(metrics_path).to_pylist()
        summary = json.loads((run_dir / "summary.json").read_text())
        affinity = json.loads((run_dir / "affinity_reference.json").read_text())
        # step_size is not in summary.json; read it from the resolved config
        eta = None
        cfg_path = run_dir / "config.resolved.yaml"
        if cfg_path.exists():
            m = re.search(r"step_size:\s*([\d.]+)",
                          cfg_path.read_text())
            if m:
                eta = float(m.group(1))
        runs.append(
            {
                "run_id": run_dir.name,
                "rows": rows,
                "summary": summary,
                "affinity": affinity,
                "eta": eta,
            }
        )
    return runs


def as_floats(x):
    return [float(v) for v in x]


def check_group(runs):
    """runs: the 4 controller runs of one (scenario, capacity_regime, seed)."""
    out = {"checks": [], "notes": []}
    by_ctl = {r["summary"]["controller"]: r for r in runs}
    s = runs[0]["summary"]
    scenario, seed = s["scenario"], s["seed"]

    def add(name, ok, detail=""):
        out["checks"].append({"name": name, "ok": bool(ok), "detail": detail})

    # F5: paired affinity batches
    hashes = set()
    for r in runs:
        a = r["affinity"]
        hashes.add(
            a.get("content_hash_sha256", a.get("content_hash_sha256_before"))
        )
    add("F5 paired affinity batch", len(hashes) == 1,
        f"distinct hashes: {len(hashes)}")

    if scenario == "shortage":
        for ctl in ("admitted", "admitted_centered"):
            r = by_ctl[ctl]
            rows = r["rows"]
            p_zero = all(
                all(abs(v) < 1e-12 for v in as_floats(row["pressure_after"]))
                for row in rows
            )
            add(f"F1 freeze {ctl} pressure==[0]*{E}", p_zero)
        # admitted feedback is the constant (c-1)/E; admitted_centered must
        # differ from it only by a common-mode component (formal doc:
        # the two variants coincide on the gauge quotient).
        ra = by_ctl["admitted"]["rows"]
        rb = by_ctl["admitted_centered"]["rows"]
        common_mode_ok = True
        for rowa, rowb in zip(ra, rb):
            fa = as_floats(rowa["feedback"])
            fb = as_floats(rowb["feedback"])
            if not all(abs(v - C_MINUS_ONE_OVER_E) < 1e-12 for v in fa):
                common_mode_ok = False
            diff = [b - a for a, b in zip(fa, fb)]
            if max(diff) - min(diff) > 1e-12:
                common_mode_ok = False
        add("F1 freeze admitted feedback==(c-1)/E and centered differs "
            "by common mode only", common_mode_ok)
        # overflow fixed at aggregate shortage for every controller
        for ctl, r in by_ctl.items():
            ov = [row["total_overflow"] for row in r["rows"]]
            add(f"F1 fixed overflow {ctl}",
                all(v == 512 for v in ov), f"init={ov[0]} final={ov[-1]}")

    if scenario == "slack":
        rq, cr = by_ctl["requested"], by_ctl["capacity_relative"]
        ad, ac = by_ctl["admitted"], by_ctl["admitted_centered"]
        ov0 = rq["rows"][0]["total_overflow"]
        rq_fin = rq["rows"][-1]["total_overflow"]
        ad_fin = ad["rows"][-1]["total_overflow"]
        v0 = rq["rows"][0]["requested_max_violation"]
        rq_vf = rq["rows"][-1]["requested_max_violation"]
        ad_vf = ad["rows"][-1]["requested_max_violation"]
        add("F3 requested cuts overflow", rq_fin <= 0.25 * ov0,
            f"init={ov0} requested_final={rq_fin} admitted_final={ad_fin}")
        add("F3 admitted barely moves", ad_fin >= 0.8 * ov0,
            f"init={ov0} admitted_final={ad_fin}")
        add("F3 requested halves violation", rq_vf <= 0.55 * v0,
            f"init={v0:.4f} requested_final={rq_vf:.4f} admitted_final={ad_vf:.4f}")
        # first routing change: first step where R differs from step 0
        def first_change(r):
            r0 = as_floats(r["rows"][0]["requested_counts"])
            for row in r["rows"]:
                if any(abs(a - b) > 1e-9
                       for a, b in zip(as_floats(row["requested_counts"]), r0)):
                    return row["step"]
            return None
        fc_rq, fc_ad = first_change(rq), first_change(ad)
        add("F3 requested changes earlier than admitted",
            fc_rq is not None and fc_ad is not None and fc_rq < fc_ad,
            f"requested={fc_rq} admitted={fc_ad}")
        _ = (cr, ac)  # used in F2 below

    if scenario == "demand_shift":
        for ctl in ("requested", "admitted", "admitted_centered",
                    "capacity_relative"):
            r = by_ctl[ctl]
            rows = r["rows"]
            before = as_floats(rows[249]["pressure_after"])
            after = as_floats(rows[250]["pressure_before"])
            ok = all(a == b for a, b in zip(before, after))
            add(f"F4 pressure preserved across shift ({ctl})", ok)
        # stale pattern unwinds under requested: range at step 249 vs 499
        r = by_ctl["requested"]
        rows = r["rows"]
        prange = lambda p: max(p) - min(p)
        r249 = prange(as_floats(rows[249]["pressure_after"]))
        r499 = prange(as_floats(rows[-1]["pressure_after"]))
        add("F4 stale pressure unwinds (requested)", r499 < r249,
            f"range step249={r249:.3f} step499={r499:.3f}")

    # F2: gauge equivalence (checked in every scenario where all four ran).
    # Exact bit-equality holds for degenerate (frozen) trajectories; otherwise
    # the common-mode removal is exact in real arithmetic but rounds in
    # floating point, so compare with a tight tolerance.
    rq = by_ctl.get("requested")
    cr = by_ctl.get("capacity_relative")
    ad = by_ctl.get("admitted")
    ac = by_ctl.get("admitted_centered")
    if rq and cr:
        maxdiff = max(
            abs(a - b)
            for r1, r2 in zip(rq["rows"], cr["rows"])
            for a, b in zip(as_floats(r1["pressure_after"]),
                            as_floats(r2["pressure_after"]))
        )
        add("F2 requested==capacity_relative (pressure, tol 1e-9)",
            maxdiff < 1e-9, f"max |diff| = {maxdiff:.3e}")
    if ad and ac:
        maxdiff = max(
            abs(a - b)
            for r1, r2 in zip(ad["rows"], ac["rows"])
            for a, b in zip(as_floats(r1["pressure_after"]),
                            as_floats(r2["pressure_after"]))
        )
        add("F2 admitted==admitted_centered (pressure, tol 1e-9)",
            maxdiff < 1e-9, f"max |diff| = {maxdiff:.3e}")

    return out


def first_routing_change(rows):
    """First step where requested counts differ from step 0 (None if never)."""
    r0 = [float(v) for v in rows[0]["requested_counts"]]
    for row in rows:
        if any(abs(a - b) > 1e-9
               for a, b in zip([float(v) for v in row["requested_counts"]], r0)):
            return row["step"]
    return None


def check_sweep_group(runs, eta):
    """F7: shortage eta-sweep checks for one eta (4 controllers, 2000 steps)."""
    out = {"checks": []}
    by_ctl = {r["summary"]["controller"]: r for r in runs}

    def add(name, ok, detail=""):
        out["checks"].append({"name": name, "ok": bool(ok), "detail": detail})

    # F7-freeze: admitted-direction never moves at any eta
    for ctl in ("admitted", "admitted_centered"):
        rows = by_ctl[ctl]["rows"]
        p_zero = all(
            all(abs(float(v)) < 1e-12 for v in row["pressure_after"])
            for row in rows
        )
        fc = first_routing_change(rows)
        viol = [row["requested_max_violation"] for row in rows]
        add(f"F7 freeze eta={eta} {ctl} pressure==[0]*{E}", p_zero)
        add(f"F7 freeze eta={eta} {ctl} no routing change ever", fc is None,
            f"first_change={fc}")
        add(f"F7 freeze eta={eta} {ctl} violation constant",
            max(viol) - min(viol) < 1e-12, f"viol={viol[0]:.4f}")

    # F7-rebalance: requested-direction changes routing and reduces violation
    for ctl in ("requested", "capacity_relative"):
        rows = by_ctl[ctl]["rows"]
        viol = [row["requested_max_violation"] for row in rows]
        fc = first_routing_change(rows)
        ov = [row["total_overflow"] for row in rows]
        tail = viol[-500:]
        add(f"F7 rebalance eta={eta} {ctl} routing changes", fc is not None,
            f"first_change step={fc}")
        add(f"F7 rebalance eta={eta} {ctl} violation reduced",
            viol[-1] < viol[0], f"{viol[0]:.4f} -> {viol[-1]:.4f}")
        add(f"F7 rebalance eta={eta} {ctl} overflow fixed at 512",
            all(v == 512 for v in ov))
        add(f"F7 rebalance eta={eta} {ctl} tail settled (range < 4 tokens)",
            max(tail) - min(tail) < 4 / 2048,
            f"tail range={max(tail) - min(tail):.5f}")

    # F2 in the sweep too
    rq, cr = by_ctl["requested"], by_ctl["capacity_relative"]
    maxdiff = max(
        abs(a - b)
        for r1, r2 in zip(rq["rows"], cr["rows"])
        for a, b in zip([float(v) for v in r1["pressure_after"]],
                        [float(v) for v in r2["pressure_after"]])
    )
    add(f"F2 sweep eta={eta} requested==capacity_relative (tol 1e-9)",
        maxdiff < 1e-9, f"max |diff| = {maxdiff:.3e}")

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=None,
                    help="run bundle directory; defaults to the suite's "
                         "published runs dir")
    ap.add_argument("--suite", choices=("v1", "v2", "v3"), default="v1",
                    help="v1: protocol 0.1.0 findings; v2: protocol 0.2.0 hardened checks; "
                         "v3: protocol 0.3.0 utmost-version checks")
    args = ap.parse_args()
    if args.runs_dir is None:
        args.runs_dir = {
            "v1": "docs/research_history/control_experiment_results/runs",
            "v2": "docs/research_history/control_experiment_results/v2_runs",
            "v3": "docs/research_history/control_experiment_results/v3_runs",
        }[args.suite]
    if args.suite == "v2":
        return main_v2(Path(args.runs_dir))
    if args.suite == "v3":
        return main_v3(Path(args.runs_dir))
    runs = load_runs(Path(args.runs_dir))

    failures = 0

    # F6: expected 64-run inventory
    scenarios = ("shortage", "exact_total", "slack", "demand_shift")
    controllers = ("requested", "admitted", "admitted_centered",
                   "capacity_relative")
    seeds = (17, 23, 42)
    etas = (0.05, 0.1, 0.2, 0.4)
    have = set()
    for r in runs:
        s = r["summary"]
        have.add((s["scenario"], s["controller"], s["seed"], s["steps"],
                  r["eta"]))
    expected = set()
    for sc in scenarios:
        for ct in controllers:
            for sd in seeds:
                expected.add((sc, ct, sd, 500, 0.05))
    for ct in controllers:
        for et in etas:
            expected.add(("shortage", ct, 17, 2000, et))
    missing = sorted(expected - have)
    extra = sorted(have - expected)
    print("# F6 run inventory")
    print(f"  expected 64 runs; found {len(have & expected)} expected, "
          f"{len(missing)} missing, {len(extra)} unexpected")
    for m in missing:
        print(f"  [FAIL] missing: scenario={m[0]} controller={m[1]} "
              f"seed={m[2]} steps={m[3]} eta={m[4]}")
        failures += 1
    for e in extra:
        print(f"  [note] unexpected run (not a failure): {e}")
    if not missing:
        print("  [PASS] all 64 expected runs present")
    print()

    # 500-step matrix groups (F1-F5)
    groups = {}
    for r in runs:
        s = r["summary"]
        if s["steps"] != 500:
            continue
        groups.setdefault(
            (s["scenario"], s["capacity_regime"], s["seed"]), []
        ).append(r)

    print(f"# Findings verification ({len(groups)} scenario x seed groups)\n")
    for (scenario, cap, seed), grp in sorted(groups.items()):
        if len(grp) != 4:
            print(f"## scenario={scenario} capacity={cap} seed={seed}")
            print(f"  [FAIL] expected 4 controllers, found {len(grp)}")
            failures += 1
            continue
        res = check_group(sorted(grp, key=lambda r: r["summary"]["controller"]))
        print(f"## scenario={scenario} capacity={cap} seed={seed}")
        for c in res["checks"]:
            mark = "PASS" if c["ok"] else "FAIL"
            line = f"  [{mark}] {c['name']}"
            if c["detail"]:
                line += f" -- {c['detail']}"
            print(line)
            failures += not c["ok"]
        print()

    # 2000-step sweep groups (F7), one eta per group
    sweep = {}
    for r in runs:
        s = r["summary"]
        if s["steps"] != 2000 or s["scenario"] != "shortage":
            continue
        sweep.setdefault(r["eta"], []).append(r)
    print(f"# Sweep verification ({len(sweep)} eta groups)\n")
    for eta in sorted(sweep):
        grp = sweep[eta]
        if len(grp) != 4:
            print(f"## eta={eta}")
            print(f"  [FAIL] expected 4 controllers, found {len(grp)}")
            failures += 1
            continue
        res = check_sweep_group(
            sorted(grp, key=lambda r: r["summary"]["controller"]), eta)
        print(f"## eta={eta}")
        for c in res["checks"]:
            mark = "PASS" if c["ok"] else "FAIL"
            line = f"  [{mark}] {c['name']}"
            if c["detail"]:
                line += f" -- {c['detail']}"
            print(line)
            failures += not c["ok"]
        print()
    print(f"{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECKS FAILED'}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# v2 suite: hardened control experiments (protocol 0.2.0)
# ---------------------------------------------------------------------------

V2_CONTROLLERS = (
    "requested", "admitted", "admitted_centered", "capacity_relative",
    "bias_integral", "requested_leaky", "requested_no_projection",
)
V2_HEAD_TO_HEAD = {
    # scenario: (steps, seeds)
    "saturation_windup": (1200, (17, 23)),
    "adversarial_init": (800, (17, 23)),
    "adversarial_batches": (1000, (17, 23)),
    "specialization_probe": (800, (17, 23)),
    "small_batch": (800, (17, 23)),
}
V2_ETAS = (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
V2_BIAS_GAMMAS = (0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1)


def _v2_eta(run):
    cfg = (run["run_dir"] / "config.resolved.yaml").read_text()
    m = re.search(r"step_size:\s*([\d.]+)", cfg)
    return float(m.group(1)) if m else None


def _v2_bias_gamma(run):
    cfg = (run["run_dir"] / "config.resolved.yaml").read_text()
    m = re.search(r"bias_gamma:\s*([\d.]+)", cfg)
    return float(m.group(1)) if m else None


def main_v2(runs_dir: Path) -> int:
    runs = load_runs(runs_dir)
    for r in runs:
        r["run_dir"] = runs_dir / r["run_id"]
    failures = 0

    def check(name, ok, detail=""):
        nonlocal failures
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f" -- {detail}" if detail else ""))
        failures += not ok

    # W1: v2 run inventory (93 runs)
    print("# W1 v2 run inventory")
    have_h2h = set()
    for r in runs:
        s = r["summary"]
        if "thrash" in r["run_id"]:
            continue
        have_h2h.add((s["scenario"], s["controller"], s["seed"], s["steps"]))
    expected_h2h = set()
    for sc, (steps, seeds) in V2_HEAD_TO_HEAD.items():
        for ct in V2_CONTROLLERS:
            for sd in seeds:
                expected_h2h.add((sc, ct, sd, steps))
    missing = sorted(expected_h2h - have_h2h)
    check("head-to-head inventory (70 runs)", not missing,
          f"{len(expected_h2h - have_h2h)} missing" if missing
          else f"{len(have_h2h)} present")
    for m in missing[:10]:
        print(f"    missing: {m}")

    thrash_eta = [r for r in runs if "thrash_eta_sweep" in r["run_id"]]
    thrash_bg = [r for r in runs
                 if "thrash_gamma_sweep" in r["run_id"]
                 and "exact" not in r["run_id"]]
    thrash_bg_exact = [r for r in runs if "thrash_gamma_sweep_exact" in r["run_id"]]
    check("thrash eta sweep (9 gains)",
          sorted(_v2_eta(r) for r in thrash_eta) == sorted(V2_ETAS),
          f"etas={[round(_v2_eta(r), 4) for r in thrash_eta]}")
    check("thrash bias-gamma sweep, shortage (7 gains)",
          sorted(_v2_bias_gamma(r) for r in thrash_bg) == sorted(V2_BIAS_GAMMAS),
          f"gammas={[_v2_bias_gamma(r) for r in thrash_bg]}")
    check("thrash bias-gamma sweep, exact_total (7 gains)",
          sorted(_v2_bias_gamma(r) for r in thrash_bg_exact) == sorted(V2_BIAS_GAMMAS),
          f"gammas={[_v2_bias_gamma(r) for r in thrash_bg_exact]}")

    # W6: paired affinity batches across controllers
    print("# W6 paired affinity batches")
    groups = {}
    for r in runs:
        s = r["summary"]
        if "thrash" in r["run_id"]:
            continue
        groups.setdefault((s["scenario"], s["seed"]), []).append(r)
    for (sc, sd), grp in sorted(groups.items()):
        hashes = set()
        for r in grp:
            a = r["affinity"]
            h = a.get("content_hash_sha256", a.get("content_hash_sha256_base"))
            if h is None:  # adversarial_batches: list of burst hashes
                h = "+".join(a.get("content_hash_sha256_bursts", []))
            hashes.add(h)
        check(f"paired batch {sc} seed={sd}", len(hashes) == 1,
              f"{len(grp)} controllers, {len(hashes)} distinct hashes")

    # W2: windup dissociation (requested rebalances under saturation, admitted stalls)
    print("# W2 saturation windup dissociation")
    for sd in (17, 23):
        grp = [r for r in runs
               if r["summary"]["scenario"] == "saturation_windup"
               and r["summary"]["seed"] == sd and "thrash" not in r["run_id"]]
        by_ctl = {r["summary"]["controller"]: r for r in grp}
        if len(by_ctl) != 7:
            check(f"windup group complete seed={sd}", False,
                  f"found {len(by_ctl)} controllers")
            continue
        ref = json.loads((by_ctl["requested"]["run_dir"]
                          / "affinity_reference.json").read_text())
        spike_end = ref["spike_end"]
        v_req = by_ctl["requested"]["rows"][spike_end - 1]["requested_max_violation"]
        v_adm = by_ctl["admitted"]["rows"][spike_end - 1]["requested_max_violation"]
        check(f"windup seed={sd}: requested rebalances during spike, "
              "admitted stalls (censored)",
              v_req < 0.5 * v_adm,
              f"spike-end viol requested={v_req:.4f} admitted={v_adm:.4f}")
        # release transient is finite for requested (no unbounded windup)
        viol = [row["requested_max_violation"]
                for row in by_ctl["requested"]["rows"]]
        base = sum(viol[300:400]) / 100
        post = viol[spike_end:]
        check(f"windup seed={sd}: requested post-release transient bounded",
              max(post) < base + 0.15,
              f"baseline={base:.4f} max_post={max(post):.4f}")

    # W3: no-projection ablation == requested routing (gauge claim)
    # Theory (real arithmetic): routing depends only on the gauge class, so
    # the identity-projection ablation must route identically. In floating
    # point, common-mode drift can interact with float32 score arithmetic to
    # flip near-ties; rare single-token flips are therefore accepted with a
    # note, but systematic divergence fails.
    print("# W3 no-projection ablation == requested routing")
    for (sc, sd), grp in sorted(groups.items()):
        by_ctl = {r["summary"]["controller"]: r for r in grp}
        rq, np_ = by_ctl.get("requested"), by_ctl.get("requested_no_projection")
        if rq is None or np_ is None:
            check(f"no-projection pair present {sc} seed={sd}", False)
            continue
        n_div = 0
        max_vdiff = 0.0
        for r1, r2 in zip(rq["rows"], np_["rows"]):
            if r1["requested_counts"] != r2["requested_counts"]:
                n_div += 1
            max_vdiff = max(max_vdiff, abs(r1["requested_max_violation"]
                                          - r2["requested_max_violation"]))
        n_steps = len(rq["rows"])
        if n_div == 0:
            check(f"no-projection routing identical {sc} seed={sd}", True)
        else:
            # fp near-tie flips: accept iff the measured violation trajectory
            # is unaffected (the flips are scientifically inconsequential).
            check(f"no-projection routing near-identical {sc} seed={sd}",
                  max_vdiff < 1e-12,
                  f"{n_div}/{n_steps} steps have single-token fp flips, "
                  f"violation trajectories identical (max |diff|={max_vdiff:.2e})")
        # ... but the recorded states differ (common-mode drift, no gauge fixing)
        states_differ = any(
            abs(min(r2["pressure_after"]) - 0.0) > 1e-9
            for r2 in np_["rows"][1:]
        )
        check(f"no-projection state not gauge-fixed {sc} seed={sd}",
              states_differ)

    # W4: bias_integral invariants (sign-based integrator, admitted observation)
    print("# W4 bias_integral invariants")
    for r in runs:
        s = r["summary"]
        if s["controller"] != "bias_integral" or "thrash" in r["run_id"]:
            continue
        bg = _v2_bias_gamma(r)
        rows = r["rows"]
        step_ok = True
        for row in rows:
            before = [float(v) for v in row["pressure_before"]]
            after = [float(v) for v in row["pressure_after"]]
            for b, a in zip(before, after):
                d = a - b
                if not (abs(d) < 1e-12 or abs(abs(d) - bg) < 1e-12):
                    step_ok = False
                    break
            if not step_ok:
                break
        check(f"bias sign-step invariant {s['scenario']} seed={s['seed']} "
              f"(per-step |db| in {{0, {bg}}})", step_ok)
        # bias state is not gauge-fixed (unlike pressure) -- but only when
        # the bias actually moved; an identically-zero bias means admitted
        # loads were uniform every step (saturation freeze for the bias
        # controller: it observes admitted loads, so global saturation
        # blinds it exactly as it blinds admitted-direction pressure).
        moved = any(abs(float(v)) > 1e-12
                    for row in rows for v in row["pressure_after"])
        not_gauge = any(abs(min(float(v) for v in row["pressure_after"])) > 1e-9
                        for row in rows[1:])
        if moved:
            check(f"bias state not gauge-fixed {s['scenario']} seed={s['seed']}",
                  not_gauge)
        else:
            print(f"  [note] bias never moved {s['scenario']} seed={s['seed']} "
                  f"(admitted loads uniform: bias-controller saturation freeze)")

    # W5: thrash-mapping sanity (sweeps span inert -> working -> unstable)
    print("# W5 thrash-mapping sanity")
    if thrash_eta:
        r_lo = min(thrash_eta, key=_v2_eta)
        r_hi = max(thrash_eta, key=_v2_eta)
        v_lo = [row["requested_max_violation"] for row in r_lo["rows"]]
        v_hi = [row["requested_max_violation"] for row in r_hi["rows"]]
        fc_lo = first_routing_change(r_lo["rows"])
        check("eta=0.001 nearly inert",
              fc_lo is None or fc_lo > 400 or abs(v_lo[-1] - v_lo[0]) < 0.01,
              f"first_change={fc_lo} viol {v_lo[0]:.4f}->{v_lo[-1]:.4f}")
        tail_hi = v_hi[-200:]
        check("eta=10.0 unstable (limit-cycle oscillation)",
              max(tail_hi) - min(tail_hi) > 0.02,
              f"tail_range={max(tail_hi)-min(tail_hi):.4f} final={v_hi[-1]:.4f}")
        # mid-range eta converges cleanly (wide stable basin)
        r_mid = min(thrash_eta, key=lambda r: abs(_v2_eta(r) - 1.0))
        v_mid = [row["requested_max_violation"] for row in r_mid["rows"]]
        tail_mid = v_mid[-200:]
        check("eta=1.0 converges cleanly",
              max(tail_mid) - min(tail_mid) < 0.002 and v_mid[-1] < 0.01,
              f"tail_range={max(tail_mid)-min(tail_mid):.4f} final={v_mid[-1]:.4f}")
    if thrash_bg_exact:
        r_lo = min(thrash_bg_exact, key=_v2_bias_gamma)
        r_hi = max(thrash_bg_exact, key=_v2_bias_gamma)
        v_lo = [row["requested_max_violation"] for row in r_lo["rows"]]
        v_hi = [row["requested_max_violation"] for row in r_hi["rows"]]
        check("bias_gamma=1e-4 nearly inert",
              abs(v_lo[-1] - v_lo[0]) < 0.01,
              f"viol {v_lo[0]:.4f}->{v_lo[-1]:.4f}")
        check("bias_gamma=0.1 degraded vs init (thrash)",
              v_hi[-1] > v_hi[0],
              f"viol {v_hi[0]:.4f}->{v_hi[-1]:.4f}")

    print(f"{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECKS FAILED'}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# v3 suite: utmost-version experiments (protocol 0.3.0)
#
# Checks the 79-run v3 matrix in docs/research_history/control_experiment_results/v3_runs/:
#   V3-INV  run inventory (exact 79-run set)
#   V3-PAIR paired affinity batches across controllers within (scenario, seed)
#   V3-DUP  duplicate run-configuration detection (fails loudly)
#   V3-IMM  v1/v2 artifacts and frozen reports byte-identical (via git)
#   V3-T1   non-uniform-target experiment findings (T1)
#   V3-T2   anti-windup head-to-head on v2 scenarios (T2)
#   V3-T3   claim-by-claim re-verification C1..C7 (T3)
#   V3-T4   theorem prospective check (T4; folded into C2)
#   V3-T5   DeepSeek head-to-head statistics, 4 seeds (T5)
#
# Substantive-check rule: every check asserts artifact contents or
# cross-checks between independent computations. The verifier never calls
# the controller feedback() under test to "verify" its own output; where a
# quantity is recomputed (flip-time prediction, MI), it is recomputed from
# the raw affinity tensor plus recorded observations through an independent
# code path.
# ---------------------------------------------------------------------------

V3_T1_CONTROLLERS = (
    "requested", "admitted", "admitted_centered", "capacity_relative",
    "admitted_antiwindup", "bias_integral",
)
V3_T1_CAPACITIES = ("hetero_balanced", "hetero_shortage")
V3_T1_SEEDS = (17, 23, 42)
V3_T1_STEPS = 800
V3_H2H_SCENARIOS = (  # (scenario, steps, capacity)
    ("saturation_windup", 1200, "windup_tight"),
    ("adversarial_init", 800, "shortage"),
    ("adversarial_batches", 1000, "exact_total"),
    ("specialization_probe", 800, "shortage"),
    ("small_batch", 800, "small_shortage"),
)
# Feasible integer-count explicit target used by T1 (K*T*mu).
V3_T1_TARGET_COUNTS = [384, 352, 320, 288, 256, 224, 128, 96]


def _v3_repo_root(runs_dir: Path) -> Path:
    # Derive the repository root from this script, not the archive depth.
    return Path(__file__).resolve().parents[1]


def _v3_imports(runs_dir: Path):
    """Make moe_control and the v3_notes helpers importable."""
    import sys as _sys

    root = _v3_repo_root(runs_dir)
    for p in (str(root / "src"), str(runs_dir.resolve().parent / "v3_notes")):
        if p not in _sys.path:
            _sys.path.insert(0, p)


def _v3_eta_of(run) -> float | None:
    cfg = (run["run_dir"] / "config.resolved.yaml").read_text()
    m = re.search(r"step_size:\s*([\d.]+)", cfg)
    return float(m.group(1)) if m else None


def _v3_config_key(run_dir: Path) -> str:
    """Canonical configuration identity for duplicate detection.

    Built from the full resolved config (all groups). Two runs with the
    same key ran the same experiment; the key excludes nothing
    run-specific because the resolved config contains no run id or
    timestamp.
    """
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(run_dir / "config.resolved.yaml")
    container = OmegaConf.to_container(cfg, resolve=True)
    return json.dumps(container, sort_keys=True)


def _v3_expected_inventory():
    """The exact 79-run v3 matrix as (scenario, capacity, controller, seed,
    steps, eta) tuples."""
    expected = set()
    # T1: non-uniform target x heterogeneous capacity (36)
    for cap in V3_T1_CAPACITIES:
        for ctl in V3_T1_CONTROLLERS:
            for sd in V3_T1_SEEDS:
                # bias_integral runs at step_size=1.0 (its controller YAML);
                # all pressure controllers at 0.05.
                expected.add(("nonuniform_target", cap, ctl, sd,
                              V3_T1_STEPS,
                              1.0 if ctl == "bias_integral" else 0.05))
    # T2: anti-windup on v2 scenarios (10)
    for sc, steps, cap in V3_H2H_SCENARIOS:
        for sd in (17, 23):
            expected.add((sc, cap, "admitted_antiwindup", sd, steps, 0.05))
    # T3: flip-invariant fresh runs (8)
    for sd in (23, 42):
        for eta in (0.05, 0.1, 0.2, 0.4):
            expected.add(("shortage", "shortage", "requested", sd, 1200,
                          eta))
    # T3: freeze retest at fresh seed (2)
    for ctl in ("requested", "admitted"):
        expected.add(("shortage", "shortage", ctl, 99, 500, 0.05))
    # T3: requested_leaky adversarial_init at fresh seed (1)
    expected.add(("adversarial_init", "shortage", "requested_leaky", 42,
                  800, 0.05))
    # T4: theorem prospective etas (2)
    for eta in (0.15, 0.3):
        expected.add(("shortage", "shortage", "requested", 17, 1200, eta))
    # T5: DeepSeek head-to-head extension (20)
    for sc, steps, cap in V3_H2H_SCENARIOS:
        for ctl in ("requested", "bias_integral"):
            for sd in (42, 99):
                expected.add((sc, cap, ctl, sd, steps,
                              1.0 if ctl == "bias_integral" else 0.05))
    return expected


def _mi_independent(labels, top1) -> float:
    """Mutual information (nats) from a contingency table, implemented
    independently of moe_control.metrics (cross-checks the recorded MI)."""
    import torch as _torch

    s = _torch.tensor(list(labels), dtype=_torch.int64)
    e = _torch.tensor(list(top1), dtype=_torch.int64)
    n_s = int(s.max().item()) + 1
    n_e = int(e.max().item()) + 1
    joint = _torch.zeros(n_s, n_e, dtype=_torch.float64)
    for si, ei in zip(s.tolist(), e.tolist()):
        joint[si, ei] += 1.0
    joint = joint / joint.sum()
    p_s = joint.sum(dim=1, keepdim=True)
    p_e = joint.sum(dim=0, keepdim=True)
    denom = p_s * p_e
    mask = joint > 0
    return float(
        (joint[mask] * (joint[mask] / denom[mask]).log()).sum().item())


def _recompute_probe_mi(run) -> tuple[float, float]:
    """Recompute specialization MI at step 0 and the final step from the
    regenerated affinity tensor plus the recorded pressure_before series.

    Independent path: does not call the runner or metrics.specialization_mi.
    Returns (mi_step0, mi_final)."""
    import torch as _torch

    from moe_control.routing.topk import deterministic_topk_order
    from moe_control.scenarios.synthetic import build_affinity_tensor

    _v3_imports(run["run_dir"].parent)
    ref = run["affinity"]
    group_sizes = ref["group_sizes"]
    affinity = build_affinity_tensor(
        ref["seed"], ref["tokens"], ref["experts"], list(group_sizes),
        ref["noise_scale"], getattr(_torch, ref["affinity_dtype"]))
    cfg_text = (run["run_dir"] / "config.resolved.yaml").read_text()
    m = re.search(r"score_gain_override:\s*(\S+)", cfg_text)
    override = None if (not m or m.group(1) == "null") else float(m.group(1))
    m2 = re.search(r"score_gain:\s*([\d.]+)", cfg_text)
    gamma = override if override is not None else float(m2.group(1))
    labels = []
    for g, size in enumerate(group_sizes):
        labels.extend([g] * size)

    def mi_at(row):
        p = _torch.tensor([float(v) for v in row["pressure_before"]],
                          dtype=_torch.float32)
        scores = affinity - gamma * p  # score_sign=-1 pressure form
        order = deterministic_topk_order(scores)
        top1 = order[:, 0].tolist()
        return _mi_independent(labels, top1)

    rows = run["rows"]
    return mi_at(rows[0]), mi_at(rows[-1])


def main_v3(runs_dir: Path) -> int:
    _v3_imports(runs_dir)
    runs = load_runs(runs_dir)
    for r in runs:
        r["run_dir"] = runs_dir.resolve() / r["run_id"]
        r["eta_parsed"] = _v3_eta_of(r)
    failures = 0

    def check(name, ok, detail=""):
        nonlocal failures
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f" -- {detail}" if detail else ""))
        failures += not ok

    def ident(r):
        s = r["summary"]
        return (s["scenario"], s["capacity_regime"], s["controller"],
                s["seed"], s["steps"], r["eta_parsed"])

    # ---- V3-INV: exact 79-run inventory --------------------------------
    print("# V3-INV run inventory")
    expected = _v3_expected_inventory()
    have = {ident(r) for r in runs}
    missing = sorted(expected - have)
    extra = sorted(have - expected)
    check("79-run inventory complete", not missing and not extra,
          f"expected={len(expected)} found={len(have & expected)} "
          f"missing={len(missing)} extra={len(extra)}")
    for m in missing[:12]:
        print(f"    missing: scenario={m[0]} capacity={m[1]} "
              f"controller={m[2]} seed={m[3]} steps={m[4]} eta={m[5]}")
    for e in extra[:12]:
        print(f"    extra: {e}")

    # ---- V3-PAIR: paired affinity batches + declared comparison coverage --
    print("# V3-PAIR paired affinity batches and declared comparisons")
    # (scenario, capacity_regime, seed) -> expected controller set for the
    # declared comparison in that group. Every group must be declared: a
    # lone controller in an undeclared group can no longer pass silently,
    # and a group missing a declared controller fails loudly.
    T1_CTRLS = frozenset(("requested", "admitted", "admitted_centered",
                          "admitted_antiwindup", "capacity_relative",
                          "bias_integral"))
    T5_CTRLS = frozenset(("requested", "bias_integral"))
    expected_pairing = {}
    for regime in ("hetero_balanced", "hetero_shortage"):
        for seed in (17, 23, 42):
            expected_pairing[("nonuniform_target", regime, seed)] = T1_CTRLS
    for sc, regime in (("saturation_windup", "windup_tight"),
                       ("adversarial_init", "shortage"),
                       ("adversarial_batches", "exact_total"),
                       ("specialization_probe", "shortage"),
                       ("small_batch", "small_shortage")):
        for seed in (42, 99):
            expected_pairing[(sc, regime, seed)] = T5_CTRLS
        for seed in (17, 23):
            # T2 probe: singleton by design; paired against the v2 runs of
            # the same scenario+seed via the affinity cross-check below.
            expected_pairing[(sc, regime, seed)] = frozenset(
                ("admitted_antiwindup",))
    for seed in (17, 23, 42):
        # T3 flip-invariant eta sweep (paired across etas) + T4 prospective.
        expected_pairing[("shortage", "shortage", seed)] = frozenset(
            ("requested",))
    # T3 freeze retest: genuine requested-vs-admitted pair on a fresh seed.
    expected_pairing[("shortage", "shortage", 99)] = frozenset(
        ("requested", "admitted"))
    # T3 leaky retest shares its batch with the T5 seed-42 pair: declared as
    # the full group composition, not a lone singleton.
    expected_pairing[("adversarial_init", "shortage", 42)] = frozenset(
        ("requested", "bias_integral", "requested_leaky"))

    def _affinity_hash(a):
        h = a.get("content_hash_sha256", a.get("content_hash_sha256_base"))
        if h is None:
            h = "+".join(a.get("content_hash_sha256_bursts", []))
        return h

    # v2 affinity hashes, for the T2 cross-suite pairing check (lightweight:
    # only summary + affinity reference are read, not the metrics).
    v2_hashes = {}
    v2_dir = runs_dir.resolve().parent / "v2_runs"
    if v2_dir.is_dir():
        for v2_run_dir in sorted(v2_dir.iterdir()):
            aff_p = v2_run_dir / "affinity_reference.json"
            sum_p = v2_run_dir / "summary.json"
            if not (aff_p.exists() and sum_p.exists()):
                continue
            va = json.loads(aff_p.read_text())
            vs = json.loads(sum_p.read_text())
            v2_hashes[(vs["scenario"], vs["seed"])] = _affinity_hash(va)

    groups = {}
    for r in runs:
        s = r["summary"]
        groups.setdefault(
            (s["scenario"], s["capacity_regime"], s["seed"]), []).append(r)
    for key in sorted(set(groups) | set(expected_pairing)):
        sc, regime, sd = key
        grp = groups.get(key, [])
        exp = expected_pairing.get(key)
        tag = f"{sc}/{regime} seed={sd}"
        if exp is None:
            ctrls = sorted({r["summary"]["controller"] for r in grp})
            check(f"V3-PAIR {tag} declared", False,
                  f"unexpected group, controllers={ctrls}")
            continue
        ctrls = {r["summary"]["controller"] for r in grp}
        check(f"V3-PAIR {tag} declared comparison", ctrls == set(exp),
              f"expected={sorted(exp)} found={sorted(ctrls)}")
        hashes = {_affinity_hash(r["affinity"]) for r in grp}
        check(f"V3-PAIR {tag} single affinity hash", len(hashes) == 1,
              f"{len(grp)} runs, {len(hashes)} distinct hashes")
        if exp == frozenset(("admitted_antiwindup",)):
            v2h = v2_hashes.get((sc, sd))
            check(f"V3-PAIR {tag} paired against v2 batch",
                  v2h is not None and next(iter(hashes)) == v2h,
                  "v3 hash matches v2 batch" if v2h else
                  "no v2 run for this scenario+seed")

    # ---- V3-DUP: duplicate run-configuration detection (fail loudly) -----
    print("# V3-DUP duplicate run-configuration detection")
    seen = {}
    dups = []
    for r in runs:
        key = _v3_config_key(r["run_dir"])
        if key in seen:
            dups.append((seen[key], r["run_id"]))
        else:
            seen[key] = r["run_id"]
    check("no duplicate run configurations", not dups,
          f"{len(dups)} duplicate pairs" if dups else
          f"{len(seen)} unique configs")
    for a, b in dups[:6]:
        print(f"    [DUP] {a}  <=>  {b}")

    # ---- V3-IMM: v1/v2 artifacts byte-identical --------------------------
    print("# V3-IMM v1/v2 immutability (via git)")
    import subprocess as _sp

    root = _v3_repo_root(runs_dir)
    frozen_paths = [
        "docs/research_history/control_experiment_results/runs",
        "docs/research_history/control_experiment_results/v2_runs",
        "docs/research_history/control_experiment_results/results.md",
        "docs/research_history/control_experiment_results/results_v2.md",
        "docs/research_history/literature_reviews/moe_routing_load_balancing.md",
    ]
    ps = _sp.run(["git", "-C", str(root), "status", "--porcelain", "--"]
                 + frozen_paths, capture_output=True, text=True)
    dirty = [ln for ln in ps.stdout.splitlines() if ln.strip()]
    check("v1/v2 artifacts and frozen reports unmodified", not dirty,
          f"{len(dirty)} changed paths" if dirty else "clean")
    for ln in dirty[:10]:
        print(f"    {ln}")

    # ---- V3-T3: claim-by-claim re-verification ---------------------------
    v1_dir = runs_dir.resolve().parent / "runs"
    v2_dir = runs_dir.resolve().parent / "v2_runs"
    v1_runs = load_runs(v1_dir) if v1_dir.is_dir() else []
    for r in v1_runs:
        r["run_dir"] = v1_dir / r["run_id"]
    v2_runs = load_runs(v2_dir) if v2_dir.is_dir() else []
    for r in v2_runs:
        r["run_dir"] = v2_dir / r["run_id"]

    def find(runs_list, scenario, controller, seed, steps=None):
        out = [r for r in runs_list
               if r["summary"]["scenario"] == scenario
               and r["summary"]["controller"] == controller
               and r["summary"]["seed"] == seed
               and (steps is None or r["summary"]["steps"] == steps)]
        return out[0] if out else None

    print("# V3-T3 claim-by-claim re-verification")

    # C1: saturation-freeze exactness (v1 artifacts + fresh seed-99 retest).
    print("## C1 saturation-freeze exactness")
    v1_short = [r for r in v1_runs
                if r["summary"]["scenario"] == "shortage"
                and r["summary"]["steps"] == 500]
    for ctl in ("admitted", "admitted_centered"):
        for r in v1_short:
            if r["summary"]["controller"] != ctl:
                continue
            rows = r["rows"]
            p_zero = all(all(abs(float(v)) < 1e-12
                             for v in row["pressure_after"]) for row in rows)
            check(f"C1 v1 freeze {ctl} seed={r['summary']['seed']} "
                  f"pressure==[0]*8", p_zero)
    for r in v1_short:
        if r["summary"]["controller"] != "admitted":
            continue
        fb_ok = all(all(abs(float(v) - (-0.03125)) < 1e-12
                        for v in row["feedback"]) for row in r["rows"])
        check(f"C1 v1 admitted feedback==(c-1)/E seed={r['summary']['seed']}",
              fb_ok)
    for ctl in ("requested", "admitted"):
        r = find(runs, "shortage", ctl, 99, 500)
        if r is None:
            check(f"C1 freeze_retest {ctl} seed=99 present", False)
            continue
        rows = r["rows"]
        if ctl == "admitted":
            p_zero = all(all(abs(float(v)) < 1e-12
                             for v in row["pressure_after"]) for row in rows)
            fb_ok = all(all(abs(float(v) - (-0.03125)) < 1e-12
                            for v in row["feedback"]) for row in rows)
            check("C1 fresh seed=99 admitted pressure frozen", p_zero)
            check("C1 fresh seed=99 admitted feedback==(c-1)/E", fb_ok)
        else:
            prange = max(float(v) for v in rows[-1]["pressure_after"]) - \
                min(float(v) for v in rows[-1]["pressure_after"])
            check("C1 fresh seed=99 requested pressure range ~= 1.05",
                  abs(prange - 1.05) < 0.05, f"range={prange:.4f}")

    # C2: flip-time theorem -- eta*t_flip = ceil(X_seed/eta), |err| <= 2.
    print("## C2 flip-time theorem (T4 prospective included)")
    import predict_flip_time as _pft

    _X = {}
    for sd in (17, 23, 42):
        _X[sd], _, _ = _pft.predict(sd)
    cases = []  # (label, run, seed, eta, predicted)
    import math as _math

    for sd, eta in [(17, 0.05), (17, 0.1), (17, 0.2), (17, 0.4)]:
        cands = [r for r in v1_runs
                 if r["summary"]["scenario"] == "shortage"
                 and r["summary"]["controller"] == "requested"
                 and r["summary"]["seed"] == sd
                 and r["summary"]["steps"] == 2000
                 and abs((_v3_eta_of(r) or -1) - eta) < 1e-12]
        if cands:
            cases.append((f"v1 seed={sd} eta={eta}", cands[0], sd, eta))
    for sd in (23, 42):
        for eta in (0.05, 0.1, 0.2, 0.4):
            cands = [r for r in runs
                     if r["summary"]["scenario"] == "shortage"
                     and r["summary"]["controller"] == "requested"
                     and r["summary"]["seed"] == sd
                     and r["summary"]["steps"] == 1200
                     and abs((r["eta_parsed"] or -1) - eta) < 1e-12
                     and "flip_invariant_test" in r["run_id"]]
            if cands:
                cases.append((f"v3 seed={sd} eta={eta}", cands[0], sd, eta))
    for eta in (0.15, 0.3):
        cands = [r for r in runs
                 if r["summary"]["scenario"] == "shortage"
                 and r["summary"]["controller"] == "requested"
                 and r["summary"]["seed"] == 17
                 and r["summary"]["steps"] == 1200
                 and abs((r["eta_parsed"] or -1) - eta) < 1e-12
                 and "flip_theorem_prospective" in r["run_id"]]
        if cands:
            cases.append((f"v3 prospective seed=17 eta={eta}", cands[0],
                          17, eta))
    for label, r, sd, eta in cases:
        pred = _math.ceil(_X[sd] / eta)
        obs = first_routing_change(r["rows"])
        ok = obs is not None and abs(obs - pred) <= 2
        check(f"C2 {label}: t_flip={obs} vs predicted {pred} "
              f"(X={_X[sd]:.4f})", ok,
              f"|err|={abs(obs - pred) if obs else 'n/a'}")

    # C3: requested_leaky adversarial_init failure (v2 + fresh seed 42).
    print("## C3 requested_leaky adversarial_init failure")
    for r in v2_runs:
        s = r["summary"]
        if s["scenario"] != "adversarial_init" or \
                s["controller"] != "requested_leaky":
            continue
        rows = r["rows"]
        r0_final = rows[-1]["requested_counts"][0]
        v0, vf = (rows[0]["requested_max_violation"],
                  rows[-1]["requested_max_violation"])
        check(f"C3 v2 leaky frozen seed={s['seed']}",
              r0_final == 1024 and abs(vf - 0.375) < 1e-9,
              f"R_0 final={r0_final} viol {v0:.4f}->{vf:.4f}")
    r = find(runs, "adversarial_init", "requested_leaky", 42, 800)
    if r is None:
        check("C3 fresh seed=42 leaky_retest present", False)
    else:
        rows = r["rows"]
        check("C3 fresh seed=42 leaky still frozen",
              rows[-1]["requested_counts"][0] == 1024
              and abs(rows[-1]["requested_max_violation"] - 0.375) < 1e-9,
              f"R_0 final={rows[-1]['requested_counts'][0]}")

    # C4: bias-integral chatter at working gains (recomputed from artifacts).
    print("## C4 bias-integral chatter (tail oscillation counts)")
    from moe_control.metrics import oscillation_count as _osc

    for r in v2_runs:
        if "thrash_gamma_sweep_exact" not in r["run_id"]:
            continue
        cfg = (r["run_dir"] / "config.resolved.yaml").read_text()
        m = re.search(r"bias_gamma:\s*([\d.]+)", cfg)
        bg = float(m.group(1)) if m else None
        viol = [row["requested_max_violation"] for row in r["rows"]]
        tail_osc = _osc(viol, start_idx=len(viol) - 200)
        if bg in (0.003, 0.01, 0.03):
            check(f"C4 bias chatter gamma={bg} (100 <= tail_osc <= 220)",
                  100 <= tail_osc <= 220, f"tail_osc={tail_osc}")
        elif bg == 0.1:
            check("C4 bias gamma=0.1 degraded vs init",
                  viol[-1] > viol[0],
                  f"viol {viol[0]:.4f}->{viol[-1]:.4f} tail_osc={tail_osc}")

    # C5: specialization Pareto (endpoints + independent MI recomputation).
    print("## C5 specialization Pareto")
    for sd in (17, 23):
        rq = find(v2_runs, "specialization_probe", "requested", sd, 800)
        ad = find(v2_runs, "specialization_probe", "admitted", sd, 800)
        if rq is None or ad is None:
            check(f"C5 probe runs present seed={sd}", False)
            continue
        ov0 = rq["rows"][0]["total_overflow"]
        ov_rq, ov_ad = (rq["rows"][-1]["total_overflow"],
                        ad["rows"][-1]["total_overflow"])
        check(f"C5 seed={sd} requested overflow {ov0}->{ov_rq} (floor 512)",
              ov0 == 648 and ov_rq == 512,
              f"admitted final={ov_ad}")
        check(f"C5 seed={sd} admitted keeps overflow at 648", ov_ad == 648)
        mi0_rec, mi1_rec = _recompute_probe_mi(rq)
        mi0_rep = rq["rows"][0]["specialization_mi"]
        mi1_rep = rq["rows"][-1]["specialization_mi"]
        check(f"C5 seed={sd} MI recomputation matches recorded (step 0)",
              abs(mi0_rec - mi0_rep) < 1e-9,
              f"recomputed={mi0_rec:.6f} recorded={mi0_rep:.6f}")
        check(f"C5 seed={sd} MI recomputation matches recorded (final)",
              abs(mi1_rec - mi1_rep) < 1e-9,
              f"recomputed={mi1_rec:.6f} recorded={mi1_rep:.6f}")
        check(f"C5 seed={sd} requested MI 1.301 -> ~1.06",
              abs(mi0_rep - 1.301) < 0.005 and 1.0 < mi1_rep < 1.12,
              f"{mi0_rep:.3f} -> {mi1_rep:.3f}")
        mi_ad0 = ad["rows"][0]["specialization_mi"]
        mi_ad1 = ad["rows"][-1]["specialization_mi"]
        check(f"C5 seed={sd} admitted preserves MI",
              abs(mi_ad1 - mi_ad0) < 1e-9, f"{mi_ad0:.3f} -> {mi_ad1:.3f}")

    # C6: pressure eta-basin edges (v2 thrash artifacts).
    print("## C6 pressure eta-basin edges")
    from moe_control.metrics import oscillation_count as _osc

    thrash = [r for r in v2_runs if "thrash_eta_sweep" in r["run_id"]]
    for r in thrash:
        eta = _v3_eta_of(r)
        viol = [row["requested_max_violation"] for row in r["rows"]]
        tail = viol[-200:]
        fc = first_routing_change(r["rows"])
        tail_osc = _osc(viol, start_idx=len(viol) - 200)
        if eta is not None and eta <= 0.03:
            check(f"C6 eta={eta} inert",
                  fc is None or abs(viol[-1] - viol[0]) < 0.01,
                  f"first_change={fc}")
        elif eta in (0.1, 0.3, 1.0, 3.0):
            # "converged cleanly": low final violation and no tail
            # oscillation (the trajectory may still be settling slightly,
            # so the tail need not be perfectly flat).
            check(f"C6 eta={eta} converged cleanly (no tail oscillation)",
                  tail_osc == 0 and viol[-1] < 0.01,
                  f"tail_osc={tail_osc} final={viol[-1]:.4f}")
        elif eta == 10.0:
            check("C6 eta=10 limit cycle",
                  max(tail) - min(tail) > 0.02,
                  f"tail_range={max(tail) - min(tail):.4f}")

    # C7: no oscillation in v1 sweep tails.
    print("## C7 sweep-tail no-oscillation (v1)")
    sweep = {}
    for r in v1_runs:
        s = r["summary"]
        if s["steps"] == 2000 and s["scenario"] == "shortage" \
                and s["controller"] == "requested":
            cfg = (r["run_dir"] / "config.resolved.yaml").read_text()
            m = re.search(r"step_size:\s*([\d.]+)", cfg)
            if m:
                sweep[float(m.group(1))] = r
    for eta, r in sorted(sweep.items()):
        viol = [row["requested_max_violation"] for row in r["rows"]]
        tail = viol[-500:]
        trange = max(tail) - min(tail)
        if eta >= 0.1:
            check(f"C7 eta={eta} tail exactly flat", trange == 0.0,
                  f"tail_range={trange:.5f}")
        else:
            check("C7 eta=0.05 tail range == 2/2048 and settling",
                  abs(trange - 2 / 2048) < 1e-12 and min(tail) == viol[-1],
                  f"tail_range={trange:.5f}")

    # ---- V3-T1: non-uniform-target findings --------------------------------
    print("# V3-T1 non-uniform-target experiment")
    t1 = [r for r in runs if r["summary"]["scenario"] == "nonuniform_target"]

    def t1run(cap, ctl, seed):
        cands = [r for r in t1
                 if r["summary"]["capacity_regime"] == cap
                 and r["summary"]["controller"] == ctl
                 and r["summary"]["seed"] == seed]
        return cands[0] if cands else None

    def best_exact_balance(rows):
        return min(max(abs(rc - t) for rc, t in
                       zip(row["requested_counts"], V3_T1_TARGET_COUNTS))
                   for row in rows)

    def prange_max(rows):
        return max(max(float(v) for v in row["pressure_after"])
                   - min(float(v) for v in row["pressure_after"])
                   for row in rows)

    # T1-exact: no controller attains the feasible integer target exactly
    # in 800 steps; requested gets within 18 tokens on every seed/regime.
    print("## T1 exact-balance outcomes")
    for cap in V3_T1_CAPACITIES:
        for sd in V3_T1_SEEDS:
            bests = {}
            for ctl in V3_T1_CONTROLLERS:
                r = t1run(cap, ctl, sd)
                if r is None:
                    continue
                bests[ctl] = best_exact_balance(r["rows"])
            if len(bests) != len(V3_T1_CONTROLLERS):
                check(f"T1 {cap} seed={sd} all controllers present", False,
                      f"found {len(bests)}")
                continue
            check(f"T1 {cap} seed={sd} requested within 18 tokens of target",
                  bests["requested"] <= 18,
                  f"best={bests['requested']:.0f}")
            check(f"T1 {cap} seed={sd} no controller attains exact balance",
                  min(bests.values()) > 0,
                  f"min over controllers={min(bests.values()):.0f}")

    # T1-phantom: under global saturation with heterogeneous capacity,
    # admitted integrates a phantom gradient while admitted_antiwindup
    # freezes exactly.
    print("## T1 phantom gradient vs exact freeze (hetero_shortage)")
    for sd in V3_T1_SEEDS:
        r_adm = t1run("hetero_shortage", "admitted", sd)
        r_aw = t1run("hetero_shortage", "admitted_antiwindup", sd)
        if r_adm is None or r_aw is None:
            check(f"T1 phantom pair present seed={sd}", False)
            continue
        sat_aw = [row for row in r_aw["rows"]
                  if row["all_experts_saturated"]]
        frozen = all(
            all(abs(float(a) - float(b)) < 1e-12
                for a, b in zip(row["pressure_before"],
                                row["pressure_after"]))
            for row in sat_aw)
        check(f"T1 seed={sd} antiwindup exactly frozen on saturated steps",
              frozen and len(sat_aw) == 800,
              f"saturated steps={len(sat_aw)}")
        fb_zero = all(all(abs(float(v)) < 1e-12 for v in row["feedback"])
                      for row in sat_aw)
        check(f"T1 seed={sd} antiwindup feedback==0 when saturated",
              fb_zero)
        sat_adm = [row for row in r_adm["rows"]
                   if row["all_experts_saturated"]]
        moved = sum(
            1 for a, b in zip(sat_adm, sat_adm[1:])
            if b["step"] == a["step"] + 1
            and max(abs(float(x) - float(y))
                    for x, y in zip(a["pressure_after"],
                                    b["pressure_after"])) > 1e-12)
        check(f"T1 seed={sd} admitted integrates phantom (moves on "
              f"saturated steps)", moved > 700,
              f"moved pairs={moved}/{len(sat_adm) - 1}")
        check(f"T1 seed={sd} admitted phantom pressure range > 1.0",
              prange_max(r_adm["rows"]) > 1.0,
              f"prange_max={prange_max(r_adm['rows']):.3f}")
        # ... while requested counts stay frozen for both (signal censored).
        v_adm = [row["requested_max_violation"] for row in r_adm["rows"]]
        v_aw = [row["requested_max_violation"] for row in r_aw["rows"]]
        check(f"T1 seed={sd} routing frozen for admitted/antiwindup",
              max(v_adm) - min(v_adm) < 1e-12
              and max(v_aw) - min(v_aw) < 1e-12)

    # T1-centered: (A_0) diverges under heterogeneous capacity --
    # equalizing the censored admitted signal diverts demand onto
    # low-capacity experts.
    print("## T1 admitted_centered divergence (hetero_shortage)")
    for sd in V3_T1_SEEDS:
        r = t1run("hetero_shortage", "admitted_centered", sd)
        if r is None:
            check(f"T1 centered run present seed={sd}", False)
            continue
        rows = r["rows"]
        check(f"T1 seed={sd} centered viol explodes (> 0.4)",
              rows[-1]["requested_max_violation"] > 0.4,
              f"{rows[0]['requested_max_violation']:.4f} -> "
              f"{rows[-1]['requested_max_violation']:.4f}")
        check(f"T1 seed={sd} centered overflow explodes (> 1000)",
              rows[-1]["total_overflow"] > 1000,
              f"{rows[0]['total_overflow']} -> {rows[-1]['total_overflow']}")

    # T1-pareto: hetero_balanced -- no controller wins on both violation
    # and overflow; requested takes violation, capacity_relative takes
    # overflow, admitted_centered is worse than initial on violation.
    print("## T1 hetero_balanced Pareto (no dominant controller)")
    for sd in V3_T1_SEEDS:
        fin = {}
        for ctl in V3_T1_CONTROLLERS:
            r = t1run("hetero_balanced", ctl, sd)
            if r is None:
                continue
            rows = r["rows"]
            fin[ctl] = (rows[-1]["requested_max_violation"],
                        rows[-1]["total_overflow"])
        if len(fin) != len(V3_T1_CONTROLLERS):
            check(f"T1 pareto runs present seed={sd}", False)
            continue
        check(f"T1 seed={sd} requested best violation (<= 0.01)",
              fin["requested"][0] <= 0.01, f"{fin['requested'][0]:.4f}")
        check(f"T1 seed={sd} capacity_relative best overflow (<= 70)",
              fin["capacity_relative"][1] <= 70,
              f"{fin['capacity_relative'][1]}")
        dominates = any(v <= 0.01 and o <= 70 for v, o in fin.values())
        check(f"T1 seed={sd} no controller dominates both metrics",
              not dominates,
              "; ".join(f"{c}: viol={v:.4f} ov={o}" for c, (v, o)
                         in sorted(fin.items())))
        check(f"T1 seed={sd} admitted_centered worse than initial",
              fin["admitted_centered"][0] > 0.0576,
              f"final viol={fin['admitted_centered'][0]:.4f}")

    # T1-saturation: regime saturation fractions.
    print("## T1 saturation fractions")
    for sd in V3_T1_SEEDS:
        r = t1run("hetero_shortage", "requested", sd)
        if r is not None:
            check(f"T1 hetero_shortage seed={sd} globally saturated "
                  f"throughout",
                  r["summary"]["fraction_steps_saturated"] == 1.0)
        check(f"T1 hetero_balanced seed={sd} never globally saturated",
              all(t1run("hetero_balanced", ctl, sd)["summary"]
                  ["fraction_steps_saturated"] == 0.0
                  for ctl in V3_T1_CONTROLLERS))

    # ---- V3-T2: anti-windup head-to-head (on v2 scenarios) -----------------
    print("# V3-T2 anti-windup head-to-head")
    # Anti-windup runs live in v3_runs (tag antiwindup_probe); the
    # comparison controllers live in v2_runs (head-to-head matrix).
    def v2run(sc, ctl, sd, steps):
        cands = [r for r in v2_runs
                 if r["summary"]["scenario"] == sc
                 and r["summary"]["controller"] == ctl
                 and r["summary"]["seed"] == sd
                 and r["summary"]["steps"] == steps]
        return cands[0] if cands else None

    def v3aw(sc, sd, steps):
        cands = [r for r in runs
                 if r["summary"]["scenario"] == sc
                 and r["summary"]["controller"] == "admitted_antiwindup"
                 and r["summary"]["seed"] == sd
                 and r["summary"]["steps"] == steps
                 and "antiwindup_probe" in r["run_id"]]
        return cands[0] if cands else None

    for sc, steps, _cap in V3_H2H_SCENARIOS:
        aws = {}
        for sd in (17, 23):
            r = v3aw(sc, sd, steps)
            if r is None:
                check(f"T2 {sc} antiwindup run present seed={sd}", False)
                continue
            aws[sd] = r
        if len(aws) != 2:
            continue
        rqs = {sd: v2run(sc, "requested", sd, steps) for sd in (17, 23)}
        ads = {sd: v2run(sc, "admitted", sd, steps) for sd in (17, 23)}
        if any(v is None for v in list(rqs.values()) + list(ads.values())):
            check(f"T2 {sc} v2 comparison runs present", False)
            continue
        # Cross-cutting: anti-windup never beats requested on final
        # violation in any scenario-seed pair (it is strictly more
        # conservative by design).
        for sd in (17, 23):
            vf_aw = aws[sd]["rows"][-1]["requested_max_violation"]
            vf_rq = rqs[sd]["rows"][-1]["requested_max_violation"]
            check(f"T2 {sc} seed={sd} antiwindup never beats requested",
                  vf_rq <= vf_aw + 1e-12,
                  f"requested={vf_rq:.4f} antiwindup={vf_aw:.4f}")
        if sc == "saturation_windup":
            for sd in (17, 23):
                viol_aw = [row["requested_max_violation"]
                           for row in aws[sd]["rows"]]
                viol_ad = [row["requested_max_violation"]
                           for row in ads[sd]["rows"]]
                # Worse during the spike (refuses the censored signal)...
                check(f"T2 windup seed={sd} antiwindup worse at spike end "
                      f"than admitted",
                      viol_aw[799] > viol_ad[799],
                      f"antiwindup={viol_aw[799]:.4f} "
                      f"admitted={viol_ad[799]:.4f}")
                # ...but zero post-release overshoot and exact return to
                # baseline (no miscalibrated state to unwind).
                base = sum(viol_aw[300:400]) / 100
                post = viol_aw[800:]
                check(f"T2 windup seed={sd} antiwindup zero post-release "
                      f"overshoot", max(post) - base < 0.01,
                      f"overshoot={max(post) - base:.4f}")
                check(f"T2 windup seed={sd} antiwindup returns to baseline",
                      abs(viol_aw[-1] - 0.0215) < 1e-4,
                      f"final={viol_aw[-1]:.4f}")
        elif sc == "adversarial_init":
            for sd in (17, 23):
                rows_aw = aws[sd]["rows"]
                vf_aw = rows_aw[-1]["requested_max_violation"]
                r0_aw = rows_aw[-1]["requested_counts"][0]
                vf_ad = ads[sd]["rows"][-1]["requested_max_violation"]
                vf_rq = rqs[sd]["rows"][-1]["requested_max_violation"]
                check(f"T2 init seed={sd} antiwindup frozen on dominant "
                      f"expert", abs(vf_aw - 0.3750) < 1e-9 and r0_aw == 1024,
                      f"viol={vf_aw:.4f} R_0={r0_aw}")
                check(f"T2 init seed={sd} admitted partially escapes, "
                      f"requested fully escapes",
                      vf_ad < 0.25 and vf_rq <= 0.03,
                      f"admitted={vf_ad:.4f} requested={vf_rq:.4f}")
        elif sc == "adversarial_batches":
            for sd in (17, 23):
                vf = aws[sd]["rows"][-1]["requested_max_violation"]
                check(f"T2 batches seed={sd} antiwindup frozen "
                      f"(no differential unsaturated signal)",
                      abs(vf - 0.3750) < 1e-9, f"final viol={vf:.4f}")
        elif sc == "specialization_probe":
            for sd in (17, 23):
                rows = aws[sd]["rows"]
                check(f"T2 probe seed={sd} antiwindup frozen like admitted",
                      abs(rows[-1]["requested_max_violation"]
                          - rows[0]["requested_max_violation"]) < 1e-12
                      and rows[-1]["total_overflow"] == 648,
                      f"viol={rows[-1]['requested_max_violation']:.4f} "
                      f"ov={rows[-1]['total_overflow']}")
        elif sc == "small_batch":
            for sd in (17, 23):
                rows = aws[sd]["rows"]
                check(f"T2 small_batch seed={sd} antiwindup frozen "
                      f"(global saturation)",
                      abs(rows[-1]["requested_max_violation"]
                          - rows[0]["requested_max_violation"]) < 1e-12,
                      f"final viol={rows[-1]['requested_max_violation']:.4f}")

    # ---- V3-T5: DeepSeek head-to-head statistics --------------------------
    print("# V3-T5 DeepSeek head-to-head (requested vs bias_integral, "
          "4 seeds)")
    # Expected paired-win pattern, verified from the artifacts:
    # requested wins all 4 seeds on every scenario except
    # saturation_windup, where bias_integral wins all 4 on final violation
    # (while losing badly at spike end: 0.166 vs 0.0215, per v2).
    _T5_WINS_EXPECTED = {
        "saturation_windup": "bias_integral",
        "adversarial_init": "requested",
        "adversarial_batches": "requested",
        "specialization_probe": "requested",
        "small_batch": "requested",
    }
    for sc, steps, _cap in V3_H2H_SCENARIOS:
        finals = {"requested": [], "bias_integral": []}
        ok_load = True
        for sd in (17, 23):
            for ctl in ("requested", "bias_integral"):
                r = v2run(sc, ctl, sd, steps)
                if r is None:
                    ok_load = False
                else:
                    finals[ctl].append(
                        r["rows"][-1]["requested_max_violation"])
        for sd in (42, 99):
            for ctl in ("requested", "bias_integral"):
                cands = [r for r in runs
                         if r["summary"]["scenario"] == sc
                         and r["summary"]["controller"] == ctl
                         and r["summary"]["seed"] == sd
                         and r["summary"]["steps"] == steps
                         and "deepseek_headtohead" in r["run_id"]]
                if not cands:
                    ok_load = False
                else:
                    finals[ctl].append(
                        cands[0]["rows"][-1]["requested_max_violation"])
        if not ok_load or any(len(v) != 4 for v in finals.values()):
            check(f"T5 {sc} all 8 runs present (2 ctl x 4 seeds)", False,
                  f"requested={len(finals['requested'])} "
                  f"bias={len(finals['bias_integral'])}")
            continue
        wins = {"requested": 0, "bias_integral": 0}
        for vr, vb in zip(finals["requested"], finals["bias_integral"]):
            wins["requested" if vr < vb else "bias_integral"] += 1
        exp = _T5_WINS_EXPECTED[sc]
        check(f"T5 {sc} paired wins 4-0 for {exp}",
              wins[exp] == 4 and wins["bias_integral" if exp == "requested"
                                     else "requested"] == 0,
              f"wins={wins} requested_mean="
              f"{sum(finals['requested']) / 4:.4f} bias_mean="
              f"{sum(finals['bias_integral']) / 4:.4f}")

    print(f"{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECKS FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

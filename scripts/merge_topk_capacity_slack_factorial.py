#!/usr/bin/env python3
"""Deterministically merge the registered E=4 and E=8 experiment blocks."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/topk_capacity_slack_factorial_2026-10-18"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    summaries = [json.loads((BASE / f"E{e}/summary.json").read_text(encoding="utf-8")) for e in (4, 8)]
    if any(not s["all_registered_invariants_passed"] for s in summaries):
        raise AssertionError("a block reports a failed registered invariant")
    for e, summary in zip((4, 8), summaries, strict=True):
        if {int(c["E"]) for c in summary["cells"]} != {e}:
            raise AssertionError(f"summary rows do not match E={e} block")
    if summaries[0]["protocol_sha256"] != summaries[1]["protocol_sha256"]:
        raise AssertionError("blocks used different protocol files")
    raw_rows: list[dict[str, str]] = []
    for e in (4, 8):
        with (BASE / f"E{e}/paired_plants.csv").open(newline="", encoding="utf-8") as f:
            raw_rows.extend(csv.DictReader(f))
    raw_rows.sort(key=lambda x: (x["E"], x["law"], x["K"], x["shortage_fraction_of_max"],
                                 x["T"], x["regime"], x["replicate"], x["H"]))
    raw_path = BASE / "paired_plants.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(raw_rows[0]))
        w.writeheader()
        w.writerows(raw_rows)
    cells = [c for s in summaries for c in s["cells"]]
    cells.sort(key=lambda x: (x["E"], x["law"], x["K"], x["shortage_fraction_of_max"],
                              x["T"], x["regime"], x["H"]))
    cells_path = BASE / "cells.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0]))
        w.writeheader()
        w.writerows(cells)
    summary = {
        "protocol": summaries[0]["protocol"],
        "protocol_sha256": summaries[0]["protocol_sha256"],
        "script_sha256": summaries[0]["script_sha256"],
        "merge_script_sha256": digest(Path(__file__)),
        "E_blocks": [4, 8],
        "paired_rows": len(raw_rows),
        "summary_cells": len(cells),
        "parameter_profiles": sum(s["parameter_profiles"] for s in summaries),
        "no_clipping_round_controls": sum(s["no_clipping_round_controls"] for s in summaries),
        "exact_score_ties": sum(s["exact_score_ties"] for s in summaries),
        "all_registered_invariants_passed": True,
        "laws": summaries[0]["laws"],
        "all_K": True,
        "shortage_fractions_of_max": summaries[0]["shortage_fractions_of_max"],
        "T_scales": summaries[0]["T_scales"],
        "regimes": summaries[0]["regimes"],
        "replicates": summaries[0]["replicates"],
        "horizons": summaries[0]["horizons"],
        "block_summaries": {
            "E4": {"block_E": 4, "summary_sha256": digest(BASE / "E4/summary.json"),
                   "raw_sha256": digest(BASE / "E4/paired_plants.csv")},
            "E8": {"block_E": 8, "summary_sha256": digest(BASE / "E8/summary.json"),
                   "raw_sha256": digest(BASE / "E8/paired_plants.csv")},
        },
        "paired_plants_sha256": digest(raw_path),
        "cells_sha256": digest(cells_path),
        "cells": cells,
    }
    summary_path = BASE / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "paired_rows", "summary_cells", "parameter_profiles", "no_clipping_round_controls",
        "exact_score_ties", "all_registered_invariants_passed", "paired_plants_sha256", "cells_sha256")}, indent=2))


if __name__ == "__main__":
    main()

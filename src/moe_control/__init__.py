"""Deterministic closed-loop MoE routing control experiment.

Implements the synthetic control experiment described in
``docs/formal_definitions/formal.md``. Its established central mechanism and
scope are documented in ``docs/central_claim/theorem.md``. The superseded
architecture plan is retained under ``docs/research_history/``.

The package compares requested-load feedback against admitted-load feedback
under capacity saturation, using gauge-normalized pressure dynamics on a
synthetic Top-K routing loop. The routing/control core is plain PyTorch;
there is no Lightning dependency in this package.
"""

__version__ = "0.1.0"

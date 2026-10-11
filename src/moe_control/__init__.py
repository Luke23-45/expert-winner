"""Deterministic closed-loop MoE routing control experiment.

Implements the control experiment described in
``docs/formal_definitions/formal.md`` and
``docs/formal_definitions/implemention_plan/architecture_implementation_plan.md``.

The package compares requested-load feedback against admitted-load feedback
under capacity saturation, using gauge-normalized pressure dynamics on a
synthetic Top-K routing loop. The routing/control core is plain PyTorch;
there is no Lightning dependency in this package (see the architecture plan
for the intended future training integration point).
"""

__version__ = "0.1.0"

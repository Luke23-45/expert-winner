from moe_control.scenarios.hardened import (
    AdversarialBatchesScenario,
    AdversarialInitScenario,
    SaturationWindupScenario,
    SpecializationProbeScenario,
    build_hardened_scenario,
)
from moe_control.scenarios.synthetic import (
    DemandShiftScenario,
    SyntheticScenario,
    affinity_content_hash,
    build_affinity_tensor,
    build_scenario as _build_synthetic_scenario,
)

__all__ = [
    "SyntheticScenario",
    "DemandShiftScenario",
    "SaturationWindupScenario",
    "AdversarialInitScenario",
    "AdversarialBatchesScenario",
    "SpecializationProbeScenario",
    "build_scenario",
    "build_affinity_tensor",
    "affinity_content_hash",
]

_HARDENED_KINDS = (
    "saturation_windup",
    "adversarial_init",
    "adversarial_batches",
    "specialization_probe",
)

_SYNTHETIC_PARAMS = {
    "seed", "tokens", "experts", "group_sizes", "noise_scale",
    "affinity_dtype", "shift_step", "shift_group_sizes",
}
_HARDENED_PARAMS = {
    "seed", "tokens", "experts", "group_sizes", "noise_scale",
    "affinity_dtype", "spike_step", "spike_end", "spike_group_sizes",
    "dominant_expert", "dominant_offset", "burst_period", "n_bursts",
    "preference_gap", "burst_noise_scale",
}


def build_scenario(name: str, kind: str, **kwargs):
    """Construct a scenario from validated config values.

    Dispatches to the synthetic/demand-shift builders or the hardened
    scenario builders based on ``kind``. The CLI passes the full validated
    scenario parameter set; only the parameters each builder accepts are
    forwarded.
    """
    if kind in _HARDENED_KINDS:
        params = {k: v for k, v in kwargs.items() if k in _HARDENED_PARAMS}
        return build_hardened_scenario(name=name, kind=kind, **params)
    params = {k: v for k, v in kwargs.items() if k in _SYNTHETIC_PARAMS}
    return _build_synthetic_scenario(name=name, kind=kind, **params)

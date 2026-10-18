"""Auto-install the experiment adapter in each Megatron torchrun worker."""

import os

if os.environ.get("MOE_FEEDBACK_EXPERIMENT") == "1":
    from adapter import install

    install()

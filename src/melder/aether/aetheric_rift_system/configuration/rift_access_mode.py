from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftAccessMode(Enum):
    """
    Internal

    System-level policy for direct Rift or RiftState retrieval.
    """

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    system_only = "system_only"


from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftCreationMode(Enum):
    """
    Internal

    System-level policy for Rift creation/programming.
    """

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    prebuilt_only = "prebuilt_only"


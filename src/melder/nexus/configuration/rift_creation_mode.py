from enum import Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg



class RiftCreationMode(Enum):
    """
    Internal

    System-level policy for Rift creation/programming.

    Members:
        open:
            Rift creation/programming is allowed without a creation token.
        token_required:
            Rift creation/programming is allowed only when the caller supplies
            the configured creation token.
        prebuilt_only:
            New Rift creation is blocked; only prebuilt/external Rift shells may
            be programmed into the system.
    """

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    prebuilt_only = "prebuilt_only"

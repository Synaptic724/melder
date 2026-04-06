from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftAccessMode(Enum):
    """
    Internal

    System-level policy for direct Rift retrieval.

    Members:
        open:
            Direct Rift lookup is allowed without an access token.
        token_required:
            Direct Rift lookup is allowed only when the caller supplies the
            configured access token.
        system_only:
            Direct Rift lookup is reserved for trusted internal/system flows.
    """

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    system_only = "system_only"

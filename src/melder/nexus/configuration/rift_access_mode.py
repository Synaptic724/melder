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

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Nexus configuration
        vocabulary.

    Subsystem Context:
        One of the process-wide policy vocabularies stored in
        `NexusConfiguration`, alongside the other access-control controls.

    System Context:
        Direct Rift retrieval is gated because holding a Rift is holding live AR access. `open` permits lookup freely, `token_required` demands the configured token, and `system_only` restricts retrieval to the system itself - a ladder from convenience to containment.
        Because this is PROCESS-WIDE policy frozen at configuration time, the
        choice applies uniformly to every Rift - which is the point. A gate that
        varied per Rift could be escaped by creating a differently configured
        one, so the governance that matters lives here rather than on the Rift.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. System-level policy for direct Rift retrieval. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    system_only = "system_only"

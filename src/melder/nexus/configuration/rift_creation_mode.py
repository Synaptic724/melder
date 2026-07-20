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

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Nexus configuration
        vocabulary.

    Subsystem Context:
        One of the process-wide policy vocabularies stored in
        `NexusConfiguration`, alongside the other creation-control controls.

    System Context:
        Creation is gated separately from access because creating a Rift and retrieving one are different privileges: a caller allowed to use an existing Rift is not necessarily allowed to mint new ones with a posture of its choosing.
        Because this is PROCESS-WIDE policy frozen at configuration time, the
        choice applies uniformly to every Rift - which is the point. A gate that
        varied per Rift could be escaped by creating a differently configured
        one, so the governance that matters lives here rather than on the Rift.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. System-level policy for Rift creation/programming. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    open = "open"
    token_required = "token_required"
    prebuilt_only = "prebuilt_only"

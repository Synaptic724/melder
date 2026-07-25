from enum import Enum



class RiftValidationMode(Enum):
    """
    Internal

    Validation posture for Rift codegen/runtime execution.

    Members:
        strict:
            Apply the full validation posture and fail on contract violations.
        relaxed:
            Apply a lighter validation posture that tolerates some non-fatal
            issues while still checking core contracts.
        unsafe:
            Minimize validation barriers for trusted/internal flows that need
            maximum freedom over safety checks.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Nexus configuration
        vocabulary.

    Subsystem Context:
        One of the process-wide policy vocabularies stored in
        `NexusConfiguration`, alongside the other validation-posture controls.

    System Context:
        `strict` fails on contract violations while `relaxed` tolerates non-fatal issues and still checks the rest. That choice belongs to process-wide policy rather than to a room, because a relaxed posture selectable per Rift would let a caller opt out of the validation the deployment intended.
        Because this is PROCESS-WIDE policy frozen at configuration time, the
        choice applies uniformly to every Rift - which is the point. A gate that
        varied per Rift could be escaped by creating a differently configured
        one, so the governance that matters lives here rather than on the Rift.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Validation posture for Rift codegen/runtime execution. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    strict = "strict"
    relaxed = "relaxed"
    unsafe = "unsafe"

from enum import Enum



class RiftSpaceType(Enum):
    """
    Internal

    Supported top-level room types for a Rift.

    Members:
        static:
            The Rift exposes the lower-risk room surface with live-only
            spell-facing behavior and no runtime topology mutation.
        capability:
            The Rift exposes broad manual runtime and object access without
            codegen while still honoring lower Melder frame truth.
        codegen:
            The Rift exposes the richer room surface intended for mutable local
            state and later codegen-oriented differentiation. It currently
            shares the same broad manual-runtime posture as capability.
        dynamic:
            Legacy alias for `codegen`. Retained temporarily so older AR
            configuration inputs can still normalize during the room rename.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Users pass a member into
        Rift configuration.

    Subsystem Context:
        The selector that programs a Rift's one primary room. `Rift` reads it at
        creation and constructs the matching `RiftSpace` subclass - it is the
        single input that fixes a Rift's capability posture for life.

    System Context:
        Room type is chosen ONCE at Rift creation and never switched: a Rift
        owns exactly one primary room with no room registry and no active-space
        switching. That is what makes the posture a real boundary rather than a
        mode flag - an agent cannot escalate from static to capability by
        switching rooms, it must obtain a differently configured Rift.
        `dynamic` is a documented LEGACY ALIAS for `codegen`, retained so older
        AR configuration inputs still normalize through the room rename. Keeping
        the alias rather than breaking those inputs is the compatibility posture
        the repo prefers, and its docstring says plainly that it is temporary -
        which is what makes eventual removal a decision rather than a surprise.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Room posture, chosen ONCE at Rift creation: static (live-only, no
        mutation), capability (broad manual, no codegen), codegen (slim manual surface plus the
        codegen engine). `dynamic` is a legacy alias for codegen.
    """

    static = "static"
    capability = "capability"
    codegen = "codegen"

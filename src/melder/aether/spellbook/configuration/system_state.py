from enum import StrEnum
from typing import Optional

class SystemState(StrEnum):
    """
    High-level runtime posture for a spellbook/system.

    Values exactly match member names. Historical numeric values 1 and 2
    remain readable by value, including in older enum pickle payloads.

    `SystemState` selects how aggressively the runtime is allowed to perform
    dynamic behaviors.

    Contract:
    - `automatic` is the safer default posture for normal managed runtime
      behavior.
    - `dynamic` enables the more permissive runtime posture required by
      AI-native and other advanced dynamic behaviors.
    - Configuration validation may enforce semantic relationships between this
      enum and other flags such as `ai_native_enabled`.

    States:
    - automatic: managed/default runtime posture
    - dynamic: advanced dynamic runtime posture

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Users pass it into
        `SpellbookConfiguration`.

    Subsystem Context:
        The runtime-posture selector for a spellbook, propagated onto the frame
        through `AethericFrameConfiguration` at conjure.

    System Context:
        This two-value enum gates more behaviour than any other flag in the
        system. Under `automatic`, `conjure` admits ONLY `Policies.default`,
        and linking, severing, ownership transfer, and lesser-to-normal upgrade
        all raise - because an automatic world promises one self-contained graph
        fixed at conjure. Under `dynamic`, the graph may be rewired afterwards,
        which is what AI-native workflows require.
        The frame is the enforcement point rather than the book: frames come
        BEFORE books in the boot order precisely because the frame owns the
        dynamic gate that conjure's `check_system_state` reads. That is also why
        a restore must posture a frame before building its books, and why the
        crystallizer warns when a book's frame twin is missing from a bundle.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Runtime posture: automatic (fixed graph, safer) or dynamic (rewiring
        allowed). Dynamic is REQUIRED for linking, severing, ownership transfer, and
        lesser-to-normal upgrade. Set it on SpellbookConfiguration.
    """
    automatic = "automatic"
    dynamic = "dynamic"

    @classmethod
    def _missing_(cls, value: object) -> Optional[SystemState]:
        """
        Resolve a historical numeric posture to its original member.

        Current names use ordinary enum lookup. Values equal to the old
        integers remain readable; unknown or unhashable inputs return None
        so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, SystemState] = {
            1: cls.automatic,
            2: cls.dynamic,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None

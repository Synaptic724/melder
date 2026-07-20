from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SystemState(Enum):
    """
    High-level runtime posture for a spellbook/system.

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
    """
    __melder_internal__ = _mrg.sentinel
    automatic = auto()
    dynamic = auto()

"""
Singleton guard for blocking registration of Melder internals.

This lives at the top level so it can be imported everywhere without
pulling additional dependencies or risking cycles.
"""
import threading
from typing import Any
from typing import Optional

from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


class MelderRegistrationGuard:
    """
    Singleton guard that classifies candidates as internal and blocks registration attempts.

    Purpose
    -------
    This guard is the single gatekeeper for preventing Melder's own kernel/control-plane
    objects from being registered as spells. It is intentionally minimal, deterministic,
    and fast. Enforcement is driven by a single sentinel tag on any object or class:
        __melder_internal__ is guard.sentinel

    Design
    ------
    * Sentinel-based: Uses an identity-checked sentinel; no reflection or deep inspection.
    * Singleton: One instance per interpreter; created eagerly and exposed as
      __melder_registration_guard__.
    * Non-invasive: Does not alter inheritance hierarchies or require base-class coupling.

    Usage
    -----
    - Tag a class or object:
        SomeClass.__melder_internal__ = __melder_registration_guard__.sentinel
    - Enforce at registration:
        __melder_registration_guard__.assert_allowed(candidate, context="bind")

    Behavior
    --------
    - If the sentinel tag is present, registration is blocked with InternalRegistrationError.
    - If absent, the guard allows the candidate (no module-prefix backstop is used).

    Threading:
        Singleton construction is guarded by a class-level lock, which matters
        under free-threaded 3.14t where several threads may race on first
        access. Enforcement itself is lock-free: it is a single identity
        comparison on a sentinel, so it adds no contention to the bind path.

    Registration:
        THE GUARD ITSELF IS DELIBERATELY UNGUARDED - it carries no
        `__melder_internal__` sentinel. Tagging it would be circular, and it is
        not a runtime participant that anyone would plausibly bind.

    Subsystem Context:
        The single gatekeeper referenced by every guarded class in `src/melder`
        via `_mrg.sentinel`. It lives at the TOP LEVEL specifically so it can be
        imported from anywhere without pulling dependencies or creating import
        cycles - a guard that could not be imported early would be useless to
        the kernel objects that need it most.

    System Context:
        THE MRO LAW is the single most important consequence of this design, and
        it is not obvious from the code. `is_internal` reads the sentinel with
        `getattr(candidate, "__melder_internal__", None)`, and Python attribute
        lookup WALKS THE MRO. Tagging a base class therefore tags every subclass
        - INCLUDING classes a USER writes. A sentinel on a user-extensible base
        silently makes user subclasses unbindable.
        The resulting classification rule has three categories, and every guard
        decision in this library states which one it is:
          - BASE CLASS with user-extensible subclasses: NEVER guard
            (`Cleanable`, `Sync`, `AbstractElasticPool`, `CrystalFactStrategy`,
            `SourceCustodyStrategy`).
          - USER-BINDABLE: not guarded, because users legitimately bind it.
          - MELDER KERNEL: guarded.
        A guarded base whose subclasses are ALL melder-internal is redundant but
        NOT defective - the inherited sentinel can never reach user code. That
        distinction is settled by the INJECTION-SEAM TEST: a guarded base is a
        defect only where a user injection seam exists (a `strategies=` kwarg, a
        factory hook). `Meld`, `Creations`, `RiftSpace`, `CommandSystem`, and
        `FrameViewer` all pass that test and correctly stay guarded.
        GUARDING AND EXPORTING ARE ORTHOGONAL. `SafeGuard` is guarded AND
        exported: a user calls it directly but must never `bind()` it. The
        sentinel restricts REGISTRATION, never USE - which is why user-facing
        enums like `Policies`, `Permissions`, and `Existence` are guarded while
        being passed by value constantly.
        The deliberate absence of a module-prefix backstop is a correctness
        choice: prefix matching would guess at intent from naming, and this
        guard is built to be deterministic rather than clever.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. The registration gatekeeper. Tag internals with `__melder_internal__ = "
        "guard.sentinel`; bind paths call assert_allowed(...). CRITICAL: the sentinel resolves "
        "through the MRO, so tagging a user-extensible base makes every user subclass unbindable."
    )

    __slots__ = ("_sentinel",)
    _SENTINEL = object()
    _CONSTRUCTION_LOCK = threading.Lock()
    _instance: Optional["MelderRegistrationGuard"] = None

    def __new__(cls) -> "MelderRegistrationGuard":
        """
        Return the singleton instance, creating it on first access.

        Threading / Concurrency:
            Singleton construction is guarded by a class-level lock so first access
            remains safe under free-threading runtimes where multiple threads may
            attempt construction concurrently.
        """
        instance = cls._instance
        if instance is None:
            with cls._CONSTRUCTION_LOCK:
                instance = cls._instance
                if instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return instance

    def __init__(self) -> None:
        """
        Idempotent initializer; sets the process-wide sentinel.

        Returns:
            None.
        """
        self._sentinel = self._SENTINEL

    @property
    def sentinel(self) -> object:
        """
        Returns the shared sentinel used to tag internal objects/classes.

        Returns:
            object: The process-wide sentinel. Assign it to `__melder_internal__`
                on a class to mark it unbindable.
        """
        return self._sentinel

    def is_internal(self, candidate: Any) -> bool:
        """
        Lightweight check: returns True if the candidate carries the sentinel tag.

        Returns:
            bool: True when the candidate carries the sentinel. Remember the lookup
                walks the MRO, so a tagged base makes every subclass report True.

        Args:
            candidate:
                The class or object being considered for registration.
        """
        return getattr(candidate, "__melder_internal__", None) is self._sentinel

    def assert_allowed(self, candidate: Any, *, context: str = "bind") -> None:
        """
        Raise InternalRegistrationError if the candidate is tagged as internal.

        Args:
            candidate: The object/class/function being considered for registration.
            context:   Optional string describing the call site (e.g., "bind").

        Returns:
            None.
        """
        if getattr(candidate, "__melder_internal__", None) is self._sentinel:
            typename = getattr(candidate, "__name__", type(candidate).__name__)
            module_name = getattr(candidate, "__module__", "") or ""
            raise InternalRegistrationError(
                f"Registration blocked for Melder internal object "
                f"(type={typename}, module='{module_name}', context='{context}'). "
                f"Melder kernel/control-plane objects cannot be registered as spells."
            )


# Eager singleton instance; exposed under a dunder name to discourage mutation.
__melder_registration_guard__ = MelderRegistrationGuard()

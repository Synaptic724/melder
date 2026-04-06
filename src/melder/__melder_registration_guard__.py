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
    """

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
        """
        self._sentinel = self._SENTINEL

    @property
    def sentinel(self) -> object:
        """
        Returns the shared sentinel used to tag internal objects/classes.
        """
        return self._sentinel

    def is_internal(self, candidate: Any) -> bool:
        """
        Lightweight check: returns True if the candidate carries the sentinel tag.
        """
        return getattr(candidate, "__melder_internal__", None) is self._sentinel

    def assert_allowed(self, candidate: Any, *, context: str = "bind") -> None:
        """
        Raise InternalRegistrationError if the candidate is tagged as internal.

        Args:
            candidate: The object/class/function being considered for registration.
            context:   Optional string describing the call site (e.g., "bind").
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

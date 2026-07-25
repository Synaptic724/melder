"""
Singleton guard for blocking registration of Melder internals.

This lives at the top level so it can be imported everywhere without
pulling additional dependencies or risking cycles.
"""
import threading
from typing import Any
from typing import Optional

from melder.__melder_cache__.__init_cache__.manifest_loader import INTERNAL_MANIFEST
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


class MelderRegistrationGuard:
    """
    Singleton guard that classifies candidates as internal and blocks registration attempts.

    Purpose
    -------
    This guard is the single gatekeeper preventing Melder's own kernel and
    control-plane objects from being registered as spells. It is intentionally
    minimal, deterministic, and fast. Enforcement is one membership test against
    a generated manifest of `(module, qualname)` pairs.

    Design
    ------
    * Manifest-based: a build-time artifact enumerates every internal class as
      strings. No reflection, no attribute stamping, no per-class runtime cost.
    * Singleton: one instance per interpreter, exposed as
      `__melder_registration_guard__`.
    * Non-invasive: alters no inheritance hierarchy and requires no base-class
      coupling. Internal classes carry nothing; the manifest knows them.

    Usage
    -----
    - Enforce at registration:
        __melder_registration_guard__.assert_allowed(candidate, context="bind")
    - Internals need NO annotation. Membership is derived from source by
      `melder.__melder_cache__.__init_cache__._builder`; adding a class to the package is
      sufficient to guard it.

    Behavior
    --------
    - If the candidate's `(module, qualname)` is in the manifest, registration is
      blocked with `InternalRegistrationError`.
    - Instances resolve through `type(candidate)`, so binding an instance of an
      internal class is refused exactly like binding the class.

    Threading:
        Singleton construction is guarded by a class-level lock, which matters
        under free-threaded 3.14t where several threads may race on first
        access. Enforcement itself is lock-free - a frozenset membership test on
        an immutable, module-level object - so it adds no contention to bind.

    Registration:
        THE GUARD ITSELF IS DELIBERATELY EXCLUDED from enforcement concerns: it
        is not a runtime participant anyone would plausibly bind.

    Subsystem Context:
        Lives at the TOP LEVEL so it can be imported from anywhere without
        pulling dependencies or creating import cycles. Its one dependency,
        `melder.__melder_cache__.__init_cache__.manifest_loader`, is a leaf that imports only the
        version string and its own builder - never the runtime it describes.

    System Context:
        EXACT MATCH, NO INHERITANCE - the single most important property of this
        design, and the reason it replaced the previous sentinel.

        The retired mechanism stamped `__melder_internal__` onto each internal
        class and read it with `getattr`, which WALKS THE MRO. Tagging a base
        therefore tagged every subclass, including classes a USER writes, so a
        sentinel on any user-extensible base silently made user subclasses
        unbindable. That forced a hand-curated three-way classification across
        329 files, where a single missed stamp produced a bindable internal.

        Manifest lookup is a tuple comparison and does not inherit. Listing
        `Cleanable` blocks `Cleanable` itself; a user subclass carries its own
        module and qualname, is absent from the manifest, and binds normally.
        That is what permits the current blanket rule - EVERY class in the
        package is guarded, with no exclusions and no classification burden.

        ACCEPTED BEHAVIOR CHANGE (owner ruling 2026-07-24): user subclasses of
        internal classes are now BINDABLE. Under the sentinel they were refused
        via inherited tagging. This is deliberate, not a regression.

        GUARDING AND EXPORTING REMAIN ORTHOGONAL. `SafeGuard`, the custom
        exceptions, and `ProtocolCrafter` are exported and importable while
        being unbindable: the guard restricts REGISTRATION, never USE. That is
        why user-facing enums like `Policies`, `Permissions`, and `Existence`
        are guarded while being passed by value constantly.

        The manifest is derived from source rather than guessed from module
        prefixes: a name-prefix backstop would infer intent from naming, and
        this guard is built to be deterministic rather than clever.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. The registration gatekeeper. Internals need NO annotation - the "
        "generated manifest in melder.__melder_cache__ enumerates them; bind paths call "
        "assert_allowed(...). CRITICAL: lookup is EXACT (module, qualname) and does NOT "
        "inherit, so user subclasses of internal classes are bindable by design."
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

    @staticmethod
    def _identity_of(candidate: Any) -> tuple[str, str]:
        """
        Resolve the `(module, qualname)` identity used for manifest lookup.

        Contract:
            Classes answer for themselves; instances answer for their type, so
            binding an instance of an internal class is refused the same as
            binding the class. Missing attributes degrade to empty strings,
            which simply miss the manifest rather than raising.

        Args:
            candidate: The class or object being considered for registration.

        Returns:
            tuple[str, str]: The candidate's module and qualname.
        """
        target = candidate if isinstance(candidate, type) else type(candidate)
        module_name = getattr(target, "__module__", "") or ""
        qualname = getattr(target, "__qualname__", "") or ""
        return module_name, qualname

    def is_internal(self, candidate: Any) -> bool:
        """
        Return True if the candidate is a Melder-internal class.

        Contract:
            EXACT-MATCH lookup against the generated manifest. Unlike the retired
            sentinel, this does NOT inherit: a user subclass of an internal class
            carries its own module/qualname, is absent from the manifest, and is
            therefore bindable.

        Returns:
            bool: True when the candidate's identity is in the manifest.

        Args:
            candidate:
                The class or object being considered for registration.
        """
        return self._identity_of(candidate) in INTERNAL_MANIFEST

    def assert_allowed(self, candidate: Any, *, context: str = "bind") -> None:
        """
        Raise InternalRegistrationError if the candidate is a Melder internal.

        Args:
            candidate: The object/class/function being considered for registration.
            context:   Optional string describing the call site (e.g., "bind").

        Returns:
            None.

        Raises:
            InternalRegistrationError: When the candidate resolves to an entry in
                the generated internal manifest.
        """
        module_name, qualname = self._identity_of(candidate)
        if (module_name, qualname) in INTERNAL_MANIFEST:
            raise InternalRegistrationError(
                f"Registration blocked for Melder internal object "
                f"(type={qualname}, module='{module_name}', context='{context}'). "
                f"Melder kernel/control-plane objects cannot be registered as spells."
            )


# Eager singleton instance; exposed under a dunder name to discourage mutation.
__melder_registration_guard__ = MelderRegistrationGuard()

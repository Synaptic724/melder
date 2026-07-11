import threading
from typing import Any, Callable, ClassVar, Dict, Iterator, List, Optional, Tuple, Type


from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.helpers.ulid_factory import new_ulid

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.spellbook_crystal import SpellbookCrystal


class SpellbookConfiguration(Cleanable):
    """
    Mutable build-time configuration surface for one spellbook/runtime context.

    `SpellbookConfiguration` is the central staging object for one Spellbook's
    rich local runtime behaviour. It owns the typed property map, idempotent
    keys, and the per-spellbook system hook registry that later runtime systems
    consume.

    It governs:
    * local Spellbook/runtime behaviour
    * disposal and phase-scheduler tuning
    * hook registration for Meld / Conduit / Link / Contract events

    Contract:
    - Properties are mutable only until the configuration is frozen.
    - Idempotent keys may be set once and then become immutable even before
      freeze.
    - Validation is explicit and freeze/finalize enforce it.
    - Thread-safe operations are serialized with the instance `RLock`.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_aether_frame",
        "_frozen",
        "_properties",
        "available_properties",
        "_idempotent_keys",
        "_conduit_hooks",
        "_meld_hooks",
    ]
    _ALLOWED_HOOKS: ClassVar[Tuple[str, ...]] = (
        # Meld pipeline hooks
        "on_meld_pre_resolve",
        "on_meld_post_resolve",

        # Conduit lifecycle hooks
        "on_conduit_pre_created",
        "on_conduit_post_created",
        "on_conduit_activated",
        "on_conduit_cleanup_start",
        "on_conduit_cleanup_complete",

        # Linking hooks
        "on_conduit_post_link",
        "on_conduit_post_unlink",

        # Contract hooks
        "on_contract_created",
        "on_contract_removed",
    )
    _CONDUIT_HOOK_NAMES: ClassVar[Tuple[str, ...]] = (
        "on_conduit_pre_created",
        "on_conduit_post_created",
        "on_conduit_activated",
        "on_conduit_cleanup_start",
        "on_conduit_cleanup_complete",
        "on_conduit_post_link",
        "on_conduit_post_unlink",
        "on_contract_created",
        "on_contract_removed",
    )
    _MELD_HOOK_NAMES: ClassVar[Tuple[str, ...]] = (
        "on_meld_pre_resolve",
        "on_meld_post_resolve",
    )
    def __init__(self, aether_frame: str = "default"):
        """
        Initialize one configuration manager.

        Args:
            aether_frame (str): The name of the Aether frame this configuration is associated with (defaults to "default").
        Contract:
            - Starts unfrozen and empty.
            - Seeds the allowed property/type map and idempotent-key set.
            - Starts with an empty per-spellbook hook registry.
        """
        # Thread-safe lock for concurrent access
        super().__init__()
        self._id = new_ulid()
        self._lock = threading.RLock()
        self._aether_frame: str = aether_frame
        self._frozen = False

        # Private dictionary storing all properties.
        self._properties: Dict = {}
        self.available_properties: Dict[str, Type] = {
            "disposal": bool,
            "disposal_method_names": list,
            "phase_scheduler_workers_per_spellbook": int,
            "phase_scheduler_barrier_timeout_milliseconds": int,
            # Patch lane generalized_singleton_specialization_2026_07_01:
            # opt-in warm-tail singleton specialization for the generalized
            # no-overrides lane. Read ONCE at hydration time, never per meld.
            "generalized_singleton_specialization_enabled": bool,
        }

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"disposal", "disposal_method_names"}

        # System hook registry (Meld / Conduit / Link / Contract).
        # Maps hook name -> list[Callable[..., Any]].
        #
        # This is per-SpellbookConfiguration and is intended to be wired into:
        #   - Meld pipeline (on_meld_pre_resolve / on_meld_post_resolve)
        #   - Conduit lifecycle (pre/post created, activated, cleanup start/complete)
        #   - Linking (on_conduit_post_link / on_conduit_post_unlink)
        #   - Contract events (on_contract_created / on_contract_removed)
        self._conduit_hooks: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
        self._meld_hooks: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}

    def cleanup(self) -> None:
        """
        Finalize the configuration and drop all owned registries.

        This method sets both the `cleaned` and `frozen` flags.

        Contract:
            - Idempotent and lock-guarded.
            - Clears property/type maps and hook registries.
            - Prevents any future mutation or validation calls through
              `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration is already cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True

            if self._properties is not None:
                self._properties.clear()
            del self._properties

            if self.available_properties is not None:
                self.available_properties.clear()
            del self.available_properties

            if self._conduit_hooks is not None:
                self._conduit_hooks.clear()
            if self._meld_hooks is not None:
                self._meld_hooks.clear()
            del self._conduit_hooks
            del self._meld_hooks

    def set_property(self, key: str, value: Any) -> None:
        """
        Defines or overwrites a property in the configuration.

        - **Idempotent properties** (e.g., 'system_state') can only be set *once* before the configuration is cleaned.
        - **Non-idempotent properties** can be freely modified before the configuration is frozen.

        Args:
            key (str): The name of the property to set.
            value (Any): The value of the property.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            RuntimeError: If attempting to modify an idempotent property that is already set.
            TypeError: If `key` is not a string.
            ValueError: If local value validation fails.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify configuration after it is frozen.")

        if not isinstance(key, str):
            raise TypeError("Key must be a string.")
        if key not in self.available_properties:
            raise KeyError(f"Unknown SpellbookConfiguration property: '{key}'.")

        with self._lock:
            if key in self._idempotent_keys and key in self._properties:
                raise RuntimeError(f"Cannot modify idempotent property '{key}' once set.")

            if self._frozen:
                raise RuntimeError("Cannot modify configuration after it is frozen.")

            self._properties[key] = value

    def clear_properties(self) -> None:
        """
        Clears all properties in the configuration.

        This method is useful for resetting the configuration to its initial state before it is frozen.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot clear properties after configuration is frozen")
            self._properties.clear()

    def freeze(
            self,
            origin_spellbook_id: Optional[str] = None,
            origin_frame_name: Optional[str] = None,
            origin_dynamic: Optional[bool] = None,
    ) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Contract:
            - Freezing is this configuration's true activation, so it is
              the emission factor for the spellbook twin: when origin
              identity is supplied, the world is dynamic, and the
              crystallizer records, the twin spawns into the active
              persistence profile.
            - Standalone freezes (user finalize()/build() before any
              Spellbook adoption) carry no origin identity and emit
              nothing; the owning spellbook's conjure-time freeze supplies
              identity.

        Args:
            origin_spellbook_id:
                Owning spellbook identity, supplied by the spellbook's
                conjure-time freeze path; None for standalone freezes.
            origin_frame_name:
                Owning frame name (the twin's parent edge).
            origin_dynamic:
                Conjure-time dynamic posture; the twin emits only when
                True (the recorded lane).

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        self.check_cleaned()
        if self._frozen:
            # Origin-carrying re-freeze (the spellbook's conjure path): the
            # dynamic-mode bind guard requires user configurations to be
            # finalized BEFORE the first bind, so every legal recorded-lane
            # configuration arrives here already frozen. The freeze
            # transition itself is a no-op, but the twin emission must
            # still fire or recorded worlds never carry their spellbooks
            # (restore_engine_2026_07_07 round-trip finding).
            self._emit_spellbook_twin_when_recording(
                origin_spellbook_id, origin_frame_name, origin_dynamic
            )
            return
        if not self.validate():
            raise ValueError("SpellbookConfiguration validation failed. Cannot freeze.")
        with self._lock:
            self._frozen = True
        self._emit_spellbook_twin_when_recording(
            origin_spellbook_id, origin_frame_name, origin_dynamic
        )

    def _emit_spellbook_twin_when_recording(
            self,
            origin_spellbook_id: Optional[str],
            origin_frame_name: Optional[str],
            origin_dynamic: Optional[bool],
    ) -> None:
        """
        Emit the spellbook twin when a freeze carries origin identity.

        Purpose:
            Configuration activation is the emission factor for the
            spellbook twin. Both freeze paths route here: the fresh freeze
            (conjure froze an unfrozen configuration) AND the origin-
            carrying re-freeze of a configuration the user legally
            finalized standalone before binds.

        Contract:
            - NO-OP without full origin identity or when the conjure
              posture is not dynamic (standalone finalize()/build() calls
              emit nothing; automatic-mode worlds are never recorded).
            - NO-OP before the crystallizer singleton boots or while it is
              not activated.
            - The payload carries plain values only: scalars pass through,
              collections stringify per element, everything else
              stringifies whole (lossy values surface as restore
              shortfalls, never as record corruption).

        Args:
            origin_spellbook_id:
                Owning spellbook identity; None for standalone freezes.
            origin_frame_name:
                Owning frame name (the twin's parent edge).
            origin_dynamic:
                Conjure-time dynamic posture; emission requires True.

        Returns:
            None.
        """
        if (
                origin_spellbook_id is not None
                and origin_frame_name is not None
                and origin_dynamic is True
        ):
        # Configuration activation is the emission factor: pull the
        # crystallizer singleton directly (guarding the pre-boot case,
        # where the singleton is not yet initialized and construction
        # requires the hosting Aether), emit when recording, then drop
        # the local handle.
            if Crystallizer._initialized:
                crystallizer = Crystallizer()
                if crystallizer.activated:
                    configuration_payload: Dict[str, object] = {}
                    for property_name, property_value in self._properties.items():
                        if (
                                isinstance(property_value, (str, int, float, bool))
                                or property_value is None
                        ):
                            configuration_payload[property_name] = property_value
                        elif isinstance(property_value, (list, tuple, set, frozenset)):
                            configuration_payload[property_name] = [
                                str(item) for item in property_value
                            ]
                        else:
                            configuration_payload[property_name] = str(property_value)
                    hook_names: List[str] = []
                    for hook_name in self._conduit_hooks.get(origin_spellbook_id, {}).keys():
                        hook_names.append("conduit:{0}".format(hook_name))
                    for hook_name in self._meld_hooks.get(origin_spellbook_id, {}).keys():
                        hook_names.append("meld:{0}".format(hook_name))
                    crystallizer.emit(
                        SpellbookCrystal(
                            spellbook_id=origin_spellbook_id,
                            frame_name=origin_frame_name,
                            configuration_payload=configuration_payload,
                            hook_names=hook_names,
                        )
                    )
                del crystallizer

    def validate(self) -> bool:
        """
        Validates that all configuration properties are present, correctly typed,
        and semantically valid.

        The validation pipeline is intentionally decomposed into small, focused
        helper methods to avoid an overly long and unmaintainable validate() method.
        """
        self.check_cleaned()

        self._validate_required_properties_exist()
        self._validate_required_property_types()
        self._validate_phase_scheduler_workers()

        return True

    # Opt-in properties: registered in `available_properties` so
    # `set_property` accepts and type-checks them, but NEVER hard-required.
    # Validation backfills the documented default when unset so defaults-free
    # fluent configurations (a supported public path) remain valid without
    # knowing about optional optimization flags.
    _OPTIONAL_PROPERTY_DEFAULTS: ClassVar[Dict[str, Any]] = {
        "generalized_singleton_specialization_enabled": False,
    }

    def _validate_required_properties_exist(self) -> None:
        """
        Ensures that all properties listed in `available_properties` are present.

        Contract:
            - Opt-in properties listed in `_OPTIONAL_PROPERTY_DEFAULTS` are
              backfilled with their documented defaults instead of raising, so
              configurations assembled without `load_default_dictionary()`
              never fail validation over optional optimization flags.
            - Every other registered property remains hard-required.
        """
        for key, default_value in self._OPTIONAL_PROPERTY_DEFAULTS.items():
            if key not in self._properties:
                self._properties[key] = default_value
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")

    def _validate_required_property_types(self) -> None:
        """
        Performs generic type checking using `available_properties`.
        """
        for key, expected_type in self.available_properties.items():
            value = self._properties[key]

            # Normalize to tuple
            expected_types: tuple[Type[Any], ...]
            if isinstance(expected_type, tuple):
                expected_types = expected_type
            else:
                expected_types = (expected_type,)

            if not isinstance(value, expected_types):
                expected_names = ", ".join(t.__name__ for t in expected_types)
                raise ValueError(
                    f"Invalid type for property '{key}': "
                    f"expected {expected_names}, got {type(value).__name__}."
                )

    def _validate_phase_scheduler_workers(self) -> None:
        """
        Ensures the phase scheduler worker count is a valid integer >= 1.
        """
        workers = self._properties.get("phase_scheduler_workers_per_spellbook")

        if not isinstance(workers, int) or workers < 1:
            raise ValueError("phase_scheduler_workers must be a positive integer >= 1.")

    def validate_enums(self) -> bool:
        """
        Local rich configuration no longer owns enum-backed frame posture
        properties, so enum validation is a no-op.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If a known enum property is set to an invalid type.
        """
        self.check_cleaned()
        return True

    def get_property(self, key: str) -> Any:
        """
        Return one configuration property value.

        Args:
            key (str): The name of the property.

        Returns:
            Any: The stored value (str, int, bool, Enum, etc.).

        Raises:
            RuntimeError: If the configuration is cleaned.
            KeyError: If the property does not exist in the configuration.

        Contract:
            - Returns the stored live value for the key.
            - Raises instead of silently defaulting when the key is missing.
        """
        self.check_cleaned()
        try:
            return self._properties[key]
        except KeyError:
            raise KeyError(f"Property '{key}' not found in Aether properties.")

    def has_property(self, key: str) -> bool:
        """
        Return whether a configuration property is currently defined.

        Args:
            key (str): The property name to check.

        Returns:
            bool: True if the property exists, False otherwise.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        return key in self._properties

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over configuration property keys.

        Returns:
            Iterator: Property names (keys) in the configuration.

        Contract:
            - Iterates the live property mapping.
            - Intended for build-time inspection/serialization, not stable
              snapshot semantics.
        """
        return iter(self._properties)

    def load_default_dictionary(self) -> None:
        """
        Load the standard default property set.

        This method sets sensible defaults for local rich-config properties.

        Contract:
            - Populates only missing local rich-config properties; existing
              explicit values are preserved.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        defaults = {
            "disposal": False,
            "disposal_method_names": [],
            "phase_scheduler_workers_per_spellbook": 5,
            "phase_scheduler_barrier_timeout_milliseconds": 60000,
            "generalized_singleton_specialization_enabled": False,
        }
        for key, value in defaults.items():
            if key not in self._properties:
                self._properties[key] = value

    def load_recorded_dictionary(
            self,
            recorded_properties: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """
        Reload lane: apply one RECORDED property payload as configuration
        truth.

        Purpose:
            The restore/reload counterpart to `load_default_dictionary`.
            A sealed world must rebuild from its recorded values - never
            from present-day defaults, which drift - so this verb applies
            the recorded payload first and backfills ONLY required keys the
            record does not carry, reporting every deviation to the caller.

        Contract:
            - Recorded values win: each recorded key routes through
              `set_property` (full registration + type checking applies).
            - A recorded value the property system refuses (unknown key,
              or type drift such as callables the emission scalar filter
              stringified) is skipped and returned under "rejected" as
              "key: reason"; nothing is silently coerced. The per-key
              exception capture is documented best-effort collection, not
              error swallowing - every refusal is surfaced to the caller.
            - Required keys absent from the record backfill through
              `load_default_dictionary` (populate-missing-only semantics)
              and each backfilled key is returned under "backfilled";
              nothing backfills silently.
            - LOADS AND FREEZES in one motion: a reloaded configuration is
              sealed truth, so the verb validates and freezes internally
              before returning - callers never finalize a reload. The
              standalone freeze carries no origin identity (no twin
              emission); the owning spellbook's conjure-time freeze
              re-enters with identity and emits.

        Args:
            recorded_properties:
                Property name -> recorded value mapping (one sealed,
                JSON-safe configuration_payload - the cached-item shape).

        Returns:
            Dict[str, List[str]]:
                {"rejected": ["key: reason", ...] for refused recorded
                 values, "backfilled": [key, ...] for schema-default
                 fills}.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If the reloaded property set fails validation at
                the internal freeze.
        """
        self.check_cleaned()
        rejected: List[str] = []
        for key, value in dict(recorded_properties).items():
            try:
                self.set_property(key, value)
            except Exception as error:
                # Best-effort collection by contract: the refusal reason
                # rides back to the caller for shortfall reporting.
                rejected.append("{0}: {1}".format(key, error))
        present_before = set(self._properties.keys())
        self.load_default_dictionary()
        backfilled = sorted(set(self._properties.keys()) - present_before)
        # Reload seals: load it in, freeze it - the reload lane never
        # hands back a mutable configuration.
        self.freeze()
        return {"rejected": rejected, "backfilled": backfilled}

    # ------------------------------------------------------------------
    # System hook API (Meld / Conduit / Link / Contract) Ã¢â‚¬â€œ normal style
    # ------------------------------------------------------------------

    def add_hook(self, spellbook_id: str, hook_name: str, hook: Callable[..., Any]) -> None:
        """
        Register a single system hook under this configuration for a specific Spellbook.

        The registry is keyed as:

            _hooks[spellbook_id][hook_name] -> list[callables]

        Covered hook categories:
            * Meld pipeline hooks:
                - "on_meld_pre_resolve"
                - "on_meld_post_resolve"
            * Conduit lifecycle hooks:
                - "on_conduit_pre_created"
                - "on_conduit_post_created"
                - "on_conduit_activated"
                - "on_conduit_cleanup_start"
                - "on_conduit_cleanup_complete"
            * Linking hooks:
                - "on_conduit_post_link"
                - "on_conduit_post_unlink"
            * Contract hooks:
                - "on_contract_created"
                - "on_contract_removed"

        Args:
            spellbook_id (str):
                The ID of the Spellbook these hooks belong to. This allows
                dynamic environments to register hooks per-Spellbook and later
                pull the appropriate hook sets when instantiating Conduits.
            hook_name (str):
                The canonical hook name to register. Must be one of: attr:`_ALLOWED_HOOKS`.
            hook (Callable[..., Any]):
                A callable to be invoked when the corresponding hook event fires.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            ValueError: If `hook_name` is unknown.
            TypeError: If `hook` is not callable.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify hooks after configuration is frozen.")

        if hook_name not in self._ALLOWED_HOOKS:
            raise ValueError(f"Unknown hook name: {hook_name!r}")

        if not callable(hook):
            raise TypeError("hook must be callable.")

        target_registry = (
            self._meld_hooks
            if hook_name in self._MELD_HOOK_NAMES
            else self._conduit_hooks
        )

        with self._lock:
            per_spellbook = target_registry.get(spellbook_id)
            if per_spellbook is None:
                per_spellbook = {}
                target_registry[spellbook_id] = per_spellbook

            hooks_list = per_spellbook.get(hook_name)
            if hooks_list is None:
                hooks_list = []
                per_spellbook[hook_name] = hooks_list

            hooks_list.append(hook)

    def add_hooks(self, spellbook_id: str, **hooks: Any) -> None:
        """
        Register multiple system hooks for a specific Spellbook in one call.

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        The internal registry shape is:

            _hooks[spellbook_id][hook_name] -> list[callables]

        Example:
            cfg.add_hooks("spellbook-123",
                on_meld_pre_resolve=trace_meld_enter,
                on_conduit_cleanup_complete=[cleanup_fn_1, cleanup_fn_2],
                on_contract_created=contract_observer,
            )

        Args:
            spellbook_id (str):
                The ID of the Spellbook these hooks belong to.
            **hooks:
                Mapping of hook name -> callable or iterable[callable].

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            ValueError: If any hook name is unknown.
            TypeError: If any value is not a callable or an iterable of callables.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify hooks after configuration is frozen.")

        for name, value in hooks.items():
            if name not in self._ALLOWED_HOOKS:
                raise ValueError(f"Unknown hook name: {name!r}")

            if value is None:
                continue

            if callable(value):
                self.add_hook(spellbook_id, name, value)
            else:
                try:
                    iterator = iter(value)
                except TypeError:
                    raise TypeError(
                        f"Value for hook '{name}' must be a callable or an iterable of callables."
                    )
                for fn in iterator:
                    if not callable(fn):
                        raise TypeError(
                            f"All entries for hook '{name}' must be callable."
                        )
                    self.add_hook(spellbook_id, name, fn)

    def get_conduit_hooks(self, spellbook_id: str) -> Dict[str, list[Callable[..., Any]]]:
        """
        Retrieve the live conduit hook map for a specific Spellbook.

        This returns the internal conduit hook map for `spellbook_id`.

        Shape:

            { hook_name: [callables...] }

        Args:
            spellbook_id (str):
                The ID of the Spellbook whose conduit hooks should be retrieved.

        Returns:
            Dict[str, list[Callable[..., Any]]]:
                Mapping of hook name -> list of callables currently registered
                for that Spellbook. Returns an empty dict if no conduit hooks exist.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._conduit_hooks is None:
                return {}
            per_spellbook = self._conduit_hooks.get(spellbook_id)
            if per_spellbook is None:
                return {}
            return per_spellbook

    def get_meld_hooks(self, spellbook_id: str) -> Dict[str, list[Callable[..., Any]]]:
        """
        Retrieve the live meld hook map for a specific Spellbook.

        This returns the internal meld hook map for `spellbook_id`.

        Args:
            spellbook_id (str):
                The ID of the Spellbook whose meld hooks should be retrieved.

        Returns:
            Dict[str, list[Callable[..., Any]]]:
                Mapping of hook name -> list of callables currently registered
                for that Spellbook. Returns an empty dict if no meld hooks exist.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._meld_hooks is None:
                return {}
            per_spellbook = self._meld_hooks.get(spellbook_id)
            if per_spellbook is None:
                return {}
            return per_spellbook

    def get_hooks(self, spellbook_id: str) -> Dict[str, list[Callable[..., Any]]]:
        """
        Retrieve a merged detached hook map for compatibility callers.

        Returns:
            Dict[str, list[Callable[..., Any]]]:
                Detached merged view of conduit and meld hooks.
        """
        self.check_cleaned()
        merged: Dict[str, list[Callable[..., Any]]] = {}
        with self._lock:
            conduit_hooks = self._conduit_hooks.get(spellbook_id)
            if conduit_hooks:
                for hook_name, hook_list in conduit_hooks.items():
                    merged[hook_name] = list(hook_list)
            meld_hooks = self._meld_hooks.get(spellbook_id)
            if meld_hooks:
                for hook_name, hook_list in meld_hooks.items():
                    merged[hook_name] = list(hook_list)
        return merged


    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------
    def with_phase_scheduler_workers(self, workers: int) -> "SpellbookConfiguration":
        """
        Set the number of worker threads used by the Resolution Phase Scheduler.
        Must be >= 1.

        Args:
            workers (int): Number of worker threads.

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Validates the worker count before writing it.
            - Mutates the live configuration and returns `self`.
        """
        if not isinstance(workers, int) or workers < 1:
            raise ValueError("phase_scheduler_workers must be a positive integer.")
        self.set_property("phase_scheduler_workers_per_spellbook", workers)
        return self


    def with_phase_scheduler_barrier_timeout(self, timeout_milliseconds: int) -> "SpellbookConfiguration":
        """
        Set the barrier timeout in milliseconds used by the Resolution Phase Scheduler.
        Must be >= 0.

        Args:
            timeout_milliseconds (int): Barrier timeout in milliseconds.

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Rejects zero and excessively large values up front.
            - Mutates the live configuration and returns `self`.
        """
        if not isinstance(timeout_milliseconds, int) or timeout_milliseconds < 0:
            raise ValueError("phase_scheduler_barrier_timeout_milliseconds must be a non-negative integer.")

        if timeout_milliseconds == 0:
            raise ValueError("phase_scheduler_barrier_timeout_milliseconds cannot be zero; use a positive integer.")

        if timeout_milliseconds > 300000:
            raise ValueError("phase_scheduler_barrier_timeout_milliseconds cannot exceed 300000 milliseconds (5 minutes).")

        self.set_property("phase_scheduler_barrier_timeout_milliseconds", timeout_milliseconds)
        return self

    def with_hook(self, spellbook_id: str, hook_name: str, hook: Callable[..., Any]) -> "SpellbookConfiguration":
        """
        Fluent

        Register a single system hook for a specific Spellbook and return "self".

        This is a fluent wrapper over: meth:`add_hook`, supporting all valid
        hook names defined in: attr:`_ALLOWED_HOOKS`.

        Example:
            (SpellbookConfiguration()
                .with_defaults()
                .with_hook("spellbook-123", "on_meld_pre_resolve", trace_meld_enter)
                .with_hook("spellbook-123", "on_conduit_cleanup_complete", cleanup_fn)
                .finalize())
        """
        self.add_hook(spellbook_id, hook_name, hook)
        return self

    def with_hooks(self, spellbook_id: str, **hooks: Any) -> "SpellbookConfiguration":
        """
        Fluent

        Register multiple system hooks for a specific Spellbook in one call
        and return "self".

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        Example:
            (SpellbookConfiguration()
                .with_defaults()
                .with_hooks("spellbook-123",
                    on_meld_pre_resolve=trace_meld_enter,
                    on_conduit_pre_created=log_conduit_construction,
                    on_contract_created=[observer_1, observer_2],
                )
                .finalize())
        """
        self.add_hooks(spellbook_id, **hooks)
        return self

    def with_defaults(self) -> "SpellbookConfiguration":
        """
        Fluent

        Load MelderÃ¢â‚¬â„¢s standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behaviour:
        - Sets local rich-config defaults:
          disposal=False, disposal_method_names=[].
        - Respects idempotency and immutability rules (raises if frozen or cleaned).

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).
        """
        self.load_default_dictionary()
        return self

    def with_disposal(self, enabled: bool = True) -> "SpellbookConfiguration":
        """
        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Writes only the `disposal` flag.
            - Returns `self` for chaining.
        """
        self.set_property("disposal", enabled)
        return self

    def with_disposal_method_names(self, names: list[str]) -> "SpellbookConfiguration":
        """
        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Replaces the entire disposal-method list.
            - Type-checks the container before writing it.
        """
        if not isinstance(names, list):
            raise TypeError("disposal_method_names must be a list[str].")
        self.set_property("disposal_method_names", names)
        return self

    def add_disposal_methods(self, *names: str) -> "SpellbookConfiguration":
        """
        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behaviour:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Initializes the disposal-method list when absent.
            - Preserves order while deduplicating names.
        """
        current = self._properties.get("disposal_method_names", [])
        if not isinstance(current, list):
            raise ValueError("Internal error: 'disposal_method_names' is not a list.")
        seen = set(current)
        extended: list[str] = list(current)
        for nm in names:
            if not isinstance(nm, str):
                raise TypeError("All disposal method names must be strings.")
            if nm not in seen:
                extended.append(nm)
                seen.add(nm)
        self.set_property("disposal_method_names", extended)
        return self

    def finalize(self) -> "SpellbookConfiguration":
        """
        Validate and freeze, returning `self`.

        Returns:
            SpellbookConfiguration: This same configuration instance (for chaining).

        Contract:
            - Runs the full validation pipeline.
            - Freezes the configuration on success.
            - Returns `self` for chaining.
        """
        self.freeze()
        return self

    def build(self) -> "SpellbookConfiguration":
        """
        Fluent alias for `finalize()`.

        Contract:
            - Performs the same validation-and-freeze behaviour as `finalize()`.
            - Returns `self` for chaining.
        """
        return self.finalize()



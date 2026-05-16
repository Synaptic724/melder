import threading
from enum import Enum
from typing import Any, Dict, Type, Callable, Optional
import ulid
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces import IConfiguration
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellbookConfiguration(Cleanable, IConfiguration):
    """
    Mutable build-time configuration surface for one spellbook/runtime context.

    `SpellbookConfiguration` is the central staging object where spellbook-wide runtime
    posture is assembled before conjure/freeze. It owns the typed property map,
    idempotent keys, and the per-spellbook system hook registry that later
    runtime systems consume.

    It governs:
    * conduit/runtime posture
    * dynamic/AI/Rift feature flags
    * disposal and phase-scheduler tuning
    * hook registration for Meld / Conduit / Link / Contract events

    Contract:
    - Properties are mutable only until the configuration is frozen.
    - Idempotent keys may be set once and then become immutable even before
      freeze.
    - Validation is explicit and freeze/finalize enforce it.
    - Thread-safe operations are serialized with the instance `RLock`.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_aether_frame",
        "_frozen",
        "_properties",
        "available_properties",
        "_idempotent_keys",
        "_hooks",
    ]
    _ALLOWED_HOOKS = (
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
        self._id = str(ulid.ULID())
        self._lock = threading.RLock()
        self._aether_frame: str = aether_frame
        self._frozen = False

        # Private dictionary storing all properties.
        self._properties: Dict = {}
        self.available_properties: Dict[str, Type] = {
            "system_state": SystemState,
            "disposal": bool,
            "disposal_method_names": list,
            "full_ahead_of_time_compilation": bool,
            "overrides_enabled": bool,
            "phase_scheduler_workers_per_spellbook": int,
            "ai_native_enabled": bool,
            "rift_enabled": bool,
            "phase_scheduler_barrier_timeout_milliseconds": int,
        }

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"system_state", "disposal", "disposal_method_names"}

        # System hook registry (Meld / Conduit / Link / Contract).
        # Maps hook name -> list[Callable[..., Any]].
        #
        # This is per-SpellbookConfiguration and is intended to be wired into:
        #   - Meld pipeline (on_meld_pre_resolve / on_meld_post_resolve)
        #   - Conduit lifecycle (pre/post created, activated, cleanup start/complete)
        #   - Linking (on_conduit_post_link / on_conduit_post_unlink)
        #   - Contract events (on_contract_created / on_contract_removed)
        self._hooks: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}

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
                self._properties = None

            if self.available_properties is not None:
                self.available_properties.clear()
                self.available_properties = None

            if self._hooks is not None:
                self._hooks.clear()
                self._hooks = None

    def set_property(self, key: str, value: Any) -> None:
        """
        Defines or overwrites a property in the configuration.

        - **Idempotent properties** (e.g., 'system_state') can only be set *once* before the configuration is cleaned.
        - **Non-idempotent properties** can be freely modified before the configuration is frozen.

        Args:
            key (str): The name of the property to set.
            value (Any): The value for the property.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            RuntimeError: If attempting to modify an idempotent property that is already set.
            TypeError: If `key` is not a string.
            ValueError: If an enum conversion fails.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify configuration after it is frozen.")

        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        with self._lock:
            if key in self._idempotent_keys and key in self._properties:
                raise RuntimeError(f"Cannot modify idempotent property '{key}' once set.")

            if self._frozen:
                raise RuntimeError("Cannot modify configuration after it is frozen.")

            value = self._convert_enum_if_needed(key, value)
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

    def freeze(self) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("SpellbookConfiguration validation failed. Cannot freeze.")
        with self._lock:
            self._frozen = True

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
        self._validate_enum_properties()
        self._validate_phase_scheduler_workers()
        self._validate_overrides_enabled()
        self._validate_ai_native_enabled()
        self._validate_rift_enabled()
        self._validate_ai_runtime_posture()

        return True

    def _validate_required_properties_exist(self) -> None:
        """
        Ensures that all properties listed in `available_properties` are present.
        """
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
            if not isinstance(expected_type, tuple):
                expected_type = (expected_type,)

            if not isinstance(value, expected_type):
                expected_names = ", ".join(t.__name__ for t in expected_type)
                raise ValueError(
                    f"Invalid type for property '{key}': "
                    f"expected {expected_names}, got {type(value).__name__}."
                )

    def _validate_enum_properties(self) -> None:
        """
        Ensures all enum-based properties contain valid enum values.
        """
        if "system_state" in self._properties:
            system_state = self._properties["system_state"]
            if not isinstance(system_state, SystemState):
                raise ValueError(
                    f"Invalid type for 'system_state': expected SystemState, got {type(system_state).__name__}."
                )

    def _validate_phase_scheduler_workers(self) -> None:
        """
        Ensures the phase scheduler worker count is a valid integer >= 1.
        """
        workers = self._properties.get("phase_scheduler_workers_per_spellbook")

        if not isinstance(workers, int) or workers < 1:
            raise ValueError("phase_scheduler_workers must be a positive integer >= 1.")

    def _validate_overrides_enabled(self) -> None:
        """
        Ensure overrides_enabled is a boolean.
        """
        enabled = self._properties.get("overrides_enabled")

        if not isinstance(enabled, bool):
            raise ValueError("overrides_enabled must be a boolean.")

    def _validate_ai_native_enabled(self) -> None:
        """
        Ensures ai_native_enabled is a boolean.
        """
        enabled = self._properties.get("ai_native_enabled")

        if not isinstance(enabled, bool):
            raise ValueError("ai_native_enabled must be a boolean.")

    def _validate_rift_enabled(self) -> None:
        """
        Ensures rift_enabled is a boolean.
        """
        enabled = self._properties.get("rift_enabled")

        if not isinstance(enabled, bool):
            raise ValueError("rift_enabled must be a boolean.")

    def _validate_ai_runtime_posture(self) -> None:
        """
        Enforce the semantic relationship between system state and AI posture.

        Contract:
            - `ai_native_enabled=True` requires `system_state == dynamic`.
            - `rift_enabled` remains valid in either automatic or
              dynamic mode.

        Raises:
            ValueError: If AI-native posture is enabled while the system state
                is not dynamic.
        """
        system_state = self._properties.get("system_state")
        ai_native_enabled = self._properties.get("ai_native_enabled")

        if ai_native_enabled and system_state != SystemState.dynamic:
            raise ValueError(
                "ai_native_enabled requires system_state to be dynamic."
            )

    def validate_enums(self) -> bool:
        """
        Validate enum-backed properties explicitly.

        This is a narrower compatibility helper kept alongside the broader
        `validate()` pipeline for callers that only want the enum-specific
        portion of validation.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If a known enum property is set to an invalid type.
        """
        self.check_cleaned()
        # Additional validation for specific properties
        if "system_state" in self._properties:
            system_state = self._properties["system_state"]
            if not isinstance(system_state, SystemState):
                raise ValueError(
                    f"Invalid type for 'system_state': expected SystemState, got {type(system_state).__name__}."
                )
        return True


    def _convert_enum_if_needed(self, key: str, value: Any) -> Any:
        """
        Converts string inputs into the correct enum types for known keys.

        Args:
            key (str): The property key.
            value (Any): The value to check/convert.

        Returns:
            Any: The converted Enum value or the original value if no conversion is needed.

        Raises:
            ValueError: If the string value is not a valid enum member or if the input type is incorrect.

        Contract:
            - Only keys listed in the local enum map are converted.
            - Unknown keys pass through untouched.
            - Known enum keys are normalized through the shared enum helper so
              strings and enum instances follow one validation path.
        """
        enum_map: Dict[str, Type[Enum]] = {
            "system_state": SystemState,
        }

        enum_type = enum_map.get(key)
        if enum_type is None:
            # No conversion rule for this key; keep the original value (per docstring).
            return value

        # Normalize via shared helper: accepts str|Enum, raises on None/invalid.
        return EnumHelpers.convert_enum_and_check(value, enum_type)

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

    def __iter__(self):
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

        This method sets sensible defaults for core properties like
        `system_state` and `disposal`.

        Contract:
            - Populates only missing properties; existing explicit values are
              preserved.
            - Seeds `system_state` through the same enum-conversion path used by
              normal property writes.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        defaults = {
            "disposal": False,
            "disposal_method_names": [],
            "full_ahead_of_time_compilation": True,
            "overrides_enabled": True,
            "phase_scheduler_workers_per_spellbook": 5,
            "ai_native_enabled": False,
            "rift_enabled": False,
            "phase_scheduler_barrier_timeout_milliseconds": 60000,
        }
        if "system_state" not in self._properties:
            defaults["system_state"] = self._convert_enum_if_needed("system_state", "automatic")
        for key, value in defaults.items():
            if key not in self._properties:
                self._properties[key] = value

    # ------------------------------------------------------------------
    # System hook API (Meld / Conduit / Link / Contract) â€“ normal style
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
                The canonical hook name to register. Must be one of
                :attr:`_ALLOWED_HOOKS`.
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

        with self._lock:
            per_spellbook = self._hooks.get(spellbook_id)
            if per_spellbook is None:
                per_spellbook = {}
                self._hooks[spellbook_id] = per_spellbook

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
            cfg.add_hooks(
                "spellbook-123",
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

    def get_hooks(self, spellbook_id: str) -> Dict[str, list[Callable[..., Any]]]:
        """
        Retrieve the live hook map for a specific Spellbook.

        This returns the internal hook map for ``spellbook_id`` so callers
        (e.g., Conduit / Meld wiring) can share a single hook registry.

        Shape:

            { hook_name: [callables...] }

        Args:
            spellbook_id (str):
                The ID of the Spellbook whose hooks should be retrieved.

        Returns:
            Dict[str, list[Callable[..., Any]]]:
                Mapping of hook name -> list of callables currently registered
                for that Spellbook. Returns an empty dict if no hooks exist yet.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._hooks is None:
                return {}

            per_spellbook = self._hooks.get(spellbook_id)
            if per_spellbook is None:
                per_spellbook = {}
                self._hooks[spellbook_id] = per_spellbook
            return per_spellbook


    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------
    def with_phase_scheduler_workers(self, workers: int) -> IConfiguration:
        """
        Set the number of worker threads used by the Resolution Phase Scheduler.
        Must be >= 1.

        Args:
            workers (int): Number of worker threads.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Validates the worker count before writing it.
            - Mutates the live configuration and returns `self`.
        """
        if not isinstance(workers, int) or workers < 1:
            raise ValueError("phase_scheduler_workers must be a positive integer.")
        self.set_property("phase_scheduler_workers_per_spellbook", workers)
        return self


    def with_phase_scheduler_barrier_timeout(self, timeout_milliseconds: int) -> IConfiguration:
        """
        Set the barrier timeout in milliseconds used by the Resolution Phase Scheduler.
        Must be >= 0.

        Args:
            timeout_milliseconds (int): Barrier timeout in milliseconds.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

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

    def with_ai_native(self, enabled: bool = True) -> IConfiguration:
        """
        Enable or disable AI-native resolution pipeline features.

        Args:
            enabled (bool): True to enable AI-native mode.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Writes only the `ai_native_enabled` flag.
            - Semantic compatibility with `system_state` is enforced later by
              validation/freeze, not here.
        """
        if not isinstance(enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        self.set_property("ai_native_enabled", enabled)
        return self

    def with_rift_enabled(self, enabled: bool = True) -> IConfiguration:
        """
        Enable or disable Rift-facing posture.

        Args:
            enabled (bool): True to enable Rift-facing posture.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Writes only the `rift_enabled` flag.
            - Returns `self` for chaining.
        """
        if not isinstance(enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        self.set_property("rift_enabled", enabled)
        return self

    def with_full_ahead_of_time_compilation(self, enabled: bool = True) -> IConfiguration:
        """
        Fluent

        Set whether spells should be fully ahead-of-time compiled at conjure.

        Semantics:
        - ``True``: Full AOT mode. Conjure/runtime behavior follows current eager
          compilation flow.
        - ``False``: JIT mode. Downstream runtime gates may defer selected
          resolution work until first runtime use.

        Args:
            enabled (bool): Desired compilation mode flag.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Raises:
            TypeError: If ``enabled`` is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("full_ahead_of_time_compilation must be a bool.")
        self.set_property("full_ahead_of_time_compilation", enabled)
        return self

    def with_overrides_enabled(self, enabled: bool = True) -> IConfiguration:
        """
        Fluent

        Set whether bound spells default to override-capable runtime posture.

        Semantics:
        - ``True`` keeps the current override-capable runtime behavior.
        - ``False`` means later runtime entrypoints should reject caller
          overrides and mutation overlays for spells using the default.

        Args:
            enabled (bool): Desired default override posture.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Raises:
            TypeError: If ``enabled`` is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("overrides_enabled must be a bool.")
        self.set_property("overrides_enabled", enabled)
        return self


    def with_hook(self, spellbook_id: str, hook_name: str, hook: Callable[..., Any]) -> IConfiguration:
        """
        Fluent

        Register a single system hook for a specific Spellbook and return ``self``.

        This is a fluent wrapper over :meth:`add_hook`, supporting all valid
        hook names defined in :attr:`_ALLOWED_HOOKS`.

        Example:
            (SpellbookConfiguration()
                .with_defaults()
                .with_hook("spellbook-123", "on_meld_pre_resolve", trace_meld_enter)
                .with_hook("spellbook-123", "on_conduit_cleanup_complete", cleanup_fn)
                .finalize())
        """
        self.add_hook(spellbook_id, hook_name, hook)
        return self

    def with_hooks(self, spellbook_id: str, **hooks: Any) -> IConfiguration:
        """
        Fluent

        Register multiple system hooks for a specific Spellbook in one call
        and return ``self``.

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        Example:
            (SpellbookConfiguration()
                .with_defaults()
                .with_hooks(
                    "spellbook-123",
                    on_meld_pre_resolve=trace_meld_enter,
                    on_conduit_pre_created=log_conduit_construction,
                    on_contract_created=[observer_1, observer_2],
                )
                .finalize())
        """
        self.add_hooks(spellbook_id, **hooks)
        return self

    def with_defaults(self) -> IConfiguration:
        """
        Fluent

        Load Melderâ€™s standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behavior:
        - Sets: system_state="automatic", disposal=False,
          disposal_method_names=[], full_ahead_of_time_compilation=True,
          overrides_enabled=True.
        - Respects idempotency and immutability rules (raises if frozen or cleaned).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.load_default_dictionary()
        return self

    def with_system_state(self, state: SystemState | str) -> IConfiguration:
        """
        Fluent

        Set the system state ("automatic" or "dynamic") and return `self`.

        Notes:
        - Accepts either SystemState or a case-insensitive string.
        - Idempotent: can be set only once before freeze; attempting to overwrite raises.

        Args:
            state: Desired system state (SystemState or "automatic"|"dynamic").

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.set_property("system_state", state)
        return self

    def with_disposal(self, enabled: bool = True) -> IConfiguration:
        """
        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Writes only the `disposal` flag.
            - Returns `self` for chaining.
        """
        self.set_property("disposal", enabled)
        return self

    def with_disposal_method_names(self, names: list[str]) -> IConfiguration:
        """
        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Replaces the entire disposal-method list.
            - Type-checks the container before writing it.
        """
        if not isinstance(names, list):
            raise TypeError("disposal_method_names must be a list[str].")
        self.set_property("disposal_method_names", names)
        return self

    def to_aetheric_frame_configuration(
            self,
            origin_spellbook_id: Optional[str] = None,
    ) -> AethericFrameConfiguration:
        """
        Build the narrow frame-level AR posture object from this configuration.

        Purpose:
            Project the full Spellbook configuration down to the narrow
            frame-level posture fields that later runtime surfaces may need,
            including the default override posture.

        Args:
            origin_spellbook_id:
                Spellbook id deriving the frame posture. May be None for
                out-of-band callers.

        Returns:
            AethericFrameConfiguration: Narrow frame-level posture object.

        Raises:
            KeyError: If any required posture field is missing.
            TypeError: If any posture field has the wrong type.
            ValueError: If `system_state` is not a valid `SystemState`.
        """
        self.check_cleaned()
        return AethericFrameConfiguration.from_spellbook_configuration(
            origin_spellbook_id=origin_spellbook_id,
            configuration=self,
        )

    def add_disposal_methods(self, *names: str) -> IConfiguration:
        """
        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behavior:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

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

    def finalize(self) -> IConfiguration:
        """
        Validate and freeze, returning `self`.

        Returns:
            IConfiguration: This same configuration instance (for chaining).

        Contract:
            - Runs the full validation pipeline.
            - Freezes the configuration on success.
            - Returns `self` for chaining.
        """
        self.freeze()
        return self

    def build(self) -> IConfiguration:
        """
        Fluent alias for `finalize()`.

        Contract:
            - Performs the same validation-and-freeze behavior as `finalize()`.
            - Returns `self` for chaining.
        """
        return self.finalize()

    def dynamic_defaults(self) -> IConfiguration:
        """
        Load defaults and force dynamic system posture.

        Contract:
            - Sets `system_state` to dynamic through the normal property path.
            - Then fills in any remaining defaults.
            - Returns `self` for chaining.
        """
        self.set_property("system_state", "dynamic")
        return self.with_defaults()

    def automatic_defaults(self) -> IConfiguration:
        """
        Load defaults and force automatic system posture.

        Contract:
            - Sets `system_state` to automatic through the normal property
              path.
            - Then fills in any remaining defaults.
            - Returns `self` for chaining.
        """
        self.set_property("system_state", "automatic")
        return self.with_defaults()

from typing import Any, Callable, Dict, Iterator, Protocol, Tuple, Type, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IConfiguration(ICleanable, Protocol):
    """
    Configuration governs the behavior of the entire system.

    It acts as the configuration core for:
    * **Conduit Management:** How Conduits handle service lifecycles.
    * **Dynamic Behavior:** Flags controlling dynamic linking, expansion, and policies.
    * **System Flags:** Global settings like resource disposal and runtime posture.

    This object should only be configured once and then frozen to prevent any further changes,
    enforcing idempotent laws across the system. Thread-safe operations are ensured with RLock.
    """

    # --- Attributes (surface expectations only) ---
    _frozen: bool
    available_properties: 'Dict[str, Type]'
    _aether_frame: str
    _id: str
    _ALLOWED_HOOKS: Tuple[str, ...]

    # --- Lifecycle ---

    def cleanup(self) -> None:
        """
        Cleans the configuration, preventing any further modifications and cleaning up resources.

        This method sets both the `cleaned` and `frozen` flags.
        """
        ...

    # --- Core property API ---

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
        ...

    def clear_properties(self) -> None:
        """
        Clears all properties in the configuration.

        This method is useful for resetting the configuration to its initial state before it is frozen.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
        """
        ...

    def freeze(self) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        ...

    def validate(self) -> bool:
        """
        Validates that all required configuration properties exist and match expected types.

        Performs both presence/type checks and enum-specific validation.

        Returns:
            bool: True if all validation checks pass.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If any property is missing or has the wrong type/value.
        """
        ...

    def validate_enums(self) -> bool:
        """
        Internal

        Validates that all properties intended to be Enums (like `SystemState`) are indeed set to a valid Enum instance.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If a known enum property is set to an invalid type.
        """
        ...

    def get_property(self, key: str) -> Any:
        """
        Retrieves the value of a configuration property.

        Args:
            key (str): The name of the property.

        Returns:
            Any: The stored value (str, int, bool, Enum, etc.).

        Raises:
            RuntimeError: If the configuration is cleaned.
            KeyError: If the property does not exist in the configuration.
        """
        ...

    def has_property(self, key: str) -> bool:
        """
        Checks if a configuration property is defined.

        Args:
            key (str): The property name to check.

        Returns:
            bool: True if the property exists, False otherwise.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        ...

    def __iter__(self) -> Iterator[str]:
        """
        Allows iteration over the configuration properties (keys).

        Returns:
            Iterator: Property names (keys) in the configuration.
        """
        ...

    def load_default_dictionary(self) -> None:
        """
        Loads and applies a default set of properties atomically.

        This method sets sensible defaults for core properties like `system_state` and `disposal`.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        ...

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
        ...
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
        ...

    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------
    def with_hook(self, spellbook_id: str, hook_name: str, hook: Callable[..., Any]) -> 'IConfiguration':
        """
        Fluent

        Register a single system hook for a specific Spellbook and return ``self``.

        This is a fluent wrapper over :meth:`add_hook`, supporting all valid
        hook names defined in :attr:`_ALLOWED_HOOKS`.

        Example:
            (Configuration()
                .with_defaults()
                .with_hook("spellbook-123", "on_meld_pre_resolve", trace_meld_enter)
                .with_hook("spellbook-123", "on_conduit_cleanup_complete", cleanup_fn)
                .finalize())
        """
        ...

    def with_hooks(self, spellbook_id: str, **hooks: Any) -> 'IConfiguration':
        """
        Fluent

        Register multiple system hooks for a specific Spellbook in one call
        and return ``self``.

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        Example:
            (Configuration()
                .with_defaults()
                .with_hooks(
                    "spellbook-123",
                    on_meld_pre_resolve=trace_meld_enter,
                    on_conduit_pre_created=log_conduit_construction,
                    on_contract_created=[observer_1, observer_2],
                )
                .finalize())
        """
        ...
    def with_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load Melder's standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behavior:
        - Sets local rich-config defaults only.
        - Respects idempotency and immutability rules (raises if frozen or cleaned).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal_method_names(self, names: list[str]) -> 'IConfiguration':
        """
        Fluent

        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def add_disposal_methods(self, *names: str) -> 'IConfiguration':
        """
        Fluent

        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behavior:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def finalize(self) -> 'IConfiguration':
        """
        Fluent

        Validate and freeze, returning `self`.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def build(self) -> 'IConfiguration':
        """
        Fluent alias for finalize().
        """
        ...


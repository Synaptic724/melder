from __future__ import annotations

from typing import Any, Optional, Callable
# Melder Imports
from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.interfaces import ISpellbook
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef


class SpellBinder(Cleanable):
    """
    A Fluent Interface for registering Spells into a `Spellbook`.

    The `SpellBinder` acts as a temporary configuration context. It allows you to
    chain methods to define the lifecycle, permissions, and hooks for a spell
    before committing it to the Spellbook via `finalize()`.

    **Core Responsibilities:**
    1.  **Fluent Configuration:** Accumulate binding parameters (e.g., `.as_unique_per_aetheric_frame()`, `.named()`).
    2.  **State Management:** Holds in-flight configuration for exactly one registration at a time.
    3.  **Safe Delegation:** Forwards the final configuration to `Spellbook.bind(...)` only when `finalize()` is called.

    **Usage Example:**
        ```python
        binder = spellbook.create_binder()

        # Complex registration with hooks and specific scoping
        binder.bind(MyDatabaseService) \\
              .as_unique_per_aetheric_frame() \\
              .named("primary_db") \\
              .under_spellframe(IDatabase) \\
              .with_pre_hook(connect_db) \\
              .finalize()
        ```

    **Note on Reusability:**
    A single `SpellBinder` instance can be reused for multiple registrations.
    Calling `finalize()` automatically clears the internal state, making the
    binder ready for the next `bind(...)` call.
    """

    __slots__ = (
        "_weak_spellbook",
        "_default_existence",
        "_default_permissions",
        "_spell",
        "_existence",
        "_permissions",
        "_spellframe",
        "_binding_name",
        "_kwargs",
    )

    def __init__(
            self,
            spellbook: ISpellbook,
            *,
            default_existence: Existence = Existence.unique_per_aetheric_frame,
            default_permissions: str = "create",
    ) -> None:
        """
        Initialize a new `SpellBinder` linked to a specific `Spellbook`.

        Args:
            spellbook (ISpellbook):
                The target Spellbook. The binder holds a weak reference to this
                book to prevent reference cycles.
            default_existence (Existence):
                The default lifecycle scope to use if one is not explicitly
                set during a chain. Defaults to `Existence.unique_per_aetheric_frame`.
            default_permissions (str):
                The default permission level ("create", "read", "block") to use
                if not explicitly set. Defaults to "create".
        """
        # 1. Initialize Base (Sets self._cleaned = False)
        Cleanable.__init__(self)

        if spellbook is None:
            raise ValueError("SpellBinder requires a valid ISpellbook instance.")

        # 2. Initialize Infrastructure
        self._weak_spellbook: SyncWeakRef[ISpellbook] = SyncWeakRef(spellbook)
        self._default_existence = default_existence
        self._default_permissions = default_permissions

        # 3. Initialize Transient State directly (Satisfying __slots__)
        # We initialize these to None/Defaults immediately to ensure the object
        # is valid before any methods (like _reset_current) are called.
        self._spell: Any = None
        self._existence: Existence = default_existence
        self._permissions: str = default_permissions
        self._spellframe: Any | None = None
        self._binding_name: Optional[str] = None
        self._kwargs: dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Deterministically cleans up the SpellBinder.

        Releases the weak reference to the Spellbook and clears all internal
        state. After cleanup, this instance cannot be used.
        """
        if self._cleaned:
            return

        # Mark cleaned first to prevent race conditions
        self._cleaned = True

        if self._weak_spellbook is not None:
            try:
                self._weak_spellbook.cleanup()
            except Exception:
                pass

        # Nullify all slots to assist GC
        self._weak_spellbook = None
        self._spell = None
        self._existence = None
        self._permissions = None
        self._spellframe = None
        self._binding_name = None
        self._kwargs = None

    def _still_alive(self) -> None:
        """
        Internal guard ensuring the binder and its target Spellbook are valid.

        Raises:
            RuntimeError: If the binder is cleaned or the Spellbook is dead.
        """
        if self._cleaned:
            raise RuntimeError(
                "SpellBinder has been cleaned up and can no longer be used."
            )
        # Defensive check: if cleanup happened partially, _weak_spellbook might be None
        if self._weak_spellbook is None or not self._weak_spellbook.is_alive():
            raise RuntimeError(
                "Spellbook is no longer alive; SpellBinder cannot be used."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_current(self) -> None:
        """
        Resets the in-flight registration state to defaults.

        This is called automatically after `finalize()` to prepare the binder
        for the next `bind(...)` call.
        """
        self._still_alive()
        self._spell = None
        self._existence = self._default_existence
        self._permissions = self._default_permissions
        self._spellframe = None
        self._binding_name = None
        self._kwargs = {}

    def _require_spell_selected(self) -> None:
        """
        Validates that a spell target has been selected.

        Raises:
            RuntimeError: If `finalize()` is called before `bind(...)`.
        """
        self._still_alive()
        if self._spell is None:
            raise RuntimeError(
                "SpellBinder.finalize() called with no active spell. "
                "Call `bind(...)` first to start a registration."
            )

    def _ensure_hook_list(self, key: str) -> list[Callable[..., Any]]:
        """
        Internal helper to initialize hook lists in `_kwargs` on demand.

        Args:
            key (str): The hook key (e.g., "pre_hooks", "post_hooks").

        Returns:
            list: The mutable list of hooks for that key.
        """
        self._still_alive()
        existing = self._kwargs.get(key)
        if existing is None:
            hooks: list[Callable[..., Any]] = []
            self._kwargs[key] = hooks
            return hooks
        if not isinstance(existing, list):
            raise TypeError(
                f"Internal error: expected list for '{key}', "
                f"found {type(existing).__name__}."
            )
        return existing

    # ------------------------------------------------------------------
    # Fluent API – Starting a Registration
    # ------------------------------------------------------------------

    def bind(
            self,
            spell: Any,
            *,
            existence: Existence | None = None,
            permissions: str | None = None,
            spellframe: Any | None = None,
            binding_name: str | None = None,
            **kwargs: Any,
    ) -> "SpellBinder":
        """
        **Start Here:** Begins a new registration chain for a spell.

        This method clears any previous configuration and targets the provided
        `spell`. You can supply arguments immediately or use fluent methods
        (e.g., `.as_unique_per_aetheric_frame()`) to configure the registration subsequently.

        Args:
            spell (Any):
                The class, function, or object to register.
            existence (Existence, optional):
                Immediate override for lifecycle scope.
            permissions (str, optional):
                Immediate override for access permissions.
            spellframe (Any, optional):
                The interface or protocol to bind this spell under.
            binding_name (str, optional):
                A unique string identifier for this specific binding.
            **kwargs:
                Pass-through arguments for the Spellbook (e.g., specific hooks).

        Returns:
            SpellBinder: Self, to enable fluent chaining.
        """
        self._still_alive()

        # Clear previous state to ensure a clean slate
        self._reset_current()

        self._spell = spell

        if existence is not None:
            self._existence = existence
        if permissions is not None:
            self._permissions = permissions
        if spellframe is not None:
            self._spellframe = spellframe
        if binding_name is not None:
            self._binding_name = binding_name

        if kwargs:
            self._kwargs.update(kwargs)

        return self

    # ------------------------------------------------------------------
    # Fluent Modifiers – Lifecycle / Scope
    # ------------------------------------------------------------------

    def with_existence(self, existence: Existence) -> "SpellBinder":
        """
        Manually set the `Existence` lifecycle for this registration.

        Use this if you need a specific existence mode not covered by the
        convenience methods below (e.g., a custom extension).
        """
        self._still_alive()
        self._existence = existence
        return self

    def as_unique_per_aetheric_frame(self) -> "SpellBinder":
        """
        Configures the spell as the current **singleton** default (per Aetheric Frame).

        **Behavior:**
        - Only one instance is created for the entire Aetheric Frame.
        - Shared by ALL conduits in that frame (Aether-wide singleton wiring is planned separately).

        **Use Case:**
        - Global configuration managers.
        - Heavy, thread-safe resources (e.g., Database Connection Pools).
        - Centralized logging or telemetry services.
        """
        self._still_alive()
        self._existence = Existence.unique_per_aetheric_frame
        return self

    def as_many(self) -> "SpellBinder":
        """
        Configures the spell as **Transient** (Many Instances).

        **Behavior:**
        - A new instance is created **every time** it is requested.
        - No caching occurs.

        **Use Case:**
        - Lightweight, stateless objects.
        - Request-specific data holders.
        - Objects that are cheap to create and should not be shared.
        """
        self._still_alive()
        self._existence = Existence.many
        return self

    def as_unique_per_conduit(self) -> "SpellBinder":
        """
        Configures the spell as **Scoped to Conduit**.

        **Behavior:**
        - Each Conduit gets its own unique instance.
        - Within a single Conduit, the instance is reused (singleton-per-conduit).

        **Use Case:**
        - Conduit-local caches.
        - Services that maintain state specific to a specific module or plugin.
        - Is isolating "sub-applications" from one another.
        """
        self._still_alive()
        self._existence = Existence.unique_per_conduit
        return self

    def as_unique_per_conduit_cluster(self) -> "SpellBinder":
        """
        Configures the spell as **Scoped to Cluster**.

        **Behavior:**
        - Conduits in the same named cluster share a single instance.
        - Conduits in different clusters get different instances.

        **Use Case:**
        - Sharing resources across a specific subsystem (e.g., "AuthCluster").
        - Grouping related services that need shared state but shouldn't leak globally.
        """
        self._still_alive()
        self._existence = Existence.unique_per_conduit_cluster
        return self

    def as_unique_per_conduit_lineage(self) -> "SpellBinder":
        """
        Configures the spell as **Scoped to Lineage** (Hierarchical).

        **Behavior:**
        - An instance is shared down a specific parent -> child -> grandchild chain.
        - Useful for recursive structures or inheritance-based contexts.

        **Use Case:**
        - Context propagation in a specific execution tree.
        - Sharing configuration overrides down a specific branch of the graph.
        """
        self._still_alive()
        self._existence = Existence.unique_per_conduit_lineage
        return self

    def as_unique_per_spell_space(self) -> "SpellBinder":
        """
        Configures the spell as **Scoped to SpellSpace** (Session/Request).

        **Behavior:**
        - The instance lives only as long as the manually managed `SpellSpace`.
        - When the space is closed/reset, the instance is discarded.

        **Use Case:**
        - Per-request handling (e.g., HTTP Request context).
        - Batch processing jobs where state must be cleared between batches.
        - "Unit of Work" patterns where objects must live for a transaction duration.
        """
        self._still_alive()
        self._existence = Existence.unique_per_spell_space
        return self

    # ------------------------------------------------------------------
    # Fluent Modifiers – Identity & Permissions
    # ------------------------------------------------------------------

    def with_permissions(self, permissions: str) -> "SpellBinder":
        """
        Sets the access permissions for this spell ("create", "read", "block").

        **"create" (Default):** Other conduits can see and instantiate this spell.
        **"read":** Other conduits can use an existing instance but cannot create new ones.
        **"block":** Only the owning conduit can use this spell (private).
        """
        self._still_alive()
        self._permissions = permissions
        return self

    def under_spellframe(self, spellframe: Any) -> "SpellBinder":
        """
        Registers the spell under a specific **Interface** or **Protocol**.

        This is the primary mechanism for Dependency Inversion. Consumers request
        the `spellframe`, and Melder injects this specific spell implementation.

        Args:
            spellframe (Any): The Protocol, Abstract Base Class, or String key.
        """
        self._still_alive()
        self._spellframe = spellframe
        return self

    def named(self, binding_name: str) -> "SpellBinder":
        """
        Assigns a specific **Binding Name** to this registration.

        Useful when you have multiple implementations of the same Interface
        (e.g., "primary_db", "replica_db") and need to disambiguate them.
        """
        self._still_alive()
        self._binding_name = binding_name
        return self

    def with_kwargs(self, **kwargs: Any) -> "SpellBinder":
        """
        Pass arbitrary keyword arguments directly to the Spellbook's bind method.

        This acts as a catch-all for advanced or future parameters that might
        not have dedicated fluent methods yet.
        """
        self._still_alive()
        if kwargs:
            self._kwargs.update(kwargs)
        return self

    # ------------------------------------------------------------------
    # Fluent Modifiers – Lifecycle Hooks
    # ------------------------------------------------------------------

    def with_pre_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Adds a **Pre-Cast Hook**.

        Executed *before* the object is instantiated.
        Useful for validation, logging, or setting up thread-local context.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("pre_hooks")
        hooks.append(hook)
        return self

    def with_pre_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """Adds multiple Pre-Cast Hooks at once."""
        self._still_alive()
        if not hooks:
            return self
        lst = self._ensure_hook_list("pre_hooks")
        lst.extend(hooks)
        return self

    def with_activation_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Adds an **Activation Hook**.

        Executed *during* instantiation (or immediately after).
        Useful for setter injection, initialization logic, or wiring up event listeners.
        Receives the instance as an argument.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("activation_hooks")
        hooks.append(hook)
        return self

    def with_activation_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """Adds multiple Activation Hooks at once."""
        self._still_alive()
        if not hooks:
            return self
        lst = self._ensure_hook_list("activation_hooks")
        lst.extend(hooks)
        return self

    def with_post_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Adds a **Post-Cast Hook**.

        Executed *after* the object is fully ready and returned to the system.
        Useful for final validation or registration with external systems.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("post_hooks")
        hooks.append(hook)
        return self

    def with_post_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """Adds multiple Post-Cast Hooks at once."""
        self._still_alive()
        if not hooks:
            return self
        lst = self._ensure_hook_list("post_hooks")
        lst.extend(hooks)
        return self

    # ------------------------------------------------------------------
    # Commit Step
    # ------------------------------------------------------------------

    def finalize(self) -> str:
        """
        **Commit:** Finalizes the configuration and registers the spell.

        This gathers all the fluent configuration (lifecycle, names, hooks)
        and calls `spellbook.bind(...)`.

        **Behavior:**
        1. Validates that a spell was actually selected via `.bind()`.
        2. Performs the binding in the Spellbook.
        3. **Resets** the binder's state, allowing it to be reused for the next spell.

        Returns:
            str: The unique SHA256 `spell_id` of the registered spell.

        Raises:
            RuntimeError: If called without first calling `.bind()`.
        """
        self._require_spell_selected()

        # Access the weakref safely; throws if Spellbook is collected
        spellbook = self._weak_spellbook.get()

        spell_id: str = spellbook.bind(
            spell=self._spell,
            existence=self._existence,
            permissions=self._permissions,
            spellframe=self._spellframe,
            binding_name=self._binding_name,
            **self._kwargs,
        )

        # Allow reuse for another registration by clearing state
        self._reset_current()
        return spell_id

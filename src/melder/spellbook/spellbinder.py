from typing import Any, Optional, Callable
# Melder Imports
from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.interfaces import ISpellbook
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellBinder(Cleanable):
    """
    Fluent registration helper for configuring one Spellbook bind operation at a time.

    `SpellBinder` is a temporary configuration object layered on top of
    `Spellbook.bind(...)`. It accumulates bind-time choices such as existence,
    permissions, spellframe, binding name, and hook lists, then forwards the
    assembled payload only when `finalize()` is called.

    Contract:
    - Holds in-flight configuration for exactly one pending registration at a
      time.
    - `bind(...)` resets any unfinished state before targeting a new spell.
    - `finalize()` delegates the assembled payload to `Spellbook.bind(...)` and
      then resets the binder for reuse.
    - Uses a weak reference to the target Spellbook so the binder does not own
      Spellbook lifetime.
    - Becomes permanently unusable after `cleanup()` completes.

    Guardrails:
    - Only one registration can be active at a time; every `bind(...)` call resets
      any in-flight state.
    - All fluent methods guard with `_still_alive` and raise `RuntimeError` if the
      binder has been cleaned or its Spellbook weak reference is dead.
    - This helper is not thread-safe; use one binder per thread or serialize access.
    - `cleanup()` is idempotent but permanently invalidates the binder for further use.

    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_weak_spellbook",
        "_default_existence",
        "_default_permissions",
        "_default_profile",
        "_spell",
        "_existence",
        "_permissions",
        "_profile",
        "_spellframe",
        "_binding_name",
        "_kwargs",
    )

    def __init__(
            self,
            spellbook: ISpellbook,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
            default_profile: str = "general",
    ) -> None:
        """
        Initialize a new `SpellBinder` linked to a specific `Spellbook`.

        Args:
            spellbook (ISpellbook):
                The target Spellbook. The binder holds a weak reference to this
                book to prevent reference cycles. If the Spellbook is collected or
                cleaned, future binder calls will raise via `_still_alive()`.
            default_existence (Existence):
                The default lifecycle scope to use if one is not explicitly
                set during a chain. Defaults to `Existence.unique`.
            default_permissions (str):
                The default permission level ("create", "read", "block") to use
                if not explicitly set. Defaults to "create".
            default_profile (str):
                The default spell profile family to use when one is not
                explicitly supplied on `bind(...)`.

        Raises:
            ValueError: If `spellbook` is None.
        """
        # 1. Initialize Base (Sets self._cleaned = False)
        Cleanable.__init__(self)

        if spellbook is None:
            raise ValueError("SpellBinder requires a valid ISpellbook instance.")

        # 2. Initialize Infrastructure
        self._weak_spellbook: SyncWeakRef[ISpellbook] = SyncWeakRef(spellbook)
        self._default_existence = default_existence
        self._default_permissions = default_permissions
        self._default_profile = default_profile

        # 3. Initialize Transient State directly (Satisfying __slots__)
        # We initialize these to None/Defaults immediately to ensure the object
        # is valid before any methods (like _reset_current) are called.
        self._spell: Any = None
        self._existence: Existence = default_existence
        self._permissions: str = default_permissions
        self._profile: str = default_profile
        self._spellframe: Any | None = None
        self._binding_name: Optional[str] = None
        self._kwargs: dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Deterministically cleans up the SpellBinder.

        Releases the weak reference to the Spellbook and clears all internal
        state. After cleanup, this instance cannot be used; subsequent API calls
        will fail via `_still_alive()`. The method is idempotent.
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
        self._profile = None
        self._spellframe = None
        self._binding_name = None
        self._kwargs = None

    def _still_alive(self) -> None:
        """
        Internal guard ensuring the binder and its target Spellbook are valid.

        Every public-facing fluent method calls this before mutating state so
        that stale weak references or post-cleanup usage is detected early.

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
        for the next `bind(...)` call, and at the start of `bind(...)` to drop
        any unfinished configuration. It restores existence/permissions to the
        defaults provided at construction, clears hook kwargs, and enforces
        liveness via `_still_alive()`.
        """
        self._still_alive()
        self._spell = None
        self._existence = self._default_existence
        self._permissions = self._default_permissions
        self._profile = self._default_profile
        self._spellframe = None
        self._binding_name = None
        self._kwargs = {}

    def _require_spell_selected(self) -> None:
        """
        Validates that a spell target has been selected.

        This is invoked by `finalize()` to ensure a prior `bind(...)` call
        successfully set `_spell`.

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

        Raises:
            TypeError: If an unexpected non-list value is already stored under the key.
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
            profile: str | None = None,
            spellframe: Any | None = None,
            binding_name: str | None = None,
            **kwargs: Any,
    ) -> "SpellBinder":
        """
        Start a new fluent registration chain for one spell target.

        Contract:
        - Clears any previous unfinished registration state before targeting the
          provided spell.
        - Reinitializes existence, permissions, and profile to the defaults captured
          at binder construction time.
        - Applies any immediate overrides supplied in the call itself.
        - Merges passthrough `kwargs` into the payload later sent to
          `Spellbook.bind(...)`; later values overwrite earlier keys.

        Args:
            spell (Any):
                The class, function, or object to register.
            existence (Existence, optional):
                Immediate override for lifecycle scope.
            permissions (str, optional):
                Immediate override for access permissions.
            profile (str, optional):
                Immediate override for the spell profile family.
            spellframe (Any, optional):
                Interface, protocol, or other frame key for the registration.
            binding_name (str, optional):
                Secondary key used to disambiguate this binding.
            **kwargs:
                Passthrough bind-time keyword arguments, including lifecycle hooks.

        Returns:
            SpellBinder:
                This binder instance so the caller can continue the fluent chain.

        Raises:
            RuntimeError:
                If the binder has been cleaned or its Spellbook weak reference is no
                longer alive.

        """
        self._still_alive()

        # Clear previous state to ensure a clean slate
        self._reset_current()

        self._spell = spell

        if existence is not None:
            self._existence = existence
        if permissions is not None:
            self._permissions = permissions
        if profile is not None:
            self._profile = profile
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        self._existence = existence
        return self

    def as_unique(self) -> "SpellBinder":
        """
        Configures the spell as a **Global Singleton** (Unique per Aetheric Frame).

        **Behavior:**
        - Only one instance is created for the entire Aetheric Frame.
        - Shared by ALL conduits in that frame.

        **Use Case:**
        - Global configuration managers.
        - Heavy, thread-safe resources (e.g., Database Connection Pools).
        - Centralized logging or telemetry services.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        self._existence = Existence.unique
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
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

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        self._existence = Existence.unique_per_spell_space
        return self

    # ------------------------------------------------------------------
    # Fluent Modifiers – Identity & Permissions
    # ------------------------------------------------------------------

    def with_permissions(self, permissions: str) -> "SpellBinder":
        """
        Set the access permissions for the pending registration.

        Contract:
        - Stores the raw permission string for later validation inside
          `Spellbook.bind(...)`.
        - Does not normalize or validate the permission value by itself.
        - Overwrites any permission value already staged on this binder.

        Typical values:
        - `create`
        - `read`
        - `block`

        Raises:
            RuntimeError:
                If the binder has been cleaned or its Spellbook weak reference is dead.

        """
        self._still_alive()
        self._permissions = permissions
        return self

    def under_spellframe(self, spellframe: Any) -> "SpellBinder":
        """
        Stage a spellframe for the pending registration.

        Purpose:
            Bind the pending spell under a shared interface, protocol, or other frame
            key so downstream resolution can target the frame instead of the concrete
            implementation directly.

        Args:
            spellframe (Any):
                Protocol, abstract base class, or other frame key to associate with the
                pending registration.

        Raises:
            RuntimeError:
                If the binder has been cleaned or its Spellbook weak reference is dead.

        """
        self._still_alive()
        self._spellframe = spellframe
        return self

    def named(self, binding_name: str) -> "SpellBinder":
        """
        Stage a binding name for the pending registration.

        Purpose:
            Disambiguate multiple registrations that share the same spellframe but
            should still resolve as distinct bindings.

        Args:
            binding_name (str):
                Secondary key for the pending registration.

        Raises:
            RuntimeError:
                If the binder has been cleaned or its Spellbook weak reference is dead.

        """
        self._still_alive()
        self._binding_name = binding_name
        return self

    def with_kwargs(self, **kwargs: Any) -> "SpellBinder":
        """
        Pass arbitrary keyword arguments directly to the Spellbook's bind method.

        This acts as a catch-all for advanced or future parameters that might
        not have dedicated fluent methods yet.

        Later calls override existing keys in the passthrough payload.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
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

        Hooks are appended in call order; callability is validated later by
        `Spellbook.bind(...)` when the registration is finalized.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("pre_hooks")
        hooks.append(hook)
        return self

    def with_pre_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Adds multiple Pre-Cast Hooks at once, preserving the provided order.

        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
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

        Hooks are appended in call order; callability is validated later by
        `Spellbook.bind(...)`.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("activation_hooks")
        hooks.append(hook)
        return self

    def with_activation_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Adds multiple Activation Hooks at once, preserving the provided order.

        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
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

        Hooks are appended in call order; callability is validated later by
        `Spellbook.bind(...)`.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        self._still_alive()
        hooks = self._ensure_hook_list("post_hooks")
        hooks.append(hook)
        return self

    def with_post_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Adds multiple Post-Cast Hooks at once, preserving the provided order.

        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.

        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
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
        Commit the current fluent configuration into the target Spellbook.

        Contract:
        - Requires a prior `bind(...)` call to have selected a spell target.
        - Delegates the assembled payload to `Spellbook.bind(...)`.
        - Resets the binder's in-flight state after a successful bind so the instance
          can be reused for another registration.
        - Propagates any staged hook lists and passthrough kwargs directly into the
          underlying Spellbook bind call.

        Returns:
            str:
                The unique SHA256 `spell_id` of the registered spell.

        Raises:
            RuntimeError:
                If called without first calling `bind()`, or if the binder has been
                cleaned or its Spellbook weak reference is dead.
            Exception:
                Any error raised by `Spellbook.bind(...)`, such as duplicate bindings or
                invalid hook payloads.

        """
        self._require_spell_selected()

        # Access the weakref safely; throws if Spellbook is collected
        spellbook = self._weak_spellbook.get()

        spell_id: str = spellbook.bind(
            spell=self._spell,
            existence=self._existence,
            permissions=self._permissions,
            profile=self._profile,
            spellframe=self._spellframe,
            binding_name=self._binding_name,
            **self._kwargs,
        )

        # Allow reuse for another registration by clearing state
        self._reset_current()
        return spell_id

from typing import Any, Callable, Optional, Protocol, runtime_checkable

@runtime_checkable
class ISpellBinder(Protocol):
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

    def cleanup(self) -> None:
        """
        Deterministically cleans up the SpellBinder.
        
        Releases the weak reference to the Spellbook and clears all internal
        state. After cleanup, this instance cannot be used; subsequent API calls
        will fail via `_still_alive()`. The method is idempotent.
        """
        ...

    def bind(self, spell: Any, *, existence: Optional['Existence'] = None, permissions: Optional[str] = None, profile: Optional[str] = None, spellframe: Optional[Any] = None, binding_name: Optional[str] = None, **kwargs: Any) -> 'ISpellBinder':
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
        ...

    def with_existence(self, existence: 'Existence') -> 'ISpellBinder':
        """
        Manually set the `Existence` lifecycle for this registration.
        
        Use this if you need a specific existence mode not covered by the
        convenience methods below (e.g., a custom extension).
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def as_unique(self) -> 'ISpellBinder':
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
        ...

    def as_many(self) -> 'ISpellBinder':
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
        ...

    def as_unique_per_conduit(self) -> 'ISpellBinder':
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
        ...

    def as_unique_per_conduit_cluster(self) -> 'ISpellBinder':
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
        ...

    def as_unique_per_conduit_lineage(self) -> 'ISpellBinder':
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
        ...

    def as_unique_per_spell_space(self) -> 'ISpellBinder':
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
        ...

    def with_permissions(self, permissions: str) -> 'ISpellBinder':
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
        ...

    def under_spellframe(self, spellframe: Any) -> 'ISpellBinder':
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
        ...

    def named(self, binding_name: str) -> 'ISpellBinder':
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
        ...

    def with_kwargs(self, **kwargs: Any) -> 'ISpellBinder':
        """
        Pass arbitrary keyword arguments directly to the Spellbook's bind method.
        
        This acts as a catch-all for advanced or future parameters that might
        not have dedicated fluent methods yet.
        
        Later calls override existing keys in the passthrough payload.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def with_pre_hook(self, hook: Callable['...', Any]) -> 'ISpellBinder':
        """
        Adds a **Pre-Cast Hook**.
        
        Executed *before* the object is instantiated.
        Useful for validation, logging, or setting up thread-local context.
        
        Hooks are appended in call order; callability is validated later by
        `Spellbook.bind(...)` when the registration is finalized.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def with_pre_hooks(self, *hooks: Callable['...', Any]) -> 'ISpellBinder':
        """
        Adds multiple Pre-Cast Hooks at once, preserving the provided order.
        
        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def with_activation_hook(self, hook: Callable['...', Any]) -> 'ISpellBinder':
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
        ...

    def with_activation_hooks(self, *hooks: Callable['...', Any]) -> 'ISpellBinder':
        """
        Adds multiple Activation Hooks at once, preserving the provided order.
        
        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def with_post_hook(self, hook: Callable['...', Any]) -> 'ISpellBinder':
        """
        Adds a **Post-Cast Hook**.
        
        Executed *after* the object is fully ready and returned to the system.
        Useful for final validation or registration with external systems.
        
        Hooks are appended in call order; callability is validated later by
        `Spellbook.bind(...)`.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

    def with_post_hooks(self, *hooks: Callable['...', Any]) -> 'ISpellBinder':
        """
        Adds multiple Post-Cast Hooks at once, preserving the provided order.
        
        An empty invocation is a no-op. Hook callability is validated later by
        `Spellbook.bind(...)`.
        
        Raises:
            RuntimeError: If the binder has been cleaned or its Spellbook weakref is dead.
        """
        ...

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
        ...

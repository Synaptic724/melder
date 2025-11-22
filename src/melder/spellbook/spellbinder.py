from __future__ import annotations

from typing import Any, Optional, Callable

from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.interfaces import ISpellbook


class SpellBinder:
    """
    Fluent registration helper for `Spellbook`.

    `SpellBinder` is an optional, ergonomic layer on top of
    :meth:`Spellbook.bind` that provides an Autofac-style fluent API for
    registering spells. It does **not** introduce a new binding pathway or
    semantics – it simply collects parameters and forwards them into the
    existing `Spellbook.bind(...)` pipeline.

    Typical usage
    -------------

    Basic one-shot registration:

        binder = spellbook.create_binder()

        binder.bind(MyService).finalize()

    Fully fluent style with lifecycle, spellframe, name, and hooks:

        binder = spellbook.create_binder()

        binder.bind(MyService) \
              .as_unique() \
              .under_spellframe(IMyServiceProtocol) \
              .named("primary") \
              .with_permissions("create") \
              .with_pre_hook(log_before) \
              .with_activation_hook(wire_dependencies) \
              .with_post_hook(log_after) \
              .finalize()

    Reuse (the same `SpellBinder` instance can be used for multiple
    registrations; each successful `finalize()` clears the in-flight state):

        binder.bind(FirstService).as_many().finalize()
        binder.bind(SecondService).as_unique_per_conduit().finalize()

    Design notes
    ------------

    * `SpellBinder` does not perform graph or container validation. It only
      assembles the arguments for a **single** registration and forwards
      them into `Spellbook.bind(...)`.
    * Any validation (existence rules, spell type checks, hook validation,
      spellframe / binding_name rules, etc.) is still owned by the existing
      Spellbook implementation.
    * `finalize()` is the “fail-fast” moment for that one registration: if
      `Spellbook.bind(...)` rejects the configuration, the exception
      surfaces immediately.
    """

    __slots__ = (
        "_spellbook",
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
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> None:
        """
        Initialize a new `SpellBinder` bound to a specific `Spellbook`.

        Args:
            spellbook:
                The `Spellbook` instance that registrations will be forwarded
                into. All calls to :meth:`finalize` ultimately delegate to
                `spellbook.bind(...)`.

            default_existence:
                Lifecycle to apply when a registration is started via
                :meth:`bind` and no explicit `existence` is supplied.
                Defaults to :data:`Existence.unique`.

            default_permissions:
                Permission string to apply when a registration is started via
                :meth:`bind` and no explicit `permissions` is supplied.
                Typical values are implementation-defined (e.g. `"create"`,
                `"read"`, `"block"`), and are passed through unchanged to
                `Spellbook.bind(...)`.
        """
        self._spellbook = spellbook
        self._default_existence = default_existence
        self._default_permissions = default_permissions
        self._reset_current()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_current(self) -> None:
        """
        Reset the in-flight registration state.

        This is called on construction and after each successful
        :meth:`finalize`, allowing a single `SpellBinder` instance to be
        reused for multiple registrations without leaking configuration
        from one registration into the next.
        """
        self._spell: Any = None
        self._existence: Existence = self._default_existence
        self._permissions: str = self._default_permissions
        self._spellframe: Any | None = None
        self._binding_name: Optional[str] = None
        self._kwargs: dict[str, Any] = {}

    def _require_spell_selected(self) -> None:
        """
        Ensure that a spell has been selected before finalization.

        Raises:
            RuntimeError:
                If :meth:`finalize` is called before any call to
                :meth:`bind`. A spell must be selected as the target of the
                registration first.
        """
        if self._spell is None:
            raise RuntimeError(
                "SpellBinder.finalize() called with no active spell. "
                "Call `bind(...)` first to start a registration."
            )

    def _ensure_hook_list(self, key: str) -> list[Callable[..., Any]]:
        """
        Ensure that a named hook list exists in the current registration.

        This helper backs the hook-oriented fluent methods such as
        :meth:`with_pre_hook`, :meth:`with_activation_hook`, and
        :meth:`with_post_hook`. It guarantees that `self._kwargs[key]` is a
        list that can be appended to.

        Args:
            key:
                The keyword under which to track a list of hook callables.
                Expected values are `"pre_hooks"`, `"activation_hooks"`, or
                `"post_hooks"`.

        Returns:
            list[Callable[..., Any]]:
                The list stored at `self._kwargs[key]` after ensuring it
                exists and is a list.

        Raises:
            TypeError:
                If there is already a value under `key` but it is not a list.
                This indicates that the registration has been misconfigured
                (for example by passing an incompatible `**kwargs` entry
                directly through :meth:`bind` or :meth:`with_kwargs`).
        """
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
    # Fluent API – starting a registration
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
        Begin a new fluent registration chain for a single spell.

        Calling :meth:`bind` clears any previous in-flight configuration and
        starts a fresh registration targeting the provided `spell`. All
        subsequent fluent calls (lifecycle, permissions, spellframe, hooks,
        extra kwargs) apply to this new registration until :meth:`finalize`
        is called.

        You may either:

        * Supply all configuration here in one shot, or
        * Provide only the spell (and maybe a few values) and refine the
          registration step-by-step via fluent methods.

        Examples
        --------

        One-shot configuration:

            binder.bind(
                MyService,
                existence=Existence.unique,
                permissions="create",
                spellframe=IMyServiceProtocol,
                binding_name="primary",
                pre_hooks=[hook_a],
                post_hooks=[hook_b],
            ).finalize()

        Fluent configuration:

            binder.bind(MyService) \\
                  .as_unique() \\
                  .under_spellframe(IMyServiceProtocol) \\
                  .named("primary") \\
                  .with_pre_hook(hook_a) \\
                  .with_post_hook(hook_b) \\
                  .finalize()

        Args:
            spell:
                The concrete class, function, wrapper, lambda, or pre-existing
                creation object that should be registered as a spell. The exact
                interpretation is delegated to the underlying `Spellbook.bind`
                implementation.

            existence:
                Optional lifecycle override for this registration. When omitted,
                the binder's `default_existence` is used.

            permissions:
                Optional permission override for this registration. When
                omitted, the binder's `default_permissions` is used.

            spellframe:
                Optional logical spellframe / protocol / interface used to
                organize this registration. This value is forwarded directly
                to the `spellframe` parameter of `Spellbook.bind(...)`.

            binding_name:
                Optional human-readable name used to distinguish multiple
                spells under the same spellframe or type. Forwarded directly
                to the `binding_name` parameter of `Spellbook.bind(...)`.

            **kwargs:
                Additional keyword arguments passed through to
                `Spellbook.bind(...)` as-is. This can be used to supply
                hook lists (`pre_hooks`, `activation_hooks`, `post_hooks`)
                or any other advanced options supported by the current
                Spellbook implementation.

        Returns:
            SpellBinder:
                The same binder instance, allowing additional fluent calls
                to be chained for this registration.
        """
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
    # Fluent modifiers – lifecycle / metadata
    # ------------------------------------------------------------------

    def with_existence(self, existence: Existence) -> "SpellBinder":
        """
        Set the lifecycle (Existence) for the active registration.

        This is a direct wrapper over the `existence` argument of
        `Spellbook.bind(...)`. Any deeper rules about how existence interacts
        with spell types, conduits, or frames remain the responsibility of
        the Spellbook implementation.

        Args:
            existence:
                The desired lifecycle mode for this registration.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = existence
        return self
    def as_unique(self) -> "SpellBinder":
        """
        Configure this spell as **unique per Aetheric Frame**.

        Effect:
            - Only one instance of this spell exists in a given Aetheric Frame.
            - All conduits in the same frame share that single instance.
            - This behaves like a traditional "singleton" *within* the frame.

        When to use:
            - For core services that should exist exactly once, such as:
              configuration, logging hubs, schedulers, orchestrators, etc.
            - When you want a stable, long-lived object that is reused across
              the entire system (or across a particular frame in multi-frame
              setups).

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.unique
        return self

    def as_many(self) -> "SpellBinder":
        """
        Configure this spell as **many instances** (no reuse).

        Effect:
            - A new instance is created *every time* the spell is resolved /
              cast.
            - No caching or reuse occurs at the Spellbook level.

        When to use:
            - For stateless or very short-lived objects.
            - For things that are cheap to construct and not worth caching.
            - When you explicitly want isolation between callers.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.many
        return self

    def as_unique_per_conduit(self) -> "SpellBinder":
        """
        Configure this spell as **unique per conduit**.

        Effect:
            - Each conduit gets its own instance of this spell.
            - Within a single conduit, the instance is reused.
            - Different conduits never share the same instance.

        When to use:
            - For per-conduit caches or services that should be shared only
              inside that conduit.
            - When each conduit represents an independent "sub-application"
              and you want local singletons for each one.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.unique_per_conduit
        return self

    def as_unique_per_conduit_cluster(self) -> "SpellBinder":
        """
        Configure this spell as **unique per conduit cluster**.

        Effect:
            - Conduits can be grouped into logical clusters (e.g., by domain,
              feature area, or subsystem).
            - All conduits in the same cluster share a single instance of
              this spell.
            - Different clusters get different instances.

        When to use:
            - For services that should be shared across a *group* of related
              conduits (e.g., "analytics cluster", "billing cluster") but not
              globally across the entire system.
            - When you want more sharing than `as_unique_per_conduit()` but
              less than a global `as_unique()` singleton.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.unique_per_conduit_cluster
        return self

    def as_unique_per_conduit_lineage(self) -> "SpellBinder":
        """
        Configure this spell as **unique per conduit lineage tree**.

        Effect:
            - A "lineage" is a parent → child → grandchild chain of conduits.
            - All conduits in the same lineage tree share a single instance.
            - Separate lineages get separate instances.

        When to use:
            - For scenarios where conduits are spawned dynamically (e.g.,
              child pipelines or subflows) and you want them to share context
              with their ancestors but stay isolated from other families.
            - When the lifetime should follow a tree of related conduits.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.unique_per_conduit_lineage
        return self

    def as_unique_per_spell_space(self) -> "SpellBinder":
        """
        Configure this spell as **unique per spell space**.

        Effect:
            - A "spell space" is a manually-controlled scope (start/close)
              that acts like a temporary sandbox or semaphore.
            - Within a given spell space, all resolutions of this spell share
              the same instance.
            - When the spell space is closed or reset, a new instance will be
              created for the next space.

        When to use:
            - For operations that run inside a bounded "session" or "phase"
              where you want a shared instance while the space is open, and a
              clean reset when it closes.
            - For workflows that need explicit "begin scope / end scope"
              semantics (e.g., batch jobs, request groups, experiments).

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._existence = Existence.unique_per_spell_space
        return self


    def with_permissions(self, permissions: str) -> "SpellBinder":
        """
        Set the permissions string for the active registration.

        The meaning and allowed values of `permissions` are defined by the
        Spellbook. The binder simply forwards the value to
        `Spellbook.bind(...)` without interpretation.

        Args:
            permissions:
                Permission label to attach to this registration.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._permissions = permissions
        return self

    def under_spellframe(self, spellframe: Any) -> "SpellBinder":
        """
        Associate the active registration with a specific spellframe.

        The spellframe acts as a logical namespace, protocol, or interface
        under which this spell is registered. It is forwarded as the
        `spellframe` argument to `Spellbook.bind(...)`.

        Args:
            spellframe:
                Spellframe / protocol / logical group key for this spell.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._spellframe = spellframe
        return self

    def named(self, binding_name: str) -> "SpellBinder":
        """
        Attach a binding name to the active registration.

        Binding names help distinguish multiple registrations under the same
        spellframe or base type. The value is forwarded as the `binding_name`
        argument to `Spellbook.bind(...)`.

        Args:
            binding_name:
                A human-readable name identifying this registration.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        self._binding_name = binding_name
        return self

    def with_kwargs(self, **kwargs: Any) -> "SpellBinder":
        """
        Add arbitrary keyword arguments to the active registration.

        Any keys provided here are merged into the internal `**kwargs` that
        will be forwarded directly to `Spellbook.bind(...)` when
        :meth:`finalize` is called. This allows the binder to expose new
        features added to `Spellbook.bind(...)` without having to change the
        fluent surface.

        Note:
            Hook-specific helpers such as :meth:`with_pre_hook` and
            :meth:`with_post_hook` also write into `self._kwargs`. If you
            pass the same keys here (e.g. `pre_hooks=`), you are responsible
            for ensuring the resulting structure matches what the Spellbook
            expects.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        if kwargs:
            self._kwargs.update(kwargs)
        return self

    # ------------------------------------------------------------------
    # Fluent modifiers – lifecycle hooks
    # ------------------------------------------------------------------

    def with_pre_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Add a single pre-hook to the active registration.

        The hook will be appended to an internal ``pre_hooks`` list, which is
        forwarded to `Spellbook.bind(...)` as ``pre_hooks=[...]`` when
        :meth:`finalize` is called. The Spellbook remains responsible for
        validating and invoking these hooks at the appropriate time.

        Args:
            hook:
                A callable that should be invoked *before* the spell is
                activated/constructed, according to the Spellbook's hook
                semantics.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        hooks = self._ensure_hook_list("pre_hooks")
        hooks.append(hook)
        return self

    def with_pre_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Add one or more pre-hooks to the active registration.

        This is a convenience wrapper around :meth:`with_pre_hook` that allows
        multiple hooks to be added in a single call.

        Args:
            *hooks:
                One or more callables to be appended to the ``pre_hooks`` list.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        if not hooks:
            return self
        lst = self._ensure_hook_list("pre_hooks")
        lst.extend(hooks)
        return self

    def with_activation_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Add a single activation-hook to the active registration.

        The hook will be appended to an internal ``activation_hooks`` list,
        forwarded to `Spellbook.bind(...)` as ``activation_hooks=[...]`` when
        :meth:`finalize` is called. Activation hooks are typically invoked at
        the point where the spell is being activated / constructed.

        Args:
            hook:
                A callable to be run during activation of the spell.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        hooks = self._ensure_hook_list("activation_hooks")
        hooks.append(hook)
        return self

    def with_activation_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Add one or more activation-hooks to the active registration.

        Args:
            *hooks:
                One or more callables to be appended to the
                ``activation_hooks`` list.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        if not hooks:
            return self
        lst = self._ensure_hook_list("activation_hooks")
        lst.extend(hooks)
        return self

    def with_post_hook(self, hook: Callable[..., Any]) -> "SpellBinder":
        """
        Add a single post-hook to the active registration.

        The hook will be appended to an internal ``post_hooks`` list, which is
        forwarded to `Spellbook.bind(...)` as ``post_hooks=[...]`` when
        :meth:`finalize` is called. Post-hooks are typically invoked after a
        spell has been activated or after a resolution event.

        Args:
            hook:
                A callable to be run *after* the spell's main work has
                completed, according to the Spellbook's hook semantics.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        hooks = self._ensure_hook_list("post_hooks")
        hooks.append(hook)
        return self

    def with_post_hooks(self, *hooks: Callable[..., Any]) -> "SpellBinder":
        """
        Add one or more post-hooks to the active registration.

        Args:
            *hooks:
                One or more callables to be appended to the ``post_hooks`` list.

        Returns:
            SpellBinder:
                The same binder instance, to allow further chaining.
        """
        if not hooks:
            return self
        lst = self._ensure_hook_list("post_hooks")
        lst.extend(hooks)
        return self

    # ------------------------------------------------------------------
    # Commit step
    # ------------------------------------------------------------------

    def finalize(self) -> str:
        """
        Commit the current registration into the owning `Spellbook`.

        This is the terminal step for the active fluent chain. It:

        * Ensures a spell has been selected via :meth:`bind`.
        * Forwards all collected parameters to `Spellbook.bind(...)`:
          `spell`, `existence`, `permissions`, `spellframe`, `binding_name`,
          plus any hook lists or additional keyword arguments accumulated
          along the way.
        * Returns the `spell_id` string produced by `Spellbook.bind(...)`.
        * Resets the internal state so this `SpellBinder` can be reused for
          another registration.

        `finalize()` does **not** perform any explicit validation beyond
        checking that `bind(...)` was called first; all binding rules and
        invariants are enforced by the Spellbook implementation. Any exception
        raised inside `Spellbook.bind(...)` will surface directly here.

        Returns:
            str:
                The spell's identifier (for example, a SHA256‐based ID)
                returned by `Spellbook.bind(...)`.

        Raises:
            RuntimeError:
                If called when no spell has been selected via :meth:`bind`.

            Exception:
                Any exception propagated from `Spellbook.bind(...)` or its
                internal binding pipeline.
        """
        self._require_spell_selected()

        spell_id: str = self._spellbook.bind(
            spell=self._spell,
            existence=self._existence,
            permissions=self._permissions,
            spellframe=self._spellframe,
            binding_name=self._binding_name,
            **self._kwargs,
        )

        # Allow reuse for another registration
        self._reset_current()
        return spell_id

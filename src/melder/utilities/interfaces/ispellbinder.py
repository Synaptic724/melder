from typing import Any, Callable, Optional, Protocol, runtime_checkable

from melder.spellbook.existence.existence import Existence


@runtime_checkable
class ISpellBinder(Protocol):
    """
    Interface for the public fluent registration surface returned by
    `Spellbook.create_binder(...)` and `Conduit.create_binder(...)`.

    This interface models the collaborator-facing fluent API rather than the
    concrete `SpellBinder` storage layout. Callers use it to stage one pending
    registration, apply fluent modifiers, and finalize that payload back into
    the owning Spellbook.

    Contract:
    - Supports one in-flight registration chain at a time.
    - Fluent modifiers return the same binder surface for chaining.
    - `finalize()` commits the staged payload and returns the registered
      `spell_id`.
    - `cleanup()` permanently invalidates the binder surface.
    """

    def cleanup(self) -> None:
        """
        Deterministically clean the binder surface.

        After cleanup, subsequent fluent calls are expected to fail according to
        the concrete runtime contract.
        """
        ...

    def bind(
            self,
            spell: Any,
            *,
            existence: Optional[Existence] = None,
            permissions: Optional[str] = None,
            profile: Optional[str] = None,
            spellframe: Optional[Any] = None,
            binding_name: Optional[str] = None,
            **kwargs: Any,
    ) -> "ISpellBinder":
        """
        Start one fluent registration chain for the provided spell target.

        Returns:
            ISpellBinder: The same binder surface for continued fluent chaining.
        """
        ...

    def with_existence(self, existence: Existence) -> "ISpellBinder":
        """Stage an explicit `Existence` lifecycle for the pending registration."""
        ...

    def as_unique(self) -> "ISpellBinder":
        """Stage `Existence.unique` for the pending registration."""
        ...

    def as_many(self) -> "ISpellBinder":
        """Stage `Existence.many` for the pending registration."""
        ...

    def as_unique_per_conduit(self) -> "ISpellBinder":
        """Stage `Existence.unique_per_conduit` for the pending registration."""
        ...

    def as_unique_per_conduit_cluster(self) -> "ISpellBinder":
        """Stage `Existence.unique_per_conduit_cluster` for the pending registration."""
        ...

    def as_unique_per_conduit_lineage(self) -> "ISpellBinder":
        """Stage `Existence.unique_per_conduit_lineage` for the pending registration."""
        ...

    def as_unique_per_spell_space(self) -> "ISpellBinder":
        """Stage `Existence.unique_per_spell_space` for the pending registration."""
        ...

    def with_permissions(self, permissions: str) -> "ISpellBinder":
        """Stage a permission string for the pending registration."""
        ...

    def under_spellframe(self, spellframe: Any) -> "ISpellBinder":
        """Stage a spellframe/interface key for the pending registration."""
        ...

    def named(self, binding_name: str) -> "ISpellBinder":
        """Stage a binding name for the pending registration."""
        ...

    def with_kwargs(self, **kwargs: Any) -> "ISpellBinder":
        """Stage passthrough bind keyword arguments for the pending registration."""
        ...

    def with_pre_hook(self, hook: Callable[..., Any]) -> "ISpellBinder":
        """Append one pre-cast hook to the pending registration."""
        ...

    def with_pre_hooks(self, *hooks: Callable[..., Any]) -> "ISpellBinder":
        """Append multiple pre-cast hooks to the pending registration."""
        ...

    def with_activation_hook(self, hook: Callable[..., Any]) -> "ISpellBinder":
        """Append one activation hook to the pending registration."""
        ...

    def with_activation_hooks(self, *hooks: Callable[..., Any]) -> "ISpellBinder":
        """Append multiple activation hooks to the pending registration."""
        ...

    def with_post_hook(self, hook: Callable[..., Any]) -> "ISpellBinder":
        """Append one post-cast hook to the pending registration."""
        ...

    def with_post_hooks(self, *hooks: Callable[..., Any]) -> "ISpellBinder":
        """Append multiple post-cast hooks to the pending registration."""
        ...

    def finalize(self) -> str:
        """
        Commit the staged payload into the owning Spellbook.

        Returns:
            str: Registered `spell_id` for the finalized spell.
        """
        ...

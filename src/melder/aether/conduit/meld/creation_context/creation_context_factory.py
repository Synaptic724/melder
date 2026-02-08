from typing import Optional

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.utilities.interfaces.interfaces import ISpell


class CreationContextFactory:
    """
    Produce spell-shaped `CreationContext` instances.

    Purpose:
        Keep Meld front-door logic minimal by centralizing context construction
        behind one factory contract.

    Contract:
        - Factory does not own shared caches outside spell ownership.
        - Spell owns context lifecycle through `spell._creation_context`.
        - Get-or-build path is lock-free and race-tolerant.
        - Factory delegates all shape rules to `CreationContextBuilder`.
    """

    __slots__ = ["_builder"]

    def __init__(
            self,
            *,
            builder: Optional[CreationContextBuilder] = None,
    ) -> None:
        """
        Initialize one factory.

        Args:
            builder:
                Optional custom builder. Defaults to `CreationContextBuilder`.
        """
        if builder is None:
            builder = CreationContextBuilder()
        self._builder: CreationContextBuilder = builder

    def build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Build one context for the given spell.

        Args:
            spell:
                Spell that will own the built context.

        Returns:
            CreationContext:
                New spell-shaped context ready for runtime execution.
        """
        return self._builder.build(spell)

    def build_and_bind_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Build one CreationContext and bind it onto the target spell.

        Contract:
            - Always builds a fresh context from current spell state.
            - Replaces any existing spell-owned context reference.
            - Best-effort cleans replaced context.
        """
        built_creation_context = self._builder.build(spell)
        previous_creation_context: Optional[CreationContext] = None
        publish_error: Optional[Exception] = None

        with spell._lock:
            try:
                spell.check_cleaned()
            except Exception as exc:
                publish_error = exc
            else:
                previous_creation_context = spell._creation_context
                if built_creation_context.is_cleaned:
                    publish_error = RuntimeError(
                        "Cannot publish a cleaned CreationContext to spell cache."
                    )
                else:
                    spell._creation_context = built_creation_context

        if publish_error is not None:
            self._cleanup_creation_context(built_creation_context)
            raise publish_error

        self._cleanup_creation_context(previous_creation_context)
        return built_creation_context

    def get_or_build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Resolve one spell-owned context and build on miss without locks.

        Contract:
            - Lock-free miss path by design.
            - Duplicate concurrent builds are accepted if output is equivalent.
            - Context ownership remains on Spell (`spell._creation_context`).
        """
        creation_context = spell._creation_context
        if creation_context is not None and not creation_context.is_cleaned:
            return creation_context

        built_creation_context = self._builder.build(spell)
        publish_error: Optional[Exception] = None
        published_creation_context: Optional[CreationContext] = None

        # Publish path only: lock-free read above, double-check under spell write lock.
        with spell._lock:
            try:
                spell.check_cleaned()
            except Exception as exc:
                publish_error = exc
            else:
                current_creation_context = spell._creation_context
                if (
                        current_creation_context is None
                        or current_creation_context.is_cleaned
                ):
                    if built_creation_context.is_cleaned:
                        publish_error = RuntimeError(
                            "Cannot publish a cleaned CreationContext to spell cache."
                        )
                    else:
                        spell._creation_context = built_creation_context
                        published_creation_context = built_creation_context
                else:
                    published_creation_context = current_creation_context

        if publish_error is not None:
            self._cleanup_creation_context(built_creation_context)
            raise publish_error

        if published_creation_context is built_creation_context:
            return built_creation_context

        self._cleanup_creation_context(built_creation_context)
        if published_creation_context is None:
            raise RuntimeError("Failed to publish CreationContext for spell.")
        return published_creation_context

    def rebuild_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Force rebuild and replace the spell-owned CreationContext.

        Contract:
            - Ignores existing context cache hit.
            - Useful for explicit runtime rebind flows.
        """
        return self.build_and_bind_for_spell(spell)

    @staticmethod
    def _cleanup_creation_context(
            creation_context: Optional[CreationContext],
    ) -> None:
        """
        Best-effort cleanup helper for detached CreationContext instances.
        """
        if creation_context is None:
            return
        try:
            creation_context.cleanup()
        except Exception:
            pass

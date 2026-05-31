from typing import TYPE_CHECKING, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.codegen_creation.spell_mutation_overrides_codegen_creation import (
        SpellMutationOverridesCodegenCreation,
    )
    from melder.aether.spellbook.spell_compiler.codegen_creation.spell_no_overrides_codegen_creation import (
        SpellNoOverridesCodegenCreation,
    )
    from melder.aether.spellbook.spell_compiler.codegen_creation.spell_overrides_codegen_creation import (
        SpellOverridesCodegenCreation,
    )


class SpellCodegenCreation(Cleanable):
    """
    Artifact-owned codegen creation container.

    Purpose:
        Hold the compiler-owned post-plan creation artifact for one spell.

    Contract:
        - Lives on `SpellCompilerArtifact` as the output of the codegen
          creation layer.
        - Top-level route/setup fields capture the spell-static creation
          configuration that `CreationContextBuilder` currently derives
          directly.
        - `selected_strategy_ids` records the ordered strategy chain that
          produced this artifact.
        - Lane payloads may remain `None` while the corresponding creation
          strategies are still being ported.
        - `metadata` is the mutable diagnostics/provenance bag.
    """

    __slots__ = Cleanable.__slots__ + [
        "selected_strategy_ids",
        "discovery_reason",
        "resolve_route_key",
        "fast_transient_no_overrides_enabled",
        "no_overrides_creation",
        "overrides_creation",
        "mutation_overrides_creation",
        "metadata",
    ]

    def __init__(
            self,
            *,
            selected_strategy_ids: Tuple[str, ...],
            discovery_reason: Optional[str],
            resolve_route_key: Optional[str],
            fast_transient_no_overrides_enabled: bool,
            no_overrides_creation: Optional["SpellNoOverridesCodegenCreation"],
            overrides_creation: Optional["SpellOverridesCodegenCreation"],
            mutation_overrides_creation: Optional["SpellMutationOverridesCodegenCreation"],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one codegen creation container.

        Contract:
            - Top-level fields describe the spell-static creation handoff.
            - Lane payloads may be absent until that lane's strategy is
              ported.
        """
        super().__init__()
        self.selected_strategy_ids = selected_strategy_ids
        self.discovery_reason = discovery_reason
        self.resolve_route_key = resolve_route_key
        self.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )
        self.no_overrides_creation = no_overrides_creation
        self.overrides_creation = overrides_creation
        self.mutation_overrides_creation = mutation_overrides_creation
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the codegen creation container.
        """
        if self._cleaned:
            return

        self._cleaned = True
        no_overrides_creation = self.no_overrides_creation
        if no_overrides_creation is not None:
            no_overrides_creation.cleanup()
        overrides_creation = self.overrides_creation
        if overrides_creation is not None:
            overrides_creation.cleanup()
        mutation_overrides_creation = self.mutation_overrides_creation
        if mutation_overrides_creation is not None:
            mutation_overrides_creation.cleanup()
        self.metadata.clear()

        del self.selected_strategy_ids
        del self.discovery_reason
        del self.resolve_route_key
        del self.fast_transient_no_overrides_enabled
        del self.no_overrides_creation
        del self.overrides_creation
        del self.mutation_overrides_creation
        del self.metadata

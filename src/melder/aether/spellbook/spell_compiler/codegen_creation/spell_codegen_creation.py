from typing import Any, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenCreation(Cleanable):
    """
    Artifact-owned codegen creation container.

    Purpose:
        Hold the post-plan codegen creation results for the 3 execution lanes:
        `no_overrides`, `overrides`, and `mutation_overrides`.

    Contract:
        - Lives on `SpellCompilerArtifact` as the output of the codegen
          creation layer.
        - Lane payloads may remain `None` while the codegen creation system is
          only scaffolded.
        - `metadata` is the mutable diagnostics/provenance bag.
    """

    __slots__ = Cleanable.__slots__ + [
        "selected_strategy_id",
        "discovery_reason",
        "no_overrides_output",
        "overrides_output",
        "mutation_overrides_output",
        "metadata",
    ]

    def __init__(
            self,
            *,
            selected_strategy_id: Optional[str],
            discovery_reason: Optional[str],
            no_overrides_output: Optional[Any],
            overrides_output: Optional[Any],
            mutation_overrides_output: Optional[Any],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one codegen creation container.
        """
        super().__init__()
        self.selected_strategy_id = selected_strategy_id
        self.discovery_reason = discovery_reason
        self.no_overrides_output = no_overrides_output
        self.overrides_output = overrides_output
        self.mutation_overrides_output = mutation_overrides_output
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the codegen creation container.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.metadata.clear()

        del self.selected_strategy_id
        del self.discovery_reason
        del self.no_overrides_output
        del self.overrides_output
        del self.mutation_overrides_output
        del self.metadata

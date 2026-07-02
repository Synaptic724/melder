from typing import Any, Callable, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenCreation(Cleanable):
    """
    Artifact-owned codegen creation container.

    Purpose:
        Hold the compiler-owned post-plan creation artifact for one spell.

    Contract:
        - Lives on `SpellCompilerArtifact` as the output of the codegen
          creation layer.
        - `selected_strategy_ids` records the ordered strategy chain that
          produced this artifact.
        - Runtime-facing output is intentionally narrow:
          `no_overrides_executor`, `no_overrides_instance_executor` (the
          instance-only no-hooks twin), and `overrides_executor`.
        - The artifact also retains the compiled code objects that produced
          those executors so cache/export lanes can persist the real compiled
          outputs without reconstructing them from live callables later.
        - The concrete codegen style chosen by phase 11 is provenance only and
          belongs in metadata, not in the top-level runtime contract.
        - These are the spell-static executor inputs consumed by
          `CreationContext`, not the final public hook/no-hook dispatch doors.
        - `metadata` is the mutable diagnostics/provenance bag.
    """

    __slots__ = Cleanable.__slots__ + [
        "selected_strategy_ids",
        "discovery_reason",
        "no_overrides_executor",
        "no_overrides_instance_executor",
        "no_overrides_code_object",
        "overrides_executor",
        "overrides_code_object",
        "metadata",
    ]

    def __init__(
            self,
            *,
            selected_strategy_ids: Tuple[str, ...],
            discovery_reason: Optional[str],
            no_overrides_executor: Optional[Callable[..., Any]],
            overrides_executor: Optional[Callable[..., Any]],
            metadata: Dict[str, Any],
            no_overrides_instance_executor: Optional[Callable[..., Any]] = None,
            no_overrides_code_object: Optional[Any] = None,
            overrides_code_object: Optional[Any] = None,
    ) -> None:
        """
        Build one codegen creation container.

        Contract:
            - Stores only the spell-static executor inputs required by
              `CreationContext`.
            - Executor fields may be `None` while a strategy scaffold is still
              incomplete.
        """
        super().__init__()
        self.selected_strategy_ids = selected_strategy_ids
        self.discovery_reason = discovery_reason
        self.no_overrides_executor = no_overrides_executor
        self.no_overrides_instance_executor = no_overrides_instance_executor
        self.no_overrides_code_object = no_overrides_code_object
        self.overrides_executor = overrides_executor
        self.overrides_code_object = overrides_code_object
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the codegen creation container.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.metadata.clear()

        del self.selected_strategy_ids
        del self.discovery_reason
        del self.no_overrides_executor
        del self.no_overrides_instance_executor
        del self.no_overrides_code_object
        del self.overrides_executor
        del self.overrides_code_object
        del self.metadata

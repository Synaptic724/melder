from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.meld.creation_context.creation_context import (
        OverrideRouteConfig,
    )


class SpellMutationOverridesCodegenCreation(Cleanable):
    """
    Compiler-owned mutation-overrides creation payload for one spell.

    Purpose:
        Reserve the spell-static mutation-aware creation packaging surface that
        the codegen-creation layer will later hand to `CreationContextBuilder`.

    Contract:
        - `override_route_config` is the spell-static mutation-aware route
          package consumed by `CreationContext`.
        - `baseline_executor` is an optional prebuilt mutation-lane override
          executor for the empty override shape.
        - `metadata` is the mutable diagnostics/provenance bag for this lane.
    """

    __slots__ = Cleanable.__slots__ + [
        "override_route_config",
        "baseline_executor",
        "metadata",
    ]

    def __init__(
            self,
            *,
            override_route_config: Optional["OverrideRouteConfig"],
            baseline_executor: Optional[Callable[..., Any]],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one mutation-overrides creation payload.
        """
        super().__init__()
        self.override_route_config = override_route_config
        self.baseline_executor = baseline_executor
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the mutation-overrides creation payload.
        """
        if self._cleaned:
            return

        self._cleaned = True
        override_route_config = self.override_route_config
        if override_route_config is not None:
            override_route_config.cleanup()
        self.metadata.clear()

        del self.override_route_config
        del self.baseline_executor
        del self.metadata

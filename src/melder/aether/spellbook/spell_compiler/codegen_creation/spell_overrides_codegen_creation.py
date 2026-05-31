from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.meld.creation_context.creation_context import (
        OverrideRouteConfig,
    )


class SpellOverridesCodegenCreation(Cleanable):
    """
    Compiler-owned overrides creation payload for one spell.

    Purpose:
        Reserve the spell-static override packaging surface that the
        codegen-creation layer will hand to `CreationContextBuilder` once the
        override lane is ported out of the runtime binder.

    Contract:
        - `override_patch_map_phase10` is the borrowed compatibility bridge to
          Phase 10 targeting until that seam is fully retired.
        - `override_route_config` is the spell-static override route package
          consumed by `CreationContext`.
        - `baseline_executor` is an optional prebuilt override executor for the
          empty override shape.
        - `metadata` is the mutable diagnostics/provenance bag for this lane.
    """

    __slots__ = Cleanable.__slots__ + [
        "override_patch_map_phase10",
        "override_route_config",
        "baseline_executor",
        "metadata",
    ]

    def __init__(
            self,
            *,
            override_patch_map_phase10: Optional[Any],
            override_route_config: Optional["OverrideRouteConfig"],
            baseline_executor: Optional[Callable[..., Any]],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one overrides creation payload.
        """
        super().__init__()
        self.override_patch_map_phase10 = override_patch_map_phase10
        self.override_route_config = override_route_config
        self.baseline_executor = baseline_executor
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the overrides creation payload.
        """
        if self._cleaned:
            return

        self._cleaned = True
        override_route_config = self.override_route_config
        if override_route_config is not None:
            override_route_config.cleanup()
        self.metadata.clear()

        del self.override_patch_map_phase10
        del self.override_route_config
        del self.baseline_executor
        del self.metadata

from typing import Any, Callable, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class SpellNoOverridesCodegenCreation(Cleanable):
    """
    Compiler-owned no-overrides creation payload for one spell.

    Purpose:
        Hold the spell-static no-overrides runtime artifact produced by the
        codegen creation layer so later runtime binders do not need to
        reconstruct Phase 13 no-overrides packaging themselves.

    Contract:
        - `compiled_executor` is the ready runtime callable for the
          no-overrides lane.
        - `executor_signature` is the deterministic compile/signature identity
          associated with that callable.
        - `metadata` is the mutable diagnostics/provenance bag for this lane.
    """

    __slots__ = Cleanable.__slots__ + [
        "compiled_executor",
        "executor_signature",
        "metadata",
    ]

    def __init__(
            self,
            *,
            compiled_executor: Optional[Callable[..., Any]],
            executor_signature: Optional[str],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one no-overrides creation payload.

        Args:
            compiled_executor:
                Ready runtime callable for the no-overrides lane, or `None`
                when this spell has no no-overrides execution body.
            executor_signature:
                Deterministic signature describing the compiled executor input
                shape.
            metadata:
                Mutable diagnostics/provenance bag for this lane.
        """
        super().__init__()
        self.compiled_executor = compiled_executor
        self.executor_signature = executor_signature
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the no-overrides creation payload.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.metadata.clear()

        del self.compiled_executor
        del self.executor_signature
        del self.metadata

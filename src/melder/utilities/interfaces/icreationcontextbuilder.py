from typing import Optional, Protocol, runtime_checkable

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.synchronization.creation_gate import CreationGate


@runtime_checkable
class ICreationContextBuilder(Protocol):
    """
    Build spell-shaped `CreationContext` instances.

    Purpose:
        Encapsulate the build-time policy for creation contexts so Meld can
        request a context without embedding shape logic in the front-door flow.

    Contract:
        - Builder only consumes spell-static data.
        - This builder accepts no caller-conduit transients.
        - Output context is deterministic for the same spell state.
    """

    @staticmethod
    def build(
            spell: ISpell,
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional[CreationGate] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> CreationContext:
        """
        Build one `CreationContext` bound to the provided spell.

        Args:
            spell:
                Spell to bind to the created runtime context.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. This flag is
                carried into the CreationContext for runtime policy selection.
            creation_gate:
                Shared spell-index CreationGate used by the built context
                for dynamic-mode execution admission.
            creation_gate_index_id:
                Stable spell-index id used for gate diagnostics.

        Returns:
            CreationContext:
                A new spell-bound runtime context.

        Raises:
            RuntimeError:
                If the spell is not in a runnable state for context creation.
        """
        ...


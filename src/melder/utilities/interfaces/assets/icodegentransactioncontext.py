import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class ICodegenTransactionContext(ICleanable, Protocol):
    """
    Interface for one codegen transaction context.
    """

    @property
    def transaction_id(self) -> str:
        """
        Return the stable transaction id.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this request.
        """
        ...

    @property
    def code(self) -> str:
        """
        Return the raw code string for this request.
        """
        ...

    @property
    def code_hash(self) -> str:
        """
        Return the deterministic code hash for this request.
        """
        ...

    @property
    def projection(self) -> Optional["CodegenProjection"]:
        """
        Return the optional resolved codegen projection.
        """
        ...

    @property
    def namespace_configuration(self) -> Optional[ICodegenNamespaceConfiguration]:
        """
        Return the optional namespace configuration.
        """
        ...

    @property
    def namespace(self) -> Optional[ICodegenNamespace]:
        """
        Return the optional live namespace.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for this transaction.
        """
        ...

    def set_projection(self, projection: Optional["CodegenProjection"]) -> None:
        """
        Replace the optional projection reference.
        """
        ...

    def set_namespace_configuration(
            self,
            namespace_configuration: Optional[ICodegenNamespaceConfiguration],
    ) -> None:
        """
        Replace the optional namespace configuration.
        """
        ...

    def set_namespace(
            self,
            namespace: Optional[ICodegenNamespace],
    ) -> None:
        """
        Replace the optional live namespace.
        """
        ...

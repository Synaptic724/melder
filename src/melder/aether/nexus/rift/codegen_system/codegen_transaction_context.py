import threading
import hashlib
from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import ICodegenTransactionContext


class CodegenTransactionContext(Cleanable, ICodegenTransactionContext):
    """
    Internal

    Per-call codegen transaction context.

    Purpose:
        Carry one shared transaction identity and one shared bundle of
        code/frame/projection/namespace state across validation, execution,
        history, and monitoring work during one codegen call.

    Contract:
        - Represents one codegen request only.
        - Stores the raw code string and its deterministic SHA256 hash.
        - May reference one `CodegenProjection`, one
          `CodegenNamespaceConfiguration`, and one `CodegenNamespace`.
        - Does not own or cleanup the referenced projection.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_transaction_id",
        "_frame_name",
        "_code",
        "_code_hash",
        "_projection",
        "_namespace_configuration",
        "_namespace",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            code: str,
            projection: Optional[CodegenProjection] = None,
            namespace_configuration: Optional[CodegenNamespaceConfiguration] = None,
            namespace: Optional[CodegenNamespace] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one codegen transaction context.

        Args:
            frame_name:
                Target frame name for the codegen request.
            code:
                Raw generated Python source for the request.
            projection:
                Optional codegen projection resolved for the frame.
            namespace_configuration:
                Optional namespace policy/configuration resolved for this call.
            namespace:
                Optional live namespace built for this call.
            metadata:
                Optional transaction-local metadata.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` or `code` is empty.
        """
        super().__init__()
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._transaction_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._code: str = code
        self._code_hash: str = hashlib.sha256(code.encode("utf-8")).hexdigest()
        self._projection: Optional[CodegenProjection] = projection
        self._namespace_configuration: Optional[CodegenNamespaceConfiguration] = (
            namespace_configuration
        )
        self._namespace: Optional[CodegenNamespace] = namespace
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear transaction-context-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._transaction_id = None
            self._frame_name = None
            self._code = None
            self._code_hash = None
            self._projection = None
            self._namespace_configuration = None
            self._namespace = None
            self._metadata.clear()
            self._metadata = None
        self._lock = None

    @property
    def transaction_id(self) -> str:
        """
        Return the stable transaction identifier for this request.

        Returns:
            str: Stable transaction id.
        """
        self.check_cleaned()
        with self._lock:
            return self._transaction_id

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this request.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def code(self) -> str:
        """
        Return the raw generated Python source for this request.

        Returns:
            str: Raw code string.
        """
        self.check_cleaned()
        with self._lock:
            return self._code

    @property
    def code_hash(self) -> str:
        """
        Return the deterministic SHA256 hash for the raw code string.

        Returns:
            str: SHA256 code hash.
        """
        self.check_cleaned()
        with self._lock:
            return self._code_hash

    @property
    def projection(self) -> Optional[CodegenProjection]:
        """
        Return the optional resolved codegen projection.

        Returns:
            Optional[CodegenProjection]: Resolved projection when available.
        """
        self.check_cleaned()
        with self._lock:
            return self._projection

    @property
    def namespace_configuration(self) -> Optional[CodegenNamespaceConfiguration]:
        """
        Return the optional namespace configuration for this request.

        Returns:
            Optional[CodegenNamespaceConfiguration]: Namespace configuration
            when assigned.
        """
        self.check_cleaned()
        with self._lock:
            return self._namespace_configuration

    @property
    def namespace(self) -> Optional[CodegenNamespace]:
        """
        Return the optional live namespace for this request.

        Returns:
            Optional[CodegenNamespace]: Built namespace when assigned.
        """
        self.check_cleaned()
        with self._lock:
            return self._namespace

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached metadata copy for this transaction.

        Returns:
            Dict[str, object]: Detached metadata copy.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def set_projection(self, projection: Optional[CodegenProjection]) -> None:
        """
        Replace the optional projection reference stored on this context.

        Args:
            projection:
                New projection reference or None.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._projection = projection

    def set_namespace_configuration(
            self,
            namespace_configuration: Optional[CodegenNamespaceConfiguration],
    ) -> None:
        """
        Replace the optional namespace configuration stored on this context.

        Args:
            namespace_configuration:
                New namespace configuration or None.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._namespace_configuration = namespace_configuration

    def set_namespace(self, namespace: Optional[CodegenNamespace]) -> None:
        """
        Replace the optional live namespace stored on this context.

        Args:
            namespace:
                New live namespace or None.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._namespace = namespace

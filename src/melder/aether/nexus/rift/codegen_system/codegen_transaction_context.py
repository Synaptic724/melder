import hashlib
from typing import Any, Dict, Optional

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.utilities.helpers.id_builder import IDBuilder


class CodegenTransactionContext:
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

    __slots__ = [
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
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
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

    @property
    def transaction_id(self) -> str:
        """
        Return the stable transaction identifier for this request.

        Returns:
            str: Stable transaction id.
        """
        return self._transaction_id

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this request.

        Returns:
            str: Target frame name.
        """
        return self._frame_name

    @property
    def code(self) -> str:
        """
        Return the raw generated Python source for this request.

        Returns:
            str: Raw code string.
        """
        return self._code

    @property
    def code_hash(self) -> str:
        """
        Return the deterministic SHA256 hash for the raw code string.

        Returns:
            str: SHA256 code hash.
        """
        return self._code_hash

    @property
    def projection(self) -> Optional[CodegenProjection]:
        """
        Return the optional resolved codegen projection.

        Returns:
            Optional[CodegenProjection]: Resolved projection when available.
        """
        return self._projection

    @property
    def namespace_configuration(self) -> Optional[CodegenNamespaceConfiguration]:
        """
        Return the optional namespace configuration for this request.

        Returns:
            Optional[CodegenNamespaceConfiguration]: Namespace configuration
            when assigned.
        """
        return self._namespace_configuration

    @property
    def namespace(self) -> Optional[CodegenNamespace]:
        """
        Return the optional live namespace for this request.

        Returns:
            Optional[CodegenNamespace]: Built namespace when assigned.
        """
        return self._namespace

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached metadata copy for this transaction.

        Returns:
            Dict[str, object]: Detached metadata copy.
        """
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
        self._namespace = namespace


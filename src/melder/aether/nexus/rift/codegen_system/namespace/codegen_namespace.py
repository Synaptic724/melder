import threading
from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ICodegenNamespace


class CodegenNamespace(Cleanable, ICodegenNamespace):
    """
    Internal

    Live namespace payload for one codegen request.

    Purpose:
        Hold the actual globals/locals dictionaries that later execution work
        will run against, while preserving the configuration object that
        produced them.

    Contract:
        - Stores one namespace configuration.
        - Stores one globals dict and one locals dict.
        - Keeps metadata separate from the raw globals/locals mappings.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_configuration",
        "_globals_dict",
        "_locals_dict",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            configuration: CodegenNamespaceConfiguration,
            globals_dict: Optional[Dict[str, object]] = None,
            locals_dict: Optional[Dict[str, object]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one live codegen namespace.

        Args:
            configuration:
                Namespace configuration that shaped this namespace.
            globals_dict:
                Optional globals dictionary.
            locals_dict:
                Optional locals dictionary.
            metadata:
                Optional live namespace metadata.

        Returns:
            None.

        Raises:
            TypeError:
                If `configuration` is None.
        """
        super().__init__()
        if configuration is None:
            raise TypeError("configuration cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._configuration: CodegenNamespaceConfiguration = configuration
        self._globals_dict: Dict[str, object] = (
            dict(globals_dict) if globals_dict else {}
        )
        self._locals_dict: Dict[str, object] = (
            dict(locals_dict) if locals_dict else {}
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear live namespace state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._configuration = None
            self._globals_dict.clear()
            self._locals_dict.clear()
            self._metadata.clear()
            self._globals_dict = None
            self._locals_dict = None
            self._metadata = None
        self._lock = None

    @classmethod
    def create_placeholder(
            cls,
            *,
            configuration: CodegenNamespaceConfiguration,
            metadata: Optional[Dict[str, object]] = None,
    ) -> "CodegenNamespace":
        """
        Build the current placeholder live namespace for the root slice.

        Args:
            configuration:
                Namespace configuration that shapes the placeholder namespace.
            metadata:
                Optional namespace metadata.

        Returns:
            CodegenNamespace: Placeholder namespace.
        """
        return cls(
            configuration=configuration,
            globals_dict={},
            locals_dict={},
            metadata=metadata,
        )

    @property
    def configuration(self) -> CodegenNamespaceConfiguration:
        """
        Return the configuration that produced this namespace.

        Returns:
            CodegenNamespaceConfiguration: Namespace configuration.
        """
        self.check_cleaned()
        with self._lock:
            return self._configuration

    @property
    def globals_dict(self) -> Dict[str, object]:
        """
        Return the live globals dictionary for this namespace.

        Returns:
            Dict[str, object]: Live globals dictionary.
        """
        self.check_cleaned()
        with self._lock:
            return self._globals_dict

    @property
    def locals_dict(self) -> Dict[str, object]:
        """
        Return the live locals dictionary for this namespace.

        Returns:
            Dict[str, object]: Live locals dictionary.
        """
        self.check_cleaned()
        with self._lock:
            return self._locals_dict

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached metadata copy for this namespace.

        Returns:
            Dict[str, object]: Detached metadata copy.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def get_result(self) -> Optional[object]:
        """
        Return the optional `result` value stored in the locals dict.

        Returns:
            Optional[object]: Stored `result` value when present.
        """
        self.check_cleaned()
        with self._lock:
            if "result" not in self._locals_dict:
                return None
            return self._locals_dict["result"]

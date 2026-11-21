import threading
from typing import TYPE_CHECKING, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.codegen_system.namespace.codegen_output_capture import (
        CodegenOutputCapture,
    )



class CodegenNamespace(Cleanable):
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
        - Owns the request's optional `CodegenOutputCapture` (the room's `print` when its configuration captures
          output) and cleans it on cleanup; `get_output()` reads it (GitHub #337, task 2).

    Registration:
        MELDER KERNEL - guarded. Produced by `CodegenNamespaceBuilder` after
        accepted validation.

    Subsystem Context:
        The live execution environment for one request - the actual
        globals/locals the executor runs against - paired with the
        configuration that produced it.

    System Context:
        Retaining the producing CONFIGURATION alongside the live dictionaries is
        what keeps an executed request auditable. The dictionaries alone would
        show what was present without recording what policy intended, and the
        two can differ where a strategy declined to contribute.
        This object exists only after validation is accepted, which is the
        engine's central invariant: no environment is built for code that has
        not passed the gate.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Live namespace payload for one codegen request. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_configuration",
        "_globals_dict",
        "_locals_dict",
        "_metadata",
        "_output_capture",
    ]

    def __init__(
            self,
            *,
            configuration: CodegenNamespaceConfiguration,
            globals_dict: Optional[Dict[str, object]] = None,
            locals_dict: Optional[Dict[str, object]] = None,
            metadata: Optional[Dict[str, object]] = None,
            output_capture: Optional[CodegenOutputCapture] = None,
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
            output_capture:
                The request's output capture, installed as its `print`; OWNED by this namespace from here on and
                cleaned with it. None when the room does not capture output.

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
        self._output_capture: Optional[CodegenOutputCapture] = output_capture

    def cleanup(self) -> None:
        """
        Idempotently clear live namespace state.

        Contract:
            - Cleans the owned output capture, when there is one, before dropping the dictionaries.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._output_capture is not None:
                self._output_capture.cleanup()
            self._globals_dict.clear()
            self._locals_dict.clear()
            self._metadata.clear()
            del self._output_capture
            del self._configuration
            del self._globals_dict
            del self._locals_dict
            del self._metadata
        del self._lock

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

    def get_output(self) -> str:
        """
        Return the text room code printed to stdout during this request, as its output capture kept it.

        Contract:
            - With a capture: the capture's `output` - at most the room's limit, plus one truncation line when text
              was dropped (GitHub #337, task 2).
            - Without one (the room's configuration turns capture off): "".

        Returns:
            str: The printed text for the execution payload's `output` key; "" when nothing was captured.
        """
        self.check_cleaned()
        with self._lock:
            if self._output_capture is None:
                return ""
            return self._output_capture.output

import threading
from typing import TYPE_CHECKING
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from types import CodeType

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )


class CodegenCompiler(Cleanable):
    """
    Internal

    Internal compile stage for codegen execution.

    Purpose:
        Compile generated Python source into one executable code object for the
        executor without absorbing execution or validation responsibilities.

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenSystem`.

    Subsystem Context:
        The compile stage between accepted validation and execution. It turns
        validated source into one executable code object for
        `CodegenExecutor`.

    System Context:
        Compilation sits AFTER validation and BEFORE namespace construction,
        and that position is the safety ordering the whole engine is built on:
        source is judged, then compiled, and only then does an environment get
        built for it to run in.
        Not absorbing execution or validation keeps the stage single-purpose, so
        the one place that turns text into executable code is small enough to
        audit.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Internal compile stage for codegen execution. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one codegen compiler.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the compiler.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def compile(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> CodeType:
        """
        Compile one codegen transaction into an executable code object.

        Args:
            transaction_context:
                Per-call codegen transaction context.

        Returns:
            CodeType: Compiled Python code object ready for `exec`.

        Raises:
            TypeError:
                If `transaction_context` is None.
        """
        self.check_cleaned()
        with self._lock:
            if transaction_context is None:
                raise TypeError("transaction_context cannot be None.")
            return compile(
                transaction_context.code,
                "<melder-codegen:{0}>".format(transaction_context.transaction_id),
                "exec",
            )

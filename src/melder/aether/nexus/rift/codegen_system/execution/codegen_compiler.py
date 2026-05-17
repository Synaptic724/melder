import threading
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from types import CodeType

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ICodegenTransactionContext


class CodegenCompiler(Cleanable):
    """
    Internal

    Internal compile stage for codegen execution.

    Purpose:
        Compile generated Python source into one executable code object for the
        executor without absorbing execution or validation responsibilities.
    """

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
        self._lock = None

    def compile(
            self,
            transaction_context: ICodegenTransactionContext,
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

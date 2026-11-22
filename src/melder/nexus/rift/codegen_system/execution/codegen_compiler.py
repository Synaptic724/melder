import threading
from typing import TYPE_CHECKING, ClassVar, Optional
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

    Contract:
        - Owns the run file-name form: each run compiles under
          `<melder-codegen:{transaction_id}>` (`run_filename`), so every code
          object a run defines - its functions and classes included - carries
          its run's id in `co_filename`, and `run_id_from_filename` reads the id
          back for the executor's failure location (GitHub #339).

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

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Internal compile stage for codegen execution. Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _RUN_FILENAME_PREFIX: ClassVar[str] = "<melder-codegen:"
    _RUN_FILENAME_SUFFIX: ClassVar[str] = ">"

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

    @staticmethod
    def run_filename(transaction_id: str) -> str:
        """
        Return the file name a run's code is compiled under.

        Contract:
            - `<melder-codegen:{transaction_id}>`; `run_id_from_filename` reads
              `transaction_id` back from it.

        Args:
            transaction_id:
                The run's transaction id (its `run_id` in the execute payload).

        Returns:
            str: The run file name.

        Raises:
            ValueError:
                If `transaction_id` is not a non-empty string.
        """
        if not isinstance(transaction_id, str) or not transaction_id:
            raise ValueError("transaction_id cannot be empty.")
        return "{0}{1}{2}".format(
            CodegenCompiler._RUN_FILENAME_PREFIX,
            transaction_id,
            CodegenCompiler._RUN_FILENAME_SUFFIX,
        )

    @staticmethod
    def run_id_from_filename(filename: str) -> Optional[str]:
        """
        Return the run id a run file name carries, or None for any other file name.

        Contract:
            - The inverse of `run_filename`: a code object's `co_filename` of the
              form `<melder-codegen:{run_id}>` answers `run_id`; a library file,
              `<string>`, or the form with no id answers None.

        Args:
            filename:
                A code object's `co_filename`.

        Returns:
            Optional[str]: The run id; None when `filename` is not a run file
            name.
        """
        prefix = CodegenCompiler._RUN_FILENAME_PREFIX
        suffix = CodegenCompiler._RUN_FILENAME_SUFFIX
        if not filename.startswith(prefix) or not filename.endswith(suffix):
            return None
        run_id = filename[len(prefix):len(filename) - len(suffix)]
        if not run_id:
            return None
        return run_id

    def compile(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> CodeType:
        """
        Compile one codegen transaction into an executable code object.

        Contract:
            - The code object is named after its run:
              `run_filename(transaction_context.transaction_id)`.

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
                self.run_filename(transaction_context.transaction_id),
                "exec",
            )

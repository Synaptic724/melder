import threading
from typing import TYPE_CHECKING, Mapping, Optional, Tuple
from types import CodeType

from melder.nexus.rift.codegen_system.execution.codegen_compiler import (
    CodegenCompiler,
)
from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )


class CodegenExecutor(Cleanable):
    """
    Internal

    Owner of governed code execution for one codegen request.

    Purpose:
        Execute one compiled code object against one built codegen namespace and
        return the execution-layer result.

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenSystem`.

    Subsystem Context:
        The final stage of the engine: it runs one compiled code object against
        one built `CodegenNamespace` and returns a `CodegenExecutionResult`.

    System Context:
        Execution is GOVERNED by construction rather than by policy checks at
        run time. By the moment this stage runs, the validator has accepted the
        source, the compiler has produced the code object, and the namespace
        builder has exposed only what configuration allowed - so the executor's
        safety comes from what the code can REACH, not from watching what it
        does.
        That is why the namespace is built only after accepted validation: the
        executor has no way to retract reach once execution begins.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Owner of governed code execution for one codegen request. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one codegen executor.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the executor.

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

    def execute(
            self,
            compiled_code: CodeType,
            transaction_context: CodegenTransactionContext,
            run_sources: Mapping[str, str],
    ) -> CodegenExecutionResult:
        """
        Execute one compiled code object against the transaction namespace.

        Contract:
            - After `exec` returns, the result carries the namespace's `result` value and the text room code printed
              (`CodegenNamespace.get_output()`); after `exec` raises, the runtime error and the text printed before it
              (GitHub #337, task 2).
            - After `exec` raises, the result also says where room code failed (GitHub #339): the error's traceback
              is walked to its end and the last entry whose code object is a run's - its `co_filename` carries a run
              id, read by `CodegenCompiler.run_id_from_filename` - gives the line (`tb_lineno`) and the run: this
              run, an earlier run whose function was called, or this run's line that called the melder or library
              code that raised. The line's text is quoted from `run_sources` when that run's source is kept and has
              the line. A traceback with no room-code entry adds no location. The walk only reads the traceback.
            - Every result carries the transaction id, which the payload reports as `run_id`.

        Args:
            compiled_code:
                Compiled Python code object produced by `CodegenCompiler`.
            transaction_context:
                Per-call transaction context holding the built namespace.
            run_sources:
                The room's kept run sources (run id -> source), owned by `CodegenSystem` and read here under the
                engine lock it already holds; never changed.

        Returns:
            CodegenExecutionResult: Execution result for the request.

        Raises:
            TypeError:
                If `transaction_context` is None.
            RuntimeError:
                If the transaction has no built namespace.
        """
        self.check_cleaned()
        with self._lock:
            if transaction_context is None:
                raise TypeError("transaction_context cannot be None.")
            namespace = transaction_context.namespace
            if namespace is None:
                raise RuntimeError("codegen transaction has no built namespace.")
            try:
                execution_namespace = namespace.globals_dict
                exec(compiled_code, execution_namespace, execution_namespace)
                namespace.locals_dict.clear()
                namespace.locals_dict.update(execution_namespace)
            except Exception as exc:
                line_number, run_id, line_text = self._locate_room_code_failure(exc, run_sources)
                return CodegenExecutionResult.runtime_failed(
                    frame_name=transaction_context.frame_name,
                    runtime_error="{0}: {1}".format(
                        exc.__class__.__name__,
                        exc,
                    ),
                    transaction_id=transaction_context.transaction_id,
                    output=namespace.get_output(),
                    runtime_error_line=line_number,
                    runtime_error_run_id=run_id,
                    runtime_error_line_text=line_text,
                )
            return CodegenExecutionResult.executed(
                frame_name=transaction_context.frame_name,
                result=namespace.get_result(),
                transaction_id=transaction_context.transaction_id,
                output=namespace.get_output(),
            )

    @staticmethod
    def _locate_room_code_failure(
            error: Exception,
            run_sources: Mapping[str, str],
    ) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """
        Find the innermost room-code frame of an error's traceback and quote its line.

        Contract:
            - Walks `error.__traceback__` to its end and keeps the LAST entry whose frame's `f_code.co_filename` is a
              run file name, so the innermost room-code frame wins: a failure inside melder or library code that room
              code called is located at the room line that made the call, and a failure inside a function an earlier
              run defined is located in that run's code.
            - Reads the traceback only: it neither clears nor re-raises anything.

        Args:
            error:
                The exception `exec` raised.
            run_sources:
                The room's kept run sources (run id -> source).

        Returns:
            Tuple[Optional[int], Optional[str], Optional[str]]: (line number, run id, line text). All None when the
            traceback holds no room-code frame; the text is None when that run's source is not kept or has no such
            line.
        """
        line_number: Optional[int] = None
        run_id: Optional[str] = None
        traceback_entry = error.__traceback__
        while traceback_entry is not None:
            entry_run_id = CodegenCompiler.run_id_from_filename(traceback_entry.tb_frame.f_code.co_filename)
            if entry_run_id is not None:
                line_number = traceback_entry.tb_lineno
                run_id = entry_run_id
            traceback_entry = traceback_entry.tb_next
        if run_id is None:
            return None, None, None
        return line_number, run_id, CodegenExecutor._kept_source_line(run_sources.get(run_id), line_number)

    @staticmethod
    def _kept_source_line(source: Optional[str], line_number: Optional[int]) -> Optional[str]:
        """
        Return one line of a kept run source, stripped.

        Contract:
            - Lines are counted as the compiler counts them: `\\n`, `\\r\\n` and `\\r` end a line; nothing else does.

        Args:
            source:
                The run's kept source; None when the room did not keep it (another room's run).
            line_number:
                The 1-based line number; None when the traceback entry carried none.

        Returns:
            Optional[str]: The line's text, stripped; None when the source is not kept or has no such line.
        """
        if source is None or line_number is None:
            return None
        source_lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if line_number < 1 or line_number > len(source_lines):
            return None
        return source_lines[line_number - 1].strip()

import threading
from typing import Dict, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable



class CodegenExecutionResult(Cleanable):
    """
    Internal

    Execution-layer result for one codegen request.

    Purpose:
        Represent the executor-owned outcome of `execute_codegen(...)`
        separately from validation-only reporting.

    Contract:
        - Carries acceptance state, target frame name, optional reason,
          optional validation issues, optional runtime error, and optional
          `result` payload.
        - Serializes to the current public payload shape expected by the room
          placeholder tests.

    Registration:
        MELDER KERNEL - guarded. Produced by `CodegenExecutor`.

    Subsystem Context:
        The executor-owned outcome type, paired with and deliberately separate
        from `CodegenValidationResult`.

    System Context:
        Carrying validation issues ALONGSIDE execution state is what makes a
        single execute call self-describing: a request rejected at the
        validation gate and a request that failed during execution are
        different outcomes, and a caller must be able to tell them apart from
        one result.
        Keeping the type executor-owned rather than shared preserves the same
        separation `validate_codegen` relies on - validation-only callers never
        receive runtime fields that could not have been populated.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Execution-layer result for one codegen request. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_accepted",
        "_frame_name",
        "_reason",
        "_validation_issues",
        "_runtime_error",
        "_result",
        "_transaction_id",
    ]

    def __init__(
            self,
            *,
            accepted: bool,
            frame_name: str,
            reason: Optional[str] = None,
            validation_issues: Optional[Tuple[str, ...]] = None,
            runtime_error: Optional[str] = None,
            result: Optional[object] = None,
            transaction_id: Optional[str] = None,
    ) -> None:
        """
        Initialize one execution result.

        Args:
            accepted:
                Final execution acceptance state.
            frame_name:
                Target frame name for the execution request.
            reason:
                Optional top-level execution reason.
            validation_issues:
                Optional validation issue tuple propagated into execution
                output.
            runtime_error:
                Optional runtime error summary.
            result:
                Optional final `result` value from execution.
            transaction_id:
                Optional internal transaction id.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._accepted: bool = accepted
        self._frame_name: str = frame_name
        self._reason: Optional[str] = reason
        self._validation_issues: Tuple[str, ...] = (
            tuple(validation_issues) if validation_issues else tuple()
        )
        self._runtime_error: Optional[str] = runtime_error
        self._result: Optional[object] = result
        self._transaction_id: Optional[str] = transaction_id

    def cleanup(self) -> None:
        """
        Idempotently clear execution-result state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            del self._accepted
            del self._frame_name
            del self._reason
            del self._validation_issues
            del self._runtime_error
            del self._result
            del self._transaction_id
        del self._lock

    @classmethod
    def not_implemented(
            cls,
            *,
            frame_name: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenExecutionResult":
        """
        Build the current placeholder execution result.

        Args:
            frame_name:
                Target frame name for the execution request.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenExecutionResult: Rejected placeholder execution result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_execution_not_implemented",
            transaction_id=transaction_id,
        )

    @classmethod
    def validation_failed(
            cls,
            *,
            frame_name: str,
            validation_issues: Tuple[str, ...],
            transaction_id: Optional[str] = None,
    ) -> "CodegenExecutionResult":
        """
        Build an execution result representing pre-exec validation failure.

        Args:
            frame_name:
                Target frame name for the execution request.
            validation_issues:
                Validation issue tuple to surface through execution output.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenExecutionResult: Rejected validation-failure result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_execution_validation_failed",
            validation_issues=validation_issues,
            transaction_id=transaction_id,
        )

    @classmethod
    def runtime_failed(
            cls,
            *,
            frame_name: str,
            runtime_error: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenExecutionResult":
        """
        Build an execution result representing runtime failure.

        Args:
            frame_name:
                Target frame name for the execution request.
            runtime_error:
                Runtime error summary.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenExecutionResult: Rejected runtime-failure result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_execution_runtime_failed",
            runtime_error=runtime_error,
            transaction_id=transaction_id,
        )

    @classmethod
    def executed(
            cls,
            *,
            frame_name: str,
            result: Optional[object],
            transaction_id: Optional[str] = None,
    ) -> "CodegenExecutionResult":
        """
        Build an execution result for one successful codegen execution.

        Args:
            frame_name:
                Target frame name for the execution request.
            result:
                Optional final `result` value from the namespace.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenExecutionResult: Successful execution result.
        """
        return cls(
            accepted=True,
            frame_name=frame_name,
            result=result,
            transaction_id=transaction_id,
        )

    @property
    def accepted(self) -> bool:
        """
        Return the execution acceptance state.

        Returns:
            bool: Execution acceptance state.
        """
        self.check_cleaned()
        with self._lock:
            return self._accepted

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this execution result.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def reason(self) -> Optional[str]:
        """
        Return the optional top-level execution reason.

        Returns:
            Optional[str]: Top-level execution reason when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._reason

    @property
    def validation_issues(self) -> Tuple[str, ...]:
        """
        Return the propagated validation issues for this execution result.

        Returns:
            Tuple[str, ...]: Validation issues when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._validation_issues

    @property
    def runtime_error(self) -> Optional[str]:
        """
        Return the optional runtime error summary.

        Returns:
            Optional[str]: Runtime error summary when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._runtime_error

    @property
    def result(self) -> Optional[object]:
        """
        Return the optional final execution result object.

        Returns:
            Optional[object]: Final execution result when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._result

    @property
    def transaction_id(self) -> Optional[str]:
        """
        Return the optional internal transaction identifier.

        Returns:
            Optional[str]: Internal transaction id when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._transaction_id

    def to_payload(self) -> Dict[str, object]:
        """
        Serialize this result to the current public execution payload shape.

        Returns:
            Dict[str, object]: Public execution payload.
        """
        self.check_cleaned()
        with self._lock:
            payload: Dict[str, object] = {
                "accepted": self._accepted,
                "frame_name": self._frame_name,
            }
            if self._reason is not None:
                payload["reason"] = self._reason
            if len(self._validation_issues) > 0:
                payload["validation_issues"] = self._validation_issues
            if self._runtime_error is not None:
                payload["runtime_error"] = self._runtime_error
            if self._result is not None:
                payload["result"] = self._result
            return payload

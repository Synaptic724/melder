import threading
from typing import Dict, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ICodegenValidationResult


class CodegenValidationResult(Cleanable, ICodegenValidationResult):
    """
    Internal

    Validation-layer result for one codegen request.

    Purpose:
        Represent the validator-owned outcome of `validate_codegen(...)`
        without mixing runtime execution state into the validation contract.

    Contract:
        - Carries acceptance state, target frame name, optional reason, and
          optional validation issue strings.
        - May also carry the internal transaction id for logging/history use.
        - Serializes to the public payload shape expected by current room tests.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_accepted",
        "_frame_name",
        "_reason",
        "_validation_issues",
        "_transaction_id",
    ]

    def __init__(
            self,
            *,
            accepted: bool,
            frame_name: str,
            reason: Optional[str] = None,
            validation_issues: Optional[Tuple[str, ...]] = None,
            transaction_id: Optional[str] = None,
    ) -> None:
        """
        Initialize one validation result.

        Args:
            accepted:
                Final validation decision.
            frame_name:
                Target frame name for the validation call.
            reason:
                Optional top-level validation reason.
            validation_issues:
                Optional tuple of detailed validation issue strings.
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
        self._transaction_id: Optional[str] = transaction_id

    def cleanup(self) -> None:
        """
        Idempotently clear validation-result state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._accepted = None
            self._frame_name = None
            self._reason = None
            self._validation_issues = None
            self._transaction_id = None
        self._lock = None

    @classmethod
    def not_implemented(
            cls,
            *,
            frame_name: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenValidationResult":
        """
        Build the current placeholder validation result.

        Args:
            frame_name:
                Target frame name for the validation request.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenValidationResult: Rejected placeholder result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_validation_not_implemented",
            transaction_id=transaction_id,
        )

    @classmethod
    def validation_accepted(
            cls,
            *,
            frame_name: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenValidationResult":
        """
        Build an accepted validation result.

        Args:
            frame_name:
                Target frame name for the validation request.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenValidationResult: Accepted validation result.
        """
        return cls(
            accepted=True,
            frame_name=frame_name,
            reason="codegen_validation_accepted",
            transaction_id=transaction_id,
        )

    @classmethod
    def syntax_error(
            cls,
            *,
            frame_name: str,
            message: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenValidationResult":
        """
        Build a validation result for one syntax failure.

        Args:
            frame_name:
                Target frame name for the validation request.
            message:
                Human-readable syntax error summary.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenValidationResult: Rejected syntax-failure result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_validation_failed",
            validation_issues=(message,),
            transaction_id=transaction_id,
        )

    @classmethod
    def validation_failed(
            cls,
            *,
            frame_name: str,
            message: str,
            transaction_id: Optional[str] = None,
    ) -> "CodegenValidationResult":
        """
        Build a validation result for one non-syntax validation failure.

        Args:
            frame_name:
                Target frame name for the validation request.
            message:
                Human-readable validation failure summary.
            transaction_id:
                Optional internal transaction id.

        Returns:
            CodegenValidationResult: Rejected validation-failure result.
        """
        return cls(
            accepted=False,
            frame_name=frame_name,
            reason="codegen_validation_failed",
            validation_issues=(message,),
            transaction_id=transaction_id,
        )

    @property
    def accepted(self) -> bool:
        """
        Return the validation acceptance state.

        Returns:
            bool: Validation acceptance state.
        """
        self.check_cleaned()
        with self._lock:
            return self._accepted

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this validation result.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def reason(self) -> Optional[str]:
        """
        Return the optional top-level validation reason.

        Returns:
            Optional[str]: Top-level validation reason when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._reason

    @property
    def validation_issues(self) -> Tuple[str, ...]:
        """
        Return the detailed validation issue strings.

        Returns:
            Tuple[str, ...]: Detailed validation issues.
        """
        self.check_cleaned()
        with self._lock:
            return self._validation_issues

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
        Serialize this result to the current public validation payload shape.

        Returns:
            Dict[str, object]: Public validation payload.
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
            return payload

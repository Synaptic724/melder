import threading
from typing import Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ICodegenValidationResult


class CodegenValidationReporter(Cleanable):
    """
    Internal

    Validation payload/report formatter.

    Purpose:
        Convert validator-owned `CodegenValidationResult` objects into the
        public payload shape returned by the room-facing validate command.

    Contract:
        - Does not perform validation itself.
        - Delegates payload formatting to the result object.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one validation reporter.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the validation reporter.

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

    def report(
            self,
            validation_result: ICodegenValidationResult,
    ) -> Dict[str, object]:
        """
        Convert one validation result into the public payload shape.

        Args:
            validation_result:
                Validator-owned result object.

        Returns:
            Dict[str, object]: Public validation payload.

        Raises:
            TypeError:
                If `validation_result` is None.
        """
        self.check_cleaned()
        with self._lock:
            if validation_result is None:
                raise TypeError("validation_result cannot be None.")
            return validation_result.to_payload()

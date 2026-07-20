import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
        CodegenValidationResult,
    )


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

    Threading:
        Stateless formatter.

    Registration:
        MELDER KERNEL - guarded. Used by the codegen command surface.

    Subsystem Context:
        The presentation layer between validator-owned results and the public
        payload the room command returns.

    System Context:
        "Does not perform validation itself" is the boundary that keeps the
        verdict single-sourced. A reporter that could reinterpret or re-derive
        would create a second place where acceptance is decided, and the two
        could disagree.
        Separating formatting from judgement also lets the public payload shape
        evolve for agents and tooling without touching the validator that
        decides what is safe.
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
            validation_result: CodegenValidationResult,
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

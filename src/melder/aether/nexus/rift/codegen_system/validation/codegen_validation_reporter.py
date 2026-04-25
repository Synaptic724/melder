from typing import Dict

from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenValidationReporter:
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

    __slots__ = []

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
        if validation_result is None:
            raise TypeError("validation_result cannot be None.")
        return validation_result.to_payload()


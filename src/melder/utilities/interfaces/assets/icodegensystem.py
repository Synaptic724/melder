from typing import runtime_checkable, Protocol, Dict, Tuple

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class ICodegenSystem(ICleanable, Protocol):
    """
    Interface for the room-owned internal codegen system.
    """

    @property
    def codegen_system_id(self) -> str:
        """
        Return the stable codegen-system identifier.
        """
        ...

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.
        """
        ...

    def validate_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> ICodegenValidationResult:
        """
        Validate one codegen request.
        """
        ...

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> ICodegenExecutionResult:
        """
        Execute one codegen request.
        """
        ...

    def validate_codegen_request(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Tuple[ICodegenTransactionContext, ICodegenValidationResult]:
        """
        Validate one codegen request and return context plus validation result.
        """
        ...

    def execute_codegen_request(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Tuple[ICodegenTransactionContext, ICodegenExecutionResult]:
        """
        Execute one codegen request and return context plus execution result.
        """
        ...

    def report_validation_result(
            self,
            validation_result: ICodegenValidationResult,
    ) -> Dict[str, object]:
        """
        Convert one validation result into the public payload shape.
        """
        ...

from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.execution.codegen_execution_result import CodegenExecutionResult
from melder.utilities.interfaces.icodegensystem import ICodegenSystem
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import CodegenValidationResult


class CodegenControlSurface:
    """
    Internal

    Runtime wrapper for the `codegen` namespace object.

    Purpose:
        Expose recursive codegen entrypoints without leaking the raw internal
        `CodegenSystem` object directly into the execution namespace.

    Contract:
        - Applies the current recursive-codegen permission at runtime.
        - Defaults recursive calls to the current transaction frame when the
          caller omits `frame_name`.
        - Returns public payload dictionaries instead of internal result
          objects.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_codegen_system",
        "_default_frame_name",
        "_recursive_codegen_allowed",
    ]

    def __init__(
            self,
            *,
            codegen_system: ICodegenSystem,
            default_frame_name: str,
            recursive_codegen_allowed: bool,
    ) -> None:
        """
        Initialize one codegen namespace control surface.

        Args:
            codegen_system:
                Room-owned internal codegen system.
            default_frame_name:
                Frame name to use when recursive calls omit `frame_name`.
            recursive_codegen_allowed:
                True when recursive codegen is permitted.

        Returns:
            None.
        """
        self._codegen_system = codegen_system
        self._default_frame_name = default_frame_name
        self._recursive_codegen_allowed = recursive_codegen_allowed

    def validate_codegen(
            self,
            code: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Validate generated code recursively through the wrapped system.

        Args:
            code:
                Generated Python source to validate.
            frame_name:
                Optional target frame name. Defaults to the current frame.

        Returns:
            Dict[str, object]: Public validation payload.

        Raises:
            RuntimeError:
                If recursive codegen is not allowed.
        """
        self._require_recursive_codegen_allowed()
        resolved_frame_name = (
            frame_name if frame_name is not None else self._default_frame_name
        )
        validation_result: CodegenValidationResult = (
            self._codegen_system.validate_codegen(
                code,
                frame_name=resolved_frame_name,
            )
        )
        return self._codegen_system.report_validation_result(validation_result)

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Execute generated code recursively through the wrapped system.

        Args:
            code:
                Generated Python source to execute.
            frame_name:
                Optional target frame name. Defaults to the current frame.

        Returns:
            Dict[str, object]: Public execution payload.

        Raises:
            RuntimeError:
                If recursive codegen is not allowed.
        """
        self._require_recursive_codegen_allowed()
        resolved_frame_name = (
            frame_name if frame_name is not None else self._default_frame_name
        )
        execution_result: CodegenExecutionResult = (
            self._codegen_system.execute_codegen(
                code,
                frame_name=resolved_frame_name,
            )
        )
        return execution_result.to_payload()

    def _require_recursive_codegen_allowed(self) -> None:
        """
        Raise when recursive codegen is not allowed for this namespace.

        Returns:
            None.

        Raises:
            RuntimeError:
                If recursive codegen is not allowed.
        """
        if self._recursive_codegen_allowed:
            return
        raise RuntimeError(
            "Recursive codegen is not allowed in this codegen mode."
        )

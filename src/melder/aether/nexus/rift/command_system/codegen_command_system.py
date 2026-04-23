from typing import Dict, Tuple

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)


class CodegenCommandSystem(CommandSystem):
    """
    Internal

    Codegen-room command surface.

    Purpose:
        Preserve the shared broad runtime command behavior for
        `CodegenRiftSpace`.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Does not narrow raw runtime-object access beyond the shared ACL
          checks already enforced by the base class.
        - Adds only the placeholder codegen seams in this slice; AST
          validation and compile/exec behavior are intentionally not active yet.
    """

    _CODEGEN_COMMAND_METHOD_NAMES: Tuple[str, ...] = (
        "validate_codegen",
        "execute_codegen",
    )

    def validate_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Dict[str, object]:
        """
        Placeholder validation surface for generated Python code.

        Purpose:
            Reserve the public codegen validation seam while the AST validation
            engine is still being designed.

        Contract:
            - Does not parse, compile, or execute the supplied code yet.
            - Returns an explicit rejected payload so callers cannot mistake
              the placeholder for a working validator.
            - Requires non-empty `code` and `frame_name` to preserve the future
              call contract.

        Args:
            code:
                Generated Python source to validate later.
            frame_name:
                Target frame whose codegen ACL/namespace policy will later be
                applied.

        Returns:
            Dict[str, object]: Rejected placeholder validation payload.

        Raises:
            ValueError: If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        return {
            "accepted": False,
            "reason": "codegen_validation_not_implemented",
            "frame_name": frame_name,
        }

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Dict[str, object]:
        """
        Placeholder execution surface for generated Python code.

        Purpose:
            Reserve the single public codegen execution seam while preserving
            the permanent one-command model: generated Python will later be
            AST-validated, compiled, and executed through this method.

        Contract:
            - Does not parse, compile, or execute the supplied code yet.
            - Returns an explicit rejected payload so callers cannot mistake
              the placeholder for a working exec surface.
            - Requires non-empty `code` and `frame_name` to preserve the future
              call contract.

        Args:
            code:
                Generated Python source to execute later.
            frame_name:
                Target frame whose codegen ACL/namespace policy will later be
                applied.

        Returns:
            Dict[str, object]: Rejected placeholder execution payload.

        Raises:
            ValueError: If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        return {
            "accepted": False,
            "reason": "codegen_execution_not_implemented",
            "frame_name": frame_name,
        }

    def list_supported_command_methods(self) -> Tuple[str, ...]:
        """
        Return the public command methods supported by codegen rooms.

        Purpose:
            Preserve the full shared capability-grade command surface and append
            the placeholder codegen seams without inheriting from
            `CapabilityCommandSystem`.

        Returns:
            Tuple[str, ...]: Shared command names plus codegen placeholder
            method names.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_supported_command_methods",
                frame_name=None,
        ):
            return self._list_supported_command_methods_tuple() + (
                self._CODEGEN_COMMAND_METHOD_NAMES
            )

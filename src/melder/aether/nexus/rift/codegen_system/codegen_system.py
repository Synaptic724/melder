import threading
from typing import Any, Dict, Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_builder import (
    CodegenNamespaceBuilder,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_reporter import (
    CodegenValidationReporter,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validator import (
    CodegenValidator,
)
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CodegenSystem(Cleanable):
    """
    Internal

    Root codegen orchestration object.

    Purpose:
        Provide the real internal runtime owner behind the public codegen room
        facade without absorbing validator, namespace-builder, executor, or
        observability responsibilities prematurely.

    Contract:
        - Owned by one `CodegenRiftSpace`.
        - Owns root transaction creation for validate/execute calls.
        - Resolves the optional `CodegenProjection` when the owning Rift can
          supply one.
        - Builds the current foundation namespace configuration and placeholder
          namespace objects for the first slice.
        - Returns validator-owned and executor-owned result types while the
          full validator/executor subsystems remain unimplemented.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_space_id",
        "_lock",
        "_rift",
        "_space",
        "_validator",
        "_validation_reporter",
        "_namespace_builder",
    ]

    def __init__(self, *, rift: Any, space: Any) -> None:
        """
        Initialize one root codegen system.

        Args:
            rift:
                Owning `Rift` that may later provide codegen projections.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            None.

        Raises:
            TypeError:
                If `rift` or `space` is None.
        """
        super().__init__()
        if rift is None:
            raise TypeError("rift cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._owner_space_id: str = space.space_id
        self._lock: threading.RLock = threading.RLock()
        self._rift: Any = rift
        self._space: Any = space
        self._validator: CodegenValidator = CodegenValidator()
        self._validation_reporter: CodegenValidationReporter = (
            CodegenValidationReporter()
        )
        self._namespace_builder: CodegenNamespaceBuilder = CodegenNamespaceBuilder()

    def cleanup(self) -> None:
        """
        Idempotently cleanup codegen-system-owned references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._owner_space_id = None
            self._rift = None
            self._space = None
            self._validator = None
            self._validation_reporter = None
            self._namespace_builder = None
            self._id = None
        self._lock = None

    @property
    def codegen_system_id(self) -> str:
        """
        Return the stable codegen-system identifier.

        Returns:
            str: Stable codegen-system id.
        """
        self.check_cleaned()
        return self._id

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.

        Returns:
            str: Owning room id.
        """
        self.check_cleaned()
        return self._owner_space_id

    def validate_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> CodegenValidationResult:
        """
        Build the current placeholder validation result through the new engine.

        Args:
            code:
                Generated Python source to validate.
            frame_name:
                Target frame name for the request.

        Returns:
            CodegenValidationResult: Placeholder validation result.

        Raises:
            ValueError:
                If `code` or `frame_name` is empty.
        """
        context = self._build_transaction_context(
            code,
            frame_name=frame_name,
        )
        return self._validator.validate(context)

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> CodegenExecutionResult:
        """
        Build the current placeholder execution result through the new engine.

        Args:
            code:
                Generated Python source to execute.
            frame_name:
                Target frame name for the request.

        Returns:
            CodegenExecutionResult: Placeholder execution result.

        Raises:
            ValueError:
                If `code` or `frame_name` is empty.
        """
        context = self._build_transaction_context(
            code,
            frame_name=frame_name,
        )
        validation_result = self._validator.validate(context)
        if (
                not validation_result.accepted
                and validation_result.reason != "codegen_validation_not_implemented"
        ):
            return CodegenExecutionResult.validation_failed(
                frame_name=frame_name,
                validation_issues=validation_result.validation_issues,
                transaction_id=context.transaction_id,
            )
        namespace = self._build_namespace(context)
        context.set_namespace(namespace)
        return CodegenExecutionResult.not_implemented(
            frame_name=frame_name,
            transaction_id=context.transaction_id,
        )

    def report_validation_result(
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
        """
        return self._validation_reporter.report(validation_result)

    def _build_transaction_context(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> CodegenTransactionContext:
        """
        Build one per-call transaction context for the root slice.

        Args:
            code:
                Raw generated Python source.
            frame_name:
                Target frame name for the request.

        Returns:
            CodegenTransactionContext: Per-call transaction context.

        Raises:
            ValueError:
                If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        projection = self._try_get_codegen_projection(frame_name)
        namespace_configuration = self._build_default_namespace_configuration(
            frame_name=frame_name,
            projection=projection,
        )
        return CodegenTransactionContext(
            frame_name=frame_name,
            code=code,
            projection=projection,
            namespace_configuration=namespace_configuration,
            metadata={
                "owner_space_id": self._owner_space_id,
            },
        )

    def _build_default_namespace_configuration(
            self,
            *,
            frame_name: str,
            projection: Optional[CodegenProjection],
    ) -> CodegenNamespaceConfiguration:
        """
        Build the current stable default namespace configuration.

        Args:
            frame_name:
                Target frame name for the request.
            projection:
                Optional resolved codegen projection.

        Returns:
            CodegenNamespaceConfiguration: Default namespace configuration.
        """
        return CodegenNamespaceConfiguration.create_default(
            frame_name=frame_name,
            metadata={
                "has_projection": projection is not None,
            },
        )

    def _build_namespace(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> CodegenNamespace:
        """
        Build one live namespace for the current transaction context.

        Args:
            transaction_context:
                Per-call transaction context.

        Returns:
            CodegenNamespace: Built live namespace.

        Raises:
            TypeError:
                If `transaction_context` is None.
        """
        if transaction_context is None:
            raise TypeError("transaction_context cannot be None.")
        namespace_configuration = transaction_context.namespace_configuration
        if namespace_configuration is None:
            namespace_configuration = self._build_default_namespace_configuration(
                frame_name=transaction_context.frame_name,
                projection=transaction_context.projection,
            )
            transaction_context.set_namespace_configuration(namespace_configuration)
        return self._namespace_builder.build(
            namespace_configuration,
            rift=self._rift,
            space=self._space,
        )

    def _try_get_codegen_projection(
            self,
            frame_name: str,
    ) -> Optional[CodegenProjection]:
        """
        Best-effort resolve one codegen projection from the owning Rift.

        Purpose:
            Allow the root slice to consume a projection when the owning Rift
            actually implements the codegen projection seam, while still
            tolerating detached/unit-test doubles that do not carry that seam
            yet.

        Args:
            frame_name:
                Target frame name for the request.

        Returns:
            Optional[CodegenProjection]: Resolved projection when available.
        """
        try:
            return self._rift._get_required_codegen_projection(frame_name)
        except AttributeError:
            return None
        except KeyError:
            return None
        except ValueError:
            return None

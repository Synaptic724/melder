import threading
from typing import TYPE_CHECKING, Dict, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.nexus.rift.codegen_system.execution.codegen_compiler import (
    CodegenCompiler,
)
from melder.nexus.rift.codegen_system.execution.codegen_executor import (
    CodegenExecutor,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_builder import (
    CodegenNamespaceBuilder,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.nexus.rift.codegen_system.observability.codegen_monitor import (
    CodegenMonitor,
)
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.nexus.rift.codegen_system.validation.codegen_validation_reporter import (
    CodegenValidationReporter,
)
from melder.nexus.rift.codegen_system.validation.codegen_validator import (
    CodegenValidator,
)
from melder.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

if TYPE_CHECKING:
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


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
        - Builds the current foundation namespace configuration and live
          namespace objects.
        - Publishes lightweight codegen lifecycle events through the owning
          room event system instead of owning a local event queue or cache.
        - Returns validator-owned and executor-owned result types without
          owning room-memory emission itself.

    Registration:
        MELDER KERNEL - guarded. Owned by one `CodegenRiftSpace` and attached to
        its `CodegenCommandSystem` during room init.

    Subsystem Context:
        The real engine beneath the codegen command facade. It owns per-call
        `CodegenTransactionContext`, `CodegenValidator`,
        `CodegenNamespaceBuilder`, `CodegenCompiler`, `CodegenExecutor`, and
        `CodegenMonitor`.

    System Context:
        The ordering invariant is the safety property: VALIDATE BEFORE EXECUTE,
        and build the live namespace ONLY AFTER validation is accepted. Building
        the namespace first would materialize the execution environment for code
        that was about to be rejected, and any side effect of that construction
        would have escaped the validation gate.
        Publishing lifecycle events through the OWNING ROOM's event system
        rather than owning a local queue or cache keeps a single event ordering
        per room - a private queue would let codegen events interleave
        inconsistently with the room's other events.
        Returning validator-owned and executor-owned result types WITHOUT owning
        room-memory emission is the same layering discipline: this engine
        produces results, and `CodegenCommandSystem` decides what gets recorded,
        so the accountability record has one author.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Root codegen orchestration object. Melder kernel machinery: read it to "
        "understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_space_id",
        "_lock",
        "_rift",
        "_space",
        "_validator",
        "_validation_reporter",
        "_namespace_builder",
        "_compiler",
        "_executor",
        "_monitor",
    ]

    def __init__(self, *, rift: Rift, space: CodegenRiftSpace) -> None:
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
        self._rift: Rift = rift
        self._space: CodegenRiftSpace = space
        self._validator: CodegenValidator = CodegenValidator()
        self._validation_reporter: CodegenValidationReporter = (
            CodegenValidationReporter()
        )
        self._namespace_builder: CodegenNamespaceBuilder = CodegenNamespaceBuilder()
        self._compiler: CodegenCompiler = CodegenCompiler()
        self._executor: CodegenExecutor = CodegenExecutor()
        self._monitor: CodegenMonitor = CodegenMonitor(space=space)

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
            self._monitor.cleanup()

            del self._owner_space_id
            del self._rift
            del self._space
            del self._validator
            del self._validation_reporter
            del self._namespace_builder
            del self._compiler
            del self._executor
            del self._monitor
            del self._id
        del self._lock

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
        Validate one codegen request through the internal engine.

        Args:
            code:
                Generated Python source to validate.
            frame_name:
                Target frame name for the request.

        Returns:
            CodegenValidationResult: Validator-owned result for the request.

        Raises:
            ValueError:
                If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        with self._lock:
            _, validation_result = self.validate_codegen_request(
                code,
                frame_name=frame_name,
            )
            return validation_result

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> CodegenExecutionResult:
        """
        Execute one codegen request through the internal engine.

        Args:
            code:
                Generated Python source to execute.
            frame_name:
                Target frame name for the request.

        Returns:
            CodegenExecutionResult: Executor-owned result for the request.

        Raises:
            ValueError:
                If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        with self._lock:
            _, execution_result = self.execute_codegen_request(
                code,
                frame_name=frame_name,
            )
            return execution_result

    def validate_codegen_request(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Tuple[CodegenTransactionContext, CodegenValidationResult]:
        """
        Validate one codegen request and return both context and result.

        Purpose:
            Let the room-facing command surface reuse the exact transaction
            context for room-memory emission while the internal engine keeps
            ownership of validation and event publication.

        Args:
            code:
                Generated Python source to validate.
            frame_name:
                Target frame name for the request.

        Returns:
            Tuple[CodegenTransactionContext, CodegenValidationResult]:
                Shared transaction context plus validator-owned result.
        """
        self.check_cleaned()
        with self._lock:
            context = self._build_transaction_context(
                code,
                frame_name=frame_name,
            )
            self._monitor.on_validation_started(context)
            validation_result = self._validator.validate(context)
            self._monitor.on_validation_finished(context, validation_result)
            return context, validation_result

    def execute_codegen_request(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Tuple[CodegenTransactionContext, CodegenExecutionResult]:
        """
        Execute one codegen request and return both context and result.

        Purpose:
            Let the room-facing command surface reuse the exact transaction
            context for room-memory emission while the internal engine keeps
            ownership of validation, execution, and event publication.

        Args:
            code:
                Generated Python source to execute.
            frame_name:
                Target frame name for the request.

        Returns:
            Tuple[CodegenTransactionContext, CodegenExecutionResult]:
                Shared transaction context plus executor-owned result.
        """
        self.check_cleaned()
        with self._lock:
            context = self._build_transaction_context(
                code,
                frame_name=frame_name,
            )
            self._monitor.on_execution_started(context)
            self._monitor.on_validation_started(context)
            validation_result = self._validator.validate(context)
            self._monitor.on_validation_finished(context, validation_result)
            if not validation_result.accepted:
                execution_result = CodegenExecutionResult.validation_failed(
                    frame_name=frame_name,
                    validation_issues=validation_result.validation_issues,
                    transaction_id=context.transaction_id,
                )
                self._monitor.on_execution_finished(context, execution_result)
                return context, execution_result
            namespace = self._build_namespace(context)
            context.set_namespace(namespace)
            compiled_code = self._compiler.compile(context)
            execution_result = self._executor.execute(compiled_code, context)
            self._monitor.on_execution_finished(context, execution_result)
            return context, execution_result

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
        self.check_cleaned()
        with self._lock:
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
        imports_enabled = False
        allowed_import_module_roots: Tuple[str, ...] = tuple()
        denied_import_module_roots: Tuple[str, ...] = tuple()
        denied_builtin_names: Tuple[str, ...] = (
            "__import__",
            "breakpoint",
            "compile",
            "dir",
            "eval",
            "exec",
            "getattr",
            "globals",
            "input",
            "locals",
            "setattr",
            "delattr",
            "vars",
        )
        allow_unsafe_reflection = False
        allow_dunder_access = False
        if projection is not None:
            compiled_access_surface = projection.compiled_access_surface
            imports_enabled = compiled_access_surface.codegen_imports_enabled
            allowed_import_module_roots = (
                compiled_access_surface.allowed_import_module_roots
            )
            denied_import_module_roots = (
                compiled_access_surface.denied_import_module_roots
            )
            denied_builtin_names = compiled_access_surface.denied_builtin_names
            allow_unsafe_reflection = (
                compiled_access_surface.codegen_unsafe_reflection_allowed
            )
            allow_dunder_access = (
                compiled_access_surface.codegen_dunder_access_allowed
            )
            allow_recursive_codegen = (
                compiled_access_surface.codegen_recursive_codegen_allowed
            )
        else:
            allow_recursive_codegen = False
        return CodegenNamespaceConfiguration.create_default(
            frame_name=frame_name,
            imports_enabled=imports_enabled,
            allowed_import_module_roots=allowed_import_module_roots,
            denied_import_module_roots=denied_import_module_roots,
            denied_builtin_names=denied_builtin_names,
            allow_unsafe_reflection=allow_unsafe_reflection,
            allow_dunder_access=allow_dunder_access,
            allow_recursive_codegen=allow_recursive_codegen,
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

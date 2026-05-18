from typing import Dict, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.aether.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.interfaces.icodegenexecutionresult import ICodegenExecutionResult
from melder.utilities.interfaces.icodegenriftspace import ICodegenRiftSpace
from melder.utilities.interfaces.icodegensystem import ICodegenSystem
from melder.utilities.interfaces.icodegentransactioncontext import ICodegenTransactionContext
from melder.utilities.interfaces.icodegenvalidationresult import ICodegenValidationResult
from melder.utilities.interfaces.irift import IRift
from melder.utilities.interfaces.iworkstation import IWorkstation


class CodegenCommandSystem(CommandSystem):
    """
    Internal

    Codegen-room command surface.

    Purpose:
        Own the slim runtime-helper plus codegen execution surface for
        `CodegenRiftSpace`.

    Contract:
        - Inherits shared selected-target, ACL, and workstation behavior from
          `CommandSystem`.
        - Owns the explicitly selected conduit/runtime helper subset for
          codegen work without inheriting the full capability command surface.
        - Routes `validate_codegen(...)` and `execute_codegen(...)` into the
          attached `CodegenSystem`.
        - Emits full-source top-level codegen memory records through the
          owning room's `RiftMemorySystem` instead of using the generic
          command-memory metadata shape.
    """

    __melder_internal__ = _mrg.sentinel
    _CODEGEN_RUNTIME_HELPER_METHOD_NAMES: Tuple[str, ...] = (
        "get_conduit_cloud",
        "get_conduit_by_id",
        "get_conduit_by_name",
        "list_conduit_ids",
        "list_conduit_names",
        "count_conduits",
        "find_conduit_id_by_name",
        "list_clusters",
        "get_links",
        "get_contracted_conduits",
        "get_spell_in_contracts",
        "get_spells_in_contract_by_conduit_name",
        "describe_spells_in_conduit",
        "find_spell_id",
        "find_spell_key",
        "get_spell_permissions",
        "get_target_attribute",
        "get_target_method",
        "execute_target_method",
    )
    _CODEGEN_COMMAND_METHOD_NAMES: Tuple[str, ...] = (
        "validate_codegen",
        "execute_codegen",
    )

    __slots__ = CommandSystem.__slots__ + [
        "_codegen_system",
    ]

    def __init__(
            self,
            *,
            rift: IRift,
            space: ICodegenRiftSpace,
            workstation: IWorkstation,
            codegen_system: Optional[ICodegenSystem] = None,
    ) -> None:
        """
        Initialize one codegen-room command surface.

        Args:
            rift:
                Owning `Rift`.
            space:
                Owning `CodegenRiftSpace`.
            workstation:
                Room-local workstation owned by the same room.
            codegen_system:
                Optional attached `CodegenSystem`. When omitted, the room may
                attach it after room initialization completes.

        Returns:
            None.
        """
        super().__init__(
            rift=rift,
            space=space,
            workstation=workstation,
        )
        self._codegen_system: Optional[ICodegenSystem] = codegen_system

    def cleanup(self) -> None:
        """
        Idempotently clear codegen-command references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._codegen_system = None
        super().cleanup()

    def attach_codegen_system(self, codegen_system: ICodegenSystem) -> None:
        """
        Attach the room-owned `CodegenSystem` after room initialization.

        Args:
            codegen_system:
                Root codegen system owned by the same room.

        Returns:
            None.

        Raises:
            TypeError:
                If `codegen_system` is None.
        """
        self.check_cleaned()
        if codegen_system is None:
            raise TypeError("codegen_system cannot be None.")
        with self._lock:
            self._codegen_system = codegen_system

    def get_conduit_cloud(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the live conduit cloud for one hosted frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit-cloud object for the resolved frame.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_cloud",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_conduit_cloud")
            self._assert_frame_command_enabled(resolved_frame_name)
            return self._aether.get_conduit_cloud(resolved_frame_name)

    def get_conduit_by_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live conduit object by id, including lesser-conduit fallback.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_by_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            return self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )

    def get_conduit_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live root/normal conduit object by name.

        Args:
            conduit_name:
                Conduit name to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_by_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_conduit_by_name")
            self._assert_frame_command_enabled(resolved_frame_name)
            conduit_id = self._get_required_published_conduit_id_by_name(
                conduit_name,
                frame_name=resolved_frame_name,
            )
            self._assert_conduit_command_enabled(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return self._aether.get_conduit_by_name(
                conduit_name,
                resolved_frame_name,
            )

    def list_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit ids for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Published command-enabled conduit ids.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_conduit_ids",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return tuple(record.conduit_id for record in conduit_records)

    def list_conduit_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit names for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Published command-enabled conduit names.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_conduit_names",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return tuple(
                record.payload.conduit_name
                for record in conduit_records
                if record.payload.conduit_name is not None
            )

    def count_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of command-enabled published conduits for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            int: Number of published command-enabled conduits.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="count_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return len(conduit_records)

    def find_conduit_id_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Return the published command-enabled conduit id for one conduit name.

        Args:
            conduit_name:
                Conduit name to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="find_conduit_id_by_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            try:
                conduit_id = self._get_required_published_conduit_id_by_name(
                    conduit_name,
                    frame_name=resolved_frame_name,
                )
            except ValueError as exc:
                if "was not found" in str(exc):
                    return None
                raise
            compiled_access_surface = self._get_required_compiled_access_surface(
                resolved_frame_name
            )
            if conduit_id in compiled_access_surface.enabled_conduit_ids:
                return conduit_id
            return None

    def list_clusters(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the cluster names visible from one conduit.

        Args:
            conduit_id:
                Conduit id whose cluster membership view should be queried.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Cluster names visible from the conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_clusters",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.list_clusters())

    def get_links(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the current peer links for one conduit.

        Args:
            conduit_id:
                Conduit id whose peer links should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[object, ...]: Linked conduit objects.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_links",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.get_links())

    def get_contracted_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the contracted peer conduits for one conduit.

        Args:
            conduit_id:
                Source conduit id whose contracted peers should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime contracted conduit collection.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_contracted_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_contracted_conduits()

    def get_spell_in_contracts(
            self,
            conduit_id: str,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one contracted spell lookup result from a conduit.

        Args:
            conduit_id:
                Source conduit id whose contract view should be queried.
            spell_id:
                Current spell id to resolve inside the conduit's contract set.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime spell-in-contract lookup result.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_in_contracts",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spell_in_contracts(spell_id)

    def get_spells_in_contract_by_conduit_name(
            self,
            conduit_id: str,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return contracted spell data keyed by peer conduit name.

        Args:
            conduit_id:
                Source conduit id whose contract table should be queried.
            conduit_name:
                Peer conduit name whose contract spell data should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime contract spell payload for the peer name.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spells_in_contract_by_conduit_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spells_in_contract_by_conduit_name(conduit_name)

    def validate_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Dict[str, object]:
        """
        Validate generated Python code through the attached codegen system.

        Purpose:
            Keep the public room-facing validation seam on the command surface
            while delegating real validation work into the internal
            `CodegenSystem`.

        Contract:
            - Delegates validation into the attached `CodegenSystem`.
            - Emits one full-source codegen memory record for the completed
              top-level validation action when room memory is enabled.
            - Requires non-empty `code` and `frame_name` to preserve the future
              call contract.

        Args:
            code:
                Generated Python source to validate later.
            frame_name:
                Target frame whose codegen ACL/namespace policy will later be
                applied.

        Returns:
            Dict[str, object]: Public validation payload.

        Raises:
            ValueError: If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._entered_action_hook_scope_if_available(
                category="codegen",
                action_name="validate_codegen",
        ):
            rift_gate = self._begin_command_action()
            transaction_context: Optional[ICodegenTransactionContext] = None
            validation_result: Optional[ICodegenValidationResult] = None
            try:
                with self._lock:
                    codegen_system = self._require_codegen_system()
                    transaction_context, validation_result = (
                        codegen_system.validate_codegen_request(
                            code,
                            frame_name=frame_name,
                        )
                    )
                    return codegen_system.report_validation_result(validation_result)
            finally:
                if rift_gate is not None:
                    rift_gate.unregister_ticket()
                if (
                        transaction_context is not None
                        and validation_result is not None
                ):
                    self._emit_codegen_memory_if_enabled(
                        action_name="validate_codegen",
                        transaction_context=transaction_context,
                        validation_result=validation_result,
                    )

    def execute_codegen(
            self,
            code: str,
            *,
            frame_name: str,
    ) -> Dict[str, object]:
        """
        Execute generated Python code through the attached codegen system.

        Purpose:
            Keep the public room-facing execution seam on the command surface
            while delegating real validation, namespace construction,
            compile/exec, and lifecycle event publication into the internal
            `CodegenSystem`.

        Contract:
            - Delegates execution into the attached `CodegenSystem`.
            - Emits one full-source codegen memory record for the completed
              top-level execution action when room memory is enabled.
            - Requires non-empty `code` and `frame_name` to preserve the future
              call contract.

        Args:
            code:
                Generated Python source to execute later.
            frame_name:
                Target frame whose codegen ACL/namespace policy will later be
                applied.

        Returns:
            Dict[str, object]: Public execution payload.

        Raises:
            ValueError: If `code` or `frame_name` is empty.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code cannot be empty.")
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._entered_action_hook_scope_if_available(
                category="codegen",
                action_name="execute_codegen",
        ):
            rift_gate = self._begin_command_action()
            transaction_context: Optional[ICodegenTransactionContext] = None
            execution_result: Optional[ICodegenExecutionResult] = None
            try:
                with self._lock:
                    codegen_system = self._require_codegen_system()
                    transaction_context, execution_result = (
                        codegen_system.execute_codegen_request(
                            code,
                            frame_name=frame_name,
                        )
                    )
                    return execution_result.to_payload()
            finally:
                if rift_gate is not None:
                    rift_gate.unregister_ticket()
                if (
                        transaction_context is not None
                        and execution_result is not None
                ):
                    self._emit_codegen_memory_if_enabled(
                        action_name="execute_codegen",
                        transaction_context=transaction_context,
                        execution_result=execution_result,
                    )

    def _emit_codegen_memory_if_enabled(
            self,
            *,
            action_name: str,
            transaction_context: ICodegenTransactionContext,
            validation_result: Optional[ICodegenValidationResult] = None,
            execution_result: Optional[ICodegenExecutionResult] = None,
    ) -> None:
        """
        Emit one full-source codegen memory record when room memory is enabled.

        Args:
            action_name:
                Stable public action name.
            transaction_context:
                Shared transaction context for the completed action.
            validation_result:
                Optional validation result for `validate_codegen(...)`.
            execution_result:
                Optional execution result for `execute_codegen(...)`.

        Returns:
            None.

        Raises:
            ValueError:
                If neither result object is supplied.
        """
        memory_system = self._get_memory_system_if_available()
        if memory_system is None or not memory_system.memory_enabled:
            return
        if validation_result is None and execution_result is None:
            raise ValueError(
                "One codegen result object must be provided for memory emission."
            )
        metadata: Dict[str, object] = {
            "surface": "codegen",
            "command_system_id": self._id,
            "owner_space_id": self._owner_space_id,
            "transaction_id": transaction_context.transaction_id,
            "code": transaction_context.code,
            "code_hash": transaction_context.code_hash,
        }
        if validation_result is not None:
            metadata["phase"] = "validate"
            metadata["accepted"] = validation_result.accepted
            if validation_result.reason is not None:
                metadata["reason"] = validation_result.reason
            if len(validation_result.validation_issues) > 0:
                metadata["validation_issues"] = validation_result.validation_issues
        if execution_result is not None:
            metadata["phase"] = "execute"
            metadata["accepted"] = execution_result.accepted
            metadata["result_present"] = execution_result.result is not None
            if execution_result.reason is not None:
                metadata["reason"] = execution_result.reason
            if len(execution_result.validation_issues) > 0:
                metadata["validation_issues"] = execution_result.validation_issues
            if execution_result.runtime_error is not None:
                metadata["runtime_error"] = execution_result.runtime_error
        memory_system.create_and_emit_memory(
            frame_name=transaction_context.frame_name,
            action_name=action_name,
            metadata=metadata,
        )

    def _require_codegen_system(self) -> ICodegenSystem:
        """
        Return the attached room-owned `CodegenSystem`.

        Returns:
            CodegenSystem: Attached codegen system.

        Raises:
            RuntimeError:
                If the room has not attached a codegen system yet.
        """
        if self._codegen_system is None:
            raise RuntimeError("codegen system is not attached.")
        return self._codegen_system

    def list_supported_command_methods(self) -> Tuple[str, ...]:
        """
        Return the public command methods supported by codegen rooms.

        Purpose:
            Preserve the explicitly approved shared frame-navigation surface,
            append the selected codegen runtime helpers, and then append the
            codegen execution seams.

        Returns:
            Tuple[str, ...]: Shared frame-navigation names plus selected
                codegen helper and execution method names.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_supported_command_methods",
                frame_name=None,
        ):
            return (
                ("link_frame", "get_nexus_frame")
                + self._CODEGEN_RUNTIME_HELPER_METHOD_NAMES
                + self._CODEGEN_COMMAND_METHOD_NAMES
            )

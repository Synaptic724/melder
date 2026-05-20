import hashlib
import pickle
from typing import Any, Dict, List, Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.interfaces.ispell import ISpell


@mypyc_attr(native_class=True)
class SharedCompilerExecutions:
    """
    Shared static execution helper surface for compiler phases.

    Purpose:
        Provide one explicit compiler-side home for execution helpers that are
        shared across multiple extracted compiler phase classes.

    Contract:
        - Slot-only static helper surface with no `__init__`.
        - Does not own compiler state, runtime collaborators, or lifecycle.
        - Exists to hold shared execution helpers used by extracted phase
          classes.
    """

    __slots__ = ()

    @staticmethod
    def ensure_codegen_ir(
            artifact: SpellCompilerArtifact,
    ) -> Dict[str, Any]:
        """
        Return the compiler artifact codegen IR payload, creating it when needed.
        """
        if artifact._codegen_ir is None:
            artifact._codegen_ir = {
                "phase2_5": {},
                "phase8_11": {},
                "signatures": {},
            }
        return artifact._codegen_ir

    @staticmethod
    def serialize_codegen_signature_part(part: Any) -> bytes:
        """
        Serialize one signature part into deterministic bytes.
        """
        part_type = type(part)
        if (
                part_type is dict
                or part_type is tuple
                or part_type is list
                or part_type is set
                or part_type is frozenset
        ):
            try:
                encoded_part_from_collection: bytes = pickle.dumps(part, protocol=5)
                return encoded_part_from_collection
            except (pickle.PickleError, TypeError, AttributeError):
                return repr(part).encode("utf-8")
        if part is None:
            return b"N"
        if part_type is bool:
            return b"B1" if part else b"B0"
        if part_type is int:
            return b"I" + str(part).encode("ascii")
        if part_type is float:
            return b"F" + repr(part).encode("ascii")
        if part_type is str:
            part_str: str = part
            return b"S" + part_str.encode("utf-8")
        if part_type is bytes:
            part_bytes: bytes = part
            return b"Y" + part_bytes
        if part_type is bytearray:
            return b"Y" + bytes(part)
        try:
            encoded_part_from_object: bytes = pickle.dumps(part, protocol=5)
            return encoded_part_from_object
        except (pickle.PickleError, TypeError, AttributeError):
            return repr(part).encode("utf-8")

    @staticmethod
    def hash_codegen_signature(*parts: Any) -> str:
        """
        Build a deterministic signature from primitive IR parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(
                SharedCompilerExecutions.serialize_codegen_signature_part(part)
            )
            digest.update(b"|")
        return digest.hexdigest()

    @staticmethod
    def socket_row_sort_key(
            socket_row: Tuple[str, str, int, str],
    ) -> Tuple[str, int, str, str]:
        """
        Build a deterministic sort key for socket schema rows.
        """
        return (
            socket_row[0],
            socket_row[2],
            socket_row[1],
            socket_row[3],
        )

    @staticmethod
    def build_phase5_socket_rows(
            artifact: SpellCompilerArtifact,
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase5 socket references.
        """
        if artifact._root_blueprint_phase5 is None:
            return ()
        rows: List[Tuple[Any, ...]] = []
        for socket_ref in artifact._root_blueprint_phase5.socket_refs:
            try:
                rows.append(
                    (
                        socket_ref.node_id,
                        socket_ref.param_name,
                        socket_ref.param_path_id,
                        socket_ref.socket_kind.value,
                    )
                )
            except AttributeError:
                continue
        rows.sort(key=SharedCompilerExecutions.socket_row_sort_key)
        return tuple(rows)

    @staticmethod
    def build_phase5_dag_edge_rows(
            artifact: SpellCompilerArtifact,
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase5 DAG edges.
        """
        if artifact._root_blueprint_phase5 is None:
            return ()
        try:
            dag = artifact._root_blueprint_phase5.dag
            nodes = dag.nodes
        except AttributeError:
            return ()
        rows: List[Tuple[Any, ...]] = []
        for parent_spell_id in sorted(nodes.keys()):
            parent_node = nodes[parent_spell_id]
            try:
                dependents = list(parent_node.dependents)
            except AttributeError:
                continue
            for child_node in dependents:
                try:
                    child_spell_id = child_node.id
                except AttributeError:
                    continue
                param_name = None
                try:
                    param_name = child_node.incoming_params.get(parent_node)
                except AttributeError:
                    param_name = None
                socket_kind = None
                try:
                    raw_socket_kind = dag._socket_kinds.get((parent_node, child_node))
                except AttributeError:
                    raw_socket_kind = None
                if raw_socket_kind is not None:
                    try:
                        socket_kind = raw_socket_kind.value
                    except AttributeError:
                        socket_kind = repr(raw_socket_kind)
                rows.append(
                    (
                        parent_spell_id,
                        child_spell_id,
                        param_name,
                        socket_kind,
                    )
                )
        rows.sort()
        return tuple(rows)

    @staticmethod
    def capture_phase2_5_codegen_ir(
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Export phases 2-5 artifacts into the spell-scoped Codegen IR payload.
        """
        symbolic_dependencies: Tuple[Tuple[Any, ...], ...] = ()
        if artifact._symbolic_graph is not None:
            symbolic_dependencies = tuple(
                (
                    dependency.param_name,
                    dependency.position,
                    dependency.di_shape.name,
                    dependency.is_optional,
                    dependency.is_collection,
                    dependency.contract_key,
                    dependency.contract_late_binding,
                )
                for dependency in artifact._symbolic_graph.dependencies
            )

        local_ordered_node_ids: Tuple[str, ...] = ()
        if artifact._resolution_frame is not None:
            local_ordered_node_ids = tuple(artifact._resolution_frame.ordered_node_ids)

        dependency_ids: Tuple[str, ...] = ()
        if spell.dependencies:
            dependency_ids = tuple(spell.dependencies)

        phase4_issue_codes: Tuple[str, ...] = ()
        if artifact._validation_result_phase4 is not None:
            phase4_issue_codes = tuple(
                issue.code
                for issue in artifact._validation_result_phase4.issues
            )

        phase5_root_spell_id: Optional[str] = None
        phase5_root_lineage_id: Optional[str] = None
        phase5_root_ordered_node_ids: Tuple[str, ...] = ()
        phase5_socket_ref_count = 0
        phase5_socket_rows: Tuple[Tuple[Any, ...], ...] = ()
        phase5_dag_edge_rows: Tuple[Tuple[Any, ...], ...] = ()
        if artifact._root_blueprint_phase5 is not None:
            phase5_root_spell_id = artifact._root_blueprint_phase5.root_spell_id
            try:
                phase5_root_lineage_id = artifact._root_blueprint_phase5.root_lineage_id
            except AttributeError:
                phase5_root_lineage_id = None
            phase5_root_ordered_node_ids = tuple(
                artifact._root_blueprint_phase5.ordered_node_ids
            )
            phase5_socket_ref_count = len(artifact._root_blueprint_phase5.socket_refs)
            phase5_socket_rows = SharedCompilerExecutions.build_phase5_socket_rows(
                artifact
            )
            phase5_dag_edge_rows = SharedCompilerExecutions.build_phase5_dag_edge_rows(
                artifact
            )

        phase5_index_spell_ids: Tuple[str, ...] = ()
        if artifact._spell_system_index_phase5 is not None:
            phase5_index_spell_ids = tuple(
                sorted(artifact._spell_system_index_phase5.nodes.keys())
            )

        phase2_5_signature = SharedCompilerExecutions.hash_codegen_signature(
            symbolic_dependencies,
            local_ordered_node_ids,
            dependency_ids,
            artifact._validated_phase4,
            artifact._is_broken,
            phase4_issue_codes,
            phase5_root_spell_id,
            phase5_root_lineage_id,
            phase5_root_ordered_node_ids,
            phase5_socket_ref_count,
            phase5_socket_rows,
            phase5_dag_edge_rows,
            phase5_index_spell_ids,
        )

        phase2_5_payload = {
            "symbolic_dependencies": symbolic_dependencies,
            "local_ordered_node_ids": local_ordered_node_ids,
            "dependency_ids": dependency_ids,
            "phase4_validated": artifact._validated_phase4,
            "phase4_is_broken": artifact._is_broken,
            "phase4_issue_codes": phase4_issue_codes,
            "phase5_root_spell_id": phase5_root_spell_id,
            "phase5_root_lineage_id": phase5_root_lineage_id,
            "phase5_root_ordered_node_ids": phase5_root_ordered_node_ids,
            "phase5_socket_ref_count": phase5_socket_ref_count,
            "phase5_socket_rows": phase5_socket_rows,
            "phase5_dag_edge_rows": phase5_dag_edge_rows,
            "phase5_index_spell_ids": phase5_index_spell_ids,
            "signature": phase2_5_signature,
        }

        ir_payload = SharedCompilerExecutions.ensure_codegen_ir(artifact)
        ir_payload["phase2_5"] = phase2_5_payload
        ir_payload["signatures"]["phase2_5"] = phase2_5_signature

    @staticmethod
    def reset_phase8_11_codegen_ir(
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Clear the phase8_11 segment from Codegen IR and Phase 12 artifacts.
        """
        if artifact._codegen_ir is not None:
            artifact._codegen_ir["phase8_11"] = {}
            artifact._codegen_ir["signatures"].pop("phase8_11", None)
        artifact._phase8_11_codegen_ir_dirty = False
        spell.resolution_complete = False

        artifact._phase12_no_overrides_executor = None
        artifact._phase12_no_overrides_executor_signature = None
        artifact._phase8_occurrence_plan_input_signature = None
        artifact._phase8_occurrence_plan_fast_key = None
        artifact._phase9_injection_plan_input_signature = None
        artifact._phase10_patch_maps_input_signature = None
        artifact._phase11_no_overrides_input_signature = None
        artifact._phase11_no_overrides_fast_key = None

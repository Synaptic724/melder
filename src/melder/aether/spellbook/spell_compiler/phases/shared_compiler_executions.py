import hashlib
import pickle
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )



from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_types.spell_types import SpellType

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
        Ensure compiler-artifact codegen IR storage is initialized.

        Purpose:
            Centralize IR allocation so phase exporters can write into one
            stable payload owned by this artifact.
        Contract:
            - Initializes once per artifact when absent.
            - Returns the artifact-owned mutable payload by reference.
            - Includes baseline phase buckets required by all phase executors.
        Returns:
            Dict[str, Any]:
                Mutable codegen IR mapping for this artifact.
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
            
            Purpose:
                Avoid expensive mega-`repr(...)` materialization on large nested
                IR payloads while preserving deterministic signature behaviour.
            Contract:
                - Uses typed fastpaths for common scalar values.
                - Uses direct `pickle` fallback for container and unsupported values.
                - Falls back to `repr(...).encode(...)` for non-picklable values.
            Args:
                part:
                    One primitive/tuple/dict/set signature segment.
            Returns:
                bytes:
                    Deterministic encoded bytes for hashing.
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
            
            Purpose:
                Produce stable fingerprints for phase-exported IR slices so
                codegen-creation compilation can skip unchanged payloads.
            Contract:
                - Signature is deterministic for equal-ordered inputs.
                - Does not depend on process-randomized object identity.
            Args:
                *parts:
                    Ordered primitive payload parts.
            Returns:
                str:
                    SHA256 hex digest for the supplied parts.
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

        Purpose:
            Normalize socket row ordering used by codegen helpers.
        Contract:
            - Sorts by node id, then path id, then parameter name, then socket kind.
            - Returns a compact tuple directly comparable by Python sort.
        Args:
            socket_row:
                Socket row `(node_id, param_name, param_path_id, socket_kind)`.
        Returns:
            Tuple[str, int, str, str]:
                Sort key for reproducible schema export order.
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

        Purpose:
            Export explicit socket routing data from the root blueprint into
            phase2-5 IR without leaking live socket objects.
        Contract:
            - Returns only primitive tuple rows.
            - Ignores malformed socket objects that do not expose required
              fields.
            - Output row order is deterministic.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(node_id, param_name, param_path_id, socket_kind)`.
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
            
            Purpose:
                Export explicit parent->child routing from the root blueprint DAG so
                codegen consumers can validate structural semantics from IR alone.
            Contract:
                - Returns only primitive tuple rows.
                - Ignores malformed DAG nodes that do not expose expected fields.
                - Output row order is deterministic.
            Returns:
                Tuple[Tuple[Any, ...], ...]:
                    Rows `(parent_spell_id, child_spell_id, param_name, socket_kind)`.
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
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Export phases 2-5 artifacts into the artifact-scoped Codegen IR payload.

        Purpose:
            Persist normalized structural metadata used by downstream phase
            planners without re-reading mutable phase objects at runtime.
        Contract:
            - Safe to call repeatedly; latest phase artifacts overwrite prior IR.
            - Captures deterministic, order-stable tuples for signatures.
            - Updates `signatures.phase2_5` on each export.
        Returns:
            None.
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
    def freeze_phase11_schema_value(value: Any) -> Any:
        """
            Normalize arbitrary values into deterministic schema-safe forms.
            
            Purpose:
                Convert nested payload values into primitive/tuple structures so
                Phase11 IR rows can be serialized without leaking live objects.
            Contract:
                - Primitive values are returned as-is.
                - Dict/list/tuple/set values are recursively normalized.
                - Non-primitive objects are represented by deterministic repr text.
            Args:
                value:
                    Raw value captured from plan metadata.
            Returns:
                Any:
                    Deterministic schema-safe value.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        SharedCompilerExecutions.freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                SharedCompilerExecutions.freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        SharedCompilerExecutions.freeze_phase11_schema_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        return repr(value)

    @staticmethod
    def normalize_instance_key(
            instance_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, Optional[int]]:
        """
            Return one explicit two-element instance key tuple.
            
            Purpose:
                Preserve the stable `(spell_id, path_id)` key shape instead of
                widening through generic `tuple(...)` reconstruction.
        """
        return instance_key[0], instance_key[1]

    @staticmethod
    def normalize_occurrence_key(
            occurrence_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, Optional[int]]:
        """
            Return one explicit two-element occurrence key tuple.
            
            Purpose:
                Preserve the stable `(spell_id, path_id)` key shape instead of
                widening through generic `tuple(...)` reconstruction.
        """
        return occurrence_key[0], occurrence_key[1]

    @staticmethod
    def instance_key_sort_key(
            instance_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        """
            Build a deterministic sort key for instance-key tuples.
            
            Purpose:
                Keep schema-row ordering stable for `(spell_id, path_id)` keys.
            Contract:
                - `None` path ids sort before concrete path ids.
                - Spell id remains the primary sort dimension.
            Args:
                instance_key:
                    Instance key `(spell_id, path_id)`.
            Returns:
                Tuple[str, int]:
                    Comparable sort key.
        """
        path_id = instance_key[1]
        return (
            instance_key[0],
            -1 if path_id is None else path_id,
        )

    @staticmethod
    def occurrence_key_sort_key(
            occurrence_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        """
            Build a deterministic sort key for occurrence-key tuples.
            
            Purpose:
                Keep occurrence schema row ordering stable across equivalent maps.
            Contract:
                - `None` path ids sort before concrete path ids.
                - Spell id remains the primary sort dimension.
            Args:
                occurrence_key:
                    Occurrence key `(spell_id, path_id)`.
            Returns:
                Tuple[str, int]:
                    Comparable sort key.
        """
        path_id = occurrence_key[1]
        return (
            occurrence_key[0],
            -1 if path_id is None else path_id,
        )

    @staticmethod
    def build_fast_transient_schema(
            transient_plan: Optional[Tuple[Any, ...]],
    ) -> Optional[Dict[str, Any]]:
        """
            Convert the Phase11 transient tuple into a schema-only IR payload.
            
            Purpose:
                Remove callable/object references from transient payload export while
                preserving all indices needed for no-overrides transient codegen.
            Contract:
                - Returns None when no transient plan exists.
                - Returned payload contains only ints and tuples of ints.
            Args:
                transient_plan:
                    Phase 11 transient tuple payload.
            Returns:
                Optional[Dict[str, Any]]:
                    Schema-only transient payload, or None.
        """
        if transient_plan is None:
            return None
        return {
            "step_count": transient_plan[0],
            "root_step_index": transient_plan[1],
            "call_modes": tuple(transient_plan[3]),
            "dep1": tuple(transient_plan[4]),
            "dep2a": tuple(transient_plan[5]),
            "dep2b": tuple(transient_plan[6]),
            "dep3a": tuple(transient_plan[7]),
            "dep3b": tuple(transient_plan[8]),
            "dep3c": tuple(transient_plan[9]),
            "dep4a": tuple(transient_plan[10]),
            "dep4b": tuple(transient_plan[11]),
            "dep4c": tuple(transient_plan[12]),
            "dep4d": tuple(transient_plan[13]),
            "dep5a": tuple(transient_plan[14]),
            "dep5b": tuple(transient_plan[15]),
            "dep5c": tuple(transient_plan[16]),
            "dep5d": tuple(transient_plan[17]),
            "dep5e": tuple(transient_plan[18]),
            "dep6a": tuple(transient_plan[19]),
            "dep6b": tuple(transient_plan[20]),
            "dep6c": tuple(transient_plan[21]),
            "dep6d": tuple(transient_plan[22]),
            "dep6e": tuple(transient_plan[23]),
            "dep6f": tuple(transient_plan[24]),
            "dep7a": tuple(transient_plan[25]),
            "dep7b": tuple(transient_plan[26]),
            "dep7c": tuple(transient_plan[27]),
            "dep7d": tuple(transient_plan[28]),
            "dep7e": tuple(transient_plan[29]),
            "dep7f": tuple(transient_plan[30]),
            "dep7g": tuple(transient_plan[31]),
            "dep8a": tuple(transient_plan[32]),
            "dep8b": tuple(transient_plan[33]),
            "dep8c": tuple(transient_plan[34]),
            "dep8d": tuple(transient_plan[35]),
            "dep8e": tuple(transient_plan[36]),
            "dep8f": tuple(transient_plan[37]),
            "dep8g": tuple(transient_plan[38]),
            "dep8h": tuple(transient_plan[39]),
        }

    @staticmethod
    def build_fast_transient_signature(
            transient_schema: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """
            Build a deterministic signature for a Phase 11 fast transient plan.
            
            Purpose:
                Fingerprint transient plan structure without including call-target
                object identities, which are process-local and nondeterministic.
            Contract:
                - Returns None when no transient plan exists.
                - Signature includes step counts, call modes, and dependency index
                  arrays used by no-overrides execution.
            Args:
                transient_schema:
                    Schema-only transient payload exported by
                    `_build_fast_transient_schema`.
            Returns:
                Optional[str]:
                    Deterministic transient signature, or None.
        """
        if transient_schema is None:
            return None
        return SharedCompilerExecutions.hash_codegen_signature(
            transient_schema["step_count"],
            transient_schema["root_step_index"],
            transient_schema["call_modes"],
            transient_schema["dep1"],
            transient_schema["dep2a"],
            transient_schema["dep2b"],
            transient_schema["dep3a"],
            transient_schema["dep3b"],
            transient_schema["dep3c"],
            transient_schema["dep4a"],
            transient_schema["dep4b"],
            transient_schema["dep4c"],
            transient_schema["dep4d"],
            transient_schema["dep5a"],
            transient_schema["dep5b"],
            transient_schema["dep5c"],
            transient_schema["dep5d"],
            transient_schema["dep5e"],
            transient_schema["dep6a"],
            transient_schema["dep6b"],
            transient_schema["dep6c"],
            transient_schema["dep6d"],
            transient_schema["dep6e"],
            transient_schema["dep6f"],
            transient_schema["dep7a"],
            transient_schema["dep7b"],
            transient_schema["dep7c"],
            transient_schema["dep7d"],
            transient_schema["dep7e"],
            transient_schema["dep7f"],
            transient_schema["dep7g"],
            transient_schema["dep8a"],
            transient_schema["dep8b"],
            transient_schema["dep8c"],
            transient_schema["dep8d"],
            transient_schema["dep8e"],
            transient_schema["dep8f"],
            transient_schema["dep8g"],
            transient_schema["dep8h"],
        )

    @staticmethod
    def build_occurrence_graph_rows(
            occurrence_graph: Mapping[
                Tuple[str, int],
                Mapping[str, Sequence[Tuple[str, int]]],
            ],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
            Build deterministic schema rows for the Phase8 occurrence graph.
            
            Purpose:
                Export occurrence graph topology as schema-only tuples so consumers
                can validate dependency routing without live plan objects.
            Contract:
                - Returns only primitive tuple rows.
                - Sorts occurrences and dependency occurrence lists deterministically.
            Args:
                occurrence_graph:
                    Occurrence graph mapping from Phase8 plan.
            Returns:
                Tuple[Tuple[Any, ...], ...]:
                    Rows `(occurrence_key, dependency_rows)`.
        """
        rows: List[Tuple[Any, ...]] = []
        for occurrence_key in sorted(
                occurrence_graph.keys(),
                key=SharedCompilerExecutions.occurrence_key_sort_key,
        ):
            dependency_map = occurrence_graph[occurrence_key]
            dependency_rows: List[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]]] = []
            for param_name in sorted(dependency_map.keys()):
                dependency_occurrences = dependency_map[param_name]
                normalized_occurrences_list = [
                    SharedCompilerExecutions.normalize_occurrence_key(
                        dependency_occurrence
                    )
                    for dependency_occurrence in dependency_occurrences
                ]
                if len(normalized_occurrences_list) > 1:
                    normalized_occurrences_list.sort(
                        key=SharedCompilerExecutions.occurrence_key_sort_key,
                    )
                normalized_occurrences = tuple(normalized_occurrences_list)
                dependency_rows.append((param_name, normalized_occurrences))
            rows.append(
                (
                    SharedCompilerExecutions.normalize_occurrence_key(occurrence_key),
                    tuple(dependency_rows),
                )
            )
        return tuple(rows)

    @staticmethod
    def build_occurrence_instance_key_rows(
            instance_keys_by_spell_id: Mapping[
                str,
                Sequence[Tuple[str, Optional[int]]],
            ],
    ) -> Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...]:
        """
            Build deterministic schema rows for Phase8 instance-key planning.
            
            Purpose:
                Export per-spell instance key planning from occurrence plans in a
                stable schema-only representation.
            Contract:
                - Returns only primitive tuple rows.
                - Spell ids and instance-key lists are deterministically ordered.
            Args:
                instance_keys_by_spell_id:
                    Mapping from spell id to planned instance keys.
            Returns:
                Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...]:
                    Rows `(spell_id, instance_keys)`.
        """
        rows: List[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]]] = []
        for spell_id in sorted(instance_keys_by_spell_id.keys()):
            instance_keys_list = [
                SharedCompilerExecutions.normalize_instance_key(instance_key)
                for instance_key in instance_keys_by_spell_id[spell_id]
            ]
            if len(instance_keys_list) > 1:
                instance_keys_list.sort(
                    key=SharedCompilerExecutions.instance_key_sort_key
                )
            rows.append((spell_id, tuple(instance_keys_list)))
        return tuple(rows)

    @staticmethod
    def build_occurrence_canonical_rows(
            canonical_occurrences_by_spell_id: Mapping[
                str,
                Tuple[str, Optional[int]],
            ],
    ) -> Tuple[Tuple[str, Tuple[str, Optional[int]]], ...]:
        """
            Build deterministic schema rows for Phase8 canonical occurrences.
            
            Purpose:
                Export the shared-occurrence canonical mapping in schema form for
                deterministic validation and signature coverage.
            Contract:
                - Returns only primitive tuple rows.
                - Spell-id order is deterministic.
            Args:
                canonical_occurrences_by_spell_id:
                    Mapping from spell id to canonical occurrence key.
            Returns:
                Tuple[Tuple[str, Tuple[str, Optional[int]]], ...]:
                    Rows `(spell_id, canonical_occurrence_key)`.
        """
        rows: List[Tuple[str, Tuple[str, Optional[int]]]] = []
        for spell_id in sorted(canonical_occurrences_by_spell_id.keys()):
            rows.append(
                (
                    spell_id,
                    SharedCompilerExecutions.normalize_occurrence_key(
                        canonical_occurrences_by_spell_id[spell_id]
                    ),
                )
            )
        return tuple(rows)

    @staticmethod
    def build_occurrence_contract_override_rows(
            contract_overrides_by_occurrence: Mapping[
                Tuple[str, int],
                Mapping[str, Any],
            ],
    ) -> Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]:
        """
            Build deterministic schema rows for occurrence-scoped contract payloads.
            
            Purpose:
                Export Phase8 contract payload overlays with deterministic value
                freezing for signature and contract-audit use.
            Contract:
                - Returns only primitive tuple rows.
                - Payload items are key-sorted and recursively frozen.
            Args:
                contract_overrides_by_occurrence:
                    Mapping from occurrence key to payload mapping.
            Returns:
                Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]:
                    Rows `(occurrence_key, payload_items)`.
        """
        rows: List[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]]] = []
        for occurrence_key in sorted(
                contract_overrides_by_occurrence.keys(),
                key=SharedCompilerExecutions.occurrence_key_sort_key,
        ):
            payload = contract_overrides_by_occurrence[occurrence_key]
            payload_items = tuple(
                sorted(
                    (
                        param_name,
                        SharedCompilerExecutions.freeze_phase11_schema_value(value),
                    )
                    for param_name, value in payload.items()
                )
            )
            rows.append(
                (
                    SharedCompilerExecutions.normalize_occurrence_key(occurrence_key),
                    payload_items,
                )
            )
        return tuple(rows)

    @staticmethod
    def build_occurrence_contract_override_spell_rows(
            contract_overrides_by_spell_id: Mapping[
                str,
                Sequence[Tuple[Tuple[str, Optional[int]], Mapping[str, Any]]],
            ],
    ) -> Tuple[
        Tuple[
            str,
            Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...],
        ],
        ...,
    ]:
        """
            Build deterministic schema rows for spell-grouped contract payloads.
            
            Purpose:
                Export spell-grouped contract payload overlays from Phase8 in a
                deterministic schema for contract completeness audits.
            Contract:
                - Returns only primitive tuple rows.
                - Spell ids and grouped occurrence rows are deterministically ordered.
            Args:
                contract_overrides_by_spell_id:
                    Mapping from spell id to `(occurrence_key, payload)` entries.
            Returns:
                Tuple[Tuple[str, Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]], ...]:
                    Rows `(spell_id, occurrence_payload_rows)`.
        """
        rows: List[
            Tuple[
                str,
                Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...],
            ]
        ] = []
        for spell_id in sorted(contract_overrides_by_spell_id.keys()):
            grouped_rows: List[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]]] = []
            for occurrence_key, payload in contract_overrides_by_spell_id[spell_id]:
                payload_items = tuple(
                    sorted(
                        (
                            param_name,
                            SharedCompilerExecutions.freeze_phase11_schema_value(value),
                        )
                        for param_name, value in payload.items()
                    )
                )
                grouped_rows.append(
                    (
                        SharedCompilerExecutions.normalize_occurrence_key(occurrence_key),
                        payload_items,
                    )
                )
            grouped_rows.sort(
                key=lambda row: SharedCompilerExecutions.occurrence_key_sort_key(row[0]),
            )
            rows.append((spell_id, tuple(grouped_rows)))
        return tuple(rows)

    @staticmethod
    def build_injection_instance_rows(
            instance_injections: Mapping[Tuple[str, Optional[int]], Any],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
            Build deterministic schema rows for Phase9 injection specifications.
            
            Purpose:
                Export per-instance injection semantics (dependency keys, contract
                payloads, aggregation flags) as deterministic schema-only rows.
            Contract:
                - Returns only primitive tuple rows.
                - Expects InjectionSpec/ParamSource contract fields to be present.
                - Fails fast when malformed/cleaned artifacts violate contract.
            Args:
                instance_injections:
                    Mapping from instance key to InjectionSpec-like objects.
            Returns:
                Tuple[Tuple[Any, ...], ...]:
                    Rows `(instance_key, allow_list, uses_positional, contract_items, param_rows)`.
        """
        rows: List[Tuple[Any, ...]] = []
        for instance_key in sorted(
                instance_injections.keys(),
                key=SharedCompilerExecutions.instance_key_sort_key,
        ):
            injection_spec = instance_injections[instance_key]
            allow_list_aggregation = bool(injection_spec.allow_list_aggregation)
            uses_positional_override = bool(injection_spec.uses_positional_override)
            contract_payload_items: Tuple[Tuple[str, Any], ...] = ()
            param_rows: List[Tuple[Any, ...]] = []
            contract_payload = injection_spec.contract_payload
            if contract_payload:
                contract_payload_items = tuple(
                    sorted(
                        (
                            param_name,
                            SharedCompilerExecutions.freeze_phase11_schema_value(value),
                        )
                        for param_name, value in contract_payload.items()
                    )
                )

            param_sources = injection_spec.param_sources
            if param_sources:
                for param_name in sorted(param_sources.keys()):
                    param_source = param_sources[param_name]
                    kind = param_source.kind
                    dependency_keys: Tuple[Tuple[str, Optional[int]], ...] = ()
                    raw_dependency_keys = param_source.dependency_keys
                    if raw_dependency_keys:
                        dependency_key_list: List[Tuple[str, Optional[int]]] = [
                            (
                                str(dependency_key[0]),
                                dependency_key[1],
                            )
                            for dependency_key in raw_dependency_keys
                        ]
                        if len(dependency_key_list) > 1:
                            dependency_key_list.sort(
                                key=SharedCompilerExecutions.instance_key_sort_key,
                            )
                        dependency_keys = tuple(dependency_key_list)
                    override_key = param_source.override_key
                    contract_key = param_source.contract_key
                    param_rows.append(
                        (
                            param_name,
                            kind,
                            dependency_keys,
                            override_key,
                            contract_key,
                        )
                    )

            rows.append(
                (
                    tuple(instance_key),
                    allow_list_aggregation,
                    uses_positional_override,
                    contract_payload_items,
                    tuple(param_rows),
                )
            )
        return tuple(rows)

    @staticmethod
    def build_override_target_rows(
            override_patch_map: Any,
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
            Build deterministic schema rows for Phase10 override patch-map targets.
            
            Purpose:
                Export concrete socket-target rows grouped by TargetSpec for
                codegen contract completeness and signature invalidation.
            Contract:
                - Returns only primitive tuple rows.
                - Includes specificity values when available.
                - Expects OverridePatchMap target/spec specificity contracts.
                - Fails fast when malformed/cleaned artifacts violate contract.
            Args:
                override_patch_map:
                    OverridePatchMap-like object.
            Returns:
                Tuple[Tuple[Any, ...], ...]:
                    Rows `(spec_key, specificity, socket_rows)`.
        """
        if override_patch_map is None:
            return ()
        targets_by_spec = override_patch_map.targets_by_spec
        specificity_by_spec = override_patch_map.specificity_by_spec
        rows: List[Tuple[Any, ...]] = []
        for spec_key in sorted(targets_by_spec.keys()):
            raw_targets = targets_by_spec[spec_key]
            socket_rows: List[Tuple[str, str, int, str]] = []
            for socket_ref in raw_targets:
                socket_rows.append(
                    (
                        socket_ref.node_id,
                        socket_ref.param_name,
                        socket_ref.param_path_id,
                        socket_ref.socket_kind.value,
                    )
                )
            if len(socket_rows) > 1:
                socket_rows.sort(key=SharedCompilerExecutions.socket_row_sort_key)

            specificity_value = None
            if specificity_by_spec:
                specificity = specificity_by_spec.get(spec_key)
                if specificity is not None:
                    specificity_value = int(specificity)

            rows.append(
                (
                    spec_key,
                    specificity_value,
                    tuple(socket_rows),
                )
            )
        return tuple(rows)

    @staticmethod
    def build_phase11_step_ir_row(
            step: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
            Build one schema-only Phase11 step row for IR export.
            
            Purpose:
                Capture step semantics without exporting live plan/spell objects.
            Contract:
                - Output contains only primitive/tuple values.
                - Includes all no-overrides and overrides semantics consumed by
                  compilers and runtime shape-key signatures.
            Args:
                step:
                    ExecutionPlanStep-like object.
            Returns:
                Dict[str, Any]:
                    Normalized step row.
        """
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        )
        contract_payload_items: Tuple[Any, ...] = ()
        if step.contract_payload:
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        SharedCompilerExecutions.freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        override_match_prefix = None
        override_match_prefix_len = 0
        override_keys: Tuple[Any, ...] = ()
        expects_overrides = False
        if include_override_metadata:
            override_match_prefix = step.override_match_prefix
            override_match_prefix_len = step.override_match_prefix_len
            override_keys = tuple(step.override_keys)
            expects_overrides = step.expects_overrides
        return {
            "instance_key": tuple(step.instance_key),
            "spell_id": step.spell.spell_index.current,
            "existence": step.existence.name,
            "creations_target_kind": step.creations_target_kind,
            "shared_instance": step.shared_instance,
            "dependency_resolution_order": dependency_resolution_order,
            "override_match_prefix": override_match_prefix,
            "override_match_prefix_len": override_match_prefix_len,
            "override_keys": override_keys,
            "expects_overrides": expects_overrides,
            "contract_keys": tuple(step.contract_keys),
            "allow_list_aggregation": step.allow_list_aggregation,
            "uses_positional_override": step.uses_positional_override,
            "contract_positional_override": SharedCompilerExecutions.freeze_phase11_schema_value(
                step.contract_positional_override,
            ),
            "has_contract_payload": step.has_contract_payload,
            "contract_payload_items": contract_payload_items,
            "lock_hint": step.lock_hint,
            "use_spell_lock_hint": step.use_spell_lock_hint,
            "requires_spellspace": step.requires_spellspace,
            "owner_conduit_required": step.owner_conduit_required,
            "must_register": step.must_register,
            "disposal_method_names": tuple(step.disposal_method_names),
        }

    @staticmethod
    def build_no_overrides_codegen_creation_step_signature_row(
            step: Any,
    ) -> Tuple[Any, ...]:
        """
            Build one deterministic signature row for no-overrides compile caching.
            
            Purpose:
                Capture only the step fields that influence no-overrides
                compiled source/namespace behaviour without constructing full IR
                payload dict rows.
            Contract:
                - Returns a tuple-only row with deterministic ordering.
                - Includes dependency, contract, lock, and registration semantics.
            Args:
                step:
                    ExecutionPlanStep-like object.
            Returns:
                Tuple[Any, ...]:
                    Deterministic row used by no-overrides plan signature hashing.
        """
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        )
        contract_payload_items: Tuple[Any, ...] = ()
        if step.contract_payload:
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        SharedCompilerExecutions.freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.current,
            step.existence.name,
            step.creations_target_kind,
            dependency_resolution_order,
            bool(step.uses_positional_override),
            SharedCompilerExecutions.freeze_phase11_schema_value(
                step.contract_positional_override
            ),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.use_spell_lock_hint),
            bool(step.must_register),
        )

    @staticmethod
    def build_phase11_spell_signature_row(
            spell: Spell,
    ) -> Tuple[Any, ...]:
        """
            Build a deterministic spell metadata row for Phase 11 no-overrides inputs.
            
            Purpose:
                Capture spell fields consumed by `ExecutionPlanBuilder.build` so
                phase11 can detect when a no-overrides rebuild is required.
            Contract:
                - Includes existence/register/disposal and optimistic-object identity.
                - Uses primitive/tuple values only for deterministic hashing.
            Args:
                spell:
                    Spell referenced by occurrence execution order.
            Returns:
                Tuple[Any, ...]:
                    Deterministic spell metadata row.
        """
        optimistic_object_identity = None
        if spell.user_created_object is not None:
            optimistic_object_identity = id(spell.user_created_object)
        is_callable_spell = spell.spell_type in (
            SpellType.SPELL,
            SpellType.SPELL_WITH_SPELLFRAME,
            SpellType.SPELL_WITH_BINDING_NAME,
            SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        must_register = True
        if spell.existence is Existence.many and not spell.has_disposal_methods:
            must_register = False
        return (
            spell.spell_index.current,
            spell.existence.name,
            bool(spell.is_existing_creation),
            bool(is_callable_spell),
            bool(must_register),
            bool(spell.has_disposal_methods),
            tuple(spell.disposal_method_names),
            optimistic_object_identity,
        )

    @staticmethod
    def build_phase11_injection_spec_signature_row(
            injection_spec: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Tuple[Any, ...]:
        """
            Build deterministic InjectionSpec row for Phase 11 input signatures.
            
            Purpose:
                Normalize injection metadata used by `ExecutionPlanBuilder.build`
                without allocating Phase 11 steps.
            Contract:
                - Includes param source wiring, aggregation flags, and contract payload.
                - Returns tuple-only deterministic structure.
            Args:
                injection_spec:
                    Phase 9 InjectionSpec-like object.
            Returns:
                Tuple[Any, ...]:
                    Deterministic signature row.
        """
        param_rows: List[Tuple[Any, ...]] = []
        param_sources = injection_spec.param_sources
        for param_name in sorted(param_sources.keys()):
            param_source = param_sources[param_name]
            dependency_keys = None
            if param_source.dependency_keys is not None:
                dependency_keys = tuple(
                    tuple(dependency_key)
                    for dependency_key in param_source.dependency_keys
                )
            override_key = None
            if include_override_metadata:
                override_key = param_source.override_key
            param_rows.append(
                (
                    param_name,
                    param_source.kind,
                    dependency_keys,
                    override_key,
                    param_source.contract_key,
                )
            )

        contract_payload = injection_spec.contract_payload
        normalized_contract_payload = None
        if contract_payload is not None:
            normalized_contract_payload = dict(contract_payload)
            if (
                    "__args__" in normalized_contract_payload
                    and isinstance(normalized_contract_payload["__args__"], list)
            ):
                normalized_contract_payload["__args__"] = tuple(
                    normalized_contract_payload["__args__"]
                )

        return (
            tuple(param_rows),
            bool(injection_spec.allow_list_aggregation),
            bool(injection_spec.uses_positional_override),
            normalized_contract_payload,
        )

    @staticmethod
    def build_phase11_variant_ir_payload(
            plan: Optional[Any],
    ) -> Dict[str, Any]:
        """
            Export one Phase 11 execution-plan variant into IR fields.
            
            Purpose:
                Normalize plan metadata and signatures so codegen creation and
                runtime dispatch can consume a deterministic payload.
            Contract:
                - Returns a payload dictionary for any input; empty plan fields are
                  represented as None/empty tuples.
                - Exposes schema-only step/transient payloads with no live objects.
            Args:
                plan:
                    Execution plan variant to export.
            Returns:
                Dict[str, Any]:
                    Normalized Phase 11 variant payload.
        """
        if plan is None:
            return {
                "plan_variant": None,
                "root_spell_id": None,
                "step_count": 0,
                "step_spell_ids": (),
                "transient_signature": None,
                "signature": None,
                "transient_schema": None,
                "steps_rows": (),
                "steps_rows_signature": None,
            }

        steps = plan.steps
        include_override_metadata = (
                plan.plan_variant != "no_overrides_fast"
        )
        steps_rows = tuple(
            SharedCompilerExecutions.build_phase11_step_ir_row(
                step,
                include_override_metadata=include_override_metadata,
            )
            for step in steps
        )
        steps_rows_signature = SharedCompilerExecutions.hash_codegen_signature(
            steps_rows
        )
        step_spell_ids = tuple(
            step.spell.spell_index.current
            for step in steps
        )
        transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
            plan.fast_transient_plan
        )
        transient_signature = SharedCompilerExecutions.build_fast_transient_signature(
            transient_schema
        )
        signature = SharedCompilerExecutions.hash_codegen_signature(
            plan.plan_variant,
            plan.root_spell_id,
            step_spell_ids,
            steps_rows_signature,
            transient_signature,
        )
        return {
            "plan_variant": plan.plan_variant,
            "root_spell_id": plan.root_spell_id,
            "step_count": len(steps),
            "step_spell_ids": step_spell_ids,
            "transient_signature": transient_signature,
            "signature": signature,
            "transient_schema": transient_schema,
            "steps_rows": steps_rows,
            "steps_rows_signature": steps_rows_signature,
        }

    @staticmethod
    def capture_phase8_11_codegen_ir(
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Export current live phases 8-11 artifacts into the spell-scoped
            Codegen IR payload.

            Purpose:
                Preserve a spell-scoped diagnostic/export snapshot for the
                substituted analyzer -> processor -> planner -> codegen creation
                path without dereferencing the deleted legacy artifact family.
            Contract:
                - Safe to call repeatedly; latest live phase outputs overwrite
                  prior IR.
                - Updates `signatures.phase8_11` on each export.
                - Uses only the current artifact-owned analyzer/model/plan/
                  creation surfaces.
            Returns:
                None.
        """
        occurrence_graph_analysis = artifact._occurrence_graph_analysis
        spell_codegen_model = artifact._spell_codegen_model
        spell_codegen_plan = artifact._spell_codegen_plan
        spell_codegen_creation = artifact._spell_codegen_creation

        no_overrides_plan = None
        overrides_plan = None
        if spell_codegen_plan is not None:
            no_overrides_plan = spell_codegen_plan.no_overrides_plan
            overrides_plan = spell_codegen_plan.overrides_plan
        creation_metadata = (
            {}
            if spell_codegen_creation is None
            else spell_codegen_creation.metadata
        )

        phase8_11_signature = SharedCompilerExecutions.hash_codegen_signature(
            None if occurrence_graph_analysis is None else occurrence_graph_analysis.root_spell_id,
            None if occurrence_graph_analysis is None else occurrence_graph_analysis.occurrence_count,
            None if occurrence_graph_analysis is None else occurrence_graph_analysis.edge_count,
            None if spell_codegen_model is None else spell_codegen_model.build_kind,
            None if spell_codegen_model is None else spell_codegen_model.route_family,
            None if spell_codegen_model is None else spell_codegen_model.node_count,
            None if spell_codegen_model is None else spell_codegen_model.max_dependency_count,
            None if no_overrides_plan is None else no_overrides_plan.root_spell_id,
            None if no_overrides_plan is None else len(no_overrides_plan.steps),
            None if overrides_plan is None else overrides_plan.root_spell_id,
            None if overrides_plan is None else len(overrides_plan.steps),
            creation_metadata.get("_no_overrides_executor_signature"),
        )

        phase8_11_payload = {
            "occurrence": None if occurrence_graph_analysis is None else {
                "root_spell_id": occurrence_graph_analysis.root_spell_id,
                "occurrence_count": occurrence_graph_analysis.occurrence_count,
                "edge_count": occurrence_graph_analysis.edge_count,
                "topology_dependency_count": occurrence_graph_analysis.topology_dependency_count,
                "dag_fallback_dependency_count": occurrence_graph_analysis.dag_fallback_dependency_count,
                "shared_collapse_enabled": occurrence_graph_analysis.shared_collapse_enabled,
            },
            "model": None if spell_codegen_model is None else {
                "build_kind": spell_codegen_model.build_kind,
                "route_family": spell_codegen_model.route_family,
                "node_count": spell_codegen_model.node_count,
                "max_dependency_count": spell_codegen_model.max_dependency_count,
                "target_spec_count": spell_codegen_model.target_spec_count,
                "applied_strategy_ids": tuple(spell_codegen_model.applied_strategy_ids),
            },
            "plan": None if spell_codegen_plan is None else {
                "processor_strategy_ids": spell_codegen_plan.processor_strategy_ids,
                "plan_strategy_ids": spell_codegen_plan.plan_strategy_ids,
                "no_overrides_step_count": (
                    0 if no_overrides_plan is None else len(no_overrides_plan.steps)
                ),
                "overrides_step_count": (
                    0 if overrides_plan is None else len(overrides_plan.steps)
                ),
            },
            "creation": None if spell_codegen_creation is None else {
                "selected_strategy_ids": spell_codegen_creation.selected_strategy_ids,
                "no_overrides_executor_signature": (
                    creation_metadata.get("_no_overrides_executor_signature")
                ),
            },
            "signature": phase8_11_signature,
        }

        ir_payload = SharedCompilerExecutions.ensure_codegen_ir(artifact)
        ir_payload["phase8_11"] = phase8_11_payload
        ir_payload["signatures"]["phase8_11"] = phase8_11_signature
        artifact._phase8_11_codegen_ir_dirty = False

    @staticmethod
    def capture_phase8_11_codegen_ir_if_dirty(
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Flush phase8_11 codegen export only when stale.
            
            Purpose:
                Avoid repeated full payload/signature rebuilds while preserving
                freshness for codegen-ir readers and any compile calls that consume
                exported phase8-11 payloads.
            Contract:
                - No-op when dirty flag is false.
                - Executes full `_capture_phase8_11_codegen_ir` once per dirty cycle.
            Returns:
                None.
        """
        if not artifact._phase8_11_codegen_ir_dirty:
            return
        SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact)

    @staticmethod
    def reset_phase2_5_codegen_ir(
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Clear the phase2_5 segment from Codegen IR.
            
            Purpose:
                Keep IR aligned with lifecycle cleanup when structural artifacts are
                discarded.
            Contract:
                - No-op when IR is not initialized.
                - Preserves phase8_11 payloads and compiled executor artifacts.
            Returns:
                None.
        """
        if artifact._codegen_ir is None:
            return
        artifact._codegen_ir["phase2_5"] = {}
        artifact._codegen_ir["signatures"].pop("phase2_5", None)

    @staticmethod
    def reset_phase8_11_codegen_ir(
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Clear the live phase-8-to-phase-11 export segment and dependent outputs.

        Purpose:
            Invalidate exported analyzer/model/plan/creation snapshots whenever
            the live post-phase5 compiler surfaces are being discarded.
        Contract:
            - No-op when IR is not initialized.
            - Clears occurrence-analysis signatures plus generic codegen outputs.
            - Leaves phase-2-to-phase-5 IR intact.
        Returns:
            None.
        """
        if artifact._codegen_ir is not None:
            artifact._codegen_ir["phase8_11"] = {}
            artifact._codegen_ir["signatures"].pop("phase8_11", None)
        artifact._phase8_11_codegen_ir_dirty = False
        artifact._occurrence_analysis_input_signature = None
        artifact._occurrence_analysis_fast_key = None
        artifact._cleanup_occurrence_analysis_artifacts()
        artifact._cleanup_codegen_outputs()
        spell.resolution_complete = False


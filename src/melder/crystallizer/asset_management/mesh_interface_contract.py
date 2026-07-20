from typing import Dict, List, ClassVar

from melder.crystallizer.persistence.record_version import RecordVersion
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class MeshInterfaceContract:
    """
    Static authority describing the external persistence mesh interface.

    Purpose:
        Describe the complete value/callable boundary between crystallizer
        assets and an external store: unit kinds, identity columns, payload
        shapes, handler signatures, and their configuration fluents. The
        emitted dictionary is sufficient to implement an adapter without
        depending on crystallizer internals.

    Guidance:
        Read this authority through `Crystallizer.describe_external_interface()`
        when generating or validating an integration. Implement handlers against
        `HANDLER_SIGNATURES`, preserve the stamped payload unchanged, and use
        `kind` as the storage partition. `IDENTITY_COLUMNS` is a suggested
        portable model rather than required DDL. The emitted checkpoint phrase
        "lexicographic = age" describes timestamp ordering only; exact ordering
        among checkpoints minted in one millisecond comes from the recorded
        checkpoint number or ledger insertion order. Do not instantiate or
        mutate this class; `describe()` returns detached copies for inspection.

    Contract:
        - Pure and stateless: class-level data plus static reads; never
          instantiated, never mutated at runtime (mirrors the
          RecordVersion static-authority precedent).
        - The shape rows mirror the REAL producers exactly:
          PersistenceCrystal.to_cached_item (checkpoint),
          PersistenceSystem.capture_formation_record (formation),
          PersistenceProfile.capture_index_graft (index_graft), and
          AssetManagementSystem.stream_emission (emission). If a
          producer's shape changes, this table changes in the same
          patch (twin-kind honesty law applied to the mesh).
        - Emitting the contract is descriptive only. Melder never
          generates storage code (callables-first law): the "columns"
          row is the suggested identity model, not DDL.

    Threading / Concurrency:
        Immutable class-level data; safe from any thread.

    Lifecycle / Cleanup:
        None. Static authority classes carry no state to clean.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Static authority describing the external persistence mesh interface. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    # The four first-class unit kinds the asset layer ships today.
    UNIT_KIND_CHECKPOINT: str = "checkpoint"
    UNIT_KIND_FORMATION: str = "formation"
    UNIT_KIND_INDEX_GRAFT: str = "index_graft"
    UNIT_KIND_EMISSION: str = "emission"

    # Suggested identity columns for ANY storage backing the mesh. The
    # payload column always carries the RecordVersion-stamped JSON dict.
    IDENTITY_COLUMNS: Dict[str, str] = {
        "kind": "unit kind partition (one of the UNIT_KIND_* values)",
        "profile_name": "recording profile the unit belongs to",
        "unit_id": (
            "kind-specific identity: checkpoint ULID, formation name, "
            "graft index_id, or a fresh per-event ULID for emissions"
        ),
        "payload": "the RecordVersion-stamped JSON document",
    }

    # Handler call signatures the user registers on the manager
    # configuration (the fluent names are the registration surface).
    HANDLER_SIGNATURES: Dict[str, Dict[str, object]] = {
        "store_unit": {
            "register_as": "with_store_handler",
            "args": ["kind", "profile_name", "unit_id", "payload"],
            "returns": "None (raise to signal failure; lenient+counted)",
        },
        "fetch_unit": {
            "register_as": "with_fetch_handler",
            "args": ["kind", "unit_id"],
            "returns": "payload dict or None when absent",
        },
        "list_units": {
            "register_as": "with_list_units_handler",
            "args": ["kind", "profile_name"],
            "returns": "list of unit_id strings",
        },
        "delete_unit": {
            "register_as": "with_delete_handler",
            "args": ["kind", "unit_id"],
            "returns": "None (raise to signal failure; deletes are STRICT)",
        },
        "stream_emissions": {
            "register_as": "with_stream_emissions",
            "args": ["enabled"],
            "returns": "n/a (bool knob; opt-in tap over store_unit)",
        },
    }

    # Per-kind payload shape: the top-level keys each stamped document
    # carries, in producer order. record_version rides every payload.
    PAYLOAD_SHAPES: Dict[str, Dict[str, object]] = {
        UNIT_KIND_CHECKPOINT: {
            "producer": "PersistenceCrystal.to_cached_item",
            "unit_id_semantics": "checkpoint ULID (lexicographic = age)",
            "keys": [
                "record_version", "checkpoint_id", "profile_name",
                "checkpoint_number", "created_at", "description",
                "sequence_range", "journal_segment", "captured_payloads",
            ],
            "reader_gate": "RecordVersion.check_readable at from_cached_item",
        },
        UNIT_KIND_FORMATION: {
            "producer": "PersistenceSystem.capture_formation_record",
            "unit_id_semantics": "user-chosen formation name",
            "keys": [
                "record_version", "formation_name", "profile_name",
                "scope", "created_at", "description", "payloads",
            ],
            "reader_gate": "RecordVersion.check_readable at load_formation_record",
        },
        UNIT_KIND_INDEX_GRAFT: {
            "producer": "PersistenceProfile.capture_index_graft",
            "unit_id_semantics": "the captured spell_index id (ULID)",
            "keys": [
                "record_version", "graft_kind", "index_id",
                "index_payload", "members", "members_without_custody",
            ],
            "reader_gate": "RecordVersion gate inside GraftRunner",
        },
        UNIT_KIND_EMISSION: {
            "producer": "AssetManagementSystem.stream_emission",
            "unit_id_semantics": "fresh ULID per event (a stream, not rows)",
            "keys": ["record_version", "crystal_kind", "payload"],
            "reader_gate": "consumer-side (events are notifications)",
        },
    }

    @staticmethod
    def unit_kinds() -> List[str]:
        """
        Return the first-class unit kinds in declaration order.

        Returns:
            List[str]: ["checkpoint", "formation", "index_graft",
            "emission"].
        """
        return [
            MeshInterfaceContract.UNIT_KIND_CHECKPOINT,
            MeshInterfaceContract.UNIT_KIND_FORMATION,
            MeshInterfaceContract.UNIT_KIND_INDEX_GRAFT,
            MeshInterfaceContract.UNIT_KIND_EMISSION,
        ]

    @staticmethod
    def describe() -> Dict[str, object]:
        """
        Emit the whole mesh interface contract as one stamped dict.

        Purpose:
            Emit the adapter-authoring table: kinds, identity columns, payload
            shapes, and handler signatures with their registration fluent names.

        Contract:
            - Detached copies only; mutating the result never touches
              the class-level authority.
            - RecordVersion-stamped like every durable mesh artifact,
              so contract snapshots version alongside the data they
              describe.

        Returns:
            Dict[str, object]: {record_version, unit_kinds,
            identity_columns, handler_signatures, payload_shapes}.
        """
        return RecordVersion.stamp({
            "unit_kinds": MeshInterfaceContract.unit_kinds(),
            "identity_columns": dict(
                MeshInterfaceContract.IDENTITY_COLUMNS
            ),
            "handler_signatures": {
                name: dict(spec)
                for name, spec in
                MeshInterfaceContract.HANDLER_SIGNATURES.items()
            },
            "payload_shapes": {
                kind: {
                    key: (list(value) if isinstance(value, list) else value)
                    for key, value in shape.items()
                }
                for kind, shape in
                MeshInterfaceContract.PAYLOAD_SHAPES.items()
            },
        })

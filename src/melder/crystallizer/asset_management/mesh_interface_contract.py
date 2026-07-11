from typing import Dict, List

from melder.crystallizer.persistence.record_version import RecordVersion


class MeshInterfaceContract:
    """
    Static authority describing the external persistence mesh interface.

    Purpose:
        The mesh is an INTERFACE LAYER (owner directive 2026-07-11):
        melder forms the calls, the user registers plain callables, and
        versioned JSON flows both ways. This class emits the whole
        contract - the unit-kind table, each kind's payload shape, the
        identity columns, and the handler call signatures - as one plain
        dict, so a user can build their storage and register handlers
        from the emitted contract alone, without reading melder source.

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
            The "emit the table and the shape" verb: everything a user
            needs to build storage and register handlers - kinds,
            identity columns, payload shapes, and the call signatures
            with their registration fluent names.

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

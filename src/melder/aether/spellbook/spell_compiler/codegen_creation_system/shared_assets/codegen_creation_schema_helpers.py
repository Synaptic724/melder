import hashlib
import pickle
from typing import Any, Dict, Optional, Sequence, Tuple


class CodegenCreationSchemaHelpers:
    """
    Shared phase-11 helper surface for codegen-creation families.

    Purpose:
        Keep phase-11 row/signature/transient helpers inside the phase-11
        codegen-creation subsystem instead of reaching back into the broader
        spell-compiler phase helper surface.

    Contract:
        - Owns only phase-11 helper behavior used by codegen creation.
        - Does not own runtime state or lifecycle.
        - Returns only deterministic primitive/tuple structures.
    """

    __slots__ = ()

    @staticmethod
    def serialize_codegen_signature_part(part: Any) -> bytes:
        """
        Serialize one signature part into deterministic bytes.

        Contract:
            Type-dispatched with a stable one-byte tag per primitive
            (N/B/I/F/S/Y) so distinct types never collide on the same payload.
            Collections and unrecognized objects fall to pickle (protocol 5),
            with a `repr()` fallback if pickling raises. Callers that need
            canonical ordering across dict/set inputs must pre-freeze via
            `freeze_phase11_schema_value`; this helper does not reorder.

        Args:
            part:
                Any signature component to encode.

        Returns:
            bytes: Deterministic encoding of `part`.
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
        Build a deterministic SHA256 signature over ordered IR parts.

        Contract:
            Each part is encoded via `serialize_codegen_signature_part` and
            followed by a `|` separator byte, so ordering and grouping are
            significant - two different partitions of the same values never
            collide.

        Args:
            *parts:
                Ordered signature components.

        Returns:
            str: Hex SHA256 digest over the encoded parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(
                CodegenCreationSchemaHelpers.serialize_codegen_signature_part(part)
            )
            digest.update(b"|")
        return digest.hexdigest()

    @staticmethod
    def freeze_phase11_schema_value(value: Any) -> Any:
        """
        Normalize an arbitrary value into a deterministic schema-safe form.

        Contract:
            Primitives (None/bool/int/float/str) pass through unchanged. Dicts
            become sorted `(key, frozen-value)` tuples; lists and tuples become
            order-preserving frozen tuples; sets become repr-sorted frozen
            tuples. Anything else collapses to `repr(value)`. Recurses into
            nested containers so the whole structure is order-canonical and
            hashable.

        Args:
            value:
                Value to freeze.

        Returns:
            Any: A deterministic, hashable projection of `value`.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        CodegenCreationSchemaHelpers.freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                CodegenCreationSchemaHelpers.freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        CodegenCreationSchemaHelpers.freeze_phase11_schema_value(item)
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
        Return the instance key as an explicit two-element tuple.

        Args:
            instance_key:
                `(spell_name, occurrence-or-None)` pair.

        Returns:
            Tuple[str, Optional[int]]:
                The same pair rebuilt explicitly, so downstream code always
                sees a plain 2-tuple regardless of the input's concrete type.
        """
        return instance_key[0], instance_key[1]

    @staticmethod
    def build_fast_transient_schema(
            transient_plan: Optional[Tuple[Any, ...]],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert the phase-11 transient plan tuple into a schema-only dict.

        Contract:
            Returns None when `transient_plan` is None (no fast lane).
            Otherwise projects the positional tuple into named fields:
            step_count (index 0), root_step_index (1), call_modes (3), and the
            full dep1..dep8h dependency-slot family (indices 4..39), each copied
            into a fresh tuple. Index 2 is intentionally not part of the schema
            surface.

        Args:
            transient_plan:
                Positional transient plan tuple, or None.

        Returns:
            Optional[Dict[str, Any]]: Named schema payload, or None.
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
        Build a deterministic signature for a phase-11 transient schema.

        Contract:
            Returns None when `transient_schema` is None. Otherwise hashes
            step_count, root_step_index, call_modes, and every dep1..dep8h slot
            in fixed order via `hash_codegen_signature`, so two transient plans
            share a signature only when all those fields match.

        Args:
            transient_schema:
                Named schema from `build_fast_transient_schema`, or None.

        Returns:
            Optional[str]: Hex signature, or None.
        """
        if transient_schema is None:
            return None
        return CodegenCreationSchemaHelpers.hash_codegen_signature(
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
    def get_phase11_step_ir_rows(
            plan: Any,
            *,
            include_override_metadata: bool,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Return the plan's phase-11 schema rows, memoized on the plan.

        Purpose:
            Phase-11 build, conjure-end cache export, override
            specialization, and the family manifest each rowified the same
            immutable plan steps independently (up to 4x per lane on a cold
            pass). Every one of those consumers resolves to THIS class's
            `build_phase11_step_ir_row` (several import it under the alias
            `SharedCompilerExecutions`), so one memo on the plan serves them
            all without crossing builder surfaces.

        Contract:
            - Memo slots (`_phase11_rows_no_meta` / `_phase11_rows_with_meta`)
              are optional: plan families without the slots (or legacy/stub
              plans) silently fall back to a fresh build, byte-identical to
              the previous behavior.
            - Consumers MUST NOT mutate returned rows; enrichment-style
              consumers (the manifest) copy per row before stamping.
            - Benign build race under multi-worker scheduling: the build is
              idempotent over immutable inputs and the last writer wins with
              an equivalent tuple.
        """
        memo_attr = (
            "_phase11_rows_with_meta"
            if include_override_metadata
            else "_phase11_rows_no_meta"
        )
        rows = getattr(plan, memo_attr, None)
        if rows is not None:
            return rows
        rows = tuple(
            CodegenCreationSchemaHelpers.build_phase11_step_ir_row(
                step,
                include_override_metadata=include_override_metadata,
            )
            for step in plan.steps
        )
        try:
            setattr(plan, memo_attr, rows)
        except AttributeError:
            pass
        return rows

    @staticmethod
    def build_phase11_step_ir_row(
            step: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Build one schema-only phase-11 step row for IR export.

        Contract:
            Projects an immutable plan step into a plain dict of primitives and
            tuples (instance key, selected spell id, existence NAME, target
            kind, dependency-resolution order, frozen contract payload, lock and
            registration hints, disposal names). When `include_override_metadata`
            is False, every override-lane field (override_match_prefix and its
            length, override_keys, expects_overrides, contract_keys) is emitted
            empty/false, so the no-overrides lane's rows stay byte-identical even
            when the step object physically carries override data. Payload
            values are frozen via `freeze_phase11_schema_value` for determinism.

        Args:
            step:
                Immutable phase-11 plan step to rowify.
            include_override_metadata:
                When True (default), emit the override-lane fields; when False,
                zero them for byte-identical no-overrides rows.

        Returns:
            Dict[str, Any]: Schema-only step row.
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
                        CodegenCreationSchemaHelpers.freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        override_match_prefix = None
        override_match_prefix_len = 0
        override_keys: Tuple[Any, ...] = ()
        expects_overrides = False
        # contract_keys is override-lane metadata like the fields above: the
        # no-overrides lane must emit () regardless of what the step carries,
        # which lets both lane plans share full-metadata step objects while
        # keeping no-overrides rows byte-identical (strip point = row build).
        contract_keys: Tuple[Any, ...] = ()
        if include_override_metadata:
            override_match_prefix = step.override_match_prefix
            override_match_prefix_len = step.override_match_prefix_len
            override_keys = tuple(step.override_keys)
            expects_overrides = step.expects_overrides
            contract_keys = tuple(step.contract_keys)
        return {
            "instance_key": tuple(step.instance_key),
            "spell_id": step.spell.spell_index.selected_spell_id,
            "existence": step.existence.name,
            "creations_target_kind": step.creations_target_kind,
            "shared_instance": step.shared_instance,
            "dependency_resolution_order": dependency_resolution_order,
            "collection_param_names": tuple(sorted(step.collection_param_names)),
            "override_match_prefix": override_match_prefix,
            "override_match_prefix_len": override_match_prefix_len,
            "override_keys": override_keys,
            "expects_overrides": expects_overrides,
            "contract_keys": contract_keys,
            "allow_list_aggregation": step.allow_list_aggregation,
            "uses_positional_override": step.uses_positional_override,
            "contract_positional_override": (
                CodegenCreationSchemaHelpers.freeze_phase11_schema_value(
                    step.contract_positional_override,
                )
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

        Contract:
            Returns a fixed-order tuple of the caching-relevant step facts:
            instance key, selected spell id, existence NAME, target kind,
            dependency-resolution order, sorted collection params, the
            positional-override flag and frozen value, contract-payload presence
            and frozen sorted items, and the lock-hint and must-register flags.
            Override-lane fields are intentionally excluded - this row is the
            no-overrides cache key, so it stays stable across override churn.

        Args:
            step:
                Immutable phase-11 plan step.

        Returns:
            Tuple[Any, ...]: Deterministic signature row for cache keying.
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
                        CodegenCreationSchemaHelpers.freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.selected_spell_id,
            step.existence.name,
            step.creations_target_kind,
            dependency_resolution_order,
            tuple(sorted(step.collection_param_names)),
            bool(step.uses_positional_override),
            CodegenCreationSchemaHelpers.freeze_phase11_schema_value(
                step.contract_positional_override
            ),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.use_spell_lock_hint),
            bool(step.must_register),
        )

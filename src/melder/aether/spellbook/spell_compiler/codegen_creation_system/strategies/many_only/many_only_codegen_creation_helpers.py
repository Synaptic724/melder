import hashlib
import pickle
from typing import Any, Optional, Tuple

from melder.aether.spellbook.spell_compiler.shared_assets.codegen_signature import (
    CodegenSignature,
)


class ManyOnlyCodegenCreationHelpers:
    """
    Many-only-local phase-11 helper surface.

    Purpose:
        Provide deterministic hashing and step-row building for the many-only
        family without reaching through the old shared transient/generalized
        helper surface.
        Contract override payload entries follow the compiler-wide projection rule
        owned by the stdlib-only leaf `CodegenSignature` (2026-09-26).
    """

    __slots__ = ()

    @staticmethod
    def serialize_signature_part(part: Any) -> bytes:
        """
        Serialize one signature part into deterministic bytes.

        Contract:
            Type-dispatched with a stable one-byte tag per primitive
            (N/B/I/F/S/Y) so distinct types never collide on the same payload.
            Collections and unrecognized objects fall to pickle (protocol 5),
            with a `repr()` fallback if pickling raises. Callers needing
            canonical ordering across dict/set inputs pre-freeze via
            `freeze_value`; this helper does not reorder.

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
                return pickle.dumps(part, protocol=5)
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
            return b"S" + part.encode("utf-8")
        if part_type is bytes:
            return b"Y" + part
        if part_type is bytearray:
            return b"Y" + bytes(part)
        try:
            return pickle.dumps(part, protocol=5)
        except (pickle.PickleError, TypeError, AttributeError):
            return repr(part).encode("utf-8")

    @staticmethod
    def hash_signature(*parts: Any) -> str:
        """
        Build a deterministic SHA256 signature over ordered parts.

        Contract:
            Each part is encoded via `serialize_signature_part` and followed by
            a `|` separator byte, so ordering and grouping are significant.

        Args:
            *parts:
                Ordered signature components.

        Returns:
            str: Hex SHA256 digest over the encoded parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(
                ManyOnlyCodegenCreationHelpers.serialize_signature_part(part)
            )
            digest.update(b"|")
        return digest.hexdigest()


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
                The same pair rebuilt explicitly as a plain 2-tuple.
        """
        return instance_key[0], instance_key[1]

    @staticmethod
    def build_no_overrides_step_signature_row(
            step: Any,
    ) -> Tuple[Any, ...]:
        """
        Build one deterministic many-only no-overrides step signature row.

        Contract:
            Returns a fixed-order tuple of the caching-relevant step facts:
            instance key, selected spell id, dependency-resolution order, sorted
            collection params, positional-override flag + projected value,
            contract-payload presence + projected sorted items (a scalar entry as
            itself, any other entry as its phase-9 reference, 2026-09-26), and
            disposal-method presence + names. Override-lane fields are excluded - this row is the
            no-overrides cache key.

        Args:
            step:
                Immutable many-only plan step.

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
            payload_refs = step.contract_payload_refs
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        CodegenSignature.project_contract_payload_entry(
                            param_name, value, payload_refs,
                        ),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.selected_spell_id,
            dependency_resolution_order,
            tuple(sorted(step.collection_param_names)),
            bool(step.uses_positional_override),
            CodegenSignature.project_contract_payload_entry(
                "__args__", step.contract_positional_override, step.contract_payload_refs,
            ),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.spell.has_disposal_methods),
            tuple(step.spell.disposal_method_names),
        )


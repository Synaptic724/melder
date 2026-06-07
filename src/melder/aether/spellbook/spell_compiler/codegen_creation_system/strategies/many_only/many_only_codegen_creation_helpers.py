import hashlib
import pickle
from typing import Any, Dict, Optional, Tuple


class ManyOnlyCodegenCreationHelpers:
    """
    Many-only-local phase-11 helper surface.

    Purpose:
        Provide deterministic hashing and step-row building for the many-only
        family without reaching through the old shared transient/generalized
        helper surface.
    """

    __slots__ = ()

    @staticmethod
    def serialize_signature_part(part: Any) -> bytes:
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
        Build a deterministic hash from primitive or tuple-backed parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(
                ManyOnlyCodegenCreationHelpers.serialize_signature_part(part)
            )
            digest.update(b"|")
        return digest.hexdigest()

    @staticmethod
    def freeze_value(value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic tuple-backed forms.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        ManyOnlyCodegenCreationHelpers.freeze_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                ManyOnlyCodegenCreationHelpers.freeze_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        ManyOnlyCodegenCreationHelpers.freeze_value(item)
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
        Return one explicit two-element instance-key tuple.
        """
        return instance_key[0], instance_key[1]

    @staticmethod
    def build_no_overrides_step_signature_row(
            step: Any,
    ) -> Tuple[Any, ...]:
        """
        Build one deterministic many-only no-overrides step signature row.
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
                        ManyOnlyCodegenCreationHelpers.freeze_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.current,
            dependency_resolution_order,
            bool(step.uses_positional_override),
            ManyOnlyCodegenCreationHelpers.freeze_value(
                step.contract_positional_override
            ),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.spell.has_disposal_methods),
            tuple(step.spell.disposal_method_names),
        )

    @staticmethod
    def build_override_step_row(
            step: Any,
    ) -> Dict[str, Any]:
        """
        Build one many-only-local override step row.
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
                        ManyOnlyCodegenCreationHelpers.freeze_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return {
            "instance_key": tuple(step.instance_key),
            "spell_id": step.spell.spell_index.current,
            "shared_instance": step.shared_instance,
            "dependency_resolution_order": dependency_resolution_order,
            "uses_positional_override": step.uses_positional_override,
            "contract_positional_override": (
                ManyOnlyCodegenCreationHelpers.freeze_value(
                    step.contract_positional_override
                )
            ),
            "has_contract_payload": step.has_contract_payload,
            "contract_payload_items": contract_payload_items,
            "override_match_prefix": step.override_match_prefix,
            "override_match_prefix_len": step.override_match_prefix_len,
            "has_disposal_methods": bool(step.spell.has_disposal_methods),
            "disposal_method_names": tuple(step.spell.disposal_method_names),
        }

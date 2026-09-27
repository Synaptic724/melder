"""
Frozen reference copy of the pre-unification codegen signature algorithm.

Purpose:
    Serve as the byte-compatibility oracle for `CodegenSignature`: these three
    functions are verbatim copies (modulo the class name) of the bodies that
    `SharedCompilerExecutions` and `CodegenCreationSchemaHelpers` carried before
    the single implementation existed. Tests compare the shipped surface against
    them on real compiler parts, so a byte drift for an input that was already
    deterministic is caught without an owner-run capture.

Contract:
    - Never import this module from runtime code.
    - Do not "fix" these bodies; their known non-determinism (hash-seed-ordered
      sets, `repr` fallback with addresses) is the defect the tests document.
"""
import hashlib
import pickle
from typing import Any


def reference_serialize_codegen_signature_part(part: Any) -> bytes:
    """
    Serialize one signature part exactly as the shipped facades did before.

    Args:
        part: One primitive/tuple/dict/set signature segment.

    Returns:
        bytes: The pre-unification encoding of `part`.
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


def reference_hash_codegen_signature(*parts: Any) -> str:
    """
    Hash ordered parts exactly as the shipped facades did before.

    Args:
        *parts: Ordered signature components.

    Returns:
        str: Hex SHA256 digest over the reference encoding of the parts.
    """
    digest = hashlib.sha256()
    for part in parts:
        digest.update(reference_serialize_codegen_signature_part(part))
        digest.update(b"|")
    return digest.hexdigest()


def reference_freeze_phase11_schema_value(value: Any) -> Any:
    """
    Freeze a value exactly as the shipped facades did before.

    Args:
        value: Value to freeze.

    Returns:
        Any: The pre-unification frozen projection (`repr` for any object).
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return tuple(
            sorted(
                (
                    key,
                    reference_freeze_phase11_schema_value(item),
                )
                for key, item in value.items()
            )
        )
    if isinstance(value, (list, tuple)):
        return tuple(
            reference_freeze_phase11_schema_value(item)
            for item in value
        )
    if isinstance(value, set):
        return tuple(
            sorted(
                (
                    reference_freeze_phase11_schema_value(item)
                    for item in value
                ),
                key=repr,
            )
        )
    return repr(value)

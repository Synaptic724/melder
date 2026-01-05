"""
Payload validation helpers for command scripts.

Purpose
- Provide consistent validation and error details for command payloads.
- Surface payload issues as structured PayloadError exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass
class PayloadError(Exception):
    """
    Error raised when command payload validation fails.

    Attributes:
        code (str): Stable error code describing the failure.
        details (dict[str, Any]): Structured error details payload.

    Contract:
        - code should be machine-readable and stable.
        - details should include command_name and payload context.
    """

    code: str
    details: dict[str, Any]


def _payload_keys(payload: Mapping[str, Any]) -> list[str]:
    """
    Return sorted payload keys for error context.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.

    Returns:
        list[str]: Sorted payload keys.
    """

    return sorted(payload.keys())


def require_field(
    payload: Mapping[str, Any],
    field: str,
    expected: str,
    command_name: str,
) -> Any:
    """
    Require a field to exist in the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        expected (str): Human-readable expected type description.
        command_name (str): Command name for error context.

    Returns:
        Any: Payload value for the field.

    Raises:
        PayloadError: If the field is missing.
    """

    if field not in payload:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": field,
                "expected": expected,
                "payload_keys": _payload_keys(payload),
            },
        )
    return payload[field]


def require_string(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    *,
    allow_empty: bool = False,
) -> str:
    """
    Require a non-empty string field in the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        command_name (str): Command name for error context.
        allow_empty (bool): Whether to accept empty strings.

    Returns:
        str: Payload string value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    value = require_field(payload, field, "string", command_name)
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "string",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    if not allow_empty and not value.strip():
        raise PayloadError(
            code="payload_empty",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "non-empty string",
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def optional_string(
    payload: Mapping[str, Any],
    field: str,
    *,
    command_name: str,
    default: str | None = None,
    allow_empty: bool = False,
) -> str | None:
    """
    Read an optional string field from the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to read.
        command_name (str): Command name for error context.
        default (str | None): Default value when missing.
        allow_empty (bool): Whether to accept empty strings.

    Returns:
        str | None: String value or default.

    Raises:
        PayloadError: If the field exists but is not a string.
    """

    if field not in payload:
        return default
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "string",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    if not allow_empty and not value.strip():
        return default
    return value


def require_bool(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
) -> bool:
    """
    Require a boolean field in the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        command_name (str): Command name for error context.

    Returns:
        bool: Payload boolean value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    value = require_field(payload, field, "boolean", command_name)
    if not isinstance(value, bool):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "boolean",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def optional_bool(
    payload: Mapping[str, Any],
    field: str,
    *,
    command_name: str,
    default: bool | None = None,
) -> bool | None:
    """
    Read an optional boolean field from the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to read.
        command_name (str): Command name for error context.
        default (bool | None): Default value when missing.

    Returns:
        bool | None: Boolean value or default.

    Raises:
        PayloadError: If the field exists but is not a boolean.
    """

    if field not in payload:
        return default
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, bool):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "boolean",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def require_int(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
) -> int:
    """
    Require an integer field in the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        command_name (str): Command name for error context.

    Returns:
        int: Payload integer value.

    Raises:
        PayloadError: If the field is missing or not an integer.
    """

    value = require_field(payload, field, "integer", command_name)
    if not isinstance(value, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "integer",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def optional_int(
    payload: Mapping[str, Any],
    field: str,
    *,
    command_name: str,
    default: int | None = None,
) -> int | None:
    """
    Read an optional integer field from the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to read.
        command_name (str): Command name for error context.
        default (int | None): Default value when missing.

    Returns:
        int | None: Integer value or default.

    Raises:
        PayloadError: If the field exists but is not an integer.
    """

    if field not in payload:
        return default
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "integer",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def require_choice(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    choices: Iterable[str],
) -> str:
    """
    Require a string field that must match one of the allowed choices.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        command_name (str): Command name for error context.
        choices (Iterable[str]): Allowed values.

    Returns:
        str: Payload string value.

    Raises:
        PayloadError: If the field is missing or not an allowed value.
    """

    value = require_string(payload, field, command_name)
    if value not in choices:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": f"one of {list(choices)}",
                "actual": value,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def require_list(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
) -> list[Any]:
    """
    Require a list field in the payload.

    Purpose:
        Enforce list-shaped payload fields for command inputs that expect
        ordered collections (e.g., explicit path lists).

    Contract:
        - Raises PayloadError when the field is missing.
        - Raises PayloadError when the field is not a list.
        - Returns the list value without coercion or mutation.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to require.
        command_name (str): Command name for error context.

    Returns:
        list[Any]: Payload list value.

    Raises:
        PayloadError: If the field is missing or not a list.
    """

    value = require_field(payload, field, "list", command_name)
    if not isinstance(value, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "list",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value


def optional_list(
    payload: Mapping[str, Any],
    field: str,
    *,
    command_name: str,
    default: list[Any] | None = None,
) -> list[Any] | None:
    """
    Read an optional list field from the payload.

    Args:
        payload (Mapping[str, Any]): Payload dictionary.
        field (str): Field name to read.
        command_name (str): Command name for error context.
        default (list[Any] | None): Default value when missing.

    Returns:
        list[Any] | None: List value or default.

    Raises:
        PayloadError: If the field exists but is not a list.
    """

    if field not in payload:
        return default
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "list",
                "actual_type": type(value).__name__,
                "payload_keys": _payload_keys(payload),
            },
        )
    return value

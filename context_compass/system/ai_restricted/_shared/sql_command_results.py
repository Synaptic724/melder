"""
Command result helpers for SQL tool and query scripts.

Purpose
- Provide CommandResult construction for sql_tools/sql_queries scripts.
- Keep SQL scripts independent from the command runner and hook pipeline.

Contract
- Error details are JSON-encoded for machine parsing.
- Helpers return CommandResult instances from command_contracts.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandError,
    CommandResult,
    build_error_details,
)
from context_compass.system.ai_restricted._shared.command_payload import PayloadError


def error_result(
    *,
    code: str,
    meaning: str,
    details: Mapping[str, Any],
    output: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    artifacts: Sequence[str] | None = None,
    queries: Sequence[dict[str, Any]] | None = None,
    extra_errors: Sequence[CommandError] | None = None,
) -> CommandResult:
    """
    Build a CommandResult representing an error for SQL scripts.

    Args:
        code (str): Stable error code identifier.
        meaning (str): Human-readable error description.
        details (Mapping[str, Any]): Structured error details payload.
        output (Mapping[str, Any] | None): Optional output payload.
        metadata (Mapping[str, Any] | None): Optional metadata payload.
        artifacts (Sequence[str] | None): Optional artifact references.
        queries (Sequence[dict[str, Any]] | None): Optional pending input queries.
        extra_errors (Sequence[CommandError] | None): Additional errors to append.

    Returns:
        CommandResult: Error result payload.

    Contract:
        - details are JSON-encoded for machine parsing.
        - output and metadata are shallow-copied to avoid mutation.
    """

    errors = [
        CommandError(
            code=code,
            meaning=meaning,
            details=build_error_details(details),
        )
    ]
    if extra_errors:
        errors.extend(extra_errors)
    return CommandResult(
        status="error",
        output=dict(output or {}),
        metadata=dict(metadata or {}),
        artifacts=list(artifacts or []),
        errors=errors,
        queries=list(queries or []),
    )


def payload_error_result(command_name: str, error: PayloadError) -> CommandResult:
    """
    Convert a PayloadError into a CommandResult for SQL scripts.

    Args:
        command_name (str): Command name for error context.
        error (PayloadError): Payload validation error instance.

    Returns:
        CommandResult: Error result describing the payload failure.

    Contract:
        - Payload error details are preserved and annotated with command_name.
    """

    details = dict(error.details)
    details.setdefault("command_name", command_name)
    return error_result(
        code=error.code,
        meaning="Payload validation failed.",
        details=details,
    )


def exception_result(
    command_name: str,
    exc: Exception,
    *,
    code: str = "command_failed",
    meaning: str = "Command execution failed.",
    details: Mapping[str, Any] | None = None,
) -> CommandResult:
    """
    Convert an exception into a CommandResult for SQL scripts.

    Args:
        command_name (str): Command name for error context.
        exc (Exception): Exception raised during execution.
        code (str): Stable error code identifier.
        meaning (str): Human-readable error description.
        details (Mapping[str, Any] | None): Optional details to merge.

    Returns:
        CommandResult: Error result capturing exception details.

    Contract:
        - Exception type and message are always included in details.
    """

    payload = {
        "command_name": command_name,
        "exception_type": exc.__class__.__name__,
        "exception_message": str(exc),
    }
    if details:
        payload.update(details)
    return error_result(code=code, meaning=meaning, details=payload)


def ok_result(
    *,
    output: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    artifacts: Sequence[str] | None = None,
    queries: Sequence[dict[str, Any]] | None = None,
) -> CommandResult:
    """
    Build a CommandResult representing a successful SQL script run.

    Args:
        output (Mapping[str, Any] | None): Output payload to return.
        metadata (Mapping[str, Any] | None): Metadata payload to return.
        artifacts (Sequence[str] | None): Artifact references to return.
        queries (Sequence[dict[str, Any]] | None): Pending input requests to return.

    Returns:
        CommandResult: Success result payload.

    Contract:
        - output and metadata are shallow-copied to avoid mutation.
    """

    return CommandResult(
        status="ok",
        output=dict(output or {}),
        metadata=dict(metadata or {}),
        artifacts=list(artifacts or []),
        queries=list(queries or []),
    )

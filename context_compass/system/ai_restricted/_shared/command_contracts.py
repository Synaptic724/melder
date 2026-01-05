"""
Command execution contracts shared across the command runner and scripts.

Purpose
- Define the data structures used by commands, hooks, and the runner.
- Provide helpers for producing machine-readable error payloads.

Contract
- CommandError.details must be JSON-encoded text for machine parsing.
- CommandResult.output is treated as immutable by hook pipelines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ExecutionContext:
    """
    Execution context passed through the command runner pipeline.

    Attributes:
        command_name (str): Command name being executed.
        agent_id (str | None): Agent identifier when available.
        work_id (str | None): Work identifier when required by policy.
        correlation_id (str | None): Correlation identifier for tracing.
        chain_depth (int): Current chain depth for activation hooks.
        annotations (dict[str, Any]): Mutable annotations for hooks or callers.

    Contract:
        - command_name identifies the command entry resolved from the registry.
        - annotations is caller-owned and may be mutated by hook pipelines.
    """

    command_name: str
    agent_id: str | None
    work_id: str | None
    correlation_id: str | None
    chain_depth: int = 0
    annotations: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandError:
    """
    Structured error payload emitted by command execution.

    Attributes:
        code (str): Stable error code for machine handling.
        meaning (str): Human-readable description of the failure.
        details (str | None): JSON-encoded details for machine parsing.

    Contract:
        - code must be stable and non-empty.
        - meaning should be actionable and concise.
        - details must be JSON text when provided.
    """

    code: str
    meaning: str
    details: str | None = None


@dataclass(frozen=True)
class CommandResult:
    """
    Result envelope for command execution.

    Attributes:
        status (str): Execution status (ok, error, pending_input).
        output (dict[str, Any]): Immutable command output payload.
        metadata (dict[str, Any]): Hook-writable metadata.
        artifacts (list[str]): Paths or identifiers for large artifacts.
        errors (list[CommandError]): Structured error list when status is error.
        queries (list[dict[str, Any]]): Pending input requests for pause/resume.

    Contract:
        - output is treated as immutable by hooks.
        - metadata may be extended by interceptors and decorators.
    """

    status: str
    output: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    errors: list[CommandError] = field(default_factory=list)
    queries: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class NextAction:
    """
    Follow-on action emitted by an activation hook.

    Attributes:
        command_name (str): Command name to execute next.
        payload (dict[str, Any]): Payload to pass to the next command.

    Contract:
        - command_name must match a registered command.
    """

    command_name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class HookResult:
    """
    Result returned by a hook invocation.

    Attributes:
        metadata_patch (dict[str, Any]): Metadata updates to apply.
        next_actions (list[NextAction]): Activation-driven follow-on commands.
        errors (list[CommandError]): Errors to halt execution.

    Contract:
        - metadata_patch merges into result metadata.
        - next_actions are only honored during activation.
    """

    metadata_patch: dict[str, Any] = field(default_factory=dict)
    next_actions: list[NextAction] = field(default_factory=list)
    errors: list[CommandError] = field(default_factory=list)


def build_error_details(details: Mapping[str, Any]) -> str:
    """
    Encode structured error details as JSON.

    Args:
        details (Mapping[str, Any]): Error detail payload.

    Returns:
        str: JSON-encoded details string.

    Contract:
        - Uses minified JSON for compact machine parsing.
    """

    return json.dumps(details, separators=(",", ":"))


def error_result(
    code: str,
    meaning: str,
    details: Mapping[str, Any],
    *,
    output: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    artifacts: list[str] | None = None,
    queries: list[dict[str, Any]] | None = None,
) -> CommandResult:
    """
    Build a CommandResult representing an error.

    Args:
        code (str): Stable error code.
        meaning (str): Human-readable error description.
        details (Mapping[str, Any]): Structured error details payload.
        output (Mapping[str, Any] | None): Output payload to return.
        metadata (Mapping[str, Any] | None): Metadata payload to return.
        artifacts (list[str] | None): Artifact references to return.
        queries (list[dict[str, Any]] | None): Pending input requests to return.

    Returns:
        CommandResult: Error result payload with JSON details.
    """

    return CommandResult(
        status="error",
        output=dict(output or {}),
        metadata=dict(metadata or {}),
        artifacts=list(artifacts or []),
        errors=[CommandError(code=code, meaning=meaning, details=build_error_details(details))],
        queries=list(queries or []),
    )


def ok_result(
    *,
    output: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    artifacts: list[str] | None = None,
    queries: list[dict[str, Any]] | None = None,
) -> CommandResult:
    """
    Build a CommandResult representing a successful command run.

    Args:
        output (Mapping[str, Any] | None): Output payload to return.
        metadata (Mapping[str, Any] | None): Metadata payload to return.
        artifacts (list[str] | None): Artifact references to return.
        queries (list[dict[str, Any]] | None): Pending input requests to return.

    Returns:
        CommandResult: Success result payload.
    """

    return CommandResult(
        status="ok",
        output=dict(output or {}),
        metadata=dict(metadata or {}),
        artifacts=list(artifacts or []),
        queries=list(queries or []),
    )

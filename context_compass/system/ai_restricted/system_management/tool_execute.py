"""
CLI dispatcher for registry-backed ToolCommandAPI execution.

Purpose
- Provide a shell-friendly entrypoint for running commands by name.
- Parse JSON payloads and forward them to execute_command.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.json_io import dump_minified, load_json
from context_compass.system.ai_restricted.system_management.tool_command_api import (
    CommandResult,
    execute_command,
)


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """
    Require that a JSON payload value is a mapping.

    Args:
        value (Any): Parsed JSON value.
        label (str): Payload label used for error messages.

    Returns:
        dict[str, Any]: Payload mapping.

    Raises:
        ValueError: If the payload is not a JSON object.
    """

    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _load_payload(payload_json: str | None, payload_path: str | None) -> dict[str, Any]:
    """
    Load a command payload from JSON text or a file path.

    Args:
        payload_json (str | None): Inline JSON payload string.
        payload_path (str | None): Path to a JSON payload file.

    Returns:
        dict[str, Any]: Parsed payload mapping.

    Raises:
        ValueError: If inputs are missing, conflicting, or invalid.
    """

    if payload_json and payload_path:
        raise ValueError("payload_json and payload_path are mutually exclusive.")
    if payload_path:
        data = load_json(Path(payload_path))
        return _require_mapping(data, "payload")
    if payload_json is not None:
        try:
            data = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise ValueError("payload_json must be valid JSON.") from exc
        return _require_mapping(data, "payload")
    raise ValueError("payload_json or payload_path is required.")


def _load_annotations(annotations_json: str | None) -> dict[str, Any]:
    """
    Parse optional annotations JSON.

    Args:
        annotations_json (str | None): Inline JSON string for annotations.

    Returns:
        dict[str, Any]: Parsed annotations mapping.

    Raises:
        ValueError: If annotations_json is invalid or not a JSON object.
    """

    if annotations_json is None:
        return {}
    try:
        data = json.loads(annotations_json)
    except json.JSONDecodeError as exc:
        raise ValueError("annotations_json must be valid JSON.") from exc
    return _require_mapping(data, "annotations")


def _result_payload(result: CommandResult) -> dict[str, Any]:
    """
    Convert a CommandResult into a JSON-serializable payload.

    Args:
        result (CommandResult): Command execution result.

    Returns:
        dict[str, Any]: Serialized CommandResult payload.
    """

    return {
        "status": result.status,
        "output": result.output,
        "metadata": result.metadata,
        "artifacts": result.artifacts,
        "errors": [error.__dict__ for error in result.errors],
        "queries": result.queries,
    }


def main() -> None:
    """
    CLI entrypoint for ToolCommandAPI dispatch.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When payload parsing fails or execution returns non-ok.
    """

    parser = argparse.ArgumentParser(
        description="Execute a registry-backed command via ToolCommandAPI."
    )
    parser.add_argument("--command-name", required=True, help="Command name to execute")
    parser.add_argument("--payload-json", default=None, help="Inline JSON payload")
    parser.add_argument("--payload-path", default=None, help="Path to JSON payload file")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", default=None, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier")
    parser.add_argument("--correlation-id", default=None, help="Correlation identifier")
    parser.add_argument("--annotations-json", default=None, help="Inline JSON annotations")
    parser.add_argument(
        "--max-chain-depth",
        type=int,
        default=3,
        help="Maximum activation chain depth",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        payload = _load_payload(args.payload_json, args.payload_path)
        annotations = _load_annotations(args.annotations_json)
    except ValueError as exc:
        logger.error("tool_execute input error: %s", exc)
        raise SystemExit(1)

    result = execute_command(
        command_name=args.command_name,
        payload=payload,
        repo_root=args.repo_root,
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=args.correlation_id,
        annotations=annotations,
        max_chain_depth=args.max_chain_depth,
    )
    result_json = dump_minified(_result_payload(result))
    if result.status != "ok":
        logger.error(result_json)
        raise SystemExit(1)
    logger.info(result_json)


if __name__ == "__main__":
    main()

"""
SQLite-backed command runner for registry-driven command execution.

Purpose
- Resolve command metadata from SQLite command registry tables.
- Provide an in-process execution surface for command and hook pipelines.

Contract
- Registry lookups are read-only and happen per invocation.
- Hooks are discovered from SQLite hook registries via sqlite_crud.
- Commands execute through their declared execution spec (module/script).
"""

from __future__ import annotations

import importlib
import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Mapping, Sequence

from context_compass.system.ai_restricted._shared.command_contracts import (
    build_error_details,
)

if TYPE_CHECKING:
    from context_compass.system.ai_restricted.database_management.sqlite_crud import (
        SqliteCrudError,
    )


COMMAND_COLUMNS: Sequence[str] = (
    "command_name",
    "category",
    "entry",
    "summary",
    "requires_certification",
    "requires_work_id",
    "feature_flag",
    "notes",
    "spec_json",
    "registry_schema_version",
    "registry_generated_at",
    "registry_updated_at",
)
HOOK_PHASE_ORDER = {"pre": 10, "activation": 20, "post": 30, "on_error": 40}
DEFAULT_HOOK_ORDER = 100
DEFAULT_ENTRYPOINT = "run_hook"
COMMAND_REGISTRY_SYSTEM_TABLE = "command_registry_system"
COMMAND_REGISTRY_USER_TABLE = "command_registry_user"
COMMAND_REGISTRY_ACTION = "by_command_name"
COMMAND_REGISTRY_ACTOR = "system:command_runner"
HOOK_REGISTRY_SYSTEM_TABLE = "hook_registry_system"
HOOK_REGISTRY_USER_TABLE = "hook_registry_user"
HOOK_REGISTRY_OPERATION = "read"
HOOK_REGISTRY_ACTION = "list_hooks"


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
        details (str | None): Additional context for debugging.

    Contract:
        - code must be stable and non-empty.
        - meaning should be actionable and concise.
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


@dataclass(frozen=True)
class HookSpec:
    """
    Hook metadata discovered from SQLite hook registries.

    Attributes:
        hook_id (str): Stable hook identifier.
        phase (str): Hook phase (pre, activation, post).
        order (int): Ordering within the phase.
        script_kind (str): Script kind (python).
        path (Path): Path to the hook script.
        entrypoint (str): Hook entrypoint callable name.
        applies_to (dict[str, list[str]] | None): Optional selector.

    Contract:
        - hook_id must be unique across all hooks.
        - phase must be one of the supported hook phases.
        - script_kind must be a supported hook script kind.
    """

    hook_id: str
    phase: str
    order: int
    script_kind: str
    path: Path
    entrypoint: str
    applies_to: dict[str, list[str]] | None


@dataclass(frozen=True)
class CommandRecord:
    """
    Parsed command registry entry loaded from SQLite.

    Attributes:
        command_name (str): Unique command name.
        category (str): Command category or domain.
        entry (str): Execution entry string.
        summary (str): Short human-readable summary.
        requires_certification (bool): Whether certification is required.
        requires_work_id (bool): Whether a work id is required.
        feature_flag (str | None): Feature flag gate for the command.
        notes (str | None): Additional notes for operators.
        spec (dict[str, Any] | None): Optional rich command spec.
        registry_schema_version (int): Registry schema version.
        registry_generated_at (str | None): Registry generation timestamp.
        registry_updated_at (str | None): Registry update timestamp.

    Contract:
        - command_name is unique within the registry table.
        - spec is parsed from JSON when present.
    """

    command_name: str
    category: str
    entry: str
    summary: str
    requires_certification: bool
    requires_work_id: bool
    feature_flag: str | None
    notes: str | None
    spec: dict[str, Any] | None
    registry_schema_version: int
    registry_generated_at: str | None
    registry_updated_at: str | None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the record into a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: JSON-friendly command record representation.
        """

        return {
            "command_name": self.command_name,
            "category": self.category,
            "entry": self.entry,
            "summary": self.summary,
            "requires_certification": self.requires_certification,
            "requires_work_id": self.requires_work_id,
            "feature_flag": self.feature_flag,
            "notes": self.notes,
            "spec": self.spec,
            "registry_schema_version": self.registry_schema_version,
            "registry_generated_at": self.registry_generated_at,
            "registry_updated_at": self.registry_updated_at,
        }


class HookRegistryLoadError(RuntimeError):
    """
    Error raised when hook registry discovery fails.

    Attributes:
        code (str): Stable error code for hook discovery failures.
        meaning (str): Human-readable error description.
        details (dict[str, Any]): Structured error details payload.

    Contract:
        - code must be stable and non-empty.
        - details must be JSON-serializable for error reporting.
    """

    def __init__(self, code: str, meaning: str, details: Mapping[str, Any]) -> None:
        """
        Initialize a hook registry error payload.

        Args:
            code (str): Stable error code identifier.
            meaning (str): Human-readable error description.
            details (Mapping[str, Any]): Structured error details payload.
        """

        super().__init__(meaning)
        self.code = code
        self.meaning = meaning
        self.details = dict(details)


@dataclass(frozen=True)
class ExecutionSpec:
    """
    Command execution spec parsed from a command record.

    Attributes:
        module (str | None): Python module path to import.
        script_path (Path | None): Script path to import.
        entrypoint (str): Callable entrypoint name.

    Contract:
        - module or script_path must be provided.
        - entrypoint must be a non-empty string.
    """

    module: str | None
    script_path: Path | None
    entrypoint: str


def _command_registry_scope(table_name: str) -> str:
    """
    Resolve the CRUD scope for a command registry table name.

    Args:
        table_name (str): Registry table name.

    Returns:
        str: CRUD scope name (system or user).

    Raises:
        RuntimeError: If the table is not a supported command registry.
    """

    if table_name == COMMAND_REGISTRY_SYSTEM_TABLE:
        return "system"
    if table_name == COMMAND_REGISTRY_USER_TABLE:
        return "user"
    raise RuntimeError(
        "CommandRunner only supports system or user command registries."
    )


def _record_dict_to_row(record: Mapping[str, Any]) -> tuple:
    """
    Convert a registry record mapping into a COMMAND_COLUMNS tuple.

    Args:
        record (Mapping[str, Any]): Registry record mapping.

    Returns:
        tuple: Row values in COMMAND_COLUMNS order.

    Raises:
        ValueError: If required columns are missing from the record.
    """

    try:
        return tuple(record[column] for column in COMMAND_COLUMNS)
    except KeyError as exc:
        raise ValueError(
            "Command registry record is missing required columns."
        ) from exc


class CommandRunner:
    """
    Resolve and execute commands backed by SQLite command registries.

    Purpose
    - Load command metadata from the registry.
    - Execute commands and hook pipelines deterministically.

    Contract
    - Registry access is read-only and per-call to avoid shared state.
    - Hook ordering is deterministic based on phase, order, and id.
    """

    def __init__(
        self,
        db_path: Path,
        table_name: str,
        context_compass_root: Path,
        max_chain_depth: int = 3,
    ) -> None:
        """
        Initialize the command runner for a specific registry table.

        Args:
            db_path (Path): SQLite database path.
            table_name (str): Registry table name.
            context_compass_root (Path): Root directory of context_compass.
            max_chain_depth (int): Maximum activation chain depth.

        Raises:
            ValueError: If configuration arguments are invalid.
        """

        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError("table_name must be a non-empty string.")
        if any(char in table_name for char in ("\"", "'", ";", " ")):
            raise ValueError("table_name contains unsafe characters.")
        if max_chain_depth < 0:
            raise ValueError("max_chain_depth must be zero or positive.")
        self._db_path = db_path
        self._table_name = table_name
        self._context_compass_root = context_compass_root
        self._max_chain_depth = max_chain_depth

    def describe_command(self, command_name: str) -> CommandRecord | None:
        """
        Load a command record by name.

        Args:
            command_name (str): Command name to load.

        Returns:
            CommandRecord | None: Parsed command record, or None if missing.

        Raises:
            ValueError: If stored spec JSON is invalid.
        """

        row = self._fetch_command_row(command_name)
        if row is None:
            return None
        return self._row_to_record(row)

    def execute(
        self, command_name: str, payload: Mapping[str, Any], context: ExecutionContext
    ) -> CommandResult:
        """
        Execute a command using the registry-backed interface.

        Args:
            command_name (str): Command name to execute.
            payload (Mapping[str, Any]): JSON-serializable kwargs payload.
            context (ExecutionContext): Execution context for the run.

        Returns:
            CommandResult: Structured result payload.

        Contract:
            - Returns command_not_found when the registry entry is missing.
            - Returns execution_not_configured when execution metadata is missing.
            - Applies on_error hooks for any error outcome.
        """

        normalized_context = self._normalize_context(context, command_name)
        record = self.describe_command(command_name)
        if record is None:
            return self._error_result(
                code="command_not_found",
                meaning="Command is not registered.",
                details={"command_name": command_name},
            )
        if normalized_context.chain_depth > self._max_chain_depth:
            return self._error_result(
                code="chain_depth_exceeded",
                meaning="Activation chain depth exceeded.",
                details={
                    "command_name": command_name,
                    "max_depth": self._max_chain_depth,
                    "chain_depth": normalized_context.chain_depth,
                },
            )

        try:
            hooks = self._load_hooks(normalized_context)
        except HookRegistryLoadError as exc:
            return self._error_result(
                code=exc.code,
                meaning=exc.meaning,
                details=exc.details,
            )

        pre_hooks = self._select_hooks(hooks, "pre", record)
        pre_result = CommandResult(status="ok")
        pre_result, pre_actions, pre_errors = self._apply_hooks(
            pre_hooks, normalized_context, payload, pre_result
        )
        if pre_actions:
            return self._apply_error_hooks(
                hooks,
                record,
                normalized_context,
                payload,
                self._error_result(
                    code="invalid_hook_phase",
                    meaning="Pre-hooks cannot emit activation actions.",
                    details={"phase": "pre", "command_name": command_name},
                    metadata=pre_result.metadata,
                ),
            )
        if pre_errors:
            return self._apply_error_hooks(
                hooks,
                record,
                normalized_context,
                payload,
                CommandResult(
                    status="error",
                    errors=pre_errors,
                    metadata=pre_result.metadata,
                ),
            )

        core_result = self._execute_core(record, payload, normalized_context)
        core_result = CommandResult(
            status=core_result.status,
            output=core_result.output,
            metadata=self._merge_metadata(pre_result.metadata, core_result.metadata),
            artifacts=core_result.artifacts,
            errors=core_result.errors,
            queries=core_result.queries,
        )
        if core_result.status != "ok":
            if core_result.status == "pending_input":
                return core_result
            return self._apply_error_hooks(
                hooks, record, normalized_context, payload, core_result
            )

        activation_hooks = self._select_hooks(hooks, "activation", record)
        activation_result, next_actions, activation_errors = self._apply_hooks(
            activation_hooks, normalized_context, payload, core_result
        )
        if activation_errors:
            return self._apply_error_hooks(
                hooks,
                record,
                normalized_context,
                payload,
                CommandResult(
                    status="error",
                    errors=activation_errors,
                    metadata=activation_result.metadata,
                    output=activation_result.output,
                    artifacts=activation_result.artifacts,
                    queries=activation_result.queries,
                ),
            )

        chained_result = activation_result
        if next_actions:
            chained_result = self._execute_next_actions(
                activation_result, normalized_context, next_actions
            )
            if chained_result.status != "ok":
                if chained_result.status == "pending_input":
                    return chained_result
                return self._apply_error_hooks(
                    hooks,
                    record, normalized_context, payload, chained_result
                )

        post_hooks = self._select_hooks(hooks, "post", record)
        post_result, post_actions, post_errors = self._apply_hooks(
            post_hooks, normalized_context, payload, chained_result
        )
        if post_actions:
            return self._apply_error_hooks(
                hooks,
                record,
                normalized_context,
                payload,
                self._error_result(
                    code="invalid_hook_phase",
                    meaning="Post-hooks cannot emit activation actions.",
                    details={"phase": "post", "command_name": command_name},
                    metadata=post_result.metadata,
                    output=post_result.output,
                    artifacts=post_result.artifacts,
                    queries=post_result.queries,
                ),
            )
        if post_errors:
            return self._apply_error_hooks(
                hooks,
                record,
                normalized_context,
                payload,
                CommandResult(
                    status="error",
                    errors=post_errors,
                    metadata=post_result.metadata,
                    output=post_result.output,
                    artifacts=post_result.artifacts,
                    queries=post_result.queries,
                ),
            )

        return post_result

    def _normalize_context(
        self, context: ExecutionContext, command_name: str
    ) -> ExecutionContext:
        """
        Normalize the execution context for a command invocation.

        Args:
            context (ExecutionContext): Provided execution context.
            command_name (str): Command name for execution.

        Returns:
            ExecutionContext: Context with a consistent command_name.
        """

        if context.command_name == command_name:
            return context
        return ExecutionContext(
            command_name=command_name,
            agent_id=context.agent_id,
            work_id=context.work_id,
            correlation_id=context.correlation_id,
            chain_depth=context.chain_depth,
            annotations=dict(context.annotations),
        )

    def _load_hooks(self, context: ExecutionContext) -> list[HookSpec]:
        """
        Load hook specs from SQLite hook registries via sqlite_crud.

        Args:
            context (ExecutionContext): Execution context for error reporting.

        Returns:
            list[HookSpec]: Hook specifications sorted by phase and order.

        Raises:
            HookRegistryLoadError: If hook registry data cannot be loaded.
        """

        repo_root = self._resolve_repo_root()
        records: list[dict[str, Any]] = []
        records.extend(
            self._fetch_hook_records(
                repo_root, "system", HOOK_REGISTRY_SYSTEM_TABLE
            )
        )
        records.extend(
            self._fetch_hook_records(repo_root, "user", HOOK_REGISTRY_USER_TABLE)
        )
        hooks: list[HookSpec] = [self._parse_hook_record(record, context) for record in records]
        hook_map: dict[str, HookSpec] = {}
        for hook in hooks:
            if hook.hook_id in hook_map:
                raise HookRegistryLoadError(
                    code="hook_registry_duplicate",
                    meaning="Hook registry contains a duplicate hook_id.",
                    details={"hook_id": hook.hook_id},
                )
            hook_map[hook.hook_id] = hook
        return sorted(
            hooks,
            key=lambda hook: (
                HOOK_PHASE_ORDER[hook.phase],
                hook.order,
                hook.hook_id,
                hook.path.as_posix(),
            ),
        )

    def _fetch_hook_records(
        self,
        repo_root: Path,
        scope: str,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch hook registry records for a scope via sqlite_crud.

        Args:
            repo_root (Path): Repository root path.
            scope (str): Registry scope (system or user).
            table_name (str): Hook registry table name.

        Returns:
            list[dict[str, Any]]: Hook registry record payloads.

        Raises:
            HookRegistryLoadError: If the registry lookup fails.
        """

        from context_compass.system.ai_restricted.database_management import sqlite_crud

        request = sqlite_crud.SqliteCrudRequest(
            operation=HOOK_REGISTRY_OPERATION,
            scope=scope,
            table_name=table_name,
            action=HOOK_REGISTRY_ACTION,
            payload={"enabled_only": True},
            actor_id=COMMAND_REGISTRY_ACTOR,
        )
        try:
            response = sqlite_crud.execute_request(repo_root, request)
        except sqlite_crud.SqliteCrudError as exc:
            raise HookRegistryLoadError(
                code="hook_registry_lookup_failed",
                meaning="Failed to read hook registry entries.",
                details={
                    "scope": scope,
                    "table_name": table_name,
                    "error_code": exc.code,
                    "error_details": exc.details,
                },
            ) from exc
        result = response.output.get("result")
        if not isinstance(result, dict):
            raise HookRegistryLoadError(
                code="hook_registry_payload_invalid",
                meaning="Hook registry response payload is invalid.",
                details={"scope": scope, "table_name": table_name},
            )
        records = result.get("records")
        if not isinstance(records, list):
            raise HookRegistryLoadError(
                code="hook_registry_payload_invalid",
                meaning="Hook registry records payload is invalid.",
                details={"scope": scope, "table_name": table_name},
            )
        return [record for record in records if isinstance(record, dict)]

    def _parse_hook_record(
        self,
        record: Mapping[str, Any],
        context: ExecutionContext,
    ) -> HookSpec:
        """
        Parse a hook registry record into a HookSpec.

        Args:
            record (Mapping[str, Any]): Hook registry record payload.
            context (ExecutionContext): Execution context for error reporting.

        Returns:
            HookSpec: Parsed hook specification.

        Raises:
            HookRegistryLoadError: If required fields are missing or invalid.
        """

        hook_id = record.get("hook_id")
        if not isinstance(hook_id, str) or not hook_id.strip():
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record missing hook_id.",
                details={"record": dict(record), "command_name": context.command_name},
            )
        phase = record.get("phase")
        if phase not in HOOK_PHASE_ORDER:
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record has invalid phase.",
                details={"hook_id": hook_id, "phase": phase},
            )
        order = record.get("order")
        if not isinstance(order, int):
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record has invalid order.",
                details={"hook_id": hook_id, "order": order},
            )
        script_kind = record.get("script_kind")
        if script_kind != "python":
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record has unsupported script_kind.",
                details={"hook_id": hook_id, "script_kind": script_kind},
            )
        script_path = record.get("script_path")
        if not isinstance(script_path, str) or not script_path.strip():
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record missing script_path.",
                details={"hook_id": hook_id, "script_path": script_path},
            )
        entrypoint = record.get("entrypoint")
        if not isinstance(entrypoint, str) or not entrypoint.strip():
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry record missing entrypoint.",
                details={"hook_id": hook_id, "entrypoint": entrypoint},
            )
        applies_to_json = record.get("applies_to_json")
        applies_to = self._parse_applies_to_json(applies_to_json, hook_id)
        path = self._resolve_hook_path(script_path, hook_id)
        return HookSpec(
            hook_id=hook_id,
            phase=phase,
            order=order,
            script_kind=script_kind,
            path=path,
            entrypoint=entrypoint,
            applies_to=applies_to,
        )

    def _resolve_hook_path(self, script_path: str, hook_id: str) -> Path:
        """
        Resolve a hook script path relative to the context_compass root.

        Args:
            script_path (str): Script path stored in the registry.
            hook_id (str): Hook identifier for error context.

        Returns:
            Path: Resolved hook script path.

        Raises:
            HookRegistryLoadError: If the path cannot be resolved.
        """

        candidate = Path(script_path)
        if candidate.is_absolute():
            resolved = candidate
        else:
            resolved = self._context_compass_root / candidate
        if not resolved.exists():
            raise HookRegistryLoadError(
                code="hook_script_missing",
                meaning="Hook script path does not exist.",
                details={"hook_id": hook_id, "script_path": script_path},
            )
        return resolved

    def _parse_applies_to_json(
        self, applies_to_json: Any, hook_id: str
    ) -> dict[str, list[str]] | None:
        """
        Parse applies_to JSON from registry records.

        Args:
            applies_to_json (Any): Raw applies_to_json field.
            hook_id (str): Hook identifier for error context.

        Returns:
            dict[str, list[str]] | None: Normalized applies_to mapping.

        Raises:
            HookRegistryLoadError: If applies_to_json is invalid.
        """

        if applies_to_json is None:
            return None
        if not isinstance(applies_to_json, str):
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry applies_to_json must be a JSON string.",
                details={"hook_id": hook_id, "applies_to_json": applies_to_json},
            )
        try:
            parsed = json.loads(applies_to_json)
        except json.JSONDecodeError as exc:
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry applies_to_json is invalid JSON.",
                details={"hook_id": hook_id, "applies_to_json": applies_to_json},
            ) from exc
        if not isinstance(parsed, dict):
            raise HookRegistryLoadError(
                code="hook_registry_invalid",
                meaning="Hook registry applies_to_json must be an object.",
                details={"hook_id": hook_id, "applies_to_json": applies_to_json},
            )
        normalized: dict[str, list[str]] = {}
        for key in ("command_names", "categories", "tags"):
            value = parsed.get(key)
            if value is None:
                continue
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                raise HookRegistryLoadError(
                    code="hook_registry_invalid",
                    meaning="Hook registry applies_to_json must contain string lists.",
                    details={"hook_id": hook_id, "field": f"applies_to.{key}"},
                )
            normalized[key] = value
        return normalized or None


    def _select_hooks(
        self,
        hooks: Sequence[HookSpec],
        phase: str,
        record: CommandRecord,
    ) -> list[HookSpec]:
        """
        Select hooks for a phase that apply to a command record.

        Args:
            hooks (Sequence[HookSpec]): Hook specifications to filter.
            phase (str): Hook phase.
            record (CommandRecord): Command record for selection.

        Returns:
            list[HookSpec]: Applicable hook specs.
        """

        selected: list[HookSpec] = []
        for hook in hooks:
            if hook.phase != phase:
                continue
            if self._hook_applies(hook, record):
                selected.append(hook)
        return selected

    def _hook_applies(self, hook: HookSpec, record: CommandRecord) -> bool:
        """
        Determine whether a hook applies to a command record.

        Args:
            hook (HookSpec): Hook specification.
            record (CommandRecord): Command record to test.

        Returns:
            bool: True if the hook applies, False otherwise.
        """

        applies_to = hook.applies_to
        if applies_to is None:
            return True
        command_names = applies_to.get("command_names")
        if command_names is not None and record.command_name not in command_names:
            return False
        categories = applies_to.get("categories")
        if categories is not None and record.category not in categories:
            return False
        tags = applies_to.get("tags")
        if tags is not None:
            record_tags = []
            if record.spec is not None:
                tags_value = record.spec.get("tags")
                if isinstance(tags_value, list):
                    record_tags = [tag for tag in tags_value if isinstance(tag, str)]
            if not any(tag in record_tags for tag in tags):
                return False
        return True

    def _apply_hooks(
        self,
        hooks: Sequence[HookSpec],
        context: ExecutionContext,
        payload: Mapping[str, Any],
        result: CommandResult,
    ) -> tuple[CommandResult, list[NextAction], list[CommandError]]:
        """
        Apply hook specs to a command result.

        Args:
            hooks (Sequence[HookSpec]): Hooks to execute.
            context (ExecutionContext): Execution context.
            payload (Mapping[str, Any]): Command payload.
            result (CommandResult): Current command result.

        Returns:
            tuple[CommandResult, list[NextAction], list[CommandError]]:
                Updated result, next actions, and errors.

        Contract:
            - Hook errors are accumulated and returned separately.
            - Hook metadata patches are shallow-merged into the result metadata.
        """

        metadata = result.metadata
        next_actions: list[NextAction] = []
        errors: list[CommandError] = []
        for hook in hooks:
            hook_result = self._execute_hook(hook, context, payload, result)
            if hook_result.metadata_patch:
                metadata = self._merge_metadata(metadata, hook_result.metadata_patch)
            if hook_result.next_actions:
                next_actions.extend(hook_result.next_actions)
            if hook_result.errors:
                errors.extend(hook_result.errors)
        updated_result = CommandResult(
            status=result.status,
            output=result.output,
            metadata=metadata,
            artifacts=result.artifacts,
            errors=result.errors,
            queries=result.queries,
        )
        return updated_result, next_actions, errors

    def _execute_hook(
        self,
        hook: HookSpec,
        context: ExecutionContext,
        payload: Mapping[str, Any],
        result: CommandResult,
    ) -> HookResult:
        """
        Execute a hook entrypoint for the given hook spec.

        Args:
            hook (HookSpec): Hook specification.
            context (ExecutionContext): Execution context.
            payload (Mapping[str, Any]): Command payload.
            result (CommandResult): Current command result.

        Returns:
            HookResult: Hook result payload.

        Contract:
            - Hook failures are returned as HookResult errors.
            - Missing or invalid entrypoints never raise to the caller.
        """

        try:
            module = self._import_module_from_path(hook.path, f"cc_hook_{hook.hook_id}")
        except RuntimeError as exc:
            return HookResult(
                errors=[
                    self._build_error(
                        code="hook_import_failed",
                        meaning="Hook module could not be imported.",
                        details={
                            "hook_id": hook.hook_id,
                            "hook_path": hook.path.as_posix(),
                            "error": str(exc),
                        },
                    )
                ]
            )
        try:
            entrypoint = getattr(module, hook.entrypoint)
        except AttributeError as exc:
            return HookResult(
                errors=[
                    self._build_error(
                        code="hook_entrypoint_missing",
                        meaning="Hook entrypoint is missing.",
                        details={
                            "hook_id": hook.hook_id,
                            "hook_path": hook.path.as_posix(),
                            "entrypoint": hook.entrypoint,
                            "error": str(exc),
                        },
                    )
                ]
            )
        if not callable(entrypoint):
            return HookResult(
                errors=[
                    self._build_error(
                        code="hook_entrypoint_invalid",
                        meaning="Hook entrypoint is not callable.",
                        details={
                            "hook_id": hook.hook_id,
                            "hook_path": hook.path.as_posix(),
                            "entrypoint": hook.entrypoint,
                        },
                    )
                ]
            )
        try:
            hook_result = entrypoint(context, dict(payload), result)
        except Exception as exc:
            return HookResult(
                errors=[
                    self._build_error(
                        code="hook_execution_failed",
                        meaning="Hook execution raised an exception.",
                        details={
                            "hook_id": hook.hook_id,
                            "hook_path": hook.path.as_posix(),
                            "entrypoint": hook.entrypoint,
                            "exception_type": exc.__class__.__name__,
                            "exception_message": str(exc),
                        },
                    )
                ]
            )
        if hook_result is None:
            return HookResult()
        if not isinstance(hook_result, HookResult):
            return HookResult(
                errors=[
                    self._build_error(
                        code="hook_result_invalid",
                        meaning="Hook did not return HookResult.",
                        details={
                            "hook_id": hook.hook_id,
                            "hook_path": hook.path.as_posix(),
                            "entrypoint": hook.entrypoint,
                        },
                    )
                ]
            )
        return hook_result

    def _merge_metadata(
        self, base: Mapping[str, Any], patch: Mapping[str, Any]
    ) -> dict[str, Any]:
        """
        Merge a metadata patch into existing metadata.

        Args:
            base (Mapping[str, Any]): Existing metadata.
            patch (Mapping[str, Any]): Patch to merge.

        Returns:
            dict[str, Any]: Merged metadata.

        Contract:
            - Dict values are shallow-merged.
            - List values are appended in order.
            - Other values are overwritten by the patch.
        """

        merged: dict[str, Any] = dict(base)
        for key, value in patch.items():
            if key in merged and isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = list(merged[key]) + list(value)
            elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged

    def _execute_next_actions(
        self,
        result: CommandResult,
        context: ExecutionContext,
        next_actions: Sequence[NextAction],
    ) -> CommandResult:
        """
        Execute activation-emitted next actions.

        Args:
            result (CommandResult): Current command result.
            context (ExecutionContext): Execution context.
            next_actions (Sequence[NextAction]): Next actions to execute.

        Returns:
            CommandResult: Updated result with chain metadata.

        Contract:
            - Stops on the first non-ok result.
            - Preserves pending_input results to allow pause/resume.
        """

        chain_results: list[dict[str, Any]] = []
        for action in next_actions:
            child_context = ExecutionContext(
                command_name=action.command_name,
                agent_id=context.agent_id,
                work_id=context.work_id,
                correlation_id=context.correlation_id,
                chain_depth=context.chain_depth + 1,
                annotations=dict(context.annotations),
            )
            child_result = self.execute(action.command_name, action.payload, child_context)
            chain_results.append(self._summarize_result(action.command_name, child_result))
            if child_result.status == "pending_input":
                metadata = self._merge_metadata(
                    result.metadata, {"chain_results": chain_results}
                )
                return CommandResult(
                    status="pending_input",
                    output=result.output,
                    metadata=metadata,
                    artifacts=result.artifacts,
                    errors=child_result.errors,
                    queries=child_result.queries,
                )
            if child_result.status != "ok":
                metadata = self._merge_metadata(
                    result.metadata, {"chain_results": chain_results}
                )
                return CommandResult(
                    status="error",
                    output=result.output,
                    metadata=metadata,
                    artifacts=result.artifacts,
                    errors=child_result.errors,
                    queries=result.queries,
                )
        metadata = self._merge_metadata(result.metadata, {"chain_results": chain_results})
        return CommandResult(
            status=result.status,
            output=result.output,
            metadata=metadata,
            artifacts=result.artifacts,
            errors=result.errors,
            queries=result.queries,
        )

    def _summarize_result(self, command_name: str, result: CommandResult) -> dict[str, Any]:
        """
        Summarize a CommandResult for chain metadata.

        Args:
            command_name (str): Command name executed.
            result (CommandResult): Result to summarize.

        Returns:
            dict[str, Any]: Summary payload for metadata.
        """

        return {
            "command_name": command_name,
            "status": result.status,
            "output": result.output,
            "metadata": result.metadata,
            "artifacts": result.artifacts,
            "errors": [error.__dict__ for error in result.errors],
            "queries": result.queries,
        }

    def _execute_core(
        self, record: CommandRecord, payload: Mapping[str, Any], context: ExecutionContext
    ) -> CommandResult:
        """
        Execute the core command handler defined by the record spec.

        Args:
            record (CommandRecord): Command record to execute.
            payload (Mapping[str, Any]): Command payload.
            context (ExecutionContext): Execution context.

        Returns:
            CommandResult: Command execution result.

        Contract:
            - Returns execution_not_configured when spec metadata is missing.
            - Returns execution_failed when the entrypoint raises.
        """

        try:
            spec = self._resolve_execution_spec(record)
        except ValueError as exc:
            return self._error_result(
                code="execution_not_configured",
                meaning="Command execution metadata is invalid.",
                details={"command_name": record.command_name, "error": str(exc)},
            )
        if spec is None:
            return self._error_result(
                code="execution_not_configured",
                meaning="Command execution metadata is missing.",
                details={"command_name": record.command_name},
            )
        try:
            entrypoint = self._load_command_callable(spec, record.command_name)
        except RuntimeError as exc:
            return self._error_result(
                code="execution_not_configured",
                meaning="Command entrypoint could not be loaded.",
                details={"command_name": record.command_name, "error": str(exc)},
            )
        try:
            result = entrypoint(dict(payload), context)
        except Exception as exc:
            return self._error_result(
                code="execution_failed",
                meaning="Command execution raised an exception.",
                details={
                    "command_name": record.command_name,
                    "exception_type": exc.__class__.__name__,
                    "exception_message": str(exc),
                },
            )
        if not isinstance(result, CommandResult):
            return self._error_result(
                code="invalid_result",
                meaning="Command did not return CommandResult.",
                details={"command_name": record.command_name},
            )
        return result

    def _resolve_execution_spec(self, record: CommandRecord) -> ExecutionSpec | None:
        """
        Resolve the execution spec from a command record.

        Args:
            record (CommandRecord): Command record to inspect.

        Returns:
            ExecutionSpec | None: Execution spec when available.

        Raises:
            ValueError: If the spec is invalid.

        Contract:
            - Requires script_path-based execution metadata.
            - Rejects module-based execution for determinism.
        """

        if record.spec is None:
            return None
        execution = record.spec.get("execution")
        if execution is None:
            return None
        if not isinstance(execution, dict):
            raise ValueError("spec.execution must be an object.")
        module = execution.get("module")
        if module is not None:
            raise ValueError("spec.execution.module is not supported; use script_path.")
        script_path = execution.get("script_path")
        if script_path is None:
            raise ValueError("spec.execution.script_path is required.")
        if not isinstance(script_path, str) or not script_path.strip():
            raise ValueError("spec.execution.script_path must be a non-empty string.")
        candidate = Path(script_path)
        resolved_path: Path = (
            candidate if candidate.is_absolute() else self._context_compass_root / candidate
        )
        entrypoint = execution.get("entrypoint")
        if not isinstance(entrypoint, str) or not entrypoint.strip():
            raise ValueError("spec.execution.entrypoint must be a non-empty string.")
        return ExecutionSpec(
            module=None,
            script_path=resolved_path,
            entrypoint=entrypoint,
        )

    def _load_command_callable(
        self, spec: ExecutionSpec, command_name: str
    ) -> Any:
        """
        Load a callable entrypoint for a command execution spec.

        Args:
            spec (ExecutionSpec): Execution spec to load.
            command_name (str): Command name for error context.

        Returns:
            Any: Callable entrypoint.

        Raises:
            RuntimeError: If the callable cannot be loaded.

        Contract:
            - Script-based execution always loads from script_path.
        """

        if spec.script_path is None:
            raise RuntimeError("Execution spec missing script path.")
        module = self._import_module_from_path(
            spec.script_path, f"cc_command_{command_name}"
        )
        try:
            entrypoint = getattr(module, spec.entrypoint)
        except AttributeError as exc:
            raise RuntimeError(
                f"Command {command_name} missing entrypoint {spec.entrypoint}"
            ) from exc
        if not callable(entrypoint):
            raise RuntimeError(f"Command {command_name} entrypoint is not callable")
        return entrypoint

    def _apply_error_hooks(
        self,
        hooks: Sequence[HookSpec],
        record: CommandRecord | None,
        context: ExecutionContext,
        payload: Mapping[str, Any],
        result: CommandResult,
    ) -> CommandResult:
        """
        Apply on_error hooks to an error result when configured.

        Args:
            hooks (Sequence[HookSpec]): Hook specifications to filter.
            record (CommandRecord | None): Command record used to select hooks.
            context (ExecutionContext): Execution context for hook execution.
            payload (Mapping[str, Any]): Command payload in flight.
            result (CommandResult): Error result to decorate.

        Returns:
            CommandResult: Error result augmented by on_error hooks.

        Contract:
            - on_error hooks may only add metadata or errors.
            - Activation actions emitted by on_error hooks are rejected.
        """

        if record is None:
            return result
        error_hooks = self._select_hooks(hooks, "on_error", record)
        if not error_hooks:
            return result
        updated_result, next_actions, hook_errors = self._apply_hooks(
            error_hooks, context, payload, result
        )
        errors = list(updated_result.errors)
        if next_actions:
            errors.append(
                self._build_error(
                    code="invalid_hook_phase",
                    meaning="on_error hooks cannot emit activation actions.",
                    details={"phase": "on_error", "command_name": record.command_name},
                )
            )
        if hook_errors:
            errors.extend(hook_errors)
        return CommandResult(
            status="error",
            output=updated_result.output,
            metadata=updated_result.metadata,
            artifacts=updated_result.artifacts,
            errors=errors,
            queries=updated_result.queries,
        )

    def _build_error(
        self, code: str, meaning: str, details: Mapping[str, Any]
    ) -> CommandError:
        """
        Build a CommandError with JSON-encoded details.

        Args:
            code (str): Stable error code identifier.
            meaning (str): Human-readable error description.
            details (Mapping[str, Any]): Structured details payload.

        Returns:
            CommandError: Structured error with JSON details.

        Contract:
            - details are JSON-encoded for machine parsing.
        """

        return CommandError(
            code=code,
            meaning=meaning,
            details=build_error_details(details),
        )

    def _error_result(
        self,
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
        Build a structured error CommandResult with JSON details.

        Args:
            code (str): Stable error code identifier.
            meaning (str): Human-readable error description.
            details (Mapping[str, Any]): Structured details payload.
            output (Mapping[str, Any] | None): Optional output payload.
            metadata (Mapping[str, Any] | None): Optional metadata payload.
            artifacts (Sequence[str] | None): Optional artifacts list.
            queries (Sequence[dict[str, Any]] | None): Optional pending queries.
            extra_errors (Sequence[CommandError] | None): Additional errors to append.

        Returns:
            CommandResult: Error payload for the runner.

        Contract:
            - Always includes the primary error in the errors list.
            - Metadata and output are shallow-copied to avoid mutation.
        """

        errors = [self._build_error(code, meaning, details)]
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

    def _fetch_command_row(self, command_name: str) -> tuple | None:
        """
        Fetch a raw command row from SQLite via sqlite_crud.

        Args:
            command_name (str): Command name to query.

        Returns:
            tuple | None: Raw row data, or None if not found.

        Raises:
            FileNotFoundError: If the registry database is missing.
            RuntimeError: If the registry tables or action registry are missing.
        """

        from context_compass.system.ai_restricted.database_management import sqlite_crud

        repo_root = self._resolve_repo_root()
        scope = _command_registry_scope(self._table_name)
        request = sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope=scope,
            table_name=self._table_name,
            action=COMMAND_REGISTRY_ACTION,
            payload={"record_id": command_name},
            actor_id=COMMAND_REGISTRY_ACTOR,
        )
        try:
            response = sqlite_crud.execute_request(repo_root, request)
        except sqlite_crud.SqliteCrudError as exc:
            return self._handle_registry_crud_error(exc)

        record = response.output.get("result", {}).get("record")
        if not isinstance(record, dict):
            raise ValueError("Command registry read returned an invalid record payload.")
        return _record_dict_to_row(record)

    def _resolve_repo_root(self) -> Path:
        """
        Resolve the repository root based on the configured context root.

        Returns:
            Path: Repository root path used for SQLite path resolution.

        Contract:
            - When context_compass_root is under context_compass/system, the
              repo root is the parent of context_compass.
            - If the context root does not match the expected layout, fallback
              to using the immediate parent.
        """

        context_root = self._context_compass_root
        if (
            context_root.name == "system"
            and context_root.parent.name == "context_compass"
        ):
            return context_root.parent.parent
        return context_root.parent

    def _handle_registry_crud_error(self, exc: "SqliteCrudError") -> tuple | None:
        """
        Map CRUD registry lookup errors to CommandRunner behavior.

        Args:
            exc (SqliteCrudError): CRUD error raised by sqlite_crud.

        Returns:
            tuple | None: None when the registry record is not found.

        Raises:
            FileNotFoundError: If the registry database is missing.
            RuntimeError: If required tables or registries are missing.
            sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        """

        if exc.code == "record_not_found":
            return None
        if exc.code == "db_missing":
            raise FileNotFoundError(
                f"Command registry database not found: {self._db_path}"
            ) from exc
        if exc.code in {
            "table_missing",
            "table_not_registered",
            "action_not_registered",
            "registry_missing",
        }:
            raise RuntimeError(
                "Command registry tables or actions are missing."
            ) from exc
        raise exc

    def _row_to_record(self, row: Sequence[object]) -> CommandRecord:
        """
        Convert a SQLite row into a CommandRecord.

        Args:
            row (Sequence[object]): Raw row values in COMMAND_COLUMNS order.

        Returns:
            CommandRecord: Parsed command record.

        Raises:
            ValueError: If the spec JSON payload is invalid.
        """

        spec_json = row[8]
        spec: dict[str, Any] | None
        if spec_json is None:
            spec = None
        else:
            try:
                spec_payload = json.loads(spec_json)
            except json.JSONDecodeError as exc:
                raise ValueError("Command spec JSON is invalid.") from exc
            if not isinstance(spec_payload, dict):
                raise ValueError("Command spec JSON must be an object.")
            spec = spec_payload

        return CommandRecord(
            command_name=str(row[0]),
            category=str(row[1]),
            entry=str(row[2]),
            summary=str(row[3]),
            requires_certification=bool(row[4]),
            requires_work_id=bool(row[5]),
            feature_flag=row[6] if row[6] is None else str(row[6]),
            notes=row[7] if row[7] is None else str(row[7]),
            spec=spec,
            registry_schema_version=int(row[9]),
            registry_generated_at=row[10] if row[10] is None else str(row[10]),
            registry_updated_at=row[11] if row[11] is None else str(row[11]),
        )

    def _import_module_from_path(self, path: Path, module_name: str) -> ModuleType:
        """
        Import a Python module from a filesystem path.

        Args:
            path (Path): Python file to import.
            module_name (str): Unique module name for import isolation.

        Returns:
            ModuleType: Imported module.

        Raises:
            RuntimeError: If the module cannot be imported.
        """

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to import module at {path}.")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            raise RuntimeError(f"Failed to import {path}: {exc}") from exc
        return module

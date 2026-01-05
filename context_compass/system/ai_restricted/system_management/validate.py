"""Validation tool for context_compass schemas and required artifacts."""

import argparse
import logging
from pathlib import Path
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.schema_validate import load_schema, validate_schema
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management import command_registry_validator
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


CURRENT_BRANCH_TABLE = "current_branch"
CURRENT_BRANCH_ACTION = "by_record_id"
CURRENT_BRANCH_RECORD_ID = "current"

BRANCH_REGISTRY_TABLE = "branch_registry"
BRANCH_REGISTRY_ACTION = "by_branch_name"

REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"

AGENT_PROFILE_TABLE = "agent_profile"
SELF_CONTEXT_TABLE = "self_context"
AGENT_WORK_QUEUE_TABLE = "agent_work_queue"
LIST_AGENT_IDS_ACTION = "list_agent_ids"

QUERY_CONTEXT_PROFILES = "read_context_profiles"
QUERY_ARCHITECTURE_CONTEXT = "read_architecture_context"
QUERY_COMPONENT_CONTEXTS = "read_component_contexts"
QUERY_BRANCH_WORK_QUEUE = "read_branch_work_queue"
QUERY_AGENT_PROFILE = "read_agent_profile"
QUERY_SELF_CONTEXT = "read_self_context"
QUERY_AGENT_WORK_QUEUE = "read_agent_work_queue"


def _validate_payload(payload: dict, schema_path: Path, label: str) -> list[str]:
    """
    Validate a JSON payload against a schema.

    Args:
        payload (dict): Payload to validate.
        schema_path (Path): Schema file path.
        label (str): Label to use for error paths.

    Returns:
        list[str]: Validation errors.
    """
    schema = load_schema(schema_path)
    return validate_schema(payload, schema, path=label)


def _crud_read_current_branch(repo_root: Path, actor_id: str) -> str:
    """
    Read the active branch name from current_branch via sqlite_crud.

    Args:
        repo_root (Path): Repo root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str: Active branch name.

    Raises:
        ValueError: If the CRUD result payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name=CURRENT_BRANCH_TABLE,
            action=CURRENT_BRANCH_ACTION,
            payload={"record_id": CURRENT_BRANCH_RECORD_ID},
            actor_id=actor_id,
        ),
    )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("current_branch read returned an invalid record payload.")
    branch_name = record.get("branch_name")
    if not isinstance(branch_name, str) or not branch_name.strip():
        raise ValueError("current_branch record is missing branch_name.")
    return branch_name


def _crud_branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Determine whether a branch is registered via sqlite_crud.

    Args:
        repo_root (Path): Repo root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if the branch registry record exists.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails unexpectedly.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_ACTION,
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            return False
        raise
    return True


def _crud_read_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read the repo_state payload via sqlite_crud.

    Args:
        repo_root (Path): Repo root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: repo_state payload and existence flag.

    Raises:
        ValueError: If the CRUD result payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name=REPO_STATE_TABLE,
            action=REPO_STATE_ACTION,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    return record, exists


def _crud_list_agent_ids(repo_root: Path, table_name: str, actor_id: str) -> list[str]:
    """
    List agent identifiers via sqlite_crud for a single table.

    Args:
        repo_root (Path): Repo root.
        table_name (str): Table name that provides agent_id values.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[str]: Sorted list of agent identifiers.

    Raises:
        ValueError: If the CRUD result payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name=table_name,
            action=LIST_AGENT_IDS_ACTION,
            payload=None,
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    agent_ids = result.get("agent_ids")
    if not isinstance(agent_ids, list) or not all(isinstance(item, str) for item in agent_ids):
        raise ValueError("list_agent_ids returned an invalid agent_ids payload.")
    return agent_ids


def _read_context_profiles(root: Path, branch_name: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read context_profiles payload via sqlite_query.

    Args:
        root (Path): Repo root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Context profiles payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_CONTEXT_PROFILES,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("context_profiles read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("context_profiles read returned an invalid exists flag.")
    return record, exists


def _read_architecture_context(
    root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read architecture_context payloads via sqlite_query.

    Args:
        root (Path): Repo root.
        branch_name (str): Branch identifier.
        kind (str): architecture_context or test_architecture_context.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Architecture context payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_ARCHITECTURE_CONTEXT,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("architecture_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("architecture_context read returned an invalid exists flag.")
    return record, exists


def _read_component_contexts(
    root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read component_contexts payloads via sqlite_query.

    Args:
        root (Path): Repo root.
        branch_name (str): Branch identifier.
        kind (str): component_contexts or test_component_contexts.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Component contexts payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_COMPONENT_CONTEXTS,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("component_contexts read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("component_contexts read returned an invalid exists flag.")
    return record, exists


def _read_branch_work_queue(
    root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read a branch work queue payload via sqlite_query.

    Args:
        root (Path): Repo root.
        branch_name (str): Branch identifier.
        bucket (str): Queue bucket name.
        work_type (str): Work type name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Work queue payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_BRANCH_WORK_QUEUE,
            payload={
                "branch_name": branch_name,
                "bucket": bucket,
                "work_type": work_type,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    queue = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue, dict):
        raise ValueError("branch work queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("branch work queue read returned an invalid exists flag.")
    return queue, exists


def _read_agent_profile(root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read an agent_profile payload via sqlite_query.

    Args:
        root (Path): Repo root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Agent profile payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_AGENT_PROFILE,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("agent_profile read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_profile read returned an invalid exists flag.")
    return record, exists


def _read_self_context(root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read a self_context payload via sqlite_query.

    Args:
        root (Path): Repo root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Self-context payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_SELF_CONTEXT,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("self_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("self_context read returned an invalid exists flag.")
    return record, exists


def _read_agent_work_queue(root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read an agent work queue payload via sqlite_query.

    Args:
        root (Path): Repo root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Agent work queue payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_AGENT_WORK_QUEUE,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    queue = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue, dict):
        raise ValueError("agent work queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent work queue read returned an invalid exists flag.")
    return queue, exists


def _validate_branch_sqlite_state(root: Path) -> list[str]:
    """
    Validate branch-scoped SQLite records for the active branch.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    schemas_dir = root / "context_compass" / "system" / "schemas"
    actor_id = "system:validate"
    try:
        branch_name = _crud_read_current_branch(root, actor_id)
    except (sqlite_crud.SqliteCrudError, ValueError) as exc:
        errors.append(f"current_branch read failed: {exc}")
        return errors

    try:
        registered = _crud_branch_registered(root, branch_name, actor_id)
    except sqlite_crud.SqliteCrudError as exc:
        errors.append(f"branch_registry read failed: {exc}")
        return errors
    if not registered:
        errors.append(f"Branch not registered in SQLite: {branch_name}")
        return errors

    try:
        repo_record, repo_exists = _crud_read_repo_state(root, branch_name, actor_id)
    except (sqlite_crud.SqliteCrudError, ValueError) as exc:
        errors.append(f"repo_state read failed: {exc}")
    else:
        if not repo_exists:
            errors.append(f"Missing repo_state record for branch: {branch_name}")
        else:
            errors.extend(
                _validate_payload(
                    repo_record,
                    schemas_dir / "repo_state.schema.json",
                    f"sqlite:branch:{branch_name}:repo_state",
                )
            )

    try:
        profiles_record, profiles_exists = _read_context_profiles(root, branch_name, actor_id)
    except (sqlite_query.SqliteQueryError, ValueError) as exc:
        errors.append(f"context_profiles read failed: {exc}")
        profiles_exists = False
        profiles_record = {}
    if not profiles_exists:
        errors.append(f"Missing context_profiles record for branch: {branch_name}")
    else:
        errors.extend(
            _validate_payload(
                profiles_record,
                schemas_dir / "context_profiles.schema.json",
                f"sqlite:branch:{branch_name}:context_profiles",
            )
        )

    for kind in ("architecture_context", "test_architecture_context"):
        try:
            record, exists = _read_architecture_context(root, branch_name, kind, actor_id)
        except (sqlite_query.SqliteQueryError, ValueError) as exc:
            errors.append(f"architecture context read failed: {exc}")
            continue
        if not exists:
            errors.append(f"Missing architecture context record: {kind}")
            continue
        errors.extend(
            _validate_payload(
                record,
                schemas_dir / "architecture_context.schema.json",
                f"sqlite:branch:{branch_name}:{kind}",
            )
        )

    for kind in ("component_contexts", "test_component_contexts"):
        try:
            record, exists = _read_component_contexts(root, branch_name, kind, actor_id)
        except (sqlite_query.SqliteQueryError, ValueError) as exc:
            errors.append(f"component contexts read failed: {exc}")
            continue
        if not exists:
            errors.append(f"Missing component contexts record: {kind}")
            continue
        errors.extend(
            _validate_payload(
                record,
                schemas_dir / "component_contexts.schema.json",
                f"sqlite:branch:{branch_name}:{kind}",
            )
        )

    work_schema = schemas_dir / "tasks.schema.json"
    for bucket in ("backlog", "active", "completed", "denied"):
        for work_type in ("epic", "story", "task"):
            try:
                queue, exists = _read_branch_work_queue(
                    root,
                    branch_name,
                    bucket,
                    work_type,
                    actor_id,
                )
            except (sqlite_query.SqliteQueryError, ValueError) as exc:
                errors.append(f"work_queue read failed: {exc}")
                continue
            if not exists:
                errors.append(
                    f"Missing work queue record for branch {branch_name}: {bucket}/{work_type}"
                )
                continue
            errors.extend(
                _validate_payload(
                    queue,
                    work_schema,
                    f"sqlite:branch:{branch_name}:work_queue:{bucket}/{work_type}",
                )
            )

    work_schema = schemas_dir / "agent_work.schema.json"
    try:
        agent_ids = _crud_list_agent_ids(root, AGENT_WORK_QUEUE_TABLE, actor_id)
    except (sqlite_crud.SqliteCrudError, ValueError) as exc:
        errors.append(f"agent_work_queue list_agent_ids failed: {exc}")
        agent_ids = []
    for agent_id in agent_ids:
        try:
            queue, exists = _read_agent_work_queue(root, agent_id, actor_id)
        except (sqlite_query.SqliteQueryError, ValueError) as exc:
            errors.append(f"agent_work_queue read failed: {exc}")
            continue
        if not exists:
            continue
        errors.extend(
            _validate_payload(
                queue,
                work_schema,
                f"sqlite:agent_work:{agent_id}",
            )
        )

    return errors


def _validate_self_context_sqlite_state(root: Path) -> list[str]:
    """
    Validate SQLite-backed self-context records.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    schema_path = root / "context_compass" / "system" / "schemas" / "self_context.schema.json"
    actor_id = "system:validate"
    try:
        agent_ids = _crud_list_agent_ids(root, SELF_CONTEXT_TABLE, actor_id)
    except (sqlite_crud.SqliteCrudError, ValueError) as exc:
        errors.append(f"self_context list_agent_ids failed: {exc}")
        return errors
    if agent_ids and not schema_path.exists():
        errors.append(f"Missing schema: {schema_path}")
        return errors
    for agent_id in agent_ids:
        try:
            record, exists = _read_self_context(root, agent_id, actor_id)
        except (sqlite_query.SqliteQueryError, ValueError) as exc:
            errors.append(f"self_context read failed: {exc}")
            continue
        if not exists:
            continue
        errors.extend(
            _validate_payload(
                record,
                schema_path,
                f"sqlite:self_context:{agent_id}",
            )
        )
    return errors


def _validate_agent_profile_sqlite_state(root: Path) -> list[str]:
    """
    Validate SQLite-backed agent profile records.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    schema_path = root / "context_compass" / "system" / "schemas" / "agent_profile.schema.json"
    actor_id = "system:validate"
    try:
        agent_ids = _crud_list_agent_ids(root, AGENT_PROFILE_TABLE, actor_id)
    except (sqlite_crud.SqliteCrudError, ValueError) as exc:
        errors.append(f"agent_profile list_agent_ids failed: {exc}")
        return errors
    if agent_ids and not schema_path.exists():
        errors.append(f"Missing schema: {schema_path}")
        return errors
    for agent_id in agent_ids:
        try:
            record, exists = _read_agent_profile(root, agent_id, actor_id)
        except (sqlite_query.SqliteQueryError, ValueError) as exc:
            errors.append(f"agent_profile read failed: {exc}")
            continue
        if not exists:
            continue
        errors.extend(
            _validate_payload(
                record,
                schema_path,
                f"sqlite:agent_profile:{agent_id}",
            )
        )
    return errors


def _validate_command_registry_sqlite_state(root: Path) -> list[str]:
    """
    Validate SQLite-backed command registry tables.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    registry_root = root / "context_compass" / "system" / "storage" / "sqlite"
    targets = [
        ("system", registry_root / "system.db", "command_registry_system"),
        ("user", registry_root / "user.db", "command_registry_user"),
    ]
    for scope, db_path, table_name in targets:
        if not db_path.exists():
            errors.append(f"Missing {scope} command registry database: {db_path}")
            continue
        try:
            issues = command_registry_validator.validate_registry_table(db_path, table_name)
        except Exception as exc:
            errors.append(f"Failed to validate {scope} command registry: {exc}")
            continue
        for issue in issues:
            label = f"sqlite:command_registry:{issue.table_name}"
            if issue.command_name:
                label = f"{label}:{issue.command_name}"
            errors.append(f"{label}: {issue.message}")
    return errors


def validate_repo(root: Path) -> list[str]:
    """
    Validate required context_compass artifacts in the repo.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    errors.extend(_validate_branch_sqlite_state(root))
    errors.extend(_validate_self_context_sqlite_state(root))
    errors.extend(_validate_agent_profile_sqlite_state(root))
    errors.extend(_validate_command_registry_sqlite_state(root))

    return errors


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Validate context_compass artifacts using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing validation errors, if any.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "validation", "validate context_compass artifacts")
        ensure_work_mode(repo_root, work_id, "validate context_compass artifacts")
        errors = validate_repo(repo_root)
        return ok_result(output={"errors": errors})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for context_compass validation.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result or validation fails.
    """
    parser = argparse.ArgumentParser(description="Validate context_compass artifacts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="validate",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("validate failed: %s", result.errors)
        raise SystemExit(1)
    errors = result.output.get("errors", [])
    if errors:
        for error in errors:
            logger.error(error)
        raise SystemExit(1)
    logger.info("Validation passed")


if __name__ == "__main__":
    main()

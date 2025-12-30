"""Validation tool for context_compass schemas and required artifacts."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.schema_validate import load_schema, validate_schema


def _validate_file(data_path: Path, schema_path: Path) -> list[str]:
    """
    Validate a JSON file against a schema.

    Args:
        data_path (Path): JSON file path.
        schema_path (Path): Schema file path.

    Returns:
        list[str]: Validation errors.
    """
    data = load_json(data_path)
    schema = load_schema(schema_path)
    return validate_schema(data, schema, path=str(data_path))


def _collect_self_context_files(root: Path) -> Iterable[Path]:
    """
    Collect self-context files under context_compass/self_context/agents.

    Args:
        root (Path): Repo root.

    Returns:
        Iterable[Path]: Self-context JSON files.
    """
    agents_dir = root / "context_compass" / "self_context" / "agents"
    if not agents_dir.exists():
        return []
    return agents_dir.glob("*.self.json")


def _collect_agent_work_files(root: Path) -> Iterable[Path]:
    """
    Collect per-agent worklist files under context_compass/self_context/agents.

    Args:
        root (Path): Repo root.

    Returns:
        Iterable[Path]: Worklist JSON files.
    """
    agents_dir = root / "context_compass" / "self_context" / "agents"
    if not agents_dir.exists():
        return []
    return agents_dir.glob("*.work.json")


def _collect_agent_profile_files(root: Path) -> Iterable[Path]:
    """
    Collect agent profile files under context_compass/self_context/agents.

    Args:
        root (Path): Repo root.

    Returns:
        Iterable[Path]: Agent profile JSON files.
    """
    agents_dir = root / "context_compass" / "self_context" / "agents"
    if not agents_dir.exists():
        return []
    return agents_dir.glob("*.profile.json")


def _required_files(root: Path) -> list[tuple[Path, Path]]:
    """
    Build required file -> schema pairs for validation.

    Args:
        root (Path): Repo root.

    Returns:
        list[tuple[Path, Path]]: Data and schema pairs.
    """
    schemas_dir = root / "context_compass" / "schemas"
    state_root = branch_paths.state_root(root)
    work_root = branch_paths.work_root(root)
    required = [
        (
            root / "context_compass" / "config" / "context_compass_configuration.json",
            schemas_dir / "context_compass_configuration.schema.json",
        ),
        (root / "context_compass" / "config" / "ignore.json", schemas_dir / "config_ignore.schema.json"),
        (root / "context_compass" / "config" / "policies.json", schemas_dir / "config_policies.schema.json"),
        (root / "context_compass" / "config" / "source_roots.json", schemas_dir / "config_source_roots.schema.json"),
        (state_root / "repo_state.json", schemas_dir / "repo_state.schema.json"),
        (state_root / "context_profiles.json", schemas_dir / "context_profiles.schema.json"),
        (state_root / "architecture_context.json", schemas_dir / "architecture_context.schema.json"),
        (state_root / "test_architecture_context.json", schemas_dir / "architecture_context.schema.json"),
        (state_root / "component_contexts.json", schemas_dir / "component_contexts.schema.json"),
        (state_root / "test_component_contexts.json", schemas_dir / "component_contexts.schema.json"),
        (root / "context_compass" / "memory" / "user_memory.json", schemas_dir / "memory_store.schema.json"),
        (root / "context_compass" / "memory" / "system_memory.json", schemas_dir / "memory_store.schema.json"),
        (root / "context_compass" / "commands" / "commands_user.json", schemas_dir / "command_registry.schema.json"),
        (root / "context_compass" / "commands" / "commands_system.json", schemas_dir / "command_registry.schema.json"),
    ]

    work_schema = schemas_dir / "tasks.schema.json"
    for state in ("backlog", "active", "completed", "denied"):
        for name in ("epics", "stories", "tasks"):
            required.append((work_root / state / f"{name}.json", work_schema))

    return required


def validate_repo(root: Path) -> list[str]:
    """
    Validate required context_compass artifacts in the repo.

    Args:
        root (Path): Repo root.

    Returns:
        list[str]: Validation errors.
    """
    errors: list[str] = []
    for data_path, schema_path in _required_files(root):
        if not data_path.exists():
            errors.append(f"Missing required file: {data_path}")
            continue
        if not schema_path.exists():
            errors.append(f"Missing schema: {schema_path}")
            continue
        errors.extend(_validate_file(data_path, schema_path))

    self_schema = root / "context_compass" / "schemas" / "self_context.schema.json"
    for self_path in _collect_self_context_files(root):
        if not self_schema.exists():
            errors.append(f"Missing schema: {self_schema}")
            break
        errors.extend(_validate_file(self_path, self_schema))

    work_schema = root / "context_compass" / "schemas" / "agent_work.schema.json"
    for work_path in _collect_agent_work_files(root):
        if not work_schema.exists():
            errors.append(f"Missing schema: {work_schema}")
            break
        errors.extend(_validate_file(work_path, work_schema))

    profile_schema = root / "context_compass" / "schemas" / "agent_profile.schema.json"
    for profile_path in _collect_agent_profile_files(root):
        if not profile_schema.exists():
            errors.append(f"Missing schema: {profile_schema}")
            break
        errors.extend(_validate_file(profile_path, profile_schema))

    environment_path = branch_paths.state_root(root) / "environment.json"
    environment_schema = root / "context_compass" / "schemas" / "environment_state.schema.json"
    if environment_path.exists():
        if not environment_schema.exists():
            errors.append(f"Missing schema: {environment_schema}")
        else:
            errors.extend(_validate_file(environment_path, environment_schema))

    return errors


def main() -> None:
    """
    CLI entrypoint for context_compass validation.
    """
    parser = argparse.ArgumentParser(description="Validate context_compass artifacts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    root = Path(args.repo_root).resolve()
    ensure_certified(root, args.agent_id)
    ensure_feature_enabled(root, "validation", "validate context_compass artifacts")
    ensure_work_mode(root, args.work_id, "validate context_compass artifacts")
    agent_presence.record_heartbeat(
        root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=None,
        notes=None,
        command_name="validate",
        command_args=sys.argv[1:],
    )
    errors = validate_repo(root)
    if errors:
        for error in errors:
            logger.error(error)
        raise SystemExit(1)
    logger.info("Validation passed")


if __name__ == "__main__":
    main()

"""
Generate command registries for context_compass tools.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import write_json_atomic, load_json


def _default_policies() -> dict:
    """
    Return default policy values for command registry generation.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    config_path = repo_root / "context_compass" / "config" / "policies.json"
    if config_path.exists():
        data = load_json(config_path)
        if isinstance(data, dict):
            policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _commands_catalog() -> list[dict]:
    """
    Return the canonical command catalog.

    Returns:
        list[dict]: Command definitions with audience tags.
    """
    return [
        {
            "name": "python_certified",
            "entry": "python python_certified.py --approval-token \"CERTIFY: APPROVED\"",
            "summary": "Finalize certification state after approval.",
            "category": "certification",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Run only after receiving CERTIFY: APPROVED.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_id",
            "entry": "python context_compass/tools/agent_id.py --prefix agent",
            "summary": "Generate a session-scoped agent id.",
            "category": "lifecycle",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "agent_manage",
            "entry": "python context_compass/tools/agent_manage.py <create|archive|delete> --repo-root . --agent-id <agent_id>",
            "summary": "Create, archive, or delete agent files.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Uses agent_id for heartbeat; add --owner-id to record actor.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_checkin",
            "entry": "python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-kind <kind> --model-name <model> --runtime <runtime>",
            "summary": "Check in an agent and start heartbeat tracking.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Metadata fields are optional but recommended.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_checkout",
            "entry": "python context_compass/tools/agent_checkout.py --repo-root . --agent-id <agent_id>",
            "summary": "Check out an agent and stop heartbeat tracking.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "agent_cleanup",
            "entry": "python context_compass/tools/agent_cleanup.py --repo-root . --agent-id <agent_id>",
            "summary": "Run cleanup scripts for stale agents.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Normally run automatically by tools.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_init",
            "entry": "python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Initialize branch-scoped state and queues.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "branch_switch",
            "entry": "python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Switch the active branch pointer.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "branch_clone",
            "entry": "python context_compass/tools/branch_clone.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Clone branch state and work queues into a new branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --activate to switch to the new branch.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_copy_context",
            "entry": "python context_compass/tools/branch_copy_context.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Copy branch context state files into another branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --preserve-repo-state to keep scan counters.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_copy_work",
            "entry": "python context_compass/tools/branch_copy_work.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Copy branch work queues into another branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --preserve-state to keep in_progress or leased states.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_delete_context",
            "entry": "python context_compass/tools/branch_delete_context.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Delete context state files for a branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --include-repo-state to remove repo_state.json too.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_delete_work",
            "entry": "python context_compass/tools/branch_delete_work.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Clear branch work queues.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Resets epics/stories/tasks queues to empty.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_cleanup",
            "entry": "python context_compass/tools/branch_cleanup.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Archive or delete a branch directory.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --no-archive for hard delete.",
            "audience": ["user", "system"],
        },
        {
            "name": "repo_state_assess",
            "entry": "python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage <stage>",
            "summary": "Assess repo lifecycle stage and tooling policy.",
            "category": "repo_state",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "repo_state",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "environment_check",
            "entry": "python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Collect OS/runtime/tool availability and optionally persist.",
            "category": "environment",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "environment_check",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "environment_check_ps1",
            "entry": "context_compass/tools/environment_check.ps1",
            "summary": "Preflight check for Windows without Python.",
            "category": "environment",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": "environment_check",
            "notes": "Read-only preflight.",
            "audience": ["user", "system"],
        },
        {
            "name": "environment_check_sh",
            "entry": "context_compass/tools/environment_check.sh",
            "summary": "Preflight check for Linux/macOS without Python.",
            "category": "environment",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": "environment_check",
            "notes": "Read-only preflight.",
            "audience": ["user", "system"],
        },
        {
            "name": "onboarding_bundle",
            "entry": "python context_compass/tools/onboarding_bundle.py --repo-root . --format markdown",
            "summary": "Generate a consolidated onboarding bundle of docs.",
            "category": "onboarding",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Allowed before certification.",
            "audience": ["user", "system"],
        },
        {
            "name": "scan",
            "entry": "python context_compass/tools/scan.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Scan repo for ctx freshness and emit tasks.",
            "category": "scan",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "scan",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_survey",
            "entry": "python context_compass/tools/context_profiles_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Survey and build context profiles from ctx JSON.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_read",
            "entry": "python context_compass/tools/context_profiles_read.py --repo-root . --agent-id <agent_id> --work-id <work_id> --profile <name>",
            "summary": "Read a named context profile and emit ctx bundle.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_review",
            "entry": "python context_compass/tools/context_profiles_review.py --repo-root . --agent-id <agent_id> --work-id <work_id> --profile <name> --grade <grade>",
            "summary": "Record a profile review and emit optimize/prune tasks.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_resurvey",
            "entry": "python context_compass/tools/context_profiles_resurvey.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Process resurvey_context_profile tasks.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_survey",
            "entry": "python context_compass/tools/context_architecture_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Build architecture_context.json from directory ctx.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_check",
            "entry": "python context_compass/tools/context_architecture_check.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Check architecture context freshness.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_resurvey",
            "entry": "python context_compass/tools/context_architecture_resurvey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Process resurvey_architecture_context tasks.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_survey",
            "entry": "python context_compass/tools/context_component_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Build component_contexts.json from directory ctx.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_check",
            "entry": "python context_compass/tools/context_component_check.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Check component context freshness.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_resurvey",
            "entry": "python context_compass/tools/context_component_resurvey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Process resurvey_component_contexts tasks.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_add",
            "entry": "python context_compass/tools/work_item_add.py --repo-root . --bucket <bucket> --kind <kind> --work-id <work_id>",
            "summary": "Add a work item to global work queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_move",
            "entry": "python context_compass/tools/work_item_move.py --repo-root . --work-id <work_id> --src-bucket <bucket> --dest-bucket <bucket>",
            "summary": "Move a work item between global buckets.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_close",
            "entry": "python context_compass/tools/work_item_close.py --repo-root . --work-id <work_id> --kind <kind>",
            "summary": "Close a work item and move it to completed.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_queue_add",
            "entry": "python context_compass/tools/work_queue_add.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Add a work item to a per-agent queue.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_global_to_branch",
            "entry": "python context_compass/tools/work_item_global_to_branch.py --repo-root . --work-id <work_id>",
            "summary": "Move a global work item into branch queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_branch_to_global",
            "entry": "python context_compass/tools/work_item_branch_to_global.py --repo-root . --work-id <work_id>",
            "summary": "Move a branch work item into global queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_agent_to_branch",
            "entry": "python context_compass/tools/work_item_agent_to_branch.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Move a per-agent work item into branch queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_agent_to_global",
            "entry": "python context_compass/tools/work_item_agent_to_global.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Move a per-agent work item into global queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "ticket_promote",
            "entry": "python context_compass/tools/ticket_promote.py --repo-root . --agent-id <agent_id> --work-id <work_id> --ticket <path>",
            "summary": "Promote a GitHub ticket markdown into work queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "ticket_intake",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "validate",
            "entry": "python context_compass/tools/validate.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Validate schemas and required artifacts.",
            "category": "validation",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "validation",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "memory_add",
            "entry": "python context_compass/tools/memory_add.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --title <title> --content <content>",
            "summary": "Add a memory entry to user or system store.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "User memory requires explicit user request.",
            "audience": ["user", "system"],
        },
        {
            "name": "memory_update",
            "entry": "python context_compass/tools/memory_update.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>",
            "summary": "Update a memory entry.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "memory_remove",
            "entry": "python context_compass/tools/memory_remove.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>",
            "summary": "Remove a memory entry.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "Removes entries entirely (no soft delete).",
            "audience": ["user", "system"],
        },
        {
            "name": "memory_read",
            "entry": "python context_compass/tools/memory_read.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system>",
            "summary": "Read memory entries.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "Use --recent to limit output.",
            "audience": ["user", "system"],
        },
        {
            "name": "command_registry_generate",
            "entry": "python context_compass/tools/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Generate command registries.",
            "category": "commands",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "command_registry",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "self_context",
            "entry": "python context_compass/tools/self_context.py --repo-root . --agent-id <agent_id>",
            "summary": "Initialize or update self context records.",
            "category": "self_context",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Use --init-self to create the self context file.",
            "audience": ["system"],
        },
        {
            "name": "skill_receipt",
            "entry": "python context_compass/tools/skill_receipt.py --repo-root . --agent-id <agent_id> --skill-id <skill>",
            "summary": "Write skill read receipts into self context.",
            "category": "self_context",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["system"],
        },
        {
            "name": "update_state",
            "entry": "python context_compass/tools/update_state.py --repo-root . --agent-id <agent_id> --work-id <work_id> <scan|work-item>",
            "summary": "Update scan counters or work item state.",
            "category": "state",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Internal maintenance helper.",
            "audience": ["system"],
        },
        {
            "name": "lease",
            "entry": "python context_compass/tools/lease.py",
            "summary": "Lock leasing helper (library module, not a CLI).",
            "category": "state",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Do not call directly; used by tools.",
            "audience": ["system"],
        },
    ]


def _filter_commands(commands: Iterable[dict], audience: str) -> list[dict]:
    """
    Filter commands by audience and strip internal keys.

    Args:
        commands (Iterable[dict]): Command definitions.
        audience (str): Audience filter.

    Returns:
        list[dict]: Filtered command list.
    """
    filtered: list[dict] = []
    for command in commands:
        audiences = command.get("audience", [])
        if audience not in audiences:
            continue
        entry = {key: value for key, value in command.items() if key != "audience"}
        filtered.append(entry)
    return filtered


def _registry_payload(now: str, commands: list[dict]) -> dict:
    """
    Build a registry payload.

    Args:
        now (str): Current timestamp.
        commands (list[dict]): Command list.

    Returns:
        dict: Registry payload.
    """
    return {
        "schema_version": 1,
        "updated_at": now,
        "generated_at": now,
        "commands": commands,
    }


def _write_registry(path: Path, payload: dict, owner_id: str, ttl_seconds: int) -> None:
    """
    Write a registry payload with a lease lock.

    Args:
        path (Path): Registry path.
        payload (dict): Registry payload.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL seconds.
    """
    locks_dir = path.parent / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, path, owner_id, ttl_seconds)
    try:
        write_json_atomic(path, payload)
    finally:
        lease.release_lock(locks_dir, path, owner_id)


def generate_registries(repo_root: Path, owner_id: str) -> dict:
    """
    Generate both user and system command registries.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Lock owner id.

    Returns:
        dict: Registry payloads for user and system.
    """
    now = utc_now_iso()
    catalog = _commands_catalog()
    user_commands = _filter_commands(catalog, "user")
    system_commands = _filter_commands(catalog, "system")

    payload_user = _registry_payload(now, user_commands)
    payload_system = _registry_payload(now, system_commands)

    commands_dir = repo_root / "context_compass" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    user_path = commands_dir / "commands_user.json"
    system_path = commands_dir / "commands_system.json"
    policies = _load_policies(repo_root)

    _write_registry(user_path, payload_user, owner_id, policies["lease_ttl_seconds"])
    _write_registry(system_path, payload_system, owner_id, policies["lease_ttl_seconds"])

    return {"user": payload_user, "system": payload_system}


def main() -> None:
    """
    CLI entrypoint for command registry generation.
    """
    parser = argparse.ArgumentParser(description="Generate context_compass command registries")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "command_registry", "generate command registries")
    ensure_work_mode(repo_root, args.work_id, "generate command registries")

    registries = generate_registries(repo_root, args.agent_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(repo_root / "context_compass" / "commands"),
        notes=None,
        command_name="command_registry_generate",
        command_args=sys.argv[1:],
    )
    logger.info(
        "command registries generated: user=%s system=%s",
        len(registries["user"]["commands"]),
        len(registries["system"]["commands"]),
    )


if __name__ == "__main__":
    main()

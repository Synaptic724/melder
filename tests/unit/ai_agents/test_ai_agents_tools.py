"""Unit tests for ai_agents tooling helpers."""

from pathlib import Path

import pytest

from ai_agents.tools import self_context
from ai_agents.tools import skill_receipt
from ai_agents.tools import lease
from ai_agents.tools import update_state
from ai_agents.tools import work_item_add
from ai_agents.tools import work_item_move
from ai_agents.tools import work_item_close
from ai_agents.tools import ticket_promote
from ai_agents.tools import work_queue_add
from ai_agents.tools import context_profiles_read
from ai_agents.tools import context_profiles_review
from ai_agents.tools import context_profiles_resurvey
from ai_agents.tools import onboarding_bundle
from ai_agents.tools.cleanup_agents import stale_agents
from ai_agents.tools._shared import agent_presence
from ai_agents.tools._shared import feature_guard
from ai_agents.tools._shared import hashing
from ai_agents.tools._shared import ignore_rules
from ai_agents.tools._shared import json_io
from ai_agents.tools._shared import paths
from ai_agents.tools._shared import schema_validate


def test_write_json_atomic_minified(tmp_path: Path) -> None:
    """
    Ensure write_json_atomic emits canonical minified JSON.
    """
    target = tmp_path / "data.json"
    payload = {"b": 2, "a": 1}
    json_io.write_json_atomic(target, payload)
    content = target.read_text(encoding="utf-8")
    assert content == '{"a":1,"b":2}'


def test_validate_schema_missing_required_key() -> None:
    """
    Ensure missing required keys are reported.
    """
    schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
    errors = schema_validate.validate_schema({"other": "x"}, schema, path="$")
    assert any("missing required key" in error for error in errors)


def test_ensure_self_context_creates_file(tmp_path: Path) -> None:
    """
    Ensure self context initialization writes a valid JSON file.
    """
    target = tmp_path / "agent.self.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    self_context._ensure_self_context(target, "agent_1")
    data = json_io.load_json(target)
    assert data["agent_id"] == "agent_1"
    assert data["schema_version"] == 1


def test_upsert_receipt_adds_and_detects_no_change() -> None:
    """
    Ensure skill receipts are added once and not duplicated.
    """
    self_data: dict = {"skill_receipts": []}
    added = skill_receipt._upsert_receipt(self_data, "python/docstrings", 1, "Summary")
    assert added is True
    assert len(self_data["skill_receipts"]) == 1
    no_change = skill_receipt._upsert_receipt(self_data, "python/docstrings", 1, "Summary")
    assert no_change is False
    assert len(self_data["skill_receipts"]) == 1


def test_lock_path_for_uses_hash(tmp_path: Path) -> None:
    """
    Ensure lock path uses a hashed filename.
    """
    resource = Path("C:/repo/path/to/file.json")
    lock_path = lease.lock_path_for(tmp_path, resource)
    assert lock_path.parent == tmp_path
    assert lock_path.name.endswith(".lock.json")
    stem = lock_path.name.replace(".lock.json", "")
    assert len(stem) == 64
    assert all(ch in "0123456789abcdef" for ch in stem)


def test_feature_guard_blocks_disabled_feature(tmp_path: Path) -> None:
    """
    Ensure feature_guard raises when a feature is disabled.
    """
    config_path = tmp_path / "ai_agents" / "config" / "ai_agents_configuration.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        config_path,
        {
            "schema_version": 1,
            "features": {
                "scan": False,
                "context_profiles": True,
                "work_management": True,
                "ticket_intake": True,
                "validation": True,
            },
            "skills": {"disabled_skill_ids": [], "disabled_skill_prefixes": []},
            "notes": None,
        },
    )

    with pytest.raises(feature_guard.FeatureDisabledError):
        feature_guard.ensure_feature_enabled(tmp_path, "scan", "run scan")


def test_record_heartbeat_creates_profile_and_active(tmp_path: Path) -> None:
    """
    Ensure heartbeat writes active_agents and agent profile files.
    """
    agent_presence.record_heartbeat(
        tmp_path,
        agent_id="agent_1",
        mode="agent",
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="unit_test",
        command_args=["--flag"],
    )
    active_path = tmp_path / "ai_agents" / "self_context" / "active_agents.json"
    profile_path = tmp_path / "ai_agents" / "self_context" / "agents" / "agent_1.profile.json"
    assert active_path.exists()
    assert profile_path.exists()
    active = json_io.load_json(active_path)
    profile = json_io.load_json(profile_path)
    assert active["agents"][0]["agent_id"] == "agent_1"
    assert profile["status"] == "active"
    assert profile["last_command"]["name"] == "unit_test"


def test_checkin_and_checkout_updates_status(tmp_path: Path) -> None:
    """
    Ensure checkin and checkout update active_agents and profile status.
    """
    agent_presence.checkin(
        tmp_path,
        agent_id="agent_2",
        mode="agent",
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="checkin",
        command_args=[],
    )
    active_path = tmp_path / "ai_agents" / "self_context" / "active_agents.json"
    profile_path = tmp_path / "ai_agents" / "self_context" / "agents" / "agent_2.profile.json"
    active = json_io.load_json(active_path)
    profile = json_io.load_json(profile_path)
    assert any(entry["agent_id"] == "agent_2" for entry in active["agents"])
    assert profile["status"] == "active"
    assert profile["last_checkin_at"] is not None

    agent_presence.checkout(
        tmp_path,
        agent_id="agent_2",
        mode="agent",
        notes=None,
        command_name="checkout",
        command_args=[],
    )
    active = json_io.load_json(active_path)
    profile = json_io.load_json(profile_path)
    assert all(entry["agent_id"] != "agent_2" for entry in active["agents"])
    assert profile["status"] == "inactive"
    assert profile["last_checkout_at"] is not None


def test_stale_cleanup_marks_profiles_and_removes_active(tmp_path: Path) -> None:
    """
    Ensure stale cleanup marks profiles and removes stale agents from active registry.
    """
    repo_root = tmp_path
    policies_path = repo_root / "ai_agents" / "config" / "policies.json"
    policies_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        policies_path,
        {
            "agent_archive_after_seconds": 100000,
            "agent_heartbeat_stale_seconds": 60,
            "ci_fail_on_needs_review": False,
            "ci_fail_states": ["missing", "stale", "blocked"],
            "dir_review_every_n_scans_default": 20,
            "lease_heartbeat_seconds": 30,
            "lease_ttl_seconds": 300,
            "lock_wait_seconds": 10,
            "max_task_attempts": 3,
            "review_every_n_scans_default": 30,
            "schema_version": 1,
        },
    )

    active_path = repo_root / "ai_agents" / "self_context" / "active_agents.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        active_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "agents": [
                {
                    "agent_id": "agent_old",
                    "mode": "agent",
                    "started_at": "2025-01-01T00:00:00Z",
                    "last_heartbeat_at": "2025-01-01T00:00:00Z",
                    "current_task_id": None,
                    "current_target": None,
                    "lease": None,
                    "notes": None,
                }
            ],
        },
    )

    profile_path = repo_root / "ai_agents" / "self_context" / "agents" / "agent_old.profile.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        profile_path,
        {
            "schema_version": 1,
            "agent_id": "agent_old",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "status": "active",
            "last_heartbeat_at": "2025-01-01T00:00:00Z",
            "last_checkin_at": "2025-01-01T00:00:00Z",
            "last_checkout_at": None,
            "mode": "agent",
            "current_task_id": None,
            "current_target": None,
            "notes": None,
            "last_command": None,
        },
    )

    stale_agents.cleanup(repo_root, "runner", now="2025-01-01T00:02:00Z")

    active_after = json_io.load_json(active_path)
    profile_after = json_io.load_json(profile_path)
    assert active_after["agents"] == []
    assert profile_after["status"] == "stale"


def test_stale_cleanup_requeues_active_work(tmp_path: Path) -> None:
    """
    Ensure stale cleanup moves active work items back to backlog.
    """
    repo_root = tmp_path
    policies_path = repo_root / "ai_agents" / "config" / "policies.json"
    policies_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        policies_path,
        {
            "agent_archive_after_seconds": 100000,
            "agent_heartbeat_stale_seconds": 60,
            "ci_fail_on_needs_review": False,
            "ci_fail_states": ["missing", "stale", "blocked"],
            "dir_review_every_n_scans_default": 20,
            "lease_heartbeat_seconds": 30,
            "lease_ttl_seconds": 300,
            "lock_wait_seconds": 10,
            "max_task_attempts": 3,
            "review_every_n_scans_default": 30,
            "schema_version": 1,
        },
    )

    active_path = repo_root / "ai_agents" / "self_context" / "active_agents.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        active_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "agents": [
                {
                    "agent_id": "agent_old",
                    "mode": "agent",
                    "started_at": "2025-01-01T00:00:00Z",
                    "last_heartbeat_at": "2025-01-01T00:00:00Z",
                    "current_task_id": None,
                    "current_target": None,
                    "lease": None,
                    "notes": None,
                }
            ],
        },
    )

    profile_path = repo_root / "ai_agents" / "self_context" / "agents" / "agent_old.profile.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        profile_path,
        {
            "schema_version": 1,
            "agent_id": "agent_old",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "status": "active",
            "last_heartbeat_at": "2025-01-01T00:00:00Z",
            "last_checkin_at": "2025-01-01T00:00:00Z",
            "last_checkout_at": None,
            "mode": "agent",
            "current_task_id": None,
            "current_target": None,
            "notes": None,
            "last_command": None,
        },
    )

    work_queue_path = repo_root / "ai_agents" / "self_context" / "agents" / "agent_old.work.json"
    work_queue_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        work_queue_path,
        {
            "schema_version": 1,
            "agent_id": "agent_old",
            "updated_at": "2025-01-01T00:00:00Z",
            "queue": [
                {
                    "work_id": "task_requeue",
                    "state": "in_progress",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_requeue",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    active_queue_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    active_queue_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        active_queue_path,
        {
            "schema_version": 1,
            "repo_id": None,
            "updated_at": None,
            "queue": [
                {
                    "work_id": "task_requeue",
                    "state": "in_progress",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_requeue",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    stale_agents.cleanup(repo_root, "runner", now="2025-01-01T00:02:00Z")

    active_after = json_io.load_json(active_queue_path)
    backlog_queue_path = repo_root / "ai_agents" / "work_management" / "backlog" / "tasks.json"
    backlog_after = json_io.load_json(backlog_queue_path)
    assert active_after["queue"] == []
    assert backlog_after["queue"][0]["work_id"] == "task_requeue"


def test_add_work_item_creates_queue(tmp_path: Path) -> None:
    """
    Ensure work_queue_add writes a work item with work_id into the agent queue.
    """
    item = {
        "work_id": "work_123",
        "state": "queued",
        "kind": "task",
        "target_path": "src/pkg/foo.py",
        "ctx_path": "src/pkg/__foo__.json",
        "reason": ["manual_add"],
        "parent_work_id": None,
        "root_work_id": "work_123",
        "priority": 10,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
    work_queue_add.add_work_item(tmp_path, "agent_a", item, owner_id="agent_a")
    queue_path = tmp_path / "ai_agents" / "self_context" / "agents" / "agent_a.work.json"
    assert queue_path.exists()
    data = json_io.load_json(queue_path)
    assert data["agent_id"] == "agent_a"
    assert data["queue"][0]["work_id"] == "work_123"


def test_work_item_add_writes_queue(tmp_path: Path) -> None:
    """
    Ensure work_item_add writes a work item into work_management queues.
    """
    item = {
        "work_id": "epic_001",
        "state": "queued",
        "kind": "epic",
        "target_path": "ai_agents/github_intake/tickets/epic.md",
        "ctx_path": "ai_agents/github_intake/tickets/epic.md",
        "reason": ["github_intake"],
        "parent_work_id": None,
        "root_work_id": "epic_001",
        "priority": 80,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
    queue_path = work_item_add.add_work_item(tmp_path, "active", "epic", item, owner_id="agent_a")
    data = json_io.load_json(queue_path)
    assert data["queue"][0]["work_id"] == "epic_001"


def test_work_item_move_transfers_queue(tmp_path: Path) -> None:
    """
    Ensure work_item_move relocates items between buckets.
    """
    repo_root = tmp_path
    source_path = repo_root / "ai_agents" / "work_management" / "backlog" / "tasks.json"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        source_path,
        {
            "schema_version": 1,
            "repo_id": None,
            "updated_at": None,
            "queue": [
                {
                    "work_id": "task_move",
                    "state": "queued",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_move",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    work_item_move.move_work_item(repo_root, "task_move", "backlog", "active", "task", owner_id="agent_a")

    source_after = json_io.load_json(source_path)
    dest_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    dest_after = json_io.load_json(dest_path)
    assert source_after["queue"] == []
    assert dest_after["queue"][0]["work_id"] == "task_move"


def test_ticket_promote_adds_root_and_child(tmp_path: Path) -> None:
    """
    Ensure ticket_promote writes a root item and child items.
    """
    repo_root = tmp_path
    ticket_path = repo_root / "ai_agents" / "github_intake" / "tickets" / "epic.md"
    ticket_path.parent.mkdir(parents=True, exist_ok=True)
    ticket_path.write_text("# Epic\n", encoding="utf-8")

    root_item = {
        "work_id": "epic_root",
        "state": "queued",
        "kind": "epic",
        "target_path": str(ticket_path),
        "ctx_path": str(ticket_path),
        "reason": ["github_intake"],
        "parent_work_id": None,
        "root_work_id": "epic_root",
        "priority": 80,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "source_ticket": str(ticket_path),
    }
    children = [
        {
            "work_id": "task_child",
            "kind": "task",
            "target_path": "src/pkg/foo.py",
            "ctx_path": "src/pkg/__foo__.json",
        }
    ]
    updated = ticket_promote.promote_ticket(
        repo_root,
        ticket_path,
        "backlog",
        "epic",
        root_item,
        owner_id="agent_a",
        children=children,
    )
    root_queue = json_io.load_json(updated[0])
    child_queue = json_io.load_json(updated[1])
    assert root_queue["queue"][0]["work_id"] == "epic_root"
    assert child_queue["queue"][0]["work_id"] == "task_child"


def test_work_item_close_moves_and_clears_queue(tmp_path: Path) -> None:
    """
    Ensure work_item_close moves the item and clears per-agent queues.
    """
    repo_root = tmp_path
    active_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        active_path,
        {
            "schema_version": 1,
            "repo_id": None,
            "updated_at": None,
            "queue": [
                {
                    "work_id": "task_close",
                    "state": "in_progress",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_close",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )
    work_queue_path = repo_root / "ai_agents" / "self_context" / "agents" / "agent_close.work.json"
    work_queue_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        work_queue_path,
        {
            "schema_version": 1,
            "agent_id": "agent_close",
            "updated_at": "2025-01-01T00:00:00Z",
            "queue": [
                {
                    "work_id": "task_close",
                    "state": "in_progress",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_close",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    work_item_close.close_work_item(
        repo_root,
        "task_close",
        "task",
        "active",
        "completed",
        owner_id="agent_close",
        new_state="done",
        queue_agent_id="agent_close",
    )

    active_after = json_io.load_json(active_path)
    completed_path = repo_root / "ai_agents" / "work_management" / "completed" / "tasks.json"
    completed_after = json_io.load_json(completed_path)
    queue_after = json_io.load_json(work_queue_path)
    assert active_after["queue"] == []
    assert completed_after["queue"][0]["work_id"] == "task_close"
    assert queue_after["queue"] == []


def test_hash_subtree_is_stable(tmp_path: Path) -> None:
    """
    Ensure hashing helpers produce stable results.
    """
    file_path = tmp_path / "data.txt"
    file_path.write_text("alpha", encoding="utf-8")
    first = hashing.hash_file(file_path)
    second = hashing.hash_file(file_path)
    assert first == second
    subtree = hashing.hash_subtree([f"data.txt:{first}"])
    assert subtree == hashing.hash_subtree([f"data.txt:{second}"])


def test_repo_relative_path_normalizes(tmp_path: Path) -> None:
    """
    Ensure repo_relative_path uses POSIX separators.
    """
    repo_root = tmp_path
    file_path = repo_root / "src" / "pkg" / "file.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("x", encoding="utf-8")
    rel = paths.repo_relative_path(repo_root, file_path)
    assert rel == "src/pkg/file.py"


def test_ignore_rules_only_roots_and_globs(tmp_path: Path) -> None:
    """
    Ensure ignore rules honor only_roots and glob patterns.
    """
    repo_root = tmp_path
    config = {
        "schema_version": 1,
        "globs": ["node_modules/"],
        "only_roots": ["src"],
        "code_extensions": [],
    }
    src_file = repo_root / "src" / "main.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("x", encoding="utf-8")
    ignored = ignore_rules.is_ignored_path(repo_root, src_file, config)
    within = ignore_rules.is_within_only_roots(repo_root, src_file, config["only_roots"])
    assert ignored is False
    assert within is True

    vendor_file = repo_root / "node_modules" / "pkg" / "index.js"
    vendor_file.parent.mkdir(parents=True, exist_ok=True)
    vendor_file.write_text("x", encoding="utf-8")
    ignored_vendor = ignore_rules.is_ignored_path(repo_root, vendor_file, config)
    assert ignored_vendor is True


def test_update_work_item_state_updates_queue(tmp_path: Path) -> None:
    """
    Ensure update_state can update a work item in place.
    """
    repo_root = tmp_path
    queue_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        queue_path,
        {
            "schema_version": 1,
            "repo_id": None,
            "updated_at": None,
            "queue": [
                {
                    "work_id": "task_update",
                    "state": "queued",
                    "kind": "task",
                    "target_path": "src/pkg/foo.py",
                    "ctx_path": "src/pkg/__foo__.json",
                    "reason": ["manual_add"],
                    "parent_work_id": None,
                    "root_work_id": "task_update",
                    "priority": 10,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )
    updated = update_state.update_work_item_state(
        repo_root,
        "active",
        "task",
        "task_update",
        owner_id="agent_test",
        state="in_progress",
    )
    assert updated["state"] == "in_progress"


def test_context_profiles_read_updates_usage(tmp_path: Path) -> None:
    """
    Ensure context profile reads increment usage_count and return ctx items.
    """
    repo_root = tmp_path
    profiles_path = repo_root / "ai_agents" / "state" / "context_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    ctx_path = repo_root / "src" / "pkg" / "__foo__.json"
    ctx_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(ctx_path, {"kind": "file_ctx", "schema_version": 1})
    json_io.write_json_atomic(
        profiles_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "rules_version": "context_profiles@v1",
            "limits": {"max_items_per_profile": 10, "max_bytes_per_profile": 1000},
            "profiles": [
                {
                    "name": "repo_overview",
                    "paths": ["src/pkg/__foo__.json"],
                    "score": 0.1,
                    "grade": "ok",
                    "usage_count": 0,
                    "last_used_at": None,
                    "last_review_at": None,
                    "review_counts": {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0},
                    "reason": "test",
                    "size_bytes": 10,
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    output = context_profiles_read.read_profile(
        repo_root=repo_root,
        profile_name="repo_overview",
        agent_id="agent_1",
        mode="agent",
        max_items=None,
        max_bytes=None,
        update_usage=True,
        emit_tasks=False,
        owner_id="agent_1",
    )
    assert output["summary"]["total_items"] == 1
    assert output["items"][0]["path"] == "src/pkg/__foo__.json"

    updated = json_io.load_json(profiles_path)
    profile = updated["profiles"][0]
    assert profile["usage_count"] == 1
    assert profile["last_used_at"] is not None


def test_context_profiles_review_updates_grade_and_tasks(tmp_path: Path) -> None:
    """
    Ensure context profile reviews update grade and emit prune tasks.
    """
    repo_root = tmp_path
    profiles_path = repo_root / "ai_agents" / "state" / "context_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        profiles_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "rules_version": "context_profiles@v1",
            "limits": {"max_items_per_profile": 10, "max_bytes_per_profile": 1000},
            "profiles": [
                {
                    "name": "repo_overview",
                    "paths": ["src/pkg/__foo__.json"],
                    "score": 0.1,
                    "grade": "ok",
                    "usage_count": 1,
                    "last_used_at": None,
                    "last_review_at": None,
                    "review_counts": {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0},
                    "reason": "test",
                    "size_bytes": 10,
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    profile = context_profiles_review.review_profile(
        repo_root=repo_root,
        profile_name="repo_overview",
        grade="poor",
        reviewer="agent_1",
        notes="too broad",
        agent_id="agent_1",
        mode="agent",
        emit_tasks=True,
        owner_id="agent_1",
    )
    assert profile["grade"] == "poor"

    updated = json_io.load_json(profiles_path)
    updated_profile = updated["profiles"][0]
    assert updated_profile["review_counts"]["poor"] == 1
    assert updated_profile["last_review_at"] is not None

    tasks_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    tasks = json_io.load_json(tasks_path)
    assert tasks["queue"][0]["kind"] == "prune_context_profile"


def test_context_profiles_read_emits_resurvey_task(tmp_path: Path) -> None:
    """
    Ensure context profile reads emit resurvey tasks when inputs drift.
    """
    repo_root = tmp_path
    code_path = repo_root / "src" / "pkg" / "foo.py"
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text("value = 1\n", encoding="utf-8")

    ctx_path = repo_root / "src" / "pkg" / "__foo__.json"
    json_io.write_json_atomic(
        ctx_path,
        {
            "kind": "file_ctx",
            "schema_version": 1,
            "identity": {"path": "src/pkg/foo.py", "ctx_path": "src/pkg/__foo__.json", "language": "python"},
            "computed": {"checksums": {"code_hash_sha256": "mismatch"}, "freshness_state": "fresh"},
            "agent": {},
        },
    )

    profiles_path = repo_root / "ai_agents" / "state" / "context_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        profiles_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "rules_version": "context_profiles@v1",
            "limits": {"max_items_per_profile": 10, "max_bytes_per_profile": 1000},
            "profiles": [
                {
                    "name": "repo_overview",
                    "paths": ["src/pkg/__foo__.json"],
                    "score": 0.1,
                    "grade": "ok",
                    "usage_count": 0,
                    "last_used_at": None,
                    "last_review_at": None,
                    "review_counts": {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0},
                    "reason": "test",
                    "size_bytes": 10,
                    "freshness_state": "fresh",
                    "staleness_reasons": [],
                    "inputs_hash": "seed",
                    "last_checked_at": None,
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    context_profiles_read.read_profile(
        repo_root=repo_root,
        profile_name="repo_overview",
        agent_id="agent_1",
        mode="agent",
        max_items=None,
        max_bytes=None,
        update_usage=False,
        emit_tasks=True,
        owner_id="agent_1",
    )

    tasks_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    tasks = json_io.load_json(tasks_path)
    assert tasks["queue"][0]["kind"] == "resurvey_context_profile"


def test_context_profiles_resurvey_closes_task(tmp_path: Path) -> None:
    """
    Ensure resurvey tool runs survey and closes queued resurvey tasks.
    """
    repo_root = tmp_path
    code_path = repo_root / "src" / "pkg" / "foo.py"
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text("value = 1\n", encoding="utf-8")

    ctx_path = repo_root / "src" / "pkg" / "__foo__.json"
    json_io.write_json_atomic(
        ctx_path,
        {
            "kind": "file_ctx",
            "schema_version": 1,
            "identity": {"path": "src/pkg/foo.py", "ctx_path": "src/pkg/__foo__.json", "language": "python"},
            "computed": {"checksums": {"code_hash_sha256": "mismatch"}, "freshness_state": "fresh"},
            "agent": {},
        },
    )

    profiles_path = repo_root / "ai_agents" / "state" / "context_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        profiles_path,
        {
            "schema_version": 1,
            "updated_at": "2025-01-01T00:00:00Z",
            "rules_version": "context_profiles@v1",
            "limits": {"max_items_per_profile": 10, "max_bytes_per_profile": 1000},
            "profiles": [
                {
                    "name": "repo_overview",
                    "paths": ["src/pkg/__foo__.json"],
                    "score": 0.1,
                    "grade": "ok",
                    "usage_count": 0,
                    "last_used_at": None,
                    "last_review_at": None,
                    "review_counts": {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0},
                    "reason": "test",
                    "size_bytes": 10,
                    "freshness_state": "stale",
                    "staleness_reasons": ["hash_mismatch"],
                    "inputs_hash": "seed",
                    "last_checked_at": None,
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    tasks_path = repo_root / "ai_agents" / "work_management" / "active" / "tasks.json"
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        tasks_path,
        {
            "schema_version": 1,
            "repo_id": None,
            "updated_at": "2025-01-01T00:00:00Z",
            "queue": [
                {
                    "work_id": "task_resurvey",
                    "state": "queued",
                    "kind": "resurvey_context_profile",
                    "target_path": "context_profile:repo_overview",
                    "ctx_path": "ai_agents/state/context_profiles.json",
                    "reason": ["profile:repo_overview", "state:stale"],
                    "parent_work_id": None,
                    "root_work_id": "task_resurvey",
                    "priority": 50,
                    "lease": None,
                    "attempts": 0,
                    "last_error_ref": None,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
        },
    )

    closed = context_profiles_resurvey.resurvey_context_profiles(
        repo_root,
        agent_id="agent_1",
        mode="agent",
        work_id="task_resurvey",
        select_all=False,
        emit_tasks=False,
    )
    assert closed == ["task_resurvey"]

    completed_path = repo_root / "ai_agents" / "work_management" / "completed" / "tasks.json"
    completed = json_io.load_json(completed_path)
    assert completed["queue"][0]["work_id"] == "task_resurvey"


def test_onboarding_bundle_includes_core_docs(tmp_path: Path) -> None:
    """
    Ensure onboarding bundle includes core ai_agents docs and skills.
    """
    repo_root = tmp_path
    (repo_root / "AGENTS.md").write_text("Root agents", encoding="utf-8")
    ai_agents_dir = repo_root / "ai_agents"
    ai_agents_dir.mkdir(parents=True, exist_ok=True)
    (ai_agents_dir / "AGENTS.md").write_text("AI agents", encoding="utf-8")
    (ai_agents_dir / "SKILLS.md").write_text("- skills/example.md\n", encoding="utf-8")
    skills_dir = ai_agents_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "example.md").write_text("Example skill", encoding="utf-8")

    payload = onboarding_bundle.build_bundle(repo_root)
    paths = [item["path"] for item in payload["files"]]
    assert "AGENTS.md" in paths
    assert "ai_agents/AGENTS.md" in paths
    assert "ai_agents/SKILLS.md" in paths
    assert "ai_agents/skills/example.md" in paths

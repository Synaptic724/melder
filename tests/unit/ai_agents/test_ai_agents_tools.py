"""Unit tests for ai_agents tooling helpers."""

from pathlib import Path

from ai_agents.tools import self_context
from ai_agents.tools import skill_receipt
from ai_agents.tools import lease
from ai_agents.tools._shared import agent_presence
from ai_agents.tools._shared import json_io
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

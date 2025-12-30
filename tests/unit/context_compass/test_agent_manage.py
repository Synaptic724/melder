"""Unit tests for agent lifecycle management."""

import sys
from pathlib import Path

import pytest

from context_compass.tools import agent_manage
from context_compass.tools._shared import agent_presence
from context_compass.tools._shared import json_io
from context_compass.tools._shared.certification_guard import default_certification_state


def _write_certified_state(repo_root: Path, agent_id: str) -> None:
    """
    Write a certified agent profile for testing.

    Args:
        repo_root (Path): Repo root path.
        agent_id (str): Agent identifier.
    """
    profile_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.profile.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    agent_presence.ensure_profile_file(profile_path, agent_id)
    profile = json_io.load_json(profile_path)
    state = default_certification_state()
    state.update(
        {
            "state": "CERTIFIED",
            "certified": True,
            "certified_at": "2025-12-28T00:00:00Z",
            "approved_at": "2025-12-28T00:00:00Z",
            "approval_token": "CERTIFY: APPROVED",
            "approved_by": "tester",
        }
    )
    profile["certification_state"] = state
    json_io.write_json_atomic(profile_path, profile)


def test_agent_create_delete_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure agent lifecycle commands create, archive, and delete files.
    """
    agent_id = "agent_1"
    _write_certified_state(tmp_path, agent_id)

    monkeypatch.setattr(
        sys,
        "argv",
        ["agent_manage.py", "--repo-root", str(tmp_path), "--agent-id", agent_id, "create"],
    )
    agent_manage.main()

    agents_dir = tmp_path / "context_compass" / "self_context" / "agents"
    self_path = agents_dir / f"{agent_id}.self.json"
    work_path = agents_dir / f"{agent_id}.work.json"
    assert self_path.exists()
    assert work_path.exists()

    monkeypatch.setattr(
        sys,
        "argv",
        ["agent_manage.py", "--repo-root", str(tmp_path), "--agent-id", agent_id, "archive"],
    )
    agent_manage.main()

    archive_root = tmp_path / "context_compass" / "archive" / "agents" / agent_id
    assert archive_root.exists()
    assert not self_path.exists()
    assert not work_path.exists()

    _write_certified_state(tmp_path, agent_id)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent_manage.py", "--repo-root", str(tmp_path), "--agent-id", agent_id, "create"],
    )
    agent_manage.main()
    assert self_path.exists()
    assert work_path.exists()

    monkeypatch.setattr(
        sys,
        "argv",
        ["agent_manage.py", "--repo-root", str(tmp_path), "--agent-id", agent_id, "delete"],
    )
    agent_manage.main()
    assert not self_path.exists()
    assert not work_path.exists()

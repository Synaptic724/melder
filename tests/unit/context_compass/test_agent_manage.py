"""Unit tests for agent lifecycle management."""

import sys
from pathlib import Path

import pytest

from context_compass.tools import agent_manage


def _write_certified_state(repo_root: Path) -> None:
    """
    Write a certified state file for testing.

    Args:
        repo_root (Path): Repo root path.
    """
    state_path = repo_root / "context_compass" / "self_context" / "certification_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        (
            '{"approval_token":"CERTIFY: APPROVED","approved_at":"2025-12-28T00:00:00Z",'
            '"approved_by":"tester","certified":true,"certified_at":"2025-12-28T00:00:00Z",'
            '"notes":null,"schema_version":1,"self_certification_hash":null,"state":"CERTIFIED"}'
        ),
        encoding="utf-8",
    )


def test_agent_create_delete_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure agent lifecycle commands create, archive, and delete files.
    """
    _write_certified_state(tmp_path)
    agent_id = "agent_1"

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

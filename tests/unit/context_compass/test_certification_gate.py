"""Unit tests for certification gating helpers."""

import sys
from pathlib import Path

import pytest

import python_certified
from context_compass.tools import self_context
from context_compass.tools._shared import certification_guard
from context_compass.tools._shared import json_io


def _write_profile(path: Path, agent_id: str, state: dict) -> None:
    """
    Write an agent profile JSON file with embedded certification state.

    Args:
        path (Path): Target path for the profile file.
        agent_id (str): Agent identifier.
        state (dict): Certification state data.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    json_io.write_json_atomic(
        path,
        {
            "schema_version": 1,
            "agent_id": agent_id,
            "agent_kind": None,
            "created_at": "2025-12-28T00:00:00Z",
            "updated_at": "2025-12-28T00:00:00Z",
            "status": "inactive",
            "last_heartbeat_at": None,
            "last_checkin_at": None,
            "last_checkout_at": None,
            "mode": "agent",
            "model_name": None,
            "current_task_id": None,
            "current_target": None,
            "notes": None,
            "runtime": None,
            "last_command": None,
            "certification_state": state,
        },
    )


def test_parse_approval_token_approved() -> None:
    """
    Ensure approval token detection returns APPROVED.
    """
    text = "CERTIFY: APPROVED"
    assert certification_guard.parse_approval_token(text) == "APPROVED"


def test_parse_approval_token_changes() -> None:
    """
    Ensure approval token detection returns CHANGES.
    """
    text = "CERTIFY: CHANGES Please revise the assumptions."
    assert certification_guard.parse_approval_token(text) == "CHANGES"


def test_parse_approval_token_none() -> None:
    """
    Ensure unknown responses return None.
    """
    assert certification_guard.parse_approval_token("looks fine") is None
    assert certification_guard.parse_approval_token("CERTIFY: APPROVED ok") is None


def test_ensure_certified_rejects_uncertified(tmp_path: Path) -> None:
    """
    Ensure the guard rejects UNCERTIFIED state.
    """
    profile_path = tmp_path / "context_compass" / "self_context" / "agents" / "agent_1.profile.json"
    _write_profile(
        profile_path,
        "agent_1",
        {
            "schema_version": 1,
            "state": "UNCERTIFIED",
            "certified": False,
            "certified_at": None,
            "approved_at": None,
            "approval_token": None,
            "approved_by": None,
            "self_certification_hash": None,
            "notes": None,
        },
    )
    with pytest.raises(SystemExit):
        certification_guard.ensure_certified(tmp_path, "agent_1")


def test_ensure_certified_accepts_certified(tmp_path: Path) -> None:
    """
    Ensure the guard allows CERTIFIED state.
    """
    profile_path = tmp_path / "context_compass" / "self_context" / "agents" / "agent_1.profile.json"
    _write_profile(
        profile_path,
        "agent_1",
        {
            "schema_version": 1,
            "state": "CERTIFIED",
            "certified": True,
            "certified_at": "2025-12-28T00:00:00Z",
            "approved_at": "2025-12-28T00:00:00Z",
            "approval_token": certification_guard.APPROVAL_TOKEN,
            "approved_by": "tester",
            "self_certification_hash": "abc123",
            "notes": None,
        },
    )
    certification_guard.ensure_certified(tmp_path, "agent_1")


def test_certification_flow_blocks_then_allows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure tools are blocked until certification is finalized.
    """
    profile_path = tmp_path / "context_compass" / "self_context" / "agents" / "agent_1.profile.json"
    _write_profile(
        profile_path,
        "agent_1",
        {
            "schema_version": 1,
            "state": "UNCERTIFIED",
            "certified": False,
            "certified_at": None,
            "approved_at": None,
            "approval_token": None,
            "approved_by": None,
            "self_certification_hash": None,
            "notes": None,
        },
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["self_context.py", "--repo-root", str(tmp_path), "--agent-id", "agent_1"],
    )
    with pytest.raises(SystemExit):
        self_context.main()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python_certified.py",
            "--repo-root",
            str(tmp_path),
            "--agent-id",
            "agent_1",
            "--approval-token",
            "CERTIFY: APPROVED",
        ],
    )
    python_certified.main()

    monkeypatch.setattr(
        sys,
        "argv",
        ["self_context.py", "--repo-root", str(tmp_path), "--agent-id", "agent_1"],
    )
    self_context.main()

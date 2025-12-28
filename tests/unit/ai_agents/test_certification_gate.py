"""Unit tests for certification gating helpers."""

import json
import sys
from pathlib import Path

import pytest

import python_certified
from ai_agents.tools import self_context
from ai_agents.tools._shared import certification_guard


def _write_state(path: Path, state: dict) -> None:
    """
    Write a certification state JSON file in minified form.

    Args:
        path (Path): Target path for the JSON file.
        state (dict): Certification state data.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            state,
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
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
    state_path = certification_guard.certification_state_path(tmp_path)
    _write_state(
        state_path,
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
        certification_guard.ensure_certified(tmp_path)


def test_ensure_certified_accepts_certified(tmp_path: Path) -> None:
    """
    Ensure the guard allows CERTIFIED state.
    """
    state_path = certification_guard.certification_state_path(tmp_path)
    _write_state(
        state_path,
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
    certification_guard.ensure_certified(tmp_path)


def test_certification_flow_blocks_then_allows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure tools are blocked until certification is finalized.
    """
    state_path = certification_guard.certification_state_path(tmp_path)
    _write_state(
        state_path,
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
        ["python_certified.py", "--repo-root", str(tmp_path), "--approval-token", "CERTIFY: APPROVED"],
    )
    python_certified.main()

    monkeypatch.setattr(
        sys,
        "argv",
        ["self_context.py", "--repo-root", str(tmp_path), "--agent-id", "agent_1"],
    )
    self_context.main()

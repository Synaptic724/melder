from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.nexus.rift.frame_viewer.view_spell import ViewSpell


@pytest.fixture()
def _spell_viewer(monkeypatch: pytest.MonkeyPatch) -> ViewSpell:
    """
    Build one detached ViewSpell whose identity read answers a fixed spell.

    Args:
        monkeypatch:
            Pytest patcher (class-level identity stub; ViewSpell is
            slotted, so per-instance method assignment is unavailable).

    Returns:
        ViewSpell: Viewer with `describe_spell_identity` stubbed.
    """
    monkeypatch.setattr(
        ViewSpell,
        "describe_spell_identity",
        lambda self, spell_source_id, frame_name=None: {
            "source_id": spell_source_id,
            "spell_id": "sha-viewer",
        },
    )
    return ViewSpell(frame_view=None)


def test_describe_spell_source_honest_when_research_inactive(
        _spell_viewer: ViewSpell,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the honest-unavailability arm: no live MR root answers a named
    reason instead of raising (viewing a spell never fails on research
    state), mirroring describe_spell_research exactly.
    """
    monkeypatch.setattr(Aether, "_instance", None)

    payload = _spell_viewer.describe_spell_source("source-1")

    assert payload == {
        "source_id": "source-1",
        "spell_id": "sha-viewer",
        "research_available": False,
        "reason": "mutation_research_not_active",
    }


def test_describe_spell_source_routes_through_mr_peek(
        _spell_viewer: ViewSpell,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the live arm: the viewer peeks the Aether-hosted root WITHOUT
    constructing it, passes the module narrowing through, and stamps the
    source payload with the viewer identity.
    """
    research = MagicMock()
    research.cleaned = False
    research.activated = True
    research.source_view.return_value = {
        "spell_id": "sha-viewer",
        "root_module": "pkg.root",
        "modules": {
            "pkg.root": {
                "source": "def cast(): ...",
                "origin": "recorded",
                "drifted": None,
                "text_unavailable": False,
            },
        },
    }
    aether = MagicMock()
    aether._mutation_research = research
    monkeypatch.setattr(Aether, "_instance", aether)

    payload = _spell_viewer.describe_spell_source(
        "source-1",
        module_name="pkg.root",
    )

    research.source_view.assert_called_once_with(
        "sha-viewer",
        module_name="pkg.root",
    )
    assert payload["research_available"] is True
    assert payload["source_id"] == "source-1"
    assert payload["modules"]["pkg.root"]["origin"] == "recorded"

import hashlib
from unittest.mock import MagicMock

import pytest

from melder.mutation_research.mutation_research import MutationResearch


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each foresight test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


ROOT_SOURCE = "def cast():\n    return 1\n"
HELPER_SOURCE = "VALUE = 41\n"


def _mock_aether() -> MagicMock:
    """
    Build one MagicMock Aether whose crystallizer poses as live custody.

    Returns:
        MagicMock: Aether double; `_crystallizer` answers the live/activated
        guards so foresight reads proceed into the mocked facades.
    """
    aether = MagicMock()
    aether._crystallizer.cleaned = False
    aether._crystallizer.activated = True
    return aether


def _activated_root(aether: MagicMock) -> MutationResearch:
    """
    Build one configured + activated root over the mocked host.

    Args:
        aether:
            Mocked Aether host.

    Returns:
        MutationResearch: Live root (no hydration - custody is a mock).
    """
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)
    root.activate(hydrate_from_record=False)
    return root


def _custody_payload(*, helper_path: str = "") -> dict:
    """
    Build one canonical custody describe() payload for a two-module world.

    Args:
        helper_path:
            Optional live-disk path recorded for the helper module (the
            helper carries NO recorded text, exercising the fallback lane).

    Returns:
        dict: describe() payload double.
    """
    return {
        "root_module_name": "pkg.root",
        "module_targets": ["pkg.root", "pkg.helper"],
        "synthetic_module_sources": {
            "pkg.root": {"source_text": ROOT_SOURCE},
        },
        "user_module_sources": {},
        "module_to_path": {"pkg.helper": helper_path} if helper_path else {},
        "physical_module_fingerprints": {
            "pkg.root": hashlib.sha256(
                ROOT_SOURCE.encode("utf-8")
            ).hexdigest(),
            "pkg.helper": hashlib.sha256(
                HELPER_SOURCE.encode("utf-8")
            ).hexdigest(),
        },
        "module_to_direct_dependencies": {
            "pkg.root": ["pkg.helper"],
            "pkg.helper": [],
        },
        "export_surfaces": {"pkg.root": ["cast"]},
        "module_load_order": ["pkg.helper", "pkg.root"],
    }


def _install_crystal(aether: MagicMock, payload: dict) -> None:
    """
    Point the mocked custody facade at one describe() payload.

    Args:
        aether:
            Mocked Aether host.
        payload:
            describe() payload double.

    Returns:
        None.
    """
    crystal = MagicMock()
    crystal.describe.return_value = payload
    aether._crystallizer.get_spell_crystal.return_value = crystal


def test_source_view_prefers_recorded_text() -> None:
    """
    Verify recorded custody text wins: origin "recorded", no drift claim.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())

    view = root.source_view("sha-1", module_name="pkg.root")

    assert view["root_module"] == "pkg.root"
    row = view["modules"]["pkg.root"]
    assert row["source"] == ROOT_SOURCE
    assert row["origin"] == "recorded"
    assert row["drifted"] is None
    assert row["text_unavailable"] is False


def test_source_view_live_disk_fallback_marks_drift(tmp_path) -> None:
    """
    Verify the live-disk fallback: unrecorded text reads through the
    recorded path and the drift marker compares against the sealed
    fingerprint (False when identical, True when edited).
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    helper_file = tmp_path / "helper.py"
    helper_file.write_text(HELPER_SOURCE, encoding="utf-8")
    _install_crystal(aether, _custody_payload(helper_path=str(helper_file)))

    clean = root.source_view("sha-1", module_name="pkg.helper")
    row = clean["modules"]["pkg.helper"]
    assert row["origin"] == "live_disk"
    assert row["source"] == HELPER_SOURCE
    assert row["drifted"] is False

    helper_file.write_text(HELPER_SOURCE + "VALUE_2 = 42\n", encoding="utf-8")
    drifted = root.source_view("sha-1", module_name="pkg.helper")
    assert drifted["modules"]["pkg.helper"]["drifted"] is True


def test_source_view_honest_misses() -> None:
    """
    Verify honest misses: a module outside the world answers
    unknown_module, and a module with neither recorded text nor a
    readable path answers text_unavailable - neither raises.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())

    unknown = root.source_view("sha-1", module_name="pkg.elsewhere")
    assert unknown["unknown_module"] is True
    assert unknown["modules"] == {}

    whole = root.source_view("sha-1")
    helper_row = whole["modules"]["pkg.helper"]
    assert helper_row["text_unavailable"] is True
    assert helper_row["source"] is None


def test_foresight_reads_refuse_dead_custody() -> None:
    """
    Verify the loud posture: foresight reads ask for recorded truth, so a
    cleaned/inactive crystallizer refuses teach-grade instead of
    fabricating empty answers.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    aether._crystallizer.cleaned = True

    with pytest.raises(RuntimeError, match="custody is unavailable"):
        root.source_view("sha-1")
    with pytest.raises(RuntimeError, match="custody is unavailable"):
        root.source_drift_view()
    with pytest.raises(RuntimeError, match="custody is unavailable"):
        root.module_graph_view("sha-1")


def test_impact_view_requires_exactly_one_center() -> None:
    """
    Verify impact_view answers exactly one question per call.
    """
    root = _activated_root(_mock_aether())

    with pytest.raises(ValueError, match="one question"):
        root.impact_view()
    with pytest.raises(ValueError, match="one question"):
        root.impact_view(spell_id="sha-1", module_name="pkg.root")


def test_impact_view_joins_research_residency() -> None:
    """
    Verify the join: the raw radius is preserved verbatim and every
    affected identity gains a residency row - declared spells carry
    lane + campaign truth, undeclared spells report declared False.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    root.set_active_campaign("apollo")
    root.record_world_entry("sha-declared")
    aether._crystallizer.analyze_impact.return_value = {
        "root_module": "pkg.root",
        "affected_spells": ["sha-declared", "sha-foreign"],
        "affected_modules": ["pkg.root"],
    }

    view = root.impact_view(module_name="pkg.root")

    assert view["affected_modules"] == ["pkg.root"]
    declared = view["research"]["sha-declared"]
    assert declared["declared"] is True
    assert declared["lane_name"] == "default"
    assert declared["campaign"] == "apollo"
    foreign = view["research"]["sha-foreign"]
    assert foreign["declared"] is False
    assert foreign["lane_id"] is None


def test_module_graph_view_builds_local_reverse_edges() -> None:
    """
    Verify the walkable payload: modules sorted, direct edges preserved,
    LOCAL reverse edges derived, load order verbatim.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())

    graph = root.module_graph_view("sha-1")

    assert graph["modules"] == ["pkg.helper", "pkg.root"]
    assert graph["direct_dependencies"]["pkg.root"] == ["pkg.helper"]
    assert graph["local_importers"]["pkg.helper"] == ["pkg.root"]
    assert graph["load_order"] == ["pkg.helper", "pkg.root"]
    assert graph["export_surfaces"]["pkg.root"] == ["cast"]


def test_source_drift_view_passes_through_full_report() -> None:
    """
    Verify source_drift_view is the honest no-args passthrough of the
    crystallizer's full drift describe.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    report = {"module_impacts": {}, "drift": {"pkg.root": "unchanged"}}
    aether._crystallizer.analyze_impact.return_value = report

    assert root.source_drift_view() is report
    aether._crystallizer.analyze_impact.assert_called_once_with()


def test_preview_candidate_reports_parse_error_honestly() -> None:
    """
    Verify previewing broken code answers a parse_error row - it never
    raises and never fabricates analysis/diff/impact sections.
    """
    root = _activated_root(_mock_aether())

    preview = root.preview_candidate("def broken(:\n")

    assert preview["parse_error"]["line"] == 1
    assert preview["defines"] == {"classes": [], "functions": []}
    assert preview["diff"] is None
    assert preview["impact"] is None


def test_preview_candidate_analyzes_defines_and_import_roots() -> None:
    """
    Verify the static analysis: top-level defines and deduped absolute
    import roots; with no against-version and no module, diff and impact
    stay None (nothing to center on).
    """
    root = _activated_root(_mock_aether())
    code = (
        "import os\n"
        "import os.path\n"
        "from json import loads\n"
        "class Widget:\n"
        "    pass\n"
        "def build():\n"
        "    return Widget()\n"
    )

    preview = root.preview_candidate(code)

    assert preview["candidate_sha256"] == hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()
    assert preview["defines"] == {
        "classes": ["Widget"],
        "functions": ["build"],
    }
    assert preview["import_roots"] == ["json", "os"]
    assert preview["diff"] is None
    assert preview["impact"] is None


def test_preview_candidate_diffs_and_radiuses_against_current() -> None:
    """
    Verify the full mock: against a recorded version, the candidate adopts
    that version's root module name, the would-be source + structural
    diffs mark the root module changed, and the impact section is that
    module's current radius joined with residency.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())
    aether._crystallizer.analyze_impact.return_value = {
        "root_module": "pkg.root",
        "affected_spells": ["sha-1"],
        "affected_modules": ["pkg.root"],
    }
    candidate = "def cast():\n    return 2\n"

    preview = root.preview_candidate(candidate, against_spell_id="sha-1")

    assert preview["module_name"] == "pkg.root"
    source_diff = preview["diff"]["source"]
    assert source_diff["strategy"] == "source"
    assert "pkg.root" in source_diff["result"]["changed_modules"]
    structural = preview["diff"]["structural"]
    assert structural["strategy"] == "structural"
    assert preview["impact"]["affected_modules"] == ["pkg.root"]
    assert "sha-1" in preview["impact"]["research"]
    aether._crystallizer.analyze_impact.assert_called_once_with(
        module_name="pkg.root",
        spell_id=None,
    )


def test_preview_candidate_with_module_name_centers_impact() -> None:
    """
    Verify the no-against lane: a bare module identity centers the impact
    section on that module and no diff is fabricated.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    aether._crystallizer.analyze_impact.return_value = {
        "root_module": "pkg.other",
        "affected_spells": [],
        "affected_modules": ["pkg.other"],
    }

    preview = root.preview_candidate(
        "VALUE = 3\n",
        module_name="pkg.other",
    )

    assert preview["diff"] is None
    assert preview["impact"]["affected_modules"] == ["pkg.other"]

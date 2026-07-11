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


def test_staged_ancestry_is_one_shot_and_rediscovery_safe() -> None:
    """
    Verify the synthesis mint seam: staged parents ride the FIRST fresh
    world entry only (multi-parent node minted, stamp consumed), while a
    rediscovery re-stages them untouched; clear works without consuming.
    """
    root = _activated_root(_mock_aether())
    root.record_world_entry("sha-left")
    root.record_world_entry("sha-right")

    with pytest.raises(ValueError, match="non-empty list"):
        root.stage_ancestry([])
    root.stage_ancestry(["sha-left", "sha-right"])
    assert root.staged_ancestry == ["sha-left", "sha-right"]

    # Rediscovery: the stamp survives untouched.
    assert root.record_world_entry("sha-left") is False
    assert root.staged_ancestry == ["sha-left", "sha-right"]

    # Fresh entry: the stamp mints and consumes.
    assert root.record_world_entry("sha-child") is True
    assert root.staged_ancestry is None
    child = root.research_set().get_lane(
        root.research_set().residence_of("sha-child")
    ).get_node("sha-child")
    assert child.parent_spell_ids == ["sha-left", "sha-right"]

    # Next fresh entry: parentless (one-shot proven).
    root.record_world_entry("sha-after")
    after = root.research_set().get_lane(
        root.research_set().residence_of("sha-after")
    ).get_node("sha-after")
    assert after.parent_spell_ids == []

    root.stage_ancestry(["sha-left"])
    root.clear_staged_ancestry()
    assert root.staged_ancestry is None


def _two_world_aether() -> MagicMock:
    """
    Build one mocked host whose custody carries TWO recorded worlds.

    Returns:
        MagicMock: Aether double; get_spell_crystal answers per identity
        (sha-base / sha-donor), analyze_impact answers a fixed radius.
    """
    aether = _mock_aether()
    base_payload = _custody_payload()
    donor_payload = _custody_payload()
    donor_payload["synthetic_module_sources"] = {
        "pkg.root": {
            "source_text": (
                "def cast():\n"
                "    return 99\n"
                "\n"
                "def fresh():\n"
                "    return 'donor'\n"
            ),
        },
    }
    crystals = {
        "sha-base": base_payload,
        "sha-donor": donor_payload,
    }

    def _get(spell_id):
        crystal = MagicMock()
        crystal.describe.return_value = crystals[spell_id]
        return crystal

    aether._crystallizer.get_spell_crystal.side_effect = _get
    aether._crystallizer.analyze_impact.return_value = {
        "root_module": "pkg.root",
        "affected_spells": ["sha-base"],
        "affected_modules": ["pkg.root"],
    }
    return aether


def test_synthesize_candidate_composes_previews_and_stages() -> None:
    """
    Verify the surgical verb end to end: donor parts splice into the base
    root module, the composed candidate rides the full foresight preview
    against the base, parents are reported, and stage_ancestry=True arms
    the mint seam.
    """
    aether = _two_world_aether()
    root = _activated_root(aether)

    verdict = root.synthesize_candidate(
        "sha-base",
        "sha-donor",
        take_functions=["cast", "fresh"],
        stage_ancestry=True,
    )

    assert verdict["parents"] == ["sha-base", "sha-donor"]
    assert verdict["parse_error"] is None
    composed = verdict["composed_source"]
    assert "return 99" in composed
    assert "def fresh():" in composed
    actions = {row["name"]: row["action"] for row in verdict["selections"]}
    assert actions == {"cast": "replaced", "fresh": "added"}
    preview = verdict["preview"]
    assert preview["module_name"] == "pkg.root"
    assert "pkg.root" in (
        preview["diff"]["source"]["result"]["changed_modules"]
    )
    assert verdict["ancestry_staged"] is True
    assert root.staged_ancestry == ["sha-base", "sha-donor"]


def test_synthesize_candidate_honest_and_loud_arms() -> None:
    """
    Verify the refusal split: unresolvable source text answers
    text_unavailable honestly (no compose, nothing staged), while an
    unknown donor selection refuses loudly (explicit ask).
    """
    aether = _two_world_aether()
    root = _activated_root(aether)

    with pytest.raises(ValueError, match="no top-level function"):
        root.synthesize_candidate(
            "sha-base",
            "sha-donor",
            take_functions=["missing"],
        )

    bare = _custody_payload()
    bare["synthetic_module_sources"] = {}
    aether._crystallizer.get_spell_crystal.side_effect = None
    crystal = MagicMock()
    crystal.describe.return_value = bare
    aether._crystallizer.get_spell_crystal.return_value = crystal

    verdict = root.synthesize_candidate(
        "sha-base",
        "sha-donor",
        take_functions=["cast"],
        stage_ancestry=True,
    )
    assert verdict["text_unavailable"] is True
    assert verdict["composed_source"] is None
    assert verdict["preview"] is None
    assert verdict["ancestry_staged"] is False
    assert root.staged_ancestry is None


def test_diff_material_drinks_user_retained_text() -> None:
    """
    Verify the comparison law fix: user-retained (physical) module text
    enters diff material alongside synthetic text, so a user-module-backed
    spell diffs as a REAL text diff instead of fingerprint-only rows.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    payloads = {
        "sha-old": {
            "synthetic_module_sources": {},
            "user_module_sources": {
                "pkg.physical": {"source_text": "VALUE = 1\n"},
            },
            "physical_module_fingerprints": {"pkg.physical": "print-old"},
        },
        "sha-new": {
            "synthetic_module_sources": {},
            "user_module_sources": {
                "pkg.physical": {"source_text": "VALUE = 2\n"},
            },
            "physical_module_fingerprints": {"pkg.physical": "print-new"},
        },
    }

    def _get(spell_id):
        crystal = MagicMock()
        crystal.describe.return_value = payloads[spell_id]
        return crystal

    aether._crystallizer.get_spell_crystal.side_effect = _get

    verdict = root.diff_research("sha-old", "sha-new")

    assert verdict["result"]["changed_modules"] == ["pkg.physical"]
    row = verdict["result"]["module_diffs"]["pkg.physical"]
    assert row["text_unavailable"] is False
    assert any("VALUE = 2" in line for line in row["unified_diff"])


def test_module_view_dossier_and_honest_miss() -> None:
    """
    Verify the crystal-well dossier: one call answers text (labeled by
    kind), fingerprint, path, deps both ways, and export surface; a module
    outside the world answers unknown_module honestly.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())

    dossier = root.module_view("sha-1", "pkg.root")

    assert dossier["unknown_module"] is False
    assert dossier["source"] == ROOT_SOURCE
    assert dossier["source_kind"] == "synthetic"
    assert dossier["direct_dependencies"] == ["pkg.helper"]
    assert dossier["local_importers"] == []
    assert dossier["export_surface"] == ["cast"]
    assert dossier["fingerprint"] is not None

    helper = root.module_view("sha-1", "pkg.helper")
    assert helper["local_importers"] == ["pkg.root"]
    assert helper["text_unavailable"] is True

    missing = root.module_view("sha-1", "pkg.elsewhere")
    assert missing["unknown_module"] is True


def test_part_view_locates_and_misses_honestly() -> None:
    """
    Verify the part-grain read: a named function resolves with its span,
    carrying module, and source kind; a kind-filtered miss answers
    found=False with the searched modules listed - never raising.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    _install_crystal(aether, _custody_payload())

    part = root.part_view("sha-1", "cast")
    assert part["found"] is True
    assert part["kind"] == "function"
    assert part["module_name"] == "pkg.root"
    assert part["source_kind"] == "synthetic"
    assert "def cast():" in part["text"]

    miss = root.part_view("sha-1", "cast", kind="class")
    assert miss["found"] is False
    assert "pkg.root" in miss["searched_modules"]

    with pytest.raises(ValueError, match="Known kinds"):
        root.part_view("sha-1", "cast", kind="method")


def test_part_diff_reports_change_and_module_radius() -> None:
    """
    Verify the class/function-grain comparison: recorded part texts diff
    between versions, the verdict carries per-side truth, and the radius
    section is the carrying module's residency-joined impact. A part
    absent on one side answers honestly.
    """
    aether = _two_world_aether()
    root = _activated_root(aether)

    verdict = root.part_diff("sha-base", "sha-donor", "cast")

    assert verdict["left_found"] is True
    assert verdict["right_found"] is True
    assert verdict["left_module"] == "pkg.root"
    assert verdict["identical"] is False
    assert any(
        "return 99" in line for line in verdict["unified_diff"]
    )
    assert verdict["impact"]["affected_modules"] == ["pkg.root"]

    # 'fresh' exists only in the donor: honest one-sided verdict, radius
    # still centered on the side that carries it.
    one_sided = root.part_diff("sha-base", "sha-donor", "fresh")
    assert one_sided["left_found"] is False
    assert one_sided["right_found"] is True
    assert one_sided["identical"] is None
    assert one_sided["unified_diff"] is None
    assert one_sided["impact"] is not None


def test_lane_type_enforcement_propagates_from_configuration() -> None:
    """
    Verify the configured posture reaches every set: armed at activation,
    inherited by sets created afterwards.
    """
    aether = _mock_aether()
    root = MutationResearch(aether=aether)
    configuration = (
        root.create_configuration()
        .with_defaults()
        .with_lane_type_enforcement(True)
        .activate()
    )
    root.configure(configuration)
    root.activate(hydrate_from_record=False)

    assert root.research_set().lane_type_enforcement is True
    assert root.create_research_set(
        "side"
    ).lane_type_enforcement is True

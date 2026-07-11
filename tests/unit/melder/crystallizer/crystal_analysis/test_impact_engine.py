"""
S3 impact-engine unit suite: reverse-index closure, honest unknowns,
custody-state flagging, and fingerprint drift over real temp files.
"""

import hashlib

from melder.crystallizer.crystal_analysis.impact_engine import ImpactEngine


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _crystal(
        *,
        spell_id,
        root_module,
        modules,
        dependencies,
        spellbook_id="book-1",
        custody_state="active",
        fingerprints=None,
        paths=None,
):
    return {
        "id": spell_id,
        "root_module_name": root_module,
        "spellbook_id": spellbook_id,
        "custody_state": custody_state,
        "module_targets": list(modules),
        "module_to_direct_dependencies": dict(dependencies),
        "physical_module_fingerprints": dict(fingerprints or {}),
        "module_to_path": dict(paths or {}),
    }


def _two_spell_world():
    """
    Two spells: alpha's root imports shared.core; beta's root imports
    shared.core THROUGH an intermediate. Changing shared.core must reach
    both; changing beta's intermediate must reach only beta.
    """
    return {
        "sha-alpha": _crystal(
            spell_id="sha-alpha",
            root_module="userland.alpha",
            modules=["userland.alpha", "shared.core"],
            dependencies={"userland.alpha": ["shared.core"]},
        ),
        "sha-beta": _crystal(
            spell_id="sha-beta",
            root_module="userland.beta",
            modules=["userland.beta", "userland.mid", "shared.core"],
            dependencies={
                "userland.beta": ["userland.mid"],
                "userland.mid": ["shared.core"],
            },
            spellbook_id="book-2",
            custody_state="inactive",
        ),
    }


def test_blast_radius_walks_reverse_imports_transitively():
    """
    Contract: the closure follows recorded reverse import edges - a leaf
    change reaches every transitive importer and every carrying spell,
    with spellbook edges and custody states riding the answer.
    """
    engine = ImpactEngine(_two_spell_world())
    try:
        radius = engine.blast_radius_of_module("shared.core")
        assert radius["unknown_module"] is False
        assert radius["affected_modules"] == [
            "shared.core", "userland.alpha", "userland.beta",
            "userland.mid",
        ]
        assert radius["affected_spells"] == ["sha-alpha", "sha-beta"]
        assert radius["affected_spellbooks"] == ["book-1", "book-2"]
        assert radius["custody_states"]["sha-beta"] == "inactive"

        narrow = engine.blast_radius_of_module("userland.mid")
        assert narrow["affected_spells"] == ["sha-beta"]
        assert "userland.alpha" not in narrow["affected_modules"]
    finally:
        engine.cleanup()


def test_unknown_inputs_answer_honestly():
    """
    Contract: unknown modules and spells return empty radii with the
    unknown marker - "nothing recorded depends on it" is an answer, not
    an error.
    """
    engine = ImpactEngine(_two_spell_world())
    try:
        unknown = engine.blast_radius_of_module("never.recorded")
        assert unknown["unknown_module"] is True
        assert unknown["affected_modules"] == []
        assert unknown["affected_spells"] == []

        ghost = engine.blast_radius_of_spell("sha-ghost")
        assert ghost["unknown_spell"] is True
        assert ghost["root_module"] is None
    finally:
        engine.cleanup()


def test_spell_radius_is_its_root_module_radius():
    """
    Contract: a spell change IS its root module changing - the spell view
    carries the module radius plus the spell identity row.
    """
    engine = ImpactEngine(_two_spell_world())
    try:
        radius = engine.blast_radius_of_spell("sha-beta")
        assert radius["unknown_spell"] is False
        assert radius["root_module"] == "userland.beta"
        # Nothing imports beta's root, so the radius is beta alone.
        assert radius["affected_spells"] == ["sha-beta"]
    finally:
        engine.cleanup()


def test_source_drift_classifies_and_carries_radii(tmp_path):
    """
    Contract: sealed fingerprints re-hash from disk with the CRLF-safe
    text read - unchanged files report quietly, edited files report
    "drifted" WITH their blast radius, deleted files report "absent".
    """
    unchanged_file = tmp_path / "steady.py"
    unchanged_file.write_text("VALUE = 1\n", encoding="utf-8")
    drifted_file = tmp_path / "edited.py"
    drifted_file.write_text("VALUE = 2\n", encoding="utf-8")

    custody = {
        "sha-alpha": _crystal(
            spell_id="sha-alpha",
            root_module="steady",
            modules=["steady", "edited", "gone"],
            dependencies={"steady": ["edited", "gone"]},
            fingerprints={
                "steady": _sha("VALUE = 1\n"),
                "edited": _sha("VALUE = ORIGINAL\n"),
                "gone": _sha("VALUE = 3\n"),
            },
            paths={
                "steady": str(unchanged_file),
                "edited": str(drifted_file),
                "gone": str(tmp_path / "gone.py"),
            },
        ),
    }
    engine = ImpactEngine(custody)
    try:
        drift = engine.describe_source_drift()
        assert drift["statuses"] == {
            "steady": "unchanged", "edited": "drifted", "gone": "absent",
        }
        assert drift["counts"]["unchanged"] == 1
        assert drift["counts"]["drifted"] == 1
        assert drift["counts"]["absent"] == 1
        assert "steady" not in drift["radii"]
        # The drifted leaf's radius climbs to its importer's spell.
        assert drift["radii"]["edited"]["affected_spells"] == ["sha-alpha"]
        assert "steady" in drift["radii"]["edited"]["affected_modules"]

        report = engine.describe()
        assert report["custody_count"] == 1
        assert report["drift"]["counts"]["drifted"] == 1
    finally:
        engine.cleanup()

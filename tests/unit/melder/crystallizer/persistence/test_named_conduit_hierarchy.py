"""Hierarchy analysis rejects malformed edges and coalesces shared unnamed support."""

from copy import deepcopy

import pytest

from melder.crystallizer.crystal_analysis.conduit_hierarchy import ConduitHierarchy
from melder.crystallizer.crystal_analysis.preflight.conduit_hierarchy_strategy import ConduitHierarchyStrategy


def _bundle() -> dict[str, dict[str, dict[str, object]]]:
    """Build a root with two named siblings sharing one unnamed supporting parent."""
    lineage = [
        {"conduit_id": "root", "parent_conduit_id": None, "conduit_name": "owner", "policy_name": "default"},
        {"conduit_id": "support", "parent_conduit_id": "root", "conduit_name": None, "policy_name": "default"},
    ]
    children = {}
    for name in ("a", "b"):
        children[name] = {
            "conduit_id": name, "conduit_name": name, "spellbook_id": "book", "dynamic": True,
            "policy_name": "default", "link_targets": [],
            "configuration_payload": {
                "conduit_state": "lesser", "root_conduit_id": "root", "parent_conduit_id": "support",
                "lineage_ancestors": deepcopy(lineage),
            },
        }
    return {
        "spellbook": {"book": {"frame_name": "frame"}},
        # Deliberately put the root last: row insertion order must not select a child as root.
        "conduit": {
            **children,
            "root": {"conduit_id": "root", "conduit_name": "owner", "spellbook_id": "book"},
        },
    }


def test_shared_support_is_built_once_after_its_root() -> None:
    """Parent ordering must work when input rows start with the children and the root is legacy-shaped."""
    bundle = _bundle()
    original = deepcopy(bundle)
    rows, order = ConduitHierarchy.build(bundle["conduit"], bundle["spellbook"])
    assert order == {"book": ["root", "support", "a", "b"]}
    assert set(rows) == {"root", "support", "a", "b"}
    assert rows["support"]["conduit_name"] is None
    assert ConduitHierarchyStrategy().analyze(bundle) == []
    assert bundle == original


def test_removed_final_carrier_leaves_no_unnamed_support() -> None:
    """Expansion derives support from surviving named records, not independent retained state."""
    bundle = _bundle()
    del bundle["conduit"]["a"]
    rows, _order = ConduitHierarchy.build(bundle["conduit"], bundle["spellbook"])
    assert "support" in rows
    del bundle["conduit"]["b"]
    rows, order = ConduitHierarchy.build(bundle["conduit"], bundle["spellbook"])
    assert set(rows) == {"root"}
    assert order == {"book": ["root"]}


@pytest.mark.parametrize("fault", [
    "missing_root", "missing_named_parent", "cross_book", "wrong_root", "wrong_parent",
    "cycle", "conflicting_support", "pooled", "empty_name", "duplicate_name", "duplicate_root",
    "malformed_lineage", "malformed_configuration", "payload_id_mismatch", "nondefault_lesser_policy",
])
def test_invalid_hierarchy_is_an_admission_blocker(fault: str) -> None:
    """Invalid ownership or ancestry must refuse before public replay can construct any scopes."""
    bundle = _bundle()
    row = bundle["conduit"]["a"]
    configuration = row["configuration_payload"]
    if fault == "missing_root":
        del bundle["conduit"]["root"]
    elif fault == "missing_named_parent":
        configuration["lineage_ancestors"][1]["conduit_name"] = "unrecorded-parent"
    elif fault == "cross_book":
        row["spellbook_id"] = "other-book"
        bundle["spellbook"]["other-book"] = {"frame_name": "frame"}
    elif fault == "wrong_root":
        configuration["root_conduit_id"] = "elsewhere"
    elif fault == "wrong_parent":
        configuration["parent_conduit_id"] = "root"
    elif fault == "cycle":
        configuration["lineage_ancestors"][1]["conduit_id"] = "a"
    elif fault == "conflicting_support":
        configuration["lineage_ancestors"][1]["policy_name"] = "block_all"
    elif fault == "pooled":
        configuration["conduit_state"] = "pooled_lesser"
    elif fault == "empty_name":
        row["conduit_name"] = ""
    elif fault == "duplicate_name":
        row["conduit_name"] = "b"
    elif fault == "duplicate_root":
        bundle["conduit"]["extra-root"] = {"conduit_name": "extra", "spellbook_id": "book"}
    elif fault == "malformed_lineage":
        configuration["lineage_ancestors"] = "not-a-list"
    elif fault == "malformed_configuration":
        row["configuration_payload"] = []
    elif fault == "nondefault_lesser_policy":
        row["policy_name"] = "block_all"
    else:
        row["conduit_id"] = "wrong-id"
    findings = ConduitHierarchyStrategy().analyze(bundle)
    assert len(findings) == 1
    assert findings[0]["severity"] == "blocker"
    assert findings[0]["strategy"] == "conduit_hierarchy"
    with pytest.raises(ValueError):
        ConduitHierarchy.build(bundle["conduit"], bundle["spellbook"])


def test_root_only_legacy_analysis_keeps_its_existing_tolerance() -> None:
    """The new strategy does not reject partial root-only bundles that older analysis accepted."""
    assert ConduitHierarchyStrategy().analyze({"conduit": {"root": {"link_targets": []}}}) == []

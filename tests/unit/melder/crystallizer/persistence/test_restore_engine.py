"""
Unit tests for the restore engine's pure-data machinery: chain folding
(later-wins, tombstones, activity moves), the RestoreReport contract,
engine lifecycle (single-use, cleanup), and hydration honesty
classification. No live world is built here; the integration suite owns
the full round trip.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.persistence.restore_engine import (
    RestoreEngine,
    RestoreReport,
)


def _window(journal, payloads):
    """
    Build one detached replay window in the PersistenceCrystal shape.

    Args:
        journal: [[sequence, kind, key], ...] entries in window order.
        payloads: {kind: {key: payload}} captured final states.

    Returns:
        dict: One replay_data-shaped window.
    """
    return {"journal": journal, "payloads": payloads}


def _engine(windows):
    """
    Build one engine over hand-made windows (ids auto-minted).

    Args:
        windows: Detached replay windows, oldest first.

    Returns:
        RestoreEngine: Fresh single-use engine.
    """
    checkpoint_ids = [
        "01TESTCHAIN{0:015d}".format(position)
        for position in range(len(windows))
    ]
    return RestoreEngine(
        profile_name="default",
        checkpoint_ids=checkpoint_ids,
        chain=windows,
    )


def _book_payload(spellbook_id="book-1", frame_name="default", **extra):
    """
    Build one folded spellbook payload with overridable fields.
    """
    payload = {
        "twin_kind": "spellbook",
        "spellbook_id": spellbook_id,
        "frame_name": frame_name,
        "configuration_payload": {},
        "hook_names": [],
        "bind_order": [],
    }
    payload.update(extra)
    return payload


def _custody_payload(spell_id, spellbook_id="book-1", **extra):
    """
    Build one folded custody payload with overridable fields.
    """
    payload = {
        "id": spell_id,
        "spellbook_id": spellbook_id,
        "spell_name": "svc",
        "binding_name": None,
        "spellframe_name": None,
        "existence_name": "unique",
        "permissions_name": "create",
        "disposal_method_names": [],
        "profile_family": "general",
        "rebindability": "hydratable",
        "root_module_kind": "user_source",
        "root_module_name": "tests.mocks.spellbook.core_classes",
        "root_target_qualname": "BasicService",
        "root_target_kind": "class",
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# Fold semantics
# ---------------------------------------------------------------------------

def test_fold_later_window_wins_per_kind_and_key():
    """
    Contract: the same (kind, key) journaled in a later window replaces the
    earlier payload entirely (full objects, never diffs).
    """
    engine = _engine([
        _window(
            [[1, "spellbook", "book-1"]],
            {"spellbook": {"book-1": _book_payload(bind_order=["a"])}},
        ),
        _window(
            [[2, "spellbook", "book-1"]],
            {"spellbook": {"book-1": _book_payload(bind_order=["a", "b"])}},
        ),
    ])
    engine._fold_chain()
    assert engine._books["book-1"]["bind_order"] == ["a", "b"]
    engine.cleanup()


def test_fold_spell_removed_tombstone_deletes_custody():
    """
    Contract: a spell_removed tombstone evicts folded custody from both
    locations.
    """
    engine = _engine([
        _window(
            [[1, "spell_crystal", "sha-1"], [2, "spell_removed", "sha-1"]],
            {
                "spell_crystal": {"sha-1": _custody_payload("sha-1")},
                "spell_removed": {"sha-1": {"spell_id": "sha-1", "removed": True}},
            },
        ),
    ])
    engine._fold_chain()
    assert "sha-1" not in engine._custody_active
    assert "sha-1" not in engine._custody_inactive
    engine.cleanup()


def test_fold_spellbook_removed_sweeps_the_parent_edge_subtree():
    """
    Contract: spellbook_removed applies the SAME parent-edge match the live
    eviction used - custody, indexes, conduits, and the dead conduits'
    contracts all leave the fold.
    """
    engine = _engine([
        _window(
            [
                [1, "spellbook", "book-1"],
                [2, "spell_crystal", "sha-1"],
                [3, "spell_index", "idx-1"],
                [4, "conduit", "cond-1"],
                [5, "contract", "con-1"],
                [6, "spellbook_removed", "book-1"],
            ],
            {
                "spellbook": {"book-1": _book_payload()},
                "spell_crystal": {"sha-1": _custody_payload("sha-1")},
                "spell_index": {
                    "idx-1": {
                        "spellbook_id": "book-1",
                        "selected_spell_id": "sha-1",
                        "member_spell_ids": ["sha-1"],
                    }
                },
                "conduit": {
                    "cond-1": {
                        "conduit_id": "cond-1",
                        "spellbook_id": "book-1",
                        "link_targets": [],
                    }
                },
                "contract": {
                    "con-1": {
                        "contract_id": "con-1",
                        "conduit_a_id": "cond-1",
                        "conduit_b_id": "cond-2",
                    }
                },
                "spellbook_removed": {
                    "book-1": {"spellbook_id": "book-1", "removed": True}
                },
            },
        ),
    ])
    engine._fold_chain()
    assert engine._books == {}
    assert engine._custody_active == {}
    assert engine._indexes == {}
    assert engine._conduits == {}
    assert engine._contracts == {}
    engine.cleanup()


def test_fold_frame_removed_cascades_books_and_clusters():
    """
    Contract: frame_removed sweeps the frame, every book recorded on it
    (via the book sweep), and the frame's clusters.
    """
    engine = _engine([
        _window(
            [
                [1, "frame", "default"],
                [2, "spellbook", "book-1"],
                [3, "cluster", "clu-1"],
                [4, "frame_removed", "default"],
            ],
            {
                "frame": {"default": {"frame_name": "default"}},
                "spellbook": {"book-1": _book_payload()},
                "cluster": {
                    "clu-1": {
                        "cluster_id": "clu-1",
                        "cluster_name": "team",
                        "frame_name": "default",
                        "member_conduit_ids": [],
                    }
                },
                "frame_removed": {
                    "default": {"frame_name": "default", "removed": True}
                },
            },
        ),
    ])
    engine._fold_chain()
    assert engine._frames == {}
    assert engine._books == {}
    assert engine._clusters == {}
    engine.cleanup()


def test_fold_custody_location_annotation_routes_staged_members():
    """
    Contract: a custody payload annotated custody_location="inactive" folds
    into the staged store (bind_inactive-born members never flip, so the
    annotation is their only location signal); unannotated payloads default
    active (pre-annotation cached checkpoints).
    """
    engine = _engine([
        _window(
            [[1, "spell_crystal", "sha-staged"], [2, "spell_crystal", "sha-old"]],
            {
                "spell_crystal": {
                    "sha-staged": _custody_payload(
                        "sha-staged", custody_location="inactive"
                    ),
                    "sha-old": _custody_payload("sha-old"),
                }
            },
        ),
    ])
    engine._fold_chain()
    assert "sha-staged" in engine._custody_inactive
    assert "sha-staged" not in engine._custody_active
    assert "sha-old" in engine._custody_active
    engine.cleanup()


def test_fold_spell_activity_moves_custody_between_locations():
    """
    Contract: spell_activity park moves custody active -> inactive; a later
    promote moves it back.
    """
    engine = _engine([
        _window(
            [
                [1, "spell_crystal", "sha-1"],
                [2, "spell_activity", "sha-1"],
            ],
            {
                "spell_crystal": {"sha-1": _custody_payload("sha-1")},
                "spell_activity": {
                    "sha-1": {
                        "spell_id": "sha-1",
                        "active": False,
                        "custody_present": True,
                    }
                },
            },
        ),
        _window(
            [[3, "spell_activity", "sha-1"]],
            {
                "spell_activity": {
                    "sha-1": {
                        "spell_id": "sha-1",
                        "active": True,
                        "custody_present": True,
                    }
                }
            },
        ),
    ])
    engine._fold_chain()
    assert "sha-1" in engine._custody_active
    assert "sha-1" not in engine._custody_inactive
    engine.cleanup()


def test_fold_single_unit_tombstones_delete_their_keys():
    """
    Contract: index / contract / cluster removals each evict exactly their
    recorded key.
    """
    engine = _engine([
        _window(
            [
                [1, "spell_index", "idx-1"],
                [2, "contract", "con-1"],
                [3, "cluster", "clu-1"],
                [4, "spell_index_removed", "idx-1"],
                [5, "contract_removed", "con-1"],
                [6, "cluster_removed", "clu-1"],
            ],
            {
                "spell_index": {"idx-1": {"spellbook_id": "b"}},
                "contract": {"con-1": {"conduit_a_id": "x", "conduit_b_id": "y"}},
                "cluster": {"clu-1": {"frame_name": "default"}},
                "spell_index_removed": {"idx-1": {"removed": True}},
                "contract_removed": {"con-1": {"removed": True}},
                "cluster_removed": {"clu-1": {"removed": True}},
            },
        ),
    ])
    engine._fold_chain()
    assert engine._indexes == {}
    assert engine._contracts == {}
    assert engine._clusters == {}
    engine.cleanup()


def test_fold_state_switches_land_in_stores_not_shortfalls():
    """
    Contract (whole-system restore cut): lifecycle state switches fold to
    their STORES silently - nexus_state feeds the nexus replay stage
    directly, and the MR stores feed the ordered mutation_research report
    stage. The fold itself files no shortfalls for them.
    """
    engine = _engine([
        _window(
            [
                [1, "nexus_state", "enabled"],
                [2, "mutation_research_state", "enabled"],
            ],
            {
                "nexus_state": {
                    "enabled": {"state": "enabled", "twin_present": True}
                },
                "mutation_research_state": {
                    "enabled": {"state": "enabled", "twin_present": True}
                },
            },
        ),
    ])
    engine._fold_chain()
    assert engine._nexus_state_name == "enabled"
    assert engine._mutation_research_state_name == "enabled"
    assert engine._report.describe()["shortfalls"] == []
    engine.cleanup()


# ---------------------------------------------------------------------------
# RestoreReport contract
# ---------------------------------------------------------------------------

def test_report_counts_shortfalls_and_identity_map_round_trip():
    """
    Contract: built counts accumulate per kind, shortfalls append in order,
    and identity translation resolves what was mapped (None otherwise).
    """
    report = RestoreReport("default", ["01X"])
    report.record_built("spellbook")
    report.record_built("spellbook")
    report.add_shortfall("spell_crystal", "sha-1", "why")
    report.map_identity("old-1", "new-1")
    assert report.translate("old-1") == "new-1"
    assert report.translate("old-404") is None
    payload = report.describe()
    assert payload["built_counts"] == {"spellbook": 2}
    assert payload["shortfalls"] == [
        {"kind": "spell_crystal", "key": "sha-1", "reason": "why"}
    ]
    report.cleanup()


def test_report_describe_returns_detached_copies():
    """
    Contract: mutating a describe() payload never mutates the report.
    """
    report = RestoreReport("default", ["01X"])
    report.record_built("link")
    payload = report.describe()
    payload["built_counts"]["link"] = 99
    payload["shortfalls"].append({"kind": "x", "key": "y", "reason": "z"})
    fresh = report.describe()
    assert fresh["built_counts"] == {"link": 1}
    assert fresh["shortfalls"] == []
    report.cleanup()


def test_report_status_transitions_and_construction_guards():
    """
    Contract: pending -> failed(stage) / complete; empty construction
    inputs raise ValueError.
    """
    report = RestoreReport("default", ["01X"])
    assert report.describe()["status"] == "pending"
    report.mark_failed("links")
    assert report.describe()["status"] == "failed"
    assert report.describe()["failed_stage"] == "links"
    report.mark_complete()
    assert report.describe()["status"] == "complete"
    report.cleanup()
    with pytest.raises(ValueError):
        RestoreReport("", ["01X"])
    with pytest.raises(ValueError):
        RestoreReport("default", [])


def test_report_cleanup_is_idempotent_and_guards_reads():
    """
    Contract: double cleanup is safe; reads after cleanup raise.
    """
    report = RestoreReport("default", ["01X"])
    report.cleanup()
    report.cleanup()
    with pytest.raises(RuntimeError):
        report.describe()


# ---------------------------------------------------------------------------
# Engine lifecycle
# ---------------------------------------------------------------------------

def test_engine_rejects_empty_or_misaligned_chains():
    """
    Contract: an empty chain and a chain/ids length mismatch both raise
    ValueError at construction.
    """
    with pytest.raises(ValueError):
        RestoreEngine(profile_name="default", checkpoint_ids=[], chain=[])
    with pytest.raises(ValueError):
        RestoreEngine(
            profile_name="default",
            checkpoint_ids=["01A", "01B"],
            chain=[_window([], {})],
        )


def test_engine_is_single_use():
    """
    Contract: the second restore() on one engine raises RuntimeError.
    """
    engine = _engine([_window([], {})])
    report = engine.restore()
    assert report.describe()["status"] == "complete"
    with pytest.raises(RuntimeError):
        engine.restore()
    report.cleanup()
    engine.cleanup()


def test_engine_empty_world_restores_to_empty_completion():
    """
    Contract: a chain recording nothing replays nothing and completes with
    empty built counts (no runtime surfaces touched).
    """
    engine = _engine([_window([], {})])
    report = engine.restore()
    payload = report.describe()
    assert payload["status"] == "complete"
    assert payload["built_counts"] == {}
    report.cleanup()
    engine.cleanup()


def test_engine_cleanup_is_idempotent_and_owns_unrun_report():
    """
    Contract: cleanup twice is safe; a never-run engine cleans its own
    report; a consumed engine leaves report ownership with the caller.
    """
    engine = _engine([_window([], {})])
    engine.cleanup()
    engine.cleanup()
    consumed = _engine([_window([], {})])
    report = consumed.restore()
    consumed.cleanup()
    assert report.describe()["status"] == "complete"
    report.cleanup()


# ---------------------------------------------------------------------------
# Hydration honesty
# ---------------------------------------------------------------------------

def test_hydrate_replay_required_files_shortfall_and_returns_none():
    """
    Contract: replay_required custody never imports; one shortfall names
    the recorded target kind.
    """
    engine = _engine([_window([], {})])
    result = engine._hydrate_target(
        "sha-1",
        _custody_payload(
            "sha-1", rebindability="replay_required",
            root_target_kind="method",
        ),
    )
    assert result is None
    shortfalls = engine._report.describe()["shortfalls"]
    assert "replay_required_target_kind" in shortfalls[0]["reason"]
    engine.cleanup()


def test_hydrate_synthetic_root_files_loader_chain_shortfall():
    """
    Contract: synthetic-rooted custody is reported until the loader chain
    (parent M3/M5) lands.
    """
    engine = _engine([_window([], {})])
    result = engine._hydrate_target(
        "sha-1",
        _custody_payload("sha-1", root_module_kind="synthetic_module"),
    )
    assert result is None
    shortfalls = engine._report.describe()["shortfalls"]
    assert shortfalls[0]["reason"] == "synthetic_root_requires_loader_chain_m3"
    engine.cleanup()


def test_hydrate_import_failure_files_shortfall_not_partial_bind():
    """
    Contract: a dead module path degrades to one hydration_failed shortfall.
    """
    engine = _engine([_window([], {})])
    result = engine._hydrate_target(
        "sha-1",
        _custody_payload(
            "sha-1", root_module_name="tests.no_such_module_anywhere",
        ),
    )
    assert result is None
    shortfalls = engine._report.describe()["shortfalls"]
    assert "hydration_failed" in shortfalls[0]["reason"]
    engine.cleanup()


def test_hydrate_hydratable_class_resolves_the_live_target():
    """
    Contract: hydratable user-source custody imports the recorded module
    and walks the qualname to the concrete class.
    """
    engine = _engine([_window([], {})])
    target = engine._hydrate_target("sha-1", _custody_payload("sha-1"))
    from tests.mocks.spellbook.core_classes import BasicService

    assert target is BasicService
    engine.cleanup()


def test_fold_routes_nexus_twin_and_later_wins_lifecycle_state():
    """
    Contract: the nexus twin folds to the root store and nexus_state is
    later-wins - the final flip is the recorded lifecycle truth.
    """
    engine = _engine([_window(
        [
            [1, "nexus", "root"],
            [2, "nexus_state", "enabled"],
            [3, "nexus_state", "disabled"],
        ],
        {
            "nexus": {"root": {
                "configured": True,
                "enabled": True,
                "configuration_payload": {"max_active_rift_count": 3},
            }},
            "nexus_state": {
                "enabled": {"state": "enabled", "twin_present": True},
                "disabled": {"state": "disabled", "twin_present": True},
            },
        },
    )])
    engine._fold_chain()
    assert engine._nexus_payload is not None
    assert engine._nexus_payload["configuration_payload"][
        "max_active_rift_count"
    ] == 3
    assert engine._nexus_state_name == "disabled"
    engine.cleanup()


def test_mutation_research_reports_in_order_never_silently():
    """
    Contract: recorded MR truth folds to stores and the ordered stage
    reports both the twin and the lifecycle state as not-restored
    (owner scope) - never silently.
    """
    engine = _engine([_window(
        [
            [1, "mutation_research", "root"],
            [2, "mutation_research_state", "enabled"],
        ],
        {
            "mutation_research": {"root": {"configured": True}},
            "mutation_research_state": {
                "enabled": {"state": "enabled", "twin_present": True},
            },
        },
    )])
    engine._fold_chain()
    engine._replay_mutation_research()
    reasons = [
        entry["reason"]
        for entry in engine._report.describe()["shortfalls"]
    ]
    assert (
        "mutation_research_recorded_not_restored_first_cut" in reasons
    )
    assert (
        "mutation_research_state_recorded_not_restored_first_cut"
        in reasons
    )
    engine.cleanup()

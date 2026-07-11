"""
Unit tests for the S4 unfold subsystem: LoadPlan declarativeness,
LoadAdmission's formation minting and scope adjudication (renamed from
BootMediator 2026-07-11), the engine's admission gate (refuse-on-blockers
before any replay), and the loader's durable load state.

Runs only on 3.14t (melder package root import chain).
"""
from melder.crystallizer.crystal_loader_system.load_admission import (
    LoadAdmission,
)
from melder.crystallizer.crystal_loader_system.crystal_loader_system import (
    CrystalLoaderSystem,
)
from melder.crystallizer.crystal_loader_system.load_plan import LoadPlan
from melder.crystallizer.crystal_loader_system.restore_engine import (
    RestoreEngine,
)
from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)


def _blocker_window():
    """
    Build one synthetic window whose folded bundle pre-flights to
    "blockers": hydratable custody with no spellbook twin and an
    unfindable module (hydration strategy blockers).
    """
    custody_payload = {
        "id": "sha-blocked",
        "spellbook_id": "book-gone",
        "rebindability": "hydratable",
        "root_module_kind": "user_source",
        "root_module_name": "tests.no_such_module_anywhere_s4",
        "root_target_kind": "class",
    }
    return {
        "journal": [[1, "spell_crystal", "sha-blocked"]],
        "payloads": {"spell_crystal": {"sha-blocked": custody_payload}},
    }


def test_load_plan_reports_counts_and_refuses_unknown_scopes():
    """
    Contract: the plan is declarative - distinct journaled keys count per
    kind, describe() carries identity + counts (never payloads), and an
    unrecognized scope refuses at construction.
    """
    plan = LoadPlan(
        scope="world",
        profile_name="default",
        source_label="ck-1",
        checkpoint_ids=["ck-0", "ck-1"],
        chain=[
            {"journal": [[1, "spellbook", "b1"], [2, "conduit", "c1"]],
             "payloads": {}},
            {"journal": [[1, "spellbook", "b1"], [2, "spellbook", "b2"]],
             "payloads": {}},
        ],
    )
    try:
        summary = plan.describe()
        assert summary["scope"] == "world"
        assert summary["window_count"] == 2
        assert summary["kind_key_counts"] == {"spellbook": 2, "conduit": 1}
        assert "payloads" not in summary
    finally:
        plan.cleanup()

    try:
        LoadPlan(
            scope="galaxy",
            profile_name="default",
            source_label="x",
            checkpoint_ids=[],
            chain=[],
        )
        raised = False
    except ValueError as exc:
        raised = True
        assert "galaxy" in str(exc)
    assert raised


def test_formation_plan_mints_the_canonical_window(tmp_path):
    """
    Contract: formation planning derives the scope from the stored record
    and mints ONE synthetic window whose journal follows the canonical
    kind order (parents before dependents), sorted within each kind.
    """
    record_system = PersistenceSystem()
    admission_plane = LoadAdmission(record_system)
    formation_record = {
        "formation_name": "keeper",
        "profile_name": "default",
        "scope": {"conduit_id": "cond-1"},
        "created_at": "01J0",
        "description": "",
        "payloads": {
            "conduit": {"cond-1": {"conduit_id": "cond-1"}},
            "spellbook": {"book-1": {"spellbook_id": "book-1"}},
            "spell_crystal": {"sha-b": {"id": "sha-b"}, "sha-a": {"id": "sha-a"}},
        },
    }
    try:
        plan = admission_plane.plan_formation_load(formation_record)
        try:
            assert plan.scope == "conduit"
            assert plan.source_label == "formation-keeper"
            assert plan.checkpoint_ids == ["formation-keeper"]
            window = plan.chain[0]
            journal_kinds_keys = [
                (entry[1], entry[2]) for entry in window["journal"]
            ]
            assert journal_kinds_keys == [
                ("spellbook", "book-1"),
                ("conduit", "cond-1"),
                ("spell_crystal", "sha-a"),
                ("spell_crystal", "sha-b"),
            ]
        finally:
            plan.cleanup()
    finally:
        admission_plane.cleanup()
        record_system.cleanup()


def test_scope_adjudication_reclassifies_expected_frame_posture():
    """
    Contract (S1 flip-back criterion): conduit-scoped admission treats
    frame_posture warnings as expected-for-scope - the admission verdict
    recomputes to clean while the reclassified rows are reported; other
    warnings and every blocker still count.
    """
    preflight = {
        "verdict": "warnings",
        "counts": {"warning": 1},
        "findings": [
            {"strategy": "frame_posture", "severity": "warning",
             "kind": "spellbook", "key": "book-1", "detail": "bare frame"},
        ],
    }
    admission = LoadAdmission._adjudicate_for_scope(preflight, "conduit")
    assert admission["verdict"] == "clean"
    assert admission["scope"] == "conduit"
    assert len(admission["reclassified"]) == 1
    assert admission["reclassified"][0]["severity"] == "expected_for_scope"

    mixed = {
        "verdict": "warnings",
        "counts": {"warning": 2},
        "findings": [
            {"strategy": "frame_posture", "severity": "warning",
             "kind": "spellbook", "key": "book-1", "detail": "bare frame"},
            {"strategy": "link_integrity", "severity": "warning",
             "kind": "conduit", "key": "cond-1", "detail": "dangling"},
        ],
    }
    mixed_admission = LoadAdmission._adjudicate_for_scope(mixed, "conduit")
    assert mixed_admission["verdict"] == "warnings"

    blocked = {
        "verdict": "blockers",
        "counts": {"blocker": 1},
        "findings": [
            {"strategy": "hydration", "severity": "blocker",
             "kind": "spell_crystal", "key": "sha-1", "detail": "gone"},
        ],
    }
    blocked_admission = LoadAdmission._adjudicate_for_scope(blocked, "frame")
    assert blocked_admission["verdict"] == "blockers"


def test_world_scope_admission_is_the_raw_verdict():
    """
    Contract: world-scoped loads never reclassify - the admission verdict
    IS the raw preflight verdict.
    """
    preflight = {
        "verdict": "warnings",
        "counts": {"warning": 1},
        "findings": [
            {"strategy": "frame_posture", "severity": "warning",
             "kind": "spellbook", "key": "book-1", "detail": "bare"},
        ],
    }
    admission = LoadAdmission._adjudicate_for_scope(preflight, "world")
    assert admission["verdict"] == "warnings"
    assert admission["reclassified"] == []


def test_admission_refuses_blocker_worlds_before_any_replay():
    """
    Contract (verdict law): with the admission knob armed, a "blockers"
    folded preflight refuses the load with a teach-grade error naming the
    blocker rows - and nothing is built (no teardown path involved).
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-blocked"],
        chain=[_blocker_window()],
        refuse_on_blockers=True,
    )
    try:
        try:
            engine.restore()
            raised = False
        except RuntimeError as exc:
            raised = True
            message = str(exc)
            assert "admission refused" in message
            assert "hydration" in message
            assert "sha-blocked" in message
        assert raised
    finally:
        engine.cleanup()


def test_legacy_direct_engines_still_report_without_gating():
    """
    Contract (default parity): a direct engine without the knob keeps the
    pre-S4 behavior - the blocker verdict rides the report's preflight
    section and the restore itself proceeds under shortfall honesty.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-blocked"],
        chain=[_blocker_window()],
    )
    try:
        report = engine.restore()
        payload = report.describe()
        report.cleanup()
        # The parity fact: no gate fired (restore returned), and the
        # blocker verdict rides the report exactly as it did pre-S4.
        assert payload["preflight"]["verdict"] == "blockers"
    finally:
        if not engine.cleaned:
            engine.cleanup()


def test_engine_mr_stage_noops_without_a_recorded_twin():
    """
    Contract (mr_restore_build_stage S2): a world without research stays
    without it - no built row, no shortfall, and the retired first_cut
    vocabulary never appears.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-no-mr"],
        chain=[{"journal": [], "payloads": {}}],
    )
    try:
        report = engine.restore()
        payload = report.describe()
        report.cleanup()
        assert "mutation_research" not in payload["built_counts"]
        assert "first_cut" not in str(payload)
        assert "mutation_research" not in str(payload.get("shortfalls", []))
    finally:
        if not engine.cleaned:
            engine.cleanup()


def test_engine_mr_stage_reports_cleaned_worlds_honestly():
    """
    Contract (mr_restore_build_stage S2): folded lifecycle "cleaned" is
    later-wins truth - the world sealed AFTER its MR died, so the stage
    files the honest shortfall and rebuilds NOTHING (no runtime touch,
    which is why this lane is unit-testable over a bare window).
    """
    window = {
        "journal": [
            [1, "mutation_research", "root"],
            [2, "mutation_research_state", "cleaned"],
        ],
        "payloads": {
            "mutation_research": {
                "root": {
                    "activated": True,
                    "configuration_payload": {
                        "unrestricted_module_mutations": False,
                    },
                    "composition_payload": {},
                },
            },
        },
    }
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-mr-cleaned"],
        chain=[window],
    )
    try:
        report = engine.restore()
        payload = report.describe()
        report.cleanup()
        assert "mutation_research" not in payload["built_counts"]
        assert "cleaned_before_seal_not_rebuilt" in str(payload)
        assert "first_cut" not in str(payload)
    finally:
        if not engine.cleaned:
            engine.cleanup()


def test_loader_remembers_nothing_until_the_first_load():
    """
    Contract: durable load state starts honest - {"loaded": False} before
    any load runs through the pipeline.
    """
    record_system = PersistenceSystem()
    loader = CrystalLoaderSystem(record_system)
    try:
        assert loader.describe_last_load() == {"loaded": False}
    finally:
        loader.cleanup()
        record_system.cleanup()


def test_detach_profile_chain_refuses_unknown_checkpoints():
    """
    Contract: the ledger's loader feedstock verb raises KeyError for ids
    the ledger never sealed.
    """
    record_system = PersistenceSystem()
    try:
        try:
            record_system.detach_profile_chain("no-such-checkpoint")
            raised = False
        except KeyError:
            raised = True
        assert raised
    finally:
        record_system.cleanup()


def _stub_host(frames):
    """
    Build a minimal Aether stand-in for host-preflight unit runs.

    The admission plane touches exactly: `_aetheric_frames` (registry
    read, never creating), `frame.frame_configuration.system_state.name`,
    `cloud.has_conduit_name`, and the documented `_conduit_clusters`
    seam - so the stubs carry exactly those surfaces.
    """
    class _StubCloud:
        def __init__(self, taken_names=(), clusters=()):
            self._taken = set(taken_names)
            self._conduit_clusters = {name: object() for name in clusters}

        def has_conduit_name(self, name):
            return name in self._taken

    class _StubState:
        def __init__(self, name):
            self.name = name

    class _StubFrameConfiguration:
        def __init__(self, state_name):
            self.system_state = _StubState(state_name)

    class _StubFrame:
        def __init__(self, state_name="dynamic", taken_names=(),
                     clusters=()):
            self.frame_configuration = _StubFrameConfiguration(state_name)
            self._conduit_cloud = _StubCloud(taken_names, clusters)

    class _StubAether:
        def __init__(self, frame_map):
            self._aetheric_frames = frame_map

    built = {
        name: _StubFrame(**spec) for name, spec in frames.items()
    }
    return _StubAether(built)


def _retargetable_record():
    """One frame-scoped formation record with every frame-edge carrier."""
    return {
        "formation_name": "mover",
        "profile_name": "default",
        "scope": {"frame_name": "alpha"},
        "created_at": "01J1",
        "description": "",
        "payloads": {
            "frame": {"alpha": {"system_state": "dynamic"}},
            "spellbook": {
                "book-1": {"spellbook_id": "book-1", "frame_name": "alpha"},
            },
            "conduit": {
                "cond-1": {
                    "conduit_id": "cond-1", "spellbook_id": "book-1",
                    "conduit_name": "pump",
                },
            },
            "cluster": {
                "clu-1": {
                    "cluster_id": "clu-1", "cluster_name": "pod",
                    "frame_name": "alpha",
                },
            },
        },
    }


def test_retarget_rewrites_the_detached_window_only():
    """
    Contract (S1): target_frame_name re-keys the frame twin, rewrites the
    journal's frame row and every book/cluster frame edge - and the stored
    record the caller passed is NEVER mutated (copy-on-write).
    """
    record_system = PersistenceSystem()
    admission_plane = LoadAdmission(record_system)
    formation_record = _retargetable_record()
    try:
        plan = admission_plane.plan_formation_load(
            formation_record, target_frame_name="beta"
        )
        try:
            assert plan.target_frame_name == "beta"
            window = plan.chain[0]
            payloads = window["payloads"]
            assert list(payloads["frame"].keys()) == ["beta"]
            assert payloads["spellbook"]["book-1"]["frame_name"] == "beta"
            assert payloads["cluster"]["clu-1"]["frame_name"] == "beta"
            frame_rows = [
                entry for entry in window["journal"] if entry[1] == "frame"
            ]
            assert [entry[2] for entry in frame_rows] == ["beta"]
            # Copy-on-write: the caller's record still says alpha.
            assert list(
                formation_record["payloads"]["frame"].keys()
            ) == ["alpha"]
            assert formation_record["payloads"]["spellbook"]["book-1"][
                "frame_name"
            ] == "alpha"
        finally:
            plan.cleanup()
    finally:
        admission_plane.cleanup()
        record_system.cleanup()


def test_retarget_refuses_multi_frame_windows_and_bad_names():
    """
    Contract (S1): formations are single-frame slices - a multi-frame
    window refuses retargeting, and falsy/non-string targets refuse.
    """
    record_system = PersistenceSystem()
    admission_plane = LoadAdmission(record_system)
    formation_record = _retargetable_record()
    formation_record["payloads"]["frame"]["gamma"] = {
        "system_state": "dynamic"
    }
    try:
        for bad_target in ("beta", ""):
            try:
                admission_plane.plan_formation_load(
                    formation_record, target_frame_name=bad_target
                )
                raised = False
            except ValueError:
                raised = True
            assert raised
    finally:
        admission_plane.cleanup()
        record_system.cleanup()


def test_host_preflight_reports_all_four_check_kinds():
    """
    Contract (S1): against a wired host, the preflight reports frame
    absence as info, posture conflict as warning, and conduit/cluster
    name collisions as blockers; with no host wired it reports empty.
    """
    record_system = PersistenceSystem()
    host = _stub_host({
        "alpha": {
            "state_name": "automatic",
            "taken_names": ("pump",),
            "clusters": ("pod",),
        },
    })
    admission_plane = LoadAdmission(record_system, aether=host)
    bare_plane = LoadAdmission(PersistenceSystem())
    try:
        plan = admission_plane.plan_formation_load(_retargetable_record())
        try:
            findings = admission_plane._preflight_host(plan)
            by_check = {row["check"]: row for row in findings}
            assert by_check["frame_posture_conflict"]["severity"] == (
                "warning"
            )
            assert by_check["conduit_name_taken"]["severity"] == "blocker"
            assert by_check["cluster_name_taken"]["severity"] == "blocker"
            assert bare_plane._preflight_host(plan) == []

            retargeted = admission_plane.plan_formation_load(
                _retargetable_record(), target_frame_name="elsewhere"
            )
            try:
                moved = admission_plane._preflight_host(retargeted)
                moved_checks = {row["check"] for row in moved}
                # The target frame does not exist: replay creates it, and
                # nothing can collide inside a frame that is not there.
                assert moved_checks == {"frame_missing"}
            finally:
                retargeted.cleanup()
        finally:
            plan.cleanup()
    finally:
        admission_plane.cleanup()
        bare_plane.cleanup()
        record_system.cleanup()


def test_host_blockers_refuse_before_any_replay_unless_skipping():
    """
    Contract (S1): host-collision blockers refuse execute_plan BEFORE the
    engine is even imported (teach-grade error names the rows); the same
    plan with skip_existing carries the downgrade armed instead.
    """
    record_system = PersistenceSystem()
    host = _stub_host({
        "alpha": {"state_name": "dynamic", "taken_names": ("pump",)},
    })
    admission_plane = LoadAdmission(record_system, aether=host)
    try:
        plan = admission_plane.plan_formation_load(_retargetable_record())
        try:
            try:
                admission_plane.execute_plan(plan)
                raised = None
            except RuntimeError as exc:
                raised = str(exc)
            assert raised is not None
            assert "host preflight" in raised
            assert "conduit_name_taken" in raised
        finally:
            plan.cleanup()

        armed = admission_plane.plan_formation_load(
            _retargetable_record(), skip_existing=True
        )
        try:
            assert armed.skip_existing is True
            assert armed.describe()["skip_existing"] is True
        finally:
            armed.cleanup()
    finally:
        admission_plane.cleanup()
        record_system.cleanup()

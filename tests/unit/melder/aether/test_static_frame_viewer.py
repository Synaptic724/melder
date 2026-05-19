from types import SimpleNamespace

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.nexus.nexus import Nexus
from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.existence.existence import Existence
from tests.unit.melder.aether.test_frame_viewer_projection import _build_viewer


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each static-viewer unit test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether


def test_static_frame_viewer_from_frame_viewer_handles_plain_and_static_sources() -> None:
    viewer = _build_viewer(("ops",))
    static_viewer = StaticFrameViewer.from_frame_viewer(viewer)
    cloned_static_viewer = StaticFrameViewer.from_frame_viewer(static_viewer)

    assert static_viewer._rift is viewer._rift
    assert cloned_static_viewer._rift is static_viewer._rift


def test_static_frame_viewer_cleanup_clone_and_dispatch_paths_work() -> None:
    viewer = _build_viewer(("ops",))
    static_viewer = StaticFrameViewer.from_frame_viewer(viewer)
    targets = static_viewer.list_targets(frame_name="ops")

    assert len(targets) == 2
    assert {link.source_kind for link in targets} == {"frame", "conduit"}

    clone = static_viewer.clone()
    assert isinstance(clone, StaticFrameViewer)
    assert clone is not static_viewer

    static_viewer.cleanup()
    static_viewer.cleanup()
    assert static_viewer.cleaned is True


def test_static_frame_viewer_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, viewer: StaticFrameViewer) -> None:
            self._viewer = viewer

        def __enter__(self):
            self._viewer._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    viewer = StaticFrameViewer.from_frame_viewer(_build_viewer(("ops",)))
    original_lock = viewer._lock
    viewer._lock = _FlipCleanedOnEnter(viewer)
    try:
        viewer.cleanup()
    finally:
        viewer._lock = original_lock

    assert viewer.cleaned is True


def test_static_frame_viewer_live_spell_helpers_cover_record_and_probe_paths(monkeypatch) -> None:
    viewer = StaticFrameViewer.from_frame_viewer(_build_viewer(("ops",)))

    monkeypatch.setattr(
        StaticFrameViewer,
        "_iter_live_spell_records_for_frame",
        lambda self, frame_name: [
            SimpleNamespace(origin_spellbook_id="ops-spellbook", spell_id="ops-spell"),
        ],
    )
    assert viewer.list_spell_source_ids_for_frame("ops") == ["ops-spellbook:ops-spell"]
    records = list(viewer._iter_spell_records(frame_name="ops"))
    assert records[0].spell_id == "ops-spell"

    with pytest.raises(ValueError, match="spell_source_id cannot be empty."):
        viewer._get_required_spell_record("")

    monkeypatch.setattr(
        StaticFrameViewer,
        "_iter_live_spell_records_for_frame",
        lambda self, frame_name: [],
    )
    with pytest.raises(ValueError, match="Spell source id 'ops-spellbook:ops-spell' was not found."):
        viewer._get_required_spell_record("ops-spellbook:ops-spell")

    monkeypatch.setattr(
        StaticFrameViewer,
        "_get_frame_names_for_query",
        lambda self, frame_name=None: ("ops", "finance"),
    )
    monkeypatch.setattr(
        StaticFrameViewer,
        "_iter_live_spell_records_for_frame",
        lambda self, frame_name: [
            SimpleNamespace(origin_spellbook_id="ops-spellbook", spell_id="ops-spell"),
        ],
    )
    with pytest.raises(ValueError, match="Spell source id 'ops-spellbook:ops-spell' is ambiguous across hosted frames."):
        viewer._get_required_spell_record("ops-spellbook:ops-spell")


def test_static_frame_viewer_live_projection_filters_and_owner_resolution_work(monkeypatch) -> None:
    viewer = StaticFrameViewer.from_frame_viewer(_build_viewer(("ops",)))
    descriptor = viewer._get_required_frame_descriptor("ops")
    original_is_live = StaticFrameViewer._is_spell_record_live
    original_get_owner = StaticFrameViewer._get_owner_conduit

    base_surface = SimpleNamespace(
        visible_spell_keys=(("ops-spellbook", "ops-spell"), ("missing-book", "missing")),
        visible_spell_index_ids=("ops-lineage", "missing-lineage"),
        frame_name="ops",
        configuration_id="cfg",
        view_profile_name="general",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        command_frame_enabled=False,
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("query",),
        frame_payload_fields=("system_state",),
        visible_conduit_ids=("ops-conduit",),
        enabled_conduit_ids=tuple(),
        enabled_spell_index_ids=tuple(),
        conduit_payload_sections_by_id={},
        spell_payload_sections_by_key={},
        metadata={},
    )
    monkeypatch.setattr(
        FrameViewer,
        "_get_required_compiled_access_surface",
        lambda self, frame_name: base_surface,
    )

    monkeypatch.setattr(
        StaticFrameViewer,
        "_is_spell_record_live",
        lambda self, frame_name, spell_record: True,
    )

    live_records = viewer._iter_live_spell_records_for_frame("ops")
    assert len(live_records) == 1
    assert live_records[0].spell_id == "ops-spell"

    spell_record = descriptor.spell_records_by_key[("ops-spellbook", "ops-spell")]
    spell_record.existence = Existence.many
    assert original_is_live(viewer, "ops", spell_record) is False
    spell_record.existence = Existence.unique
    spell_record.owner_conduit_id = None
    assert original_is_live(viewer, "ops", spell_record) is False
    spell_record.owner_conduit_id = "ops-conduit"

    monkeypatch.setattr(
        StaticFrameViewer,
        "_get_owner_conduit",
        lambda self, frame_name, conduit_id: None,
    )
    assert original_is_live(viewer, "ops", spell_record) is False

    class _Owner:
        def __init__(self, raises: bool) -> None:
            self._raises = raises

        def has_live_creation(self, spell: str) -> bool:
            if self._raises:
                raise ValueError("boom")
            return True

    monkeypatch.setattr(
        StaticFrameViewer,
        "_get_owner_conduit",
        lambda self, frame_name, conduit_id: _Owner(True),
    )
    assert original_is_live(viewer, "ops", spell_record) is False

    monkeypatch.setattr(
        StaticFrameViewer,
        "_get_owner_conduit",
        lambda self, frame_name, conduit_id: _Owner(False),
    )
    assert original_is_live(viewer, "ops", spell_record) is True

    fake_lesser = object()
    fake_ward = SimpleNamespace(_get_lesser_conduit=lambda conduit_id: fake_lesser)
    fake_frame = SimpleNamespace(_conduits={"root": SimpleNamespace(_conduit_ward=fake_ward)})
    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(ValueError("missing")),
            _aetheric_frames={"ops": fake_frame},
            _ensure_default_frame=lambda: None,
            _default_frame=fake_frame,
        ),
        raising=False,
    )
    assert original_get_owner(viewer, "ops", "missing") is fake_lesser
    assert original_get_owner(viewer, "default", "missing") is fake_lesser

    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(ValueError("missing")),
            _aetheric_frames={"ops": None},
            _ensure_default_frame=lambda: None,
            _default_frame=None,
        ),
        raising=False,
    )
    assert original_get_owner(viewer, "ops", "missing") is None

    no_match_frame = SimpleNamespace(
        _conduits={
            "root": SimpleNamespace(_conduit_ward=None),
            "root-2": SimpleNamespace(
                _conduit_ward=SimpleNamespace(_get_lesser_conduit=lambda conduit_id: None)
            ),
        }
    )
    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(ValueError("missing")),
            _aetheric_frames={"ops": no_match_frame},
            _ensure_default_frame=lambda: None,
            _default_frame=no_match_frame,
        ),
        raising=False,
    )
    assert original_get_owner(viewer, "ops", "missing") is None

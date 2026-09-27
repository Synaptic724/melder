"""Step 4b of the aether_conduit_lookup_api lane: Nexus-side unit tests and transfer fakes.

- test_nexus.py: the capability lesser lookup test now runs Aether's live walk; static-room fakes and
  monkeypatches move to get_root_conduit_by_id; the ACL-denial fake names the method CommandSystem calls.
- test_static_command_system_direct.py: fakes move to get_root_conduit_by_id.
- test_static_frame_viewer.py: owner resolution is delegation to Aether.get_conduit_by_id.
- test_command_system_direct.py: adds the missing-frame error-mapping test.
- transfer tests: FakeAether exposes the root names TransferOfOwnership now calls.

Usage: python apply_tests_nexus_unit.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

ROOT = sys.argv[1]
UNIT = os.path.join(ROOT, "tests/unit/melder/aether")
NEXUS = os.path.join(UNIT, "test_nexus.py")
STATIC_DIRECT = os.path.join(UNIT, "test_static_command_system_direct.py")
STATIC_VIEWER = os.path.join(UNIT, "test_static_frame_viewer.py")
COMMAND_DIRECT = os.path.join(UNIT, "test_command_system_direct.py")
TRANSFER = os.path.join(UNIT, "conduit/conduit_ward/transfer/test_transfer_of_ownership.py")
TRANSFER_CONTRACTS = os.path.join(UNIT, "conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py")

CAPABILITY_OLD = '''def test_capability_command_system_can_get_conduit_by_id_with_lesser_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify capability conduit lookup falls back to lesser-conduit lineage traversal when root lookup misses.

    Returns:
        None.
    """
'''
CAPABILITY_NEW = '''def test_capability_command_system_get_conduit_by_id_resolves_lessers_through_aether(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify capability conduit lookup returns a lesser through Aether's live lookup (roots, then root wards).

    Returns:
        None.
    """
'''
CAPABILITY_STUB_OLD = '''    sentinel = object()
    root_conduit = SimpleNamespace(
        _conduit_ward=SimpleNamespace(
            _get_lesser_conduit=lambda conduit_id: sentinel,
        )
    )
    aether_stub = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(
            ValueError("missing")
        ),
        _aetheric_frames={
            "ops": SimpleNamespace(
                _conduits={"root-1": root_conduit},
            )
        },
    )
'''
CAPABILITY_STUB_NEW = '''    sentinel = object()
    root_conduit = SimpleNamespace(
        _conduit_ward=SimpleNamespace(
            _get_lesser_conduit=lambda conduit_id: sentinel,
        )
    )
    frame = SimpleNamespace(_conduits={"root-1": root_conduit})

    def live_lookup(conduit_id: str, frame_name: str) -> object:
        """Run Aether's live walk over the stub frame, raising like Aether.get_conduit_by_id on a miss."""
        conduit = Aether._find_live_conduit(frame, conduit_id)
        if conduit is None:
            raise ValueError(f"Conduit with id '{conduit_id}' not found in frame '{frame_name}'.")
        return conduit

    aether_stub = SimpleNamespace(
        get_conduit_by_id=live_lookup,
        _aetheric_frames={"ops": frame},
    )
'''
ACL_FAKE_OLD = '''        SimpleNamespace(_get_conduit_by_id=lambda conduit_id, frame_name: object()),
'''
ACL_FAKE_NEW = '''        SimpleNamespace(get_conduit_by_id=lambda conduit_id, frame_name: object()),
'''
STATIC_PATCH_OLD = '''        type(type(space.command_system)._aether),
        "_get_conduit_by_id",
        lambda self, conduit_id, frame_name: owner_conduit,
'''
STATIC_PATCH_NEW = '''        type(type(space.command_system)._aether),
        "get_root_conduit_by_id",
        lambda self, conduit_id, frame_name: owner_conduit,
'''
STATIC_FAKE_12_OLD = '''            _get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
'''
STATIC_FAKE_12_NEW = '''            get_root_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
'''
STATIC_FAKE_8_OLD = '''    space.command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )
'''
STATIC_FAKE_8_NEW = '''    space.command_system._aether = SimpleNamespace(
        get_root_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )
'''

STATIC_DIRECT_OLD = '''        _get_conduit_by_id=lambda conduit_id, frame_name: SimpleNamespace(
'''
STATIC_DIRECT_NEW = '''        get_root_conduit_by_id=lambda conduit_id, frame_name: SimpleNamespace(
'''

VIEWER_OLD = '''    fake_lesser = object()
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
'''
VIEWER_NEW = '''    # Owner resolution is Aether's live lookup (roots and attached lessers); the viewer maps a miss to None.
    fake_lesser = object()
    seen_lookups: list[tuple[str, str]] = []

    def live_lookup(conduit_id: str, frame_name: str) -> object:
        """Stand in for Aether.get_conduit_by_id: record the call and return the live lesser."""
        seen_lookups.append((conduit_id, frame_name))
        return fake_lesser

    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(get_conduit_by_id=live_lookup),
        raising=False,
    )
    assert original_get_owner(viewer, "ops", "lesser-id") is fake_lesser
    assert original_get_owner(viewer, "default", "lesser-id") is fake_lesser
    assert seen_lookups == [("lesser-id", "ops"), ("lesser-id", "default")]

    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(ValueError("missing")),
        ),
        raising=False,
    )
    assert original_get_owner(viewer, "ops", "missing") is None
'''

COMMAND_DIRECT_OLD = '''    with pytest.raises(ValueError, match="Conduit id 'missing-lesser' was not found in frame 'ops'"):
        command_system.get_conduit_by_id("missing-lesser")

    assert command_system.find_conduit_id_by_name("missing", frame_name="ops") is None
'''
COMMAND_DIRECT_NEW = '''    with pytest.raises(ValueError, match="Conduit id 'missing-lesser' was not found in frame 'ops'"):
        command_system.get_conduit_by_id("missing-lesser")

    assert command_system.find_conduit_id_by_name("missing", frame_name="ops") is None


def test_command_system_conduit_lookup_reports_a_missing_runtime_frame_before_the_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A lookup whose runtime frame Aether does not hold keeps the frame error, not the id error.

    Returns:
        None.
    """
    command_system, viewer, _ = _make_command_system()
    viewer.compiled_access_surface.enabled_conduit_ids = ("missing-lesser",)
    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(
                ValueError(f"Aetheric frame '{frame_name}' does not exist.")
            ),
            _aetheric_frames={},
        ),
    )

    with pytest.raises(ValueError, match="Aetheric frame 'ops' does not exist."):
        command_system.get_conduit_by_id("missing-lesser")
'''

TRANSFER_LIST_OLD = '''    def list_conduit_ids(self, frame_name: str) -> List[str]:
        """
        Return registered conduit ids for the requested frame.
'''
TRANSFER_LIST_NEW = '''    def list_root_conduit_ids(self, frame_name: str) -> List[str]:
        """
        Return registered root conduit ids for the requested frame.
'''
TRANSFER_GET_OLD = '''    def get_conduit_by_id(self, conduit_id: str, frame_name: str) -> Any:
        """
        Return a conduit by id from the requested frame.
'''
TRANSFER_GET_NEW = '''    def get_root_conduit_by_id(self, conduit_id: str, frame_name: str) -> Any:
        """
        Return a root conduit by id from the requested frame.
'''

print("nexus capability:", replace_block(NEXUS, CAPABILITY_OLD, CAPABILITY_NEW))
print("nexus capability stub:", replace_block(NEXUS, CAPABILITY_STUB_OLD, CAPABILITY_STUB_NEW))
print("nexus acl fake:", replace_block(NEXUS, ACL_FAKE_OLD, ACL_FAKE_NEW))
print("nexus static patches:", replace_block(NEXUS, STATIC_PATCH_OLD, STATIC_PATCH_NEW, count=2))
print("nexus static fake (12):", replace_block(NEXUS, STATIC_FAKE_12_OLD, STATIC_FAKE_12_NEW))
print("nexus static fakes (8):", replace_block(NEXUS, STATIC_FAKE_8_OLD, STATIC_FAKE_8_NEW, count=2))
print("static direct:", replace_block(STATIC_DIRECT, STATIC_DIRECT_OLD, STATIC_DIRECT_NEW, count=3))
print("static viewer:", replace_block(STATIC_VIEWER, VIEWER_OLD, VIEWER_NEW))
print("command direct:", replace_block(COMMAND_DIRECT, COMMAND_DIRECT_OLD, COMMAND_DIRECT_NEW))
for path in (TRANSFER, TRANSFER_CONTRACTS):
    print(os.path.basename(path), "list:", replace_block(path, TRANSFER_LIST_OLD, TRANSFER_LIST_NEW))
    print(os.path.basename(path), "get:", replace_block(path, TRANSFER_GET_OLD, TRANSFER_GET_NEW))

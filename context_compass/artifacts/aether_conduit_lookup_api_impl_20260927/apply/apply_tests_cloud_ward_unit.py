"""Step 4c of the aether_conduit_lookup_api lane: ConduitCloud.list_conduits and ConduitWard walk unit tests.

Usage: python apply_tests_cloud_ward_unit.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

ROOT = sys.argv[1]
CLOUD = os.path.join(ROOT, "tests/unit/melder/aether/test_conduit_cloud.py")
WARD = os.path.join(ROOT, "tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py")

CLOUD_ANCHOR = '''def test_frame_name_property_returns_configured_name(conduit_cloud) -> None:
'''
CLOUD_NEW = '''def test_list_conduits_returns_the_named_scopes_by_identity(
        conduit_cloud,
        mock_conduit,
) -> None:
    """
    Verify list_conduits returns the conduits behind the named directory and drops a retired name.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud
    root_conduits["conduit-1"] = mock_conduit
    conduit_ids_by_name["test_conduit"] = "conduit-1"
    lesser = MagicMock()
    lesser.id = "lesser-1"
    lesser._id = "lesser-1"
    lesser.name = "group"
    lesser._name = "group"
    lesser._conduit_state = ConduitState.lesser

    assert cloud.list_conduits() == ()

    cloud._register_named_conduit(mock_conduit)
    cloud._register_named_conduit(lesser)
    listed = cloud.list_conduits()

    assert isinstance(listed, tuple)
    assert len(listed) == 2
    assert {id(conduit) for conduit in listed} == {id(mock_conduit), id(lesser)}
    assert {conduit._name for conduit in listed} == set(cloud.list_conduit_names())

    cloud._unregister_named_conduit(lesser)
    remaining = cloud.list_conduits()

    assert len(remaining) == 1
    assert remaining[0] is mock_conduit


def test_list_conduits_raises_after_cleanup(conduit_cloud) -> None:
    """
    Verify list_conduits guards against use-after-clean like every Cloud read.
    """
    cloud, _, _ = conduit_cloud
    cloud.cleanup()

    with pytest.raises(RuntimeError):
        cloud.list_conduits()


def test_frame_name_property_returns_configured_name(conduit_cloud) -> None:
'''

WARD_IMPORT_OLD = '''import pytest
import threading
'''
WARD_IMPORT_NEW = '''import pytest
import threading
from types import SimpleNamespace
'''

WARD_ANCHOR = '''def test_convert_to_normal_sets_root_conduit() -> None:
'''
WARD_NEW = '''class _PopsSiblingOnIdRead:
    """Lesser stand-in whose `_id` read removes a sibling from its parent's registry, as a pool return does."""

    def __init__(self, parent_registry: dict, sibling_id: str) -> None:
        """Remember the parent's live registry and the sibling to remove on the first `_id` read."""
        self._parent_registry = parent_registry
        self._sibling_id = sibling_id
        self._conduit_ward = None

    @property
    def _id(self) -> str:
        """Remove the sibling from the live parent registry, then return this stand-in's id."""
        self._parent_registry.pop(self._sibling_id, None)
        return "first"


def test_get_lesser_conduit_walks_a_snapshot_when_a_child_detaches_mid_walk(ward):
    """
    Verify the lineage walk survives a child leaving the parent registry while it runs.

    A child returning to its pool pops itself from the parent's registry under its OWN lock, so no lock the
    walk could take prevents it; iterating the live dict raised "dictionary changed size during iteration".
    The walk reads a snapshot, so it completes and still returns the child it had already seen.
    """
    second = MagicMock()
    second._id = "second"
    second._conduit_ward = None
    ward._lesser_conduits["first"] = _PopsSiblingOnIdRead(ward._lesser_conduits, "second")
    ward._lesser_conduits["second"] = second

    assert ward._get_lesser_conduit("second") is second
    assert "second" not in ward._lesser_conduits


def test_get_lesser_conduit_skips_a_child_whose_ward_was_deleted(ward):
    """
    Verify a child whose ward hard teardown deleted is matched by id but not searched, and is never fatal.
    """
    torn_down = SimpleNamespace(_id="torn")
    target = MagicMock()
    target._id = "target"
    target._conduit_ward = None
    ward._lesser_conduits["torn"] = torn_down
    ward._lesser_conduits["target"] = target

    assert ward._get_lesser_conduit("target") is target
    assert ward._get_lesser_conduit("torn") is torn_down
    assert ward._get_lesser_conduit("missing") is None


def test_convert_to_normal_sets_root_conduit() -> None:
'''

print("cloud:", replace_block(CLOUD, CLOUD_ANCHOR, CLOUD_NEW))
print("ward import:", replace_block(WARD, WARD_IMPORT_OLD, WARD_IMPORT_NEW))
print("ward tests:", replace_block(WARD, WARD_ANCHOR, WARD_NEW))

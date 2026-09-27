"""Aether conduit lookups cover what their names say.

Regression for ledger item MF7: on 0.2.78 `Aether.get_conduit_by_name` read only the frame's root maps, so a
live named lesser scope looked absent from Aether while the frame's ConduitCloud returned it. Since 0.2.79 the
root-only lookups carry `*_root_*` names, `get_conduit_by_name` answers over the frame's named scopes (named
roots and active named lessers), `get_conduit_by_id` answers over every live conduit in the frame (roots and
attached lessers, named or anonymous), and every lookup takes its frame as a string defaulting to "default".
"""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from tests._codegen_system_support import reset_runtime_singletons


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Give every scenario a fresh Aether and clean the singletons deterministically afterwards."""
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


def _scope_tree(frame_name: str, *, dynamic: bool) -> tuple[Conduit, Conduit, Conduit]:
    """Conjure one root in `frame_name`, a named lesser under it and a named lesser under that one."""
    root = Spellbook(aetheric_frame=frame_name).conjure(name=f"root-{frame_name}", dynamic=dynamic)
    group = root.create_lesser_conduit(name=f"group-{frame_name}")
    subgroup = group.create_lesser_conduit(name=f"subgroup-{frame_name}")
    return root, group, subgroup


@pytest.mark.parametrize("dynamic", [False, True], ids=["automatic", "dynamic"])
def test_get_conduit_by_name_returns_named_lesser_scopes_at_any_depth(dynamic: bool) -> None:
    """Every named scope in the frame resolves through Aether to the same object the frame's Cloud holds."""
    root, group, subgroup = _scope_tree("lookups", dynamic=dynamic)
    aether = Aether()
    cloud = aether.get_conduit_cloud("lookups")
    for scope in (root, group, subgroup):
        assert aether.get_conduit_by_name(scope.name, "lookups") is scope
        assert cloud.get_conduit_by_name(scope.name) is scope


def test_get_conduit_by_name_needs_no_frame_argument_for_the_default_frame() -> None:
    """Scopes in the default frame resolve with the frame argument omitted."""
    root = Spellbook().conjure(name="root")
    group = root.create_lesser_conduit(name="group")
    aether = Aether()
    assert aether.get_conduit_by_name("group") is group
    assert aether.get_conduit_by_name("root") is root
    assert aether.get_conduit_by_id(group.id) is group


def test_named_scope_returned_to_its_pool_no_longer_resolves() -> None:
    """A returned named lesser leaves both the named and the live lookup; its parent still resolves."""
    root, group, subgroup = _scope_tree("lookups", dynamic=True)
    subgroup_id = subgroup.id
    subgroup.cleanup()
    aether = Aether()
    with pytest.raises(ValueError, match="'subgroup-lookups' not found in frame 'lookups'"):
        aether.get_conduit_by_name("subgroup-lookups", "lookups")
    with pytest.raises(ValueError, match=f"'{subgroup_id}' not found in frame 'lookups'"):
        aether.get_conduit_by_id(subgroup_id, "lookups")
    assert aether.get_conduit_by_name("group-lookups", "lookups") is group
    assert aether.get_conduit_by_id(group.id, "lookups") is group
    assert aether.get_conduit_by_id(root.id, "lookups") is root


@pytest.mark.parametrize("dynamic", [False, True], ids=["automatic", "dynamic"])
def test_get_conduit_by_id_returns_anonymous_and_nested_lessers(dynamic: bool) -> None:
    """Ids resolve for the root and for anonymous lessers at any depth, which the Cloud does not hold."""
    root = Spellbook(aetheric_frame="lookups").conjure(name="root", dynamic=dynamic)
    anonymous = root.create_lesser_conduit()
    nested = anonymous.create_lesser_conduit()
    aether = Aether()
    for scope in (root, anonymous, nested):
        assert aether.get_conduit_by_id(scope.id, "lookups") is scope
    assert anonymous.id not in aether.get_conduit_cloud("lookups").list_conduit_ids()


def test_root_lookups_answer_over_roots_only() -> None:
    """The root-named lookups keep the root-only answers; a named lesser is not a root."""
    root, group, _subgroup = _scope_tree("lookups", dynamic=False)
    aether = Aether()
    assert aether.get_root_conduit_by_name(root.name, "lookups") is root
    assert aether.get_root_conduit_by_id(root.id, "lookups") is root
    assert aether.list_root_conduit_ids("lookups") == (root.id,)
    assert aether.list_root_conduit_names("lookups") == (root.name,)
    assert aether.count_root_conduits("lookups") == 1
    assert aether.has_root_conduit_id(group.id, "lookups") is False
    assert aether.has_root_conduit_name(group.name, "lookups") is False
    assert aether.find_root_conduit_id_by_name(group.name, "lookups") is None
    with pytest.raises(ValueError, match="Root conduit with name 'group-lookups' not found in frame 'lookups'"):
        aether.get_root_conduit_by_name(group.name, "lookups")
    with pytest.raises(ValueError, match=f"Root conduit with id '{group.id}' not found in frame 'lookups'"):
        aether.get_root_conduit_by_id(group.id, "lookups")


def test_lookup_in_another_frame_names_the_frame_it_searched() -> None:
    """A scope in one frame is absent from another, and the error names the frame that was searched."""
    _root, group, _subgroup = _scope_tree("frame-a", dynamic=False)
    Spellbook(aetheric_frame="frame-b").conjure(name="root-frame-b")
    aether = Aether()
    with pytest.raises(ValueError, match="'group-frame-a' not found in frame 'frame-b'"):
        aether.get_conduit_by_name("group-frame-a", "frame-b")
    with pytest.raises(ValueError, match="'group-frame-a' not found in frame 'default'"):
        aether.get_conduit_by_name("group-frame-a")
    with pytest.raises(ValueError, match="not found in frame 'frame-b'"):
        aether.get_conduit_by_id(group.id, "frame-b")
    assert aether.get_conduit_by_name("group-frame-a", "frame-a") is group


def test_lookup_in_a_missing_custom_frame_keeps_the_frame_error() -> None:
    """A custom frame that was never created still fails with the frame error, for both lookups."""
    aether = Aether()
    with pytest.raises(ValueError, match="Aetheric frame 'nowhere' does not exist."):
        aether.get_conduit_by_name("anything", "nowhere")
    with pytest.raises(ValueError, match="Aetheric frame 'nowhere' does not exist."):
        aether.get_conduit_by_id("anything", "nowhere")


@pytest.mark.parametrize("bad_frame", [None, 7, ("default",)], ids=["none", "int", "tuple"])
def test_lookup_frame_must_be_a_string(bad_frame: object) -> None:
    """A non-string frame fails fast with TypeError instead of a misleading not-found or dict error."""
    root = Spellbook().conjure(name="root")
    aether = Aether()
    with pytest.raises(TypeError, match="aetheric_frame_name must be a frame name string"):
        aether.get_conduit_by_name(root.name, bad_frame)
    with pytest.raises(TypeError, match="aetheric_frame_name must be a frame name string"):
        aether.get_conduit_by_id(root.id, bad_frame)


def test_conduit_cloud_lists_its_named_scopes_as_objects() -> None:
    """The Cloud returns the named root and named lessers it holds, by identity; anonymous lessers are absent."""
    root, group, subgroup = _scope_tree("lookups", dynamic=True)
    anonymous = root.create_lesser_conduit()
    listed = Aether().get_conduit_cloud("lookups").list_conduits()
    assert len(listed) == 3
    assert {id(scope) for scope in listed} == {id(root), id(group), id(subgroup)}
    assert all(scope is not anonymous for scope in listed)

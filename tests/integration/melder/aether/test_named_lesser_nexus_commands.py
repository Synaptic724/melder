"""Real Rift projections and commands must follow named lesser identity through pool transitions."""

from collections.abc import Iterator

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.rift import Rift
from tests._codegen_system_support import create_enabled_nexus, reset_runtime_singletons


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Keep real singleton state local to one command scenario and clean it deterministically."""
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


def _world(room: str = "capability") -> tuple[Rift, Conduit]:
    """Create a real room attached to one empty, Nexus-managed dynamic frame."""
    nexus = create_enabled_nexus()
    configuration = nexus.create_rift_configuration().with_space_type(room)
    rift = nexus.create_rift(configuration=configuration, rift_name="named")
    root = rift.create_nexus_frame(frame_name="named-scopes")
    rift.create_frame_link("named-scopes")
    return rift, root


@pytest.mark.parametrize("room", ["capability", "codegen"])
def test_named_getter_resolves_authorized_lesser_and_preserves_root_lookup(room: str) -> None:
    """Both raw-object postures return the named lesser after the normal explicit refresh."""
    rift, root = _world(room)
    child = root.create_lesser_conduit(name="request")
    commands = rift.space.command_system
    with pytest.raises(ValueError, match="disabled"):
        commands.get_conduit_by_name("request", frame_name="named-scopes")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    assert commands.get_conduit_by_name("request", frame_name="named-scopes") is child
    assert commands.get_conduit_by_name(root.name, frame_name="named-scopes") is root
    assert commands.get_conduit_by_id(child.id, frame_name="named-scopes") is child


@pytest.mark.parametrize("room", ["capability", "codegen"])
def test_existing_projection_sees_named_retirement_and_same_id_reuse(room: str) -> None:
    """Descriptor replacement changes the visible name without rebuilding already-authorized IDs."""
    rift, root = _world(room)
    child = root.create_lesser_conduit(name="old")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    viewer = rift.space.frame_viewer
    commands = rift.space.command_system
    before = viewer.describe_conduit(child.id, frame_name="named-scopes")
    assert before["display_name"] == "old"
    child.cleanup()
    pooled = viewer.describe_conduit(child.id, frame_name="named-scopes")
    assert pooled["display_name"] == child.id
    assert "old" not in commands.list_conduit_names(frame_name="named-scopes")
    with pytest.raises(ValueError, match="not found"):
        commands.get_conduit_by_name("old", frame_name="named-scopes")
    assert root.create_lesser_conduit(name="new") is child
    assert viewer.describe_conduit(child.id, frame_name="named-scopes")["display_name"] == "new"
    assert commands.get_conduit_by_name("new", frame_name="named-scopes") is child
    assert before["display_name"] == "old"


def test_capability_creation_forwards_name_without_in_command_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    """Creating a named lesser inside an admitted command never drains that command's Rift gate."""
    rift, root = _world()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        """Reject synchronous projection refresh during the admitted creation call."""
        pytest.fail("Creation attempted a synchronous Rift refresh")

    with monkeypatch.context() as patch:
        patch.setattr(Rift, "refresh_runtime_projections", forbidden)
        child = rift.space.command_system.create_lesser_conduit(
            root.id, frame_name="named-scopes", name="command-child",
        )
    assert root.get_conduit_cloud().get_conduit("command-child") is child
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    assert rift.space.command_system.get_conduit_by_name("command-child", frame_name="named-scopes") is child


@pytest.mark.parametrize("same_shell", [False, True])
@pytest.mark.parametrize("room", ["capability", "codegen"])
def test_name_reuse_during_lookup_cannot_redirect_authorization(
    monkeypatch: pytest.MonkeyPatch, same_shell: bool, room: str,
) -> None:
    """A selected published ID cannot authorize a replacement ID or a renamed use of the old shell."""
    rift, root = _world(room)
    child = root.create_lesser_conduit(name="request")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    original = CommandSystem._get_required_published_conduit_id_by_name
    replacements: list[Conduit] = []

    def select_then_recycle(system: CommandSystem, name: str, *, frame_name: str) -> str:
        """Schedule one deterministic lifecycle race between descriptor selection and runtime lookup."""
        selected = original(system, name, frame_name=frame_name)
        if same_shell:
            child.cleanup()
            replacements.append(root.create_lesser_conduit(name="different"))
            assert replacements[-1] is child
        else:
            child.permanent_cleanup()
            replacements.append(root.create_lesser_conduit(name="request"))
            assert replacements[-1].id != selected
        return selected

    monkeypatch.setattr(CommandSystem, "_get_required_published_conduit_id_by_name", select_then_recycle)
    with pytest.raises((ValueError, RuntimeError)):
        rift.space.command_system.get_conduit_by_name("request", frame_name="named-scopes")
    assert len(replacements) == 1


@pytest.mark.parametrize("replacement_name", ["request", "promoted"])
def test_promotion_replaces_published_role_without_changing_visible_identity(replacement_name: str) -> None:
    """Graduation uses ordinary root publication while retaining the already-visible conduit ID."""
    rift, root = _world()
    child = root.create_lesser_conduit(name="request")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    child.upgrade_to_normal(replacement_name)
    record = Nexus()._get_required_frame_descriptor("named-scopes").conduit_records_by_id[child.id]
    assert record.root_conduit_id == child.id
    assert record.payload.conduit_state is ConduitState.normal
    assert record.payload.parent_conduit_id is None
    assert record.origin_spellbook_id != root._spellbook.id
    assert rift.space.command_system.get_conduit_by_name(replacement_name, frame_name="named-scopes") is child


def test_permanent_removal_uses_existing_explicit_projection_refresh() -> None:
    """Deleted IDs leave descriptor truth immediately and compiled membership on explicit refresh."""
    rift, root = _world()
    child = root.create_lesser_conduit(name="request")
    child_id = child.id
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    child.permanent_cleanup()
    assert not rift.space.command_system.has_conduit_name("request", frame_name="named-scopes")
    with pytest.raises(ValueError, match="Missing ConduitRecord"):
        rift.space.frame_viewer.list_conduits(frame_name="named-scopes")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    assert child_id not in {
        link.source_id for link in rift.space.frame_viewer.list_conduits(frame_name="named-scopes")
    }


def test_static_room_cannot_fetch_raw_named_lesser() -> None:
    """A name does not add a raw runtime-object door to a static room."""
    rift, root = _world("static")
    root.create_lesser_conduit(name="request")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    with pytest.raises(AttributeError, match="does not expose"):
        rift.space.command_system.get_conduit_by_name("request", frame_name="named-scopes")


@pytest.mark.parametrize("room", ["capability", "codegen"])
def test_named_lookup_obeys_conduit_command_denial_after_acl_revision(room: str) -> None:
    """Current metadata visibility never bypasses an explicit conduit command-family denial."""
    rift, root = _world(room)
    root.create_lesser_conduit(name="request")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    builder = Nexus().get_frame_acl_builder("named-scopes")
    builder.begin_command_change(contract_name="named-scopes").deny_conduit_enable()
    builder.commit_change()
    assert "request" not in rift.space.command_system.list_conduit_names(frame_name="named-scopes")
    with pytest.raises(ValueError, match="disabled"):
        rift.space.command_system.get_conduit_by_name("request", frame_name="named-scopes")


def test_named_command_result_keeps_lesser_capability_restrictions() -> None:
    """Discovery supplies the existing lesser; it does not grant root binding or peer-link rights."""
    rift, root = _world()
    child = root.create_lesser_conduit(name="request")
    rift.refresh_runtime_projections(frame_names=("named-scopes",))
    fetched = rift.space.command_system.get_conduit_by_name("request", frame_name="named-scopes")
    assert fetched is child
    with pytest.raises(RuntimeError, match="normal"):
        fetched.clear_bind_hooks()
    with pytest.raises(RuntimeError):
        root.link(fetched)

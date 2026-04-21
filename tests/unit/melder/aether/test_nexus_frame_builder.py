import pytest

from melder.aether.nexus.nexus_frame_builder import NexusFrameBuilder
from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.spellbook.configuration.system_state import SystemState


class _RecordingFrameManager:
    def __init__(self) -> None:
        self.created = []

    def create(self, configuration):
        self.created.append(configuration)
        return object()


def test_nexus_frame_builder_rejects_missing_manager() -> None:
    with pytest.raises(TypeError, match="manager cannot be None"):
        NexusFrameBuilder(manager=None, frame_name="ops")


@pytest.mark.parametrize("frame_name", ["", None])
def test_nexus_frame_builder_rejects_empty_frame_name(frame_name) -> None:
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        NexusFrameBuilder(manager=_RecordingFrameManager(), frame_name=frame_name)


def test_nexus_frame_builder_defaults_to_dynamic_ai_native_rift_enabled() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    assert builder._frame_name == "ops"
    assert builder._system_state == SystemState.dynamic
    assert builder._ai_native_enabled is True
    assert builder._rift_enabled is True
    assert builder._immutable is False
    assert builder._metadata == {}
    assert builder._root_conduit_name is None


def test_nexus_frame_builder_dynamic_defaults_is_idempotent() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    returned = builder.dynamic_defaults()

    assert returned is builder
    assert builder._system_state == SystemState.dynamic
    assert builder._ai_native_enabled is True
    assert builder._rift_enabled is True


@pytest.mark.parametrize("immutable", [True, False])
def test_nexus_frame_builder_immutable_toggles_flag(immutable: bool) -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    returned = builder.immutable(immutable)

    assert returned is builder
    assert builder._immutable is immutable


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        (None, {}),
        ({}, {}),
        ({"team": "ops"}, {"team": "ops"}),
    ],
)
def test_nexus_frame_builder_metadata_replaces_payload(metadata, expected) -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    returned = builder.metadata(metadata)

    assert returned is builder
    assert builder._metadata == expected
    if metadata:
        metadata["team"] = "other"
        assert builder._metadata == expected


@pytest.mark.parametrize(
    ("root_conduit_name", "expected"),
    [
        ("root", "root"),
        ("alpha", "alpha"),
    ],
)
def test_nexus_frame_builder_with_root_conduit_sets_name(
        root_conduit_name: str,
        expected: str,
) -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    returned = builder.with_root_conduit(root_conduit_name)

    assert returned is builder
    assert builder._root_conduit_name == expected


def test_nexus_frame_builder_with_root_conduit_rejects_empty_name() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    with pytest.raises(ValueError, match="root_conduit_name cannot be empty"):
        builder.with_root_conduit("")


def test_nexus_frame_builder_without_root_conduit_clears_name() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    ).with_root_conduit("root")

    returned = builder.without_root_conduit()

    assert returned is builder
    assert builder._root_conduit_name is None


@pytest.mark.parametrize(
    ("immutable", "metadata", "root_conduit_name"),
    [
        (False, None, None),
        (True, None, None),
        (False, {"team": "ops"}, None),
        (False, None, "root"),
        (True, {"team": "ops"}, "root"),
    ],
)
def test_nexus_frame_builder_build_matrix(
        immutable,
        metadata,
        root_conduit_name,
) -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )
    builder.immutable(immutable)
    builder.metadata(metadata)
    if root_conduit_name is not None:
        builder.with_root_conduit(root_conduit_name)

    configuration = builder.build()

    assert isinstance(configuration, NexusFrameConfiguration)
    assert configuration.frame_name == "ops"
    assert configuration.system_state == SystemState.dynamic
    assert configuration.ai_native_enabled is True
    assert configuration.rift_enabled is True
    assert configuration.immutable is immutable
    assert configuration.metadata == (metadata or {})
    assert configuration.root_conduit_name == root_conduit_name


def test_nexus_frame_builder_build_returns_detached_configuration() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )
    builder.metadata({"team": "ops"})

    configuration = builder.build()
    builder.metadata({"team": "other"})
    builder.with_root_conduit("root")

    assert configuration.metadata == {"team": "ops"}
    assert configuration.root_conduit_name is None


def test_nexus_frame_builder_create_delegates_to_manager() -> None:
    manager = _RecordingFrameManager()
    builder = NexusFrameBuilder(manager=manager, frame_name="ops")

    result = builder.create()

    assert result is not None
    assert len(manager.created) == 1
    assert isinstance(manager.created[0], NexusFrameConfiguration)
    assert manager.created[0].frame_name == "ops"


def test_nexus_frame_builder_cleanup_is_idempotent() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    )

    builder.cleanup()
    builder.cleanup()

    assert builder.cleaned is True


def test_nexus_frame_builder_cleanup_clears_owned_state() -> None:
    builder = NexusFrameBuilder(
        manager=_RecordingFrameManager(),
        frame_name="ops",
    ).with_root_conduit("root").metadata({"team": "ops"}).immutable(True)

    builder.cleanup()

    assert builder._manager is None
    assert builder._frame_name is None
    assert builder._system_state is None
    assert builder._ai_native_enabled is None
    assert builder._rift_enabled is None
    assert builder._immutable is None
    assert builder._metadata is None
    assert builder._root_conduit_name is None

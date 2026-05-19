import pytest

from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState


@pytest.mark.parametrize(
    ("immutable", "metadata", "root_conduit_name"),
    [
        (False, None, "root"),
        (True, None, "root"),
        (False, {"team": "ops"}, "root"),
        (False, None, "root"),
        (True, {"team": "ops"}, "root"),
    ],
)
def test_nexus_frame_configuration_create_dynamic_defaults_matrix(
        immutable,
        metadata,
        root_conduit_name,
) -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        immutable=immutable,
        metadata=metadata,
        root_conduit_name=root_conduit_name,
    )

    assert configuration.frame_name == "ops"
    assert configuration.system_state == SystemState.dynamic
    assert configuration.ai_native_enabled is True
    assert configuration.rift_enabled is True
    assert configuration.immutable is immutable
    assert configuration.metadata == (metadata or {})
    assert configuration.root_conduit_name == root_conduit_name


@pytest.mark.parametrize("frame_name", ["", None])
def test_nexus_frame_configuration_rejects_empty_frame_name(frame_name) -> None:
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        NexusFrameConfiguration(
            frame_name=frame_name,
            system_state=SystemState.dynamic,
            ai_native_enabled=True,
            rift_enabled=True,
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("ai_native_enabled", "true"),
        ("ai_native_enabled", 1),
        ("ai_native_enabled", object()),
        ("rift_enabled", "true"),
        ("rift_enabled", 1),
        ("rift_enabled", object()),
        ("immutable", "true"),
        ("immutable", 1),
        ("immutable", object()),
    ],
)
def test_nexus_frame_configuration_rejects_invalid_boolean_inputs(
        field_name,
        value,
) -> None:
    kwargs = {
        "frame_name": "ops",
        "system_state": SystemState.dynamic,
        "ai_native_enabled": True,
        "rift_enabled": True,
        "immutable": False,
    }
    kwargs[field_name] = value

    with pytest.raises(TypeError, match=field_name):
        NexusFrameConfiguration(**kwargs)


@pytest.mark.parametrize(
    ("system_state", "ai_native_enabled", "rift_enabled", "message"),
    [
        (
            SystemState.automatic,
            True,
            True,
            "system_state=SystemState.dynamic",
        ),
        (
            SystemState.dynamic,
            False,
            True,
            "ai_native_enabled=True",
        ),
        (
            SystemState.dynamic,
            True,
            False,
            "rift_enabled=True",
        ),
    ],
)
def test_nexus_frame_configuration_rejects_invalid_posture(
        system_state,
        ai_native_enabled,
        rift_enabled,
        message,
) -> None:
    with pytest.raises(ValueError, match=message):
        NexusFrameConfiguration(
            frame_name="ops",
            system_state=system_state,
            ai_native_enabled=ai_native_enabled,
            rift_enabled=rift_enabled,
        )


@pytest.mark.parametrize("root_conduit_name", ["", None])
def test_nexus_frame_configuration_rejects_empty_root_conduit_name(
        root_conduit_name,
) -> None:
    with pytest.raises(ValueError, match="root_conduit_name cannot be empty"):
        NexusFrameConfiguration(
            frame_name="ops",
            system_state=SystemState.dynamic,
            ai_native_enabled=True,
            rift_enabled=True,
            root_conduit_name=root_conduit_name,
        )


def test_nexus_frame_configuration_exposes_stable_id_and_properties() -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        immutable=True,
        metadata={"team": "ops"},
        root_conduit_name="root",
    )

    assert configuration.id is not None
    assert configuration.frame_name == "ops"
    assert configuration.system_state == SystemState.dynamic
    assert configuration.ai_native_enabled is True
    assert configuration.rift_enabled is True
    assert configuration.immutable is True
    assert configuration.metadata == {"team": "ops"}
    assert configuration.root_conduit_name == "root"


def test_nexus_frame_configuration_metadata_is_detached() -> None:
    metadata = {"team": "ops"}
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        metadata=metadata,
    )

    metadata["team"] = "other"
    snapshot = configuration.metadata
    snapshot["team"] = "third"

    assert configuration.metadata == {"team": "ops"}


def test_nexus_frame_configuration_to_aetheric_frame_configuration_matches_contract() -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        immutable=True,
        metadata={"team": "ops"},
        root_conduit_name="root",
    )

    frame_configuration = configuration.to_aetheric_frame_configuration()

    assert frame_configuration.origin_spellbook_id is None
    assert frame_configuration.system_state == SystemState.dynamic
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.rift_enabled is True


def test_nexus_frame_configuration_to_spellbook_configuration_matches_contract() -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        immutable=True,
        metadata={"team": "ops"},
        root_conduit_name="root",
    )

    spellbook_configuration = configuration.to_spellbook_configuration()

    frame_configuration = configuration.to_aetheric_frame_configuration()
    spellbook_configuration.load_default_dictionary()
    assert frame_configuration.system_state == SystemState.dynamic
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.rift_enabled is True
    assert spellbook_configuration.has_property("phase_scheduler_workers_per_spellbook") is True


def test_nexus_frame_configuration_cleanup_is_idempotent() -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults("ops")

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_nexus_frame_configuration_cleanup_clears_owned_state() -> None:
    configuration = NexusFrameConfiguration.create_dynamic_defaults(
        "ops",
        immutable=True,
        metadata={"team": "ops"},
        root_conduit_name="root",
    )

    configuration.cleanup()

    assert not hasattr(configuration, '_frame_name')
    assert not hasattr(configuration, '_system_state')
    assert not hasattr(configuration, '_ai_native_enabled')
    assert not hasattr(configuration, '_rift_enabled')
    assert not hasattr(configuration, '_immutable')
    assert not hasattr(configuration, '_metadata')
    assert not hasattr(configuration, '_root_conduit_name')
    assert not hasattr(configuration, '_id')
    assert not hasattr(configuration, '_lock')

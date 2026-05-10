from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_conduit import MutationConduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.mutation_research.mutation_research import MutationResearch


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each root/config test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def test_mutation_research_configuration_defaults_validate() -> None:
    """
    Verify the default mutation-research configuration is the restricted posture.
    """
    configuration = MutationResearchConfiguration().with_defaults()

    assert configuration.get_property("restricted_module_mutations") is True
    assert configuration.get_property("unrestricted_module_mutations") is False
    assert configuration.validate() is True


def test_mutation_research_configuration_rejects_both_modes_enabled() -> None:
    """
    Verify configuration rejects enabling both restricted and unrestricted modes.
    """
    configuration = MutationResearchConfiguration()
    configuration.set_property("restricted_module_mutations", True)
    configuration.set_property("unrestricted_module_mutations", True)

    with pytest.raises(ValueError, match="Exactly one"):
        configuration.validate()


def test_mutation_research_configuration_builder_activate_hands_off_configuration() -> None:
    """
    Verify the builder activates and hands off a configured object.
    """
    builder = MutationResearchConfigurationBuilder()
    configuration = builder.with_defaults().activate()

    assert configuration.activated is True
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        builder.build()


def test_mutation_research_root_configure_and_activate() -> None:
    """
    Verify the Aether-owned root follows the config/activate pattern.
    """
    aether = MagicMock()
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()

    root.configure(configuration)
    root.activate()

    assert root.is_configured is True
    assert root.is_activated is True
    assert root.configuration is configuration


def test_mutation_research_root_create_mutation_conduit_returns_placeholder() -> None:
    """
    Verify the root can construct a placeholder MutationConduit.
    """
    aether = MagicMock()
    aether._get_change_control_manager.return_value = MagicMock()
    root = MutationResearch(aether=aether)
    conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(_spell_system_states=MagicMock()),
        _aetheric_frame="default",
    )

    mutation_conduit = root.create_mutation_conduit(conduit)

    assert isinstance(mutation_conduit, MutationConduit)
    assert mutation_conduit.conduit is conduit
    assert mutation_conduit.mutation_research is root


def test_mutation_research_root_create_mutation_frame_returns_placeholder() -> None:
    """
    Verify the root can construct a placeholder MutationFrame.
    """
    aether = MagicMock()
    aether._get_spell_system_states.return_value = MagicMock()
    aether._get_change_control_manager.return_value = MagicMock()
    root = MutationResearch(aether=aether)

    mutation_frame = root.create_mutation_frame("ops")

    assert isinstance(mutation_frame, MutationFrame)
    assert mutation_frame.aetheric_frame_name == "ops"
    assert mutation_frame.mutation_research is root


def test_mutation_conduit_cleanup_releases_references() -> None:
    """
    Verify the placeholder MutationConduit releases its references on cleanup.
    """
    placeholder = MutationConduit(
        conduit=MagicMock(),
        mutation_research=MagicMock(),
        spell_system_states=MagicMock(),
        change_control_manager=MagicMock(),
    )

    placeholder.cleanup()

    assert placeholder.cleaned is True
    with pytest.raises(RuntimeError):
        _ = placeholder.conduit


def test_mutation_frame_cleanup_releases_references() -> None:
    """
    Verify the placeholder MutationFrame releases its references on cleanup.
    """
    placeholder = MutationFrame(
        aetheric_frame_name="ops",
        mutation_research=MagicMock(),
        spell_system_states=MagicMock(),
        change_control_manager=MagicMock(),
    )

    placeholder.cleanup()

    assert placeholder.cleaned is True
    with pytest.raises(RuntimeError):
        _ = placeholder.aetheric_frame_name

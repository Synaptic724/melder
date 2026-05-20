from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_conduit import MutationConduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.mutation_research.mutation_research import MutationResearch
from melder.aether.spellbook.bind.spell_index import SpellIndex


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each matrix test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


@pytest.mark.parametrize(
    "index_id",
    [f"unit-index-{i:02d}" for i in range(1, 21)],
)
def test_unit_root_session_matrix(index_id: str) -> None:
    """
    Verify session creation/retrieval/removal across many lineage ids.
    """
    root = MutationResearch(aether=MagicMock())
    index = SpellIndex(index_id)
    try:
        session = root.create_session(index, name=f"session-{index_id}")
        assert root.get_session_for_index(index) is session
        assert root.get_session_by_index_id(index.id) is session
        assert root.list_sessions() == [session]
        root.remove_session_for_index(index)
        assert root.get_session_for_index(index) is None
    finally:
        root.cleanup()
        index.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 21)),
)
def test_unit_configuration_builder_handoff_matrix(case_index: int) -> None:
    """
    Verify builder handoff paths remain stable across repeated cases.
    """
    builder = MutationResearchConfigurationBuilder()
    if case_index % 2 == 0:
        builder.with_defaults()
    else:
        builder.with_unrestricted_module_mutations(True)

    if case_index % 4 == 0:
        configuration = builder.activate()
        assert configuration.activated is True
    elif case_index % 4 == 1:
        configuration = builder.finalize()
        assert configuration.frozen is True
    else:
        configuration = builder.build()
        assert configuration.cleaned is False

    assert configuration.has_property("unrestricted_module_mutations") is True
    if case_index % 2 == 0:
        assert configuration.get_property("unrestricted_module_mutations") is False
    else:
        assert configuration.get_property("unrestricted_module_mutations") is True


@pytest.mark.parametrize(
    "frame_name",
    [f"frame-{i:02d}" for i in range(1, 21)],
)
def test_unit_create_mutation_frame_name_matrix(frame_name: str) -> None:
    """
    Verify placeholder MutationFrame preserves the supplied frame name.
    """
    aether = MagicMock()
    aether._get_spell_system_states.return_value = MagicMock()
    aether._get_change_control_manager.return_value = MagicMock()
    root = MutationResearch(aether=aether)
    try:
        mutation_frame = root.create_mutation_frame(frame_name)
        assert isinstance(mutation_frame, MutationFrame)
        assert mutation_frame.aetheric_frame_name == frame_name
    finally:
        root.cleanup()


@pytest.mark.parametrize(
    "conduit_label",
    [f"conduit-{i:02d}" for i in range(1, 21)],
)
def test_unit_create_mutation_conduit_identity_matrix(conduit_label: str) -> None:
    """
    Verify placeholder MutationConduit preserves the supplied conduit reference.
    """
    aether = MagicMock()
    aether._get_change_control_manager.return_value = MagicMock()
    root = MutationResearch(aether=aether)
    conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(_spell_system_states=MagicMock()),
        _aetheric_frame_name="default",
        label=conduit_label,
    )
    try:
        mutation_conduit = root.create_mutation_conduit(conduit)
        assert isinstance(mutation_conduit, MutationConduit)
        assert mutation_conduit.conduit.label == conduit_label
    finally:
        root.cleanup()


@pytest.mark.parametrize(
    "operation_index",
    list(range(1, 24)),
)
def test_unit_cleanup_guard_matrix(operation_index: int) -> None:
    """
    Verify cleaned-state guards stay consistent across the new root objects.
    """
    aether = MagicMock()
    aether._get_spell_system_states.return_value = MagicMock()
    aether._get_change_control_manager.return_value = MagicMock()
    root = MutationResearch(aether=aether)
    conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(_spell_system_states=MagicMock()),
        _aetheric_frame_name="default",
    )
    mutation_conduit = root.create_mutation_conduit(conduit)
    mutation_frame = root.create_mutation_frame("ops")
    configuration = root.create_configuration().with_defaults()

    targets = [
        lambda: root.cleanup(),
        lambda: mutation_conduit.cleanup(),
        lambda: mutation_frame.cleanup(),
        lambda: configuration.cleanup(),
        lambda: root.id,
        lambda: root.is_configured,
        lambda: mutation_conduit.id,
        lambda: mutation_conduit.conduit,
        lambda: mutation_frame.id,
        lambda: mutation_frame.aetheric_frame_name,
        lambda: configuration.id,
        lambda: configuration.frozen,
        lambda: configuration.activated,
        lambda: configuration.with_defaults(),
        lambda: configuration.with_unrestricted_module_mutations(False),
        lambda: configuration.validate(),
        lambda: configuration.freeze(),
        lambda: configuration.finalize(),
        lambda: configuration.activate(),
        lambda: mutation_conduit.change_control_manager,
        lambda: mutation_conduit.spell_system_states,
        lambda: mutation_frame.change_control_manager,
        lambda: mutation_frame.spell_system_states,
    ]

    target = targets[operation_index - 1]
    if operation_index <= 4:
        target()
    else:
        configuration.cleanup()
        mutation_conduit.cleanup()
        mutation_frame.cleanup()
        root.cleanup()
        with pytest.raises(RuntimeError):
            target()


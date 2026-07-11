from unittest.mock import MagicMock

import pytest

from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_research import MutationResearch


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
    "set_name",
    [f"unit-set-{i:02d}" for i in range(1, 21)],
)
def test_unit_root_research_set_registry_matrix(set_name: str) -> None:
    """
    Verify set creation/retrieval across many names on one root.
    """
    root = MutationResearch(aether=MagicMock())
    try:
        created = root.create_research_set(set_name)
        assert root.research_set(set_name) is created
        assert set_name in root.list_research_set_names()
        assert root.research_set() is not created
        with pytest.raises(ValueError):
            root.create_research_set(set_name)
    finally:
        root.cleanup()


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
    "sha_index",
    list(range(1, 21)),
)
def test_unit_default_set_registration_matrix(sha_index: int) -> None:
    """
    Verify default-set registration lands in the default lane across many
    identities.
    """
    root = MutationResearch(aether=MagicMock())
    spell_sha = f"sha-{sha_index:02d}"
    try:
        node = root.research_set().register_spell(spell_sha)
        assert node.spell_sha == spell_sha
        assert root.research_set().residence_of(spell_sha) == (
            root.research_set().default_lane.lane_id
        )
    finally:
        root.cleanup()


@pytest.mark.parametrize(
    "operation_index",
    list(range(1, 15)),
)
def test_unit_cleanup_guard_matrix(operation_index: int) -> None:
    """
    Verify cleaned-state guards stay consistent across the root surface.
    """
    root = MutationResearch(aether=MagicMock())
    configuration = root.create_configuration().with_defaults()
    research_set = root.research_set()

    targets = [
        lambda: root.cleanup(),
        lambda: configuration.cleanup(),
        lambda: root.id,
        lambda: root.is_configured,
        lambda: root.research_set(),
        lambda: root.create_research_set("late"),
        lambda: root.list_research_set_names(),
        lambda: root.describe_research_composition(),
        lambda: research_set.register_spell("sha-late"),
        lambda: research_set.lane_names(),
        lambda: configuration.id,
        lambda: configuration.frozen,
        lambda: configuration.validate(),
        lambda: configuration.activate(),
    ]

    target = targets[operation_index - 1]
    if operation_index <= 2:
        target()
    else:
        configuration.cleanup()
        root.cleanup()
        with pytest.raises(RuntimeError):
            target()

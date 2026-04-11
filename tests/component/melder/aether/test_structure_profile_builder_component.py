from typing import List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.structure_profiles.structure_profile_builder import (
    StructureProfileBuilder,
    StructureProfileTooling,
)
from melder.aether.structure_profiles.structure_profile_models import (
    FrameStructureProfile,
    SpellStructureRecord,
)
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig


@pytest.fixture(autouse=True)
def reset_singletons_for_component_structure_profile_builder() -> None:
    """
    Ensure structure-profile component tests start from clean runtime state.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _NeedsConfigAlpha:
    """
    Simple spell that depends on BasicConfig for topology/state assertions.
    """

    def __init__(self, config: BasicConfig) -> None:
        self.config = config


class _NeedsConfigBeta:
    """
    Second config-dependent spell used for related-spell assertions.
    """

    def __init__(self, config: BasicConfig) -> None:
        self.config = config


def _make_spellbook() -> Spellbook:
    """
    Build one Spellbook configured for structure-profile component tests.

    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = Configuration(aether_frame="ops")
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame="ops", configuration=configuration)


def _build_real_frame_profile() -> Tuple[
    Spellbook,
    Conduit,
    StructureProfileBuilder,
    FrameStructureProfile,
]:
    """
    Build one live frame profile from real Spellbook and conduit runtime state.

    Returns:
        Tuple[Spellbook, Conduit, StructureProfileBuilder, FrameStructureProfile]:
            Live runtime objects plus the resulting frame profile.
    """
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=_NeedsConfigAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=_NeedsConfigBeta,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    builder = StructureProfileBuilder(max_related=7)
    frame = Aether()._ensure_frame("ops")
    profile = builder.build_frame_profile(frame)
    return spellbook, conduit, builder, profile


def _find_dependent_records(
        frame_profile: FrameStructureProfile,
) -> List[SpellStructureRecord]:
    """
    Return spell records that expose at least one direct dependency.

    Args:
        frame_profile:
            Built frame profile to inspect.

    Returns:
        List[SpellStructureRecord]: Dependent spell records.
    """
    return [
        record
        for record in frame_profile.spell_records.values()
        if len(record.dependencies.get("direct_dependencies", [])) > 0
    ]


def _find_dependency_root_record(
        frame_profile: FrameStructureProfile,
) -> Optional[SpellStructureRecord]:
    """
    Return the config-root record that other spells depend on.

    Args:
        frame_profile:
            Built frame profile to inspect.

    Returns:
        Optional[SpellStructureRecord]: Dependency root record when present.
    """
    for record in frame_profile.spell_records.values():
        if len(record.dependencies.get("direct_dependents", [])) > 0:
            return record
    return None


def test_component_builder_build_frame_profile_captures_live_runtime_state() -> None:
    """
    Verify the builder captures real frame, conduit, dependency, and socket state.

    Returns:
        None.
    """
    spellbook, conduit, builder, frame_profile = _build_real_frame_profile()
    try:
        dependent_records = _find_dependent_records(frame_profile)

        assert frame_profile.frame_name == "ops"
        assert frame_profile.max_related == 7
        assert conduit._id in frame_profile.conduit_profiles
        assert len(frame_profile.spell_records) == 3
        assert len(dependent_records) == 2
        assert all(
            len(record.dependencies["direct_dependencies"]) == 1
            for record in dependent_records
        )
        assert all(len(record.sockets) >= 1 for record in dependent_records)
        assert frame_profile.clusters == []
    finally:
        builder.cleanup()
        conduit.cleanup()
        spellbook.cleanup()


def test_component_tooling_queries_real_frame_profile_graph() -> None:
    """
    Verify tooling queries operate correctly on a real built frame profile.

    Returns:
        None.
    """
    spellbook, conduit, builder, frame_profile = _build_real_frame_profile()
    tooling = StructureProfileTooling(frame_profile)
    try:
        dependent_records = sorted(
            _find_dependent_records(frame_profile),
            key=lambda record: record.spell_id,
        )
        dependency_root = _find_dependency_root_record(frame_profile)

        assert dependency_root is not None

        description = tooling.describe_spell_structure(dependent_records[0].spell_id)
        related = tooling.find_related_spells(dependent_records[0].spell_id, k=5)
        recommendations = tooling.recommend_next_inspection(
            dependent_records[0].spell_id,
        )

        assert description is not None
        assert description["spell_id"] == dependent_records[0].spell_id
        assert len(description["dependencies"]["direct_dependencies"]) == 1
        assert len(description["sockets"]) >= 1
        assert dependent_records[1].spell_id in [
            spell_id
            for spell_id, _score in related
        ]
        assert dependency_root.spell_id in recommendations
        assert tooling.list_subsystems() == []
    finally:
        tooling.cleanup()
        builder.cleanup()
        conduit.cleanup()
        spellbook.cleanup()

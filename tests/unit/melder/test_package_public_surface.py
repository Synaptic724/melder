"""
Unit tests for the LOADED package-root surface (owner ruling 2026-07-19):
every __all__ name resolves, and each curated export IS the concrete-path
object - identity, not equality.

Runs only on 3.14t (melder package root import chain).
"""
import melder


def test_every_all_name_resolves_on_the_root():
    """
    Purpose:
        The flat eager facade must never advertise a name it cannot serve.
    Contract:
        getattr succeeds for every __all__ entry (introspection over the
        PUBLIC documented contract, not a private surface).
    """
    for name in melder.__all__:
        assert getattr(melder, name) is not None


def test_core_objects_are_the_concrete_path_classes():
    """
    Purpose:
        Root exports are re-exports, never copies or wrappers.
    Contract:
        Identity with the concrete-path classes.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.crystallizer.crystallizer import Crystallizer
    from melder.mutation_research.mutation_research import MutationResearch
    from melder.nexus.nexus import Nexus

    assert melder.Aether is Aether
    assert melder.Conduit is Conduit
    assert melder.Spellbook is Spellbook
    assert melder.Crystallizer is Crystallizer
    assert melder.MutationResearch is MutationResearch
    assert melder.Nexus is Nexus


def test_configuration_surfaces_are_loaded():
    """
    Purpose:
        "All configurations included in this space" - the owner's ruling,
        verbatim.
    Contract:
        Identity for every configuration (+builder) export.
    """
    from melder.crystallizer.configuration.crystallizer_configuration import (
        CrystallizerConfiguration,
    )
    from melder.crystallizer.configuration.crystallizer_configuration_builder import (
        CrystallizerConfigurationBuilder,
    )
    from melder.mutation_research.mutation_configuration import (
        MutationResearchConfiguration,
    )
    from melder.mutation_research.mutation_configuration_builder import (
        MutationResearchConfigurationBuilder,
    )
    from melder.nexus.configuration.nexus_configuration import (
        NexusConfiguration,
    )
    from melder.nexus.configuration.rift_configuration import (
        RiftConfiguration,
    )

    assert melder.CrystallizerConfiguration is CrystallizerConfiguration
    assert (
        melder.CrystallizerConfigurationBuilder
        is CrystallizerConfigurationBuilder
    )
    assert (
        melder.MutationResearchConfiguration is MutationResearchConfiguration
    )
    assert (
        melder.MutationResearchConfigurationBuilder
        is MutationResearchConfigurationBuilder
    )
    assert melder.NexusConfiguration is NexusConfiguration
    assert melder.RiftConfiguration is RiftConfiguration


def test_enum_vocabularies_are_loaded():
    """
    Purpose:
        Front-facing enums reach the root so user code never digs paths.
    Contract:
        Identity for every enum export.
    """
    from melder.mutation_research.research_set.research_lane import LaneType
    from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
    from melder.nexus.configuration.rift_space_type import RiftSpaceType

    assert melder.LaneType is LaneType
    assert melder.NexusFrameMode is NexusFrameMode
    assert melder.RiftSpaceType is RiftSpaceType


def test_di_descriptors_are_loaded():
    """
    Purpose:
        SpellMap/SpellContract are the user's declarative DI hands.
    Contract:
        Identity with the contracts module classes.
    """
    from melder.aether.conduit.meld.contracts.spell_contract import (
        SpellContract,
    )
    from melder.aether.conduit.meld.contracts.spell_map import SpellMap

    assert melder.SpellMap is SpellMap
    assert melder.SpellContract is SpellContract


def test_registration_guard_sentinel_exists_at_import():
    """
    Purpose:
        Owner ruling: the guard is a sentinel and must exist early -
        redundancy with Aether's own boot is intentional.
    Contract:
        The package-level guard instance is live after import.
    """
    from melder.__melder_registration_guard__ import MelderRegistrationGuard

    assert isinstance(
        melder.__melder_registration_guard__, MelderRegistrationGuard
    )

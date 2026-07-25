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
def test_user_held_work_surfaces_are_loaded():
    """
    Purpose:
        Owner ruling 2026-07-19: everything a user HOLDS AND CALLS in
        normal workflows reaches the root - Rift/room/viewer/workstation,
        spellspaces, the cloud, research sets, the examiner, and the
        persistence bootstrap/mesh surfaces.
    Contract:
        Identity with the concrete-path classes.
    """
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
    from melder.aether.conduit.spell_space.spell_space import SpellSpace
    from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import (
        SpellExaminer,
    )
    from melder.crystallizer.asset_management.external_persistence_manager import (
        ExternalPersistenceManager,
    )
    from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
        ExternalPersistenceManagerConfiguration,
    )
    from melder.crystallizer.crystal_loader_system.bootstrap_loader import (
        CrystallizerBootstrap,
    )
    from melder.mutation_research.research_set.research_set import ResearchSet
    from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.rift_space.rift_space import RiftSpace
    from melder.nexus.rift.rift_space.workstation import Workstation

    import melder

    assert melder.ConduitCloud is ConduitCloud
    assert melder.SpellSpace is SpellSpace
    assert melder.SpellExaminer is SpellExaminer
    assert melder.ExternalPersistenceManager is ExternalPersistenceManager
    assert (
        melder.ExternalPersistenceManagerConfiguration
        is ExternalPersistenceManagerConfiguration
    )
    assert melder.CrystallizerBootstrap is CrystallizerBootstrap
    assert melder.ResearchSet is ResearchSet
    assert melder.FrameViewer is FrameViewer
    assert melder.Rift is Rift
    assert melder.RiftSpace is RiftSpace
    assert melder.Workstation is Workstation


def test_scan_bind_decorator_is_loaded():
    """
    Purpose:
        The deferred-registration lane is a first-class user hand:
        @md.scan_bind(...) then md.Spellbook().scan(module).
    Contract:
        Identity with the scan module's decorator.
    """
    from melder.aether.spellbook.bind.scan import scan_bind

    import melder

    assert melder.scan_bind is scan_bind


def test_user_catchable_error_vocabulary_is_loaded():
    """
    Purpose:
        Every exception a public verb raises at users is catchable from
        the root namespace - error handling never digs internal paths.
    Contract:
        Identity for the nine curated exception types.
    """
    from melder.utilities.custom_exceptions.dead_reference_error import (
        DeadReferenceError,
    )
    from melder.utilities.custom_exceptions.hook_execution_error import (
        HookExecutionError,
    )
    from melder.utilities.custom_exceptions.internal_registration_error import (
        InternalRegistrationError,
    )
    from melder.utilities.custom_exceptions.meld_execution_error import (
        MeldExecutionError,
    )
    from melder.utilities.custom_exceptions.phase_execution_error import (
        PhaseExecutionError,
    )
    from melder.utilities.custom_exceptions.phase_scheduler_error import (
        PhaseSchedulerError,
    )
    from melder.utilities.custom_exceptions.phase_timeout_error import (
        PhaseTimeoutError,
    )
    from melder.utilities.custom_exceptions.spell_space_scope_error import (
        SpellSpaceScopeError,
    )
    from melder.utilities.custom_exceptions.spellbook_validation_error import (
        SpellbookValidationError,
    )

    import melder

    assert melder.SpellbookValidationError is SpellbookValidationError
    assert melder.MeldExecutionError is MeldExecutionError
    assert melder.SpellSpaceScopeError is SpellSpaceScopeError
    assert melder.HookExecutionError is HookExecutionError
    assert melder.InternalRegistrationError is InternalRegistrationError
    assert melder.PhaseSchedulerError is PhaseSchedulerError
    assert melder.PhaseExecutionError is PhaseExecutionError
    assert melder.PhaseTimeoutError is PhaseTimeoutError
    assert melder.DeadReferenceError is DeadReferenceError


def test_internal_depths_stay_off_the_root():
    """
    Purpose:
        The owner's counter-example law: objects that LOOK public but are
        not user-facing never reach the root - ConduitWard and its kin
        stay internal.
    Contract:
        The curated exclusions are absent from __all__ and the namespace.
    """
    import melder

    for name in (
        "ConduitWard",
        "Meld",
        "Creations",
        "PhaseScheduler",
        "LoadGate",
        "RestoreEngine",
        "TransactionMediator",
        "ClaimMode",
        "ConduitCluster",
        "StaticFrameViewer",
    ):
        assert name not in melder.__all__
        assert name not in vars(melder)
def test_pass_two_doc_named_surfaces_are_loaded():
    """
    Purpose:
        Second C-doc iteration (External Interfaces section): the viewer
        family the doc names as user surfaces, the DiffEngine that
        create_diff_engine() hands users, LaneState (the enum behind the
        public lane.state property).
    Contract:
        Identity with the concrete-path objects.
    """
    from melder.mutation_research.diff.diff_engine import DiffEngine
    from melder.mutation_research.research_set.research_lane import LaneState
    from melder.nexus.rift.frame_viewer.view_conduit import ViewConduit
    from melder.nexus.rift.frame_viewer.view_frame import ViewFrame
    from melder.nexus.rift.frame_viewer.view_multiframe import ViewMultiFrame
    from melder.nexus.rift.frame_viewer.view_spell import ViewSpell

    import melder

    assert melder.ViewFrame is ViewFrame
    assert melder.ViewConduit is ViewConduit
    assert melder.ViewSpell is ViewSpell
    assert melder.ViewMultiFrame is ViewMultiFrame
    assert melder.DiffEngine is DiffEngine
    assert melder.LaneState is LaneState


def test_all_names_are_unique_and_sorted_groups_are_complete():
    """
    Purpose:
        The facade ledger stays exact: no duplicate advertisements, and
        every name in __all__ is actually present on the module.
    Contract:
        len(set) == len(list); vars coverage for all 64 names.
    """
    import melder

    assert len(set(melder.__all__)) == len(melder.__all__)
    for name in melder.__all__:
        assert name in vars(melder)
def test_pass_four_domain_nouns_are_loaded():
    """
    Purpose:
        Workflow iteration (owner: think how a user/agent uses this):
        the public read surfaces hand out the system's two domain nouns -
        spells (find_spell_by_id -> Spell) and the index keys of the
        spells mapping (SpellIndex) - so both types reach the root.
    Contract:
        Identity with the concrete-path classes; the init docstring
        carries the agent workflow map naming the hardcopy doc objects.
    """
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.spellbook.spell import Spell

    import melder

    assert melder.Spell is Spell
    assert melder.SpellIndex is SpellIndex
    assert "Workflow map" in melder.__doc__
    assert "__architecture__" in melder.__doc__

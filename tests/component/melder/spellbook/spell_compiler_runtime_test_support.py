"""Shared runtime helpers for compiler component and integration tests."""

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.spell_compiler import SpellCompiler
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spell_compiler.validation.validation_system import (
    SpellValidationSystem,
)
from melder.aether.spellbook.spellbook import Spellbook


def reset_aether_runtime() -> None:
    """Reset the Aether singleton and rebind Spellbook and Conduit to it."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def make_spellbook() -> Spellbook:
    """Build a Spellbook with deterministic single-worker phase scheduling."""
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def get_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """Resolve a live local spell by its current version id."""
    return spellbook._spell_id_pool.get(spell_id)


def run_structural_phases(
        compiler_system: SpellCompilerSystem,
        spellbook: Spellbook,
        spell,
) -> None:
    """Run phases 1 to 4 for one spell through SpellCompilerSystem."""
    compiler_system.run_phase_requirements(spell)
    compiler_system.run_phase_symbolic_graph(spell)
    compiler_system.run_phase_local_frame(spellbook, spell)
    compiler_system.run_phase_validation(spellbook, spell)


def run_foundational_phases(
        compiler_system: SpellCompilerSystem,
        spellbook: Spellbook,
        spell,
        conduit_id: str,
) -> None:
    """Run phases 5 to 7 for one spell through SpellCompilerSystem."""
    compiler_system.run_phase_root_blueprints(spellbook, spell, conduit_id)
    compiler_system.run_phase_system_validation(spellbook, spell, conduit_id)
    compiler_system.run_phase_change_control(spellbook, spell, conduit_id)


def run_local_foundational_phases(
        compiler_system: SpellCompilerSystem,
        spellbook: Spellbook,
        spell,
        conduit_id: str,
) -> None:
    """Run local phases 5 to 7 for one target spell through SpellCompilerSystem."""
    compiler_system.run_phase_root_blueprints_local(spellbook, spell, conduit_id)
    compiler_system.run_phase_system_validation_local(spellbook, spell, conduit_id)
    compiler_system.run_phase_change_control_local(spellbook, spell, conduit_id)


def run_plan_phases(
        compiler_system: SpellCompilerSystem,
        spellbook: Spellbook,
        spell,
) -> None:
    """Run phases 8 to 11 for one spell through SpellCompilerSystem."""
    compiler_system.run_phase_occurrence_plan(spellbook, spell)
    compiler_system.run_phase_injection_plan(spell)
    compiler_system.run_phase_patch_maps(spell)
    compiler_system.run_phase_execution_plan(spellbook, spell)


def run_all_phases(
        compiler_system: SpellCompilerSystem,
        spellbook: Spellbook,
        spell,
        conduit_id: str,
) -> None:
    """Run phases 1 to 11 for one spell through SpellCompilerSystem."""
    compiler_system.run_all_phases(spellbook, spell, conduit_id)


def run_structural_phases_with_compiler(
        compiler: SpellCompiler,
        spellbook: Spellbook,
        spell,
) -> None:
    """Run phases 1 to 4 for one spell through the direct SpellCompiler surface."""
    validator = SpellValidationSystem()
    compiler.run_phase_requirements(spell, spell._compiler_artifact)
    compiler.run_phase_symbolic_graph(spell, spell._compiler_artifact)
    compiler.run_phase_local_frame(
        spell,
        spell._compiler_artifact,
        spellbook,
        spellbook._spell_system_states,
    )
    compiler.run_phase_validation(
        spell,
        spell._compiler_artifact,
        validator,
        spellbook._spell_system_states,
    )

"""
Purpose:
    Provide component-test helpers for running spell compiler phases after the
    hard `Spell` seam removal.

Contract:
    - Uses `SpellCompilerSystem` as the only phase-execution surface.
    - Creates a short-lived compiler-system instance per helper call.
    - Never restores removed `Spell` methods or `_crafter`.
"""

from typing import Any, Optional

from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)


def run_phase_requirements(spell: Any, cancel_event: Optional[Any] = None) -> None:
    """Run compiler phase 1 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_requirements(spell, cancel_event=cancel_event)
    finally:
        compiler_system.cleanup()


def run_phase_symbolic_graph(spell: Any, cancel_event: Optional[Any] = None) -> None:
    """Run compiler phase 2 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_symbolic_graph(spell, cancel_event=cancel_event)
    finally:
        compiler_system.cleanup()


def run_phase_local_frame(spell: Any, cancel_event: Optional[Any] = None) -> None:
    """Run compiler phase 3 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_local_frame(
            spell._spellbook,
            spell,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_validation(
        spell: Any,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 4 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_validation(
            spell._spellbook,
            spell,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_root_blueprints(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 5 frame-wide for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_root_blueprints(
            spell._spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_root_blueprints_local(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 5 local for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_root_blueprints_local(
            spell._spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_system_validation(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 6 frame-wide for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_system_validation(
            spell._spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_system_validation_local(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 6 local for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_system_validation_local(
            spell._spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
    finally:
        compiler_system.cleanup()


def run_phase_change_control(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 7 frame-wide for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_change_control(spell._spellbook, spell, conduit_id)
    finally:
        compiler_system.cleanup()


def run_phase_change_control_local(
        spell: Any,
        conduit_id: str,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 7 local for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_change_control_local(
            spell._spellbook,
            spell,
            conduit_id,
        )
    finally:
        compiler_system.cleanup()


def run_phase_occurrence_plan(
        spell: Any,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 8 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_occurrence_plan(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


def run_phase_injection_plan(
        spell: Any,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 9 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_injection_plan(spell)
    finally:
        compiler_system.cleanup()


def run_phase_patch_maps(
        spell: Any,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phase 10 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_patch_maps(spell)
    finally:
        compiler_system.cleanup()


def run_phase_execution_plan(
        spell: Any,
        cancel_event: Optional[Any] = None,
) -> None:
    """Run compiler phases 11-12 for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_execution_plan(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


def cleanup_phase_artifacts(spell: Any) -> None:
    """Cleanup structural phase artifacts for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.cleanup_phase_artifacts(spell)
    finally:
        compiler_system.cleanup()


def clear_phase5_artifacts(spell: Any) -> None:
    """Cleanup phase 5+ artifacts for one spell."""
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.clear_phase5_artifacts(spell)
    finally:
        compiler_system.cleanup()

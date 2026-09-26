"""
Quarantined import manifest for the generalized family.

Every symbol the family still consumes from the generalized compilers passes
through this single module, so the remaining coupling surface is one visible,
auditable list instead of scattered private imports.

What stays bridged and why:
    - RUNTIME HELPERS (pure hot-path functions called by emitted source):
      construction, kwargs assembly, creation reuse, and registration. These
      are stable, battle-tested, and shared verbatim; duplicating them would
      fork hot-path semantics for zero benefit.
    - TRANSIENT SOURCE BUILDER: a pure function of the transient schema
      (call-mode + dependency-index arrays). Identity-free by construction;
      owning it would mean transcribing arg-ref tables, not design.
    - The override lane is no longer bridged: override melds run
      `SitePlanOverrideRuntime` (shared_assets), which imports the
      no-overrides helpers directly (2026-09-26).

What the family owns outright (NOT bridged):
    - step-plan no-overrides source emission (row-driven, factory-direct)
    - executor bindings construction for both lanes
    - runtime step rows (slotted) replacing SimpleNamespace hydration

Promotion note:
    When the generalized family is retired, the bridged runtime helpers and
    emitters should move into `shared_assets/` and this module should shrink
    to nothing.
"""

# --- no-overrides lane: runtime helpers called by emitted source -----------
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_no_overrides_codegen_executor_source as build_transient_no_overrides_source,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _construct_spell_instance as construct_spell_instance,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _get_existing_creation as get_existing_creation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _normalize_transient_schema as normalize_transient_schema,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _raise_meld_construction_error as raise_meld_construction_error,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _register_spell_instance as register_spell_instance,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _register_spell_instance_prebound as register_spell_instance_prebound,
)

# --- shared planner data labels ---------------------------------------------
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanTargetKind,
)

__all__ = [
    "SpellGeneralizedCodegenPlanTargetKind",
    "build_transient_no_overrides_source",
    "construct_spell_instance",
    "get_existing_creation",
    "normalize_transient_schema",
    "raise_meld_construction_error",
    "register_spell_instance",
    "register_spell_instance_prebound",
]

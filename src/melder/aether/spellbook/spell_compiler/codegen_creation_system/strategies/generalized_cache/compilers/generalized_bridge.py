"""
Quarantined import manifest for the generalized_cache family.

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
    - OVERRIDES SHAPE EMITTER + TARGET PREFILTER: row-driven public emission
      seams plus the path-registry target prefilter they depend on.

What the family owns outright (NOT bridged):
    - step-plan no-overrides source emission (row-driven, factory-direct)
    - executor bindings construction for both lanes
    - the override runtime orchestration (shape dispatch, payload split,
      socket grouping, process-wide shape caches)
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

# --- overrides lane: runtime helpers + row-driven emission seams ------------
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _EMPTY_OVERRIDE_VALUES as EMPTY_OVERRIDE_VALUES,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _MISSING as MISSING,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _build_kwargs_with_overrides as build_kwargs_with_overrides,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _build_step_override_targets as build_step_override_targets,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _build_step_override_values as build_step_override_values,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _construct_spell_instance_with_overrides as construct_spell_instance_with_overrides,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _invoke_spell_with_kwargs as invoke_spell_with_kwargs,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _raise_override_on_existing_instance as raise_override_on_existing_instance,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    build_overrides_codegen_creation_step_target_counts_from_rows,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    emit_overrides_codegen_creation_executor_shape_source,
)

# --- override targeting artifact (generalized lane shape) -------------------
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)

# --- shared planner data labels ---------------------------------------------
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanTargetKind,
)

__all__ = [
    "EMPTY_OVERRIDE_VALUES",
    "MISSING",
    "SpellGeneralizedCodegenPlanTargetKind",
    "SpellOverrideTargetingCodegenCreation",
    "build_kwargs_with_overrides",
    "build_overrides_codegen_creation_step_target_counts_from_rows",
    "build_step_override_targets",
    "build_step_override_values",
    "build_transient_no_overrides_source",
    "construct_spell_instance",
    "construct_spell_instance_with_overrides",
    "emit_overrides_codegen_creation_executor_shape_source",
    "get_existing_creation",
    "invoke_spell_with_kwargs",
    "normalize_transient_schema",
    "raise_meld_construction_error",
    "raise_override_on_existing_instance",
    "register_spell_instance",
    "register_spell_instance_prebound",
]

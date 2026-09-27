"""R2: retire the old normal emitters of the generalized and many_only families (owner-approved, 2026-09-26).

Usage: python apply_r2_edits.py <tree_root> [--check]

Removes, by AST, the top-level symbols (and two helper methods) that r2_reach.py found unreachable from live code,
then prunes the imports those removals orphaned (names used before, unused after; a multi-name import keeps its
other names). Anchored edits rewrite module docstrings for what remains, drop the library's dead re-exports and
lift the many_only executor signature into the manifest module. DELETES lists modules the caller removes. Every
anchor must match exactly once and every named symbol must exist, or nothing is written.
Engine: ../s3_staging/apply_s3b1_edits.py (_apply_one).
"""

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

CCS = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/"
GEN = CCS + "strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py"
MAN = CCS + "strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py"
LIB = CCS + "strategies/generalized/compilers/generalized_runtime_library.py"
MO = CCS + "strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py"
MOM = CCS + "strategies/many_only/manifest/many_only_manifest.py"
MOH = CCS + "strategies/many_only/many_only_codegen_creation_helpers.py"
ECC = "src/melder/aether/spellbook/spell_compiler/executor_code_cache.py"
DELETES = [CCS + "strategies/many_only/steps/many_only_no_overrides_codegen_creation_step.py"]

REMOVE = {
    GEN: [
        "_TRANSIENT_SCHEMA_SEQUENCE_FIELDS", "compile_no_overrides_codegen_creation_executor",
        "compile_no_overrides_codegen_creation_executor_from_plan", "_compile_no_overrides_executor_from_entry_inputs",
        "_compile_no_overrides_executor_from_steps", "_normalize_transient_schema", "_resolve_root_instance_key",
        "_supports_transient_unrolled_plan", "_compile_emitted_no_overrides_executor", "_inlinable_common_shape",
        "_emit_construct_instance", "_build_step_plan_executor_source", "_append_step_creations_target_source",
        "_all_steps_inlinable", "_instance_index_by_key", "_append_step_result_store", "_append_step_resolution_source",
        "_append_step_register_source", "_build_step_executor_namespace", "_select_creations_for_target_kind",
        "_get_existing_creation", "_build_no_overrides_codegen_executor_source", "_build_unrolled_call_expression",
        "_build_unrolled_call_arg_refs", "_build_executor_namespace", "_resolve_transient_targets",
    ],
    MAN: [
        "EXECUTOR_NAME", "_STEP_FACTORY_SOURCE_NAME", "_TRANSIENT_FACTORY_SOURCE_NAME", "_STEP_BINDING_NAMES",
        "_TRANSIENT_STATIC_NAMESPACE", "_TRANSIENT_SCHEMA_SEQUENCE_FIELDS", "hydrate_no_overrides_executor",
        "emit_step_plan_source", "_build_transient_bindings", "_rows_support_transient",
    ],
    MO: [
        "_MISSING", "_TRANSIENT_SCHEMA_SEQUENCE_FIELDS", "ManyOnlyCodegenPlanTargetKind",
        "compile_no_overrides_codegen_creation_executor", "compile_no_overrides_codegen_creation_executor_from_plan",
        "_compile_no_overrides_executor_from_entry_inputs", "_compile_no_overrides_executor_from_steps",
        "_normalize_transient_schema", "_compile_emitted_no_overrides_executor", "_inlinable_common_shape",
        "_raise_meld_construction_error", "_emit_construct_instance", "_build_step_plan_executor_source",
        "_append_step_resolution_source", "_build_step_executor_namespace", "_construct_spell_instance",
        "_build_kwargs_no_overrides", "_build_no_overrides_codegen_executor_source", "_build_unrolled_call_expression",
        "_build_unrolled_call_arg_refs", "_build_executor_namespace", "_resolve_transient_targets",
    ],
    MOH: ["ManyOnlyCodegenCreationHelpers.freeze_value", "ManyOnlyCodegenCreationHelpers.build_override_step_row"],
}

GEN_DOC = '''"""
Runtime helpers shared by the generalized family's plans.

What remains of the generalized no-overrides compiler after normal melds moved to the site-plan
runtime (S2b-2) and the old step and transient emitters were retired (R2, 2026-09-26); the module
path is kept so no importer moves:
    - `_hydrate_steps_from_rows`: Codegen IR row hydration (manifest rows plus live spells ->
      step views), read by the hydrator and the site-plan lowering.
    - `_construct_spell_instance` / `_build_kwargs_no_overrides`: the generic construction helper
      plans call for steps they do not emit as a direct call.
    - `_raise_meld_construction_error`: the shared construction-failure raise.
    - `_register_spell_instance` / `_register_spell_instance_prebound`: registration helpers the
      opt-in singleton specializer's emitted source calls.
"""

'''

MAN_DOC_OLD = '''"""
Family-owned no-overrides lane compiler for the generalized family.

This module owns the no-overrides lane end to end:
    - row-driven source emission (manifest rows in, factory source out;
      no live spells touched during emission),
    - executor bindings construction (flat arrays + slotted runtime rows),
    - hydration through the process-wide executor factory cache (one compile
      plus one exec per source shape per process; one factory call per spell).

Emission semantics are a faithful port of the legacy step-plan emitter with
one deliberate hot-path improvement: reuse reads are inlined as direct
'''
MAN_DOC_NEW = '''"""
Opt-in singleton specializer and shared row helpers for the generalized family.

Normal melds run the site-plan runtime's normal plan since S2b-2; the row-driven step and
transient emitters this module owned were retired on 2026-09-26 (R2). What remains:
    - the opt-in singleton warm-tail specializer
      (`generalized_singleton_specialization_enabled`): `select_specializable_step_indexes`,
      `emit_specialized_step_plan_source` and `build_specialized_no_overrides_executor`
      (row-driven source, hydrated through the process-wide executor factory cache; it deopts
      to the site-plan normal plan);
    - row helpers the hydrator and the specializer share: `resolve_contract_payload_rows`,
      `resolve_root_instance_key_from_rows`, `row_inlinable_common_shape` and the positional
      prefix helpers (`positional_dependency_names`, P1).

Emission semantics are a faithful port of the legacy step-plan emitter with
one deliberate hot-path improvement: reuse reads are inlined as direct
'''

MAN_IMPORT_OLD = '''    SpellGeneralizedCodegenPlanTargetKind,
    build_transient_no_overrides_source,
    construct_spell_instance,
    normalize_transient_schema,
    raise_meld_construction_error,
'''
MAN_IMPORT_NEW = '''    SpellGeneralizedCodegenPlanTargetKind,
    construct_spell_instance,
    raise_meld_construction_error,
'''

LIB_DOC_OLD = '''    - RUNTIME HELPERS (pure hot-path functions called by emitted source):
      construction, kwargs assembly, creation reuse, and registration. These
      are stable, battle-tested, and shared verbatim; duplicating them would
      fork hot-path semantics for zero benefit.
    - TRANSIENT SOURCE BUILDER: a pure function of the transient schema
      (call-mode + dependency-index arrays). Identity-free by construction;
      owning it would mean transcribing arg-ref tables, not design.
'''
LIB_DOC_NEW = '''    - RUNTIME HELPERS (pure hot-path functions called by the opt-in
      specializer's emitted source): construction, the construction-failure
      raise and registration. These are stable, battle-tested, and shared
      verbatim; duplicating them would fork hot-path semantics for zero benefit.
    - The transient source builder, creation-reuse helper and schema
      normalizer went with the old normal emitters (R2, 2026-09-26).
'''
LIB_OWNED_OLD = '''What the family owns outright (NOT bridged):
    - step-plan no-overrides source emission (row-driven, factory-direct)
    - executor bindings construction for both lanes
    - runtime step rows (slotted) replacing SimpleNamespace hydration
'''
LIB_OWNED_NEW = '''What the family owns outright (NOT bridged):
    - the opt-in specializer's source emission (row-driven, factory-direct)
    - its executor bindings construction
    - runtime step rows (slotted) replacing SimpleNamespace hydration
'''
LIB_IMPORTS = [
    ('''from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_no_overrides_codegen_executor_source as build_transient_no_overrides_source,
)
''', ""),
    ('''from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _get_existing_creation as get_existing_creation,
)
''', ""),
    ('''from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _normalize_transient_schema as normalize_transient_schema,
)
''', ""),
    ('''    "build_transient_no_overrides_source",
''', ""),
    ('''    "get_existing_creation",
''', ""),
    ('''    "normalize_transient_schema",
''', ""),
]

MO_DOC = '''"""
Codegen IR helpers of the many_only family.

What remains of the many_only no-overrides compiler after normal melds moved to the site-plan
runtime (S2b-2) and the old step and transient emitters were retired (R2, 2026-09-26); the module
path is kept so no importer moves:
    - `ManyOnlyCodegenPlanCallMode`: the call-mode labels of the Phase-10 transient schema;
    - `_build_many_only_unrolled_schema_from_plan`: the manifest's transient schema (data only);
    - `_hydrate_steps_from_rows` / `_resolve_root_instance_key`: manifest row hydration, read by
      the hydrator.
"""

'''

MOM_DOC_OLD = '''Bridging note:
    The unrolled-schema builder and the lane signature builders are bridged
    from the many_only compilers/steps; they are pure functions of plan data.
    Lift them into family-public seams when the legacy eager steps are
    retired.
'''
MOM_DOC_NEW = '''Bridging note:
    The unrolled-schema builder is bridged from the many_only compiler; it is a
    pure function of plan data. The no-overrides executor signature is built
    here (`build_many_only_executor_signature`), lifted from the retired eager
    no-overrides step (R2, 2026-09-26).
'''
MOM_IMPORT_OLD = '''from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step import (
    ManyOnlyNoOverridesCodegenCreationStep,
)
'''
MOM_IMPORT_NEW = '''from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (
    ManyOnlyCodegenCreationHelpers,
)
'''
MOM_CALL_OLD = '''            "executor_signature": (
                ManyOnlyNoOverridesCodegenCreationStep._build_executor_signature(
                    no_overrides_plan=no_overrides_plan,
                )
            ),
'''
MOM_CALL_NEW = '''            "executor_signature": build_many_only_executor_signature(
                no_overrides_plan
            ),
'''
MOM_FUNC_ANCHOR = '''def _build_many_only_no_overrides_row(step: Any) -> Dict[str, Any]:
'''
MOM_FUNC_NEW = '''def build_many_only_executor_signature(no_overrides_plan: Any) -> str:
    """
    Build the deterministic signature of one many_only no-overrides lane.

    Contract:
        - A pure hash of plan data: the root spell id and instance key, one
          signature row per step, the step call modes, the root step index and
          the per-step disposal flags, in that order - the parts the retired
          eager step hashed (lifted from
          `ManyOnlyNoOverridesCodegenCreationStep._build_executor_signature`,
          R2, 2026-09-26), so manifests keep their signature values.

    Args:
        no_overrides_plan:
            The many_only no-overrides lane plan.

    Returns:
        str: The signature digest.
    """
    step_signature_rows = tuple(
        ManyOnlyCodegenCreationHelpers.build_no_overrides_step_signature_row(
            step
        )
        for step in no_overrides_plan.steps
    )
    root_instance_key = ManyOnlyCodegenCreationHelpers.normalize_instance_key(
        no_overrides_plan.root_instance_key
    )
    return ManyOnlyCodegenCreationHelpers.hash_signature(
        no_overrides_plan.root_spell_id,
        root_instance_key,
        step_signature_rows,
        no_overrides_plan.step_call_modes,
        no_overrides_plan.root_step_index,
        no_overrides_plan.step_has_disposal_methods,
    )


def _build_many_only_no_overrides_row(step: Any) -> Dict[str, Any]:
'''
MOM_ALL_OLD = '''    "build_many_only_manifest",
'''
MOM_ALL_NEW = '''    "build_many_only_executor_signature",
    "build_many_only_manifest",
'''

ECC_OLD = '''This module owns one process-wide, bounded cache keyed on the SHA-256 of the
emitted source. It is consumed by both codegen-creation compile chokepoints:
``_compile_emitted_no_overrides_executor`` (no-overrides lane) and
``compile_overrides_codegen_creation_executor_code_object`` (overrides lane).
'''
ECC_NEW = '''This module owns one process-wide, bounded cache keyed on the SHA-256 of the
emitted source. It is consumed by every codegen-creation compile chokepoint:
the site-plan runtime (normal and override plans), the creation-runtime door
compiler and the solo compilers.
'''

MAN_DOCFIX = [
    ('''        - One tuple per row, in row order, for `emit_step_plan_source` and
          `emit_specialized_step_plan_source`.
''', '''        - One tuple per row, in row order, for
          `emit_specialized_step_plan_source`.
'''),
    ('''        non-captured step exactly as the generic emitter does.
''', '''        non-captured step through the shared per-step emitters, exactly as
        the retired generic step emitter did (R2, 2026-09-26).
'''),
    ('''            Optional per-row positional-dependency prefixes (see
            `emit_step_plan_source`); non-captured steps receive theirs so
            they compile exactly as in the generic body.
''', '''            Optional per-row positional-dependency prefixes (see
            `positional_dependency_names`); non-captured steps receive theirs
            so their direct calls pass the P1-safe positional prefix.
'''),
    ('''    # Mirror the generic emitter's locals-mode decision exactly so the
    # non-captured steps compile identically in both bodies.
''', '''    # Locals mode follows the rule the retired generic step emitter used (the
    # root key is a step and every row's dependency keys resolve to steps), so
    # non-captured steps compile exactly as they did before R2.
'''),
]

EDITS = {
    GEN: [("prepend", GEN_DOC)],
    MAN: [("replace", MAN_DOC_OLD, MAN_DOC_NEW), ("replace", MAN_IMPORT_OLD, MAN_IMPORT_NEW)]
         + [("replace", old, new) for old, new in MAN_DOCFIX],
    LIB: [("replace", LIB_DOC_OLD, LIB_DOC_NEW), ("replace", LIB_OWNED_OLD, LIB_OWNED_NEW)]
         + [("replace", old, new) for old, new in LIB_IMPORTS],
    MO: [("prepend", MO_DOC)],
    MOM: [("replace", MOM_DOC_OLD, MOM_DOC_NEW), ("replace", MOM_IMPORT_OLD, MOM_IMPORT_NEW),
          ("replace", MOM_CALL_OLD, MOM_CALL_NEW), ("replace", MOM_FUNC_ANCHOR, MOM_FUNC_NEW),
          ("replace", MOM_ALL_OLD, MOM_ALL_NEW)],
    MOH: [],
    ECC: [("replace", ECC_OLD, ECC_NEW)],
}


def _remove_symbols(data: str, names: list, rel: str) -> str:
    """Remove named top-level defs/classes/assignments and `Class.method` members; every name must exist."""
    tree = ast.parse(data)
    lines = data.splitlines(keepends=True)
    drop = set()
    found = set()
    for node in tree.body:
        targets = []
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            targets = [node.name]
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = [t.id for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
                       if isinstance(t, ast.Name)]
        for name in targets:
            if name in names:
                found.add(name)
                start = min([d.lineno for d in getattr(node, "decorator_list", [])] + [node.lineno])
                drop.update(range(start - 1, node.end_lineno))
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                qual = f"{node.name}.{getattr(member, 'name', '')}"
                if isinstance(member, ast.FunctionDef) and qual in names:
                    found.add(qual)
                    start = min([d.lineno for d in member.decorator_list] + [member.lineno])
                    drop.update(range(start - 1, member.end_lineno))
    missing = set(names) - found
    if missing:
        raise SystemExit(f"{rel}: symbols not found: {sorted(missing)}")
    text = "".join(line for index, line in enumerate(lines) if index not in drop)
    return _collapse_blank_lines(text)


def _collapse_blank_lines(text: str) -> str:
    """Collapse runs of more than two blank lines, including between class members (more than one)."""
    nl = "\r\n" if "\r\n" in text else "\n"
    while nl * 4 in text:
        text = text.replace(nl * 4, nl * 3)
    return text


def _used_names(data: str) -> set:
    """Names read anywhere in the module."""
    return {n.id for n in ast.walk(ast.parse(data)) if isinstance(n, ast.Name)}


def _prune_orphaned_imports(original: str, data: str, rel: str) -> str:
    """Drop imported names used in `original` and unused in `data`; keep the rest of each statement."""
    used_before = _used_names(original)
    while True:
        tree = ast.parse(data)
        used = _used_names(data)
        lines = data.splitlines(keepends=True)
        changed = False
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            bound = [(a, (a.asname or a.name).split(".")[0]) for a in node.names]
            orphans = [name for alias, name in bound if name in used_before and name not in used]
            if not orphans:
                continue
            keep = [alias for alias, name in bound if name not in orphans]
            first, last = node.lineno - 1, node.end_lineno
            nl = "\r\n" if lines[first].endswith("\r\n") else "\n"
            if not keep:
                replacement = []
            elif first + 1 == last:
                head = lines[first].split(" import ")[0]
                names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in keep)
                replacement = [f"{head} import {names}{nl}"]
            else:
                replacement = [line for line in lines[first:last]
                               if line.strip().rstrip(",").split(" as ")[-1] not in orphans]
            lines[first:last] = replacement
            data = "".join(lines)
            print(f"{rel}: pruned import {orphans}")
            changed = True
            break
        if not changed:
            return _collapse_blank_lines(data)


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one anchored edit (`prepend` adds a module docstring before the first line)."""
    if edit[0] == "prepend":
        nl = "\r\n" if "\r\n" in data else "\n"
        return edit[1].replace("\n", nl) + data
    return _apply_one(data, edit, rel)


def main() -> None:
    """Check everything, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    for rel in DELETES:
        if not (root / rel).is_file():
            raise SystemExit(f"missing file to delete: {rel}")
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        original = path.read_bytes().decode("utf-8")
        data = original
        if rel in REMOVE:
            data = _remove_symbols(data, REMOVE[rel], rel)
        for edit in edits:
            data = _apply(data, edit, rel)
        data = _prune_orphaned_imports(original, data, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETES:
        print("to delete: " + rel)


if __name__ == "__main__":
    main()

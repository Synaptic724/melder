"""Apply the S3a hydrator edits (override key-set plans) to one melder tree.

Usage: python apply_s3a_edits.py <tree_root> [--check]

Each edit replaces one exact anchored block. A block must match exactly once, in
the file's own line endings (CRLF or LF, detected per block), or the script stops
before writing anything.
"""

import pathlib
import sys

HYD = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies"
MANY_ONLY = f"{HYD}/many_only/hydration/many_only_hydrator.py"
GENERALIZED = f"{HYD}/generalized/hydration/generalized_hydrator.py"

SHARED = "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets"

MANY_ONLY_EDITS = [
    (
        """from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor,
)
""",
        f"""from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows,
    _resolve_root_instance_key,
    compile_no_overrides_codegen_creation_executor,
)
from {SHARED}.site_plan_lowering import (
    SitePlanStep,
)
from {SHARED}.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
""",
    ),
    (
        """    execute_with_overrides = _hydrate_overrides_runtime(
        overrides_payload=manifest["overrides"],
        spell=spell,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
""",
        """    execute_with_overrides = _hydrate_overrides_runtime(
        no_overrides_payload=no_overrides_payload,
        spell=spell,
        spell_lookup=spell_lookup,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
""",
    ),
    (
        '''def _hydrate_overrides_runtime(
        *,
        overrides_payload: Dict[str, Any],
        spell: Any,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Rebuild the many_only override runtime from manifest rows.

    Contract:
        - Reuses the bridged many_only finalize builder fed cached rows plus
          the live phase-5 path registry, so per-shape override executors
          still compile lazily at meld time.
    """
    spell_lookup = _resolve_spell_lookup(
        spell=spell,
        step_spell_ids=overrides_payload["step_spell_ids"],
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    path_registry = _resolve_live_path_registry(spell)
    plan_rows = list(overrides_payload["plan_rows"])
    plan_signature = coerce_manifest_sequences(
        overrides_payload["plan_signature"]
    )
    empty_shape_key = coerce_manifest_sequences(
        overrides_payload["empty_shape_key"]
    )

    baseline_executor = compile_overrides_codegen_creation_executor(
        execution_plan=None,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
    )

    finalize_step = ManyOnlyFinalizeCreationContextStep()
    return finalize_step._build_overrides_runtime(
        spell_codegen_model=_NULL_MODEL,
        overrides_plan=None,
        root_spell=spell,
        base_no_overrides_executor=inner_no_overrides_executor,
        override_targeting=override_targeting,
        plan_signature=plan_signature,
        path_registry=path_registry,
        plan_rows=plan_rows,
        override_root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
        empty_shape_key=empty_shape_key,
        baseline_executor=baseline_executor,
    )
''',
        '''def _hydrate_overrides_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell: Any,
        spell_lookup: Dict[str, Any],
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build the many_only override runtime: one compiled plan per override key set.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's own
          row hydration, so override plans and the normal lane see the same
          steps (design v2 S3a). The manifest's overrides payload is not read.
        - Returns `SitePlanOverrideRuntime.execute_with_overrides`; plans
          compile lazily per key set at meld time, and the runtime lives as
          long as the returned callable (the lazy override door holds it).

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell:
            Live root spell.
        spell_lookup:
            Live spell per step spell id (already resolved for the no-overrides
            lane).
        inner_no_overrides_executor:
            The lane's inner `(meld) -> instance` executor.

    Raises:
        RuntimeError:
            When no step carries the root instance key.

    Returns:
        Callable[..., Any]:
            `(meld, overrides) -> instance`.
    """
    rows = _hydrate_steps_from_rows(
        steps_rows=no_overrides_payload["steps_rows"],
        spell_lookup=spell_lookup,
    )
    root_instance_key = _resolve_root_instance_key(
        steps=rows,
        root_spell_id=no_overrides_payload["root_spell_id"],
    )
    if root_instance_key is None:
        raise RuntimeError(
            "many_only override runtime could not resolve the root instance key."
        )
    runtime = SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(row) for row in rows),
        root_spell=spell,
        root_instance_key=root_instance_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
    return runtime.execute_with_overrides
''',
    ),
]

GENERALIZED_EDITS = [
    (
        """from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
""",
        f"""from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows,
)
from {SHARED}.site_plan_lowering import (
    SitePlanStep,
)
from {SHARED}.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
""",
    ),
    (
        '''def _hydrate_overrides_runtime(
        *,
        overrides_payload: Dict[str, Any],
        resolver: Any,
        root_spell: Any,
) -> Callable[..., Any]:
    """
    Hydrate the family override runtime from manifest rows.
    """
    plan_rows = list(overrides_payload["plan_rows"])
    spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=overrides_payload["step_spell_ids"],
    )
    runtime_rows = build_runtime_rows(
        rows=plan_rows,
        spell_lookup=spell_lookup,
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    root_instance_key = resolve_root_instance_key_from_rows(
        rows=plan_rows,
        explicit_root_instance_key=None,
        root_spell_id=overrides_payload["root_spell_id"],
    )
    return build_overrides_execute_runtime(
        plan_rows=plan_rows,
        plan_signature=coerce_manifest_sequences(
            overrides_payload["plan_signature"]
        ),
        empty_shape_key=coerce_manifest_sequences(
            overrides_payload["empty_shape_key"]
        ),
        root_spell_id=overrides_payload["root_spell_id"],
        root_instance_key=root_instance_key,
        runtime_rows=runtime_rows,
        spell_lookup=spell_lookup,
        root_spell=root_spell,
        override_targeting=override_targeting,
        path_registry=resolver.resolve_path_registry(),
    )
''',
        '''def _hydrate_overrides_runtime(
        *,
        manifest: Dict[str, Any],
        resolver: Any,
        root_spell: Any,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build the family override runtime: one compiled plan per override key set.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's
          step-row hydration (`_hydrate_steps_from_rows`), which also resolves
          contract payload references to live values where rows carry them, so
          override plans and the normal lane see the same steps (design v2
          S3a). The manifest's overrides payload is not read.
        - Returns `SitePlanOverrideRuntime.execute_with_overrides`; plans
          compile lazily per key set at meld time, and the runtime lives as
          long as the returned callable (the lazy override door holds it).

    Args:
        manifest:
            Validated family manifest.
        resolver:
            Binding resolver for live spell identity.
        root_spell:
            Live root spell.
        inner_no_overrides_executor:
            The lane's inner `(meld) -> instance` executor.

    Raises:
        RuntimeError:
            When rows or the root instance key cannot be resolved.

    Returns:
        Callable[..., Any]:
            `(meld, overrides) -> instance`.
    """
    no_overrides_payload = manifest["no_overrides"]
    steps_rows = no_overrides_payload["steps_rows"]
    spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    rows = _hydrate_steps_from_rows(
        steps_rows=steps_rows,
        spell_lookup=spell_lookup,
    )
    root_instance_key = resolve_root_instance_key_from_rows(
        rows=steps_rows,
        explicit_root_instance_key=no_overrides_payload["root_instance_key"],
        root_spell_id=no_overrides_payload["root_spell_id"],
    )
    runtime = SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_generalized_row(row) for row in rows),
        root_spell=root_spell,
        root_instance_key=root_instance_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
    return runtime.execute_with_overrides
''',
    ),
    (
        """            execute_with_overrides = _hydrate_overrides_runtime(
                overrides_payload=manifest["overrides"],
                resolver=resolver,
                root_spell=root_spell,
            )
""",
        """            execute_with_overrides = _hydrate_overrides_runtime(
                manifest=manifest,
                resolver=resolver,
                root_spell=root_spell,
                inner_no_overrides_executor=inner_no_overrides_executor,
            )
""",
    ),
]


def _apply(path: pathlib.Path, edits: list, check: bool) -> None:
    """Replace each anchored block once, in the file's own line endings."""
    data = path.read_bytes().decode("utf-8")
    for old, new in edits:
        replaced = False
        for nl in ("\r\n", "\n"):
            old_nl = old.replace("\n", nl)
            count = data.count(old_nl)
            if count == 1:
                data = data.replace(old_nl, new.replace("\n", nl))
                replaced = True
                break
            if count > 1:
                raise SystemExit(f"{path}: anchor matched {count} times: {old[:70]!r}")
        if not replaced:
            raise SystemExit(f"{path}: anchor not found: {old[:70]!r}")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


def main() -> None:
    """Apply (or check) every edit against the tree given on the command line."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    _apply(root / MANY_ONLY, MANY_ONLY_EDITS, check=True)
    _apply(root / GENERALIZED, GENERALIZED_EDITS, check=True)
    if check:
        return
    _apply(root / MANY_ONLY, MANY_ONLY_EDITS, check=False)
    _apply(root / GENERALIZED, GENERALIZED_EDITS, check=False)


if __name__ == "__main__":
    main()

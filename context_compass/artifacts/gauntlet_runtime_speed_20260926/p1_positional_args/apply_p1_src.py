"""melder_2 apply script P1 (source): positional dependency prefix in the generalized no-overrides step emitter.

Usage: python apply_p1_src.py --root <repo root> (--check | --apply)
Anchored edits on LF-normalized text; the file's CRLF convention is restored on write. Every anchor must match
exactly once or nothing is written.
"""
import argparse, pathlib, sys

REL = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py"

EDITS = []

def edit(old, new, count=1):
    EDITS.append((old, new, count))

# E1 import
edit("from typing import Any, Callable, Dict, Optional, Sequence, Tuple\n",
     "from types import FunctionType\nfrom typing import Any, Callable, Dict, Optional, Sequence, Tuple\n")

# E2 hydrate docstring
edit("""        - Emission is a pure function of rows/schema; live spells are touched
          only by bindings construction.
""", """        - Emission is a pure function of rows/schema plus each step's
          positional-dependency prefix. Live spells are touched only by
          bindings construction and by `rows_positional_dependency_names`,
          which reads each step target's construction path, never its
          annotations.
""")

# E3 hydrate emit call
edit("""    inner_source = emit_step_plan_source(
        rows=rows,
        root_instance_key=resolved_root_instance_key,
    )
""", """    inner_source = emit_step_plan_source(
        rows=rows,
        root_instance_key=resolved_root_instance_key,
        positional_dependency_names=rows_positional_dependency_names(
            rows=rows,
            spell_lookup=spell_lookup,
        ),
    )
""")

# E4 emit_step_plan_source signature + docstring head
edit("""def emit_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
        root_instance_key: Tuple[str, Any],
) -> str:
    \"\"\"
    Emit the inner no-overrides step-plan executor source from manifest rows.

    Contract:
        - Pure function of row data plus the root key's POSITION (the emitted
          source embeds step indices only, never identity values, so factory
          sharing across same-shape spells is preserved).
""", """def emit_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
        root_instance_key: Tuple[str, Any],
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]] = None,
) -> str:
    \"\"\"
    Emit the inner no-overrides step-plan executor source from manifest rows.

    Contract:
        - Pure function of row data plus the root key's POSITION (the emitted
          source embeds step indices only, never identity values, so factory
          sharing across same-shape spells is preserved) and, when supplied,
          each step's positional-dependency prefix.
        - POSITIONAL PREFIX: `positional_dependency_names` holds one tuple per
          row (built by `rows_positional_dependency_names`). A step passes the
          named dependency values positionally, in that order, ahead of its
          remaining keyword arguments; every value still binds to the
          parameter it was resolved for. `None` keeps every argument keyword,
          which is what a caller without live spells gets. A tuple whose
          length differs from `rows` raises RuntimeError.
""")

# E5 emit_step_plan_source length validation (anchored on its unique docstring tail)
edit("""        - DICT MODE: any generic-constructor step falls back to the
          `instance_results` dict so `_construct_spell_instance` keeps its
          full recipe surface.
    \"\"\"
    key_to_step_index: Dict[Any, int] = {}
""", """        - DICT MODE: any generic-constructor step falls back to the
          `instance_results` dict so `_construct_spell_instance` keeps its
          full recipe surface.
    \"\"\"
    _require_positional_names_per_row(
        rows=rows,
        positional_dependency_names=positional_dependency_names,
    )
    key_to_step_index: Dict[Any, int] = {}
""")

# E6 emit_step_plan_source step loop
edit("""    lines.append(f"def {EXECUTOR_NAME}(meld):")
    if not locals_mode:
        lines.append("    instance_results = {}")
    for step_index, row in enumerate(rows):
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
        )
""", """    lines.append(f"def {EXECUTOR_NAME}(meld):")
    if not locals_mode:
        lines.append("    instance_results = {}")
    for step_index, row in enumerate(rows):
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
            positional_names=(
                positional_dependency_names[step_index]
                if positional_dependency_names is not None
                else ()
            ),
        )
""")

# E7 _append_step_resolution_source signature + docstring
edit("""def _append_step_resolution_source(
        *,
        lines: list,
        step_index: int,
        row: Dict[str, Any],
        key_to_step_index: Optional[Dict[Any, int]] = None,
) -> None:
    \"\"\"
    Append emitted source for one step from its manifest row.

    Contract:
        - When `key_to_step_index` is supplied (locals mode), step results
          are plain locals: no `instance_results` stores are emitted and
          inlined constructor dependencies compile to direct local loads.
    \"\"\"
""", """def _append_step_resolution_source(
        *,
        lines: list,
        step_index: int,
        row: Dict[str, Any],
        key_to_step_index: Optional[Dict[Any, int]] = None,
        positional_names: Tuple[str, ...] = (),
) -> None:
    \"\"\"
    Append emitted source for one step from its manifest row.

    Contract:
        - When `key_to_step_index` is supplied (locals mode), step results
          are plain locals: no `instance_results` stores are emitted and
          inlined constructor dependencies compile to direct local loads.
        - `positional_names` is the step's positional-dependency prefix; it is
          forwarded unchanged to every constructor emission for this step.
    \"\"\"
""")

# E9 _emit_construct_instance signature + docstring
edit("""        key_to_step_index: Optional[Dict[Any, int]] = None,
        row: Optional[Dict[str, Any]] = None,
) -> None:
    \"\"\"
    Append construction source for one step at `indent`.
""", """        key_to_step_index: Optional[Dict[Any, int]] = None,
        row: Optional[Dict[str, Any]] = None,
        positional_names: Tuple[str, ...] = (),
) -> None:
    \"\"\"
    Append construction source for one step at `indent`.
""")
edit("""          position instead - visible only to constructors introspecting
          `**kwargs` insertion order for payload-overridden names.
    \"\"\"
    if inlinable_params is None:
""", """          position instead - visible only to constructors introspecting
          `**kwargs` insertion order for payload-overridden names.
        - Dependency values named in `positional_names` compile to leading
          positional arguments in that order, which is the target's own
          parameter order (see `positional_dependency_names`); every other
          dependency stays a keyword. A step with a `*positional_N` payload
          splat ignores the prefix, because the splat already owns the
          leading positions. Why: on CPython 3.14 a positional class call
          takes the interpreter's specialized allocate-and-init path, while a
          keyword call builds a kwargs dict and goes through the generic
          `type.__call__` route (3.14t: 77 ns vs 170 ns for a two-parameter
          class).

    Raises:
        RuntimeError:
            When a `positional_names` entry is not an emitted dependency of
            this step.
    \"\"\"
    if inlinable_params is None:
""")

# E10 _emit_construct_instance emission body
edit("""        # Flat cursor over the row's flattened dependency-key tuple: single-dep
        # NON-collection params compile to one scalar reference; collection-DI
        # params compile to an order-preserving list literal REGARDLESS of
        # member count (parity with the generic `_build_kwargs_no_overrides`:
        # collection socket -> list even with 1 member; >=2 deps -> list).
        flat_dep_cursor = 0
""", """        # Signature-order prefix first (positional), then every other
        # dependency by keyword, then payload keywords. A payload splat owns
        # the leading positions, so it disables the prefix.
        leading_names = positional_names if positional is None else ()
        leading_values: Dict[str, str] = {}
        keyword_lines: list = []
        # Flat cursor over the row's flattened dependency-key tuple: single-dep
        # NON-collection params compile to one scalar reference; collection-DI
        # params compile to an order-preserving list literal REGARDLESS of
        # member count (parity with the generic `_build_kwargs_no_overrides`:
        # collection socket -> list even with 1 member; >=2 deps -> list).
        flat_dep_cursor = 0
""")
edit("""                value_expression = "[" + ", ".join(references) + "]"
            lines.append(
                f"{indent}        {param_name}={value_expression},"
            )
        for payload_index, payload_name in enumerate(payload_names):
""", """                value_expression = "[" + ", ".join(references) + "]"
            if param_name in leading_names:
                leading_values[param_name] = value_expression
            else:
                keyword_lines.append(
                    f"{indent}        {param_name}={value_expression},"
                )
        for leading_name in leading_names:
            if leading_name not in leading_values:
                raise RuntimeError(
                    f"Positional prefix name '{leading_name}' is not an "
                    f"emitted dependency of step {step_index}."
                )
            lines.append(f"{indent}        {leading_values[leading_name]},")
        lines.extend(keyword_lines)
        for payload_index, payload_name in enumerate(payload_names):
""")

# E11 new helpers, placed right before _row_contract_call_extras
edit("""def _row_contract_call_extras(
""", '''def positional_dependency_names(
        *,
        target: Any,
        dependency_param_names: Tuple[str, ...],
) -> Tuple[str, ...]:
    """
    Return the leading dependency parameters `target` receives by position.

    Purpose:
        Let emitted constructor calls pass dependency values positionally.
        On CPython 3.14 a positional class call takes the interpreter's
        specialized allocate-and-init path; a keyword call builds a kwargs
        dict and runs the generic `type.__call__` route (measured on 3.14t:
        77 ns vs 170 ns for a two-parameter class).

    Contract:
        - Qualifies only plain construction: `target` is a class whose
          metaclass keeps `type.__call__`, whose `__new__` is
          `object.__new__` (so it ignores the arguments), and whose
          `__init__` is a plain Python function. Anything else returns `()`
          and the step keeps its keyword call.
        - Reads parameter order from `__init__.__code__` - the function that
          actually receives the arguments - so a positional value binds to
          exactly the parameter the keyword would have named. Annotations,
          `__signature__` and wrapper metadata are never consulted or
          evaluated (a TYPE_CHECKING-only annotation cannot raise here).
        - Returns the longest prefix of the positional parameters (after
          `self`, positional-only included) whose every name is in
          `dependency_param_names`. The first parameter that is not a
          dependency - a default, an unresolved input, a payload name -
          ends the prefix, so no value can shift into another parameter.
          Keyword-only parameters are never in the prefix.
        - Pure: attribute reads only, no side effects.

    Args:
        target:
            The step's construction target (`Spell.spell`).
        dependency_param_names:
            Parameter names the step fills from resolved dependencies, as
            returned by `row_inlinable_common_shape`.

    Returns:
        Tuple[str, ...]: Prefix names in the target's parameter order; empty
        when the target does not qualify or its first parameter is not a
        dependency.
    """
    if not dependency_param_names or not isinstance(target, type):
        return ()
    if type(target).__call__ is not type.__call__:
        return ()
    if target.__new__ is not object.__new__:
        return ()
    initializer = target.__init__
    if type(initializer) is not FunctionType:
        return ()
    code = initializer.__code__
    prefix = []
    for parameter_name in code.co_varnames[1:code.co_argcount]:
        if parameter_name not in dependency_param_names:
            break
        prefix.append(parameter_name)
    return tuple(prefix)


def rows_positional_dependency_names(
        *,
        rows: Sequence[Dict[str, Any]],
        spell_lookup: Dict[str, Any],
) -> Tuple[Tuple[str, ...], ...]:
    """
    Compute each row's positional-dependency prefix from its live target.

    Contract:
        - One tuple per row, in row order, for `emit_step_plan_source` and
          `emit_specialized_step_plan_source`.
        - Non-inlinable rows (generic constructor, existing creation), rows
          with no dependency parameters and rows whose call carries a
          `*positional_N` payload splat get `()` without a spell lookup.
        - Every other row gets `positional_dependency_names` over its
          `Spell.spell`, with the dependency names from
          `row_inlinable_common_shape`.
        - Expects RESOLVED rows (`resolve_contract_payload_rows`), the same
          rows emission receives.

    Args:
        rows:
            Resolved manifest step rows for the no-overrides lane.
        spell_lookup:
            Spell id -> live Spell for every step row.

    Returns:
        Tuple[Tuple[str, ...], ...]: Positional prefix names per row.

    Raises:
        RuntimeError:
            When an inlinable row's spell is missing from `spell_lookup`.
    """
    names_by_row = []
    for row in rows:
        inlinable_params = row_inlinable_common_shape(row)
        if not inlinable_params:
            names_by_row.append(())
            continue
        _payload_names, positional = _row_contract_call_extras(row)
        if positional is not None:
            names_by_row.append(())
            continue
        spell = spell_lookup.get(row["spell_id"])
        if spell is None:
            raise RuntimeError(
                "Cannot compute the positional dependency prefix: spell "
                f"'{row['spell_id']}' is missing from spell_lookup."
            )
        names_by_row.append(positional_dependency_names(
            target=spell.spell,
            dependency_param_names=tuple(
                param_name for param_name, _keys in inlinable_params
            ),
        ))
    return tuple(names_by_row)


def _require_positional_names_per_row(
        *,
        rows: Sequence[Dict[str, Any]],
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]],
) -> None:
    """
    Fail fast when a positional-prefix tuple does not match the rows.

    Raises:
        RuntimeError:
            When `positional_dependency_names` is supplied with a length
            other than `len(rows)`.
    """
    if (
            positional_dependency_names is not None
            and len(positional_dependency_names) != len(rows)
    ):
        raise RuntimeError(
            "positional_dependency_names must hold exactly one entry per "
            f"row: {len(positional_dependency_names)} entries for "
            f"{len(rows)} rows."
        )


def _row_contract_call_extras(
''')

# E12 specialized emitter signature + validation + loop
edit("""def emit_specialized_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
        captured_step_indexes: Tuple[int, ...],
        root_instance_key: Tuple[str, Any],
) -> str:
""", """def emit_specialized_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
        captured_step_indexes: Tuple[int, ...],
        root_instance_key: Tuple[str, Any],
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]] = None,
) -> str:
""")
edit("""        root_instance_key:
            Resolved root instance key for the lane.

    Returns:
        str: Identity-free specialized executor source (one `def` statement).

    Raises:
        RuntimeError:
            When the capture set is empty or references a non-`unique` row.
    \"\"\"
""", """        root_instance_key:
            Resolved root instance key for the lane.
        positional_dependency_names:
            Optional per-row positional-dependency prefixes (see
            `emit_step_plan_source`); non-captured steps receive theirs so
            they compile exactly as in the generic body.

    Returns:
        str: Identity-free specialized executor source (one `def` statement).

    Raises:
        RuntimeError:
            When the capture set is empty or references a non-`unique` row,
            or when `positional_dependency_names` does not hold one entry per
            row.
    \"\"\"
    _require_positional_names_per_row(
        rows=rows,
        positional_dependency_names=positional_dependency_names,
    )
""")
edit("""    for step_index, row in enumerate(rows):
        if step_index in captured_set:
            continue
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
        )
""", """    for step_index, row in enumerate(rows):
        if step_index in captured_set:
            continue
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
            positional_names=(
                positional_dependency_names[step_index]
                if positional_dependency_names is not None
                else ()
            ),
        )
""")
edit("""    inner_source = emit_specialized_step_plan_source(
        rows=rows,
        captured_step_indexes=captured_step_indexes,
        root_instance_key=resolved_root_instance_key,
    )
""", """    inner_source = emit_specialized_step_plan_source(
        rows=rows,
        captured_step_indexes=captured_step_indexes,
        root_instance_key=resolved_root_instance_key,
        positional_dependency_names=rows_positional_dependency_names(
            rows=rows,
            spell_lookup=spell_lookup,
        ),
    )
""")

def apply_text(text):
    for old, new, count in EDITS:
        found = text.count(old)
        if found != count:
            raise SystemExit(f"anchor count {found} != {count}:\n{old[:200]}")
        text = text.replace(old, new, count)
    # E8: forward positional_names through all five _emit_construct_instance calls in _append_step_resolution_source
    start = text.index("def _append_step_resolution_source(")
    end = text.index("def _append_creations_target_source(")
    body = text[start:end]
    a = "            row=row,\n        )\n"
    b = "        row=row,\n    )\n"
    n_a, n_b = body.count(a), body.count(b)
    if (n_a, n_b) != (4, 1):
        raise SystemExit(f"call-site counts {(n_a, n_b)} != (4, 1)")
    body = body.replace(a, "            row=row,\n            positional_names=positional_names,\n        )\n")
    body = body.replace(b, "        row=row,\n        positional_names=positional_names,\n    )\n")
    return text[:start] + body + text[end:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    path = pathlib.Path(a.root) / REL
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    new = apply_text(text)
    out = new.replace("\n", "\r\n") if crlf else new
    compile(new, str(path), "exec")
    if a.check:
        print(f"CHECK OK {REL} crlf={crlf} bytes {len(raw)} -> {len(out.encode())}")
        return
    path.write_bytes(out.encode("utf-8"))
    print(f"APPLIED {REL} crlf={crlf}")

main()

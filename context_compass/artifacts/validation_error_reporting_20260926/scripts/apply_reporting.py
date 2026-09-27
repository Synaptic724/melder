"""Apply the owner-approved conjure-report changes (2026-09-26) to a repository root.

Usage: python apply_reporting.py <repo_root>
Anchored, line-ending preserving edits (patch_util.replace_block); refuses when any anchor moved.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

root = pathlib.Path(sys.argv[1])
M = root / "src/melder"
SC = M / "aether/spellbook/spell_compiler"
V4 = SC / "validation/strategies"
V6 = SC / "system/validation"
HELPER_IMPORT = "from melder.utilities.helpers.general_helpers import SpellInputUtils"
DIAG_IMPORT = """from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)"""
VISIBILITY_FIX = "Bind it in this Spellbook, or give this conduit access to it."

# --- SpellInputUtils.describe_spell_id -------------------------------------------------------
gh = M / "utilities/helpers/general_helpers.py"
replace_block(gh, "from typing import Any, Optional, Tuple, Union, TypeVar, Type, ClassVar",
"""from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple, Union, TypeVar, Type, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell""")
replace_block(gh, """            spell_name = SpellInputUtils.normalize_spell_name(spell)

        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key""", """            spell_name = SpellInputUtils.normalize_spell_name(spell)

        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key

    @staticmethod
    def describe_spell_id(spell_id: Optional[str], spells: Mapping[str, Spell]) -> str:
        \"\"\"
        Name a spell version id for a user-facing message.

        Purpose:
            Validation and resolution run on spell version ids; users know spells
            by name. Messages call this so a 64-character id is shown only when
            no name is available.

        Contract:
            - Returns the spell's name, quoted, when `spells` holds `spell_id`.
            - Otherwise returns "spell id <first 12 characters>"; `None` gives
              "an unknown spell".
            - Pure; reads one mapping entry and the spell's name.

        Args:
            spell_id: Spell version id, or None.
            spells: Visible spell id -> Spell lookup (a spellbook's
                `_spell_id_pool` or a phase's `spell_lookup`).

        Returns:
            str: Display text such as "'CodecPacket'" or "spell id 3ba8e3be488d".
        \"\"\"
        if spell_id is None:
            return "an unknown spell"
        spell = spells.get(spell_id)
        if spell is not None:
            return repr(spell.spell_name)
        return f"spell id {spell_id[:12]}\"""")

# --- SpellbookValidationError: new renderer (whole file) -----------------------------------
sve = M / "utilities/custom_exceptions/spellbook_validation_error.py"
raw = sve.read_bytes().decode("utf-8")
new_text = (pathlib.Path(__file__).parent / "new_files/spellbook_validation_error.py").read_text(encoding="utf-8")
assert raw.replace("\r\n", "\n").startswith("from typing import TYPE_CHECKING, Any, Optional\n"), "exception file moved"
ending = "\r\n" if raw.count("\r\n") * 2 > raw.count("\n") else "\n"
sve.write_bytes(new_text.replace("\n", ending).encode("utf-8"))
print("rewrote spellbook_validation_error.py")

# --- SpellbookCreationSystem: gates hand over the diagnostics ------------------------------
scs = M / "aether/spellbook/spellbook_creation_system.py"
replace_block(scs, """            - Raises `SpellbookValidationError` naming the spells the ERROR
              diagnostics attribute the failure to; graph-level errors that
              carry no spell_id fall back to every scoped spell.""", """            - Raises `SpellbookValidationError` naming the spells the ERROR
              diagnostics attribute the failure to; graph-level errors that
              carry no spell_id fall back to every scoped spell.
            - Hands the conduit diagnostics to the error, which states their
              reasons; the phase artifacts that used to carry them are already
              cleaned when this gate runs (2026-09-26).""")
replace_block(scs, """        offending = [
            spell_id_pool[spell_id]
            for spell_id in dict.fromkeys(offender_ids)
            if spell_id in spell_id_pool
        ]
        raise SpellbookValidationError(offending)""", """        offending = [
            spell_id_pool[spell_id]
            for spell_id in dict.fromkeys(offender_ids)
            if spell_id in spell_id_pool
        ]
        raise SpellbookValidationError(
            offending,
            system_diagnostics=resolution_state.list_diagnostics(),
        )""")
replace_block(scs, """            # builder with an opaque RuntimeError instead of the validation
            # contract callers rely on.
            raise SpellbookValidationError([target_spell])""", """            # builder with an opaque RuntimeError instead of the validation
            # contract callers rely on. The conduit diagnostics carry the
            # reasons (the phase artifacts were just cleaned), so hand them over.
            resolution_state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
            raise SpellbookValidationError(
                [target_spell],
                system_diagnostics=(
                    resolution_state.list_diagnostics() if resolution_state is not None else None
                ),
            )""")
replace_block(scs, """                    message=(
                        f"Local resolution referenced dependency "
                        f"'{missing_dependency_id}', but it is not visible "
                        "to this Spellbook."
                    ),""", """                    message=(
                        f"Resolving this spell needs spell id {missing_dependency_id[:12]}, "
                        "which is not visible to this Spellbook. Bind it in this "
                        "Spellbook, or give this conduit access to it."
                    ),""")

# --- Phase 4: CircularDependencyStrategy ------------------------------------------------------
cds = V4 / "circular_dependency_strategy.py"
replace_block(cds, "from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy",
"from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy\n" + HELPER_IMPORT)
replace_block(cds, """        if cycle_path:
            # Format as "A -> B -> C -> A"
            pretty = " -> ".join(cycle_path + [cycle_path[0]])
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=(
                        f"Circular dependency detected starting from spell "
                        f"{context.spell.spell_name!r}: {pretty}."
                    ),""", """        if cycle_path:
            # `cycle_path` already closes the loop ("A -> B -> A"): the node that
            # closes it was appended before the recursion that found it. Name
            # every member; an id appears only for a spell the book cannot name.
            pool = spellbook._spell_id_pool
            pretty = " -> ".join(
                SpellInputUtils.describe_spell_id(spell_id, pool) for spell_id in cycle_path
            )
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=(
                        f"Spell {context.spell.spell_name!r} is part of a dependency cycle: "
                        f"{pretty}. Melder cannot build any spell in the cycle; remove one of "
                        "these constructor dependencies or give that parameter a default."
                    ),""")

# --- Phase 4: DanglingDependenciesStrategy / SelfDependencyStrategy ---------------------------
replace_block(V4 / "dangling_dependency_strategy.py", """                        message=(
                            f"Spell {spell.spell_name!r} depends on spell_id={dep_id!r}, "
                            "but no such spell is visible in the owning Spellbook."
                        ),""", """                        message=(
                            f"Spell {spell.spell_name!r} depends on spell id {dep_id[:12]}, "
                            "which this Spellbook does not hold. Bind that dependency in "
                            "this Spellbook, or remove the parameter that needs it."
                        ),""")
replace_block(V4 / "self_validation_strategy.py", """                    message=(
                        f"Spell {spell.spell_name!r} declares a dependency on itself "
                        f"(spell_id={root_id}). This indicates a configuration bug."
                    ),""", """                    message=(
                        f"Spell {spell.spell_name!r} depends on itself: one of its constructor "
                        "parameters resolves to this same spell. Remove that parameter or give "
                        "it a default."
                    ),""")

# --- Phase 4: ContractProviderPresenceStrategy -------------------------------------------------
cpp = V4 / "contract_provider_presence_strategy.py"
replace_block(cpp, """                        message=(
                            f"Spell {spell.spell_name!r} declares a contract socket for "
                            f"parameter {param.name!r} while system_state is automatic. "
                            "Contracts require dynamic mode to resolve."
                        ),""", """                        message=(
                            f"Spell {spell.spell_name!r} parameter {param.name!r} has a "
                            "SpellContract default, but this frame is automatic and contracts "
                            "only resolve in a dynamic frame. Remove the SpellContract default, "
                            "or build the frame dynamic (conjure(dynamic=True) before it settles)."
                        ),""")
replace_block(cpp, """                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} "
                                f"matches multiple providers for contract key {contract_key}."
                            ),""", """                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r}: "
                                f"{len(providers)} providers match contract {contract_key}, so "
                                "Melder cannot choose one. Keep a single provider for this "
                                "contract, for example by severing one of the links that supply it."
                            ),""")
replace_block(cpp, """                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} selects "
                                f"non-resolvable provider {providers[0][0]!r}. A SpellContract needs "
                                "a resolvable provider; select one or use a required supplied input."
                            ),""", """                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} selects "
                                f"provider {contract_key}, which is registered with "
                                "resolvable=False. A SpellContract needs a resolvable provider: "
                                "register one, or make this parameter a caller-supplied input."
                            ),""")

# --- Phase 4: ParameterPolicyStrategy (message + typing.Any misfire) ---------------------------
pps = V4 / "parameter_policy_strategy.py"
replace_block(pps, """                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                "is variadic but annotated for DI. Variadic DI is not supported."
                            ),""", """                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} is "
                                "variadic (*args/**kwargs) and annotated with an injectable type, "
                                "but Melder never injects variadic parameters. Use a list[...] "
                                "parameter to receive every registered implementation, or drop "
                                "the annotation."
                            ),""")
replace_block(pps, """    def _looks_like_di_target(self, annotation: Any) -> bool:
        \"\"\"
        Best-effort check for DI-eligible annotations.
        \"\"\"
        if isinstance(annotation, typing.ForwardRef):""", """    def _looks_like_di_target(self, annotation: Any) -> bool:
        \"\"\"
        Best-effort check for DI-eligible annotations.

        Contract:
            False for `typing.Any` (a class since Python 3.11), matching Phase 1's
            `SpellRequirementsFinder._looks_like_di_target`, so `*args: Any` and
            `**kwargs: Any` are not reported as variadic DI (2026-09-26).
        \"\"\"
        if annotation is typing.Any:
            return False

        if isinstance(annotation, typing.ForwardRef):""")

# --- Phase 4: AnnotationShapeGuardStrategy (list warning only when a user class is inside) -----
asg = V4 / "annotation_shape_guard_strategy.py"
replace_block(asg, """        access: internal. Phase-4 strategy: warns about list[T] elements and forward references
        Melder cannot inject. Emits LIST_ELEMENT_NOT_DI_TARGET and UNRESOLVED_FORWARD_REF
        (warnings). Only list[FrameType] is collection DI; set/dict/tuple parameters are caller
        inputs, reported by RequiredHolesStrategy.""", """        access: internal. Phase-4 strategy: warns about list[T] elements and forward references
        Melder cannot inject. Emits LIST_ELEMENT_NOT_DI_TARGET (only when a user class sits inside
        the element, e.g. list[Optional[Plugin]]; plain data such as list[str] gets nothing) and
        UNRESOLVED_FORWARD_REF (warnings). Only list[FrameType] is collection DI; set/dict/tuple
        parameters are caller inputs, reported by RequiredHolesStrategy.""")
replace_block(asg, """                if not self._looks_like_di_target(element):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="LIST_ELEMENT_NOT_DI_TARGET",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses list[{element!r}], which is not a DI frame/type. "
                                "Collection DI only works for list[FrameType]."
                            ),""", """                # Plain data lists (list[str], list[Any]) are ordinary caller
                # inputs; warn only when a user class hides inside the element
                # (list[Optional[Plugin]]), where injection may have been meant.
                if not self._looks_like_di_target(element) and self._mentions_di_target(element):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="LIST_ELEMENT_NOT_DI_TARGET",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} is "
                                f"list[{element!r}]. Melder injects a list only when its element is "
                                "one registered type (list[Plugin]), so this parameter is left for "
                                "the caller to supply."
                            ),""")
replace_block(asg, """    def _looks_like_di_target(self, annotation: Any) -> bool:
        \"\"\"
        Best-effort check for whether an annotation looks like a DI target.""", """    def _mentions_di_target(self, annotation: Any) -> bool:
        \"\"\"
        Report whether a DI-eligible class or forward reference appears among the
        annotation's type arguments (one level down), as in `Optional[Plugin]`.

        Contract:
            Only classes and forward references count; strings and literals do not.
        \"\"\"
        return any(
            (inspect.isclass(arg) or isinstance(arg, typing.ForwardRef)) and self._looks_like_di_target(arg)
            for arg in get_args(annotation)
        )

    def _looks_like_di_target(self, annotation: Any) -> bool:
        \"\"\"
        Best-effort check for whether an annotation looks like a DI target.""")

# --- Phase 4: RequiredHolesStrategy (container hint only when a user class is inside) ----------
rhs = V4 / "required_holes_strategy.py"
replace_block(rhs, "from typing import TYPE_CHECKING, Any, get_origin", "import inspect\nfrom typing import TYPE_CHECKING, Any, get_args, get_origin")
replace_block(rhs, """        Contract:
            - Returns a leading-space sentence when the annotation's origin is set,
              frozenset, dict or tuple (bare generics such as `dict[str, X]` and
              their typing aliases); otherwise an empty string.
            - Pure; reads only the annotation object.""", """        Contract:
            - Returns a leading-space sentence when the annotation's origin is set,
              frozenset, dict or tuple (bare generics such as `dict[str, X]` and
              their typing aliases) AND one of its type arguments is a user class,
              where someone may have expected injection; plain data such as
              `dict[str, Any]` gets no hint (2026-09-26). Otherwise an empty string.
            - Pure; reads only the annotation object.""")
replace_block(rhs, """        origin = get_origin(annotation)
        if origin not in (set, frozenset, dict, tuple):
            return \"\"""", """        origin = get_origin(annotation)
        if origin not in (set, frozenset, dict, tuple):
            return ""
        if not any(
            inspect.isclass(arg) and arg.__module__ != "builtins" and arg is not Any
            for arg in get_args(annotation)
        ):
            return \"\"""")

# --- Phase 6: strategies -------------------------------------------------------------------
for name in ("scope_ordering", "cycle_detection", "visibility_gap", "empty_collection", "broken_spell_in_dag"):
    replace_block(V6 / f"{name}_strategy.py", DIAG_IMPORT, DIAG_IMPORT + "\n" + HELPER_IMPORT)

replace_block(V6 / "scope_ordering_strategy.py", """                if node_rank >= dep_rank:
                    continue

                diagnostics.append(
                    SystemDiagnostic(
                        code="scope_ordering_violation",
                        message=(
                            f"Spell '{node.spell_id}' ({node.existence.name}) depends on "
                            f"'{dep_id}' ({dep_node.existence.name}), which is a narrower scope."
                        ),""", """                if node_rank >= dep_rank:
                    continue

                holder = SpellInputUtils.describe_spell_id(node.spell_id, spell_lookup)
                dependency = SpellInputUtils.describe_spell_id(dep_id, spell_lookup)
                diagnostics.append(
                    SystemDiagnostic(
                        code="scope_ordering_violation",
                        message=(
                            f"Spell {holder} ({node.existence.name}) depends on {dependency} "
                            f"({dep_node.existence.name}), which lives for a shorter scope, so "
                            f"{holder} would keep a stale {dependency} after that scope ends. "
                            f"Give {holder} the same or a shorter existence (or many), or give "
                            f"{dependency} a longer one."
                        ),""")

cyc = V6 / "cycle_detection_strategy.py"
replace_block(cyc, """            spell_lookup: Mapping of visible spell version ids (unused by this strategy).""",
"""            spell_lookup: Mapping of visible spell version ids, used to name the spells
                left in or behind a cycle.""")
replace_block(cyc, """        if visited != len(indegree):
            diagnostics.append(
                SystemDiagnostic(
                    code="cycle_detected",
                    message="Cycle detected in system dependency graph.",
                    severity=SystemDiagnosticSeverity.ERROR,
                )
            )""", """        if visited != len(indegree):
            # Nodes Kahn's algorithm could not release sit in a cycle or behind one.
            blocked_ids = sorted(node_id for node_id, degree in indegree.items() if degree > 0)
            named = [SpellInputUtils.describe_spell_id(node_id, spell_lookup) for node_id in blocked_ids[:10]]
            if len(blocked_ids) > 10:
                named.append(f"and {len(blocked_ids) - 10} more")
            diagnostics.append(
                SystemDiagnostic(
                    code="cycle_detected",
                    message=(
                        "Cycle detected in the dependency graph. These spells are in a dependency "
                        f"cycle or depend on one: {', '.join(named)}. Remove one constructor "
                        "dependency in the cycle, or give that parameter a default."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    details={"blocked_spell_ids": blocked_ids},
                )
            )""")

replace_block(V6 / "visibility_gap_strategy.py", """                    message=(
                        f"Spell '{node.spell_id}' depends on missing spell ids "
                        f"{sorted(missing)}, which are not visible in the current spellbook."
                    ),""", """                    message=(
                        f"Spell {SpellInputUtils.describe_spell_id(node.spell_id, spell_lookup)} "
                        "depends on spells this Spellbook cannot see ("
                        + ", ".join(
                            SpellInputUtils.describe_spell_id(dep_id, spell_lookup)
                            for dep_id in sorted(missing)
                        )
                        + "). Bind them in this Spellbook, or give this conduit access to them."
                    ),""")

replace_block(V6 / "empty_collection_strategy.py", """                        message=(
                            f"Spell '{spell_id}' parameter '{socket.param_name}' "
                            "declares a required collection dependency (list[...]) "
                            "but no providers wired into it in the resolved graph. "
                            f"{remediation}"
                        ),""", """                        message=(
                            f"Spell {SpellInputUtils.describe_spell_id(spell_id, spell_lookup)} "
                            f"parameter '{socket.param_name}' is a required list[...] "
                            "dependency, but no provider is wired into it. "
                            f"{remediation}"
                        ),""")

replace_block(V6 / "broken_spell_in_dag_strategy.py", """                if node_id in broken_spell_ids:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="broken_spell_in_dag",
                            message=(
                                f"Broken spell '{node_id}' is reachable in root DAG '{root_id}'."
                            ),""", """                if node_id in broken_spell_ids:
                    node_label = SpellInputUtils.describe_spell_id(node_id, spell_lookup)
                    root_label = SpellInputUtils.describe_spell_id(root_id, spell_lookup)
                    if node_id == root_id:
                        message = f"Root spell {node_label} is broken (see its own errors)."
                    else:
                        message = (
                            f"Spell {root_label} depends on {node_label}, which is broken, so "
                            f"root {root_label} cannot be built either."
                        )
                    diagnostics.append(
                        SystemDiagnostic(
                            code="broken_spell_in_dag",
                            message=message,""")

# --- Phase 6: CompilerPhase6 local visibility guards -----------------------------------------
cp6 = SC / "phases/compiler_phase_6.py"
replace_block(cp6, DIAG_IMPORT, DIAG_IMPORT + "\n" + HELPER_IMPORT)
replace_block(cp6, """                            message=(
                                f"Spell '{spell_id}' parameter '{socket.param_name}' "
                                f"depends on '{dependency_id}', but that dependency is "
                                "not visible to this Spellbook."
                            ),""", """                            message=(
                                f"Spell {SpellInputUtils.describe_spell_id(spell_id, spell_lookup)} "
                                f"parameter '{socket.param_name}' resolves to "
                                f"{SpellInputUtils.describe_spell_id(dependency_id, spell_lookup)}, "
                                "which is not visible to this Spellbook. Bind it in this "
                                "Spellbook, or give this conduit access to it."
                            ),""")
replace_block(cp6, """                        message=(
                            f"Root '{root_id}' references dependency "
                            f"'{dependency_id}', but that dependency is not "
                            "visible to this Spellbook."
                        ),""", """                        message=(
                            "The dependency graph of "
                            f"{SpellInputUtils.describe_spell_id(root_id, spell_lookup)} includes "
                            f"{SpellInputUtils.describe_spell_id(dependency_id, spell_lookup)}, "
                            "which is not visible to this Spellbook. Bind it in this "
                            "Spellbook, or give this conduit access to it."
                        ),""")
print("done")

"""S4b: every family decides unresolved inputs before construction - anchored source edits.

Usage: python apply_s4b_edits.py <tree_root> [--check]

Solo: `_call_target_for` binds a decided call target that raises `UnresolvedInputError.for_unsupplied` before calling
the constructor. `UnresolvedInputError.from_failed_construction` is deleted. The families'
`_raise_meld_construction_error(spell, exc)` lose the unresolved branch and the supplied-argument parameters, and their
callers (the site-plan lowering, both families' generic helper and transient emitter, the generalized manifest
emitter) stop passing them. Each anchor must match exactly once or nothing is written. Engine:
../s3_staging/apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

C = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/"
SOLO_NO = C + "strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py"
SOLO_OV = C + "strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py"
GEN = C + "strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py"
MANY = C + "strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py"
MANIFEST = C + "strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py"
LOWERING = C + "shared_assets/site_plan_lowering.py"
ERROR = "src/melder/utilities/custom_exceptions/unresolved_input_error.py"

SOLO_DOC_OLD = """        - Binds `call_target` through `_call_target_for`: the raw spell callable,
          or an unresolved-input guard when the spell has UNRESOLVED_INPUT sockets.
"""
SOLO_DOC_NEW = """        - Binds `call_target` through `_call_target_for`: the raw spell callable,
          or, when the spell has UNRESOLVED_INPUT sockets, a decided call target
          that raises `UnresolvedInputError` for an unsupplied one before calling.
"""

CALL_TARGET_NEW = '''def _call_target_for(spell: Any) -> Callable[..., Any]:
    """
    Return the callable a solo executor invokes for one spell.

    Purpose:
        A solo root with an unresolved input (a typed parameter no registered
        spell provides) must name what the caller left out instead of letting its
        constructor fail. The decision is made before the call, as the many_only
        and generalized plans make it (design v2 S4, B6).

    Contract:
        - When the spell's Phase-3 topology has no UNRESOLVED_INPUT socket, returns
          `spell.spell` itself: those executors keep the direct call.
        - Otherwise returns a decided call target. It checks the call's keyword
          names and positional count against those sockets (a positional-capable
          socket counts as supplied when its position is below the count; a name
          passed with None counts as supplied) and raises
          `UnresolvedInputError.for_unsupplied(spell, missing)` without calling
          the constructor when any is left out. Otherwise it calls `spell.spell`
          and lets every exception propagate unchanged.
        - The sockets are read once, when the executor is compiled or hydrated;
          a topology change re-resolves the spell and rebuilds its executor. The
          emitted source is identical either way, so the code-object cache is
          unaffected.

    Args:
        spell: The root spell the solo executor constructs.

    Returns:
        Callable[..., Any]: The callable bound as `call_target`.
    """
    call_target = spell.spell
    topology = spell._spell_system_states.get_local_topology(spell.spell_index)
    if topology is None:
        return call_target
    unresolved = tuple(
        (
            socket.param_name,
            socket.position
            if socket.parameter_kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
            else None,
        )
        for socket in topology.sockets
        if socket.socket_kind is SocketKind.UNRESOLVED_INPUT
    )
    if not unresolved:
        return call_target

    def decided_call_target(*args: Any, **kwargs: Any) -> Any:
        """
        Call the spell only when every unresolved input is supplied.

        Raises:
            UnresolvedInputError: An unresolved input is neither among `kwargs`
                nor covered by a positional argument; nothing was constructed.
        """
        positional_count = len(args)
        missing = [
            name
            for name, position in unresolved
            if name not in kwargs and (position is None or position >= positional_count)
        ]
        if missing:
            raise UnresolvedInputError.for_unsupplied(spell, missing)
        return call_target(*args, **kwargs)

    return decided_call_target


'''

ERR_WHEN_OLD = """        its unresolved inputs, and conjure succeeds regardless. The many_only and
        generalized plans raise it before constructing anything under that object
        (2026-09-26); the solo lane raises it from the failed constructor call.
"""
ERR_WHEN_NEW = """        its unresolved inputs, and conjure succeeds regardless. It is decided before
        construction: the many_only and generalized plans raise it before building
        anything under that object, and a solo root's call target raises it instead
        of calling the constructor (2026-09-26).
"""
ERR_INNER_OLD = """        - `inner` carries the constructor-call exception that exposed the gap on
          the solo failure path; it is None when a plan raised before building.
"""
ERR_INNER_NEW = """        - `inner` is None: nothing has been called when it is raised.
"""
ERR_CTX_OLD = """        Fires in the resolution layer at meld, after conjure produced the Conduit:
        from a plan before construction (many_only, generalized) or on the solo
        constructor-failure path. Successful melds never evaluate it.
"""
ERR_CTX_NEW = """        Fires in the resolution layer at meld, after conjure produced the Conduit,
        before construction: from a plan (many_only, generalized) or from a solo
        root's call target. Successful melds never evaluate it.
"""
ERR_INIT_OLD = """            inner:
                Constructor-call exception that exposed the missing input.
"""
ERR_INIT_NEW = """            inner:
                None when Melder raises it (nothing was called); kept for the
                `MeldExecutionError` shape.
"""
ERR_FOR_OLD = """        Purpose:
            The plan-side decision (design v2 S4a, B6): a many_only or generalized
            plan raises this instead of calling a constructor that must fail.

        Contract:
            - Selects the consumer's UNRESOLVED_INPUT sockets named in
              `param_names` from its live Phase-3 topology; message, fields and
              ordering are exactly `from_failed_construction`'s, and `inner` is
              None (nothing was called).

        Args:
            spell:
                The consumer the plan was about to build.
            param_names:
                Its UNRESOLVED_INPUT parameters that have no winning key.
"""
ERR_FOR_NEW = """        Purpose:
            The decision before construction (design v2 S4, B6): a many_only or
            generalized plan, or a solo root's call target, raises this instead of
            calling a constructor that must fail.

        Contract:
            - Selects the consumer's UNRESOLVED_INPUT sockets named in
              `param_names` from its live Phase-3 topology and builds the message
              and fields in signature order; `inner` is None (nothing was called).

        Args:
            spell:
                The consumer about to be built.
            param_names:
                Its UNRESOLVED_INPUT parameters that the call does not supply.
"""
ERR_FOR_CALL_OLD = """        return cls._from_missing_sockets(spell, missing, None)
"""
ERR_FOR_CALL_NEW = """        return cls._from_missing_sockets(spell, missing)
"""
ERR_BUILD_OLD = """            missing: List[SpellSocketDescriptor],
            inner: Optional[BaseException],
    ) -> UnresolvedInputError:
        \"\"\"
        Build the error from the consumer's missing UNRESOLVED_INPUT sockets (shared message builder).

        Args:
            spell: The consumer.
            missing: Its unsupplied UNRESOLVED_INPUT sockets (any order; sorted here).
            inner: The constructor-call exception, or None when nothing was called.
"""
ERR_BUILD_NEW = """            missing: List[SpellSocketDescriptor],
    ) -> UnresolvedInputError:
        \"\"\"
        Build the error from the consumer's missing UNRESOLVED_INPUT sockets.

        Args:
            spell: The consumer.
            missing: Its unsupplied UNRESOLVED_INPUT sockets (any order; sorted here).
"""
ERR_INNER_ARG_OLD = """            param_name=param_name,
            inner=inner,
            expected_type=expected_type,
"""
ERR_INNER_ARG_NEW = """            param_name=param_name,
            inner=None,
            expected_type=expected_type,
"""


def _raise_new(shared_by: str) -> str:
    """Return the replacement `_raise_meld_construction_error` for one family file."""
    return f'''def _raise_meld_construction_error(spell: Any, exc: BaseException) -> None:
    """
    Raise the ``MeldExecutionError`` for a failed constructor call.

    {shared_by}
    Lives off the hot path: only the failure branch calls it.

    Contract:
        - Always raises ``MeldExecutionError`` chained from ``exc``. Unresolved
          inputs never reach it: every family decides them before the call
          (``UnresolvedInputError.for_unsupplied``, design v2 S4).

    Raises:
        MeldExecutionError: Always.
    """
'''


RAISE_OLD = """def _raise_meld_construction_error(
        spell: Any,
        exc: BaseException,
        supplied_names: Collection[str] = (),
        supplied_positional_count: int = 0,
) -> None:
    \"\"\"
    Raise the ``MeldExecutionError`` for a failed constructor call.

    Shared by the inlined fast path, the generic ``_construct_spell_instance``
    helper and the transient unrolled executor, so all three report
    construction failures identically. Lives off the hot path: only the
    failure branch calls it.

    Contract:
        - First asks ``UnresolvedInputError.from_failed_construction`` whether
          an unresolved input (a typed parameter no registered spell provides)
          was left out of the call; if so that error is raised, chained from
          ``exc``. INTERIM until the build plan decides it (design S3/S4).
        - Otherwise raises the existing ``MeldExecutionError`` unchanged.
        - ``supplied_names`` / ``supplied_positional_count`` describe what the
          call actually passed. Inlined calls pass only dependency keywords,
          which never name an unresolved input, so they use the defaults.

    Raises:
        UnresolvedInputError: An unresolved input was not supplied.
        MeldExecutionError: Any other constructor failure.
    \"\"\"
    unresolved = UnresolvedInputError.from_failed_construction(
        spell,
        exc,
        supplied_names=supplied_names,
        supplied_positional_count=supplied_positional_count,
    )
    if unresolved is not None:
        raise unresolved from exc
"""
RAISE_STOP = """    raise MeldExecutionError(
        spell_id=spell.spell_index.selected_spell_id,
        spell_name=spell.spell_name,
        message=f"Error invoking spell '{spell.spell_name}'.",
        inner=exc,
    ) from exc
"""
GEN_SHARED = ("Shared by the site-plan lowering, the inlined fast path, the generic\n"
              "    ``_construct_spell_instance`` helper and the transient unrolled executor, so\n"
              "    all of them report construction failures identically.")
MANY_SHARED = ("Shared by the inlined fast path, the generic ``_construct_spell_instance``\n"
               "    helper and the transient unrolled executor, so all three report\n"
               "    construction failures identically.")

HELPER_CALL_OLD = "        _raise_meld_construction_error(spell, exc, call_kwargs, len(args))\n"
HELPER_CALL_NEW = "        _raise_meld_construction_error(spell, exc)\n"
TRANSIENT_OLD = """        # Transient calls pass their CALLn dependencies positionally, so the
        # failure helper is told how many positions the call supplied.
        lines.append(
            f"        _raise_meld_construction_error(steps[{step_index}].spell, exc, (), {int(call_mode)})"
        )
"""
TRANSIENT_NEW = """        lines.append(
            f"        _raise_meld_construction_error(steps[{step_index}].spell, exc)"
        )
"""
IMPORT_ERR = "from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError\n"
TYPING_OLD = "from typing import Any, Callable, Collection, Dict, Optional, Sequence, Tuple, Union\n"
TYPING_NEW = "from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union\n"

MANIFEST_OLD = """    # Contract-payload keywords and a positional payload are supplied by this
    # call too; the failure helper needs them to tell an unsupplied unresolved
    # input apart from any other constructor failure. Dependency keywords never
    # name an unresolved input, so they are not repeated here.
    supplied_arguments = ""
    if positional is not None:
        supplied_arguments = f", {tuple(payload_names)!r}, len(positional_{step_index})"
    elif payload_names:
        supplied_arguments = f", {tuple(payload_names)!r}"
    lines.extend([
        f"{indent}except Exception as exc:",
        f"{indent}    _raise_meld_construction_error(spell_{step_index}, exc{supplied_arguments})",
    ])
"""
MANIFEST_NEW = """    lines.extend([
        f"{indent}except Exception as exc:",
        f"{indent}    _raise_meld_construction_error(spell_{step_index}, exc)",
    ])
"""

LOW_DOC_OLD = """            MeldExecutionError: When `__args__` is not a list or tuple, or the
                constructor fails (through `_raise_meld_construction_error`).
            UnresolvedInputError: When the failed call left out an unresolved input.
"""
LOW_DOC_NEW = """            MeldExecutionError: When `__args__` is not a list or tuple, or the
                constructor fails (through `_raise_meld_construction_error`).
"""
LOW_CALL_OLD = "            _raise_meld_construction_error(spell, exc, tuple(kwargs), len(args))\n"
LOW_CALL_NEW = "            _raise_meld_construction_error(spell, exc)\n"
LOW_RAISE_DOC_OLD = """            Emitted before anything under the site is constructed, so the
            error has no TypeError cause; message and fields are the failure
            path's (`UnresolvedInputError.for_unsupplied`).
"""
LOW_RAISE_DOC_NEW = """            Emitted before anything under the site is constructed, so the
            error has no TypeError cause (`UnresolvedInputError.for_unsupplied`,
            the same decision the solo lane's call target makes).
"""
LOW_EMIT_DOC_OLD = """            Direct steps call the spell with operands and route failures through
            `_raise_meld_construction_error` with this call's keyword names and
            positional count. Generic steps call the no-overrides helper, or the
"""
LOW_EMIT_DOC_NEW = """            Direct steps call the spell with operands and route failures through
            `_raise_meld_construction_error`. Generic steps call the no-overrides helper, or the
"""
LOW_EMIT_OLD = """        keyword_names = tuple(name for name, _ in keyword)
        count_expression = "len(args)" if star_args else str(len(positional))
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    {local} = {call_name}({', '.join(parts)})")
        lines.append(f"{indent}except Exception as exc:")
        lines.append(
            f"{indent}    _raise_meld_construction_error(spells[{index}], exc, "
            f"{keyword_names!r}, {count_expression})"
        )
"""
LOW_EMIT_NEW = """        lines.append(f"{indent}try:")
        lines.append(f"{indent}    {local} = {call_name}({', '.join(parts)})")
        lines.append(f"{indent}except Exception as exc:")
        lines.append(f"{indent}    _raise_meld_construction_error(spells[{index}], exc)")
"""

EDITS = {
    SOLO_NO: [
        ("replace", SOLO_DOC_OLD, SOLO_DOC_NEW),
        ("cut", "def _call_target_for(spell: Any) -> Callable[..., Any]:", "def _normalize_disposal_methods("),
        ("replace", "def _normalize_disposal_methods(\n", CALL_TARGET_NEW + "def _normalize_disposal_methods(\n"),
    ],
    SOLO_OV: [("replace", SOLO_DOC_OLD, SOLO_DOC_NEW)],
    ERROR: [
        ("replace", ERR_WHEN_OLD, ERR_WHEN_NEW),
        ("replace", ERR_INNER_OLD, ERR_INNER_NEW),
        ("replace", ERR_CTX_OLD, ERR_CTX_NEW),
        ("replace", ERR_INIT_OLD, ERR_INIT_NEW),
        ("cut", "    @classmethod\n    def from_failed_construction(", "    def for_unsupplied("),
        ("replace", "    def for_unsupplied(cls", "    @classmethod\n    def for_unsupplied(cls"),
        ("replace", ERR_FOR_OLD, ERR_FOR_NEW),
        ("replace", ERR_FOR_CALL_OLD, ERR_FOR_CALL_NEW),
        ("replace", ERR_BUILD_OLD, ERR_BUILD_NEW),
        ("replace", ERR_INNER_ARG_OLD, ERR_INNER_ARG_NEW),
    ],
    GEN: [
        ("replace", TYPING_OLD, TYPING_NEW),
        ("replace", IMPORT_ERR, ""),
        ("replace", RAISE_OLD, _raise_new(GEN_SHARED)),
        ("replace", HELPER_CALL_OLD, HELPER_CALL_NEW),
        ("replace", TRANSIENT_OLD, TRANSIENT_NEW),
    ],
    MANY: [
        ("replace", TYPING_OLD, TYPING_NEW),
        ("replace", IMPORT_ERR, ""),
        ("replace", RAISE_OLD, _raise_new(MANY_SHARED)),
        ("replace", HELPER_CALL_OLD, HELPER_CALL_NEW),
        ("replace", TRANSIENT_OLD, TRANSIENT_NEW),
    ],
    MANIFEST: [("replace", MANIFEST_OLD, MANIFEST_NEW)],
    LOWERING: [
        ("replace", LOW_DOC_OLD, LOW_DOC_NEW),
        ("replace", LOW_CALL_OLD, LOW_CALL_NEW),
        ("replace", LOW_RAISE_DOC_OLD, LOW_RAISE_DOC_NEW),
        ("replace", LOW_EMIT_DOC_OLD, LOW_EMIT_DOC_NEW),
        ("replace", LOW_EMIT_OLD, LOW_EMIT_NEW),
    ],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()

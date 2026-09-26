"""P5: the site-plan lowering passes an operand positionally only where the receiving code binds it by that name.

Usage: python apply_p5_edits.py <tree_root> [--check]

Adds SitePlanLowering.positional_run (P1's rule, generalized to functions and bound methods) and uses it in
SitePlanEmission._call_arguments. Each anchor must match exactly once or nothing is written.
Engine: ../s3_staging/apply_s3b1_edits.py (_apply_one).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"

IMPORT_OLD = "from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, FrozenSet, List, Optional, Set, Tuple\n"
IMPORT_NEW = "from types import FunctionType, MethodType\n" + IMPORT_OLD

KINDS_OLD = '''    VARIADIC_KINDS: ClassVar[Tuple[str, ...]] = ("VAR_POSITIONAL", "VAR_KEYWORD")
'''
KINDS_NEW = '''    VARIADIC_KINDS: ClassVar[Tuple[str, ...]] = ("VAR_POSITIONAL", "VAR_KEYWORD")

    @staticmethod
    def positional_run(target: Any, names: Tuple[str, ...]) -> int:
        """
        Return how many leading `names` the code that receives a call of `target` binds by position.

        Purpose:
            Decide where an emitted call may pass operands positionally. Injection is by parameter
            name, so a value goes positionally only where the receiving code provably binds that
            position to that name; code that can observe argument names (a custom `__new__`, a
            metaclass `__call__`, a signature-preserving `*args, **kwargs` wrapper) gets names.
            Positional class calls are the fast path on CPython 3.14 (P1, melder_2).

        Contract:
            - A class qualifies when its metaclass keeps `type.__call__`, its `__new__` is
              `object.__new__` and its `__init__` is a plain Python function; the receiving names
              are that `__init__`'s positional parameters after `self`.
            - A plain function or lambda gives its own positional parameters; a bound method of a
              plain function gives its function's positional parameters after the bound one.
            - Anything else receives no positional operands (returns 0).
            - Counts the leading `names` equal, in order, to the receiving names; positional-only
              parameters count like the others.
            - Pure attribute reads: annotations, `__signature__` and `__wrapped__` are never read.

        Args:
            target: The step's call target (`Spell.spell`).
            names: The call site's positional-capable parameter names in signature order.

        Returns:
            int: The length of the matching leading run (0 when `target` does not qualify).
        """
        receiving: Tuple[str, ...] = ()
        if isinstance(target, type):
            initializer = target.__init__
            if (
                    type(target).__call__ is type.__call__
                    and target.__new__ is object.__new__
                    and type(initializer) is FunctionType
            ):
                code = initializer.__code__
                receiving = code.co_varnames[1:code.co_argcount]
        elif type(target) is FunctionType:
            code = target.__code__
            receiving = code.co_varnames[:code.co_argcount]
        elif type(target) is MethodType and type(target.__func__) is FunctionType:
            code = target.__func__.__code__
            receiving = code.co_varnames[1:code.co_argcount]
        run = 0
        for name, received in zip(names, receiving):
            if name != received:
                break
            run += 1
        return run
'''

CALL_DOC_OLD = '''        Contract:
            Parameters are taken in signature order; operands go positionally
            until the first omitted parameter, then by keyword. A root whose
            `__args__` is longer than its positional parameters passes `*args`
            (extra values fail in the constructor, as today). A variadic,
            unknown-kind or out-of-order positional-only operand is not
            expressible.
        """
'''
CALL_DOC_NEW = '''        Contract:
            Parameters are taken in signature order. An operand goes positionally
            while positionals are open and it is either a caller's root
            `__args__` value or bound to that position by name in the target's
            receiving code (`SitePlanLowering.positional_run`); the first
            operand that does not qualify, or the first omitted parameter,
            closes positionals and the rest go by keyword. A root whose
            `__args__` is longer than its positional parameters passes `*args`
            (extra values fail in the constructor, as today). A variadic or
            unknown-kind operand, or a positional-only operand that cannot go
            positionally, is not expressible (the step uses the generic helper).
        """
'''

RUN_OLD = '''            if self._arity > len(capable):
                star_args = True
                positional_open = False
        for param in ordered:
'''
RUN_NEW = '''            if self._arity > len(capable):
                star_args = True
                positional_open = False
        run = SitePlanLowering.positional_run(
            step.spell.spell,
            tuple(param.name for param in ordered if param.parameter_kind in SitePlanLowering.POSITIONAL_KINDS),
        )
        winners = self._winners
        for param in ordered:
'''

LOOP_OLD = '''            if positional_open and kind in SitePlanLowering.POSITIONAL_KINDS:
                positional.append(expression)
                continue
            if kind == "POSITIONAL_ONLY":
'''
LOOP_NEW = '''            if positional_open and kind in SitePlanLowering.POSITIONAL_KINDS:
                if len(positional) < run or winners.get((site_index, param.name)) == "__args__":
                    positional.append(expression)
                    continue
                positional_open = False
            if kind == "POSITIONAL_ONLY":
'''

EDITS = {
    LOWERING: [
        ("replace", IMPORT_OLD, IMPORT_NEW),
        ("replace", KINDS_OLD, KINDS_NEW),
        ("replace", CALL_DOC_OLD, CALL_DOC_NEW),
        ("replace", RUN_OLD, RUN_NEW),
        ("replace", LOOP_OLD, LOOP_NEW),
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

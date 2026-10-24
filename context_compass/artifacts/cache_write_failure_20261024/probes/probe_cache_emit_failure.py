"""Creation-cache write failures on the meld path (melder_0; TASK-2026-10-24-cache_file_write_failure_fails_meld).

Run from a scratch folder against a COPY of a tree's src/ - the creation cache is written under the melder package
root, so a copy keeps the probe's bundles out of the tree - with the GIL off and on, as a user file modes bind:
    PYTHONPATH=<copy>/src python -X gil=0 <this file>

Windows refuses the bundle's os.replace (WinError 5) while another handle holds the destination; Linux never does,
so case A injects that refusal once. Case B makes a frame's cache folder read-only after conjure (a read-only
install), case C makes the conjure-cache root read-only before conjure, case D leases a limited_quantity managed
spell through a refused write. Each case prints what the caller saw.
"""
import pathlib
import sys
from typing import Any, Callable, Dict, Optional

import melder as md

BUILT: Dict[str, int] = {}
CACHE = pathlib.Path(md.__file__).resolve().parent / "__melder_cache__" / "__conjure_cache__"


class Built:
    """Counts constructions per class name, so the probe can tell a built object from a returned one."""

    def __init__(self) -> None:
        BUILT[type(self).__name__] = BUILT.get(type(self).__name__, 0) + 1


class FirstA(Built):
    """Bound before conjure (case A)."""


class LateA(Built):
    """Bound after conjure, so its first meld compiles it and stages its payload (case A)."""


class FirstB(Built):
    """Bound before conjure (case B)."""


class LateB(Built):
    """Bound after conjure (case B)."""


class FirstC(Built):
    """Bound before conjure (case C)."""


class FirstD(Built):
    """Bound before conjure (case D)."""


class PooledD(Built):
    """A managed spell, bound after conjure with a limit of one (case D)."""


class ReplaceRefusal:
    """Refuses the next Path.replace onto one target, as Windows refuses a destination another handle holds."""

    def __init__(self) -> None:
        self.target: Optional[pathlib.Path] = None
        self.refused = 0
        path_type = type(pathlib.Path("."))
        original = path_type.replace
        refusal = self

        def replace(path: pathlib.Path, target: Any) -> pathlib.Path:
            if refusal.target is not None and pathlib.Path(target) == refusal.target:
                refusal.target = None
                refusal.refused += 1
                raise PermissionError(13, "Access is denied (injected; Windows reports [WinError 5])",
                                      str(path), None, str(target))
            return original(path, target)

        path_type.replace = replace


def attempt(case: str, label: str, call: Callable[[], Any]) -> Any:
    """Run one call and print what its caller saw."""
    try:
        result = call()
    except BaseException as error:  # the probe reports every outcome, including the ones under test
        print(f"{case}: {label}: raised {type(error).__name__}: {error}")
        return None
    print(f"{case}: {label}: returned {type(result).__name__}")
    return result


def case_a(refusal: ReplaceRefusal) -> None:
    book = md.Spellbook(aetheric_frame="probe_case_a")
    book.bind(spell=FirstA, existence="unique", permissions="create")
    root = book.conjure(dynamic=True, name="root_a")
    bundle = CACHE / "probe_case_a" / "root_a.meldercache"
    temp = bundle.with_name(bundle.name + ".tmp")
    print(f"A: conjure wrote the bundle: {bundle.exists()}")
    root.bind(spell=LateA, existence="unique", permissions="create")
    refusal.target = bundle
    attempt("A", "first meld of LateA (bound after conjure), the next replace refused once",
            lambda: root.meld(spell=LateA))
    print(f"A: replaces refused: {refusal.refused}; LateA built {BUILT.get('LateA', 0)} time(s); "
          f"temp file left: {temp.exists()}")
    refusal.target = None
    first = attempt("A", "second meld of LateA", lambda: root.meld(spell=LateA))
    second = attempt("A", "third meld of LateA", lambda: root.meld(spell=LateA))
    print(f"A: LateA built {BUILT.get('LateA', 0)} time(s); second and third melds returned one object: "
          f"{first is second and first is not None}; temp file left: {temp.exists()}")
    root.cleanup()


def case_b() -> None:
    book = md.Spellbook(aetheric_frame="probe_case_b")
    book.bind(spell=FirstB, existence="unique", permissions="create")
    root = book.conjure(dynamic=True, name="root_b")
    folder = CACHE / "probe_case_b"
    attempt("B", "meld of FirstB before the folder is made read-only", lambda: root.meld(spell=FirstB))
    root.bind(spell=LateB, existence="unique", permissions="create")
    folder.chmod(0o555)
    try:
        attempt("B", "first meld of LateB (bound after conjure), frame folder read-only",
                lambda: root.meld(spell=LateB))
        for number in (1, 2, 3):
            attempt("B", f"meld {number} of FirstB (built earlier, nothing new staged), folder read-only",
                    lambda: root.meld(spell=FirstB))
    finally:
        folder.chmod(0o755)
    attempt("B", "meld of FirstB, folder writable again", lambda: root.meld(spell=FirstB))
    print(f"B: FirstB built {BUILT.get('FirstB', 0)} time(s), LateB built {BUILT.get('LateB', 0)} time(s)")
    root.cleanup()


def case_c() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    folder = CACHE / "probe_case_c"
    CACHE.chmod(0o555)
    root = None
    try:
        book = md.Spellbook(aetheric_frame="probe_case_c")
        book.bind(spell=FirstC, existence="unique", permissions="create")
        root = attempt("C", "conjure with the conjure-cache root read-only",
                       lambda: book.conjure(dynamic=True, name="root_c"))
        print(f"C: frame folder created: {folder.exists()}")
        if root is not None:
            attempt("C", "first meld of FirstC, root read-only", lambda: root.meld(spell=FirstC))
            attempt("C", "second meld of FirstC, root read-only", lambda: root.meld(spell=FirstC))
    finally:
        CACHE.chmod(0o755)
    if root is not None:
        attempt("C", "meld of FirstC, root writable again", lambda: root.meld(spell=FirstC))
        print(f"C: FirstC built {BUILT.get('FirstC', 0)} time(s); frame folder created: {folder.exists()}")
        root.cleanup()


def case_d(refusal: ReplaceRefusal) -> None:
    book = md.Spellbook(aetheric_frame="probe_case_d")
    book.bind(spell=FirstD, existence="unique", permissions="create")
    root = book.conjure(dynamic=True, name="root_d")
    bundle = CACHE / "probe_case_d" / "root_d.meldercache"
    root.bind(spell=PooledD, existence="managed_spell_quantity", permissions="create",
              managed_spell_mode="limited_quantity", managed_spell_limit=1)
    before = refusal.refused
    refusal.target = bundle
    attempt("D", "first managed_spell_meld of PooledD (limited_quantity, limit 1), the next replace refused once",
            lambda: root.managed_spell_meld(spell=PooledD))
    print(f"D: replaces refused: {refusal.refused - before}; PooledD built {BUILT.get('PooledD', 0)} time(s)")
    refusal.target = None
    lease = attempt("D", "second managed_spell_meld of PooledD", lambda: root.managed_spell_meld(spell=PooledD))
    if lease is not None:
        lease.release()
    print(f"D: PooledD built {BUILT.get('PooledD', 0)} time(s)")
    attempt("D", "root teardown", root.cleanup)


def main() -> None:
    gil = sys._is_gil_enabled()
    print(f"melder {md.__version__} from {pathlib.Path(md.__file__).parent}; Python {sys.version.split()[0]}; "
          f"GIL {'on' if gil else 'off'}")
    refusal = ReplaceRefusal()
    case_a(refusal)
    case_b()
    case_c()
    case_d(refusal)


if __name__ == "__main__":
    main()

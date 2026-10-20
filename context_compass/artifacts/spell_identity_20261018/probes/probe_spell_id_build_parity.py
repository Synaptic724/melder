"""Probe (melder_0, 2026-10-18; STORY-2026-10-18-spell_id_hashes_the_object_code): is a spell_id the same on a
free-threaded and a GIL build of one Python release, and with the GIL off and on?

A spell_id is the SHA256 of `v5-code`, `sys.implementation.cache_tag` and the target's encoding, which reads each
function's instructions. Both 3.14.7 builds report the cache tag `cpython-314`, so the ids agree exactly when the two
builds compile the same instructions. This digests every class and function Melder's package defines (they stand in
for user code; the digest does not check bindability) and a handful of user-like classes executed from source, and
writes "<qualified name>\t<spell_id>" lines, sorted, to the file given as the first argument:
    PYTHONPATH=<repo>/src python3.14t -X gil=0 probe_spell_id_build_parity.py ../runs/build_parity/ft_gil0.tsv
    PYTHONPATH=<repo>/src python3.14 probe_spell_id_build_parity.py ../runs/build_parity/gil_build.tsv
"""
import hashlib
import importlib
import inspect
import pathlib
import sys
import sysconfig
import types
import warnings
from typing import Any, Dict, List, Tuple

warnings.simplefilter("ignore")

import melder
from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest


def collect() -> Tuple[Dict[str, Any], List[str]]:
    """Every class and plain function defined by an importable melder module, by qualified name."""
    targets: Dict[str, Any] = {}
    failed: List[str] = []
    root = pathlib.Path(melder.__file__).parent
    names = sorted("melder." + ".".join(path.relative_to(root).with_suffix("").parts)
                   for path in root.rglob("*.py") if path.name != "__init__.py" and "_build_assets" not in path.parts)
    for name in names:
        try:
            module = importlib.import_module(name)
        except Exception as error:  # report, do not stop
            failed.append(f"{name}: {type(error).__name__}")
            continue
        for value in vars(module).values():
            if (inspect.isclass(value) or isinstance(value, types.FunctionType)) and value.__module__ == name:
                targets[f"{value.__module__}.{value.__qualname__}"] = value
    return targets, failed


def user_targets() -> Dict[str, Any]:
    """User-like classes and functions executed from source: comprehensions, closures, try/except, match, async."""
    source = (
        "import functools\n"
        "class Worker:\n    retries = 3\n    def run(self, x: int) -> list:\n"
        "        try:\n            return [v * x for v in range(4) if v]\n        except ValueError:\n"
        "            return []\n    async def fetch(self, n):\n        return n\n"
        "    def pick(self, v):\n        match v:\n            case 1:\n                return 'one'\n"
        "            case _:\n                return 'many'\n"
        "def make(n):\n    def inner(y):\n        return y + n\n    return inner\n"
        "Lambda = lambda q, k=2: q ** k\n")
    space: Dict[str, Any] = {"__name__": "userworld"}
    exec(source, space)
    return {"userworld.Worker": space["Worker"], "userworld.make": space["make"],
            "userworld.make(3)": space["make"](3), "userworld.Lambda": space["Lambda"]}


def main(out_path: str) -> None:
    """Digest every target with one SpellCodeDigest and write the sorted lines; print the build and a summary."""
    targets, failed = collect()
    targets.update(user_targets())
    digest = SpellCodeDigest()
    rows: List[str] = []
    try:
        for name in sorted(targets):
            try:
                rows.append(f"{name}\t{digest.spell_id(targets[name])}")
            except Exception as error:  # report, do not stop
                rows.append(f"{name}\tERROR:{type(error).__name__}")
    finally:
        digest.cleanup()
    text = "\n".join(rows) + "\n"
    pathlib.Path(out_path).write_text(text, encoding="utf-8")
    print(sys.version.split()[0], "free_threaded_build=" + str(sysconfig.get_config_var("Py_GIL_DISABLED")),
          "gil_enabled=" + str(sys._is_gil_enabled()), "cache_tag=" + str(sys.implementation.cache_tag),
          "targets=" + str(len(rows)), "errors=" + str(sum("ERROR:" in row for row in rows)),
          "failed_imports=" + str(len(failed)), "sha256=" + hashlib.sha256(text.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main(sys.argv[1])

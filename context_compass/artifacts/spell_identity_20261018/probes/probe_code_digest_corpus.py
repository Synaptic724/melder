"""Probe (melder_0, 2026-10-18; STORY-2026-10-18-spell_id_hashes_the_object_code): the code digest v2 over a large
real corpus - every class and function Melder's own package defines - for three answers: does it digest every
target without raising, are the digests identical across hash seeds and GIL modes, and what does it cost against
the fingerprint bind computes today (`Bind.spell_id_inspector`)?

Melder's own classes stand in for user code here (they cannot be bound; the inspector does not check that). Timing
per target: "cold" uses a fresh CodeDigest (nothing memoized), "warm" one shared CodeDigest on its second pass
(code-object digests memoized), "today" the current inspector. Writes "<qualified name>\t<digest>" lines, sorted,
to the file given as the first argument, for comparison across runs.
    PYTHONPATH=<repo>/src PYTHONHASHSEED=1 python -X gil=0 probe_code_digest_corpus.py ../runs/corpus_gil0_seed1.tsv
"""
import importlib
import inspect
import pathlib
import statistics
import sys
import time
import types

import melder
from code_digest_v2 import CodeDigest
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence


def collect() -> tuple:
    """Every class and plain function defined by an importable melder module, by qualified name."""
    targets, failed = {}, []
    # Most melder directories are namespace packages (no __init__.py), which pkgutil does not walk: list the files.
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


def timed(function, target) -> tuple:
    start = time.perf_counter_ns()
    try:
        result = function(target)
    except Exception as error:  # report, do not stop
        result = "ERROR:" + type(error).__name__ + ":" + str(error)[:80]
    return result, (time.perf_counter_ns() - start) / 1000.0


def summary(label: str, costs: dict) -> None:
    values = sorted(costs.values())
    worst = max(costs, key=costs.get)
    print(f"{label:<6} n={len(values)} total={sum(values) / 1000:.1f} ms median={statistics.median(values):.1f} us "
          f"p95={values[int(len(values) * 0.95)]:.1f} us max={values[-1]:.1f} us ({worst})")


def main() -> None:
    targets, failed = collect()
    print(f"modules not imported: {len(failed)}" + ("".join("\n    " + line for line in failed)))
    cold, warm, now, digests, errors = {}, {}, {}, {}, []
    shared = CodeDigest()
    for name, target in targets.items():
        digests[name], cold[name] = timed(lambda t: CodeDigest().spell_id(t), target)
        shared.spell_id(target)
    for name, target in targets.items():
        _, warm[name] = timed(shared.spell_id, target)
        spell_name = getattr(target, "__name__", None)
        _, now[name] = timed(lambda t: Bind.spell_id_inspector(t, spell_name=spell_name, existence=Existence.unique),
                             target)
        if digests[name].startswith("ERROR"):
            errors.append(f"{name}: {digests[name]}")
    classes = sum(1 for target in targets.values() if inspect.isclass(target))
    print(f"targets: {len(targets)} ({classes} classes, {len(targets) - classes} functions); digest errors: {len(errors)}")
    for line in errors[:20]:
        print("    " + line)
    summary("cold", cold)
    summary("warm", warm)
    summary("today", now)
    with open(sys.argv[1], "w", encoding="utf-8") as handle:
        for name in sorted(digests):
            handle.write(f"{name}\t{digests[name]}\n")
    print(f"digests written: {len(digests)} -> {sys.argv[1]}")


if __name__ == "__main__":
    main()

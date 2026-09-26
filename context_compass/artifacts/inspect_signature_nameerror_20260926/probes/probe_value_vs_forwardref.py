"""Compare str(VALUE signature) with str(FORWARDREF signature) wherever VALUE succeeds.

Usage: python -X gil=0 probe_value_vs_forwardref.py <src_root>
"""
import annotationlib, collections, importlib, inspect, pkgutil, sys, traceback, typing
sys.path.insert(0, sys.argv[1])
import melder
mods, import_errors = [], []
import pathlib
src_root = pathlib.Path(sys.argv[1])
for path in sorted((src_root / "melder").rglob("*.py")):
    if "__pycache__" in path.parts:
        continue
    rel = path.relative_to(src_root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    name = ".".join(parts)
    try:
        mods.append(importlib.import_module(name))
    except Exception as exc:
        import_errors.append((name, f"{type(exc).__name__}: {exc}"))
seen = set()
targets = []  # (qualname, obj, owner_module, public)
for mod in mods:
    for name, obj in vars(mod).items():
        if getattr(obj, "__module__", None) != mod.__name__:
            continue
        if inspect.isclass(obj):
            key = id(obj)
            if key in seen: continue
            seen.add(key)
            targets.append((f"{mod.__name__}.{obj.__qualname__}", obj, mod.__name__, not name.startswith("_"), "class"))
            for mname, member in vars(obj).items():
                fn = member
                if isinstance(member, (staticmethod, classmethod)):
                    fn = member.__func__
                elif isinstance(member, property):
                    fn = member.fget
                if inspect.isfunction(fn):
                    targets.append((f"{mod.__name__}.{obj.__qualname__}.{mname}", fn, mod.__name__,
                                    not name.startswith("_") and not mname.startswith("_") or mname == "__init__", "method"))
        elif inspect.isfunction(obj):
            targets.append((f"{mod.__name__}.{obj.__qualname__}", obj, mod.__name__, not name.startswith("_"), "function"))

import re
addr = re.compile(r"0x[0-9a-f]+")
same = diff_addr = diff_noaddr = 0
ex = []
for qual, obj, modname, public, kind in targets:
    try:
        v = str(inspect.signature(obj))
    except Exception:
        continue
    f = str(inspect.signature(obj, annotation_format=annotationlib.Format.FORWARDREF))
    if v == f:
        same += 1
    elif addr.search(f):
        diff_addr += 1; ex.append(("addr", qual, f[:160]))
    else:
        diff_noaddr += 1; ex.append(("noaddr", qual, v[:120] + " || " + f[:120]))
print(f"VALUE ok: identical={same} forwardref_differs_with_address={diff_addr} forwardref_differs_no_address={diff_noaddr}")
for e in ex[:12]:
    print("  ", e)

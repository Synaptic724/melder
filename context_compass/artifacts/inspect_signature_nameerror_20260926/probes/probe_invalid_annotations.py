"""List Melder callables whose annotations raise something other than NameError in every format.

Usage: python -X gil=0 probe_invalid_annotations.py <src_root>
A TypeError raised while evaluating an annotation (for example `"Conduit" | None`) is a defect in
the annotation itself: no annotation format can read it.
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

bad = []
for qual, obj, modname, public, kind in targets:
    try:
        inspect.signature(obj, annotation_format=annotationlib.Format.FORWARDREF)
    except (ValueError, TypeError) as exc:
        if "unsupported operand" in str(exc) or "|" in str(exc):
            bad.append((qual, f"{type(exc).__name__}: {exc}"))
    except Exception as exc:
        bad.append((qual, f"{type(exc).__name__}: {exc}"))
print(f"callables={len(targets)} invalid_annotations={len(bad)}")
for q, e in bad:
    print("  ", q, "->", e)

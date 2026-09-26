"""Validate SignatureReflection (display_signature, stabilize_signature, class_annotations) over every Melder callable and class.

Usage: python -X gil=0 probe_display_equivalence.py <src_root_with_helper>
For each target: when VALUE-format inspect.signature succeeds, str(display_signature) must equal it;
when it raises NameError, display_signature must succeed and render no ForwardRef or address.
Class annotations: when cls.__annotations__ evaluates, class_annotations(cls) must equal it.
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

from melder.utilities.helpers.signature_reflection import SignatureReflection as SR
import re
addr = re.compile(r"0x[0-9a-f]+")
same = differ = recovered = bad_render = display_fail = stab_differ = stab_bad = 0
examples = []
for qual, obj, modname, public, kind in targets:
    try:
        value_text = str(inspect.signature(obj))
    except NameError:
        value_text = None
    except (ValueError, TypeError):
        continue
    try:
        text = str(SR.display_signature(obj))
        fr = inspect.signature(obj, annotation_format=annotationlib.Format.FORWARDREF)
        stable_text = str(SR.stabilize_signature(fr, obj))
    except Exception as exc:
        display_fail += 1; examples.append(("display_fail", qual, repr(exc))); continue
    if value_text is not None and stable_text != value_text:
        stab_differ += 1; examples.append(("stabilize_differs_from_value", qual, value_text[:100] + " || " + stable_text[:100]))
    if "owner=" in stable_text:
        stab_bad += 1; examples.append(("stabilize_bad", qual, stable_text[:160]))
    if value_text is None:
        recovered += 1
        if "owner=" in text:
            bad_render += 1; examples.append(("bad_render", qual, text))
    elif value_text == text:
        same += 1
    else:
        differ += 1; examples.append(("differ", qual, value_text + " || " + text))
ann_same = ann_differ = ann_recovered = ann_bad = 0
for qual, obj, modname, public, kind in targets:
    if kind != "class":
        continue
    try:
        value = dict(obj.__annotations__)
    except NameError:
        value = None
    except AttributeError:
        value = {}
    got = SR.class_annotations(obj)
    if value is None:
        ann_recovered += 1
        if any("owner=" in repr(v) for v in got.values()):
            ann_bad += 1; examples.append(("ann_bad", qual, repr(got)))
    elif value == got:
        ann_same += 1
    else:
        ann_differ += 1; examples.append(("ann_differ", qual, repr(value)[:150] + " || " + repr(got)[:150]))
print(f"callables={len(targets)} display_signature: identical_to_VALUE={same} differ={differ} recovered_from_NameError={recovered} bad_render={bad_render} failures={display_fail}")
print(f"stabilize_signature(FORWARDREF): differs_from_VALUE={stab_differ} renders_owner_or_address={stab_bad}")
print(f"class annotations: identical={ann_same} differ={ann_differ} recovered={ann_recovered} bad={ann_bad}")
for e in examples[:20]:
    print("  ", e)

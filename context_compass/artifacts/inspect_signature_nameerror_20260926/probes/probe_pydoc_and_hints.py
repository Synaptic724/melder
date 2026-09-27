"""External-tool view: pydoc/help() and typing.get_type_hints on Melder's public API.

Usage: python -X gil=0 probe_pydoc_and_hints.py <src_root>
"""
import pydoc
import sys
import typing

sys.path.insert(0, sys.argv[1])
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402

for obj in (Aether, Conduit, Aether.get_conduit_by_name):
    name = getattr(obj, "__qualname__", repr(obj))
    try:
        pydoc.render_doc(obj, renderer=pydoc.plaintext)
        print(f"pydoc {name}: OK")
    except Exception as exc:
        print(f"pydoc {name}: RAISED {type(exc).__name__}: {exc}")
try:
    typing.get_type_hints(Aether.get_conduit_by_name)
    print("get_type_hints: OK")
except Exception as exc:
    print(f"get_type_hints: RAISED {type(exc).__name__}: {exc}")

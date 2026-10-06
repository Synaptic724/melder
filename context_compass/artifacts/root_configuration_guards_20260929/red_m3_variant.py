"""Build the M3 red tree: reverse every hunk of apply_m3_conjure_refusal_order.py in a copy of the landed source
(melder_0, 2026-09-30). Usage: python red_m3_variant.py <artifact_dir> <variant_src_root>
"""
import ast
import pathlib
import sys

ARTIFACTS = pathlib.Path(sys.argv[1])
SRC = pathlib.Path(sys.argv[2])

tree = ast.parse((ARTIFACTS / "apply_m3_conjure_refusal_order.py").read_text(encoding="utf-8"))
constants = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        constants[node.targets[0].id] = node.value.value
pairs = [
    (constants["SETTLE_DOC_OLD"], constants["SETTLE_DOC_NEW"]),
    (constants["HELPERS_ANCHOR"], constants["HELPERS_NEW"]),
    (constants["CONJURE_DOC_OLD"], constants["CONJURE_DOC_NEW"]),
    (constants["CONJURE_BODY_OLD"], constants["CONJURE_BODY_NEW"]),
    (constants["WINDOW_DOC_OLD"], constants["WINDOW_DOC_NEW"]),
    (constants["WINDOW_BODY_OLD"], constants["WINDOW_BODY_NEW"]),
]
path = SRC / "melder/aether/spellbook/spellbook.py"
raw = path.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
for old, new in pairs:
    assert text.count(new) == 1, new[:70]
    text = text.replace(new, old, 1)
path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("reverted spellbook.py to pre-M3")

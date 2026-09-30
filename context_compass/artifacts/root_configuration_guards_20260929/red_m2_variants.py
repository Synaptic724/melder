"""Build the two red trees for M2 from a copy of the landed source (melder_0, 2026-09-30).

pre_m2:      nexus.py guard reverted AND restore stage 4 reverted (the 0.2.8208 behaviour).
no_stage4:   the nexus.py guard kept, restore stage 4 reverted (proves stage 4 is needed).

Each variant reverses the exact OLD/NEW constants of the apply scripts, so the red source differs from the
landed source only in those hunks. Usage: python red_m2_variants.py <artifact_dir> <variant_src_root> <variant>
"""
import ast
import pathlib
import sys

ARTIFACTS = pathlib.Path(sys.argv[1])
SRC = pathlib.Path(sys.argv[2])
VARIANT = sys.argv[3]


def constants(script_name: str) -> dict:
    """Return the module-level string constants of one apply script."""
    tree = ast.parse((ARTIFACTS / script_name).read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                found[node.targets[0].id] = node.value.value
    return found


def reverse(relative: str, pairs: list) -> None:
    """Swap each NEW hunk back to its OLD text in one file, keeping its line endings."""
    path = SRC / relative
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert text.count(new) == 1, (relative, new[:60])
        text = text.replace(new, old, 1)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("reverted", relative)


guard = constants("apply_m2_nexus_active_guard.py")
stage4 = constants("apply_m2_restore_stage4.py")
reverse("melder/crystallizer/crystal_loader_system/restore_engine.py",
        [(stage4["DOC_OLD"], stage4["DOC_NEW"]), (stage4["CODE_OLD"], stage4["CODE_NEW"])])
if VARIANT == "pre_m2":
    reverse("melder/nexus/nexus.py",
            [(guard["CONFIGURE_OLD"], guard["CONFIGURE_NEW"]), (guard["ACTIVATE_OLD"], guard["ACTIVATE_NEW"])])
elif VARIANT != "no_stage4":
    raise SystemExit("unknown variant " + VARIANT)

"""Part 7 of the scope-exit dispose lane: correct the landing version named in docstrings.

The docstrings written for this change say 0.2.8201, the notch fable_0's meld entry cache took first;
the change landed at 0.2.8203. Docstring text only. Every edit is anchored on its full context string,
must match exactly once, and keeps the file's bytes (BOM, line endings) otherwise unchanged.

Usage: python apply_7_version_text.py <repository root>
"""
import pathlib
import sys

EDITS = [
    ("src/melder/aether/conduit/conduit.py",
     b"disposal failure is raised as one ExceptionGroup (since 0.2.8201;"),
    ("src/melder/aether/conduit/conduit.py",
     b"changes (changed 0.2.8201; `with conduit:` used to hold the conduit"),
    ("src/melder/utilities/general_base/cleanable.py",
     b"0.2.8201; it used to be swallowed). When the block raised too,"),
    ("src/melder/utilities/general_base/cleanable.py",
     b"(changed 0.2.8201; it used to be swallowed), chained to the"),
    ("tests/unit/melder/aether/conduit/test_conduit_lifecycle.py",
     b"Verify `with conduit:` is a dispose scope (0.2.8201; it used to hold the lock)."),
    ("tests/integration/melder/conduit/test_conduit_integration_public_api.py",
     b"Validate `with conduit:` as a dispose scope on a root conduit (0.2.8201)."),
    ("tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py",
     b"raises the failure as an ExceptionGroup (since 0.2.8201; it used to only log"),
]


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    by_file = {}
    for rel, anchor in EDITS:
        by_file.setdefault(rel, []).append(anchor)
    for rel, anchors in by_file.items():
        path = root / rel
        data = path.read_bytes()
        for anchor in anchors:
            count = data.count(anchor)
            if count != 1:
                raise SystemExit(f"{rel}: anchor found {count} times: {anchor!r}")
            data = data.replace(anchor, anchor.replace(b"0.2.8201", b"0.2.8203"))
        if b"0.2.8201" in data:
            raise SystemExit(f"{rel}: 0.2.8201 still present after the edits")
        if rel.endswith(".py"):
            compile(data, str(path), "exec")
        path.write_bytes(data)
        print("edited", rel, len(anchors))


if __name__ == "__main__":
    main()

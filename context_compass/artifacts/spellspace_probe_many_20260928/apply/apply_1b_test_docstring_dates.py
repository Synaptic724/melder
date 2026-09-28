"""After apply_1_tests.py: date the fix in the new test docstrings instead of naming a version.

The version is read at landing, so docstrings name the fix date (2026-09-28). Run from the repository root.
"""
import pathlib

EDITS = {
    "tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py": [
        ("    from, so the probe counts that bucket. Before 0.2.8204 it read the owner\r\n"
         "    conduit's store and missed what the space held.\r\n",
         "    from, so the probe counts that bucket. Before the 2026-09-28 fix it read\r\n"
         "    the owner conduit's store and missed what the space held.\r\n"),
    ],
    "tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py": [
        ("          store and counted by the space door's probe (before 0.2.8204 the probe\r\n"
         "          read the owner conduit's store and reported none).\r\n",
         "          store and counted by the space door's probe (before the 2026-09-28\r\n"
         "          fix the probe read the owner conduit's store and reported none).\r\n"),
    ],
}
for path, pairs in EDITS.items():
    p = pathlib.Path(path)
    text = p.read_bytes().decode("utf-8")
    for old, new in pairs:
        assert text.count(old) == 1, (path, text.count(old))
        text = text.replace(old, new)
    p.write_bytes(text.encode("utf-8"))
print("docstrings dated")

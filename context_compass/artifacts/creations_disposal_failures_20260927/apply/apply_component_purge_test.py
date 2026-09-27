"""Update the component purge test that pinned the old stop-at-first-failure posture (melder_0, 2026-09-27)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eol_lines
replace_lines = eol_lines.replace_lines

path = os.path.join(sys.argv[1], "tests/component/melder/aether/conduit/test_conduit_component_purge.py")
edits = [
    ("""    Contract: Many runs newest-first; methods run in order. Failures from multiple
        objects are collected while successful objects still complete. Unrelated
        creations survive, and final cleanup does not repeat target disposal.
""", """    Contract: Many runs newest-first; methods run in order. Failures from multiple
        objects are collected while successful objects still complete, and since
        2026-09-27 a failing method no longer skips its object's later methods.
        Unrelated creations survive, and final cleanup does not repeat target disposal.
"""),
    ("""            (2, "first"),
            (1, "first"),
""", """            (2, "first"),
            (2, "second"),
            (1, "first"),
"""),
    ("""    assert len(events) == 7
""", """    assert len(events) == 8
"""),
]
for old, new in edits:
    print(replace_lines(path, old, new))

"""D-10: tests_components entries for the codegen file-posture tests (run from the repo root).

Targeted, asserted replacements only; re-read the document before running (melder_2's lane edits it too).
"""
import datetime
import pathlib

DOC = pathlib.Path("context_compass/system_docs/tests_components.md")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "0.2.8269"
MODULE = pathlib.Path("tests/integration/melder/aether/test_codegen_core_boundary_integration.py")


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of `old`, or stop."""
    assert text.count(old) == 1, (text.count(old), old[:90])
    return text.replace(old, new)


loc = len(MODULE.read_text(encoding="utf-8").splitlines())
assert loc == 455, loc
text = DOC.read_text(encoding="utf-8")
assert "file postures, 2026-10-25" not in text, "already applied"

# --- Subcomponent: Aether Integration Cluster ------------------------------------------------
text = replace_once(
    text,
    "- what the codegen room's profiles stop around the core today (2026-10-10; a characterization, not\n"
    "  protection): an `import melder` statement refused under every standard profile but full_access, hybrid\n"
    "  refusing import statements of its denied roots, and two known gaps held as their profiles' documented\n"
    "  contracts under strict xfail - safe codegen writing files through the `open` builtin, and `__import__`\n"
    "  loading roots the hybrid profile and the precision overlay deny\n",
    "- what the codegen room's profiles stop around the core and what each does with files (2026-10-10, file\n"
    "  postures {v}; a characterization, not protection; 46 tests): an `import melder` statement refused under\n"
    "  every standard profile but full_access; hybrid refusing import statements of its denied roots; every\n"
    "  profile's file posture - `open` called to write or read, or only named, refused under safe, hybrid, the\n"
    "  precision overlay and the engine's default posture for a frame the room holds no projection for, and run\n"
    "  under permissive and full_access; `io.open`, `os.open` and pathlib writes following each profile's import\n"
    "  list (a pathlib write runs under hybrid) - with `test_safe_profile_refuses_writing_files`, the strict xfail\n"
    "  for this gap (D-10) until {v}, passing; and one known gap held as its profiles' documented contract under\n"
    "  strict xfail, `__import__` loading roots the hybrid profile and the precision overlay deny\n".format(v=VERSION),
)
text = replace_once(
    text,
    "- `tests/integration/melder/aether/test_codegen_core_boundary_integration.py` (characterization, 2026-10-10)\n",
    "- `tests/integration/melder/aether/test_codegen_core_boundary_integration.py` (characterization, 2026-10-10;\n"
    "  file postures, 2026-10-25)\n",
)

# --- Subcomponent: Aether/Nexus/Rift Unit Cluster --------------------------------------------
anchor = (
    "  object; both rooms advertise `get_spell_by_spell_id` and keep no `get_spell_by_id`\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/aether/test_nexus.py`\n"
)
text = replace_once(
    text,
    anchor,
    "  object; both rooms advertise `get_spell_by_spell_id` and keep no `get_spell_by_id`\n"
    "- the codegen presets' `open` posture ({v}, D-10): the compiled deny list carries `open` for safe (the\n"
    "  default profile), hybrid and every chain with the precision overlay, and not for permissive or full_access\n"
    "  (`test_frame_acl_codegen_validation_profiles.py`); the engine's no-projection default denies `__import__`\n"
    "  plus exactly the safe tuple, imports off (`test_codegen_system_unit_matrix.py`); and runtime builtins built\n"
    "  from the safe tuple carry no `open` (`test_codegen_namespace_runtime_unit_matrix.py`)\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/aether/test_nexus.py`\n".format(v=VERSION),
)

# --- C1 Code Map ---------------------------------------------------------------------------------
text = replace_once(
    text,
    "- path: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`\n  start_line: 1\n"
    "  end_line: 206\n  loc: 206\n  verified_at: 2026-10-10T12:34:42Z\n"
    "  note: codegen import gate around melder and two strict-xfail profile gaps (open writes, __import__).\n",
    "- path: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`\n  start_line: 1\n"
    "  end_line: {loc}\n  loc: {loc}\n  verified_at: {now}\n"
    "  note: codegen import gate around melder, every profile's file posture (open, io, os, pathlib; the\n"
    "    no-projection default) and one strict-xfail gap (__import__).\n".format(loc=loc, now=NOW),
)

# --- Information Sources (append) --------------------------------------------------------------
last = (
    "- `tests/integration/melder/conduit/test_conduit_integration_holder_cleanup_leaves_its_many_children.py`\n"
    "\n## Open Questions\n"
)
text = replace_once(
    text,
    last,
    "- `tests/integration/melder/conduit/test_conduit_integration_holder_cleanup_leaves_its_many_children.py`\n"
    "- `tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py`\n"
    "- `tests/unit/melder/aether/test_codegen_system_unit_matrix.py`\n"
    "- `tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py`\n"
    "\n## Open Questions\n",
)

# --- Context / Handoff Summary (one dated entry at the top) ----------------------------------
HANDOFF = """2026-10-25 the codegen presets' file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10): the Aether Integration Cluster's codegen entry pins every profile's file posture in
`test_codegen_core_boundary_integration.py` (46 tests, D-11's four strict xfails among them) - `open` called or
named refused under safe, hybrid, the precision overlay and the engine's no-projection default and run under
permissive and full_access; `io.open`, `os.open` and pathlib writes following each import list - and
`test_safe_profile_refuses_writing_files` passes without the strict xfail it carried since 2026-10-10. The
Aether/Nexus/Rift Unit Cluster protects the compiled `open` deny per preset, the no-projection default and the
runtime builtins of the safe tuple (new tests in three existing modules, named in its entry and in Information
Sources). The core map remeasures the integration module (455); the key-file union stays 283 paths, and this lane
adds no module, so the counts are unchanged.

""".format(v=VERSION)
text = replace_once(text, "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + HANDOFF)

DOC.write_text(text, encoding="utf-8")
print("tests_components updated at", NOW, "-", len(text.splitlines()), "lines")

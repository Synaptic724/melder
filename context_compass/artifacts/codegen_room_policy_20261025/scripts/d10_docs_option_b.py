"""D-10: the docs follow option B and the notch number moves to 0.2.8270 (run from the repo root).

melder_1 took 0.2.8269 (M1-64), so this lane's entries are retagged; only this lane's own text is touched. The old
text of each block is rebuilt from the scripts that wrote it, so every replacement is an exact, asserted match.
"""
import ast
import datetime
import pathlib

SCRIPTS = pathlib.Path("context_compass/artifacts/codegen_room_policy_20261025/scripts")
DOCS = pathlib.Path("context_compass/system_docs")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD_V, NEW_V = "0.2.8269", "0.2.8270"


def constants(script: str) -> dict:
    """Return the module-level string constants of one earlier script."""
    tree = ast.parse((SCRIPTS / script).read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            value = node.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr == "format":
                value = value.func.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                found[node.targets[0].id] = value.value
    return found


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of `old`, or stop."""
    assert text.count(old) == 1, (text.count(old), old[:100])
    return text.replace(old, new)


# --- src_architecture ------------------------------------------------------------------------------
arch_old = constants("d10_src_architecture.py")
INVARIANT = """- Codegen presets hold their file posture (2026-10-25, {v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
  which closes defect D-10, on the owner's decisions in chat, 2026-10-25: deny `open` under safe, hybrid and precision,
  keep permissive and full_access open, and "focus on B" for hybrid's `pathlib`): the safe, hybrid and precision
  codegen presets - a frame's profile, or precision as its overlay - deny the builtins of one tuple,
  `SAFE_DENIED_BUILTIN_NAMES`, and `open` is on it. Room code under those presets that calls `open` is refused at
  validation by the builtin gate ("Builtin 'open' is not allowed in this codegen mode."), code that only names it is
  refused by name resolution ("Name 'open' is not available in the codegen namespace."), and the room's runtime
  `__builtins__` leaves it out, so a form the static gates miss fails when it runs. A request naming a frame the room
  holds no codegen projection for runs under the engine's default posture, which denies `__import__` plus that same
  tuple, read from the preset module rather than copied, so the default cannot fall behind safe again. Permissive and
  full_access keep `open`: their file posture is open by design. The other file routes follow the import lists: safe
  refuses every import, and `io`, `os` and `pathlib` are permissive extras that no other preset's list admits -
  `pathlib` is not on the common list hybrid uses, so hybrid refuses `import pathlib`, path arithmetic included. Each
  preset's docstring states its file posture. The compiled deny list is the union of the denies of the preset, the
  precision overlay and the frame's codegen capability override, minus the union of their allows, so a
  `builtin_names` allow rule in a frame's override still re-allows `open` for that frame. This is policy checked in
  the room's own process - defence in depth, not isolation. Nothing persisted, cached or recorded reads the deny or
  import lists (each projection compiles its own), so no cache generation or record version moves. Locks: none
  added; the tuples are immutable module values read at each compile and at each no-projection request.
  EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,
  `_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS`,
  `src/melder/nexus/acl/frame_acl_compiler.py:FrameACLCompiler._compile_codegen_builtin_controls`,
  `src/melder/nexus/rift/codegen_system/codegen_system.py:CodegenSystem._build_default_namespace_configuration`,
  `CodegenSystem._try_get_codegen_projection`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:CodegenBuiltinPolicyStrategy.validate`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:CodegenNameResolutionStrategy.validate`
  and `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:CodegenBuiltinsStrategy.build_namespace_entries`.
""".format(v=NEW_V)
FAILURE = """- Breaking ({v}): code run in a codegen room under the safe, hybrid or precision preset - or in any room, for a
  request naming a frame the room holds no codegen projection for - that calls `open` is refused at validation:
  `validate_codegen` and `execute_codegen` answer `accepted` False with "Builtin 'open' is not allowed in this
  codegen mode.", or with "Name 'open' is not available in the codegen namespace." for a bare reference (`reader =
  open`), and nothing runs; `open` is gone from the room's runtime builtins. Under hybrid `import pathlib` is refused
  too, with "Import root 'pathlib' is not allowed in this codegen mode.". Through {p} every preset ran `open`, which
  read or wrote any file the process could reach - under safe too, whose posture says it denies writes - and hybrid
  ran pathlib writes. Code that must use files runs under the permissive or full_access preset.
  EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,
  `_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS` and
  `src/melder/nexus/rift/codegen_system/codegen_system.py:CodegenSystem._build_default_namespace_configuration`.
""".format(v=NEW_V, p=OLD_V)
HANDOFF = """2026-10-25 codegen presets hold their file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10, on the owner's decisions): `open` joins the denied-builtin tuple the safe, hybrid and precision presets
share, so their room code is refused at validation when it calls or names `open` and finds no `open` in its runtime
builtins, and the engine's no-projection default posture reads that tuple instead of keeping its own copy; `pathlib`
becomes a permissive extra, so hybrid refuses `import pathlib`; permissive and full_access keep `open`, and each
preset's docstring states its file posture. A new operational invariant, a Breaking failure mode, the code map
(codegen_system.py remeasured) and the sources carry it; the component map carries the per-component contracts.
Still unknown: see Unknowns. Where to start: src_components, Component: Nexus Descriptor And ACL Managers (the
presets' file posture) and Component: Codegen Internal Engine (the default posture).

""".format(v=NEW_V)
path = DOCS / "src_architecture.md"
text = path.read_text(encoding="utf-8")
text = replace_once(text, arch_old["INVARIANT"].format(v=OLD_V), INVARIANT)
text = replace_once(text, arch_old["FAILURE"].format(v=OLD_V), FAILURE)
text = replace_once(text, arch_old["HANDOFF"].format(v=OLD_V), HANDOFF)
path.write_text(text, encoding="utf-8")

# --- src_components --------------------------------------------------------------------------------
comp_old = constants("d10_src_components.py")
path = DOCS / "src_components.md"
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "  posture ({o}): imports off; no unsafe reflection, dunder access or recursive codegen; and the\n".format(o=OLD_V),
    "  posture ({v}): imports off; no unsafe reflection, dunder access or recursive codegen; and the\n".format(v=NEW_V),
)
text = replace_once(text, "  `__builtins__` holds no `open` ({o})\n".format(o=OLD_V),
                    "  `__builtins__` holds no `open` ({v})\n".format(v=NEW_V))
presets_old = comp_old["PRESETS"].format(v=OLD_V)
presets_new = presets_old.replace(
    "Codegen presets' file posture ({o}):\n".format(o=OLD_V),
    "Codegen presets' file posture ({v}):\n".format(v=NEW_V),
).replace(
    "- The file posture that follows, per preset: safe - no file access through builtins or imports (`open` denied,\n"
    "  imports off); hybrid - `open` denied, `io` and `os` off its allow list and `pathlib` on it, so a `pathlib.Path`\n"
    "  write runs; precision, alone or as the overlay - `open` denied and none of `io`, `os` or `pathlib` on its list;\n"
    "  permissive and full_access - open by design, `open` kept and `io`, `os` and `pathlib` importable. Each preset's\n"
    "  docstring states its posture.\n",
    "- The file posture that follows, per preset: safe - `open` denied and imports off, so `io`, `os` and `pathlib` are\n"
    "  refused too; hybrid and precision (alone or as the overlay) - `open` denied and none of `io`, `os` or `pathlib`\n"
    "  on their allow lists, since the three are permissive extras, not common roots; permissive and full_access - open\n"
    "  by design, `open` kept and `io`, `os` and `pathlib` importable. Each preset's docstring states its posture.\n",
).replace(
    "- EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,\n",
    "- EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,\n"
    "  `_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS`,\n",
)
assert presets_new != presets_old and presets_new.count(NEW_V) == 1 and "pathlib` on it" not in presets_new
text = replace_once(text, presets_old, presets_new)
text = replace_once(text, "  `SAFE_DENIED_BUILTIN_NAMES` denied ({o})\n".format(o=OLD_V),
                    "  `SAFE_DENIED_BUILTIN_NAMES` denied ({v})\n".format(v=NEW_V))
handoff_old = comp_old["HANDOFF"].format(v=OLD_V)
handoff_new = """2026-10-25 codegen presets hold their file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10). What component contracts changed: Nexus Descriptor And ACL Managers gains the presets' file posture -
`open` is on `SAFE_DENIED_BUILTIN_NAMES`, the denied-builtin tuple safe, hybrid and precision share, so their room
code is refused at validation when it calls or names `open` and finds no `open` in its runtime builtins; `io`, `os`
and `pathlib` are permissive extras, so hybrid refuses `import pathlib`; how the compiler unites and subtracts the
denied builtins (an override's allow rule re-allows a name) and intersects the import allow lists; each preset's
posture for `open`, `io`, `os` and `pathlib`; and the refusal texts. Codegen Internal Engine and its CodegenSystem
subcomponent say a request without a projection runs under the safe posture, the safe tuple read from the presets'
module instead of a copy, and the refusals it meets. codegen_system.py grew eight lines (an import and the
default's docstring): its numeric citations moved three lines and point at `validate_codegen_request`,
`execute_codegen_request` and the instance lock again, and the code map remeasures it; stdlib_import_sets.py gained
a module docstring, so the Full Package Inventory carries its purpose instead of UNKNOWN; Information Sources adds
the six source files these entries cite. Still unknown: the Unknowns section, unchanged. Verify next: Codegen
Internal Engine - whether a request naming a frame without a projection should run at all (out of D-10's scope),
and the dynamic-import gap (D-11) beside these entries.

""".format(v=NEW_V)
text = replace_once(text, handoff_old, handoff_new)
path.write_text(text, encoding="utf-8")

# --- tests_components ------------------------------------------------------------------------------
tests_old = constants("d10_tests_components.py")
module = pathlib.Path("tests/integration/melder/aether/test_codegen_core_boundary_integration.py")
loc = len(module.read_text(encoding="utf-8").splitlines())
assert loc == 456, loc
path = DOCS / "tests_components.md"
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "- the codegen presets' `open` posture ({o}, D-10): the compiled deny list carries `open` for safe (the\n"
    "  default profile), hybrid and every chain with the precision overlay, and not for permissive or full_access\n"
    "  (`test_frame_acl_codegen_validation_profiles.py`); the engine's no-projection default denies `__import__`\n"
    "  plus exactly the safe tuple, imports off (`test_codegen_system_unit_matrix.py`); and runtime builtins built\n"
    "  from the safe tuple carry no `open` (`test_codegen_namespace_runtime_unit_matrix.py`)\n".format(o=OLD_V),
    "- the codegen presets' file posture ({v}, D-10): the compiled deny list carries `open` for safe (the default\n"
    "  profile), hybrid and every chain with the precision overlay, and not for permissive or full_access, and\n"
    "  `pathlib` is an allowed import root of the permissive list only\n"
    "  (`test_frame_acl_codegen_validation_profiles.py`); the engine's no-projection default denies `__import__` plus\n"
    "  exactly the safe tuple, imports off (`test_codegen_system_unit_matrix.py`); and runtime builtins built from\n"
    "  the safe tuple carry no `open` (`test_codegen_namespace_runtime_unit_matrix.py`)\n".format(v=NEW_V),
)
text = replace_once(
    text,
    "- what the codegen room's profiles stop around the core and what each does with files (2026-10-10, file\n"
    "  postures {o}; a characterization, not protection; 46 tests): an `import melder` statement refused under\n"
    "  every standard profile but full_access; hybrid refusing import statements of its denied roots; every\n"
    "  profile's file posture - `open` called to write or read, or only named, refused under safe, hybrid, the\n"
    "  precision overlay and the engine's default posture for a frame the room holds no projection for, and run\n"
    "  under permissive and full_access; `io.open`, `os.open` and pathlib writes following each profile's import\n"
    "  list (a pathlib write runs under hybrid) - with `test_safe_profile_refuses_writing_files`, the strict xfail\n"
    "  for this gap (D-10) until {o}, passing; and one known gap held as its profiles' documented contract under\n"
    "  strict xfail, `__import__` loading roots the hybrid profile and the precision overlay deny\n".format(o=OLD_V),
    "- what the codegen room's profiles stop around the core and what each does with files (2026-10-10, file\n"
    "  postures {v}; a characterization, not protection; 46 tests): an `import melder` statement refused under\n"
    "  every standard profile but full_access; hybrid refusing import statements of its denied roots; every\n"
    "  profile's file posture - `open` called to write or read, or only named, refused under safe, hybrid, the\n"
    "  precision overlay and the engine's default posture for a frame the room holds no projection for, and run\n"
    "  under permissive and full_access; `io.open`, `os.open` and pathlib writes following each profile's import\n"
    "  list, so only permissive and full_access run them - with `test_safe_profile_refuses_writing_files`, the\n"
    "  strict xfail for this gap (D-10) until {v}, passing; and one known gap held as its profiles' documented\n"
    "  contract under strict xfail, `__import__` loading roots the hybrid profile and the precision overlay deny\n"
    .format(v=NEW_V),
)
old_map_head = "- path: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`\n  start_line: 1\n  end_line: 455\n  loc: 455\n  verified_at: "
assert text.count(old_map_head) == 1
start = text.index(old_map_head) + len(old_map_head)
stamp_end = text.index("\n", start)
text = text[:text.index(old_map_head)] + (
    "- path: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`\n  start_line: 1\n"
    "  end_line: {loc}\n  loc: {loc}\n  verified_at: {now}".format(loc=loc, now=NOW)
) + text[stamp_end:]
handoff_old = tests_old["HANDOFF"].format(v=OLD_V)
handoff_new = """2026-10-25 the codegen presets' file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10): the Aether Integration Cluster's codegen entry pins every profile's file posture in
`test_codegen_core_boundary_integration.py` (46 tests, D-11's four strict xfails among them) - `open` called or
named refused under safe, hybrid, the precision overlay and the engine's no-projection default and run under
permissive and full_access; `io.open`, `os.open` and pathlib writes following each import list, hybrid's included
now that `pathlib` is a permissive extra - and `test_safe_profile_refuses_writing_files` passes without the strict
xfail it carried since 2026-10-10. The Aether/Nexus/Rift Unit Cluster protects the compiled `open` deny per preset,
`pathlib` as a permissive-only import root, the no-projection default and the runtime builtins of the safe tuple
(new tests in three existing modules, named in its entry and in Information Sources). The core map remeasures the
integration module ({loc}); the key-file union stays 283 paths, and this lane adds no module, so the counts are
unchanged.

""".format(v=NEW_V, loc=loc)
text = replace_once(text, handoff_old, handoff_new)
path.write_text(text, encoding="utf-8")
print("docs follow option B and", NEW_V, "at", NOW)

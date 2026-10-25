"""D-10: src_components entries for the codegen presets' file posture (run from the repo root).

Targeted, asserted replacements only; re-read the document before running (other lanes edit it).
"""
import datetime
import pathlib

DOC = pathlib.Path("context_compass/system_docs/src_components.md")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "0.2.8269"


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of `old`, or stop."""
    assert text.count(old) == 1, (text.count(old), old[:90])
    return text.replace(old, new)


text = DOC.read_text(encoding="utf-8")
assert "Codegen presets' file posture" not in text, "already applied"

# --- Component: Codegen Internal Engine -------------------------------------------------------
text = replace_once(
    text,
    "  EVIDENCE: src/melder/nexus/rift/codegen_system/codegen_system.py:260\n"
    "  (`validate_codegen_request`), :295 (`execute_codegen_request`)\n",
    "  EVIDENCE: src/melder/nexus/rift/codegen_system/codegen_system.py:263\n"
    "  (`validate_codegen_request`), :298 (`execute_codegen_request`)\n",
)
text = replace_once(
    text,
    "- room-memory emission stays on `CodegenCommandSystem`, not the engine root\n",
    "- room-memory emission stays on `CodegenCommandSystem`, not the engine root\n"
    "- a request naming a frame the owning Rift holds no codegen projection for runs under the safe\n"
    "  posture ({v}): imports off; no unsafe reflection, dunder access or recursive codegen; and the\n"
    "  denied builtins `__import__` plus `SAFE_DENIED_BUILTIN_NAMES`, `open` among them, read from the\n"
    "  presets' module so this default follows safe (Component: Nexus Descriptor And ACL Managers carries\n"
    "  the presets' file posture)\n"
    "  EVIDENCE: `src/melder/nexus/rift/codegen_system/codegen_system.py:CodegenSystem._build_default_namespace_configuration`,\n"
    "  `CodegenSystem._try_get_codegen_projection` and\n"
    "  `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`\n"
    .format(v=VERSION),
)
text = replace_once(
    text,
    "- missing projection support degrades to `None` projection instead of failing\n"
    "  transaction construction\n",
    "- missing projection support degrades to `None` projection instead of failing\n"
    "  transaction construction\n"
    "- under that default, and under every projection whose compiled surface denies it, a call of `open` is\n"
    "  refused at validation (\"Builtin 'open' is not allowed in this codegen mode.\"), a bare reference by\n"
    "  name resolution (\"Name 'open' is not available in the codegen namespace.\"), and the runtime\n"
    "  `__builtins__` holds no `open` ({v})\n".format(v=VERSION),
)

# --- Component: Nexus Descriptor And ACL Managers --------------------------------------------
PRESETS = """Codegen presets' file posture ({v}):
- The five standard codegen presets - safe, hybrid, precision, permissive and full_access - state in their
  capability rulesets which builtins and import roots room code may use. Safe, hybrid and precision deny the
  builtins of one tuple, `SAFE_DENIED_BUILTIN_NAMES` (hybrid and precision alias it), and `open` is on it; the
  codegen engine's no-projection default reads the same tuple (Component: Codegen Internal Engine).
- `FrameACLCompiler` compiles a frame's denied builtins as the union of the denies of its preset, its precision
  overlay and its codegen capability override, minus the union of their allows, plus `__import__` when imports are
  off, sorted into `CompiledFrameACLAccessSurface.denied_builtin_names`; a `builtin_names` allow rule in the override
  therefore re-allows `open` for that frame. Import roots compile differently: the allow lists intersect, so the
  overlay narrows the preset's, and the deny lists unite.
- The file posture that follows, per preset: safe - no file access through builtins or imports (`open` denied,
  imports off); hybrid - `open` denied, `io` and `os` off its allow list and `pathlib` on it, so a `pathlib.Path`
  write runs; precision, alone or as the overlay - `open` denied and none of `io`, `os` or `pathlib` on its list;
  permissive and full_access - open by design, `open` kept and `io`, `os` and `pathlib` importable. Each preset's
  docstring states its posture.
- A refusal names what it refused: a call of a denied builtin - "Builtin 'open' is not allowed in this codegen
  mode." (the builtin gate); a bare reference - "Name 'open' is not available in the codegen namespace." (name
  resolution, which runs after the builtin gate); a refused import - "Import statements are not allowed in this
  codegen mode." under safe, "Import root '<root>' is not allowed in this codegen mode." under an allow list; and at
  run time the room's `__builtins__` holds no denied name. These are policy checks in the room's own process -
  defence in depth, not isolation.
- EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,
  `src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:SafeCodegenProfileStrategy.build`,
  `src/melder/nexus/acl/frame_acl_compiler.py:FrameACLCompiler._compile_codegen_builtin_controls`,
  `FrameACLCompiler._collect_import_module_roots_from_rulesets`,
  `src/melder/nexus/rift/codegen_system/validation/codegen_validator.py:CodegenValidator.validate`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:CodegenBuiltinPolicyStrategy.validate`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:CodegenNameResolutionStrategy.validate`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:CodegenImportPolicyStrategy`
  and `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:CodegenBuiltinsStrategy.build_namespace_entries`.

""".format(v=VERSION)
text = replace_once(
    text,
    "Responsibilities:\n- `FrameDescriptorManager` owns `frame_name -> FrameDescriptor`.\n",
    PRESETS + "Responsibilities:\n- `FrameDescriptorManager` owns `frame_name -> FrameDescriptor`.\n",
)

# --- Subcomponent: CodegenSystem Internal Engine ---------------------------------------------
text = replace_once(
    text,
    "- `_build_transaction_context(...)`\n- `_build_namespace(...)`\nInvariants/Guarantees:\n"
    "- validation precedes execution\n- namespace is built only after accepted validation\n",
    "- `_build_transaction_context(...)`\n- `_build_default_namespace_configuration(...)`\n"
    "- `_build_namespace(...)`\nInvariants/Guarantees:\n"
    "- validation precedes execution\n- namespace is built only after accepted validation\n"
    "- with no projection for the requested frame, the safe posture: imports off and `__import__` plus\n"
    "  `SAFE_DENIED_BUILTIN_NAMES` denied ({v})\n".format(v=VERSION),
)
text = replace_once(
    text,
    "  EVIDENCE: src/melder/nexus/rift/codegen_system/codegen_system.py:139\n",
    "  EVIDENCE: src/melder/nexus/rift/codegen_system/codegen_system.py:142\n",
)

# --- C1 Code Map ---------------------------------------------------------------------------------
text = replace_once(
    text,
    "- path: `src/melder/nexus/rift/codegen_system/codegen_system.py`\n  start_line: 1\n  end_line: 537\n"
    "  loc: 537\n  verified_at: 2026-10-25T01:07:42Z\n",
    "- path: `src/melder/nexus/rift/codegen_system/codegen_system.py`\n  start_line: 1\n  end_line: 545\n"
    "  loc: 545\n  verified_at: {now}\n".format(now=NOW),
)

# --- Full Package Inventory ------------------------------------------------------------------
text = replace_once(
    text,
    "- `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`\n"
    "  UNKNOWN - no module docstring, `__agent_purpose__`, or class docstring\n",
    "- `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`\n"
    "  The import roots and denied builtins the standard codegen presets read\n",
)

# --- Information Sources (sorted list; recount and re-resolve) ------------------------------
head = "Primary source files (286, all resolved 2026-10-25T01:07:42Z):\n\n"
assert text.count(head) == 1
start = text.index(head) + len(head)
end = text.index("\nCompanion documents:\n", start)
block = text[start:end]
entries = [line for line in block.split("\n") if line.startswith("- `")]
assert len(entries) == 286, len(entries)
added = [
    "src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py",
    "src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py",
    "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py",
    "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py",
    "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py",
    "src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py",
]
paths = [line[3:line.index("`", 3)] for line in entries]
for path in added:
    assert path not in paths, path
src_paths = sorted(p for p in paths + added if p.startswith("src/"))
other_paths = [p for p in paths if not p.startswith("src/")]
assert [p for p in paths if p.startswith("src/")] == sorted(p for p in paths if p.startswith("src/")), "unsorted"
missing = [p for p in src_paths + other_paths if not pathlib.Path(p).exists()]
assert not missing, missing
new_block = "\n".join("- `{0}`".format(p) for p in src_paths + other_paths) + "\n"
text = text[:start] + new_block + text[end:]
text = replace_once(
    text,
    head,
    "Primary source files ({n}, all resolved {now}):\n\n".format(n=len(src_paths) + len(other_paths), now=NOW),
)

# --- Context / Handoff Summary (one dated entry at the top) ----------------------------------
HANDOFF = """2026-10-25 codegen presets hold their file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10). What component contracts changed: Nexus Descriptor And ACL Managers gains the presets' file posture -
`open` is on `SAFE_DENIED_BUILTIN_NAMES`, the denied-builtin tuple safe, hybrid and precision share, so their room
code is refused at validation when it calls or names `open` and finds no `open` in its runtime builtins, how the
compiler unites and subtracts the denied builtins (an override's allow rule re-allows a name) and intersects the
import allow lists, each preset's posture for `open`, `io`, `os` and `pathlib`, and the refusal texts; Codegen
Internal Engine and its CodegenSystem subcomponent say a request without a projection runs under the safe posture,
the safe tuple read from the presets' module instead of a copy, and the refusals it meets. codegen_system.py grew
eight lines (an import and the default's docstring): its numeric citations moved three lines and point at
`validate_codegen_request`, `execute_codegen_request` and the instance lock again, and the code map remeasures it;
stdlib_import_sets.py gained a module docstring, so the Full Package Inventory carries its purpose instead of
UNKNOWN; Information Sources adds the six source files these entries cite. Still unknown: the Unknowns section,
unchanged. Verify next: Codegen Internal Engine - whether a request naming a frame without a projection should run
at all (out of D-10's scope), and the dynamic-import gap (D-11) beside these entries.

""".format(v=VERSION)
text = replace_once(text, "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + HANDOFF)

DOC.write_text(text, encoding="utf-8")
print("src_components updated at", NOW, "-", len(text.splitlines()), "lines;", len(src_paths) + len(other_paths),
      "primary source files")

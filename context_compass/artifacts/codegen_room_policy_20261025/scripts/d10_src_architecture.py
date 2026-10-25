"""D-10: src_architecture entries for the codegen presets' file posture (run from the repo root).

Targeted, asserted replacements only; re-read the document before running (other lanes edit it).
"""
import datetime
import pathlib

DOC = pathlib.Path("context_compass/system_docs/src_architecture.md")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "0.2.8269"

INVARIANT = """- Codegen presets hold their file posture (2026-10-25, {v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
  which closes defect D-10, on the owner's decision in chat, 2026-10-25: deny `open` under safe, hybrid and precision,
  and keep permissive and full_access open): the safe, hybrid and precision codegen presets - a frame's profile, or
  precision as its overlay - deny the builtins of one tuple, `SAFE_DENIED_BUILTIN_NAMES`, and `open` is on it. Room
  code under those presets that calls `open` is refused at validation by the builtin gate ("Builtin 'open' is not
  allowed in this codegen mode."), code that only names it is refused by name resolution ("Name 'open' is not
  available in the codegen namespace."), and the room's runtime `__builtins__` leaves it out, so a form the static
  gates miss fails when it runs. A request naming a frame the room holds no codegen projection for runs under the
  engine's default posture, which denies `__import__` plus that same tuple, read from the preset module rather than
  copied, so the default cannot fall behind safe again. Permissive and full_access keep `open`: their file posture
  is open by design. The other file routes follow the import lists: safe refuses every import, the hybrid and
  precision lists leave out `io` and `os`, and hybrid's admits `pathlib`, so a `pathlib.Path` write runs there while
  precision's list leaves `pathlib` out. Each preset's docstring states its file posture. The compiled deny list is
  the union of the denies of the preset, the precision overlay and the frame's codegen capability override, minus
  the union of their allows, so a `builtin_names` allow rule in a frame's override still re-allows `open` for that
  frame. This is policy checked in the room's own process - defence in depth, not isolation. Nothing persisted,
  cached or recorded reads the deny lists (each projection compiles its own), so no cache generation or record
  version moves. Locks: none added; the tuple is an immutable module value read at each compile and at each
  no-projection request.
  EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`,
  `src/melder/nexus/acl/frame_acl_compiler.py:FrameACLCompiler._compile_codegen_builtin_controls`,
  `src/melder/nexus/rift/codegen_system/codegen_system.py:CodegenSystem._build_default_namespace_configuration`,
  `CodegenSystem._try_get_codegen_projection`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:CodegenBuiltinPolicyStrategy.validate`,
  `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:CodegenNameResolutionStrategy.validate`
  and `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:CodegenBuiltinsStrategy.build_namespace_entries`.
""".format(v=VERSION)

FAILURE = """- Breaking ({v}): code run in a codegen room under the safe, hybrid or precision preset - or in any room, for a
  request naming a frame the room holds no codegen projection for - that calls `open` is refused at validation:
  `validate_codegen` and `execute_codegen` answer `accepted` False with "Builtin 'open' is not allowed in this
  codegen mode.", or with "Name 'open' is not available in the codegen namespace." for a bare reference (`reader =
  open`), and nothing runs; `open` is gone from the room's runtime builtins. Through 0.2.8268 every preset ran such
  code, which read or wrote any file the process could reach - under safe too, whose posture says it denies writes.
  Code that must use files runs under the permissive or full_access preset.
  EVIDENCE: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:SAFE_DENIED_BUILTIN_NAMES`
  and `src/melder/nexus/rift/codegen_system/codegen_system.py:CodegenSystem._build_default_namespace_configuration`.
""".format(v=VERSION)

HANDOFF = """2026-10-25 codegen presets hold their file posture ({v}; TASK-2026-10-10-deny-file-access-under-safe-codegen,
defect D-10, on the owner's decision): `open` joins the denied-builtin tuple the safe, hybrid and precision presets
share, so their room code is refused at validation when it calls or names `open` and finds no `open` in its runtime
builtins, and the engine's no-projection default posture reads that tuple instead of keeping its own copy;
permissive and full_access keep `open`, and each preset's docstring states its file posture. A new first
operational invariant, a Breaking failure mode, the code map (codegen_system.py remeasured) and the sources carry
it; the component map carries the per-component contracts. Still unknown: see Unknowns. Where to start:
src_components, Component: Nexus Descriptor And ACL Managers (the presets' file posture) and Component: Codegen
Internal Engine (the default posture).

""".format(v=VERSION)

SOURCES = """- `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py`
- `src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py`
- `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py`
- `src/melder/nexus/acl/frame_acl_compiler.py`
- `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`
"""


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of `old`, or stop."""
    assert text.count(old) == 1, (text.count(old), old[:80])
    return text.replace(old, new)


text = DOC.read_text(encoding="utf-8")
assert "Codegen presets hold their file posture" not in text, "already applied"
text = replace_once(text, "## Operational Invariants\n", "## Operational Invariants\n" + INVARIANT)
text = replace_once(text, "## Failure Modes and Error Paths\n", "## Failure Modes and Error Paths\n" + FAILURE)
old_map = """- path: `src/melder/nexus/rift/codegen_system/codegen_system.py`
  start_line: 1
  end_line: 537
  loc: 537
  verified_at: 2026-10-24T22:31:53Z
"""
new_map = """- path: `src/melder/nexus/rift/codegen_system/codegen_system.py`
  start_line: 1
  end_line: 545
  loc: 545
  verified_at: {now}
""".format(now=NOW)
text = replace_once(text, old_map, new_map)
src_line = "- `src/melder/nexus/rift/codegen_system/observability/codegen_event_publisher.py`\n"
text = replace_once(text, src_line, src_line + SOURCES)
text = replace_once(text, "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + HANDOFF)
DOC.write_text(text, encoding="utf-8")
print("src_architecture updated at", NOW, "-", len(text.splitlines()), "lines")

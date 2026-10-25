"""D-10: give stdlib_import_sets.py a module docstring (documentation only; run from the repo root)."""
import pathlib

PATH = pathlib.Path("src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py")
DOCSTRING = '''"""
The import roots and denied builtins the standard codegen presets read.

Purpose:
    Keep the name tuples the safe, hybrid, precision and permissive codegen presets put in their
    capability rulesets in one place, so presets that share a posture share one tuple and cannot
    drift apart.

Contract:
    - Values only: every public name is a tuple of str built at import and never mutated, and the
      module imports nothing, so a preset or the codegen engine imports it without an import cycle.
    - Import roots: `HYBRID_IMPORT_MODULE_ROOTS` is the common list, `PRECISION_IMPORT_MODULE_ROOTS`
      a narrower one, and `PERMISSIVE_IMPORT_MODULE_ROOTS` the common list plus the permissive
      extras, sorted. `HYBRID_DENIED_IMPORT_MODULE_ROOTS` (which precision aliases) names roots the
      compiler refuses even where an allow list admits them.
    - Denied builtins: `SAFE_DENIED_BUILTIN_NAMES` is the one tuple safe, hybrid and precision deny
      (`HYBRID_DENIED_BUILTIN_NAMES` and `PRECISION_DENIED_BUILTIN_NAMES` are the same object), and
      the codegen engine's no-projection default denies it plus `__import__`. `open` is on it, so
      those postures refuse file access through that builtin; permissive and full_access do not use
      it and keep `open`.
    - Policy, not isolation: these names feed checks that run in the room's own process, as defence
      in depth.
"""
'''

text = PATH.read_text(encoding="utf-8")
assert text.startswith("_COMMON_SAFE_IMPORT_MODULE_ROOTS = (\n"), text[:60]
assert '"""' not in text.split("\n", 1)[0]
PATH.write_text(DOCSTRING + "\n" + text, encoding="utf-8")
print("module docstring added;", len((DOCSTRING + "\n" + text).splitlines()), "lines")

"""S6 part A: pin creation-cache generation 22 in the schema-history integration test.

Run from the repository root:  python context_compass/artifacts/correctness_defects_20261017/scripts/s6_part_a_cache_test.py [--dry-run]
The test pins every generation of CachingSystem.CACHE_VERSION_HISTORY and proves that only the newest one loads;
part A added 22, "managed_settings_leave_spell_id", so the expected history gains that row (as 0.2.8248 added 21).
"""
import pathlib
import sys

DRY = "--dry-run" in sys.argv
PATH = pathlib.Path("tests/integration/melder/spellbook/test_cache_schema_version_integration.py")


def sub(text: str, old: str, new: str) -> str:
    count = text.count(old)
    assert count == 1, (old, count)
    return text.replace(old, new)


text = PATH.read_text(encoding="utf-8")
text = sub(
    text,
    '    21: "managed_spell_lease_codegen",\n}\n',
    '    21: "managed_spell_lease_codegen",\n    22: "managed_settings_leave_spell_id",\n}\n',
)
too_long = [line for line in text.splitlines() if len(line) > 120]
assert not too_long, too_long
if DRY:
    print("dry run: ok")
else:
    PATH.write_text(text, encoding="utf-8")
    print("wrote", PATH)

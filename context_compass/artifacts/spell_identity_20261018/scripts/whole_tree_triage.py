"""Sort the S1+S2 whole-tree failures (the /tmp mirror, GIL off, before the test tranche) into the tranche's
categories. Inputs: the failed-id list (one `tests/...::test` per line) and `first_error_kinds.py`'s grouping (per
file and first `E` line, with its count). The grouping misses tests that fail at setup; their remainder per file is
attributed by file. melder_0, 2026-10-18. Usage: python whole_tree_triage.py <failed ids> <kinds file>."""
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


class Triage:
    """Category rules, checked in order; the first that matches a (file, first error) group wins."""

    BASELINE_FILES = (
        "tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py",
        "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py",
    )
    ENVIRONMENT_FILES = (
        "tests/unit/melder/build_assets/test_system_documents_builder.py",
        "tests/unit/github_workflows/test_workflow_contracts.py",
    )
    DOUBLES_FILES = (
        "tests/unit/melder/crystallizer/test_spell_crystal.py",
        "tests/component/melder/crystallizer/test_spell_crystal_component.py",
        "tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py",
        "tests/unit/melder/spellbook/test_cache_runtime_verification.py",
        "tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py",
        "tests/unit/melder/crystallizer/persistence/test_restore_engine.py",
        "tests/unit/melder/crystallizer/test_crystallizer.py",
        "tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py",
        "tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py",
        "tests/integration/melder/spellbook/test_cache_schema_version_integration.py",
    )
    RETIRED_API = ("sha256_profile", "fingerprint_repr", "spell_id_inspector() got an unexpected keyword",
                   "spell_id_inspector() takes", "assert 0 == 2")
    REVERSED = ("AssertionError: assert '",)
    LINE = re.compile(r"^\s*(\d+) (\S+) :: (.*)$")

    def categorize(self, path: str, error: str) -> str:
        if path in self.BASELINE_FILES:
            return "f_baseline_melder_1_s8"
        if path in self.ENVIRONMENT_FILES:
            return "g_environment_fixed_in_mirror"
        if path in self.DOUBLES_FILES:
            return "a_doubles"
        if any(marker in error for marker in self.RETIRED_API):
            return "b_retired_api"
        if "Spell ID collision detected" in error:
            return "c_one_object_twice"
        if any(error.startswith(marker) and "!= '" in error for marker in self.REVERSED):
            return "d_reversed_premise"
        return "e_other"

    def run(self, failed: str, kinds: str) -> None:
        per_file_failed: Dict[str, int] = defaultdict(int)
        for line in open(failed, encoding="utf-8").read().split("\n"):
            if "::" in line:
                per_file_failed[line.split("::", 1)[0].split()[-1]] += 1
        totals: Dict[str, int] = defaultdict(int)
        rows: Dict[str, List[Tuple[int, str, str]]] = defaultdict(list)
        grouped: Dict[str, int] = defaultdict(int)
        for line in open(kinds, encoding="utf-8").read().split("\n"):
            match = self.LINE.match(line)
            if not match:
                continue
            count, path, error = int(match.group(1)), match.group(2), match.group(3)
            category = self.categorize(path, error)
            totals[category] += count
            grouped[path] += count
            rows[category].append((count, path, error[:110]))
        for path, count in per_file_failed.items():
            rest = count - grouped[path]
            if rest > 0:
                category = self.categorize(path, "setup error (not grouped)")
                totals[category] += rest
                rows[category].append((rest, path, "setup error (not grouped)"))
        print("FAILED", sum(per_file_failed.values()), "CATEGORIZED", sum(totals.values()))
        for category in sorted(totals):
            print(f"{category}: {totals[category]}")
        for category in sorted(rows):
            print(f"\n## {category}")
            per_file: Dict[str, int] = defaultdict(int)
            for count, path, _error in rows[category]:
                per_file[path] += count
            for path, count in sorted(per_file.items(), key=lambda item: (-item[1], item[0])):
                print(f"{count:4d} {path}")
            if category in ("d_reversed_premise", "e_other"):
                for count, path, error in rows[category]:
                    print(f"     {count} {path.rsplit('/', 1)[-1]} :: {error}")


if __name__ == "__main__":
    Triage().run(sys.argv[1], sys.argv[2])

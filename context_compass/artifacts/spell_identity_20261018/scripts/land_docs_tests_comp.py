"""S1 and S2 into tests_components (melder_0, 2026-10-18): the new tests, the rewritten ones and the counts.

One all-or-nothing pass over system_docs/tests_components.md: the tier and tree counts recounted from disk, the
three spellbook unit bullets that described the retired fingerprint rewritten to the code digest, new bullets and key
files for the seven new test files (the digest's, the libraries', the manifest's, the crystal's binding hash, the
component test of spell identity, the ordered-disposal replay as a key file, and the `version_of` support module),
the mock harness's binding hash, the cache generation 23, a code-map record per new key file, every code-map range
checked against disk (the records of rewritten files re-stamped), the sources and the handoff. `--write` flushes;
the index is regenerated after it.
"""
import pathlib
import re
import subprocess
import sys
from typing import Dict, List, Set, Tuple

from docs_common import DocsRecord


class LandTestsComponents(DocsRecord):
    """The tests_components pass."""

    CHANGED = pathlib.Path("/tmp/m0_mq/docs_tests/changed_tests.txt")
    NEW_FILES = {
        "tests/_spell_identity_test_support.py": "tests/_annotation_audit_support.py",
        "tests/unit/melder/spellbook/bind/test_spell_code_digest.py":
            "tests/unit/melder/spellbook/bind/test_stable_spell_fingerprint.py",
        "tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py":
            "tests/unit/melder/spellbook/bind/test_spell_code_digest.py",
        "tests/unit/melder/spellbook/bind/test_binding_manifest.py":
            "tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py",
        "tests/unit/melder/crystallizer/test_spell_crystal_binding_hash.py":
            "tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py",
        "tests/component/melder/spellbook/test_spellbook_component_spell_identity.py":
            "tests/component/melder/spellbook/test_spell_id_process_stability.py",
        "tests/integration/melder/crystallizer/test_ordered_disposal_replay.py":
            "tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py",
    }
    NOTES = {
        "tests/_spell_identity_test_support.py": "`version_of`: a version of a class - same name, qualname and module, "
                                                 "other class-level values - for tests that need a second "
                                                 "registration of one class (0.2.8257).",
        "tests/unit/melder/spellbook/bind/test_spell_code_digest.py": "what moves a spell_id and what does not "
                                                                      "(0.2.8257).",
        "tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py": "installed third-party code named by "
                                                                                "distribution version (0.2.8257).",
        "tests/unit/melder/spellbook/bind/test_binding_manifest.py": "the binding manifest and its hash (0.2.8258).",
        "tests/unit/melder/crystallizer/test_spell_crystal_binding_hash.py": "the crystal's binding hash, record "
                                                                             "4.3.0 (0.2.8258).",
        "tests/component/melder/spellbook/test_spellbook_component_spell_identity.py": "one object, one spell, over "
                                                                                       "real wiring (0.2.8257-0.2.8258).",
        "tests/integration/melder/crystallizer/test_ordered_disposal_replay.py": "disposal order through a record; a "
                                                                                 "receiving policy keeps every "
                                                                                 "spell_id (0.2.8258).",
    }

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.restamped: List[str] = []
        self.core_size = 0

    def replace_once(self, old: str, new: str, label: str) -> None:
        self.stage(self.TESTS_COMP, self.once(self.read(self.TESTS_COMP), old, new, label))

    def _section_key_files(self, lines: List[str], heading: str) -> Tuple[int, int]:
        """(index of the `Key Files (C1):` line, index after its last list line) inside the section `heading`."""
        starts = [i for i, line in enumerate(lines) if line == heading]
        if len(starts) != 1:
            sys.exit(f"HEADING {heading}: {len(starts)}")
        i = starts[0] + 1
        while not lines[i].startswith("Key Files (C1):"):
            if lines[i].startswith("### ") or lines[i].startswith("## "):
                sys.exit(f"NO KEY FILES in {heading}")
            i += 1
        end = i + 1
        while end < len(lines) and (lines[end].startswith("- ") or lines[end].startswith("  ")):
            end += 1
        return i, end

    def bullet_before_key_files(self, heading: str, bullet: str) -> None:
        self.check_width(bullet, heading)
        lines = self.read(self.TESTS_COMP).split("\n")
        at, _ = self._section_key_files(lines, heading)
        self.stage(self.TESTS_COMP, "\n".join(lines[:at] + bullet.split("\n") + lines[at:]))

    def key_file(self, heading: str, entry: str) -> None:
        self.check_width(entry, heading)
        lines = self.read(self.TESTS_COMP).split("\n")
        _, end = self._section_key_files(lines, heading)
        self.stage(self.TESTS_COMP, "\n".join(lines[:end] + [entry] + lines[end:]))

    @staticmethod
    def tier_counts() -> Dict[str, int]:
        root = DocsRecord.REPO / "tests"
        counts = {}
        for tier in ("unit", "component", "integration"):
            counts[tier] = len(list((root / tier).rglob("test_*.py")))
            counts[tier + "_py"] = len(list((root / tier).rglob("*.py")))
        for tier, tree in (("unit", "crystallizer"), ("unit", "spellbook"), ("component", "spellbook"),
                           ("integration", "spellbook")):
            counts[f"{tier}_{tree}"] = len(list((root / tier / "melder" / tree).rglob("test_*.py")))
        return counts

    def counts(self, c: Dict[str, int]) -> None:
        """The tier and tree counts the catalog states, recounted from disk."""
        self.replace_once("- the densest tier: 510 `test_*.py` modules among 513 `.py` files (recounted 2026-10-18)",
                          f"- the densest tier: {c['unit']} `test_*.py` modules among {c['unit_py']} `.py` files "
                          "(recounted 2026-10-18)", "unit tier")
        self.replace_once("the 48 test_*.py modules in\n  tests/unit/melder/crystallizer/",
                          f"the {c['unit_crystallizer']} test_*.py modules in\n  tests/unit/melder/crystallizer/",
                          "unit crystallizer")
        self.replace_once("- The spellbook tree carries 158 `test_*.py` modules beneath these;",
                          f"- The spellbook tree carries {c['unit_spellbook']} `test_*.py` modules beneath these;",
                          "unit spellbook")
        self.replace_once("- 166 `test_*.py` modules among 168 `.py` files (recounted 2026-10-17)",
                          f"- {c['component']} `test_*.py` modules among {c['component_py']} `.py` files "
                          "(recounted 2026-10-18)", "component tier")
        self.replace_once("- The spellbook tree carries 77 `test_*.py` modules beneath these;",
                          f"- The spellbook tree carries {c['component_spellbook']} `test_*.py` modules beneath "
                          "these;", "component spellbook")
        self.replace_once("- 175 `test_*.py` modules among 182 `.py` files (recounted 2026-10-18);",
                          f"- {c['integration']} `test_*.py` modules among {c['integration_py']} `.py` files "
                          "(recounted 2026-10-18);", "integration tier")
        self.replace_once("the 52 test_*.py modules in\n  tests/integration/melder/spellbook/",
                          f"the {c['integration_spellbook']} test_*.py modules in\n  tests/integration/melder/spellbook/",
                          "integration spellbook")
        total = c["unit"] + c["component"] + c["integration"]
        self.replace_once("builders - not every `test_*.py` module beneath it. The 851 test modules of the",
                          f"builders - not every `test_*.py` module beneath it. The {total} test modules of the",
                          "core paragraph modules")

    def shared_support(self) -> None:
        self.replace_once(
            "  (`_annotation_audit_support.py`, enforced by\n  `tests/unit/melder/test_annotation_integrity.py`)\n",
            "  (`_annotation_audit_support.py`, enforced by\n  `tests/unit/melder/test_annotation_integrity.py`)\n"
            "- that one object stays one spell where a test needs a second registration of \"the same\" class\n"
            "  (`_spell_identity_test_support.py`, 0.2.8257): `version_of` builds a version of it - a subclass with the\n"
            "  same name, qualname and module and the class-level values given - whose code, and so spell_id, differs\n"
            "  while every lookup by name reads the original's; a test that restores or grafts the version defines a\n"
            "  module-level class instead, because a runtime class cannot be imported by its qualname\n",
            "shared support protects")
        self.replace_once("- `tests/_annotation_audit_support.py`\n- `tests/component/melder/spellbook/compiler_test_helpers.py`",
                          "- `tests/_annotation_audit_support.py`\n- `tests/_spell_identity_test_support.py`\n"
                          "- `tests/component/melder/spellbook/compiler_test_helpers.py`", "shared support key file")

    def spellbook_unit(self) -> None:
        self.replace_once(
            "  without `unique` existence, unnamed lambdas; binding-profile hashing, including\n"
            "  fingerprints with no memory address in them\n",
            "  without `unique` existence, unnamed lambdas, a non-bool `resolvable` before the target is examined;\n"
            "  the spell_id is the target's code digest (`Bind.spell_id_inspector` answers it), and two objects with\n"
            "  identical code and data share one spell_id while a content difference keeps them apart, with no\n"
            "  memory address in either (0.2.8257; `test_stable_spell_fingerprint.py` keeps its name)\n",
            "spellbook unit fingerprint bullet")
        self.replace_once(
            "  reset names that are not a list or tuple naming methods of the class; every existing member's spell id\n"
            "  byte-identical to 0.2.8241, and a managed binding hashing exactly the inputs every binding hashes, "
            "whatever its\n"
            "  settings (0.2.8254; from 0.2.8242 to 0.2.8253 a `managed:<mode>:<limit>:<timeout>:<names>` part moved "
            "its id);\n"
            "  the index minted with that id; the decorator form and `spell_id_inspector` parity, which ignores the "
            "settings\n"
            "  too. Around it:\n",
            "  reset names that are not a list or tuple naming methods of the class; one spell_id - the class's code\n"
            "  digest - whatever the mode, limit, timeout and reset names (0.2.8257; the 0.2.8241 literal ids are\n"
            "  retired; 0.2.8254 took the settings out of the id, and from 0.2.8242 to 0.2.8253 a\n"
            "  `managed:<mode>:<limit>:<timeout>:<names>` part moved it); the index minted with that id; the decorator\n"
            "  form and `spell_id_inspector` parity, which answers the class's code too. Around it:\n",
            "spellbook unit managed bullet")
        self.bullet_before_key_files(
            "### Subcomponent: Spellbook Runtime And Binding Unit Cluster",
            "- spell identity is the code (0.2.8257-0.2.8258): `test_spell_code_digest.py` (35 tests, 69 cases) pins\n"
            "  what moves a spell_id - a class's code (TestClassCode), a change inside a method body (TestInsideAMethod),\n"
            "  functions and values (TestFunctionsAndValues), an existing object's class and data (TestExistingObjects)\n"
            "  - what runtime state does not count (TestRuntimeStateDoesNotCount) and the digest's contract\n"
            "  (TestContract); `test_spell_code_digest_libraries.py` (9 tests) names installed third-party code by its\n"
            "  distribution version, digests an application class over an installed base by its own code, counts a\n"
            "  decorator and the function it wraps and a dataclass default factory, and leaves out a class a\n"
            "  class-level value names and a module-level helper a method calls; `test_binding_manifest.py` (7 tests,\n"
            "  20 cases) moves the binding hash with every manifest field and the disposal order, writes equal\n"
            "  settings alike and pins the hash's SHA256 input and `describe()`")
        for path in ("tests/unit/melder/spellbook/bind/test_spell_code_digest.py (the spell_id is the code, 2026-10-18)",
                     "tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py (installed code, 2026-10-18)",
                     "tests/unit/melder/spellbook/bind/test_binding_manifest.py (the binding hash, 2026-10-18)"):
            name, rest = path.split(" ", 1)
            self.key_file("### Subcomponent: Spellbook Runtime And Binding Unit Cluster", f"- `{name}` {rest}")

    def crystallizer(self) -> None:
        self.bullet_before_key_files(
            "### Subcomponent: Crystallizer Unit Cluster",
            "- the binding hash in the record (0.2.8258; `test_spell_crystal_binding_hash.py`, 3 tests): a crystal\n"
            "  records its spell's `binding_hash`, two bindings of one spell_id record two binding hashes, and a cleaned\n"
            "  crystal refuses the read; RecordVersion is 4.3.0")
        self.key_file("### Subcomponent: Crystallizer Unit Cluster",
                      "- `tests/unit/melder/crystallizer/test_spell_crystal_binding_hash.py` (record 4.3.0, 2026-10-18)")
        self.bullet_before_key_files(
            "### Subcomponent: Crystallizer Integration Cluster",
            "- disposal order through a record (`test_ordered_disposal_replay.py`, 6 tests, 23 cases): the crystal and\n"
            "  its JSON keep each member's order, a cached restore keeps the order and the real cleanup, a graft keeps\n"
            "  the members under the receiving Book's order, and a restore under another receiving policy keeps every\n"
            "  spell_id and the exact selected member, reports each binding it rebuilt in `binding_changes` (0.2.8258)\n"
            "  and regrants contract details; a merge does not adopt a skipped resident's selection")
        self.key_file("### Subcomponent: Crystallizer Integration Cluster",
                      "- `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py` (receiving policy, "
                      "2026-10-18)")
        self.replace_once(
            "- the harness spell double carries `aetheric_frame = \"default\"`, which SpellCrystal reads for its custody "
            "key\n  (0.2.8214)\n",
            "- the harness spell double carries `aetheric_frame = \"default\"`, which SpellCrystal reads for its custody "
            "key\n  (0.2.8214), and a `binding_hash` - the SHA256 of \"binding:\" and its spell_id, a fixed 64-hex value "
            "per\n  spell_id - which SpellCrystal records (record 4.3.0, 0.2.8258)\n",
            "mock harness")

    def spellbook_component_and_integration(self) -> None:
        self.bullet_before_key_files(
            "### Subcomponent: Spellbook Runtime And Binding Component Cluster",
            "- one object, one spell over real wiring (0.2.8257-0.2.8258; `test_spellbook_component_spell_identity.py`,\n"
            "  8 tests): the spell_id bind returns is the object's code digest; a class bound another way keeps its\n"
            "  spell_id and changes its binding hash; a second registration of one object, and a second staging of one\n"
            "  class, are refused naming its spell_id; an edited class stages beside the old one and melds after a\n"
            "  notch; `inspect_spell` finds an existing object by its code and data; a spell keeps its binding after\n"
            "  cleanup; and a binding changed under one spell_id is another world to the creation cache")
        self.key_file("### Subcomponent: Spellbook Runtime And Binding Component Cluster",
                      "- `tests/component/melder/spellbook/test_spellbook_component_spell_identity.py` (one object, one "
                      "spell, 2026-10-18)")
        self.replace_once(
            "after the notch, `with` giving the object back. The creation cache's generation history ends at 22\n"
            "  (`test_cache_schema_version_integration.py`: generation 22 is admitted, 1-21 load cold; 22 joined at "
            "0.2.8254)\n",
            "after the notch, `with` giving the object back. The creation cache's generation history ends at 23\n"
            "  (`test_cache_schema_version_integration.py`: generation 23 is admitted, 1-22 load cold; 22 joined at "
            "0.2.8254,\n  23 - the binding manifest's keys - at 0.2.8258)\n",
            "generation 23")
        self.replace_once(
            "- the public notch target (0.2.8249; `test_notch_spell_by_id_integration.py`, 10 tests):",
            "- one spell_id, three binding hashes (0.2.8258; `test_managed_bind_options_integration.py`): one managed\n"
            "  class bound three ways keeps one spell_id - its code - and each binding has its own binding hash, because\n"
            "  the existence and the settings are the binding; a refused binding leaves the Book unchanged\n"
            "- the public notch target (0.2.8249; `test_notch_spell_by_id_integration.py`, 10 tests):",
            "managed binding hashes")

    def code_map(self) -> None:
        """New records, the rewritten files re-stamped, every range checked against disk."""
        for path, after in self.NEW_FILES.items():
            self.add_entry_after(self.TESTS_COMP, after, path, self.NOTES[path])
        changed = [line.split("\t")[1] for line in self.CHANGED.read_text(encoding="utf-8").splitlines()
                   if line.startswith("M\t")]
        for path in changed:
            if self.remeasure(self.TESTS_COMP, path, "Rewritten for S1 and S2 (0.2.8257-0.2.8258)."):
                self.restamped.append(path)
        text = self.read(self.TESTS_COMP)
        for match in re.finditer(r"^- path: `([^`]+)`\n  start_line: (\d+)\n  end_line: (\d+)\n  loc: (\d+)\n",
                                 text, flags=re.M):
            path, end, loc = match.group(1), int(match.group(3)), int(match.group(4))
            if not (self.REPO / path).is_file():
                sys.exit(f"MISSING {path}")
            if self.line_count(path) != end or end != loc:
                if path in self.restamped:
                    sys.exit(f"RESTAMP FAILED {path}")
                self.remeasure(self.TESTS_COMP, path, "Remeasured (it had drifted).")
                self.restamped.append(path)

    def core_set(self) -> Set[str]:
        """The union of every Key Files (C1) list, checked against the code map's paths."""
        lines = self.read(self.TESTS_COMP).split("\n")
        core: Set[str] = set()
        i = 0
        while i < len(lines):
            if lines[i].startswith("Key Files (C1):"):
                core.update(p for p in re.findall(r"`([^`]+)`", lines[i]) if "/" in p and "*" not in p)
                i += 1
                while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  ")):
                    if lines[i].startswith("- `"):
                        core.update(p for p in re.findall(r"^- `([^`]+)`", lines[i]) if "*" not in p)
                    i += 1
                continue
            i += 1
        mapped = set(re.findall(r"^- path: `([^`]+)`", "\n".join(lines), flags=re.M))
        if core != mapped:
            sys.exit(f"CORE != MAP: only core {sorted(core - mapped)}; only map {sorted(mapped - core)}")
        return core

    def sources_and_handoff(self, c: Dict[str, int]) -> None:
        listing = "\n".join(f"- `{path}`" for path in self.NEW_FILES)
        self.replace_once("\n\n## Open Questions\n", "\n" + listing + "\n\n## Open Questions\n", "sources")
        core = self.core_set()
        self.replace_once("above - 264 paths (recounted 2026-10-18) - and nothing else.",
                          f"above - {len(core)} paths (recounted 2026-10-18) - and nothing else.", "core count")
        self.core_size = len(core)
        total = c["unit"] + c["component"] + c["integration"]
        paragraph = self.wrap(
            "2026-10-18 spell identity is the code (0.2.8257-0.2.8258; S1 and S2 of "
            "EPIC-2026-10-18-spell_identity_is_the_code): the Spellbook Runtime And Binding Unit Cluster gains "
            "`test_spell_code_digest.py` (35 tests, 69 cases), `test_spell_code_digest_libraries.py` (9) and "
            "`test_binding_manifest.py` (7 tests, 20 cases), and its bind, fingerprint and managed-option bullets now "
            "describe the code digest instead of the retired fingerprint; the Crystallizer Unit Cluster gains "
            "`test_spell_crystal_binding_hash.py` (3, record 4.3.0); the Spellbook Runtime And Binding Component Cluster "
            "gains `test_spellbook_component_spell_identity.py` (8); the Crystallizer Integration Cluster names "
            "`test_ordered_disposal_replay.py` (6 tests, 23 cases) as a key file; the shared support gains "
            "`_spell_identity_test_support.py` (`version_of`), which the suites use where a test bound one class "
            "twice; the Spellbook Integration Cluster names the managed binding's three binding hashes and generation "
            "23; the mock harness's spell double carries a binding hash. Each new key file has a code-map record, so "
            f"the core set is {len(core)} paths, equal to the code map. Every code-map range was checked against disk "
            f"on this pass and {len(self.restamped)} records of rewritten files were re-stamped. Counts are recounted "
            f"from disk (unit {c['unit']} of {c['unit_py']} `.py`, crystallizer tree {c['unit_crystallizer']}, "
            f"spellbook tree {c['unit_spellbook']}; component {c['component']} of {c['component_py']}, spellbook "
            f"tree {c['component_spellbook']}; integration {c['integration']} of {c['integration_py']}, spellbook "
            f"tree {c['integration_spellbook']}; {total} test modules in the three tiers).", "", "")
        self.replace_once("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + paragraph + "\n\n",
                          "handoff")
        self.set_field(self.TESTS_COMP, "Updated") if "\n- Updated: " in self.read(self.TESTS_COMP) else None


def main() -> None:
    record = LandTestsComponents("tests_comp_s1s2")
    counts = record.tier_counts()
    record.counts(counts)
    record.shared_support()
    record.spellbook_unit()
    record.crystallizer()
    record.spellbook_component_and_integration()
    record.code_map()
    record.sources_and_handoff(counts)
    text = record.read(record.TESTS_COMP)
    if "\r" in text:
        sys.exit("CR")
    print("counts", counts)
    print("restamped", len(record.restamped), record.restamped)
    print("core", record.core_size, "lines", len(text.rstrip("\n").split("\n")))
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()
    subprocess.run([sys.executable, str(record.ROOT / "tools/system_documents/index_document.py"), "--doc",
                    str(record.ROOT / record.TESTS_COMP)], check=True)


if __name__ == "__main__":
    main()

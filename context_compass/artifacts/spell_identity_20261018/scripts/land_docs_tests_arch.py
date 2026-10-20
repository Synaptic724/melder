"""S1 and S2 into tests_architecture (melder_0, 2026-10-18): the inventory, the spell-identity support module and
the one-object invariant.

One all-or-nothing pass over system_docs/tests_architecture.md: the tier inventory recounted from disk, the new
shared support module `tests/_spell_identity_test_support.py` in the evidence, the responsibilities, the C2 overview
and the code map, a new operational invariant (one object is one spell in the suite too), the xfail evidence into the
notch-revalidation file remapped to the marker's decorator and body, every code-map range checked against disk, the
sources and the handoff. `--write` flushes; the index is regenerated after it.
"""
import re
import subprocess
import sys
from typing import List

from docs_common import DocsRecord


class LandTestsArchitecture(DocsRecord):
    """The tests_architecture pass."""

    SUPPORT = "tests/_spell_identity_test_support.py"
    IDENTITY = "tests/component/melder/spellbook/test_spellbook_component_spell_identity.py"
    NOTCH = "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py"

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.restamped: List[str] = []

    def replace_once(self, old: str, new: str, label: str) -> None:
        self.stage(self.TESTS_ARCH, self.once(self.read(self.TESTS_ARCH), old, new, label))

    @staticmethod
    def count(tier: str, pattern: str) -> int:
        return len(list((DocsRecord.REPO / "tests" / tier).rglob(pattern)))

    def inventory(self) -> int:
        unit, unit_py = self.count("unit", "test_*.py"), self.count("unit", "*.py")
        comp, comp_py = self.count("component", "test_*.py"), self.count("component", "*.py")
        integ, integ_py = self.count("integration", "test_*.py"), self.count("integration", "*.py")
        if (self.count("mocks", "*.py"), self.count("experimentation", "*.py")) != (44, 204):
            sys.exit("mocks or experimentation moved; recount their lines too")
        self.replace_once("- `unit/`: 513 `.py` files, 510 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)",
                          f"- `unit/`: {unit_py} `.py` files, {unit} of them `test_*.py` (465 on 2026-09-26, 334 on "
                          "2026-06-13)", "unit inventory")
        self.replace_once("- `component/`: 168 `.py` files, 166 of them `test_*.py` (143, 81)",
                          f"- `component/`: {comp_py} `.py` files, {comp} of them `test_*.py` (143, 81)",
                          "component inventory")
        self.replace_once("- `integration/`: 182 `.py` files, 175 of them `test_*.py` (149, 88)",
                          f"- `integration/`: {integ_py} `.py` files, {integ} of them `test_*.py` (149, 88)",
                          "integration inventory")
        self.replace_once("the three tiers' 851 `test_*.py`", f"the three tiers' {unit + comp + integ} `test_*.py`",
                          "tier total")
        return unit + comp + integ

    def support_module(self) -> None:
        self.replace_once("Direct evidence used in this pass:\n- `pyproject.toml`\n- `tests/conftest.py`\n"
                          "- `tests/_frame_posture_test_support.py`\n- `tests/_codegen_system_support.py`\n",
                          "Direct evidence used in this pass:\n- `pyproject.toml`\n- `tests/conftest.py`\n"
                          "- `tests/_frame_posture_test_support.py`\n- `tests/_codegen_system_support.py`\n"
                          f"- `{self.SUPPORT}`\n", "evidence list")
        self.replace_once(
            "- Codegen/compiler support centralizes namespace doubles, event/memory doubles,\n",
            "- Spell-identity support (`version_of`, 0.2.8257) gives a test that needs a second registration of one\n"
            "  class a version of it - a subclass with the same name, qualname and module and class-level values of\n"
            "  its own - because one object is one spell and a second registration of it is refused.\n"
            "- Codegen/compiler support centralizes namespace doubles, event/memory doubles,\n", "responsibilities")
        self.replace_once(
            "  Purpose: shared codegen-system doubles and helper builders for compiler and\n  codegen test lanes.\n",
            "  Purpose: shared codegen-system doubles and helper builders for compiler and\n  codegen test lanes.\n"
            f"- `{self.SUPPORT}`\n"
            "  Purpose: `version_of`, a version of a class for a test that needs a second registration of one\n"
            "  class; a test that restores or grafts the version defines a module-level class instead.\n",
            "c2 overview")

    def invariant_and_evidence(self) -> None:
        bullet = "\n".join([
            "- One object is one spell in the suite too (0.2.8257): no test registers one class twice - under a second",
            "  binding name, existence or spellframe, in a second Book of a process-wide world, or staged again with",
            "  `bind_inactive` - because bind refuses it; a test that needs the shape binds a version (`version_of`) or",
            "  a class of its own, and the tests that pin the refusal expect RuntimeError naming the spell_id.",
            "  EVIDENCE:",
            f"  - {self.SUPPORT}:1-46",
            f"  - {self.IDENTITY}:98-135",
        ])
        self.check_width(bullet, "invariant")
        self.replace_once("\n\n## Source Coverage and Evidence\n", "\n" + bullet + "\n\n## Source Coverage and Evidence\n",
                          "invariant")
        self.replace_once(f"  EVIDENCE: {self.NOTCH}:624-673", f"  EVIDENCE: {self.NOTCH}:626-675", "xfail evidence")
        lines = (self.REPO / self.NOTCH).read_text(encoding="utf-8").split("\n")
        if not lines[625].startswith("@pytest.mark.xfail(") or len(lines[:-1]) != 675:
            sys.exit("notch-revalidation xfail range moved")

    def code_map(self) -> int:
        self.add_entry_after(self.TESTS_ARCH, "tests/_nexus_viewer_matrix_support.py", self.SUPPORT,
                             "`version_of`: a version of a class for a second registration of one class (0.2.8257).")
        text = self.read(self.TESTS_ARCH)
        entries = re.findall(r"^- path: `([^`]+)`\n  start_line: (\d+)\n  end_line: (\d+)\n  loc: (\d+)\n", text,
                             flags=re.M)
        for path, _start, end, loc in entries:
            if not (self.REPO / path).is_file():
                sys.exit(f"MISSING {path}")
            if self.line_count(path) != int(end) or end != loc:
                self.remeasure(self.TESTS_ARCH, path, "Remeasured (it had drifted).")
                self.restamped.append(path)
        mapped = len(entries)
        self.replace_once(
            "the mock corpus and the CI driver: 36 paths, every one of\nthem in the core set of `tests_components` "
            "(the deduplicated union of its `Key Files (C1)` lists, 247 paths on\n2026-10-15;",
            f"the mock corpus and the CI driver: {mapped} paths, every one of\nthem in the core set of "
            "`tests_components` (the deduplicated union of its `Key Files (C1)` lists, 272 paths on\n2026-10-18;",
            "map paragraph")
        return mapped

    def sources_and_handoff(self, total: int, mapped: int) -> None:
        self.replace_once(f"- `{self.NOTCH}`\n", f"- `{self.NOTCH}`\n- `{self.SUPPORT}`\n- `{self.IDENTITY}`\n",
                          "sources")
        restamped = ", ".join(f"`{p}`" for p in self.restamped) if self.restamped else "none"
        paragraph = self.wrap(
            "2026-10-18 spell identity is the code (0.2.8257-0.2.8258): the inventory is recounted from disk (unit 517 "
            "`.py`, component 169, integration 183, mocks 44, experimentation 204; "
            f"{total} test modules in the three tiers) - the lane adds four unit modules (the digest's, the "
            "libraries', the manifest's and the crystal's binding hash) and one component module (spell identity "
            "over real wiring), catalogued in `tests_components`, and the integration count takes in the red-test "
            "module of STORY-2026-10-17-minted_index_missing_from_frame_registry "
            "(`test_separated_version_is_known_to_its_frame_integration.py`), which fails on purpose until that "
            "story lands. One shared support module joins the suite, `tests/_spell_identity_test_support.py` "
            "(`version_of`), and with it the evidence, the responsibilities, the C2 overview, a new operational "
            f"invariant (one object is one spell in the suite too) and this map ({mapped} paths). The xfail evidence "
            "into the notch-revalidation file is remapped to the marker's decorator and body (626-675); every range "
            f"in this map was checked against disk (re-stamped: {restamped}). No tier, conftest or declared marker "
            "changes.", "", "")
        self.replace_once("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + paragraph + "\n\n",
                          "handoff")


def main() -> None:
    record = LandTestsArchitecture("tests_arch_s1s2")
    total = record.inventory()
    record.support_module()
    record.invariant_and_evidence()
    mapped = record.code_map()
    record.sources_and_handoff(total, mapped)
    text = record.read(record.TESTS_ARCH)
    if "\r" in text:
        sys.exit("CR")
    print("total", total, "mapped", mapped, "restamped", record.restamped,
          "lines", len(text.rstrip("\n").split("\n")))
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()
    subprocess.run([sys.executable, str(record.ROOT / "tools/system_documents/index_document.py"), "--doc",
                    str(record.ROOT / record.TESTS_ARCH)], check=True)


if __name__ == "__main__":
    main()

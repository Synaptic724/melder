"""ContextCompass sync for the 0.2.8229 landing: ticket notes/state, attention and artifact boards. Keeps EOL."""
import datetime, pathlib, sys

CC = pathlib.Path(sys.argv[1]) / "context_compass"
REPO = CC.parent
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TICKET = "tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md"
EV = "context_compass/artifacts/spell_lookup_race_20261010/r6"


def nlines(rel):
    return len((REPO / rel).read_bytes().decode("utf-8").splitlines())


def span(rel, start_marker, end_marker):
    lines = (REPO / rel).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    s = next(i for i, l in enumerate(lines) if l.startswith(start_marker)) + 1
    e = next(i for i, l in enumerate(lines) if i >= s and l.strip() == end_marker) + 1
    return f"{rel}:{s}-{e}"


def edit(rel, ops):
    path = CC / rel
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    for kind, anchor, payload in ops:
        if text.count(anchor) != 1:
            raise SystemExit(f"{rel}: anchor x{text.count(anchor)}: {anchor[:80]!r}")
        if kind == "replace":
            text = text.replace(anchor, payload, 1)
        elif kind == "after":
            text = text.replace(anchor, anchor + payload, 1)
        elif kind == "before":
            text = text.replace(anchor, payload + anchor, 1)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


FIND = span("src/melder/aether/spellbook/spellbook.py", "    def find_spell_by_id(", "return self._spells.get(spell_index)")
ACC = span("src/melder/aether/spellbook/spell.py", "    def _spell_index_unless_cleaned(", "return self.spell_index")
R = f"{EV}/runs"
NOTES = f"""
- DATETIME: {NOW}
  TYPE: MEASURE
  CLAIM: R6 built and tested in scratch (git-archive exports of 3d184cac plus apply_r6.py; CPython 3.14.7t). The
    14 new tests - 10 component (lineage contract across notch, add/remove-from-index, transfer, parked disposal,
    unknown and foreign ids; no iteration of the live map; the parked-disposal window forced by an Event pause) and
    4 unit tests of Spell._spell_index_unless_cleaned - pass on R6 under -X gil=0 and gil=1. On 3d184cac 6 fail in
    both modes (the no-walk and mid-lookup-disposal tests and the four accessor tests: the method is new) and the 8
    contract tests pass, so R6 keeps every answer the walk gave. Full test tree on R6 (-X gil=0, the 23 chunks of
    the R5 baseline): 13,654 passed, 31 skipped, 17 xfailed, 2 xpassed - the 3d184cac baseline of 13,640 plus the
    14 new tests, nothing else. The crystallizer integration chunk first failed with ENOSPC (the VM's /sessions
    volume, pytest's temp root, was full from other sessions); rerun with TMPDIR on /tmp it matched the baseline,
    273 passed and 3 xfailed. Spell.cleanup never deleted _lock although its docstring said it did; the docstring is
    corrected, since the accessor's never-raises contract relies on the lock surviving cleanup.
  EVIDENCE:
  - {R}/new_tests_head_gil0.log:1-{nlines(R + '/new_tests_head_gil0.log')}
  - {R}/new_tests_head_gil1.log:1-{nlines(R + '/new_tests_head_gil1.log')}
  - {R}/new_tests_cand_r6_gil0.log:1-{nlines(R + '/new_tests_cand_r6_gil0.log')}
  - {R}/new_tests_cand_r6_gil1.log:1-{nlines(R + '/new_tests_cand_r6_gil1.log')}
  - {R}/summary_full_r6_gil0.txt:1-{nlines(R + '/summary_full_r6_gil0.txt')}
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/suites/summary_full_tree_gil0.txt:1-46
  - src/melder/aether/spellbook/spell.py:550-655
  IMPACT: The gate for landing (Note 29: nothing lands before the scratch tests pass) is met.
  NEXT: Land R6 through the patch lane: src, tests, notch, release note, docs, graph, then assets last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  TYPE: FACT
  CLAIM: R6 landed on the working tree as 0.2.8229 (no commit or push). find_spell_by_id answers from
    _spells_by_id, then _inactive_spells and the parked spell's index read through the new
    Spell._spell_index_unless_cleaned, then _spells.get(index); the Spell.cleanup docstring says _lock is kept. After
    the tree run one docstring sentence was made exact - an index move has no None window, a lookup racing it
    answers as before or as after the move - code unchanged. Tests: the component and unit files below.
    __version__ 0.2.8228 -> 0.2.8229; release note header, a user-facing section and the rebuild line.
    src_architecture (operational invariant, failure mode, code map, handoff) and src_components (Spellbook Core
    threading and failure modes, Binding Pipeline threading, code map, handoff), both indexes regenerated and
    checked. Graph: extract --strict, the Spell node re-read against its prose and accepted (it went stale only
    through this change; Spellbook was already stale at 3d184cac and is left so), reassembled; extract --check
    reports what 3d184cac reports (10 unsemantic, 208 stale) and assemble --check is OK. Patch docs promoted and
    archived to system_docs/patches/completed/find_spell_by_id_id_maps_2026_10_11/.
  EVIDENCE:
  - {FIND}
  - {ACC}
  - src/melder/__version__.py:12-12
  - tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py:1-{nlines('tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py')}
  - tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py:1-{nlines('tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py')}
  - release_docs/next_version_release.md:1-{nlines('release_docs/next_version_release.md')}
  - {EV}/scripts/land_docs_r6.py:1-{nlines(EV + '/scripts/land_docs_r6.py')}
  - {R}/extract_check2.log:1-{nlines(R + '/extract_check2.log')}
  IMPACT: The MelderOps lane can move once a Melder build carries 0.2.8229; the owner commits and pushes.
  NEXT: Rebuild the assets and llm_support bundles, then both --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = f"""REVIEW (melder_1), {NOW}: R6 LANDED as 0.2.8229 on the working tree, not committed - find_spell_by_id
answers from the Book's id maps, the parked branch reads its index through Spell._spell_index_unless_cleaned; 14
new tests; full tree identical to 3d184cac plus those tests (Notes 31-32). Owner: commit and push, accept or
redirect; Windows tiers, hosted CI, the gauntlet and MelderOps' x40 run are the owner's. Earlier state follows.
"""

edit(TICKET, [
    ("replace", "- Status: in_progress\n", "- Status: review\n"),
    ("replace", "- Updated: 2026-10-11T01:07:38Z\n", f"- Updated: {NOW}\n"),
    ("replace", "  then landing.\n\n## Steps / Checklist",
     "  then landing.\n- from_state: in_progress\n- to_state: review\n"
     f"- transition_reason: ({NOW}) R6 landed as 0.2.8229 with its tests, docs, graph, release note and rebuilt\n"
     "  assets (Notes 31-33); the owner accepts or redirects. No commit or push.\n\n## Steps / Checklist"),
    ("replace", "- [ ] Patch docs written and linked; build R6 in scratch with its tests, cost and the full tree.\n",
     "- [x] Patch docs written and linked; R6 built in scratch with its tests and the full tree (Notes 30-31;\n"
     "      single-thread cost not re-measured).\n"),
    ("replace", "- [ ] If it holds: land R6 through the patch lane",
     "- [x] If it holds: land R6 through the patch lane"),
    ("replace", "- [ ] No production change without the owner's approval of the proposed repair.\n",
     "- [x] No production change without the owner's approval of the proposed repair.\n"),
    ("replace", "- [ ] No sleep-based reproduction presented as deterministic.\n",
     "- [x] No sleep-based reproduction presented as deterministic.\n"),
    ("replace", "- [ ] No historical report presented as a current defect without a current reproduction.\n",
     "- [x] No historical report presented as a current defect without a current reproduction.\n"),
    ("after", "  closure run, coverage.\n",
     "- Run for the R6 landing (Notes 31-33; logs under artifacts/spell_lookup_race_20261010/r6/runs/): the 14 new\n"
     "  tests on 3d184cac and R6 (gil=0/1), the full test tree on R6 (gil=0), the index, graph, asset and llm_support\n"
     "  checks. Not run: the full tree under -X gil=1, a single-thread cost re-measure, the owner's Windows tiers,\n"
     "  hosted CI, the gauntlet, MelderOps' x40 closure run, coverage.\n"),
    ("after", "- this ticket; context_compass/attention_board.md; context_compass/artifact_board.md\n",
     "- Landing (0.2.8229): src/melder/aether/spellbook/spellbook.py, src/melder/aether/spellbook/spell.py,\n"
     "  src/melder/__version__.py, tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py (new),\n"
     "  tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py (new), release_docs/next_version_release.md,\n"
     "  context_compass/system_docs (src_architecture, src_components, their indexes, graph descriptors, src_graph),\n"
     "  the rebuilt src/melder/_build_assets and llm_support; artifacts/spell_lookup_race_20261010/r6/ (evidence).\n"),
    ("replace", "  - system_docs/patches/active/find_spell_by_id_id_maps_2026_10_11/\n",
     "  - system_docs/patches/completed/find_spell_by_id_id_maps_2026_10_11/\n"),
    ("before", "\n## Context / Handoff Summary\n", NOTES),
    ("after", "## Context / Handoff Summary\n", HANDOFF),
])

edit("attention_board.md", [
    ("replace", "| spell_lookup_race | in_progress | implementation | claude | melder_1 | none | Write the R6 patch docs, then build and "
                "test R6 in scratch, then land it as 0.2.8229 (ticket Note 29). | R6 landed with its tests, docs, notch and rebuilt "
                "assets. | Landed with checks green, then the owner accepts or redirects. | " + TICKET + " | 2026-10-11T01:07:38Z | REQUIRED |",
     "| spell_lookup_race | review | handoff | claude | melder_1 | none | Owner: git add -A (two new test files, the "
     "archived patch folder, r6/ evidence), commit and push; accept or redirect. | find_spell_by_id answers from the Book's "
     "id maps (0.2.8229); regression tests lock the lineage contract, the no-walk rule and the parked-disposal window. | "
     "The owner accepts or redirects; Windows tiers and hosted CI are the owner's. | " + TICKET + f" | {NOW} | REQUIRED |"),
    ("replace", "- spell_lookup_race: SWITCH_TRIGGER is R6 landed with green checks (Note 29 plan), then the owner's acceptance.\n",
     "- spell_lookup_race: SWITCH_TRIGGER is the owner's acceptance of the 0.2.8229 landing, or an owner redirect.\n"),
    ("before", "### Device VM git hazard (melder_2, 2026-09-26)\n",
     "### Notch notice (melder_1, 2026-10-11)\n"
     "- melder_1 landed 0.2.8229 (Spellbook.find_spell_by_id answers from the Book's id maps instead of walking the\n"
     "  live index map). Notch above it if you land after.\n"),
])

PATCH_ROWS = [l for l in (CC / "artifact_board.md").read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
              if "system_docs/patches/active/find_spell_by_id_id_maps_2026_10_11/" in l]
assert len(PATCH_ROWS) == 3, PATCH_ROWS
edit("artifact_board.md", [("replace", row + "\n", "") for row in PATCH_ROWS] + [
    ("replace", " The matrix's contract tests become the regression tests on approval. | 2026-10-10T22:20:34Z |",
     " r6/ (0.2.8229 landing: scripts, the two landed test files, new-test and full-tree runs). | " + NOW + " |"),
    ("after", "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
     "| " + TICKET + " | system_docs/patches/completed/find_spell_by_id_id_maps_2026_10_11/ | promote_to_documentation | "
     "Promoted to src_architecture and src_components (lookup by version id, 0.2.8229) and the graph at landing; three "
     "patch docs archived. | " + NOW + " |\n"),
])
print("NOW", NOW, FIND, ACC)

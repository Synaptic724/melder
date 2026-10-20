"""Turn in S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code (melder_0, 2026-10-18).

The docs checks' MEASURE note, the closure of both stories (completion summary naming the notch, Status done, the
closure checklist, the transition note, the handoff), the epic's note and handoff, the attention board (rows and
details out, two closed anchors in, the two oldest dropped, the epic row), the artifact board (S1's and S2's rows
cleared with their dispositions, a runs/ row, the scripts row), then - after the flush - the moves: both stories to
completed/, the patch folder to patches/completed/, staged/ into _to_delete/ (deletes need the owner's permission).
"""
import os
import sys
from typing import List

from docs_common import DocsRecord


class Close(DocsRecord):
    """The turn-in of S1 and S2."""

    A = "artifacts/spell_identity_20261018"
    PATCH = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18"
    DONE_PATCH = "system_docs/patches/completed/spell_identity_is_the_code_2026_10_18"
    S1_DONE = "tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md"
    S2_DONE = "tickets/stories/completed/2026-10-18_binding_manifest_hash_story.md"
    SUMMARY = {
        "s1": "notched 0.2.8257: a spell_id is the SHA256 of the registered object's code (SpellCodeDigest), nothing from "
              "the bind call; one object is one spell; examples, docs, system documents, graph and the Breaking "
              "release-note section carry it.",
        "s2": "notched 0.2.8258: the binding manifest and its hash (Spell.binding_manifest, Spell.binding_hash) key both "
              "creation-cache tiers (generation 23) and ride the SpellCrystal (record 4.3.0); a restore reports "
              "binding_changes; the release-note section \"A spell's binding is a manifest with its own hash\".",
    }

    def docs_note(self) -> str:
        return self.note(self.now, "MEASURE", [
            "The docs checks pass over the landed tree with both lanes' docs (this landing's pages and lessons, melder_2's",
            "managed spells chapter): docs unit tests OK; build_docs check - 313 pages, 54 assets; build - 313 pages",
            "(the only warning is melder's GIL-mode UserWarning at import); check_site - 39255 local links, sources",
            "match; check_seo with READTHEDOCS_CANONICAL_URL set - 0 errors, 303 warnings (missing descriptions, warnings",
            "by policy). Run in a /tmp mirror with a uv venv of docs/requirements.txt on CPython 3.14.7.",
        ], [self.whole(self.A + "/runs/docs_checks/summary.txt"),
            self.whole(self.A + "/runs/docs_checks/check_seo.txt")],
            ["Nothing in docs/ blocks the rebuild."], ["The closure of S1 and S2, then the rebuild."], "HELPFUL", 7)

    def close_story(self, rel: str, key: str, nxt_old: str) -> None:
        text = self.read(rel)
        title_end = text.index("\n") + 1
        text = text[:title_end] + f"\n- Completed: {self.now}\n- Summary: {self.SUMMARY[key]}\n" + text[title_end:]
        text = self.once(text, "- Status: in_progress\n", "- Status: done\n", f"{key} status")
        for box in ("Work walkthrough shared with user", "Criteria, required tests/reviews and delegated acceptance or "
                    "reserved-owner disposition recorded", "Applicable anti-pattern checks are clear or escalated with "
                    "evidence."):
            text = self.once(text, f"- [ ] {box}", f"- [x] {box}", f"{key} box")
        text = self.once(text, nxt_old, f"- Closed: {self.now} - {self.SUMMARY[key].split(':')[0]}; landed on the "
                         "owner's word\n  (the epic's DECISION notes of 2026-10-18T15:01:53Z and 16:18:35Z).\n",
                         f"{key} handoff")
        self.stage(rel, text)
        self.set_field(rel, "Updated")
        note = self.note(self.now, "DECISION", [
            f"State transition in_progress -> done ({self.SUMMARY[key].split(':')[0]}): the owner's word to land S1 with",
            "S2 and the crystallizer call are met - source, tests (whole tree green but melder_1's 18 S8 tests, the GIL",
            "off and on), examples, docs and their checks, the four system documents, the graph, the release note -",
            "and the rebuild follows as the landing's last step.",
        ], [self.doc_section(rel, "## Context / Handoff Summary")], [
            "The story moves to completed/; S3-S5 continue under the epic."], [
            "The rebuild for 0.2.8258."], "HELPFUL", 7)
        self.append_notes(rel, [note], f"{key} transition")

    def boards(self) -> None:
        board = self.read(self.BOARD).split("\n")
        board = [l for l in board if not (l.startswith("| spell_id_code_hash | ") or
                                          l.startswith("| binding_manifest_hash | ") or
                                          l.startswith("| managed_docs_release | done |") or
                                          l.startswith("| parked_versions_wired_at_conjure | done |"))]
        text = "\n".join(board)
        for item, story in (("spell_id_code_hash", "2026-10-18_spell_id_hashes_the_object_code_story.md"),
                            ("binding_manifest_hash", "2026-10-18_binding_manifest_hash_story.md")):
            lines = text.split("\n")
            i = lines.index(f"- WORK_ITEM: {item}")
            j = i + 1
            while lines[j].startswith("  "):
                j += 1
            if story not in "\n".join(lines[i:j]):
                sys.exit(f"detail {item}")
            text = "\n".join(lines[:i] + lines[j:])
        rows = text.split("\n")
        k = [n for n, l in enumerate(rows) if l.startswith("| spell_identity_is_the_code | ")]
        cells = rows[k[0]].split(" | ")
        cells[6] = "The rebuild for 0.2.8258 (last step of S1 and S2); then S3-S5, each after its own patch."
        cells[10] = self.now
        rows[k[0]] = " | ".join(cells)
        text = "\n".join(rows)
        anchors = (f"| spell_id_code_hash | done | melder_0 | {self.S1_DONE} | Landed 0.2.8257 (S1: a spell_id is the "
                   f"object's code, one object one spell). Next: S3-S5 under the epic. | {self.now} |\n"
                   f"| binding_manifest_hash | done | melder_0 | {self.S2_DONE} | Landed 0.2.8258 (S2: the binding "
                   f"manifest and its hash in the caches and the record). Next: S3-S5 under the epic. | {self.now} |\n")
        text = self.once(text, "<!-- BEGIN USER-DEFINED: closed_anchors -->\n",
                         "<!-- BEGIN USER-DEFINED: closed_anchors -->\n" + anchors, "anchors")
        head, rest = text.split("<!-- BEGIN USER-DEFINED: closed_anchors -->\n", 1)
        region, tail = rest.split("<!-- END USER-DEFINED: closed_anchors -->", 1)
        rows = [r for r in region.split("\n") if r.startswith("| ")]
        while len(rows) > 12:
            oldest = min(rows, key=lambda r: r.rstrip(" |").rsplit("| ", 1)[1])
            print("drop anchor", oldest.split(" | ")[0])
            rows.remove(oldest)
        text = (head + "<!-- BEGIN USER-DEFINED: closed_anchors -->\n" + "\n".join(rows) + "\n"
                + "<!-- END USER-DEFINED: closed_anchors -->" + tail)
        self.stage(self.BOARD, text)

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        cleared: List[str] = []
        plan = {
            self.A + "/staged/": (self.S1_DONE, self.A + "/_to_delete/staged/", "delete_on_close",
                                  "Moved with mv -n into _to_delete/ (deletes need the owner's permission); the modules "
                                  "and tests are in the repository (5e3800c7a)."),
            self.A + "/probes/": (self.S1_DONE, self.A + "/probes/", "retain_as_reference",
                                  "S1 closed (0.2.8257): the digest prototype, cases, corpus and bind-cost probes and "
                                  "their runs stay as its design evidence."),
            self.A + "/blast_radius/": (self.S1_DONE, self.A + "/blast_radius/", "retain_as_reference",
                                        "S1 closed (0.2.8257): the blast radius and the whole-tree runs stay as the "
                                        "landing's evidence."),
            self.PATCH + "/": ("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md", self.DONE_PATCH + "/",
                               "promote_to_documentation", "Promoted at landing (0.2.8257-0.2.8258) to the four system "
                               "documents and the graph; the six patch docs archived at S1 and S2's turn-in."),
            self.PATCH + "/component_patch_creation_cache.md": (self.S2_DONE, self.DONE_PATCH +
                                                                "/component_patch_creation_cache.md",
                                                                "promote_to_documentation", "Promoted at 0.2.8258; "
                                                                "archived with the folder."),
            self.PATCH + "/component_patch_crystallizer_record.md": (self.S2_DONE, self.DONE_PATCH +
                                                                     "/component_patch_crystallizer_record.md",
                                                                     "promote_to_documentation", "Promoted at 0.2.8258; "
                                                                     "archived with the folder."),
        }
        lines = text.split("\n")
        kept = []
        for line in lines:
            cells = line.split(" | ")
            if len(cells) == 8 and cells[1] in plan:
                ticket, path, disp, reason = plan.pop(cells[1])
                cleared.append(f"| {ticket} | {path} | {disp} | {reason} | {self.now} |")
                continue
            if len(cells) == 8 and cells[0] == "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md" and \
                    cells[1] == self.A + "/":
                cells[5] += ("; and checkin_reonboard.py, consume_m2_15.py, consume_m2_16_17.py, consume_m2_18_send_m0_203.py, "
                             "consume_m2_19.py, docs_common.py, land_docs_arch.py, land_docs_comp.py, "
                             "remap_s1s2_citations.py, record_landing_applied.py, record_docs_promotion.py, "
                             "record_ux_sweep.py, tests_edits_new_tests.py, rewrite_ux_examples.py, record_ux_rewrite.py, "
                             "rewrite_docs_identity.py, fix_docs_disposal_sentence.py, record_docs_sweep.py, "
                             "land_docs_tests_comp.py, land_docs_tests_arch.py, land_docs_src_followups.py, "
                             "record_tests_docs.py, land_graph_s1s2.py, notch_and_release_note.py, "
                             "record_graph_and_notch.py and close_s1_s2.py (the landing's docs, examples, graph, notch "
                             "and turn-in)")
                cells[6] = self.now
                line = " | ".join(cells)
            kept.append(line)
        if plan:
            sys.exit(f"artifact rows not found: {sorted(plan)}")
        text = "\n".join(kept)
        runs = (f"| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {self.A}/runs/ | measurement_evidence "
                f"| active | retain_as_reference | S1 and S2's runs: the probes' runs, bind cost, build parity and the -O "
                f"encodings, the examples' rewrite (ux_examples/), the docs sweep (docs_sweep/) and the docs checks "
                f"(docs_checks/). | {self.now} | HELPFUL |\n")
        text = self.once(text, "\n<!-- END USER-DEFINED: active_artifacts -->", "\n" + runs.rstrip("\n") +
                         "\n<!-- END USER-DEFINED: active_artifacts -->", "runs row")
        text = self.once(text, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                         "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + "\n".join(cleared) + "\n", "cleared")
        self.stage(self.ARTIFACTS, text)

    def epic(self) -> None:
        note = self.note(self.now, "FACT", [
            "S1 and S2 turned in: S1 notched 0.2.8257, S2 0.2.8258; both moved to completed/, their board rows and",
            "details out, two closed anchors in; the patch folder archived; staged/ moved into _to_delete/. S3 (a",
            "changed binding revalidates), S4 (the refusal names the existing registration) and S5 (records holding",
            "one object twice) stay draft, each after its own patch; S6 stays parked.",
        ], [f"context_compass/{self.S1_DONE}", f"context_compass/{self.S2_DONE}"], [
            "The epic's first milestone - identity is the code, the binding a manifest - is landed but for the rebuild."],
            ["The rebuild for 0.2.8258, then the NOTICEs to melder_1 (M1-40) and melder_2."], "REQUIRED", 8)
        self.append_notes(self.EPIC, [note], "epic close")
        text = self.read(self.EPIC)
        start = text.index("- Next: the docs checks, the release\n")
        end = text.index("\n\n## Project-Specific Additions")
        text = text[:start] + (f"- Done since: S1 and S2 turned in (FACT note of {self.now}).\n"
                               "- Next: the rebuild for 0.2.8258 (assets and LLM bundles, last); then a NOTICE hands\n"
                               "  spellbook.py and spell.py back to melder_1 (M1-40) and another tells melder_2 the\n"
                               "  rebuild carried its docs and bullet; then S3-S5, each after its own patch.") + text[end:]
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = Close("close_s1s2")
    record.append_notes(record.S1, [record.docs_note()], "s1 docs checks")
    record.close_story(record.S1, "s1", "- Next: the docs checks, the closure, the rebuild last.\n")
    record.close_story(record.S2, "s2", "- Next: with S1 - the docs checks, the closure, the rebuild last.\n")
    record.boards()
    record.artifacts()
    record.epic()
    for target in (record.S1_DONE, record.S2_DONE, record.DONE_PATCH, record.A + "/_to_delete/staged"):
        if (record.ROOT / target).exists():
            sys.exit(f"EXISTS {target}")
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()
    (record.ROOT / record.A / "_to_delete").mkdir(exist_ok=True)
    for src, dst in ((record.S1, record.S1_DONE), (record.S2, record.S2_DONE), (record.PATCH, record.DONE_PATCH),
                     (record.A + "/staged", record.A + "/_to_delete/staged")):
        os.rename(record.ROOT / src, record.ROOT / dst)
        print("moved", src, "->", dst)


if __name__ == "__main__":
    main()

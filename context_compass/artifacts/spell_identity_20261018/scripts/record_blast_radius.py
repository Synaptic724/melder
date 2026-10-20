"""Record the S1+S2 blast-radius run, the __annotate_func__ rule and S3's slot probe (melder_0, 2026-10-18).

S1 gets a MEASURE note (101 new failures by category, none a Melder defect) and a FACT note (Python 3.14 adds
`__annotate_func__` to a class's dict when its annotations are read); S2 a MEASURE note (S1 alone breaks the creation
cache across bindings, S2's keys repair it); S3 a FACT note (a rebind under another slotted existence meets the
removed definition's object); the epic a MEASURE note pointing at them. Handoffs, the artifact rows and the board
rows follow. No Decision Log line is added, so no note above moves and the citations written earlier stay true.
Ranges are computed from the files after staging. All-or-nothing; prose within 120 characters; no CR written.
"""
import datetime
import pathlib
import re
import shutil
import sys


class Pass:
    """One staged read-modify-write pass over the tickets and boards this record touches."""

    REPO = pathlib.Path.home() / "mnt/melder_private"
    ROOT = REPO / "context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t6")
    EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
    S2 = "tickets/stories/2026-10-18_binding_manifest_hash_story.md"
    S3 = "tickets/stories/2026-10-18_revalidate_on_binding_change_story.md"
    BOARD = "attention_board.md"
    ARTIFACTS = "artifact_board.md"
    BR = "artifacts/spell_identity_20261018/blast_radius"
    PROTO = "artifacts/spell_identity_20261018/probes/code_digest_v2.py"
    CODE_PATCH = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md"
    PROFILE = "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py"

    def __init__(self) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.staged: dict = {}

    def read(self, rel: str) -> str:
        if rel in self.staged:
            return self.staged[rel]
        return (self.ROOT / rel).read_text(encoding="utf-8")

    def stage(self, rel: str, text: str) -> None:
        self.staged[rel] = text

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        count = text.count(old)
        if count != 1:
            sys.exit(f"ANCHOR {label}: found {count}")
        for line in new.split("\n"):
            if len(line) > 120 and "context_compass/" not in line and not line.startswith("| "):
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")
        return text.replace(old, new)

    def whole(self, rel: str) -> str:
        count = len((self.ROOT / rel).read_text(encoding="utf-8").rstrip("\n").split("\n"))
        return f"context_compass/{rel}:1-{count}"

    def span(self, rel: str, first: str, last: str, base: str = "cc") -> str:
        root = self.ROOT if base == "cc" else self.REPO
        lines = (root / rel).read_text(encoding="utf-8").split("\n")
        starts = [i for i, line in enumerate(lines) if first in line]
        if len(starts) != 1:
            sys.exit(f"SPAN {first}: {len(starts)}")
        end = next((i for i in range(starts[0], len(lines)) if last in lines[i]), None)
        if end is None:
            sys.exit(f"SPAN END {last}")
        prefix = "context_compass/" if base == "cc" else ""
        return f"{prefix}{rel}:{starts[0] + 1}-{end + 1}"

    def method(self, rel: str, name: str) -> str:
        lines = (self.REPO / rel).read_text(encoding="utf-8").split("\n")
        starts = [i for i, line in enumerate(lines) if re.match(rf"^    def {re.escape(name)}\(", line)]
        if len(starts) != 1:
            sys.exit(f"METHOD {name}: {len(starts)}")
        start = starts[0]
        while start > 0 and lines[start - 1].startswith("    @"):
            start -= 1
        end = starts[0] + 1
        while end < len(lines) and not re.match(r"^    (def |@)", lines[end]) and not re.match(r"^class ", lines[end]):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"{rel}:{start + 1}-{end}"

    def note_range(self, rel: str, marker: str, type_line: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines)
                if line == marker and i + 3 < len(lines) and lines[i + 3] == type_line]
        if len(hits) != 1:
            sys.exit(f"NOTE {rel} {marker} {type_line}: found {len(hits)}")
        end = hits[0] + 1
        while end < len(lines) and lines[end] != "":
            end += 1
        return f"context_compass/{rel}:{hits[0] + 1}-{end}"

    @staticmethod
    def note(now: str, kind: str, claim: list, evidence: list, impact: list, nxt: list, reread: str,
             score: int) -> str:
        lines = [f"- DATETIME: {now}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer",
                 f"  TYPE: {kind}", "  CLAIM: " + claim[0]] + ["    " + c for c in claim[1:]]
        lines += ["  EVIDENCE:"] + [f"  - {e}" for e in evidence]
        lines += ["  IMPACT: " + impact[0]] + ["    " + c for c in impact[1:]]
        lines += ["  NEXT: " + nxt[0]] + ["    " + c for c in nxt[1:]]
        lines += [f"  REREAD: {reread}", f"  SCORE_0_TO_10: {score}"]
        return "\n".join(lines)

    def append_notes(self, rel: str, notes: list, label: str) -> None:
        text = self.read(rel)
        text = self.once(text, "\n\n## Closure Confirmation\n",
                         "\n\n" + "\n\n".join(notes) + "\n\n## Closure Confirmation\n", label)
        self.stage(rel, text)

    def set_updated(self, rel: str) -> None:
        text = self.read(rel)
        found = re.findall(r"^- Updated: \S+$", text, flags=re.M)
        if len(found) != 1:
            sys.exit(f"UPDATED {rel}: {len(found)}")
        self.stage(rel, text.replace(found[0], f"- Updated: {self.now}"))

    def s1(self) -> None:
        now = self.now
        measure = self.note(now, "MEASURE", [
            "The blast radius (the architecture patch's Migration step 2), measured in a /tmp mirror of 0.2.8255",
            "with nothing in the repository edited: the prototype code digest with decision B as the spell_id (in",
            "`Bind._bind_logic` and `spell_id_inspector`) and S2's binding hash in the creation cache's structural",
            "key and world stamp. The whole tree ran with the GIL off and on: 14542 tests each, 126 failed, 25 of them",
            "in the unpatched baseline (melder_1's S8 and S9 red tests), so 101 new failures - the same set in both",
            "modes - and none is a Melder defect: 88 register one object twice and meet strict uniqueness at bind",
            "(\"Spell ID collision detected\"); 1 binds one class in two frames' Books under process-wide ids and",
            "meets conjure's integrity check; 5 pin S2's cache format and stamp; 2 use `Bind.sha256_profile` as their",
            "oracle; 3 assert that a binding change moves the spell_id; 1 asserts the opposite of the owner's call 1",
            "(a base-class change); 1 expects the frame claim's message before the collision. triage.md lists each",
            "test and its rewrite. The landing's own whole-tree run gives the final count (the FACT note below).",
        ], [
            self.whole(f"{self.BR}/triage.md"),
            self.whole(f"{self.BR}/tally_output.txt"),
            self.whole(f"{self.BR}/mirror/_br_digest.py"),
            self.whole(f"{self.BR}/mirror/mirror_bind.diff"),
            self.whole(f"{self.BR}/mirror/mirror_structural_snapshot.diff"),
        ], [
            "The landing rewrites 101 tests by category - distinct classes or subclasses where a test wants two",
            "registrations, a refusal test where one object twice is the point, the new oracle, the reversed premises",
            "- and no src finding blocks S1.",
        ], ["The crystallizer record patch (S2); then S1 built in a /tmp working mirror from the code-description",
            "patch."], "REQUIRED", 9)
        fact = self.note(now, "FACT", [
            "Python 3.14 adds keys to a class's `__dict__` when its annotations are read: a class with no annotations",
            "gains `__annotate_func__` = None and `__annotations_cache__` (A1); a class with annotations holds",
            "`__annotate_func__` from creation and gains `__annotations_cache__` (A2). The prototype excluded only",
            "`__annotations_cache__`, so one class's spell_id differed before and after anything read its annotations",
            "(A3: False), and Melder reads them itself (the binding profile's `_read_class_annotations`). Skipping",
            "`__annotate_func__` while it is None keeps the id stable (A3: True), with the GIL off and on. The",
            "code-description patch's excluded keys and validation list gain that rule before SpellCodeDigest is",
            "written; a class with annotations keeps its annotate function in the encoding (its annotations' code).",
        ], [
            self.whole(f"{self.BR}/probes/probe_annotate_func_in_class_dict.py"),
            self.whole(f"{self.BR}/runs/probe_annotate_func_in_class_dict_gil0.txt"),
            self.whole(f"{self.BR}/runs/probe_annotate_func_in_class_dict_gil1.txt"),
            self.span(self.PROTO, "EXCLUDED_CLASS_KEYS = frozenset({", "})"),
            self.span(self.CODE_PATCH, "- Excluded class keys:", "__annotations_cache__"),
            self.method(self.PROFILE, "_read_class_annotations"),
        ], [
            "Without the rule a spell_id would depend on whether a class's annotations had been read before bind:",
            "unstable across processes and call orders, the opposite of S1's contract.",
        ], ["The rule into the code-description patch, with the crystallizer record patch."], "REQUIRED", 9)
        self.append_notes(self.S1, [measure, fact], "s1 notes")
        self.set_updated(self.S1)
        text = self.read(self.S1)
        text = self.once(
            text,
            "- Next: the blast-radius run in a /tmp mirror; the landing pass with S2 once spell.py and spellbook.py are\n"
            "  back (M1-37).\n",
            f"- Done since: the blast radius measured and the `__annotate_func__` rule found (MEASURE and FACT notes of\n"
            f"  {now}).\n"
            "- Next: the rule into the code-description patch; S1 built in a /tmp working mirror; the landing pass with\n"
            "  S2 once melder_1 hands back spell.py and spellbook.py after S9 (0.2.8256; M1-37).\n", "s1 handoff")
        self.stage(self.S1, text)

    def s2(self) -> None:
        now = self.now
        measure = self.note(now, "MEASURE", [
            "The blast-radius run shows S1 cannot land without S2's keys (the architecture patch's invariant 7): with",
            "the code digest alone (the unit and component tiers, the GIL off) 12 more component tests failed - 11 in",
            "test_conduit_component_purge.py, one in test_conduit_component_spellspace_creations.py - and all pass with",
            "the binding hash in the structural key and the world stamp (test_conduit_component_purge.py 79 of 79).",
            "Their parametrizations bind one class under several existences, so one spell_id named several bindings",
            "and a creation-cache bundle built for one binding was replayed for another: purges found nothing to",
            "remove (0 for 1) and a store came back None. With S2's keys the run's only other S2 effect is the 5",
            "tests that pin format 1 and the old stamp text, which move to format 2 and the new stamp lines.",
        ], [
            self.span(self.BR + "/triage.md", "## S1 alone", "S1 cannot land without S2's keys."),
            self.span(self.BR + "/triage.md", "## S2 structural format and stamp pins", "structural_payload_per_owned_spell"),
            self.whole(f"{self.BR}/mirror/mirror_structural_snapshot.diff"),
        ], [
            "The creation-cache patch's interface (format 2, the stamp lines, generation 23) is confirmed by the run;",
            "S1 and S2 stay one landing.",
        ], ["The crystallizer record patch."], "REQUIRED", 9)
        self.append_notes(self.S2, [measure], "s2 notes")
        self.set_updated(self.S2)
        text = self.read(self.S2)
        text = self.once(
            text,
            "- Next: the blast-radius record; the record patch; S2 built with S1 in a /tmp working mirror; the landing\n"
            "  pass once spell.py is back.\n",
            f"- Done since: the blast radius recorded (MEASURE note of {now}).\n"
            "- Next: the record patch; S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is\n"
            "  back.\n", "s2 handoff")
        self.stage(self.S2, text)

    def s3(self) -> None:
        now = self.now
        inventory = self.note_range(self.S2, "- DATETIME: 2026-10-18T15:45:30Z", "  TYPE: FACT")
        fact = self.note(now, "FACT", [
            "For S3, answered by probe (the UNKNOWN in S2's inventory note): under S1 and S2 (the blast-radius",
            "mirror) a rebind of one class under another existence after `cleanup_spell` keeps its spell_id, and on a",
            "root the new binding's first meld returns the object the removed definition left in its slot whenever",
            "both existences are slotted (unique -> unique_per_conduit and unique_per_conduit -> unique:",
            "second_meld_is_old_object=True); a `many` side builds fresh (unique_per_conduit -> many and",
            "many -> unique_per_conduit: False). unique -> unique is the case of the 2026-10-03 surviving-product",
            "ruling. The same with the GIL off and on. Today the existence is in the spell_id, so such a rebind is",
            "another spell_id and another slot; S1 changes that, and this story decides whether a slotted entry",
            "follows the new binding (kept per binding hash, or retired on a binding change).",
        ], [
            self.whole(f"{self.BR}/probes/probe_same_id_rebind_store.py"),
            self.whole(f"{self.BR}/runs/probe_same_id_rebind_store_gil0.txt"),
            self.whole(f"{self.BR}/runs/probe_same_id_rebind_store_gil1.txt"),
            inventory,
        ], [
            "Between S1 and S2's landing and this story's, a rebind under another slotted existence meets the removed",
            "definition's object: a RISK the epic carries to the release note unless this story lands in the same",
            "release.",
        ], ["This story's component patch, after S1 and S2."], "REQUIRED", 8)
        self.append_notes(self.S3, [fact], "s3 notes")
        self.set_updated(self.S3)

    def epic(self) -> None:
        now = self.now
        measure = self.note(now, "MEASURE", [
            "Migration step 2 is done: the blast radius of S1 and S2 is 101 new failures with the GIL off and on and",
            "none a Melder defect (S1's MEASURE note); S1 alone replays the creation cache across bindings and S2's",
            "keys repair it (S2's MEASURE note); a class's spell_id must not depend on whether its annotations were",
            "read, so the digest skips `__annotate_func__` while it is None (S1's FACT note); and until S3 lands a",
            "rebind under another slotted existence meets the object the removed definition left in its slot (S3's",
            "FACT note) - a RISK carried to the release note unless S3 lands in the same release.",
        ], [
            self.note_range(self.S1, f"- DATETIME: {now}", "  TYPE: MEASURE"),
            self.note_range(self.S1, f"- DATETIME: {now}", "  TYPE: FACT"),
            self.note_range(self.S2, f"- DATETIME: {now}", "  TYPE: MEASURE"),
            self.note_range(self.S3, f"- DATETIME: {now}", "  TYPE: FACT"),
        ], [
            "Nothing found blocks S1 and S2; the landing rewrites the 101 tests from triage.md.",
        ], ["The crystallizer record patch for S2; M0-198 to melder_1; S1 and S2 built in a /tmp working mirror."],
            "REQUIRED", 8)
        self.append_notes(self.EPIC, [measure], "epic notes")
        self.set_updated(self.EPIC)
        text = self.read(self.EPIC)
        text = self.once(
            text,
            "- Next: (1) record the blast-radius run (101 new failures, none a Melder defect); (2) the crystallizer\n"
            "  record patch for S2; (3) S1 and S2 built in a /tmp working mirror while S9 lands, then the landing pass -\n"
            "  red tests, src, green, the moved tests, the whole tree with the GIL off and on, docs, notches, the\n"
            "  rebuild last.\n",
            f"- Done since: the blast radius recorded (MEASURE note of {now}).\n"
            "- Next: (1) the crystallizer record patch for S2, with the `__annotate_func__` rule in the code-description\n"
            "  patch; (2) S1 and S2 built in a /tmp working mirror while S9 lands, then the landing pass - red tests,\n"
            "  src, green, the moved tests, the whole tree with the GIL off and on, docs, notches, the rebuild last.\n",
            "epic handoff")
        self.stage(self.EPIC, text)

    def boards(self) -> None:
        now = self.now
        art = self.read(self.ARTIFACTS)
        row = (f"| {self.S1} | {self.BR}/ | measurement_evidence | active | retain_as_reference | The blast radius of S1 "
               "and S2 (triage.md: 101 new failures by category, none a Melder defect; tally, ids, the mirror's digest "
               "and diffs, the runs gzip'd - baseline, S1 and S2 with the GIL off and on, S1 alone) and the probes of "
               "the `__annotate_func__` rule and S3's slot reuse with their runs; the landing rewrites the tests from "
               f"triage.md. | {now} | REQUIRED |")
        art = self.once(art, "\n<!-- END USER-DEFINED: active_artifacts -->", "\n" + row + "\n<!-- END USER-DEFINED: "
                        "active_artifacts -->", "artifact row")
        old = re.findall(r"^\| tickets/epics/2026-10-18_spell_identity_is_the_code_epic\.md \| artifacts/spell_identity"
                         r"_20261018/ \| investigation_evidence \|.*$", art, flags=re.M)
        if len(old) != 1:
            sys.exit(f"scripts row: {len(old)}")
        cells = old[0].split(" | ")
        anchor = "and record_s2_patch_and_inventory.py (their record); probes/ and runs/ are rowed under S1."
        if anchor not in cells[5]:
            sys.exit("scripts row text")
        cells[5] = cells[5].replace(anchor, "and record_s2_patch_and_inventory.py (their record); "
                                    "consume_m1_37_record_crystal_call.py (M1-37 consumed, the owner's crystallizer "
                                    "call) and record_blast_radius.py (the blast radius recorded); probes/, runs/ and "
                                    "blast_radius/ are rowed under S1.")
        cells[6] = now
        art = art.replace(old[0], " | ".join(cells))
        self.stage(self.ARTIFACTS, art)
        board = self.read(self.BOARD)
        updates = {
            "spell_identity_is_the_code": (
                "The crystallizer record patch for S2; S1 and S2 in a /tmp working mirror until S9 (0.2.8256) hands "
                "back spell.py and spellbook.py.", None),
            "spell_id_code_hash": (
                "The __annotate_func__ rule into the code-description patch; S1 built in a /tmp working mirror; the "
                "landing after S9 (0.2.8256).", None),
            "binding_manifest_hash": (
                "The crystallizer record patch (the binding hash in the SpellCrystal); then S2 with S1 in the /tmp "
                "mirror.",
                "The bind signature a binding manifest with its own SHA256, in the creation cache's keys beside the "
                "spell_id and in the SpellCrystal."),
        }
        for item, (nxt, outcome) in updates.items():
            rows = re.findall(rf"^\| {item} \|.*$", board, flags=re.M)
            if len(rows) != 1:
                sys.exit(f"board row {item}: {len(rows)}")
            cells = rows[0].split(" | ")
            if len(cells) != 12:
                sys.exit(f"board row {item} cells {len(cells)}")
            cells[6] = nxt
            if outcome is not None:
                cells[7] = outcome
            cells[10] = now
            board = board.replace(rows[0], " | ".join(cells))
        self.stage(self.BOARD, board)

    def flush(self) -> None:
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        self.BACKUP.mkdir(parents=True, exist_ok=True)
        for rel, text in self.staged.items():
            shutil.copy2(self.ROOT / rel, self.BACKUP / (pathlib.Path(rel).name + ".pre_blast_radius"))
            (self.ROOT / rel).write_text(text, encoding="utf-8", newline="\n")
            print("wrote", rel)


if __name__ == "__main__":
    run = Pass()
    run.s1()
    run.s2()
    run.s3()
    run.epic()
    run.boards()
    run.flush()
    print("now", run.now)

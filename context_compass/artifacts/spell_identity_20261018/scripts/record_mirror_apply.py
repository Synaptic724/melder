"""S1 and S2 applied to the /tmp working mirror and smoke-checked: the stories' FACT notes, their handoffs, the epic's
handoff, the three board rows and the two artifact rows. One all-or-nothing pass (melder_0, 2026-10-18)."""
import sys

from cc_record import Record

SCRIPTS = "artifacts/spell_identity_20261018/scripts/"
RUNS = "artifacts/spell_identity_20261018/staged/runs/"


class RecordMirrorApply(Record):

    def in_row(self, row: str, old: str, new: str, label: str) -> str:
        """Replace inside one table row; the width rule exempts table rows, so the whole row is checked."""
        if row.count(old) != 1:
            sys.exit(f"ANCHOR {label}: found {row.count(old)}")
        row = row.replace(old, new)
        self.check_width(row, label)
        return row

    def s1(self) -> None:
        note = self.note(self.now, "FACT", [
            "S1 is applied to the /tmp working mirror (0.2.8256 plus the two new modules; nothing in the repository's",
            "src): one applier over every edit list, all anchors matched in check mode, then written. edits_bind:",
            "26 edits, one of them the 246-line cut of the old inspector and `sha256_profile`; edits_spell: 19;",
            "edits_profiles: binding_profile.py 22 and binding_profile_strategy.py 13 (the fingerprint-only fields",
            "and the `stable_repr` calls that filled them removed, the docstrings corrected); edits_statements: 21 -",
            "spellbook.py 7 (`inspect_spell`'s stage 3 and its two comments, the conjure refusal, both collision",
            "refusals, which now name the colliding spell_id, and the research entry's Args), lookup_container.py,",
            "aether.py, aether_configuration.py (2), the three meld doors, meld.py's two resolvers, details.py (2),",
            "inspector_utility.py, spell_system_states.py and spell_index.py. The sweep of src/ for \"fingerprint\"",
            "found three statements the architecture patch's table did not list (the research entry's",
            "\"Binding-signature SHA256\", spell_system_states.py's \"the same class at the same address mints the same",
            "id\", spell_index.py's \"hottest fingerprint read\"); what still says fingerprint is the crystallizer's",
            "module and seal fingerprints, the codegen's row constants, generation 22's history comment and the new",
            "modules' mentions of the retired fingerprint. binding_profile_strategy.py mixes CRLF (244 lines) and LF",
            "(77) in the working tree while git holds it LF; the applier writes it all CRLF, as binding_profile.py is.",
            "Smoke on the mirror, the GIL off and on, identical: a bound class's spell_id is SpellCodeDigest's, its",
            "Spell carries its binding manifest, a second registration under another binding name and existence is",
            "refused with the new text naming the spell_id, and `inspect_spell` finds the class after conjure (an",
            "unbound class: None).",
        ], [
            self.whole(SCRIPTS + "apply_s1_s2.py"),
            self.whole(SCRIPTS + "edits_statements.py"),
            self.whole(SCRIPTS + "edits_profiles.py"),
            self.whole(RUNS + "mirror_s1s2_src.diff"),
            self.whole(RUNS + "mirror_smoke_s1s2_gil0.txt"),
            self.whole(RUNS + "mirror_smoke_s1s2_gil1.txt"),
            self.doc_section(self.PATCHES + "/architecture_patch.md", "## Statements That Define the spell_id Today"),
            "src/melder/aether/spellbook/spellbook.py:2544-2675",
        ], [
            "S1's source edits are complete in the mirror; before the landing come its tests - the digest's cases",
            "as unit tests, red against the repository's src and green on the mirror - the blast radius's 101",
            "rewrites and the whole tree with the GIL off and on; then docs, the notch and the rebuild.",
        ], [
            "test_spell_code_digest.py from the probes' cases (E01-E34, D1-D10, A1-A3, P1-P10, I1-I9) and the four",
            "refinements.",
        ], "REQUIRED", 9)
        self.append_notes(self.S1, [note], "S1 note")
        text = self.read(self.S1)
        text = self.once(text,
                         "- Next: S1 finished in the /tmp working mirror (the profiles, the statements); then the landing pass with S2,\n"
                         "  notched above 0.2.8256.\n",
                         "- Done since: S1 applied to the /tmp working mirror with S2 - the profiles and the statements sweep -\n"
                         f"  and smoke-checked (FACT note of {self.now}).\n"
                         "- Next: the red tests in the mirror (the digest's cases first); then the 101 moved tests, the whole tree\n"
                         "  with the GIL off and on, and the landing pass with S2, notched above 0.2.8256.\n", "S1 next")
        self.stage(self.S1, text)
        self.set_field(self.S1, "Updated")

    def s2(self) -> None:
        note = self.note(self.now, "FACT", [
            "S2 is applied with S1 to the /tmp working mirror in the same pass. The cache keys (edits_cache):",
            "structural_snapshot.py 8 - PAYLOAD_FORMAT 2, the key's `binding_hash`, the world stamp's",
            "`<spell_id>=<binding_hash>` lines for the pool's and the borrowed spells, the class, key and stamp",
            "docstrings; caching_system.py 3 - generation 23 \"binding_manifest_keys\" and its history comment;",
            "spellbook_creation_system.py 2; the generalized compiler's comment and the manifest's docstring. The",
            "crystal's record (edits_crystal): spell_crystal.py 7 - the `_binding_hash` slot captured from",
            "`spell.binding_hash`, its property, `describe()`'s key and cleanup's del; record_version.py CURRENT",
            "4.3.0; restore_engine.py 20 - RestoreReport's `binding_changes` (`record_binding_change`, its describe",
            "key and cleanup) and the engine's `_record_binding_change`, called from `_bind_one_active` and",
            "`_bind_one_staged`, with the docstrings; graft_runner.py 3 docstrings. The smoke's bound class",
            "carries its manifest and binding hash, the GIL off and on.",
        ], [
            self.whole(SCRIPTS + "edits_cache.py"),
            self.whole(SCRIPTS + "edits_crystal.py"),
            self.whole(RUNS + "mirror_s1s2_src.diff"),
            self.whole(RUNS + "mirror_smoke_s1s2_gil0.txt"),
        ], [
            "S2's source edits are complete in the mirror; its tests follow S1's in the same tranche.",
        ], [
            "The red tests for the manifest, the cache keys and stamp (format 2, generation 23), the record (4.3.0)",
            "and restore's binding_changes.",
        ], "REQUIRED", 9)
        self.append_notes(self.S2, [note], "S2 note")
        text = self.read(self.S2)
        text = self.once(text,
                         "- Next: S2 finished with S1 in the /tmp working mirror (the cache keys, the crystal's record); then\n"
                         "  the landing pass.\n",
                         "- Done since: the cache keys (format 2, generation 23) and the crystal's record (4.3.0, the binding hash,\n"
                         f"  restore's binding_changes) applied with S1 to the /tmp working mirror (FACT note of {self.now}).\n"
                         "- Next: the red tests in the mirror (the manifest, the cache keys and stamp, the record and its restore);\n"
                         "  then the landing pass with S1.\n", "S2 next")
        self.stage(self.S2, text)
        self.set_field(self.S2, "Updated")

    def epic(self) -> None:
        text = self.read(self.EPIC)
        text = self.once(text,
                         "- Next: (1) S1 and S2 finished in the /tmp working mirror (profiles, cache keys, record, statements); (2) the\n"
                         "  landing pass - red tests, src,\n"
                         "  green, the moved tests, the whole tree with the GIL off and on, docs, notches, the rebuild last.\n",
                         "- Done since: S1 and S2 applied to the /tmp working mirror and smoke-checked, the GIL off and on (the\n"
                         f"  stories' FACT notes of {self.now}).\n"
                         "- Next: (1) the red tests in the mirror - the digest's cases, the manifest, the cache keys, the record -\n"
                         "  then the 101 moved tests and the whole tree with the GIL off and on; (2) the landing pass - src,\n"
                         "  green, docs, notches, the rebuild last.\n", "epic next")
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")

    def board(self) -> None:
        text = self.read(self.BOARD)
        rows = [
            ("| S1 and S2 finished in the /tmp working mirror (S9 landed as 0.2.8256; spell.py and spellbook.py are back, "
             "M1-38); then the landing pass. |",
             "| S1 and S2 applied in the /tmp mirror; the red tests there, then the moved tests and the whole tree (GIL off "
             "and on), then the landing pass. |"),
            ("| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | 2026-10-18T17:23:22Z |",
             f"| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {self.now} |"),
            ("| S1 finished in the /tmp working mirror; then the landing with S2 (S9 landed as 0.2.8256). |",
             "| S1 applied in the /tmp mirror with S2; its red tests (the digest's cases), then the landing with S2. |"),
            ("| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | 2026-10-18T17:23:22Z |",
             f"| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | {self.now} |"),
            ("| S2 (the manifest, the cache keys, the crystal's record) finished with S1 in the /tmp mirror; then the "
             "landing (S9 landed as 0.2.8256). |",
             "| S2 applied in the /tmp mirror with S1; its red tests (manifest, cache keys, record), then the landing "
             "with S1. |"),
            ("| tickets/stories/2026-10-18_binding_manifest_hash_story.md | 2026-10-18T17:23:22Z |",
             f"| tickets/stories/2026-10-18_binding_manifest_hash_story.md | {self.now} |"),
        ]
        for index, (old, new) in enumerate(rows):
            text = self.once(text, old, new, f"board row {index}")
        self.stage(self.BOARD, text)

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        lines = text.split("\n")
        scripts = [i for i, line in enumerate(lines)
                   if "| artifacts/spell_identity_20261018/ | investigation_evidence |" in line]
        staged = [i for i, line in enumerate(lines)
                  if "| artifacts/spell_identity_20261018/staged/ | implementation_staging |" in line]
        if len(scripts) != 1 or len(staged) != 1:
            sys.exit(f"artifact rows: {len(scripts)}, {len(staged)}")
        row = lines[scripts[0]]
        row = self.in_row(row, "consume_m1_38.py (M1-38 consumed); probes/",
                        "consume_m1_38.py (M1-38 consumed); edits_profiles.py, edits_cache.py, edits_crystal.py and "
                        "edits_statements.py (S1's profiles and statements, S2's cache keys and record) and "
                        "record_mirror_apply.py (S1 and S2 applied to the mirror, recorded); probes/", "scripts row")
        row = self.in_row(row, "| 2026-10-18T17:23:22Z | HELPFUL |", f"| {self.now} | HELPFUL |", "scripts stamp")
        lines[scripts[0]] = row
        row = lines[staged[0]]
        row = self.in_row(row, "runs/ holds the probes re-run against them (cases, design edges, corpus, stability).",
                        "runs/ holds the probes re-run against them (cases, design edges, corpus, stability) and the "
                        "mirror's S1 and S2 src diff and smoke (mirror_s1s2_src.diff, mirror_smoke_s1s2*).",
                        "staged row")
        row = self.in_row(row, "| 2026-10-18T17:05:55Z | REQUIRED |", f"| {self.now} | REQUIRED |", "staged stamp")
        lines[staged[0]] = row
        self.stage(self.ARTIFACTS, "\n".join(lines))


def main() -> None:
    record = RecordMirrorApply("mirror_apply")
    record.s1()
    record.s2()
    record.epic()
    record.board()
    record.artifacts()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()

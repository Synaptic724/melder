"""Write S2's crystallizer record patch and align the patch folder and the tickets (melder_0, 2026-10-18).

The new component_patch_crystallizer_record.md (the binding hash in the SpellCrystal, record 4.3.0, the restore
report's binding changes) from /tmp/m0_mq/drafts; the architecture patch (matrix row, interface delta, statements
row, the measured blast radius, the accepted third-party reading, two RISKs, migration steps 2 and 4, handoff); the
Binding Pipeline patch's S2 consumers; the code-description patch's `__annotate_func__` rule; the creation-cache
patch's dependency line; S2's task, artifact link, PLAN mapping and handoff; S1's and the epic's handoffs; the
artifact rows and the board rows. Earlier session citations are resynced. All-or-nothing via cc_record.Record.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cc_record import Record  # the shared staged-pass helper beside this script


class Pass(Record):
    """The record-patch pass."""

    ARCH = Record.PATCHES + "/architecture_patch.md"
    PIPE = Record.PATCHES + "/component_patch_binding_pipeline.md"
    CODE = Record.PATCHES + "/code_description_patch_spell_code_digest.md"
    CACHE = Record.PATCHES + "/component_patch_creation_cache.md"
    CRYSTAL = Record.PATCHES + "/component_patch_crystallizer_record.md"
    DRAFT = pathlib.Path("/tmp/m0_mq/drafts/component_patch_crystallizer_record.md")

    def new_patch(self) -> None:
        if (self.ROOT / self.CRYSTAL).exists():
            sys.exit("record patch exists")
        text = self.DRAFT.read_text(encoding="utf-8").replace("@NOW@", self.now)
        self.check_width(text, "record patch")
        self.stage(self.CRYSTAL, text)

    def arch(self) -> None:
        now = self.now
        self.set_field(self.ARCH, "Updated")
        text = self.read(self.ARCH)
        rows = [line for line in text.split("\n") if line.startswith("| Creation cache (S2):")]
        if len(rows) != 1:
            sys.exit("arch cache row")
        row = ("| Crystallizer record (S2, on the owner's word): `SpellCrystal` records the binding hash; `RecordVersion` "
               "4.3.0; `RestoreReport` and `RestoreEngine` report a binding a restore rebuilt differently; restore and graft "
               "docstrings | modify | the owner (chat 2026-10-18): \"make sure you land the binding hash going into "
               "crystallizer too\" (component_patch_crystallizer_record.md) | Binding manifest |")
        text = self.once(text, rows[0] + "\n", rows[0] + "\n" + row + "\n", "arch matrix")
        text = self.once(
            text,
            "  shows both, and both creation-cache tiers key on the binding hash beside the spell_id.\n",
            "  shows both, and both creation-cache tiers key on the binding hash beside the spell_id. The SpellCrystal\n"
            "  records the binding hash (record 4.3.0) and a restore reports each binding it rebuilt differently from the\n"
            "  record (component_patch_crystallizer_record.md, on the owner's word).\n", "arch interface")
        statement = ("| `restore_engine.py` (`RestoreReport.map_identity`, `RestoreEngine._replay_books_and_binds`, "
                     "`_bind_one_active`, `_bind_one_staged`, `_map_spell_identity`, `_replay_contracts`, "
                     "`_replay_one_contract`), `graft_runner.py` (`_bind_selected`, `_merge_members`) | \"receiving "
                     "policy can change the new SHA\" | S1 (with S2's record patch) |")
        text = self.once(
            text,
            "| the crystallizer's record and restore docs, the system documents, the README | recorded ids | S5 |\n",
            statement + "\n"
            "| the crystallizer's record and restore docs, the system documents, the README | recorded ids | S5 |\n",
            "arch statements")
        text = self.once(
            text,
            "- UNKNOWN: the test suite's blast radius (step 2 measures it).\n",
            "- MEASURED (2026-10-18, step 2): the blast radius is 101 new failures with the GIL off and on, none a Melder\n"
            "  defect (S1's MEASURE note); S1 without S2's keys replays the creation cache across bindings (S2's MEASURE\n"
            "  note); a class's id must skip `__annotate_func__` while it is None (code-description patch).\n"
            "- RISK (until S3 lands): a rebind under another slotted existence - `cleanup_spell`, then `bind` as\n"
            "  `unique_per_conduit` of a class bound `unique` - keeps its spell_id, and its first meld returns the object\n"
            "  the removed definition left in its slot (S3's FACT note); listed in the release note unless S3 lands in\n"
            "  the same release.\n"
            "- RISK (until S5 lands): a record written before S1 that holds one object twice fails to restore at its second\n"
            "  replayed bind (component_patch_crystallizer_record.md, Failure Mode Deltas).\n", "arch unknowns")
        text = self.once(
            text,
            "  uniqueness would then refuse the second; the owner can narrow it to type and version.\n",
            "  uniqueness would then refuse the second; the owner accepted this reading as written (chat 2026-10-18:\n"
            "  \"those 3 things for library version are fine\").\n", "arch B")
        text = self.once(
            text,
            "   twice, a pinned id, a message text, a real defect) and reported before any src edit.\n",
            "   twice, a pinned id, a message text, a real defect) and reported before any src edit. Done 2026-10-18:\n"
            "   101 new failures with the GIL off and on, none a Melder defect (S1's MEASURE note).\n", "arch step 2")
        text = self.once(
            text,
            "4. spell.py and spellbook.py back from melder_1 by message (M0-196): S9 holds them (M1-33, M1-35); their order\n"
            "   waits for the owner's pick in S9 - under the refusal S9 lands first, under the hole rule after S1 (M1-36,\n"
            "   M1-37). S8 is on hold.\n",
            "4. spell.py and spellbook.py back from melder_1 by message once S9 lands: the owner chose the refusal, so S9\n"
            "   lands first as 0.2.8256 (M1-37); S1 and S2 are built and run in a /tmp mirror until then. S8 is on hold.\n",
            "arch step 4")
        text = self.once(
            text,
            "- What remains: the blast-radius run (step 2); spell.py and spellbook.py back from melder_1 (M0-196; their order\n"
            "  waits for the owner's pick in S9, M1-36); the landing pass (step 5).\n"
            "- Next entrypoint: component_patch_binding_pipeline.md, component_patch_creation_cache.md, then\n"
            "  code_description_patch_spell_code_digest.md.\n",
            f"- What changed since ({now}): the blast radius measured (step 2); the owner's word to land the\n"
            "  binding hash in the SpellCrystal and his acceptance of the third-party reading; the crystallizer record patch.\n"
            "- What remains: spell.py and spellbook.py back from melder_1 after S9 (0.2.8256; M1-37); the landing pass\n"
            "  (step 5).\n"
            "- Next entrypoint: component_patch_binding_pipeline.md, component_patch_creation_cache.md,\n"
            "  component_patch_crystallizer_record.md, then code_description_patch_spell_code_digest.md.\n",
            "arch handoff")
        self.stage(self.ARCH, text)

    def pipe(self) -> None:
        self.set_field(self.PIPE, "Updated")
        text = self.read(self.PIPE)
        text = self.once(
            text,
            "- Consumers in this landing: the creation cache (component_patch_creation_cache.md). Later: S3 revalidates a\n"
            "  spell whose binding hash changes; S5 adds the hash to the SpellCrystal with the record's other changes (the\n"
            "  crystal already records every field, and a restore replays them through bind, which rebuilds the same hash).\n",
            "- Consumers in this landing: the creation cache (component_patch_creation_cache.md) and, on the owner's word, the\n"
            "  SpellCrystal, which records the hash, and restore, which reports a binding it rebuilt differently from the\n"
            "  record (component_patch_crystallizer_record.md). Later: S3 revalidates a spell whose binding hash changes.\n",
            "pipe consumers")
        text = self.once(
            text,
            "- UNKNOWN: how many tests outside the 14 bind one object twice (the blast-radius run measures it).\n",
            "- MEASURED (2026-10-18): 89 tests register one object twice; the landing rewrites them, none is a Melder\n"
            "  defect (the blast radius, S1's MEASURE note).\n", "pipe unknown")
        self.stage(self.PIPE, text)

    def code(self) -> None:
        self.set_field(self.CODE, "Updated")
        text = self.read(self.CODE)
        text = self.once(
            text,
            "  (derived from the methods' code), `__annotations_cache__` (filled when annotations are read). Opaque key:\n"
            "  `_abc_impl` (ABCMeta's registry, mutated by `register` and isinstance checks).\n",
            "  (derived from the methods' code), `__annotations_cache__` (filled when annotations are read), and\n"
            "  `__annotate_func__` while it is None: 3.14 writes it, with the cache, the first time anything reads the\n"
            "  annotations of a class that has none, and Melder reads them at bind; a class with annotations holds its\n"
            "  annotate function from creation, and that function is encoded (blast-radius probe A1-A3). Opaque key:\n"
            "  `_abc_impl` (ABCMeta's registry, mutated by `register` and isinstance checks).\n", "code excluded")
        text = self.once(
            text,
            "  `ABC.register` do not (E25, E25b, E25c).\n",
            "  `ABC.register` do not (E25, E25b, E25c; for a class without annotations through the excluded\n"
            "  `__annotate_func__`, probe A3).\n", "code mutable")
        text = self.once(
            text,
            "  installed packages like the application).\n",
            "  installed packages like the application); `__annotate_func__` excluded while None (the prototype excluded\n"
            "  only `__annotations_cache__`, so a class without annotations changed id once they were read).\n",
            "code changed")
        text = self.once(
            text,
            "  third-party object by type, version and repr, an application or `__main__` class digested.\n",
            "  third-party object by type, version and repr, an application or `__main__` class digested.\n"
            "- The annotate key (blast-radius probe A1-A3): a class without annotations keeps its id when its annotations\n"
            "  are read, and a class with annotations keeps its id too (only the cache is added).\n", "code validation")
        self.stage(self.CODE, text)

    def cache(self) -> None:
        self.set_field(self.CACHE, "Updated")
        text = self.read(self.CACHE)
        text = self.once(
            text,
            "1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py\n"
            "   (M0-196; the order waits for the owner's pick in S9, M1-36).\n",
            "1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py\n"
            "   (back from melder_1 after S9 lands as 0.2.8256; M1-37).\n", "cache dependency")
        self.stage(self.CACHE, text)

    def tickets(self) -> None:
        now = self.now
        self.set_field(self.S2, "Updated")
        s2 = self.read(self.S2)
        s2 = self.once(
            s2,
            "- [ ] Task: the record patch - the binding hash in the SpellCrystal (the owner's word, DECISION note of\n"
            "  2026-10-18T16:18:35Z), before its code.\n",
            "- [x] Task: the record patch - the binding hash in the SpellCrystal (the owner's word, DECISION note of\n"
            "  2026-10-18T16:18:35Z), written as component_patch_crystallizer_record.md.\n", "s2 task")
        s2 = self.once(
            s2,
            "  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md (cache keys)\n",
            "  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_creation_cache.md (cache keys)\n"
            "  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_crystallizer_record.md (record)\n",
            "s2 links")
        s2 = self.once(
            s2,
            "- Done since: the blast radius recorded (MEASURE note of 2026-10-18T16:24:12Z).\n"
            "- Next: the record patch; S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is\n"
            "  back.\n",
            "- Done since: the blast radius recorded (MEASURE note of 2026-10-18T16:24:12Z); the record patch written and\n"
            f"  mapped (PLAN note of {now}).\n"
            "- Next: S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is back.\n", "s2 handoff")
        self.stage(self.S2, s2)
        plan = self.note(now, "PLAN", [
            "Patch section -> implementation -> validation for the record (component_patch_crystallizer_record.md),",
            "beside the PLAN note of 2026-10-18T15:45:30Z. (1) Interface Deltas, SpellCrystal -> spell_crystal.py:",
            "the `_binding_hash` slot appended, captured from `spell.binding_hash` with the bind-signature fields, the",
            "`binding_hash` property, the `describe()` key, `cleanup`'s del, the class and `__init__` contracts -> the",
            "crystal of a class, a staged version and a managed spell carries its spell's binding hash; cleanup",
            "deletes it. (2) RecordVersion -> record_version.py: CURRENT 4.3.0 and its history comment -> CURRENT is",
            "4.3.0 and a 4.2.0 payload passes `check_readable`. (3) RestoreReport and RestoreEngine -> restore_engine.py:",
            "`_binding_changes`, `record_binding_change`, `describe()[\"binding_changes\"]` and its cleanup; the engine's",
            "`_record_binding_change`, called by `_bind_one_active` and `_bind_one_staged` -> a restore under the",
            "recording policy reports none; under another disposal priority one per changed binding, the spell_ids",
            "unchanged and grants and selections found. (4) The docstring rows -> restore_engine.py and",
            "graft_runner.py -> the documentation ritual. Row (1) of the earlier mapping (spell.py's `binding_hash`)",
            "comes first.",
        ], [
            self.whole(self.CRYSTAL),
            self.note_range(self.S2, "- DATETIME: 2026-10-18T15:45:30Z", "  TYPE: PLAN"),
        ], ["The patch gate's consumption mapping for the record is in place before any crystallizer code."],
            ["S1 and S2 built in a /tmp working mirror."], "REQUIRED", 8)
        self.append_notes(self.S2, [plan], "s2 plan")
        self.set_field(self.S1, "Updated")
        s1 = self.read(self.S1)
        s1 = self.once(
            s1,
            "- Next: the rule into the code-description patch; S1 built in a /tmp working mirror; the landing pass with\n"
            "  S2 once melder_1 hands back spell.py and spellbook.py after S9 (0.2.8256; M1-37).\n",
            f"- Done since: the `__annotate_func__` rule written into the code-description patch ({now}).\n"
            "- Next: S1 built in a /tmp working mirror; the landing pass with S2 once melder_1 hands back spell.py and\n"
            "  spellbook.py after S9 (0.2.8256; M1-37).\n", "s1 handoff")
        self.stage(self.S1, s1)
        self.set_field(self.EPIC, "Updated")
        epic = self.read(self.EPIC)
        epic = self.once(
            epic,
            "- Next: (1) the crystallizer record patch for S2, with the `__annotate_func__` rule in the code-description\n"
            "  patch; (2) S1 and S2 built in a /tmp working mirror while S9 lands, then the landing pass - red tests,\n"
            "  src, green, the moved tests, the whole tree with the GIL off and on, docs, notches, the rebuild last.\n",
            "- Done since: the crystallizer record patch written and the `__annotate_func__` rule added to the\n"
            f"  code-description patch (S2's PLAN note of {now}).\n"
            "- Next: (1) S1 and S2 built in a /tmp working mirror while S9 lands; (2) the landing pass - red tests, src,\n"
            "  green, the moved tests, the whole tree with the GIL off and on, docs, notches, the rebuild last.\n",
            "epic handoff")
        self.stage(self.EPIC, epic)

    def boards(self) -> None:
        now = self.now
        art = self.read(self.ARTIFACTS)
        row = (f"| {self.S2} | {self.CRYSTAL} | patch_doc | active | promote_to_documentation | S2's record patch (the "
               "binding hash in the SpellCrystal, record 4.3.0, the restore report's binding changes), on the owner's "
               f"word (2026-10-18T16:18:35Z). | {now} | REQUIRED |")
        art = self.once(art, "\n<!-- END USER-DEFINED: active_artifacts -->",
                        "\n" + row + "\n<!-- END USER-DEFINED: active_artifacts -->", "artifact row")
        rows = re.findall(rf"^\| {re.escape(self.EPIC)} \| {re.escape(self.PATCHES)}/ \|.*$", art, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"patch folder row: {len(rows)}")
        cells = rows[0].split(" | ")
        anchor = "approved by the owner's word to land (2026-10-18T15:01:53Z); S3-S5 add theirs."
        if anchor not in cells[5]:
            sys.exit("patch folder row text")
        cells[5] = cells[5].replace(anchor, "approved by the owner's word to land (2026-10-18T15:01:53Z), and S2's "
                                    "crystallizer record patch on his word (16:18:35Z); S3-S5 add theirs.")
        cells[6] = now
        art = art.replace(rows[0], " | ".join(cells))
        self.stage(self.ARTIFACTS, art)
        board = self.read(self.BOARD)
        updates = {
            "spell_identity_is_the_code": "S1 and S2 built in a /tmp working mirror until S9 (0.2.8256) hands back "
                                          "spell.py and spellbook.py; then the landing pass.",
            "spell_id_code_hash": "S1 built in a /tmp working mirror; the landing with S2 after S9 (0.2.8256).",
            "binding_manifest_hash": "S2 (the manifest, the cache keys, the crystal's record) built with S1 in the "
                                     "/tmp mirror; the landing after S9.",
        }
        for item, nxt in updates.items():
            found = re.findall(rf"^\| {item} \|.*$", board, flags=re.M)
            if len(found) != 1:
                sys.exit(f"board row {item}: {len(found)}")
            cells = found[0].split(" | ")
            cells[6] = nxt
            cells[10] = now
            board = board.replace(found[0], " | ".join(cells))
        self.stage(self.BOARD, board)


if __name__ == "__main__":
    run = Pass("record_patch")
    run.new_patch()
    run.arch()
    run.pipe()
    run.code()
    run.cache()
    run.tickets()
    run.boards()
    run.resync()
    run.flush()
    print("now", run.now)

"""Align the spell_identity_is_the_code patch docs after update_patches_b_strict.py.

The re-read of the updated docs found: two matrix rows and the migration step still pointing at M1-31 / M0-196
alone, Spell's "no field changes" beside S2's manifest, D9's digest cost stated where decision B now names the
base, S6 missing from the coverage map, and no edge for a third-party object's repr. Staged edits; nothing is
written unless every anchor matches once.
"""
import pathlib
import shutil
import sys


class Align:
    """One read-modify-write pass over the patch folder, all-or-nothing."""

    FOLDER = (pathlib.Path.home()
              / "mnt/melder_private/context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18")
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t5")

    def __init__(self) -> None:
        self.pending: list = []

    def read(self, name: str) -> str:
        return (self.FOLDER / name).read_text(encoding="utf-8")

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        if text.count(old) != 1:
            sys.exit(f"ANCHOR {label}: found {text.count(old)}")
        for line in new.split("\n"):
            if len(line) > 120 and not line.startswith("|") and "`src/" not in line:
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")
        return text.replace(old, new)

    def architecture(self) -> None:
        t = self.read("architecture_patch.md")
        t = self.once(t, "| spellbook.py back from melder_1 (M1-31) |",
                      "| spellbook.py back from melder_1 (S9; M0-196, M1-36) |", "a row53")
        t = self.once(t, "(component_patch_binding_pipeline.md, S2 section) | S1 (same landing) |",
                      "(component_patch_binding_pipeline.md, S2 section) | S1 (same landing); spell.py back from "
                      "melder_1 (M0-196, M1-36) |", "a row55")
        t = self.once(t,
            "4. spell.py and spellbook.py back from melder_1 by message (M0-196): S9 holds them (M1-33, M1-35); S8 is on hold.\n",
            "4. spell.py and spellbook.py back from melder_1 by message (M0-196): S9 holds them (M1-33, M1-35); their order\n"
            "   waits for the owner's pick in S9 - under the refusal S9 lands first, under the hole rule after S1 (M1-36,\n"
            "   M1-37). S8 is on hold.\n", "a step4")
        t = self.once(t,
            "  0.064 ms, prototype cold median 0.29 ms and warm 0.11 ms); a class over a large third-party base (D9: 2.6-3.2 ms\n"
            "  cold, 1.9 ms warm, against 0.03 ms for a plain class).\n",
            "  0.064 ms, prototype cold median 0.29 ms and warm 0.11 ms); a class over a large third-party base (D9, digested:\n"
            "  2.6-3.2 ms cold, 1.9 ms warm, against 0.03 ms for a plain class), which decision B names instead - a\n"
            "  site-packages check and a distribution-version lookup (about 0.2 ms; 14.7 ms once per SpellCodeDigest when\n"
            "  `packages_distributions()` is needed, measured on the device) - measured on src at landing.\n", "a cost")
        t = self.once(t,
            "  STORY-2026-10-18-one_registration_per_object (S4), STORY-2026-10-18-spell_id_migration (S5).\n",
            "  STORY-2026-10-18-one_registration_per_object (S4), STORY-2026-10-18-spell_id_migration (S5);\n"
            "  STORY-2026-10-18-explicit_duplicate_binding (S6) is parked in the backlog.\n", "a coverage")
        t = self.once(t,
            "- What remains: the blast-radius run (step 2); spell.py and spellbook.py back from melder_1 (M0-196); the landing\n"
            "  pass (step 5).\n",
            "- What remains: the blast-radius run (step 2); spell.py and spellbook.py back from melder_1 (M0-196; their order\n"
            "  waits for the owner's pick in S9, M1-36); the landing pass (step 5).\n", "a handoff")
        self.pending.append(("architecture_patch.md", t))

    def binding_pipeline(self) -> None:
        t = self.read("component_patch_binding_pipeline.md")
        t = self.once(t, "- Spell and SpellIndex: no field changes.\n",
                      "- Spell and SpellIndex: no field changes for S1; S2 adds `Spell.binding_manifest` (S2 section).\n",
                      "b fields")
        t = self.once(t,
            "   docstrings, the S2 manifest) wait for both files to come back from melder_1 (M0-196; S9 holds them, M1-33).\n",
            "   docstrings, the S2 manifest) wait for both files to come back from melder_1 (M0-196; S9 holds them, M1-33;\n"
            "   their order waits for the owner's pick in S9, M1-36).\n", "b order")
        t = self.once(t,
            "- Remaining risks: the bind cost of classes over large third-party bases (D9); records holding one object twice (S5).\n",
            "- Remaining risks: the bind cost of the distribution-version lookup for installed packages (decision B; D9's\n"
            "  digest cost no longer applies to them); records holding one object twice (S5).\n", "b risks")
        self.pending.append(("component_patch_binding_pipeline.md", t))

    def creation_cache(self) -> None:
        t = self.read("component_patch_creation_cache.md")
        t = self.once(t,
            "1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py\n"
            "   (M0-196).\n",
            "1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py\n"
            "   (M0-196; the order waits for the owner's pick in S9, M1-36).\n", "c order")
        self.pending.append(("component_patch_creation_cache.md", t))

    def code_description(self) -> None:
        t = self.read("code_description_patch_spell_code_digest.md")
        t = self.once(t,
            "  (D6: two C `Mark` objects); today's rule has the same limit.\n",
            "  (D6: two C `Mark` objects); today's rule has the same limit.\n"
            "- An installed third-party object is its type, its distribution version and its repr (decision B): two objects\n"
            "  of one library class whose repr carries no data are one spell, as under today's rule; an upgrade of the\n"
            "  package moves the id of every spell that holds one or inherits from its code.\n", "d edge")
        self.pending.append(("code_description_patch_spell_code_digest.md", t))

    def run(self) -> None:
        self.architecture()
        self.binding_pipeline()
        self.creation_cache()
        self.code_description()
        for name, text in self.pending:
            if "\r" in text:
                sys.exit(f"CR in {name}")
            shutil.copy2(self.FOLDER / name, self.BACKUP / (name + ".pre_align"))
            (self.FOLDER / name).write_text(text, encoding="utf-8", newline="\n")
        print("OK", [name for name, _ in self.pending])


if __name__ == "__main__":
    Align().run()

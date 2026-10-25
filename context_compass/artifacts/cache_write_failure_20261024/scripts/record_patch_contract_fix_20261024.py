"""Record the patch docs' completion to their contracts (melder_0, 2026-10-24).

Reading the design_engineer patch contracts at F5 showed the patch docs short of them: the architecture patch had no
"Validation expectations and evidence plan" section, the two component patches no "Component purpose and boundary",
and the Spellbook patch also covered Spell (one component per file). They were completed and re-indexed; this pass
corrects Note 23's ranges, adds the Spell patch to its evidence and appends the FACT. All-or-nothing.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
PATCH = "system_docs/patches/active/cache_save_best_effort_2026_10_24"
CONTRACTS = "agent_onboarding/default/design_engineer/skills"


class Pass(Record):
    """The correction pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def main() -> None:
    r = Pass("record_patch_contract_fix")
    text = r.read(TICKET)
    old = "\n".join([
        f"  - context_compass/{PATCH}/architecture_patch.md:1-91",
        f"  - context_compass/{PATCH}/component_patch_caching_system.md:1-62",
        f"  - context_compass/{PATCH}/component_patch_spellbook_cache_save.md:1-56"]) + "\n"
    new = "\n".join([
        f"  - {r.whole(PATCH + '/architecture_patch.md')}",
        f"  - {r.whole(PATCH + '/component_patch_caching_system.md')}",
        f"  - {r.whole(PATCH + '/component_patch_spellbook_cache_save.md')}",
        f"  - {r.whole(PATCH + '/component_patch_spell_emit_cache_file.md')}"]) + "\n"
    text = r.once(text, old, new, "note 23 ranges")
    fact = r.note(r.now, "FACT", [
        "Correction to F4 (Note 23): reading the design_engineer patch contracts before the system-doc edits showed",
        "the patch docs short of them - the architecture patch had no \"Validation expectations and evidence plan\"",
        "section, the CachingSystem and Spellbook component patches no \"Component purpose and boundary\", and the",
        "Spellbook patch also covered Spell against one component per file. The sections were added (MUST wording for",
        "the boundaries), Spell got component_patch_spell_emit_cache_file.md, every patch doc was re-indexed and Note",
        "23's ranges now point at the completed files. The content the src change followed did not change: the added",
        "text restates the boundaries and the validation already mapped, so M1-M2 and F6 stand."],
        [r.whole(f"{CONTRACTS}/architecture_patch_contracts.md"),
         r.whole(f"{CONTRACTS}/component_patch_contracts.md"),
         r.whole(PATCH + "/architecture_patch.md"),
         r.whole(PATCH + "/component_patch_spell_emit_cache_file.md")],
        ["The patch gate's contract-quality check now holds for the record; no rework of code or tests."],
        ["F5: the system docs, starting with src_architecture."], "HELPFUL", 7)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + fact + "\n\n## Context / Handoff Summary\n",
                  "note")
    text = r.once(text, f"  - {PATCH}/ (four patch docs and their indexes)\n",
                  f"  - {PATCH}/ (five patch docs and their indexes)\n", "artifact path")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()

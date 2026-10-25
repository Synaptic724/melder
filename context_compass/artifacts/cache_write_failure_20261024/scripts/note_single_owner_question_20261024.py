"""Record the owner's single-owner question on TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0).

Appends one FACT Note after Note 12, refreshes Updated and names the Note in the summary. All-or-nothing: anchors
match once, lines fit 120 characters, no CR.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"


def main() -> None:
    r = Record("note_single_owner_question")
    note = r.note(r.now, "FACT", [
        "The owner asked (chat 2026-10-24) whether one module could own the cache entirely, serialize its reads and",
        "writes and never keep the file open. That module exists: `CachingSystem` is built in one place only",
        "(`Spellbook._get_or_create_caching_system`, once per Book), and a search of src/melder finds no other code",
        "that reads or writes a conjure-cache file - one `read_bytes` at construction, then `mkdir`, `write_bytes`",
        "and `replace` per save, under its lock. Each call opens and closes the file, so Melder holds no handle",
        "between calls. One owner per file keeps Books from waiting on each other; another serializer (or a",
        "mediator) on top would add waiting and overhead and change nothing about the refusal."],
        ["src/melder/aether/spellbook/spellbook.py:1023-1062",
         "src/melder/utilities/caching_system/caching_system.py:766-789",
         "src/melder/utilities/caching_system/caching_system.py:885-918"],
        ["The fix belongs inside CachingSystem and its one caller: tolerate a refused save (directions 1 and 2) and",
         "save less often (direction 3, which also takes the whole-file rewrite off most melds); no new layer."],
        ["The owner picks a direction and an executor."], "HELPFUL", 8)
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + note + "\n\n## Context / Handoff Summary\n",
                  "note")
    text = r.once(text, "aetheric mediator in Note 12: neither can reach the refusal, which comes from outside Melder.\n",
                  "aetheric mediator in Note 12: neither can reach the refusal, which comes from outside Melder. Note 13:\n"
                  "CachingSystem already is the single owner of each cache file; no new layer is needed.\n", "summary")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.flush()


if __name__ == "__main__":
    main()

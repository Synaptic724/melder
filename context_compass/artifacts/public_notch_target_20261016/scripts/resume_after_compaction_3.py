"""Refresh the board row and the ticket's resume view after the 15:31Z re-onboarding.

Usage: python resume_after_compaction_3.py <NOW>   (run from context_compass/)
"""
import pathlib
import sys

now = sys.argv[1]

board = pathlib.Path("attention_board.md")
text = board.read_text(encoding="utf-8")
lines = text.split("\n")
hits = [i for i, l in enumerate(lines) if l.startswith("| public_notch_target |")]
assert len(hits) == 1, hits
cells = lines[hits[0]].split(" | ")
# cells: [0]'| work_item', status, mode, owner, agent_name, blocker, next, outcome, exit_signal, ticket, updated_at, 'reread |'
assert len(cells) == 12, len(cells)
cells[6] = ("Finish the spell_id wording, release note and system docs for the add/remove extension; then archive "
            "the lane, close with NOTICE M0-177 and rebuild last.")
cells[7] = ("`Conduit.notch_spell(spell_index=..., spell_id=...)` notches to a staged version on public calls, its "
            "target checked before the transaction; `add_to_spell_index` / `remove_from_spell_index` take "
            "`spell_id=` too; the README and docs loops run as written.")
cells[10] = now
lines[hits[0]] = " | ".join(cells)
board.write_text("\n".join(lines), encoding="utf-8")

ticket = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")
t = ticket.read_text(encoding="utf-8")
start = t.index("## Context / Handoff Summary\n")
end = t.index("## Project-Specific Additions\n")
summary = """## Context / Handoff Summary
- Scope: `Conduit.notch_spell(spell_index=..., spell_id=...)` - option A, the owner's choice - so the stage ->
  notch -> meld loop runs on public calls; on the owner's extension (Notes 15:04:47Z) `add_to_spell_index` and
  `remove_from_spell_index` take `spell_id=` too, and the lane's text says spell_id, not "version id".
- State: in_progress (melder_0), implementation; notched 0.2.8249, which carries the notch target and the
  extension. Done: the notch target with its tests, docs, system docs, graph, release-note section and archived
  patch lane (Notes 13:28:26Z-14:23:00Z); the owner's answer (15:04:47Z); the lane reopened with the mapping
  (15:10:41Z); the extension built, red then green, regression with the GIL off and on (15:23:08Z); codex_mcp.md
  rewritten to the off notice; governed-change.md and UX expert 17 and 26 reworded to spell_id.
- Remaining: rerun lessons 17 and 26; the spell_id wording in the concept map, the two notch test files'
  docstrings and the release note (retitled, the add/remove bullets and the new messages, probed again); the
  system docs and their indexes, the graph descriptor and census, the tests docs; the patch lane archived again;
  the closure (summary "notched 0.2.8249" naming the release-note section, move to completed/, board sync
  dropping the oldest anchor, NOTICE M0-177 releasing conduit.py to melder_1 with the INTENT-docstring FYI); the
  rebuild last.
- Owners: conduit.py is held by this task until it lands; spellbook.py and transfer_of_ownership.py are melder_1's.
- Limits: the whole tree was not run; the suites run are listed in the 13:28:26Z and 15:23:08Z notes; the build
  assets and LLM bundles are stale until the rebuild; "version id" text in other lanes' release-note sections is
  left as it is.

"""
t = t[:start] + summary + t[end:]
t = t.replace("- Updated: 2026-10-16T15:23:08Z\n", "- Updated: " + now + "\n", 1)
ticket.write_text(t, encoding="utf-8")
print("ok")

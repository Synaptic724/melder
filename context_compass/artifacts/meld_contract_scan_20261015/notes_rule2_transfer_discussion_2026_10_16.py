"""Record the owner's acceptance and his two discussion questions, the removal defect's leftovers, how an ownership
transfer meets contracts today, and rule 2's own gap on the transfer path; hold the closure (melder_1, 2026-10-16).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"
TOO = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"
WARD = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
SSS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner accepted the rule 2 landing (chat 2026-10-16, "Accept (Recommended)"). On the remove_index_from_
    contract defect he first answered "no lets fix it if you want to melder_0 is done", then, after the explanation,
    opened a discussion instead: after a notch, should the unlink not remove the borrower's inactive copy rather than
    the current one, and how do ownership transfers and contracts affect each other ("thats also an important
    question"). The closure waits for that discussion, because the transfer reading below found a gap in rule 2's own
    coverage. A batch of his earlier messages (D1-D5, "btw you can start", the mailbox switch) was delivered again
    in this exchange; all of them were acted on before and need nothing new.
  EVIDENCE: {ART}/runs/release_example_rule2_2026_10_16.txt:1-14
  IMPACT: Rule 2 is accepted; its closure and rebuild follow the owner's call on the transfer gap.
  NEXT: Put the findings below to the owner and take his direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What a failed unlink leaves (the defect of the FACT above, probed under PYTHONHASHSEED 3 and 0 on 0.2.8250):
    with English parked and French active, the failing order removes French's active copy under English's id, then
    raises for French; the contract no longer links the index, but the borrower Book still tracks it and still holds
    English parked. A second `remove_index_from_contract` returns normally and drops the tracking, yet English stays
    parked for good: the per-version loop runs only while the contract still lists the index. Seed 0 (French first)
    removes both copies cleanly.
  EVIDENCE:
  - {WARD}:2221-2272
  - {ART}/probe_index_uncontract_retry.py:1-73
  - {ART}/runs/probe_index_uncontract_retry_gil0.txt:1-16
  IMPACT: A retry hides the failure and keeps the orphan, so the fix belongs in the removal itself: each version
    removes its own copy (the active slot only when that copy is the version, else the parked map).
  NEXT: Discuss with the owner which copy a removal takes after a notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How an ownership transfer meets contracts today (code read whole; probe on 0.2.8250, GIL off; the transfer
    code predates rule 2). Borrowers of the moved spell: (1) a version grant under the default `force_unshare=True`
    is removed, and the consumer's next meld names the lost contract - as documented; (2) an index link under the
    default is NOT removed: `_unshare_everywhere` removes borrower details one spell at a time, the ward refuses that
    for an index-link member ("cannot be removed on its own. Use remove_index_from_contract") and the transfer
    swallows the refusal, so the borrower keeps its index link and copy from the OLD owner and its consumer keeps
    building the provider; (3) `force_unshare=False` never repoints a grant or a link: `_repoint_borrowers` calls
    `_add_spell_to_contract` on the new owner's ward with the borrower as `conduit`, the roles reversed, so the
    ownership check refuses every time ("is not owned by this conduit, cannot contract it"), the refusal is
    swallowed, and the borrower stays on the old owner's contract while the new owner gains an empty link. The new
    owner: (4) it can meld the moved spell but cannot stage a version on its index - the flip adds the id to the new
    Book's `_spells_by_id` and pool but not its owned-id set `_spell_ids`, which `_apply_add_to_index` checks
    ("target index ... is not owned by this spellbook"), and the source drops it from its own, so neither Book lists
    it. The moved spell as a consumer: (5) its contracts stay with its old conduit pair; on the new owner its first
    meld names the missing contract (stewardship, not a working setup), and preflight's dependency check cannot see
    it, because a SpellContract is a key, not a dependency edge. From the code only: a target that borrowed the
    spell from the source loses that borrowed copy before the flip (`_unshare_target_conduit_contract`).
  EVIDENCE:
  - {TOO}:367-509
  - {TOO}:567-624
  - {TOO}:1004-1052
  - {TOO}:1383-1507
  - {TOO}:1808-1905
  - {TOO}:1907-1978
  - {WARD}:1779-1842
  - {WARD}:1844-1952
  - {WARD}:3189-3240
  - src/melder/aether/spellbook/spellbook.py:1251-1300
  - src/melder/aether/spellbook/spellbook.py:4089-4155
  - src/melder/aether/conduit/conduit.py:4264-4340
  - {ART}/probe_transfer_and_contracts.py:1-163
  - {ART}/runs/probe_transfer_and_contracts_gil0.txt:1-71
  - {ART}/probe_transfer_unshare_refusal.py:1-44
  - {ART}/runs/probe_transfer_unshare_refusal_gil0.txt:1-7
  - {ART}/probe_transfer_repoint_refusal.py:1-42
  - {ART}/runs/probe_transfer_repoint_refusal_gil0.txt:1-3
  IMPACT: A transfer silently leaves index-link borrowers on an owner that no longer owns the spell, the repoint
    option does nothing, and the receiving agent cannot continue the stage -> notch loop on the object it received;
    each is pre-existing and outside rule 2's approved patch except the gap in the next Note.
  NEXT: Put the transfer findings and the design question (what borrowers should get after a transfer) to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: A gap in rule 2's own coverage, missed in its build: the transfer flip calls `unregister_index` (which drops
    the lineage's binding key) and then `register_index` without `binding_key=`, so after a transfer the registry
    holds no key for the moved lineage (probe: "registry binding key=None"). The downstream walk finds a lineage's
    SpellContract consumers only through that key, so until the moved lineage is notched or bound again, a notch of
    something it depends on does not mark its borrowers' consumers. src_architecture's rule-2 invariant says
    `register_index(binding_key=...)` records one key per lineage; after a transfer it does not. The five Book
    mutators still mark by the copy's own key, so direct provider changes are covered. Fix: pass
    `binding_key=spell_obj._key` in the flip's `register_index` and in its rollback.
  EVIDENCE:
  - {TOO}:1383-1507
  - {SSS}:470-482
  - {SSS}:973-1036
  - {SSS}:1147-1222
  - {ART}/runs/probe_transfer_and_contracts_gil0.txt:1-71
  IMPACT: The accepted change set misses one path its invariant claims; the owner decides whether the fix joins rule
    2 before its closure or the transfer follow-up.
  NEXT: Ask the owner, with the transfer findings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

OLD_NEXT_START = "Next: rule 2 with D3 is applied to the real tree"
OLD_NEXT_END = "\n\n## Project-Specific Additions"
NEW_NEXT = """Next: rule 2 with D3 is applied to the real tree - 18 files, byte-identical to the fresh tree that passed every
suite chunk with the GIL off and on; the race test is xfail naming
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (the owner's decision B). The four system docs
and their indexes (rubric 83 / 83 / 83 / 77, band B) and the graph (seven nodes re-authored and accepted,
reassembled) carry it, the patch docs are archived, `__version__` is 0.2.8250 (NOTICE M1-21 sent) and the release
note carries its entry with both examples verified. The owner accepted the landing; the closure is held for his
discussion of two questions (Notes, {hhmm}): which copy an unlink removes after a notch, and how ownership transfers
and contracts affect each other - including rule 2's gap on the transfer path (the binding key). Remaining: (1) his
direction on the gap and on the transfer and removal findings; (2) closure and board sync; (3) the rebuild last."""

ROW_PREFIX = "| meld_contract_scan | in_progress | implementation | claude | melder_1 | none | "
ROW_NEXT = ("Owner discussion: which copy an unlink removes after a notch, transfers vs contracts and rule 2's "
            "binding-key gap on transfer; then closure, rebuild last.")


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


text = read(TICKET)
assert "How an ownership transfer meets contracts today" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
i = text.index(OLD_NEXT_START)
j = text.index(OLD_NEXT_END, i)
assert text.count(OLD_NEXT_START) == 1
text = text[:i] + NEW_NEXT.replace("{hhmm}", NOW[11:16] + "Z") + text[j:]
check_lengths(text, TICKET)

board = read(BOARD)
rows = [l for l in board.split("\n") if l.startswith(ROW_PREFIX)]
assert len(rows) == 1, rows
cells = rows[0].split(" | ")
assert cells[9] == "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md", cells[9]
cells[6] = ROW_NEXT
cells[10] = NOW
board = board.replace(rows[0], " | ".join(cells), 1)

print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
print(("CHECK " if CHECK else "WRITE ") + str(BOARD))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))

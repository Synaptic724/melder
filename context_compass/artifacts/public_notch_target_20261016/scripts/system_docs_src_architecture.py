"""Promote patch lane public_notch_target_2026_10_16 into src_architecture (0.2.8249).

Run from the context_compass root:  python <this file> <NOW>
Exact, asserted replacements on an LF file; prints new lines over 120 characters that are not unbreakable paths.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("system_docs/src_architecture.md")

EDITS = [
    (  # System Boundary and External Interfaces: the notch target and the remeasured verb citations
        "  opposite correctly. The code settles it.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit.py:5622, 5694 (`notch_spell`; starts the transaction)\n"
        "  - src/melder/aether/conduit/conduit.py:5712, 5767 (`add_to_spell_index`; starts it)\n"
        "  - src/melder/aether/conduit/conduit.py:5790, 5838 (`remove_from_spell_index`; starts it)\n",
        "  opposite correctly. The code settles it. `notch_spell`'s docstring has said so since 0.2.8249; the add and\n"
        "  remove docstrings still carry the old wording.\n"
        "  `notch_spell` names the version to make active by `spell_id=` - the id `bind` or `bind_inactive` returned - or by\n"
        "  `spell=`, exactly one, and resolves an id inside the call to the exact version the conduit's Spellbook owns,\n"
        "  active or parked (0.2.8249). Before the transaction and again inside the held window it refuses a version that\n"
        "  Spellbook does not own or one of another index (ValueError); a non-str id or a str given as `spell` is a\n"
        "  TypeError. `get_spell_by_id` and `find_spell_by_id` still answer a parked id with the index's active member, so a\n"
        "  parked version is named by its id.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit.py:5622, 5731 (`notch_spell`; starts the transaction)\n"
        "  - src/melder/aether/conduit/conduit.py:5753-5859 (`_resolve_notch_target`, `_owned_notch_target`)\n"
        "  - src/melder/aether/conduit/conduit.py:5861, 5916 (`add_to_spell_index`; starts it)\n"
        "  - src/melder/aether/conduit/conduit.py:5939, 5987 (`remove_from_spell_index`; starts it)\n",
    ),
    (  # Architecture Summary
        "fan-out).\n"
        "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3826-4262 (the three seams, remeasured 2026-10-16);\n"
        "`src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._deactivate_borrowed_spell` and\n",
        "fan-out). A notch names its target by version id or by Spell and checks that it is the Book's version of that\n"
        "index before anything moves (0.2.8249).\n"
        "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3826-4262 (the three seams, remeasured 2026-10-16);\n"
        "`src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._owned_notch_target` (the target check),\n"
        "`Conduit._deactivate_borrowed_spell` and\n",
    ),
    (  # Sequence: SpellIndex Mutation Entry, steps 1-4
        "1. Caller targets one live SpellIndex member through `Conduit.notch_spell(...)`,\n"
        "   `Conduit.add_to_spell_index(...)`, or `Conduit.remove_from_spell_index(...)`.\n"
        "   The entry point is the Conduit; it delegates to its owning Spellbook.\n"
        "2. Spellbook derives the binding key plus source/target SpellIndex metadata\n"
        "   and starts the corresponding transaction family:\n"
        "   `notch`, `add_to_index`, or `remove_from_index`.\n"
        "3. The resolved transaction strategy seals the owning spellbook/conduit\n"
        "   surfaces and the targeted binding key for the duration of the mutation.\n"
        "4. Inside the held transaction window the Conduit calls the Spellbook's\n",
        "1. Caller targets one live SpellIndex member through `Conduit.notch_spell(...)`,\n"
        "   `Conduit.add_to_spell_index(...)`, or `Conduit.remove_from_spell_index(...)`.\n"
        "   The entry point is the Conduit. A notch names its target by `spell_id=` (the id\n"
        "   `bind` or `bind_inactive` returned) or by `spell=`, exactly one:\n"
        "   `_resolve_notch_target` checks the arguments and `_owned_notch_target` resolves the\n"
        "   id through the Spellbook's `_get_owned_spell` - the exact owned version, active or\n"
        "   parked - and refuses a version the Spellbook does not own or one of another index\n"
        "   before anything starts (0.2.8249).\n"
        "2. The Conduit derives the binding key plus source/target SpellIndex metadata\n"
        "   and starts the corresponding transaction family through the frame's DevOps\n"
        "   mediator: `notch`, `add_to_index`, or `remove_from_index` (corrected\n"
        "   2026-10-16: this step said the Spellbook starts it; the Conduit does - see\n"
        "   System Boundary and External Interfaces).\n"
        "3. The resolved transaction strategy seals the owning spellbook/conduit\n"
        "   surfaces and the targeted binding key for the duration of the mutation. The\n"
        "   notch claims the Spellbook, the acting conduit and the conduits linked to it\n"
        "   EXCLUSIVE and freezes their creation gates until it ends.\n"
        "4. Inside the held transaction window a notch checks its target again\n"
        "   (`_owned_notch_target`; a refusal ends the transaction as failed before the\n"
        "   Spellbook is called), then the Conduit calls the Spellbook's\n",
    ),
    (  # Sequence: SpellIndex Mutation Entry, evidence
        "   - src/melder/aether/conduit/conduit.py:5622-5710\n"
        "   - src/melder/aether/conduit/conduit.py:5907-5936\n",
        "   - src/melder/aether/conduit/conduit.py:5622-5751\n"
        "   - src/melder/aether/conduit/conduit.py:5753-5859\n"
        "   - src/melder/aether/conduit/conduit.py:6056-6085\n"
        "   - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/"
        "notch_transaction_strategy.py:239-269\n",
    ),
    (  # Operational Invariants: the new invariant first
        "## Operational Invariants\n"
        "- Parked versions are wired at conjure (2026-10-16, 0.2.8248):",
        "## Operational Invariants\n"
        "- The notch names its target and checks it (2026-10-16, 0.2.8249): `Conduit.notch_spell(*, spell_index, spell=None,\n"
        "  spell_id=None, change_reason=...)` takes exactly one of `spell_id` and `spell`. `_resolve_notch_target` refuses\n"
        "  both or neither (ValueError) and a non-str id or a str given as `spell` (TypeError); `_owned_notch_target`\n"
        "  resolves the id through `Spellbook._get_owned_spell` - a read of `_spells_by_id`, then of `_inactive_spells`, under\n"
        "  the Book lock alone, released before it returns - and refuses a version that call does not return, a `spell` that\n"
        "  is not the object it returns (a disposed, rebound or another Book's version; a cleaned Spell keeps its id, so it is\n"
        "  refused before its deleted `spell_index` is read), and a version whose `spell_index` is not the index passed.\n"
        "  `notch_spell` runs the checks before `start_transaction`, so a refusal starts nothing (no seal, no gate freeze),\n"
        "  and again first inside the held window, where the notch strategy holds the Book, the acting conduit and the\n"
        "  conduits linked to it EXCLUSIVE: no bind, transfer or other index operation on the Book is admitted between that\n"
        "  check and the switch, and a refusal there ends the transaction as failed (its `on_end` reopens the frozen gates)\n"
        "  before `Spellbook._notch_spell` runs. The resolved Spell is rebound to `spell`, so the transaction metadata, the\n"
        "  seam and the fan-out read one object and a valid call behaves as before; a notch to the active version stays a\n"
        "  no-op. The checks exist because the seam cannot be handed a foreign target: `_apply_notch` parks the outgoing\n"
        "  version before `_reactivate_owned_spell` checks the incoming one, and files it under its own `spell_index`.\n"
        "  `Conduit.cleanup_spell` is not admitted through a transaction, so a disposal of the target between the in-window\n"
        "  check and the seam's Book lock still meets that park-first order (pre-existing; filed for the seam). No lock or\n"
        "  lock-order edge is added: `_get_owned_spell` takes the Book lock alone and the identity reads take none.\n"
        "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,\n"
        "  `Conduit._owned_notch_target`, `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`,\n"
        "  `Spellbook._apply_notch`, `Spellbook._reactivate_owned_spell` and\n"
        "  `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/"
        "notch_transaction_strategy.py:NotchTransactionStrategy._seal_scope_keys`.\n"
        "- Parked versions are wired at conjure (2026-10-16, 0.2.8248):",
    ),
    (  # Failure Modes and Error Paths: three new entries first
        "## Failure Modes and Error Paths\n"
        "- A Book holding a definition bound resolvable=False",
        "## Failure Modes and Error Paths\n"
        "- `Conduit.notch_spell` refuses its target before anything moves (0.2.8249): ValueError \"notch_spell accepts either\n"
        "  `spell` or `spell_id`, not both.\" and \"notch_spell needs the version to make active: pass spell_id=<the id bind or\n"
        "  bind_inactive returned>, or spell=<its Spell object>.\"; TypeError \"notch_spell `spell_id` must be a string; got\n"
        "  <type>.\" and, for a str given as `spell`, one that names `spell_id=`; ValueError \"notch_spell: version '<id>' is\n"
        "  not owned by this conduit's Spellbook. ...\" (remedy: notch through the conduit of the Spellbook that owns it, or\n"
        "  stage the class on this index with bind_inactive) and \"notch_spell: version '<id>' belongs to another SpellIndex,\n"
        "  not the one passed. ...\" (remedy: pass `conduit.get_spell_by_id('<id>').spell_index`, or move the version with\n"
        "  add_to_spell_index first). A refusal before the transaction changes nothing; one inside the window (another\n"
        "  operation moved the target after the first check) ends the transaction as failed, and the Spellbook is never\n"
        "  called.\n"
        "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._resolve_notch_target` and `Conduit._owned_notch_target`.\n"
        "- A notch to a version of another index, or to another Spellbook's version, no longer damages the index (fixed in\n"
        "  0.2.8249). Through 0.2.8248 nothing checked the target: a version parked in another index of the same Book was\n"
        "  accepted and corrupted both indexes - this one selected it with no active entry (a meld of its former version\n"
        "  raised KeyError), the other kept selecting its old version while its active entry was the moved one, and a meld\n"
        "  of the moved version raised RuntimeError \"Cannot build CreationContext before spell_codegen_creation exists.\";\n"
        "  the active version of another index, or another Book's version, raised RuntimeError \"Owned spell_id not parked\n"
        "  for reactivation\" after this index's active version had been parked, leaving the index with no active version\n"
        "  until a notch back. Each now raises the ValueError above with both indexes as they were.\n"
        "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._owned_notch_target`,\n"
        "  `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_notch` and `Spellbook._reactivate_owned_spell`.\n"
        "- A notch to the Spell `get_spell_by_id` or `find_spell_by_id` returns for a parked id is a silent no-op, by their\n"
        "  contract: they answer a parked id with the index's active member. Name a parked version by `spell_id=`.\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`.\n"
        "- A Book holding a definition bound resolvable=False",
    ),
    (  # C1 Code Map: conduit.py remeasured
        "- path: `src/melder/aether/conduit/conduit.py`\n"
        "  start_line: 1\n"
        "  end_line: 7463\n"
        "  loc: 7463\n"
        "  verified_at: 2026-10-15T21:20:35Z\n",
        "- path: `src/melder/aether/conduit/conduit.py`\n"
        "  start_line: 1\n"
        "  end_line: 7612\n"
        "  loc: 7612\n"
        f"  verified_at: {NOW}\n",
    ),
    (
        "    (0.2.8240); `managed_spell_meld` (0.2.8245) and the managed options on its bind facades (0.2.8242).\n",
        "    (0.2.8240); `managed_spell_meld` (0.2.8245) and the managed options on its bind facades (0.2.8242);\n"
        "    `notch_spell` names its target by `spell_id=` or `spell=` and checks it before and inside its transaction\n"
        "    (0.2.8249).\n",
    ),
    (  # Context / Handoff Summary: the new entry first
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): conjure stamps",
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 public notch target (0.2.8249): `Conduit.notch_spell` takes `spell_id=` - the id `bind` or `bind_inactive`\n"
        "returned - beside `spell=`, exactly one, and resolves it inside the call to the exact version the Book owns, active\n"
        "or parked (owner ruling, option A: \"just use the private version if its inside the public call thats\n"
        "reasonable\"), so the stage -> notch -> meld loop runs on public calls. Both forms are checked - owned by the\n"
        "conduit's Book, a member of the index passed - before the transaction and again under its seal, which closes\n"
        "three ways a notch used to damage a Book. The boundary list (its conduit.py citations remeasured), the summary,\n"
        "the SpellIndex Mutation Entry sequence (whose steps 1-2 said the Spellbook starts the transaction; the Conduit\n"
        "does), a new operational invariant, three failure modes and the code map carry it; the component map carries the\n"
        "per-component contract. Open for the owner: whether `add_to_spell_index` and `remove_from_spell_index` take the\n"
        "same keyword.\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): conjure stamps",
    ),
]


def main() -> None:
    """Apply every edit once, in order, and report over-long new lines."""
    text = DOC.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("expected LF")
    for old, new in EDITS:
        found = text.count(old)
        if found != 1:
            raise SystemExit(f"{found} occurrences of {old[:90]!r}")
        text = text.replace(old, new, 1)
    DOC.write_bytes(text.encode("utf-8"))
    for _old, new in EDITS:
        for line in new.splitlines():
            if len(line) > 120 and "src/melder/" not in line:
                print("LONG", len(line), line[:70])
    print(f"{DOC}: {len(EDITS)} edits; {text.count(chr(10))} lines")


if __name__ == "__main__":
    main()

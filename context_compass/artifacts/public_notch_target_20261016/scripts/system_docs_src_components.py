"""Promote patch lane public_notch_target_2026_10_16 into src_components (0.2.8249).

Run from the context_compass root:  python <this file> <NOW>
Exact, asserted replacements on an LF file; prints new lines over 120 characters that are not unbreakable paths.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("system_docs/src_components.md")

NOTCH_PARAGRAPH = (
    "Notch target (2026-10-16, 0.2.8249): `notch_spell(*, spell_index, spell=None, spell_id=None, change_reason=...)`\n"
    "names the version to make active by `spell_id` - the id `bind` or `bind_inactive` returned - or by its Spell,\n"
    "exactly one. `_resolve_notch_target` refuses both or neither (ValueError) and a non-str id or a str given as `spell`\n"
    "(TypeError), then hands the id to `_owned_notch_target`, which resolves it through the Book's `_get_owned_spell` (the\n"
    "exact owned version, active or parked; the Book lock alone) and refuses, with a ValueError naming the version and\n"
    "the remedy, a version the Book does not own, a `spell` that is not the object the Book owns under that id, and a\n"
    "version whose `spell_index` is not the index passed. `notch_spell` runs both before `start_transaction` (a refusal\n"
    "starts nothing) and `_owned_notch_target` again first inside the held window, where the notch seal (the Book, the\n"
    "acting conduit and the conduits linked to it EXCLUSIVE) keeps every other index operation out; a refusal there\n"
    "ends the transaction as failed and `Spellbook._notch_spell` is never called. The resolved Spell is rebound to\n"
    "`spell`, so the metadata, the seam call and the fan-out are as before for every valid call, and a notch to the\n"
    "active version stays a no-op. The docstring now says the conduit admits the transaction (it said the Spellbook\n"
    "did). `get_spell_by_id` keeps answering a parked id with the index's active member.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,\n"
    "`Conduit._owned_notch_target` and `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`.\n"
)

NOTCH_FLOW = (
    "### Flow: Conduit.notch_spell -> Target Check -> Spellbook._apply_notch\n"
    "1. `Conduit.notch_spell(spell_index=..., spell_id=...)` (or `spell=`): `check_cleaned`, the dynamic gate\n"
    "   (RuntimeError), the owning-Book check (RuntimeError).\n"
    "2. `Conduit._resolve_notch_target`: exactly one of `spell` and `spell_id` (ValueError), a str id and no str `spell`\n"
    "   (TypeError); then `Conduit._owned_notch_target` -> `Spellbook._get_owned_spell(spell_id)` (Book lock) -> the\n"
    "   owned version, and the given object when one was given, else ValueError; `owned.spell_index is spell_index`,\n"
    "   else ValueError. The resolved Spell is rebound to `spell` (0.2.8249).\n"
    "3. Metadata from that Spell; `outgoing_id = spell_index.selected_spell_id`; `start_transaction(NOTCH)`: the plan\n"
    "   claims the Book, the acting conduit, the conduits linked to it and the binding key EXCLUSIVE\n"
    "   (`NotchTransactionStrategy.build_start_plan`), and `on_start` freezes their creation gates.\n"
    "4. Inside the window: `Conduit._owned_notch_target` again, then `Spellbook._notch_spell` ->\n"
    "   `Spellbook._apply_notch` (park the outgoing version, `_reactivate_owned_spell` the incoming one, repoint the\n"
    "   index and the framewide lookup, re-register the index gated). Any raise -> `end_transaction(success=False)`\n"
    "   (`on_end` reopens the gates) and the raise propagates.\n"
    "5. `end_transaction(success=True)`; when the version changed, `Conduit._deactivate_borrowed_spell(outgoing_id)` and\n"
    "   `ConduitWard._emit_index_notch(spell_index, outgoing_id, spell.spell_id)`; returns the now-active Spell.\n"
    "\n"
)

EDITS = [
    (  # Spellbook Core: the mediator acquisitions remeasured
        "  - src/melder/aether/conduit/conduit.py:5671, 5747, 5827 (notch/add/remove\n",
        "  - src/melder/aether/conduit/conduit.py:5708, 5896, 5976 (notch/add/remove\n",
    ),
    (  # Conduit Runtime: the dated paragraph first
        "### Component: Conduit Runtime (Normal and Lesser)\n"
        "Purpose:\n"
        "- Execution scope for resolving spells and managing object lifecycles.\n"
        "\n",
        "### Component: Conduit Runtime (Normal and Lesser)\n"
        "Purpose:\n"
        "- Execution scope for resolving spells and managing object lifecycles.\n"
        "\n" + NOTCH_PARAGRAPH + "\n",
    ),
    (  # Conduit Runtime: responsibilities
        "- Transfer spell ownership between conduits in dynamic mode.\n"
        "- Gate meld execution per conduit via `CreationGate` and register gates in the\n",
        "- Transfer spell ownership between conduits in dynamic mode.\n"
        "- Admit the SpellIndex mutations (`notch_spell`, `add_to_spell_index`, `remove_from_spell_index`) as\n"
        "  change-control transactions; a notch resolves and checks its target by version id (0.2.8249; Subcomponent:\n"
        "  SpellIndex Mutation Surface).\n"
        "- Gate meld execution per conduit via `CreationGate` and register gates in the\n",
    ),
    (  # Conduit Runtime: inputs
        "- Target conduit and transfer options for `transfer_spell_ownership(...)`.\n"
        "\n"
        "Outputs:\n",
        "- Target conduit and transfer options for `transfer_spell_ownership(...)`.\n"
        "- A SpellIndex and the version to make active - its id or its Spell - for `notch_spell(...)` (0.2.8249).\n"
        "\n"
        "Outputs:\n",
    ),
    (  # Conduit Runtime: outputs
        "- The Spellbook it resolves through, borrowed, from `spellbook` (0.2.8208).\n"
        "\n"
        "Owned State:\n",
        "- The Spellbook it resolves through, borrowed, from `spellbook` (0.2.8208).\n"
        "- The now-active Spell from `notch_spell(...)`.\n"
        "\n"
        "Owned State:\n",
    ),
    (  # Conduit Runtime: the link TypeError citation, stale since earlier lanes
        "  EVIDENCE: src/melder/aether/conduit/conduit.py:5296-5298.\n",
        "  EVIDENCE: src/melder/aether/conduit/conduit.py:5571-5573.\n",
    ),
    (  # Conduit Runtime: failure modes
        "- RuntimeError if `transfer_spell_ownership` is called in non-dynamic mode.\n"
        "- Meld calls block while the local `CreationGate` is disabled.\n",
        "- RuntimeError if `transfer_spell_ownership` is called in non-dynamic mode.\n"
        "- ValueError or TypeError from `notch_spell` for its target (0.2.8249): both or neither of `spell` and `spell_id`,\n"
        "  a version the Book does not own and a version of another index are ValueErrors naming the version and the\n"
        "  remedy; a non-str id and a str given as `spell` are TypeErrors. A refusal before the transaction starts\n"
        "  nothing; one inside it ends the transaction as failed. Through 0.2.8248 a version of another index or Book was\n"
        "  accepted, corrupting the indexes or leaving the index with no active version (`src_architecture`, Failure\n"
        "  Modes and Error Paths).\n"
        "- Meld calls block while the local `CreationGate` is disabled.\n",
    ),
    (  # SpellIndex Mutation Surface: the three verbs, remeasured
        "- `Conduit.notch_spell(...)` opens the `notch` transaction at\n"
        "  `src/melder/aether/conduit/conduit.py:5419`, then calls `Spellbook._notch_spell(...)`, which delegates\n"
        "  the member-store switch to the seam `_apply_notch(...)`.\n"
        "- `Conduit.add_to_spell_index(spell=, target_index=)` opens `add_to_index` at\n"
        "  `src/melder/aether/conduit/conduit.py:5492`, then calls `Spellbook._add_to_spell_index(...)`, which\n"
        "  delegates the move-in to `_apply_add_to_index(...)`.\n"
        "- `Conduit.remove_from_spell_index(spell=, source_index=)` opens\n"
        "  `remove_from_index` at `src/melder/aether/conduit/conduit.py:5563`, then calls\n",
        "- `Conduit.notch_spell(spell_index=, spell_id= | spell=)` resolves and checks its target\n"
        "  (`_resolve_notch_target`, `_owned_notch_target`: owned by the Book, a member of the index passed; 0.2.8249),\n"
        "  opens the `notch` transaction at `src/melder/aether/conduit/conduit.py:5731`, checks the target again inside\n"
        "  the window, then calls `Spellbook._notch_spell(...)`, which delegates the member-store switch to the seam\n"
        "  `_apply_notch(...)`.\n"
        "- `Conduit.add_to_spell_index(spell=, target_index=)` opens `add_to_index` at\n"
        "  `src/melder/aether/conduit/conduit.py:5916`, then calls `Spellbook._add_to_spell_index(...)`, which\n"
        "  delegates the move-in to `_apply_add_to_index(...)`.\n"
        "- `Conduit.remove_from_spell_index(spell=, source_index=)` opens\n"
        "  `remove_from_index` at `src/melder/aether/conduit/conduit.py:5987`, then calls\n",
    ),
    (  # SpellIndex Mutation Surface: the docstring warning and its evidence
        "  DO NOT TRUST THE CONDUIT DOCSTRINGS HERE. All three say \"Delegates to the\n"
        "  owning Spellbook, WHICH ADMITS the [...] change-control transaction\". That is\n"
        "  false in all three, and the same three methods call\n"
        "  `mediator.start_transaction(...)` a few lines further down. `src/melder/aether/spellbook/spellbook.py:3811-3813`\n"
        "  states it correctly. Raised on TASK-2026-08-02-stale-source-docstrings.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit.py:5622, 5712, 5790 (public verbs)\n",
        "  DO NOT TRUST THE ADD AND REMOVE DOCSTRINGS HERE. Both say \"Delegates to the\n"
        "  owning Spellbook, WHICH ADMITS the [...] change-control transaction\". That is\n"
        "  false, and both methods call `mediator.start_transaction(...)` a few lines\n"
        "  further down. `src/melder/aether/spellbook/spellbook.py:3811-3813` states it correctly.\n"
        "  `notch_spell`'s docstring said the same until 0.2.8249 and now says the conduit\n"
        "  admits the transaction. Raised on TASK-2026-08-02-stale-source-docstrings.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit.py:5622, 5861, 5939 (public verbs)\n"
        "  - src/melder/aether/conduit/conduit.py:5753, 5806 (`_resolve_notch_target`, `_owned_notch_target`)\n",
    ),
    (  # SpellIndex Mutation Surface: behavior, the corrected seal, key files
        "  pin them), which is how several agents iterate on one object and converge on a version.\n"
        "Concurrency/Threading:\n"
        "- Public entrypoints use the Spellbook lock and the transaction mediator; the\n"
        "  seams then run INSIDE the held transaction window (owning spellbook INTENT +\n"
        "  binding key EXCLUSIVE for notch; source and target surfaces EXCLUSIVE for the\n"
        "  membership moves), which is what makes the choreography race-safe.\n"
        "Key Files (C1):\n"
        "- `src/melder/aether/spellbook/spellbook.py`\n",
        "  pin them), which is how several agents iterate on one object and converge on a version.\n"
        "- A notch's target (0.2.8249): exactly one of `spell_id` and `spell`; the id resolves through\n"
        "  `Spellbook._get_owned_spell` to the exact owned version, active or parked. A version the Book does not own, a\n"
        "  `spell` that is not the object it owns under that id, and a version of another index are refused (ValueError)\n"
        "  before the transaction - nothing is sealed or frozen - and again inside the window, where a refusal ends the\n"
        "  transaction as failed before `_notch_spell` runs. `_apply_notch` itself parks the outgoing version before it\n"
        "  checks the incoming one, so it must only ever be handed a parked member of the index it is notching.\n"
        "Concurrency/Threading:\n"
        "- Public entrypoints use the Spellbook lock and the transaction mediator; the\n"
        "  seams then run INSIDE the held transaction window (the owning spellbook, the\n"
        "  acting conduit, the conduits linked to it and the binding key EXCLUSIVE for\n"
        "  notch, their creation gates frozen; source and target surfaces EXCLUSIVE for\n"
        "  the membership moves), which is what makes the choreography race-safe.\n"
        "  Corrected 2026-10-16: this said spellbook INTENT for notch, as the seam\n"
        "  docstrings in spellbook.py still do; `NotchTransactionStrategy._seal_scope_keys`\n"
        "  claims the Book EXCLUSIVE. That seal is why a notch checks its target again\n"
        "  inside the window: no other index operation on the Book is admitted until the\n"
        "  notch ends.\n"
        "Key Files (C1):\n"
        "- `src/melder/aether/conduit/conduit.py`\n"
        "- `src/melder/aether/spellbook/spellbook.py`\n",
    ),
    (  # Method-Level Call Flows: the notch flow before the SpellSpace flow
        "### Flow: SpellSpace Scoped Meld\n",
        NOTCH_FLOW + "### Flow: SpellSpace Scoped Meld\n",
    ),
    (  # C1 Code Map: conduit.py remeasured
        "- path: `src/melder/aether/conduit/conduit.py`\n"
        "  start_line: 1\n"
        "  end_line: 7463\n"
        "  loc: 7463\n"
        "  verified_at: 2026-10-15T21:40:35Z\n",
        "- path: `src/melder/aether/conduit/conduit.py`\n"
        "  start_line: 1\n"
        "  end_line: 7612\n"
        "  loc: 7612\n"
        f"  verified_at: {NOW}\n",
    ),
    (  # Context / Handoff Summary: the new entry first
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): Spellbook Core carries",
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 public notch target (0.2.8249): Conduit Runtime carries `notch_spell`'s `spell_id=` and its target check\n"
        "(the two helpers, the refusals, both check points, the docstring that now says the conduit admits the\n"
        "transaction); the SpellIndex Mutation Surface carries the same at the C2 level, with its three verb citations\n"
        "remeasured (its Contract/Interface lines had pointed at 5419, 5492 and 5563 since earlier lanes), the notch seal\n"
        "corrected from spellbook INTENT to EXCLUSIVE, and conduit.py among its Key Files; a new call flow follows a notch\n"
        "by id. Spellbook Core's mediator citations and the Conduit Runtime's `link` TypeError citation (5296-5298, stale\n"
        "since earlier lanes) point at their code again, and the code map remeasures conduit.py. The seam docstrings in\n"
        "spellbook.py (`_notch_spell`, `_apply_notch`) still say the notch claims the Book INTENT.\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): Spellbook Core carries",
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

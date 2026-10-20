"""Reopen patch lane public_notch_target_2026_10_16 for the owner's extension (2026-10-16): add_to_spell_index and
remove_from_spell_index take spell_id=, and the lane's text says spell_id, not "version id".

Run from the context_compass root:  python <this file> <NOW>
Exact, asserted replacements on LF files; writes the new index-move component patch (refuses an existing file).
"""
import pathlib
import sys

NOW = sys.argv[1]
LANE = pathlib.Path("system_docs/patches/active/public_notch_target_2026_10_16")
ARCH = LANE / "architecture_patch.md"
NOTCH = LANE / "component_patch_conduit_notch_target.md"
MOVES = LANE / "component_patch_conduit_index_move_target.md"

ARCH_EDITS = [
    ("- Status: landed 0.2.8249 (2026-10-16) as patched; promoted to src_architecture, src_components, tests_components,\n"
     "  tests_architecture and the graph; archived\n",
     "- Status: reopened 2026-10-16 for the owner's extension (`add_to_spell_index` / `remove_from_spell_index` take\n"
     "  `spell_id=`; the lane's text says spell_id); the notch part landed as patched and is promoted; the extension is\n"
     "  written before its `src/` edit\n"),
    ("- Updated: 2026-10-16T14:20:33Z\n", "- Updated: " + NOW + "\n"),
    ("passed - before the transaction starts and once more inside the held window, for both forms.\n\n## Non-goals\n",
     "passed - before the transaction starts and once more inside the held window, for both forms.\n\n"
     "Extension (owner, 2026-10-16: \"yeah that makes sense sure\"). `add_to_spell_index` and `remove_from_spell_index`\n"
     "have the same gap: they take only a Spell object and move only a spell parked in the Book, and no public call\n"
     "returns a parked spell's Spell object. They take `spell_id=` beside `spell=` too, resolved the same way. The owner\n"
     "also ruled on the vocabulary: the identifier is the `spell_id` that `bind` and `bind_inactive` generate, so this\n"
     "lane's messages, docstrings, tests and docs say spell_id, not \"version id\".\n\n## Non-goals\n"),
    ("- `add_to_spell_index` and `remove_from_spell_index` keep their signatures unless the owner extends this scope (open\n"
     "  DECISION_REQUEST in the ticket); their seams already check ownership and membership before they mutate.\n",
     "- No new check for `add_to_spell_index` / `remove_from_spell_index` beyond resolving a `spell_id` to a spell the\n"
     "  Book owns: their seams keep refusing (RuntimeError) a spell another Book owns, an active spell and, for remove, a\n"
     "  spell outside the source index or its only member; for add, a target index the Book does not own. Their `spell=`\n"
     "  form passes through unchanged.\n"),
    ("| system docs, conduit.py's graph descriptor, release note | the boundary list, the SpellIndex mutation sequence, an invariant, failure modes, the code map; the Conduit component entries; the tests docs | melder_0 |\n",
     "| system docs, conduit.py's graph descriptor, release note | the boundary list, the SpellIndex mutation sequence, an invariant, failure modes, the code map; the Conduit component entries; the tests docs | melder_0 |\n"
     "| Conduit (`add_to_spell_index`, `remove_from_spell_index`; shared `_check_spell_argument`, new `_owned_spell_by_id`) | `spell_id: Optional[str] = None` beside `spell` (now defaulting to None); exactly one of the two; a `spell_id` resolved through `Spellbook._get_owned_spell`, an id the Book does not own refused before the transaction; the docstrings say the conduit admits the transaction and list the seams' refusals (extension) | melder_0 (this task) |\n"),
    ("5. No new lock and no new lock edge: `_get_owned_spell` takes the Book lock alone and releases it; the identity\n"
     "   checks read without a lock. Nothing on a meld path changes.\n",
     "5. No new lock and no new lock edge: `_get_owned_spell` takes the Book lock alone and releases it; the identity\n"
     "   checks read without a lock. Nothing on a meld path changes.\n"
     "6. `add_to_spell_index` and `remove_from_spell_index` take exactly one of `spell` and `spell_id`, with invariant\n"
     "   1's rules and texts worded for their verb (one shared argument check). A `spell_id` resolves through\n"
     "   `_get_owned_spell`; one the Book does not own is a ValueError before the transaction, so nothing is started.\n"
     "   The resolved spell is what the metadata, the seam and the index-link fan-out read; the seams' own refusals and\n"
     "   everything after resolution are unchanged, as is every call made with `spell=`.\n"
     "7. One word for the identifier: messages, docstrings, tests and docs of this lane say `spell_id`. The notch\n"
     "   refusals read \"spell_id '<id>' ...\" where they read \"version '<id>' ...\".\n"),
    ("- Internal: `Conduit._resolve_notch_target` (the argument checks) and `Conduit._owned_notch_target` (the\n"
     "  resolution and both target checks, in one place; planned as `_refuse_foreign_notch_target`).\n",
     "- Internal: `Conduit._resolve_notch_target` (the argument checks) and `Conduit._owned_notch_target` (the\n"
     "  resolution and both target checks, in one place; planned as `_refuse_foreign_notch_target`).\n"
     "- Extension: `Conduit.add_to_spell_index(*, spell=None, spell_id: Optional[str] = None, target_index)` and\n"
     "  `Conduit.remove_from_spell_index(*, spell=None, spell_id: Optional[str] = None, source_index)`; every argument\n"
     "  stays keyword-only. New refusals: ValueError (both, neither, a `spell_id` the Book does not own) and TypeError\n"
     "  (a non-str `spell_id`, a str `spell`). Internal: `Conduit._check_spell_argument` (the argument checks, shared\n"
     "  with `_resolve_notch_target`) and `Conduit._owned_spell_by_id`. The notch messages change wording only\n"
     "  (invariant 7).\n"),
    ("assembled -> release note -> notch -> closure -> rebuild last.\n",
     "assembled -> release note -> notch -> closure -> rebuild last.\n"
     "Extension, before the closure: this amendment and the index-move component patch -> the mapping note -> red\n"
     "tests (unit: the argument checks and the id resolution of both verbs against a stubbed Book, nothing started on a\n"
     "refusal; integration: add and remove by spell_id in a real dynamic world, the refusals with the indexes intact)\n"
     "-> the conduit.py change (the shared argument check, the two verbs, their docstrings, the notch wording) -> green\n"
     "with the GIL off and on, the index-move suites unchanged -> the spell_id wording in the lane's docs -> system docs,\n"
     "graph, release note -> archive -> closure -> rebuild last. The notch stays 0.2.8249: one landing.\n"),
    ("| 5 | review of the touched lines; the conduit, spellbook and crystallizer suites in both GIL modes |\n",
     "| 5 | review of the touched lines; the conduit, spellbook and crystallizer suites in both GIL modes |\n"
     "| 6 | unit: both, neither, a non-str spell_id and a str `spell` refused for each verb before the Book is asked and before any transaction; an unknown spell_id refused with nothing started; a spell_id resolved through `_get_owned_spell` reaches the metadata and the seam; `spell=` passed through; integration: add and remove by spell_id move a parked spell, an active spell_id is refused by the seam with the indexes intact, the existing index-move suites unchanged |\n"
     "| 7 | the notch unit and integration tests assert the reworded messages; a search of the lane's files for \"version id\" |\n"),
    ("- DECISION_REQUEST (ticket Notes): the same keyword for `add_to_spell_index` / `remove_from_spell_index`.\n",
     "- Resolved 2026-10-16: the owner extended the landing to `add_to_spell_index` / `remove_from_spell_index` (the\n"
     "  ticket's DECISION note) and asked for spell_id wording.\n"),
    ("- What remains: nothing in this lane. Backlog: the same id keyword for `add_to_spell_index` /\n"
     "  `remove_from_spell_index` (the owner's DECISION_REQUEST), and the seam's park-first ordering (Risks).\n"
     "- Next entrypoint: the canonical docs - src_architecture (Operational Invariants, \"The notch names its target and\n"
     "  checks it\") and src_components (Conduit Runtime; SpellIndex Mutation Surface).\n",
     "- Reopened for the extension (invariants 6-7; component_patch_conduit_index_move_target.md): nothing built for it\n"
     "  yet.\n"
     "- What remains: the extension's mapping, tests, code, wording, docs and release note; then the archive, the\n"
     "  closure and the rebuild. Backlog: the seam's park-first ordering (Risks).\n"
     "- Next entrypoint: component_patch_conduit_index_move_target.md, then the red tests.\n"),
]

MOVES_TEXT = """# Component patch: Conduit - add_to_spell_index and remove_from_spell_index by spell_id

## Metadata
- Patch ID: public_notch_target_2026_10_16
- Component: `Conduit.add_to_spell_index`, `Conduit.remove_from_spell_index` (src/melder/aether/conduit/conduit.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: <NOW>
- Status: written before the extension's `src/` edit (the owner's extension, 2026-10-16)

## Before (0.2.8248, and 0.2.8249 until this extension)
- `add_to_spell_index(self, *, spell: Any, target_index: Any)`: dynamic gate (RuntimeError on an automatic frame),
  owning-Book check (RuntimeError), metadata from `spell.spell_id` and `spell._key`, the source lineage read before
  admission (`spell.spell_index`, whether the move empties it, its members), `start_transaction(ADD_TO_INDEX)`,
  `Spellbook._add_to_spell_index` inside a `try` that ends the transaction as failed and re-raises,
  `end_transaction(success=True)`, then the index-link fan-out (member added on the target; member removed, or the
  index destroyed, on the source).
- `remove_from_spell_index(self, *, spell: Any, source_index: Any)`: the same gates, metadata,
  `start_transaction(REMOVE_FROM_INDEX)`, `Spellbook._remove_from_spell_index`, end, fan-out (member removed).
- Both take only a Spell object and move only a spell parked in the Book: the seams raise RuntimeError for a spell
  another Book owns, for an active spell ("notch away from it before moving it") and - remove - for a spell outside
  `source_index` or its only member ("use cleanup_spell"); add - for a target index the Book does not own. No public
  call returns a parked spell's Spell object (`get_spell_by_id` answers a parked spell_id with the index's active
  spell), so neither verb can be used from public code.
- Both docstrings say the Spellbook admits the transaction; the conduit does. The remove docstring says removing the
  active member leaves the index selecting a non-member; the seam refuses an active member.

## After
- Signatures: `add_to_spell_index(self, *, spell: Any = None, spell_id: Optional[str] = None, target_index: Any)` and
  `remove_from_spell_index(self, *, spell: Any = None, spell_id: Optional[str] = None, source_index: Any)`. After the
  dynamic gate and the Book check: `spell = self._resolve_spell_to_move(verb=..., spell=spell, spell_id=spell_id)`;
  everything after it is unchanged and reads the resolved spell.
- `_check_spell_argument(*, verb, spell, spell_id) -> str`, shared with `_resolve_notch_target`:
  - both given: ValueError "<verb> accepts either `spell` or `spell_id`, not both.";
  - neither: ValueError "<verb> needs a spell: pass spell_id=<the spell_id bind or bind_inactive returned>, or
    spell=<its Spell object>.";
  - a non-str `spell_id`: TypeError "<verb> `spell_id` must be a string; got <type>.";
  - a str `spell`: TypeError "<verb> `spell` takes a Spell object; to name a spell by its spell_id, pass
    spell_id='<id>'.";
  - returns the spell_id to resolve (`spell_id`, or `spell.spell_id`).
- `_owned_spell_by_id(*, verb, spell_id) -> Spell`: `self._spellbook._get_owned_spell(spell_id)`; None ->
  ValueError "<verb>: spell_id '<id>' is not owned by this conduit's Spellbook. Call <verb> through the conduit of the
  Spellbook that owns it."
- `_resolve_spell_to_move(*, verb, spell, spell_id) -> Spell`: the argument check, then `_owned_spell_by_id` for a
  `spell_id`; a `spell` is returned as given (the seams check it as before).
- Docstrings: the conduit admits the transaction; name the spell by `spell_id` (the spell_id `bind` or
  `bind_inactive` returned) or `spell`; every refusal, the seams' included; remove: only a parked member is split
  out - the active one is refused, so notch away first - and the only member is refused (`cleanup_spell` disposes it).

## Interface deltas
- `spell` gains a default (None); `spell_id: Optional[str] = None` is new; all arguments stay keyword-only, so every
  existing call keeps working.
- Raises: ValueError and TypeError as above (new, before any transaction); the seams' RuntimeErrors unchanged;
  RuntimeError unchanged for an automatic frame, a cleaned conduit and a conduit without a Book.
- Returns: unchanged (the seam's result, the moved Spell).

## State and failure deltas
- A refusal by the argument check or `_owned_spell_by_id` starts nothing (no metadata, no transaction, no fan-out).
- A spell_id that resolves to an active spell, or (remove) to a spell outside `source_index`, reaches the seam and
  is refused there as `spell=` is: the transaction ends as failed and nothing moves.

## Dependency and ordering
- `_get_owned_spell` takes the Book lock alone (cold path) and releases it before admission; no new lock edge.
- The index-move tests that pass a Spell object (index lifecycle and depth, index-link follow, notch lifecycle, op
  guards, the crystallizer membership integration, the find-by-id component test) run unchanged as regression.

## Validation expectations
- Unit (new file tests/unit/melder/aether/conduit/test_conduit_index_move_target.py, the stubbed Book of the conduit
  unit conftest): for each verb, both, neither, a non-str spell_id and a str `spell` are refused before the Book is
  asked and before any transaction; an unknown spell_id is refused after `_get_owned_spell` answers None, nothing
  started; a resolved spell_id reaches the transaction metadata and the Book's entry; `spell=` is passed through
  without asking `_get_owned_spell`.
- Integration (new file tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py): in a
  dynamic world, `add_to_spell_index(spell_id=..., target_index=...)` moves a parked spell onto another index and
  `remove_from_spell_index(spell_id=..., source_index=...)` splits a parked spell into a fresh index, each meldable
  after a notch to it; an unknown spell_id, both or neither are refused with the indexes intact; an active spell_id
  is refused by the seam with the indexes intact.
"""

NOTCH_EDIT = (
    "## Interface deltas\n",
    "Amendment (owner, 2026-10-16): the refusals say spell_id - \"notch_spell: spell_id '<id>' is not owned ...\",\n"
    "\"... belongs to another SpellIndex ...\", \"notch_spell needs a spell: pass spell_id=<the spell_id bind or\n"
    "bind_inactive returned>, ...\" - and the argument checks are shared with the index moves\n"
    "(component_patch_conduit_index_move_target.md).\n\n## Interface deltas\n",
)


def replace_all(path: pathlib.Path, pairs: list) -> None:
    """Apply exact (old, new) replacements, each old occurring exactly once in an LF file."""
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit(f"{path}: {text.count(old)} occurrences of {old[:70]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"{path}: {len(pairs)} edit(s)")


if __name__ == "__main__":
    replace_all(ARCH, ARCH_EDITS)
    replace_all(NOTCH, [NOTCH_EDIT])
    if MOVES.exists():
        raise SystemExit(f"{MOVES} exists")
    MOVES.write_text(MOVES_TEXT.replace("<NOW>", NOW), encoding="utf-8")
    print("wrote", MOVES)
    for path in (ARCH, NOTCH, MOVES):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if len(line) > 120 and not line.startswith("|"):
                print("LONG", path.name, number, len(line))

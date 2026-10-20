# S4 documentation drafts (melder_1, 2026-10-18) - applied at landing, re-read against the landed tree first

`<notch>` is the version S4 takes when it lands (above S1's and S2's). Citations are by symbol; numeric ranges are
measured at landing. Every target section is re-sliced through its index before the edit.

## src_architecture - Operational Invariants (new first entry)

- A version moved into an index of its own is known to its frame (2026-10-18, <notch>; the owner's word, chat
  2026-10-18: "it should properly follow the general spell index creation and registry binding processes the same
  way it does during bind"): `Spellbook._apply_remove_from_index` mints the fresh index as Bind creates one
  (`SpellIndex(initial_id=spell_id)`) and, right after its Book-locked move, registers it in the frame's spell
  registry the way a post-conjure `bind` registers the index it creates - bind's guard (the Book is conjured) and
  call (`Aether._register_single_spell_index` under the Book's root conduit). Every walk of that registry then
  finds the version, parked there or notched active: `find_index_for_spell` and `find_conduit_id_for_spell`, and
  through them the Conduit's spell_id lookups, a grant and an ownership transfer by spell_id, bind's collision
  guard (`Aether._check_for_spell`, in the frame and across frames under process-wide spell ids) and
  MutationResearch residency. The index leaves the registry when it empties (`_destroy_spell_index`, as an index
  bind created does) or with its root: `_unregister_conduit_spells_from_aether`, which only the root's teardown
  calls, unregisters the index of every parked version beside the active versions' indexes, so the frame keeps no
  entry for a torn-down root. Residency calls a version active only when its index selects it and the frame's
  lineage registry tracks it as that index's current version (`SpellSystemStates.get_by_index_id(...)
  .current_spell_id`): the minted index selects its parked member (activation takes a notch; the owner's ruling,
  2026-10-17) and no lineage tracks that member until a notch registers it, so it reads parked; members of every
  other index read as before. No new index state, and nothing persisted, cached or emitted changes. Locks: the
  registration takes the frame lock alone after the Book lock is released (bind's order); the teardown reads each
  parked version's index under the Book lock through the spell's own lock (Book -> spell, Book teardown's order)
  and unregisters with the frame lock alone; residency takes the lineage registry's lock, then the state's, each
  alone. Until <notch> the minted index was never registered, so the version was unknown to its frame by spell_id -
  the Conduit lookups raised "not found in any conduit", a grant and a transfer by spell_id were refused, and
  another Book could bind its spell_id - and residency read it `declared_only`.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_remove_from_index`,
  `Spellbook._unregister_conduit_spells_from_aether`, `Spellbook._destroy_spell_index`,
  `src/melder/aether/aether.py:Aether._register_single_spell_index`, `Aether._check_for_spell`,
  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.find_index_for_spell`,
  `AethericFrame.unregister_conduit_spells`, `src/melder/aether/conduit/conduit.py:Conduit._cleanup_normal_conduit`,
  `src/melder/mutation_research/mutation_research.py:MutationResearch._locate_live_membership` and
  `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`.

## src_architecture - the 0.2.8256 invariant's filed gaps

"... and a minted index is missing from the frame registry (STORY-2026-10-17-minted_index_missing_from_frame_registry)"
gains "(fixed in <notch>)".

## src_architecture - Failure Modes and Error Paths (new first entry)

- Fixed in <notch>: a version moved into an index of its own with `remove_from_spell_index` is found by its
  spell_id. The frame never listed that index, so `Conduit.get_spell_by_spell_id` and `get_conduit_by_spell_id`
  raised ValueError "Spell version <id> not found in any conduit." for a version the conduit's own Book owns, parked
  there or notched active; a grant (`add_spell_to_contract(spell_id=...)`) and an ownership transfer by spell_id
  raised the same; another Book bound its spell_id - of the frame, or of another frame under process-wide spell
  ids - so two Books held one spell_id, and a Book not yet conjured then had its conjure refused; and
  `residency_view` read it `declared_only`. A second bind now raises the existing RuntimeError "Spell ID collision
  detected. ...".
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_remove_from_index` and
  `src/melder/aether/aether.py:Aether._check_for_spell`.

## src_architecture - the 0.2.8253 Breaking failure mode

"the Conduit lookup still raises "not found in any conduit" for such a version, because the index the move mints
is missing from the frame registry (pre-existing; STORY-...)" gains "- fixed in <notch>".

## src_architecture - Sequence: SpellIndex Mutation Entry, step 5

"remove mints a fresh inactive index instead of destroying anything;" becomes "remove mints a fresh inactive index
instead of destroying anything and registers it with the frame as `bind` registers the index it creates (<notch>);".

## src_architecture - C1 Code Map notes (extents measured at landing)

- spellbook.py: "...; `_apply_remove_from_index` registers the index it mints with the frame as `bind` registers
  its new one, and the root's teardown unregisters the indexes that hold only parked versions (<notch>)."
- spell.py: "...; `_spell_index_unless_cleaned` lists the root's teardown among its readers (<notch>)."
- mutation_research.py: "...; residency calls a version active only while the frame's lineage registry tracks it
  as its index's current version (<notch>)."

## src_architecture - Context / Handoff Summary (new first paragraph)

2026-10-18 the minted index is registered (<notch>; STORY-2026-10-17-minted_index_missing_from_frame_registry, on
the owner's word "it should properly follow the general spell index creation and registry binding processes the
same way it does during bind"): the index `remove_from_spell_index` mints is registered with the frame as a
post-conjure `bind` registers the index it creates, the root's teardown unregisters it with the rest, and
residency reads its version parked until a notch. A new operational invariant, a fixed failure mode, the index
mutation sequence and the code map carry it; the 0.2.8256 invariant's and the 0.2.8253 failure mode's filed gap
is marked fixed; the component map carries the per-component contracts. No new index state (the owner withdrew
it).

## src_components - Subcomponent: SpellIndex Mutation Surface, Behavior

"remove never destroys - it mints a fresh inactive index for the separated spell and leaves the source with its
remaining members." becomes "... leaves the source with its remaining members, and registers the fresh index in
the frame's spell registry the way a post-conjure `bind` registers the index it creates (bind's guard and call,
the Book's root conduit; <notch>), so the lookups by spell_id, grants, transfers and bind's collision guard find
the separated version; it leaves the registry when it empties or with its root."

## src_components - Flow: Conduit Index Moves by spell_id -> Spellbook Seams, step 4

Append: "remove then registers the index it minted (`Aether._register_single_spell_index` under the Book's root
conduit, the frame lock alone after the Book lock; <notch>)."

## src_components - Component: AethericFrame Services, Responsibilities (new bullet after "Maintain selected-spell
registry.")

- List every index a conjured Book owns in the spell registry under the Book's root conduit (<notch>): conjure
  registers the indexes with an active version, a post-conjure `bind` the index it creates and
  `remove_from_spell_index` the index it mints; `_destroy_spell_index` unregisters an emptied index and the root's
  teardown every index the root registered, the parked-only ones included. `find_index_for_spell`,
  `find_conduit_id_for_spell` and the cleanup-safe probes walk it.

## src_components - MutationResearch ResearchSet Package, residency bullet

"(frame scan via `find_index_for_spell`; selected member -> `active`, unselected member -> `parked`)" becomes
"(frame scan via `find_index_for_spell`; a member its index selects and its lineage tracks as current ->
`active`, any other member -> `parked` - a version moved into an index of its own reads parked until a notch;
<notch>)".

## tests_components - Spellbook Integration Cluster

- a version moved into an index of its own is known to its frame (<notch>;
  `test_separated_version_is_known_to_its_frame_integration.py`, 12 tests): in a dynamic world with English
  active and French parked on English's index under its own binding name, after `remove_from_spell_index(French)`
  the frame finds French's index under the lender and both Conduit lookups answer, parked and notched active; a
  linked borrower's grant by spell_id gives a parked or an active copy as French is; a transfer by spell_id moves
  French to the target root; a second bind of French's spell_id is refused by another Book of the frame and of
  another frame, conjured or not; the lender's teardown takes French's index out of the frame and a new Book may
  bind French; moving French back leaves no registered index behind; and residency reads French parked in its own
  index, then active after a notch.
- Key file `tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py`
  (2026-10-18) and its code-map record; the residency unit file's code-map record remeasured (a selected version
  no lineage tracks reads parked).

## release_docs/next_version_release.md (before "## Packaging and documentation")

## A version moved into an index of its own is found by its spell_id

`Conduit.remove_from_spell_index` moves a parked version out of its spell index into a fresh index of its own,
where it stays parked until you notch to it. Until <notch> the frame never learned about that index, so the
version - parked there or notched active there - could not be found by its spell_id from a conduit:

    (the example, run by probes/probe_release_note_s4.py before it goes in)

- `get_spell_by_spell_id` and `get_conduit_by_spell_id` answer for such a version, parked or active; they raised
  `ValueError` "Spell version <spell_id> not found in any conduit.".
- A linked conduit's `add_spell_to_contract(spell_id=...)` and `transfer_spell_ownership(spell=<spell_id>)`
  proceed for it; both raised that `ValueError`. The borrower's copy is parked or active as the version is.
- Another Spellbook can no longer bind the same spell_id while the version sits in its own index: the bind raises
  the usual `RuntimeError` "Spell ID collision detected. ...", in the same frame and, under process-wide spell ids
  (the default), in another frame. The bind used to be accepted, so two Spellbooks held one spell_id.
- `MutationResearch.residency_view(spell_id)` reads the version `parked` in its own index and `active` there once a
  notch makes it active; it read `declared_only`.

What stays the same: what `remove_from_spell_index` moves and refuses, the version staying parked until a notch,
moving it back with `add_to_spell_index` (its emptied index goes), and every lookup of a version in any other
index. No public signature changes.

Packaging bullet: "The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the
packaged graph describe the registration of the index `remove_from_spell_index` mints, its removal at the root's
teardown and residency's parked verdict; the code-map extents of the three changed files are remeasured, and
their line citations remapped." The rebuild line names <notch>.

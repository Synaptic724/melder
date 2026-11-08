# code_description_patch_change_control_announcing

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: the type-key announce (`ChangeControlManager._default_dirty_marker`, `Spellbook._add_contracted_spell`)
  and the hidden-frame watch (`SpellSystemStates._extract_collection_frame_keys`)
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Trigger Justification
- Ordering- and concurrency-sensitive: the announce runs in the commit hook chain after the structural validator,
  resolves live spells under the Book lock, and marks the frame registry under its lock; it changes which consumers
  are gated by a commit, so it decides when step 6c of code_description_patch_hidden_provider_refusal.md takes
  effect.

## Control-Flow Description (Pseudocode Level)
1. Commit of a bind, notch or link (`_dispatch_commit_validator` -> structural validator ran; then
   `_dispatch_commit_hook` -> dirty marker -> commit hook):
   ```
   if staged.spellbook_id is None or (no binding keys and no contract keys): return     # unchanged
   frame_keys = {frame for frame, _ in staged.binding_keys if frame}
                | {frame for frame, _, _ in staged.contract_keys if frame}             # unchanged
   book = self._resolve_spellbook_for_staged(staged)                                   # may be None
   for spell in self._resolve_spells_for_binding_keys(book, staged.binding_keys):      # Book lock, brief
       type_key = CompilerPhase3._hidden_type_key(spell)                               # bind-time fields only
       if type_key: frame_keys.add(type_key)
   if frame_keys: sss.mark_collection_dependents_dirty(spellbook_id, frame_keys)        # ONE call, as today
   contract part unchanged
   ```
2. Contract grant (`Spellbook._add_contracted_spell`): inside the existing Book-lock block take
   `frame_key = spell.key[0]` (unchanged) and `type_key = CompilerPhase3._hidden_type_key(spell)`; after the lock,
   when conjured, mark `{frame_key, type_key} - {None}` in the existing single call; the contract-dependent mark is
   unchanged.
3. Topology registration (`register_local_topology` -> `_extract_collection_frame_keys`): for each UNRESOLVED_INPUT
   socket add `dependency_key[0]` (unchanged) and each of its `hidden_frame_keys`; other kinds unchanged.
4. A gated consumer is not recompiled here: its next meld reruns phases 1-4 (existing gate).

## Edge/Error and Rollback Semantics
- Edge: a bare spell (default or named binding) adds nothing - its frame key already is its type key.
- Edge: a departed spell no longer resolves at commit; only its frame key is announced, and a refused consumer hears
  it through `hidden_frame_keys`.
- Edge: no spellbook resolvable for the staged mutation (unit fakes, spellbook-only initiators) -> no type keys; the
  frame-key mark is unchanged.
- Error: a failure resolving spells must not break the commit hook any differently than today's mark would: resolve
  failures are swallowed into "no type key" (the frame-key mark still runs); a failing registry mark propagates as
  today.
- Rollback: removing steps 1-2's type key restores today's announces; `hidden_frame_keys` can stay (harmless).

## Invariants and Idempotency Expectations
- Invariant: one predicate (`_hidden_type_key`) for Phase 3 and the announcers; a key is announced only for a spell
  that a class lookup cannot reach.
- Invariant: still exactly one `mark_collection_dependents_dirty` call per commit and per grant.
- Idempotency: marking an already-gated consumer again is a no-op beyond the dirty registry; no lock is held across
  the two registries (Book lock released before the frame-registry mark, as today).

## Explicit Non-Goals
- No announce for departures that announce nothing today (`cleanup_spell` D1, G4 - watchers epic).
- No eager recompilation; no new transaction type; no change to contract-key marking.

## Validation Focus Points
- Unit: union into one call; nothing added for bare and bare-named spells; grant marks the type key; the watch index
  adds `hidden_frame_keys` for UNRESOLVED_INPUT only.
- Component: S1 framed cells give one answer (refused) LIVE and FRESH; a notch of the hidden candidate's index to a
  version of another name turns a refused consumer back into UNRESOLVED_INPUT; the frame's own consumer still wakes.
- Concurrency: the S1 and probe tests the GIL off and on; the full suite's multithreading files unchanged.

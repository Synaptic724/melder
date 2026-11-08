# code_description_patch_hidden_provider_refusal

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: the HIDDEN_PROVIDER refusal across Phase 3, Phase 4, the bind and meld gates, Phase 6 and
  UnresolvedInputError
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Trigger Justification
- Non-trivial error semantics: worlds that conjure today refuse (D2); a SpellMap miss moves from a Phase 3 raise to a
  Phase 4 report; a late bind refuses but leaves the spell registered; every meld then refuses, override or not; the
  refusal lifts through two different wake paths. Several branches (single, string, Optional, SpellMap, list,
  automatic, dynamic) must agree.

## Control-Flow Description (Pseudocode Level)
1. Phase 3, per socket of a resolvable spell (resolution exactly as today):
   ```
   resolved = resolve(dep)                       # unchanged
   if not resolved:
       if SINGLE_BY_ANNOTATION:
           unresolved.add(key)                   # unchanged
           ids, frames = hidden(annotation, single)
           if ids: socket_hidden[key] = (ids, frames)
       elif COLLECTION_BY_ANNOTATION and not dep.is_optional:
           ids, _ = hidden(annotation, collection)
           if ids: socket_hidden[key] = (ids, ())
       elif SPELLMAP_DEFAULT and found(hidden_out):   # resolver returned {} instead of raising
           unresolved.add(key); socket_hidden[key] = (ids(found), frames(found))
       continue
   ```
   `hidden(...)` is () for a Protocol annotation and for a name in a collection. A SpellMap miss with X bound nowhere,
   frame-named, or ambiguous raises as today.
2. Phase 4, per spell: RequiredHoles skips UNRESOLVED_INPUT sockets with ids; HiddenProviderStrategy emits one
   `error HIDDEN_PROVIDER` per such socket (annotation or SpellMap form); CompilerPhase4 marks the spell broken and
   its SpellIndex `invalid`.
3. Conjure (automatic or dynamic): any broken spell -> SpellbookValidationError; the block lists
   "  - <message> [HIDDEN_PROVIDER]"; nothing is constructed.
4. Late bind in a dynamic world: the commit's structural validator runs phases 1-4 for the new spell ->
   SpellbookValidationError from the bind; the spell stays registered, `invalid` (today's AMBIGUOUS behaviour).
5. Meld of a refused spell: the validity gate (`Meld._gated_validation_required`) reads `invalid` ->
   SpellbookValidationError (same block) whatever override the meld carries; no rerun, nothing constructed.
6. Re-gate paths (the spell becomes `gated`; the next meld reruns phases 1-4 and steps 1-2 decide again):
   a. the class is bound bare -> its frame key equals the consumer's dependency key -> NORMAL, meld succeeds;
   b. a hidden candidate's address is announced (`hidden_frame_keys` watch) -> e.g. its index notched to a version
      of another name (the C4 shape) -> no hidden left -> UNRESOLVED_INPUT warning, the meld needs an override again
      (a same-named version keeps the refusal);
   c. a framed spell of the class arrives (bind, notch, contract grant) -> its type key is announced (D1 = B) -> a
      consumer that compiled UNRESOLVED_INPUT before it is refused at its next meld.
7. Phase 6 (a valid spell only): an empty required class collection with ids -> `collection_socket_no_providers`
   naming the bindings; ERROR when the Book is not dynamic, WARNING and `[]` when it is.
8. Meld of a consumer with an unsupplied UNRESOLVED_INPUT socket (no ids recorded): `UnresolvedInputError` computes
   hidden candidates live and names them, else keeps today's text.

## Edge/Error and Rollback Semantics
- Edge: a class also bound bare (resolvable or a non-resolvable definition) is found - NORMAL or OVERRIDE_REQUIRED -
  so no ids (F2 stays as is). A Protocol's own definition never counts. A method spell never counts for a single
  socket. Non-resolvable framed definitions count for single sockets, not for collections (D5).
- Edge: `Optional[Class]` without a default is refused; with an ordinary default the parameter is PLAIN and never
  looked up (a migration path, D2).
- Edge: same-named classes from different modules share a type key; all are listed (D5).
- Edge: an id the spellbook no longer finds renders `spell id <id>`; rendering never raises.
- Error: HIDDEN_PROVIDER is an error, never a warning, and not a gating warning.
- Rollback: reverting the change set restores the UNRESOLVED_INPUT path and the Phase 3 SpellMap raise; generation 27
  may stay.

## Invariants and Idempotency Expectations
- Invariant: steps 1-2 are a pure function of the pool snapshot Phase 3 reads (the index or the scan copy); rerunning
  them over the same pool yields the same ids, frames, issues and texts (sorted ids, address-ordered entries).
- Invariant: no candidate is ever a target, edge, dependency id or Nexus relationship.
- Idempotency: marking a refused consumer `gated` twice before its meld reruns once (existing gate).

## Explicit Non-Goals
- No change to what resolves, to the meld doors, or to SpellMap misses with X bound nowhere or frame-named (D4).
- No unregistering of a spell refused at its late bind (existing bind-commit semantics).
- No new configuration switch or warning-mode variant.

## Validation Focus Points
- The probe matrix as an integration file: placements (Protocol +/- name, category +/- name, bare + name, two
  frames) x consumers (class, string, `Optional[Class]`, `list[Class]`, `SpellMap(Class)`, `SpellMap(Class,
  binding_name=...)`) x postures (automatic, dynamic pre-bound, dynamic late-bound): exact codes and texts; late bind
  refused and melds refused with and without override; controls (bare, bare + framed version, nothing) unchanged.
- Re-gate paths 6a, 6b, 6c each pinned; the ORDER cases (framed, category, bare-named, bare) under D1 = B.
- The GIL off and on.

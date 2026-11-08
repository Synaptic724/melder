# architecture_patch

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Status: draft (design approved by the owner, chat 2026-11-07: "ok go ahead ... lets fucken send it"; calls D1-D5
  below)
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Patch Scope and Non-Goals
- Objective: part (a) of TASK-2026-11-07-spellframe_ambiguity_validation_check. A class lookup - a class annotation,
  a single string annotation's type part, `Optional[Class]` without a default, `SpellMap(spell=Class)` without a
  spellframe - that finds no spell bound bare while spells of that class are bound under a spellframe or a binding
  name refuses its consumer at conjure with the Phase 4 error `HIDDEN_PROVIDER`, naming every place the class is
  bound and the lookup that reaches it. The empty required `list[Class]` (`collection_socket_no_providers`) and
  `UnresolvedInputError` name the same places. A class also bound bare is found as today. A framed spell's bind,
  notch or contract grant also announces its type key, so a consumer compiled before is re-checked and refused at
  its next meld (D1 = B). AMBIGUOUS_PROVIDER loses its unworkable override remedy (D4).
- Owner calls (chat 2026-11-07): D1 = B (announce the type key at the two announcer sites); D2 = the break, yes (an
  override no longer rescues such a consumer; migration: a frame SpellMap default, a Protocol annotation, binding the
  class bare, or an ordinary Python default); D3 = a dynamic empty `list[Class]` stays WARNING + `[]`, its text naming
  the bindings; D4 = drop AMBIGUOUS_PROVIDER's "supply it at meld with override=..."; other SpellMap misses (X bound
  nowhere, frame-named) stay as they are; D5 = `Optional[Class]` without a default is refused, a Protocol's own
  definition never counts, non-resolvable framed definitions count for single sockets only, same-named classes from
  different modules are all listed. Name `HIDDEN_PROVIDER`; cache generation 27 (`class_lookup_hidden_providers`);
  structural `PAYLOAD_FORMAT` 3.
- Non-goals: what resolves (the matching table, the buckets resolution reads, the meld doors); SpellMap misses with
  X bound nowhere and frame-named SpellMap misses (the Phase 3 RuntimeError stays); the dynamic empty-list policy;
  departures that announce nothing today (`cleanup_spell` D1, G4 - EPIC-2026-10-25-dependency_watchers_listen_for_names);
  Bind, addresses, SpellContract, codegen, Nexus publication; part (b).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler Phase 3 (`CompilerPhase3`) and `SpellSocketDescriptor` | modify | compute and record hidden candidates on a class-lookup miss; `SpellMap(Class)` miss records instead of raising | none |
| Spell Validation Strategies (Phase 4): `HiddenProviderStrategy` (add), `HiddenProviderReport` renderer (add), `SpellValidationSystem`, `RequiredHolesStrategy`, `AmbiguousProviderStrategy` | add/modify | refuse with the addresses; no duplicate UNRESOLVED_INPUT warning; drop the override remedy | Phase 3 |
| System Validation (Phase 6): `EmptyCollectionStrategy` | modify | name the bindings of an empty required `list[Class]` | Phase 3, renderer |
| `UnresolvedInputError` | modify | name the bindings, computed live on its failure path | Phase 3 predicate, renderer |
| `StructuralSnapshot` and `CachingSystem` | modify | rows carry the two new descriptor fields (format 3); generation 27 | Phase 3 |
| DevOps Control Plane: `ChangeControlManager._default_dirty_marker`, `Spellbook._add_contracted_spell`, `SpellSystemStates._extract_collection_frame_keys` | modify | announce a framed spell's type key (D1 = B); a refused consumer watches its hidden candidates' frames | Phase 3 predicate |

## Interface and Boundary Deltas
- Boundary delta 1: none public. New internal fields `SpellSocketDescriptor.hidden_spell_ids` and
  `hidden_frame_keys`; new internal bucket `by_hidden_type`; new Phase 4 code `HIDDEN_PROVIDER`; no new exception type.
- Interface delta 1 (Breaking): a consumer whose class lookup misses a class bound only under a spellframe or a
  binding name is refused - at conjure (SpellbookValidationError), at its late bind in a dynamic world (the bind
  raises; the spell stays registered and invalid, as AMBIGUOUS_PROVIDER today) and at every meld after, override or
  not. Today it conjures with an UNRESOLVED_INPUT socket and melds with an override.
- Interface delta 2 (Breaking): `SpellMap(Class)` / `SpellMap(Class, binding_name=b)` that misses a Class registered
  elsewhere refuses through SpellbookValidationError [HIDDEN_PROVIDER] instead of PhaseExecutionError at conjure and a
  bare RuntimeError at a late bind or meld.
- Interface delta 3 (text): `collection_socket_no_providers` (both severities) and `UnresolvedInputError` name the
  bindings when there are any; texts are unchanged otherwise. AMBIGUOUS_PROVIDER's text loses its override remedy.
- Interface delta 4 (announce): a framed spell's bind, notch and contract grant announce its type key beside its
  frame key; a bare spell's announce is unchanged (its frame key is already its type key).

## Cross-Component Invariants
- Invariant 1: what resolves is unchanged. Hidden candidates are computed only after a class lookup came back empty;
  no socket gains a target, no NORMAL socket changes kind.
- Invariant 2: one predicate. `CompilerPhase3._hidden_type_key(spell)` - the type key of a spell that does not answer
  a class lookup and is not a Protocol definition - is the only definition, read by Phase 3 (scan and the
  `by_hidden_type` bucket, equal membership), `UnresolvedInputError` (live) and the announcers.
- Invariant 3: a single or SpellMap socket with hidden ids makes its spell broken, so it never reaches planning,
  Phase 8 signature rows, Nexus relationships or a structural replay; only an empty required class-collection socket
  carries hidden ids on a valid spell.
- Invariant 4 (LIVE = FRESH): a consumer compiled before its class was bound under a frame and one compiled after
  give one answer - refused - through the type-key announce; a refused consumer is re-gated when the class arrives
  bare (its dependency key) or a hidden candidate's address is announced (`hidden_frame_keys`).
- Invariant 5: `SpellbookValidationError` composition is unchanged: HIDDEN_PROVIDER is an ordinary user-fixable error
  (not internal, not gating, not restating, not superseded).

## Migration and Rollout Order
1. Phase 3: `_hidden_type_key`, `by_hidden_type`, `_hidden_class_candidates`, the descriptor fields, the
   `_build_local_frame_dag` miss branch, `_build_local_topology(socket_hidden=...)`, `_resolve_spellmap_default(hidden_out=...)`.
2. Phase 4: `HiddenProviderReport`, `HiddenProviderStrategy` registered after `AmbiguousProviderStrategy`;
   `RequiredHolesStrategy` skip; AMBIGUOUS_PROVIDER text.
3. Phase 6 text; `UnresolvedInputError` text.
4. `SpellSystemStates` watch keys; the two announcers.
5. `StructuralSnapshot` format 3; cache generation 27.
6. Tests (component patches, Validation Expectations): new tests; the 39 measured flips (30 of the refusal, 9 of the
   announce); the by-design updates.
7. Docs: release note (Breaking), src_architecture, src_components, graph and indexes, docstrings; this patch merged.
8. Notch 0.2.8281; rebuild (assets, llm_support) and `--check` last.

## Rollback Strategy
- Rollback trigger: the owner reverses D2 (a world he wants to conjure refuses), or the announce causes failures or
  rebuild load the suite or a consumer world shows.
- Rollback steps: revert the change set as one commit. Partial: reverting step 4's announcers alone leaves the
  compile-time verdict (a consumer compiled before its framed provider keeps UNRESOLVED_INPUT; its UnresolvedInputError
  names the binding) - documented as LIVE != FRESH. Generation 27 may stay (a bundle is cold once either way).
- Post-rollback verification: the full suite at the 0.2.8280 baseline; the probe matrix back to the measured current
  table (scratch run_0_2_8280_gil0.txt).

## Validation Expectations and Evidence Plan
- Validation item 1: the new tests in each component patch pass, the GIL off and on.
- Validation item 2: the 39 tests the emulated design flips are rewritten to the new contract and pass - the 30 of the
  refusal (6 files; component_patch_phase4_validation_strategies.md) and 9 of option B's announce in
  tests/unit/melder/spellbook/test_spellbook.py (component_patch_change_control_announcing.md); measured on the full
  suite (mode 1 and mode 2 against the as-shipped run, the GIL off) and confirmed on the 7 files the GIL off and on
  (same 39 both modes); the by-design updates (index key set x2, snapshot format and rows, cache history, AMBIGUOUS
  unit test) pass.
- Validation item 3: the full suite, the GIL off and on, at the baseline but for the rewritten tests; the example
  suite unchanged (0 of 627 flips measured); the probe matrix re-run reads HIDDEN_PROVIDER in every hidden cell and
  the controls unchanged.
- Evidence source 1: scratch runs of the design (hidden_class_probe.py and its runs; hidden_provider_plugin.py modes
  1 and 2; suite_hidden_mode0/1/2 and their diffs; affected_diff_gil0/gil1, affectedB_diff_gil0/gil1; the example
  suite, 0 of 627 flipped in either mode) - copied to context_compass/artifacts/hidden_provider_20261107/ at
  implementation, then the after-runs beside them. Harness note: the cache-test flips between full runs (16 between
  modes 0 and 1, 11 between modes 0 and 2, all in test_conjure_cache_restage, the executor world-stamp test,
  test_cache_runtime_integration and the cache-parity probe) came from runs sharing the suite's gitignored cache
  folders under src/melder/tests/; rerun alone, those four files pass in modes 0, 1 and 2 (38 of 38).

## Ticket Coverage Map
- Epic: EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Story: none (epic-level task)
- Tasks: TASK-2026-11-07-spellframe_ambiguity_validation_check, part (a)

## Unknowns and Decision Requests
- UNKNOWN: which departure paths announce the removed spell's frame key; `hidden_frame_keys` re-gates a refused
  consumer only where one does (a notch does - S1 C1/C2; `cleanup_spell` does not - S1 D1, watchers epic; the others
  are measured by the new integration tests).
- Measured (no longer unknown): option B adds 9 flips, all in tests/unit/melder/spellbook/test_spellbook.py, whose
  `DummySpell` stub has no `.spell` and whose framed-copy mark assertions name only the frame key.
- DECISION_REQUEST: none open (D1-D5 decided 2026-11-07).

## Context / Handoff Summary
- What changed: nothing in src; this patch fixes the contract.
- What remains: rollout steps 1-8.
- Next entrypoint: component_patch_compiler_phase_3.md, then code_description_patch_hidden_provider_refusal.md.

# architecture_patch

## Metadata
- Patch ID: class_lookup_bare_spells_2026_11_07
- Status: completed (merged into src_architecture and src_components 2026-11-07; moved to patches/completed/)
- Owner: Mark (owner); written by melder_0 (synaptic_python_developer)
- Created: 2026-11-07T13:48:07Z
- Updated: 2026-11-07T13:48:07Z

## Patch Scope and Non-Goals
- Objective: a class lookup reaches a spell only when the spell is bound bare - no spellframe and the default
  binding - as the class meld door already requires (Autofac: a declared service hides the component's own type;
  the owner's rulings E1-E3 and the 13 settled points, chat 2026-11-07). The class lookups are a class annotation, a
  single string annotation's type part, `list[Class]` and `SpellMap(spell=Class)` without a spellframe. A spell bound
  under a spellframe is reached through the frame - Melder's interface dict, keyed by binding name - and a bare spell
  with a binding name through `SpellMap(Class, binding_name=...)` or `meld(Class, binding_name=...)`.
- Non-goals: the meld doors (already address lookups); Bind, addresses and the frame lookup containers; SpellContract
  (already address-based, `canonical_key`); Protocol/contract, definition and label matching; the Phase 4 check
  (TASK-2026-11-07-spellframe_ambiguity_validation_check); an AsSelf-style option (declined, 2026-11-07); S1's other
  misses (EPIC-2026-10-25-dependency_watchers_listen_for_names).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler Phase 3 (Component: SpellCompiler and Validation Pipeline) | modify | the type row of the matching table and the explicit-spell SpellMap branch admit only bare, default-binding spells | none |
| SpellMap descriptor (Subcomponent: SpellMap Descriptor) | modify (docstring only) | its class docstring states what `SpellMap(spell=X)` reaches | Phase 3 |
| Creation cache (Component: Spellbook Core, the cache envelope) | modify (constant) | generation 26 retires bundles whose replayed phase 3-4 rows hold class matches of framed or named spells | Phase 3 |

## Interface and Boundary Deltas
- Boundary delta 1: none. No public signature, no new parameter, no new exception type; Phase 3 stays the only place
  a class lookup is decided (T1 found no other matcher).
- Interface delta 1 (behaviour, Breaking): a consumer annotated `x: English` (or `"English"`, or `list[English]`)
  no longer resolves an English bound under a spellframe or with a binding name; its single socket compiles
  UNRESOLVED_INPUT like any missing provider (the meld raises UnresolvedInputError unless the value is supplied),
  and the collection gathers only bare, default-binding members.
- Interface delta 2 (behaviour, Breaking): `SpellMap(spell=English)` with no spellframe reaches only an English bound
  with no spellframe - with no binding_name given, only the default binding; with `binding_name=b`, only English bound
  bare under `b`. A miss raises the existing RuntimeError "SpellMap default could not be resolved".

## Cross-Component Invariants
- Invariant 1: one rule for class lookups - Phase 3 class matching reaches English only when it is bound with no
  spellframe and the default binding, and the class meld door (`meld(English)`, an address lookup) reaches only the
  address ("english", default binding), so neither reaches English under a Protocol, another category or a
  binding name. One edge differs, by the settled rule ("no spellframe"): English under a string category spelled
  as its own name (`spellframe="English"`) holds the bare address, so `meld(English)` still returns it while
  `x: English` does not; the upgrade path drops that redundant category (amended 2026-11-07, measured by the
  system-docs merge).
- Invariant 2: a class annotation's watch key (`_dependency_key_for_dep`: the annotation's name, default binding) is
  the address of every provider it can match, so a waiting consumer and an announced change agree by construction
  (the S1 key split cannot occur for class annotations).
- Invariant 3: Protocol, definition and label matching are unchanged; a frame's lookups (Protocol annotation,
  `list[Protocol]`, `list["label"]`, `SpellMap(spellframe=, binding_name=)`, `meld(spellframe=, binding_name=)`) read
  the interface dict as shipped - `meld(spellframe=F)` with no binding name reads the default slot while `x: F` finds
  the single implementation (dict behaviour, kept and documented).
- Invariant 4: scan path and index path stay equal - `_spell_keys_for` and the `by_type` bucket apply the same
  predicate, so candidate membership is identical with and without a pass cache.

## Migration and Rollout Order
1. Phase 3: one predicate (`_answers_class_lookup`) read by `_spell_keys_for` (type row, and a single name's type
   part), `_build_candidate_index` (`by_type`) and `_resolve_spellmap_default`'s explicit-spell branch without a
   spellframe; docstrings of the touched methods and the class docstring (still the 2026-10-03 address-key rule).
2. SpellMap's class docstring; creation-cache generation 26 with its history comment.
3. Tests: rewrite the 41 that assert the old rule, convert the 65 whose fixtures reach a provider through a frame or
   name (runs/suite_autofac_reading_0_2_8277_diff_gil0.txt).
4. Docs: README, handbook example 25, agents/MELDER_AGENT_OPERATIONS.md, UX AGENTS.md if it states the old rule;
   src_architecture and src_components with their indexes.
5. Release note (Breaking, four upgrade paths), notch 0.2.8278, ticket closure, rebuild and `--check` last.

## Rollback Strategy
- Rollback trigger: the owner rejects the break, or a converted test shows intent the owner wants kept.
- Rollback steps: revert the change set (src, tests, docs, release note, notch) as one commit.
- Post-rollback verification: the full suite at 0.2.8277's baseline (9 standing failures of the enum lanes), the
  S1 file back to its 14 strict xfails. No record format moves; the creation cache is cold once either way.

## Validation Expectations and Evidence Plan
- Validation item 1: the 41 rewritten tests assert the new contract and pass; the 65 converted tests keep their
  intent and pass; the full suite passes the GIL off and on but for the 9 standing failures.
- Validation item 2: the S1 matrix probe re-run shows no key-split MISS; the interface check re-run reads class
  consumers of framed spells unresolved; the example suite is unchanged (10 pre-existing failures).
- Validation item 3: the asset and llm_support rebuilds and their `--check` runs print only OK lines.
- Evidence source 1: context_compass/artifacts/dependency_watchers_20261107/runs/ (before: *_0_2_8277_*; after:
  *_0_2_8278_*).

## Ticket Coverage Map
- Epic: EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Story: none (epic-level tasks)
- Tasks: TASK-2026-11-07-class_annotation_selects_only_bare_spells (this patch); T3 builds on it.

## Unknowns and Decision Requests
- UNKNOWN: none open for the code path. T1 measured the blast radius (106 tests in 20 files, no example) and found no
  other matcher; the owner settled every edge case (epic Decision Log 2026-11-07T12:08:59Z).
- DECISION_REQUEST: none. A converted test whose intent looks worth keeping is raised on T2 before it is changed.
- No code_description_patch: no control-flow or state-machine change, no policy gate pipeline, no new error
  semantics (a miss uses the existing UNRESOLVED_INPUT path or the existing SpellMap RuntimeError), no concurrency
  change (pass-invariant keys, no lock).

## Context / Handoff Summary
- What changed: the patch is written; nothing in src yet.
- What remains: the rollout steps 1-5.
- Next entrypoint: component_patch_compiler_phase_3.md, then the T2 mapping note, then compiler_phase_3.py.

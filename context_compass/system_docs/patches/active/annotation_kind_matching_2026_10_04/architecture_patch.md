# architecture_patch

## Metadata
- Patch ID: annotation_kind_matching_2026_10_04
- Status: active (entry gate for the repair task)
- Owner: user (agent fable_1)
- Created: 2026-10-04T01:20:00Z
- Updated: 2026-10-04T01:20:00Z

<!-- BEGIN ENTRY: "annotation kind matching: scope, deltas, invariants" -->
## Patch Scope and Non-Goals
- Objective: a constructor annotation never reads a spellframe category as a provider set. Since 0.2.8218
  Phase 3 matches an annotation to a spell when the lowercased name of the annotation equals the spell's
  frame key OR its type key, so a string category named like a class (MelderOps: "spectrum" holding
  Toolbox, consumer `spectrum: Spectrum`) makes every member a candidate - an ambiguity when the provider is
  bound, a silently injected wrong type when it is not. Owner rulings (2026-10-03): a spellframe is a label; a
  string frame is a category; a Protocol frame is a category AND a contract (bind already checks its direct
  public members); a concrete class is not a valid spellframe; the binding records the kind so the matcher
  differentiates instead of guessing from a name.
- Non-goals: no change to explicit addressing (`meld(spellframe=, binding_name=)`, SpellMap, SpellContract),
  to Phase 4's one-address rule, to the meld hot path, to what the Protocol check verifies (a deeper check is
  a follow-up ticket), to an explicit `implements=` bind argument (follow-up ticket), to the Phase 4
  binding-key cycle heuristic or the frame-key watcher (both key annotations by name today and keep doing so).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Binding Pipeline (Bind, Spell) | modify (one enum, two Spell fields, one refusal) | the Spell carries no frame kind, so Phase 3 cannot tell a category from a contract | none |
| SpellCompiler and Validation Pipeline / Phase 3 | modify (kind-aware predicate and index) | one name-equality predicate serves singles and collections for every kind | the Spell fields |
| Crystallizer record and loader | modify (three crystal fields, frame hydration) | restore and graft rebind with the frame NAME, which would turn every Protocol frame into a category | the enum |
| Creation cache | modify (generation 20) | structural snapshot rows captured under the name matcher replay a retired rule | none |

## Interface and Boundary Deltas
- New public enum `SpellframeKind` (`melder.aether.spellbook.spellframe_kind.spellframe_kind`): `none`
  (bound bare; the address label is the spell's own name), `category` (a string), `contract` (a Protocol).
  Exported at the package root beside `Existence`.
- `Spell.spellframe_kind: SpellframeKind` and `Spell.implemented_protocols: Tuple[type, ...]` (the Protocol
  the spell was structurally checked against, else empty) - set at construction from inputs the fingerprint
  already hashes, so no spell id moves; both survive cleanup like `spellframe`.
- Breaking change: `Spellbook.bind(..., spellframe=X)` raises TypeError when X is neither a string nor a
  Protocol class (a concrete class, an instance, any other object). Before, any object was accepted and
  keyed by `str()`/`__name__`.
- Phase 3 matching: a class-object annotation selects spells of that class (type key); a Protocol annotation
  selects spells whose contract is that Protocol (by name); a string or ForwardRef annotation selects by name
  among type keys and contract names, never a category; a collection annotation gathers the group its kind
  names - a string: the members whose label (frame key) is that name; a Protocol: that contract's
  implementers; a class: spells of that class. Ambiguity, UNRESOLVED_INPUT and `require_class_spell` are
  unchanged. The pass index carries one bucket map per key kind; indexed and scan membership agree.
- Crystal payload gains `spellframe_kind`, `spellframe_module`, `spellframe_qualname` (RecordVersion 4.1.0:
  minor, additive). Restore and graft rebind a `contract` frame through the import lane and file a shortfall
  (binding the name as a category) when the Protocol cannot be hydrated; records without the fields rebind
  by name as before.
- Cache generation 20 (`annotation_kind_matching`) retires bundles captured under the name matcher.

## Cross-Component Invariants
- A category never satisfies an annotation; only explicit addressing and collections reach a category.
- A Protocol frame is checked at bind (unchanged) and is the only thing a Protocol-typed parameter resolves
  against; a bare class and an existing object answer to their class.
- Frame key, address and Phase 4 uniqueness are unchanged: `make_spell_key_from_parts` still lowercases the
  frame's name, so `SpellMap(spellframe=IService)` and `meld(spellframe="spectrum", binding_name=...)` find
  what they found before.
- A restored world resolves as the recorded world did when its Protocols import; when one does not, the
  report says which spell was rebound as a category.

## Migration Order
1. Patch lane linked; regressions red on the unpatched tree (the four strict-xfail cases run with
   `--runxfail`, the new bind-refusal and Spell-field tests, the crystal-field tests).
2. Source: enum module, Spell fields, Bind classification + refusal, Phase 3 predicate/index/resolvers,
   crystal fields + loader hydration, generation 20; docstrings included.
3. Test sweep (codemod): the 127 plain-class frames in 28 test files become Protocols or string labels per
   file; `repo: "extra_frame"` becomes a SpellMap default; the rebind M2 guard uses a Protocol.
4. Four tiers green; README DI/spellframe text, architecture invariant, components entries, graph
   descriptors; notch (read at landing), release note (Breaking change lead), closure, rebuild last.

## Rollback
- Revert the source files together with the tests added; records written at 4.1.0 stay readable by 4.0.0
  readers (same major), bundles at generation 20 are cold for a 19 reader by the existing rule.

## Ticket Coverage Matrix
| patch section | ticket |
|---|---|
| all | tickets/tasks/2026-10-04_repair_annotation_kind_matching_task.md |
| cause, survey, decision | tickets/tasks/2026-10-03_reproduce_annotation_category_collision_task.md |
<!-- END ENTRY: "annotation kind matching: scope, deltas, invariants" -->

# Component Patch: collection members get their own compiler paths (SpellCompiler Phases 5 and 8)

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: SpellCompiler and Validation Pipeline (PathRegistry, Phase-5 root blueprint overlay, Phase-8
  occurrence graph) plus the creation cache generation
- Task: TASK-2026-09-26-fix-collection-member-many-sharing
- Status: active
- Created: 2026-09-26T12:20:00Z

## Before
- `PathRegistry.extend_path(parent, name)` interns child paths by `(parent, name)`. Phase 5 and Phase 8 call
  it once per socket target, so every member of a collection socket sits on the same path id.
- A `many` spell below two members is therefore one occurrence `(spell, id("members>leaf"))`, one Phase-9
  instance key and one constructed object handed to every member. Owner ruling 2026-09-26: defect
  ("a many is not meant to be shared like that").

## After
- `PathRegistry.extend_path(parent, name, *, member=None)` interns by `(parent, name, member)`; the stored
  segment stays `name`, so `materialize_path`, `format_path`, `depth` and `parent_id` answer exactly as
  before for every path, and all string keys (override PATH specs, diagnostics) are unchanged.
- A collection socket keeps its own member-less path (its SocketRef is unchanged); each member target is
  queued (Phase 5) and expanded (Phase 8) on `extend_path(path, name, member=target_spell_id)`. Sockets of a
  member therefore have `parent_id == that member's occurrence path`, which is the rule the override
  compilers already use to attach socket targets to plan steps.
- Phase 8 DAG fallback (no topology, so collection-ness unknown): a parameter fed by two or more nodes uses
  the member rule; a single-node parameter is unchanged.
- `resolve_path_id` follows member-less edges only (no live caller; documented).
- Creation cache generation 13 `collection_member_paths`: version-12 bundles carry plans that share one
  object across members and cold-reset.

## Interface / State Deltas
- `extend_path` gains a keyword-only `member: Optional[str] = None`; positional callers are unchanged.
- Path ids of collection members' subtrees change (new ids, same strings). Non-collection graphs mint the
  same ids in the same order as before.

## Behavior Deltas (all follow from the owner ruling)
- Each collection member gets its own `Existence.many` dependencies, transitively. Shared existences
  (unique, unique_per_conduit, lineage, cluster, spell space) are unchanged: they are keyed `(spell, None)`.
- UNIQUE override counts for a parameter below those objects count each member's copy (`*z` under two
  members now matches 2). Today's PATH row for `members>leaf` stays last-write-wins until S3's resolver.

## Validation Expectations
- New component regression `test_spellbook_component_collection_many_instances.py`: red before, green after
  (distinct many objects per member, transitively; shared stays one; a second meld shares nothing).
- S1 oracle re-run; full unit and component suites A/B on 3.14t, spellbook suites on GIL; cache schema
  integration test updated to 13.

## Rollback
- Drop the `member` arguments at the three call sites and the cache entry; nothing else depends on them.

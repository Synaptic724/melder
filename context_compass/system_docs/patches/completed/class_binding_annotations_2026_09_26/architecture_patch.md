# Architecture patch: class binding profiles keep TYPE_CHECKING-named annotations (2026-09-26)

Ticket: tickets/tasks/completed/2026-09-26_fix_class_binding_profile_annotations_for_type_checking_names_task.md (owner approved
the fix and its one-time id change).

## Objective
A class whose class-level annotations name a type imported only under `TYPE_CHECKING` keeps those annotations in its
binding profile, unavailable names rendered as source text, so the class fingerprint reflects its annotated fields and
Nexus publishes them. Today every annotation of such a class is dropped (`{}`).

## Non-goals
- No change for classes whose annotations evaluate: same keys, same values, same spell id.
- No change to callable, instance or other profiles, to ClassInspector or the detailed profile, or to the
  fingerprint schema (`v4-binding` keeps hashing sorted annotation keys).
- No new bind failure: other exceptions, and a failure inside the fallback, still yield `{}` (documented
  best-effort, as today).
- No cache-generation bump.

## Changed components
- BindingProfileStrategy (spell_examiner/strategies): `_build_class_profile` catches NameError from the evaluated read
  and falls back to `SignatureReflection.class_annotations(cls)`, the shape ClassInspector already uses.

## Invariants
- Annotation reflection (existing, extended): Melder reads user annotations without evaluating names unbound at
  runtime; the class binding profile now follows it too. Keys equal the class's own annotation names.
- Process stability: unchanged - the fingerprint hashes keys only; the fallback is deterministic.
- An affected class gets a new spell id once (its keys join the fingerprint); later runs are stable.

## Interface deltas
- None. `ClassBindingProfile.annotations` may now hold `str` values (source text) for unavailable names, as the
  detailed ClassProfile already does.

## Consequences of the one-time id change (existing mechanisms, no new code)
- Creation cache: the new id is a miss; the non-full-hit conjure rewrites the bundle and drops the old id
  (generation 12 behaviour).
- Crystallizer restore maps recorded ids to the new ones; MutationResearch records a new version.

## Migration order
Strategy change -> unit tests (strategy + fingerprint) -> docs, graph descriptor, release note.

## Rollback
Restore the `except` block; no data, cache or persisted-format change.

## Coverage matrix
| change | validation |
| --- | --- |
| NameError fallback | unit: TYPE_CHECKING, quoted, nested and dataclass shapes keep keys; names as text |
| unaffected classes | unit: resolvable annotations keep evaluated values; RuntimeError still yields {} |
| fingerprint | unit: adding a TYPE_CHECKING-typed field changes the id; id identical across two processes |
| probes | before/after on the six-shape probe module |

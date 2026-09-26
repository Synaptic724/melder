# architecture_patch

## Metadata
- Patch ID: stable_callable_spell_ids_2026_09_26
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T10:42:41Z
- Updated: 2026-09-26T10:42:41Z

## Patch Scope and Non-Goals
- Objective: a spell's id is the same in every process for the same bound object and binding metadata,
  for callables (functions, lambdas, static/bound/class methods, partials, callable instances) and
  existing objects, as it already is for classes; and the conjure creation cache always holds a set of
  payloads built in one compile, so a changed provider id can never leave a consumer's cached plan
  pointing at an id that no longer exists.
- Non-goals:
  - No change to the class fingerprint (class ids do not move) or to the "v4-binding" schema prefix.
  - No body/bytecode identity for functions (owner chose signature-shaped identity, like classes).
  - No change to displayed reprs (binding profile repr_string, Nexus descriptors), to hydration, to the
    payload replayability gate (fable_0) or to Spellbook._emit_spell_cache.
  - Reprs that embed an address in a form other than CPython's " at 0x..." stay the object's concern.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Spell Examination Profiles (binding profiles, strategy, InspectorUtility) | modify | carry an address-free, untruncated repr for fingerprinting | none |
| Binding Pipeline (Bind, Spell, SpellIndex) | modify | sha256_profile hashes the address-free text | profiles |
| Spellbook Core (Binding and Conjure) - creation cache | modify | re-stage every live payload on a non-full-hit conjure, drop the rest; generation 12 | none |

## Interface and Boundary Deltas
- Interface delta (additive, keyword-optional): `fingerprint_repr` on CallableBindingProfile,
  InstanceBindingProfile and OtherBindingProfile; `default_fingerprint_repr` on
  CallableParameterBindingSummary; `InspectorUtility.stable_repr(obj)`. Omitted values fall back to the
  display text with addresses removed, so existing constructors keep working.
- Behaviour delta: ids of address-bearing spells change once to stable values; conduit cache bundles
  hold exactly the live payload-eligible set after any non-full-hit conjure.

## Cross-Component Invariants
- Invariant 1: fingerprint inputs contain no memory address.
- Invariant 2: two binds share a fingerprint only if they share every lookup-key component (spell name or
  spellframe, binding name), which Spellbook already rejects; removing addresses adds no new collision
  between distinct keys.
- Invariant 3: after a non-full-hit conjure, every payload in the bundle was built by that conjure's
  compile (or by a later meld-time stage in the same world); a full hit therefore never hydrates a plan
  that references a spell id outside the live pool.
- Invariant 4: class spell ids are unchanged.

## Migration and Rollout Order
1. Profiles + InspectorUtility (fields and helper), strategy fills them.
2. Bind.sha256_profile hashes them (fallback: address-stripped display text).
3. Conjure-end re-stage + prune; CachingSystem generation 12.
4. Tests: unit (helper, fingerprint), component (in-process distinct-object equality, provider-change
   A/B/B cache sequence, bundle size bounded), one cross-process id check.
5. Promote to src_components/src_architecture, graph, asset rebuild.

## Rollback Strategy
- Rollback trigger: class ids move, or any suite failure attributable to these files.
- Rollback steps: restore the six modified modules; delete the new tests; generation 12 bundles are then
  rejected by generation 11 readers and cold-reset (safe).
- Post-rollback verification: unit/component suites; asset --check.

## Validation Expectations and Evidence Plan
- Before evidence: artifacts/function_spell_ids_20260926/results (10 of 14 shapes unstable; bundle growth;
  stale consumer crash). After: all 14 shapes stable across processes; A/B/B melds succeed; bundle stays
  at the live count.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks: tickets/tasks/2026-09-26_stabilize_function_spell_ids_across_processes_task.md

## Unknowns and Decision Requests
- UNKNOWN: MutationResearch declares one more version per affected spell on the first run after upgrade
  (read from source, not probed).
- DECISION_REQUEST: none open (owner approved 2026-09-26: option 1, cache fix in this lane, full-repr
  fingerprint text).

## Context / Handoff Summary
- What changed: see component patches and the code description patch.
- What remains: implementation, validation, promotion, asset rebuild.
- Next entrypoint: the task ticket's latest Notes NEXT.

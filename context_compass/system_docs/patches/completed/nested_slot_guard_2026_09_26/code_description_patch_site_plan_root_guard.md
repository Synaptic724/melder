# code_description_patch_site_plan_root_guard

## Metadata
- Patch ID: nested_slot_guard_2026_09_26
- Component: SpellCompiler and Validation Pipeline
- Status: draft
- Created: 2026-09-26T21:48:30Z

## Control Flow
- SitePlanEmission.__init__ records whether the root's guard is held by the calling door:
  normal_mode and (door_route_key, root step existence) is ("unique_per_conduit", unique_per_conduit) or
  ("spellspace", unique_per_spell_space). The mapping is a class-level constant on SitePlanEmission.
- _emit_miss(index): when index is the root and that flag is set, emit
    children; v = c._creations.get(sid); if v is None: construct; publish; return v
  at one indentation level less and without "with <guard>:". Otherwise emit today's guarded miss.
- SitePlanOverrideRuntime._compile_normal_plan(door_route_key) forwards it to emit; _compile_plan (override key
  sets) does not.
- generalized_hydrator._build_site_plan_runtime(route_key=...) constructs the runtime with door_route_key.

## Edge / Error Semantics
- Door-held root, store cleaned mid-build: AttributeError at the recheck instead of at the guard read (both
  before construction). Disposal-bearing roots publish through add_creation as before, so a cleanup during their
  construction still disposes and raises RuntimeError.
- Same-thread nested meld of the root during a child's construction: the nested door re-enters the held guard
  (unchanged) and publishes; the outer root recheck returns that instance (unchanged).
- A normal plan called without holding the root's guard is a contract violation for the eligible routes only;
  every in-tree caller holds it (I4), and the default door_route_key=None keeps the guard for any other caller.

## Invariants / Idempotency
- Emission stays a pure function of its inputs; eligible and ineligible roots produce different source, so they
  get different code objects in the in-process cache.
- Nothing else in the emitted plan changes: hit reads, children placement, unresolved-input checks, disposal
  registration, operands.

## Non-goals
- Override key-set plans (their root keeps the re-entrant take).
- The door compiler, the specializer's own body, creations.py.

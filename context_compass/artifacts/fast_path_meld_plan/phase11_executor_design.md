# Phase 11 Executor Design (Draft, 2026-01-27)

## Purpose
Define a max-efficiency executor that consumes Phase 8-10 artifacts and
minimizes per-call overhead. This is optional and only for strict best-case.

## Inputs (from Phase 8-10)
- OccurrencePlan (Phase 8): execution order + instance keys.
- InjectionPlan (Phase 9): dependency wiring rules.
- PatchMaps (Phase 10): optional, only if Phase 11 allows limited overrides.

## Design Goals
- Minimal allocations per call.
- Minimal branching per step.
- Pre-resolved creation targets and reuse policies.
- Fall back to Phase 8-10 executor on any mismatch.

## Executor Model (Draft)
### Step Array
Represent the entire plan as a flat array of steps, each with precomputed
metadata. Example step layout:

```
Step:
  spell_id: str
  instance_key: _InstanceKey
  existence: Existence
  creation_target: "owner" | "caller" | "spellspace"
  action: "reuse" | "construct"
  inject_spec: InjectionSpecRef
  register: bool
```

### Execution Loop
For each Step in order:
1) If action == reuse, fetch from creations (no graph walk).
2) If construct, build kwargs from InjectionPlan (no per-call resolution).
3) Call the callable (or return existing object for existing-creation spells).
4) Register if required (per existence and disposal metadata).
5) Store instance in results map (or preallocated array).

### Prebinding Opportunities
- Prebind spell callables or constructors (store as direct callables).
- Prebind param name lists for kwargs assembly.
- Prebind creations target (owner/caller/spellspace) into step.
- Precompute register flags (skip for Existence.many without disposal methods).

### Allocation Strategy
- Preallocate list for instance results indexed by step id.
- Use array/list for kwargs when no overrides (convert once to dict if needed).
- Reuse scratch lists for dependency aggregation.

## Optional Optimizations
- Batch consecutive steps that share the same callable type.
- Use positional arg arrays for known signatures (skip kwargs).
- Use "no overrides" fast lane (zero dict merges).
- Pool Creation wrappers for many/unique registrations (optional).

## Fallback Strategy
If any gate fails or a step is unsupported, fall back to the Phase 8-10 executor.

## Open Questions
- How to represent instance results (dict vs index array).
- How to encode spellspace gating in step layout.
- Whether to allow any overrides in Phase 11 at all.

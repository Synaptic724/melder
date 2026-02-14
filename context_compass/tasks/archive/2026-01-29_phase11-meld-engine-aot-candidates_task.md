# Task: Identify conjure-time compilation candidates in MeldEngine

## Metadata
- Task ID: TASK-2026-01-29-phase11-meld-engine-aot-candidates
- Story: STORY-2026-01-29-phase11-conjure-fastpath
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Inspect meld runtime/engine responsibilities to determine which pieces can be
precompiled at conjure time for Phase 11 (or Phase 12) fast-path execution.

## Scope Boundaries
- In scope:
  - Review MeldEngine/MeldRuntime to catalog runtime work.
  - Identify candidate steps for prebinding or preallocation.
  - Map candidates to Phase 11 step model requirements.
- Out of scope:
  - Implementing any runtime or conjure changes.

## Steps / Checklist
- [x] Review MeldEngine/MeldRuntime execution flow for per-call work.
- [x] Identify precomputable inputs (kwargs wiring, creation targets, reuse flags).
- [x] Map candidates to Phase 11 step model fields and note gaps.

## Deliverables
- Evidence-backed list of conjure-time compilation candidates.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- context_compass/artifacts/README.md

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: candidate list omits hidden runtime responsibilities.
  Rollback: add follow-up investigation tasks for missing areas.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Findings Summary: Conjure-time (Phase 11) candidates
### Primary candidates already executed per call in MeldEngine
1) **Occurrence planning** (Phase 8 responsibilities)
   - Build occurrence graph, extend with ordered nodes, compute execution order,
     and instance plan (instance keys + canonical occurrences). These are pure
     DAG/topology computations and can be precompiled once per root blueprint.
   - Evidence: MeldEngine.run and delegated Phase 8 builder methods.

2) **Injection wiring** (Phase 9 responsibilities)
   - When an InjectionPlan exists, kwargs are built from injection specs and
     instance results without graph walking. This wiring can be precompiled
     per instance key in Phase 9 and represented as injection specs in Phase 11
     steps. (No new behavior—just frontloaded wiring.)
   - Evidence: build_kwargs_from_injection_spec usage in MeldEngine.run.

3) **Instance plan metadata**
   - Instance key mapping (shared vs per-path) and canonical occurrences already
     computed during plan building, suitable for Phase 11 step array metadata.
   - Evidence: _instance_key_for_occurrence / _occurrence_for_instance_key logic.

### Per-step execution metadata that can be prebound
4) **Creation target and reuse policy**
   - `_select_creations_for_spell` and existence policy (shared vs per-path)
     can be encoded into Phase 11 step metadata: creation_target (owner/caller/
     spellspace) and action (reuse vs construct). This removes per-step branch
     logic in the fast path.
   - Evidence: _select_creations_for_spell, _resolve_spell_instance.

5) **Registration policy**
   - Register flags derive from existence and disposal-method presence; these
     can be precomputed per step (e.g., Existence.many without disposal -> no
     register).
   - Evidence: _register_spell and disposal method guards.

6) **Callable prebinding**
   - `spell.spell` callables can be prebound into steps when stable, avoiding
     repeated attribute lookups.
   - Evidence: _construct_spell and _construct_root_only call patterns.

### Gate-related logic (should remain runtime gates, not compiled behavior)
- Overrides and contract payloads remain runtime gates for Phase 11 (no new
  behavior). `_detect_any_overrides` and contract override tracking indicate
  dynamic inputs that should disqualify fast path rather than be precompiled.
  - Evidence: _detect_any_overrides and _get_contract_override_payload_for_instance.

## Mapping to Phase 11 Step Model
| Phase 11 field | Source in MeldEngine | Notes |
| --- | --- | --- |
| spell_id | execution_order | Direct mapping from execution order |
| instance_key | instance plan | Derived from occurrence plan |
| existence | spell.existence | Used for reuse/register behavior |
| creation_target | _select_creations_for_spell | Encode owner/caller/spellspace |
| action (reuse/construct) | _resolve_spell_instance | Action precomputed per step |
| inject_spec | InjectionPlan | Precompiled in Phase 9 |
| register | _register_spell | Precomputed flag per existence |

## Evidence Anchors
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- context_compass/artifacts/README.md
- context_compass/artifacts/README.md

## Context / Handoff Summary
Phase 11 can frontload occurrence planning, injection wiring, and per-step
creation/registration metadata. Runtime should continue to gate overrides,
mutation overrides, validation, hooks, and spellspace status before selecting
the fast path.

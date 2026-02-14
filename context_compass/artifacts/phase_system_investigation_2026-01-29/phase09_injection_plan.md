# Phase 9 Investigation (Injection Plan)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase09-injection-plan-investigation

## Scope
Analyze injection plan compilation, root-only behavior, and runtime usage.

## Key Questions
- What inputs are required to build an injection plan?
- How does the injection plan map dependencies to parameters?
- How is the plan selected at runtime?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_injection_plan
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py: InjectionPlanBuilder.build
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py: InjectionPlan.select_for_runtime
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py: build_kwargs_from_injection_spec
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py: MeldEngine.run
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py: MeldEngine.run_execution_plan
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py: ExecutionPlanBuilder.build

## Findings
- Phase 9 requires Phase 5 root blueprint and a Phase 8 occurrence plan. If the spell is a root but root_blueprint is missing, it raises; otherwise non-root spells no-op.
- InjectionPlanBuilder converts the Phase 8 occurrence graph into per-instance InjectionSpec entries and ParamSource mappings.
- InjectionPlanBuilder uses shared instance keys for shared spells and uses the canonical occurrence when instance_key path is None.
- InjectionPlan.select_for_runtime returns None if the root id does not match or if the plan has been cleaned.
- ExecutionPlanBuilder uses InjectionPlan.select_for_runtime; if it returns None, it raises ValueError for root mismatch or a cleaned plan.
- build_kwargs_from_injection_spec is the runtime consumer: it builds kwargs from dependency instance results and contract payloads, and raises MeldExecutionError when a dependency instance is missing.

## Risks / Concerns
- Root-only injection plan compilation means non-root spells do not get injection plans.
- build_kwargs_from_injection_spec raises on missing dependency instance results, which can surface as meld-time failures if execution ordering or instance_keys are incorrect.

## Unknowns
- Whether injection plans should be generated for non-root spells (design decision).
- Whether contract payload handling should differ between plan time and runtime for dynamic linking.

## Next Steps
- Review how occurrence plans and injection plans behave when contracted providers are added/removed after plan compilation.

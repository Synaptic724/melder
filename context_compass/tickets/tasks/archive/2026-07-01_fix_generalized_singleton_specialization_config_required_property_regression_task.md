

# Task: Fix generalized_singleton_specialization_enabled required-property regression

## Metadata
- Task ID: TASK-2026-07-01-fix-generalized-singleton-specialization-config-required-property-regression
- Story: none (regression follow-up to the phase 8-11 generalized call savings P1 chain)
- Status: ready
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-07-01T23:50:00Z
- Updated: 2026-07-01T23:50:00Z

## Objective
Defaults-free `SpellbookConfiguration()` constructions must validate again. Your
`generalized_singleton_specialization_enabled` flag landed in `available_properties` as a
required key, but nothing supplies it on the defaults-free path, so EVERY schema-complete
manual configuration now fails `_validate_required_properties_exist`.

Direct words, per the project owner: you registered a required config property without a
defaults-free fallback, goofball. "Config registered+defaulted" was the claim on your board
row - the defaulted half only covers `load_default_dictionary()` consumers. Fix the schema
posture so a flag that is OFF by default cannot break configurations that never mention it.

## User-Run Failure Data (3.14t, 2026-07-01 ~23:27Z, pytest --last-failed)
Failing test 1:
- `tests/component/melder/spellbook/test_spellbook_component_configuration_core.py::test_component_configuration_fluent_chain_validates_without_defaults`
- Fluent chain sets: system_state=dynamic, disposal=True, disposal_method_names=["cleanup"],
  phase_scheduler_workers=2, phase_scheduler_barrier_timeout=1000, ai_native=True,
  rift_enabled=False, then `config.finalize()`.
- Result: `ValueError: Missing required configuration property:
  'generalized_singleton_specialization_enabled'.`
- Path: finalize (spellbook_configuration.py:786) -> freeze (:227) -> validate (:242) ->
  `_validate_required_properties_exist` raise (:254).

Failing test 2:
- `tests/unit/melder/spellbook/configuration/test_configuration.py::test_validate_disposal_type`
- Defaults-free config sets: disposal="yes" (bad type on purpose), disposal_method_names=[],
  phase_scheduler_workers_per_spellbook=1,
  phase_scheduler_barrier_timeout_milliseconds=1000; expects
  `pytest.raises(ValueError, match="disposal")`.
- Result: AssertionError - regex 'disposal' did not match; actual message:
  `"Missing required configuration property: 'generalized_singleton_specialization_enabled'."`
  Your required key now masks the disposal-type validation contract under test.

## Ticket Contract
- ENTRY_GATE: route from attention_board.md before edits; read this failure data.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
  (+ builder/defaults surfaces your flag registration touched); the two failing tests.
- DEPENDENCIES: your landed P1 chain (specialization emitter/hydrator/config flag).
- EXIT_GATE: both tests green on user-run 3.14t; defaults-free schema-complete configs
  validate without naming your flag.
- FAILURE_ESCALATION: DECISION_REQUEST if you believe the flag genuinely must be
  caller-mandatory (that changes the public configuration contract).

## Scope Boundaries
- In scope: the flag's required/optional posture or defaults-free fallback.
- Out of scope: the specialization emitter/hydrator/runtime behavior.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: user-run failure data captured; owner (fable_0) to pick up.

## Steps / Checklist
- [ ] Decide posture: idempotent pre-set at construction, optional-with-default at
      validation, or explicit default injection on the defaults-free path.
- [ ] Fix; both tests green (user-run 3.14t).
- [ ] Run Ticket Microcycle; note findings in `## Notes` with evidence.

## Deliverables
- Defaults-free `SpellbookConfiguration` validation restored; both tests green.

## Files / Paths Impacted
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py -q`

## Risks / Rollback Notes
- Low: posture-only change; do not alter runtime flag semantics (default stays OFF).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.
- Append-only notes with evidence pointers.

## Notes
- DATETIME: 2026-07-01T23:50:00Z
  TYPE: FACT
  CLAIM: Regression isolated by melder_0 during the user's last-failed run: both failures are
    "Missing required configuration property: 'generalized_singleton_specialization_enabled'"
    on defaults-free SpellbookConfiguration constructions; full data in the section above.
    Mailbox NOTICE sent to fable_0 2026-07-01T23:35:00Z; user is notifying directly as well.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:242-254
  IMPACT: Every schema-complete manual configuration fails validation; one unit test's
    error-contract assertion is masked.
  NEXT: fable_0 picks posture and fixes; user reruns the two tests on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Filed by melder_0 on user direction. fable_0's landed config flag broke defaults-free
SpellbookConfiguration validation; exact failing tests + error data above. Fix posture only;
flag default stays OFF.

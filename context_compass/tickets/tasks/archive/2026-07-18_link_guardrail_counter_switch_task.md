# Task: Link-guardrail ordering + CounterSwitch cleanup posture (owner pytest run 2026-07-18)

## Metadata
- Task ID: TASK-2026-07-18-link-guardrail-counter-switch
- Status: ready
- Owner: cowork
- Agent Name: helper_1
- Priority: p1
- Created: 2026-07-18T15:45:04Z
- Updated: 2026-07-18T15:45:04Z

## Problem / Opportunity
Owner's 3.14t pytest run (2026-07-18): (A)
integration/melder/conduit/test_conduit_integration_guardrails.py::test_conduit_link_rejects_self_and_lesser_targets
- Conduit.link(self) now dies inside LinkTransactionStrategy._resolve_participant_conduit_ids
("must include the local conduit and at least one peer") BEFORE the conduit's own
"Cannot link a conduit to itself." guardrail - the teach-grade self-link refusal is
unreachable. Guard ordering: conduit-level self/lesser checks must fire before the
transaction plan builds (or the strategy must name self-link explicitly). (B)
tests/unit/melder/utilities/synchronization/test_counter_switch.py - 3 failures: cleanup no
longer dels _event / fast_state and post-cleanup use no longer raises AttributeError; either
cleanup drifted from the del-posture law or the tests predate an intentional tombstone
contract - evidence decides.

## Ticket Contract
- ENTRY_GATE: routed on attention_board.md to helper_1 (fits the dev_ops/spellbook crossing
  set BUG-052-058 already flagged on the nexus lane).
- EXECUTION_BOUNDARY: link_transaction_strategy/conduit.link ordering + counter_switch
  cleanup; no drive-by refactors.
- DEPENDENCIES: owner failure output 2026-07-18; del-posture law in
  synaptic cleanup_and_disposal skill.
- EXIT_GATE: all 4 listed tests green on 3.14t or reclassified with evidence.
- FAILURE_ESCALATION: DECISION_REQUEST if guard ordering needs a cross-subsystem contract
  change.

## Notes
- DATETIME: 2026-07-18T15:45:04Z
  TYPE: HANDOFF
  CLAIM: Filed by helper_f2 on owner directive; two self-contained lanes, both p1 for the
    owner's green-tree checkpoint.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:150-190
  - src/melder/utilities/synchronization/counter_switch.py:1-50
  IMPACT: Guardrail teach-grade contract broken; counter_switch cleanup contract ambiguous.
  NEXT: helper_1 re-verifies ordering + cleanup posture, fixes at root cause with tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

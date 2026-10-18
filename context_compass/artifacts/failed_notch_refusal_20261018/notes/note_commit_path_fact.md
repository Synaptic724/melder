- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The commit path, re-read whole on 0.2.8255; melder_0's FACT note stands, with three precisions. (1) On
    `end_transaction(success=True)` the mediator runs the session's own commit pipeline (empty), then the strategy's
    commit delta (the notch strategy keeps the base one: fact stamps for the Book and every sealed conduit), then the
    orchestrator's commit: the CCM's structural validator - phases 1-4 for the index's now-active member when it has
    no Phase-4 result and no Phase-5 root blueprint; the CCM's general validator is never set - then its hooks, the
    dirty marker first. (2) When the validator raises, the orchestrator's abort hook (wired to the CCM dispatcher,
    whose own hook nothing sets) and the session's abort pipeline run - nothing in src/melder registers a session
    hook or rollback action - and `on_end` reopens the frozen gates: the seam's switch and the delta's fact stamps
    stay. (3) The validator checks the incoming version after the switch, while it is in `_spell_id_pool`; parked, it
    is not (the park pops it), and Phase 3 takes its candidates from a copy of that pool, so a check of the parked
    version before the switch would read another candidate set (SelfMade could not resolve to itself). The refusal
    has to undo the switch after the check and before the transaction ends, while the seal and gate freeze hold.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5650-5787
  - src/melder/aether/spellbook/spellbook.py:3856-4066
  - src/melder/aether/spellbook/spellbook.py:1500-1611
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:136-159
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-520
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:786-817
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1091
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:169-240
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:452-587
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:240-244
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:744-835
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-526
  - src/melder/aether/spellbook/spellbook_creation_system.py:1586-1654
  IMPACT: The mechanism is an undo inside the window, not a check before the switch; the patch docs say where it
    runs and what it reverses (the seam's steps, the journal entry, the record and Nexus rows).
  NEXT: Draft the architecture, component and code-description patches for the notch's commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

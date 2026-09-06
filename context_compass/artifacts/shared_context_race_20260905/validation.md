# Shared context rebuild race validation

Investigation: tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md, performed by workflows_1.
Lifecycle owner: tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md, assigned to codex_1.
Retain this report and controlled-window.json as core handoff evidence through epic acceptance.
The XML/passive trace outputs are disposable scratch; codex_1 adjudicates them at epic closure.
No commits, pushes, or uploads are authorized by this diagnostic handoff.

## Scope and constraints
Analysis only by owner instruction. No runtime or test files were edited, no lock was added,
and no object fields were monkeypatched. Historical lock-oriented documents were treated as leads,
not as proof of the correct repair. The owner requires the deque/ticket protocol to be understood.

## Existing checks
- 32 existing CounterSwitch, cleanup-contract, and creation-factory checks pass on Windows 3.14t,
  PYTHON_GIL=0: switch-contracts.xml.
- 20 independent invocations of the unchanged cluster test pass with PYTHON_GIL=0:
  cluster-attempt-1.xml through cluster-attempt-20.xml.
- 20 independent GIL-enabled diagnostic invocations also pass:
  gil-cluster-attempt-1.xml through gil-cluster-attempt-20.xml.
- 10 observer-traced invocations pass: trace-attempt-1.json through trace-attempt-10.json.
- The earlier duplicate-node invocation ran only one test. One malformed report argument ran zero
  tests. Neither is included in the forty independent-run count.

## Controlled reproduction before teardown
Data: controlled-window.json. Captured 2026-09-05T19:54:37Z on Windows 3.14t with the GIL disabled.
The runtime/test files involved match hosted job commit a116ec22cd89cc148c719847ac83662078cd87e6
according to a direct Git comparison with local HEAD.

The existing test and original methods ran under debugger trace hooks. The hooks only paused
threads and read state; they did not replace methods, clear fields, alter tickets, or inject errors.

Reproduction sequence:
1. In the existing cluster-a owner worker, pause ConduitMeld.meld immediately before line 371,
   the current-context readiness read. Identify this worker from _run_concurrent_melds' tasks.
2. Let its existing cluster-a peer run normal local phase revalidation. Pause compiler_phase_5's
   run_local on return, after its original cleanup/reset and before phase 11 can publish.
3. Let both unrelated cluster-b workers finish, so they are not interrupted during cache emission.
4. Resume the owner while the phase-5 worker remains paused.
5. Capture CreationContextBuilder.build's original RuntimeError, then stop the diagnostic child
   before the test's finally/terminal cleanup executes.

| Observation | Context | Codegen input | CounterSwitch |
| --- | --- | --- | --- |
| Owner before context read | Present | Absent (cached context is available) | 2 / ready |
| Peer after phase 5, before phase 11 | Absent | Absent | 0 / idle |
| Owner's original builder exception | Absent | Absent | 1 / leader claimed |

At the original exception, all of these flags were False:
- cluster_a_owner._cleaned
- cluster_a_peer._cleaned
- cluster_b_owner._cleaned
- cluster_b_peer._cleaned
- target Spell._cleaned
- SpellCompilerArtifact container._cleaned
- CounterSwitch._cleaned

The original exception text was:
`Cannot build CreationContext before spell_codegen_creation exists. Run analyzer -> processor -> planner -> codegen creation first.`

The child deliberately stopped at this exception (requested diagnostic status 42; the PowerShell
wrapper reported nonzero). This is a controlled-interleaving reproduction, not a completed passing
test run or a measurement of how frequently the hosted runner hits it.

## What the evidence establishes
- The exact missing-input error can occur before terminal object cleanup, with the original CI
  runtime/test code. The displayed cleaned Conduit repr is not needed to cause this failure.
- Phase-5 invalidation retires the old payload/context but leaves their owning objects alive.
- CounterSwitch correctly grants leadership from state 0. The caller made that state visible while
  the replacement compiled input was not ready. The mismatch is at the reset/rebuild/publication
  boundary; the reproduction does not demonstrate a broken deque or duplicate leader election.
- The test's normal cleanup runs after every worker is joined and the collected errors are asserted.
  It is therefore later than the original worker exception in this path.
- These results do not establish that an additional lock is required, and no repair was selected.

## Remaining design questions
- What should prevent a context build while its phase inputs are being replaced: lifecycle gating,
  phase-owned publication, or another protocol consistent with existing fast-path constraints?
- How should a selected builder's exception release/abort pending followers? The captured latch is
  still 1 at the exception; the controlled child was stopped before subsequent recovery was observed.
- The full hosted history may have other failure paths. This proof establishes one valid interleaving
  producing the exact error, not a claim that every similar message has the same cause.

## Source evidence
- CounterSwitch state/election: src/melder/utilities/synchronization/counter_switch.py:255-341.
- Phase reset: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-692.
- Live latch reset: src/melder/aether/spellbook/spell.py:660-686.
- Builder election/publication: src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339.
- Missing-input refusal: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:103-146.
- Later payload publication: src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:61-128.
- Test join/assert: tests/integration/melder/conduit/test_conduit_integration_concurrency.py:344-351.
- Test teardown: tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1007-1015.

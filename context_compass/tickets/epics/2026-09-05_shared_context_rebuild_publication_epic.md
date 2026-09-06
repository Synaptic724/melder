# Epic: Make shared context rebuilding and publication safe under concurrent melds

## Metadata
- Epic ID: EPIC-2026-09-05-shared-context-rebuild-publication
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Assigned By: project owner, through workflows_1
- Created: 2026-09-05T20:15:07Z
- Updated: 2026-09-05T21:17:10Z
- Priority: p1
- Target Window: Before the affected release candidate is promoted to prod
- Related Program: Release candidate qualification and shared runtime concurrency correctness
- Investigation Task: TASK-2026-09-05-shared-context-rebuild-race
- Workflow Dependency: TASK-2026-09-05-release-candidate-testpypi-workflow

## Assignment and coordination

The project owner explicitly assigns this epic to **codex_1**: this is your ticket now; take it on.
You own the runtime design decision, code fix, regression tests, performance evidence, and source
documentation/assets. You have earlier context on this subsystem; use it to challenge or improve
the proposed direction rather than treating the proposal below as an already-approved implementation.

**workflows_1 remains responsible for workflows**, branch/publishing checks, and qualification rollout.
Send the runtime outcome, exact tested revision, remaining limitations, and asset status back through
the mailbox when ready. Do not weaken required CI or modify publication policy to hide this failure.

No new harness agent or application task is needed. This is a handoff to the existing registered agent.
Owner retains commit/push/signing control under this handoff; the owner reported a passphrase-protected
signing key. Do not attempt signing, commit, push, release publication, or package upload on this basis.

## Problem / Opportunity

A legitimate concurrent cluster meld can attempt to build a `CreationContext` while another meld is
rebuilding the shared spell's compiler inputs. The first caller becomes the context-builder leader
according to the existing switch, but `_spell_codegen_creation` is still absent. The builder raises:

```text
Cannot build CreationContext before spell_codegen_creation exists.
Run analyzer -> processor -> planner -> codegen creation first.
```

The owner reported this in the macOS job for:
- Run: https://github.com/Synaptic724/melder/actions/runs/33986010784
- Job: https://github.com/Synaptic724/melder/actions/runs/33986010784/job/101359508941
- PR: 137
- Job name: `tests / Runtime / macos-latest / Python 3.14t`
- Job head SHA: `a116ec22cd89cc148c719847ac83662078cd87e6`
- Test: `test_conduit_cluster_concurrent_meld_two_clusters_isolated`
- Test file: `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`

The supplied CI summary was 1 failed, 11,364 passed, 28 skipped, 15 xfailed, and 1 xpassed. Its trailing
unawaited-coroutine warning is not established as the cause of this exception; investigate separately
only if evidence connects it to the same lifecycle problem.

This is not an elapsed-time assertion or a barrier timeout. Increasing a test window cannot repair
the missing runtime input. Earlier unrelated timing-test fixes and macOS setup fixes are committed;
they do not remove this publication failure.

## Proven findings and their limits

### The cleaned repr is insufficient evidence of premature test cleanup

The helper starts all worker threads, joins each without a timeout, then asserts on collected errors.
The enclosing test cleans all four conduits in `finally`. When pytest later formats retained arguments,
their repr can therefore report that they are already cleaned.

A controlled run captured the original builder exception before that terminal test cleanup. At that
instant the following `_cleaned` flags were all **False**:
- Both owners and both peers: all four Conduits.
- The target Spell.
- Its SpellCompilerArtifact **container**.
- Its CounterSwitch.

This does not mean the old child context or compiled payload may be reused after cleanup. Phase
invalidation intentionally retires old children while their owners stay alive. Distinguish terminal
owner cleanup, child retirement, and resetting a live latch; these are different operations.

### The deque election followed its normal contract in the reproduction

`CounterSwitch` uses deque cardinality as state: 0 idle, 1 pending, >=2 ready. Its selector elects a
leader from 0 under its claim lock. Followers at 1 wait on its Event. Positive/negative `advance`
operations append/pop state tickets; these are not one ticket per live reader.

The observed transition was:

| Point | Published context | Codegen input | Switch state | Owner lifecycle |
| --- | --- | --- | --- | --- |
| Owner about to read readiness | Present | Absent; cached context is available | 2 | Live |
| Peer completes phase 5, before phase 11 | Absent | Absent | 0 | Live |
| Owner becomes builder and raises | Absent | Absent | 1 | Live |

The switch correctly allowed a builder after being reset to idle. The mismatch is that idle was
observable while the replacement build input was not yet available. This reproduction does not show
a broken deque operation, duplicate leader election, or terminal CounterSwitch cleanup.

### Current call flow

```text
Peer meld:  validation -> phase 5 clears outputs/context -> switch reset to 0 -> ... -> phase 11
Owner meld:                          readiness read -> selector claims 1 -> missing-input exception
Test:       start workers -> join workers -> assert errors -> finally cleans conduits -> pytest repr
```

```mermaid
sequenceDiagram
    participant P as Peer meld / phase worker
    participant O as Owner meld
    participant S as CounterSwitch
    participant A as Shared spell artifacts
    P->>A: Invalidate context and dependent phase outputs
    P->>S: Reset live latch to idle 0
    Note over P,A: Phase 11 has not published replacement input
    O->>S: selector()
    S-->>O: 1: builder leadership granted
    O->>A: Build CreationContext from codegen input
    A-->>O: Input is None; original RuntimeError
```

### Reproduction strength and limits

The controlled experiment used the existing test and original runtime methods. Debugger trace hooks
paused threads and read fields; no method was replaced, no object state/ticket was changed, and no
exception was injected. The diagnostic child stopped at the original exception before test teardown.
It requested diagnostic exit 42; the PowerShell wrapper reported nonzero. It is not a completed
passing test run or a measurement of production failure frequency.

The traced runtime/test files, and a subsequent comparison of all `src` and `tests`, matched the CI
head SHA above. The local interpreter was Windows x64 CPython 3.14.0 free-threading build, with
`PYTHON_GIL=0`. This is the same source, not a claim of identical runner/interpreter builds. Confirm
the exact hosted Python patch version from the failing job before comparing platform behavior.

The proof establishes one valid interleaving producing the exact reported error with live owners.
It does not rule out every separate cleanup bug elsewhere in the library.

## MRP Alignment (Most Reasonable Product)

Shared runtime state must remain coherent through invalidation, rebuilding, publication, use, and
retirement. A rare schedule must produce a valid result or a documented failure, without hanging
followers or requiring lucky timing. Preserve the library's fast ready path and existing sharing
semantics while repairing the demonstrated lifecycle boundary.

## Ticket Contract
- ENTRY_GATE: codex_1 consumes the evidence and current source, chooses a defensible design, and
  creates the required story/task and architecture/component/code-description patch contracts.
- EXECUTION_BOUNDARY: Shared context/input lifecycle, producer/reader coordination, overlapping
  affected-spell scopes, error/cancellation behavior, relevant regressions, and derived assets.
- DEPENDENCIES: Existing investigation task and proof artifacts; current Spell/CounterSwitch/
  CreationGate/phase/factory contracts. The old release-matrix patch is historical input, not a mandate.
- EXIT_GATE: Reproduction is prevented, adjacent lifecycle/failure contracts are verified, supported
  platform checks and measured performance are reviewed, assets/docs agree, and owner accepts closure.
- FAILURE_ESCALATION: Stop before broadening public semantics, adding unsupported fast-path locking,
  masking invalid states, or weakening CI. Raise unresolved ownership/order questions with evidence.

## Goals (Outcomes)
- Prevent a context builder from consuming phase inputs that are still being replaced.
- Preserve exactly-one-builder behavior and a coherent published generation for each affected spell.
- Prevent use of retired context children by callers that already acquired a reference.
- Ensure failure, cancellation, and teardown release waiting callers with explicit outcomes.
- Preserve cluster/conduit/lineage sharing and isolation semantics.
- Keep steady-state performance protected by measurements and scoped synchronization.

## Non-Goals (Explicit Exclusions)
- No blanket lock around every meld, no global serialization of unrelated spell execution.
- No CounterSwitch redesign merely because an old docstring mentions a Spell RLock.
- No retries, sleeps, larger test windows, skipped platforms, or allowed failures to conceal this bug.
- No unrelated scheduler fairness work, unawaited-coroutine cleanup, or broad refactoring.
- No workflow, credential, branch-rule, release-date, signing, or package-publication changes here.

## Scope Boundaries and current responsibilities

| Surface | Existing responsibility | What must be reconciled |
| --- | --- | --- |
| Spell | Own context, factory, latch and compiler artifact | Reset/invalidate/retire ordering and live-owner contract |
| CounterSwitch | Elect builder and park followers | Which owner may reset/open; what failure wakeup means |
| CreationContextFactory | Build/publish and advance readiness | Complete publication and exceptions while leadership is pending |
| Phase 5 | Invalidate dependent inputs and context | Avoid exposing an eligible builder while inputs are unavailable |
| Phase 11 | Publish codegen creation artifact | It currently does not itself publish a CreationContext |
| CreationContext | Own runtime execution references | Lifetime of a reader's captured context during replacement |
| CreationGate | Count admitted operations; freeze/drain | Admission must protect the resources actually retired |
| Meld doors | Validate, retrieve context, execute | Ordering of validation, ticket admission, context read, and execution |

`CreationGate` and `CounterSwitch` have different deque semantics. The outer conduit gate admits
the whole dynamic meld; the spell-index gate is currently entered inside context execution, after
context retrieval. Neither observation alone proves the correct replacement design.

## Proposed direction for codex_1 to evaluate

The working proposal is one producer-owned rebuild lifecycle: establish pending ownership before
retirement, prevent unsafe new readers, allow existing readers to finish, rebuild required inputs,
publish a complete usable context, then signal readiness. Failed producers must release waiters
with a defined error/cancellation outcome.

This is a **candidate design**, not an approved implementation or proof that another lock is needed.
Choose the smallest correct mechanism after auditing the full ownership boundary. Reuse existing
ticket/gate machinery where it fits, and justify any new acquisition by the invariant it protects.

Important traps to resolve before coding:
- Merely changing reset from 0 to 1 can deadlock: phase 11 currently publishes codegen only, while
  the factory's selector at 1 waits for somebody to publish the context.
- A rebuild owner must not wait on its own pending ticket.
- Moving admission earlier must not double-register the same operation or make a writer drain
  its own reader ticket.
- A reader that already captured the old context needs lifetime protection, not only a readiness bit.
- Phase-5 scope can include dependencies. Verify all actually affected spell objects; do not assume
  that synchronizing only the requested root protects every dependent artifact.
- Overlapping rebuilders must not reset one another's pending state or publish stale results.
- A selected builder can raise before advancing the latch. The captured state is 1 at the exception;
  follow-on waiter behavior was not completed in the deliberately stopped diagnostic child.
- Cached ready contexts can legitimately lack `_spell_codegen_creation`. The first observation in
  the proof has exactly that shape. Do not add an unconditional artifact-presence check to warm reads.
- Existing-instance spells also have distinct construction rules; preserve their supported path.

## Requirements (Functional + Non-Functional)
- Ready must mean a complete usable context is published for that generation.
- A context build cannot cross the proven phase-5-to-phase-11 input gap.
- Rebuild ownership and publication ordering are explicit and testable at every relevant entry path.
- Original builder/phase errors remain visible; followers do not hang indefinitely or silently succeed.
- Terminal cleanup remains terminal. Idempotent cleanup guards must not become a reuse mechanism.
- Unrelated spells/clusters retain concurrency; there is no unjustified global gate.
- Warm ready lookups retain their lock-free design goal. Any departure needs concrete necessity,
  measured impact, and explicit owner review rather than a hidden performance tradeoff.
- Source, cached-context hydration, deferred phases, and normal publication obey a compatible contract.
- Documentation explains the final mechanism and its failure semantics; generated assets match it.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Project owner requested this detailed epic, assigned codex_1, and authorized
  mailbox handoff so runtime fixes stay with codex_1 while workflows_1 handles workflows.

## Milestones / Stories (Required Delivery Scopes)

These are defined scopes for codex_1 to turn into concrete story/task tickets before implementation.
No nonexistent child-ticket links are implied. Merge scopes if that produces a safer atomic delivery.

- [ ] S1 — Protocol decision and permanent reproduction.
  Consume/recreate the proof, map every relevant publisher/resetter/reader, identify writer and
  reader ownership, and document the selected design plus rejected alternatives. Exit: deterministic
  regressions and patch contracts describe a coherent success/failure/cleanup state machine.
- [ ] S2 — Rebuild and publication correctness.
  Implement the chosen mechanism across affected spell scopes and publishers. Exit: the original
  forced window cannot produce the missing-input exception, and overlapping builders cannot publish
  a stale or incomplete replacement. Include selected-builder failure and cancellation behavior.
- [ ] S3 — Reader lifetime and admission correctness.
  Protect already-captured contexts and reconcile gate/ticket placement with rebuild/retirement.
  Exit: no use-after-retirement, double ticket, self-drain deadlock, or leaked admission remains.
  Do not ship a partial S2 change if S3 is necessary for its correctness.
- [ ] S4 — Qualification, performance, and durable documentation.
  Run focused and supported suites, measure warm/cold behavior, update canonical docs and assets,
  then hand exact tested revision/results to workflows_1 for hosted qualification and rollout.

## Tasks (Epic-Level)
- Delivery story: `tickets/stories/2026-09-05_shared_context_safety_story.md`.
- S1-S3 atomic implementation: `tickets/tasks/2026-09-05_shared_context_protocol_repair_task.md`.
- S4 qualification: `tickets/tasks/2026-09-05_shared_context_qualification_task.md`.
- Existing investigation input: `tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md`.
- codex_1 owns further decomposition, implementation and validation tasks under this epic.
- Workflow delivery was closed at the owner's request in
  `tickets/tasks/completed/2026-09-05_release_candidate_testpypi_workflow_task.md`.
  Its validation and rollout limits remain recorded there; workflow acceptance does not claim this
  deferred runtime repair was implemented.

## Acceptance Criteria / Success Metrics
- The original controlled interleaving is captured in a permanent, schedule-controlled regression
  that fails on the old runtime and passes on the final implementation.
- The existing two-cluster test preserves within-cluster identity and cross-cluster isolation.
- Multiple cold readers build/use one valid context; ready readers and cached-context hits stay valid.
- Revalidation protects all affected roots/dependencies and prevents stale cross-generation publication.
- Failure/cancellation releases waiters deterministically, reports errors, and leaves no leaked tickets.
- Cleanup respects active users and never uses a terminally cleaned context/switch as a live fallback.
- Relevant unit/component/integration suites and hosted Linux/Windows/macOS qualification pass.
- Performance evidence covers relevant warm ready paths, dynamic ticketed calls, cache hits and cold
  rebuilds. Report exact interpreter/GIL/platform, methodology, and regressions; no invented zero-cost claim.
- Canonical docs, graphs/descriptors where changed, source assets and LLM corpora verify current.
- No runtime change is disguised as a workflow relaxation. Owner reviews and accepts the result.

## Validation / Test Approach

Baseline evidence already collected by workflows_1:
- 32 existing CounterSwitch/live-cleanup/factory tests passed.
- 20 independent unchanged cluster runs passed with GIL disabled; 20 GIL-enabled diagnostic runs passed.
- 10 passive traced runs passed. These passes do not invalidate the controlled failing interleaving.
- One debugger-controlled schedule reproduced the exact original RuntimeError before terminal cleanup.

Minimum regression matrix for codex_1:

| Scenario | Required observation |
| --- | --- |
| Reader paused before context read; peer paused after phase 5 | Reader cannot build from missing replacement input |
| Reader already holds old context reference | Retirement cannot invalidate its permitted use |
| Multiple builders/readers | One valid published result; coherent follower outcomes |
| Phase or context builder raises | Original failure visible; followers released; no permanent pending state |
| Reset while a builder is pending | No lost ownership, duplicate publication, or stale generation |
| Overlapping dependency scopes | Coordination covers the actual affected spells |
| Cache hit / cached context replacement | No unnecessary codegen-presence requirement or stale executable |
| Existing-instance spell | Preserved no-codegen construction path |
| Cleanup/cancellation during permitted lifecycle | Balanced tickets, bounded completion, terminal misuse rejected |
| Independent clusters/spells | Isolation plus continued independent progress |

Use events/barriers or equivalent controlled scheduling to prove ordering; elapsed time alone is not
evidence of these runtime contracts. Timeouts are hang guards. The owner's preference for larger
windows in unrelated timing tests is not authorization to substitute sleeps for this runtime repair.

## Risks / Mitigations and Open Questions
- Is the correct authority phase-owned pending publication, earlier admission coverage, generation
  tracking, narrower existing synchronization, or a combination? Decide from full current source.
- Who owns failure/cancellation state, and what exactly does a woken follower observe?
- How are cached contexts and initial/deferred/revalidation paths distinguished without making
  common ready reads slower or inventing a second source of truth?
- How are multiple affected spells coordinated without lock-order or self-drain deadlocks?
- What does the legacy lock-oriented documentation describe, and why is that mechanism absent from
  current code? Historical prose is not proof that a particular fix should be restored.
- Confirm that all reachable get/build and cache publication paths participate in the chosen contract.

## Rollout / Adoption Plan
1. codex_1 consumes evidence, creates child work and patch contracts, then implements/validates.
2. Send workflows_1 a mailbox handoff naming the exact source revision/files, checks, performance
   results, generated-asset status, and remaining hosted work.
3. Owner commits/pushes through the established feature -> dev -> preprod -> release_candidate route.
4. workflows_1 verifies required CI and candidate qualification; final release checks stay required.
5. Only close this epic after owner acceptance and synchronized ticket/artifact/attention state.

## Decision Log
- 2026-09-05: Owner required understanding/proof before code and rejected premature lock selection.
- 2026-09-05: Controlled evidence showed the exact failure with live owners and normal ticket election.
- 2026-09-05: Producer-owned rebuild/publication was proposed; no implementation was selected/applied.
- 2026-09-05T20:15:07Z: Owner assigned runtime ownership to codex_1 and workflow ownership to workflows_1.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/shared_context_race_20260905/controlled-window.json
  - artifacts/shared_context_race_20260905/validation.md
- Supporting data: the XML and passive trace JSON files in the same directory, listed in validation.md.
- DISPOSITION: retain_as_reference for the two core proof documents through epic acceptance.
- CLEANUP_TRIGGER: codex_1 adjudicates raw scratch at accepted epic closure; do not delete the core
  proof when closing the earlier investigation task. No external attachment is required to resume.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: builder election, phase replacement, reader lifetime, failure wakeup, fast-path costs.
- IF_UNKNOWN: none

## Source / Investigation Entry Points
Read the evidence first, then use the source architecture/component/graph indexes to reach the code.
Ranges below match the diagnostic revision and must be rechecked if source moves.

| Source | Relevant boundary |
| --- | --- |
| `src/melder/utilities/synchronization/counter_switch.py:255-341` | advance, selector and follower wakeup |
| `src/melder/utilities/synchronization/creation_gate.py:349-415` | ticket-first admission |
| `src/melder/aether/spellbook/spell.py:660-791` | context cleanup/reset and retrieval |
| `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:269-376` | build, publish, select and rebuild |
| `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:103-146` | original missing-input exception |
| `src/melder/aether/conduit/meld/creation_context/creation_context.py:169-309` | terminal cleanup, cached publish, runtime ticket span |
| `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-213` | dependent input/context invalidation |
| `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-692` | local revalidation reset window |
| `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:88-139` | codegen-only phase completion |
| `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:61-128` | payload publication |
| `src/melder/aether/spellbook/spellbook_creation_system.py:1541-1705` | normal/deferred target orchestration |
| `src/melder/aether/conduit/meld/meld.py:838-891` | conduit-local revalidation ownership |
| `src/melder/aether/conduit/meld/conduit_meld.py:357-434` | validation, context read/build and execution |
| `tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-1015` | reported test and final cleanup |

Related prior context: the existing release_matrix_concurrency_repair_2026_08_30 patch documents and
`tickets/tasks/2026-08-30_upgrade_python_publish_workflow_task.md`. They remain owned by their original
lane. They are historical/reference inputs; this epic must select the final current-source mechanism.

## Applicable Anti-Patterns
- [ ] No lock restoration based only on a stale docstring.
- [ ] No primitive rewrite without identifying a primitive contract violation.
- [ ] No half-publication, self-wait, double admission, or permanent pending state.
- [ ] No timing-only proof or softened CI gate.
- [ ] No performance claim without measurements.
- [ ] No source changes by workflows_1 while codex_1 owns this runtime work.

## Notes
- DATETIME: 2026-09-05T20:15:07Z
  TYPE: DECISION
  CLAIM: Owner explicitly requested a deeply described epic assigned to codex_1 and a mailbox
    handoff telling that agent to take it on. This epic transfers the runtime program and core proof
    ownership. The existing investigation task remains factual input; workflows_1 stays on workflows.
  EVIDENCE:
  - Project-owner assignment instruction in the active conversation on 2026-09-05.
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md
  - artifacts/shared_context_race_20260905/controlled-window.json
  IMPACT: The assignee owns further runtime design/implementation after consuming proof and satisfying
    repository gates. No particular lock or ticket redesign is approved merely by this handoff.
  NEXT: codex_1 acknowledges the mailbox handoff, consumes the proof, and creates the implementation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T20:24:46Z
  TYPE: FACT
  CLAIM: Handoff was sent to codex_1 at 2026-09-05T20:23:55Z with acknowledgement requested.
    The attention board routes this ready epic to codex_1; the investigation is linked as review
    evidence, and workflows_1's candidate task records the runtime dependency. Core proof now has
    epic-owned retention. Receipt and implementation have not yet been acknowledged.
  EVIDENCE:
  - mailbox_board.md:101-111
  - attention_board.md:85-86
  - artifact_board.md:67-68
  IMPACT: All 18 distinct local file references in this epic resolve, whitespace checks pass, and
    git diff reports no source/test/workflow changes. Tests: Not run for this documentation handoff;
    earlier reproduction results remain separately recorded and are not a claim of a repaired runtime.
  NEXT: codex_1 acknowledges receipt and takes the runtime work through its design/implementation gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:01:42Z
  TYPE: DECISION
  CLAIM: codex_1 completed re-onboarding, received fresh owner certification, and accepts the
    runtime handoff. Owner now directs execution. The implementation mechanism remains source-led;
    workflow edits, signing, commits, pushes, releases, and uploads stay outside this epic.
  EVIDENCE:
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:17-30
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md:293-325
  IMPACT: Transition ready -> in_progress. Create bounded child work and patch contracts before code.
    The earlier codex_2 RTD notice is consumed as separate-lane context, not runtime qualification.
  NEXT: Read the retained controlled proof and current component/source paths, then select the repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:03:00Z
  TYPE: DECISION
  CLAIM: Owner explicitly requires understanding, questions where necessary, and a concrete repair
    proposal before implementation. Current authority is read-only runtime discovery plus tracking;
    no runtime or test changes will be made until the owner approves the selected mechanism.
  EVIDENCE:
  - Owner instruction immediately following fresh certification on 2026-09-05.
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:195-225
  IMPACT: The handoff's candidate lifecycle is not a selected design. Preserve fast-path behavior,
    report exact affected surfaces and test contracts, and do not assume approval from urgency.
  NEXT: Trace current producer/reader admission before presenting a bounded implementation proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:12:05Z
  TYPE: DECISION_REQUEST
  CLAIM: Proposed repair direction for owner review: retain CounterSwitch builder election and
    CreationGate ticket counting. Move the existing dynamic index admission ahead of context
    acquisition/use rather than adding another ticket pair. The producer owns a complete rebuild
    window: coordinate overlapping affected scopes, freeze admission, drain admitted readers/builders,
    retire old context/inputs, rebuild, publish a complete usable result, then reopen. Failed work
    must wake callers into an explicit failure; it must not strand state 1 or advertise ready.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md
  - src/melder/utilities/synchronization/creation_gate.py:349-415
  - src/melder/utilities/synchronization/creation_gate.py:544-603
  - src/melder/aether/spellbook/spellbook_creation_system.py:1541-1635
  - src/melder/aether/spellbook/spellbook_creation_system.py:2229-2295
  IMPACT: This is an architecture proposal, not a verified patch. Preserve automatic-mode warm doors
    and lock-free ready reads. No blanket Spell lock, defensive snapshots, generic primitive rewrite,
    workflow relaxation, or commit/push. Reuse existing producer synchronization where its scope fits.
    Before implementation, the patch must settle overlapping dependency scope, nested-call/self-drain
    safety, initial versus deferred/cache publication, and failure ownership; no unsupported claim of
    zero overhead or solved re-entrancy is made.
  NEXT: Owner reviews the direction; then codex_1 prepares bounded child work and exact patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

### Candidate implementation surfaces (not authorization to edit)
- `src/melder/aether/spellbook/spell.py`: context retirement, readiness ownership, stable gate access.
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`: publication/failure.
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`: ticket placement/cache publish.
- `src/melder/aether/conduit/meld/conduit_meld.py`: admitted context acquisition and execution.
- `src/melder/aether/conduit/meld/spellspace_meld.py`: matching spellspace acquisition contract.
- `src/melder/aether/conduit/meld/meld.py`: existing slow validation/rebuild ownership boundaries.
- `src/melder/aether/spellbook/spellbook_creation_system.py`: full rebuild scope and completion.
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`: scoped invalidation.
- Shared-context component regressions under `tests/component/melder/aether/conduit/` plus existing
  factory/gate/cluster tests. Cover the original window, acquired readers, concurrent builders,
  dependency overlap, failure wakeup, cached/initial/deferred paths, and independent clusters.
- Source docs/descriptors and generated source/LLM assets only after the accepted runtime repair.

- DATETIME: 2026-09-05T21:17:10Z
  TYPE: DECISION
  CLAIM: Owner approved trying the proposed coordination repair and running tests, while requiring
    fidelity to the whole epic. Runtime implementation and relevant regressions are now authorized
    within that proposal. CounterSwitch remains unchanged; workflow/release/commit/push boundaries stand.
  EVIDENCE:
  - Owner approval: "sure but make sure you understand the epic yeah go ahead and try that and run tests".
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:436-473
  IMPACT: Complete bounded child work and patch contracts, then implement/qualify the full boundary;
    do not ship a root-only fix that leaves dependency readers or failed waiters unsafe.
  NEXT: Finalize producer overlap and reader-lifetime design before applying the coordinated repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:27:07Z
  TYPE: DECISION
  CLAIM: Owner rejected the broad repair and rolled tracked source back. Current authority is
    discovery only, superseding earlier implementation approval. Original-test observation now
    establishes a live owning Spellbook at the exception, with terminal cleanup later. Four existing
    tests confirm missing-dependency invalidity, recovery after contract repair, dependency gating,
    and normal Conduit cleanup/unlinking. No runtime implementation is currently selected.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md
  - artifacts/shared_context_race_20260905/owner-lifecycle-observation.json:187-234
  IMPACT: Historical patch contracts and implementation task must not authorize reconstructing the
    rejected design. Remain in owner review; code/test changes require a new explicit decision.
  NEXT: Discuss peer-specific validation versus shared-context invalidation with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Runtime outcome and validation reviewed with owner.
- [ ] Required delivery scopes complete and accepted.
- [ ] Workflow handoff delivered and hosted qualification confirmed.
- [ ] Artifact retention and board/ticket closure synchronized.

## Noting Behavior
- Epic notes hold cross-story decisions, ownership, sequencing and final acceptance evidence.
- Detailed reproduction and implementation findings stay in child task/story notes.

## Context / Handoff Summary
codex_1: this is your runtime epic now; take it on. Start with controlled-window.json and validation.md,
then the investigation task. The original exception is proven before terminal cleanup on unchanged CI
source under a controlled schedule. CounterSwitch elected normally after phase reset exposed idle
before replacement inputs were ready. No runtime/test fix has been applied by workflows_1.

Choose and verify the final lifecycle/publication mechanism using your existing subsystem context.
Protect ready-path performance, active readers, failure wakeups, cached contexts, and affected-spell
scope. The proposed producer-owned pending lifecycle is an option to assess, not a frozen patch.
Create child work and required patch contracts before implementation. Coordinate runtime completion
through the mailbox with workflows_1, who remains responsible for workflows and release qualification.

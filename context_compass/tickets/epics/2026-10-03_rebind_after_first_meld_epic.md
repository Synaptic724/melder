# Epic: Restore ordinary meld after removing and rebinding an already-used definition

## Metadata
- Epic ID: EPIC-2026-10-03-rebind_after_first_meld
- Status: in_progress
- Owner: project owner; receiving Melder maintainer to be assigned
- Agent Name: command_0 (report author), fable_1 (receiving maintainer, 2026-10-03)
- Priority: p1
- Created: 2026-10-03T19:07:45.991467+00:00
- Updated: 2026-10-03T21:08:00Z
- Target Window: next owner-selected Melder correctness investigation
- Related Program/Initiative: MelderOps dynamic Actions factory integration
- Origin: priv_commandops / Actions native factory migration
- Last tested distribution: Melder 0.2.8215 in priv_commandops/.venv314
- Last saved retest: 2026-10-03T13:55:44Z receipt; 5 tests, 2 passed, 3 failed
- Current source/wheel status: REPRODUCED on 0.2.8216 and 0.2.8218 source (2 failed / 2 passed), REPAIRED at
  0.2.8219 (source landed 2026-10-03 by fable_1; work package C on the delivered build is the owner's)

## Problem / Opportunity

The observed sequence is **bind -> meld -> withdraw sharing permission if present ->
cleanup_spell -> bind the same class/address -> meld**. The first meld succeeds. After
removal and replacement, the second ordinary meld fails before returning a new object:

```text
RuntimeError: Cannot build CreationContext before spell_codegen_creation exists.
Run analyzer -> processor -> planner -> codegen creation first.
```

The three failures are two variants of a small native-operation probe and one real Actions
integration test. They are evidence of the same operation-prefix failure, not proof of three
independent defects. Two controls that remove/rebind before any first meld pass.

The user calls the removal step `unregister`. The MelderOps method is
`Actions.unregister_action`; the isolated native equivalent withdraws the exact peer contract
entry when linked, then calls `root.cleanup_spell(spell=definition)`. This is not `purge`.
The preexisting product deliberately remains usable after its definition is removed; it is
still owned by the scope that created it. Rebinding should allow creation of another product.

## Earlier Epic: Related Error Message, Different Operation

[The injected-dependency direct-resolution epic](completed/2026-09-30_injected_dependency_direct_resolution_epic.md)
was completed with the 0.2.8215 repair and subsequently accepted by MelderOps. That sequence was
consumer meld -> successful dependency injection -> direct meld of the injected provider.
It contained no removal/rebind between those melds.

This rebind sequence was already documented in the MelderOps Actions story and native finding,
but no dedicated Melder rebind epic was found. This handoff does not reopen the completed epic
or claim that its implementation caused this failure. A shared exception message is not enough
to identify a shared cause.

## MRP Alignment (Most Reasonable Product)

Dynamic registration is a normal Melder lifecycle operation. A consuming facade must be able to
remove a definition and replace it while previously dispensed products retain their intended
scope lifetime. Melder owns whatever compilation/readiness work an ordinary subsequent meld
requires. Application callers should not need private cache edits or undocumented recompilation.

## Ticket Contract
- ENTRY_GATE: Owner requested this epic and evidence handoff. Receiving maintainer first compares
  the saved installed build with the current source/wheel and reproduces using fresh native state.
- EXECUTION_BOUNDARY: Definition removal and same-reference/address rebind after first creation;
  native resolution readiness, compiler artifacts, context publication and focused regressions.
- DEPENDENCIES: Copied probe/results, singleton-isolation fixture, relevant native APIs, and an
  owner-selected maintainer before source repair begins.
- EXIT_GATE: The unchanged four native cases and real Actions replacement case pass against the
  delivered build; old-product lifetime and contract withdrawal remain correct; required repository
  documentation/build/release work is completed by the receiving maintainer.
- FAILURE_ESCALATION: If current Melder already passes, document the source/wheel difference and
  arrange installed-consumer acceptance rather than inventing another fix. If the reduced fixture
  changes the outcome, retain the original host as a dependency until the difference is explained.

## Exact Saved Evidence

| Case | First meld before removal | Shared to peer | Saved outcome |
| --- | --- | --- | --- |
| Native probe `[False-False]` | No | No | Pass |
| Native probe `[False-True]` | No | Yes | Pass |
| Native probe `[True-False]` | Yes | No | CreationContext/codegen exception |
| Native probe `[True-True]` | Yes | Yes | Same exception |
| Actions replacement regression | Yes | Spectrum contract | Same exception |

Native case IDs are ordered `(first_meld, linked)` by pytest. The earlier native-only receipt
contains 4 cases: 2 passed / 2 failed. The saved combined retest contains 5 cases: 2 passed /
3 failed / 0 errors / 0 skipped, exit 1. Python was 3.14.7 free-threading; installed Melder
was 0.2.8215. Exact invocation, test hashes and inspected installed-native file hashes are
preserved in `rebind_retest_2026-10-03.json`.

The handoff copies the saved evidence rather than running it again. Its manifest records both
raw and LF-normalized hashes. The current integration module differs from its recorded hash
only by CRLF versus LF; the current JUnit differs only in the opposite newline direction.
The probe matches its recorded hash byte-for-byte. The copied XML still reports the exact
five case names and three failures above. No current-version failure is asserted.

## Reproduction Topology and Operations

The probe class is `RebindProbe(Cleanable)`: one integer `value`, an idempotent cleanup method,
and no constructor collaborators, logger, Package, tool, agent, greenlet or dependency graph.

1. Create a Spellbook in frame `rebind-probe`; configure dynamic mode and
   `system_caching_enabled=False`, with frame disposal defaults explicitly unset. Freeze its
   configuration and conjure the empty named root `action_definitions` with `dynamic=True`.
2. Conjure the peer root `application` in the same frame. Create the owner's lesser conduit
   `center_actions`. The peer exists in all variants; the `linked` flag controls actual sharing.
3. Late-bind `RebindProbe` on the owner root with `existence="many"`, `spellframe="actions"`,
   `binding_name="probe"`, `disposal_method_names=["cleanup"]`.
4. For linked cases, link the peer and add the exact spell ID to its create-permission contract.
5. For first-meld cases, resolve `scope.meld(spellframe="actions", binding_name="probe")`.
   The result has value 1.
6. Fetch the original spell definition. In linked cases, withdraw its peer contract entry inside
   the existing link transaction. Call `root.cleanup_spell(spell=definition)`.
7. If an original product exists, confirm it is not cleaned and still has value 1.
8. Bind the same class at the same spellframe/name with the same many lifetime and cleanup method.
   Re-establish its exact peer contract when testing the linked variant.
9. Call `scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})`.
   Controls return value 2; the two first-meld variants raise before returning.
10. Cleanup the owner and peer roots in `finally`; the fixture also resets runtime state.

There is no thread race in this probe, no conduit registration, no runtime `purge`, no change
of existence, and no explicit extra conjure between replacement bind and second meld. Both
books were conjured before registration, so this is a dynamic late-registration path. The
unlinked failure demonstrates that peer contract sharing is not necessary for reproduction.
The caching configuration above does not establish that every internal artifact cache is disabled.

## Singleton and Fixture Boundary

The probe imports `tests.mocks.melder_isolation.reset_spectrum_and_melder`. It runs before and
after every case, retires any existing Spectrum, resets native Aether through its test hook,
creates a fresh Aether, refreshes Spellbook/Conduit class references and reloads MelderOps exports.
The copied fixture shows exactly how this was done; do not replace it with tests that reuse a
cleaned singleton and then misclassify that setup mistake as a native defect.

The probe body uses only native public registration/resolution/removal operations. The surrounding
fixture still imports MelderOps and uses native test-reset machinery. Therefore the evidence is a
native-operation reproduction in the MelderOps test environment, not an executed fully standalone
Melder-only fixture. The receiving maintainer should port that isolation boundary to the canonical
Melder test fixture while preserving the operation sequence and two control cases.

The copied probe is an evidence snapshot. Running it from this artifacts directory without the
origin's test package is not a supported standalone invocation.

## Original Reproduction Command

Run from `C:/Users/Mark/PycharmProjects/priv_commandops`, after recording which wheel is actually
installed. The saved command was:

```powershell
.venv314\Scripts\python.exe -m pytest -o pythonpath=src `
  context_compass/artifacts/2026-10-03_actions_native_factory/test_native_rebind_probe.py `
  tests/component/spectrum/test_actions_native_factory.py::test_duplicate_requires_explicit_removal_and_contract_is_withdrawn `
  -q --tb=short --timeout=60
```

Use the environment's existing timeout plugin if retaining `--timeout`; do not install dependencies
or change the test body merely to match this historical command. Preserve the new JUnit separately
from these copied historical receipts.

## Application Acceptance Path

The real test creates a configured Spectrum and a command center, registers `PayloadAction` as
`payload`, melds a product with payload 5, and proves duplicate registration is rejected. It then:

- Calls `host.actions.unregister_action("payload")`.
- Confirms the exact Spectrum contract entry is absent.
- Confirms the old product still executes and returns 5.
- Confirms class lookup by that name fails after removal.
- Registers `PayloadAction` under `payload` again.
- Melds with payload 6 and expects the new product to execute and return 6.
- Cleans the center and expects its original product to be cleaned.

The recorded failure occurs at the second meld. It does not demonstrate failure of the preceding
contract withdrawal or surviving-product assertions. The final cleanup assertion is downstream of
the failure and must be reached during successful acceptance.

## Observed Native Call Chain

```text
Conduit.meld
  -> ConduitMeld.meld
  -> Meld._execute_admitted
  -> Spell._get_or_build_creation_context
  -> CreationContextFactory.get_or_build_for_spell
  -> CreationContextBuilder.build
```

The recorded builder raises at line 121 because `spell_codegen_creation` is absent. Line numbers
are from the saved installed distribution, not a promise about current source locations.
The transition responsible for that absence is UNKNOWN. Possible investigation questions include
whether removal clears shared artifacts, whether replacement starts in the correct readiness state,
and whether identity reuse chooses an incomplete context/plan. These are hypotheses, not findings.

## Goals (Outcomes)
- Explain why the second ordinary meld can reach context construction without creation codegen.
- Preserve dynamic late binding, many-instance semantics, named scopes and explicit cleanup.
- Make same-class/address replacement resolve without caller-side repair.
- Preserve old products until their actual lifetime owner cleans them.
- Confirm the fixed behavior on the delivered consumer installation, not only a source checkout.

## Non-Goals and Scope Boundaries
- No Melder runtime edits, package installation, benchmark changes or publication are performed
  by this epic-writing task.
- Do not rewrite Actions, Spectrum, agent pools, logging, greenlets or application lifetimes to
  suppress the failure.
- Do not remove the CreationContext guard, insert private cache manipulation, introduce an extra
  caller conjure/validation step, or hide the regression with skip/xfail.
- Do not treat purge as definition unregister, clean the preexisting product during unregister,
  or keep a stale sharing permission alive as a workaround.
- No claim is made that all references, roots, spellframes, existence kinds or platforms fail.

## Requirements and Acceptance Criteria
- All four operation-matrix cases pass with fresh native state per case.
- The first product stays live after definition removal; the replacement resolves value 2.
- Peer sharing permissions are removed and re-established for the intended definition; no stale
  permission entry is retained to make a lookup appear successful.
- Ordinary meld performs any required native readiness work automatically.
- The exact Actions integration regression passes unchanged on the delivered package and reaches
  its center-cleanup assertion.
- Root cleanup and fixture reset complete without masking the primary failure.
- Regressions, installed/source provenance, and source/test documentation obligations are recorded.

## Proposed Stories and Milestones

Receiving lead opens the concrete story tickets when taking ownership; no other agent is assigned
or started by this handoff.

| Work package | Outcome | Completion evidence |
| --- | --- | --- |
| A: Reproduce and compare builds | Verify old installation versus current source/wheel; preserve the four-case matrix and fixture contract | New native JUnit and exact build/import hashes, or a documented already-fixed classification |
| B: Locate and repair the state transition | Prove the missing-artifact cause and make ordinary replacement meld work | Red-to-green regression with the original guard and lifetime semantics retained |
| C: Consumer acceptance and delivery | Deliver the intended build and rerun the unchanged five-case selection | 5 passes, matching installed-wheel provenance, docs/assets/release requirements satisfied |

## Risks / Mitigations
- Historical evidence may already be fixed in newer code: compare builds before repairing.
- Equal version labels may hide different installed bytes: use the receipt's import/file hashes.
- A host/fixture reduction can change the result: retain the original reproduction until the
  difference is explained.
- Same exception text may tempt reopening an unrelated closed epic: classify the differing
  operation prefix first.
- Definition cleanup and product cleanup have different responsibilities: preserve the original
  product and verify its scope cleans it later.

## Validation / Rollout

Begin with the exact copied evidence and unchanged operation sequence, then the current native
fixture. Add focused regression coverage around whichever transition is proved responsible. After
repair, run the affected native lifecycle/readiness/contract tests, then validate the installed
MelderOps acceptance case. Broader testing and release steps follow the receiving repository's
normal requirements. This draft does not authorize a publish, install or push.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-10-03_rebind_after_first_meld/handoff_manifest.json
  - artifacts/2026-10-03_rebind_after_first_meld/test_native_rebind_probe.py
  - artifacts/2026-10-03_rebind_after_first_meld/native_rebind_finding.md
  - artifacts/2026-10-03_rebind_after_first_meld/native_rebind.xml
  - artifacts/2026-10-03_rebind_after_first_meld/rebind_retest_2026-10-03.json
  - artifacts/2026-10-03_rebind_after_first_meld/rebind_retest_2026-10-03.xml
  - artifacts/2026-10-03_rebind_after_first_meld/snapshot/tests/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain alongside the accepted native repair and consumer evidence.
- Origin story: C:/Users/Mark/PycharmProjects/priv_commandops/context_compass/tickets/stories/2026-10-03_actions_native_factory_story.md

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: receiving maintainer establishes current-build behavior before source edits.

## Decision Log / Notes
- DATETIME: 2026-10-03T19:07:45.991467+00:00
  TYPE: FACT
  CLAIM: The earlier direct-injected-provider epic is closed; this handoff covers the distinct
    rebind-after-first-meld sequence already recorded in the Actions story. Saved combined evidence
    contains 2 passes and 3 failures on 0.2.8215. No new test run or native fix is claimed.
  EVIDENCE:
  - artifacts/2026-10-03_rebind_after_first_meld/rebind_retest_2026-10-03.json
  - artifacts/2026-10-03_rebind_after_first_meld/handoff_manifest.json
  - tickets/epics/completed/2026-09-30_injected_dependency_direct_resolution_epic.md
  IMPACT: A dedicated Melder handoff now exists; the owner can assign native investigation.
  NEXT: Compare the current build with the saved reproduction and classify its present behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-03T21:00:00Z
  TYPE: DECISION
  CLAIM: Work packages A and B are done (fable_1). A: reproduced on current source with Melder's own reset
  fixture (2 failed / 2 passed, identical to the 0.2.8215 receipt). Cause (FACT): per-conduit resolution
  verdicts keyed by the content-stable spell id survived `cleanup_spell` -> `SpellSystemStates.unregister_index`,
  and the same-id rebind - a new Spell with no compiler artifact and a structural state that late binding makes
  valid eagerly - inherited the dead `valid`, so Meld skipped phases 5-11 and the context builder raised. B: the
  registry now retires an id's conduit verdicts on `unregister_index` and on `register_index`
  (`ConduitResolutionState.forget_spell`); landed at 0.2.8219 with 37 regressions (the four-case probe, the
  replacement's own resolution, a peer conduit, dependents, disposal of both products, the validation flag),
  four tiers green, release note, system docs, graph, assets and bundles. Owner ruling: a product built from the
  removed definition is deliberately left alive; for slotted existences it keeps its slot and the replacement's
  first meld returns it. Remaining: C - install the 0.2.8219 build in priv_commandops and rerun the unchanged
  five-case selection (the owner's).
  EVIDENCE:
  - tickets/tasks/completed/2026-10-03_reproduce_rebind_after_first_meld_task.md:146-262
  - tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:156-254
  - artifacts/rebind_after_first_meld_20261003/fix/landing_results.txt:1-25
  IMPACT: the epic's native half is delivered; the exit gate waits on consumer acceptance.
  NEXT: owner runs work package C and turns in the two tasks; the epic closes on C's result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested the handoff; reproduction, controls, saved failures, provenance,
  lifetime expectations and receiving work packages are now collected in the Melder repository.

## Closure Confirmation
- [x] Receiving maintainer establishes current-build behavior. (fable_1, 2026-10-03: reproduced on 0.2.8216/0.2.8218)
- [x] Native repair or already-fixed delivery is verified. (fable_1, 2026-10-03: repaired at 0.2.8219, 37 regressions, four tiers green)
- [ ] Unchanged consumer acceptance passes on the intended installation.
- [ ] Owner accepts the epic outcome.

## Context / Handoff Summary

Start with the copied four-case native probe and the five-case retest receipt. First meld is the
observed differentiator: removing/rebinding without it passes; with it, the second meld lacks
creation codegen, with and without peer sharing. The real Actions replacement case agrees.
Current Melder source/wheel behavior and the responsible internal transition remain unverified.
This epic and its copied evidence are the only delivery here; no application/native test or
runtime code was changed, no new failure was claimed, and no agent was dispatched.

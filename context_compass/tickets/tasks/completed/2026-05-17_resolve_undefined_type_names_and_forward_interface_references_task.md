# Task: resolve undefined type names and forward interface references

- Completed: 2026-05-21T09:48:52Z
- Summary: Closed by explicit user request as a historical tranche record. The task notes and partial execution state are retained for reference rather than as a claim that every original checklist item was fully completed in this ticket.

## Metadata
- Task ID: TASK-2026-05-17-resolve-undefined-type-names-and-forward-interface-references
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_0
- Priority: p1
- Created: 2026-05-17T16:03:44Z
- Updated: 2026-05-21T09:48:52Z

## Objective
Resolve the undefined-name/missing-import/forward-reference tranche using
repo-compatible fixes only: normal imports, quoted annotations, local runtime
imports, `TYPE_CHECKING` guards for typing-only dependencies, and
interface/protocol extraction only when the structural contract is real.

## Ticket Contract
- ENTRY_GATE: task 1 is complete or explicitly judged unrelated to the current
  undefined-name sites being touched
- EXECUTION_BOUNDARY: the 266-count undefined-name/import/forward-reference lane
- DEPENDENCIES: experiment fix-order docs plus the active profile rules
  preferring `TYPE_CHECKING` for typing-only imports
- EXIT_GATE: chosen sites are resolved with real type visibility and the solved
  experiment lines are removed
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when ownership is unclear enough
  that we cannot tell concrete-type imports from interface extraction

## Scope Boundaries
- In scope:
  - undefined type names
  - missing imports
  - forward interface references
- Out of scope:
  - fake structural shims used only to avoid truthful `TYPE_CHECKING` imports
  - wider interface/runtime redesign beyond what the resolved sites require

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the first concrete slice in this tranche is the
  `ISpellBinder` interface extraction and borrower-facing type replacement

## Steps / Checklist
- [ ] classify each touched site as normal import, quoted annotation, local
      runtime import, `TYPE_CHECKING` guard, or interface/protocol extraction
- [ ] use `TYPE_CHECKING` as the default typing-only import path and avoid fake
      structural shims
- [ ] remove solved backlog lines from the experiment markdown
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- repo-compatible resolution of undefined type names and forward references

## Files / Paths Impacted
- `Experiments/02_signature_and_annotation_errors.md`
- `Experiments/07_fix_order.md`
- source/interface files required by the resolved sites

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q`

## Risks / Rollback Notes
- Replacing honest typing-only imports with fake structural shims here would
  create a second policy debt while fixing the first.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-17T16:03:44Z
  TYPE: DECISION
  CLAIM: The experiment doc's generic undefined-name guidance is intentionally
    grounded here as `TYPE_CHECKING`-first for typing-only imports, with normal
    imports, quoted annotations, local runtime imports, and
    interface/protocol extraction only when the structure itself is the
    contract.
  EVIDENCE:
  - Experiments/07_fix_order.md:60-60
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md:16-21
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:68-70
  IMPACT: This task must solve real type-visibility problems without replacing
    truthful typing-only imports with fake structural shims.
  NEXT: classify the first undefined-name sites by concrete import vs interface
    boundary vs quoted annotation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:13:38Z
  TYPE: FACT
  CLAIM: The first concrete undefined-name slice is landed: `ISpellBinder` now
    exists in the real interfaces tree, `SpellBinder` implements it, and the
    borrower-facing `create_binder(...)` surfaces now type against the
    interface instead of the concrete forward reference.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellbinder.py:1-127
  - src/melder/utilities/interfaces/__init__.py:1-171
  - src/melder/spellbook/spellbinder.py:1-10
  - src/melder/spellbook/spellbook.py:20-27
  - src/melder/spellbook/spellbook.py:1918-1964
  - src/melder/aether/conduit/conduit.py:16-27
  - src/melder/aether/conduit/conduit.py:1793-1840
  - src/melder/utilities/interfaces/ispellbook.py:1-8
  - src/melder/utilities/interfaces/ispellbook.py:352-394
  IMPACT: Two real `SpellBinder` undefined-name error sites are no longer part
    of the remaining backlog, and the repo now has a production interface
    surface for this collaborator boundary.
  NEXT: continue through the remaining undefined-name sites after the
    `ISpellBinder` slice, starting with the next highest-leverage interface or
    import boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:13:38Z
  TYPE: MEASURE
  CLAIM: The focused binder and protocol utility regression ring is green after
    the `ISpellBinder` landing.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbinder.py
  - tests/unit/melder/utilities/test_protocol_crafter.py
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py
  IMPACT: The interface extraction did not break the binder implementation
    surface or the current protocol-generation utility/tests.
  NEXT: remove the resolved `SpellBinder` backlog lines from the experiment
    markdown and keep moving through task 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:17:59Z
  TYPE: FACT
  CLAIM: After the `ISpellBinder` landing, `ispellbook.py` still had five
    unresolved names. Four of them were straightforward visibility issues:
    `IConfiguration`, `ISpellSystemStates`, and `ChangeTransactionType` (used in
    two signatures). The remaining uncertain site is
    `_spell_validator: 'SpellValidationSystem'`, because importing the concrete
    validation system into the interface file would create the wrong dependency
    direction.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellbook.py:44-49
  - src/melder/utilities/interfaces/ispellbook.py:236-291
  - src/melder/spellbook/spell_crafter/validation/validation_system.py:1-54
  IMPACT: We can continue burning down task 2 with safe import fixes while
    keeping the validator-boundary decision explicit instead of guessing.
  NEXT: land the four safe imports in `ispellbook.py`, then decide whether the
    validator field needs its own interface or a narrower interface-file shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:24:16Z
  TYPE: FACT
  CLAIM: The validator-boundary slice is landed. `ISpellValidationSystem` now
    lives in the interfaces tree, the concrete `SpellValidationSystem`
    implements it, `Spellbook` owns that collaborator through the interface,
    `SpellCrafter` borrows it through the interface, and `ispellbook.py` no
    longer needs a concrete validator type reference.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellvalidationsystem.py:1-42
  - src/melder/utilities/interfaces/__init__.py:1-172
  - src/melder/spellbook/spell_crafter/validation/validation_system.py:1-54
  - src/melder/spellbook/spellbook.py:20-28
  - src/melder/spellbook/spellbook.py:219-219
  - src/melder/spellbook/spell_crafter/spell_crafter.py:256-259
  - src/melder/utilities/interfaces/ispellbook.py:1-10
  - src/melder/utilities/interfaces/ispellbook.py:47-52
  IMPACT: The remaining `SpellValidationSystem` undefined-name sites are no
    longer part of the live backlog, and task 2 keeps moving through real
    interface extraction rather than concrete import hacks.
  NEXT: continue with the next undefined-name site family after `ispellbook.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:24:16Z
  TYPE: MEASURE
  CLAIM: The validation-system and spell-crafter regression ring is green after
    the `ISpellValidationSystem` landing.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbinder.py
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py
  IMPACT: The second interface slice did not destabilize spellbook validation,
    spell crafter behavior, or the earlier binder work.
  NEXT: keep burning down the remaining undefined-name sites in task 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:28:48Z
  TYPE: FACT
  CLAIM: A further plain-interface-import cleanup slice is landed:
    `ispellgeneralprofile.py`, `ispellrecord.py`, and `ispellspace.py` now
    import the interface names they already referenced instead of relying on
    unresolved forward names.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellgeneralprofile.py:1-4
  - src/melder/utilities/interfaces/ispellrecord.py:1-7
  - src/melder/utilities/interfaces/ispellspace.py:1-3
  IMPACT: Six more undefined-name backlog lines are gone without changing
    runtime behavior or introducing new abstraction surfaces.
  NEXT: continue into the next remaining interface-file name family, starting
    with `ispellsystemstates.py` or another similarly narrow visibility slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:28:48Z
  TYPE: MEASURE
  CLAIM: The narrow profile/record/spellspace regression ring is green after the
    latest interface-import cleanup.
  EVIDENCE:
  - tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profile_models.py
  - tests/unit/melder/aether/test_frame_acl_set_compatibility_validator.py
  - tests/unit/melder/aether/test_spell_record.py
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_additional.py
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_hooks.py
  - tests/integration/melder/conduit/test_conduit_integration_clusters_spellspace.py
  IMPACT: The plain interface-import fixes remain low-risk and validated.
  NEXT: keep chipping away at task 2 with the next smallest visibility family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:42:09Z
  TYPE: FACT
  CLAIM: A second direct-mypy-guided plain-visibility batch is landed:
    `iconduitresolutionstate.py`, `icontract.py`, `iaether.py`, and
    `iaethericframe.py` now import the concrete value types or existing
    interfaces they actually referenced. One bad `IAether` /
    `IAethericFrame` import cycle was caught immediately and corrected by
    keeping the strong public collaborator typing on the right side of the
    boundary and not forcing a private back-reference cycle through the
    interface package.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitresolutionstate.py:1-3
  - src/melder/utilities/interfaces/icontract.py:1-6
  - src/melder/utilities/interfaces/iaether.py:1-9
  - src/melder/utilities/interfaces/iaethericframe.py:1-4
  IMPACT: Twenty-six more undefined-name backlog lines are gone, and the next
    interface-file slices can be approached from a much smaller remaining set.
  NEXT: continue with the next direct-mypy interface family, likely
    `iconduitward.py`, `ichangecontrolmanager.py`, or `ispell.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:42:09Z
  TYPE: MEASURE
  CLAIM: The interface importability check plus the narrow
    aether/contracts/state regression ring is green after the latest four-file
    visibility batch.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame.py
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_conduit_resolution_state.py
  - tests/unit/melder/aether/conduit/conduit_ward/contract/test_contract.py
  IMPACT: The latest import-only fixes did not destabilize the frame, contract,
    or per-conduit resolution-state surfaces.
  NEXT: keep moving through task 2 with another direct-mypy interface family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T17:06:51Z
  TYPE: FACT
  CLAIM: The frame/config side of the interface package is stronger now.
    `IAethericFrame` was expanded to model the real public frame surface,
    `IAethericFrameConfiguration` now exists as a real contract instead of
    posture `Any`, and the `INexusFrameConfiguration` interface resolved the
    earlier `INexusFrameManager` concrete-config cycle cleanly.
  EVIDENCE:
  - src/melder/utilities/interfaces/iaethericframe.py
  - src/melder/utilities/interfaces/iaethericframeconfiguration.py
  - src/melder/utilities/interfaces/inexusframeconfiguration.py
  - src/melder/utilities/interfaces/inexusframemanager.py
  - src/melder/aether/nexus/nexus_frame_configuration.py
  IMPACT: The Aether/Nexus frame configuration surfaces are now modeled with
    real interfaces instead of concrete leaks or posture `Any`.
  NEXT: continue clearing the remaining undefined-name families with the same
    "real boundary, no shortcut" standard.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T17:06:51Z
  TYPE: MEASURE
  CLAIM: The Aether frame / Nexus frame-config regression rings are green after
    the config-interface hardening, and direct local mypy checks for the config
    interface files are clean with import following skipped.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py
  - tests/unit/melder/aether/test_aetheric_frame.py
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  - tests/unit/melder/aether/test_nexus_frame_configuration.py
  - tests/unit/melder/aether/test_nexus_frame_manager.py
  IMPACT: The richer config/frame interfaces did not break the runtime slices
    they describe.
  NEXT: keep hammering through task 2 with the next remaining direct-mypy
    visibility cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T17:13:33Z
  TYPE: FACT
  CLAIM: The DevOps/change-control interface cluster is now typed against the
    right surfaces: `IDevOpsManager` uses `IIncidentManager` and
    `IChangeControlManager`, `IIncidentManager` now sees its concrete incident
    DTOs, and `IChangeControlManager` uses `ISpellSystemStates` / `ISpellIndex`
    plus the concrete request/staged/admission DTOs needed for its public API.
  EVIDENCE:
  - src/melder/utilities/interfaces/idevopsmanager.py:1-5
  - src/melder/utilities/interfaces/iincidentmanager.py:1-4
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:1-7
  IMPACT: Another direct-mypy visibility family is cleared without introducing
    new runtime abstractions or policy drift.
  NEXT: continue with the next remaining interface-file family from the live
    mypy output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T17:13:33Z
  TYPE: MEASURE
  CLAIM: The DevOps/change-control interface files import cleanly, the local
    mypy check for those three files is green with `--follow-imports skip`, and
    the direct state/change-control/incident regression ring is green.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py
  - tests/unit/melder/aether/dev_ops/incident_manager/test_incident_manager.py
  IMPACT: This cluster is safe to count as cleared and we can keep progressing
    through task 2 without revisiting it.
  NEXT: move to the next smallest direct-mypy visibility batch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T17:47:45Z
  TYPE: FACT
  CLAIM: The remaining plain visibility errors in `INexus` and `IRift` are
    cleared: both files now import `IConduit`, and `IRift` now imports
    `CodegenProjection` explicitly for its codegen-projection accessor.
  EVIDENCE:
  - src/melder/utilities/interfaces/inexus.py:1-9
  - src/melder/utilities/interfaces/irift.py:1-7
  IMPACT: Direct local mypy on those two files now reports only the three
    `no-redef` issues in `INexus`; the unresolved-name part of that family is
    gone.
  NEXT: skip the `INexus` `no-redef` trio for now and continue with another
    name-visibility family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T17:47:45Z
  TYPE: MEASURE
  CLAIM: Direct local mypy on `INexus` / `IRift` confirms the visibility fixes
    landed cleanly: the only remaining diagnostics in that two-file slice are
    the three existing `no-redef` issues on `INexus`.
  EVIDENCE:
  - src/melder/utilities/interfaces/inexus.py
  - src/melder/utilities/interfaces/irift.py
  IMPACT: We can keep treating task 2 as an import/interface-visibility lane
    without drifting into the separate `no-redef` tranche.
  NEXT: continue with the next direct-mypy visibility cluster instead of
    touching the `INexus` duplicate-definition issues.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:06:55Z
  TYPE: DECISION
  CLAIM: The remaining task-2 work now splits into two clean visibility-only
    clusters and two mixed clusters. `IMutationResearch` already has the
    companion interface files it references, and
    `ICodegenTransactionContext` only lacks `CodegenProjection` visibility.
    By contrast, `IConduitWard` and `IConduit` are mixed files because their
    remaining name-defined errors sit beside implicit-optional/default-`None`
    diagnostics that belong to the user-owned Optional lane.
  EVIDENCE:
  - src/melder/utilities/interfaces/imutationresearch.py:1-59
  - src/melder/utilities/interfaces/imutationresearchconfiguration.py:1-29
  - src/melder/utilities/interfaces/imutationresearchconfigurationbuilder.py:1-24
  - src/melder/utilities/interfaces/imutationconduit.py:1-20
  - src/melder/utilities/interfaces/imutationframe.py:1-20
  - src/melder/utilities/interfaces/icodegentransactioncontext.py:1-68
  - src/melder/utilities/interfaces/iconduitward.py:1-66
  - src/melder/utilities/interfaces/ispell.py:1-129
  IMPACT: The next safe task-2 slice is the mutation-research and
    codegen-transaction visibility cleanup, while the larger conduit-facing
    interfaces should stay deferred until their Optional/default-`None`
    conflicts can be handled intentionally.
  NEXT: land the `IMutationResearch` and `ICodegenTransactionContext`
    visibility fixes first, then reassess whether `ISpell` is still the next
    clean non-Optional cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:08:20Z
  TYPE: FACT
  CLAIM: The next clean visibility slice is landed. `IMutationResearch` now
    imports the mutation companion interfaces it already referenced, and
    `ICodegenTransactionContext` now imports the concrete `CodegenProjection`
    type used by the live transaction-context implementation.
  EVIDENCE:
  - src/melder/utilities/interfaces/imutationresearch.py:1-11
  - src/melder/utilities/interfaces/icodegentransactioncontext.py:1-8
  - src/melder/mutation_research/mutation_research.py:4-23
  - src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py:3-14
  IMPACT: Seven more name-defined errors are resolved without touching the
    user-owned Optional/default-`None` lanes in the larger conduit-facing
    interface files.
  NEXT: remove the solved backlog lines for these two files and then reassess
    whether `ISpell` or another small visibility-only file is the next clean
    task-2 slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:08:20Z
  TYPE: MEASURE
  CLAIM: The direct type-check and focused runtime validation ring are green
    after the mutation-research/codegen visibility patch.
  EVIDENCE:
  - src/melder/utilities/interfaces/imutationresearch.py
  - src/melder/utilities/interfaces/icodegentransactioncontext.py
  - tests/unit/melder/mutation_research/test_mutation_research_root.py
  - tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py
  - tests/unit/melder/aether/test_codegen_system_unit_matrix.py
  IMPACT: The current slice is safe to count as landed and remove from the live
    experiment backlog.
  NEXT: sync the backlog markdown and summary counters before moving to the
    next task-2 cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:16:13Z
  TYPE: FACT
  CLAIM: A chunk of the task-2 backlog is stale against the current repo.
    Direct file-scoped mypy now passes on `ISpellSystemStates`,
    `IChangeControlManager`, `IDevOpsManager`, `IIncidentManager`,
    `IConfiguration`, `IDetail`, `ICodegenRiftSpace`, and
    `IFrameACLCommandProfileStrategy`; only `ICreations` is still live in that
    small interface batch, and it is just missing `Dict` from `typing`.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellsystemstates.py:1-11
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:1-9
  - src/melder/utilities/interfaces/idevopsmanager.py:1-6
  - src/melder/utilities/interfaces/iincidentmanager.py:1-6
  - src/melder/utilities/interfaces/iconfiguration.py:1-2
  - src/melder/utilities/interfaces/idetail.py:1-3
  - src/melder/utilities/interfaces/icodegenriftspace.py:1-3
  - src/melder/utilities/interfaces/iframeaclcommandprofilestrategy.py:1-2
  - src/melder/utilities/interfaces/icreations.py:1-3
  IMPACT: We can remove several stale undefined-name backlog lines without
    pretending they still need code work, and the only real edit needed in this
    micro-slice is the `ICreations` import.
  NEXT: add the `Dict` import to `ICreations`, re-run targeted mypy, and then
    trim the stale backlog lines for the now-clean mini-batch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:17:22Z
  TYPE: FACT
  CLAIM: The mini-batch is landed. `ICreations` now imports `Dict`, and the
    whole nine-file visibility slice is green under direct file-scoped mypy:
    `ICreations`, `ICodegenRiftSpace`, `IConfiguration`, `IDetail`,
    `IFrameACLCommandProfileStrategy`, `IChangeControlManager`,
    `IDevOpsManager`, `IIncidentManager`, and `ISpellSystemStates`.
  EVIDENCE:
  - src/melder/utilities/interfaces/icreations.py:1-3
  - src/melder/utilities/interfaces/icodegenriftspace.py:1-3
  - src/melder/utilities/interfaces/iconfiguration.py:1-2
  - src/melder/utilities/interfaces/idetail.py:1-3
  - src/melder/utilities/interfaces/iframeaclcommandprofilestrategy.py:1-2
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:1-9
  - src/melder/utilities/interfaces/idevopsmanager.py:1-6
  - src/melder/utilities/interfaces/iincidentmanager.py:1-6
  - src/melder/utilities/interfaces/ispellsystemstates.py:1-11
  IMPACT: The backlog can now drop one real live line (`ICreations`) plus the
    stale undefined-name lines for the eight already-clean interface files.
  NEXT: remove those stale lines from `Experiments/02_signature_and_annotation_errors.md`
    and sync the summary counters before selecting the next active cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:17:22Z
  TYPE: MEASURE
  CLAIM: Direct file-scoped mypy and the focused creations/dev-ops unit ring
    are green after the mini-batch cleanup.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/creations/test_creations.py
  - tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py
  - tests/unit/melder/aether/dev_ops/incident_manager/test_incident_manager.py
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py
  IMPACT: The small interface cleanup is safe to count as done and the
    remaining task-2 backlog should now be narrower and more trustworthy.
  NEXT: sync the backlog docs, then choose the next clean non-Optional
    name-defined cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:21:18Z
  TYPE: DECISION
  CLAIM: `mutation_research.py` is not a clean task-2 file because its two
    remaining name-defined misses sit beside `_cleaned`, nullable assignment,
    and union-attr diagnostics. `spellbook_validation_error.py` is the next
    bounded target instead: it has one name-defined miss and only needs a
    spell-facing read contract, so `ISpell` is the right boundary rather than a
    concrete `Spell` import.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:524-572
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:1-28
  IMPACT: Task 2 keeps moving on real name-defined work without crossing into
    the user-owned Optional/None cleanup tranche.
  NEXT: patch `spellbook_validation_error.py` to type against `ISpell`, then
    validate it and remove its stale backlog line.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:22:14Z
  TYPE: FACT
  CLAIM: The spellbook-validation exception slice is landed.
    `SpellbookValidationError` now types its broken-spell list against
    `ISpell`, which matches the read-only surface the formatter actually uses
    and removes the stale concrete `Spell` name-defined miss.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:1-28
  - src/melder/utilities/interfaces/ispell.py:1-32
  IMPACT: Another clean task-2 line is gone without widening scope into the
    Optional/None tranche or concrete-runtime imports.
  NEXT: remove the stale backlog line for `spellbook_validation_error.py` and
    sync the summary counters again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:22:14Z
  TYPE: MEASURE
  CLAIM: Direct mypy and the focused validation/exception unit ring are green
    after the `ISpell` exception-surface patch.
  EVIDENCE:
  - tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  IMPACT: The exception boundary is safe to count as resolved and the backlog
    can drop its stale line.
  NEXT: sync the backlog docs, then return to the next unresolved clean
    name-defined cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:25:07Z
  TYPE: DECISION
  CLAIM: The next bounded task-2 slice is the validation-strategy family, but
    only for `SpellValidationContext` visibility. A direct mypy probe on the
    strategy directory shows a clean separation: most remaining diagnostics are
    `name-defined` misses for `SpellValidationContext`, while the leftover base
    strategy `_cleaned` problem and the `binding_resolution_cycle_strategy`
    object-shape errors belong to later tranches.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/strategies/spell_validation_strategy.py:58-66
  - src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:46-46
  - src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:217-222
  - src/melder/spellbook/spell_crafter/validation/strategies/duplicate_spell_name_strategy.py:42-47
  IMPACT: We can shrink the undefined-name backlog further without stepping
    into the object-shape or cleanup-state lanes.
  NEXT: add the missing `SpellValidationContext` imports across the affected
    strategy files, validate that the remaining diagnostics in that directory
    are non-name-defined only, and then trim the stale backlog lines.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:27:38Z
  TYPE: FACT
  CLAIM: The validation-strategy name-defined slice is landed. The affected
    strategy modules now import `SpellValidationContext`, and the directory-wide
    mypy run is reduced to one base-strategy `_cleaned` `has-type` issue plus
    four `attr-defined` issues in `binding_resolution_cycle_strategy.py`; the
    `SpellValidationContext` name-defined errors are gone.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/strategies/spell_validation_strategy.py:1-3
  - src/melder/spellbook/spell_crafter/validation/strategies/duplicate_spell_name_strategy.py:1-6
  - src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:1-18
  IMPACT: Thirteen stale undefined-name backlog lines can be removed while the
    remaining strategy-directory diagnostics stay clearly classified outside
    task 2.
  NEXT: trim those thirteen lines from `Experiments/02_signature_and_annotation_errors.md`
    and sync the summary counters again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:27:38Z
  TYPE: MEASURE
  CLAIM: The focused strategy/validation unit ring is green after the
    `SpellValidationContext` import pass.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_spell_validation_strategy.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  IMPACT: The strategy import cleanup is safe to count as resolved for the
    undefined-name tranche.
  NEXT: sync the backlog docs before picking the next non-Optional cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:29:34Z
  TYPE: FACT
  CLAIM: Another stale mini-batch is confirmed. `IRift`,
    `INexusFrameManager`, `IFrameACLCodegenProfileStrategy`, and
    `IFrameACLViewProfileStrategy` are already clean under direct file-scoped
    mypy, while the two runtime dev-ops files in the same backlog neighborhood
    are still mixed with `has-type`, `assignment`, `union-attr`, and
    `attr-defined` diagnostics.
  EVIDENCE:
  - src/melder/utilities/interfaces/irift.py:1-7
  - src/melder/utilities/interfaces/inexusframemanager.py:1-6
  - src/melder/utilities/interfaces/iframeaclcodegenprofilestrategy.py:1-2
  - src/melder/utilities/interfaces/iframeaclviewprofilestrategy.py:1-2
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:63-83
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:87-110
  IMPACT: We can remove seven more stale undefined-name lines from the backlog
    without claiming the adjacent runtime files are fixed.
  NEXT: trim the stale interface-file lines from `Experiments/02_signature_and_annotation_errors.md`
    and leave the mixed runtime files for later tranches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:38:24Z
  TYPE: DECISION
  CLAIM: The next bounded runtime slice is the validation-runtime trio itself:
    `spell_validation_context.py`, `spell_validation_result.py`, and
    `validation_system.py`. Their remaining name-defined misses are plain
    visibility problems for `ISpell`, `ISpellbook`, `SpellRequirements`,
    `SpellSymbolicGraph`, `SpellResolutionFrame`, `CancellationEvent`,
    `SpellValidationIssue`, and `SpellValidationStrategy`; the separate
    `_cleaned` / assignment issues will remain untouched.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/spell_validation_context.py:1-58
  - src/melder/spellbook/spell_crafter/validation/spell_validation_result.py:1-37
  - src/melder/spellbook/spell_crafter/validation/validation_system.py:1-88
  IMPACT: We can keep shrinking task 2 with real source-file fixes instead of
    only pruning stale backlog lines.
  NEXT: add the missing imports in the three validation-runtime files, validate
    the remaining diagnostics are non-name-defined only, and then sync the
    backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:39:30Z
  TYPE: FACT
  CLAIM: The validation-runtime name-defined slice is landed.
    `spell_validation_context.py`, `spell_validation_result.py`, and
    `validation_system.py` now import the runtime types they already
    referenced, and the direct mypy probe on those files is reduced to
    `_cleaned` `has-type` and cleanup-assignment leftovers only.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/spell_validation_context.py:1-18
  - src/melder/spellbook/spell_crafter/validation/spell_validation_result.py:1-7
  - src/melder/spellbook/spell_crafter/validation/validation_system.py:1-39
  IMPACT: Nine more stale undefined-name backlog lines can be removed without
    pretending the remaining cleanup-state diagnostics are part of task 2.
  NEXT: trim those stale validation-runtime lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the counters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:39:30Z
  TYPE: MEASURE
  CLAIM: The focused validation-runtime unit ring is green after the import
    cleanup.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_result.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  IMPACT: The runtime validation slice is safe to count as resolved for the
    undefined-name tranche.
  NEXT: sync the backlog docs before choosing the next clean cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:41:47Z
  TYPE: DECISION
  CLAIM: The next bounded artifact slice is the phase-artifact layer:
    `spell_requirements.py`, `spell_symbolic_graph.py`,
    `spell_system_adjacency_builder.py`, and
    `spell_system_adjacency_snapshot.py`. Their remaining name-defined misses
    are concrete artifact types that already exist in sibling modules:
    `SpellParameterRequirement`, `SpellSymbolicDependency`,
    `SpellLocalTopology`, and `SpellSocketDescriptor`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_requirements_finder/spell_parameter_requirements.py:12-12
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_dependency.py:10-10
  - src/melder/spellbook/spell_crafter/topology/spell_local_topology.py:9-9
  - src/melder/spellbook/spell_crafter/topology/spell_local_topology.py:78-78
  IMPACT: We can continue burning down task 2 on concrete source files without
    touching the cycle-heavy interface files yet.
  NEXT: add the sibling-module imports for those artifact types, validate that
    only the non-task-2 cleanup-state diagnostics remain, and then sync the
    backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:42:38Z
  TYPE: FACT
  CLAIM: The phase-artifact name-defined slice is landed.
    `spell_requirements.py`, `spell_symbolic_graph.py`,
    `spell_system_adjacency_builder.py`, and
    `spell_system_adjacency_snapshot.py` now import their sibling artifact
    types, and the direct mypy probe on those files is reduced to the
    pre-existing cleanup-state `has-type` / `assignment` leftovers.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_requirements_finder/spell_requirements.py:1-13
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_graph.py:1-8
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py:1-5
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_snapshot.py:1-4
  IMPACT: Thirteen more stale undefined-name backlog lines can be removed while
    leaving the cleanup-state tranche untouched.
  NEXT: trim those thirteen lines from `Experiments/02_signature_and_annotation_errors.md`
    and sync the summary counters again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:42:38Z
  TYPE: MEASURE
  CLAIM: The focused phase-artifact and validation/system unit ring is green
    after the sibling-import cleanup.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_result.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  - tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_validation_system.py
  IMPACT: The artifact visibility slice is safe to count as resolved for task 2.
  NEXT: sync the backlog docs before moving to the next cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:44:40Z
  TYPE: DECISION
  CLAIM: `mutation_research.py` is now the cleanest real runtime file left in
    task 2. Its two remaining name-defined misses are just the sibling mutation
    node types, and those node classes already exist under the research tree.
    The other diagnostics in that file remain outside task 2.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:524-572
  - src/melder/mutation_research/research/spell/node/spell_mutation_node.py:8-8
  - src/melder/mutation_research/research/creation/node/creation_mutation_node.py:9-9
  IMPACT: We can keep shrinking the undefined-name bucket with a real code
    change instead of only removing stale backlog rows.
  NEXT: import the two mutation node types into `mutation_research.py`,
    validate the file, and then sync the backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:45:14Z
  TYPE: FACT
  CLAIM: The `mutation_research.py` name-defined slice is landed. The file now
    imports `SpellMutationNode` and `CreationMutationNode`, and the direct mypy
    probe is reduced to the existing cleanup-state and nullable follow-on
    diagnostics only.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1-19
  - src/melder/mutation_research/research/spell/node/spell_mutation_node.py:8-8
  - src/melder/mutation_research/research/creation/node/creation_mutation_node.py:9-9
  IMPACT: Two more real undefined-name backlog lines can be removed without
    crossing into the Optional/None lane.
  NEXT: trim the two stale mutation-research lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the summary
    counters again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:45:14Z
  TYPE: MEASURE
  CLAIM: The focused mutation-research unit/component/integration ring is green
    after the node-import cleanup.
  EVIDENCE:
  - tests/unit/melder/mutation_research/test_mutation_research_root.py
  - tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py
  - tests/integration/melder/mutation_research/test_mutation_research_root_integration.py
  IMPACT: The mutation-research visibility patch is safe to count as resolved
    for task 2.
  NEXT: sync the backlog docs and keep moving through the remaining real
    undefined-name surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:46:26Z
  TYPE: DECISION
  CLAIM: The next bounded slice is `dag_index.py` plus the non-cycle concrete
    imports in `spell.py`. `SpellSocketDescriptor`, `SpellRequirements`,
    `SpellSymbolicGraph`, and `SpellSystemState` are plain concrete artifact
    types; the `SpellCrafter` references remain excluded because they sit on a
    real cycle boundary.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/dag/dag_index.py:1-5
  - src/melder/spellbook/spell.py:738-759
  - src/melder/spellbook/spell.py:862-873
  - src/melder/spellbook/spell.py:1574-1598
  IMPACT: We can keep removing real name-defined lines from task 2 without
    forcing a premature `SpellCrafter` interface decision.
  NEXT: add the concrete artifact imports, validate that only the remaining
    cycle/mixed diagnostics stay, and sync the backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:47:11Z
  TYPE: FACT
  CLAIM: The `dag_index.py` and partial `spell.py` artifact slice is landed.
    `dag_index.py` now sees `SpellSocketDescriptor`, and `spell.py` now sees
    `SpellRequirements`, `SpellSymbolicGraph`, and `SpellSystemState`. The only
    remaining `spell.py` name-defined misses are the two `SpellCrafter` cycle
    points.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/dag/dag_index.py:1-7
  - src/melder/spellbook/spell.py:1-30
  - src/melder/spellbook/spell.py:357-357
  - src/melder/spellbook/spell.py:747-747
  IMPACT: Four more real undefined-name backlog lines can be removed while the
    harder `SpellCrafter` cycle decision stays isolated.
  NEXT: trim the solved `dag_index.py` and `spell.py` lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the counters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:47:11Z
  TYPE: MEASURE
  CLAIM: The focused spell/system unit ring is green after the concrete import
    slice.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell.py
  - tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_validation_system.py
  IMPACT: The partial `spell.py` and `dag_index.py` visibility cleanup is safe
    to count as resolved for task 2.
  NEXT: sync the backlog docs and keep reducing the remaining real bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:51:35Z
  TYPE: DECISION
  CLAIM: The next control-plane slice is `spell_system_states.py` plus
    `change_control_manager.py`. The frame annotation in
    `spell_system_states.py` can use `IAethericFrame` cleanly because the file
    only stores the frame handle, while `change_control_manager.py` should keep
    the concrete `SpellSystemStates` type because it reaches through the
    borrowed object to `_frame`, which the current interface does not model.
  EVIDENCE:
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:63-83
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:512-530
  - src/melder/utilities/interfaces/iaethericframe.py:1-45
  - src/melder/utilities/interfaces/ispellsystemstates.py:1-52
  IMPACT: We can remove nine more real undefined-name lines without inventing a
    fake interface guarantee for `_frame`.
  NEXT: patch the concrete/interface imports accordingly, validate the two files,
    and then sync the backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:52:59Z
  TYPE: FACT
  CLAIM: The control-plane name-defined slice is landed.
    `spell_system_states.py` now imports `SpellLocalTopology` and types its
    frame handle against `IAethericFrame`, while
    `change_control_manager.py` now imports the concrete `SpellSystemStates`
    type it actually uses. The direct mypy probe on those files is reduced to
    cleanup-state, nulling, and one object-shape follow-on only.
  EVIDENCE:
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:1-17
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1-28
  - src/melder/utilities/interfaces/iaethericframe.py:1-45
  IMPACT: Nine more real undefined-name backlog lines can be removed without
    inventing new type hacks.
  NEXT: trim the solved control-plane lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the counters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:52:59Z
  TYPE: MEASURE
  CLAIM: The focused control-plane unit ring is green after the import cleanup.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py
  IMPACT: The control-plane visibility patch is safe to count as resolved for
    task 2.
  NEXT: sync the backlog docs and keep reducing the remaining real bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:55:15Z
  TYPE: DECISION
  CLAIM: The next interface slice is `iconduitward.py`, not `iconduit.py`.
    `IConduitWard` can import `IConduit`, `ISafeLogger`, `ISpell`, `IContract`,
    and `IDetail` cleanly, while still using the concrete enum/value types
    (`ConduitState`, `Policies`, `Permissions`, `ContractTypes`,
    `ChangeTransactionType`) that describe its actual policy surface. Pulling
    concrete `Contract` or `Detail` back into the protocol file would create an
    avoidable interface-to-concrete loop.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitward.py:1-36
  - src/melder/utilities/interfaces/icontract.py:1-24
  - src/melder/utilities/interfaces/idetail.py:1-12
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:10-18
  IMPACT: We can shrink the largest remaining interface backlog file without
    worsening the cycle picture.
  NEXT: patch the `IConduitWard` imports and type aliases, validate the file,
    and then sync the backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:57:34Z
  TYPE: FACT
  CLAIM: The `iconduitward.py` name-defined slice is landed. The file now
    imports its conduit/spell/logger/policy/value collaborators cleanly, uses
    an internal `Any` contract storage surface instead of introducing an
    interface cycle, and direct mypy is reduced to the user-owned implicit
    Optional/default-`None` diagnostics only.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitward.py:1-16
  - src/melder/utilities/interfaces/iconduitward.py:31-43
  - src/melder/utilities/interfaces/icontract.py:1-24
  IMPACT: A large chunk of the remaining undefined-name backlog can now be
    removed without destabilizing the runtime import graph.
  NEXT: trim the stale `iconduitward.py` lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the counters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T18:57:34Z
  TYPE: MEASURE
  CLAIM: The focused conduit-ward contract/change-control/spellbinder unit ring
    is green after the `IConduitWard` import cleanup.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/conduit_ward/contract/test_contract.py
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py
  - tests/unit/melder/spellbook/test_spellbinder.py
  IMPACT: The `IConduitWard` visibility patch is safe to count as resolved for
    task 2.
  NEXT: sync the backlog docs before picking the next remaining real slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T18:59:35Z
  TYPE: DECISION
  CLAIM: The next interface slice is `iconduit.py`. The safe shape is:
    interface-first for `IAether`, `IConfiguration`, `ISafeLogger`,
    `ICreations`, `IMeld`, `ISpellbook`, `ISpell`, `IConduitCloud`, and
    `IConduitResolutionState`; concrete import for `ConduitState`,
    `ChangeTransactionType`, and `CreationGate`; and keep `_conduit_ward`
    opaque for now to avoid introducing a mutual `IConduit` <-> `IConduitWard`
    import cycle.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduit.py:1-35
  - src/melder/utilities/interfaces/imeld.py:1-18
  - src/melder/utilities/interfaces/icreations.py:1-20
  - src/melder/utilities/interfaces/iaether.py:1-20
  - src/melder/utilities/synchronization/creation_gate.py:1-9
  IMPACT: We can remove a large chunk of remaining interface name-defined lines
    without destabilizing the interface import graph.
  NEXT: patch the `IConduit` imports/types accordingly, validate the file, and
    then sync the backlog again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T19:01:22Z
  TYPE: FACT
  CLAIM: The `iconduit.py` name-defined slice is landed. The file now uses
    interface-first imports for the stable collaborator surfaces, keeps
    `CreationGate` and the value enums concrete, and leaves only one `no-redef`
    plus the user-owned implicit-optional defaults in direct mypy.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduit.py:1-17
  - src/melder/utilities/interfaces/iconduit.py:23-35
  - src/melder/utilities/interfaces/iconduit.py:266-279
  IMPACT: Another large chunk of stale undefined-name backlog lines can be
    removed without reintroducing interface import cycles.
  NEXT: trim the stale `iconduit.py` lines from
    `Experiments/02_signature_and_annotation_errors.md` and sync the counters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T19:01:22Z
  TYPE: MEASURE
  CLAIM: The corrected conduit-facing validation ring is green after the
    `IConduit` import cleanup.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py
  - tests/unit/melder/aether/conduit/conduit_ward/contract/test_contract.py
  - tests/unit/melder/spellbook/test_spellbinder.py
  IMPACT: The `IConduit` visibility patch is safe to count as resolved for
    task 2.
  NEXT: sync the backlog docs and continue with the remaining real bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T19:07:36Z
  TYPE: DECISION
  CLAIM: The next `ISpell` pass is the concrete-artifact half only. The file
    can safely import `SpellIndex`, `SpellType`, `SpellSystemState`,
    `SpellRequirements`, `SpellSymbolicGraph`, `CreationGateController`, and
    `CancellationEvent` directly. The two remaining interface names
    (`ISpellbook`, `ISpellSystemStates`) stay deferred because they sit on real
    interface-cycle boundaries.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispell.py:1-12
  - src/melder/utilities/interfaces/ispell.py:45-50
  - src/melder/utilities/interfaces/ispell.py:370-370
  - src/melder/utilities/interfaces/ispell.py:427-437
  - src/melder/utilities/interfaces/ispell.py:496-710
  IMPACT: We can reduce the remaining undefined-name bucket again without
    forcing a weak cycle hack for the spellbook/control-plane references.
  NEXT: patch those concrete imports, validate that only the two real cycle
    names remain in `ispell.py`, and then sync the backlog.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T19:19:09Z
  TYPE: FACT
  CLAIM: The `ISpell` cycle-break slice is landed. `ISpell` now uses
    `ISpellIndex` plus two narrow local spell-owned protocols
    (`ISpellbookSpellSurface` and `ISpellSystemStatesSpellSurface`) instead of
    importing the full `ISpellbook` / `ISpellSystemStates` interfaces back into
    the same module. That removes the real interface-package cycle while
    keeping the spell-facing contract explicit.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispell.py:1-54
  - src/melder/utilities/interfaces/ispell.py:61-66
  - src/melder/utilities/interfaces/ispell.py:110-127
  IMPACT: Eighteen more real undefined-name backlog lines are gone, and the
    last runtime-cycle regression from the earlier concrete-import attempt is
    fixed properly instead of being papered over with `Any`.
  NEXT: shrink the undefined-name backlog section to the final `spell.py`
    `SpellCrafter` cycle lines and sync the summary docs to match.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-17T19:19:09Z
  TYPE: MEASURE
  CLAIM: Direct mypy on `ispell.py` is fully clean and the spell/validation
    tests that previously failed during collection now pass.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  IMPACT: The `ISpell` boundary is now strong enough to serve as the main spell
    interface without breaking runtime imports.
  NEXT: sync the backlog docs and then decide whether the final two
    `SpellCrafter` references in `spell.py` should stay as the last task-2
    cycle decision or be converted to a narrow local protocol too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T09:48:52Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this task for turn-in as a historical execution record even though the original tranche checklist was not fully exhausted inside this one ticket.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: The task can move to `completed/` without pretending that the unresolved remainder of the undefined-name tranche was finished here.
  NEXT: move the ticket to `tickets/tasks/completed/` and record the closure on the board as a user-requested historical turn-in.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Second task in the tranche. The `ISpellBinder` extraction is the first landed
slice. Remaining work in this task should continue to use repo-compatible type
visibility fixes only: real imports, quoted annotations, local runtime imports,
and interface/protocol extraction.

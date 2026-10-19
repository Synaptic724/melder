

# Task: Record in the system documents that a root's teardown cleans only what the root holds

## Metadata
- Task ID: TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds
- Story: none (standalone; follows the open teardown item of EPIC-2026-10-18-managed_spell_examples_and_docs,
  closed)
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T23:49:36Z
- Updated: 2026-10-18T23:49:36Z

## Objective
The two source system documents, src_architecture and src_components, state the owner's ruling (chat,
2026-10-18): "if the root cleans up it only cleans up whats held by the root". They describe what the code does
today at a root's teardown, with source evidence, and mark where today's code differs from the ruling as open
with the owner. Nothing in either document keeps claiming a teardown behaviour the source does not have.

## Ticket Contract
- ENTRY_GATE: this ticket's board row routes here; the ruling and the owner's question are recorded in Notes;
  the teardown source is re-read before any document edit.
- EXECUTION_BOUNDARY: `context_compass/system_docs/src_architecture.md` and
  `context_compass/system_docs/src_components.md` - only their text on a root's teardown of managed pools and
  the release that follows it, plus a Context / Handoff Summary entry each - and their two indexes, regenerated
  by the index tool, never hand-edited; this ticket, the boards, the mailbox and a lane folder under
  `artifacts/`. No `src/`, `tests/`, `docs/`, `release_docs/` or graph edit.
- DEPENDENCIES: the owner's ruling (chat, 2026-10-18); STORY-2026-10-18-managed_spell_lifecycle_map (the
  teardown map and probe cases P07 and P17); melder_0 (its docs pass corrected the release-after-teardown failure
  mode) and melder_1 (its S4 landing promotes patches into the same two documents), told by mailbox.
- EXIT_GATE: both documents state the ruling and today's behaviour with source evidence; the two places the code
  differs from the ruling are marked open with the owner; no stale teardown claim remains in the sections
  touched; both indexes regenerated and `--check` clean; no path into the documentation tooling in the produced
  text; Notes recorded; closure and board sync.
- FAILURE_ESCALATION: a document's hash moving between read and write (another writer) - re-read, re-apply
  against the new text and mailbox that writer; a teardown behaviour that contradicts the ruling beyond the two
  known gaps - DECISION_REQUEST to the owner before writing it down; the index tool refusing - BLOCKER.

## Scope Boundaries
- In scope: the teardown and release text of the two source system documents, their indexes, the mailbox
  notices.
- Out of scope: the code changes the two gaps would need (the owner decides whether to file them); the user
  page `docs/intermediate/managed-spells.md`, which states today's behaviour and changes only with the code; the
  tests system documents; the graph; the asset and LLM-bundle rebuild, which the owner waived for this session's
  lane ("other agents are working") and which melder_0's next rebuild carries.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the owner asked for the update in chat ("update the system docs please"); the row routes
  here and the ruling is recorded below.

## Steps / Checklist
- [x] Consume M0-205 into Notes.
- [x] Re-read the teardown source: `Creations.cleanup`, `ManagedSpellQuantity.cleanup` and `put_back`,
      `ReleaseManagedSpell.unregister` and `_resolve_pool`, `ManagedSpellLease.release`.
- [x] Read the authoring instructions for the two documents (on demand: writing a system document).
- [x] Slice the current teardown text of both documents and record what each says.
- [x] NOTICE melder_0 (M2-20) and melder_1 (M2-21) naming the sections.
- [ ] Edit src_architecture and regenerate its index; edit src_components and regenerate its index.
- [ ] Validate: `--check` on both indexes, the tooling-path leak check, the citation bounds check, re-read the
      touched sections.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The updated `src_architecture.md` and `src_components.md` with their regenerated indexes.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_architecture_index.md
- context_compass/system_docs/src_components.md
- context_compass/system_docs/src_components_index.md

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/tools/system_documents/index_document.py --doc context_compass/system_docs/src_architecture.md --check`
  - `python context_compass/tools/system_documents/index_document.py --doc context_compass/system_docs/src_components.md --check`

## Risks / Rollback Notes
- melder_1's S4 landing edits the same documents: anchored edits on fresh reads, and a NOTICE before the edit.
- Rollback: the apply scripts keep the before-copies in the lane folder; the indexes regenerate from the text.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No behaviour claim in a system document without the source read behind it.
- [ ] No hand-edited index; no path into the documentation tooling in a produced document.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/root_teardown_docs_20261018/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: at closure; the apply scripts, the before-copies and the check runs stay as the edit's
  evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_2; prose and evidence; this ticket and the two documents' teardown text;
  revision in progress; Notes below.
- Published By: UNKNOWN before publication (the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-18T23:49:36Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ruling, in chat on 2026-10-18 after the managed-spell lane closed: "if the root cleans up it
    only cleans up whats held by the root, update the system docs please". With it the owner asked why a root's
    teardown raises at all: "if the root is cleaning up why would it raise? ... A cleanup means the objects are
    being disposed why are we going to throw an exception?" The answer given in chat: the ExceptionGroup comes
    from a consumer the root itself holds whose disposal method gives a pooled object back - the root's store
    has already unregistered and cleaned its pools, so the release raises inside that disposal and the store
    collects it (S1's RISK note, probe P17; the same consumer in a lesser conduit is fine, P07). Read against
    today's code, two places differ from the ruling: (1) the teardown order - pools unregistered and cleaned
    before the root's other disposals, so a root-held consumer's release fails; (2) a pool's cleanup disposes
    the `many` children recorded with every pooled object, objects that are still out included, though an out
    object is its holder's. This task writes the ruling and today's behaviour into src_architecture and
    src_components and marks both gaps open with the owner; the code changes are the owner's to file.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md:263-280
  - context_compass/tickets/epics/completed/2026-10-18_managed_spell_examples_and_docs_epic.md:241-267
  IMPACT: Sets the documents' target text: the rule, the current behaviour, the two open gaps - and no code edit.
  NEXT: Add this ticket's board row, then consume M0-205 into these Notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:51:32Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-205 consumed (melder_0, 2026-10-18T23:43:33Z, re M2-19): melder_0's 0.2.8258 rebuild - assets and LLM
    bundles, both --check runs OK - carries the closed lane's docs, lessons 42-48 and its release-note bullet,
    which stays directly above the rebuild line; the docs checks passed over both lanes' docs (313 pages,
    check_site and check_seo clean of errors); nothing is owed by that lane. For this task: the packaged system
    documents (4 assets) were rebuilt at 0.2.8258, so this task's edits leave them stale again until the next
    rebuild, which M2-20 asks melder_0's next rebuild to carry.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:898-916
  IMPACT: No wait on melder_0 for the earlier lane; the system-docs asset goes stale with this edit, by the
    owner's waiver of this session's rebuild.
  NEXT: Re-read the teardown source.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:59:08Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Today's root teardown, read whole on 0.2.8258 (the teardown files unchanged since 0.2.8254):
    `Conduit._cleanup_normal_conduit` tears down the cluster facade, the Meld, the ward (the lesser lineage) and the
    SpellSpaces before the root's own store, so consumers held there give leased objects back while the root's
    pools are still registered. `Creations.cleanup` then detaches its maps under the store lock, unregisters every
    pool from ReleaseManagedSpell (`_unregister_managed_quantities`), cleans the pools newest first
    (`_cleanup_managed_quantities`), disposes its registry newest first (`_dispose_disposable_registry`) and raises
    one ExceptionGroup. `ManagedSpellQuantity.cleanup` drains the idle objects and swaps its children maps under its
    lock, then disposes each idle object (newest first) with its recorded children, then the children recorded for
    objects still out, then the orphaned records; it never disposes an out object. After the unregister,
    `ReleaseManagedSpell.release` finds no pool for the class and `_resolve_pool` raises ValueError "<Type> is not a
    managed spell class in any live root: ..."; a cleaned pool's `put_back` raises the torn-down RuntimeError, which
    `ManagedSpellLease.release` reaches; `Conduit._permanent_cleanup` raises the collected store groups as
    ExceptionGroup "Conduit torn down with disposal failures.". So both gaps against the ruling are code facts.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1034-1178
  - src/melder/aether/conduit/conduit.py:805-875
  - src/melder/aether/conduit/creations/creations.py:326-399
  - src/melder/aether/conduit/creations/creations.py:525-578
  - src/melder/aether/conduit/creations/creations.py:1261-1282
  - src/melder/aether/conduit/creations/creations.py:1285-1311
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:202-263
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:553-611
  - src/melder/aether/conduit/creations/release_managed_spell.py:319-355
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/managed_spell_lease.py:103-127
  IMPACT: The documents can state the order, the rule and both gaps from source, not from the earlier probe alone.
  NEXT: Measure both gaps on the current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T23:59:08Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: `probe_root_teardown_scope.py` on 0.2.8258 (CPython 3.14.7t from uv, a /tmp copy of `src/`), the GIL off and
    on, identical rows but object addresses: R1 - a `many` handler melded on the root whose `finish` releases its
    pooled connection: the root's teardown raises ExceptionGroup "Conduit torn down with disposal failures." with one
    leaf, RuntimeError "Failed to dispose object <RequestHandler ...> using method 'finish': ..." chained from the
    not-managed ValueError; the handler's `finish` ran; the connection stays open (never disposed). R2 - two pooled
    sessions, each with a disposal-bearing `many` cursor (children_recorded=2), one released, one out: the teardown
    raises nothing; the idle session and its cursor close; the out session stays open and its cursor closes. R3
    (control) - the same handler in a lesser conduit gives its lease back at the lesser's exit and the root's
    teardown raises nothing, closing the idle connection.
  EVIDENCE:
  - context_compass/artifacts/root_teardown_docs_20261018/probes/probe_root_teardown_scope.py:1-190
  - context_compass/artifacts/root_teardown_docs_20261018/runs/probe_root_teardown_scope_gil0.txt:1-12
  - context_compass/artifacts/root_teardown_docs_20261018/runs/probe_root_teardown_scope_gil1.txt:1-16
  IMPACT: Gap 1 (a root-held consumer's release raises) and gap 2 (an out object's children disposed) are measured on
    the tree the documents describe; the lesser path is the clean one.
  NEXT: Record what the two documents say today.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T23:59:08Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The documents today (index hashes 44e02e45... for src_architecture, 8e44963a... for src_components, both
    regenerated 23:17:42Z): melder_0's 2026-10-18 follow-up already corrected the release-after-teardown failure
    mode in both, so that part of the old plan is done. Still missing or wrong: (a) the ruling is stated nowhere;
    (b) src_architecture Sequence: Cleanup step 7 and src_components Managed Spell Pools' Lifecycle/Cleanup state
    the disposal of out objects' children as plain fact, with no rule and no gap; (c) the root-held consumer's
    ExceptionGroup appears in neither document (only on the user page `docs/intermediate/managed-spells.md`); (d)
    src_architecture's Managed Lease and Release diagram reads "pools first (idle objects + recorded children) ->
    unregistered", the reverse of the code's order (unregister, then clean). Out of scope, recorded only:
    src_components' Creations and SpellSpace Lifecycle/Cleanup cites `creations.py:376-468` for the
    reverse-creation-order walk, which is now `_dispose_disposable_registry` at 525-578.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:37-41
  - context_compass/system_docs/src_architecture.md:1101-1111
  - context_compass/system_docs/src_architecture.md:2540-2556
  - context_compass/system_docs/src_architecture.md:4421-4448
  - context_compass/system_docs/src_components.md:3591-3608
  - context_compass/system_docs/src_components.md:3926-3938
  - context_compass/system_docs/src_components.md:3962-3975
  - context_compass/system_docs/src_components.md:3757-3763
  - context_compass/system_docs/src_components.md:8275-8290
  IMPACT: Fixes the edit list: the rule, both gaps, the diagram order - and nothing else.
  NEXT: The PLAN note, then the NOTICEs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:59:08Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Edits, each anchored on exact text that must occur once, applied by a script that keeps a before-copy and
    refuses when a document's hash moved since this read. src_architecture: one sentence of the rule in "Runtime
    Model: Structure Is the Contract"; Sequence: Cleanup step 7 gains the unregister-first order, the ward and
    SpellSpaces ending before the store, and a pointer to the rule; a new top Operational Invariants entry (the rule,
    today's order, both gaps open with the owner, measured); a Failure Modes entry after the ReleaseManagedSpell one
    (Known, not fixed: the root-held consumer's ExceptionGroup); the Managed Lease and Release diagram's two
    teardown lines in the code's order; a Context / Handoff Summary entry. src_components: one line in Creations and
    SpellSpace; one Lifecycle/Cleanup bullet and one Failure Modes bullet in Managed Spell Pools; one line under
    Flow: Managed Lease -> Release step 5; a Context / Handoff Summary entry. Then both indexes regenerated and
    checked, the Content Preservation Gate (multiset of non-blank lines before and after; only the replaced lines
    may leave), the tooling-path leak check and the citation bounds recipe. The quality rubric is not run: its
    scope is a document created, recomposed or reviewed, and this is a targeted edit. Before the edit: M2-20 to
    melder_0 and M2-21 to melder_1 name the sections.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:246-319
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:10-13
  IMPACT: Every change is small, anchored and reversible; the two code gaps stay with the owner.
  NEXT: Send M2-20 and M2-21, then write the apply script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T00:02:13Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Another writer is in both documents: at 2026-10-19T00:01:12Z src_architecture went from 5306 to 5360 lines
    and src_components from 12275 to 12298, with both indexes still the 23:17:42Z ones (stale). melder_1's S4 story
    names the step - its 00:00:59Z MEASURE note's NEXT is "The system documents (land_s4_docs.py, the citation
    remap, the four indexes), then the graph." Nothing was written to either document by this task. This task holds
    its edits until melder_1's docs pass ends with the indexes regenerated, then re-reads both documents and applies
    its anchored edits to the new text (the apply script refuses unless each document's hash equals the hash its
    fresh index records). M2-22 asks melder_1 for that NOTICE.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md:803-833
  - context_compass/system_docs/src_architecture_index.md:9-19
  - context_compass/system_docs/src_components_index.md:9-19
  IMPACT: No race on the shared documents; this task's edits wait minutes, not hours.
  NEXT: Send M2-22, write the apply script against the new text, apply once melder_1's NOTICE arrives.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Scope: write the owner's teardown ruling into src_architecture and src_components with today's behaviour and the
two gaps marked open. State: ticket opened 2026-10-18T23:49:36Z; nothing edited yet. Next: the board row, M0-205,
then the source re-read.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->

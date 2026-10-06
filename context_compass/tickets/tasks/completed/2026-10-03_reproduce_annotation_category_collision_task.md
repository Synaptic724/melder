

# Task: Reproduce the annotation/category collision on current source and settle the matching semantics

## Metadata
- Task ID: TASK-2026-10-03-reproduce-annotation-category-collision
- Story: STORY-2026-10-03-annotation-type-vs-category-matching
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-03T23:52:00Z
- Updated: 2026-10-04T11:55:00Z

- Completed: 2026-10-04T11:55:00Z
- Summary: Reproduced the collision on 0.2.8221 with a Melder-only probe (2 failed / 2 passed), read the matcher,
  surveyed 441 class-object frames (278 Protocols, 127 plain markers in 28 files), put three options to the owner
  and recorded the DECISION (P2 + concrete-class refusal) that the repair task landed at 0.2.8222. No source
  landed here. Closed by owner directive with the repair task.

## Objective
Run the epic's four-case public-API probe against current Melder source with a Melder-only fixture, read the
Phase 3 matcher and the 0.2.8218 patch record in full, survey how the suites rely on frame-name matching, and
put the semantics options in front of the owner as a STRATEGY_DISCUSSION with a recommendation, so the repair
task starts from a DECISION.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; epic read; the 0.2.8218 patch docs read.
- EXECUTION_BOUNDARY: reads anywhere under src/ and tests/; writes only to this ticket, the story, the epic's
  metadata/notes, the boards and `artifacts/annotation_category_collision_20261003/` (probe, runs, survey).
  Prototypes run in the VM mirror only. No src/ edit in this task.
- DEPENDENCIES: the epic's external evidence (hashes in the epic); the VM env (/tmp/fable_1, CPython 3.14.7t).
- EXIT_GATE: a MEASURE with the probe's result on current source; FACTs naming the matching rule from source;
  a suite survey of frame-name reliance; a STRATEGY_DISCUSSION with options and a recommendation; the owner's
  DECISION recorded; handoff to the repair task.
- FAILURE_ESCALATION: DECISION_REQUEST when the options trade a supported pattern; CONFLICT if the matcher
  file is held by another live agent.

## Scope Boundaries
- In scope: reproduction, matcher read, suite survey, options, decision.
- Out of scope: any src edit, any doc edit. (Owner widened scope 2026-10-03 17:52: the regression module
  lands in tests/ under strict xfail until the repair.)

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner assigned the epic to fable_1 in chat (2026-10-03 17:46 local); story routed.

## Steps / Checklist
- [x] Port the probe to the Melder-only fixture in the VM scratch and run it on current source.
- [x] Read compiler_phase_3.py matching path in full and normalize_frame_key; record the rule as FACT.
- [x] Survey tests/ for consumers resolved through a frame name equal to the annotation (string frames vs
      class-object frames); prototype the candidate predicates in the mirror and run the tiers.
- [x] STRATEGY_DISCUSSION with options, tradeoffs, recommendation; owner's DECISION.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/annotation_category_collision_20261003/ with the ported probe, runs, the survey and prototypes.
- Notes here with the rule, the survey, the options and the decision.

## Files / Paths Impacted
- context_compass/artifacts/annotation_category_collision_20261003/
- this ticket, the story, the epic, attention_board.md, artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `. ~/.fable_1_env && cd $MELDER_MIRROR && $PY -m pytest /tmp/fable_1/spectrum/test_spectrum_category_collision_melder_only.py -q -p no:cacheprovider`

## Risks / Rollback Notes
- fable_0 is mid-lane (flat_warm_body) in the working tree; the mirror is synced from it, so unrelated
  failures may be theirs - classify before reporting. Nothing to roll back: no tree edit.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] A search hit is not a read: the rule is named only from source read in full.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/annotation_category_collision_20261003/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept with the epic's evidence at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-03T23:52:00Z
  TYPE: FACT
  CLAIM: The epic's saved evidence (command_2, installed 0.2.8220): a class or string `Spectrum` annotation on a
  consumer resolves when the competing Toolbox is bound in another category and raises a Phase 3 ambiguity
  (candidates Spectrum and Toolbox) when Toolbox shares spellframe "spectrum"; 4 tests, 2 passed / 2 failed. The
  0.2.8218 patch record states the current rule: a spell is a candidate when
  `normalize_frame_key(annotation)` equals its address frame key (spellframe, else its own name) OR its type
  key (class name) - and its own "Before" section records that the pre-0.2.8218 object path matched a frame
  only by identity (`spellframe is annotation`), so a string category "spectrum" did not match a class
  annotation `Spectrum` before 0.2.8218 and does now. Current-source behaviour is UNKNOWN until run.
  EVIDENCE:
  - tickets/epics/2026-10-03_annotation_category_provider_collision_epic.md:14-33
  - tickets/epics/2026-10-03_annotation_category_provider_collision_epic.md:60-75
  - system_docs/patches/completed/annotation_address_matching_2026_10_03/component_patch_spellcompiler_phase3.md:7-24
  IMPACT: the regression is scoped to the 0.2.8218 widening of the object path; the string path's frame-name
  matching predates it, which is the compatibility question the owner must rule on.
  NEXT: port the probe (class + string annotations x same/other category) and run it on the mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T23:58:00Z
  TYPE: MEASURE
  CLAIM: REPRODUCED ON CURRENT SOURCE (working tree at 0.2.8221, Melder-only reset fixture, CPython 3.14.7t): the
  ported four-case probe gives 2 failed / 2 passed - [True-class] and [True-string] raise RuntimeError
  "SpellCrafter Phase 3: multiple DI candidates found for parameter 'spectrum' ... Candidates: Spectrum, Toolbox"
  at the consumer's late bind (Phase 3 runs eagerly for a late bind), [False-class] and [False-string] resolve
  the Spectrum provider. Same shape as the saved 0.2.8220 receipt. Note: the quoted "Spectrum" annotation is
  resolved to the class at read time when the name is bound in the module (the error prints the class), so a
  TYPE_CHECKING-only string needs an unbound name in the regression set.
  EVIDENCE:
  - artifacts/annotation_category_collision_20261003/test_spectrum_category_collision_melder_only.py:1-104
  - artifacts/annotation_category_collision_20261003/probe_current_source_0_2_8221.xml:1-1
  IMPACT: the defect is live on the tree; the matcher read can start from a live repro.
  NEXT: read compiler_phase_3.py 185-495 and 761-887 and normalize_frame_key in full; record the rule as FACT.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:12:00Z
  TYPE: DECISION
  CLAIM: Owner directed (chat, 2026-10-03 17:52 local) that the problems be repeated as a regression test in this
  repository; this task's "no test added to tests/" boundary is widened by that directive. Landed
  tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py (CRLF, tree
  convention): four defect cases under `xfail(strict=True, reason=EPIC-...)` - the matrix's two shared-category
  cases (class and resolvable-string annotation), a truly unbound string annotation (a consumer class in its own
  module that never imports Spectrum, so Phase 3 sees annotation='Spectrum'), and the silent lone-member case
  (Toolbox alone in "spectrum" is handed to `spectrum: Spectrum` today; ruled behaviour: UnresolvedInputError
  without an override, the supplied object with one) - plus five guards that pass today and must keep passing:
  the two controls, a class-object frame as a shape label (`spellframe=IService` satisfies `svc: IService`),
  two providers of the annotated type still an ambiguity, explicit address melds unchanged. With --runxfail every
  defect case fails for the reported reason ("multiple DI candidates ... Spectrum, Toolbox"; "DID NOT RAISE
  UnresolvedInputError"). Strict xfail keeps the shared suite green for the other live agents while the lane is
  open and fails loudly (XPASS) the moment the matcher is repaired with a marker still on.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py:1-279
  - artifacts/annotation_category_collision_20261003/test_annotation_category_collision_integration.py:1-279
  - artifacts/annotation_category_collision_20261003/probe_current_source_0_2_8221.xml:1-1
  IMPACT: the defect is pinned in the repository in the owner's ruled form; the repair flips four markers.
  NEXT: read the matcher in full (compiler_phase_3.py 147-495, 761-887; normalize_frame_key) and record the rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:30:00Z
  TYPE: FACT
  CLAIM: THE RULE, from source. `CompilerPhase3._matches_annotation` (and the pass index `_build_candidate_index` /
  `_indexed_annotation_candidates`, one `by_key` bucket map) accept a spell when `normalize_frame_key(annotation)`
  (ForwardRef -> name; class -> `__name__`; string -> itself; lowercased) is in `_spell_keys(spell)` = {frame key
  (spellframe, else own name), type key (class name / existing object's class name)}; the same predicate serves
  SINGLE_BY_ANNOTATION (`_resolve_single_by_annotation`, ambiguity on >1 resolvable candidates, UNRESOLVED_INPUT on
  0) and COLLECTION_BY_ANNOTATION (`_resolve_collection_by_annotation`, all matches). Before 0.2.8218 (git 4ddf7530f)
  a class annotation matched `spell.spell is annotation` or `frame is/== annotation` (object identity), and a string
  annotation matched `spell_name`, a string frame or a class frame's `__name__` by exact, case-sensitive equality -
  so MelderOps' lowercase category "spectrum" never matched the class `Spectrum` nor the string "Spectrum". The
  0.2.8218 widening to lowercased names on both kinds is the regression. Collections, SpellMap defaults
  (`_resolve_spellmap_default`) and `_dependency_key_for_dep` (the watcher key) are separate paths.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:186-284
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:310-412
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:413-535
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:630-673
  - artifacts/annotation_category_collision_20261003/fix/compiler_phase_3_pre8218_matches_annotation.txt:1-70
  IMPACT: the predicate is one function pair shared by both paths, so one change keeps indexed and scan parity.
  NEXT: prototype the type-provider predicate and survey the tiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:30:00Z
  TYPE: MEASURE
  CLAIM: OPTION B PROTOTYPED in the mirror (fix/apply_type_providers.py: `_spell_type_keys` = class name, plus the
  frame key only when the spellframe is a class/Protocol object; `_matches_annotation(..., type_providers_only)`;
  a second `by_type_key` bucket map; the single resolver uses type keys on both the indexed and scan paths; the
  collection resolver is unchanged). Regression module 9/9 with --runxfail. Tiers: unit 8868 passed with 2
  failures - the 0.2.8218 index-layout pin (`{"by_key"}`) and fable_0's pending asset stamp; component 2293 passed;
  integration 2025 passed with 6 failures - the four defect cases XPASSing under strict xfail (expected at landing)
  plus TWO reliance findings: `test_future_annotations_string_literal_frame_annotation_resolves_single`
  (`repo: "extra_frame"` - a string annotation naming a string category expects its single member; the only
  such annotation in the suite) and my own M2 guard (ProviderV2 bound under the string frame "provider" to satisfy
  `p: Provider`; B wants `spellframe=Provider`, the class object). Other tier 250 passed. The README's spellframe
  section already distinguishes "a plain string when you just want grouping" from "a Protocol when you want a
  shape"; its 0.2.8218 DI sentence ("a spell bound under a spellframe to that frame's name as well") is what B
  changes.
  EVIDENCE:
  - artifacts/annotation_category_collision_20261003/fix/apply_type_providers.py:1-300
  - artifacts/annotation_category_collision_20261003/fix/prototype_option_b.diff:1-200
  - artifacts/annotation_category_collision_20261003/fix/survey_option_b.txt:1-22
  - tests/integration/melder/spellbook/test_spellbook_integration_future_annotations_more.py:577-628
  - README.md:387-423
  IMPACT: B fixes all four defect cases with one predicate and costs exactly one tested idiom (a string-literal
  category annotation on a single socket) plus one of my guards; the explicit form of that idiom (SpellMap default)
  is already tested in the same file.
  NEXT: STRATEGY_DISCUSSION to the owner; DECISION before any tree edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:50:00Z
  TYPE: FACT
  CLAIM: Relayed by the owner from fable_0 (2026-10-03 18:08 local): (1) the codex bridge lists no chat for
  melder_2/muse_0 in this repository, so a notch notice to them lives in the ticket, the board row and the release
  note, as for the earlier notches; (2) `llm_support/_builder.py --check --include-untracked` now reports the `tests`
  bundle fingerprint moved because this lane's regression module landed on disk at 23:56Z, after fable_0's bundle
  build; `src` and `other` still check OK; fable_0 did not touch this lane. The `tests` drift is this lane's and is
  taken by this lane's landing rebuild (rebuild last, after the repair, docs and closures).
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py:1-279
  - special_instructions/agent_contribution_guide.md:75-87
  - special_instructions/codex_mcp.md:8-20
  IMPACT: nothing to do now; the bundle check is expected red on `tests` until this lane rebuilds at landing.
  NEXT: STRATEGY_DISCUSSION note with the options, the survey and the recommendation; DECISION_REQUEST to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-04T01:00:00Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Held in chat with the owner (2026-10-03 18:22-19:00 local). Objective: a type annotation must never read a
  category as a provider set; keep every intended behaviour. Facts from source: a Protocol cannot be bound as a
  resolvable spell (bind.py:670-675); a Protocol spellframe runs a bind-time structural check of the members declared
  directly on the Protocol (presence, callability) for class and existing-object spells (bind.py:738-754, 1265-1314) -
  not inherited members, annotation-only fields, signatures or function spells; 441 class-object frames in the tree:
  278 Protocols, 127 plain marker classes used as labels in 28 test files, 22 unresolvable, 0 ABCs (survey script in
  the artifact folder). Options put: P1 Protocol frame = label + check, singles by type only (Protocol-typed
  parameters could never resolve by annotation - rejected); P2 the annotation's kind decides (class -> type,
  Protocol -> recorded implementers, TYPE_CHECKING string -> type-or-contract by name, never a string category;
  collections -> the group their kind names); P3 = P2 + a deeper Protocol check (own ticket). Owner rulings: a
  spellframe is a label or categorizer and nothing groups by class name or binding; a Protocol frame is a label AND a
  contract; a concrete class is not a valid spellframe; the binding records the frame kind so Phase 3 differentiates.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:664-675
  - src/melder/aether/spellbook/bind/bind.py:731-754
  - src/melder/aether/spellbook/bind/bind.py:1265-1314
  - artifacts/annotation_category_collision_20261003/fix/survey_option_b.txt:1-22
  - artifacts/annotation_category_collision_20261003/class_frame_survey.txt:1-16
  IMPACT: the repair is P2 plus the bind-time refusal of non-Protocol class frames, with the recorded kind on the
  Spell as the single source Phase 3 reads.
  NEXT: record the DECISION; open the repair task and its patch lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T01:00:00Z
  TYPE: DECISION
  CLAIM: OWNER DECISION (chat, 2026-10-03 19:00 local: "yeah this all makes sense go ahead and implement all of this
  please") on the change set: (1) the binding records the frame kind - `category` (string) or `contract` (Protocol) -
  and the Protocol the spell was structurally checked against; (2) bind refuses a class-object spellframe that is not
  a Protocol (breaking change, led as such in the release note) and the 127 plain-class test frames are swept by
  codemod; (3) Phase 3 matches by kind: a class annotation selects the type, a Protocol annotation its recorded
  implementers, a TYPE_CHECKING string the type or contract by name and never a category; collections gather the group
  their annotation's kind names (category members / contract implementers / that class); one predicate for the indexed
  and scan paths; cache generation 20; (4) the four strict-xfail defect cases flip, predicate and parity unit tests
  are added, `repo: "extra_frame"` converts to a SpellMap default, the rebind M2 guard is rewritten with a Protocol;
  README, architecture invariant, components entry, graph, notch, release note, rebuild. (c) Follow-ups opened as
  their own backlog tickets, not implemented here: the deeper Protocol check (inherited members, annotation-only
  fields, arity) and an explicit `implements=(...)` bind argument. The pre-0.2.8218 "class-object frame satisfies a
  same-named single annotation by identity" idiom is retired with (2).
  EVIDENCE:
  - tickets/epics/2026-10-03_annotation_category_provider_collision_epic.md:39-44
  - artifacts/annotation_category_collision_20261003/fix/survey_option_b.txt:1-22
  - artifacts/annotation_category_collision_20261003/class_frame_survey.txt:1-16
  IMPACT: the story's EXIT_GATE "the semantics are a DECISION the owner confirmed" is met; the repair task opens with
  its patch lane; this task's remaining deliverable is the handoff.
  NEXT: create the repair task and the patch lane (architecture, component x2, code description), route the board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
STATE 2026-10-03T23:52:00Z: IN_PROGRESS. Reproduction next. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

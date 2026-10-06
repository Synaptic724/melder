"""Open the flat-warm-body lane (S9 + S11; S2a parked): story, task, board row/detail, epic note, S2a story parked."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, insert_after_regex, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TS = now_utc()
STORY_REL = "tickets/stories/2026-10-03_flat_warm_body_constants_story.md"
TASK_REL = "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md"
S2A_REL = "tickets/stories/2026-10-01_existing_object_constants_story.md"
S2A_BACKLOG_REL = "tickets/stories/backlog/2026-10-01_existing_object_constants_story.md"
EPIC_REL = "tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md"
BOARD = os.path.join(CC, "attention_board.md")

STORY = f"""# Story: Flat warm body - site and store constants (S9) and key identity (S11) on every shared site

## Metadata
- Story ID: STORY-2026-10-03-flat-warm-body-constants
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: {TS}
- Updated: {TS}

## User Narrative
As the Melder owner, I want every shared site of a site plan (a unique or per-conduit provider read by a
consumer's plan) to stop paying a tuple index and an attribute read per creation for things that are fixed when
the plan is hydrated - the site's Spell object and, in an automatic world, its owner store - and to look its
instance up by a key object that is identical to the store's key, so that the warm path of every root over
shared providers gets cheaper without a store change, a guard or a posture-dependent branch in the body.

## Value / MRP Alignment
Owner (2026-10-03): existing objects are rare, so S2a alone helps little; take the parts that help "everything in
general". S9 and S11 apply to every shared site of every dict-mode and direct-mode plan: S9 removes
`spells[i]` and `._owner_creations` from the body (HYPOTHESIS -8..-12 ns per shared site, from the epic's
catalogue), S11 makes the store lookup hit the dict's identity fast path for cache-restored plans (MEASURED micro
-1.5..-2 ns per lookup). Both are certified in the harness before any src edit (owner: "test it first").

## Ticket Contract
- ENTRY_GATE: the owner's word (2026-10-03: "go ahead and implement the next steps ... just make sure you test
  it first"); the harness certifies S9 and S11 on the five shapes BEFORE the patch docs; patch docs (component:
  SpellCompiler codegen, site-plan lowering and the hydrators) written and linked before any src edit.
- EXECUTION_BOUNDARY: `tests/experimentation/codegen_strategy_certification.py` (S9/S11 transforms),
  `site_plan_lowering.py` (shared-site emission and the plan namespace), the hydrators that bind the plan
  namespace (generalized, many_only; the cache-restored path), `caching_system.py` (generation), tests, docs.
- DEPENDENCIES: S8 landed (0.2.8217); the certification table; the posture read at hydration (transfer repoints
  the owner store in dynamic posture only).
- EXIT_GATE: the harness table with S9/S11 columns; differential tests (same objects, same errors; a dynamic
  transfer test proving the store read survives in dynamic posture); suites green; harness re-run; owner-run
  gauntlet.
- FAILURE_ESCALATION: DECISION_REQUEST if the harness shows S9 within noise on every shape (then S11 alone, or
  nothing, ships); BLOCKER if a hydrator cannot bind the live key objects without a manifest format change.

## Requirements (Functional)
- A shared site reads `cI._creations.get(sidI)` with `cI` bound at hydration in automatic posture (the owner
  store cannot move) and `sI._owner_creations` read per creation in dynamic posture (transfer repoints it).
- `sidI` is the live Spell's `spell_id` object in every plan namespace, including cache-restored plans.
- Every other line of every plan is unchanged; the same objects and errors as today.

## Requirements (Non-Functional)
- Measured on the VM first; a strategy ships only when the harness shows a win above noise on the shapes it
  applies to; generation bump retires the old executors.

## Scope Boundaries
- In scope: S9 and S11 in the normal plan and the key-set plans; the harness transforms; tests; docs.
- Out of scope: S2a existing-object constants (parked by the owner's remark - rare; its own backlog story);
  S10 subscript hits (low value); S12 direct emission of generic steps; the doors (next story).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's word ({TS}); the certification task is routed on the board.

## Dependencies / Related Work
- tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md (Non-PGO Strategy Catalogue: S9, S11)
- tickets/stories/backlog/2026-10-01_existing_object_constants_story.md (S2a, parked)
- artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-10-03-certify-and-implement-site-store-constants - harness S9/S11 columns, then the
      emitter and hydrator edits with tests. {TASK_REL}
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Harness table recorded before the edit; same objects on every shape after it; the dynamic transfer test green;
  measured plan delta recorded; owner-run numbers recorded.

## Validation / Test Plan
- Harness (before and after); unit tests on the emitter output per posture; component tests through real
  conjures in both postures including a transfer in dynamic posture and a cache full hit; the suites sharded.

## UX / API / Data Notes
- No public API change; cache generation bump when the emitted body changes.

## Risks / Mitigations
- A dynamic transfer repoints the owner store after hydration -> the constant is automatic-only; the dynamic
  body keeps the read; a test proves it.
- The harness measures a transform of the captured body, not the shipped emitter -> the shipped body is
  re-measured by the same harness after landing.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.
- [ ] No src edit before the harness verdict, the patch docs and the mapping note.

## Open Questions
- Does any automatic-world path repoint a spell's owner store after conjure (upgrade? cluster?) - to verify in
  source before the constant is emitted.

## Decision Log
- {TS} (owner): existing objects are rare; implement what helps in general, test first, ignore the PGO
  epic. fable_0: S9 + S11 as this story, S2a parked, the door lane next.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/flat_warm_body_20261003/ (harness runs, apply scripts, logs)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - shared-site emission; plan namespace; hydration constants; key identity
- IF_UNKNOWN: none

## Notes
- DATETIME: {TS}
  TYPE: PLAN
  CLAIM: Opened on the owner's word. Order: read the shared-site emission and the plan namespace (lowering),
    then the hydrators' namespace binding (live and cache-restored); add S9/S11 transforms to the harness and
    measure; patch docs; implement; tests; land. S2a parked in the backlog with the owner's remark.
  EVIDENCE:
  - tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md:190-215
  - tests/experimentation/codegen_strategy_certification.py:183-245
  IMPACT: One emitter pass over every shared site; the doors follow.
  NEXT: the task's investigation read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE {TS}: IN_PROGRESS. The certification/implementation task is the active lane. Resume from its
latest STATE line.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
"""

TASK = f"""# Task: Certify S9/S11 in the harness, then emit site and store constants and live key objects

## Metadata
- Task ID: TASK-2026-10-03-certify-and-implement-site-store-constants
- Story: STORY-2026-10-03-flat-warm-body-constants
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: {TS}
- Updated: {TS}

## Objective
The certification harness gains S9 (site Spell and, in automatic posture, owner-store namespace constants) and
S11 (live `spell_id` key objects) columns and measures them on the five shapes; when the table shows a win above
noise, the lowering stops emitting `cI = spells[i]._owner_creations` on the warm path (binding `sI` and, in
automatic posture, `cI` at hydration) and every plan namespace, cache-restored ones included, binds `sidI` to the
live Spell's `spell_id` object. Same objects, same errors; a dynamic transfer still repoints the read.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's word (2026-10-03); the harness table BEFORE the patch
  docs; patch docs under `system_docs/patches/active/flat_warm_body_2026_10_03/` linked here with the mapping
  note BEFORE any src edit.
- EXECUTION_BOUNDARY: `tests/experimentation/codegen_strategy_certification.py`,
  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`,
  `.../site_plan_override_runtime.py`, the hydrators under `.../strategies/*/hydration/` and the manifest cache
  loader (`manifest_creation_cache.py`) where the namespace is rebuilt, `caching_system.py` (generation), tests,
  the two canonical system documents and indexes, graph descriptors, release note, `__version__`.
- DEPENDENCIES: S8 (0.2.8217) and the matcher (0.2.8218) landed; the structural/executor cache (0.2.8220).
- EXIT_GATE: harness table recorded; red-to-green emitter unit tests; component tests in both postures (incl. a
  dynamic transfer and a cache full hit); the suites green on the VM copy (sharded); landed with notch, release
  note, docs, graph, assets and bundles with --check OK; owner-run suites requested.
- FAILURE_ESCALATION: DECISION_REQUEST if S9 is within noise on every shape; BLOCKER if the cache-restored
  namespace cannot carry live key objects without a manifest format change.

## Scope Boundaries
- In scope: the harness columns, the emitter and hydrator edits, the generation bump, tests, docs, notch, note.
- Out of scope: S2a (parked), S10, S12, the doors.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's word ({TS}).

## Steps / Checklist
- [ ] Read the shared-site emission and the plan namespace in `site_plan_lowering.py` (render, _place,
      _emit_context, _emit_shared_hit, _emit_miss, the namespace build) and the hydrators' namespace binding on
      the live and cache-restored paths; verify in source whether an automatic-world path can repoint an owner
      store after hydration; one FACT note.
- [ ] Harness: S9 and S11 transforms (and S9+S11), measured on the five shapes, interleaved; MEASURE note.
- [ ] Patch docs and the mapping note (only when the table says ship).
- [ ] Implement on the VM copy; emitter unit tests; component tests (both postures, transfer, full hit); shards.
- [ ] Land on the tree (CRLF), notch above `__version__`, release-note section, docs, graph; patch docs promoted
      and archived; assets and LLM bundles LAST; both checks OK; post-landing shards.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The harness table with S9/S11; the emitter and hydrator changes; tests; docs; release-note entry; notch.

## Files / Paths Impacted
- tests/experimentation/codegen_strategy_certification.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/ (hydrators, manifest cache loader)
- src/melder/utilities/caching_system/caching_system.py
- tests/ (unit, component)
- context_compass/system_docs/patches/active/flat_warm_body_2026_10_03/
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 tests/experimentation/codegen_strategy_certification.py`
  - `python -X gil=0 -m pytest tests/unit/melder/spellbook/spell_compiler tests/component/melder/aether/conduit -q`

## Risks / Rollback Notes
- A transfer in dynamic posture repoints the owner store -> the constant is emitted for automatic posture only.
- Rollback: re-emit the per-creation read; keep the generation bumped.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the harness verdict, the patch docs and the mapping note.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

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
  - artifacts/flat_warm_body_20261003/ (harness runs, apply scripts, logs)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: patch docs promoted and archived at landing; artifacts kept.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - shared-site emission; plan namespace; hydration constants; key identity
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: {TS}
  TYPE: PLAN
  CLAIM: Lane opened. Everything about the shared-site emission and the hydrators is UNKNOWN until read; the
    harness measures before any design is written down as a patch.
  EVIDENCE:
  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:1-40
  IMPACT: Reading order fixed: lowering first, hydrators second, harness third.
  NEXT: read the shared-site emission and the namespace build in `site_plan_lowering.py` whole (chunks).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE {TS}: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
"""

for text in (STORY, TASK):
    bad = check_line_lengths(text)
    if bad:
        raise SystemExit(f"lines over cap: {bad}")
for rel, text in ((STORY_REL, STORY), (TASK_REL, TASK)):
    path = os.path.join(CC, rel)
    assert not os.path.exists(path), rel
    write_text(path, text, "\n")

# park S2a
s2a_path = os.path.join(CC, S2A_REL)
text, nl = read_text(s2a_path)
text = replace_once(text, "- Status: ready\n", "- Status: ready (parked)\n", "s2a status")
text = replace_once(text, "- Updated: 2026-10-01T00:55:51Z\n", f"- Updated: {TS}\n", "s2a updated")
note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Parked by the owner's remark (2026-10-03: existing objects are very rare); the general parts of the\n"
    "    emitter pass (S9, S11) ship through tickets/stories/2026-10-03_flat_warm_body_constants_story.md. Reopen\n"
    "    on explicit request; the open question (purge of an existing-object registration) stays open.\n"
    "  EVIDENCE:\n"
    "  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:1-40\n"
    "  IMPACT: No lane; not routed.\n"
    "  NEXT: none unless reopened.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + note + "## Closure Confirmation\n", "s2a notes end")
text = text.rstrip("\n").replace("\n## Project-Specific Additions",
    f"\nSTATE {TS}: READY (parked). Existing objects are rare (owner); S9/S11 ship separately. Not routed.\n\n## Project-Specific Additions") + "\n"
write_text(s2a_path, text, nl)
os.makedirs(os.path.join(CC, "tickets/stories/backlog"), exist_ok=True)
shutil.move(s2a_path, os.path.join(CC, S2A_BACKLOG_REL))

# epic
epic_path = os.path.join(CC, EPIC_REL)
text, nl = read_text(epic_path)
text = replace_once(
    text,
    "- [ ] Story: STORY-2026-10-01-existing-object-constants (S2a) - existing-object sites bound as constants at\n"
    "      hydration. tickets/stories/2026-10-01_existing_object_constants_story.md\n",
    "- [ ] Story: STORY-2026-10-03-flat-warm-body-constants (S9 + S11) - site and store constants and live key\n"
    f"      objects on every shared site. {STORY_REL}\n"
    "- [ ] Story: STORY-2026-10-01-existing-object-constants (S2a) - PARKED (owner, 2026-10-03: existing objects\n"
    f"      are rare). {S2A_BACKLOG_REL}\n", "epic stories")
text = replace_once(text, f"- Updated: ", f"- Updated: ", "noop")
epic_note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-03): \"existing objects are very rare but sure, if it helps with everything in general ...\n"
    "    implement the next steps, ignore the PGO epic, test it first.\" fable_0: the emitter pass is S9 + S11 (every\n"
    "    shared site; certified in the harness before the patch docs), S2a is parked in the backlog, the door lane\n"
    "    follows (audit, harness, D5 then D1-D3); the PGO epic stays queued and untouched.\n"
    "  EVIDENCE:\n"
    f"  - {STORY_REL}:1-40\n"
    "  IMPACT: Milestone 3 is redefined as the flat-warm-body story (S9/S11); S2a leaves the exit gate.\n"
    "  NEXT: the certification/implementation task's investigation read.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 8\n\n"
)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + epic_note + "## Closure Confirmation\n", "epic notes end")
text = replace_once(text, "- [ ] Milestone 3: S2a shipped and turned in.\n",
                    "- [ ] Milestone 3: the flat warm body (S9 + S11) shipped and turned in; S2a parked (owner, 2026-10-03).\n",
                    "milestone 3")
text = text.rstrip("\n").replace("\n## Project-Specific Additions",
    f"\nSTATE {TS}: IN_PROGRESS. The flat-warm-body story (S9/S11) is the active lane; S2a parked; PGO epic ignored.\n"
    "Resume from the task's latest STATE line.\n\n## Project-Specific Additions") + "\n"
import re as _re
text = _re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=_re.MULTILINE)
write_text(epic_path, text, nl)

# board
board, nl = read_text(BOARD)
row = (
    "| flat_warm_body | in_progress | discovery | claude | fable_0 | none | "
    "Read the shared-site emission and the hydrators' namespace binding, then add S9/S11 to the harness and measure "
    "before any patch doc. | "
    "S9 (site/store constants) and S11 (live key objects) certified on the five shapes; if they win, emitted with "
    "tests, docs and a notch; S2a parked. | "
    "Harness verdict recorded (ship or DECISION_REQUEST), then landed and in review. | "
    f"{TASK_REL} | {TS} | REQUIRED |\n"
)
board = replace_once(board, "<!-- BEGIN USER-DEFINED: active_items -->\n",
                     "<!-- BEGIN USER-DEFINED: active_items -->\n" + row, "active_items begin")
detail = (
    "- flat_warm_body: SWITCH_TRIGGER is the harness verdict (S9/S11 within noise -> DECISION_REQUEST), or the\n"
    "  landing and turn-in; then the door lane story opens (audit first). The PGO epic stays queued with no row\n"
    "  (owner: ignore it). RESUME_HIERARCHY: tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md ->\n"
    f"  {STORY_REL} ->\n"
    f"  {TASK_REL}.\n"
)
board = insert_after_regex(board, r"^### Active Attention Details\n\n", detail, "details head")
write_text(BOARD, board, nl)
print("opened", TS)

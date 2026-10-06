"""Open the executor-cache world-stamp lane: task ticket, board row and detail, S8 cross-note."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, insert_after_regex, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md"
TASK = os.path.join(CC, TASK_REL)
BOARD = os.path.join(CC, "attention_board.md")
S8_TASK = os.path.join(CC, "tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md")

TS = now_utc()

TICKET = f"""# Task: Require the world stamp for an executor-cache full hit - a changed world never replays a stale executor

## Metadata
- Task ID: TASK-2026-10-03-require-world-stamp-for-executor-cache-full-hit
- Story: none (standalone defect task; the RISK found in the S8 lane, owner-directed 2026-10-03)
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: {TS}
- Updated: {TS}

## Objective
The conduit creation-cache bundle records the world it was compiled in - the structural tier's world stamp (sorted
pool ids, posture, sorted borrowed ids) - and the executor tier admits a full hit only when the live world carries the
same stamp. A world that differs only by an existing creation or a non-resolvable definition (ids the executor tier
never counted) no longer hydrates a consumer's executor compiled when nothing provided one of its parameters: it
recompiles phases 8-11 for every eligible spell and re-stages the bundle under the new stamp, exactly as a missing
live spell does today. Generation 19 retires bundles without a stamp. Regression tests, unit and component, hold the
rule: classification with a matching and a mismatching recorded stamp, the stamp recorded at staging, the envelope
round trip; and through a real conjure with caching on: a warm cache from a Worker-only world, then a bare existing
Service beside Worker melds a Worker holding that service, the inverse (provider removed) raises
UnresolvedInputError, and a repeat world stays a full hit that leaves the bundle untouched.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's word (2026-10-03: "add tests please and lets properly fix
  the defects you found too"); patch docs under `system_docs/patches/active/executor_cache_world_stamp_2026_10_03/`
  written and linked here with the mapping note BEFORE any src edit.
- EXECUTION_BOUNDARY: `src/melder/utilities/caching_system/caching_system.py` (envelope field `world_stamp`, the
  `world_stamp` property, `set_world_stamp`, generation 19), `src/melder/aether/spellbook/spellbook_creation_system.py`
  (`_build_conjure_cache_state`, `_stage_spell_payloads_at_conjure_end`), tests (the cache runtime verification unit
  file, the caching-system envelope tests, the schema-version pin, one new component file), the two canonical system
  documents and their indexes, graph descriptors, `release_docs/next_version_release.md`, `__version__`.
- DEPENDENCIES: S8 and the matcher landed (0.2.8217 / 0.2.8218); `StructuralSnapshot.world_stamp`. One writer per
  source file: fable_1's rebind lane reads the creation system's target pass next; CONFLICT (no edit) if that lane
  claims `spellbook_creation_system.py` before this lands.
- EXIT_GATE: red-to-green regression tests (unit and component); the touched suites green on the VM copy (sharded);
  landed with the notch, the release-note section, docs, graph, assets and bundles with --check OK; owner-run suites
  requested.
- FAILURE_ESCALATION: DECISION_REQUEST if the stamp cannot be computed where the executor tier classifies (posture
  unbound) or an existing cache test depends on a full hit across a changed world; BLOCKER if the envelope cannot
  carry the field without a format change beyond the generation bump.

## Scope Boundaries
- In scope: the envelope field, the classification rule, the staging write, generation 19, tests, docs, notch, note.
- Out of scope: the structural tier (its stamp and replay rule are reused unchanged); the Autofac-strict tightening
  (owner: not wanted); a per-spell resolution fingerprint (a finer key than the world - not needed, since a missing
  live spell already recompiles the whole eligible set); fable_1's rebind-after-first-meld defect (its own lane).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's word ({TS}); the RISK note of the S8 task (reproduced
  twice, cold cache resolves) is the entry evidence.

## Steps / Checklist
- [ ] Re-read in full: `_build_conjure_cache_state`, `_load_cached_spell_payloads_for_conjure`, the cache branches
      of `_activate_conjured_conduit`, `_stage_spell_payloads_at_conjure_end`, the emit-at-conjure-end path,
      `_build_structural_cache_state`, the CachingSystem envelope methods and properties, `StructuralSnapshot.
      world_stamp` / `classify`, and the cache tests' stubs and helpers; one FACT note.
- [ ] Patch docs (architecture, component Spellbook Core / caching, code description of the admission) and the
      mapping note; link them here.
- [ ] Reproduce red on the working copy (the component test), then the anchored apply script (src + tests); run the
      touched suites sharded; FACT and MEASURE notes.
- [ ] Land on the tree (CRLF), notch above `__version__` (0.2.8218 now), release-note section, docs, graph
      descriptors; promote and archive the patch docs; rebuild assets and LLM bundles LAST; both checks OK;
      post-landing shards on a fresh copy.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The `world_stamp` envelope field with its property and setter; the full-hit rule on the stamp; the staging write;
  generation 19.
- Tests: unit (classification, staging, envelope round trip, the history pin) and component (real conjures, caching
  on, red-to-green on the reproduced defect and its inverse; the repeat-world full hit).
- Patch docs promoted into `src_architecture.md` / `src_components.md`; release-note section; notch.

## Files / Paths Impacted
- src/melder/utilities/caching_system/caching_system.py
- src/melder/aether/spellbook/spellbook_creation_system.py
- tests/unit/melder/spellbook/test_cache_runtime_verification.py
- tests/unit/melder/utilities/ (caching-system envelope tests)
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py
- tests/component/melder/spellbook/ (new file)
- context_compass/system_docs/patches/active/executor_cache_world_stamp_2026_10_03/
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest tests/unit/melder/spellbook tests/unit/melder/utilities -q`
  - `python -X gil=0 -m pytest tests/component/melder/spellbook tests/integration/melder/spellbook -q`

## Risks / Rollback Notes
- A world identical in ids, posture and borrowed ids but with a different payload set is still classified by the
  matched / missing sets (unchanged). A stamp that changes with no payload change must still be persisted, or every
  later conjure recompiles: the staging write flags the emit when the recorded stamp changes.
- Rollback: drop the stamp requirement from the full-hit rule and keep the generation bumped.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the patch docs and the mapping note.
- [ ] No edit of a source file another lane has claimed (one writer per file).

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
  - artifacts/executor_cache_world_stamp_20261003/ (lane scripts, red/green and shard logs)
  - system_docs/patches/active/executor_cache_world_stamp_2026_10_03/ (patch docs; written before the edit)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs promoted and archived at landing; artifacts kept.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - creation-cache classification; executor payload staging; world stamp; cache generation
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: {TS}
  TYPE: PLAN
  CLAIM: Lane opened on the owner's word. Entry evidence: the S8 task's RISK note - with caching on, a world whose
    only difference is a bare existing Service beside Worker(service: Service) is served Worker's executor compiled
    when nothing provided `service` (TypeError at meld), while a cold cache resolves it. Design candidate, UNKNOWN
    against the source until the two tiers are re-read: the executor tier classifies a full hit on payload ids
    only (live = resolvable, non-existing-creation spells), so ids outside that set change the world without
    changing the classification; the structural tier already stamps the world (pool ids, posture, borrowed ids).
    Candidate fix: the executor bundle envelope records that stamp at staging and a full hit requires it.
  EVIDENCE:
  - tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md:244-268
  - src/melder/aether/spellbook/spellbook_creation_system.py:616-721
  IMPACT: Fixes the reading order: classification, loading, staging and emit in the creation system, then the
    envelope, then the structural stamp, then the tests' stubs.
  NEXT: re-read those methods whole (chunks <= 500 lines) and write one FACT note with the exact admission rule and
    the write path for the stamp.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE {TS}: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
"""

bad = check_line_lengths(TICKET)
if bad:
    raise SystemExit(f"ticket lines over cap: {bad}")
if os.path.exists(TASK):
    raise SystemExit("task already exists")
write_text(TASK, TICKET, "\n")

# --- attention board: new row, new detail, refreshed next on the two review rows ---
board, nl = read_text(BOARD)
row = (
    "| executor_cache_world_stamp | in_progress | discovery | claude | fable_0 | none | "
    "Re-read the two cache tiers and the staging path in full, then the patch docs and the mapping note "
    "before the apply script. | "
    "The executor cache admits a full hit only on the recorded world stamp; a changed world recompiles 8-11 "
    "and re-stages; unit + component regression tests; generation 19; landed with notch and docs. | "
    "Landed and in review, or a DECISION_REQUEST, or a CONFLICT on the file overlap with fable_1's lane. | "
    f"{TASK_REL} | {TS} | REQUIRED |\n"
)
board = replace_once(board, "<!-- BEGIN USER-DEFINED: active_items -->\n",
                     "<!-- BEGIN USER-DEFINED: active_items -->\n" + row, "active_items begin")

old_s8_next = ("Owner runs the full-tree suites and the gauntlet on 0.2.8218 and turns S8 in; then S2a (with S9/S11) "
               "opens with its patch docs. Owner's call on the conjure-cache staleness defect (RISK note).")
new_s8_next = ("Owner runs the full-tree suites and the gauntlet on 0.2.8218 and turns S8 in; then S2a (with S9/S11) "
               "opens with its patch docs. The conjure-cache staleness defect (RISK note) is worked under "
               "executor_cache_world_stamp.")
board = replace_once(board, old_s8_next, new_s8_next, "s8 next")
old_m_next = ("Owner runs the full-tree suites on 0.2.8218 and turns it in; decides the Autofac-strict tightening "
              "(breaking) and the cache-staleness task.")
new_m_next = ("Owner runs the full-tree suites on 0.2.8218 and turns it in. The Autofac-strict tightening is not "
              "wanted (owner, 2026-10-03); the cache-staleness defect is worked under executor_cache_world_stamp.")
board = replace_once(board, old_m_next, new_m_next, "matcher next")
for old_ts_row in ("| tickets/tasks/2026-10-03_resolve_annotations_by_address_key_task.md | 2026-10-03T19:36:16Z | REQUIRED |",
                   "| tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md | 2026-10-03T19:36:16Z | REQUIRED |"):
    board = replace_once(board, old_ts_row, old_ts_row.replace("2026-10-03T19:36:16Z", TS), "row ts")

detail = (
    "- executor_cache_world_stamp: SWITCH_TRIGGER is the fix landed and turned in, or a CONFLICT when fable_1's\n"
    "  rebind repair claims spellbook_creation_system.py first (one writer per file), or a DECISION_REQUEST if an\n"
    "  existing cache test depends on a full hit across a changed world. RESUME_HIERARCHY:\n"
    f"  {TASK_REL} (standalone; the RISK note in\n"
    "  tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md is the origin).\n"
)
board = insert_after_regex(board, r"^- annotation_address_matching: SWITCH_TRIGGER.*\n(?:  .*\n)*", detail, "matcher detail")
old_m_detail = ("the Autofac-strict tightening and the cache-staleness\n"
                "  investigation are follow-up decisions, not part of this lane.")
new_m_detail = ("the Autofac-strict tightening is not wanted (owner, 2026-10-03) and the\n"
                "  cache-staleness defect is worked under executor_cache_world_stamp.")
board = replace_once(board, old_m_detail, new_m_detail, "matcher detail text")
old_s8_detail = ("The PGO epic\n"
                 "  (tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md) stays queued behind this one with no row.")
assert board.count(old_s8_detail) == 1, "s8 detail anchor"
write_text(BOARD, board, nl)

# --- S8 task: a FACT note pointing at the new lane (append-only) ---
s8, nl8 = read_text(S8_TASK)
note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: FACT\n"
    "  CLAIM: The cache-staleness RISK above is now worked as its own lane on the owner's word (2026-10-03: \"add\n"
    "    tests please and lets properly fix the defects you found too\"): tickets/tasks/2026-10-03_require_world_\n"
    "    stamp_for_executor_cache_full_hit_task.md. The Autofac-strict tightening is not wanted (owner: \"the\n"
    "    autofac thing was just an example\"). This task stays in review for the owner's turn-in.\n"
    "  EVIDENCE:\n"
    f"  - {TASK_REL}:1-40\n"
    "  IMPACT: No change to S8; the follow-up decisions recorded in the 19:36:16Z note are settled.\n"
    "  NEXT: owner runs the suites and the gauntlet and turns S8 in.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
s8 = replace_once(s8, "\n## Context / Handoff Summary\n", "\n" + note + "## Context / Handoff Summary\n", "s8 handoff")
write_text(S8_TASK, s8, nl8)
print("opened", TS)

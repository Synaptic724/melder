"""The three backlog follow-ups of the cache-save fix, as drafts (melder_0, 2026-10-24; closure).

Imported by close_task_20261024.py, which writes them in its all-or-nothing pass. Each is the full task template
(templates/task_template.md): the boilerplate sections are copied from the template itself, the rest is this
lane's text. No board row: parked drafts route nowhere until the owner schedules them.
"""
import pathlib
from typing import Dict, List

TEMPLATE = pathlib.Path.home() / "mnt/melder_private/context_compass/templates/task_template.md"
FIX = "TASK-2026-10-24-cache_file_write_failure_fails_meld"
FIX_DONE = "context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md"


def template_block(first: str, stop: str) -> str:
    """Return the template's text from the line `first` up to (not including) the line `stop`."""
    lines = TEMPLATE.read_text(encoding="utf-8").split("\n")
    start = lines.index(first)
    end = lines.index(stop)
    return "\n".join(lines[start:end]).rstrip("\n")


def template_tail(first: str) -> str:
    lines = TEMPLATE.read_text(encoding="utf-8").split("\n")
    return "\n".join(lines[lines.index(first):]).rstrip("\n") + "\n"


MICROCYCLE = """\
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy."""

ANTI = """\
## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion."""


def ticket(now: str, slug: str, title: str, story: str, objective: str, contract: str, scope: str,
           transition: str, steps: str, deliverables: str, files: str, validation: str, risks: str,
           extra_anti: str, note: str, summary: str) -> str:
    done = template_block("## Done Checklist", "## Artifact Links (Optional)")
    artifact_head = template_block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED: true | false")
    noting = template_block("## Noting Behavior", "## Contribution Attribution")
    tail = template_tail("## Project-Specific Additions")
    parts = [
        f"# Task: {title[0].upper()}{title[1:]}",
        "",
        "## Metadata",
        f"- Task ID: TASK-2026-10-24-{slug}",
        f"- Story: {story}",
        "- Status: draft",
        "- Owner: user",
        "- Agent Name: unassigned",
        "- Agent Role: UNKNOWN",
        "- Priority: p3",
        f"- Created: {now}",
        f"- Updated: {now}",
        "",
        "## Objective", objective, "",
        "## Ticket Contract", contract, "",
        "## Scope Boundaries", scope, "",
        "## State Transition Event", transition, "",
        "## Steps / Checklist", steps, MICROCYCLE, "",
        "## Deliverables", deliverables, "",
        "## Files / Paths Impacted", files, "",
        "## Validation", validation, "",
        "## Risks / Rollback Notes", risks, "",
        ANTI + (("\n" + extra_anti) if extra_anti else ""), "",
        done, "",
        artifact_head.rstrip("\n"),
        "",
        "- ARTIFACTS_REQUIRED: false",
        "- ARTIFACT_PATHS:",
        "  - none",
        "- DISPOSITION: delete_on_close",
        "- CLEANUP_TRIGGER: none",
        "",
        "## Context Management",
        "- CONTEXT_MANAGEMENT_REQUIRED: false",
        "- CONTEXT_IDS:",
        "  - none",
        "- CONTEXT_TOPICS:",
        "  - none",
        "- IF_UNKNOWN: none",
        "",
        noting, "",
        "## Contribution Attribution",
        "- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this ticket, at the closure of",
        f"  {FIX}; {now[:10]}.",
        "- Published By: UNKNOWN (local repository; not published)",
        "- Independent Review: none requested",
        "",
        "## Notes", note, "",
        "## Context / Handoff Summary", summary, "",
        tail.rstrip("\n"),
    ]
    return "\n".join(parts) + "\n"


def tests_docs(now: str, note: str) -> str:
    return ticket(
        now, "document_refused_cache_save_tests", "the test maps describe the refused-save tests of 0.2.8266",
        f"none (standalone backlog task; a follow-up of {FIX})",
        """\
The test system documents (tests_architecture, tests_components) describe the tests the best-effort cache save
added at 0.2.8266. The fix lane left them out while melder_2's CI set held both documents (M2-28); that set
landed on 2026-10-24 (M2-31):
- tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py - eight
  cases (five tests, three of them over a refused rename and a refused temp write) through every kind of meld door
  with the save refused: the meld returns its object, a managed lease comes back, a spellspace meld returns;
- tests/unit/melder/utilities/test_caching_system_refused_save.py - eleven `CachingSystem` save tests: the bool, no
  temp file left behind, the Windows-only rename retry and its budget, one WARNING per bundle, the per-writer temp
  name, a refused temp write or folder, a temp file that cannot be removed;
- six new cases in tests/unit/melder/spellbook/test_cache_runtime_verification.py: the Book's save seam (the flag
  left cleared, no retry until cache is staged again), the explicit save (True when written, False when refused,
  through `Spell.emit_cache_file()` too) and the conjure-end save.""",
        """\
- ENTRY_GATE: the owner schedules it; an active board row; both tests documents re-read after the lanes that edit
  them last (melder_1's 0.2.8267 landing among them).
- EXECUTION_BOUNDARY: tests_architecture.md, tests_components.md and their indexes - the entries for the three
  files above; no test, src, version or release-note change; the asset rebuild last.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266).
- EXIT_GATE: each file has its entry under the tests documents' instructions; both indexes regenerated and
  --check OK; the content-preservation gate met; the rebuild's two checks OK.
- FAILURE_ESCALATION: CONFLICT when another lane holds the tests documents; DECISION_REQUEST when an entry needs
  a section the instructions do not provide.""",
        """\
- In scope: the three files' entries in both tests documents.
- Out of scope: changing the tests; the src documents, which carry the fix since 0.2.8266.""",
        f"""\
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure, as its plan recorded (Notes 22 and 28 of
  {FIX}); no lane is opened.""",
        """\
- [ ] The owner schedules it; a board row; both tests documents and their instructions re-read.
- [ ] Slice the sections holding the neighbouring cache and meld-door tests; write the three entries.
- [ ] Both indexes regenerated, --check, the content-preservation diff; the rebuild last.""",
        "- The three entries in tests_components, and in tests_architecture where its sections call for them.",
        """\
- context_compass/system_docs/tests_architecture.md and its index
- context_compass/system_docs/tests_components.md and its index""",
        """\
- Not run.
- Recommended commands:
  - `python context_compass/tools/system_documents/index_document.py --doc context_compass/system_docs/tests_components.md --check`
  - the same for tests_architecture.md""",
        "- Low: documentation only. Count the cases from the files at pickup rather than from this ticket.",
        "", note,
        """\
Draft, parked: the entries for the three refused-save test files of 0.2.8266 (Objective). Waits for the owner's
scheduling and for the shared tests documents to be free. Evidence: the FACT note above and the fix ticket.""")


def frequency_location(now: str, note: str) -> str:
    return ticket(
        now, "cache_save_frequency_and_location", "fewer meld-time cache saves and a cache root outside the package",
        f"none (standalone backlog task; directions 3 and 4 of {FIX})",
        f"""\
Two follow-ups of the best-effort cache save (0.2.8266), each the owner's call (directions 3 and 4 of the fix's
DECISION_REQUEST, Note 10 of {FIX}):
- Fewer saves: a meld that stages new plans rewrites the whole bundle before it returns - the failing MelderOps
  configure wrote one bundle twice within 1 ms. Save at conjure end, then at most once per short interval or at the
  Book's teardown, so most melds never touch the disk.
- Location and growth: the cache root is a fragment under the package root, so every process of an install
  writes into site-packages (read-only in a system install, watched by scanners on Windows), and frame folders
  are never pruned (55 per-trial folders, 5.9 MB, in the MelderOps venv). Allow an absolute or per-user root,
  and prune the folders a run will not reuse.
Both are recorded with source evidence in the fix ticket (Notes 3, 4 and 10); re-read the source at pickup.""",
        """\
- ENTRY_GATE: the owner picks either, both or neither, and the shape (an interval or the Book's teardown; the
  root's form; the pruning rule); an active board row; the patch gate (the save points and the cache location are
  boundary changes).
- EXECUTION_BOUNDARY: `CachingSystem` and its caller's save seam (`Spellbook._emit_cache_file_if_required`,
  `_emit_cache_file`), the cache-root option of the frame configuration and its resolution; their tests; the
  system documents; the release note; one notch per src change; the rebuild last.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266: a refused save is
  harmless, so neither follow-up is a correctness fix).
- EXIT_GATE: the chosen behaviour with red-then-green tests, the GIL off and on; documents, release note, notch
  and rebuild done.
- FAILURE_ESCALATION: DECISION_REQUEST for any change to when a bundle is on disk (a crash between coalesced saves
  loses only accelerator state, but another process reads an older bundle for longer).""",
        """\
- In scope: when the creation cache is saved; where it lives; pruning frame folders.
- Out of scope: the cache format and its admission rules; the bind-guard and agent-documentation asset caches;
  the Crystallizer's cache.""",
        f"""\
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure; the owner's go took directions 1 and 2
  and left 3 and 4 as follow-ups (Notes 19-21 of {FIX});
  no lane is opened.""",
        """\
- [ ] The owner's calls (ENTRY_GATE); a board row; the patch gate.
- [ ] Red tests for the chosen behaviour (a meld after the conjure-end save writes nothing until the interval or
      the teardown; a root outside the package is written and read back; a pruned folder is one no run reuses).
- [ ] The change; green with the GIL off and on; the fix lane's probe re-run.
- [ ] Documents, release note, notch, NOTICEs; closure; the rebuild last.""",
        "- The chosen save points and cache location, with tests, documents and the release note.",
        """\
- src/melder/utilities/caching_system/caching_system.py
- src/melder/aether/spellbook/spellbook.py (the save seam)
- src/melder/aether/aetheric_frame/aetheric_frame_configuration.py (the cache root)
- their tests; context_compass/system_docs/src_architecture.md, src_components.md; release_docs/next_version_release.md""",
        """\
- Not run.
- Recommended commands:
  - VM, against a copy of the tree:
    `python -X gil=0 -m pytest -q tests/unit/melder/utilities tests/component/melder/spellbook`""",
        "- Coalescing changes when another process sees a new bundle; a moved root makes every existing bundle cold once.",
        "", note,
        """\
Draft, parked: directions 3 and 4 of the cache-save fix (Objective), each waiting for the owner's call. Evidence:
the FACT note above and Notes 3, 4 and 10 of the fix ticket.""")


def windows_holder(now: str, note: str) -> str:
    return ticket(
        now, "identify_windows_cache_file_holder",
        "name what held the bundle open in the owner's WinError 5 failure",
        f"none (standalone backlog task; the open HYPOTHESIS of {FIX})",
        f"""\
Find what refused the rename of `melderops.meldercache` with PermissionError [WinError 5] in the owner's MelderOps
run on 0.2.8265 (chat 2026-10-24). The fix recorded the cause as a HYPOTHESIS (Note 5 of
{FIX}): Windows refuses a rename onto a file another handle holds open
without FILE_SHARE_DELETE - an on-access scanner (Microsoft Defender), the Windows Search or an IDE indexer, a
reader in another process. Since 0.2.8266 the meld no longer fails and the rename is retried for about 100 ms;
this task names the holder and says whether that budget fits.""",
        f"""\
- ENTRY_GATE: the owner runs it on his Windows machine (the VM cannot raise WinError 5); an active board row.
- EXECUTION_BOUNDARY: measurement only - the owner's MelderOps test with 0.2.8266 installed, and this ticket's
  Notes. A change the finding calls for gets a task of its own.
- DEPENDENCIES: {FIX} (completed, 0.2.8266).
- EXIT_GATE: the holder named from a capture, or the refusal shown to stop with real-time scanning excluded; the
  rerun's WARNING count recorded.
- FAILURE_ESCALATION: DECISION_REQUEST when refusals outlast the retry budget often enough to matter.""",
        """\
- In scope: one or two reruns on the owner's machine and their record.
- Out of scope: changing the retry budget or the save frequency (TASK-2026-10-24-cache_save_frequency_and_location).""",
        f"""\
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure; the HYPOTHESIS of Note 5 of
  {FIX} stays open; no lane is opened.""",
        """\
- [ ] With 0.2.8266 in priv_commandops/.venv314, from priv_commandops:
      `uv run pytest tests/benchmarks/postgres_row_transfer_v2/test_submission_batches.py -k list50 -x`;
      count the WARNING lines that start "Could not save the creation-cache bundle".
- [ ] Rerun under Process Monitor filtered on paths ending in .meldercache, to name the process holding the
      handle at the refused rename; or rerun with the venv excluded from real-time scanning.
- [ ] Record the MEASURE here; file a task when the budget or the save frequency should change.""",
        "- A MEASURE note naming the holder, or showing the refusal stops with scanning excluded.",
        "- none in the repository (the owner's machine; this ticket's Notes)",
        """\
- Not run (the owner's machine).
- Recommended commands: the Steps above.""",
        "- None in the repository; Process Monitor captures can be large - filter before recording.",
        "", note,
        """\
Draft, parked: the owner's rerun on Windows to name the holder behind WinError 5 (Objective); the fix makes the
refusal harmless either way. Evidence: the FACT note above and Notes 4-5 of the fix ticket.""")


def notes(now: str, ranges: Dict[str, str]) -> Dict[str, str]:
    """The first FACT note of each draft, with ranges computed by the caller."""
    def note(claim: List[str], evidence: List[str], impact: List[str], nxt: str) -> str:
        lines = [f"- DATETIME: {now}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer",
                 "  TYPE: FACT", "  CLAIM: " + claim[0]] + ["    " + c for c in claim[1:]]
        lines += ["  EVIDENCE:"] + [f"  - {e}" for e in evidence]
        lines += ["  IMPACT: " + impact[0]] + ["    " + c for c in impact[1:]]
        lines += [f"  NEXT: {nxt}", "  REREAD: REQUIRED", "  SCORE_0_TO_10: 7"]
        return "\n".join(lines)
    return {
        "tests": note([
            "The three files exist at 0.2.8266 with the counts in the Objective (five component tests, three over",
            "two failure steps; eleven CachingSystem tests; six new Book and Spell cases), green the GIL off and on",
            "in the fix's F6 runs; the fix deferred their tests-document entries (its Notes 22 and 28)."],
            ["tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py:271-434",
             "tests/unit/melder/utilities/test_caching_system_refused_save.py:1-485",
             "tests/unit/melder/spellbook/test_cache_runtime_verification.py:315-364",
             "tests/unit/melder/spellbook/test_cache_runtime_verification.py:561-617",
             "tests/unit/melder/spellbook/test_cache_runtime_verification.py:679-704",
             ranges["note22"], ranges["note28"]],
            ["The test maps miss three files of a landed fix until this task runs."],
            "The owner schedules it."),
        "frequency": note([
            "The fix's DECISION_REQUEST (its Note 10) offered four directions; the owner's go took 1 and 2 (its",
            "Note 21), so 3 (fewer meld-time saves) and 4 (the cache root and pruning) stand as follow-ups. Notes 3",
            "and 4 there carry the source evidence: the root is a fragment under the package root, and the failing",
            "configure wrote one bundle twice within 1 ms."],
            [ranges["note3"], ranges["note4"], ranges["note10"], ranges["note21"]],
            ["Neither is a correctness fix since 0.2.8266; both cut disk writes and site-packages growth."],
            "The owner's calls in the ENTRY_GATE."),
        "windows": note([
            "The holder behind WinError 5 is unmeasured: the fix ticket's Note 5 states it as a HYPOTHESIS with",
            "this verification, and its Note 4 records the evidence (two writes of one bundle 1 ms apart, inside one",
            "configure, in a frame unique to the trial; the orphaned temp file beside the bundle)."],
            [ranges["note4"], ranges["note5"]],
            ["Without it the retry budget (about 100 ms) is a guess against the holder's hold time."],
            "The owner's rerun (Steps)."),
    }

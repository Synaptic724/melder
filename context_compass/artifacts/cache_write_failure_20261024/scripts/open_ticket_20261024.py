"""Open TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0, 2026-10-24).

Writes the task ticket (refusing an existing one), its attention_board.md row and detail entry, its
artifact_board.md row and the MelderOps cache listing it cites. All-or-nothing: every anchor must match once, every
new line must fit 120 characters, no CR; a board that changed between the read and the write is refused (melder_1
is cleaning the boards concurrently), and nothing is written.
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
FOLDER = "artifacts/cache_write_failure_20261024"
LISTING = FOLDER + "/runs/melderops_cache_listing_20261024.txt"
CACHE = pathlib.Path.home() / "mnt/priv_commandops/.venv314/Lib/site-packages/melder/__melder_cache__/__conjure_cache__"
FRAME = "c8pg_d339c5b10fe4"


def stamp(ns: int) -> str:
    seconds, rest = divmod(ns, 1_000_000_000)
    base = datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    return f"{base}.{rest:09d}Z"


def listing(now: str) -> str:
    lines = [f"MelderOps conjure cache, read by melder_0 at {now} (the VM's view of the Windows folder; times UTC)",
             f"root: priv_commandops/.venv314/Lib/site-packages/melder/__melder_cache__/__conjure_cache__", "",
             f"frame folder {FRAME}:"]
    for entry in sorted((CACHE / FRAME).iterdir(), key=lambda p: p.stat().st_mtime_ns):
        info = entry.stat()
        lines.append(f"  {stamp(info.st_mtime_ns)}  {info.st_size:>7} B  {entry.name}")
    frames = [p for p in CACHE.iterdir() if p.is_dir()]
    trial = [p for p in frames if p.name.startswith("c8pg_")]
    temps = sorted(str(p.relative_to(CACHE)) for p in CACHE.rglob("*.tmp"))
    total = sum(p.stat().st_size for p in CACHE.rglob("*") if p.is_file())
    lines += ["", f"frame folders: {len(frames)} ({len(trial)} named c8pg_<12 hex>, one per benchmark trial)",
              f"files: {sum(1 for p in CACHE.rglob('*') if p.is_file())}, {total} B in all",
              f"temp files left behind: {len(temps)}"] + [f"  {t}" for t in temps]
    return "\n".join(lines) + "\n"


class Open(Record):
    """The opening pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            now_text = (self.ROOT / rel).read_text(encoding="utf-8")
            if now_text != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def ticket_text(r: Open, notes: str, summary: str) -> str:
    return f"""# Task: A failed creation-cache file write fails the meld that triggered it (WinError 5 on Windows)

## Metadata
- Task ID: TASK-2026-10-24-cache_file_write_failure_fails_meld
- Story: none (standalone owner-directed defect record)
- Status: in_progress
- Owner: Mark
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {r.now}
- Updated: {r.now}

## Objective
Document, with source evidence and a reproducer, the Melder defect behind the owner's Windows failure (chat
2026-10-24, "document:" with a MelderOps pytest log): `CachingSystem.emit()` raised PermissionError [WinError 5]
from its `os.replace` onto `melderops.meldercache`, and the meld that triggered the write raised it to its caller
after building its object. A creation-cache bundle is an accelerator: a meld must not fail because one could not be
written. This round records the defect and the fix directions; the fix waits for the owner's word.

## Ticket Contract
- ENTRY_GATE: this task's active row on attention_board.md; the source-read notes recorded before the probe runs.
- EXECUTION_BOUNDARY: documentation only - this ticket, its board row, and {FOLDER}/
  (probe, runs, scripts) with its artifact row. No change to src/, tests/, docs/ or release_docs/ (no notch, no
  release-note entry, no rebuild). MelderOps (priv_commandops) is read, never written.
- DEPENDENCIES: none for the record. A fix touches src/melder/utilities/caching_system/caching_system.py,
  src/melder/aether/spellbook/spellbook.py and possibly src/melder/aether/conduit/meld/conduit_meld.py;
  spellbook.py is held by melder_1's EPIC-2026-10-17-correctness_defects (one writer per file), so a fix is
  coordinated with that lane.
- EXIT_GATE: Notes cover the write, its callers, the location, the owner's run, the Windows hypothesis and the
  probe's MEASURE; the fix directions are a DECISION_REQUEST; status ready and the board row removed.
- FAILURE_ESCALATION: CONFLICT if the probe contradicts a source-read note; DECISION_REQUEST for the fix
  direction; BLOCKER if the probe cannot run on the VM.

## Scope Boundaries
- In scope: the creation-cache bundle write (`CachingSystem`), its callers on the meld and conjure paths, the
  cache location and defaults, the Windows replace refusal and the orphaned temp file.
- Out of scope: the bind-guard and agent-documentation build-asset caches; the Crystallizer's cache; MelderOps
  changes (its per-trial unique frame is its own choice); the fix itself (the owner's word).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's "document:" request (chat 2026-10-24) and this task's board row.

## Steps / Checklist
- [x] Read the write (`CachingSystem.emit`, `_write_current_cache_to_disk_locked`, construction and load), its
      callers (`Spellbook._emit_cache_file_if_required`, `_emit_spell_cache`, `_get_or_create_caching_system`,
      `ConduitMeld.meld`, `Conduit.meld`, `Conduit.managed_spell_meld`, the conjure-end emit, the publish-time
      staging) and the cache-root resolution.
- [x] Read the MelderOps path (`NativeCohort.start`, `Spectrum.configure` -> `_init_services`) and its cache
      folder.
- [ ] Probe cases A-D on a copy of the tree, the GIL off and on; record the MEASURE.
- [ ] Record the fix directions as a DECISION_REQUEST; set ready; remove the board row.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- This ticket: the defect with its evidence, consequences, Windows hypothesis and fix directions.
- {FOLDER}/: the probe (cases A-D) and its runs, the MelderOps cache listing, the scripts.

## Files / Paths Impacted
- context_compass/{TICKET}
- context_compass/attention_board.md (this task's row, removed when it is ready)
- context_compass/artifact_board.md (one active row)
- context_compass/{FOLDER}/

## Validation
- Not run: the owner's MelderOps test on Windows (the failure is his run, reported in chat). The VM cannot raise
  WinError 5; the probe injects the refusal instead.
- Recommended commands:
  - Windows, from priv_commandops:
    `uv run pytest tests/benchmarks/postgres_row_transfer_v2/test_submission_batches.py -k list50 -x`
  - VM, from a scratch folder, against a copy of the tree (the bundles land under the copy's package root):
    `PYTHONPATH=/tmp/m0_mq/wincache/src python -X gil=0 <repo>/context_compass/{FOLDER}/probes/probe_cache_emit_failure.py`

## Risks / Rollback Notes
- Making the write best-effort must not hide a broken install for good: log it (once per Book, not per meld) and
  keep the in-memory bundle, so the next conjure or a later write can still persist it.
- A retry with sleeps belongs off the hot path: the meld-time write runs on the melding thread.
- Two processes that share one frame and conduit name (the ordinary melderops frame) share one temp file name;
  a unique temp name per writer keeps one process from writing into another's temp file.
- Frame folders are never pruned; frames unique per run grow the cache in site-packages without bound.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No fix from the Windows HYPOTHESIS alone: the Melder-side contract (a failed write fails the meld) is FACT
      and fixable on its own; the root cause stays HYPOTHESIS until a Windows capture or rerun confirms it.
- [ ] No broad `except Exception` as the fix unless it is a documented best-effort contract that logs.

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
  - {FOLDER}/probes/probe_cache_emit_failure.py
  - {FOLDER}/runs/
  - {FOLDER}/scripts/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept as the defect's reproducer; rerun at the fix, then disposed with the fix's turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence; this ticket, the probe and its
  runs; 2026-10-24; the Notes below.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
{notes}

## Context / Handoff Summary
{summary}

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
"""


def build_notes(r: Open, listing_lines: int, contract_ref: str) -> str:
    listing_ref = f"context_compass/{LISTING}:1-{listing_lines}"
    n1 = r.note(r.now, "FACT", [
        "A conduit's creation-cache bundle is written by `CachingSystem.emit()`: under one per-instance RLock it",
        "marshals the whole in-memory envelope to `<conduit>.meldercache.tmp` with `write_bytes`, then",
        "`Path.replace`s it onto `<cache root>/<frame>/<conduit>.meldercache`. No retry; the temp file is not removed",
        "when the replace raises; every writer of one bundle uses the same temp name. The bundle is read once, at",
        "construction, with `read_bytes`, and any load error only makes the cache cold (logged)."],
        ["src/melder/utilities/caching_system/caching_system.py:728-741",
         "src/melder/utilities/caching_system/caching_system.py:885-918",
         "src/melder/utilities/caching_system/caching_system.py:257-316",
         "src/melder/utilities/caching_system/caching_system.py:766-789"],
        ["The replace is the step that raised in the owner's Windows run; nothing in the write tolerates it or",
         "cleans up after it, and a missing or bad bundle is otherwise harmless (cold cache)."],
        ["Follow the callers up to the meld (next note)."], "REQUIRED", 8)
    n2 = r.note(r.now, "FACT", [
        "The meld path writes the bundle after it has built and stored its object, and does not catch: every exit",
        "of `ConduitMeld.meld` (two fast lanes, the no-hooks lane, the hooks lane; lines 470-471, 505-506, 682-683,",
        "722-723) calls `Spellbook._emit_cache_file_if_required()` when `_cache_emit_required` is set, after the",
        "executor returned the instance. That method clears the flag, calls `emit()` and, on any exception, sets the",
        "flag again and re-raises; `Conduit.meld` passes it through (its dynamic branch has only a `finally` for the",
        "gate ticket). Conjure treats the same call as best-effort: `_emit_conduit_cache_file_at_conjure_end` logs",
        "and returns (\"Never propagates cache failures into the conjure path\"), leaving the flag set for the first",
        "meld to retry. Staging is lazy: a CreationContext published at a meld (a spell compiled at its first meld,",
        "for example one bound after conjure) stages its payload and sets the flag, so that meld rewrites the bundle."],
        ["src/melder/aether/conduit/meld/conduit_meld.py:282-731",
         "src/melder/aether/spellbook/spellbook.py:1143-1180",
         "src/melder/aether/conduit/conduit.py:4864-5090",
         "src/melder/aether/spellbook/spellbook_creation_system.py:1252-1285",
         "src/melder/aether/spellbook/spellbook.py:1064-1141",
         "src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:166-183"],
        ["A write failure surfaces from an unrelated user call (here `Spectrum.configure`'s fifth meld) after the",
         "object was built: a unique is stored and comes back from the next meld, a many is lost to its caller, and",
         "while the failure lasts (a read-only folder) every meld through that Book raises, since the flag is set",
         "again each time. A bad bundle only makes the cache cold, so failing a meld over a write inverts that."],
        ["Reproduce the propagation on the VM with an injected replace refusal and read-only folders (probe)."],
        "REQUIRED", 9)
    n3 = r.note(r.now, "FACT", [
        "Caching is on by default for every frame, and the bundle lives under the melder package itself:",
        "`<melder package root>/__melder_cache__/__conjure_cache__/<frame>/<conduit>.meldercache` - site-packages for",
        "an installed Melder, shared by every process that imports that install. `with_system_cache_root_path`",
        "takes only a fragment relative to the package root (an absolute path raises ValueError), so no setting",
        "moves the cache out of site-packages; the only opt-out is `system_caching_enabled=False` for the frame."],
        ["src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1645-1672",
         "src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1705-1742",
         "src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:746-795",
         "src/melder/aether/spellbook/spellbook.py:1023-1062"],
        ["A read-only install (system site-packages, a locked image) makes the persistent case of the previous note",
         "the default outcome; on Windows every process of a venv writes into one folder that scanners watch."],
        ["Record the MelderOps evidence (next note)."], "HELPFUL", 8)
    n4 = r.note(r.now, "FACT", [
        "The owner's run (pytest log, chat 2026-10-24; Windows, cpython 3.14 free-threaded via uv, melder 0.2.8265",
        "in priv_commandops/.venv314) failed in",
        "`test_list50_async_transactions_still_each_commit_a_complete_unit[False-100-expected_lists0]`:",
        "`BatchExperiment.trial` -> `Experiment.trial` -> `NativeCohort.start` -> `Spectrum.configure` ->",
        "`_init_services` -> its fifth `conduit.meld` (SpectrumSystemState) -> `Conduit.meld` -> `ConduitMeld.meld`",
        "-> `_emit_cache_file_if_required` -> `CachingSystem.emit` -> `temp_bundle_path.replace(bundle_path)`:",
        "PermissionError [WinError 5] Access is denied, .../c8pg_d339c5b10fe4/melderops.meldercache.tmp ->",
        ".../melderops.meldercache. The trial's frame is its own (\"c8pg_\" + 12 hex of a uuid4, unique_frame=True),",
        "so no other process writes that bundle. The folder holds the bundle (34402 B, written 11:07:49.9347 UTC)",
        "and the orphaned temp file (36143 B, 11:07:49.9357): the bundle had been replaced 1 ms before the failing",
        "write. 55 per-trial c8pg_ folders (6.4 MB in all) have accumulated in that venv's cache."],
        ["priv_commandops/tests/benchmarks/postgres_row_transfer_v2/test_submission_batches.py:83-130",
         "priv_commandops/benchmarks/postgres_row_transfer_v2/run.py:375-375",
         "priv_commandops/benchmarks/postgres_row_transfer_v2/operative_adapter.py:64-121",
         "priv_commandops/src/melder_ops/command_center/spectrum/spectrum.py:1523-1523",
         "priv_commandops/src/melder_ops/command_center/spectrum/spectrum.py:2224-2260",
         listing_ref],
        ["Two writes of one bundle 1 ms apart, inside one configure on one thread, with no other Melder process on",
         "the bundle: the refusal comes from outside Melder (next note), and Melder turns it into a failed configure."],
        ["State the Windows cause as a HYPOTHESIS with its verification."], "REQUIRED", 9)
    n5 = r.note(r.now, "HYPOTHESIS", [
        "On Windows `Path.replace` is `os.replace`, a MoveFileExW(MOVEFILE_REPLACE_EXISTING) rename, which fails",
        "with ERROR_ACCESS_DENIED (WinError 5) while the destination is open in a handle that did not grant",
        "FILE_SHARE_DELETE - an on-access antivirus scan (Microsoft Defender), the Windows Search or an IDE indexer, a",
        "reader in another process - or when it is read-only. A scanner opening each freshly written .meldercache fits",
        "a refusal 1 ms after the previous replace. POSIX rename has no such refusal, so the VM cannot reproduce it."],
        ["src/melder/utilities/caching_system/caching_system.py:885-918", listing_ref],
        ["If true, a Windows user with real-time scanning can hit it whenever two bundle writes come close together",
         "(a configure that compiles several spells at their first melds), and a short retry of the replace would",
         "succeed."],
        ["Verify on the owner's machine: a Process Monitor capture filtered on melderops.meldercache during the test",
         "names the handle's process; or rerun with the venv excluded from real-time scanning."], "REQUIRED", 8)
    n6 = r.note(r.now, "UNKNOWN", [
        "A managed lease taken by a meld that then fails its bundle write may never go back:",
        "`Conduit.managed_spell_meld` wraps the object in its lease only after `self.meld(...)` returns, so the raise",
        "would leave the object out of its pool with no holder - for limited_quantity or queue, a place lost for good."],
        ["src/melder/aether/conduit/conduit.py:5095-5207",
         "src/melder/aether/conduit/meld/conduit_meld.py:282-731"],
        ["The worst consequence if it holds: a pool that refuses leases until its root is torn down."],
        ["Run probe case D (limited_quantity, limit 1, a failing write on the leasing meld)."], "HELPFUL", 7)
    n7 = r.note(r.now, "PLAN", [
        "Document only this round (the owner's \"document:\"). Reproduce the Melder-side contract on the VM against a",
        "copy of the tree at 0.2.8265 (/tmp/m0_mq/wincache/src, so no bundle is written into the repository): case A",
        "injects one PermissionError into the next Path.replace onto the probe's bundle (the Windows refusal), case B",
        "makes a frame's cache folder read-only after conjure, case C makes the conjure-cache root read-only before",
        "conjure, case D leases a limited_quantity managed spell through a failing write. Then the MEASURE, the fix",
        "directions as a DECISION_REQUEST, status ready and the board row removed."],
        [contract_ref],
        ["Turns notes 2 and 6 into measured behaviour before the owner picks a fix."],
        ["Write the probe into the artifact folder and run it with the GIL off and on."], "HELPFUL", 7)
    return "\n\n".join([n1, n2, n3, n4, n5, n6, n7])


def main() -> None:
    r = Open("open_cache_write_failure")
    if (r.ROOT / TICKET).exists():
        sys.exit(f"EXISTS {TICKET}")
    listing_text = listing(r.now)
    listing_lines = len(listing_text.rstrip("\n").split("\n"))
    # The Ticket Contract section precedes the Notes, so its range does not depend on them.
    pre = ticket_text(r, "", "").split("\n")
    start = pre.index("## Ticket Contract")
    end = pre.index("## Scope Boundaries") - 1
    while pre[end].strip() == "":
        end -= 1
    contract_ref = f"context_compass/{TICKET}:{start + 1}-{end + 1}"
    notes = build_notes(r, listing_lines, contract_ref)
    summary = "\n".join([
        "Scope: document the defect only (the owner's \"document:\", chat 2026-10-24). Done: source read of the write,",
        "its callers and the cache location, the MelderOps path and its cache folder (Notes 1-6). Remaining: probe",
        "cases A-D with the GIL off and on -> MEASURE; the fix directions as a DECISION_REQUEST; status ready and the",
        "board row removed. Holds: no src change without the owner's word; spellbook.py is held by melder_1's",
        "correctness epic. Next: write the probe and run it against /tmp/m0_mq/wincache/src (a copy of 0.2.8265)."])
    text = ticket_text(r, notes, summary)
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    lines = text.split("\n")
    if lines[start] != "## Ticket Contract" or not lines[end].startswith("  direction;"):
        sys.exit(f"SPAN {start + 1}-{end + 1}: {lines[start]!r} / {lines[end]!r}")
    row = ("| cache_write_failure | in_progress | discovery | claude | melder_0 | none | Run the cache-emit probe "
           "(cases A-D, GIL off and on) and record the result. | The defect documented with source evidence, a "
           "reproducer and fix directions for the owner. | Ticket ready with its MEASURE and DECISION_REQUEST "
           f"recorded, or the owner redirects. | {TICKET} | {r.now} | REQUIRED |")
    detail = "\n".join([
        "- WORK_ITEM: cache_write_failure",
        "  SWITCH_TRIGGER: Ticket ready with its MEASURE and DECISION_REQUEST recorded, or the owner redirects.",
        "  RESUME_HIERARCHY:",
        f"    - {TICKET}"])
    board = r.read(r.BOARD)
    board = r.once(board, "\n<!-- END USER-DEFINED: active_items -->", "\n" + row + "\n<!-- END USER-DEFINED: active_items -->",
                   "board row")
    board = r.once(board, "\n<!-- END USER-DEFINED: active_attention_details -->",
                   "\n" + detail + "\n<!-- END USER-DEFINED: active_attention_details -->", "board detail")
    r.stage(r.BOARD, board)
    art_row = (f"| {TICKET} | {FOLDER}/ | defect_reproducer | active | retain_as_reference | Probe cases A-D with "
               "their runs (GIL off and on), the MelderOps cache listing and the scripts; rerun the probe at the fix. "
               f"| {r.now} | REQUIRED |")
    arts = r.read(r.ARTIFACTS)
    arts = r.once(arts, "\n<!-- END USER-DEFINED: active_artifacts -->",
                  "\n" + art_row + "\n<!-- END USER-DEFINED: active_artifacts -->", "artifact row")
    r.stage(r.ARTIFACTS, arts)
    r.checked_flush()
    (r.ROOT / LISTING).write_text(listing_text, encoding="utf-8", newline="\n")
    print("wrote", LISTING, listing_lines, "lines")


if __name__ == "__main__":
    main()

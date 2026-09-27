"""Closure sync for the validation_error_reporting lane (owner accepted 2026-09-26).

Run from the context_compass root. Anchored, whole-line edits only (patch_util); board rows are located by a
unique prefix at run time and removed or inserted without touching neighbouring rows of other agents.
"""
import datetime
import pathlib
import subprocess
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

T = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NAME = "2026-09-26_review_conjure_validation_error_reporting_task.md"
TICKET = pathlib.Path("tickets/tasks") / NAME
DONE_TICKET = pathlib.Path("tickets/tasks/completed") / NAME
LANE = pathlib.Path("system_docs/patches/active/validation_error_reporting_2026_09_26")
DONE_LANE = pathlib.Path("system_docs/patches/completed/validation_error_reporting_2026_09_26")
COMMIT_LIST = pathlib.Path("artifacts/validation_error_reporting_20260926/results/commit_files.txt")


def unique_line(path: pathlib.Path, prefix: str) -> str:
    """Return the single line of `path` that starts with `prefix` (CR stripped)."""
    hits = [line.rstrip("\r\n") for line in path.read_bytes().decode("utf-8").splitlines(keepends=True)
            if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"{path}: expected one line starting {prefix!r}, found {len(hits)}")
    return hits[0]


def delete_block(path: pathlib.Path, old_lines: list) -> None:
    """Remove one exact consecutive block of lines from `path`, keeping every other line's ending."""
    lines = path.read_bytes().decode("utf-8").splitlines(keepends=True)
    norm = [line.rstrip("\r\n") for line in lines]
    n = len(old_lines)
    hits = [i for i in range(len(norm) - n + 1) if norm[i:i + n] == old_lines]
    if len(hits) != 1:
        raise SystemExit(f"{path}: expected one block starting {old_lines[0][:60]!r}, found {len(hits)}")
    del lines[hits[0]:hits[0] + n]
    path.write_bytes("".join(lines).encode("utf-8"))
    print(f"deleted {n} line(s) from {path.name}")


def insert_after(path: pathlib.Path, anchor: str, new: str) -> None:
    """Insert `new` directly after the unique line `anchor`."""
    replace_block(path, anchor, anchor + "\n" + new)


if DONE_TICKET.exists() or DONE_LANE.exists():
    raise SystemExit("closure destination already exists")

# 1. Ticket: metadata, transition, checklist, artifact link, closure note, handoff line.
replace_block(TICKET, "## Metadata\n- Task ID: TASK-2026-09-26-review-conjure-validation-error-reporting",
    f"- Completed: {T}\n"
    "- Summary: Conjure's refusal report names each broken spell with its errors and a fix, keeps the conduit\n"
    "  verdict's reasons (scope, visibility, cycles), counts warnings and marks Melder-internal codes; *args: Any\n"
    "  and the list-only notices on plain data no longer misfire. Source and tests in a62df80cb; owner accepted.\n"
    "\n## Metadata\n- Task ID: TASK-2026-09-26-review-conjure-validation-error-reporting")
replace_block(TICKET, "- Status: review", "- Status: done")
replace_block(TICKET, "- Updated: 2026-09-26T15:49:18Z", f"- Updated: {T}")
last = unique_line(TICKET, "- transition_reason: Applied to the worktree, suites green on a worktree sync;")
replace_block(TICKET, last, last + "\n- from_state: review\n- to_state: done\n"
    f"- transition_reason: Owner accepted (\"ok cool so thats fine\"); closure sync done ({T}).")
for item in ("Steps complete and checked off", "Deliverables produced and linked", "Validation status recorded",
             "Acceptance criteria reviewed with user and confirmed",
             "Board sync completed for successor routing or closure anchor update."):
    replace_block(TICKET, f"- [ ] {item}", f"- [x] {item}")
replace_block(TICKET, "  - system_docs/patches/active/validation_error_reporting_2026_09_26/",
              "  - system_docs/patches/completed/validation_error_reporting_2026_09_26/")
replace_block(TICKET, "## Context / Handoff Summary",
    f"- DATETIME: {T}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner accepted the lane (\"ok cool so thats fine notch the version and add details to the release\").\n"
    "    Closure: ticket moved to tickets/tasks/completed/; the three patch docs moved to\n"
    "    system_docs/patches/completed/validation_error_reporting_2026_09_26/ (deltas already promoted to\n"
    "    src_components and src_architecture); artifacts retained as reference; attention and artifact boards synced;\n"
    "    the commit list names the moved paths. Owner-machine suites: Not run. Open follow-up, not fixed: Phase 3\n"
    "    raises a bare \"DagNode cannot depend on itself\" for a constructor taking its own class.\n"
    "  EVIDENCE:\n"
    "  - context_compass/system_docs/patches/completed/validation_error_reporting_2026_09_26/architecture_patch.md:1-54\n"
    "  - context_compass/artifacts/validation_error_reporting_20260926/scripts/close_lane.py:1-150\n"
    "  IMPACT: The version notch and release-note details continue in a new ticket.\n"
    "  NEXT: none (closed).\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n"
    "\n## Context / Handoff Summary\n"
    f"CLOSED {T}: owner accepted; ticket, patch lane, boards and commit list synced. The Phase-3 self-dependency\n"
    "message stays an open follow-up.")

# 2. Patch doc pointer, then the moves (same folder, so mv is a rename).
replace_block(LANE / "architecture_patch.md",
    unique_line(LANE / "architecture_patch.md", "Ticket: tickets/tasks/" + NAME),
    unique_line(LANE / "architecture_patch.md", "Ticket: tickets/tasks/" + NAME).replace(
        "tickets/tasks/", "tickets/tasks/completed/", 1))
subprocess.run(["mv", "-n", str(TICKET), str(DONE_TICKET)], check=True)
subprocess.run(["mv", "-n", str(LANE), str(DONE_LANE)], check=True)
if TICKET.exists() or LANE.exists() or not DONE_TICKET.exists() or not DONE_LANE.is_dir():
    raise SystemExit("move did not land")
print("moved ticket and patch lane")

# 3. Attention board: row, detail, anchor (cap 12, oldest dropped).
AB = pathlib.Path("attention_board.md")
delete_block(AB, [unique_line(AB, "| validation_error_reporting | review | handoff |")])
delete_block(AB, [unique_line(AB, "- validation_error_reporting: SWITCH_TRIGGER"),
                  "  RESUME_HIERARCHY: tickets/tasks/" + NAME + "."])
insert_after(AB, "<!-- BEGIN USER-DEFINED: closed_anchors -->",
    f"| validation_error_reporting | done | melder_1 | tickets/tasks/completed/{NAME} | Conjure refusal report rewritten "
    "(names, reasons, fixes; conduit reasons kept); *args: Any fixed; in a62df80cb; patch lane archived; owner "
    f"accepted. | {T} |")
raw = AB.read_bytes().decode("utf-8").splitlines()
start = raw.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
end = raw.index("<!-- END USER-DEFINED: closed_anchors -->")
anchors = [line for line in raw[start + 1:end] if line.startswith("| ")]
while len(anchors) > 12:
    delete_block(AB, [anchors[-1]])
    anchors.pop()
print(f"closed anchors: {len(anchors)}")

# 4. Artifact board: active rows -> cleared rows.
ART = pathlib.Path("artifact_board.md")
prefix = f"| tickets/tasks/{NAME} |"
rows = [line.rstrip("\r\n") for line in ART.read_bytes().decode("utf-8").splitlines(keepends=True)
        if line.startswith(prefix)]
if len(rows) != 2:
    raise SystemExit(f"artifact board: expected 2 rows, found {len(rows)}")
delete_block(ART, rows)
insert_after(ART, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->",
    f"| tickets/tasks/completed/{NAME} | system_docs/patches/completed/validation_error_reporting_2026_09_26/ | "
    "promote_to_documentation | Promoted to src_components/src_architecture (conjure validation report) and the "
    f"release note; three patch files archived. | {T} |\n"
    f"| tickets/tasks/completed/{NAME} | artifacts/validation_error_reporting_20260926/ | retain_as_reference | "
    "Probes, issue catalog, before/after renders, apply and closure scripts, diffs, suite results, commit list. "
    f"| {T} |")

# 5. Commit list: moved paths.
replace_block(COMMIT_LIST,
    "context_compass/system_docs/patches/active/validation_error_reporting_2026_09_26/   (3 files, new)",
    "context_compass/system_docs/patches/completed/validation_error_reporting_2026_09_26/   (3 files; moved from\n"
    "  patches/active/ at closure - stage the deletion of the active/ copies committed in a62df80cb as well)")
replace_block(COMMIT_LIST, "context_compass/tickets/tasks/" + NAME,
    "context_compass/tickets/tasks/completed/" + NAME + "   (moved from tickets/tasks/ at closure)")
print("closure sync done at", T)

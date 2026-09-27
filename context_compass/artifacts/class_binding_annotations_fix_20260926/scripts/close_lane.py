"""Closure sync for the class binding-profile annotation lane (owner accepted 2026-09-26).

Run from the context_compass root. Anchored whole-line edits; board rows located by unique prefix at run time.
"""
import datetime
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

T = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NAME = "2026-09-26_fix_class_binding_profile_annotations_for_type_checking_names_task.md"
TICKET = pathlib.Path("tickets/tasks") / NAME
DONE_TICKET = pathlib.Path("tickets/tasks/completed") / NAME
LANE = pathlib.Path("system_docs/patches/active/class_binding_annotations_2026_09_26")
DONE_LANE = pathlib.Path("system_docs/patches/completed/class_binding_annotations_2026_09_26")
COMMIT_LIST = pathlib.Path("artifacts/class_binding_annotations_fix_20260926/results/commit_files.txt")


def lines(path: pathlib.Path) -> list:
    """Return the lines of `path` with CR/LF stripped."""
    return [line.rstrip("\r\n") for line in path.read_bytes().decode("utf-8").splitlines(keepends=True)]


def unique_line(path: pathlib.Path, prefix: str) -> str:
    """Return the single line of `path` starting with `prefix`."""
    hits = [line for line in lines(path) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"{path}: expected one line starting {prefix!r}, found {len(hits)}")
    return hits[0]


def delete_block(path: pathlib.Path, old: list) -> None:
    """Remove one exact consecutive block of lines from `path`, keeping other lines' endings."""
    raw = path.read_bytes().decode("utf-8").splitlines(keepends=True)
    norm = [line.rstrip("\r\n") for line in raw]
    hits = [i for i in range(len(norm) - len(old) + 1) if norm[i:i + len(old)] == old]
    if len(hits) != 1:
        raise SystemExit(f"{path}: expected one block starting {old[0][:60]!r}, found {len(hits)}")
    del raw[hits[0]:hits[0] + len(old)]
    path.write_bytes("".join(raw).encode("utf-8"))
    print(f"deleted {len(old)} line(s) from {path.name}")


if DONE_TICKET.exists() or DONE_LANE.exists():
    raise SystemExit("closure destination already exists")

# Ticket
replace_block(TICKET, "## Metadata\n- Task ID: TASK-2026-09-26-fix-class-binding-profile-annotations-for-type-checking-names",
    f"- Completed: {T}\n"
    "- Summary: Class binding profiles keep class-level annotations that name TYPE_CHECKING-only types (source text,\n"
    "  the ClassInspector read), so those fields count in the spell id and appear in Nexus; affected classes get a\n"
    "  new id once. Tests, docs, graph and release note done; owner accepted. Ships in 0.2.59+ (owner notches).\n"
    "\n## Metadata\n- Task ID: TASK-2026-09-26-fix-class-binding-profile-annotations-for-type-checking-names")
replace_block(TICKET, "- Status: review", "- Status: done")
replace_block(TICKET, unique_line(TICKET, "- Updated: "), f"- Updated: {T}")
last = unique_line(TICKET, "  current (2026-09-26T16:28:45Z).")
replace_block(TICKET, last, last + "\n- from_state: review\n- to_state: done\n"
    f"- transition_reason: Owner accepted (\"ok cool whats next?\"); closure sync done ({T}).")
replace_block(TICKET, "- [ ] Owner review.", "- [x] Owner review.")
replace_block(TICKET, "- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:")
for item in ("Steps complete and checked off", "Deliverables produced and linked", "Validation status recorded",
             "Acceptance criteria reviewed with user and confirmed",
             "Board sync completed for successor routing or closure anchor update."):
    replace_block(TICKET, f"- [ ] {item}", f"- [x] {item}")
replace_block(TICKET, "  - system_docs/patches/active/class_binding_annotations_2026_09_26/",
              "  - system_docs/patches/completed/class_binding_annotations_2026_09_26/")
replace_block(TICKET, "## Context / Handoff Summary",
    f"- DATETIME: {T}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner accepted (\"ok cool whats next? btw each change we make is a notch of 0.01 so its fine\").\n"
    "    Closure: ticket to tickets/tasks/completed/, patch lane to system_docs/patches/completed/ (deltas already\n"
    "    in src_components and src_architecture), artifacts retained, boards synced, commit list names the moved\n"
    "    paths. Version: owner convention is one notch per change; __version__ is left to the owner's commit-time\n"
    "    notch. Owner-machine suites: Not run.\n"
    "  EVIDENCE:\n"
    "  - context_compass/system_docs/patches/completed/class_binding_annotations_2026_09_26/architecture_patch.md:1-50\n"
    "  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/close_lane.py:1-140\n"
    "  IMPACT: melder_1 moves to the next lane (self-referencing constructor message).\n"
    "  NEXT: none (closed).\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n"
    "\n## Context / Handoff Summary\n"
    f"CLOSED {T}: owner accepted; ticket, patch lane, boards and commit list synced.")

# Patch doc pointer and moves
arch = LANE / "architecture_patch.md"
first = unique_line(arch, "Ticket: tickets/tasks/" + NAME)
replace_block(arch, first, first.replace("tickets/tasks/", "tickets/tasks/completed/", 1))
subprocess.run(["mv", "-n", str(TICKET), str(DONE_TICKET)], check=True)
subprocess.run(["mv", "-n", str(LANE), str(DONE_LANE)], check=True)
if TICKET.exists() or LANE.exists() or not DONE_TICKET.exists() or not DONE_LANE.is_dir():
    raise SystemExit("move did not land")
print("moved ticket and patch lane")

# Attention board
AB = pathlib.Path("attention_board.md")
delete_block(AB, [unique_line(AB, "| class_binding_annotations_fix | review | handoff |")])
delete_block(AB, [unique_line(AB, "- class_binding_annotations_fix: SWITCH_TRIGGER"),
                  "  RESUME_HIERARCHY: tickets/tasks/" + NAME + "."])
replace_block(AB, "<!-- BEGIN USER-DEFINED: closed_anchors -->",
    "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    f"| class_binding_annotations_fix | done | melder_1 | tickets/tasks/completed/{NAME} | Class binding profiles keep "
    f"TYPE_CHECKING-named annotations as source text; fields count in the id; patch lane archived; owner accepted. "
    f"| {T} |")
raw = lines(AB)
start = raw.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
end = raw.index("<!-- END USER-DEFINED: closed_anchors -->")
anchors = [line for line in raw[start + 1:end] if line.startswith("| ")]
while len(anchors) > 12:
    delete_block(AB, [anchors[-1]])
    anchors.pop()
print(f"closed anchors: {len(anchors)}")

# Artifact board
ART = pathlib.Path("artifact_board.md")
rows = [line for line in lines(ART) if line.startswith(f"| tickets/tasks/{NAME} |")]
if len(rows) != 2:
    raise SystemExit(f"artifact board: expected 2 rows, found {len(rows)}")
for row in rows:
    delete_block(ART, [row])
replace_block(ART, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->",
    "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    f"| tickets/tasks/completed/{NAME} | system_docs/patches/completed/class_binding_annotations_2026_09_26/ | "
    "promote_to_documentation | Promoted to src_components/src_architecture (class binding-profile annotations); "
    f"two patch files archived. | {T} |\n"
    f"| tickets/tasks/completed/{NAME} | artifacts/class_binding_annotations_fix_20260926/ | retain_as_reference | "
    f"Probes, suite results, apply/promote/author/closure scripts, diffs, commit list. | {T} |")

# Commit list
replace_block(COMMIT_LIST,
    "context_compass/system_docs/patches/active/class_binding_annotations_2026_09_26/   (2 files, new; moves to "
    "completed/ at closure)",
    "context_compass/system_docs/patches/completed/class_binding_annotations_2026_09_26/   (2 files, new; moved "
    "there at closure)")
replace_block(COMMIT_LIST, "context_compass/tickets/tasks/" + NAME,
    "context_compass/tickets/tasks/completed/" + NAME + "   (moved at closure)")
print("closure sync done at", T)

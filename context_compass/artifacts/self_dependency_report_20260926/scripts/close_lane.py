"""Closure sync for the self-dependency lane (owner: "turn it in and continue", 2026-09-26). Run from context_compass."""
import datetime
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

T = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NAME = "2026-09-26_report_self_referencing_constructor_as_validation_error_task.md"
TICKET = pathlib.Path("tickets/tasks") / NAME
DONE_TICKET = pathlib.Path("tickets/tasks/completed") / NAME
LANE = pathlib.Path("system_docs/patches/active/self_dependency_report_2026_09_26")
DONE_LANE = pathlib.Path("system_docs/patches/completed/self_dependency_report_2026_09_26")


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

long_reason = unique_line(TICKET, "- transition_reason: compiler_phase_3.py is fable_0's in-review file (C-C);")
replace_block(TICKET, long_reason,
    "- transition_reason: compiler_phase_3.py is fable_0's in-review file (C-C); CONFLICT recorded, M1-15 sent\n"
    "  (2026-09-26T16:42:46Z).")
replace_block(TICKET, "## Metadata\n- Task ID: TASK-2026-09-26-report-self-referencing-constructor-as-validation-error",
    f"- Completed: {T}\n"
    "- Summary: A constructor that takes its own class is refused through the readable report (SELF_DEPENDENCY,\n"
    "  naming the parameter) instead of a Phase-3 PhaseExecutionError or a bare ValueError at a late dynamic bind.\n"
    "  Phase-3 half landed in fable_0's C-C on request; strategy/report/tests here, committed in afded5ce6.\n"
    "\n## Metadata\n- Task ID: TASK-2026-09-26-report-self-referencing-constructor-as-validation-error")
replace_block(TICKET, "- Status: in_progress", "- Status: done")
replace_block(TICKET, unique_line(TICKET, "- Updated: "), f"- Updated: {T}")
last = unique_line(TICKET, "- transition_reason: fable_0 included the Phase-3 change in C-C (F0-16); CONFLICT resolved")
replace_block(TICKET, last, last + "\n- from_state: in_progress\n- to_state: done\n"
    f"- transition_reason: Owner asked to turn it in once done (\"turn it in and continue\"); closure sync ({T}).")
for item in ("Owner review.", "Run Ticket Microcycle during execution:",
             "Document each meaningful finding immediately in `## Notes` before further investigation.",
             "Steps complete and checked off", "Deliverables produced and linked", "Validation status recorded",
             "Acceptance criteria reviewed with user and confirmed",
             "Board sync completed for successor routing or closure anchor update."):
    replace_block(TICKET, f"- [ ] {item}", f"- [x] {item}")
replace_block(TICKET, "  - artifacts/self_dependency_report_20260926/\n- DISPOSITION: retain_as_reference",
    "  - artifacts/self_dependency_report_20260926/\n"
    "  - system_docs/patches/completed/self_dependency_report_2026_09_26/\n"
    "- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)")
replace_block(TICKET, "## Context / Handoff Summary",
    f"- DATETIME: {T}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Closure on the owner's instruction (\"ok cool turn it in and continue\", given with the choice of the\n"
    "    best option). Ticket to tickets/tasks/completed/, patch lane to system_docs/patches/completed/ (deltas in\n"
    "    src_components/src_architecture), artifacts retained, boards synced. Open follow-up, not done: a spell that\n"
    "    only consumes a cycle is listed as \"part of\" it (all cycles). Owner-machine suites: Not run.\n"
    "  EVIDENCE:\n"
    "  - context_compass/system_docs/patches/completed/self_dependency_report_2026_09_26/architecture_patch.md:1-45\n"
    "  - context_compass/artifacts/self_dependency_report_20260926/scripts/close_lane.py:1-130\n"
    "  IMPACT: melder_1 is free for the next lane.\n"
    "  NEXT: none (closed).\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n"
    "\n## Context / Handoff Summary\n"
    f"CLOSED {T}: turned in on the owner's instruction; ticket, patch lane and boards synced.")

arch = LANE / "architecture_patch.md"
first = unique_line(arch, "Ticket: tickets/tasks/" + NAME)
replace_block(arch, first, first.replace("tickets/tasks/", "tickets/tasks/completed/", 1))
subprocess.run(["mv", "-n", str(TICKET), str(DONE_TICKET)], check=True)
subprocess.run(["mv", "-n", str(LANE), str(DONE_LANE)], check=True)
if TICKET.exists() or LANE.exists() or not DONE_TICKET.exists() or not DONE_LANE.is_dir():
    raise SystemExit("move did not land")
print("moved ticket and patch lane")

AB = pathlib.Path("attention_board.md")
delete_block(AB, [unique_line(AB, "| self_dependency_report | in_progress |")])
delete_block(AB, [unique_line(AB, "- self_dependency_report: SWITCH_TRIGGER"), "  RESUME_HIERARCHY: tickets/tasks/" + NAME + "."])
replace_block(AB, "<!-- BEGIN USER-DEFINED: closed_anchors -->",
    "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    f"| self_dependency_report | done | melder_1 | tickets/tasks/completed/{NAME} | Self-referencing constructors refused "
    f"via SELF_DEPENDENCY naming the parameter (Phase-3 half in fable_0's C-C); in afded5ce6; turned in. | {T} |")
raw = lines(AB)
start = raw.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
end = raw.index("<!-- END USER-DEFINED: closed_anchors -->")
anchors = [line for line in raw[start + 1:end] if line.startswith("| ")]
while len(anchors) > 12:
    delete_block(AB, [anchors[-1]])
    anchors.pop()
print(f"closed anchors: {len(anchors)}")

ART = pathlib.Path("artifact_board.md")
delete_block(ART, [unique_line(ART, f"| tickets/tasks/{NAME} |")])
replace_block(ART, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->",
    "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    f"| tickets/tasks/completed/{NAME} | system_docs/patches/completed/self_dependency_report_2026_09_26/ | "
    "promote_to_documentation | Promoted to src_components/src_architecture (self-referencing constructors); two "
    f"patch files archived (written after implementation, recorded). | {T} |\n"
    f"| tickets/tasks/completed/{NAME} | artifacts/self_dependency_report_20260926/ | retain_as_reference | Probes, "
    f"before/prototype/after renders, apply/own/promote/author/closure scripts, diffs, fable_0 proposal, suites. | {T} |")
print("closure sync done at", T)

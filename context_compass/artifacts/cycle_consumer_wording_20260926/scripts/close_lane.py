"""Closure sync for the cycle-consumer wording lane (owner: "go ahead and turn in everything", 2026-09-26).

Run from context_compass. Refuses to run twice (destinations must not exist).
"""
import datetime
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

T = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NAME = "2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md"
TICKET = pathlib.Path("tickets/tasks") / NAME
DONE_TICKET = pathlib.Path("tickets/tasks/completed") / NAME
LANE = pathlib.Path("system_docs/patches/active/cycle_consumer_wording_2026_09_26")
DONE_LANE = pathlib.Path("system_docs/patches/completed/cycle_consumer_wording_2026_09_26")
ART_DIR = "artifacts/cycle_consumer_wording_20260926/"
SELF_LINES = len(pathlib.Path(__file__).read_text(encoding="utf-8").splitlines())


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
arch_lines = len(lines(LANE / "architecture_patch.md"))

# --- ticket ----------------------------------------------------------------------------------------------------
replace_block(TICKET, "## Metadata\n- Task ID: TASK-2026-09-26-word-cycle-consumers-in-circular-dependency-report",
    f"- Completed: {T}\n"
    "- Summary: A spell that only needs a dependency cycle is named as its consumer (\"cannot be built: it needs 'Y',\n"
    "  which is part of / depends on a dependency cycle ... 'X' itself is not part of that cycle\"; self-loops read\n"
    "  \"depends on itself\" with \"Fix '<loop spell>'\"); members, codes and details unchanged. Five unit tests, one\n"
    "  integration test, docs, graph and release note; not committed (owner commits results/commit_files.txt).\n"
    "\n## Metadata\n- Task ID: TASK-2026-09-26-word-cycle-consumers-in-circular-dependency-report")
replace_block(TICKET, "- Status: review", "- Status: done")
replace_block(TICKET, unique_line(TICKET, "- Updated: "), f"- Updated: {T}")
last = unique_line(TICKET, "- transition_reason: Code, tests, docs, graph and release note applied;")
replace_block(TICKET, last, last + "\n- from_state: review\n- to_state: done\n"
    f"- transition_reason: Owner accepted (\"ok great go ahead and turn in everything\"); closure sync ({T}).")
for item in ("Owner review.", "Run Ticket Microcycle during execution:",
             "Document each meaningful finding immediately in `## Notes` before further investigation.",
             "Steps complete and checked off", "Deliverables produced and linked", "Validation status recorded",
             "Acceptance criteria reviewed with user and confirmed",
             "Board sync completed for successor routing or closure anchor update."):
    replace_block(TICKET, f"- [ ] {item}", f"- [x] {item}")
replace_block(TICKET, "  - system_docs/patches/active/cycle_consumer_wording_2026_09_26/",
                      "  - system_docs/patches/completed/cycle_consumer_wording_2026_09_26/")
handoff = [l for l in lines(TICKET) if l.startswith("Opened 2026-09-26T17:04:41Z on owner approval. In review since")]
assert len(handoff) == 1, handoff
i = lines(TICKET).index(handoff[0])
old_handoff = lines(TICKET)[i:i + 3]
replace_block(TICKET, "\n".join(old_handoff),
    f"CLOSED {T}: owner accepted and asked to turn it in; ticket, patch lane and boards synced. Files for the\n"
    "owner's commit: artifacts/cycle_consumer_wording_20260926/results/commit_files.txt.")
replace_block(TICKET, "\n## Context / Handoff Summary",
    f"- DATETIME: {T}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Closure on owner acceptance (\"ok great go ahead and turn in everything if your happy with it\").\n"
    "    Ticket to tickets/tasks/completed/, patch lane to system_docs/patches/completed/ (deltas promoted into\n"
    "    src_components/src_architecture), artifacts retained, boards synced. Owner-side: commit, version notch,\n"
    "    asset/LLM bundle rebuild, owner-machine suites (Not run here). No open follow-up from this lane.\n"
    "  EVIDENCE:\n"
    f"  - system_docs/patches/completed/cycle_consumer_wording_2026_09_26/architecture_patch.md:1-{arch_lines}\n"
    f"  - {ART_DIR}scripts/close_lane.py:1-{SELF_LINES}\n"
    "  IMPACT: melder_1 is free for the next lane.\n"
    "  NEXT: none (closed).\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n"
    "\n## Context / Handoff Summary")

arch = LANE / "architecture_patch.md"
first = unique_line(arch, "Ticket: tickets/tasks/" + NAME)
replace_block(arch, first, first.replace("tickets/tasks/", "tickets/tasks/completed/", 1))
commits = pathlib.Path(ART_DIR) / "results/commit_files.txt"
replace_block(commits, unique_line(commits, "context_compass/system_docs/patches/active/cycle_consumer_wording_2026_09_26/"),
    "context_compass/system_docs/patches/completed/cycle_consumer_wording_2026_09_26/  (archived at closure)")
replace_block(commits, "context_compass/tickets/tasks/" + NAME, "context_compass/tickets/tasks/completed/" + NAME)
subprocess.run(["mv", "-n", str(TICKET), str(DONE_TICKET)], check=True)
subprocess.run(["mv", "-n", str(LANE), str(DONE_LANE)], check=True)
if TICKET.exists() or LANE.exists() or not DONE_TICKET.exists() or not DONE_LANE.is_dir():
    raise SystemExit("move did not land")
print("moved ticket and patch lane")

# --- attention board -------------------------------------------------------------------------------------------
AB = pathlib.Path("attention_board.md")
delete_block(AB, [unique_line(AB, "| cycle_consumer_wording | review |")])
delete_block(AB, ["- cycle_consumer_wording: SWITCH_TRIGGER is owner review of the applied wording.",
                  "  RESUME_HIERARCHY: tickets/tasks/" + NAME + "."])
replace_block(AB, "<!-- BEGIN USER-DEFINED: closed_anchors -->",
    "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    f"| cycle_consumer_wording | done | melder_1 | tickets/tasks/completed/{NAME} | A cycle's consumers are named as "
    f"consumers (members unchanged); tests, docs, graph, release note; patch lane archived; owner accepted. | {T} |")
raw = lines(AB)
start = raw.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
end = raw.index("<!-- END USER-DEFINED: closed_anchors -->")
anchors = [line for line in raw[start + 1:end] if line.startswith("| ")]
while len(anchors) > 12:
    delete_block(AB, [anchors[-1]])
    anchors.pop()
print(f"closed anchors: {len(anchors)}")

# --- artifact board --------------------------------------------------------------------------------------------
ART = pathlib.Path("artifact_board.md")
delete_block(ART, [unique_line(ART, f"| tickets/tasks/{NAME} | {ART_DIR} |")])
delete_block(ART, [unique_line(ART, f"| tickets/tasks/{NAME} | system_docs/patches/active/cycle_consumer_wording_2026_09_26/ |")])
replace_block(ART, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->",
    "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    f"| tickets/tasks/completed/{NAME} | system_docs/patches/completed/cycle_consumer_wording_2026_09_26/ | "
    "promote_to_documentation | Promoted to src_components/src_architecture (cycle consumers); two patch files "
    f"archived. | {T} |\n"
    f"| tickets/tasks/completed/{NAME} | {ART_DIR} | retain_as_reference | Probes, before/after renders, apply/"
    f"author/promote/closure scripts, diffs, suites, commit list. | {T} |")
print("closure sync done at", T)

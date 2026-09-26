"""Close the tests-docs task on the owner's turn-in (2026-09-26): notes, closure fields, move, board sync."""
import pathlib
import re
import sys

CC = pathlib.Path.home() / "mnt/melder_private/context_compass"
NAME = "2026-09-26_refresh_tests_system_docs_task.md"


def section_insert(t: str, heading: str, text: str) -> str:
    """Append `text` at the end of the section that starts at `heading`."""
    start = t.index(heading)
    nxt = t.find("\n## ", start + len(heading))
    return t[:start] + t[start:nxt].rstrip("\n") + "\n" + text + t[nxt:]


def close_ticket(now: str) -> None:
    """Write the notes and closure fields, then move the ticket to completed."""
    src = CC / "tickets/tasks" / NAME
    t = src.read_text(encoding="utf-8")
    measure = (f"\n- DATETIME: {now}\n  TYPE: MEASURE\n"
               "  CLAIM: Notched and noted: src/melder/__version__.py 0.2.73 -> 0.2.74 (CRLF kept); release header\n"
               "    `# Melder 0.2.74`; a Packaging and documentation bullet for the refreshed test maps and the\n"
               "    order-independent registration-guard and view tests; the asset line reads 0.2.74. NOTICEs M0-52 to\n"
               "    M0-54 sent first. Build assets and LLM bundles are NOT rebuilt here (owner with melder_2), so the\n"
               "    asset --check and the version-stamp unit test fail until that rebuild.\n"
               "  EVIDENCE:\n  - src/melder/__version__.py:12-12\n  - release_docs/next_version_release.md:582-589\n"
               "  IMPACT: The change carries its own notch per the owner's versioning rule.\n"
               "  NEXT: Close on the owner's turn-in.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    decision = (f"\n- DATETIME: {now}\n  TYPE: DECISION\n"
                "  CLAIM: Closed on the owner's turn-in (see the Closure Basis).\n"
                f"  EVIDENCE: tickets/tasks/completed/{NAME}\n"
                "  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.\n"
                "  NEXT: none.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    t = section_insert(t, "## Notes\n", measure + decision)
    basis = ("owner turn-in in chat (2026-09-26T22:17Z): \"if your done everything go ahead and turn in your\n"
             "  tickets and notch the version and finish adding your note to the release\".")
    summary = ("tests_architecture (895 lines, rubric 91) and tests_components (2,503 lines, rubric 85, was 74)\n"
               "  describe the current suite: CI driver, Protects lines, new clusters, corrected reset flow and counts,\n"
               "  C1 core 183 remeasured, indexes current; 0.2.74 notch and release bullet. Raised, not changed: tracked\n"
               "  bundle.json and experimentation case packages, the root conftest comment, inert Conduit._aether lines.")
    meta = t.index("## Metadata\n")
    head, body = t[:meta], t[meta:]
    assert body.count("\n- Status: review\n") == 1
    body = body.replace("\n- Status: review\n", "\n- Status: done\n", 1)
    body = re.sub(r"\n- Updated: \S+", f"\n- Updated: {now}", body, count=1)
    body = body.replace("## Metadata\n", f"## Metadata\n- Completed: {now}\n- Closure Basis: {basis}\n- Summary: {summary}\n", 1)
    t = head + body
    t = section_insert(t, "## State Transition Event\n",
                       f"- from_state: review\n- to_state: done\n- transition_reason: Owner turn-in, {now}; see the Closure Basis.\n")
    t = section_insert(t, "## Context / Handoff Summary\n", f"Closed {now} on the owner's turn-in; artifacts retained.\n")
    t = t.replace("- [ ] ", "- [x] ")
    dst = CC / "tickets/tasks/completed" / NAME
    assert not dst.exists()
    dst.write_text(t, encoding="utf-8")
    src.unlink()


def sync_boards(now: str) -> None:
    """Remove the active row and detail, add the anchor (cap 12), clear the artifact row."""
    ab = CC / "attention_board.md"
    t = ab.read_text(encoding="utf-8")
    row = [l for l in t.split("\n") if l.startswith("| tests_system_docs_refresh |")]
    assert len(row) == 1
    t = t.replace(row[0] + "\n", "")
    det = ("- tests_system_docs_refresh: SWITCH_TRIGGER is the owner's turn-in (both docs refreshed, indexed, scored >= 80).\n"
           "  RESUME_HIERARCHY: tickets/tasks/2026-09-26_refresh_tests_system_docs_task.md.\n"
           "  RESUME_HIERARCHY: tickets/tasks/2026-09-26_refresh_tests_system_docs_task.md.\n")
    assert t.count(det) == 1
    t = t.replace(det, "")
    top = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    anchor = (f"| tests_system_docs_refresh | done | melder_0 | tickets/tasks/completed/{NAME} | tests_architecture (91) and "
              f"tests_components (85) describe the current suite; 0.2.74 notch and release bullet; owner turn-in. | {now} |\n")
    t = t.replace(top, top + anchor)
    s = t.index(top) + len(top)
    e = t.index("<!-- END USER-DEFINED: closed_anchors -->")
    rows = [l for l in t[s:e].split("\n") if l.startswith("| ")]
    while len(rows) > 12:
        t = t.replace(rows[-1] + "\n", "", 1)
        rows = rows[:-1]
    ab.write_text(t, encoding="utf-8")
    art = CC / "artifact_board.md"
    a = art.read_text(encoding="utf-8")
    arow = [l for l in a.split("\n") if l.startswith("| tickets/tasks/2026-09-26_refresh_tests_system_docs_task.md |")]
    assert len(arow) == 1
    a = a.replace(arow[0] + "\n", "")
    ctop = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    cleared = (f"| tickets/tasks/completed/{NAME} | artifacts/tests_system_docs_refresh_20260926/ | retain_as_reference | "
               "Edit, remeasure, closure and inventory scripts, the citation recipe and preservation diffs of the tests "
               f"docs refresh. | {now} |\n")
    a = a.replace(ctop, ctop + cleared)
    art.write_text(a, encoding="utf-8")


def main() -> int:
    """Close and sync."""
    now = sys.argv[1]
    close_ticket(now)
    sync_boards(now)
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

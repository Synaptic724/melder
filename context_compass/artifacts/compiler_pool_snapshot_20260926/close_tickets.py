"""Closure edits for melder_0's Phase-5 pool and guard-test tickets (owner turn-in 2026-09-26). --check writes nothing."""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass/tickets"
BASIS = ("owner turn-in in chat (2026-09-26T21:59Z): \"I accept your 2/3 continue working on the last part\"\n"
         "  (the Phase-5 pool fix and the guard-test fix; the tests docs task stays open).")


def section_insert(t: str, heading: str, text: str) -> str:
    """Append `text` at the end of the section that starts at `heading`."""
    start = t.index(heading)
    nxt = t.find("\n## ", start + len(heading))
    if nxt < 0:
        return t.rstrip("\n") + "\n" + text
    return t[:start] + t[start:nxt].rstrip("\n") + "\n" + text + t[nxt:]


def close(path: str, summary: str, handoff: str, validation: str, extra: List[Tuple[str, str]], now: str) -> str:
    """Return the closed text of one ticket in review."""
    t = (ROOT / path).read_text(encoding="utf-8")
    meta = t.index("## Metadata\n")
    head, body = t[:meta], t[meta:]
    assert body.count("\n- Status: review\n") == 1, (path, "status")
    body = body.replace("\n- Status: review\n", "\n- Status: done\n", 1)
    i = body.index("\n- Updated: ")
    j = body.index("\n", i + 1)
    body = body[:i] + f"\n- Updated: {now}" + body[j:]
    body = body.replace("## Metadata\n", f"## Metadata\n- Completed: {now}\n- Closure Basis: {BASIS}\n- Summary: {summary}\n", 1)
    t = head + body
    t = section_insert(t, "## State Transition Event\n",
                       f"- from_state: review\n- to_state: done\n- transition_reason: Owner turn-in, {now}; see the Closure Basis.\n")
    note = (f"- DATETIME: {now}\n  TYPE: DECISION\n  CLAIM: Closed on the owner's turn-in (see the Closure Basis); acceptance given.\n"
            f"  EVIDENCE: tickets/tasks/completed/{path.split('/')[-1]}\n"
            "  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.\n"
            "  NEXT: none.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    t = section_insert(t, "## Notes\n", "\n" + note)
    t = section_insert(t, "## Context / Handoff Summary\n", handoff)
    assert t.count("## Validation\n- Not run.\n") == 1, (path, "validation")
    t = t.replace("## Validation\n- Not run.\n", "## Validation\n" + validation)
    for old, new in extra:
        assert t.count(old) == 1, (path, old)
        t = t.replace(old, new)
    t = t.replace("- [ ] ", "- [x] ")
    for line in t.split("\n"):
        if len(line) > 120 and (line.startswith("- Summary:") or line.startswith("- Closure Basis:")):
            raise SystemExit(f"LONG {path}: {line[:60]}")
    return t


def main() -> int:
    """Build both closed tickets, then write and move unless --check."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--now", required=True)
    a = ap.parse_args()
    now = a.now
    jobs: Dict[str, Tuple[str, str, str, List[Tuple[str, str]]]] = {
        "tasks/2026-09-26_snapshot_phase5_live_spell_pool_task.md": (
            "Compiler passes on the meld-time path (Phases 3, 4 strategies, 5, 6 frame-wide, the Phase-8 walk) iterate\n"
            "  a copy of the spell pool, and Phase 5 admits only ids with a registered state, so a concurrent bind cannot\n"
            "  abort revalidation; regression test red before, green after; 0.2.72 docs, graph, assets, LLM bundles and\n"
            "  release note current. Raised, not changed: conjure-time sweeps and the Nexus publisher's pool tuple.",
            f"Closed {now} on the owner's turn-in. Patch lane archived to\n"
            "system_docs/patches/completed/compiler_pool_snapshot_2026_09_26/ (retired_edges.json inside).\n",
            "- Regression test 5/5 red on unfixed src, 5/5 green with the fix on 3.14t and GIL; suites in the 21:35:35Z\n"
            "  note; asset and document tests 21:45:09Z. Nothing was rerun at closure.\n",
            [("  - system_docs/patches/active/compiler_pool_snapshot_2026_09_26/\n",
              "  - system_docs/patches/completed/compiler_pool_snapshot_2026_09_26/\n")]),
        "tasks/2026-09-26_fix_registration_guard_test_order_task.md": (
            "The system-document view fixtures boot a fresh Aether after their teardown resets and the guard test sets\n"
            "  up its own world, so the selection passes in either order on 3.14t and GIL. Test-only change.",
            f"Closed {now} on the owner's turn-in.\n",
            "- Both orders on 3.14t and GIL (21:26:50Z note); the 7-file selection 255 passed, 1 skipped (21:45:09Z).\n"
            "  Nothing was rerun at closure.\n",
            []),
    }
    out: Dict[str, str] = {}
    for path, (summary, handoff, validation, extra) in jobs.items():
        out[path] = close(path, summary, handoff, validation, extra, now)
        print("ok", path)
    if a.check:
        return 0
    for path, t in out.items():
        src = ROOT / path
        dst = ROOT / "tasks" / "completed" / src.name
        assert not dst.exists(), dst
        dst.write_text(t, encoding="utf-8")
        src.unlink()
        print("moved", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())

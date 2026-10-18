"""Recompute the line ranges this turn's notes cite between the epic, its stories and S6 (melder_0, 2026-10-18).

Re-wrapping a file moves its lines, so the citations are derived from the files as they stand, never typed in:
- each story's PLAN note cites the epic's first two notes (DECISION, FACT);
- the epic's DECISION note cites S6's closure DECISION note; its PLAN note the epic's Stories and Open Questions;
- S6's closure DECISION note cites the epic's DECISION note, its closure FACT note the epic's Stories section.
Idempotent; prints every range it writes. Usage (from context_compass/): sync_ranges.py
"""
import pathlib
import re

EPIC = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S6 = pathlib.Path("tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md")
STORIES = sorted(pathlib.Path("tickets/stories").glob("2026-10-18_*_story.md"))
EPIC_REF = "context_compass/" + EPIC.as_posix()
S6_REF = "context_compass/" + S6.as_posix()


def index_of(lines: list, prefix: str, start: int = 0) -> int:
    """0-based index of the first line at or after start beginning with prefix."""
    for index in range(start, len(lines)):
        if lines[index].startswith(prefix):
            return index
    raise SystemExit(f"no line starts with {prefix!r}")


def note_span(lines: list, start: int) -> str:
    """1-based range of the note whose '- DATETIME' line is at 0-based start: through its SCORE line."""
    end = index_of(lines, "  SCORE_0_TO_10:", start)
    return f"{start + 1}-{end + 1}"


def section_span(lines: list, header: str) -> str:
    """1-based range of a section: its header through the last non-blank line before the next '## '."""
    start = index_of(lines, header)
    nxt = index_of(lines, "## ", start + 1)
    end = nxt - 1
    while not lines[end].strip():
        end -= 1
    return f"{start + 1}-{end + 1}"


def set_range(text: str, pattern: str, value: str, label: str) -> str:
    """Replace the range in exactly one citation matching pattern (group 1 keeps the prefix)."""
    found = re.findall(pattern, text, flags=re.M)
    if len(found) != 1:
        raise SystemExit(f"{label}: expected one citation, found {len(found)}")
    print(f"{label}: {value}")
    return re.sub(pattern, lambda m: m.group(1) + value + m.group(2), text, flags=re.M)


def main() -> None:
    """Derive and write every range."""
    epic_lines = EPIC.read_text(encoding="utf-8").split("\n")
    first = index_of(epic_lines, "- DATETIME:", index_of(epic_lines, "## Notes"))
    second = index_of(epic_lines, "- DATETIME:", first + 1)
    fact_end = index_of(epic_lines, "  SCORE_0_TO_10:", second)
    epic_notes = f"{first + 1}-{fact_end + 1}"
    epic_decision = note_span(epic_lines, first)
    stories = section_span(epic_lines, "## Stories (Required to Complete)")
    openq = section_span(epic_lines, "## Open Questions")
    s6_lines = S6.read_text(encoding="utf-8").split("\n")
    s6_decision = None
    for index, line in enumerate(s6_lines):
        if line == "- DATETIME: 2026-10-18T11:45:58Z" and s6_lines[index + 3] == "  TYPE: DECISION":
            s6_decision = note_span(s6_lines, index)
    if s6_decision is None:
        raise SystemExit("S6's closure DECISION note not found")

    text = EPIC.read_text(encoding="utf-8")
    text = set_range(text, rf"^(  - {re.escape(S6_REF)}:)\d+-\d+()$", s6_decision, "epic DECISION -> S6")
    plan = re.findall(rf"^  - {re.escape(EPIC_REF)}:\d+-\d+$", text, flags=re.M)
    if len(plan) != 2:
        raise SystemExit(f"epic PLAN: expected two self-citations, found {len(plan)}")
    text = text.replace(plan[0], f"  - {EPIC_REF}:{stories}", 1)
    text = text.replace(plan[1], f"  - {EPIC_REF}:{openq}", 1)
    print(f"epic PLAN: {stories}, {openq}")
    EPIC.write_text(text, encoding="utf-8")

    for story in STORIES:
        text = story.read_text(encoding="utf-8")
        text = set_range(text, rf"^(  EVIDENCE: {re.escape(EPIC_REF)}:)\d+-\d+()$", epic_notes, story.name)
        story.write_text(text, encoding="utf-8")

    text = S6.read_text(encoding="utf-8")
    text = set_range(text, rf"^(  - {re.escape(EPIC_REF)}:)\d+-\d+(\n  IMPACT: Part B)", epic_decision,
                     "S6 DECISION -> epic")
    text = set_range(text, rf"^(  - {re.escape(EPIC_REF)}:)\d+-\d+(\n  - release_docs/)", stories, "S6 FACT -> epic")
    S6.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

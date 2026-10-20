"""S7 start: ready -> in_progress, the PLAN note, the handoff; the board row's next.

Run from the repository root: python s7_story_start.py <NOW>
"""
import pathlib
import re
import sys

now = sys.argv[1]
STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md")
BOARD = pathlib.Path("context_compass/attention_board.md")


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new)


story = STORY.read_text(encoding="utf-8")
before = set(story.splitlines())
story = replace_once(story, "- Status: ready\n", "- Status: in_progress\n")
story = replace_once(story, "- Updated: 2026-10-15T09:29:51Z\n", f"- Updated: {now}\n")
story = replace_once(story, """## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: ready once S6 lands.
""", f"""## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S6 landed and closed (0.2.8246, rebuilt and checked); S7 starts with the benchmarks.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S6 lands.
""")
story = replace_once(story, """  NEXT: Start after S6 closes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
""", f"""  NEXT: Start after S6 closes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S7 started on 0.2.8246 (S1-S6 landed; the S6 rebuild checks printed only OK). Order: (1) benchmarks - the
    existing meld shapes and scope cycles A/B, HEAD's 0.2.8240 tree (exported read-only with `git archive` into the VM's
    /tmp) against the working copy, processes interleaved, both GIL modes; the managed warm cycle again at 0.2.8246;
    (2) align the patch lane with the source as built (architecture patch, then each story's component and
    code-description patches), then promote it: src_architecture (boundary list, boot and cleanup sequences, meld and
    transfer sequences, invariants, failure modes, code map, sources, a diagram, handoff) and its index; src_components
    (the components and flows the member touches, sliced through the index, the code map) and its index; the tests
    docs; graph descriptors for the new modules, authored semantics and reassembly; (3) README and docs/ where the
    Existence members are listed; the release note's packaging lines; (4) archive the patch lane, sync the artifact
    board, rebuild last, close the story and hand the epic to the owner for acceptance. No `src/` change, no notch.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:21-45
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:36-56
  - context_compass/special_instructions/agent_contribution_guide.md:18-27
  IMPACT: The epic's EXIT_GATE items that remain (benchmarks, docs, graph, README, release note, rebuild) map onto
    this order; the owner's acceptance closes the epic.
  NEXT: Export HEAD's src into /tmp and write the existing-shapes A/B probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
""")
story = replace_once(story, """## Context / Handoff Summary
- Scope: S7 - docs and release.
- State: ready, blocked on S6.
- Next: benchmarks.
""", """## Context / Handoff Summary
- Scope: S7 - benchmarks, docs, graph, README, release note, patch promotion, rebuild; no `src/` change, no notch.
- State: in_progress on 0.2.8246 (PLAN note).
- Next: the existing-shapes A/B (HEAD 0.2.8240 vs the working copy), then the patch-lane alignment.
""")
long = [l for l in story.splitlines() if l not in before and len(l) > 120]
assert not long, long
STORY.write_text(story, encoding="utf-8")

board = BOARD.read_text(encoding="utf-8")
row = re.compile(r"^(\| melder_object_pools \| in_progress \| implementation \| claude \| melder_0 \| none \| )([^|]*)( \|.*\| )(\S+)( \| REQUIRED \|)$", re.M)
assert len(row.findall(board)) == 1
board = row.sub(lambda m: m.group(1) + "S7: benchmarks A/B (HEAD 0.2.8240 vs the working copy), then align and promote the patch lane into the system docs." + m.group(3) + now + m.group(5), board)
BOARD.write_text(board, encoding="utf-8")
print("S7 started", now)

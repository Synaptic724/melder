"""Record the 0.2.8247 rebuild and tick the landing's checklist item (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC now> [--check]
One MEASURE Note before the handoff summary, three checklist ticks, the handoff's rebuild and custody lines,
Updated. Every anchor must occur exactly once; new lines stay within 120 characters and ASCII.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
PATH = pathlib.Path("context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
R = "context_compass/artifacts/meld_contract_scan_20261015/runs/"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last, from the repository root on Python 3.14.7t. The first asset run wrote the agent-documentation
    and bind-guard manifests and the system-documents index, then stopped with PermissionError: the
    system-documents builder deletes its three payload modules before writing them again, and the connected folder
    refused deletes. The owner granted delete permission on melder_private for this session (used for those three
    files only), and the full run wrote all three assets at v0.2.8247 (468 agent-documentation entries, 628
    bind-guard entries, 4 system documents); --check printed only OK lines. The LLM bundles, built with
    --include-untracked because the three new test files are untracked, rewrote src (583 files), tests (1117) and
    other (404) and the manifest; --check printed only OK lines.
  EVIDENCE:
  - {R}rebuild_assets_2026_10_16_first_attempt.txt:1-29
  - {R}rebuild_assets_2026_10_16.txt:1-8
  - {R}rebuild_assets_check_2026_10_16.txt:1-8
  - {R}llm_support_2026_10_16.txt:1-9
  - {R}llm_support_check_2026_10_16.txt:1-8
  IMPACT: The change set is complete and consistent: code, tests, docs, graph, release note, notch and generated
    assets agree at 0.2.8247.
  NEXT: Send M1-19 to melder_0 (the landing is done; its files are released); then the owner's acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:70], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw
text = raw.decode("ascii")
text = replace_once(text, "- [ ] Docs, release note, notch, rebuild last.\n", "- [x] Docs, release note, notch, rebuild last.\n")
text = replace_once(text, "- [ ] Run Ticket Microcycle during execution:\n", "- [x] Run Ticket Microcycle during execution:\n")
text = replace_once(text, "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence\n",
                    "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence\n")
text = replace_once(text, "- Updated: 2026-10-16T01:50:42Z\n", f"- Updated: {NOW}\n")
text = replace_once(
    text,
    "system_docs/patches/completed/meld_state_gate_2026_10_15/; rubric 83 / 83 / 83 / 77 (B). Rebuild: pending, last.\n",
    "system_docs/patches/completed/meld_state_gate_2026_10_15/; rubric 83 / 83 / 83 / 77 (B). The assets and LLM\n"
    "bundles are rebuilt for 0.2.8247 and both checks print only OK lines.\n",
)
text = replace_once(
    text,
    "consumer costs about 2 ms a meld) await his answer. melder_0 takes back the four call-site lines and five test\n"
    "doubles at M1-19. Recorded, not fixed (outside this change): the notch-swap KeyError race, the stale spellbook.py\n",
    "consumer costs about 2 ms a meld) await his answer. M1-19 (mailbox) hands melder_0 back the four call-site lines\n"
    "and five test doubles. Recorded, not fixed (outside this change): the notch-swap KeyError race, the stale spellbook.py\n",
)
text = replace_once(text, "\n\n## Context / Handoff Summary\n", "\n" + NOTE + "\n## Context / Handoff Summary\n")
old_lines = set(raw.decode("ascii").split("\n"))
too_long = [l for l in text.split("\n") if len(l) > 120 and l not in old_lines]
assert not too_long, too_long
if not CHECK:
    PATH.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written")

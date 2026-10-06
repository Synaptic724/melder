"""Move the lane task to review: the rebuild note, checklists, state transition, validation and handoff lines.

Usage: python to_review.py <context_compass root> <UTC timestamp>
Every anchor must match exactly once; every new line must fit 120 characters.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
TICKET = ROOT / "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
RUNS = "context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs"

NOTE = f"""- DATETIME: {NOW}
  TYPE: MEASURE
  CLAIM: Rebuild, last: the system docs and the release note were copied byte-for-byte into the VM mirror, the
    asset runner wrote the three manifests there at v0.2.8215 (bind guard 619 entries, unchanged; 460 agent
    documentation entries; 4 system documents), copy_back_assets.py copied the 8 changed manifest and payload
    files to the device keeping CRLF, and the device's asset --check prints OK for all three. The LLM builder on
    the device (--include-untracked, GIT_OPTIONAL_LOCKS=0) rewrote the src, tests and other bundles and its
    --check prints OK for all three; no .git/index.lock was left. After the rebuild the mirror passes the
    package-root unit files with the stamp test, build_assets and the agent-text reader component test: 280
    passed, 24 skipped - the one failure of the landing run is gone.
  EVIDENCE:
  - {RUNS}/rebuild_assets_vm.log:1-3
  - {RUNS}/copy_back_assets.log:1-8
  - {RUNS}/check_assets_device.log:1-3
  - {RUNS}/rebuild_llm_device.log:1-4
  - {RUNS}/check_llm_device.log:1-3
  - {RUNS}/post_rebuild_package_root_vm.log:1-6
  IMPACT: The lane is complete on the tree at 0.2.8215 and waits on the owner's review and turn-in; work
    package D (MelderOps revalidation) follows the owner's wheel delivery.
  NEXT: Owner reviews and turns in this task; then D on the owner's wheel delivery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
REPLACEMENTS = [
    ("- Status: in_progress\n", "- Status: review\n"),
    ("- from_state: draft\n- to_state: in_progress\n"
     "- transition_reason: (2026-09-30T19:07:02Z) the owner's pick in chat; ticket, board row and artifact rows created"
     " before the\n  regression tests.\n",
     "- from_state: in_progress\n- to_state: review\n"
     f"- transition_reason: ({NOW}) option B landed as 0.2.8215, its regression and unit tests red,\n"
     "  then green; the system docs, graph, release note and patch archive followed, and the assets and LLM\n"
     "  bundles were rebuilt last (--check OK); the owner's turn-in remains. Earlier: draft -> in_progress\n"
     "  (2026-09-30T19:07:02Z) on the owner's pick; ticket, board row and artifact rows created before the\n"
     "  regression tests.\n"),
    ("- [ ] System docs, graph descriptors, release note, one notch, assets and LLM bundles last.\n",
     "- [x] System docs, graph descriptors, release note, one notch, assets and LLM bundles last.\n"),
    ("- [ ] Run Ticket Microcycle during execution:\n", "- [x] Run Ticket Microcycle during execution:\n"),
    ("- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.\n",
     "- [x] Document each meaningful finding immediately in `## Notes` before further investigation.\n"),
    ("  by the rebuild at the end); the epic's probe passes in every variant (runs_0_2_8215/).\n",
     "  by the rebuild at the end); the epic's probe passes in every variant (runs_0_2_8215/).\n"
     f"- After the rebuild ({NOW}): asset --check OK (device), LLM --check OK (device, --include-untracked); the\n"
     "  package-root unit files with the stamp test, build_assets and the agent-text reader component test in the\n"
     "  mirror: 280 passed, 24 skipped. Coverage: Not run.\n"),
    ("- [ ] No status transition without evidence-backed transition reason.\n",
     "- [x] No status transition without evidence-backed transition reason.\n"),
    ("- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.\n",
     "- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.\n"),
    ("- [ ] No src edit before the red regression tests, the patch docs and the NOTICE.\n",
     "- [x] No src edit before the red regression tests, the patch docs and the NOTICE.\n"),
    ("- [ ] No removal of the builder guard, no catch-and-retry.\n",
     "- [x] No removal of the builder guard, no catch-and-retry.\n"),
    ("- [ ] Steps complete and checked off\n", "- [x] Steps complete and checked off\n"),
    ("- [ ] Deliverables produced and linked\n", "- [x] Deliverables produced and linked\n"),
    ("- [ ] Documentation updated (if needed)\n", "- [x] Documentation updated (if needed)\n"),
    ("- [ ] Validation status recorded\n", "- [x] Validation status recorded\n"),
    ("- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)\n",
     "- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)\n"),
    ("- [ ] Notes quality maintained (`SCORE_0_TO_10` >=\n", "- [x] Notes quality maintained (`SCORE_0_TO_10` >=\n"),
    ("- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
     "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n"),
    ("Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). Regression and unit\n"
     "tests went red, then green; option B landed at 2026-09-30T19:44:38Z as 0.2.8215 (NOTICE M0-149..151), the full"
     " suite\nand the epic's probe green in the VM. Next: system docs, graph descriptors, release note, then the asset"
     " and\nLLM bundle rebuild last; then review for the owner's turn-in.\n",
     "Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). Regression and unit tests\n"
     "went red, then green; option B landed at 2026-09-30T19:44:38Z as 0.2.8215 (NOTICE M0-149..151), the full suite\n"
     "and the epic's probe green in the VM. The docs pass (src_architecture, src_components, tests_components), the\n"
     "graph, the release note section, the patch archive and the rebuild followed; asset and LLM --check OK.\n"
     f"In review since {NOW} (NOTICE M0-152..154): the owner's turn-in remains; work package D (MelderOps\n"
     "revalidation) waits on the owner's wheel delivery. melder_0 stays the only writer of the lane's files until\n"
     "the turn-in.\n"),
]
raw = TICKET.read_bytes()
assert b"\r\n" not in raw
text = raw.decode("utf-8")
for old, new in REPLACEMENTS:
    if text.count(old) != 1:
        raise SystemExit(f"anchor matched {text.count(old)} times: {old[:80]!r}")
    text = text.replace(old, new)
anchor = "## Context / Handoff Summary\n"
assert text.count(anchor) == 1
text = text.replace(anchor, NOTE + anchor)
text, n = re.subn(r"^- Updated: \S+$", f"- Updated: {NOW}", text, count=1, flags=re.M)
assert n == 1
added = NOTE.split("\n") + [line for _, new in REPLACEMENTS for line in new.split("\n")]
long = [line for line in added if len(line) > 120]
if long:
    raise SystemExit(f"long lines: {long}")
TICKET.write_bytes(text.encode("utf-8"))
print("review", NOW)

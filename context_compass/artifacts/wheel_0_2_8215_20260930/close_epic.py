"""Close work package C, work package D and the injected-dependency epic on the owner's directive (melder_private).

Usage: python close_epic.py <context_compass root> <UTC timestamp>
Edits the three tickets in place (the caller then moves them with mv -n), the attention and artifact boards and the
mailbox. Every anchor must match exactly once; nothing is written unless all do. Keeps each file's line endings.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
C = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
D = "tickets/tasks/2026-09-30_deliver_0_2_8215_wheel_and_revalidate_melderops_task.md"
E = "tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md"
C_DONE = C.replace("tickets/tasks/", "tickets/tasks/completed/")
D_DONE = D.replace("tickets/tasks/", "tickets/tasks/completed/")
E_DONE = E.replace("tickets/epics/", "tickets/epics/completed/")
DIRECTIVE = ("owner directive (chat, 2026-09-30): \"you can close that epic if its done, please remake the wheel and"
             " install it into priv_commandops env\"")
pending = {}
original_lines = {}


def load(relative: str) -> str:
    """Return a file's text with LF endings, remembering whether it was CRLF."""
    if relative not in pending:
        raw = (ROOT / relative).read_bytes()
        pending[relative] = [raw.decode("utf-8").replace("\r\n", "\n"), b"\r\n" in raw]
        original_lines[relative] = set(pending[relative][0].split("\n"))
    return pending[relative][0]


def edit(relative: str, old: str, new: str) -> None:
    """Replace one exact, unique anchor."""
    text = load(relative)
    if text.count(old) != 1:
        raise SystemExit(f"{relative}: anchor matched {text.count(old)} times: {old[:90]!r}")
    pending[relative][0] = text.replace(old, new)


def stamp(relative: str) -> None:
    """Set the ticket's Updated line to NOW."""
    text, n = re.subn(r"^- Updated: \S+$", f"- Updated: {NOW}", load(relative), count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"{relative}: no Updated line")
    pending[relative][0] = text


def note(relative: str, body: str) -> None:
    """Insert a note before the handoff summary."""
    edit(relative, "\n## Context / Handoff Summary\n", "\n" + body.rstrip("\n") + "\n\n## Context / Handoff Summary\n")


# ---- work package C -------------------------------------------------------------------------------------------
stamp(C)
edit(C, "- Status: review\n", "- Status: done\n")
edit(C, f"- Updated: {NOW}\n",
     f"- Updated: {NOW}\n\n- Completed: {NOW}\n"
     "- Summary: Option B landed as 0.2.8215 (notched 0.2.8215): a successful target-local pass flags each owned\n"
     "  dependency it compiled without a plan of its own, and the deferred lane runs the full target pass for a spell\n"
     "  that is not its Phase 5 root, so a provider bound after conjure melds directly after injection. 13 component\n"
     "  regressions and 14 unit tests red then green; docs, graph, release note section \"Fixed: a class bound after\n"
     "  conjure melds directly after it was injected\", assets and LLM bundles; patch docs archived.\n")
edit(C, "- from_state: in_progress\n- to_state: review\n- transition_reason: (2026-09-30T20:21:24Z) option B landed",
     f"- from_state: review\n- to_state: done\n- transition_reason: ({NOW}) the owner's directive in chat (\"you can\n"
     "  close that epic if its done\"), after work package D revalidated the installed wheel in MelderOps.\n"
     "  Earlier: in_progress -> review (2026-09-30T20:21:24Z): option B landed")
edit(C, "- [ ] No closure without acceptance confirmation and board-sync completion.\n",
     "- [x] No closure without acceptance confirmation and board-sync completion.\n")
edit(C, "- [ ] Acceptance criteria reviewed with user and confirmed\n",
     "- [x] Acceptance criteria reviewed with user and confirmed (owner directive to close the epic)\n")
edit(C, "- [ ] Board sync completed for successor routing or closure anchor update.\n",
     "- [x] Board sync completed for successor routing or closure anchor update.\n")
note(C, f"""- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Turned in on the owner's directive (chat): "you can close that epic if its done". Work package D
    rebuilt and installed the 0.2.8215 wheel in MelderOps' environments and the epic's unchanged diagnostic
    passes on it (red on 0.2.8212 in the same env), so the acceptance this task waited on is met; the board
    rows move to closed anchors and the artifact rows to cleared. melder_0 releases M0-146..148.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_0_2_8215.log:1-14
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_control_0_2_8212.log:1-15
  IMPACT: Option B is delivered and closed; nothing of this lane remains open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
""")
edit(C, "\n## Context / Handoff Summary\nOpened 2026-09-30T19:07:02Z",
     f"\n## Context / Handoff Summary\nTurned in {NOW} on the owner's directive after work package D.\n"
     "Opened 2026-09-30T19:07:02Z")

# ---- work package D -------------------------------------------------------------------------------------------
stamp(D)
edit(D, "- Status: in_progress\n", "- Status: done\n")
edit(D, f"- Updated: {NOW}\n",
     f"- Updated: {NOW}\n\n- Completed: {NOW}\n"
     "- Summary: dist/melder-0.2.8215-py3-none-any.whl built and verified (verify_wheel, smoke, sha256 cfaf55b6...4191),\n"
     "  installed in priv_commandops/.venv314 over 0.2.8212 (RECORD-verified; old files in\n"
     "  .venv314/_to_delete/melder-0.2.8212/) and in the VM env; the epic's diagnostic and the order matrix pass on it\n"
     "  (red on 0.2.8212); MelderOps suite 6561 of 6573 passed, 3 pre-existing timing failures. No source change.\n")
edit(D, "- from_state: draft\n- to_state: in_progress\n",
     f"- from_state: in_progress\n- to_state: done\n- transition_reason: ({NOW}) every exit-gate item met; the\n"
     "  owner's directive closes the epic once the diagnostic passes on the installed wheel. Earlier: draft ->\n"
     "  in_progress below.\n- from_state: draft\n- to_state: in_progress\n")
for old in ("- [ ] Stage the packaging inputs", "- [ ] Install into priv_commandops/.venv314",
            "- [ ] Upgrade the VM env;", "- [ ] Run the diagnostic, the order matrix", "- [ ] Close work package C,",
            "- [ ] Run Ticket Microcycle during execution:", "- [ ] Document each meaningful finding immediately",
            "- [ ] No status transition without evidence-backed transition reason.",
            "- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
            "- [ ] No closure without acceptance confirmation and board-sync completion.",
            "- [ ] No bytecode compiled into the Windows venv", "- [ ] Steps complete and checked off",
            "- [ ] Deliverables produced and linked", "- [ ] Documentation updated (if needed)",
            "- [ ] Validation status recorded", "- [ ] Unknown-first discipline followed",
            "- [ ] Notes quality maintained", "- [ ] Applicable anti-pattern checks are clear or escalated",
            "- [ ] Board sync completed for successor routing or closure anchor update."):
    edit(D, old, old.replace("- [ ]", "- [x]", 1))
edit(D, "- [ ] Acceptance criteria reviewed with user and confirmed\n",
     "- [x] Acceptance criteria reviewed with user and confirmed (owner directive to close the epic)\n")
edit(D, "## Validation\n- Not run yet.\n",
     "## Validation\n"
     "- verify_wheel for 0.2.8215 and the CI smoke script in an isolated 3.14t venv (GIL off); 594 RECORD hashes in\n"
     "  .venv314; an import of a copy of the installed tree; on the installed wheel in the VM env: the diagnostic and\n"
     "  the order matrix 4/4 (control on 0.2.8212: 2 failed), Toolbox 85/87 (2 skipped), melder_setup 265/265, the\n"
     "  whole MelderOps suite 6561/6573 (9 skipped; 3 timing failures that fail on 0.2.8212 too). Not run: anything\n"
     "  with the Windows interpreter itself (it compiles bytecode on its first import); coverage.\n")
note(D, f"""- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Closure on the owner's directive (chat): "you can close that epic if its done". Every exit-gate item of
    this task is met, and with it the epic's: work package C (option B, 0.2.8215), this task and the epic move to
    their completed folders; board rows become closed anchors, artifact rows cleared; NOTICEs M0-155..157 in
    melder_private and M0-158 to command_0 in priv_commandops.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/summary.txt:1-67
  - context_compass/artifacts/wheel_0_2_8215_20260930/melderops_env_install_check.log:1-3
  IMPACT: MelderOps runs the fix; the Windows run of the diagnostic is left to the owner or command_0.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
""")
edit(D, "\n## Context / Handoff Summary\nOpened ",
     f"\n## Context / Handoff Summary\nDone {NOW}: wheel in dist/, .venv314 and the VM env; diagnostic green on it;\n"
     "the old 0.2.8212 files wait in .venv314/_to_delete/melder-0.2.8212/ for an owner delete.\nOpened ")

# ---- the epic -------------------------------------------------------------------------------------------------
stamp(E)
edit(E, "- Status: in_progress\n", "- Status: done\n")
edit(E, "- Implementation status: no Melder repair attempted or claimed\n",
     "- Implementation status: repaired in Melder 0.2.8215 (work package C); the handoff itself claimed none\n")
edit(E, f"- Updated: {NOW}\n",
     f"- Updated: {NOW}\n- Completed: {NOW}\n"
     "- Summary: A dependency bound after conjure and first built by a consumer melds directly afterwards and returns\n"
     "  its scope's instance: Melder 0.2.8215 (option B) flags it at the consumer's target pass and runs its own full\n"
     "  pass on its first direct meld, with no caller step. The unchanged diagnostic passes on the installed wheel in\n"
     "  a MelderOps host (red on 0.2.8212); the wheel is in priv_commandops/.venv314.\n")
for old in ("- [ ] Both plain class binds succeed using supported public APIs.",
            "- [ ] Consumer meld succeeds with a usable injected service.",
            "- [ ] Subsequent direct service meld succeeds in the same scope and returns that exact instance.",
            "- [ ] Repeated same-scope requests preserve the selected lifetime; sibling scopes remain isolated.",
            "- [ ] The test observes the real result, not just absence of the previous error string.",
            "- [ ] No application-side compiler-cache mutation, fake instance binding or forced warm-up is required.",
            "- [ ] The original failing diagnostic is green against the delivered installed build.",
            "- [ ] Cause and supported configuration boundary are recorded; untested variants stay identified.",
            "- [ ] Any source repair completes the normal Melder validation/documentation/release obligations."):
    edit(E, old, old.replace("- [ ]", "- [x]", 1))
edit(E, "- from_state: review\n- to_state: in_progress\n",
     f"- from_state: in_progress\n- to_state: done\n- transition_reason: ({NOW}) the owner's directive in chat\n"
     "  (\"you can close that epic if its done\"); C and D met every acceptance criterion. Earlier: review ->\n"
     "  in_progress below.\n- from_state: review\n- to_state: in_progress\n")
note(E, f"""- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Epic closed on the owner's directive (chat): "you can close that epic if its done". Acceptance: the two
    binds, the consumer meld and the direct meld returning the injected instance, lifetimes and sibling isolation
    (13 component regressions, 0.2.8215); no caller step; the unchanged diagnostic green on the installed wheel in
    a MelderOps host, red on 0.2.8212 in the same env; cause and boundary recorded in the reproduce task and C;
    release obligations met (notch, release note, docs, assets, bundles). Not run: the diagnostic under the
    Windows interpreter (the same RECORD-verified files are in .venv314).
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_0_2_8215.log:1-14
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_control_0_2_8212.log:1-15
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/summary.txt:1-67
  - tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py:174-286
  - release_docs/next_version_release.md:282-306
  IMPACT: The injected-dependency defect is fixed and delivered; no work package remains open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9
""")
text = load(E)
tail = "D (installed-wheel\nrevalidation in MelderOps) follows the owner's wheel delivery.\n"
if text.count(tail) != 1:
    raise SystemExit("epic handoff tail not found")
pending[E][0] = text.replace(tail, tail + f"\n{NOW} (melder_0): D done - 0.2.8215 installed in MelderOps' environments, the "
                             "diagnostic green on it;\nepic closed on the owner's directive.\n")

# ---- attention board ------------------------------------------------------------------------------------------
B = "attention_board.md"
text = load(B)
for prefix in ("| injected_dependency_direct_resolution | review |", "| injected_dependency_wheel_delivery | in_progress |"):
    rows = [line for line in text.split("\n") if line.startswith(prefix)]
    if len(rows) != 1:
        raise SystemExit(f"board row {prefix}: {len(rows)}")
    edit(B, rows[0] + "\n", "")
    text = load(B)
edit(B, "- injected_dependency_direct_resolution: SWITCH_TRIGGER is the owner's turn-in of the task (option B landed\n"
        "  at 0.2.8215, in review) or the owner's wheel delivery opening work package D.\n"
        "  RESUME_HIERARCHY: tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md ->\n"
        "  tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md.\n", "")
edit(B, "- injected_dependency_wheel_delivery: SWITCH_TRIGGER is the diagnostic's result on the installed 0.2.8215 wheel\n"
        "  (pass: close C, D and the epic; fail: reopen C). RESUME_HIERARCHY:\n"
        "  tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md ->\n"
        "  tickets/tasks/2026-09-30_deliver_0_2_8215_wheel_and_revalidate_melderops_task.md.\n", "")
anchors = (
    f"| injected_dependency_direct_resolution | done | melder_0 | {E_DONE} | A dependency bound after conjure and "
    "first built by a consumer melds directly afterwards (option B, 0.2.8215); the unchanged MelderOps diagnostic "
    f"passes on the installed wheel. Next: none. | {NOW} |\n"
    f"| injected_dependency_wheel_delivery | done | melder_0 | {D_DONE} | 0.2.8215 wheel verified and installed in "
    ".venv314 (0.2.8212 in _to_delete/) and the VM env; diagnostic 4/4 (red on 0.2.8212); MelderOps suite "
    f"6561/6573, 3 pre-existing timing failures. Next: none. | {NOW} |\n"
    f"| injected_provider_first_direct_meld | done | melder_0 | {C_DONE} | Option B landed and notched 0.2.8215: "
    "target-pass flags, the deferred lane's full pass; regressions red to green; docs, graph, release note, "
    f"assets and bundles. Next: none. | {NOW} |\n")
edit(B, "<!-- BEGIN USER-DEFINED: closed_anchors -->\n", "<!-- BEGIN USER-DEFINED: closed_anchors -->\n" + anchors)
text = load(B)
for prefix in ("| transaction_session_cleanup_race | done |", "| document_publication_race | done |",
               "| owner_assets_rebuild | done |"):
    rows = [line for line in text.split("\n") if line.startswith(prefix)]
    if len(rows) != 1:
        raise SystemExit(f"anchor {prefix}: {len(rows)}")
    edit(B, rows[0] + "\n", "")
    text = load(B)
region = text.split("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")[1].split("<!-- END USER-DEFINED")[0]
if len([line for line in region.split("\n") if line.startswith("| ")]) != 12:
    raise SystemExit("closed anchors are not 12")
edit(B, "<!-- END USER-DEFINED: alerts -->\n",
     "".join(f"- NEW MESSAGE for {who} (from melder_0, {NOW})\n" for who in ("fable_0", "muse_0", "melder_2"))
     + "<!-- END USER-DEFINED: alerts -->\n")

# ---- artifact board -------------------------------------------------------------------------------------------
R = "artifact_board.md"
text = load(R)
cleared = []
for ticket, path, disposition, reason in (
        (C, "system_docs/patches/completed/injected_provider_first_direct_meld_2026_09_30/", "promote_to_documentation",
         "Promoted to src_architecture, src_components, tests_components and the graph at landing (0.2.8215); four "
         "patch docs archived."),
        (C, "artifacts/injected_provider_first_direct_meld_20260930/", "retain_as_reference",
         "Src, test, doc, graph and release-note apply scripts, the verified release example, red/green and suite "
         "logs, the 0.2.8215 rebuild and check logs."),
        (C, "artifacts/injected_provider_direct_meld_20260930/", "retain_as_reference",
         "Bare-Melder probe and runs (0.2.8212, 0.2.8214 and 0.2.8215); the acceptance probe of option B."),
        (E, "artifacts/2026-09-30_injected_dependency_direct_resolution/", "retain_as_reference",
         "command_0's red receipts, provenance and diagnostic; the diagnostic passes on the installed 0.2.8215 wheel."),
        (D, "artifacts/wheel_0_2_8215_20260930/", "retain_as_reference",
         "Wheel build, verify and smoke logs, the .venv314 install check, the diagnostic red/green and the MelderOps "
         "suite runs with their timing controls."),
):
    rows = [line for line in text.split("\n") if line.startswith(f"| {ticket} | {path} |")]
    if len(rows) != 1:
        raise SystemExit(f"artifact row {path}: {len(rows)}")
    edit(R, rows[0] + "\n", "")
    text = load(R)
    done = {C: C_DONE, D: D_DONE, E: E_DONE}[ticket]
    cleared.append(f"| {done} | {path} | {disposition} | {reason} | {NOW} |\n")
edit(R, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
     "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + "".join(cleared))

# ---- mailbox --------------------------------------------------------------------------------------------------
M = "mailbox_board.md"
text = load(M)
messages = ""
for number, who in ((155, "fable_0"), (156, "muse_0"), (157, "melder_2")):
    messages += (f"- TO: {who}\n  FROM: melder_0\n  DATETIME: {NOW}\n  TYPE: NOTICE\n"
                 f"  CLAIM: M0-{number}. The injected-dependency epic is closed on the owner's word: option B (0.2.8215)\n"
                 "    is turned in, dist/melder-0.2.8215-py3-none-any.whl is installed in priv_commandops/.venv314 and the\n"
                 "    VM MelderOps env, and the epic's diagnostic passes on it. melder_0 releases M0-146..148 (meld.py,\n"
                 "    spellbook_creation_system.py, the two comment files, the lane's tests). Notch above 0.2.8215 if you\n"
                 "    land a src change after.\n"
                 f"  EVIDENCE: context_compass/{E_DONE}\n  ACK_REQUESTED: false\n")
edit(M, "<!-- END USER-DEFINED: messages -->\n", messages + "<!-- END USER-DEFINED: messages -->\n")
rows = [line for line in load(M).split("\n") if line.startswith("| melder_0 | claude | 2026-09-26T22:24:06Z |")]
if len(rows) != 1:
    raise SystemExit("mailbox row")
edit(M, rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {NOW} | active |")

# ---- write ----------------------------------------------------------------------------------------------------
for relative, (text, crlf) in pending.items():
    for number, line in enumerate(text.split("\n"), 1):
        if line in original_lines[relative]:
            continue  # pre-existing text is not this pass's to rewrap
        if len(line) > 120 and not line.startswith("|") and relative.startswith("tickets/"):
            if " " in line.strip()[2:] or not line.strip().startswith("- "):
                raise SystemExit(f"{relative}:{number} is {len(line)} characters: {line[:80]}")
for relative, (text, crlf) in pending.items():
    (ROOT / relative).write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("wrote", relative, "CRLF" if crlf else "LF")

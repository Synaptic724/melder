"""Open the two epics the owner asked for on 2026-10-24, with their children routed (melder_0, 2026-10-25).

The owner's ask (chat 2026-10-24): "focus on 2 and 3 make an epic for each and investigate them" - 2 being the three
codegen-room p1 defects (D-10, D-11, D-20), 3 the in-flight borrower meld racing a lender's notch fan-out. One
all-or-nothing pass: EPIC-2026-10-25-codegen_room_policy_defects and EPIC-2026-10-25-notch_fanout_inflight_melds from
templates/epic_template.md; their four existing backlog tasks moved to tickets/tasks/ (os.rename, no delete), set
in_progress for melder_0, each with a PLAN note, a re-measure step and a current resume view; four board rows with
their detail entries; the four artifact rows repointed and one added for this folder; M2-38 consumed into the first
epic, its message deleted and its alert cleared; M0-222 sent to melder_1 (author of the race task) with its alert;
melder_0's roster row refreshed. Refuses when another message for melder_0 waits, when a target exists, when a file
changed since it was read, or when a line breaks the width rule.
Usage: open_epics_20261025.py --check | --apply
"""
import os
import pathlib
import re
import sys
from typing import Dict, List

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

EPIC_A = "tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md"
EPIC_B = "tickets/epics/2026-10-25_notch_fanout_inflight_melds_epic.md"
D10 = "2026-10-10_deny_file_access_under_safe_codegen_task.md"
D11 = "2026-10-10_enforce_import_policy_on_dynamic_imports_task.md"
D20 = "2026-10-10_refuse_materializing_over_live_modules_task.md"
RACE = "2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md"
OLD = {name: "tickets/tasks/backlog/" + name for name in (D10, D11, D20, RACE)}
NEW = {name: "tickets/tasks/" + name for name in (D10, D11, D20, RACE)}
FOLDER_A = "artifacts/codegen_room_policy_20261025/"
FOLDER_B = "artifacts/notch_fanout_race_20261025/"
PACK = "artifacts/core_protection_review_20261010/probes/"
SCAN = "artifacts/meld_contract_scan_20261015/"
STORY_M2 = "tickets/stories/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md"
ARCH = "system_docs/src_architecture.md"
CORE_TEST = "tests/integration/melder/aether/test_codegen_core_boundary_integration.py"
ASK = "\"focus on 2 and 3 make an epic for each and investigate them\""


class Pass(Record):
    """The opening pass: staged edits, moved tasks, one checked flush."""

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.moved_from: Dict[str, str] = {}

    def checked_flush(self, apply: bool) -> None:
        for rel, before in list(self.original.items()) + list(self.moved_from.items()):
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel in (EPIC_A, EPIC_B) + tuple(NEW.values()):
            if (self.ROOT / rel).exists():
                sys.exit(f"EXISTS {rel}; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for old in self.moved_from:
                print("would move", old)
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        for name in (D10, D11, D20, RACE):
            os.rename(self.ROOT / OLD[name], self.ROOT / NEW[name])
            print("moved", OLD[name], "->", NEW[name])
        self.flush()


def template_block(template: str, first: str, stop: str) -> str:
    lines = (Record.ROOT / template).read_text(encoding="utf-8").split("\n")
    return "\n".join(lines[lines.index(first):lines.index(stop)]).rstrip("\n")


def template_tail(template: str, first: str) -> str:
    lines = (Record.ROOT / template).read_text(encoding="utf-8").split("\n")
    return "\n".join(lines[lines.index(first):]).rstrip("\n")


def replace_section(r: Pass, text: str, heading: str, body: str, label: str) -> str:
    """Replace the body under `heading` (a whole `## ` line) up to the next `## ` heading."""
    start = text.index(heading + "\n") if text.count(heading + "\n") == 1 else sys.exit(f"SECTION {label}")
    end = text.index("\n\n## ", start)
    r.check_width(body, label)
    return text[:start] + heading + "\n" + body + text[end:]


def plan_notes(r: Pass) -> Dict[str, str]:
    """One PLAN note per child task, with the evidence the plan runs from."""
    plans = {}
    plans[D10] = r.note(r.now, "PLAN", [
        "Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),", ASK + ".",
        "The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) codegen_probe.py, open-write and",
        "open-read of a core file under the five postures; (2) the strict xfail test_safe_profile_refuses_writing_files;",
        "(3) a read at today's lines of the safe deny list and the profiles that reuse it, the builtins strategy and the",
        "builtin-policy and name-resolution strategies; (4) the file routes the acceptance criteria name (`open`,",
        "`io.open`, `os.open`, pathlib writes) probed under each profile, so the posture question (D2) is put to the",
        "owner with each profile's answer today."],
        ["context_compass/" + PACK + "codegen_probe.py:1-60", CORE_TEST + ":136-166"],
        ["The owner decides D2 on today's postures, not on the 2026-10-10 ones."],
        ["Copy the 0.2.8267 tree to /tmp and run the probe, the GIL off and on."], "REQUIRED", 8)
    plans[D11] = r.note(r.now, "PLAN", [
        "Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),", ASK + ".",
        "The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) codegen_probe2.py, `__import__`",
        "of denied and unlisted roots under the five postures; (2) the four strict xfails",
        "test_hybrid_refuses_dynamic_imports_of_its_denied_roots; (3) a read at today's lines of the compiler's builtin",
        "controls and the import-policy, name-resolution and reflection strategies; (4) the routes a static refusal of",
        "the name would miss (an alias of `__import__`, `builtins.__import__`, `__builtins__['__import__']`,",
        "`importlib` reached through an allowed module) probed, so options A and B are costed on what each covers."],
        ["context_compass/" + PACK + "codegen_probe2.py:1-38", CORE_TEST + ":169-206"],
        ["The owner chooses A, B or both knowing which dynamic routes each option closes today."],
        ["Copy the 0.2.8267 tree to /tmp and run the probe, the GIL off and on."], "REQUIRED", 8)
    plans[D20] = r.note(r.now, "PLAN", [
        "Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),", ASK + ".",
        "The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) probe_materialize.py and",
        "probe_materialize_fail.py (a core, a new melder.*, a stdlib and an installed name materialized; the originals",
        "lost on a failed materialize and on cleanup); (2) the materialize verb unit tests; (3) a read at today's lines",
        "of CodegenCommandSystem.materialize_codegen and SyntheticModule's publication, execution and cleanup; (4) every",
        "other publisher of a SyntheticModule (the crystallizer's restore, rebuild and graft lanes) listed with what it",
        "expects of sys.modules, so the guard's place is chosen with them in view; (5) the builtins materialized source",
        "runs with, observed."],
        ["context_compass/" + PACK + "probe_materialize.py:1-52",
         "context_compass/" + PACK + "probe_materialize_fail.py:1-34",
         "tests/unit/melder/aether/test_codegen_materialize_verb.py:1-146"],
        ["The owner answers the namespace and builtins questions knowing which lanes a guard would meet."],
        ["Copy the 0.2.8267 tree to /tmp and run both probes, the GIL off and on."], "REQUIRED", 8)
    plans[RACE] = r.note(r.now, "PLAN", [
        "Scheduled under EPIC-2026-10-25-notch_fanout_inflight_melds at the owner's ask (chat 2026-10-24),", ASK + ";",
        "melder_0 takes it over from melder_1, its author (M0-222). The re-measure, on a /tmp copy of the 0.2.8267 tree:",
        "(1) probe_rule2_race_rate.py <tree> 20 with the GIL off and on, and diag_race_kinds.py <tree> 400 140 with it",
        "off; (2) the race test (-k racing) in both modes; (3) the in-Book probe this task asks for: a dependent melded",
        "on four threads while its own Book notches the dependency; (4) a whole read of `Conduit.notch_spell` and its",
        "fan-out, `ConduitWard._emit_index_notch`, the receivers' contracted-map mutators, the notch transaction's seal",
        "and gate freeze, the creation gates a borrower meld holds, `Meld._execute_admitted`, the hydrators'",
        "`_resolve_spell_lookup` and Phase 8's `_allow_missing_contract_providers`, with why the emissions run after the",
        "transaction (0.2.8231); (5) both designs costed - refuse at the three sites, or order the fan-out under the",
        "borrowers' frozen gates."],
        ["context_compass/" + SCAN + "probe_rule2_race_rate.py:1-97",
         "context_compass/" + SCAN + "diag_race_kinds.py:1-178",
         "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:626-675"],
        ["The owner chooses the design on today's mechanism and cost, not on the 0.2.8249 measurement."],
        ["Copy the 0.2.8267 tree to /tmp and run the rate probe, the GIL off and on."], "REQUIRED", 8)
    return plans


TRANSITION = """\
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), {ask},
  scheduled it under {epic}; melder_0 re-measures it on 0.2.8267
  and puts {question} to the owner."""

STEP = ("- [ ] Re-measure on 0.2.8267 ({epic}): rerun the reproducer\n"
        "      and the {tests}, the GIL off and on; read the cited code at today's lines; record MEASURE\n"
        "      and FACT notes; put {question} to the owner.\n")

SUMMARIES = {
    D10: """\
Scheduled 2026-10-25 under EPIC-2026-10-25-codegen_room_policy_defects (the owner's ask); in_progress, melder_0,
investigation only. Scope unchanged: `open` reads and writes files under every codegen profile, safe included,
against safe's documented posture (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note);
nothing run yet. Next: (1) rerun codegen_probe.py and the strict xfail on a /tmp copy, the GIL off and on; (2) read
the deny list and the strategies at today's lines; (3) put D2 to the owner as a DECISION_REQUEST.""",
    D11: """\
Scheduled 2026-10-25 under EPIC-2026-10-25-codegen_room_policy_defects (the owner's ask); in_progress, melder_0,
investigation only. Scope unchanged: `__import__` bypasses the codegen import gate under hybrid, the precision
overlay and permissive (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note); nothing run
yet. Next: (1) rerun codegen_probe2.py and the four strict xfails on a /tmp copy, the GIL off and on; (2) read the
compiler's controls and the strategies at today's lines and probe the routes option A would miss; (3) put the
choice of A, B or both to the owner as a DECISION_REQUEST.""",
    D20: """\
Scheduled 2026-10-25 under EPIC-2026-10-25-codegen_room_policy_defects (the owner's ask); in_progress, melder_0,
investigation only. Scope unchanged: materialize_codegen replaces live core, stdlib and dependency modules and
cannot restore them (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note); nothing run
yet. Next: (1) rerun probe_materialize.py and probe_materialize_fail.py on a /tmp copy, the GIL off and on; (2) read
the verb and SyntheticModule at today's lines and list the other publishers; (3) put the namespace and builtins
questions to the owner as a DECISION_REQUEST.""",
    RACE: """\
Scheduled 2026-10-25 under EPIC-2026-10-25-notch_fanout_inflight_melds (the owner's ask); in_progress, melder_0
(taken over from melder_1, its author; M0-222), investigation only. Scope: a borrower meld in flight during a lender
notch's fan-out must end in a version or the clean SpellbookValidationError refusal (the 0.2.8227 rule), never an
object built with the SpellContract default or an internal RuntimeError. Evidence so far: melder_1's two Notes of
2026-10-16 (0.2.8248-0.2.8249). State: the re-measure on 0.2.8267 is planned (PLAN note); nothing run yet. Rule 2
landed the race test marked xfail(strict=False) naming this task; removing that marker is part of the exit gate.
Next: (1) rerun both probes and the race test on a /tmp copy, the GIL off and on; (2) write and run the in-Book
probe; (3) read the fan-out and the gates whole, then cost the two designs for the owner.""",
}


def edit_task(r: Pass, name: str, plan: str) -> None:
    old, new = OLD[name], NEW[name]
    text = r.read(old)
    r.moved_from[old] = text
    if name == RACE:
        text = r.once(text, "- Story: none (standalone backlog task; split off "
                      "TASK-2026-10-16-recheck_contract_consumers_when_provider_changes by\n"
                      "  the owner's decision of 2026-10-16)\n",
                      "- Story: none; parent EPIC-2026-10-25-notch_fanout_inflight_melds (split off\n"
                      "  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes by the owner's decision of "
                      "2026-10-16)\n", "race story")
        text = r.once(text, "- Agent Name: unassigned\n- Agent Role: UNKNOWN\n",
                      "- Agent Name: melder_0\n- Agent Role: synaptic_python_developer\n", "race agent")
        text = r.once(text, "- context_compass/tickets/tasks/backlog/" + RACE + "\n",
                      "- context_compass/tickets/tasks/" + RACE + "\n- context_compass/" + FOLDER_B +
                      " (the re-measure's runs and the in-Book probe)\n", "race files")
        text = r.once(text, "- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created "
                      "2026-10-16T15:54:20Z; evidence in Notes.\n",
                      "- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created "
                      "2026-10-16T15:54:20Z; evidence in Notes.\n  melder_0 (synaptic_python_developer); "
                      "investigation and evidence; from 2026-10-25 (Notes).\n", "race attribution")
        epic, tests, question = "EPIC-2026-10-25-notch_fanout_inflight_melds", "race test", "the design choice"
        text = r.once(text, "- [ ] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on the current tree, GIL "
                      "off and on; add an in-Book\n      probe (a dependent melded on threads while its own Book "
                      "notches the dependency).\n",
                      "- [ ] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on 0.2.8267\n      (" + epic +
                      "), GIL off and on; add an in-Book probe (a dependent melded on\n      threads while its "
                      "own Book notches the dependency).\n", "race step")
        text = r.once(text, "- context_compass/" + SCAN + " (the probes and runs; new probes land beside them)\n",
                      "- context_compass/" + SCAN + " (the probes and their 2026-10-16 runs; rule 2's evidence)\n",
                      "race scan line")
        steps_done = True
    else:
        text = r.once(text, "- Story: none (defect found by TASK-2026-10-08-review_core_protection_fork_aware_updates,"
                      " completed 2026-10-10)\n",
                      "- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by\n"
                      "  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)\n",
                      name + " story")
        text = r.once(text, "- Agent Name: unassigned\n",
                      "- Agent Name: melder_0\n- Agent Role: synaptic_python_developer\n", name + " agent")
        epic = "EPIC-2026-10-25-codegen_room_policy_defects"
        tests = {D10: "strict xfail", D11: "four strict xfails", D20: "materialize verb tests"}[name]
        question = {D10: "the posture question (D2)", D11: "the choice of A, B or both",
                    D20: "the two questions"}[name]
        first = {D10: "- [ ] Owner answers the posture question; patch docs written and linked.\n",
                 D11: "- [ ] Record the design choice; write and link patch docs.\n",
                 D20: "- [ ] Owner answers the two questions; patch docs written and linked.\n"}[name]
        step = STEP.format(epic=epic, tests=tests, question=question)
        text = r.once(text, first, step + first, name + " step")
        steps_done = True
    assert steps_done
    text = r.once(text, "- Status: draft\n", "- Status: in_progress\n", name + " status")
    text = replace_section(r, text, "## State Transition Event",
                           TRANSITION.format(ask=ASK, epic=epic, question=question), name + " transition")
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + plan + "\n\n## Context / Handoff Summary\n",
                  name + " note")
    text = replace_section(r, text, "## Context / Handoff Summary", SUMMARIES[name], name + " summary")
    r.stage(new, text)
    r.set_field(new, "Updated")


ANTI = """\
## Applicable Anti-Patterns
- [ ] No epic-state transition without task-level evidence.
- [ ] No closure while a child task is incomplete or unaccepted.
- [ ] No program claims without source evidence from task notes.
- [ ] No src/ edit before the owner's answer and the patch docs."""

def epic_a_notes(r: Pass) -> str:
    decision = r.note(r.now, "DECISION", [
        "The owner's ask (chat 2026-10-24), after melder_0 listed what it could take next:",
        ASK + " - 2 being the three codegen-room p1",
        "defects D-10, D-11 and D-20. This epic reuses their three backlog tasks as its children (ticketing.md:",
        "search and reuse before creating), each moved to tickets/tasks/ and in_progress for melder_0 with its own",
        "board row. The investigation is read-only on src/ and tests/, runs on a /tmp copy of 0.2.8267 with the GIL",
        "off and on, and ends in one DECISION_REQUEST per task; no fix starts before the owner's answer and its",
        "patch docs."],
        [r.whole(NEW[D10]), r.whole(NEW[D11]), r.whole(NEW[D20])],
        ["The defects are re-measured on today's tree before the owner is asked, so his answers rest on current code."],
        ["Run the four reproducers and the five strict xfails on the /tmp copy, the GIL off and on."], "REQUIRED", 8)
    fact = r.note(r.now, "FACT", [
        "M2-38 (melder_2's NOTICE, 2026-10-24T23:21:55Z, consumed here): melder_2's lane",
        "(STORY-2026-10-24-testpypi_trusted_publishing_and_provenance) edits .github/workflows/release-candidate.yml,",
        ".github/scripts (testpypi_candidate.py, ci_policy.py, a new testpypi_provenance.py), a new .github/provenance/,",
        "tests/unit/github_workflows, .github/ci_cd, .github/BRANCH_WORKFLOW.md and system_docs/tests_components.md,",
        "with no src change, and rebuilds at its turn-in. melder_0 holds none of them. This epic's investigation",
        "touches none of them; a fix that adds tests updates tests_components.md after melder_2's turn-in or by",
        "arrangement with melder_2."],
        [r.doc_block(STORY_M2, "- EXECUTION_BOUNDARY:")],
        ["tests_components.md is not free for this epic until melder_2 turns in; a fix is the first step that needs it."],
        ["Check melder_2's board row before a fix updates tests_components.md."], "HELPFUL", 7)
    return decision + "\n\n" + fact


def epic_b_notes(r: Pass) -> str:
    return r.note(r.now, "DECISION", [
        "The owner's ask (chat 2026-10-24): " + ASK + " - 3 being",
        "the in-flight borrower meld racing a lender's notch fan-out (p1: one of its outcomes returns a wrong object",
        "silently). This epic takes melder_1's backlog task",
        "TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout as its child, moved to tickets/tasks/,",
        "in_progress for melder_0 (melder_1 told by M0-222), and keeps the two related backlog tasks out (the lent",
        "consumer's provider loss; the seam's park-before-check order). The investigation is read-only on src/ and",
        "tests/, runs on a /tmp copy of 0.2.8267 with the GIL off and on, adds the in-Book probe the task asks for,",
        "and ends in one DECISION_REQUEST: refuse at the failure sites, or order the fan-out under the borrowers'",
        "frozen gates."],
        [r.whole(NEW[RACE]),
         r.doc_block(ARCH, "- Known, not fixed (pre-existing; filed as TASK-2026-10-16-order_inflight")],
        ["The design is put to the owner with today's mechanism and cost, not the 0.2.8249 measurement."],
        ["Run probe_rule2_race_rate.py, diag_race_kinds.py and the race test on the /tmp copy, the GIL off and on."],
        "REQUIRED", 8)


def epic_a(r: Pass) -> str:
    t = "templates/epic_template.md"
    parts = [
        "# Epic: Codegen rooms hold the policy their profile states (D-10, D-11, D-20)",
        "",
        "## Metadata",
        "- Epic ID: EPIC-2026-10-25-codegen_room_policy_defects",
        "- Status: in_progress",
        "- Owner: Mark",
        "- Agent Name: melder_0",
        "- Agent Role: synaptic_python_developer",
        "- Priority: p1",
        f"- Created: {r.now}",
        f"- Updated: {r.now}",
        "- Target Window: set by the owner once the three decision requests are answered",
        "- Related Program/Initiative: the core-protection review (TASK-2026-10-08-review_core_protection_fork_aware_"
        "updates,\n  completed 2026-10-10) and its governed-evolution contract (C1.4, C3.2, C6)",
        "",
        "## Problem / Opportunity",
        """\
The core-protection review left three p1 defects of the codegen rooms open, each in a draft backlog task, on the
owner's word (2026-10-10): "Keep the filesystem-access and dynamic-import gaps explicitly open until fixed and
verified".
- D-10: the `safe` profile documents that it denies writes, yet room code under it - and under every other
  profile - reads and writes any file the process can reach through the `open` builtin.
- D-11: under hybrid, the precision overlay and permissive, `__import__(...)` loads roots their import lists deny
  or leave out, because the import gate reads import statements only.
- D-20: `materialize_codegen` publishes a SyntheticModule over any live module name - Melder's own, the standard
  library's, an installed dependency's - and its failure and cleanup paths never put the displaced module back.
Codegen rooms are where agents build the subsystem they sit in (src_architecture, What Melder Is), and the ACL
profile is the structure that states what their code may do; a profile that does not hold the posture it states is
wrong structure. All three were measured at 66939dfe8 (2026-10-10); the tree is 0.2.8267 now, so each recorded
cause is UNKNOWN until re-measured. The owner's ask (chat 2026-10-24):
""" + ASK + ".",
        "",
        "## MRP Alignment (Most Reasonable Product)",
        """\
The profiles are the contract an agent or an owner reads before running code in a room. The MRP is a profile that
holds what it states - its file posture, its import roots and the names its room may publish - and a refusal that
names what was refused and why. In-process checks are defence in depth, never isolation (review contract C6.1),
and every fix is described that way.""",
        "",
        "## Ticket Contract",
        """\
- ENTRY_GATE: the owner's ask recorded (Notes, DECISION); the three child tasks moved out of the backlog, assigned
  to melder_0 and routed on attention_board.md, one row each.
- EXECUTION_BOUNDARY: now, investigation: read-only on src/ and tests/; runs on a /tmp copy of the 0.2.8267 tree,
  the GIL off and on; scripts, runs and any new probe under """ + FOLDER_A + """; findings in
  each task's Notes, the synthesis and the decision requests here. After the owner's answers, task by task: patch
  docs before any src/ edit (patch_framework_gating), then the fix, its tests, docs, notch, release-note entry and
  the rebuild.
- DEPENDENCIES: the review's evidence pack (artifacts/core_protection_review_20261010/: probes, recorded outputs,
  README) and its contract (C1.4, C3.2, C3.4, C4.3, C6; the open D2); src_components (Component: Codegen Internal
  Engine, Component: Nexus Descriptor And ACL Managers, Component: RiftSpace Workstation And Command Surface,
  Subcomponent: SyntheticModule Runtime); tests_components.md is held by melder_2 until its turn-in (M2-38, Notes).
- EXIT_GATE: each child task closed with its acceptance criteria met, or closed on the owner's word; each Breaking
  change in the release note; src_architecture records each defect closed; board and artifact sync.
- FAILURE_ESCALATION: a DECISION_REQUEST per owner question (D-10's posture, D-11's option, D-20's namespace and
  builtins); CONFLICT when today's tree contradicts a task's recorded cause; BLOCKER when a file a fix needs is
  held by another lane.""",
        "",
        "## Goals (Outcomes)",
        """\
- Each defect re-measured on 0.2.8267, the GIL off and on, its mechanism read at today's lines, and its owner
  question put with options, cost and a recommendation.
- After the answers: every profile holds the file and import posture it states, and a materialize never displaces
  a live module and leaves sys.modules as it found it on every exit.""",
        "",
        "## Non-Goals (Explicit Exclusions)",
        """\
- An OS sandbox, read-only mounts or a separate agent process (the review's D2 item 4, the owner's decision).
- The contents of the allow and deny lists (D2), ProtocolCrafter's writers, and live in-place module replacement
  as a feature (the review's D7 keeps it an experiment lane).
- Calling any fix isolation (the C6.4 wording rule).""",
        "",
        "## Scope Boundaries",
        """\
- In scope: D-10, D-11 and D-20 as their tasks define them, and whether today's tree changed any recorded cause.
- Out of scope: other codegen-room behaviour; writers outside the process (contract C6.3).""",
        "",
        "## State Transition Event",
        """\
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24),
  """ + ASK + """ - 2 being the three codegen-room p1 defects.""",
        "",
        "## Success Metrics",
        """\
- The four reproducers and the five strict xfails run on 0.2.8267, the GIL off and on, and recorded in the tasks.
- Each owner question answered before its fix starts.
- After the fixes: the five strict xfail markers gone because their tests pass, and the probes report refusals.""",
        "",
        "## Requirements (Functional + Non-Functional)",
        """\
- Functional: after the owner's answers, each task's acceptance criteria.
- Non-functional: room code that stays inside its posture pays no cost the fix does not measure and record; each
  refusal names the builtin, import root or module refused and the remedy.""",
        "",
        "## Constraints / Assumptions",
        """\
- Device git is read-only for agents; the owner commits.
- Runs use /tmp copies of the tree only: cache writes land under the package root.
- UNKNOWN until re-measured: whether the 2026-10-10 causes hold at 0.2.8267.""",
        "",
        "## Dependencies / External References",
        """\
- TASK-2026-10-08-review_core_protection_fork_aware_updates (completed) and its evidence pack,
  context_compass/artifacts/core_protection_review_20261010/README.md
- The three child tasks (Tasks).""",
        "",
        "## Milestones (Track Progress)",
        """\
- [ ] Milestone 1: re-measured - each reproducer and xfail run on 0.2.8267 and the cited code read (task Notes).
- [ ] Milestone 2: decided - the owner answers the three questions (this epic's Notes).
- [ ] Milestone 3: fixed - each task lands with its patch docs, tests, notch, release-note entry and rebuild.""",
        "",
        "## Stories (Required to Complete)",
        "- none: each defect is one deliverable and stays a task (Tasks).",
        "",
        "## Tasks (Cross-Cutting or Epic-Level)",
        """\
- [ ] Task: TASK-2026-10-10-deny-file-access-under-safe-codegen (D-10) - `open` under safe; the posture question.
- [ ] Task: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports (D-11) - `__import__` against the import
      lists; option A, B or both.
- [ ] Task: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20) - the generation namespace and exits
      that restore sys.modules; room builtins for materialized code.
- [ ] Task: Verify Ticket Microcycle enforcement across the three tasks.""",
        "",
        "## Acceptance Criteria (Epic Done)",
        """\
- The three child tasks closed with their acceptance criteria met, or closed on the owner's word.
- The release note carries each Breaking change; src_architecture records each defect closed.
- Board and artifact sync done at each closure.""",
        "",
        "## Risks / Mitigations",
        """\
- A fix breaks a room workflow that relied on the old posture (Breaking): each task pins the posture the owner
  chooses with symptom-named tests, and the release note names the change.
- A guard inside SyntheticModule would also meet the crystallizer's restore, rebuild and graft lanes: the D-20
  task lists every publisher before the guard's place is chosen.
- Overstated protection: every document says defence in depth, not isolation (C6.4).""",
        "",
        ANTI,
        "",
        "## Validation / Test Approach",
        """\
- Reproducers, run on a /tmp copy, the GIL off and on: codegen_probe.py (D-10), codegen_probe2.py (D-11),
  probe_materialize.py and probe_materialize_fail.py (D-20), from the review's pack.
- Tests: the five strict xfails in """ + CORE_TEST + """ and
  tests/unit/melder/aether/test_codegen_materialize_verb.py.
- Not run until recorded in the tasks' Notes.""",
        "",
        "## Rollout / Adoption Plan",
        """\
- Each fix ships with a Breaking entry in the running release note for room code that relied on the old
  behaviour. No persisted state, cache generation or record version is expected to move (UNKNOWN until each
  design is written).""",
        "",
        "## Open Questions",
        """\
- D-10 (the review's D2): deny `open` under hybrid and precision too, which reuse safe's deny list today? The
  task's recommendation (2026-10-10): deny it under safe, hybrid and precision; leave permissive and full_access
  as documented open postures.
- D-11: option A (deny the `__import__` name statically wherever an import list applies), B (a runtime guard on
  the room's `__import__`), or both? The task's recommendation (2026-10-10): both.
- D-20: where is the generation namespace declared - an ACL capability rule, a Nexus or room configuration value,
  or one fixed prefix (recommended: an ACL rule) - and does materialized code run with the room's filtered
  builtins (recommended: yes)?
- Each is checked against today's tree before it is put to the owner.""",
        "",
        "## Decision Log",
        "- " + r.now[:10] + ": the epic opened on the owner's ask; its children are the three existing tasks.",
        "",
        template_block(t, "## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED: true | false"),
        "",
        """\
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + FOLDER_A + """ (this epic's scripts and runs)
  - """ + PACK + """ (the reproducers and their 2026-10-10 outputs; the review's)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure; the review's pack stays with the review.""",
        "",
        """\
## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none""",
        "",
        """\
## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this epic; """ + r.now[:10] + """.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested""",
        "",
        "## Notes",
        epic_a_notes(r),
        "",
        template_block(t, "## Closure Confirmation", "## Context / Handoff Summary"),
        "",
        "## Context / Handoff Summary",
        """\
Scope: the three codegen-room p1 defects - D-10 `open` under safe, D-11 `__import__` past the import lists, D-20 a
materialize over live modules - each in its own child task. State: in_progress, melder_0; investigation only; the
three tasks are routed on the board, one row each. Controlling decisions: none yet; the three owner questions are
in Open Questions. Next: (1) rerun the reproducers and the five strict xfails on a /tmp copy of 0.2.8267, the GIL
off and on; (2) read each task's cited code at today's lines; (3) put each question to the owner with today's
options.""",
        "",
        template_tail(t, "## Project-Specific Additions"),
    ]
    return "\n".join(parts) + "\n"


def epic_b(r: Pass) -> str:
    t = "templates/epic_template.md"
    parts = [
        "# Epic: A borrower meld in flight during a lender's notch ends in a version or a clean refusal",
        "",
        "## Metadata",
        "- Epic ID: EPIC-2026-10-25-notch_fanout_inflight_melds",
        "- Status: in_progress",
        "- Owner: Mark",
        "- Agent Name: melder_0",
        "- Agent Role: synaptic_python_developer",
        "- Priority: p1",
        f"- Created: {r.now}",
        f"- Updated: {r.now}",
        "- Target Window: set by the owner once the design decision is made",
        "- Related Program/Initiative: rule 2 of the owner's 2026-10-15 direction\n"
        "  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes, completed, 0.2.8250), which filed this\n"
        "  race as known and not fixed",
        "",
        "## Problem / Opportunity",
        """\
With the GIL off, a meld of a borrower's SpellContract consumer that runs while the lender's `notch_spell` fans out
to its borrowers can return the consumer built with the raw SpellContract default - its AttributeError surfaces
only when the object is used - or raise one of the internal RuntimeErrors "Cannot build CreationContext before
spell_codegen_creation exists.", "many_only manifest references unknown spell_id" and "Spell creation context was
not published". melder_1 measured it on 0.2.8248-0.2.8249 (with the GIL off 7 of 20 runs of four meld threads
against 20 notches end a thread so; with it on, 0 of 20) and traced it to one gap: `notch_spell` fans out after its
transaction ends, so a meld already past its gate is not ordered against the park and the reactivation
(src_architecture, Failure Modes and Error Paths: "Known, not fixed"). A consumer built against no provider is
wrong structure handed to an agent, and nothing tells the agent until it calls the object. The owner's ask (chat
2026-10-24): """ + ASK + ".",
        "",
        "## MRP Alignment (Most Reasonable Product)",
        """\
Agents iterate on one object through notches while its borrowers keep melding (src_architecture, What Melder Is).
The MRP is a meld racing a notch that ends in a version - the outgoing or the incoming one - or in the clean
SpellbookValidationError refusal the 0.2.8227 rule gives a meld racing a sever, and never in an object built
against no provider or an internal RuntimeError.""",
        "",
        "## Ticket Contract",
        """\
- ENTRY_GATE: the owner's ask recorded (Notes, DECISION); the child task moved out of the backlog, assigned to
  melder_0 and routed on attention_board.md; melder_1, its author, told (M0-222).
- EXECUTION_BOUNDARY: now, investigation: read-only on src/ and tests/; runs on a /tmp copy of the 0.2.8267 tree,
  the GIL off and on; runs and the in-Book probe under """ + FOLDER_B + """; findings in the
  task's Notes, the design request here. After the owner's decision: patch docs before any src/ edit, then the
  fix, its tests, docs, notch, release-note entry and the rebuild.
- DEPENDENCIES: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (completed, 0.2.8250: the marks,
  the meld's catch-up and the race test marked xfail with the task's id); the 0.2.8227 rule (a meld racing a sever
  refuses cleanly) and the 0.2.8231 lock rule (the ward's emissions run after the transaction); custody of
  conduit.py, conduit_ward.py, meld.py and the hydrators, asked for before any edit (no active board row names
  them today); tests_components.md is held by melder_2 until its turn-in (M2-38, recorded in
  EPIC-2026-10-25-codegen_room_policy_defects).
- EXIT_GATE: the child task closed with its exit gate met; src_architecture's "Known, not fixed" entry replaced by
  the fix's invariant; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST for the design; CONFLICT if ordering the fan-out inside the notch window
  breaks the ward or mediator lock order; BLOCKER while a file the fix needs is held by another lane.""",
        "",
        "## Goals (Outcomes)",
        """\
- The race re-measured on 0.2.8267, the GIL off and on, and its in-Book variant (a dependent melded while its own
  Book notches the dependency) measured for the first time.
- The mechanism read whole at today's lines and the two designs costed - refuse at the failure sites, or order the
  fan-out under the borrowers' frozen gates - for the owner's decision.
- After the decision: no meld in flight during a notch returns an object built with a SpellContract default or
  raises an internal RuntimeError, in either GIL mode.""",
        "",
        "## Non-Goals (Explicit Exclusions)",
        """\
- Rule 2's marks and the meld's catch-up: they make the next meld correct and stay as they are.
- The lent consumer's Book-local provider loss (TASK-2026-10-16-investigate_lent_consumer_provider_loss, backlog)
  and the seam's park-before-check order (TASK-2026-10-16-notch_seam_checks_incoming_before_parking, backlog).
- Conjure's link-later tolerance of a missing provider.""",
        "",
        "## Scope Boundaries",
        """\
- In scope: melds of borrower spells whose plan resolves a contracted copy, in flight during a lender notch's
  fan-out; the three failure sites; the order of the fan-out against the notch transaction and the borrowers'
  creation gates; the in-Book variant.
- Out of scope: the Non-Goals above.""",
        "",
        "## State Transition Event",
        """\
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24),
  """ + ASK + """ - 3 being the in-flight borrower
  meld racing a lender's notch fan-out.""",
        "",
        "## Success Metrics",
        """\
- Both race probes and the race test run on 0.2.8267, the GIL off and on, and recorded in the task.
- The owner's design decision recorded before any src/ edit.
- After the fix: the race test passes without its xfail marker in both GIL modes, and the race probe shows no
  unexpected exception over at least 100 GIL-off runs (the task's exit gate).""",
        "",
        "## Requirements (Functional + Non-Functional)",
        """\
- Functional: after the decision, the task's exit gate.
- Non-functional: a warm meld pays nothing measurable; a notch's cost is measured before and after the fix.""",
        "",
        "## Constraints / Assumptions",
        """\
- Device git is read-only for agents; the owner commits.
- Runs use /tmp copies of the tree only.
- UNKNOWN until re-measured: whether the 0.2.8249 rate and kinds hold at 0.2.8267, and whether the in-Book variant
  races at all.""",
        "",
        "## Dependencies / External References",
        """\
- context_compass/""" + SCAN + """ (the race probes and their 2026-10-16 runs; rule 2's evidence)
- tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py (the race test)""",
        "",
        "## Milestones (Track Progress)",
        """\
- [ ] Milestone 1: re-measured - both probes, the race test and the in-Book probe run on 0.2.8267 (task Notes).
- [ ] Milestone 2: decided - the owner chooses the design (this epic's Notes).
- [ ] Milestone 3: fixed - the task lands with its patch docs, tests, measurements, notch and rebuild.""",
        "",
        "## Stories (Required to Complete)",
        "- none: the race is one deliverable and stays a task (Tasks).",
        "",
        "## Tasks (Cross-Cutting or Epic-Level)",
        """\
- [ ] Task: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout - re-measure, read the fan-out and
      the gates, cost the designs, then the fix.
- [ ] Task: Verify Ticket Microcycle enforcement on the task.""",
        "",
        "## Acceptance Criteria (Epic Done)",
        """\
- The child task closed with its exit gate met, or closed on the owner's word.
- src_architecture's "Known, not fixed" entry replaced; the release note carries the fix.
- Board and artifact sync done.""",
        "",
        "## Risks / Mitigations",
        """\
- Refusing at the sites keeps the window (a meld refuses where it could have built either version) and touches
  compile and hydration paths; ordering the fan-out closes the window but moves ward emissions that 0.2.8231 placed
  after the transaction on purpose. Both are costed before the owner is asked.
- A race probe is statistical: a rate over too few runs hides a regression; the exit gate asks for 100 runs.""",
        "",
        ANTI,
        "",
        "## Validation / Test Approach",
        """\
- probe_rule2_race_rate.py <tree> 20 and diag_race_kinds.py <tree> 400 140 from rule 2's evidence folder, and the
  race test (-k racing), on a /tmp copy, the GIL off and on; the in-Book probe beside them.
- Not run until recorded in the task's Notes.""",
        "",
        "## Rollout / Adoption Plan",
        """\
- The fix ships with an entry in the running release note. No persisted state, cache generation or record version
  is expected to move (UNKNOWN until the design is written).""",
        "",
        "## Open Questions",
        """\
- The design: refuse at the three failure sites (Phase 8's missing-provider tolerance at meld time,
  `Meld._execute_admitted` after a failed rebuild, the hydrators' pool lookup of a plan's step ids), or order the
  fan-out under the borrowers' frozen gates? Each is costed in the task before the owner is asked.
- Does a notch inside one Book race a dependent's in-flight meld the same way? Not measured yet (the in-Book
  probe).""",
        "",
        "## Decision Log",
        "- " + r.now[:10] + ": the epic opened on the owner's ask; its child is melder_1's existing backlog task.",
        "",
        template_block(t, "## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED: true | false"),
        "",
        """\
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + FOLDER_B + """ (this epic's runs and the in-Book probe; created with the first runs)
  - """ + SCAN + """ (the race probes and their 2026-10-16 runs; rule 2's)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure; rule 2's folder stays with rule 2.""",
        "",
        """\
## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none""",
        "",
        """\
## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this epic; """ + r.now[:10] + """.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested""",
        "",
        "## Notes",
        epic_b_notes(r),
        "",
        template_block(t, "## Closure Confirmation", "## Context / Handoff Summary"),
        "",
        "## Context / Handoff Summary",
        """\
Scope: the in-flight borrower meld racing a lender's notch fan-out (p1), in one child task. State: in_progress,
melder_0; investigation only; the task is routed on the board. Controlling decisions: none yet; the design question
is in Open Questions. Next: (1) rerun both race probes and the race test on a /tmp copy of 0.2.8267, the GIL off
and on; (2) write and run the in-Book probe; (3) read the fan-out and the gates whole, then cost the two designs.""",
        "",
        template_tail(t, "## Project-Specific Additions"),
    ]
    return "\n".join(parts) + "\n"


ROWS = [
    ("codegen_open_file_d10", D10, EPIC_A,
     "Rerun codegen_probe.py and the strict xfail on a /tmp copy of 0.2.8267, the GIL off and on; read the deny list "
     "and the strategies at today's lines.",
     "D-10 re-measured on 0.2.8267, its mechanism read and the posture question (D2) put to the owner.",
     "The owner answers the posture question, or redirects."),
    ("codegen_dynamic_import_d11", D11, EPIC_A,
     "Rerun codegen_probe2.py and the four strict xfails on the /tmp copy, the GIL off and on; probe the routes "
     "option A would miss.",
     "D-11 re-measured on 0.2.8267, its mechanism read and options A and B costed for the owner.",
     "The owner chooses A, B or both, or redirects."),
    ("codegen_materialize_d20", D20, EPIC_A,
     "Rerun probe_materialize.py and probe_materialize_fail.py on the /tmp copy, the GIL off and on; list every "
     "SyntheticModule publisher.",
     "D-20 re-measured on 0.2.8267, its mechanism read and the namespace and builtins questions put to the owner.",
     "The owner answers both questions, or redirects."),
    ("notch_fanout_race", RACE, EPIC_B,
     "Rerun probe_rule2_race_rate.py, diag_race_kinds.py and the race test on the /tmp copy, the GIL off and on; "
     "write the in-Book probe.",
     "The race re-measured on 0.2.8267 and in one Book, its mechanism read and the two designs costed for the owner.",
     "The owner chooses the design, or redirects."),
]


def board(r: Pass) -> None:
    text = r.read(r.BOARD)
    rows, details = "", ""
    for item, name, epic, nxt, outcome, exit_signal in ROWS:
        rows += (f"| {item} | in_progress | discovery | claude | melder_0 | none | {nxt} | {outcome} | {exit_signal} "
                 f"| {NEW[name]} | {r.now} | REQUIRED |\n")
        details += (f"- WORK_ITEM: {item}\n  SWITCH_TRIGGER: {exit_signal}\n  RESUME_HIERARCHY:\n    - {epic}\n"
                    f"    - {NEW[name]}\n")
    text = r.once(text, "<!-- END USER-DEFINED: active_items -->", rows + "<!-- END USER-DEFINED: active_items -->",
                  "rows")
    text = r.once(text, "<!-- END USER-DEFINED: active_attention_details -->",
                  details + "<!-- END USER-DEFINED: active_attention_details -->", "details")
    text = r.once(text, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-24T23:21:55Z)\n", "", "alert M2-38")
    text = r.once(text, "<!-- END USER-DEFINED: alerts -->",
                  f"- NEW MESSAGE for melder_1 (from melder_0, {r.now})\n<!-- END USER-DEFINED: alerts -->",
                  "alert M0-222")
    r.stage(r.BOARD, text)


def artifacts(r: Pass) -> None:
    text = r.read(r.ARTIFACTS)
    reruns = {
        D10: ("D-10 reproducer with its recorded output (codegen_probe_output.txt); rerun on 0.2.8267 under "
              "EPIC-2026-10-25-codegen_room_policy_defects, the runs in " + FOLDER_A + "runs/."),
        D11: ("D-11 reproducer with its recorded output (codegen_probe2_output.txt); rerun on 0.2.8267 under "
              "EPIC-2026-10-25-codegen_room_policy_defects, the runs in " + FOLDER_A + "runs/."),
        D20: ("D-20 reproducers (with probe_materialize_fail.py) and their recorded outputs; rerun on 0.2.8267 under "
              "EPIC-2026-10-25-codegen_room_policy_defects, the runs in " + FOLDER_A + "runs/."),
        RACE: ("The meld-vs-notch race classifier (kinds, first tracebacks, timelines) with probe_rule2_race_rate.py "
               "and their runs (runs/diag_race_kinds_*_gil0.txt, runs/probe_rule2_race_rate_*_gil*.txt); rerun on "
               "0.2.8267 under EPIC-2026-10-25-notch_fanout_inflight_melds, the runs in " + FOLDER_B + "runs/."),
    }
    for name, nxt in reruns.items():
        found = re.findall(r"^\| " + re.escape(OLD[name]) + r" \| (\S+) \| (\S+) \| backlog \| retain_as_reference \| "
                           r"[^|]+ \| \S+ \| HELPFUL \|$", text, flags=re.M)
        lines = [line for line in text.split("\n") if line.startswith("| " + OLD[name] + " |")]
        if len(found) != 1 or len(lines) != 1:
            sys.exit(f"ARTIFACT ROW {name}: {len(lines)}")
        path, kind = found[0]
        text = text.replace(lines[0], f"| {NEW[name]} | {path} | {kind} | active | retain_as_reference | {nxt} | "
                                      f"{r.now} | HELPFUL |")
    row = (f"| {EPIC_A} | {FOLDER_A} | investigation_evidence | active | retain_as_reference | The opening script of "
           f"both epics (scripts/) and the 0.2.8267 reruns of D-10, D-11 and D-20 (runs/, as they land); disposition "
           f"decided at closure. | {r.now} | HELPFUL |\n")
    text = r.once(text, "<!-- END USER-DEFINED: active_artifacts -->", row + "<!-- END USER-DEFINED: active_artifacts -->",
                  "artifact row")
    r.stage(r.ARTIFACTS, text)


def mailbox(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    region = text[text.index("<!-- BEGIN USER-DEFINED: messages -->"):text.index("<!-- END USER-DEFINED: messages -->")]
    mine = re.findall(r"^- TO: melder_0\n(?:  .*\n)+", region, flags=re.M)
    if len(mine) != 1 or "FROM: melder_2\n  DATETIME: 2026-10-24T23:21:55Z" not in mine[0] or "CLAIM: M2-38." not in mine[0]:
        sys.exit("MESSAGES for melder_0 other than M2-38 wait: read them first; nothing written")
    text = r.once(text, mine[0], "", "M2-38 consumed")
    message = """\
- TO: melder_1
  FROM: melder_0
  DATETIME: {now}
  TYPE: NOTICE
  CLAIM: M0-222. On the owner's ask (chat 2026-10-24: "focus on 2 and 3 make an epic for each and investigate
    them") I took your TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout under the new
    EPIC-2026-10-25-notch_fanout_inflight_melds: moved to tickets/tasks/, in_progress, melder_0. Investigation only -
    read-only on src/, runs on /tmp copies of 0.2.8267. Before any edit of conduit.py, conduit_ward.py, meld.py or
    the hydrators I will ask you for custody; tell me if you hold or plan any of them.
  EVIDENCE: context_compass/{epic}
  ACK_REQUESTED: false
""".format(now=r.now, epic=EPIC_B)
    r.check_width(message, "M0-222")
    text = r.once(text, "<!-- END USER-DEFINED: messages -->", message + "<!-- END USER-DEFINED: messages -->",
                  "M0-222")
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW melder_0: {len(rows)}")
    r.stage(r.MAILBOX, text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |"))


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("open_epics_20261025")
    mailbox(r)
    plans = plan_notes(r)
    for name in (D10, D11, D20, RACE):
        edit_task(r, name, plans[name])
    for rel, build in ((EPIC_A, epic_a), (EPIC_B, epic_b)):
        text = build(r)
        r.check_width(text, rel)
        r.stage(rel, text)
    # The tasks' new lines are width-checked where they are staged (`once`, `replace_section`); their older lines
    # stay as their authors wrote them.
    board(r)
    artifacts(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()

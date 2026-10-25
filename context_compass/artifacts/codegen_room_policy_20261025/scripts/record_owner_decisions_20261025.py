"""Record the owner's three codegen decisions of 2026-10-25 (melder_0).

The owner answered the three decision requests of EPIC-2026-10-25-codegen_room_policy_defects in chat on 2026-10-25:
D-10 "safe + hybrid + precision", D-11 "A + B (static + runtime)", D-20 "ACL rule + filtered builtins" - each the
recommended option. One all-or-nothing pass: a DECISION note on each child task and a program-level DECISION note on
the epic; the epic's milestones 1-2, Open Questions, Decision Log and Context / Handoff Summary; each task's re-measure
step checked and its summary; the three codegen board rows' `next`. Refuses when a file changed since it was read or
a line breaks the width rule. Usage: record_owner_decisions_20261025.py --check | --apply
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

EPIC = "tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md"
D10 = "tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md"
D11 = "tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md"
D20 = "tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md"
REMEASURE = "- DATETIME: 2026-10-25T00:23:47Z"


class Pass(Record):
    @staticmethod
    def check_width(block: str, label: str) -> None:
        """As Record.check_width, also exempting a lone unbreakable path bullet (configuration_standards.md)."""
        for line in block.split("\n"):
            if len(line) <= 120 or "context_compass/" in line or line.startswith("| ") or line.startswith("|---"):
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and " " not in stripped[2:]:
                continue
            sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def task_decision(r: Pass, rel: str, section: str, claim: list, impact: list, nxt: list) -> str:
    return r.note(r.now, "DECISION", claim,
                  [r.doc_section(rel, section), r.note_range(rel, REMEASURE, "  TYPE: FACT")],
                  impact, nxt, "REQUIRED", 9)


def record_task(r: Pass, rel: str, note: str, summary_old: str, summary_new: str) -> None:
    text = r.read(rel)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + note + "\n\n## Context / Handoff Summary\n",
                  rel + " note")
    text = r.once(text, "- [ ] Re-measure on 0.2.8267 (", "- [x] Re-measure on 0.2.8267 (", rel + " step")
    text = r.once(text, summary_old, summary_new, rel + " summary")
    r.stage(rel, text)
    r.set_field(rel, "Updated")


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_owner_decisions")
    d10 = task_decision(r, D10, "## Decision Needed Before Implementation", [
        "The owner's decision on D2 (chat 2026-10-25, answering the decision request): deny `open` under safe,",
        "hybrid and precision; permissive and full_access stay documented open postures - the recommended option.",
        "The three share one tuple today (`SAFE_DENIED_BUILTIN_NAMES`, which hybrid and precision alias), so the",
        "deny-list change covers exactly them. Carried into the patch doc for the owner's confirmation: hybrid also",
        "allows `import pathlib` (it is on hybrid's import allow list, not precision's), and the re-measure shows a",
        "pathlib write accepted under hybrid; denying `open` leaves that route, so the patch doc states hybrid's",
        "file posture with and without pathlib on its list."],
        ["The fix proceeds on a decided posture; the pathlib residue is named before the patch doc, not found after."],
        ["On the owner's go: write the patch docs (architecture + component patch for the codegen ACL profiles)."])
    d11 = task_decision(r, D11, "## Design Options (implementer proposes, owner decides)", [
        "The owner's decision (chat 2026-10-25, answering the decision request): option A + B - the recommended",
        "option. A: wherever an import list applies, the static gate refuses a reference to the `__import__` name,",
        "with a message naming it. B: the room's runtime `__builtins__['__import__']` becomes a wrapper that checks",
        "each import's root against the compiled allowed and denied roots and raises ImportError naming the root;",
        "import statements of allowed roots keep working because they call the wrapper. A design constraint the",
        "re-measure's read fixes: A cannot reuse `denied_builtin_names` as it stands, because that one list also",
        "strips names from the runtime builtins, and a missing `__import__` breaks every import statement; A is a",
        "static-only refusal and B keeps the name present, wrapped."],
        ["The fix proceeds on a decided design with its one structural constraint recorded before the patch doc."],
        ["On the owner's go: write the patch docs (the compiler's builtin controls, the static strategies,",
         "the namespace builtins)."])
    d20 = task_decision(r, D20, "## Questions for the Owner", [
        "The owner's decision (chat 2026-10-25, answering the decision request): the generation namespace is declared",
        "as a codegen ACL capability rule (module-root conditions in each frame's posture, carried by the existing",
        "compile path), and materialized code runs with the room's filtered builtins, the same mapping",
        "execute_codegen uses - the recommended option. What follows for the patch doc: materialize_codegen refuses",
        "a name outside the declared namespace, a name already in sys.modules, a protected core root, a stdlib name",
        "and an installed import name, before anything is registered or published; every exit leaves sys.modules and",
        "the parent attribute as found; the guard sits at the verb, because the crystallizer's restore, rebuild and",
        "graft lanes publish SyntheticModules outside any room's posture. Carried into the patch doc for the owner's",
        "confirmation: a frame that declares no namespace rule refuses every materialize (recommended: fail closed)."],
        ["The fix proceeds on a decided design; the default for a frame without a rule is named before the patch doc."],
        ["On the owner's go: write the patch docs (the verb's name policy, SyntheticModule's exits, the builtins)."])
    record_task(r, D10, d10,
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the\n"
                "strict xfail still XFAILs. Decision pending: D2 (deny `open` under safe; hybrid and precision too?).",
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the\n"
                "strict xfail still XFAILs. Decided 2026-10-25 (DECISION note): deny `open` under safe, hybrid and\n"
                "precision; hybrid's pathlib route goes to the patch doc. Next, on the owner's go: patch docs, red\n"
                "tests, the fix, notch and rebuild.")
    record_task(r, D11, d11,
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
                "four\nstrict xfails still XFAIL. Decision pending: option A, B or both.",
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
                "four\nstrict xfails still XFAIL. Decided 2026-10-25 (DECISION note): A + B, with A static-only. Next,"
                " on the\nowner's go: patch docs, red tests, the fix, notch and rebuild.")
    record_task(r, D20, d20,
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
                "verb\ntests pass. Decision pending: the generation namespace, and room builtins for materialized code.",
                "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
                "verb\ntests pass. Decided 2026-10-25 (DECISION note): an ACL capability rule declares the namespace;"
                " materialized\ncode gets the room's filtered builtins; a frame with no rule fails closed (to confirm"
                " in the patch doc).\nNext, on the owner's go: patch docs, red tests, the fix, notch and rebuild.")
    epic_note = r.note(r.now, "DECISION", [
        "The owner answered the epic's three decision requests in chat on 2026-10-25, each with the recommended",
        "option: D-10 deny `open` under safe, hybrid and precision (permissive and full_access stay open); D-11 A + B",
        "(a static refusal of the `__import__` name where an import list applies, plus a runtime `__import__` wrapper",
        "checking every root); D-20 an ACL capability rule declares the generation namespace and materialized code",
        "runs with the room's filtered builtins. Each task's DECISION note carries the one point its patch doc puts",
        "back to the owner (D-10 hybrid's pathlib route; D-11 A is static-only; D-20 a frame with no rule fails",
        "closed). Tranche order when the owner says go: D-10, D-11, D-20 - smallest to largest, each with its own",
        "patch docs, red tests, notch and rebuild."],
        [r.doc_section(D10, "## Decision Needed Before Implementation"),
         r.doc_section(D11, "## Design Options (implementer proposes, owner decides)"),
         r.doc_section(D20, "## Questions for the Owner")],
        ["Milestone 2 is met; the epic moves to its fixes on the owner's go."],
        ["Ask the owner for the go on D-10 first."], "REQUIRED", 9)
    text = r.read(EPIC)
    text = r.once(text, "\n\n## Closure Confirmation\n", "\n\n" + epic_note + "\n\n## Closure Confirmation\n",
                  "epic note")
    text = r.once(text, "- [ ] Milestone 1: re-measured", "- [x] Milestone 1: re-measured", "milestone 1")
    text = r.once(text, "- [ ] Milestone 2: decided", "- [x] Milestone 2: decided", "milestone 2")
    start = text.index("## Open Questions\n")
    end = text.index("\n\n## Decision Log")
    open_questions = """\
## Open Questions
- Answered on 2026-10-25 (Decision Log; Notes): D-10, D-11 and D-20, each with the recommended option.
- Put back to the owner in the patch docs: hybrid's `pathlib` route once `open` is denied (D-10), and a frame that
  declares no generation namespace failing closed (D-20)."""
    r.check_width(open_questions, "open questions")
    text = text[:start] + open_questions + text[end:]
    text = r.once(text, "- 2026-10-25: the epic opened on the owner's ask; its children are the three existing tasks.\n",
                  "- 2026-10-25: the epic opened on the owner's ask; its children are the three existing tasks.\n"
                  "- 2026-10-25: D-10 - deny `open` under safe, hybrid and precision (the owner).\n"
                  "- 2026-10-25: D-11 - A + B, a static refusal of the name plus a runtime `__import__` wrapper (the "
                  "owner).\n"
                  "- 2026-10-25: D-20 - an ACL capability rule declares the namespace; filtered builtins (the owner).\n",
                  "decision log")
    old_summary = text[text.index("## Context / Handoff Summary\n"):text.index("\n\n## Project-Specific Additions")]
    new_summary = """\
## Context / Handoff Summary
Scope: the three codegen-room p1 defects - D-10 `open` under safe, D-11 `__import__` past the import lists, D-20 a
materialize over live modules - each in its own child task. State: in_progress, melder_0. Milestones 1 (all three
re-measured on 0.2.8267: unchanged, causes confirmed at today's lines) and 2 (the owner's three decisions, Notes) are
met. Next, on the owner's go, task by task in the order D-10, D-11, D-20: patch docs, red tests, the fix, notch,
release-note entry and rebuild."""
    r.check_width(new_summary, "epic summary")
    text = text.replace(old_summary, new_summary)
    r.stage(EPIC, text)
    r.set_field(EPIC, "Updated")
    board = r.read(r.BOARD)
    nexts = {
        "codegen_open_file_d10": "On the owner's go: patch docs for his decision (deny `open` under safe, hybrid and "
        "precision), then red tests, the fix, notch and rebuild.",
        "codegen_dynamic_import_d11": "On the owner's go: patch docs for his decision (A + B), then red tests, the "
        "fix, notch and rebuild.",
        "codegen_materialize_d20": "On the owner's go: patch docs for his decision (ACL namespace rule, filtered "
        "builtins), then red tests, the fix, notch and rebuild.",
    }
    for item, nxt in nexts.items():
        rows = [line for line in board.split("\n") if line.startswith("| " + item + " |")]
        if len(rows) != 1:
            sys.exit(f"ROW {item}: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[6] = nxt
        cells[10] = r.now
        board = board.replace(rows[0], " | ".join(cells))
    r.stage(r.BOARD, board)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()

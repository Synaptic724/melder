"""Record the 0.2.8267 re-measure of D-10, D-11 and D-20 into their tasks and flip the three codegen board rows
(melder_0, 2026-10-25).

One all-or-nothing pass: a MEASURE and a FACT note on each of the three codegen child tasks, naming the reruns on a
/tmp copy of the 0.2.8267 tree (the GIL off and on) and confirming each 2026-10-10 cause still holds at today's
lines; each task's Updated field and Context / Handoff Summary; the three codegen rows moved from discovery to
handoff with the owner-question as `next`. Refuses when a file changed since it was read or a line breaks the width
rule. Usage: record_codegen_remeasure_20261025.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

D10 = "tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md"
D11 = "tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md"
D20 = "tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md"
RUNS = "artifacts/codegen_room_policy_20261025/runs/"


class Pass(Record):
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


def add_notes(r: Pass, rel: str, notes: str, summary_old: str, summary_new: str) -> None:
    text = r.read(rel)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + notes + "\n\n## Context / Handoff Summary\n",
                  rel + " notes")
    text = r.once(text, summary_old, summary_new, rel + " summary")
    r.stage(rel, text)
    r.set_field(rel, "Updated")


def d10_notes(r: Pass) -> str:
    measure = r.note(r.now, "MEASURE", [
        "Re-measured on a /tmp copy of the 0.2.8267 working tree (copied from the device checkout at git 9f240166f),",
        "the GIL off and on, Python 3.14.7 free-threaded. codegen_probe.py: under all five postures (safe, hybrid,",
        "hybrid+precision, permissive, full_access) an `open(path, 'w').write(...)` is accepted and the file is",
        "written, and `open(<core .py>).read()` is accepted and returns the file (74042 chars of bind.py now, where",
        "it was 64109 at 2026-10-10 because bind.py grew; the acceptance is unchanged). pathlib-write, import-melder",
        "and import-subprocess match the 2026-10-10 run exactly. The GIL-on output is byte-identical to the GIL-off",
        "run. The strict xfail test_safe_profile_refuses_writing_files still XFAILs (pytest: 16 passed, 5 xfailed,",
        "both GIL modes). So D-10 reproduces unchanged at 0.2.8267."],
        [RUNS + "codegen_probe_0_2_8267_gil0.txt:1-28",
         RUNS + "codegen_probe_0_2_8267_gil1.txt:1-28",
         RUNS + "codegen_tests_0_2_8267_gil0.txt:1-40"],
        ["The recorded symptom holds on today's tree, so the owner's D2 decision rests on current behaviour."],
        ["Confirm the cause at today's lines (next note), then put D2 to the owner."], "REQUIRED", 8)
    fact = r.note(r.now, "FACT", [
        "The 2026-10-10 cause holds at 0.2.8267, read at today's lines. `SAFE_DENIED_BUILTIN_NAMES` still omits",
        "`open`, and `HYBRID_DENIED_BUILTIN_NAMES` and `PRECISION_DENIED_BUILTIN_NAMES` are still that same tuple.",
        "The safe profile builds its one `builtin_names` deny rule from that tuple, so `open` is on no deny list; the",
        "runtime builtins are `vars(builtins)` minus the denied names (so `open` stays in `__builtins__`); and the",
        "static builtin gate refuses only an `ast.Call` whose `func` is an `ast.Name` in the denied set, so a call to",
        "`open` is never refused and `f = open; f(...)` would not be either. imports being off under safe stops the",
        "`import io`/`pathlib` routes, not `open` itself. The posture question (D2) is unchanged: deny `open` under",
        "safe, and whether hybrid and precision (which reuse the tuple) too."],
        ["src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:83-99",
         "src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:106-124",
         "src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:100-108",
         "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:103-127",
         "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:252-265"],
        ["The fix is still a deny-list change plus a pinned per-profile file matrix, after D2."],
        ["DECISION_REQUEST to the owner: D2 (deny `open` under safe; hybrid and precision too?)."], "REQUIRED", 8)
    return measure + "\n\n" + fact


def d11_notes(r: Pass) -> str:
    measure = r.note(r.now, "MEASURE", [
        "Re-measured on the /tmp copy of 0.2.8267, the GIL off and on. codegen_probe2.py: `__import__('subprocess')`,",
        "`__import__('socket')`, `__import__('importlib')` and `__import__('melder')` are all accepted and return the",
        "module under hybrid, hybrid+precision and permissive, and all refused under safe (\"Builtin '__import__' is",
        "not allowed in this codegen mode.\"); identical to 2026-10-10 and byte-identical across GIL modes (session",
        "paths in the result were normalised to `~`). The four strict xfails",
        "test_hybrid_refuses_dynamic_imports_of_its_denied_roots[None-subprocess|None-socket|None-importlib|",
        "precision-subprocess] still XFAIL. So D-11 reproduces unchanged at 0.2.8267."],
        [RUNS + "codegen_probe2_0_2_8267_gil0.txt:1-19",
         RUNS + "codegen_probe2_0_2_8267_gil1.txt:1-19",
         RUNS + "codegen_tests_0_2_8267_gil0.txt:1-40"],
        ["The recorded symptom holds, so the owner chooses A/B/both on current behaviour."],
        ["Confirm the cause at today's lines (next note), then cost the options."], "REQUIRED", 8)
    fact = r.note(r.now, "FACT", [
        "The cause holds at 0.2.8267, read at today's lines. `FrameACLCompiler._compile_codegen_builtin_controls`",
        "adds `__import__` to the denied builtins ONLY when `imports_enabled` is False, so a profile that enables",
        "imports (hybrid, precision, permissive) leaves `__import__` a live builtin. The import-policy strategy walks",
        "only `ast.Import` and `ast.ImportFrom` nodes, so a `__import__(...)` call is outside its reach, and",
        "`_import_root_is_denied` is never consulted for it. Name resolution admits every builtin not on the deny",
        "list, so the name resolves. Option A (deny the `__import__` name statically wherever an import list applies)",
        "and B (a runtime `__import__` wrapper checking each root) are unchanged; A alone misses an alias or",
        "`__builtins__['__import__']`, B covers the forms static analysis cannot see."],
        ["src/melder/nexus/acl/frame_acl_compiler.py:600-630",
         "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:114-198",
         "src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:134-155"],
        ["The fix makes every import answer to the compiled roots; A+B is still the recommendation."],
        ["DECISION_REQUEST to the owner: option A, B or both."], "REQUIRED", 8)
    return measure + "\n\n" + fact


def d20_notes(r: Pass) -> str:
    measure = r.note(r.now, "MEASURE", [
        "Re-measured on the /tmp copy of 0.2.8267, the GIL off and on. probe_materialize.py: under safe and hybrid",
        "alike a materialize over `melder.aether.spellbook.bind.bind` replaces the core module (import_module and the",
        "parent package attribute return the SyntheticModule), a new `melder.injected_probe` joins the package, `csv`",
        "is replaced and `pytest` is shadowed. probe_materialize_fail.py: a materialize over `csv` whose exec raises",
        "leaves `csv` absent from sys.modules, and cleanup of a `json` replacement leaves `json` absent - the",
        "original is never restored. Identical to 2026-10-10 and byte-identical across GIL modes. The materialize",
        "verb unit tests still pass (5 passed). So D-20 reproduces unchanged at 0.2.8267."],
        [RUNS + "probe_materialize_0_2_8267_gil0.txt:1-11",
         RUNS + "probe_materialize_fail_0_2_8267_gil0.txt:1-6",
         RUNS + "codegen_tests_0_2_8267_gil0.txt:1-40"],
        ["The recorded symptom holds, so the owner's namespace and builtins answers rest on current behaviour."],
        ["Confirm the cause at today's lines (next note), then put the two questions to the owner."], "REQUIRED", 8)
    fact = r.note(r.now, "FACT", [
        "The cause holds at 0.2.8267, read at today's lines (line numbers, not bodies). `materialize_codegen`",
        "(codegen_command_system.py:739) checks `module_name` for dotted-identifier legality only, with no existing /",
        "protected / stdlib / installed check. `SyntheticModule.publish_to_sys_modules` (:930) assigns",
        "`sys.modules[self.__name__]` unconditionally (:947) and keeps no record of what it displaced;",
        "`SyntheticModule.cleanup` (:462, del at :501; a second path at :970) removes only its own object, so a",
        "displaced original is never put back. `execute_source` (:901) execs into the module dict and sets no",
        "`__builtins__`, so materialized code runs with the interpreter's full builtins, where execute_codegen uses",
        "the room's filtered set. The two owner questions (generation namespace; room builtins for materialized",
        "code) are unchanged, and the crystallizer restore/rebuild/graft lanes that also publish SyntheticModules",
        "remain the reason to prefer the verb as the enforcement point."],
        ["src/melder/nexus/rift/command_system/codegen_command_system.py:739-739",
         "src/melder/crystallizer/synthetic_module.py:901-947",
         "src/melder/crystallizer/synthetic_module.py:462-501"],
        ["The fix is a name policy plus restoring exits, after the owner answers; a guard's place weighs the lanes."],
        ["DECISION_REQUEST to the owner: where the generation namespace is declared; room builtins for materialized",
         "code."], "REQUIRED", 8)
    return measure + "\n\n" + fact


def board(r: Pass) -> None:
    text = r.read(r.BOARD)
    flips = {
        "codegen_open_file_d10": "Put D2 to the owner (deny `open` under safe; hybrid and precision too?); the "
        "re-measure on 0.2.8267 is recorded.",
        "codegen_dynamic_import_d11": "Put the option choice to the owner (A static deny, B runtime guard, or both); "
        "the re-measure on 0.2.8267 is recorded.",
        "codegen_materialize_d20": "Put the two questions to the owner (generation namespace; room builtins for "
        "materialized code); the re-measure on 0.2.8267 is recorded.",
    }
    for item, nxt in flips.items():
        rows = [line for line in text.split("\n") if line.startswith("| " + item + " |")]
        if len(rows) != 1:
            sys.exit(f"ROW {item}: {len(rows)}")
        cells = rows[0].split(" | ")
        # columns: work_item status mode owner agent blocker next outcome exit_signal ticket updated_at reread
        cells[2] = "handoff"
        cells[6] = nxt
        cells[10] = r.now
        new = " | ".join(cells)
        r.check_width("| x |", item)  # no-op width anchor; row itself is a table row (exempt)
        text = text.replace(rows[0], new)
    r.stage(r.BOARD, text)


SUMMARIES = {
    D10: ("Next: (1) rerun codegen_probe.py and the strict xfail on a /tmp copy, the GIL off and on; (2) read\n"
          "the deny list and the strategies at today's lines; (3) put D2 to the owner as a DECISION_REQUEST.",
          "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the\n"
          "strict xfail still XFAILs. Decision pending: D2 (deny `open` under safe; hybrid and precision too?)."),
    D11: ("Next: (1) rerun codegen_probe2.py and the four strict xfails on a /tmp copy, the GIL off and on; (2) read "
          "the\ncompiler's controls and the strategies at today's lines and probe the routes option A would miss; "
          "(3) put the\nchoice of A, B or both to the owner as a DECISION_REQUEST.",
          "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
          "four\nstrict xfails still XFAIL. Decision pending: option A, B or both."),
    D20: ("Next: (1) rerun probe_materialize.py and probe_materialize_fail.py on a /tmp copy, the GIL off and on; "
          "(2) read\nthe verb and SyntheticModule at today's lines and list the other publishers; (3) put the "
          "namespace and builtins\nquestions to the owner as a DECISION_REQUEST.",
          "Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the "
          "verb\ntests pass. Decision pending: the generation namespace, and room builtins for materialized code."),
}


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_codegen_remeasure")
    add_notes(r, D10, d10_notes(r), *SUMMARIES[D10])
    add_notes(r, D11, d11_notes(r), *SUMMARIES[D11])
    add_notes(r, D20, d20_notes(r), *SUMMARIES[D20])
    board(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()

"""Record the regression tests' PLAN on TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0, 2026-10-24).

Appends one PLAN Note (the tests, the fault and what they assert) before the tests are written, refreshes Updated.
All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a ticket that changed since it was read
refuses the pass.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
REPO = pathlib.Path.home() / "mnt/melder_private"
CACHE_TESTS = "tests/component/melder/spellbook/test_spellbook_component_caching_system.py"


def def_range(rel: str, name: str) -> str:
    """`rel:a-b` of a top-level function, its decorator included, up to the last non-blank line before the next."""
    lines = (REPO / rel).read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith(f"def {name}(")]
    if len(starts) != 1:
        sys.exit(f"DEF {name}: {len(starts)}")
    start = starts[0] - 1 if lines[starts[0] - 1].startswith("@") else starts[0]
    end = starts[0] + 1
    while end < len(lines) and not lines[end].startswith(("def ", "@", "class ")):
        end += 1
    end -= 1
    while lines[end].strip() == "":
        end -= 1
    return f"{rel}:{start + 1}-{end + 1}"


class Pass(Record):
    """The PLAN pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def main() -> None:
    r = Pass("plan_regression_tests")
    plan = r.note(r.now, "PLAN", [
        "The regression tests, before they are written (Note 14's boundary). Component file, each test in a fresh",
        "Aether with caching on in a frame of its own whose cache folder is emptied before and removed after:",
        "1. `test_meld_returns_its_object_when_the_cache_save_fails` [replace, write] - a dynamic root, a spell bound",
        "after conjure, its first meld's save fails once: the meld returns the object and a second meld returns the",
        "same object (probe A).",
        "2. `test_melds_keep_returning_while_every_cache_save_fails` [replace, write] - every save fails: the late",
        "spell's first meld and warm melds of a spell built before return (probe B).",
        "3. `test_first_melds_after_a_failed_conjure_save_return_their_object` [replace, write] - an automatic world,",
        "every save failing from before conjure: conjure returns (it logs the failure) and the first melds return",
        "(probe C).",
        "4. `test_managed_lease_survives_a_failed_cache_save` - limited_quantity, limit 1, bound after conjure, its",
        "leasing meld's save fails once: the lease comes back, is released and the pool leases again (probe D).",
        "5. `test_spellspace_meld_returns_its_object_when_the_cache_save_fails` - unique_per_spell_space, bound after",
        "conjure, first melded in a spellspace whose save fails once (the spellspace doors, Note 8).",
        "Unit file: 6. `test_refused_save_leaves_no_temp_file_behind` - a bundle saved, then a save whose rename is",
        "refused every time: the frame folder holds no temp file and the saved bundle still loads (emit's atomic",
        "contract).",
        "The fault is the save's own OS calls, patched for the test and only for .meldercache paths under its folder:",
        "`os.replace`, which `Path.replace` calls (PermissionError EACCES, the WinError 5 refusal), and",
        "`Path.write_bytes` on the temp file (a read-only folder). Each test asserts its fault fired. They assert the",
        "outcome only - the object returned, the lease reusable, no temp file - not where the tolerance sits, how it",
        "logs or whether the save is retried, so any of the DECISION_REQUEST's directions can turn them green."],
        ["src/melder/utilities/caching_system/caching_system.py:885-918",
         "src/melder/aether/spellbook/spellbook.py:1143-1180",
         "src/melder/aether/conduit/conduit.py:5095-5207",
         "src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1726-1742",
         def_range(CACHE_TESTS, "reset_aether_singleton_for_component_spellbook_caching"),
         def_range(CACHE_TESTS, "_activate_aether_cache_configuration"),
         "cpython 3.14.7 Lib/pathlib/__init__.py:1081-1094 (`Path.replace` calls `os.replace(self, target)`)",
         "context_compass/artifacts/cache_write_failure_20261024/probes/probe_cache_emit_failure.py:1-185"],
        ["Six tests covering the four measured symptoms through every kind of meld door, red today for the bug's",
         "reason; the fix plan maps onto them one by one."],
        ["Write the two test files and run them on a /tmp copy of the tree, the GIL off and on."], "REQUIRED", 8)
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + plan + "\n\n## Context / Handoff Summary\n",
                  "plan")
    text = r.once(text, "Next: read the save, the meld doors and the cache-test\nconventions; record the tests' PLAN; ",
                  "Next (the tests' PLAN is Note 16):\n", "summary next")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()

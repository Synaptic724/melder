"""FACT note: the seams a shell in the owner store touches (read whole on 0.2.8238)."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The seams, read whole on 0.2.8238. (1) The store: `Creations._creations[sid]` holds one object (slotted) or a
    list (many); `_disposable_creations[sid]` holds a tuple, a `ManyDisposalBucket` or a `HolderDisposalEntry` (the
    holder plus its adopted `many` children, 0.2.8238), and every retirement dispatches on those three shapes by
    isinstance (`_dispose_disposable_registry`, `_dispose_entry`, `extract_spell_creations`, `restore_spell_creations`,
    `_detach_purge_entries`). A shell stored under the spell id is therefore a FOURTH record shape that each of those
    five readers must name explicitly (the `else` branches assume a holder record today); nothing else in the store
    changes. (2) The readers outside the store: the two meld doors (`conduit_meld.py:843-1086`,
    `spellspace_meld.py:783-1027`: live-creation probes, purge resolution, existing lookups) and the emitted door
    templates in `creation_runtime_door_compiler.py:498-865`, one `(route, lane)` template per Existence that reads
    `_owner_creations._creations.get(_spell_id)` and returns the value. (3) The warm lane of `Conduit.meld`
    (`conduit.py:4878-4938`) calls the emitted door's executor (`captured_context._no_overrides_instance_executor`)
    after its guard ladder - it never reads a store itself - so a managed route is one more door template
    (`shell = ..._creations.get(_spell_id); creation = shell.acquire(); if None: reserve, build, publish_out`) and the
    hot door needs no change at all. (4) Ownership: `Spell._add_owned_conduit` (`spell.py:1558-1606`) stamps
    `_owner_creations` under the spell lock at conjure, the one place to create and register the shell; the lowering
    binds that store as a constant for automatic unique sites (`site_plan_lowering.py:1341-1381`), so a managed site
    binds the shell the same way and emits `v = sh.acquire()`. (5) Phase 6 (`scope_ordering_strategy.py:80-121`): a
    rank table keyed by Existence; `managed` = rank 0 is one entry. (6) Bind: `disposal_method_names` flows
    `Spellbook.bind` (`spellbook.py:5400-5450`) -> `Bind._bind_logic` (`bind.py:464-562`) into the Spell; a
    `reset_method_names` list rides the same path and is fingerprinted only for managed bindings. (7) The Existence
    enum (`existence.py:60-117`) is six `auto()` members with `__str__` = name; a seventh member is additive.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:10-120
  - src/melder/aether/conduit/creations/creations.py:470-560
  - src/melder/aether/conduit/creations/creations.py:1134-1206
  - src/melder/aether/conduit/creations/creations.py:1296-1470
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-660
  - src/melder/aether/conduit/conduit.py:4878-4938
  - src/melder/aether/spellbook/spell.py:1558-1606
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/spellbook.py:5400-5450
  - src/melder/aether/spellbook/existence/existence.py:60-117
  IMPACT: The owner's "minimal change" reading holds: one new class, one Existence member, one door template, one
    lowering branch, five explicit store branches, one Phase 6 rank entry, one bind keyword; the warm meld lane and
    every existing member are untouched.
  NEXT: the spike - `ManagedShell` + `ReleaseManagedSpell` prototype with the three modes, a stress probe, then the
    captured-plan and door-shape measurement on the VM copy at 0.2.8238.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTE, exempt=r"^  - src/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] Read the seams whole: the Existence enum and the resolution matrix, Creations publish/purge/cleanup and the\n",
    "- [x] Read the seams whole: the Existence enum and the resolution matrix, Creations publish/purge/cleanup and the\n",
    "step1")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
print("noted", TS)

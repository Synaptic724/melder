"""S4: record the validation MEASURE in the story and refresh its resume view."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_release_managed_spell_story.md"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S4 validated on the device VM (CPython 3.14.7t, every suite under `-X gil=0` and `-X gil=1`). Red first:
    5 import errors, 8 failed, 88 passed. Green, each mode: the new and changed tests 197 passed; unit aether +
    spellbook 6874 passed; unit rest 2508 passed, 3 skipped, 7 xfailed; component spellbook 819 passed; component
    rest 1545 passed, 23 skipped, 1 xfailed; integration aether 785 passed, 5 xfailed; integration conduit, spellbook,
    mutation_research and live_sim 1003 passed, 2 skipped, 1 xfailed, 2 xpassed; integration multithreading 54
    passed; integration crystallizer 276 passed, 3 xfailed (all 279 ids, through the resumable shard runner, because
    the Aether lifecycle changed); experimentation, experiments and tests/tests 250 passed, 4 skipped. The only
    warning is Melder's GIL-mode UserWarning under `-X gil=1`. A docstring-only edit made after those runs (the
    class's Performance section) was rechecked: build assets, creations, public surface, the probe and the
    integration file, 401 passed, 1 skipped. Routing (release then `_idle.pop()`, 200,000 cycles x 7 rounds): the
    pool's `put_back` 66-69 ns a cycle; a bound `registry.release` +50 to +51 ns (min); the one-line
    `ReleaseManagedSpell().release` +137 to +144 ns, because the singleton call itself costs about 70 ns, the same
    as `Aether()` (69-72 ns both). Density: 70 tests on the 294 code lines of the two new modules (24 per 100),
    plus 12 on the changed lines elsewhere. Not run: coverage and hosted CI (the owner's).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_validation_index.md:1-49
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_resumable_summary.txt:1-8
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_release_routing_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_release_routing_gil1.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_singleton_call_gil0.txt:1-5
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_probe_singleton_call_gil1.txt:1-5
  - src/melder/aether/conduit/creations/release_managed_spell.py:52-61
  IMPACT: The exit gate's test half is met in both modes. The routing target (about 100 ns over the pool call) is
    met with the registry bound once; the documented one-liner also pays the Aether-shaped singleton call, which the
    owner's singleton ruling fixes, so the class docstring and AGENT_PURPOSE now tell hot loops to bind it once.
  NEXT: Notch 0.2.8244 and extend the running release note's managed section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""

story = STORY.read_text(encoding="utf-8")
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
story = story.replace(anchor, NOTE + anchor)
old_state = """- State: implemented on the working copy (0.2.8243; not notched, nothing committed). New and changed tests green in
  both GIL modes (197 each); unit trees green in both modes (aether + spellbook 6874 each; the rest 2508 passed,
  3 skipped, 7 xfailed each). Runs: artifacts/managed_spell_quantity_20261015/runs/s4_*."""
new_state = """- State: implemented and validated on the working copy (0.2.8243; not notched, nothing committed): the whole tree
  green in both GIL modes, routing measured (MEASURE note). Runs: artifacts/managed_spell_quantity_20261015/runs/
  s4_validation_index.md."""
assert story.count(old_state) == 1, "state"
story = story.replace(old_state, new_state)
old_rem = """- Remaining: component and integration shards in both modes (crystallizer integration included); the routing-cost
  probe; the MEASURE note; notch 0.2.8244 and the release note; epic B1/B4; closure and board sync; rebuild last."""
new_rem = """- Remaining: notch 0.2.8244 and the release note; epic B1/B4; closure and board sync; rebuild last."""
assert story.count(old_rem) == 1, "remaining"
story = story.replace(old_rem, new_rem)
old_next = "- Next: the component shards in both GIL modes.\n"
assert story.count(old_next) == 1, "next"
story = story.replace(old_next, "- Next: notch 0.2.8244.\n")
STORY.write_text(story, encoding="utf-8")
print("ok", NOW)

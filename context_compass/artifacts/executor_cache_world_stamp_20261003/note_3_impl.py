"""Implementation + validation FACT note."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md")
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Implemented and validated on the working copy (`$HOME/work/melder_cc`, re-synced from the tree at
    0.2.8219 - fable_1's rebind notch landed at 20:41Z in the DevOps control plane, no file overlap). The
    component file ran RED first on the tree's rule (4 failed: the provider-added world melds with
    TypeError missing 'service'; the provider-removed world fails with "generalized manifest references
    unknown spell_id"; no `world_stamp` in the envelope; no generation 19). The anchored script
    `apply_world_stamp.py` (per-line endings kept; the helper block is apply_s8.py's) then edited:
    caching_system.py - envelope `world_stamp` ("" in the empty store; optional on load, a non-str is
    rejected; always written), the `world_stamp` property and `set_world_stamp` (changed bool, under the
    lock), generation 19 `executor_world_stamp` with its history comment and the class-contract bullet;
    spellbook_creation_system.py - `_build_conjure_cache_state` computes the live stamp when caching is
    enabled and requires `world_matches` for the full hit (`is_mixed = matched and not is_full_hit`),
    returns `world_stamp` / `world_matches`; `_stage_spell_payloads_at_conjure_end` records the stamp after
    the re-stage and flags the emit when it changed; docstrings updated. Tests: caching-system unit (three
    new, the emit-shape key set, a non-string stamp rejected), cache runtime unit (stubs carry the posture
    and borrowed attributes and a stamp surface; five new classification rows; four staging tests), the
    fastpath stubs, the history pin (19), the integration surplus contract re-pinned as "a removed spell
    reruns once, then full-hits", the new component file (4 green). Shards on the working copy, GIL off:
    unit spellbook+utilities 3048 passed; unit aether+crystallizer+mutation_research+build_assets 5169
    passed (build_assets needs the docs mirror linked: 116 passed with it); unit root files 144 passed and 1
    failed in `test_generated_build_assets_are_stamped_for_the_live_version` - the TREE's assets are still
    stamped 0.2.8218 under fable_1's 0.2.8219 notch (its rebuild is pending; not this lane); component
    spellbook+utilities+crystallizer+mutation_research 982 passed, component aether 1308 passed;
    integration spellbook+conduit 878 passed; integration aether+crystallizer+mutation_research 1093
    passed. Not run: integration multithreading and live_sim, the owner's full-tree suites, the gauntlet.
  EVIDENCE:
  - artifacts/executor_cache_world_stamp_20261003/logs/component_red_tree_0_2_8219.log:1-40
  - artifacts/executor_cache_world_stamp_20261003/apply_world_stamp.py:80-330
  - artifacts/executor_cache_world_stamp_20261003/logs/green_targeted_1.log:1-3
  - artifacts/executor_cache_world_stamp_20261003/logs/green_targeted_2.log:1-3
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_unit_spellbook_utilities.log:1-2
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_unit_aether_crystallizer_mr.log:1-2
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_component_a.log:1-2
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_component_aether.log:1-2
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_integration_spellbook_conduit.log:1-2
  - artifacts/executor_cache_world_stamp_20261003/logs/shard_integration_aether_crystallizer_mr.log:1-2
  IMPACT: Ready to land. Cost of the rule: one sorted-id digest per conjure when caching is enabled (the
    structural tier already computes the same digest once per conjure); no meld-path change.
  NEXT: land on the tree once fable_1's rebuild window is closed (its row leaves implementation): apply
    script with --skip-tests? no - full apply, notch above `__version__` (next number at landing),
    release-note section, docs, graph, patch docs promoted, assets and bundles last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTE)
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] Reproduce red on the working copy (the component test), then the anchored apply script (src + tests); run the\n"
    "      touched suites sharded; FACT and MEASURE notes.",
    "- [x] Reproduce red on the working copy (the component test), then the anchored apply script (src + tests); run the\n"
    "      touched suites sharded; FACT and MEASURE notes.", "step3")
write_text(TASK, text, nl)
print("noted", TS)

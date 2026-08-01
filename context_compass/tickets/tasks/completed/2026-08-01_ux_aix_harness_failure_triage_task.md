# Task: UX/AIX harness failure triage - 7 reds from the owner 3.14t run

## Metadata
- Task ID: TASK-2026-08-01-ux-aix-harness-failure-triage
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Parent: EPIC-2026-07-19-ux-aix-intermediate (also touches -advanced)
- Created: 2026-08-01T11:04:00Z
- Updated: 2026-08-01T11:04:00Z

## Problem / Opportunity
Owner ran `UX_and_AIX_experiences/pytest_examples` on 3.14t: **7 failed, 113 passed
in 1.64s**. The reds are NOT one bug. They are four distinct root causes, and two of
them are runtime-contract questions the owner must rule on before any code moves.

Beginner tier is unaffected: 41/41 green including lesson 41, which retires the
caveat this epic was closed under.

## Context
The tiers are the evidence lane for init curation. A red here means either the
example teaches something false, or the runtime does something the tier's author
reasonably did not expect. Telling those two apart is the whole job of this task -
"fix the assert until it goes green" would destroy the signal the tier exists to
produce.

## Ticket Contract
- ENTRY_GATE: owner 3.14t run pasted into this session with full tracebacks.
- EXECUTION_BOUNDARY: triage + owner rulings ONLY in this task. Example edits route
  through the owning tier epic; any `src/melder` change routes through its own
  story under the patch framework, because two findings touch public semantics.
- DEPENDENCIES: owner rulings on FINDING-1 and FINDING-3 (both public-contract).
- EXIT_GATE: every one of the 7 reds is classified example-defect or runtime-defect
  with file:line evidence; owner has ruled on both contract questions; green run.
- FAILURE_ESCALATION: DECISION_REQUEST on anything that would widen or change the
  public surface.

## Applicable Anti-Patterns
- Editing the assert to match observed behavior without deciding whether the
  behavior is correct. This is the primary risk in this task.
- Treating four independent causes as one "test fix" sweep.

## Noting Behavior
- Task notes: tactical findings, immediate impact, one-step continuation.

## Notes

- DATETIME: 2026-08-01T11:04:00Z
  TYPE: FACT
  CLAIM: FINDING-1 (4 of the 7 reds, RUNTIME CONTRACT DEFECT - not example rot).
    `disposal` and `disposal_method_names` are declared set-once
    (`_idempotent_keys`), but `load_default_dictionary()` PRE-SEEDS both by writing
    `self._properties[key] = value` DIRECTLY, bypassing `set_property`. The
    idempotency guard is `if key in self._idempotent_keys and key in
    self._properties`, so the default seed CONSUMES the single allowed write before
    any user touches the config. Net effect: on any book or config that has loaded
    defaults, `set_property("disposal", True)` and therefore `with_disposal(True)`
    are PERMANENTLY REFUSED. Disposal cannot be enabled through the public surface.
    A fresh `Spellbook()` loads defaults at spellbook.py:5282, so this hits the
    default path, not an exotic one. The `with_defaults` docstring makes the
    opposite promise - "overwriting anything set earlier, so call it FIRST and
    override afterwards" - which is exactly what the four failing callers did.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:148
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:232-233
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:576-585
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1063-1064
    - src/melder/aether/spellbook/spellbook.py:5282
  IMPACT: Teardown is advertised as core to Melder's correctness contract, and the
    README sells "automatic teardown" as a headline. If disposal cannot be turned
    on after defaults load, that headline is unreachable by the documented route.
    This is a library defect surfaced by the tier, which is the tier working.
  NEXT: Owner ruling - stop seeding idempotent keys in the defaults dict, OR make
    the idempotency guard ignore default-seeded values, OR declare the docstring
    wrong and require disposal before `with_defaults()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:04:00Z
  TYPE: FACT
  CLAIM: FINDING-2 (1 red, EXAMPLE DEFECT - runtime is right).
    `35_one_config_every_book` conjures two books in the SAME frame with no name,
    so both root conduits are born `default` and the frame correctly refuses the
    second with `ValueError: Conduit with name default already exists.` Proof the
    runtime is right and the example is wrong: the sibling probe
    `test_probe_manual_config_share_across_books` teaches the SAME lesson and
    PASSES, because it names them - `conjure(name="share-a")` /
    `conjure(name="share-b")`.
  EVIDENCE:
    - UX_and_AIX_experiences/02_intermediate/35_one_config_every_book.py:99-100
    - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py:19-20
    - src/melder/aether/aetheric_frame/aetheric_frame.py:363-372
  IMPACT: Lowest-risk red. One-line example fix, no owner ruling needed.
  NEXT: Name both conjures in the example, matching the probe that already passes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T11:04:00Z
  TYPE: DECISION_REQUEST
  CLAIM: FINDING-3 (1 red, RUNTIME BEHAVIOR QUESTION - the interesting one).
    `02_deep_spell_override_paths` binds all three spells `existence="unique"`,
    melds the root WITH a deep override, then melds `Transport` plainly and asserts
    it still carries `source == "vault"`. It does not. The overridden meld
    CONSTRUCTS the singleton `Transport` around the injected test fixture and
    REGISTERS it as the canonical singleton, so every later plain meld reuses the
    fixture-contaminated object. Registration on the override lane is real, not
    inferred: the generalized override runtime carries `must_register` flags and
    calls `register_spell_instance_prebound`.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/02_deep_spell_override_paths.py:43-53
    - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:39,70,514-515
  IMPACT: This is a footgun with a sharp edge: injecting a test fixture ONCE through
    `spell_override` silently becomes the application's singleton for the rest of
    the process. Defensible under `unique` semantics (the override built the
    singleton; first meld wins) - but the tier author assumed the opposite, and the
    example's own prose teaches the opposite ("Untouched melds keep the DI-built
    world"). One of the two has to give.
  NEXT: OWNER DECISION. Either (a) the behavior is correct and the example must
    rebind as `many` or meld plainly first, with the lesson rewritten to TEACH the
    contamination rule; or (b) override-built instances should not be registered as
    the canonical singleton, which is a runtime change under the patch framework.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:04:00Z
  TYPE: FACT
  CLAIM: FINDING-4 (1 red, EXAMPLE DEFECT - derived-count drift).
    `07_frame_posture_cheatsheet` prints 17 items from its own dict and asserts
    `total == 15`. The live `AethericFrameConfiguration` carries 14 public posture
    knobs; the example lists those 14 plus 3 preset METHODS
    (`automatic_defaults`/`dynamic_defaults`/`with_defaults`). The stale 15 is
    consistent with an earlier 12-knob posture: the caching pair
    (`system_caching_enabled`, `system_cache_root_path`) was added to the posture
    later, the example's dict was updated, and the hardcoded count was not.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/07_frame_posture_cheatsheet.py:40-62
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
  IMPACT: Exactly the silent-derived-count failure mode
    `special_instructions/new_skills/system_doc_index_generation.md` was written
    about (the C1 map generated at 550 modules and silently wrong at 553). A
    hand-maintained count over a live surface WILL drift again.
  NEXT: Decide the honest number (14 knobs, or 17 including presets) and stop
    hardcoding it - assert against the length of the example's own dict so the
    count cannot drift from the list it describes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Validation Plan
- Owner re-runs `pytest UX_and_AIX_experiences/pytest_examples -v` on 3.14t after
  each ruling lands. No agent may claim a green run.

## Artifact Links (Optional)
- none yet. A `src/melder` change under FINDING-1 or FINDING-3 requires patch docs
  before implementation per patch_framework_gating.md.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Context / Handoff Summary
7 reds, 4 root causes, 2 of them owner-contract questions. Nothing has been edited:
no example, no source, no assert. The two safe fixes (FINDING-2, FINDING-4) are
one-liners held deliberately so all four land under one ruling pass rather than
half-fixing the suite and losing the signal. Beginner tier is 41/41 green and its
closure caveat is retired.

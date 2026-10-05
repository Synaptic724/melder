# Native rebind after first creation loses creation codegen

Owner: command_0. Relevant story: tickets/stories/2026-10-03_actions_native_factory_story.md.
Installed distribution: .venv314/Lib/site-packages/melder-0.2.8215.dist-info.
No Melder source is edited by this investigation.

## Observable failure
Actions native test registers PayloadAction, melds one instance, withdraws the exact Spectrum
contract, cleans its definition, rebinds the same class at the same subgroup/name, and melds again.
The original object remains live as intended. The second meld raises:

    RuntimeError: Cannot build CreationContext before spell_codegen_creation exists.
    Run analyzer -> processor -> planner -> codegen creation first.

The corrected application selection has 83 tests, 82 passing and this one failure:
focused_corrected.xml. The earlier focused.xml is the peer-run pre-correction receipt.

## Fresh public-API isolation
test_native_rebind_probe.py uses one scalar-only Cleanable class, two ordinary dynamic books,
one lesser conduit and only public Melder bind/meld/contract/cleanup_spell calls. It imports the
existing reset_spectrum_and_melder autouse fixture, so every case begins and ends with fresh native
singleton state. It never constructs Spectrum, Actions, a logger facade or an agent.

| First meld before removal | Shared to peer | Result |
| --- | --- | --- |
| No | No | pass |
| No | Yes | pass |
| Yes | No | same CreationContext failure |
| Yes | Yes | same CreationContext failure |

Receipt: native_rebind.xml, 4 tests, 2 passed / 2 failed / 0 errors / 0 skipped, exit 1.
Command from repository root, runner command_0:

    .venv314\Scripts\python.exe -m pytest -o pythonpath=src context_compass/artifacts/2026-10-03_actions_native_factory/test_native_rebind_probe.py -q --tb=short --junitxml=context_compass/artifacts/2026-10-03_actions_native_factory/native_rebind.xml

## Native call chain
conduit.py meld -> conduit_meld.py meld -> meld.py _execute_admitted ->
spell.py _get_or_build_creation_context -> creation_context_factory.py get_or_build_for_spell ->
creation_context_builder.py build:121. The final builder refuses the absent codegen artifact.
The responsible invalidation/cache transition is UNKNOWN; this is operation-prefix evidence,
not a claim that a particular native cache implementation is faulty.

## Boundary and next action
Ordinary first creation, class lookup, factory scoping, explicit cleanup, purge and replacement
before first creation pass in the focused application selection. Keep the failing integration
test; do not hide it with skip/xfail, mutate Melder internals or force a revalidation workaround.
The native maintainer should run the four-case reproduction and repair ordinary dynamic rebind
so the next meld rebuilds what it needs. Retest the unmodified application case afterwards.

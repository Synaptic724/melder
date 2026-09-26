"""Promote shared_context_rebuild_2026_09_26 into src_architecture and src_components (anchored edits).

Usage: python promote_docs.py <context_compass_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block as _replace_block


def replace_block(path: pathlib.Path, old: str, new: str, count: int = 1) -> None:
    """Idempotent wrapper: skip a block whose new text is already present (safe re-run)."""
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if new in text:
        print(f"already applied in {path.name}: {new.splitlines()[0][:60]}")
        return
    _replace_block(path, old, new, count)

cc = pathlib.Path(sys.argv[1])
arch = cc / "system_docs/src_architecture.md"
comp = cc / "system_docs/src_components.md"

# ============================================================ src_architecture
replace_block(arch,
'''3. `CreationContext` compiled execution:
   - Select no-hooks/hooks and no-overrides/overrides lanes.
   - Execute codegen-creation-backed runtime lanes and return the resolved instance.''',
'''3. `CreationContext` compiled execution:
   - Select no-hooks/hooks and no-overrides/overrides lanes.
   - Execute codegen-creation-backed runtime lanes and return the resolved instance.
   - Dynamic spells: the door takes the spell-index CreationGate ticket BEFORE it reads the context and
     holds it until the executor returns, calling the executor slots itself (2026-09-26).''')
replace_block(arch,
'''3. If per-conduit resolution validity is UNKNOWN/GATED:
   - Run `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)`.
   - Raise SpellbookValidationError if validity stays invalid/gated.''',
'''3. If per-conduit resolution validity is UNKNOWN/GATED:
   - Run `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)`.
   - Raise SpellbookValidationError if validity stays invalid/gated.
4. Under dynamic ownership every rerun above (and the deferred 8-11 run) first enters the spell's rebuild
   window: freeze and drain the spell-index gate, then take `spell._lock`, run the phases, publish the
   rebuilt context when its plan is present, reopen the gate (2026-09-26).''')
replace_block(arch,
'''## Operational Invariants''',
'''## Operational Invariants
- Shared context rebuild windows (2026-09-26): a dynamic spell's CreationContext and phase-11 plan are shared
  by every conduit that melds it, and a conduit-local rebuild (structural 1-4, resolution 5-11, deferred
  8-11) replaces them. Each such rebuild runs inside a CreationContextRebuild window that freezes and drains
  the spell-index gate BEFORE the phases touch the plan or context, and publishes the rebuilt context before
  reopening; a dynamic meld holds one index ticket from before its context read until its executor returns.
  So no meld builds from the gap between Phase 5 clearing the plan and Phase 11 republishing it, and none
  uses a context that is cleaned under it. The window is entered before `spell._lock` because an
  `Existence.unique` build holds the spell lock while its meld holds a ticket. Revalidation itself, the warm
  read and automatic-mode doors are unchanged; the ticket pair moved, it was not added. Resets outside
  windows (ownership restamp, notch, teardown, transfer) do not drain. A failed context build releases its
  pending claim and records its cause, so waiting callers raise instead of hanging.
  EVIDENCE: `src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:CreationContextRebuild`,
  `src/melder/aether/conduit/meld/meld.py:Meld._rebuild_window`, `Meld._execute_admitted` and
  `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:CreationContextFactory.get_or_build_for_spell`.''')
replace_block(arch,
'''## Failure Modes and Error Paths''',
'''## Failure Modes and Error Paths
- A context build that raises records its cause on the spell and releases its pending claim; a meld that
  waited on it raises RuntimeError chained from that cause. A rebuild window that cannot drain within 30 s
  raises RuntimeError from the rebuilding meld and leaves the gate open. A constructor that melds its own
  spell through a conduit that must rebuild it drains itself and hits that timeout (2026-09-26).
  EVIDENCE: `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:CreationContextFactory.get_or_build_for_spell`
  and `src/melder/utilities/synchronization/creation_gate.py:CreationGate.close_and_drain`.''')
replace_block(arch,
'''## Context / Handoff Summary

2026-09-26 deterministic signatures and live contract operands (tranche T1 of the IR epic): one signature''',
'''## Context / Handoff Summary

2026-09-26 shared context rebuild windows (the September 5 design, finished): concurrent first melds of a
shared dynamic spell failed in two ways - building a context from the gap between Phase 5 and Phase 11
("Cannot build CreationContext before spell_codegen_creation exists") and using a context cleaned under
them. Rebuilds now freeze and drain the spell-index gate before replacing the plan, and dynamic melds hold
their ticket across the context read and execution; the two tests skipped in September run again. Warm melds
measured unchanged within noise. The component map carries the mechanics.

2026-09-26 deterministic signatures and live contract operands (tranche T1 of the IR epic): one signature''')

# ============================================================ src_components (Meld Resolution Runtime)
replace_block(comp,
'''- INTERIM: the demand-driven build plan (override design S3/S4) is meant to decide this error before the
  call and retire these failure-path hooks. OVERRIDE_REQUIRED inputs keep their existing errors when omitted.''',
'''- INTERIM: the demand-driven build plan (override design S3/S4) is meant to decide this error before the
  call and retire these failure-path hooks. OVERRIDE_REQUIRED inputs keep their existing errors when omitted.

Shared context rebuild windows (2026-09-26):
- Scope: dynamic spells. `Spell._configure_creation_context_factory` resolves the spell-index CreationGate
  through `CreationContextFactory.resolve_spell_index_gate` and keeps it on `Spell._creation_gate` (None in
  automatic mode; dropped with the factory). The gate is the frame controller's; the spell only borrows it.
- Readers: when `_creation_gate` is set, both lanes of ConduitMeld and SpellSpaceMeld call
  `Meld._execute_admitted`: admit one ticket, then while `resolution_required` release, run
  `_ensure_runtime_resolution_ready` and re-admit, then read the context (warm read inlined, cold path
  through the spell's CounterSwitch election), call the executor slot directly and unregister in finally.
  `CreationContext.execute*` keep their own ticketing for direct callers; the doors no longer route dynamic
  melds through them, so there is exactly one ticket pair per meld. Automatic doors, including the fast-door
  memo, are unchanged.
- Producers: `_ensure_lineage_resolvable` (structural 1-4; Phase 3 resets the context),
  `_ensure_resolution_resolvable` (5-11) and `_ensure_runtime_resolution_ready` (deferred 8-11) run inside
  `Meld._rebuild_window(spell)` - a CreationContextRebuild over the spell, or a no-op without a gate -
  entered BEFORE `spell._lock`. The window takes the gate's transition lock (index-id order when several),
  closes it, drains admitted tickets with a 1 ms poll, and clears the spell's recorded failure. On exit it
  publishes a context for a spell whose phase-11 plan is present (a plan-less spell stays unpublished for
  its next meld's normal validation and is NOT marked resolution_required), or on failure records the cause
  and idles the switch; then it restores the prior gate posture and releases the lock. The affected set is
  the target spell because local Phase 5 publishes only to its target (2026-09-19).
- Why the window precedes the spell lock: an `Existence.unique` build holds `Spell._lock` while its meld
  holds a ticket (slot build guards, 2026-09-25); draining under the spell lock would wait on that reader.
  Producers run before admission, so a producer never drains its own ticket.
- Failed builds: the CounterSwitch leader records the exception on `Spell._creation_context_failure`,
  releases its claim (1 -> 0) and re-raises; a follower woken with nothing published raises RuntimeError
  chained from that cause; a successful build clears it.
- Not covered: resets outside windows (ownership restamp, notch, teardown, transfer) do not drain; a
  constructor that melds its own spell through a conduit that must rebuild it drains itself (30 s timeout).
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._rebuild_window`, `Meld._execute_admitted`,
  `src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:CreationContextRebuild`,
  `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:CreationContextFactory.get_or_build_for_spell`,
  `src/melder/aether/spellbook/spell.py:Spell._configure_creation_context_factory`.''')
replace_block(comp,
'''- Spell-owned CreationContext retrieval has a second, narrower boundary. A
  ready state-2 context remains a lock-free read. A missing or invalidated
  context takes `spell._lock`, rechecks readiness, and enters factory election
  only if a build is still required. Conduit-local phase revalidation owns the
  same RLock while Phase 5 clears and Phase 11 republishes context inputs, so a
  competing conduit cannot build from that transient artifact gap.''',
'''- CORRECTED 2026-09-26: spell-owned CreationContext retrieval never took
  `spell._lock` (the August text here described a cold-path lock the code did
  not have). A ready state-2 context is a lock-free read; a missing one is built
  through the spell's CounterSwitch election. Input stability for dynamic spells
  comes from the spell-index gate: melds hold a ticket across the context read
  and execution, and rebuilds freeze and drain that gate before phases replace
  the plan. See "Shared context rebuild windows (2026-09-26)" above.''')
replace_block(comp,
'''- Gated validity triggers Phase 1-4 and Phase 5-11 reruns under spell lock.''',
'''- Gated validity triggers Phase 1-4 and Phase 5-11 reruns under spell lock; for dynamic spells each
  rerun first enters the spell's rebuild window (freeze and drain the spell-index gate).''')
replace_block(comp,
'''- A cold context build cannot interleave with a Phase 5-11 rebuild for the same
  spell; the ready context/executor hot path remains outside the spell lock.''',
'''- For dynamic spells, no context build or execution interleaves with a rebuild of the same spell (the
  window drains the index gate first); the ready context/executor hot path takes no lock.''')
replace_block(comp,
'''- UnresolvedInputError (a MeldExecutionError subclass, exported at the package root) when a constructed
  spell's unresolved input was not supplied. `param_name` is the first missing parameter,
  `expected_type` its display type and `unresolved_params` every missing one in signature order.''',
'''- UnresolvedInputError (a MeldExecutionError subclass, exported at the package root) when a constructed
  spell's unresolved input was not supplied. `param_name` is the first missing parameter,
  `expected_type` its display type and `unresolved_params` every missing one in signature order.
- RuntimeError chained from the recorded cause when a meld waited on a context build that failed; the
  building meld re-raises the original. RuntimeError from a rebuild window that cannot drain within 30 s.''')
replace_block(comp,
'''- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/utilities/custom_exceptions/unresolved_input_error.py`''',
'''- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/utilities/custom_exceptions/unresolved_input_error.py`''')
replace_block(comp,
'''## Context / Handoff Summary

2026-09-26 deterministic signatures and live contract override operands (tranche T1 of the IR epic): the''',
'''## Context / Handoff Summary

2026-09-26 shared context rebuild windows: the September 5 freeze/drain design is finished and wired, adapted
to the slot build guards (window before the spell lock) and to target-only Phase 5 (the window covers the
target). Promoted into the Meld Resolution Runtime entry ("Shared context rebuild windows"), which also
corrects the old claim of a cold-path spell lock that the code never had.

2026-09-26 deterministic signatures and live contract override operands (tranche T1 of the IR epic): the''')

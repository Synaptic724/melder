"""Append the S5 FACT note (parked-before-conjure versions are never stamped) and the S5 DECISION note (dispense design)."""
import datetime
import pathlib
import sys

STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_dispense_codegen_story.md")
SC = "src/melder/aether/spellbook/spell_compiler"
CG = SC + "/codegen_creation_system"
ART = "context_compass/artifacts/managed_spell_quantity_20261015"


def notes(now: str) -> str:
    fact = f"""- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A version staged with `bind_inactive` before conjure is never given an owner. `bind_inactive` needs a
    dynamic posture (so only dynamic worlds hold such versions), conjure's `define_conduit_into_spells` stamps only
    the Book's active spells, and a notch promotes the member through `_reactivate_owned_spell`, which stamps
    nothing - although the bind_inactive comment says pre-conjure inactive spells are wired at conjure. Probed on
    0.2.8244 (dynamic; unique, unique_per_conduit and many): after conjure and a notch the promoted version's owner
    store is None and its first meld raises RuntimeError "Spell has no configured CreationContextFactory." for
    every existence. Pre-existing and not managed-specific; a managed version promoted that way has no pool.
  EVIDENCE:
  - {ART}/probes/probe_parked_notch_owner.py:1-55
  - {ART}/runs/s5_probe_parked_notch_owner_gil1.txt:1-20
  - src/melder/aether/spellbook/spellbook_creation_system.py:1331-1382
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  - src/melder/aether/spellbook/spellbook.py:3826-3966
  - src/melder/aether/spellbook/spellbook.py:5276-5306
  IMPACT: S5 cannot make such a version meld (its context never builds) and does not try. The per-creation pool read
    of a managed site raises a named error instead of AttributeError or KeyError when a consumer's managed dependency
    has no owner store or no pool (a torn-down root's store reads the same way). The structural fix - stamp the
    promoted member at notch with the Book's live conduit, which would also re-point members a transfer migrated
    (U9) - changes behaviour for every existence, so it goes with S6's notch work and to the owner, not into S5.
  NEXT: Record the dispense design as a DECISION, then write the S5 component and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
    decision = f"""- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: S5's dispense design, from the U7/U8 reads, the override runtime and resolver and the pool's API.
    (1) Door: route "managed" maps onto the existing `many` template objects in the four route tables - the same
    bodies (`created` True, U7), no new module-level template globals (the synaptic module-scope rule) and no new
    compiled template; this replaces the U7 note's "eight new template objects". (2) Sites: a third kind in
    SitePlanEmission. A leasing managed site (no winning key on its own parameters) has its own `_miss{{i}}` like a
    shared site and one consumer (per path); a managed site with winning keys on its own parameters is "fresh",
    constructed like a many step and never pooled, counted, registered or adopted. (3) Hit: `h{{i}}` (the pool) and
    `pp{{i}}` (its `_idle.pop`) bound as plan constants under S9's rule (automatic owner, owner store set) when the
    pool is present at emission - `_idle` is assigned once and drained, never swapped; otherwise per creation
    `h{{i}} = spells[i]._owner_creations._managed_quantities[sid{{i}}]`, whose AttributeError or KeyError becomes a
    named error. Then `try: v = pop() except IndexError: v = _miss(...)`. (4) Placement: each lease is emitted
    right before its one consumer's construction region - for a shared or managed consumer at the end of its miss's
    children, before the guard - so nothing but that consumer's other leases runs between a lease and its use.
    (5) Return (F9, widened to any failure before the consumer exists): from the first lease through the consumer's
    construction (for a shared consumer also its guard, recheck and publication) is one try; an exception puts back
    every lease taken for it (failures become notes on the exception) and re-raises; a shared consumer that loses
    its cold race puts back its unused leases (failures raised as one ExceptionGroup after all were tried).
    (6) Miss: unresolved check, `reserve()` (an object served returns at once), `kids` when disposal-bearing many
    children live inside, then `try:` children, leases and construction `except BaseException: abandon(kids, exc);
    raise`, then `adopt` when kids exist; many children there append `(v, dm)` to `kids`, not `register_many`.
    (7) No cache generation 21: rows and manifests of existing spells do not change, plans are emitted at hydration,
    and every notch already makes the cache cold (generation 9 compares the stamped release with `__version__`);
    the epic's B7 line is corrected. (8) `Conduit.managed_spell_meld`: resolve the target (`Meld._resolve_spell`),
    refuse a non-managed spell before melding, meld it by id, return `ManagedSpellLease(obj, pool)` on its owner
    store's pool.
  EVIDENCE:
  - {CG}/shared_assets/creation_runtime_door_compiler.py:54-85
  - {CG}/shared_assets/creation_runtime_door_compiler.py:1162-1229
  - {CG}/shared_assets/site_plan_lowering.py:1117-1234
  - {CG}/shared_assets/site_plan_lowering.py:1331-1513
  - {CG}/shared_assets/site_plan_override_runtime.py:337-405
  - {CG}/shared_assets/override_key_resolver.py:139-204
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:432-547
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:623-703
  - src/melder/utilities/general_base/abstract_elastic_pool.py:208-250
  - src/melder/utilities/caching_system/caching_system.py:765-857
  - src/melder/aether/conduit/meld/meld.py:1839-1921
  - src/melder/aether/conduit/creations/managed_spell_lease.py:84-99
  IMPACT: Non-managed shapes keep their emission: every new branch keys on a managed step, and the door tables only
    gain rows. Limited and queue pools cannot lose a place to a failed meld or a lost race. The patches restate this
    as the contract the red tests check.
  NEXT: Write component_patch_managed_dispense_codegen.md and code_description_patch_managed_dispense_codegen.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
    return fact + decision


def main() -> int:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = STORY.read_text(encoding="utf-8")
    anchor = "## Closure Confirmation"
    if text.count(anchor) != 1:
        print("anchor count", text.count(anchor))
        return 1
    block = notes(now)
    text = text.replace(anchor, block + anchor)
    updated = [line for line in text.splitlines() if line.startswith("- Updated: ")]
    if len(updated) != 1:
        print("updated lines", updated)
        return 1
    text = text.replace(updated[0], f"- Updated: {now}")
    STORY.write_text(text, encoding="utf-8", newline="")
    over = [line for line in block.splitlines() if len(line) > 120 and not line.lstrip().startswith("- ")]
    print("notes appended", now, "prose lines over 120:", len(over))
    for line in over:
        print(len(line), line[:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())

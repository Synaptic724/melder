"""S5 turn-in: update the epic's Build Specification (B7, B8, B12), Open Questions, Stories, Decision Log, Notes and
resume view with what S5 settled."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
EPIC = ROOT / "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
NOTE = ROOT.parent / "release_docs/next_version_release.md"

B7_OLD_START = "### B7 Codegen (S5)\n"
B7_OLD_END = "### B8 Ownership transfer (S6)\n"
B7_NEW = """### B7 Codegen (S5; as built in 0.2.8245, U7 and U8 settled)
- Four site kinds in SitePlanEmission (site_plan_lowering.py): shared (a slotted existence), `many`, and two managed
  kinds. A LEASING managed site has no winning override key on its own parameters: it is placed like a shared site
  (its own `_miss{i}` context, so its children build only on a miss) and feeds exactly one consumer, its own path's
  (the emission refuses another count with RuntimeError); the root may be one. A FRESH managed site has winning keys
  on its own parameters: it is built like a `many` step with the supplied values and never pooled, counted,
  registered or adopted - the caller's object.
- The lease is emitted right before its consumer's construction region (for a consumer with a miss, at the end of
  that miss's children, before its guard):
  ```text
      try:                                  # automatic owner, owner store set, pool present at emission:
          v{i} = pp{i}()                    #   pp{i} = pool._idle.pop and h{i} = pool, bound as plan constants
      except IndexError:
          v{i} = _miss{i}(meld, h{i}, <outer values>)
  ```
  Otherwise (a dynamic world, an unowned provider) the plan reads the pool per creation,
  `h{i} = spells[i]._owner_creations._managed_quantities[sid{i}]`, and an AttributeError or KeyError becomes
  `_raise_missing_managed_pool(spells[i])`: MeldExecutionError "Managed spell '<name>' has no pool to lease from: its
  owner root was torn down, or this version was never given one (a version staged with bind_inactive before conjure
  and notched in after it). Meld it through a live root, or stage the version after conjure."
- The miss: the unresolved-input check, `v{i} = h{i}.reserve()` (an idle object served to a queue waiter returns at
  once), `kids{i} = []` when disposal-bearing `many` children live inside, then `try:` the children, the site's own
  leases and its construction, `except BaseException as exc: h{i}.abandon(kids{i} or [], exc); raise`, then
  `h{i}.adopt(v{i}, kids{i})` when there are such children, `return v{i}`. A `many` child inside appends `(vK, dmK)`
  to `kids{i}` instead of `register_many`; shared children publish to their own stores as before.
- Lease return (F9, widened): from a consumer's first lease through its construction - for a shared consumer also
  its guard, recheck and publication - is one `try`; an exception returns every lease taken for that consumer
  (`_return_leases`: `put_back` each, a failing put-back added as a note on the exception) and re-raises. A shared
  consumer that loses its cold race returns its unused leases after its guard (`_return_unused_leases`: all tried,
  the failures raised as one ExceptionGroup). The three helpers are SitePlanRuntimeHelpers static methods, bound into
  a plan's namespace only when it leases.
- Overrides: a winning key on a consumer parameter fed by a managed site removes the site (no lease); winning keys on
  the managed site's own parameters make it fresh (above); deeper keys apply only when the site misses.
- Door (U7): route `"managed"` maps onto the existing `many` template objects in the four route tables (both fast
  bits), so `created` is True on every lease and a direct meld runs the activation hooks (the spell's and
  `on_meld_activation`) for a reused object too. No template is added or recompiled.
- Classification seams (U8): both `_is_shared_existence` predicates answer False for managed (B6); solo discovery
  declines a model holding one (B6); the generalized manifest's route-key whitelist takes "managed";
  `rows_contain_managed_step(rows)` makes `_install_specializing_door` keep the plain door. The lane plan's other
  existence branches are metadata the site plan never reads, and managed rows hydrate in the existing row shape.
- No cache generation 21: rows and manifests of existing spells do not change, plans are emitted at hydration, and
  every notch makes the creation cache cold (generation 9 admits only its own release).
- `Conduit.managed_spell_meld` (conduit.py, after `meld`): resolves the target as `meld` does, refuses `spell` with
  `spell_id` and a spell of another existence (ValueError, nothing melded), reads the pool from the version's owner
  store (none -> the missing-pool error), melds the version by id and returns `ManagedSpellLease(obj, pool)`. With
  own-parameter overrides the object is fresh and the lease's release still gives it to the pool (Decision Log).
- Gate met: the emission capture over 4461 non-managed shapes, door bodies and harness worlds is identical before and
  after (the S5 story's MEASURE note); a warm cycle (meld plus release) measured 320 ns on an automatic root and
  742 ns on a dynamic one.

"""

edits = [
    (
        """- Parked members move as rows; they are not re-stamped (`_migrate_inactive_members`, 1592-1635). UNKNOWN U9: whether
  `_apply_notch` (spellbook.py:3824-3964) re-stamps a promoted parked member's owner store after a transfer.
""",
        """- Parked members move as rows; they are not re-stamped (`_migrate_inactive_members`, 1592-1635). UNKNOWN U9: whether
  `_apply_notch` (spellbook.py:3824-3964) re-stamps a promoted parked member's owner store after a transfer.
- Found in S5 (the story's FACT note of 2026-10-15T16:18:21Z): a version staged with `bind_inactive` before conjure
  is never stamped - conjure stamps only the Book's active spells and `_apply_notch` stamps nothing - so after a
  notch to it, its first meld raises "Spell has no configured CreationContextFactory." for every existence, and a
  managed consumer's per-creation read raises the missing-pool error. Stamping the promoted member at notch (with U9)
  changes behaviour for every existence: S6 raises it to the owner.
- Transfers are dynamic-only and dynamic plans read the pool per creation (B7), so a plan finds a moved pool through
  the target's store; no plan binds a pool that a transfer can move.
""",
    ),
    (
        """- S5: tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py (managed shapes);
  tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py (direct meld reuse, injection
  into many and unique holders, overrides, failed-construction return, children disposed on trim);
  tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py (two roots, two binding names,
  per-frame ids, crystallizer restore, managed_spell_meld).
""",
        """- S5 (as built): tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py (51:
  emitted shapes and runtime on real pools), tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py
  and the discovery and specializer additions;
  tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py (23);
  tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py (7: two frames, two binding
  names, a dynamic late bind, a notch, a borrower, a lesser, a crystallizer restore).
""",
    ),
    (
        """- None open with the owner. U1-U6, U10 and U11 are settled (S2-S4); U7-U9 are read in source by S5 and S6.
""",
        """- None open with the owner. U1-U8, U10 and U11 are settled (S2-S5); U9 is read in source by S6, which also raises
  the stamping of a version notched in from before conjure (B8). For review: the build decisions (Decision Log).
""",
    ),
    (
        """- [ ] S5 STORY-2026-10-15-managed_dispense_codegen - per-path classification, discovery, manifest, lowering, door,
      overrides, failed-construction return, specializer, `Conduit.managed_spell_meld`, cache generation 21.
      tickets/stories/2026-10-15_managed_dispense_codegen_story.md
""",
        """- [x] S5 STORY-2026-10-15-managed_dispense_codegen - per-path classification, discovery, manifest, lowering, door,
      overrides, failed-construction return, specializer, `Conduit.managed_spell_meld`.
      Landed 0.2.8245. tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md
""",
    ),
    (
        """## Decision Log
- 2026-10-15 (owner, chat with melder_0): `ReleaseManagedSpell` is a singleton like Aether""",
        """## Decision Log
- 2026-10-15 (melder_0, S5 build decisions inside the owner's go-ahead, open to the owner's review): (1) the
  `managed` door route reuses the `many` template objects, so `created` is True on every lease and a direct meld runs
  the activation hooks for reused objects too; (2) no cache generation 21 (plans are emitted at hydration and a notch
  makes the cache cold); (3) F9 widened: any failure between a consumer's first lease and its construction, its
  publication included, and a lost cold race give the leases back; (4) a leasing site feeds exactly one consumer
  (per path; the emission refuses another count); (5) `managed_spell_meld` with overrides on the managed spell's own
  parameters returns a lease on that fresh, uncounted object, and its release adds the object to the pool - under the
  trusted-release ruling (2026-10-13) a `limited_quantity` or `queue` pool can then hold more than its limit.
- 2026-10-15 (owner, chat with melder_0): `ReleaseManagedSpell` is a singleton like Aether""",
    ),
]

note = NOTE.read_text(encoding="utf-8").splitlines()
section_start = next(n for n, line in enumerate(note, 1) if line.startswith("## `Existence.managed_spell_quantity`"))
section_end = next(n for n, line in enumerate(note, 1) if line == "## Packaging and documentation") - 1

MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S5 landed as 0.2.8245: meld and injection lease from the pools through the emitted plans - leasing and fresh
    managed sites, the inline pop (a plan constant on automatic roots, a per-creation read elsewhere), the
    reserve-first miss with children recorded with the object, the widened F9 return, the door rows on the many
    templates, the seams (per-path predicates, solo decline, manifest key, specializer decline) and
    `Conduit.managed_spell_meld`. Green in both GIL modes on the 51 lowering tests, the seam, discovery and
    specializer tests, 23 component and 7 integration tests and the whole tree; every non-managed emitted plan
    byte-identical (4461 entries); a warm cycle (meld plus release) 320 ns automatic, 742 ns dynamic. U7 and U8 are
    settled in B7; the pre-conjure staging gap is in B8.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md:1-STORY_LINES
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_validation_index.md:1-51
  - release_docs/next_version_release.md:{section_start}-{section_end}
  IMPACT: S6 moves pools the plans now lease from; transfers are dynamic-only and dynamic plans read the pool per
    creation, so a moved pool is found through the target's store.
  NEXT: Rebuild and check for 0.2.8245, then S6 - read TransferOfOwnership's creation moves and `_apply_notch` (U9).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""

epic = EPIC.read_text(encoding="utf-8")
start = epic.index(B7_OLD_START)
end = epic.index(B7_OLD_END)
epic = epic[:start] + B7_NEW + epic[end:]
for old, new in edits:
    assert epic.count(old) == 1, old[:80]
    epic = epic.replace(old, new)
anchor = "## Closure Confirmation"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, MEASURE + anchor)

start = epic.index("## Context / Handoff Summary")
end = epic.index("## Project-Specific Additions")
handoff = """## Context / Handoff Summary
- Scope: build `Existence.managed_spell_quantity` end to end (Build Specification B1-B12) in seven stories, one notch
  per landed story, rebuild last.
- Controlling decisions: the Decision Log (owner rulings 2026-10-12 to 2026-10-15; melder_0's build decisions of
  2026-10-15, the S4 story's DECISION note: the lease on the root, the holding root; the S5 build decisions). The
  objects handed out are the agents'; Melder keeps the structure right.
- Source revision: 0.2.8245 - S1 landed 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0);
  S2 0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3 0.2.8243
  (the pool, the exhaustion error, the Creations pool map, owner stamping, the probes, purge 0); S4 0.2.8244
  (`ReleaseManagedSpell`, the lease, the Creations register/unregister calls, the root exports); S5 0.2.8245 (leases
  through the emitted plans and doors, `Conduit.managed_spell_meld`).
- Done: Milestone 1; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S5 landed and
  closed (tickets/stories/completed/); U1-U8, U10 and U11 settled (B2-B7).
- Remaining: S6 (transfer; U9; the pre-conjure staging gap to the owner) and S7 (docs, graph, README, release note,
  benchmarks before/after against baseline_0_2_8244/, patch promotion).
- Limits: the codex_bridge listing fails ("Codex app tool request failed" on every try on 2026-10-15, last at
  17:15Z), so the tickets and the board row are the coordination record; hosted CI runs and coverage are the
  owner's (Not run).
- Owners: melder_0 builds; the owner accepts; no other lane holds a file of this one.
- Next 1-3 actions: rebuild the assets and bundles for 0.2.8245 and check them; S6 - read TransferOfOwnership's
  creation moves, rollback and `_migrate_inactive_members` and `_apply_notch` whole (U9), then the S6 component patch.

"""
epic = epic[:start] + handoff + epic[end:]
updated = [line for line in epic.splitlines() if line.startswith("- Updated: ")]
assert len(updated) == 1
epic = epic.replace(updated[0], f"- Updated: {NOW}")
long = [line for line in epic.splitlines() if len(line) > 120 and not line.lstrip().startswith(("- ", "|"))]
assert not long, long
EPIC.write_text(epic, encoding="utf-8")
print("epic updated", NOW, "release-note section", section_start, section_end)

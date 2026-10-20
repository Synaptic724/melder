"""Rescope the slotted_lifetime_ownership patch docs to the owner's transfer ruling (2026-10-14, D3 transfer default)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edit_tool import apply

ROOT = pathlib.Path(sys.argv[1]) / "context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14"

ARCH = [
    ("- Status: active - written before any src edit (2026-10-14)\n",
     "- Status: active - written before any src edit (2026-10-14); D3 rescoped by the owner (2026-10-14T22:14Z)\n"),
    ("- D3 transfer teardown (`move_creations=False`) and contract invalidation drop stored instances undisposed.\n",
     "- D3 a default transfer (`move_creations=False` until 0.2.8239) takes the source's instances out of its store and\n"
     "  puts them nowhere, so a transferred `unique` is rebuilt as a second instance; owner ruling 2026-10-14: the public\n"
     "  verb defaults to `move_creations=True` and its docstrings say what each value does. Contract invalidation drops\n"
     "  a retired consumer undisposed and leaves a lesser's consumer in place (b7, l2): pending the owner's ruling.\n"),
    ("| Creations | holder disposal record with adopted children; `adopt_children`; extract/restore carry children; whole-store, purge and retirement disposal include them; `dispose_extracted_creations`; `retire_singleton_creation` | D3, D4, D5 |\n",
     "| Creations | holder disposal record with adopted children; `adopt_children`; extract/restore carry children; whole-store and purge disposal include them; `retire_singleton_creation` only if the owner rules the invalidation fix in | D4, D5 (D3 pending) |\n"),
    ("| TransferOfOwnership / ConduitWard / Conduit transfer | teardown retires per existence and the extracted rows are disposed after the transfer finished, outside its transaction window | D3 |\n",
     "| Conduit / ConduitWard transfer verbs | `move_creations` defaults to True; the docstrings (the verbs, `TransferOfOwnership`, its move and teardown helpers) and the docs page state what each value does; no transfer logic changes | D3 |\n"),
    ("| ConduitWard contract invalidation | retires and disposes slotted consumers, leaves `many` objects in their store, logs disposal failures | D3 |\n",
     "| ConduitWard contract invalidation | pending the owner's ruling (b7: a retired consumer is dropped undisposed; l2: a lesser keeps serving its consumer) | D3 (pending) |\n"),
    ("5. (the earlier invariant 5 text, erased at the owner's direction on 2026-10-14)\n",
     "5. A transfer disposes nothing. By default (`move_creations=True`) the source's instances of every index member move\n"
     "   to the target's store with the spell, so a transferred `unique` stays one object and a holder's adopted children\n"
     "   move with it; `move_creations=False` is the caller's opt-out and keeps its behaviour (the active member's entries\n"
     "   leave the source store and are neither moved nor disposed). Contract invalidation: pending the owner's ruling.\n"),
    ("8. Disposal failures are never swallowed: purge, cluster deletion and transfer raise one ExceptionGroup after\n"
     "   finishing; frame teardown and contract invalidation (which run inside operations that must complete) log them.\n",
     "8. Disposal failures are never swallowed: purge and cluster deletion raise one ExceptionGroup after finishing; frame\n"
     "   teardown (which must complete) logs them.\n"),
    ("- Internal only (no public signature changes): `ConduitCluster.release_member(conduit)`, `drop_member(conduit)`;\n"
     "  `ClusterCreations.bind(store, leader_conduit_id)` and `leader_conduit_id`; `Creations.adopt_children(...)`,\n"
     "  `dispose_extracted_creations(rows)`, `retire_singleton_creation(spell_id)`; `HolderDisposalEntry`;\n"
     "  `TransferOfOwnership.take_retired_creations()`; `ConduitWard._transfer_spell_ownership(..., retired_creations=)`;\n"
     "  `Conduit._leave_cluster_for_teardown()`.\n",
     "- Internal: `ConduitCluster.release_member(conduit)`, `drop_member(conduit)`; `ClusterCreations.bind(store,\n"
     "  leader_conduit_id)` and `leader_conduit_id`; `Creations.adopt_children(...)`; `HolderDisposalEntry`;\n"
     "  `Conduit._leave_cluster_for_teardown()`; the ward's `_transfer_spell_ownership` default `move_creations=True`.\n"
     "- Public signature default (owner ruling 2026-10-14, Breaking): `Conduit.transfer_spell_ownership(...,\n"
     "  move_creations=True)` (was False). No other public signature changes.\n"),
    ("- Behaviour visible to users: a root's teardown leaves its cluster; an explicit leave unshares the leaver's roots;\n"
     "  cluster instances survive leader changes and die with the cluster; `delete_cluster` and `transfer_spell_ownership`\n"
     "  may raise an ExceptionGroup of disposal failures after finishing; a transferred `unique`/`unique_per_conduit`\n"
     "  instance is disposed when not moved; a `many` spell's objects stay with the source when not moved; a contract\n"
     "  change disposes the slotted consumers it retires; purging or moving a holder disposes or moves its children; a\n"
     "  `many` purge or live-creation probe of a child spell no longer counts children owned by a holder.\n",
     "- Behaviour visible to users: a root's teardown leaves its cluster; an explicit leave unshares the leaver's roots;\n"
     "  cluster instances survive leader changes and die with the cluster; `delete_cluster` may raise an ExceptionGroup of\n"
     "  disposal failures after finishing; a transfer moves the source's instances with the spell unless the caller passes\n"
     "  `move_creations=False`; purging or moving a holder disposes or moves its children; a `many` purge or\n"
     "  live-creation probe of a child spell no longer counts children owned by a holder.\n"),
    ("Patch docs -> red tests per task (GIL off and on) -> D1 src (notch 0.2.8236, with the D6 docstring) -> D2 src\n"
     "(0.2.8237) -> D4/D5 src (0.2.8238) -> D3 src (0.2.8239) -> red tests green, existing tests updated where they pin a\n"
     "corrected representation (reason recorded) -> audit probe clean -> full tree GIL off and on -> emission diff and\n"
     "meld benchmarks -> system docs, indexes, graph -> release note -> patch archived -> assets and llm_support last.\n",
     "Patch docs -> red tests per task (GIL off and on) -> D1 src (notch 0.2.8236, with the D6 docstring) -> D2 src\n"
     "(0.2.8237) -> D4/D5 src (0.2.8238) -> D3 transfer default (0.2.8239) -> red tests green, existing tests updated\n"
     "where they pin a corrected representation (reason recorded) -> audit probe clean -> full tree GIL off and on ->\n"
     "emission diff and meld benchmarks -> system docs, indexes, graph -> release note -> patch archived -> assets and\n"
     "llm_support last. The invalidation half of D3 waits for the owner's ruling.\n"),
    ("| 5 | component: transfer teardown per existence; contract sever disposes the borrower's slotted consumer, leaves `many` |\n",
     "| 5 | integration: a default transfer keeps a transferred `unique` one object (holder and consumer share it) and moves a tracked `many` object; `move_creations=False` still builds anew on the target |\n"),
    ("| 8 | component: delete_cluster and transfer raise after finishing; frame teardown logs |\n",
     "| 8 | component: delete_cluster raises after finishing; frame teardown logs |\n"),
]

CREATIONS = [
    ("Component: Creations and SpellSpace (the generic `Creations` store, `ConduitCreations` inherits it). Defects D3, D4,\n"
     "D5.\n",
     "Component: Creations and SpellSpace (the generic `Creations` store, `ConduitCreations` inherits it). Defects D4, D5\n"
     "(landed 0.2.8238); D3's invalidation helper pending the owner's ruling.\n"),
    ("- `dispose_extracted_creations(rows)` (new): runs the disposal methods recorded in extracted rows - newest row first,\n"
     "  a holder before its children - and returns the failures. Used for transfer teardown after the transfer finished.\n",
     "- WITHDRAWN (owner ruling 2026-10-14: a transfer disposes nothing): `dispose_extracted_creations` is not added.\n"),
    ("- `retire_singleton_creation(spell_id)` (new): under the store lock detach one slotted entry (and its holder record);\n"
     "  a `many` key or an absent key is left untouched; dispose outside the lock and return the failures. Used by contract\n"
     "  invalidation.\n",
     "- PENDING the owner's ruling on contract invalidation (b7, l2): `retire_singleton_creation(spell_id)` - under the\n"
     "  store lock detach one slotted entry (and its holder record), leave `many` keys alone, dispose outside the lock.\n"),
    ("Internal: `HolderDisposalEntry`; `Creations.adopt_children`, `dispose_extracted_creations`,\n"
     "`retire_singleton_creation`, and the private `_dispose_entry` / `_dispose_holder_entry`. `StoredDisposalValue` grows\n"
     "the new member. No public surface; the bind-guard manifest gains one internal class.\n",
     "Internal: `HolderDisposalEntry`; `Creations.adopt_children` and the private `_dispose_entry` /\n"
     "`_dispose_holder_entry` (0.2.8238); `retire_singleton_creation` only if the invalidation fix is ruled in.\n"
     "`StoredDisposalValue` grows the new member. No public surface; the bind-guard manifest gains one internal class.\n"),
    ("- Emitters (site-plan lowering) call `adopt_children`; transfer and the ward call the two retirement helpers.\n",
     "- Emitters (site-plan lowering) call `adopt_children`; the ward would call `retire_singleton_creation` (pending).\n"),
    ("extract/restore round-trip with children; `dispose_extracted_creations` order and aggregation;\n"
     "`retire_singleton_creation` leaves `many` keys. Component: p5 (purge disposes the children), t4b (move carries them).\n",
     "extract/restore round-trip with children (0.2.8238). Component: p5 (purge disposes the children), t4b (move carries\n"
     "them).\n"),
]

WARD = [
    ("Component: ConduitWard and Contracts (`_invalidate_contract_consumers`). Defect D3.\n",
     "Status: PENDING the owner's ruling (2026-10-14). The transfer half of D3 was rescoped to the default flip; this\n"
     "invalidation fix is not applied until the owner decides.\n"
     "\n"
     "Component: ConduitWard and Contracts (`_invalidate_contract_consumers`). Defect D3.\n"),
]

TRANSFER = """# Component patch: Ownership transfer - instances move by default (slotted_lifetime_ownership_2026_10_14)

Components: Conduit Runtime (`transfer_spell_ownership`), ConduitWard and Contracts (`_transfer_spell_ownership`,
`TransferOfOwnership`). Defect D3 (transfer half), rescoped by the owner on 2026-10-14 (epic Decision Log, "transfer
default"); D4 (children move with a moved holder) landed in 0.2.8238 through the Creations rows.

## Before / after
- Before: `transfer_spell_ownership(..., move_creations=False)` by default. The transfer moves the spell (the whole
  index, the registry entry, the owner pointer and owner store, borrowers), and `_teardown_creations` takes the active
  member's entries out of the source store, keeps them only for rollback and moves them nowhere: a transferred
  `unique` is rebuilt by the target as a second instance while whatever already held the first keeps it, and no
  `close` ever runs on the first (probes t3, u2). The docstrings call this tearing the source side down.
- After: the public verb (and the ward's mirror) default to `move_creations=True`: the source's instances of every
  index member move into the target's store with the spell, so a transferred `unique` stays one object (and a holder's
  adopted children move with it, 0.2.8238). `move_creations=False` keeps its behaviour as the caller's opt-out. A move
  into a slot the target already fills keeps its behaviour (the moved entry replaces it; probe m1). Lineage instances
  still never move; spellspace and cluster instances are not in a conduit's store. Nothing is disposed by a transfer.
- Docstrings (`Conduit.transfer_spell_ownership`, `ConduitWard._transfer_spell_ownership`, the `TransferOfOwnership`
  class and constructor, `_move_creations`, `_teardown_creations`) and the docs page state what each value does.
- `TransferOfOwnership.__init__` keeps `move_creations=False` as its own default: the conduit and the ward always pass
  the value, and 119 unit tests construct the helper directly with the default.

## Interface deltas
Public: `Conduit.transfer_spell_ownership(move_creations=True)` (was False) - Breaking, in the release note with the
opt-out. Internal: `ConduitWard._transfer_spell_ownership(move_creations=True)`.

## State / failure deltas
- A default transfer keeps the source's instances (moved, not rebuilt); the source's teardown no longer sees them and
  the target's teardown disposes them once.
- No new failure modes; a failed transfer's rollback moves the instances back (unchanged code path).

## Dependency / ordering
None beyond the 0.2.8238 Creations rows (children travel in a holder's row).

## Validation expectations
Integration: a default transfer keeps a transferred `unique` one object (a source consumer and the target's meld
share it; disposed once, at the target's teardown, not at the source's); a tracked `many` object moves by default;
`move_creations=False` still builds a new instance on the target. The existing transfer suites run unchanged.
"""

DISPOSAL = """# Code description patch: transfer teardown disposal and rollback (slotted_lifetime_ownership_2026_10_14)

SUPERSEDED by the owner's ruling of 2026-10-14 (epic Decision Log, "transfer default"): a transfer disposes nothing,
so the retired-row hand-off, the deferred disposal outside the TRANSFER_OWNERSHIP window and the ExceptionGroup this
document described are not implemented. D3's transfer half is the default flip described in
`component_patch_ownership_transfer`. Kept for traceability until the patch is archived.
"""

print("architecture", apply(str(ROOT / "architecture_patch.md"), ARCH))
print("creations", apply(str(ROOT / "component_patch_creations.md"), CREATIONS))
print("ward", apply(str(ROOT / "component_patch_conduit_ward_contracts.md"), WARD))
(ROOT / "component_patch_ownership_transfer.md").write_bytes(TRANSFER.encode("utf-8"))
(ROOT / "code_description_patch_transfer_disposal.md").write_bytes(DISPOSAL.encode("utf-8"))
print("transfer and disposal docs rewritten")

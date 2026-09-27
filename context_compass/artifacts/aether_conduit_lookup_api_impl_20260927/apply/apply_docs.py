"""Promotion of the aether_conduit_lookup_api patch lane into src_components, src_architecture and
tests_components (melder_0, 2026-09-27). LF documents; every anchor must match exactly once.

Usage: python apply_docs.py <system_docs dir> <verified_at UTC>
"""
import os
import sys

DOCS = sys.argv[1]
NOW = sys.argv[2]


def edit(name: str, pairs: list) -> None:
    path = os.path.join(DOCS, name)
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    assert "\r\n" not in text, name
    for old, new in pairs:
        found = text.count(old)
        if found != 1:
            raise SystemExit(f"{name}: anchor matched {found} times: {old[:80]!r}")
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    print(name, "edited:", len(pairs))


def c1(path: str, old_end: int, old_verified: str, new_end: int) -> tuple:
    old = (f"- path: `{path}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n"
           f"  verified_at: {old_verified}\n")
    new = f"- path: `{path}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {NOW}\n"
    return old, new


C1_CHANGES = [
    ("src/melder/aether/aether.py", 2456, "2026-09-26T20:10:34Z", 2690),
    ("src/melder/aether/aetheric_frame/conduit_cloud.py", 1018, "2026-09-23T12:28:41Z", 1051),
    ("src/melder/aether/conduit/conduit_ward/conduit_ward.py", 3788, "2026-09-26T20:10:34Z", 3813),
    ("src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py", 1998, "2026-08-02T13:00:45Z", 2000),
    ("src/melder/nexus/rift/command_system/command_system.py", 1697, "2026-09-23T11:33:20Z", 1696),
    ("src/melder/nexus/rift/command_system/static_command_system.py", 680, "2026-08-02T13:00:45Z", 682),
    ("src/melder/nexus/rift/frame_viewer/static_frame_viewer.py", 340, "2026-08-02T13:00:45Z", 333),
]

COMPONENTS = [
    ("- Doc ID: COMP-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-09-26\n",
     "- Doc ID: COMP-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-09-27\n"),
    ("""- Privately host singleton support roots for utility logging, crystallizer
  policy/activation, and Nexus AR behavior.

Inputs:
- Conduit objects, SpellIndex sets""",
     """- Privately host singleton support roots for utility logging, crystallizer
  policy/activation, and Nexus AR behavior.
- Answer frame-scoped conduit lookups at three coverages (0.2.79). ROOT: `list_root_conduit_ids`,
  `list_root_conduit_names`, `count_root_conduits`, `has_root_conduit_id`, `has_root_conduit_name`,
  `find_root_conduit_id_by_name`, `get_root_conduit_by_name` and `get_root_conduit_by_id` read the frame's
  root maps. NAMED: `get_conduit_by_name` reads the frame Cloud's directory (named roots and active named
  lessers). LIVE: `get_conduit_by_id` reads the root map, then each root ward's lineage (roots and attached
  lessers, named or anonymous). Every lookup takes `aetheric_frame_name: str = "default"`.

Inputs:
- Conduit objects, SpellIndex sets"""),
    ("""Invariants/Guarantees:
- One Aether instance per interpreter.
- Default frame exists when needed.
""",
     """Invariants/Guarantees:
- One Aether instance per interpreter.
- Default frame exists when needed.
- Conduit lookups resolve their frame through one resolver (`_resolve_lookup_frame`): TypeError unless the
  frame is a `str`, then `_get_existing_frame` ("default" is created lazily; a custom frame must exist). They
  return borrowed references, grant no lease and take no lock beyond the Cloud's leaf lock (NAMED); the LIVE
  walk reads `dict.copy()` snapshots of the root map and of every ward's child map (0.2.79).
  EVIDENCE: `src/melder/aether/aether.py:Aether._resolve_lookup_frame`, `Aether.get_conduit_by_name`,
  `Aether.get_conduit_by_id` and `Aether._find_live_conduit`.
"""),
    ("""- ValueError for missing frames, duplicate registry entries, or not-found lookups.
- TypeError for invalid input types (e.g., non-string frame names).
""",
     """- ValueError for missing frames, duplicate registry entries, or not-found lookups. A not-found conduit
  lookup names the searched frame and points at the wider lookup (0.2.79).
- TypeError for invalid input types (e.g., non-string frame names, including every conduit lookup's frame).
"""),
    ("""- Provide ConduitCloud for active named root/lesser lookup in automatic and dynamic mode.
""",
     """- Provide ConduitCloud for active named root/lesser lookup in automatic and dynamic mode.
  `ConduitCloud.list_conduits()` returns those scopes as a tuple snapshot of borrowed conduits, and
  `Aether.get_conduit_by_name` reads the same directory (0.2.79).
"""),
    ("""- Internal RLock; contract creation uses ordered locking (per docstring).
""",
     """- Internal RLock; contract creation uses ordered locking (per docstring).
- The lineage walk `_get_lesser_conduit` takes no lock and iterates a `dict.copy()` snapshot of
  `_lesser_conduits` at every level: links write that dict under this ward's lock while a returning child
  pops itself from it under its OWN lock (`_detach_for_pool`), so no single lock gives a stable view. A child
  whose `_conduit_ward` hard teardown deleted is skipped. `Aether.get_conduit_by_id` runs this walk root by
  root (0.2.79).
  EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._get_lesser_conduit` and
  `ConduitWard._detach_for_pool`.
"""),
    ("""- Capability and codegen named getters resolve the published authorized ID through existing
  root/lesser traversal, then refuse changed live names. Capability create_lesser_conduit forwards
""",
     """- Capability and codegen named getters resolve the published authorized ID through Aether's
  live-conduit lookup (`Aether.get_conduit_by_id`: root map, then root wards; 0.2.79), then refuse
  changed live names. Capability create_lesser_conduit forwards
"""),
    ("""- `src/melder/aether/aether.py`

### Subcomponent: Conduit Normal Initialization
""",
     """- `src/melder/aether/aether.py`

### Subcomponent: Aether Conduit Lookups
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Frame-scoped conduit discovery from the runtime root, with each lookup's coverage stated in its name (0.2.79).
Contract/Interface:
- ROOT: `list_root_conduit_ids`, `list_root_conduit_names`, `count_root_conduits`, `has_root_conduit_id`,
  `has_root_conduit_name`, `find_root_conduit_id_by_name` (None when absent), `get_root_conduit_by_name` and
  `get_root_conduit_by_id`; private `_get_root_conduit_by_name` / `_get_root_conduit_by_id`, which spell-owner
  resolution (`_get_conduit_by_spell_id`) uses because only roots own spells.
- NAMED: `get_conduit_by_name` returns the frame Cloud's entry (named roots and active named lessers).
- LIVE: `get_conduit_by_id` returns a root from the root map or a lesser from a root ward's lineage.
- Every lookup takes `aetheric_frame_name: str = "default"`; `_resolve_lookup_frame` raises TypeError for a
  non-string frame and otherwise defers to `_get_existing_frame`. Not-found ValueErrors name the frame.
- Before 0.2.79 the eight lookups carried generic names and answered over roots only; six of those names were
  removed without aliases, and `get_conduit_by_name` / `get_conduit_by_id` were reused for NAMED / LIVE.
Data Structures:
- None owned. Reads the frame's `_conduits` and `_conduit_ids_by_name` and the frame Cloud's directory.
Concurrency/Threading:
- ROOT reads take no lock; NAMED takes the Cloud's leaf lock; LIVE copies the root map and each ward's child
  map, so a scope attached or returned during the walk may or may not be seen and never makes it raise.
Key Files (C1):
- `src/melder/aether/aether.py`
- `src/melder/aether/aetheric_frame/conduit_cloud.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`

### Subcomponent: Conduit Normal Initialization
"""),
    ("""- `get_conduit`, name/id/list/count reads; internal `_register_named_conduit`,
  `_unregister_named_conduit`, `_reserve_conduit_name` and `_release_conduit_name`.
""",
     """- `get_conduit`, name/id/list/count reads, `list_conduits()` (a tuple snapshot of the named conduits,
  0.2.79); internal `_register_named_conduit`, `_unregister_named_conduit`, `_reserve_conduit_name` and
  `_release_conduit_name`.
"""),
    ("""- `Conduit.transfer_spell_ownership(...)` and `_transfer_spell_ownership(...)`.
""",
     """- `Conduit.transfer_spell_ownership(...)` and `_transfer_spell_ownership(...)`.
- The impacted-conduit sweep (`TransferOfOwnership._collect_impacted_conduit_ids`) reads ROOT conduits only,
  through `Aether.list_root_conduit_ids` / `get_root_conduit_by_id`: a lesser owns only the lifecycle of what
  it creates (owner ruling, 2026-09-27).
"""),
    ("""- Frame-local operations require explicit `frame_name`; there is no
  default-frame routing contract.
""",
     """- Frame-local operations require explicit `frame_name`; there is no
  default-frame routing contract.
- `StaticFrameViewer._get_owner_conduit` resolves a spell record's owner through `Aether.get_conduit_by_id`
  (roots and attached lessers) and returns None on a miss (0.2.79).
"""),
    ("""- Static-owned:
  live-only spell retrieval, `meld_existing_spell(...)`, and static
  spell-status helpers.
""",
     """- Static-owned:
  live-only spell retrieval, `meld_existing_spell(...)`, and static
  spell-status helpers.
- Conduit id lookups (`_get_conduit_by_id_locked`) pass the ACL gates, then delegate to
  `Aether.get_conduit_by_id`; a miss reports the frame error when the frame is gone, else "Conduit id 'I' was
  not found in frame 'F'.". Static spell owners resolve through `Aether.get_root_conduit_by_id` (0.2.79).
"""),
    ("""
### Flow: Purge a Target's Retained Creations
""",
     """
### Flow: Aether Conduit Lookup by Name or Id
1. `Aether.get_conduit_by_name(name, aetheric_frame_name="default")` runs `check_cleaned`, then
   `_resolve_lookup_frame` (TypeError unless a `str`; `_get_existing_frame` creates "default" lazily and
   requires a custom frame to exist), then `ConduitCloud.get_conduit_by_name(name)` under the Cloud's leaf
   lock; a Cloud ValueError is re-raised naming the frame.
2. `Aether.get_conduit_by_id(conduit_id, aetheric_frame_name="default")` resolves the frame the same way,
   then `_find_live_conduit`: `frame._conduits.copy()` answers a root id; otherwise each root's
   `ConduitWard._get_lesser_conduit` walks `_lesser_conduits.copy()` depth-first, skipping deleted or None
   wards. A miss raises ValueError naming the frame.
3. The ROOT lookups resolve the frame the same way and read `frame._conduits` / `frame._conduit_ids_by_name`
   only; `_get_conduit_by_spell_id` resolves spell owners through `_get_root_conduit_by_id`.
4. `CommandSystem._get_conduit_by_id_locked` (after its ACL gates) and `StaticFrameViewer._get_owner_conduit`
   use step 2; `StaticCommandSystem` and `TransferOfOwnership._collect_impacted_conduit_ids` use step 3.

### Flow: Purge a Target's Retained Creations
"""),
    ("""  `has_conduit_name`, `src/melder/aether/aetheric_frame/conduit_cloud.py:547`).
  Both re-measured 2026-08-02; the patch-lane copy cited :411 and :379.
""",
     """  `has_conduit_name`, `src/melder/aether/aetheric_frame/conduit_cloud.py:720`).
  Both re-measured 2026-08-02; the patch-lane copy cited :411 and :379. The Cloud line was
  re-measured again 2026-09-27 (it had drifted to :687 before the 0.2.79 edit moved it to :720).
"""),
    ("""  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:951` passes `SafeGuard(tgt_book._lock, src_book._lock)`
  and `:1442` passes `SafeGuard(src_book._lock, tgt_book._lock)`. Do NOT "tidy"
""",
     """  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:953` passes `SafeGuard(tgt_book._lock, src_book._lock)`
  and `:1444` passes `SafeGuard(src_book._lock, tgt_book._lock)`. Do NOT "tidy"
"""),
    ("""  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:951, 1442
""",
     """  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:953, 1444
"""),
    ("""  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2483-2537.
""",
     """  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2508-2562.
"""),
]
COMPONENTS += [c1(*change) for change in C1_CHANGES]

ARCHITECTURE = [
    ("- Created: 2026-01-17\n- Updated: 2026-09-26\n", "- Created: 2026-01-17\n- Updated: 2026-09-27\n"),
    ("""- `Conduit.create_lesser_conduit(...)` for child scopes.
""",
     """- `Conduit.create_lesser_conduit(...)` for child scopes.
- `Aether.get_conduit_by_name(...)` (named roots and active named lessers) and
  `Aether.get_conduit_by_id(...)` (any live conduit) for frame-scoped discovery; root-only discovery is
  the `*_root_*` family (`get_root_conduit_by_name`, `get_root_conduit_by_id`, `list_root_conduit_ids`,
  ...), and `ConduitCloud.list_conduits()` lists one frame's named scopes (0.2.79).
"""),
    ("""  `Conduit._prepare_named_for_pool` and `Conduit.upgrade_to_normal`.
- Dynamic named recording stores detached ancestor values inside each surviving named twin.
""",
     """  `Conduit._prepare_named_for_pool` and `Conduit.upgrade_to_normal`.
- Conduit lookup coverage (2026-09-27, 0.2.79): Aether's lookups name what they cover. The `*_root_*` family
  reads the frame's root maps only; `get_conduit_by_name` reads the frame Cloud's named directory, so a live
  named lesser resolves by name at any depth and returns the same object as the Cloud; `get_conduit_by_id`
  reads the root map, then every root ward's lineage, so anonymous lessers resolve by id. Scopes returned to
  their pool or cleaned do not resolve. Lookups are frame-scoped (`aetheric_frame_name: str = "default"`, a
  non-string raises TypeError), grant no lease and read snapshots (`dict.copy()` of the root map and of each
  ward's child map), because links and pool returns write a ward's child map under two different locks.
  Ownership stays root-only: spell-owner resolution and the transfer impact sweep use the root lookups.
  EVIDENCE: `src/melder/aether/aether.py:Aether.get_conduit_by_name`, `Aether.get_conduit_by_id`,
  `Aether._find_live_conduit` and
  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._get_lesser_conduit`.
- Dynamic named recording stores detached ancestor values inside each surviving named twin.
"""),
    ("""- Named collision/acquisition failures preserve other directory owners. Soft retirement failures
""",
     """- A conduit lookup given a non-string frame raises TypeError naming the lookup; a not-found lookup raises
  ValueError naming the searched frame, and a missing custom frame keeps "Aetheric frame 'F' does not exist."
  (0.2.79). Before 0.2.79 `Aether.get_conduit_by_name` answered over roots only, so a live named lesser raised
  "not found" while its frame's Cloud returned it.
  EVIDENCE: `src/melder/aether/aether.py:Aether._resolve_lookup_frame` and `Aether.get_conduit_by_name`.
- Named collision/acquisition failures preserve other directory owners. Soft retirement failures
"""),
    ("""### ASCII Context Diagram (C4)
""",
     """### Conduit Lookup Coverage
```text
Aether lookup(frame: str = "default") -> _resolve_lookup_frame -> frame
  *_root_*            -> frame root maps              -> roots
  get_conduit_by_name -> frame ConduitCloud directory -> named roots + active named lessers
  get_conduit_by_id   -> root map snapshot, then each root ward's lineage snapshot -> any live conduit
```

```mermaid
flowchart LR
  L[Aether lookup with frame name] --> R[Frame resolver: str required]
  R --> F[Existing frame]
  F -->|root lookups| M[Root maps: roots]
  F -->|get_conduit_by_name| C[ConduitCloud: named roots and named lessers]
  F -->|get_conduit_by_id| W[Root map, then ward lineages: any live conduit]
```

### ASCII Context Diagram (C4)
"""),
    ("""## Context / Handoff Summary

2026-09-26 door-held first builds (0.2.73)""",
     """## Context / Handoff Summary

2026-09-27 conduit lookup coverage (0.2.79): Aether's eight root-only lookups carry `*_root_*` names;
`get_conduit_by_name` now answers over a frame's named scopes and `get_conduit_by_id` over every live conduit,
lessers included; one frame resolver makes a non-string frame a TypeError; `ConduitCloud.list_conduits()`
lists named scopes. The boundary list, the operational invariants, the failure modes, the diagrams and the code
map carry it; the component map carries the lookup contract and the snapshot ward walk.

2026-09-26 door-held first builds (0.2.73)"""),
]
ARCHITECTURE += [c1(*change) for change in C1_CHANGES]

TESTS = [
    ("- Created: 2026-01-22\n- Updated: 2026-09-26\n", "- Created: 2026-01-22\n- Updated: 2026-09-27\n"),
    ("""  through both Nexus and Rift; the ACL chain provisioned on publish, advanced and
  rolled back after conjure, and removed on frame detach
Key Files (C1):
- `tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py`
- `tests/integration/melder/aether/test_frame_acl_chain_integration.py`
""",
     """  through both Nexus and Rift; the ACL chain provisioned on publish, advanced and
  rolled back after conjure, and removed on frame detach; Aether's conduit lookups over real
  scopes - named lessers by name at any depth, anonymous and nested lessers by id, roots through
  the root-named lookups, returned scopes absent, frame-naming errors and the frame-string TypeError
  (0.2.79 regression for named lessers looking absent from Aether)
Key Files (C1):
- `tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py`
- `tests/integration/melder/aether/test_frame_acl_chain_integration.py`
- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`
"""),
    ("""  guardrails; command-system lookups, and one room memory per top-level public call
""",
     """  guardrails; command-system lookups (conduit ids resolve through Aether's live lookup and a
  missing runtime frame keeps its frame error), and one room memory per top-level public call
"""),
    ("""- path: `tests/integration/melder/aether/test_frame_acl_chain_integration.py`
  start_line: 1
  end_line: 283
  loc: 283
  verified_at: 2026-09-26T22:11:36Z
""",
     f"""- path: `tests/integration/melder/aether/test_frame_acl_chain_integration.py`
  start_line: 1
  end_line: 283
  loc: 283
  verified_at: 2026-09-26T22:11:36Z
- path: `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`
  start_line: 1
  end_line: 145
  loc: 145
  verified_at: {NOW}
"""),
    ("""- path: `tests/unit/melder/aether/test_command_system_direct.py`
  start_line: 1
  end_line: 457
  loc: 457
  verified_at: 2026-09-26T22:11:36Z
""",
     f"""- path: `tests/unit/melder/aether/test_command_system_direct.py`
  start_line: 1
  end_line: 483
  loc: 483
  verified_at: {NOW}
"""),
    ("""- `tests/unit/melder/aether/test_command_system_direct.py`
- direct filesystem inventory of `tests/`
""",
     """- `tests/unit/melder/aether/test_command_system_direct.py`
- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`
- direct filesystem inventory of `tests/`
"""),
    ("""## Context / Handoff Summary

REFRESHED 2026-09-26""",
     """## Context / Handoff Summary

2026-09-27 conduit lookup coverage (0.2.79): `test_aether_named_lesser_lookup.py` joined the Aether Integration
Cluster (named lessers by name, anonymous and nested lessers by id, root-named lookups, returned scopes, frame
errors); the Aether/Nexus/Rift Unit Cluster's command-system lookups now resolve through Aether's live lookup.
Unit coverage of the lookup family, the Cloud listing and the snapshot ward walk sits in files this map keeps
below cluster level (`test_aether.py`, `test_conduit_cloud.py`, `test_conduit_ward.py`).

REFRESHED 2026-09-26"""),
]

edit("src_components.md", COMPONENTS)
edit("src_architecture.md", ARCHITECTURE)
edit("tests_components.md", TESTS)

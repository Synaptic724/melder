# SpellIndex Multi-Spell Transfer Blast Radius

## Metadata
- Artifact ID: ART-2026-05-22-spellindex-multi-spell-transfer-blast-radius
- Parent Epic: EPIC-2026-05-22-pin-down-spellindex-transfer-and-version-semantics
- Status: active
- Created: 2026-05-22T10:34:19Z
- Updated: 2026-05-22T10:34:19Z

## Purpose
Capture the concrete runtime blast radius for this proposed direction:

- keep public index resolution singular through `SpellIndex.current`
- allow a `SpellIndex` to manage multiple concrete spells internally
- extend `transfer_of_ownership` so a concrete spell can move from one index to
  another
- delete an old index when it no longer contains any spells

This artifact is not the final semantic decision.
It is the mechanics map showing what currently assumes:
- one index -> one spell
- one index -> one owner spellbook
- one index -> one owner conduit

and what likely stays valid if index resolution remains singular.

## Current Public Contract To Preserve
The proposal does not require changing the public runtime meaning of
`SpellIndex`.

The contract we appear to want to preserve is:
- `SpellIndex` remains a runtime handle
- `SpellIndex.current` remains the current meldable spell version
- `meld` / `get_spell_by_index_id(...)` still resolve one active spell through
  the current version

So the problem is not:
- public resolution ambiguity

The problem is:
- internal storage and management mechanics that still assume one concrete
  spell per index

## Core Finding
Current runtime is a mixed model.

It already has some multi-version/index-like machinery:
- `SpellIndex.current`
- `SpellIndex.get_all_versions()`
- frame-level version caches built from those versions

But the main ownership and lookup mechanics are still one-to-one:
- local spellbook storage
- contracted spellbook storage
- transfer-of-ownership movement
- some support helpers

So the likely implementation direction is:
- preserve current public resolution semantics
- widen internal membership mechanics
- widen transfer mechanics
- keep current-version consumers intact where possible

## Semantics Audit Against The One-Active-Spell Model

The target model being checked here is:
- one index may manage many concrete spells/versions internally
- exactly one spell is active through `SpellIndex.current`
- normal runtime resolution by index stays singular and resolves that active
  spell

### Already aligned or likely aligned

#### Aether frame version advertising
Current behavior:
- frame `_spell_registry` stores `Set[SpellIndex]`
- `_version_registry` is rebuilt from `spell_index.get_all_versions()`
- `_check_for_spell(...)` returns the index advertising the version

Why this is likely aligned:
- it does not require a direct one-index -> one-spell mapping
- it only requires the index to advertise version membership and one current
  active spell

Evidence:
- `src/melder/aether/aetheric_frame/aetheric_frame.py:469-576`
- `src/melder/aether/aether.py:1243-1277`

#### Current-version compiler / meld / validation surfaces
Current behavior:
- many runtime surfaces consume `spell.spell_index.current`
- they do not directly care how many inactive spells live under the same index

Why this is likely aligned:
- if `current` remains the one active resolution target, these callers can
  continue to work without semantic change

Representative evidence:
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py`

#### Nexus read-side lookup
Current behavior:
- published spell records carry `spell_index_id`
- command lookup resolves by `spell_index_id`, then asks the owner conduit for
  the spell by index id

Why this is likely aligned:
- if `get_spell_by_index_id(...)` remains "return the current active spell for
  this index", Nexus does not need a semantic rewrite

Evidence:
- `src/melder/nexus/frame_descriptor/spell_record.py:56-58`
- `src/melder/nexus/frame_descriptor/spell_record.py:125-127`
- `src/melder/nexus/rift/command_system/command_system.py:204-268`

### Clear blockers or incompletely aligned surfaces

#### Local spellbook storage
Current behavior:
- `_spells: Dict[SpellIndex, Spell]`
- `_find_spell(spell_index)` returns one `Spell`

Why this is a blocker:
- this is a direct one-index -> one-spell store
- it cannot represent inactive/member spells under the same index

Evidence:
- `src/melder/aether/spellbook/spellbook.py:212-216`
- `src/melder/aether/spellbook/spellbook.py:1150-1165`
- `src/melder/aether/spellbook/spellbook.py:2873-2874`

#### Contracted spellbook storage
Current behavior:
- `_contracted_spells: Dict[str, Dict[SpellIndex, Spell]]`
- `_find_contracted_spell(spell_index)` returns one `Spell`

Why this is a blocker:
- same singular assumption exists on the contracted side

Evidence:
- `src/melder/aether/spellbook/spellbook.py:220-223`
- `src/melder/aether/spellbook/spellbook.py:1168-1187`

#### Bind path
Current behavior:
- bind always creates a new `SpellIndex(initial_id=fingerprint)`

Why this is a blocker:
- there is no current path to bind another spell into an existing index

Evidence:
- `src/melder/aether/spellbook/bind/bind.py:272-273`

#### Transfer-of-ownership
Current behavior:
- resolves one concrete spell from an index
- moves the spell while keeping the same `spell_obj.spell_index`
- rewrites SpellIndex-side owner fields on the same index

Why this is a blocker:
- no "move spell to another index" mechanic
- no empty-index deletion path

Evidence:
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:380-387`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:747-803`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1223-1342`

#### ConduitCluster helper
Current behavior:
- resolves one spell from one index via `book._spells.get(spell_index)`
- `share_to_borrower(...)` and `remove_shared_from_borrower(...)` then use the
  resolved spell's `spell.spell_id` as the cluster-root contract source

Why this is a blocker:
- helper is hard-wired to singular spellbook storage
- helper is not explicitly current-aware; it assumes the spellbook map already
  returns the one active spell for that index instead of deliberately resolving
  through the index's current selection semantics

Evidence:
- `src/melder/aether/conduit/conduit_cluster.py:545-561`
- `src/melder/aether/conduit/conduit_cluster.py:438-470`
- `src/melder/aether/conduit/conduit_cluster.py:490-517`

Why it matters:
- if one index manages many concrete spells internally, cluster sharing and
  cluster unsharing need to resolve the active/current spell explicitly
- otherwise cluster-root ids and borrowed contract cleanup can drift onto the
  wrong member spell

#### SpellSystemStates owner bookkeeping
Current behavior:
- stores one `_index_owner_spellbook_id[index_id]`
- resolves that owner from `spell_index._owner_spellbook`

Why this is at least a pressure point:
- this assumes one owner spellbook per index
- whether that stays valid depends on the final multi-spell-per-index
  ownership model

Evidence:
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:255-285`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:335-351`

## Direct Blast Radius: Must Change

### 1. Bind always creates a fresh index
Current behavior:
- `Bind._bind_logic(...)` always computes a fingerprint and creates a new
  `SpellIndex(initial_id=fingerprint)`.

Evidence:
- `src/melder/aether/spellbook/bind/bind.py:272-273`

Why it matters:
- bind currently has no path to attach a new spell to an existing index
- any multi-spell-per-index design needs a new bind path or explicit attach
  path

### 2. Local spellbook storage is one index -> one spell
Current behavior:
- `_lookup_spells[new_spell._key] = spell_index`
- `_spells[spell_index] = new_spell`
- `_find_spell(spell_index)` returns one spell from `_spells`

Evidence:
- `src/melder/aether/spellbook/spellbook.py:1150-1165`
- `src/melder/aether/spellbook/spellbook.py:2873-2874`

Why it matters:
- this is the clearest direct blocker
- if one index can hold many concrete spells, `_spells` cannot remain a simple
  `SpellIndex -> Spell` map

### 3. Contracted spellbook storage is also one index -> one spell
Current behavior:
- `_find_contracted_spell(spell_index)` scans contracted maps and returns a
  single spell

Evidence:
- `src/melder/aether/spellbook/spellbook.py:1168-1187`

Why it matters:
- any multi-spell-per-index model must decide whether contracted storage also
  becomes membership-aware or remains current-only

### 4. Conduit runtime index lookup is singular by spellbook shape
Current behavior:
- `Conduit.get_spell_by_index_id(...)` delegates into `Spellbook`
- internal conduit paths expect `Spellbook._find_spell(spell_index)` to return
  one spell

Evidence:
- `src/melder/aether/conduit/conduit.py:1638-1673`
- `src/melder/aether/conduit/conduit.py:1712-1738`

Why it matters:
- if spellbook storage changes, conduit index lookup must either stay as a
  current-only facade or become membership-aware for management-only callers

### 5. Transfer-of-ownership assumes same-index movement
Current behavior:
- resolving a passed `SpellIndex` returns one spell from the source spellbook
- rollback writes the spell back under the same `spell_obj.spell_index`
- ownership flip updates `spell_obj.spell_index._owner_spellbook`,
  `_owner_spell`, and `_owner_conduit_id`
- target spellbook local lookup writes `spell_obj._key -> spell_obj.spell_index`

Evidence:
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:380-387`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:747-803`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1223-1342`

Why it matters:
- this is the main mechanic that must be extended
- transfer currently means stewardship move with fixed index
- the new direction needs:
  - transfer while keeping index
  - transfer into another index
  - old-index deletion when empty

### 6. ConduitCluster spell resolution assumes one spell per index
Current behavior:
- `_resolve_spell_from_index(...)` returns `book._spells.get(spell_index)`

Evidence:
- `src/melder/aether/conduit/conduit_cluster.py:545-561`

Why it matters:
- cluster auto-sharing and any cluster-local resolution that uses this helper
  will need an explicit current-only or membership-aware path

### 7. SpellSystemStates assumes one owner spellbook per index
Current behavior:
- `register_index(...)` stores one `current_spell_id` for the index
- `_index_owner_spellbook_id[index_id] = owner_spellbook_id`
- `_resolve_spellbook_id_from_index(...)` reads `spell_index._owner_spellbook`

Evidence:
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:232-285`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:335-351`

Why it matters:
- if one index can host many spells across different management states, this
  owner-spellbook model becomes a pressure point immediately
- even if current resolution stays singular, registration semantics may need a
  better owner or membership model here

## Direct Blast Radius: Probably Needs Audit

### 8. Aether frame spell registry and version cache
Current behavior:
- frame `_spell_registry` is `conduit_id -> Set[SpellIndex]`
- version cache is rebuilt from `spell_index.get_all_versions()`
- `_check_for_spell(...)` returns the index advertising the version

Evidence:
- `src/melder/aether/aetheric_frame/aetheric_frame.py:96-102`
- `src/melder/aether/aetheric_frame/aetheric_frame.py:469-499`
- `src/melder/aether/aetheric_frame/aetheric_frame.py:550-576`
- `src/melder/aether/aether.py:1243-1277`

Why it matters:
- this may still be viable if index-level version membership semantics remain
  valid
- but empty-index deletion and cross-index spell transfer will require explicit
  registry refresh/update rules

### 9. Nexus published spell records and command lookup
Current behavior:
- published spell records store both `spell_index_id` and `owner_conduit_id`
- command lookup resolves by published `spell_index_id`, then goes through the
  owner conduit and spellbook to get the live spell

Evidence:
- `src/melder/nexus/frame_descriptor/spell_record.py:56-58`
- `src/melder/nexus/frame_descriptor/spell_record.py:125-127`
- `src/melder/nexus/frame_descriptor_manager.py:514-516`
- `src/melder/nexus/rift/command_system/command_system.py:204-268`

Why it matters:
- this is downstream, not primary semantics
- it probably survives unchanged if one index still exposes one current spell
- but any "many spells under one index" management surface needs a clear rule
  for what published `spell_index_id` means

### 10. Transfer pressure in contract/ward surfaces
Current behavior:
- contract and borrower resolution often use `SpellIndex` plus version checks
- some paths use `detail.spell_index` and then resolve through
  `_find_contracted_spell(spell_index)`

Evidence:
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py:2644-2691`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py:2749-2780`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py:3071-3071`

Why it matters:
- if a contracted index can now hold multiple spells, these callers need a
  clear rule for whether contract resolution is "current-only" or can target a
  non-current member spell

## Broad Current-Version Surfaces: Likely Safe If Resolution Stays Singular

There are many consumers of `spell.spell_index.current` across compiler, meld,
validation, risk, and execution-plan code.

Representative examples:
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py`

Why this matters:
- these call sites are large in number, but many may not require semantic
  change if the runtime contract remains:
  one index -> one current meldable spell version

So these are probably:
- downstream audit surfaces
- not first-cut blockers

## Current Bind-Time Existence Check
Bind-time existence already has two separate checks:

1. SHA/version collision in Aether
- `Spellbook.bind(...)` calls `_aether._check_for_spell(new_spell.spell_id, frame)`
- this checks the frame version cache and returns the index advertising that
  version if found

Evidence:
- `src/melder/aether/spellbook/spellbook.py:2845-2856`
- `src/melder/aether/aether.py:1243-1277`

2. Binding-key collision in Spellbook
- `_assert_lookup_key_available(...)`

Evidence:
- `src/melder/aether/spellbook/spellbook.py:1362-1417`
- `src/melder/aether/spellbook/spellbook.py:2859-2865`

Why it matters:
- if bind can add another spell to an existing index intentionally, both of
  these checks need explicit policy rules for when they still block and when
  they should allow index membership growth

## Operation Set That Now Needs Definition

### A. Stewardship transfer
- same spell
- same index
- new spellbook/conduit/runtime steward

### B. Reindex transfer
- same spell
- old index membership removed
- new index membership added
- old index deleted if empty

### C. Bind-into-existing-index
- new spell
- existing index chosen explicitly
- membership added
- current selection rule applied

### D. Empty-index garbage collection
- remove from spellbook maps
- remove from Aether frame registry
- refresh version cache
- clean up any downstream state that should not survive an empty index

### E. Reindex invalidation / revalidation
- moving a spell into another index should gate that spell/index by default
- the target-side active spell should be forced back through structural or
  register/rebind validation before normal trust resumes
- this should be a built-in invalidation step, not an optional higher-layer
  follow-up

## Open Mechanics Questions
- What is the internal storage shape for many spells under one index?
- Is there exactly one current spell object per index, or only one current
  spell id that resolves to one spell object?
- When bind adds a spell to an existing index, does it become current by
  default or only explicitly?
- When transfer moves a spell into another index, what happens to
  `SpellIndex.current` on both source and target?
- If the old index becomes empty, what owns deletion and cleanup?
- Does MutationResearch stay keyed to `SpellIndex.id`, or is that a separate
  semantic problem that should remain outside this first mechanics cut?

## Initial Work Buckets

### Bucket 1: Primary blockers
- `Bind`
- `Spellbook` local storage
- `Spellbook` contracted storage
- `TransferOfOwnership`

### Bucket 2: Support/runtime helpers
- `Conduit`
- `ConduitCluster`
- contract/ward spell resolution helpers
- `SpellSystemStates` owner/index assumptions

### Bucket 3: Downstream audit
- `Aether` registry/cache refresh paths
- `Nexus` published spell records and command lookup
- broad `spell.spell_index.current` consumers

## Summary
The blast radius is real, but concentrated.

The main blockers are not:
- meld semantics
- generic current-version consumers

The main blockers are:
- spellbook singular storage
- transfer assuming fixed index
- bind always minting a fresh index
- owner-spellbook assumptions inside `SpellSystemStates`

If the public rule remains "resolve one current spell through the index," then
most of the broad `spell_index.current` runtime can probably stay intact while
the membership and transfer mechanics are widened underneath it.

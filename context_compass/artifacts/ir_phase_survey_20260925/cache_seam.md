# Survey record: the cache seam - `.melc` mechanics (D4) and snapshot key composition (D3)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 3, step S9).
Status: COMPLETE. Read whole: `utilities/caching_system/caching_system.py` (618, two chunks).
Read by method: `spellbook_creation_system.py:412-518` (`_build_conjure_cache_state`,
`_resolve_conjure_cache_path`; re-verified), `phases/shared_compiler_executions.py:60-137`
(serializer, hash) and `:266-377` (`capture_phase2_5_codegen_ir`; re-verified against the moving
working tree, below), `bind/bind.py:695-716` and `:837-994` (`sha256_profile`: the spell id).
Bounded expansion outside `spell_compiler/**`: one file, `bind/bind.py`, because the spell id is
the per-spell key and its composition decides what invalidates a per-spell row.
Working-tree note: another lane (melder_0, `missing_dependency_sockets`) is editing
`spell_compiler/**` now; `shared_compiler_executions.py` carries a CRLF sweep plus content hunks at
`:875-1263` (none in the ranges cited here) and the other `M` files under the compiler are
line-ending-only (`git diff -w -U0` shows no hunks). Ranges cited from earlier records stand.

## D4 - `.melc` envelope mechanics
- One `CachingSystem` per `(frame_name, conduit_name)`; bundle path
  `<cache_root>/<frame_name>/<conduit_name>.melc` (caching_system.py:159-218). Created through
  `spellbook._get_or_create_caching_system(conduit_name)` only when
  `spellbook._system_caching_enabled_in_aether()` is true (spellbook_creation_system.py:450-462).
- Envelope (one `marshal` dict): `version` (format generation, CURRENT 10), `melder_version`
  (`__version__`), `python` (`sys.implementation.cache_tag`), `frame_name`, `conduit_name`,
  `spell_payloads: {spell_id: nested-marshal BYTES}` (:470-489, :129-146). Payload values stay bytes
  in memory (GC-untracked; measured rationale :56-62); `get_spell_payload` decodes fresh per call
  (:328-347); `upsert` serializes immediately (:349-369); `transfer_spell_payload_to` moves bytes
  between conduits' caches (:414-453). Per-spell payload content is the phase-11 manifest package
  or a legacy `CodeType` payload (resolution_driver.md).
- Admission at construction (:491-585): the file is read and `marshal.loads`-ed once; the envelope is
  accepted only when `version == 10`, `melder_version == __version__`, `python == cache_tag`,
  `conduit_name` matches, and every payload is `bytes`; any failure (or a corrupt file) logs a
  warning and installs an EMPTY envelope stamped with the current release/tag (:509-514). Rejection
  is wholesale: no per-spell salvage. `frame_name` is tolerated when absent (:582).
- Emit (:455-468, :587-618): under the instance lock, the in-memory dict is marshalled to
  `<bundle>.melc.tmp` and atomically `replace`d; the release stamped at creation/acceptance is
  preserved, never relabelled. Conjure emits once at conjure end on every path
  (resolution_driver.md; `_emit_conduit_cache_file_at_conjure_end`). Cleanup never deletes the file.
- Generation history (:99-144): every semantic change to payload content bumped `version`; the
  reader rejects any other generation, so ADDING a snapshot section to the envelope is a
  generation bump (11) that cold-resets every existing bundle once. Sidecar placement avoids that
  bump but needs its own admission stamp (release, tag, generation) - the same four checks.
- Classification (`_build_conjure_cache_state`, :412-487): `live_spell_ids` = pool ids with
  `resolvable and not is_existing_creation` (:451-455); `cached_spell_ids` = the envelope's keys;
  `full_hit` = live non-empty and no missing id; `mixed` = some matched and some missing; else
  `full_miss`; `disabled` when caching is off (:463-487, :490-517). The `dynamic` flag is RECORDED
  in the state dict (`dynamic_mode`, :472-473) but plays no part in the classification or the
  envelope; frame posture is not in the key today.

## D3 - what a structural-snapshot key must contain (from source)
### Per-spell tier (phases 1-3 rows) - the spell id is most of the key
The spell id is `Bind.sha256_profile(...)` (bind.py:707-716, :890-994): SHA256 over
`v4-binding` (or `v4-binding-non-resolvable`), and for a class binding: `name`, `qualname`,
`module`, sorted `bases`, sorted `mro`, sorted annotation NAMES, sorted method names and the
`init_signature` STRING (:937-947); for a callable: name, qualname, module, signature string, per
parameter `name:kind=default_repr`, repr string, type name, lambda/builtin/extension flags
(:948-964); for an instance or other object: type name, module, repr string (:965-976); then
`spell_name`, `str(spellframe)`, `binding_name`, `existence.name` and the resolved disposal method
names in order (:981-991). Docstring intent (:909-925): "constructor changes invalidate caches,
docstring edits do not". Consequences for the per-spell rows:
- Phase 1 facts are a function of the constructor signature plus annotation RESOLUTION in the
  user's module namespace (phase_01.md); the id covers the signature text and the annotation names,
  not the resolved objects. A referenced type that moves module while keeping its rendered name
  yields the same id and stale rows: RISK, needs the design story's module-fingerprint decision.
- Phase 2 rows are a pure function of phase-1 rows plus the id (phase_02.md): keyed by the id.
- Phase 3 rows depend on the POOL PROJECTION `(id, name, frame, object, type, binding name,
  resolvable, eq-safety)` of every visible spell (phase_03.md). Every value in that projection
  except object identity and eq-safety is INSIDE each spell's own id hash (name, frame string,
  binding name, resolvable, module/qualname), so the sorted set of visible spell ids determines the
  projection under name matching. Object identity is a process fact and drops out of a value key
  by design; the custom-`__eq__` frame case is the owner ruling already recorded.
- Per-spell hazard (UNKNOWN, bind-time): callable `default_repr` and instance `repr_string` feed the
  id; a default object with an address-bearing repr would make the id process-local. Where to
  look: `spell_examiner/profiles/binding_profile.py:238-265` and the profile builder that renders
  `init_signature` (`general_profile.py`). Existing-creation spells are outside the cache
  classification anyway (:454).

### Per-conduit tier (phases 4-7 rows)
- Inputs from source: the sorted VISIBLE resolvable id set (phase 3 world read; phase 5 visibility
  filter `resolvable`, phase_05.md); the OWNED id set `spellbook._spells_by_id` (phase-5 publication
  scope, phase-7 owned roots; borrowed spells arrive through links); frame posture `system_state`
  (phase 4 error-vs-warning, phase_04.md; phase 6 `empty_collection_strategy`, phase_06.md);
  `spellbook._contracted_spells` (phase 4, phase_04.md); per-spell `existence`, `spell_type`,
  `is_existing_creation`, `_owner_conduit_id` (phase 5; existence and type are inside the id, the
  owner conduit id is a runtime value); `_is_broken` per spell and phase-4 presence (phase 6);
  frame name and conduit id (phase 5/7 registrations: runtime values, not key material).
- Configuration flags read on the hydrate/emit path: `generalized_singleton_specialization_enabled`
  at first-meld hydration (resolution_driver.md); flags consumed inside phases 8-11 are deferred
  with that survey. `enforce_priority_disposal_methods` is already folded into the id (bind).
- Envelope level, already enforced: format generation, Melder release, Python cache tag,
  frame name, conduit name (D4).

### The dormant phase 2-5 signature is a content digest, not a lookup key
`capture_phase2_5_codegen_ir` (shared_compiler_executions.py:266-376) hashes the OUTPUTS of one
spell's phases 2-5: symbolic dependency tuples `(param, position, di_shape name, optional,
collection, contract_key)`, the local ordered node ids, `spell.dependencies`, `_validated_phase4`,
`_is_broken`, phase-4 issue codes, the phase-5 root spell/lineage ids, ordered node ids, socket
count, socket rows, DAG edge rows and the sorted index ids, via `hash_codegen_signature` (:341-355).
It is per SPELL and mixes per-spell (2-4) and per-conduit (5) results; it reads `_symbolic_graph`,
`_resolution_frame` and `_validation_result_phase4`, which the post-pass reset nulls
(structural_driver.md), so called after a pass it digests empty tuples. Uses: a verification stamp
for hydrated rows (rows -> recompute digest -> compare) and a change detector between conjures; it
cannot select rows before the phases run. The value-shaped ROWS it defines are the snapshot's row
schema for 2-5 (`build_phase5_socket_rows`, `build_phase5_dag_edge_rows`, :328-333).

### Hash determinism for this seam
`hash_codegen_signature` (:114-137) folds `serialize_codegen_signature_part` bytes with `|`
separators: typed one-byte tags for None/bool/int/float/str/bytes, `pickle.dumps(protocol=5)` for
dict/tuple/list/set/frozenset and for other objects, `repr` on pickle failure (:60-111). The phase
2-5 parts are tuples of primitives and strings (`contract_key` is a `(frame_key, binding_key)`
tuple, phase_02.md), so neither of driver.md's hazards (set iteration order; `repr` fallback via
`freeze_phase11_schema_value`) reaches this signature. They remain live for the phase-11 executor
signature; the determinism test (I-0) targets that path.

## Contradictions
- None against the maps on behaviour. `src_architecture.md:853-861` (generation 9 release
  admission) is current except the generation number, which the maps already carry as 10 at
  `:841-849`; the "Creation Cache Compatibility" diagram (:2242-2255) matches `:491-585`.
- `_build_conjure_cache_state` docstring says it "reads dynamic/automatic posture from the caller"
  (:428); the posture is only echoed into the state dict (:472-473), never used for the decision.

## UNKNOWN (with where to look)
- Whether `init_signature` and callable `default_repr` render object defaults by repr (process-local
  ids): `spell_examiner/profiles/general_profile.py`, `binding_profile.py:238-265`.
- `spellbook._get_or_create_caching_system` and `_system_caching_enabled_in_aether` bodies (cache
  policy source; `aether_configuration.py`): read when the snapshot's enable flag is designed.
- Which configuration flags phases 8-11 read (deferred survey).
- Whether the crystallizer restore path conjures through the same classification (it calls the
  public `conjure`, architecture "Persistence & Restore"; not read here).

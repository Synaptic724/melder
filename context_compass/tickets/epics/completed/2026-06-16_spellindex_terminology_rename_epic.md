# EPIC — SpellIndex Terminology Rename (lineage vocabulary → index vocabulary)

- Completed: 2026-07-11T19:10:00Z
- Summary: Wrapper epic for the rename program; its execution task
  (2026-06-17, P1-P8, 401 sites, zero old tokens) closed on inheritance
  2026-07-12 with confirmation via the owner's 9702 full-tree greens.
  Closed on owner-directed general_0 cleanup; nothing of this epic
  remains unexecuted (the Tier-2 residual is recorded on the closed
  tier2 task, not here).
- id: 2026-06-16_spellindex_terminology_rename_epic
- created_at: 2026-06-16T23:21:15Z
- owner: cowork / general_0 (inherited + closed by melder_0)
- status: closed (owner-directed cleanup 2026-07-11)
- mode: implementation (mechanical, behavior-preserving)
- relates_to:
  - tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md (the BUILD epic — blocked on this)
  - tickets/tasks/2026-06-12_spell_index_lineage_separation_map_task.md (the map)
- sequencing: **RENAME FIRST.** This epic lands and the full unit tree goes green
  BEFORE any `_apply_*` seam work in the genuine-index-operations epic. Clean names
  first so the lineage vocabulary cannot creep back into the new code.

---

## 1. Goal

Replace the lineage-era vocabulary on `SpellIndex` (and the frame registry that
indexes it) with index vocabulary, everywhere, as a **single behavior-preserving
mechanical rename**. After this epic, the word "version" no longer appears in the
`SpellIndex` public surface; an index has a **selected spell**, it **contains
spells**, and you ask whether it **has a spell**.

The names encode the bug. While the type said `.current` / `get_all_versions` /
`has_version`, every consumer was free to think "current version of a lineage."
The rename makes the model honest: an index selects one of its member spells.

## 2. Non-goals (do NOT do these here)

- **No behavior change.** This is a pure vocabulary swap. Same control flow, same
  data, same locks, same hot-path read semantics on the selected-spell-id property.
  The full unit tree must be green with zero logic edits.
- **No seam implementation.** `_apply_notch` / `_apply_add_to_index` /
  `_apply_remove_from_index` stay as they are (NotImplementedError). They get built
  in the genuine-index-operations epic, AFTER this lands, using the new names.
- **No model reconciliation.** Whether the new `_members` store and the renamed
  `_versions` field collapse into one is a BUILD-phase decision (flagged in §8),
  not a rename decision. Here we only rename `_versions` → `_spells_in_index`.
- **No Tier-2 sweep without sign-off** (see §6). The adjacent spellbook/conduit
  "version" vocabulary is a separate, decision-gated batch.

## 3. Locked mapping — Tier 1 (the user-named surface)

These are the names the user explicitly called for. They are LOCKED.

### 3a. SpellIndex public API
| old | new | kind |
| --- | --- | --- |
| `current` (property) | `selected_spell_id` | property — the selected member's SHA id |
| `get_all_versions()` | `spells_in_index()` | method — the member spells |
| `has_version(...)` | `has_spell(...)` | method — membership test |

### 3b. SpellIndex internals
| old | new | kind |
| --- | --- | --- |
| `_current_id` | `_selected_spell_id` | field — SHA of the selected member |
| `_versions` | `_spells_in_index` | field — member/history set (reconcile w/ `_members` in BUILD) |
| `_active_spell` | `_selected_spell` | field — the selected `Spell` object |
| `_set_active_member(...)` | `_select_member(...)` | new-model method (added in map phase) |
| `_attach_member` / `_detach_member` / `_has_member` / `_member_count` / `_member_snapshot` | keep "member" wording | "member" is index vocabulary, not lineage — **no rename** |

> `_members` stays `_members`. "Member" is correct index language. Only the
> "version"/"current"/"active" words are lineage residue.

### 3c. Frame registry (indexes SpellIndex by name → the index)
| old | new | kind |
| --- | --- | --- |
| `_version_registry` | `_selected_spell_registry` | field |
| `has_version(...)` (frame) | `has_spell(...)` | method |
| `find_and_return_spell_index(...)` | `find_index_for_spell(...)` | method |
| `refresh_version_registry(...)` | `refresh_selected_spell_registry(...)` | method (verify it still exists; grep now returns 0) |
| `_check_for_spell(...)` | **keep name**, update the version-registry references inside its body | method |

## 4. Why the property is the hard part

`.current` is a *generic* attribute name. Other objects in the tree expose
`.current` too, so a blind `s/.current/selected_spell_id/` is WRONG. The rename of
the property and its readers must be **type-aware** — only rewrite `.current`
accesses whose receiver is a `SpellIndex` (or a `spell.spell_index`). The
uniquely-named symbols (`get_all_versions`, `has_version`, `_version_registry`,
`find_and_return_spell_index`) are safe token renames because nothing else owns
those names.

## 5. Target inventory (measured 2026-06-16)

Counts are matches, not unique sites; treat as effort signal.

### Tier 1 — in scope, locked
| symbol | src | tests | notes |
| --- | --- | --- | --- |
| `.current` on SpellIndex (`spell_index.current`, `.spell_index.current`, `SpellIndex.current`) | ~138 | ~242 | **dominant cost**; type-aware codemod required |
| `get_all_versions` | 7 (+1 def) | 35 | unique name → safe token rename |
| `has_version` | 14 (+1 def) | 67 | unique name → safe token rename |
| `_current_id` | 16 (all in spell_index.py) | — | private field |
| `_versions` (SpellIndex field) | 7 internal + 9 external | (scoped) | raw token inflated by `_contracted_versions`/`_spell_versions` — MUST scope |
| `_active_spell` (SpellIndex field) | 10 internal + 3 external | (scoped) | raw token inflated by `get_active_spellspace` — MUST scope |
| `_version_registry` (frame) | 16 | — | field |
| `find_and_return_spell_index` (frame) | 2 | — | method |
| docstrings: "version" in spell_index.py | 43 | — | manual prose rewrite |

Rough Tier-1 magnitude: **~400 edited sites** (the `.current` property dominates;
everything else is ~250 combined including tests).

### Tier 2 — adjacent lineage vocabulary, DECISION-GATED (do not touch without sign-off)
The lineage era left "version" naming across the spellbook/conduit layer. These are
NOT in the user's named set and have a wider blast radius. Recommend a follow-on
consistency batch, decided per-symbol:
| symbol | src | likely intent |
| --- | --- | --- |
| `current_spell_id` (dev-ops / SpellSystemStates) | 62 | → `selected_spell_id` for consistency |
| `_spell_versions` (spellbook pool) | 18 | the {sha → SpellIndex} pool — "spells_by_id"-style |
| `_contracted_versions` / `contracted_versions` | 25 / 4 | contracted-spell pools |
| `lineage_to_versions` | 6 | **explicit lineage word** — strong rename candidate |
| `visible_versions` | 5 | |
| `_reindex_conduit_versions` | 5 | |
| `_get_all_spell_versions` / `_refresh_*_spell_versions` | ~7 | |

## 6. Codemod strategy

1. **Type-aware pass for `.current` → `selected_spell_id`.** Use a libcst/bowler
   (or ast-grep with manual review) codemod that rewrites attribute access only
   when the receiver resolves to a `SpellIndex`. Practical receiver patterns to
   target: `*.spell_index.current`, `<known SpellIndex var>.current`,
   `SpellIndex(...).current`. Everything else with `.current` is reviewed by hand,
   NOT auto-rewritten. Land the property def + `_current_id` field in the same pass.
2. **Safe token renames** for the uniquely-named symbols (`get_all_versions`,
   `has_version`, `_version_registry`, `find_and_return_spell_index`,
   `refresh_version_registry`). Whole-word, all files (src + tests).
3. **Scoped field renames** for `_versions` and `_active_spell`: restrict to
   `self._versions` / `self._active_spell` inside `spell_index.py`, plus the
   verified external receivers (`<spell_index_expr>._versions`). Explicitly EXCLUDE
   `_contracted_versions`, `_spell_versions`, `get_active_spellspace`, etc.
4. **Docstring/comment prose pass** in `spell_index.py` (43 "version" hits) and any
   touched method docstrings — "current version" → "selected spell", "all versions"
   → "spells in the index", "has version" → "has spell".
5. Re-align the map-phase additions (`_active_spell` → `_selected_spell`,
   `_set_active_member` → `_select_member`) in the same pass so the new model code
   speaks the new vocabulary from the start.

## 7. Execution order (batches, each ends green)

1. **B1 — frame registry** (`_version_registry`, `has_version`, `find_and_return_spell_index`, `refresh_*`): small, self-contained, ~30 sites. Run frame unit tests.
2. **B2 — SpellIndex methods** (`get_all_versions` → `spells_in_index`, `has_version` → `has_spell`) + their src + test callers: ~120 sites. Run bind/spellbook tests.
3. **B3 — SpellIndex internals** (`_current_id`, `_versions`, `_active_spell`, map-phase method names) scoped to spell_index.py + verified receivers.
4. **B4 — the property** (`current` → `selected_spell_id`): the big type-aware pass + ~380 readers (src + tests). Run the FULL tree.
5. **B5 — docstring/prose pass.**
6. **B6 — full unit tree green** in the 3.14t venv; diff review.

Tier-2 is a separate epic/story opened only after B6 + user sign-off.

## 8. Open reconciliation flagged to BUILD phase (not done here)
- `_versions` (renamed `_spells_in_index`) vs the new `_members` store: do we keep
  both, or is `_members` the single source of truth and `_spells_in_index()` just
  reads it? Decide when implementing the seams. Rename leaves both in place.
- Whether `spells_in_index()` returns Spell objects or ids (today `get_all_versions`
  returns the `_versions` SHA set). Preserve current return type during rename;
  revisit in BUILD if the seam needs objects.

## 9. Risk register
- **R1 — `.current` over-rewrite.** Generic name; a blind replace corrupts unrelated
  `.current` users. Mitigation: type-aware codemod + manual review of every
  non-`spell_index` `.current` hit. (HIGH)
- **R2 — hot-path read.** `selected_spell_id` replaces a deliberately lock-free hot
  read. The rename must preserve the exact read semantics (no added lock, no
  property side-effects). (HIGH — behavior-preserving check)
- **R3 — test surface (~340 hits).** Tests encode the old vocabulary heavily.
  Mitigation: rename tests in the same batch as their target so the tree never goes
  red between batches. (MED)
- **R4 — scoped-field false positives** (`_versions`/`_active_spell`). Mitigation:
  the exclusion list in §6.3; grep-verify zero unrelated rewrites per batch. (MED)
- **R5 — concurrent lanes.** compiler_strategy_0 / hope_0 are active; a 400-site
  rename will collide. Mitigation: land in tight batches, announce on the boards,
  rebase between batches. (MED)

## 10. Validation (definition of done)
- Full unit tree green in the 3.14t (no-GIL) venv after B6, with **zero logic
  changes** in the diff (rename-only diff review).
- `grep -rE "\b(get_all_versions|has_version|_version_registry|find_and_return_spell_index)\b" src tests` → 0.
- No `SpellIndex.current` / `.spell_index.current` remain; `selected_spell_id`
  everywhere instead.
- `py_compile` clean; `spell_index.py` line count sane (no truncation).
- The genuine-index-operations epic's seams still raise NotImplementedError
  (untouched) but now reference the new names in their signatures/docstrings.

## 11. Phased execution plan (no backward compat — user-directed 2026-06-17)

Execution ticket: `tickets/tasks/2026-06-17_spellindex_terminology_rename_execution_task.md`
Divide-and-conquer, easiest -> hardest, ONE phase at a time. Each phase renames
SOURCE + TESTS together (tree never goes red between phases) and ends with
`py_compile` + a grep proving zero surviving old-token references. NO aliases, NO
shims, NO deprecation paths — clean rename (user authority overrides the default
public-API-compat guardrail for this work).

- P1 — `find_and_return_spell_index` -> `find_index_for_spell` (2 src files / 3 test files). EASIEST.
- P2 — `_version_registry` -> `_selected_spell_registry` (2 src files / 2 test files; `refresh_version_registry` already gone).
- P3 — `get_all_versions` -> `spells_in_index` (3 src / 6 test files; unique name).
- P4 — `has_version` -> `has_spell` (verify the 10 src files are SpellIndex/frame first; 15 src / 15 test files).
- P5 — internals `_current_id`/`_versions`/`_active_spell`/`_set_active_member` (scoped; exclude `_spell_versions`/`_contracted_versions`/`_active_spellspace`).
- P6 — property `current` -> `selected_spell_id` (type-aware; SpellIndex receivers only; ~138 src + 87 test; leave the ~155 non-SpellIndex test `.current` alone). HARDEST.
- P7 — docstrings/comments/prose + `system_docs` sync (`src_architecture.md`/`src_components.md`/`readable_src_graph.json` reference the old names).
- P8 — final verification: grep-clean whole tree + `py_compile` all touched + rename-only diff review + request full unit tree run in the user's 3.14t venv (report "Not run" until the user runs it).

Tier-2 adjacent vocabulary (`_spell_versions`, `_contracted_versions`, `current_spell_id`,
`lineage_to_versions`, ...) stays OUT of this pass and is surfaced to the user for a
separate decision at close (per §5 Tier-2).

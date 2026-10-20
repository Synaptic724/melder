"""Land S1's system documents (melder_1, 0.2.8263; STORY-2026-10-17-staged_version_releases_active_signature):
src_architecture (an operational invariant, a fixed failure mode, the spellbook.py code-map extent and note, a
handoff entry), src_components (Spellbook Core's invariant and failure, the code-map extent, a handoff entry),
tests_components (the cluster's Protects bullet and key file, a code-map record, the information source, the
component count, a handoff entry) and tests_architecture (the component inventory, a handoff entry). Every anchor
found once; LF; new lines within 120 characters. Usage (repository root): land_s1_docs.py --check|--apply
"""
import datetime
import pathlib
import sys

DOCS = pathlib.Path("context_compass/system_docs")
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
TEST = "tests/component/melder/spellbook/test_spellbook_component_staged_version_keeps_active_signature.py"
TEST_LOC = len(pathlib.Path(TEST).read_bytes().decode("utf-8").splitlines())
SB_LOC = len(pathlib.Path("src/melder/aether/spellbook/spellbook.py").read_bytes().decode("utf-8").splitlines())

ARCH_INVARIANT = """- Staging, moving or disposing a parked version keeps every other spell's binding signature (2026-10-19,
  0.2.8263; STORY-2026-10-17-staged_version_releases_active_signature, on the owner's word, chat 2026-10-19: "try
  doing a few small ones"): `Spellbook._destroy_spell_index` destroys an index a PARKED member just left empty - the
  index Bind mints for every `bind_inactive` (folded off by `_apply_add_to_index`), a source index an index move
  emptied, or the index a lone parked version is disposed out of (`_dispose_spell`) - and touches no other spell's
  signature: the Book route `_lookup_spells[key]` goes only when it routes the key to that index, and the frame
  claim is released by the departing member's spell_id (`release_lookup_by_spell_id`, as `cleanup_and_remove_spell`
  releases), a no-op when it holds none, as a parked version claims no signature. Both callers pass the departing
  member's spell_id. Until 0.2.8263 the seam popped the route and released the claim by key, whoever held them: a
  parked member shares its key with the active version it was staged beside, or with an active spell of another
  Book of the frame, so that version lost its claim and route while it still served. Restores and grafts stage
  through `bind_inactive` and keep the active version's signature with it. Not changed: the notch's own signature
  handling (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); staging stays open to any key (the
  owner, 2026-10-17). Locks: the route check stays under the Book lock the pop took; the release is the frame
  container's leaf call, by spell_id instead of by key; no lock or lock-order edge is added.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._destroy_spell_index`,
  `Spellbook._apply_add_to_index`, `Spellbook._dispose_spell`, `Spellbook.bind_inactive`,
  `Spellbook.cleanup_and_remove_spell` and
  `src/melder/aether/aetheric_frame/lookup_container.py:LookupContainer.release_by_spell_id`.
"""
ARCH_FAILURE = """- Fixed in 0.2.8263: staging a version keyed like the active one no longer takes the active version's binding
  signature. After `bind_inactive` (before or after conjure), an `add_to_spell_index` back, or a `cleanup_spell` of
  a parked version alone in its index, the active version lost its frame claim and its Book route: a meld by address
  raised KeyError "[MELD] No spell found for frame='<frame>', binding='<binding>'.", `find_spell_index` raised
  RuntimeError "Spell not found in the spellbook.", and another Book of the frame could bind the signature while
  the version still served; staging in one Book under a key another Book's active spell held released that
  spell's claim. Each now keeps its claim and route.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._destroy_spell_index`.
"""
ARCH_HANDOFF = """2026-10-19 staging keeps the active signature (0.2.8263; STORY-2026-10-17-staged_version_releases_active_signature,
on the owner's word "try doing a few small ones"): `_destroy_spell_index` drops a Book route only when it routes the
key to the destroyed index and releases only the departing member's frame claim, by spell_id, so staging, an index
move back and a lone parked disposal keep every other spell's signature. A new operational invariant, a fixed failure
mode and the code map (spellbook.py remeasured) carry it; the component map carries the per-component contract.
Numeric citations into spellbook.py past the edit were remapped line by line.

"""
COMP_INVARIANT = """- Destroying an index a parked member left empty touches no other spell's binding signature (0.2.8263;
  STORY-2026-10-17-staged_version_releases_active_signature): `_destroy_spell_index(spell_index, *, spell_id,
  binding_key, owner_conduit_id)` pops `_lookup_spells[binding_key]` only when it is `spell_index` and releases
  the frame claim by the departing member's `spell_id` (`release_lookup_by_spell_id`; a no-op for a parked
  version, which claims none), never by key; `_apply_add_to_index` (every `bind_inactive` folds off the index Bind
  minted) and the parked branch of `_dispose_spell` pass the departing member's spell_id.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._destroy_spell_index`,
  `Spellbook._apply_add_to_index` and `Spellbook._dispose_spell`.
"""
COMP_FAILURE = """- Fixed in 0.2.8263: `bind_inactive` keyed like the active version, an `add_to_spell_index` that empties its
  source, and `cleanup_spell` of a lone parked version no longer release the active version's claim and route (a
  meld by address raised KeyError "[MELD] No spell found ...", `find_spell_index` raised "Spell not found in the
  spellbook.", and another Book could bind the signature).
"""
COMP_HANDOFF = """2026-10-19 staging keeps the active signature (0.2.8263; STORY-2026-10-17-staged_version_releases_active_signature):
Spellbook Core gains an invariant (`_destroy_spell_index` drops only its own route and releases only the departing
member's claim, by spell_id) and a fixed failure mode; the code map's spellbook.py extent is remeasured. Numeric
citations into spellbook.py past the edit were remapped line by line.

"""
TC_PROTECTS = """- staging keeps the active signature (0.2.8263;
  `test_spellbook_component_staged_version_keeps_active_signature.py`, 6 tests): `bind_inactive` keyed like the
  active version, after conjure and before it, an index move back, a lone parked `cleanup_spell` and a staging
  under another Book's key leave the active spell's frame claim, Book route and address melds in place and the
  signature refused to another Book; a version staged under its own key claims nothing
"""
TC_RECORD = f"""- path: `{TEST}`
  start_line: 1
  end_line: {TEST_LOC}
  loc: {TEST_LOC}
  verified_at: {NOW}
  note: staging, an index move back and a lone parked disposal keep the active spell's binding signature
    (0.2.8263).
"""
TC_HANDOFF = """2026-10-19 staging keeps the active signature (0.2.8263; STORY-2026-10-17-staged_version_releases_active_signature):
the Spellbook Runtime And Binding Component Cluster gains
`test_spellbook_component_staged_version_keeps_active_signature.py` (6 tests: staging after and before conjure, an
index move back, a lone parked cleanup, another Book's key, a version staged under its own key), a key file with a
code-map record. Counts are recounted from disk (component 169 of 171; 861 test modules in the three tiers); the
core key-file union is 279 paths.

"""
TA_HANDOFF = """2026-10-19 staging keeps the active signature (0.2.8263): the inventory is recounted from disk (component 171
`.py`, 169 of them `test_*.py`; 861 test modules in the three tiers) - the lane adds one component module (staging,
an index move back and a lone parked disposal keep the active spell's signature), catalogued in `tests_components`.
No tier, conftest, declared marker or shared support module changes, and no extent in this map moves.

"""
EDITS = {
    "src_architecture.md": [
        ("\n## Operational Invariants\n- A notch either stands", "\n## Operational Invariants\n" + ARCH_INVARIANT
         + "- A notch either stands"),
        ("## Failure Modes and Error Paths\n", "## Failure Modes and Error Paths\n" + ARCH_FAILURE),
        ("  end_line: 8344\n  loc: 8344\n  verified_at: 2026-10-19T13:16:16Z\n  note: Spellbook core and conjure",
         f"  end_line: {SB_LOC}\n  loc: {SB_LOC}\n  verified_at: {NOW}\n  note: Spellbook core and conjure"),
        ("    `_apply_notch` no longer journals (0.2.8262).\n",
         "    `_apply_notch` no longer journals (0.2.8262). `_destroy_spell_index` drops a route only when it routes its\n"
         "    key to the destroyed index and releases only the departing member's claim, by spell_id (0.2.8263).\n"),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + ARCH_HANDOFF),
    ],
    "src_components.md": [
        ("- Existing-object spells are registered into Creations on conjure/bind.\n",
         "- Existing-object spells are registered into Creations on conjure/bind.\n" + COMP_INVARIANT),
        ("- `SpellbookValidationError` when Phase 1-4 produces broken spells.\n",
         "- `SpellbookValidationError` when Phase 1-4 produces broken spells.\n" + COMP_FAILURE),
        ("  end_line: 8344\n  loc: 8344\n  verified_at: 2026-10-19T13:16:16Z\n- path: `src/melder/aether/spellbook/spellbinder.py`",
         f"  end_line: {SB_LOC}\n  loc: {SB_LOC}\n  verified_at: {NOW}\n- path: `src/melder/aether/spellbook/spellbinder.py`"),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + COMP_HANDOFF),
    ],
    "tests_components.md": [
        ("  disposal, and a raising hook disposes nothing, clears the in-flight mark and lets a retry complete\n",
         "  disposal, and a raising hook disposes nothing, clears the in-flight mark and lets a retry complete\n"
         + TC_PROTECTS),
        ("- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py` (2026-10-19)\n",
         "- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py` (2026-10-19)\n"
         f"- `{TEST}` (2026-10-19)\n"),
        ("    refusal; a raising hook disposes nothing and a retry completes (0.2.8261).\n",
         "    refusal; a raising hook disposes nothing and a retry completes (0.2.8261).\n" + TC_RECORD),
        ("- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py`\n",
         "- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py`\n"
         f"- `{TEST}`\n"),
        ("- 168 `test_*.py` modules among 170 `.py` files (recounted 2026-10-19)\n",
         "- 169 `test_*.py` modules among 171 `.py` files (recounted 2026-10-19)\n"),
        ("- Updated: 2026-10-19T13:16:16Z\n", f"- Updated: {NOW}\n"),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + TC_HANDOFF),
    ],
    "tests_architecture.md": [
        ("- `component/`: 170 `.py` files, 168 of them `test_*.py` (143, 81)\n",
         "- `component/`: 171 `.py` files, 169 of them `test_*.py` (143, 81)\n"),
        ("the three tiers' 860 `test_*.py`", "the three tiers' 861 `test_*.py`"),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + TA_HANDOFF),
    ],
}


def main() -> None:
    """Apply every edit in memory, check it, write with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    out = {}
    for name, edits in EDITS.items():
        path = DOCS / name
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in " + name)
        text = raw.decode("utf-8")
        for old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("%s: anchor found %d times: %r" % (name, text.count(old), old[:70]))
            for line in new.split("\n"):
                if len(line) > 120 and line not in old:
                    raise SystemExit("%s: line over 120: %s" % (name, line))
            text = text.replace(old, new)
        out[path] = text
        print(name, "lines:", text.count("\n"))
    print("spellbook.py loc", SB_LOC, "test loc", TEST_LOC, "ts", NOW)
    if sys.argv[1] == "--apply":
        for path, text in out.items():
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch " + str(path))
        print("applied")


main()

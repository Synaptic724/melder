"""melder_2 P4 apply script: SpellSpace.meld serves warm id melds from the spellspace door's fast-door entry.

usage: python apply_p4.py --root <repo root> [--check]
Anchored, count-checked, line-wise edits; every untouched line keeps its own line ending.
"""
import argparse, pathlib, sys

SPACE_DOC_OLD = """        Call shape:
            Positional strings are human SpellNames. Machine callers use
            keyword-only `spell_id=...`, which is forwarded positionally to the
            spellspace door's existing ID fast lane.

        Contract:
            - Delegates resolution and lifecycle behavior to the shared
              conduit meld runtime through its spellspace front door.
            - Keeps human `spell` and machine `spell_id` identities mutually
              exclusive.
            - Propagates runtime failures from the meld pipeline unchanged.
"""
SPACE_DOC_NEW = """        Call shape:
            Positional strings are human SpellNames. Machine callers use
            keyword-only `spell_id=...`. A warm id meld is served here from the
            spellspace door's fast-door entry; any other id meld is forwarded
            positionally to the door's existing ID fast lane.

        Contract:
            - Delegates resolution and lifecycle behavior to the shared
              conduit meld runtime through its spellspace front door.
            - Keeps human `spell` and machine `spell_id` identities mutually
              exclusive.
            - Warm id lane (2026-09-26): a `spell_id=...` meld with no
              `spell`, `spellframe` or `binding_name` reads the door's
              fast-door entry and applies the same guard ladder and arms as
              `SpellSpaceMeld.meld` (plain, non-empty dict override, bound
              existing object). A hit returns without entering the door; a miss
              or any failed guard continues in the door, so results, errors and
              the cache-emit check are identical to calling the door.
            - Propagates runtime failures from the meld pipeline unchanged.
"""
SPACE_BODY_OLD = """                Optional positional or keyword override payload.
        \"\"\"
        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")
"""
SPACE_BODY_NEW = """                Optional positional or keyword override payload.
        \"\"\"
        # Warm id lane (2026-09-26): the dominant scoped call - `spell_id=...` alone - reads the
        # spellspace door's fast-door entry here, saving the door frame and its keyword marshaling on
        # a hit. The guard ladder and both arms mirror `SpellSpaceMeld.meld` and `Conduit.meld`
        # exactly (`Meld._fast_meld_doors` lists every reader); only guard reads sit inside the
        # AttributeError try, so an executor's own AttributeError is never swallowed. A miss continues
        # in the door's positional id lane; every other call shape keeps the path below.
        if (
            type(spell_id) is str
            and spell is None
            and spellframe is None
            and binding_name is None
        ):
            meld_door = self._meld
            fast_entry = meld_door._fast_meld_doors.get(spell_id)
            if fast_entry is not None:
                (
                    door_spell,
                    captured_context,
                    captured_epoch,
                    existing_object_entry,
                ) = fast_entry
                fast_executor = None
                try:
                    if (
                        not meld_door._meld_hooks
                        and door_spell._door_epoch == captured_epoch
                        and door_spell._creation_context is captured_context
                        and not meld_door._spellbook._spellbook_validation_required
                    ):
                        # Slots are read per hit: hydration swaps them in place.
                        if override is None:
                            fast_executor = captured_context._no_overrides_instance_executor
                        elif type(override) is dict and override:
                            fast_executor = captured_context._overrides_executor
                except AttributeError:
                    # Cleaned spell/context: guard miss; the door decides.
                    fast_executor = None
                if fast_executor is not None:
                    if override is None:
                        if existing_object_entry:
                            # Existing object: the door returns this same bound slot.
                            instance = door_spell.user_created_object
                        else:
                            instance = fast_executor(meld_door)
                    else:
                        instance = fast_executor(meld_door, override)[0]
                    spellbook = meld_door._spellbook
                    if spellbook._cache_emit_required:
                        spellbook._emit_cache_file_if_required()
                    return instance
            if override is None:
                return meld_door.meld(spell_id)
            return meld_door.meld(spell_id, spell_override=override)
        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")
"""
MELD_DOC_OLD = """      Three readers apply one guard ladder and both arms and must stay
      identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld` and
      `Conduit.meld` (automatic id melds). Cardinality is bounded by
"""
MELD_DOC_NEW = """      Four readers apply one guard ladder and both arms and must stay
      identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld`,
      `Conduit.meld` (automatic id melds) and `SpellSpace.meld` (id melds,
      2026-09-26). Cardinality is bounded by
"""
EDITS = {
    "src/melder/aether/conduit/spell_space/spell_space.py": [
        (SPACE_DOC_OLD, SPACE_DOC_NEW, 1),
        (SPACE_BODY_OLD, SPACE_BODY_NEW, 1),
    ],
    "src/melder/aether/conduit/meld/meld.py": [
        (MELD_DOC_OLD, MELD_DOC_NEW, 1),
    ],
}


def _apply_edits(raw: bytes, edits, rel: str) -> bytes:
    """Apply anchored edits line-wise, keeping every untouched line's own ending (files may mix CRLF and LF)."""
    lines = raw.decode("utf-8").splitlines(keepends=True)
    for old, new, count in edits:
        norm = [line.rstrip("\r\n") for line in lines]
        old_lines = old.split("\n")[:-1]
        new_lines = new.split("\n")[:-1]
        hits = [i for i in range(len(norm) - len(old_lines) + 1) if norm[i:i + len(old_lines)] == old_lines]
        if len(hits) != count:
            raise SystemExit(f"ANCHOR MISMATCH {rel}: expected {count}, found {len(hits)}: {old[:70]!r}")
        for i in reversed(hits):
            ending = "\r\n" if lines[i].endswith("\r\n") else "\n"
            lines[i:i + len(old_lines)] = [line + ending for line in new_lines]
    return "".join(lines).encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    plans = [(root / rel, _apply_edits((root / rel).read_bytes(), edits, rel)) for rel, edits in EDITS.items()]
    print(f"OK: {len(plans)} files" + (" (check only)" if a.check else ""))
    if not a.check:
        for path, data in plans:
            path.write_bytes(data)
        print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

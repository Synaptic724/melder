"""Fix the SpellSpace door's live-creation probe: `many` is read from the space's own store.

Edits src/melder/aether/conduit/meld/spellspace_meld.py (CRLF): the class contract, the probe's contract and
its `many` branch. Run from the repository root; each anchor must match exactly once.
"""
import pathlib

PATH = pathlib.Path("src/melder/aether/conduit/meld/spellspace_meld.py")

EDITS = [
    (
        "        - Routes `unique_per_spell_space` work into spellspace-local storage.\n",
        "        - Routes `unique_per_spell_space` work into spellspace-local storage.\n"
        "        - Tracks disposal-bearing `many` in spellspace-local storage too (the\n"
        "          innermost scope); `purge` and the live-creation probe read `many`\n"
        "          only there.\n",
    ),
    (
        "        Contract:\n"
        "            - `unique_per_spell_space` reads from spellspace-local storage.\n"
        "            - `unique_per_conduit` and `many` read from owner-conduit storage.\n"
        "            - broader shared existences read from spell-owned\n"
        "              `owner_creations`.\n",
        "        Contract:\n"
        "            - `unique_per_spell_space` and `many` read from spellspace-local\n"
        "              storage. A disposal-bearing `many` melded through this door is\n"
        "              registered in the space's store (the innermost scope), the only\n"
        "              store `purge` retires it from; a `many` without disposal methods\n"
        "              is never tracked and reports 0. Before the 2026-09-28 fix `many`\n"
        "              was read from the owner conduit's store, so what the space held\n"
        "              was missed and a `many` melded through the conduit was counted.\n"
        "            - `unique_per_conduit` reads from owner-conduit storage.\n"
        "            - `unique` reads the Spell owner's `owner_creations`;\n"
        "              `unique_per_conduit_lineage` the owner conduit's lineage-root\n"
        "              store; `unique_per_conduit_cluster` the elected leader's store,\n"
        "              and is not live while no leader is elected.\n",
    ),
    (
        "        if existence is Existence.many:\n"
        "            creation_bucket = self._conduit_creations.get_creation(spell_id)\n"
        "            creation_count = (\n"
        "                len(creation_bucket)\n"
        "                if isinstance(creation_bucket, list)\n"
        "                else 0\n"
        "            )\n"
        "            return {\n"
        "                \"is_live\": creation_count > 0,\n"
        "                \"spell_id\": spell_id,\n"
        "                \"spell_name\": spell.spell_name,\n"
        "                \"existence\": existence.name,\n"
        "                \"query_conduit_id\": query_conduit_id,\n"
        "                \"storage_scope_kind\": \"owner_conduit_many\",\n"
        "                \"storage_owner_conduit_id\": self._owner_conduit_id,\n"
        "                \"active_spellspace_id\": None,\n"
        "                \"creation_count\": creation_count,\n"
        "            }\n",
        "        if existence is Existence.many:\n"
        "            # Disposal-bearing `many` melded through this door lives in the\n"
        "            # space's store (every emitter picks the innermost scope), and\n"
        "            # `purge` retires it from there only, so the probe reads it there.\n"
        "            creation_bucket = self._spellspace_creations.get_creation(spell_id)\n"
        "            creation_count = (\n"
        "                len(creation_bucket)\n"
        "                if isinstance(creation_bucket, list)\n"
        "                else 0\n"
        "            )\n"
        "            return {\n"
        "                \"is_live\": creation_count > 0,\n"
        "                \"spell_id\": spell_id,\n"
        "                \"spell_name\": spell.spell_name,\n"
        "                \"existence\": existence.name,\n"
        "                \"query_conduit_id\": query_conduit_id,\n"
        "                \"storage_scope_kind\": \"spellspace_many\",\n"
        "                \"storage_owner_conduit_id\": self._owner_conduit_id,\n"
        "                \"active_spellspace_id\": self._spellspace_id,\n"
        "                \"creation_count\": creation_count,\n"
        "            }\n",
    ),
]

raw = PATH.read_bytes().decode("utf-8")
assert raw.count("\r\n") == raw.count("\n"), "expected a CRLF-only file"
text = raw.replace("\r\n", "\n")
for old, new in EDITS:
    assert text.count(old) == 1, (old[:60], text.count(old))
    text = text.replace(old, new)
PATH.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
print("probe fixed")

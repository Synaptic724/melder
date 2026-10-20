"""melder_0, 2026-10-18: S2's creation-cache edits (component_patch_creation_cache.md): the structural key and the
world stamp carry each spell's binding hash (payload format 2), cache generation 23 "binding_manifest_keys", and the
docstrings and comments that trusted the spell_id to cover the binding."""
from apply_common import Applier

SNAPSHOT = "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py"
CACHING = "src/melder/utilities/caching_system/caching_system.py"
CREATION = "src/melder/aether/spellbook/spellbook_creation_system.py"
GENERALIZED = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/"
NO_OVERRIDES = GENERALIZED + "compilers/generalized_manifest_no_overrides_compiler.py"
MANIFEST = GENERALIZED + "manifest/generalized_manifest.py"


def snapshot(applier: Applier) -> None:
    """The key, the stamp and their contracts (structural_snapshot.py, CRLF in the working tree)."""
    applier.edit(SNAPSHOT, [
        ("        - Payload schema (`PAYLOAD_FORMAT` 1):\n"
         "          ``{\"key\": {\"format\", \"spell_id\", \"annotation_refs\"},\n",
         "        - Payload schema (`PAYLOAD_FORMAT` 2):\n"
         "          ``{\"key\": {\"format\", \"spell_id\", \"binding_hash\", \"annotation_refs\"},\n"),
        ("        - The world stamp is a SHA-256 over the inputs phases 3-4 read from\n"
         "          the world: the sorted pool ids, the frame posture and the sorted\n"
         "          borrowed (contracted) spell ids. A payload is only meaningful for\n"
         "          the world it was captured in.\n",
         "        - The world stamp is a SHA-256 over the inputs phases 3-4 read from\n"
         "          the world: the sorted pool ids, each with its spell's binding hash,\n"
         "          the frame posture and the sorted borrowed (contracted) spell ids,\n"
         "          each with its binding hash. A payload is only meaningful for the\n"
         "          world it was captured in; a binding changed under one spell_id is\n"
         "          another world (EPIC-2026-10-18-spell_identity_is_the_code).\n"),
        ("    PAYLOAD_FORMAT: ClassVar[int] = 1\n",
         "    # Format 2 (EPIC-2026-10-18-spell_identity_is_the_code, S2): the key carries the spell's\n"
         "    # binding hash beside its spell_id, which became the code digest alone.\n"
         "    PAYLOAD_FORMAT: ClassVar[int] = 2\n"),
        ("            - ``{\"format\": PAYLOAD_FORMAT, \"spell_id\": spell.spell_id,\n"
         "              \"annotation_refs\": [...]}``; the spell id already covers the\n"
         "              spell's own signature, names, existence and resolvability, and\n"
         "              the annotation refs add the (module, qualname) of every type the\n"
         "              spell's sockets match on, so a type that moves module while\n"
         "              keeping its rendered name changes the key.\n",
         "            - ``{\"format\": PAYLOAD_FORMAT, \"spell_id\": spell.spell_id,\n"
         "              \"binding_hash\": spell.binding_hash, \"annotation_refs\": [...]}``.\n"
         "              The spell_id is the spell's code (`SpellCodeDigest`), the binding\n"
         "              hash how it is bound - address, spellframe, existence, disposal\n"
         "              order, resolvable and managed settings (`BindingManifest`) - so\n"
         "              a payload captured for one binding is never replayed for another\n"
         "              under the same spell_id. The annotation refs add the (module,\n"
         "              qualname) of every type the spell's sockets match on, so a type\n"
         "              that moves module while keeping its rendered name changes the key.\n"),
        ("            \"spell_id\": spell.spell_id,\n"
         "            \"annotation_refs\": StructuralSnapshot.annotation_refs(requirements),\n",
         "            \"spell_id\": spell.spell_id,\n"
         "            \"binding_hash\": spell.binding_hash,\n"
         "            \"annotation_refs\": StructuralSnapshot.annotation_refs(requirements),\n"),
        ("            - SHA-256 hex over three lines: the sorted ids of\n"
         "              `spellbook._spell_id_pool`, the frame posture name\n"
         "              (`system_state`, empty when no frame configuration is bound)\n"
         "              and the sorted ids of the borrowed spells in\n"
         "              `spellbook._contracted_spells`.\n",
         "            - SHA-256 hex over three lines: `pool:` and the sorted\n"
         "              `<spell_id>=<binding_hash>` entries of `spellbook._spell_id_pool`,\n"
         "              `posture:` and the frame posture name (`system_state`, empty when\n"
         "              no frame configuration is bound), and `borrowed:` and the sorted\n"
         "              `<spell_id>=<binding_hash>` entries of the borrowed spells in\n"
         "              `spellbook._contracted_spells`. With the binding hash a binding\n"
         "              changed under one spell_id is another world, for both cache\n"
         "              tiers (payload format 2, cache generation 23).\n"),
        ("        pool_ids = sorted(spellbook._spell_id_pool.keys())\n",
         "        pool_entries = sorted(\n"
         "            f\"{spell_id}={spell.binding_hash}\" for spell_id, spell in spellbook._spell_id_pool.items()\n"
         "        )\n"),
        ("        borrowed_ids: set[str] = set()\n"
         "        for by_index in spellbook._contracted_spells.values():\n"
         "            for borrowed in by_index.values():\n"
         "                borrowed_ids.add(borrowed.spell_id)\n"
         "        text = \"\\n\".join((\n"
         "            \"pool:\" + \",\".join(pool_ids),\n"
         "            \"posture:\" + posture,\n"
         "            \"borrowed:\" + \",\".join(sorted(borrowed_ids)),\n",
         "        borrowed_entries: set[str] = set()\n"
         "        for by_index in spellbook._contracted_spells.values():\n"
         "            for borrowed in by_index.values():\n"
         "                borrowed_entries.add(f\"{borrowed.spell_id}={borrowed.binding_hash}\")\n"
         "        text = \"\\n\".join((\n"
         "            \"pool:\" + \",\".join(pool_entries),\n"
         "            \"posture:\" + posture,\n"
         "            \"borrowed:\" + \",\".join(sorted(borrowed_entries)),\n"),
    ], "snapshot")


def caching(applier: Applier) -> None:
    """Generation 23 with its history comment, and the envelope contract (caching_system.py)."""
    applier.edit(CACHING, [
        ("          structural tier's world stamp (sorted pool ids, posture, borrowed\n"
         "          ids) recorded by `set_world_stamp` when the executor payloads were\n",
         "          structural tier's world stamp (the sorted pool and borrowed ids,\n"
         "          each with its spell's binding hash since generation 23, and the\n"
         "          posture) recorded by `set_world_stamp` when the executor payloads were\n"),
        ("    # records why, as the owner asked (\"you gotta notch the version for the\n"
         "    # cache because this is a bug\").\n",
         "    # records why, as the owner asked (\"you gotta notch the version for the\n"
         "    # cache because this is a bug\").\n"
         "    # Version 23 retires bundles keyed by the spell_id before it became the\n"
         "    # SHA256 of the registered object's code alone (S1 of\n"
         "    # EPIC-2026-10-18-spell_identity_is_the_code): the bind call left it and\n"
         "    # became the binding manifest, whose hash the structural key (payload\n"
         "    # format 2) and the world stamp now carry beside each spell_id (S2), so a\n"
         "    # binding changed under one spell_id misses both tiers. Every spell_id\n"
         "    # moved, and a release change already cold-starts every bundle (version 9);\n"
         "    # the bump records why.\n"),
        ("        22: \"managed_settings_leave_spell_id\",\n    })\n",
         "        22: \"managed_settings_leave_spell_id\",\n        23: \"binding_manifest_keys\",\n    })\n"),
    ], "caching")


def creation(applier: Applier) -> None:
    """`_build_conjure_cache_state`'s contract and comment (spellbook_creation_system.py, CRLF)."""
    applier.edit(CREATION, [
        ("              different stamp is the mixed path; nothing matched is the full\n"
         "              miss; an empty live set stays a full miss.\n",
         "              different stamp is the mixed path; nothing matched is the full\n"
         "              miss; an empty live set stays a full miss.\n"
         "            - The stamp carries each pool and borrowed spell's binding hash\n"
         "              beside its spell_id (generation 23,\n"
         "              EPIC-2026-10-18-spell_identity_is_the_code), so a binding\n"
         "              changed under one spell_id - its existence, disposal order,\n"
         "              address, resolvable or managed settings - is another world too.\n"),
        ("            # The executor payloads are a function of the world the structural\n"
         "            # tier already stamps (pool ids, posture, borrowed ids); a bundle\n"
         "            # staged in another world is never replayed as a full hit.\n",
         "            # The executor payloads are a function of the world the structural\n"
         "            # tier already stamps (pool and borrowed ids, each with its binding\n"
         "            # hash, and the posture); a bundle staged in another world - another\n"
         "            # binding under one spell_id included - is never replayed as a full hit.\n"),
    ], "creation")


def generalized(applier: Applier) -> None:
    """The generalized family's comment and docstring that trusted the spell fingerprint."""
    applier.edit(NO_OVERRIDES, [
        ("    # Bind-time spell truth stamped by the manifest builder; disposal facts\n"
         "    # compose into the spell fingerprint, so this can never go stale without\n"
         "    # rolling the spell version (and with it, this manifest).\n",
         "    # Bind-time spell truth stamped by the manifest builder; disposal facts\n"
         "    # compose into the spell's binding hash, which the creation cache keys on\n"
         "    # beside the spell_id, so this can never go stale without rebuilding this\n"
         "    # manifest (EPIC-2026-10-18-spell_identity_is_the_code).\n"),
    ], "no-overrides compiler")
    applier.edit(MANIFEST, [
        ("          fact, read from bind-time spell truth (which composes into the spell\n"
         "          fingerprint alongside existence) rather than trusting plan-step\n"
         "          plumbing for disposal data.\n",
         "          fact, read from bind-time spell truth (which composes into the spell's\n"
         "          binding hash alongside existence; the creation cache keys on it) rather\n"
         "          than trusting plan-step plumbing for disposal data.\n"),
    ], "generalized manifest")


def apply(applier: Applier) -> None:
    """Stage every creation-cache edit."""
    snapshot(applier)
    caching(applier)
    creation(applier)
    generalized(applier)

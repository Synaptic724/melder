"""melder_0, 2026-10-18: S1's batch for test_bind_managed_spell_options.py. The 0.2.8241 literal ids it pinned through
`Bind.sha256_profile` retire with that function (every spell_id moves once with the code digest); the settings test
asserts one spell_id, the class's code digest; the inspector test asserts the inspector answers the id bind gives;
the inspector's refusal test retires (the inspector takes only the target and checks no binding rule - bind does)."""

MANAGED = "tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py"

OLD_DOCSTRING = (
    "`managed_spell_timeout_seconds` and `managed_spell_reset_methods`. Bind normalizes them once - after the profile,\n"
    "before the fingerprint - refuses every malformed combination before a Spell exists, hands the normalized values\n"
    "to the Spell, and never hashes them: they are settings of the one spell, not part of its spell_id (owner ruling,\n"
    "2026-10-17: \"the bind call itself shouldn't impact the actual SHA256\"; 0.2.8242-0.2.8253 appended a `managed:`\n"
    "part, STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool removed it). Every other binding keeps\n"
    "its spell id byte for byte: the literal ids below were computed on 0.2.8241, before the options existed\n"
    "(context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_golden_ids_pre.txt).\n"
)
NEW_DOCSTRING = (
    "`managed_spell_timeout_seconds` and `managed_spell_reset_methods`. Bind normalizes them once, after the profile,\n"
    "refuses every malformed combination before a Spell exists, and hands the normalized values to the Spell, whose\n"
    "binding manifest records them: they are settings of the one spell, not part of its spell_id (owner ruling,\n"
    "2026-10-17: \"the bind call itself shouldn't impact the actual SHA256\"; 0.2.8242-0.2.8253 appended a `managed:`\n"
    "part, STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool removed it). The spell_id is the\n"
    "target's code (`SpellCodeDigest`, S1 of EPIC-2026-10-18-spell_identity_is_the_code): the 0.2.8241 literal ids this\n"
    "file pinned through `Bind.sha256_profile` retired with that function, since every spell_id moves once.\n"
)
OLD_SECTION_START = "# -------------------------\n# Fingerprint\n# -------------------------\n"
NEW_SECTION = (
    "# -------------------------\n# The spell_id\n# -------------------------\n\n\n"
    "def code_spell_id(target: Any) -> str:\n"
    "    \"\"\"The spell_id bind gives `target`: its code digest, from a fresh digest cleaned before returning.\"\"\"\n"
    "    digest = SpellCodeDigest()\n"
    "    try:\n"
    "        return digest.spell_id(target)\n"
    "    finally:\n"
    "        digest.cleanup()\n\n\n"
)
INSPECTOR_START = "def test_spell_id_inspector_matches_the_bind_fingerprint_for_a_managed_class() -> None:\n"
REFUSAL_START = "def test_spell_id_inspector_refuses_what_bind_refuses() -> None:\n"
NEW_TAIL = (
    "def test_spell_id_inspector_matches_the_id_bind_gives_a_managed_class(monkeypatch: pytest.MonkeyPatch) -> None:\n"
    "    \"\"\"The read-only inspector answers the id bind gives the class, whatever its managed settings: its code.\"\"\"\n"
    "    settings_variants = (\n"
    "        {},\n"
    "        {\n"
    "            \"managed_spell_mode\": \"queue\", \"managed_spell_limit\": 2, \"managed_spell_timeout_seconds\": 1.5,\n"
    "            \"managed_spell_reset_methods\": [\"reset\"],\n"
    "        },\n"
    "    )\n"
    "    bound = {\n"
    "        bind_with(monkeypatch, Existence.managed_spell_quantity, **settings).kwargs[\"spell_id\"]\n"
    "        for settings in settings_variants\n"
    "    }\n"
    "    assert bound == {Bind.spell_id_inspector(PooledTarget)}\n"
)


def tail(applier) -> None:
    """Replace the two inspector tests at the end of the file by the one that still has a contract to test."""
    text = applier._load(MANAGED)
    if text.count(INSPECTOR_START) != 1 or text.count(REFUSAL_START) != 1:
        applier.errors.append(f"TAIL in {MANAGED}: {text.count(INSPECTOR_START)} / {text.count(REFUSAL_START)}")
        return
    start = text.index(INSPECTOR_START)
    remainder = text[start:]
    if remainder.index(REFUSAL_START) < 0 or remainder.rstrip("\n").count("\ndef ") != 1:
        applier.errors.append(f"TAIL in {MANAGED}: the two inspector tests do not end the file")
        return
    applier.texts[MANAGED] = text[:start] + NEW_TAIL
    applier.counts[MANAGED] = applier.counts.get(MANAGED, 0) + 1


def apply(applier) -> None:
    """The managed-options batch."""
    applier.edit(MANAGED, [
        (OLD_DOCSTRING, NEW_DOCSTRING),
        ("import hashlib\nimport math\nfrom typing import Any, Dict, List\n", "import math\nfrom typing import Any, List\n"),
        ("from melder.aether.spellbook.bind.bind import Bind\n",
         "from melder.aether.spellbook.bind.bind import Bind\n"
         "from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest\n"),
        ("    The class profile the 0.2.8241 literal ids were computed from (module \"golden_mod\").\n",
         "    The class profile the examiner double returns (module \"golden_mod\"). It decides no spell_id: bind's id is\n"
         "    the target's code (`SpellCodeDigest`), never its profile.\n"),
        ("    \"\"\"The callable profile of the literal ids.\"\"\"\n",
         "    \"\"\"A callable profile for the examiner double (a managed function is refused).\"\"\"\n"),
        ("    \"\"\"The existing-object profile of the literal ids.\"\"\"\n",
         "    \"\"\"An existing-object profile for the examiner double (a managed object is refused).\"\"\"\n"),
        ("    \"\"\"Mode, limit, timeout and reset names (in any order) give one spell_id: the managed id with no settings.\"\"\"\n",
         "    \"\"\"Mode, limit, timeout and reset names (in any order) give one spell_id: the class's code digest.\"\"\"\n"),
        ("    assert ids == {\n"
         "        Bind.sha256_profile(golden_class_profile(), spell_name=\"PooledTarget\", existence=Existence.managed_spell_quantity)\n"
         "    }\n",
         "    assert ids == {code_spell_id(PooledTarget)}\n"),
        ("    \"\"\"The fresh SpellIndex and the Spell share the managed fingerprint.\"\"\"\n",
         "    \"\"\"The fresh SpellIndex and the Spell share the spell_id.\"\"\"\n"),
    ], "managed")
    applier.cut(MANAGED, OLD_SECTION_START, "def test_managed_settings_do_not_change_the_spell_id(", NEW_SECTION,
                "managed goldens")
    tail(applier)

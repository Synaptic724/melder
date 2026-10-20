"""melder_0, 2026-10-18: S1's batch for test_stable_spell_fingerprint.py. Its address-freedom contracts hold for the
code digest: the twins and the content differences run through `Bind.spell_id_inspector(target)` (the inspector takes
only the target now); the strategy test keeps its display-repr half (the profile's fingerprint text fields are gone);
the hand-built-profile hash test retires with `Bind.sha256_profile` (successors: the digest's cross-process and
existing-object tests)."""

FINGERPRINT = "tests/unit/melder/spellbook/bind/test_stable_spell_fingerprint.py"

OLD_MODULE_DOC = (
    "Regression contracts: bind fingerprints never depend on memory addresses.\n\n"
    "CPython's default reprs embed an object's address (`<function f at 0x...>`, `<C object at 0x...>`), which\n"
    "differs between processes. The bind fingerprint hashed those reprs (and signature text, where a default such\n"
    "as `object()` renders its address), so function, lambda, method, partial, callable-instance and default-repr\n"
    "instance spells got a new id in every process. Two content-identical objects created in one process differ\n"
    "only by address, which makes them a deterministic stand-in for \"the same object in another process\".\n"
)
NEW_MODULE_DOC = (
    "Regression contracts: a spell_id never depends on a memory address.\n\n"
    "CPython's default reprs embed an object's address (`<function f at 0x...>`, `<C object at 0x...>`), which\n"
    "differs between processes. The bind fingerprint once hashed those reprs (and signature text, where a default\n"
    "such as `object()` renders its address), so function, lambda, method, partial, callable-instance and\n"
    "default-repr instance spells got a new id in every process (fixed 2026-09-26). Since S1 of\n"
    "EPIC-2026-10-18-spell_identity_is_the_code the spell_id is the target's code (`SpellCodeDigest`): it reads an\n"
    "object by its type and data and keeps the address-free repr only where no Python-visible state exists. Two\n"
    "content-identical objects created in one process differ only by address, which makes them a deterministic\n"
    "stand-in for \"the same object in another process\".\n"
)
OLD_IMPORTS = (
    "from melder.aether.spellbook.bind.bind import Bind\n"
    "from melder.aether.spellbook.existence.existence import Existence\n"
    "from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility\n"
    "from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (\n"
    "    CallableBindingProfile,\n"
    "    CallableParameterBindingSummary,\n"
    "    InstanceBindingProfile,\n"
    "    SpellBindingKind,\n"
    ")\n"
)
NEW_IMPORTS = (
    "from melder.aether.spellbook.bind.bind import Bind\n"
    "from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility\n"
)
OLD_HELPER = (
    "def _spell_id(target: Any) -> str:\n"
    "    \"\"\"Fingerprint one candidate exactly as the binding pipeline would (unique existence).\"\"\"\n"
    "    return Bind.spell_id_inspector(target, existence=Existence.unique)\n"
)
NEW_HELPER = (
    "def _spell_id(target: Any) -> str:\n"
    "    \"\"\"The spell_id one candidate is bound under: the inspector answers what bind gives (its code digest).\"\"\"\n"
    "    return Bind.spell_id_inspector(target)\n"
)
OLD_STRATEGY = (
    "def test_strategy_keeps_display_reprs_and_adds_fingerprint_text() -> None:\n"
    "    \"\"\"\n"
    "    Purpose: Display reprs are unchanged; the fingerprint text is carried beside them.\n"
    "    Contract: repr_string/default_repr keep the address; fingerprint fields have none.\n"
    "    \"\"\"\n"
    "    strategy = BindingProfileStrategy()\n"
    "    callable_profile = strategy.build_profile(_make_with_marker)\n"
    "    instance_profile = strategy.build_profile(_Settings())\n"
    "    marker = callable_profile.parameters[0]\n\n"
    "    assert \" at 0x\" in callable_profile.repr_string\n"
    "    assert callable_profile.fingerprint_repr == f\"<function {_make_with_marker.__qualname__}>\"\n"
    "    assert \" at 0x\" in marker.default_repr\n"
    "    assert marker.default_fingerprint_repr == \"<object object>\"\n"
    "    assert \" at 0x\" in instance_profile.repr_string\n"
    "    assert \" at 0x\" not in instance_profile.fingerprint_repr\n"
)
NEW_STRATEGY = (
    "def test_strategy_keeps_display_reprs_with_their_addresses() -> None:\n"
    "    \"\"\"\n"
    "    Purpose: Display reprs are unchanged, and no profile text feeds the spell_id any more.\n"
    "    Contract: repr_string and default_repr keep the address (S1 removed the profile's fingerprint text fields;\n"
    "    the code digest reads the target itself).\n"
    "    \"\"\"\n"
    "    strategy = BindingProfileStrategy()\n"
    "    callable_profile = strategy.build_profile(_make_with_marker)\n"
    "    instance_profile = strategy.build_profile(_Settings())\n"
    "    marker = callable_profile.parameters[0]\n\n"
    "    assert \" at 0x\" in callable_profile.repr_string\n"
    "    assert \" at 0x\" in marker.default_repr\n"
    "    assert \" at 0x\" in instance_profile.repr_string\n"
)
RETIRED_START = "\n\ndef test_profiles_without_fingerprint_text_hash_address_free_display_text() -> None:\n"


def retire_tail(applier) -> None:
    """Drop the last test (hand-built profiles through `Bind.sha256_profile`), which ends the file."""
    text = applier._load(FINGERPRINT)
    if text.count(RETIRED_START) != 1:
        applier.errors.append(f"RETIRE in {FINGERPRINT}: {text.count(RETIRED_START)}")
        return
    start = text.index(RETIRED_START)
    remainder = text[start + 2:]
    if remainder.count("\ndef ") != 0 or "Bind.sha256_profile(instance(" not in remainder:
        applier.errors.append(f"RETIRE in {FINGERPRINT}: the retired test does not end the file")
        return
    applier.texts[FINGERPRINT] = text[:start] + "\n"
    applier.counts[FINGERPRINT] = applier.counts.get(FINGERPRINT, 0) + 1


def apply(applier) -> None:
    """The fingerprint-regression batch."""
    applier.edit(FINGERPRINT, [
        (OLD_MODULE_DOC, NEW_MODULE_DOC),
        (OLD_IMPORTS, NEW_IMPORTS),
        (OLD_HELPER, NEW_HELPER),
        ("    Purpose: The fingerprint helper removes CPython's \" at 0x<hex>\" fragments, nested ones included.\n",
         "    Purpose: The address-free repr (the code digest's text for an object it reads by repr) removes\n"
         "    CPython's \" at 0x<hex>\" fragments, nested ones included.\n"),
        ("    Purpose: The fingerprint text is not the truncated display text.\n",
         "    Purpose: The address-free repr is not the truncated display text.\n"),
        ("    Contract: Two distinct objects with identical fingerprint content get the same id.\n",
         "    Contract: Two distinct objects with identical code and data get the same id.\n"),
        (OLD_STRATEGY, NEW_STRATEGY),
    ], "fingerprint")
    retire_tail(applier)

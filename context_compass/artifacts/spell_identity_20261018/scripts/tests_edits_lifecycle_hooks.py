"""melder_0, 2026-10-18: S1's batch for test_bind_lifecycle_hooks.py. The hook-lifecycle case bound one class three
times under three binding names, which strict uniqueness now refuses: each registration binds a class of its own. The
native-hash case reads the expected id from the inspector given the class alone."""

HOOKS = "tests/component/melder/spellbook/test_bind_lifecycle_hooks.py"


def apply(applier) -> None:
    """The bind-lifecycle-hooks batch."""
    applier.edit(HOOKS, [
        ("from melder.aether.spellbook.existence.existence import Existence\n", ""),
        ("    try:\n"
         "        book.add_bind_hooks(**{stage: [first]})\n"
         "        book.add_bind_hooks(**{stage: [second, first]})\n"
         "        book.bind(spell=HookService, existence=\"unique\", binding_name=\"one\")\n"
         "        assert calls == [\"first\", \"second\", \"first\"]\n"
         "        book.clear_bind_hooks()\n"
         "        book.clear_bind_hooks()\n"
         "        book.bind(spell=HookService, existence=\"unique\", binding_name=\"two\")\n"
         "        assert calls == [\"first\", \"second\", \"first\"]\n"
         "        book.add_bind_hooks(**{stage: [second]})\n"
         "        book.bind(spell=HookService, existence=\"unique\", binding_name=\"three\")\n",
         "    # One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code), so each registration binds a\n"
         "    # class of its own; the binding names stay as they were.\n"
         "    class FirstTarget:\n"
         "        \"\"\"The first registration's target.\"\"\"\n\n"
         "    class SecondTarget:\n"
         "        \"\"\"The second registration's target, bound after the hooks were cleared.\"\"\"\n\n"
         "    class ThirdTarget:\n"
         "        \"\"\"The third registration's target, bound after a hook was registered again.\"\"\"\n\n"
         "    try:\n"
         "        book.add_bind_hooks(**{stage: [first]})\n"
         "        book.add_bind_hooks(**{stage: [second, first]})\n"
         "        book.bind(spell=FirstTarget, existence=\"unique\", binding_name=\"one\")\n"
         "        assert calls == [\"first\", \"second\", \"first\"]\n"
         "        book.clear_bind_hooks()\n"
         "        book.clear_bind_hooks()\n"
         "        book.bind(spell=SecondTarget, existence=\"unique\", binding_name=\"two\")\n"
         "        assert calls == [\"first\", \"second\", \"first\"]\n"
         "        book.add_bind_hooks(**{stage: [second]})\n"
         "        book.bind(spell=ThirdTarget, existence=\"unique\", binding_name=\"three\")\n"),
        ("        expected_id = Bind.spell_id_inspector(\n"
         "            HookService, spell_name=\"HookService\", existence=Existence.unique,\n"
         "        )\n",
         "        expected_id = Bind.spell_id_inspector(HookService)\n"),
    ], "lifecycle hooks")

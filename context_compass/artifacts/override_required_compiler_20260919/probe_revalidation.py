"""Inspect compiler/runtime validity around a selector-sensitive bind without changing policy."""

import sys
from pathlib import Path


def main() -> None:
    """Build a fresh real world and print the states needed to locate stale-plan admission."""
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))
    from tests.component.melder.spellbook.test_spellbook_component_override_required import (
        Consumer,
        Definition,
        Implementation,
        compiler_book,
    )

    fixture = compiler_book.__wrapped__()
    book = next(fixture)
    try:
        book._aetheric_frame_configuration.with_system_caching_enabled(False)
        book.bind(spell=Definition, binding_name="definition", existence="unique", resolvable=False)
        consumer_id = book.bind(spell=Consumer, existence="many")
        conduit = book.conjure(dynamic=True, name="probe-selector-revalidation")
        consumer = book.find_spell_by_id(consumer_id)
        states = book._spell_system_states
        print("cache", book._aetheric_frame_configuration.system_caching_enabled)
        print("watchers before", states._collection_dependents_by_spellbook)
        print("before", consumer.system_state.validity, book._spellbook_validation_required)
        provider_id = conduit.bind(
            spell=Implementation, spellframe=Definition, binding_name="runtime", existence="unique",
        )
        print("watchers after", states._collection_dependents_by_spellbook)
        print("after", consumer.system_state.validity, book._spellbook_validation_required)
        print("dependencies", consumer.dependencies, "provider", provider_id)
        print("required", consumer.resolution_required)
        resolution = states.get_conduit_resolution_state(conduit._id)
        print("resolution fields", {name: getattr(resolution, name) for name in resolution.__slots__ if "valid" in name or "dirty" in name})
        try:
            conduit.meld(spell=Consumer)
        except (RuntimeError, TypeError) as exc:
            print("error", type(exc).__name__, str(exc))
        print("post-meld", consumer.system_state.validity, consumer.dependencies, book._spellbook_validation_required)
        print("creation artifact", consumer._compiler_artifact._spell_codegen_creation is not None)
    finally:
        fixture.close()


if __name__ == "__main__":
    main()

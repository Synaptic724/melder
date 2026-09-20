"""Characterize registration uniqueness separately from existing-value identity.

This research probe runs only when explicitly selected. It uses public configuration,
binding and meld APIs, with the repository's singleton reset for isolated test worlds.
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

import melder
from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class IdentityService:
    """A resource-free supplied value or class factory with observable use."""

    def read(self) -> str:
        """Return a stable value while identity comparisons distinguish instances."""
        return "identity-service"


@pytest.fixture
def identity_world() -> Iterator[Aether]:
    """Run against this checkout and retire all test-owned roots between cases."""
    repository = Path(__file__).resolve().parents[3]
    assert Path(melder.__file__).resolve() == repository / "src" / "melder" / "__init__.py"
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    try:
        yield world
    finally:
        Aether._reset_singleton_for_tests()
        refreshed = Aether()
        Spellbook._aether = refreshed
        Conduit._aether = refreshed


@pytest.mark.parametrize(
    "case,process_unique,same_book,same_frame,same_reference,second_name,kind,existence,accepted",
    [
        ("same_reference_same_key", True, True, True, True, "main", "instance", "unique", False),
        ("same_reference_two_names", True, True, True, True, "alternate", "instance", "unique", True),
        ("two_objects_two_names", True, True, True, False, "alternate", "instance", "unique", True),
        ("two_objects_same_key", True, True, True, False, "main", "instance", "unique", False),
        ("same_reference_cross_frame_strict", True, False, False, True, "main", "instance", "unique", False),
        ("same_reference_cross_frame_relaxed", False, False, False, True, "main", "instance", "unique", True),
        ("same_reference_same_frame_relaxed", False, False, True, True, "main", "instance", "unique", False),
        ("class_singletons_cross_frame_relaxed", False, False, False, False, "main", "class", "unique", True),
        ("prebuilt_many_refused", True, True, True, True, "alternate", "instance", "many", False),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_melder_existing_identity_matrix(
        identity_world: Aether,
        case: str,
        process_unique: bool,
        same_book: bool,
        same_frame: bool,
        same_reference: bool,
        second_name: str,
        kind: str,
        existence: str,
        accepted: bool,
) -> None:
    """Assert each sequential admission result and the actual references returned by meld.

    The first root is live before the second registration, so cross-frame spell-ID
    checks see an already published provider. This does not test concurrent admission.
    """
    configuration = AetherConfiguration().with_defaults()
    configuration.with_process_wide_unique_spell_ids(process_unique)
    identity_world.configure(configuration)
    first_book = Spellbook(aetheric_frame="identity-a")
    first_book.configure_aether_frame(
        system_state="dynamic", system_caching_enabled=False,
        disposal=None, disposal_method_names=None,
    )
    first_input = IdentityService if kind == "class" else IdentityService()
    second_input = (
        IdentityService if kind == "class"
        else first_input if same_reference else IdentityService()
    )
    first_id = first_book.bind(
        spell=first_input, existence="unique", spellframe="identity-services", binding_name="main",
    )
    first_root = first_book.conjure(dynamic=True)
    second_book = first_book
    try:
        if not same_book:
            second_book = Spellbook(aetheric_frame="identity-a" if same_frame else "identity-b")
            if not same_frame:
                second_book.configure_aether_frame(
                    system_state="dynamic", system_caching_enabled=False,
                    disposal=None, disposal_method_names=None,
                )
        try:
            second_id = second_book.bind(
                spell=second_input, existence=existence,
                spellframe="identity-services", binding_name=second_name,
            )
            second_root = first_root if same_book else second_book.conjure(dynamic=True)
        except (RuntimeError, ValueError) as error:
            assert not accepted, f"{case}: unexpected refusal: {error}"
            print("IDENTITY " + json.dumps({
                "case": case, "outcome": "refused", "error_type": type(error).__name__, "error": str(error),
            }, sort_keys=True))
            return
        assert accepted, f"{case}: expected registration refusal"
        first = first_root.meld(spellframe="identity-services", binding_name="main")
        second = second_root.meld(spellframe="identity-services", binding_name=second_name)
        assert first.read() == second.read() == "identity-service"
        assert first_root.meld(spell_id=first_id) is first
        assert second_root.meld(spell_id=second_id) is second
        if kind == "instance":
            assert first is first_input and second is second_input
        assert (first is second) is (kind == "instance" and same_reference)
        print("IDENTITY " + json.dumps({
            "case": case, "outcome": "accepted", "same_spell_id": first_id == second_id,
            "same_object": first is second, "lookup_and_id_agree": True,
        }, sort_keys=True))
    finally:
        if second_book is not first_book and not second_book.cleaned:
            if second_book.conduit is None:
                second_book.cleanup()
            else:
                second_book.conduit.cleanup()
        if not first_book.cleaned:
            first_root.cleanup()

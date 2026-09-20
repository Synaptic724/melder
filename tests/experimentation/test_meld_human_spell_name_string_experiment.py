"""Prove human SpellName and explicit machine-ID public meld behavior."""

import melder as md
import pytest
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spellbook import Spellbook

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit


class MyService:
    """Minimal service whose class name is the human lookup value under test."""


class ServiceFrame:
    """Concrete logical frame type with a name distinct from the bound service."""


def test_positional_human_spell_name_and_explicit_id_behavior() -> None:
    """
    Prove positional strings resolve names while `spell_id=` preserves IDs.

    Contract:
        Positional and `spell=` strings resolve the human name. The exact SHA
        returned by bind resolves only through explicit `spell_id=`.
    """
    book = md.Spellbook(aetheric_frame="meld-human-name-string-experiment")
    spell_id = book.bind(
        spell=MyService,
        existence="unique",
        binding_name="primary",
    )
    conduit = book.conjure()
    try:
        positional = conduit.meld("MyService", binding_name="primary")
        keyword = conduit.meld(spell="MyService", binding_name="primary")
        machine = conduit.meld(spell_id=spell_id)
        assert positional is keyword is machine
        print("human and machine identity lanes resolved one live service")
    finally:
        conduit.cleanup()
        book.cleanup()


@pytest.fixture(params=("automatic_prebind", "dynamic_prebind", "dynamic_postbind"))
def named_binding_runtime(request: pytest.FixtureRequest) -> Iterator[tuple[Conduit, str]]:
    """Yield a real root containing only MyService's named binding.

    Each case owns a fresh frame/book/root and releases them deterministically.
    Caching and recording are excluded from this identifier-resolution test.
    Unique existence makes identity comparisons meaningful across call forms.
    A tuple parameter supplies (mode, spellframe); a plain mode leaves the
    spellframe unspecified for the original named-only tests.
    """
    if isinstance(request.param, tuple):
        mode, spellframe = request.param
    else:
        mode, spellframe = str(request.param), None
    dynamic = mode != "automatic_prebind"
    book = Spellbook(aetheric_frame=f"named_binding_lookup_{mode}")
    frame = book._aetheric_frame
    conduit: Optional[Conduit] = None
    try:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else "automatic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
            ai_native=False,
            rift_enabled=False,
        )
        if mode == "dynamic_postbind":
            conduit = book.conjure(dynamic=True)
        spell_id = book.bind(
            spell=MyService, existence="unique", binding_name="test", spellframe=spellframe,
        )
        if conduit is None:
            conduit = book.conjure(dynamic=dynamic)
        yield conduit, spell_id
    finally:
        try:
            if conduit is not None:
                conduit.permanent_cleanup()
        finally:
            try:
                if not book.cleaned:
                    book.cleanup()
            finally:
                if not frame.cleaned:
                    frame.cleanup()


def test_omitted_binding_does_not_fall_back_before_or_after_named_meld(
        named_binding_runtime: tuple[Conduit, str],
) -> None:
    """Prove an omitted qualifier refuses before and after a named lookup succeeds.

    A successful named lookup must not make its instance accessible through
    the absent default binding by warming the input-resolution cache.
    """
    conduit, spell_id = named_binding_runtime
    with pytest.raises(KeyError, match="binding='__default__'") as before:
        conduit.meld("MyService")
    named = conduit.meld("MyService", binding_name="test")
    assert isinstance(named, MyService)
    assert named is conduit.meld(spell_id=spell_id)
    with pytest.raises(KeyError, match="binding='__default__'") as after:
        conduit.meld("MyService")
    with pytest.raises(KeyError, match="binding='__default__'"):
        conduit.meld(MyService)
    assert before.value.args == after.value.args
    print(f"meld('MyService') before/after explicit success: {before.value}")


def test_explicit_binding_call_forms_return_the_same_unique_instance(
        named_binding_runtime: tuple[Conduit, str],
) -> None:
    """Prove string, concrete-class and machine-ID forms select one named instance."""
    conduit, spell_id = named_binding_runtime
    positional = conduit.meld("MyService", binding_name="test")
    keyword = conduit.meld(spell="MyService", binding_name="test")
    concrete = conduit.meld(MyService, binding_name="test")
    machine = conduit.meld(spell_id=spell_id)
    assert isinstance(positional, MyService)
    assert positional is keyword is concrete is machine
    print("Explicit string/class binding and spell_id: same MyService instance")


def test_binding_keyword_alone_requires_a_spell_identity(
        named_binding_runtime: tuple[Conduit, str],
) -> None:
    """Prove binding_name alone is a qualifier, not a complete meld address."""
    conduit, _ = named_binding_runtime
    with pytest.raises(ValueError) as failure:
        conduit.meld(binding_name="test")
    print(f"meld(binding_name='test'): {failure.value}")


@pytest.mark.parametrize("positional_text", ("test", 'binding_name="test"'))
def test_binding_value_or_assignment_text_is_not_a_spell_name(
        named_binding_runtime: tuple[Conduit, str],
        positional_text: str,
) -> None:
    """Prove positional text is interpreted as a spell name, without keyword parsing."""
    conduit, _ = named_binding_runtime
    with pytest.raises(KeyError) as failure:
        conduit.meld(positional_text)
    assert failure.value.args == (
        f"[MELD] No spell found for frame='{positional_text.lower()}', binding='__default__'.",
    )
    print(f"meld({positional_text!r}): {failure.value}")


@pytest.mark.parametrize(
    "named_binding_runtime",
    (
        pytest.param(("automatic_prebind", "ServiceFrame"), id="automatic-string-frame"),
        pytest.param(("dynamic_prebind", "ServiceFrame"), id="dynamic-string-frame"),
        pytest.param(("dynamic_postbind", "ServiceFrame"), id="late-bind-string-frame"),
        pytest.param(("automatic_prebind", ServiceFrame), id="automatic-type-frame"),
        pytest.param(("dynamic_prebind", ServiceFrame), id="dynamic-type-frame"),
        pytest.param(("dynamic_postbind", ServiceFrame), id="late-bind-type-frame"),
    ),
    indirect=True,
)
def test_explicit_frame_changes_the_address_and_does_not_create_a_class_name_alias(
        named_binding_runtime: tuple[Conduit, str],
) -> None:
    """Prove distinct spellframe identity remains necessary after named resolution.

    Both string and type frames normalize to the same logical frame name.
    Omitting the keyword works only when the positional value supplies that
    frame identity; the bound class name alone is a different address.
    """
    conduit, spell_id = named_binding_runtime
    with pytest.raises(KeyError, match="frame='myservice', binding='test'") as before:
        conduit.meld("MyService", binding_name="test")
    with pytest.raises(KeyError, match="frame='serviceframe', binding='__default__'"):
        conduit.meld(spellframe="ServiceFrame")
    with pytest.raises(ValueError):
        conduit.meld(binding_name="test")

    qualified = conduit.meld(spellframe="ServiceFrame", binding_name="test")
    assert isinstance(qualified, MyService)
    assert qualified is conduit.meld("MyService", spellframe="ServiceFrame", binding_name="test")
    assert qualified is conduit.meld(MyService, spellframe=ServiceFrame, binding_name="test")
    assert qualified is conduit.meld(spellframe=ServiceFrame, binding_name="test")
    assert qualified is conduit.meld("ServiceFrame", binding_name="test")
    assert qualified is conduit.meld(ServiceFrame, binding_name="test")
    assert qualified is conduit.meld(spell_id=spell_id)

    with pytest.raises(KeyError, match="frame='myservice', binding='test'") as after:
        conduit.meld("MyService", binding_name="test")
    with pytest.raises(KeyError, match="frame='myservice', binding='test'"):
        conduit.meld(MyService, binding_name="test")
    with pytest.raises(KeyError, match="frame='serviceframe', binding='__default__'"):
        conduit.meld(spellframe="ServiceFrame")
    assert before.value.args == after.value.args
    print(f"Explicit ServiceFrame, omitted frame before/after success: {before.value}")
    print("Explicit frame, positional frame name/type and SHA: same MyService instance")


@pytest.mark.parametrize(
    "named_binding_runtime",
    (
        pytest.param(("automatic_prebind", "MyService"), id="automatic-same-name-frame"),
        pytest.param(("dynamic_prebind", "MyService"), id="dynamic-same-name-frame"),
        pytest.param(("dynamic_postbind", "MyService"), id="late-bind-same-name-frame"),
    ),
    indirect=True,
)
def test_omitted_frame_works_when_it_normalizes_to_the_class_name(
        named_binding_runtime: tuple[Conduit, str],
) -> None:
    """Prove equal normalized names share an address without any fallback search."""
    conduit, spell_id = named_binding_runtime
    unqualified = conduit.meld("MyService", binding_name="test")
    qualified = conduit.meld(spellframe="MyService", binding_name="test")
    assert isinstance(unqualified, MyService)
    assert unqualified is qualified is conduit.meld(spell_id=spell_id)
    print("Frame name equals class name: omitted frame resolves the same address and instance")

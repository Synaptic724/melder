"""
Unit contracts for `HiddenProviderReport` (patch hidden_provider_2026_11_07): the one renderer of the spells a class
lookup cannot reach - its class bound under a spellframe or a binding name - shared by HIDDEN_PROVIDER, the empty
`list[Class]` report, UnresolvedInputError and Phase 3's SpellMap RuntimeError.
"""
from types import SimpleNamespace
from typing import Any, Dict, Optional, Protocol

import pytest

from melder.aether.spellbook.spell_compiler.validation.hidden_provider_report import HiddenProviderReport
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


class Greeter(Protocol):
    """The Protocol frame of the cases below."""

    def greet(self) -> str: ...


class English:
    """The class a lookup names."""


def _spell(spellframe: Any = None, binding_name: Optional[str] = None, spell_name: str = "English") -> SimpleNamespace:
    """A spell stub carrying the bind-time fields `describe` reads, its frame kind derived as Bind records it."""
    if spellframe is None:
        kind = SpellframeKind.none
    elif isinstance(spellframe, str):
        kind = SpellframeKind.category
    else:
        kind = SpellframeKind.contract
    return SimpleNamespace(spell_name=spell_name, spellframe=spellframe, spellframe_kind=kind,
                           binding_name=binding_name)


def _described(spellframe: Any = None, binding_name: Optional[str] = None, spell_id: str = "sid",
               spell_name: str = "English") -> Dict[str, Optional[str]]:
    """Describe one stub spell."""
    return HiddenProviderReport.describe(spell_id, _spell(spellframe, binding_name, spell_name))


def test_describe_renders_each_frame_kind_and_an_unknown_id() -> None:
    """A Protocol frame by `__name__`, a category as itself, bare as None; an unfound spell by its id alone."""
    assert _described(Greeter, "english") == {
        "spell_id": "sid", "spell_name": "English", "spellframe": "Greeter", "spellframe_kind": "contract",
        "binding_name": "english",
    }
    assert _described("greeters")["spellframe"] == "greeters"
    assert _described("greeters")["spellframe_kind"] == "category"
    assert _described(None, "v1")["spellframe"] is None
    assert HiddenProviderReport.describe("gone", None) == {
        "spell_id": "gone", "spell_name": None, "spellframe": None, "spellframe_kind": None, "binding_name": None,
    }


@pytest.mark.parametrize(
    ("candidates", "expected"),
    [
        pytest.param([("greeters", None)], "under a spellframe", id="framed"),
        pytest.param([(None, "v1")], "under a binding name", id="named"),
        pytest.param([("greeters", None), (None, "v1")], "under a spellframe or a binding name", id="mixed"),
    ],
)
def test_where_names_the_kind_of_place_the_class_is_bound(candidates: list, expected: str) -> None:
    """The phrase follows the described candidates."""
    assert HiddenProviderReport.where([_described(frame, name) for frame, name in candidates]) == expected


def test_where_without_a_described_candidate_names_both_places() -> None:
    """Candidates known by id alone say nothing about their place."""
    assert HiddenProviderReport.where([HiddenProviderReport.describe("x", None)]) == (
        "under a spellframe or a binding name"
    )


@pytest.mark.parametrize(
    ("frame", "binding", "shape", "expected"),
    [
        pytest.param(Greeter, None, HiddenProviderReport.SHAPE_SINGLE, "SpellMap(spellframe=Greeter)",
                     id="single-protocol-default"),
        pytest.param(Greeter, "english", HiddenProviderReport.SHAPE_SINGLE,
                     "SpellMap(spellframe=Greeter, binding_name='english')", id="single-protocol-named"),
        pytest.param("greeters", None, HiddenProviderReport.SHAPE_SINGLE, "SpellMap(spellframe='greeters')",
                     id="single-category-default"),
        pytest.param("greeters", "english", HiddenProviderReport.SHAPE_SINGLE,
                     "SpellMap(spellframe='greeters', binding_name='english')", id="single-category-named"),
        pytest.param(None, "english", HiddenProviderReport.SHAPE_SINGLE, "SpellMap(English, binding_name='english')",
                     id="single-bare-named"),
        pytest.param(None, None, HiddenProviderReport.SHAPE_SPELLMAP, "SpellMap(English)", id="spellmap-bare-default"),
        pytest.param(Greeter, None, HiddenProviderReport.SHAPE_LIST, "list[Greeter]", id="list-protocol"),
        pytest.param("greeters", "english", HiddenProviderReport.SHAPE_LIST, "list['greeters']", id="list-category"),
        pytest.param(None, "english", HiddenProviderReport.SHAPE_LIST, "list['English']", id="list-bare-named"),
    ],
)
def test_lookup_renders_the_surface_that_reaches_the_candidate(frame: Any, binding: Optional[str], shape: str,
                                                               expected: str) -> None:
    """A Protocol unquoted, a category quoted, the default binding left out, a bare candidate by its class."""
    assert HiddenProviderReport.lookup(_described(frame, binding), shape=shape) == expected


def test_lookup_of_a_bare_candidate_uses_the_class_name_it_is_given() -> None:
    """A SpellMap report names X as the SpellMap wrote it, not the candidate's own spelling."""
    assert HiddenProviderReport.lookup(_described(None, "v1"), shape=HiddenProviderReport.SHAPE_SPELLMAP,
                                       class_name="Outer.English") == "SpellMap(Outer.English, binding_name='v1')"


def test_entry_and_entries_render_addresses_in_order_and_unknown_ids_without_a_lookup() -> None:
    """Entries are ordered by address, None first; an unfound candidate reads `spell id <id>`."""
    candidates = [_described("greeters", "english", "b"), _described(Greeter, "english", "a"),
                  HiddenProviderReport.describe("gone", None)]
    assert HiddenProviderReport.entries(candidates, shape=HiddenProviderReport.SHAPE_SINGLE) == (
        "spell id gone; "
        "English at (spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, "
        "binding_name='english'); "
        "English at (spellframe='greeters', binding_name='english') - use SpellMap(spellframe='greeters', "
        "binding_name='english')"
    )


def test_with_uses_adds_the_lookup_without_mutating_the_inputs() -> None:
    """The details payload gets a `use` per candidate; the described dicts stay as they were."""
    candidate = _described(Greeter, "english")
    rendered = HiddenProviderReport.with_uses([candidate], shape=HiddenProviderReport.SHAPE_LIST)
    assert rendered == [{**candidate, "use": "list[Greeter]"}]
    assert "use" not in candidate


@pytest.mark.parametrize(
    ("frames", "expected"),
    [
        pytest.param(["greeters"], "", id="no-protocol"),
        pytest.param([Greeter], ", or a Greeter annotation while that spell is the only one bound under Greeter",
                     id="one-protocol"),
    ],
)
def test_protocol_clause_offers_the_protocol_annotation_only_for_a_protocol_frame(frames: list, expected: str) -> None:
    """A category is never offered as an annotation; one Protocol is named."""
    assert HiddenProviderReport.protocol_clause([_described(frame) for frame in frames]) == expected


def test_protocol_clause_with_several_protocols_names_none_of_them() -> None:
    """Several Protocol frames read generically."""
    class Speaker(Protocol):
        """A second Protocol frame."""

        def speak(self) -> str: ...

    assert HiddenProviderReport.protocol_clause([_described(Greeter), _described(Speaker)]) == (
        ", or an annotation with its Protocol while that spell is the only one bound under it"
    )


def test_annotation_message_is_the_hidden_provider_text() -> None:
    """The exact single-socket text for a class bound only under a Protocol frame with a binding name."""
    assert HiddenProviderReport.annotation_message(
        param_name="greeter", consumer_name="Host", expected_type="English",
        candidates=[_described(Greeter, "english")],
    ) == (
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a spellframe: English at "
        "(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). "
        "Ask for it where it is bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while "
        "that spell is the only one bound under Greeter - or bind English bare."
    )


def test_annotation_message_for_several_candidates_asks_for_the_one_it_needs() -> None:
    """Two candidates read "the SpellMap of the one it needs"; a bare named one reads "under a binding name"."""
    message = HiddenProviderReport.annotation_message(
        param_name="greeter", consumer_name="Host", expected_type="English",
        candidates=[_described(None, "v1", "a"), _described(None, "v2", "b")],
    )
    assert "English is bound only under a binding name: English at (spellframe=None, binding_name='v1') - use " \
           "SpellMap(English, binding_name='v1'); English at (spellframe=None, binding_name='v2')" in message
    assert message.endswith("Ask for it where it is bound - the SpellMap of the one it needs, as the parameter's "
                            "default - or bind English bare.")


@pytest.mark.parametrize(
    ("binding_name", "expected"),
    [
        pytest.param(None, (
            "Parameter 'greeter' on spell 'Host' has the default SpellMap(English), a class lookup that reaches "
            "English only where it is bound bare under the default binding, but English is bound only where that "
            "lookup does not reach: English at (spellframe='greeters', binding_name=None) - use "
            "SpellMap(spellframe='greeters'). Point the SpellMap at the address it means, as shown, or bind English "
            "bare."
        ), id="default-binding"),
        pytest.param("v1", (
            "Parameter 'greeter' on spell 'Host' has the default SpellMap(English, binding_name='v1'), a class lookup "
            "that reaches English only where it is bound bare under the binding name 'v1', but English is bound only "
            "where that lookup does not reach: English at (spellframe='greeters', binding_name=None) - use "
            "SpellMap(spellframe='greeters'). Point the SpellMap at the address it means, as shown, or bind English "
            "bare under the binding name 'v1'."
        ), id="named-binding"),
    ],
)
def test_spellmap_message_is_the_hidden_provider_text(binding_name: Optional[str], expected: str) -> None:
    """The exact SpellMap form, for the default and a named binding."""
    assert HiddenProviderReport.spellmap_message(
        param_name="greeter", consumer_name="Host", class_name="English", binding_name=binding_name,
        candidates=[_described("greeters", None)],
    ) == expected


def test_described_count_counts_the_entries_that_show_a_lookup() -> None:
    """A found candidate's entry shows a lookup; a candidate known by id alone shows none."""
    gone = HiddenProviderReport.describe("gone", None)
    assert HiddenProviderReport.described_count([]) == 0
    assert HiddenProviderReport.described_count([gone]) == 0
    assert HiddenProviderReport.described_count([gone, _described(Greeter, "english"), _described("greeters")]) == 2


def test_remedies_name_no_spellmap_when_no_entry_shows_one() -> None:
    """
    Regression (STEP 3 of patch hidden_provider_2026_11_07): with every candidate known by id alone no SpellMap is
    shown, so the annotation form's remedy reads "Ask for it where it is bound, or bind T bare." and the SpellMap form
    leaves out "as shown"; beside a found candidate the remedy points at "the SpellMap shown" - it counts the
    SpellMaps the entries show, not the candidates.
    """
    gone = HiddenProviderReport.describe("gone", None)
    assert HiddenProviderReport.annotation_message(
        param_name="greeter", consumer_name="Host", expected_type="English", candidates=[gone],
    ) == (
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a spellframe or a binding "
        "name: spell id gone. Ask for it where it is bound, or bind English bare."
    )
    assert HiddenProviderReport.spellmap_message(
        param_name="greeter", consumer_name="Host", class_name="English", binding_name="v1", candidates=[gone],
    ) == (
        "Parameter 'greeter' on spell 'Host' has the default SpellMap(English, binding_name='v1'), a class lookup "
        "that reaches English only where it is bound bare under the binding name 'v1', but English is bound only "
        "where that lookup does not reach: spell id gone. Point the SpellMap at the address it means, or bind English "
        "bare under the binding name 'v1'."
    )
    mixed = HiddenProviderReport.annotation_message(
        param_name="greeter", consumer_name="Host", expected_type="English",
        candidates=[gone, _described(Greeter, "english")],
    )
    assert mixed.endswith(
        "English is bound only under a spellframe: spell id gone; English at (spellframe='Greeter', "
        "binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). Ask for it where it is "
        "bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while that spell is the only "
        "one bound under Greeter - or bind English bare."
    )


def test_collection_clause_names_the_list_that_gathers_each_candidate() -> None:
    """The clause an empty required list[Class] inserts; no described candidate gives no clause."""
    assert HiddenProviderReport.collection_clause([_described(Greeter, "english")]) == (
        ": list[English] gathers English only where it is bound bare (no spellframe, the default binding), and English "
        "is bound only under a spellframe: English at (spellframe='Greeter', binding_name='english') - use "
        "list[Greeter].",
        "English",
    )
    assert HiddenProviderReport.collection_clause([HiddenProviderReport.describe("gone", None)]) == ("", None)


def test_unresolved_input_message_names_the_bindings_and_keeps_the_override_paths() -> None:
    """The meld-time text when the class is bound only where a class lookup does not reach."""
    assert HiddenProviderReport.unresolved_input_message(
        consumer_name="Host", param_name="greeter", expected_type="English",
        candidates=[_described(Greeter, "english")],
    ) == (
        "Host.greeter expects English, but this meld did not supply it and a class lookup reaches English only where "
        "it is bound bare (no spellframe, the default binding), while English is bound only under a spellframe: "
        "English at (spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, "
        "binding_name='english'). Supply it with override={'greeter': ...} when melding Host, a path key ending in "
        "'>greeter' (or '**greeter') when Host is built as a dependency, ask for it where it is bound, as shown, or "
        "bind English bare."
    )


def test_spellmap_runtime_suffix_and_display_names() -> None:
    """Phase 3's appended sentence; a class renders by qualname, an object by its type's; "" is the default binding."""
    assert HiddenProviderReport.spellmap_runtime_suffix(class_name="English", candidates=[_described(None, "v1")]) == (
        "English is bound only where this class lookup does not reach: English at (spellframe=None, "
        "binding_name='v1') - use SpellMap(English, binding_name='v1')."
    )
    assert HiddenProviderReport.spell_display_name(English) == "English"
    assert HiddenProviderReport.spell_display_name(English()) == "English"
    assert HiddenProviderReport.spellmap_text("English", "") == "SpellMap(English)"
    assert HiddenProviderReport.spellmap_text("English", "V1") == "SpellMap(English, binding_name='V1')"

"""
Component tests: a SpellIndex keeps the binding its first version was bound with.

WHY THIS EXISTS. STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (EPIC-2026-10-17-correctness_defects),
on the owner's go of 2026-10-25: "if you want to use notch you gotta use the signature that was used originally and
spell_index would retain that validation check". A SpellIndex records the binding of the version it was created for -
the kind of its spellframe (none, a string category or a Protocol) and its address (frame key and binding key, both
case-insensitive) - and every version of the index is bound the same way. `bind_inactive` and `add_to_spell_index`
refuse a version bound any other way before anything is registered or moved, so a notch never moves an index's
address; a renamed class or a new binding name is a new spell. A notch also refuses an address the frame claim gives to
another index's active version - a version split off with `remove_from_spell_index`, in this Book, or another Book's
spell - before anything moves.

Before this change a version could be staged at any address: a notch across addresses moved the index's address and
left the parked version holding the old one, a split version notched active took an address its source index's
active version still held (two active spells at one address; the next meld by address was refused), and another
Book's notch could take a third Book's address.

Each test runs in a fresh Aether with its own dynamic frame and caching off, and asserts through public calls and the
frame's claim surface.
"""

from typing import Any, Protocol, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


class Greeter(Protocol):
    """The contract every greeter version implements."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class EnglishGreeter:
    """Version 1 of the greeter index."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class FrenchGreeter:
    """Version 2 of the greeter index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class SpanishGreeter:
    """Another Book's spell at the greeter index's address."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


def _report_versions() -> Tuple[type, type]:
    """
    Purpose:
        Two versions of one class named `Report`: the same name, different code, so two spell_ids.

    Returns:
        Tuple[type, type]: Version 1 and version 2.
    """

    class Report:
        """Version 1 of the report."""

        def run(self) -> str:
            """Return version 1's text."""
            return "v1"

    first = Report

    class Report:  # the edited class keeps its name
        """Version 2 of the report."""

        def run(self) -> str:
            """Return version 2's text."""
            return "v2"

    return first, Report


class ReportV2:
    """A renamed report class: a new spell, not a version of `Report`."""

    def run(self) -> str:
        """Return the renamed class's text."""
        return "renamed"


@pytest.fixture(autouse=True)
def reset_aether_for_index_bindings() -> Any:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.

    Contract:
        - Resets before and after, so no frame claim or Book leaks between tests.

    Returns:
        Any: The generator pytest drives (yields None).
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Build a Spellbook on `frame_name` with its own default configuration.

    Args:
        frame_name (str): The aetheric frame the Spellbook belongs to.

    Returns:
        Spellbook: An unconjured Spellbook.
    """
    return Spellbook(aetheric_frame=frame_name, configuration=SpellbookConfiguration(frame_name).with_defaults())


def _settle_dynamic(spellbook: Spellbook) -> None:
    """
    Purpose:
        Settle the Spellbook's frame dynamic with caching off, so staging, notches and index moves are allowed.

    Args:
        spellbook (Spellbook): A Spellbook whose frame is not yet settled.

    Returns:
        None.
    """
    spellbook.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )


def _greeter_world(frame_name: str, binding_name: str = "english") -> Tuple[Spellbook, Conduit, Spell]:
    """
    Purpose:
        EnglishGreeter active under (Greeter, `binding_name`) in a conjured dynamic Book.

    Args:
        frame_name (str): The frame the Book lives on.
        binding_name (str): The binding name of the index's address.

    Returns:
        Tuple[Spellbook, Conduit, Spell]: The Book, its root conduit and the active English version.
    """
    book = _book(frame_name)
    _settle_dynamic(book)
    english_id = book.bind(
        spell=EnglishGreeter, spellframe=Greeter, binding_name=binding_name, existence=Existence.many,
    )
    root = book.conjure(dynamic=True, name=f"{frame_name}-root")
    english = book.find_spell_by_spell_id(english_id)
    assert english is not None
    return book, root, english


def _stage_greeter(root: Conduit, cls: type, binding_name: str, spell_index: Any) -> str:
    """
    Purpose:
        Stage `cls` parked under (Greeter, `binding_name`) on `spell_index`.

    Args:
        root (Conduit): The conduit that stages.
        cls (type): The greeter class to stage.
        binding_name (str): The binding name it is staged under.
        spell_index (Any): The index it joins.

    Returns:
        str: The spell_id `bind_inactive` returned.
    """
    return root.bind_inactive(
        spell=cls, spell_index=spell_index, spellframe=Greeter, binding_name=binding_name, existence=Existence.many,
    )


def _claim(book: Spellbook, spell: Spell) -> Any:
    """
    Purpose:
        The spell_id holding the frame claim for `spell`'s address.

    Args:
        book (Spellbook): A Book on the frame.
        spell (Spell): The spell whose address is read.

    Returns:
        Any: The holder's spell_id, or None when the address is unclaimed.
    """
    return book._aetheric_frame.get_lookup(spell._key)


@pytest.mark.parametrize(
    "spellframe, binding_name, expected",
    [
        (Greeter, "English", ("contract", "greeter", "english")),
        (None, None, ("none", "report", "__default__")),
        ("Reports", "Main", ("category", "reports", "main")),
    ],
    ids=["protocol", "bare", "category"],
)
def test_index_records_the_binding_its_first_version_was_bound_with(
        spellframe: Any, binding_name: Any, expected: Tuple[str, str, str],
) -> None:
    """
    Purpose:
        A SpellIndex keeps the kind of spellframe and the address its first version was bound with.

    Contract:
        - `SpellIndex.binding_signature` is (kind, frame key, binding key), normalized as every address is.

    Returns:
        None.
    """
    book = _book("index-records-binding")
    _settle_dynamic(book)
    target = EnglishGreeter if spellframe is Greeter else _report_versions()[0]
    spell_id = book.bind(spell=target, spellframe=spellframe, binding_name=binding_name, existence=Existence.many)
    assert book.find_spell_by_spell_id(spell_id).spell_index.binding_signature == expected


@pytest.mark.parametrize("how", ["protocol_other_case", "bare_same_class_name", "category_other_case"])
def test_bind_inactive_admits_a_version_bound_the_way_its_index_was(how: str) -> None:
    """
    Purpose:
        A version bound with its index's spellframe and binding name - case aside - is staged.

    Contract:
        - Protocol: FrenchGreeter under (Greeter, 'ENGLISH') joins English's (Greeter, 'english') index.
        - Bare: the edited `Report` class, bound bare, joins the first `Report`'s index.
        - Category: version 2 under ('reports', 'main') joins version 1's ('Reports', 'Main') index.

    Returns:
        None.
    """
    book = _book(f"admits-{how}")
    _settle_dynamic(book)
    first, second = _report_versions()
    if how == "protocol_other_case":
        first_id = book.bind(spell=EnglishGreeter, spellframe=Greeter, binding_name="english", existence="many")
        frame, binding, staged = Greeter, "ENGLISH", FrenchGreeter
    elif how == "bare_same_class_name":
        first_id = book.bind(spell=first, existence="many")
        frame, binding, staged = None, None, second
    else:
        first_id = book.bind(spell=first, spellframe="Reports", binding_name="Main", existence="many")
        frame, binding, staged = "reports", "main", second
    root = book.conjure(dynamic=True, name=f"admits-{how}-root")
    index = book.find_spell_by_spell_id(first_id).spell_index

    staged_id = root.bind_inactive(
        spell=staged, spell_index=index, spellframe=frame, binding_name=binding, existence="many",
    )

    assert index.has_spell(staged_id)
    assert book.find_spell_by_spell_id(staged_id).spell_index is index


def test_bind_inactive_refuses_another_binding_name_and_registers_nothing() -> None:
    """
    Purpose:
        A version staged under another binding name than its index's is refused, and nothing of it stays behind.

    Contract:
        - FrenchGreeter under (Greeter, 'french') on English's (Greeter, 'english') index raises ValueError naming the
          index's binding and the version's; the Book owns no version under French's spell_id, the index holds
          English alone, and staging French under 'english' afterwards succeeds (no spell_id collision).
        - Before this change the version was staged and a notch to it moved the index's address to 'french'.

    Returns:
        None.
    """
    book, root, english = _greeter_world("refuses-binding-name")
    index = english.spell_index
    french_id = Bind.spell_id_inspector(FrenchGreeter)

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with") as refused:
        _stage_greeter(root, FrenchGreeter, "french", index)

    assert "binding_name 'english'" in str(refused.value)
    assert "binding_name 'french'" in str(refused.value)
    assert book.find_spell_by_spell_id(french_id) is None
    assert index.spells_in_index() == {english.spell_id}
    assert _stage_greeter(root, FrenchGreeter, "english", index) == french_id


def test_bind_inactive_refuses_a_renamed_class_bound_bare() -> None:
    """
    Purpose:
        A renamed class is a new spell: staged bare on the old class's index, it is refused.

    Contract:
        - `ReportV2` bound bare on the bare `Report` index raises ValueError; the index holds its first version alone.

    Returns:
        None.
    """
    book = _book("refuses-renamed-class")
    _settle_dynamic(book)
    first, _second = _report_versions()
    first_id = book.bind(spell=first, existence="many")
    root = book.conjure(dynamic=True, name="refuses-renamed-class-root")
    index = book.find_spell_by_spell_id(first_id).spell_index

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with"):
        root.bind_inactive(spell=ReportV2, spell_index=index, existence="many")

    assert index.spells_in_index() == {first_id}


@pytest.mark.parametrize("first_frame, staged_frame", [(None, "Report"), ("Report", None)], ids=["bare", "category"])
def test_bind_inactive_refuses_the_other_kind_of_spellframe_at_the_same_address(
        first_frame: Any, staged_frame: Any,
) -> None:
    """
    Purpose:
        The kind of spellframe is part of an index's binding: a category spelled like a bare class's name, or the
        reverse, is another binding even at the same address.

    Contract:
        - The edited `Report` staged with spellframe='Report' on a bare `Report` index - or bare on a 'Report'
          category index - raises ValueError, although both normalize to ('report', '__default__').

    Returns:
        None.
    """
    book = _book("refuses-other-kind")
    _settle_dynamic(book)
    first, second = _report_versions()
    first_id = book.bind(spell=first, spellframe=first_frame, existence="many")
    root = book.conjure(dynamic=True, name="refuses-other-kind-root")
    index = book.find_spell_by_spell_id(first_id).spell_index

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with"):
        root.bind_inactive(spell=second, spell_index=index, spellframe=staged_frame, existence="many")

    assert index.spells_in_index() == {first_id}


def test_bind_inactive_onto_another_books_index_registers_nothing() -> None:
    """
    Purpose:
        A staging refused because the index belongs to another Book leaves nothing registered.

    Contract:
        - Book B's `bind_inactive` of FrenchGreeter onto Book A's index raises RuntimeError ("not owned"); Book B owns
          no version under French's spell_id afterwards, and staging French on Book B's own index succeeds.
        - Before this change the refusal came after the version was registered: Book B kept it parked in an index of
          its own, and the retry raised "Spell ID collision detected".

    Returns:
        None.
    """
    book_a, _root_a, english = _greeter_world("foreign-index")
    book_b = _book("foreign-index")
    spanish_id = book_b.bind(spell=SpanishGreeter, spellframe=Greeter, binding_name="spanish", existence="many")
    root_b = book_b.conjure(dynamic=True, name="foreign-index-b")
    french_id = Bind.spell_id_inspector(FrenchGreeter)

    with pytest.raises(RuntimeError, match="not owned by this spellbook"):
        _stage_greeter(root_b, FrenchGreeter, "english", english.spell_index)

    assert book_b.find_spell_by_spell_id(french_id) is None
    spanish_index = book_b.find_spell_by_spell_id(spanish_id).spell_index
    assert _stage_greeter(root_b, FrenchGreeter, "spanish", spanish_index) == french_id


def test_add_to_spell_index_refuses_a_version_of_another_binding_and_moves_nothing() -> None:
    """
    Purpose:
        A parked version cannot be moved into an index bound another way.

    Contract:
        - FrenchGreeter parked on the (Greeter, 'spanish') index cannot be added to English's (Greeter, 'english')
          index: ValueError, and French stays a member of the Spanish index, which still holds it; English's index
          holds English alone.

    Returns:
        None.
    """
    book, root, english = _greeter_world("add-refuses")
    spanish_id = root.bind(spell=SpanishGreeter, spellframe=Greeter, binding_name="spanish", existence="many")
    spanish_index = book.find_spell_by_spell_id(spanish_id).spell_index
    french_id = _stage_greeter(root, FrenchGreeter, "spanish", spanish_index)

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with"):
        root.add_to_spell_index(spell_id=french_id, target_index=english.spell_index)

    assert book.find_spell_by_spell_id(french_id).spell_index is spanish_index
    assert spanish_index.spells_in_index() == {spanish_id, french_id}
    assert english.spell_index.spells_in_index() == {english.spell_id}


def test_notch_keeps_the_index_address() -> None:
    """
    Purpose:
        A notch moves which version an address serves, never the address.

    Contract:
        - English -> French at (Greeter, 'english'): a meld by address builds French, French holds the claim; a notch
          back builds English again at the same address.

    Returns:
        None.
    """
    book, root, english = _greeter_world("notch-keeps-address")
    index = english.spell_index
    french_id = _stage_greeter(root, FrenchGreeter, "english", index)

    root.notch_spell(spell_index=index, spell_id=french_id)
    assert isinstance(root.meld(spellframe=Greeter, binding_name="english"), FrenchGreeter)
    assert _claim(book, english) == french_id

    root.notch_spell(spell_index=index, spell_id=english.spell_id)
    assert isinstance(root.meld(spellframe=Greeter, binding_name="english"), EnglishGreeter)
    assert _claim(book, english) == english.spell_id


def _split_french(compile_first: bool) -> Tuple[Spellbook, Conduit, Spell, Any, str]:
    """
    Purpose:
        English active at (Greeter, 'english') with French split off its index into one of its own, parked there.

    Args:
        compile_first (bool): Notch to French and back first, so French is compiled before the split.

    Returns:
        Tuple[Spellbook, Conduit, Spell, Any, str]: The Book, its root conduit, English, French's index, French's
            spell_id.
    """
    book, root, english = _greeter_world(f"split-{compile_first}")
    index = english.spell_index
    french_id = _stage_greeter(root, FrenchGreeter, "english", index)
    if compile_first:
        root.notch_spell(spell_index=index, spell_id=french_id)
        root.meld(spellframe=Greeter, binding_name="english")
        root.notch_spell(spell_index=index, spell_id=english.spell_id)
    root.remove_from_spell_index(spell_id=french_id, source_index=index)
    french_index = book.find_spell_by_spell_id(french_id).spell_index
    assert french_index is not index
    return book, root, english, french_index, french_id


@pytest.mark.parametrize("compile_first", [True, False], ids=["compiled", "never_compiled"])
def test_notch_refuses_an_address_another_index_of_the_book_holds(compile_first: bool) -> None:
    """
    Purpose:
        A version split off its index cannot become active while its source index still serves the address.

    Contract:
        - Notching French's own index to French raises RuntimeError naming English's spell_id as the holder; nothing
          moved: English's index selects English, holds the claim and serves a meld by address; French's index still
          has no active version.
        - Before this change a compiled French was notched active (two active spells at one address; every meld at
          it then raised SpellbookValidationError), and a French never compiled was refused as a failed structural
          check instead of for the taken address.

    Returns:
        None.
    """
    book, root, english, french_index, french_id = _split_french(compile_first)

    with pytest.raises(RuntimeError, match=f"is held by spell_id '{english.spell_id}'") as refused:
        root.notch_spell(spell_index=french_index, spell_id=french_id)

    assert not isinstance(refused.value, SpellbookValidationError)
    assert english.spell_index.selected_spell_id == english.spell_id
    assert _claim(book, english) == english.spell_id
    assert isinstance(root.meld(spellframe=Greeter, binding_name="english"), EnglishGreeter)
    assert book._spells.get(french_index) is None


def test_split_version_goes_active_once_its_address_is_free() -> None:
    """
    Purpose:
        Once nothing else holds the address, the split version's index can be notched active.

    Contract:
        - After English, now the only member of its index, is disposed (its index goes with it and its claim is
          released), notching French's own index to French stands: French holds the claim and serves the address.

    Returns:
        None.
    """
    book, root, english, french_index, french_id = _split_french(True)
    key = english._key
    root.cleanup_spell(spell=english)
    assert book._aetheric_frame.get_lookup(key) is None

    root.notch_spell(spell_index=french_index, spell_id=french_id)

    assert book._aetheric_frame.get_lookup(key) == french_id
    assert isinstance(root.meld(spellframe=Greeter, binding_name="english"), FrenchGreeter)


def test_notch_refuses_an_address_another_books_spell_holds() -> None:
    """
    Purpose:
        A notch never takes an address from another Book's active spell.

    Contract:
        - Book L's English is disposed after French was split off; Book O then binds SpanishGreeter at the same
          address. Notching French's index active in Book L raises RuntimeError naming Spanish's spell_id; Spanish
          keeps the claim and French stays parked.
        - Before this change the notch stood and took the claim from Spanish: two active spells at one address, and
          once Book L ended its teardown freed the address while Spanish still served it.

    Returns:
        None.
    """
    book_l, root_l, english, french_index, french_id = _split_french(True)
    key = english._key
    root_l.cleanup_spell(spell=english)
    book_o = _book("split-True")
    spanish_id = book_o.bind(spell=SpanishGreeter, spellframe=Greeter, binding_name="english", existence="many")
    assert book_o._aetheric_frame.get_lookup(key) == spanish_id

    with pytest.raises(RuntimeError, match=f"is held by spell_id '{spanish_id}'"):
        root_l.notch_spell(spell_index=french_index, spell_id=french_id)

    assert book_o._aetheric_frame.get_lookup(key) == spanish_id
    assert book_l._spells.get(french_index) is None

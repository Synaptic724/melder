"""
Integration: a graft merges only the members bound the way its target is
(STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, R7).

Every version of a SpellIndex is bound the way its first version was - the kind of its spellframe (none, a string
category, a Protocol contract) and the address that gives, the case of the names aside (the owner's rule,
2026-10-25) - and `bind_inactive` refuses a version bound another way. The graft's merge lane parks recorded members
onto a caller's live index through `bind_inactive`, so it checks each member against the target's binding first: a
member bound another way is a shortfall, `member_binding_differs_from_merge_target`, that names both bindings and the
remedy, and nothing is registered for it. One stray member never ends a merge part-way, and the members that fit
still park.

Each test records one index at (Greeter, 'english') - EnglishGreeter active, EnglishGreeterNext parked - captures its
graft record as plain JSON values and tears the source world down, so the members' process-wide spell_ids are free
for the host frame. The host's own HostGreeter index is the merge target, bound the way each case needs.

Runs only on 3.14t (melder package root import chain).
"""
import json
from typing import TYPE_CHECKING, Dict, Protocol, Tuple, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    _activate_crystallizer,
    cache_root,
    reset_world_singletons,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.bind.spell_index import SpellIndex


pytestmark = pytest.mark.usefixtures("reset_world_singletons", "cache_root")


class Greeter(Protocol):
    """The contract the captured index's versions are bound under; module-scoped so the graft can import it."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class EnglishGreeter:
    """The captured index's first version, bound active under (Greeter, 'english')."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class EnglishGreeterNext:
    """The captured index's second version: new code, parked on the index under the index's binding."""

    def greet(self) -> str:
        """Return the warmer English greeting."""
        return "hello there"


class HostGreeter:
    """The merge target's own version: another class, bound the way each case gives the target."""

    def greet(self) -> str:
        """Return the host's greeting."""
        return "hi"


def _book(frame: str) -> Spellbook:
    """
    A dynamic-posture Spellbook in `frame`, its configuration finalized before any bind (the recorded lane's canon).

    Args:
        frame: The frame the Book binds in; the Book births it.

    Returns:
        Spellbook: The Book, not conjured.
    """
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _index_of(book: Spellbook, spell_id: str) -> SpellIndex:
    """
    The index of the version `book` holds under `spell_id`, active or parked.

    Args:
        book: The owning Book.
        spell_id: The spell_id `bind` or `bind_inactive` returned.

    Returns:
        SpellIndex: The version's index.
    """
    spell = book.find_spell_by_spell_id(spell_id)
    assert spell is not None
    return spell.spell_index


def _captured_english_index(crystallizer: Crystallizer) -> Tuple[Dict[str, object], str, str]:
    """
    Record one index at (Greeter, 'english'), capture its graft record, then tear the source world down.

    EnglishGreeter is bound active and EnglishGreeterNext staged on its index under the same binding. The record goes
    through JSON, so a merge works from stored values, not from live objects. The source root and Book are torn down
    before any graft: under process-wide spell_ids a live member cannot be grafted into another frame.

    Args:
        crystallizer: The activated crystallizer recording the source world.

    Returns:
        Tuple[Dict[str, object], str, str]: The graft record, EnglishGreeter's spell_id (the recorded selection) and
            EnglishGreeterNext's.
    """
    source = _book("graft-binding-source")
    english_id = source.bind(
        spell=EnglishGreeter, spellframe=Greeter, binding_name="english", existence=Existence.unique,
        permissions="create",
    )
    root = source.conjure(dynamic=True, name="graft-binding-source")
    index = _index_of(source, english_id)
    next_id = root.bind_inactive(
        spell=EnglishGreeterNext, spell_index=index, spellframe=Greeter, binding_name="english",
        existence=Existence.unique, permissions="create",
    )
    record = json.loads(json.dumps(crystallizer.capture_index_graft(index.id)))
    assert set(record["members"]) == {english_id, next_id}
    assert record["index_payload"]["selected_spell_id"] == english_id
    root.cleanup()
    source.cleanup()
    return record, english_id, next_id


def _host_with_target(spellframe: Union[str, type], binding_name: str) -> Tuple[Spellbook, Conduit, str]:
    """
    A conjured host Book in a frame of its own, whose HostGreeter index - bound with the given binding - is the target.

    Args:
        spellframe: HostGreeter's spellframe: the Greeter Protocol or a string category.
        binding_name: HostGreeter's binding name.

    Returns:
        Tuple[Spellbook, Conduit, str]: The host Book, its root conduit and HostGreeter's spell_id.
    """
    host = _book("graft-binding-host")
    host_id = host.bind(
        spell=HostGreeter, spellframe=spellframe, binding_name=binding_name, existence=Existence.unique,
        permissions="create",
    )
    root = host.conjure(dynamic=True, name="graft-binding-host")
    return host, root, host_id


@pytest.mark.parametrize("target_binding_name", ["english", "ENGLISH"])
def test_merge_parks_every_member_bound_the_way_the_target_is(target_binding_name: str) -> None:
    """
    Purpose:
        R7's admitting side: members recorded under the target's binding - the same Protocol and the same binding
        name, in any case, since the address is case-insensitive - park onto the target, and a notch to one of them
        moves the target's address to it.
    Contract:
        - The merge parks both members with no shortfall; the target holds its version and both members and still
          selects its own.
        - After a notch to EnglishGreeterNext a meld by (Greeter, 'english') builds an EnglishGreeterNext.
    """
    crystallizer = _activate_crystallizer()
    record, english_id, next_id = _captured_english_index(crystallizer)
    host, root, host_id = _host_with_target(Greeter, target_binding_name)
    target = _index_of(host, host_id)

    report = crystallizer.graft_index(record, host, merge_into_index=target)

    assert report["status"] == "complete"
    assert report["merged_into_existing"] is True
    assert report["live_index_id"] == target.id
    assert report["members_bound"] == 0
    assert report["members_parked"] == 2
    assert report["shortfalls"] == []
    assert target.spells_in_index() == {host_id, english_id, next_id}
    assert target.selected_spell_id == host_id

    root.notch_spell(spell_index=target, spell_id=next_id)
    greeter = root.meld(spellframe=Greeter, binding_name="english")
    assert isinstance(greeter, EnglishGreeterNext)
    assert greeter.greet() == "hello there"


@pytest.mark.parametrize(
    ("target_frame", "target_binding_name", "target_words"),
    [
        pytest.param(
            Greeter, "french", "the Protocol spellframe Greeter and binding_name 'french'",
            id="another_binding_name",
        ),
        pytest.param(
            "Greeter", "english", "the string spellframe 'Greeter' and binding_name 'english'",
            id="a_category_at_the_same_address",
        ),
    ],
)
def test_merge_files_each_member_bound_another_way_as_a_shortfall(
        target_frame: Union[str, type],
        target_binding_name: str,
        target_words: str,
) -> None:
    """
    Purpose:
        R7's refusing side: a member recorded under another binding than the target's - another binding name, or a
        string category spelled like the Protocol, which gives the same address with another kind - is not parked.
        It is a shortfall naming both bindings and the remedy, and nothing is registered for it.
    Contract:
        - The merge completes with no member parked and one `member_binding_differs_from_merge_target` row per
          member, naming the member, its recorded binding, the target's binding and the remedy.
        - Neither spell_id is known to the host Book or its frame; the target holds its own version alone, still
          selected.
    """
    crystallizer = _activate_crystallizer()
    record, english_id, next_id = _captured_english_index(crystallizer)
    host, _root, host_id = _host_with_target(target_frame, target_binding_name)
    target = _index_of(host, host_id)

    report = crystallizer.graft_index(record, host, merge_into_index=target)

    assert report["status"] == "complete"
    assert report["members_bound"] == 0
    assert report["members_parked"] == 0
    reasons = {row["member"]: row["reason"] for row in report["shortfalls"]}
    assert set(reasons) == {english_id, next_id}
    for member_id, name in ((english_id, "EnglishGreeter"), (next_id, "EnglishGreeterNext")):
        reason = reasons[member_id]
        assert reason.startswith(f"member_binding_differs_from_merge_target: '{name}' was recorded with ")
        assert "the Protocol spellframe Greeter and binding_name 'english'" in reason
        assert f"every version of the merge target is bound with {target_words}." in reason
        assert "Graft without merge_into_index to give it an index of its own" in reason
    frame = Aether().get_frame("graft-binding-host")
    for member_id in (english_id, next_id):
        assert host.find_spell_by_spell_id(member_id) is None
        assert frame.find_index_for_spell(member_id) is None
    assert target.spells_in_index() == {host_id}
    assert target.selected_spell_id == host_id


def test_a_refused_merge_registers_nothing_so_the_record_grafts_again() -> None:
    """
    Purpose:
        A merge that refuses every member leaves nothing behind, so the remedy its shortfalls name works on the same
        host: grafted without `merge_into_index`, the members get an index of their own at their recorded binding.
    Contract:
        - The refused merge parks nothing and files a shortfall per member.
        - The fresh graft then binds EnglishGreeter active and parks EnglishGreeterNext on a new index, with no
          spell_id collision and no shortfall; (Greeter, 'english') builds an EnglishGreeter while the target still
          serves (Greeter, 'french').
    """
    crystallizer = _activate_crystallizer()
    record, english_id, next_id = _captured_english_index(crystallizer)
    host, root, host_id = _host_with_target(Greeter, "french")
    target = _index_of(host, host_id)

    refused = crystallizer.graft_index(record, host, merge_into_index=target)
    assert refused["members_parked"] == 0
    assert len(refused["shortfalls"]) == 2

    report = crystallizer.graft_index(record, host)

    assert report["status"] == "complete"
    assert report["merged_into_existing"] is False
    assert report["members_bound"] == 1
    assert report["members_parked"] == 1
    assert report["shortfalls"] == []
    own_index = _index_of(host, english_id)
    assert own_index.id == report["live_index_id"]
    assert own_index.id != target.id
    assert own_index.spells_in_index() == {english_id, next_id}
    assert own_index.selected_spell_id == english_id
    assert isinstance(root.meld(spellframe=Greeter, binding_name="english"), EnglishGreeter)
    assert isinstance(root.meld(spellframe=Greeter, binding_name="french"), HostGreeter)


def test_a_selection_refused_for_its_binding_is_not_adopted() -> None:
    """
    Purpose:
        `adopt_recorded_selection` adopts only a member that was parked: when the recorded selection is refused for
        its binding, the merge says so with the existing adoption shortfall and the target keeps its selection.
    Contract:
        - Shortfalls: a binding row per member, plus `recorded_selection_not_grafted_not_adopted` for the recorded
          selection; `selection_adopted` is False.
        - The target still selects its own version.
    """
    crystallizer = _activate_crystallizer()
    record, english_id, next_id = _captured_english_index(crystallizer)
    host, _root, host_id = _host_with_target(Greeter, "french")
    target = _index_of(host, host_id)

    report = crystallizer.graft_index(record, host, merge_into_index=target, adopt_recorded_selection=True)

    assert report["selection_adopted"] is False
    assert report["members_parked"] == 0
    rows = sorted((row["member"], row["reason"].split(":")[0]) for row in report["shortfalls"])
    assert rows == sorted([
        (english_id, "member_binding_differs_from_merge_target"),
        (next_id, "member_binding_differs_from_merge_target"),
        (english_id, "recorded_selection_not_grafted_not_adopted"),
    ])
    assert target.selected_spell_id == host_id

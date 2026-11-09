"""
Integration: two spells are never ACTIVE at one address - every same-frame path that registers or exposes a spell
refuses the second one.

WHY THIS EXISTS. The owner's rule (chat, 2026-11-07): "sure 2 spells with the same name without differentiation, 2
spells with the same spellframe without a binding_name ... you can add these or extend various features for this, if
we don't already have it". An address is the normalized `(frame_key, binding_key)` pair: the spellframe's name - or
the spell's own name when it is bound bare - and the binding name, both lowercased, an empty binding name being
`__default__`. Two shapes put two spells at one address:
    S - the same spellframe without a binding name: two classes under the string category 'Reports' (spelled
        'Reports' and 'reports'), under the Protocol `Greeter`, or under two Protocols both named `Greeter`;
    N - the same name without differentiation: two bare classes named `Report` declared in different scopes, or
        `Report` and `report`.
Each test runs once per shape (`tests/_one_active_spell_per_address_support.py`).

The guards these tests pin, measured on every path by
`context_compass/artifacts/duplicate_address_paths_20261107/probes/duplicate_address_paths_probe.py` (0.2.8279, and
0.2.8280 after the cross-frame transfer refusal; the GIL off and on, identical):
    - the frame claim (`LookupContainer.claim`, through `Spellbook.bind`): one active spell per address per frame,
      so a second bind - in the same Book, another Book of the frame, through a live root, a scan, a borrower holding
      a contracted copy, or a lesser upgraded to a root of its own - raises RuntimeError "Binding signature already
      active in this frame ... is held by spell_id='<holder>'" and registers nothing (a scan keeps the declarations
      bound before the refused one);
    - `SpellIndex.check_admits` (0.2.8273): `bind_inactive` and `add_to_spell_index` refuse a version bound another
      way than the index's first version with ValueError "... keeps the binding its first version was bound with";
    - the notch's compare-and-set (`Spellbook._apply_notch`, 0.2.8273): a version in another index at a held address
      never goes active - RuntimeError "notch_spell refused: the address of SpellIndex <id> - <binding> - is held by
      spell_id '<holder>' ...";
    - `add_to_spell_index` refuses an active version ("is active in its index"), and `link` refuses a conduit of
      another frame, so no contracted copy crosses frames;
    - `transfer_spell_ownership` refuses a target conduit of another frame (the owner's ruling, chat 2026-11-07:
      "they shouldn't be able to transfer between frames thats an illegal operation"; 0.2.8280) with RuntimeError
      "Cannot transfer spell ownership across different AethericFrames: <source> != <target>. ..." before anything
      moves. Until then the probe's P08c/P08d admitted it: the target Book held two active spells at one address,
      and the source frame's claim kept naming the moved spell.

Not duplicates, by design, and not pinned here: the versions of ONE SpellIndex (a notch moves which one is active) and
a borrower's contracted copy of a lender's spell (the same spell, lent).

Each test runs in fresh singletons, on dynamic frames with caching off, and tears its roots and Books down.
"""
from types import ModuleType
from typing import Iterator, List, Optional, Tuple, Union

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.scan import scan_bind
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spellbook import Spellbook
from tests._one_active_spell_per_address_support import (
    AddressShape,
    AddressWorld,
    Ledger,
    address_shape,
    address_shape_labels,
    index_of,
    reset_address_world,
)

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def fresh_singletons() -> Iterator[None]:
    """
    Purpose:
        Isolate each test behind fresh Aether, Nexus, Crystallizer and utility singletons.

    Contract:
        - Resets before and after, so no frame claim, Book or root leaks between tests.

    Yields:
        None while the test runs.
    """
    reset_address_world()
    yield
    reset_address_world()


@pytest.fixture(params=address_shape_labels())
def shape(request: pytest.FixtureRequest) -> AddressShape:
    """
    Purpose:
        Run the test once per shape that puts two spells at one address.

    Args:
        request (pytest.FixtureRequest): Carries the shape label.

    Returns:
        AddressShape: The shape's three spells (X, Y, W), their address and its meld door.
    """
    return address_shape(request.param)


@pytest.fixture()
def world() -> Iterator[AddressWorld]:
    """
    Purpose:
        Hand the test a world that keeps every Book and root it builds, then tear them down.

    Contract:
        - Roots are cleaned last first, then Books; a failing cleanup fails the test.

    Yields:
        AddressWorld: The world.
    """
    address_world = AddressWorld()
    try:
        yield address_world
    finally:
        address_world.teardown()


def _assert_only_holder_serves(
        world: AddressWorld, shape: AddressShape, conduit: Conduit, spellbook: Spellbook, holder_id: str, letter: str,
) -> None:
    """
    Purpose:
        Assert that `holder_id` - and nothing else - is active at the shape's address, holds the frame claim, and is
        what a meld by address through `conduit` builds.

    Args:
        world (AddressWorld): The test's world (every live Book is counted).
        shape (AddressShape): The shape.
        conduit (Conduit): The conduit whose meld by address is asked.
        spellbook (Spellbook): A Book of the frame, to read the claim.
        holder_id (str): The spell_id that must hold the address.
        letter (str): Its letter ("X", "Y" or "W").

    Returns:
        None.

    Raises:
        AssertionError: If another spell is active at the address, holds its claim or answers its meld.
    """
    assert world.active_ids_at(shape.address) == [holder_id]
    assert AddressWorld.claim(spellbook, shape.address) == holder_id
    assert shape.letter(shape.meld(conduit)) == letter


def _assert_refused_for_the_held_address(error: BaseException, shape: AddressShape, holder_id: str) -> None:
    """
    Purpose:
        Assert a RuntimeError is the frame claim's refusal of the shape's address, naming the holder.

    Args:
        error (BaseException): The raised error.
        shape (AddressShape): The shape.
        holder_id (str): The spell_id the message must name.

    Returns:
        None.

    Raises:
        AssertionError: If the message does not name the address and its holder.
    """
    message = str(error)
    assert f"frame_key='{shape.address[0]}', binding_name='__default__'" in message
    assert f"is held by spell_id='{holder_id}'" in message


def _split_version(world: AddressWorld, shape: AddressShape, frame: str) -> Tuple[Spellbook, Conduit, str, str, SpellIndex]:
    """
    Purpose:
        X active in a conjured Book; Y staged on X's index under X's binding, notched to, melded and notched back (so
        Y is compiled), then split off into an index of its own with `remove_from_spell_index`.

    Args:
        world (AddressWorld): The test's world.
        shape (AddressShape): The shape.
        frame (str): The frame suffix.

    Returns:
        Tuple[Spellbook, Conduit, str, str, SpellIndex]: The Book, its root, X's and Y's spell_ids and Y's own index.
    """
    spellbook = world.book(frame)
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, f"{frame}-root")
    x_index = index_of(spellbook, x_id)
    y_id = shape.stage(root, "second", x_index)
    root.notch_spell(spell_index=x_index, spell_id=y_id)
    shape.meld(root)
    root.notch_spell(spell_index=x_index, spell_id=x_id)
    root.remove_from_spell_index(spell_id=y_id, source_index=x_index)
    y_index = index_of(spellbook, y_id)
    assert y_index is not x_index
    return spellbook, root, x_id, y_id, y_index


def test_bind_refuses_a_second_spell_at_a_held_address_before_conjure(shape: AddressShape, world: AddressWorld) -> None:
    """
    Purpose:
        P01: in one Book, before conjure, a second spell at an address the first holds is refused at bind.

    Contract:
        - `Spellbook.bind(Y)` raises RuntimeError "Binding signature already active in this frame", naming the address
          and X's spell_id; nothing of Y is registered.
        - After conjure, X alone serves the address and holds its claim.

    Returns:
        None.
    """
    spellbook = world.book("p01")
    x_id = shape.bind(spellbook, "first")

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(spellbook, "second")

    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    assert spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
    root = world.conjure(spellbook, "p01-root")
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def test_live_root_bind_refuses_a_second_spell_at_a_held_address(shape: AddressShape, world: AddressWorld) -> None:
    """
    Purpose:
        P02: a dynamic root's post-conjure bind of a second spell at an address its Book serves is refused.

    Contract:
        - `Conduit.bind(Y)` raises RuntimeError "Binding signature already active in this frame" naming X; Y is not
          registered and X keeps serving the address.

    Returns:
        None.
    """
    spellbook = world.book("p02")
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "p02-root")

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(root, "second")

    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    assert spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


@pytest.mark.parametrize("when", ["both_before_conjure", "after_the_holders_conjure", "both_conjured"])
def test_another_book_of_the_frame_cannot_bind_a_held_address(
        shape: AddressShape, world: AddressWorld, when: str,
) -> None:
    """
    Purpose:
        P03: the claim is frame-wide - a second Book of the frame cannot bind a spell at an address the first Book's
        spell holds, whenever either Book conjures.

    Contract:
        - both_before_conjure: Book 2's bind before either Book conjured; after_the_holders_conjure: Book 2's bind
          (before its own conjure) once Book 1 conjured; both_conjured: Book 2's live root binds once both conjured.
        - Each raises RuntimeError "Binding signature already active in this frame" naming X; X alone stays active at
          the address and Book 1's root serves it.

    Returns:
        None.
    """
    first_book = world.book("p03")
    x_id = shape.bind(first_book, "first")
    second_book = world.book("p03")
    first_root: Optional[Conduit] = None if when == "both_before_conjure" else world.conjure(first_book, "p03-r1")
    binder: Union[Spellbook, Conduit] = second_book
    if when == "both_conjured":
        second_book.bind(spell=Ledger, existence="many", permissions="create")
        binder = world.conjure(second_book, "p03-r2")

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(binder, "second")

    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    if first_root is None:
        first_root = world.conjure(first_book, "p03-r1")
    _assert_only_holder_serves(world, shape, first_root, first_book, x_id, "X")


def test_bind_inactive_refuses_a_second_spell_onto_an_index_of_another_binding(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P04a: a second spell at a held address cannot be staged onto ANOTHER index - one bound another way (Ledger's,
        bare at ('ledger', '__default__')).

    Contract:
        - `Conduit.bind_inactive(Y, spell_index=<Ledger's index>)` raises ValueError "bind_inactive refused: SpellIndex
          <id> keeps the binding its first version was bound with"; nothing of Y is registered and X keeps serving.

    Returns:
        None.
    """
    spellbook = world.book("p04a")
    x_id = shape.bind(spellbook, "first")
    ledger_id = spellbook.bind(spell=Ledger, existence="many", permissions="create")
    root = world.conjure(spellbook, "p04a-root")

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with") as refused:
        shape.stage(root, "second", index_of(spellbook, ledger_id))

    assert str(refused.value).startswith("bind_inactive refused: SpellIndex")
    assert spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def test_a_version_staged_onto_a_split_index_is_never_notched_active_while_the_address_is_held(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P04b: a second spell staged onto ANOTHER index at the held address - one split off the holder's index - stays
        parked, and a notch to it is refused (0.2.8273).

    Contract:
        - W is split off X's index; Y staged onto W's index is admitted parked (bound the way that index was) and is
          not active there.
        - `notch_spell(W's index -> Y)` raises RuntimeError "notch_spell refused: the address of SpellIndex <id> ... is
          held by spell_id '<X>' ('...'), the active version of another index of this Spellbook"; X keeps the
          address.

    Returns:
        None.
    """
    spellbook = world.book("p04b")
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "p04b-root")
    x_index = index_of(spellbook, x_id)
    w_id = shape.stage(root, "third", x_index)
    root.remove_from_spell_index(spell_id=w_id, source_index=x_index)
    w_index = index_of(spellbook, w_id)
    y_id = shape.stage(root, "second", w_index)
    assert spellbook.spells.get(w_index) is None

    with pytest.raises(RuntimeError, match="notch_spell refused: the address of SpellIndex") as refused:
        root.notch_spell(spell_index=w_index, spell_id=y_id)

    assert f"is held by spell_id '{x_id}'" in str(refused.value)
    assert "the active version of another index of this Spellbook" in str(refused.value)
    assert spellbook.spells.get(w_index) is None
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def test_a_version_split_off_with_remove_from_spell_index_is_never_notched_active_while_its_source_serves(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P05: a compiled version split off its index with `remove_from_spell_index` cannot be notched active in its new
        index while its source index's version serves the address (the pre-0.2.8273 two-actives path, C7).

    Contract:
        - `notch_spell(Y's own index -> Y)` raises RuntimeError "notch_spell refused ... is held by spell_id '<X>'"
          naming the other index of this Spellbook; Y's index has no active version and X keeps the address.

    Returns:
        None.
    """
    spellbook, root, x_id, y_id, y_index = _split_version(world, shape, "p05")

    with pytest.raises(RuntimeError, match="notch_spell refused: the address of SpellIndex") as refused:
        root.notch_spell(spell_index=y_index, spell_id=y_id)

    assert f"is held by spell_id '{x_id}'" in str(refused.value)
    assert "the active version of another index of this Spellbook" in str(refused.value)
    assert spellbook.spells.get(y_index) is None
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def test_add_to_spell_index_refuses_a_version_onto_an_index_of_another_binding(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P06a: a parked version bound at the held address cannot be moved into an index bound another way.

    Contract:
        - `add_to_spell_index(Y -> Ledger's index)` raises ValueError "add_to_spell_index refused: SpellIndex <id>
          keeps the binding its first version was bound with"; Y stays in its own index and X keeps the address.

    Returns:
        None.
    """
    spellbook, root, x_id, y_id, y_index = _split_version(world, shape, "p06a")
    ledger_id = root.bind(spell=Ledger, existence="many", permissions="create")

    with pytest.raises(ValueError, match="keeps the binding its first version was bound with") as refused:
        root.add_to_spell_index(spell_id=y_id, target_index=index_of(spellbook, ledger_id))

    assert str(refused.value).startswith("add_to_spell_index refused: SpellIndex")
    assert index_of(spellbook, y_id) is y_index
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def test_add_to_spell_index_refuses_to_move_the_active_version_into_another_index_at_its_address(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P06c: the version serving the address cannot be moved into another index at that address.

    Contract:
        - `add_to_spell_index(X -> Y's own index)` raises RuntimeError "... is active in its index; notch away from it
          before moving it."; X stays in its index and keeps the address.

    Returns:
        None.
    """
    spellbook, root, x_id, _y_id, y_index = _split_version(world, shape, "p06c")
    x_index = index_of(spellbook, x_id)

    with pytest.raises(RuntimeError, match="is active in its index") as refused:
        root.add_to_spell_index(spell_id=x_id, target_index=y_index)

    assert x_id in str(refused.value)
    assert index_of(spellbook, x_id) is x_index
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")


def _scan_module(shape: AddressShape, module_name: str) -> Tuple[ModuleType, type, type]:
    """
    Purpose:
        A module declaring X's and Y's classes with `scan_bind`, bound the shape's way.

    Contract:
        - Each declaration is a fresh subclass of the shape's class with the same `__name__` and the module's
          `__module__` (a scan refuses re-exports), so the shared classes are not mutated. For N-scope both are named
          `Report` under two attribute names; for N-case they are `Report` and `report`.

    Args:
        shape (AddressShape): The shape.
        module_name (str): The module's name.

    Returns:
        Tuple[ModuleType, type, type]: The module, its first and its second declaration.
    """
    module = ModuleType(module_name)
    declared: List[type] = []
    for attribute, role in (("FirstDeclared", "first"), ("SecondDeclared", "second")):
        base = shape.cls(role)
        declaration = type(base.__name__, (base,), {"__module__": module_name})
        scan_bind(existence="many", permissions="create", spellframe=shape.spellframe(role))(declaration)
        setattr(module, attribute, declaration)
        declared.append(declaration)
    return module, declared[0], declared[1]


@pytest.mark.parametrize("door", ["spellbook_pre_conjure", "conduit_post_conjure"])
def test_scan_refuses_the_second_declaration_at_one_address(
        shape: AddressShape, world: AddressWorld, door: str,
) -> None:
    """
    Purpose:
        P07: a module declaring two spells at one address scans the first and refuses the second, before conjure
        through the Book and after it through the live root.

    Contract:
        - The scan raises RuntimeError "Binding signature already active in this frame" naming the first
          declaration; a scan is not atomic, so the first declaration stays registered and serves the address, and
          the second is not registered.

    Returns:
        None.
    """
    spellbook = world.book("p07")
    module, first, second = _scan_module(shape, f"one_active_spell_per_address_scan_{door}")
    root = world.conjure(spellbook, "p07-root") if door == "conduit_post_conjure" else None
    first_id = Bind.spell_id_inspector(first)

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        (root if root is not None else spellbook).scan(module)

    _assert_refused_for_the_held_address(refused.value, shape, first_id)
    assert spellbook.find_spell_by_spell_id(first_id) is not None
    assert spellbook.find_spell_by_spell_id(Bind.spell_id_inspector(second)) is None
    if root is None:
        root = world.conjure(spellbook, "p07-root")
    assert world.active_ids_at(shape.address) == [first_id]
    assert type(shape.meld(root)) is first


def test_transfer_into_another_book_of_the_frame_moves_the_holder_and_keeps_one_active_spell(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P08a: in one frame no Book can serve an address another Book's spell holds, so an ownership transfer of the
        holder's index into another Book moves the holder itself - one active spell at the address.

    Contract:
        - The target Book's bind of Y raises RuntimeError "Binding signature already active in this frame" naming X.
        - `transfer_spell_ownership(X -> the target root)` then stands: X is the only active spell at the address,
          it is the target's, keeps the claim, and the target's meld by address builds it.

    Returns:
        None.
    """
    source_book = world.book("p08a")
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "p08a-src")
    target_book = world.book("p08a")
    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(target_book, "second")
    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    target = world.conjure(target_book, "p08a-tgt")

    source.transfer_spell_ownership(spell=x_id, target_conduit=target)

    assert [spell.spell_id for spell in target_book.spells.values() if spell.key == shape.address] == [x_id]
    _assert_only_holder_serves(world, shape, target, target_book, x_id, "X")


def test_a_transferred_holder_keeps_the_targets_own_parked_version_from_going_active(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P08b: a Book holding its own index at an address with no active version (W split off, the active version
        disposed) receives the holder of that address by transfer; it cannot then notch its own index active.

    Contract:
        - After `transfer_spell_ownership(X -> the target root)`, `notch_spell(W's index -> W)` in the target raises
          RuntimeError "notch_spell refused ... is held by spell_id '<X>' ('...'), the active version of another index
          of this Spellbook"; X alone serves the address.

    Returns:
        None.
    """
    target_book = world.book("p08b")
    y_id = shape.bind(target_book, "second")
    target = world.conjure(target_book, "p08b-tgt")
    y_index = index_of(target_book, y_id)
    w_id = shape.stage(target, "third", y_index)
    target.remove_from_spell_index(spell_id=w_id, source_index=y_index)
    w_index = index_of(target_book, w_id)
    target.cleanup_spell(spell=target_book.find_spell_by_spell_id(y_id))
    source_book = world.book("p08b")
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "p08b-src")
    source.transfer_spell_ownership(spell=x_id, target_conduit=target)

    with pytest.raises(RuntimeError, match="notch_spell refused: the address of SpellIndex") as refused:
        target.notch_spell(spell_index=w_index, spell_id=w_id)

    assert f"is held by spell_id '{x_id}'" in str(refused.value)
    assert "the active version of another index of this Spellbook" in str(refused.value)
    _assert_only_holder_serves(world, shape, target, target_book, x_id, "X")


def _assert_the_source_frame_still_holds_x(
        world: AddressWorld, shape: AddressShape, source_book: Spellbook, source: Conduit, x_id: str, frame: str,
) -> None:
    """
    Purpose:
        Assert a refused cross-frame transfer moved nothing out of the source frame: its Book still owns X active at
        the address, X holds the frame's claim and the source root melds X - by address and by spell_id - and a new
        Book of that frame is refused the address naming X, which is still there (so the claim is not stale).

    Args:
        world (AddressWorld): The test's world (the new Book joins it).
        shape (AddressShape): The shape.
        source_book (Spellbook): The source Book.
        source (Conduit): Its root.
        x_id (str): X's spell_id.
        frame (str): The source frame's suffix.

    Returns:
        None.

    Raises:
        AssertionError: If X left the source frame, lost its claim or stopped serving, or the frame's address is
            refused for any other reason.
    """
    assert AddressWorld.active_ids_in(source_book, shape.address) == [x_id]
    assert AddressWorld.claim(source_book, shape.address) == x_id
    assert source.get_conduit_by_spell_id(x_id) is source
    assert shape.letter(shape.meld(source)) == "X"
    assert shape.letter(source.meld(spell_id=x_id)) == "X"
    late_book = world.book(frame)
    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as held:
        shape.bind(late_book, "third")
    _assert_refused_for_the_held_address(held.value, shape, x_id)
    assert AddressWorld.active_ids_in(source_book, shape.address) == [x_id]


def test_transfer_across_frames_is_refused_and_moves_nothing_into_a_frame_serving_the_address(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P08c: X serves the address in frame a, Y serves it in frame b (each frame has its own claims); a transfer of
        X's index to frame b's root is refused - a frame is a world with its own addresses, links and contracts
        (the owner's ruling, 2026-11-07; 0.2.8280) - and nothing moves.

    Contract:
        - `transfer_spell_ownership(X -> frame b's root)` raises RuntimeError "Cannot transfer spell ownership across
          different AethericFrames: addr-p08c-a != addr-p08c-b".
        - Frame a is untouched: its Book still owns X active at the address, X holds the claim, the source root melds
          X, and a new frame-a Book is refused the address naming X (X is still there; no stale claim).
        - Frame b is untouched: its Book holds only Y at the address, X is unknown to it, Y holds the claim and the
          target root melds Y, as before the attempt. Before 0.2.8280 the transfer stood and the target Book held X
          and Y both active at the address (every meld of it then raised DUPLICATE_SPELL_NAME), while frame a's claim
          kept naming the departed X.

    Returns:
        None.
    """
    source_book = world.book("p08c-a")
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "p08c-src")
    target_book = world.book("p08c-b")
    y_id = shape.bind(target_book, "second")
    target = world.conjure(target_book, "p08c-tgt")
    assert shape.letter(shape.meld(target)) == "Y"

    with pytest.raises(RuntimeError, match="Cannot transfer spell ownership across different AethericFrames") as refused:
        source.transfer_spell_ownership(spell=x_id, target_conduit=target)

    assert "addr-p08c-a != addr-p08c-b" in str(refused.value)
    _assert_the_source_frame_still_holds_x(world, shape, source_book, source, x_id, "p08c-a")
    assert AddressWorld.active_ids_in(target_book, shape.address) == [y_id]
    assert target_book.find_spell_by_spell_id(x_id) is None
    assert AddressWorld.claim(target_book, shape.address) == y_id
    assert shape.letter(shape.meld(target)) == "Y"
    assert shape.letter(target.meld(spell_id=y_id)) == "Y"


def test_transfer_across_frames_is_refused_and_a_later_bind_in_the_target_frame_is_an_ordinary_first_bind(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P08d: X serves the address in frame a; frame b serves nothing there. A transfer of X's index to frame b's root
        is refused (0.2.8280) and nothing moves, so frame b's address stays free and a later bind of Y there is an
        ordinary first bind.

    Contract:
        - `transfer_spell_ownership(X -> frame b's root)` raises RuntimeError "Cannot transfer spell ownership across
          different AethericFrames: addr-p08d-a != addr-p08d-b".
        - Frame a is untouched (as in P08c). Frame b still serves nothing at the address: no active spell, no claim,
          and the target root's meld by address raises KeyError, as before the attempt.
        - Then `target.bind(Y)` returns Y's spell_id without raising; Y is frame b's only active spell at the address,
          holds its claim and is what the target root melds, while frame a keeps serving X. Before 0.2.8280 the
          transfer stood without moving any claim, and this bind registered Y beside the moved X - two active at one
          address - before raising SpellbookValidationError (DUPLICATE_SPELL_NAME) from its commit.

    Returns:
        None.
    """
    source_book = world.book("p08d-a")
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "p08d-src")
    target_book = world.book("p08d-b")
    target_book.bind(spell=Ledger, existence="many", permissions="create")
    target = world.conjure(target_book, "p08d-tgt")
    with pytest.raises(KeyError):
        shape.meld(target)

    with pytest.raises(RuntimeError, match="Cannot transfer spell ownership across different AethericFrames") as refused:
        source.transfer_spell_ownership(spell=x_id, target_conduit=target)

    assert "addr-p08d-a != addr-p08d-b" in str(refused.value)
    _assert_the_source_frame_still_holds_x(world, shape, source_book, source, x_id, "p08d-a")
    assert AddressWorld.active_ids_in(target_book, shape.address) == []
    assert AddressWorld.claim(target_book, shape.address) is None
    with pytest.raises(KeyError):
        shape.meld(target)

    y_id = shape.bind(target, "second")

    assert y_id == shape.spell_id("second")
    assert AddressWorld.active_ids_in(target_book, shape.address) == [y_id]
    assert AddressWorld.claim(target_book, shape.address) == y_id
    assert shape.letter(shape.meld(target)) == "Y"
    assert shape.letter(shape.meld(source)) == "X"


def _lender_with_a_split_parked_version(world: AddressWorld, shape: AddressShape) -> Tuple[Conduit, str, SpellIndex]:
    """
    Purpose:
        A lender whose own index at the shape's address has no active version: X bound, W staged on X's index and
        split off, X disposed (its claim released), so the address is free for a borrower's bind.

    Args:
        world (AddressWorld): The test's world.
        shape (AddressShape): The shape.

    Returns:
        Tuple[Conduit, str, SpellIndex]: The lender root, W's spell_id and W's index.
    """
    lender_book = world.book("p09")
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "p09-lender")
    x_index = index_of(lender_book, x_id)
    w_id = shape.stage(lender, "third", x_index)
    lender.remove_from_spell_index(spell_id=w_id, source_index=x_index)
    w_index = index_of(lender_book, w_id)
    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(x_id))
    return lender, w_id, w_index


def _borrower_serving_the_address(world: AddressWorld, shape: AddressShape, lender: Conduit) -> Tuple[Spellbook, Conduit, str]:
    """
    Purpose:
        A borrower Book serving the shape's address with its own Y, conjured and linked to `lender`.

    Args:
        world (AddressWorld): The test's world.
        shape (AddressShape): The shape.
        lender (Conduit): The lender root to link to.

    Returns:
        Tuple[Spellbook, Conduit, str]: The borrower Book, its root and Y's spell_id.
    """
    borrower_book = world.book("p09")
    y_id = shape.bind(borrower_book, "second")
    borrower = world.conjure(borrower_book, "p09-borrower")
    borrower.link(lender)
    return borrower_book, borrower, y_id


def test_a_parked_copy_shared_to_a_borrower_serving_the_address_never_goes_active(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P09a (spell door): a copy of a lender's version at an address arrives at a borrower that serves the address
        with its own spell. In one frame it can arrive only parked (the address was free for the borrower's bind
        because the lender's index had no active version), and the lender's notch to it is refused, so the copy never
        goes active beside the borrower's spell.

    Contract:
        - `borrower.add_spell_to_contract(W)` admits the share with the copy parked: W is in the borrower's parked
          contracted copies and not among its active ones.
        - The lender's `notch_spell(W's index -> W)` raises RuntimeError "notch_spell refused ... is held by spell_id
          '<Y>', an active spell of another Spellbook of this frame"; the copy stays parked and Y alone serves the
          borrower's address.

    Returns:
        None.
    """
    lender, w_id, w_index = _lender_with_a_split_parked_version(world, shape)
    borrower_book, borrower, y_id = _borrower_serving_the_address(world, shape, lender)

    assert borrower.add_spell_to_contract(spell_id=w_id, conduit=lender) is True

    assert w_id in borrower_book._inactive_contracted_spells.get(lender.id, {})
    assert all(spell.spell_id != w_id for spell in borrower_book.contracted_spells.get(lender.id, {}).values())
    with pytest.raises(RuntimeError, match="notch_spell refused: the address of SpellIndex") as refused:
        lender.notch_spell(spell_index=w_index, spell_id=w_id)
    assert f"is held by spell_id '{y_id}'" in str(refused.value)
    assert "an active spell of another Spellbook of this frame" in str(refused.value)
    assert all(spell.spell_id != w_id for spell in borrower_book.contracted_spells.get(lender.id, {}).values())
    _assert_only_holder_serves(world, shape, borrower, borrower_book, y_id, "Y")


def test_an_index_without_an_active_version_is_not_index_linked_to_a_borrower_serving_the_address(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P09a (index door): the same lender index - no active version, at the address the borrower's own spell serves -
        cannot be index-linked to the borrower, and the lender's notch to its parked version is refused.

    Contract:
        - `borrower.add_index_to_contract(W's index)` raises RuntimeError "... is not an active owned index of conduit
          ..."; no copy reaches the borrower.
        - The lender's `notch_spell(W's index -> W)` raises RuntimeError "notch_spell refused ... is held by spell_id
          '<Y>'"; Y alone serves the borrower's address.

    Returns:
        None.
    """
    lender, w_id, w_index = _lender_with_a_split_parked_version(world, shape)
    borrower_book, borrower, y_id = _borrower_serving_the_address(world, shape, lender)

    with pytest.raises(RuntimeError, match="is not an active owned index"):
        borrower.add_index_to_contract(index=w_index, conduit=lender)

    assert w_id not in borrower_book._inactive_contracted_spells.get(lender.id, {})
    assert all(spell.spell_id != w_id for spell in borrower_book.contracted_spells.get(lender.id, {}).values())
    with pytest.raises(RuntimeError, match="notch_spell refused: the address of SpellIndex") as refused:
        lender.notch_spell(spell_index=w_index, spell_id=w_id)
    assert f"is held by spell_id '{y_id}'" in str(refused.value)
    _assert_only_holder_serves(world, shape, borrower, borrower_book, y_id, "Y")


@pytest.mark.parametrize("door", ["add_spell_to_contract", "add_index_to_contract"])
def test_a_borrower_cannot_bind_its_own_spell_over_a_contracted_copy(
        shape: AddressShape, world: AddressWorld, door: str,
) -> None:
    """
    Purpose:
        P09b: a borrower holding a contracted copy of the lender's spell at an address cannot bind its own spell
        there - the lender's spell holds the frame claim.

    Contract:
        - With X's copy pulled through `door`, the borrower's meld by address builds X (the lent spell).
        - `borrower.bind(Y)` raises RuntimeError "Binding signature already active in this frame" naming X; Y is not
          registered in the borrower's Book and the borrower still melds X.

    Returns:
        None.
    """
    lender_book = world.book("p09b")
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "p09b-lender")
    borrower_book = world.book("p09b")
    borrower_book.bind(spell=Ledger, existence="many", permissions="create")
    borrower = world.conjure(borrower_book, "p09b-borrower")
    borrower.link(lender)
    if door == "add_index_to_contract":
        borrower.add_index_to_contract(index=index_of(lender_book, x_id), conduit=lender)
    else:
        borrower.add_spell_to_contract(spell_id=x_id, conduit=lender)
    assert shape.letter(shape.meld(borrower)) == "X"

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(borrower, "second")

    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    assert borrower_book.find_spell_by_spell_id(shape.spell_id("second")) is None
    _assert_only_holder_serves(world, shape, borrower, borrower_book, x_id, "X")


def test_a_link_across_frames_is_refused_so_no_copy_reaches_a_frame_serving_the_address(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P09c: each frame has its own claims, so X in frame a and Y in frame b may serve one address each; a borrower
        in frame b cannot link to frame a's root to receive X's copy beside its own Y.

    Contract:
        - `borrower.link(lender)` raises RuntimeError "Cannot link conduits across different AethericFrames"; each
          root keeps serving its own spell at the address.

    Returns:
        None.
    """
    lender_book = world.book("p09c-a")
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "p09c-lender")
    borrower_book = world.book("p09c-b")
    y_id = shape.bind(borrower_book, "second")
    borrower = world.conjure(borrower_book, "p09c-borrower")

    with pytest.raises(RuntimeError, match="Cannot link conduits across different AethericFrames"):
        borrower.link(lender)

    assert AddressWorld.claim(lender_book, shape.address) == x_id
    assert AddressWorld.claim(borrower_book, shape.address) == y_id
    assert shape.letter(shape.meld(lender)) == "X"
    assert shape.letter(shape.meld(borrower)) == "Y"


def test_an_upgraded_lesser_cannot_bind_an_address_its_former_book_holds(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P10: `upgrade_to_normal` gives a lesser a new, empty Book of the same frame; that Book cannot bind a spell at
        an address the former Book's spell holds.

    Contract:
        - The upgraded root serves nothing at the address (KeyError from its meld by address).
        - Its `bind(Y)` raises RuntimeError "Binding signature already active in this frame" naming X; X alone stays
          active at the address and the former root serves it.

    Returns:
        None.
    """
    spellbook = world.book("p10")
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "p10-root")
    lesser = root.create_lesser_conduit()
    lesser.upgrade_to_normal("p10-promoted")
    world.adopt(lesser)
    with pytest.raises(KeyError):
        shape.meld(lesser)

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        shape.bind(lesser, "second")

    _assert_refused_for_the_held_address(refused.value, shape, x_id)
    _assert_only_holder_serves(world, shape, root, spellbook, x_id, "X")

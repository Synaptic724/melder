"""
Integration: a graft never puts a second spell at an address its host frame already serves.

WHY THIS EXISTS. The owner's rule (chat, 2026-11-07): two spells are never ACTIVE at one address - not two with the
same name without differentiation, not two under the same spellframe without a binding name. A graft
(`Crystallizer.graft_index`, fresh-index mode) re-integrates a recorded index into a live host Book: it binds the
recorded selection ACTIVE through `Spellbook.bind` (`GraftRunner._bind_selected`), so it meets the frame claim like
every other bind. When the host frame already serves the recorded spell's address with a spell of its own, the anchor
bind is refused with RuntimeError "Binding signature already active in this frame ... is held by
spell_id='<host spell>'", the graft raises, and nothing of the recorded spell is registered in the host.

Path P12 of `context_compass/artifacts/duplicate_address_paths_20261107/probes/duplicate_address_paths_probe.py`
(0.2.8279 and 0.2.8280, the GIL off and on). Each test runs once per shape of `tests/_one_active_spell_per_address_support.py`
(whose classes are module-level, so the graft hydrates the recorded one by qualname): X is recorded in a source frame
torn down before the graft (under process-wide spell_ids a live member cannot be grafted elsewhere), and the host
frame's Book serves the same address with its own Y. The crystallizer cache goes to a per-test directory.

Runs only on 3.14t (melder package root import chain).
"""
import json
from typing import Iterator

import pytest

from tests._one_active_spell_per_address_support import (
    AddressShape,
    AddressWorld,
    address_shape,
    address_shape_labels,
    index_of,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    _activate_crystallizer,
    cache_root,
    reset_world_singletons,
)

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("reset_world_singletons", "cache_root")]


@pytest.fixture(params=address_shape_labels())
def shape(request: pytest.FixtureRequest) -> AddressShape:
    """
    Purpose:
        Run the test once per shape that puts two spells at one address.

    Args:
        request (pytest.FixtureRequest): Carries the shape label.

    Returns:
        AddressShape: The shape's spells (X recorded, Y the host's own), their address and its meld door.
    """
    return address_shape(request.param)


@pytest.fixture()
def world() -> Iterator[AddressWorld]:
    """
    Purpose:
        Hand the test a world that keeps every Book and root it builds, then tear them down while the per-test
        crystallizer cache is still in place (this fixture is set up after `cache_root`, so it is torn down first).

    Yields:
        AddressWorld: The world.
    """
    address_world = AddressWorld()
    try:
        yield address_world
    finally:
        address_world.teardown()


def test_graft_refuses_to_bind_its_recorded_spell_at_an_address_the_host_frame_serves(
        shape: AddressShape, world: AddressWorld,
) -> None:
    """
    Purpose:
        P12: a graft of X's recorded index into a host frame whose Book serves X's address with its own Y is refused
        at the graft's anchor bind, and leaves the host as it was.

    Contract:
        - `crystallizer.graft_index(record, host_book)` raises RuntimeError "Binding signature already active in this
          frame" naming the address and Y's spell_id.
        - Nothing of X is registered in the host Book; Y alone is active at the address, holds the host frame's claim
          and is what the host root's meld by address builds.

    Returns:
        None.
    """
    crystallizer = _activate_crystallizer()
    source_book = world.book("p12-src", finalized=True)
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "p12-src")
    record = json.loads(json.dumps(crystallizer.capture_index_graft(index_of(source_book, x_id).id)))
    world.retire(source, source_book)
    host_book = world.book("p12-host", finalized=True)
    y_id = shape.bind(host_book, "second")
    host = world.conjure(host_book, "p12-host")

    with pytest.raises(RuntimeError, match="Binding signature already active in this frame") as refused:
        crystallizer.graft_index(record, host_book)

    assert f"frame_key='{shape.address[0]}', binding_name='__default__'" in str(refused.value)
    assert f"is held by spell_id='{y_id}'" in str(refused.value)
    assert host_book.find_spell_by_spell_id(x_id) is None
    assert world.active_ids_at(shape.address) == [y_id]
    assert AddressWorld.claim(host_book, shape.address) == y_id
    assert shape.letter(shape.meld(host)) == "Y"

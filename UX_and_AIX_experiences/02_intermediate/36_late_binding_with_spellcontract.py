"""
TIER: intermediate (36)
GOAL: SpellContract - the LATE-BOUND socket. A SpellMap says "resolve this
      from MY book" and must be satisfiable at conjure. A SpellContract says
      "someone will hand me this later", and stays OPEN until a linked
      conduit supplies the provider. That is the difference: SpellMap is a
      lookup, SpellContract is a PROMISE.

      The socket closes with normal verbs only - link, grant, meld. Nothing
      reaches into another book; the provider conduit GRANTS the spell across
      the link and the consumer melds as usual.

      Contracts are dynamic-mode only. In an automatic world Phase 4 refuses
      them outright, which is why this lesson settles a dynamic world first.
SURFACE EXERCISED: md.SpellContract(spellframe=..., binding_name=...),
      conduit.link(...), conduit.add_spell_to_contract(...)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _dynamic_world import dynamic_spellbook

import melder as md

from typing import Protocol


class IStore(Protocol):
    """The SHAPE the consumer depends on - not the class that provides it."""

    def get(self, key: str) -> str: ...


class PlatformStore:
    """Lives in the platform book. The consumer never imports this."""

    def get(self, key: str) -> str:
        return f"{key}-ok"


class NeedsStore:
    """
    The socket is declared as a DEFAULT VALUE on the constructor.

    Read it as: "I need something shaped like IStore, named 'platform'.
    I do not know who provides it and I am not looking it up myself."
    """

    def __init__(self, store: IStore = md.SpellContract(
            spellframe=IStore, binding_name="platform")) -> None:
        self.store = store


def main() -> None:
    # TWO SEPARATE BOOKS - two independent worlds of registration. The
    # consumer book has NO PlatformStore in it. That is the whole point:
    # if it could resolve the socket locally you would use SpellMap.
    platform_book = dynamic_spellbook()
    store_id = platform_book.bind(
        spell=PlatformStore,
        existence="unique",
        spellframe=IStore,
        binding_name="platform",
    )

    services_book = dynamic_spellbook()
    consumer_id = services_book.bind(spell=NeedsStore, existence="unique")

    # Both conjure fine even though the socket is still OPEN. An unfilled
    # contract is not a build error - that is exactly what makes it LATE
    # binding. A SpellMap that resolved to nothing would have failed here.
    platform = platform_book.conjure(dynamic=True, name="platform")
    services = services_book.conjure(dynamic=True, name="services")

    # THE LINK is the relationship. It grants nothing on its own.
    platform.link(services)

    # THE GRANT is what actually closes the socket: the borrowing side asks
    # for one spell, by id, from a named conduit, at a stated permission.
    # Narrow and explicit - not "share everything you have".
    assert services.add_spell_to_contract(
        spell_id=store_id,
        conduit=platform,
        permissions="create",
    )

    # Now meld normally. The consumer never mentions PlatformStore, never
    # touches the platform conduit, and never knew who filled the socket.
    consumer = services.meld(spell=consumer_id)
    assert isinstance(consumer, NeedsStore)
    assert consumer.store.get("region") == "region-ok"
    print("contract socket closed across the link:",
          consumer.store.get("region"))

    # WHEN TO REACH FOR WHICH:
    #   SpellMap      - the provider is in MY book. Resolve it now.
    #   SpellContract - the provider arrives from SOMEONE ELSE'S book, later.
    # If you find yourself binding a placeholder just to satisfy a SpellMap,
    # you wanted a contract.

    services.cleanup()
    platform.cleanup()


if __name__ == "__main__":
    main()

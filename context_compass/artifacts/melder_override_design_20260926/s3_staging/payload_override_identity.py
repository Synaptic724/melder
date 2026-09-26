"""Does a meld that passes its own override deliver a SpellMap payload object by identity? (families: many, unique)."""
import sys
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook


class Marker:
    """Payload object with the default repr."""


PAYLOAD = Marker()


class Service:
    def __init__(self, marker: object = None) -> None:
        self.marker = marker


class Other:
    pass


class Consumer:
    def __init__(self, other: Other, service: Service = SpellMap(spell=Service, override={"marker": PAYLOAD})) -> None:
        self.other = other
        self.service = service


for existence in ("many", "unique_per_conduit"):
    book = Spellbook(aetheric_frame=f"probe_{existence}")
    book.bind(spell=Service, existence="many")
    book.bind(spell=Other, existence="many")
    cid = book.bind(spell=Consumer, existence=existence)
    conduit = book.conjure()
    plain = conduit.meld(spell_id=cid)
    supplied = Other()
    over = conduit.meld(spell_id=cid, override={"other": supplied}) if existence == "many" else None
    print(existence, "normal identity:", plain.service.marker is PAYLOAD,
          "| override identity:", None if over is None else (over.service.marker is PAYLOAD, over.other is supplied))
    book.cleanup()

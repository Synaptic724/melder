"""The release-note example for 0.2.8215, run as written (plus the prints that show what it proves)."""
from melder import Spellbook


class Service:
    def __init__(self) -> None:
        self.value = 7


class Consumer:
    def __init__(self, service: Service) -> None:
        self.service = service


book = Spellbook(aetheric_frame="app")
root = book.conjure(name="app-root", dynamic=True)
root.bind(spell=Service, existence="unique_per_conduit")   # bound after conjure
root.bind(spell=Consumer, existence="many")
scope = root.create_lesser_conduit()
consumer = scope.meld(spell=Consumer)          # Service is built as Consumer's dependency
assert scope.meld(spell=Service) is consumer.service   # raised RuntimeError before 0.2.8215
print("direct meld returns the injected instance:", scope.meld(spell=Service) is consumer.service)
print("value:", consumer.service.value)

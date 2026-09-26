"""Does a consumer's cached payload go stale when its provider's spell id changes between processes?

PROBE_ENGINE_VARIANT selects the provider constructor signature (A or B), so the provider's spell id changes
while the consumer's does not. Run: A, B, B in three fresh processes against one melder package root.
"""
import marshal
import os

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

VARIANT = os.environ["PROBE_ENGINE_VARIANT"]

if VARIANT == "A":
    class Engine:
        """Provider, variant A."""

        def __init__(self) -> None:
            self.variant = "A"
else:
    class Engine:
        """Provider, variant B (different constructor signature)."""

        def __init__(self, size: int = 2) -> None:
            self.variant = "B"


class Car:
    """Consumer whose own spell id does not depend on the provider."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine


book = Spellbook(aetheric_frame="fsid-stale-consumer")
engine_id = book.bind(spell=Engine, existence=Existence.unique, permissions="create")
car_id = book.bind(spell=Car, existence=Existence.many, permissions="create")
caching_system_before = None
conduit = book.conjure(name="fsid-stale-consumer")
bundle = marshal.loads(book._caching_system._bundle_path.read_bytes())
print(f"variant={VARIANT} engine={engine_id[:12]} car={car_id[:12]} cached={sorted(k[:12] for k in bundle['spell_payloads'])}")
car = conduit.meld(spell=Car)
print("car.engine variant:", car.engine.variant, "| engine is unique:", car.engine is conduit.meld(spell=Engine))

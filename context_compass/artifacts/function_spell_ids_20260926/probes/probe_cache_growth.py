"""One process: bind a class and a function spell, conjure, meld, then report the conduit cache bundle.

Run it several times in fresh processes against the same melder package root to see whether the cache
reaches a full hit and whether the bundle grows.
"""
import marshal
import sys

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

import probe_user_shapes as shapes


class Car:
    """Consumer of the function-built Engine."""

    def __init__(self, engine: shapes.Engine) -> None:
        self.engine = engine


book = Spellbook(aetheric_frame="fsid-cache-probe")
book.bind(spell=shapes.make_engine, spellframe=shapes.Engine, existence=Existence.unique, permissions="create")
book.bind(spell=Car, existence=Existence.many, permissions="create")
conduit = book.conjure(name="fsid-cache-probe")
car = conduit.meld(spell=Car)
caching_system = book._caching_system
bundle = marshal.loads(caching_system._bundle_path.read_bytes())
live = sorted(sid[:12] for sid, spell in book._spell_id_pool.items())
print("live spell ids:", live)
print("bundle payload ids:", sorted(k[:12] for k in bundle["spell_payloads"]))
print("bundle payload count:", len(bundle["spell_payloads"]), "bytes:", caching_system._bundle_path.stat().st_size)
sys.stdout.flush()

from typing import Any, Optional

class SpellMap:
    """
    SpellMap is a lightweight declarative placeholder used during object construction
    to signal that a specific spell should be injected at this location.

    It mirrors the `meld()` interface but performs no resolution until runtime.
    It is used by `SpellCrafter` to extract spell declarations and build the `_Creations` DAG.

    ─────────────────────────────────────────────
    ✅ You do NOT subclass SpellMap.
    ✅ You instantiate it inside a constructor or as a default param.
    ✅ You use it to describe *intent*, and `meld(...)` replaces it with the real spell.

    ─────────────────────────────────────────────
    🔧 Example Usage:

        class MyModel:
            def __init__(self, logic: ILogic = SpellMap(MyParser, spellframe=ILogic)):
                self.logic = logic  # Gets replaced during `meld(...)`

        class MyOtherModel:
            def __init__(self):
                self.db = SpellMap(Postgres, spell_override={"dsn": "localhost"})
                self.logic = SpellMap(ILogic, binding_name="primary")

    ─────────────────────────────────────────────
    Attributes:
        spell : Any
            The target spell (class, function, UUID, etc.)

        spellframe : Optional[Any]
            Interface, protocol, or category used for spell grouping.

        binding_name : Optional[str]
            Named lookup key for disambiguation.

        spell_override (dict | list | tuple, optional):
            Optional override to inject custom arguments when creating the spell.
    """

    __slots__ = ("spell", "spellframe", "binding_name", "override")

    def __init__(
        self,
        spell: Any,
        *,
        spellframe: Optional[Any] = None,
        binding_name: Optional[str] = None,
        spell_override: Optional[dict | list | tuple] = None
    ):
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.override = spell_override or {}

    @property
    def spell_key(self) -> tuple[str, str]:
        spell_name = getattr(self.spell, "__name__", str(self.spell))
        return (self.spellframe or spell_name, self.binding_name or "__default__")

    def __repr__(self):
        return (
            f"<SpellMap spell={self.spell} frame={self.spellframe} "
            f"binding_name={self.binding_name}>"
        )

#───────────────────────────────────────────────────────────────────────────────

class SM:
    """
    SM is a shorthand alias for `SpellMap` to allow faster typing and cleaner syntax.

    It uses abbreviated lowercase parameter names:
        - s  = spell
        - sf = spellframe
        - bn = binding_name
        - so = spell_override

    🔧 Example Usage:

        self.cache = SM(s=CacheService, sf=ICache, bn="local", so={"ttl": 300})

    Equivalent to:

        self.cache = SpellMap(CacheService, spellframe=ICache, binding_name="local", spell_override={"ttl": 300})
    """

    __slots__ = ("s", "sf", "bn", "so")

    def __init__(
        self,
        s: Any,
        *,
        sf: Optional[Any] = None,
        bn: Optional[str] = None,
        so: Optional[dict | list | tuple] = None
    ):
        self.s = s
        self.sf = sf
        self.bn = bn
        self.so = so or {}

    @property
    def spell_key(self) -> tuple[str, str]:
        spell_name = getattr(self.s, "__name__", str(self.s))
        return (self.sf or spell_name, self.bn or "__default__")

    def __repr__(self):
        return (
            f"<SM s={self.s} sf={self.sf} bn={self.bn}>"
        )

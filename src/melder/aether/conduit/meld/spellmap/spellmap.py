from typing import Dict, Generic, TypeVar, Optional, Iterator

T = TypeVar("T")


class SpellMap(Generic[T]):
    """
    A named spell dispatcher for a given interface type.

    Typically injected into constructors when multiple named implementations
    of the same interface exist. Allows access by key (e.g., 'json', 'xml').

    Usage:
        parser = spellmap["json"]
        parser.parse(data)

        all_parsers = spellmap.all()
    """

    def __init__(self, spells: Dict[str, T]):
        self._spells: Dict[str, T] = spells

    def __getitem__(self, key: str) -> T:
        return self._spells[key]

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        return self._spells.get(key, default)

    def dispatch(self, key: str, *args, **kwargs):
        return self._spells[key](*args, **kwargs)

    def all(self) -> Dict[str, T]:
        return self._spells

    def keys(self) -> Iterator[str]:
        return self._spells.keys()

    def values(self) -> Iterator[T]:
        return self._spells.values()

    def items(self) -> Iterator[tuple[str, T]]:
        return self._spells.items()

    def __contains__(self, key: str) -> bool:
        return key in self._spells

    def __repr__(self) -> str:
        return f"<SpellMap keys={list(self._spells.keys())}>"

#Example just like autofac
# class ParserDispatcher:
#     def __init__(self, parsers: SpellMap[IParser]):
#         # SpellMap is injected here like Autofac's IIndex<string, IParser>
#         self._parsers = parsers
#         self._default = self._parsers["json"]  # Pick one manually
#
#     def parse(self, type: str, data: str) -> dict:
#         return self._parsers[type].parse(data)
#
#     def parse_default(self, data: str) -> dict:
#         return self._default.parse(data)


#
# registry = SpellRegistry()
#
# # Bind named spell handlers
# registry.bind_named("json", JsonParser, spellframe=IParser)
# registry.bind_named("xml", XmlParser, spellframe=IParser)
#
# # Simulated container injection:
# def inject_parser_dispatcher():
#     bound = registry.interface_index["iparser"]
#     map = SpellMap({
#         name: registry.resolve_named(name).profile.cls()
#         for name in bound
#     })
#     return ParserDispatcher(map)

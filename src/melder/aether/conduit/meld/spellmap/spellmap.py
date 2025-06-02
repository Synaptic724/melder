from typing import Dict, Generic, TypeVar, Optional, Iterator

T = TypeVar("T")
# TODO: We will need to have enumerable injection for the spellmap, so that we can inject a list of spells that match a certain interface

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


# ──────────────────────────────────────────────────────────────────────────────
# 🧠 TODO: Implement SpellMap and MethodMap Separation
#
# Melder currently stores all spells in a single unified dictionary (_spells),
# but for clarity and faster access patterns, we should split spells into:
#
# 1. SpellMap    — for class-based/service spells (SpellType.CLASS-derived)
# 2. MethodMap   — for method/lambda/function spells (SpellType.METHOD-derived)
#
# 🔧 Why?
# - Enables type-safe operations (e.g., casting only class spells from one map)
# - Improves lookup logic during DAG execution and reflection
# - Lets us build specialized tooling for each spell type
#
# 🎯 Action Plan:
# - [ ] Create internal SpellMap and MethodMap dictionaries
# - [ ] Update bind() to insert into the correct map based on SpellType
# - [ ] Refactor resolve logic (Meld) to query the appropriate map
# - [ ] Build diagnostics: print all class spells, all method spells, etc.
# - [ ] Optional: Add a unified API for read-only merged view (if needed)
#
# 📌 Key Insight:
# SpellType already encodes all needed type info. Let that guide partitioning.
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# 🧙 Melder Spell Entry Matrix — Autofac-style Constructor Injection
#
# This matrix shows how to bind, resolve, and inject spells using Melder’s spellmaps.
# It mirrors Autofac’s DI model, especially for named/multi-resolution logic.
#
# spellname        — Method/class name being bound
# interface        — Optional SpellFrame (grouping interface)
# binding_name     — Optional user label for disambiguation
# bind(...)        — How the spell is registered
# meld(...)        — How the spell is resolved
# constructor_injection — How to inject it into a class
#───────────────────────────────────────────────────────────────────────────────
# SpellType                  | spellname         | interface           | binding_name | bind(...)                                             | meld(...)                              | constructor_injection
#────────────────────────────|-------------------|----------------------|---------------|-------------------------------------------------------|----------------------------------------|-------------------------------------------
# NORMAL                     | "MyService"       | None                 | None          | bind(MyService)                                      | meld(MyService)                        | def __init__(self, svc: MyService)
# NAMED                      | "MyService"       | None                 | "alpha"       | bind(MyService, name="alpha")                        | meld(MyService, name="alpha")          | def __init__(self, svcs: dict[str, MyService]): svc = svcs["alpha"]
# NORMAL_INTERFACED          | "MyService"       | IMyService           | None          | bind(MyService, spellframe=IMyService)               | meld(IMyService)                       | def __init__(self, svc: IMyService)
# NAMED_INTERFACED           | "MyService"       | IMyService           | "v1"          | bind(MyService, spellframe=IMyService, name="v1")    | meld(IMyService, name="v1")            | def __init__(self, svcs: dict[str, IMyService]): svc = svcs["v1"]
# EXISTING_CLASS             | "MyService"       | None                 | None          | bind(my_service_instance)                            | meld(MyService)                        | def __init__(self, svc: MyService)
# EXISTING_INTERFACED_CLASS  | "MyService"       | IMyService           | None          | bind(my_service_instance, spellframe=IMyService)     | meld(IMyService)                       | def __init__(self, svc: IMyService)
# NORMAL_METHOD              | "process_data"    | None                 | None          | bind(process_data)                                   | meld(process_data)                     | def __init__(self, fn: Callable): result = fn()
# NAMED_METHOD               | "process_data"    | None                 | "process"     | bind(process_data, name="process")                   | meld("process")                        | def __init__(self, fns: dict[str, Callable]): result = fns["process"]()
# NAMED_METHOD (interfaced)  | "process_data"    | IDataPipeline        | "process"     | bind(process_data, name="process", spellframe=...)   | meld(IDataPipeline, name="process")    | def __init__(self, fns: dict[str, Callable]): result = fns["process"]()
# NAMED_LAMBDA_METHOD        | "<lambda>"        | IMathOps             | "scale"       | bind(lambda x: x+1, name="scale", spellframe=...)    | meld(IMathOps, name="scale")           | def __init__(self, mathops: dict
# ──────────────────────────────────────────────────────────────────────────────



# ──────────────────────────────────────────────────────────────────────────────
# 🧠 Autofac Constructor Injection Patterns — Reference for Melder Injection Logic
#
# This block explains how Autofac performs injection and how we should mirror that
# behavior in Melder using `meld(...)`, `spellmaps[...]`, and other patterns.
#
# ✅ Standard (Unnamed) Injection
# Autofac:
#   builder.RegisterType[MyService]().As[IMyService]()
#   Constructor:
#       def __init__(self, service: IMyService): ...
#
# Melder:
#   bind(MyService, spellframe=IMyService)
#   Constructor:
#       def __init__(self, service: IMyService): ...
#
# 🔐 Named Injection (using a label/key)
# Autofac:
#   builder.RegisterType[MyService]().Named[IMyService]("alpha")
#   Constructor:
#       def __init__(self, services: IIndex[str, IMyService]):
#           self._service = services["alpha"]
#
# Melder:
#   bind(MyService, name="alpha", spellframe=IMyService)
#   Constructor:
#       def __init__(self, services: dict[str, IMyService]):
#           self._service = services["alpha"]
#   or
#       def __init__(self, spellmaps: SpellMap):
#           self._service = spellmaps[IMyService]["alpha"]
#
# 🧩 Multiple Implementations (all registered services)
# Autofac:
#   builder.RegisterType[AlphaService]().As[IMyService]()
#   builder.RegisterType[BetaService]().As[IMyService]()
#   Constructor:
#       def __init__(self, services: list[IMyService]): ...
#
# Melder:
#   bind(AlphaService, spellframe=IMyService)
#   bind(BetaService, spellframe=IMyService)
#   Constructor:
#       def __init__(self, services: list[IMyService]): ...
#   or (explicit helper)
#       services = meld_all(IMyService)
#
# 🛠 Factory Injection (runtime key-based access)
# Autofac:
#   def __init__(self, factory: Callable[[str], IMyService]):
#       self._svc = factory("alpha")
#
# Melder:
#   def __init__(self, resolver: Callable[[str], IMyService]):
#       self._svc = resolver("alpha")
#
#       # This can be generated by:
#       factory = lambda name: spellmaps[IMyService].get(name)
# ──────────────────────────────────────────────────────────────────────────────

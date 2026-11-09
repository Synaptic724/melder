"""Matrix probe (melder_0, 2026-11-07; STORY-2026-10-25-map_dependency_watchers_and_announcers, S1 of
EPIC-2026-10-25-dependency_watchers_listen_for_names): for each cell - a socket kind, an annotation kind, a provider
binding shape and a change event - does a consumer's next meld see the change?

Oracle. After the event the consumer is melded as it stands (LIVE); then it is disposed, bound again and melded
(FRESH - what Phase 3 compiles from the pool as it now is). LIVE == FRESH is OK; any difference is a MISS: the
consumer is stuck on a provider that is gone, or blind to one that arrived. Outcomes are the qualname of the
greeter the consumer holds, the sorted qualnames of a collection, or "raises <Type>".

Behaviour comes from public calls only. The [diag] lines read internals for the diagnosis, labelled so: the
consumer's validity and sockets (kind, dependency_key), and every mark the step made, recorded through class-level
wrappers installed in this process only -
  watch  SpellSystemStates.mark_collection_dependents_dirty: the frame keys announced -> the consumers reached
  edge   SpellSystemStates.compute_impact_closure: the index ids seeded -> the dependents reached by registry edge
  walk   SpellSystemStates.mark_dependents_for_revalidation: a notch's downstream walk

One cell per process (each process is a fresh Aether):
    python probe_watcher_announcer_matrix.py <cell>
    python probe_watcher_announcer_matrix.py --list
"""
import re
import sys
from typing import Any, Callable, Dict, List, Protocol

import melder as md
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates


class Greeter(Protocol):
    """The contract a framed provider is checked against."""

    def greet(self) -> str: ...


class English:
    """The provider every consumer names."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Another class: the second version a notch moves to."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Edited:
    """Namespace for a second class whose __name__ is English: another spell_id, the same type key."""

    class English:
        """An edited English: the same name, other code."""

        def greet(self) -> str:
            """Return the edited greeting."""
            return "hello again"


class ByClass:
    """A single socket by a class annotation (type kind)."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


class ByProtocol:
    """A single socket by a Protocol annotation (contract kind)."""

    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class ByName:
    """A single socket by a string annotation (name kind: type or contract keys)."""

    def __init__(self, greeter: "English") -> None:
        self.greeter = greeter


class ListByClass:
    """A collection of a class (type kind)."""

    def __init__(self, greeters: list[English]) -> None:
        self.greeters = greeters


class ListByProtocol:
    """A collection of a Protocol (contract kind)."""

    def __init__(self, greeters: list[Greeter]) -> None:
        self.greeters = greeters


class ListByLabel:
    """A collection written as a name (name kind on a collection: the address label)."""

    def __init__(self, greeters: list["langs"]) -> None:
        self.greeters = greeters


class CycB:
    """Phase 4 cells: the class CycA names, bound under the category 'q'."""

    def __init__(self) -> None:
        self.ready = True


class CycA:
    """Phase 4 cells: needs CycB by class annotation; bound bare at ('cyca', '__default__')."""

    def __init__(self, b: CycB) -> None:
        self.b = b


class CycZ:
    """Phase 4 cells: needs CycA; bound under a category whose name may equal CycA's annotated name."""

    def __init__(self, a: CycA) -> None:
        self.a = a


SHAPES: Dict[str, Dict[str, Any]] = {
    "bare": {},
    "category": {"spellframe": "langs"},
    "protocol": {"spellframe": Greeter, "binding_name": "greeter"},
}
BOOKS: List[Any] = []
MARKS: List[tuple] = []


def install_mark_recorders() -> None:
    """Wrap the three SpellSystemStates mark entry points to record what each step marks (diagnosis only)."""
    original_watch = SpellSystemStates.mark_collection_dependents_dirty
    original_closure = SpellSystemStates.compute_impact_closure
    original_walk = SpellSystemStates.mark_dependents_for_revalidation

    def watch(self, *, spellbook_id, frame_keys, change_reason=None):
        keys = sorted({key for key in frame_keys if key})
        impacted = original_watch(self, spellbook_id=spellbook_id, frame_keys=keys, change_reason=change_reason)
        MARKS.append(("watch", tuple(keys), tuple(sorted(impacted))))
        return impacted

    def closure(self, root_index_ids):
        roots = tuple(root_index_ids)
        impacted = original_closure(self, roots)
        MARKS.append(("edge", roots, tuple(sorted(impacted))))
        return impacted

    def walk(self, index_ids):
        seeds = tuple(index_id for index_id in index_ids if index_id)
        impacted = original_walk(self, seeds)
        MARKS.append(("walk", seeds, tuple(sorted(impacted))))
        return impacted

    SpellSystemStates.mark_collection_dependents_dirty = watch
    SpellSystemStates.compute_impact_closure = closure
    SpellSystemStates.mark_dependents_for_revalidation = walk


def index_names() -> Dict[str, str]:
    """Map live index ids to spell names across the cell's Books (internal read, diagnosis only)."""
    names: Dict[str, str] = {}
    for book in BOOKS:
        try:
            pool = list(book._spell_id_pool.values())
        except Exception:
            continue
        for spell in pool:
            try:
                names[spell.spell_index.id] = spell.spell_name
            except Exception:
                continue
    return names


def show_marks() -> None:
    """Print the marks recorded since the last step, ids rendered as names where the pool still has them."""
    names = index_names()
    for kind, keys, impacted in list(MARKS):
        seeds = list(keys) if kind == "watch" else [names.get(key, key[:8]) for key in keys]
        reached = [names.get(index_id, index_id[:8]) for index_id in impacted]
        print("    [diag] %-5s %s -> %s" % (kind, seeds, reached))
    MARKS.clear()


def step(label: str, call: Callable[[], Any]) -> str:
    """Run one public call, print its outcome and the marks it made, and return the outcome string."""
    MARKS.clear()
    detail = ""
    try:
        value = call()
        outcome = value if isinstance(value, str) else "ok"
    except Exception as error:
        outcome = "raises %s" % type(error).__name__
        text = str(error)
        codes = sorted(set(re.findall(r"\[([A-Z][A-Z_]+)\]", text)))
        detail = (text.splitlines() or [""])[0][:110] + (" codes=%s" % codes if codes else "")
    print("  %-56s -> %s%s" % (label, outcome, (": " + detail) if detail else ""))
    show_marks()
    return outcome


def diag(book: Any, consumer_id: str) -> None:
    """Print the consumer's lineage validity and its recorded sockets (internal reads, diagnosis only)."""
    states = book._spell_system_states
    spell = book.find_spell_by_spell_id(consumer_id)
    if spell is None:
        print("    [diag] consumer not registered")
        return
    state = states.get_by_index_id(spell.spell_index.id)
    topology = states.get_local_topology_by_id(consumer_id)
    sockets = [] if topology is None else [(s.socket_kind.name, s.dependency_key) for s in topology.iter_sockets()]
    print("    [diag] consumer validity %s; sockets %s" % (state.validity.name if state else None, sockets))


def meld_single(world: Any, consumer_id: str) -> str:
    """Meld a single-socket consumer and name the greeter it holds."""
    return type(world.meld(spell_id=consumer_id).greeter).__qualname__


def meld_list(world: Any, consumer_id: str) -> str:
    """Meld a collection consumer and name the greeters it holds, sorted."""
    return "[%s]" % ", ".join(sorted(type(item).__qualname__ for item in world.meld(spell_id=consumer_id).greeters))


def label_of(provider: Any) -> str:
    """Name a provider: a class by qualname, an existing object as Class()."""
    return provider.__qualname__ if isinstance(provider, type) else "%s()" % type(provider).__qualname__


def bind_after(world: Any, provider: Any, shape: str, existence: str = "many", **extra: Any) -> str:
    """Bind a provider through the conduit after conjure and report its address."""
    spell_id = world.bind(spell=provider, existence=existence, permissions="create", **SHAPES[shape], **extra)
    return "ok, at %s/%s" % world.get_spell_by_spell_id(spell_id).key


def fresh_compile(world: Any, consumer: type, consumer_id: str, meld: Callable[[Any, str], str]) -> str:
    """Dispose the consumer, bind it again and meld it: what a fresh compile gives (the oracle)."""
    def run() -> str:
        world.cleanup_spell(spell=world.get_spell_by_spell_id(consumer_id))
        rebound = world.bind(spell=consumer, existence="many", permissions="create")
        return meld(world, rebound)
    return step("dispose + bind the consumer again, meld (FRESH)", run)


def verdict(live: str, fresh: str, note: str = "") -> None:
    """Print the cell's verdict: OK when LIVE equals FRESH, MISS otherwise."""
    print("  VERDICT: %s - live %s; fresh %s%s" % ("OK" if live == fresh else "MISS", live, fresh,
                                                  ("; " + note) if note else ""))


def new_book() -> Any:
    """A Spellbook in the default frame, remembered for the diagnosis maps."""
    book = md.Spellbook()
    BOOKS.append(book)
    return book


def arrival(consumer: type, meld: Callable, provider: Any, shape: str, existence: str = "many",
            before: tuple = ()) -> None:
    """A consumer conjured with no matching provider; the provider bound after conjure."""
    book = new_book()
    for spell, spell_shape, extra in before:
        book.bind(spell=spell, existence="many", permissions="create", **SHAPES[spell_shape], **extra)
    consumer_id = book.bind(spell=consumer, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    step("meld the consumer (no provider yet)", lambda: meld(world, consumer_id))
    diag(book, consumer_id)
    step("bind %s after conjure (%s)" % (label_of(provider), shape),
         lambda: bind_after(world, provider, shape, existence))
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld(world, consumer_id))
    verdict(live, fresh_compile(world, consumer, consumer_id, meld))


def notch_back(consumer: type, meld: Callable, shape: str, second: type) -> None:
    """English active, `second` staged on its index; notch away to `second`, then back to English."""
    book = new_book()
    english_id = book.bind(spell=English, existence="many", permissions="create", **SHAPES[shape])
    consumer_id = book.bind(spell=consumer, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(english_id).spell_index
    second_id = world.bind_inactive(spell=second, spell_index=index, existence="many", permissions="create",
                                    **SHAPES[shape])
    step("meld the consumer (English active)", lambda: meld(world, consumer_id))
    step("notch to %s" % second.__qualname__,
         lambda: world.notch_spell(spell_index=index, spell_id=second_id).spell_name)
    step("meld the consumer (%s active)" % second.__qualname__, lambda: meld(world, consumer_id))
    diag(book, consumer_id)
    step("notch back to English", lambda: world.notch_spell(spell_index=index, spell_id=english_id).spell_name)
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE, English active again)", lambda: meld(world, consumer_id))
    verdict(live, fresh_compile(world, consumer, consumer_id, meld))


def cell_index_moves() -> None:
    """I1: a parked version moved out of its index and back; the active provider never changes."""
    book = new_book()
    english_id = book.bind(spell=English, existence="many", permissions="create", spellframe="langs")
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(english_id).spell_index
    french_id = world.bind_inactive(spell=French, spell_index=index, existence="many", permissions="create",
                                    spellframe="langs")
    step("meld the consumer (English active, French parked)", lambda: meld_single(world, consumer_id))
    step("remove_from_spell_index(French)",
         lambda: (world.remove_from_spell_index(spell_id=french_id, source_index=index), "ok")[1])
    step("meld the consumer", lambda: meld_single(world, consumer_id))
    step("add_to_spell_index(French, back into English's index)",
         lambda: (world.add_to_spell_index(spell_id=french_id, target_index=index), "ok")[1])
    live = step("meld the consumer (LIVE)", lambda: meld_single(world, consumer_id))
    verdict(live, fresh_compile(world, ByClass, consumer_id, meld_single))


def cell_notch_to_wanted() -> None:
    """I2: French active under 'langs'; English staged (bind_inactive) and notched in; ByClass waited from conjure."""
    book = new_book()
    french_id = book.bind(spell=French, existence="many", permissions="create", spellframe="langs")
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(french_id).spell_index
    step("meld the consumer (French active)", lambda: meld_single(world, consumer_id))
    english_box: Dict[str, str] = {}

    def stage() -> str:
        english_box["id"] = world.bind_inactive(spell=English, spell_index=index, existence="many",
                                                permissions="create", spellframe="langs")
        return "ok"
    step("bind_inactive English onto the 'langs' index", stage)
    step("meld the consumer (English parked)", lambda: meld_single(world, consumer_id))
    diag(book, consumer_id)
    step("notch to English", lambda: world.notch_spell(spell_index=index, spell_id=english_box["id"]).spell_name)
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE, English active)", lambda: meld_single(world, consumer_id))
    verdict(live, fresh_compile(world, ByClass, consumer_id, meld_single))


def competitor_world() -> tuple:
    """English bare and ByClass conjured (ByClass resolved); then Edited.English bound under 'langs'."""
    book = new_book()
    book.bind(spell=English, existence="many", permissions="create")
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    step("meld the consumer (English only)", lambda: meld_single(world, consumer_id))
    diag(book, consumer_id)
    box: Dict[str, str] = {}

    def bind_competitor() -> str:
        box["id"] = world.bind(spell=Edited.English, existence="many", permissions="create", spellframe="langs")
        return "ok, at %s/%s" % world.get_spell_by_spell_id(box["id"]).key
    step("bind Edited.English after conjure (category)", bind_competitor)
    diag(book, consumer_id)
    return book, world, consumer_id, box["id"]


def cell_competitor_arrives() -> None:
    """E1: a second matching provider arrives for a resolved single socket (NORMAL single is not watched)."""
    book, world, consumer_id, _ = competitor_world()
    live = step("meld the consumer (LIVE)", lambda: meld_single(world, consumer_id))
    verdict(live, fresh_compile(world, ByClass, consumer_id, meld_single))


def cell_competitor_leaves() -> None:
    """D1: ByClass compiled AMBIGUOUS between two providers; one of them disposed with cleanup_spell."""
    book, world, consumer_id, competitor_id = competitor_world()
    step("dispose + bind the consumer again (compile it AMBIGUOUS)",
         lambda: (world.cleanup_spell(spell=world.get_spell_by_spell_id(consumer_id)),
                  world.bind(spell=ByClass, existence="many", permissions="create"), "ok")[2])
    diag(book, consumer_id)
    if book.find_spell_by_spell_id(consumer_id) is None:
        print("  VERDICT: BLOCKED - the AMBIGUOUS consumer is not registered after its refused bind")
        return
    step("meld the consumer (two providers)", lambda: meld_single(world, consumer_id))
    step("cleanup_spell(Edited.English)",
         lambda: (world.cleanup_spell(spell=world.get_spell_by_spell_id(competitor_id)), "ok")[1])
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE, one provider left)", lambda: meld_single(world, consumer_id))
    verdict(live, fresh_compile(world, ByClass, consumer_id, meld_single))


def cell_member_leaves() -> None:
    """D2: a collection with two members; one disposed with cleanup_spell (members are registry edges)."""
    book = new_book()
    book.bind(spell=English, existence="many", permissions="create")
    edited_id = book.bind(spell=Edited.English, existence="many", permissions="create", spellframe="langs")
    consumer_id = book.bind(spell=ListByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    step("meld the consumer (two members)", lambda: meld_list(world, consumer_id))
    step("cleanup_spell(Edited.English)",
         lambda: (world.cleanup_spell(spell=world.get_spell_by_spell_id(edited_id)), "ok")[1])
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld_list(world, consumer_id))
    verdict(live, fresh_compile(world, ListByClass, consumer_id, meld_list))


def cell_provider_leaves() -> None:
    """D3: a resolved single socket whose provider is disposed with cleanup_spell (a registry edge)."""
    book = new_book()
    english_id = book.bind(spell=English, existence="many", permissions="create")
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    step("meld the consumer", lambda: meld_single(world, consumer_id))
    step("cleanup_spell(English)",
         lambda: (world.cleanup_spell(spell=world.get_spell_by_spell_id(english_id)), "ok")[1])
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld_single(world, consumer_id))
    again = step("meld the consumer again (LIVE, second meld)", lambda: meld_single(world, consumer_id))
    diag(book, consumer_id)
    verdict(live, fresh_compile(world, ByClass, consumer_id, meld_single),
            "the second live meld %s" % again)


def two_roots(owner_spells: tuple, consumer_spells: tuple) -> tuple:
    """An owner Book and a borrower Book in the default frame, both conjured dynamic."""
    owner_book, borrower_book = new_book(), new_book()
    ids: Dict[str, str] = {}
    for key, spell, shape in owner_spells:
        ids[key] = owner_book.bind(spell=spell, existence="many", permissions="create", **SHAPES[shape])
    for key, spell, shape in consumer_spells:
        ids[key] = borrower_book.bind(spell=spell, existence="many", permissions="create", **SHAPES[shape])
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    return owner_book, borrower_book, owner, borrower, ids


def borrowed(shape: str, then_leave: bool = False) -> None:
    """G: ByClass waits in the borrower; the owner's English arrives by link + add_spell_to_contract."""
    _, book, owner, borrower, ids = two_roots((("english", English, shape),), (("consumer", ByClass, "bare"),))
    consumer_id = ids["consumer"]
    step("meld the consumer in the borrower", lambda: meld_single(borrower, consumer_id))
    diag(book, consumer_id)
    step("owner.link(borrower)", lambda: str(owner.link(borrower)))
    step("borrower.add_spell_to_contract(English, owner)",
         lambda: str(borrower.add_spell_to_contract(spell_id=ids["english"], conduit=owner, permissions="create")))
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld_single(borrower, consumer_id))
    fresh = fresh_compile(borrower, ByClass, consumer_id, meld_single)
    if not then_leave:
        verdict(live, fresh)
        return
    print("  (arrival: live %s, fresh %s; the consumer is now compiled against the borrowed copy)" % (live, fresh))

    def remove() -> str:
        with borrower.transaction("link", conduits=[borrower, owner]):
            return str(borrower.remove_spell_from_contract(spell_id=ids["english"], conduit=owner))
    step("borrower.remove_spell_from_contract(English, owner)", remove)
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE, contract removed)", lambda: meld_single(borrower, consumer_id))
    verdict(live, fresh_compile(borrower, ByClass, consumer_id, meld_single))


def transferred(shape: str) -> None:
    """H1/H2: ByClass waits in the target root; the owner transfers English to it."""
    _, book, owner, target, ids = two_roots((("english", English, shape),), (("consumer", ByClass, "bare"),))
    consumer_id = ids["consumer"]
    step("meld the consumer in the target", lambda: meld_single(target, consumer_id))
    diag(book, consumer_id)
    step("owner.transfer_spell_ownership(English -> target)",
         lambda: (owner.transfer_spell_ownership(spell=ids["english"], target_conduit=target), "ok")[1])
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld_single(target, consumer_id))
    verdict(live, fresh_compile(target, ByClass, consumer_id, meld_single))


def cell_transfer_leaves() -> None:
    """H3: ByClass resolved in its own root; that root transfers English away."""
    _, book, other, home, ids = two_roots((("french", French, "bare"),),
                                          (("english", English, "bare"), ("consumer", ByClass, "bare")))
    consumer_id = ids["consumer"]
    step("meld the consumer at home", lambda: meld_single(home, consumer_id))
    step("home.transfer_spell_ownership(English -> other)",
         lambda: (home.transfer_spell_ownership(spell=ids["english"], target_conduit=other), "ok")[1])
    diag(book, consumer_id)
    live = step("meld the consumer (LIVE)", lambda: meld_single(home, consumer_id))
    verdict(live, fresh_compile(home, ByClass, consumer_id, meld_single))


def override_required(definition: type, definition_shape: str, consumer: type, provider: type, shape: str) -> None:
    """F: the consumer's only match is a definition bound resolvable=False (OVERRIDE_REQUIRED); a provider arrives."""
    arrival(consumer, meld_single, provider, shape,
            before=((definition, definition_shape, {"resolvable": False}),))


def binding_cycle(z_frame: str) -> None:
    """P1: CycA (bare) needs CycB (category 'q'); CycZ (category z_frame) needs CycA. No real cycle exists."""
    book = new_book()
    book.bind(spell=CycB, existence="many", permissions="create", spellframe="q")
    a_id = book.bind(spell=CycA, existence="many", permissions="create")
    z_id = book.bind(spell=CycZ, existence="many", permissions="create", spellframe=z_frame)
    box: Dict[str, Any] = {}

    def conjure() -> str:
        box["world"] = book.conjure(dynamic=True, name="world")
        return "ok"
    outcome = step("conjure (CycZ under category %r)" % z_frame, conjure)
    if "world" in box:
        step("meld CycA", lambda: type(box["world"].meld(spell_id=a_id).b).__qualname__)
        step("meld CycZ", lambda: type(box["world"].meld(spell_id=z_id).a).__qualname__)
    note = "the same world with CycZ under 'zz' is cell P1b"
    print("  VERDICT: %s - conjure %s; %s" % ("OK" if outcome == "ok" else "MISS", outcome, note))


CELLS: Dict[str, tuple] = {
    "A1": ("single class English | provider bare | bind after conjure",
           lambda: arrival(ByClass, meld_single, English, "bare")),
    "A2": ("single class English | provider category 'langs' | bind after conjure",
           lambda: arrival(ByClass, meld_single, English, "category")),
    "A3": ("single class English | provider Protocol frame (Greeter,'greeter') | bind after conjure",
           lambda: arrival(ByClass, meld_single, English, "protocol")),
    "A4": ("single class English | existing object bare | bind after conjure",
           lambda: arrival(ByClass, meld_single, English(), "bare", existence="unique")),
    "A5": ("single class English | existing object category 'langs' | bind after conjure",
           lambda: arrival(ByClass, meld_single, English(), "category", existence="unique")),
    "A6": ("single Protocol Greeter | provider Protocol frame | bind after conjure",
           lambda: arrival(ByProtocol, meld_single, English, "protocol")),
    "A7": ("single name 'English' | provider bare | bind after conjure",
           lambda: arrival(ByName, meld_single, English, "bare")),
    "A8": ("single name 'English' | provider category 'langs' | bind after conjure",
           lambda: arrival(ByName, meld_single, English, "category")),
    "A9": ("single name 'English' | provider Protocol frame | bind after conjure",
           lambda: arrival(ByName, meld_single, English, "protocol")),
    "A10": ("single Protocol Greeter | provider category named 'greeter' (no match) | bind after conjure",
            lambda: arrival(ByProtocol, meld_single, English, "category_greeter")),
    "B1": ("collection list[English] | provider bare | bind after conjure",
           lambda: arrival(ListByClass, meld_list, English, "bare")),
    "B2": ("collection list[English] | provider category 'langs' | bind after conjure",
           lambda: arrival(ListByClass, meld_list, English, "category")),
    "B3": ("collection list[English] | provider Protocol frame | bind after conjure",
           lambda: arrival(ListByClass, meld_list, English, "protocol")),
    "B4": ("collection list[Greeter] | provider Protocol frame | bind after conjure",
           lambda: arrival(ListByProtocol, meld_list, English, "protocol")),
    "B5": ("collection list['langs'] | provider category 'langs' | bind after conjure",
           lambda: arrival(ListByLabel, meld_list, English, "category")),
    "C1": ("single class English | index under Protocol frame | notch away to French and back",
           lambda: notch_back(ByClass, meld_single, "protocol", French)),
    "C2": ("single class English | index under category 'langs' | notch away to French and back",
           lambda: notch_back(ByClass, meld_single, "category", French)),
    "C3": ("single Protocol Greeter | index under Protocol frame | notch to French and back",
           lambda: notch_back(ByProtocol, meld_single, "protocol", French)),
    "C4": ("collection list[English] | index under category 'langs' | notch away to French and back",
           lambda: notch_back(ListByClass, meld_list, "category", French)),
    "C5": ("single name 'English' | index under category 'langs' | notch away to French and back",
           lambda: notch_back(ByName, meld_single, "category", French)),
    "C6": ("collection list['langs'] | index under category 'langs' | notch to French and back",
           lambda: notch_back(ListByLabel, meld_list, "category", French)),
    "I1": ("single class English | index under 'langs' | remove_from_spell_index / add_to_spell_index of a parked one",
           cell_index_moves),
    "I2": ("single class English | French active under 'langs' | bind_inactive English, notch to it",
           cell_notch_to_wanted),
    "E1": ("single class English, resolved | a second English (category) arrives | bind after conjure",
           cell_competitor_arrives),
    "D1": ("single class English, AMBIGUOUS | one competitor disposed | cleanup_spell",
           cell_competitor_leaves),
    "D2": ("collection list[English], two members | one disposed | cleanup_spell",
           cell_member_leaves),
    "D3": ("single class English, resolved (bare) | provider disposed | cleanup_spell",
           cell_provider_leaves),
    "F1": ("OVERRIDE_REQUIRED Protocol Greeter (definition bound resolvable=False) | provider Protocol frame",
           lambda: override_required(Greeter, "bare", ByProtocol, English, "protocol")),
    "F2": ("OVERRIDE_REQUIRED class English (definition bound resolvable=False) | Edited.English category",
           lambda: override_required(English, "bare", ByClass, Edited.English, "category")),
    "G1": ("single class English in a borrower | owner's English bare | link + add_spell_to_contract",
           lambda: borrowed("bare")),
    "G2": ("single class English in a borrower | owner's English Protocol frame | link + add_spell_to_contract",
           lambda: borrowed("protocol")),
    "G3": ("single class English in a borrower | owner's English category | link + add_spell_to_contract",
           lambda: borrowed("category")),
    "G4": ("single class English in a borrower, resolved to the borrowed copy | remove_spell_from_contract",
           lambda: borrowed("bare", then_leave=True)),
    "H1": ("single class English in the target | owner's English bare | transfer_spell_ownership",
           lambda: transferred("bare")),
    "H2": ("single class English in the target | owner's English Protocol frame | transfer_spell_ownership",
           lambda: transferred("protocol")),
    "H3": ("single class English, resolved at home | English transferred away | transfer_spell_ownership",
           cell_transfer_leaves),
    "P1a": ("Phase 4 binding-key cycle: CycZ under category 'cycb' (CycA's annotated name) | conjure",
            lambda: binding_cycle("cycb")),
    "P1b": ("Phase 4 binding-key cycle control: CycZ under category 'zz' | conjure",
            lambda: binding_cycle("zz")),
}
SHAPES["category_greeter"] = {"spellframe": "greeter"}


def main() -> None:
    """Run one cell, or list the cells."""
    if len(sys.argv) != 2:
        raise SystemExit("usage: probe_watcher_announcer_matrix.py <cell> | --list")
    if sys.argv[1] == "--list":
        print(" ".join(CELLS))
        return
    description, run = CELLS[sys.argv[1]]
    print("cell %s (melder %s, GIL %s): %s" % (sys.argv[1], md.__version__,
                                                "on" if sys._is_gil_enabled() else "off", description))
    install_mark_recorders()
    run()


if __name__ == "__main__":
    main()

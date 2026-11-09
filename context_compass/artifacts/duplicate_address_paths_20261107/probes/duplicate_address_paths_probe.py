"""
Probe (2026-11-07): can two spells be ACTIVE at one address, on any path that registers or exposes a spell?

The owner's rule (chat, 2026-11-07): "sure 2 spells with the same name without differentiation, 2 spells with the same
spellframe without a binding_name ... you can add these or extend various features for this, if we don't already
have it". An address is the normalized `(frame_key, binding_key)` pair (`SpellInputUtils.make_spell_key_from_parts`,
the key `Spell._key` and the frame claim use): the spellframe's name - or the spell's own name when it is bound bare -
and the binding name, both lowercased, an empty binding name being `__default__`.

Shapes (one row each per path):
    S-category          two classes under the string spellframe 'Reports' / 'reports', default binding.
    S-protocol          two classes under the Protocol `Greeter`, default binding.
    S-protocol-homonym  one class under `Greeter`, the other under another Protocol also named `Greeter`.
    N-scope             two bare classes both named `Report`, declared in different scopes.
    N-case              two bare classes named `Report` and `report`.

Not duplicates, by design (controls): versions of ONE SpellIndex (P00, P06b) and a borrower's contracted copy of a
lender's spell (P08a/P09b: the same spell, lent or moved).

Paths: P01 bind before conjure; P02 bind after conjure (live dynamic root); P03 two Books of one frame; P04
bind_inactive into ANOTHER index; P05 remove_from_spell_index then notch; P06 add_to_spell_index; P07 scan of a module
declaring both; P08 ownership transfer into a root whose Book serves the address (one frame: P08a/P08b; across frames:
P08c into a frame serving it, P08d into a frame that does not, then a bind there - both admitted at 0.2.8279, the
transfer refused across frames since 0.2.8280 on the owner's ruling of 2026-11-07); P09 contracted copies
(add_spell_to_contract / add_index_to_contract); P10 upgrade_to_normal; P11 conjure's Phase 4 (DUPLICATE_SPELL_NAME);
P12 crystallizer graft into a host frame that serves the address (checkpoint restore is not driven).

Each row prints: REFUSED (where, error type, message head), ADMITTED (what the address answers and which spells are
active there), BY DESIGN, UNREACHABLE or PROBE-ERROR (a setup step failed - not a measurement). After every row the
probe counts, across every Book of the scenario, the ACTIVE spells whose key is the shape's address (`Book._spells`)
and reads the frame claim (`AethericFrame.get_lookup`), so an admission cannot hide behind a single answer.

Read-only on src/. Run from the repository root with the repository's interpreter, the GIL off and on:
    .venv_new/Scripts/python.exe -X gil=0 context_compass/artifacts/duplicate_address_paths_20261107/probes/duplicate_address_paths_probe.py
    .venv_new/Scripts/python.exe -X gil=1 context_compass/artifacts/duplicate_address_paths_20261107/probes/duplicate_address_paths_probe.py
The script re-imports itself under its file name, so the module-level spell classes are importable by qualname - the
graft (P12) hydrates its recorded class from custody. Every scenario runs in fresh Aether / Nexus / Crystallizer
singletons with caching off; P12 routes the crystallizer cache into a temporary directory and removes it.
"""
import importlib
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple


class Greeter(Protocol):
    """The Protocol the S-protocol shapes bind under, with the default binding name."""

    def tag(self) -> str:
        """Return the implementation's role tag."""
        ...


class _TwinScope:
    """A second scope declaring another Protocol named `Greeter`: another object, the same address."""

    class Greeter(Protocol):
        """A homonym of the module-level `Greeter` Protocol."""

        def tag(self) -> str:
            """Return the implementation's role tag."""
            ...


class CategoryAlpha:
    """S-category, first spell: bound under the string spellframe 'Reports'."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-first"


class CategoryBeta:
    """S-category, second spell: bound under the string spellframe 'reports' (the same address)."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-second"


class CategoryGamma:
    """S-category, third spell: bound under the string spellframe 'REPORTS' (the same address)."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-third"


class AlphaGreeter:
    """S-protocol shapes, first spell: bound under `Greeter`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-first"


class BetaGreeter:
    """S-protocol shapes, second spell: bound under `Greeter` (or its homonym)."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-second"


class GammaGreeter:
    """S-protocol shapes, third spell: bound under `Greeter`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-third"


class Report:
    """N shapes, first spell: a bare class named `Report` at ('report', '__default__')."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-first"


class _ScopeTwo:
    """A second scope declaring a class named `Report`."""

    class Report:
        """N-scope, second spell: another class named `Report`."""

        def tag(self) -> str:
            """Return this spell's role tag."""
            return "report-scope-two"


class _ScopeThree:
    """A third scope declaring a class named `Report`."""

    class Report:
        """N-scope, third spell: a third class named `Report`."""

        def tag(self) -> str:
            """Return this spell's role tag."""
            return "report-scope-three"


class report:
    """N-case, second spell: a bare class named `report` (the same address as `Report`)."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-lower"


class REPORT:
    """N-case, third spell: a bare class named `REPORT` (the same address as `Report`)."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-upper"


class Ledger:
    """An unrelated bare spell at ('ledger', '__default__'): 'another index at another address'."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "ledger"


class AddressShape:
    """
    One way two spells can claim one address, with three spells (X, Y, W) bound that way.

    Contract:
        - `members` maps a role ("first" = X, "second" = Y, "third" = W) to (class, spellframe); every member
          normalizes to `address`, and each class has its own code, so each has its own spell_id.
        - `meld` asks the address through the public meld door the shape is addressed by: `meld(spellframe=...)`
          for the S shapes, `meld("Report")` (a human SpellName) for the N shapes.
        - Pure value holder plus thin call helpers; owns nothing that needs cleanup.
    """

    def __init__(
            self,
            label: str,
            address: Tuple[str, str],
            members: Dict[str, Tuple[type, Any]],
            meld_kwargs: Dict[str, Any],
            meld_name: Optional[str],
    ) -> None:
        """
        Build the shape.

        Args:
            label (str): The row label ("S-category", ...).
            address (Tuple[str, str]): The normalized (frame_key, binding_key) every member is bound at.
            members (Dict[str, Tuple[type, Any]]): role -> (class, spellframe or None).
            meld_kwargs (Dict[str, Any]): Keyword arguments of the meld by address (S shapes).
            meld_name (Optional[str]): The SpellName string of the meld by address (N shapes), else None.

        Returns:
            None.
        """
        self.label: str = label
        self.address: Tuple[str, str] = address
        self.members: Dict[str, Tuple[type, Any]] = members
        self.meld_kwargs: Dict[str, Any] = meld_kwargs
        self.meld_name: Optional[str] = meld_name
        self.letters: Dict[str, str] = {"first": "X", "second": "Y", "third": "W"}

    def cls(self, role: str) -> type:
        """
        Return the class of `role`.

        Args:
            role (str): "first", "second" or "third".

        Returns:
            type: The class.
        """
        return self.members[role][0]

    def bind(self, binder: Any, role: str) -> str:
        """
        Bind `role`'s class ACTIVE through `binder` (a Spellbook or a Conduit) at the shape's address.

        Args:
            binder (Any): A Spellbook or a normal Conduit.
            role (str): "first", "second" or "third".

        Returns:
            str: The spell_id `bind` returned.

        Raises:
            Exception: Whatever `bind` raises; the caller measures it.
        """
        target, spellframe = self.members[role]
        return binder.bind(spell=target, spellframe=spellframe, existence="many", permissions="create")

    def stage(self, conduit: Any, role: str, spell_index: Any) -> str:
        """
        Stage `role`'s class PARKED on `spell_index` through `conduit.bind_inactive`, bound the shape's way.

        Args:
            conduit (Any): A normal dynamic Conduit (or a Spellbook) exposing `bind_inactive`.
            role (str): "first", "second" or "third".
            spell_index (Any): The SpellIndex the version joins.

        Returns:
            str: The spell_id `bind_inactive` returned.

        Raises:
            Exception: Whatever `bind_inactive` raises; the caller measures it.
        """
        target, spellframe = self.members[role]
        return conduit.bind_inactive(
            spell=target, spell_index=spell_index, spellframe=spellframe, existence="many", permissions="create",
        )

    def meld(self, conduit: Any) -> Any:
        """
        Meld the shape's address through `conduit`.

        Args:
            conduit (Any): The conduit asked.

        Returns:
            Any: The object the address builds.

        Raises:
            Exception: Whatever the meld raises; the caller reports it.
        """
        if self.meld_name is not None:
            return conduit.meld(self.meld_name)
        return conduit.meld(**self.meld_kwargs)

    def spell_id(self, role: str) -> str:
        """
        Return the spell_id `bind` gives `role`'s class, without registering it.

        Args:
            role (str): "first", "second" or "third".

        Returns:
            str: The SHA256 spell_id.
        """
        from melder.aether.spellbook.bind.bind import Bind

        return Bind.spell_id_inspector(self.cls(role))

    def labels(self) -> Dict[str, str]:
        """
        Map each member's spell_id and tag to its letter (X, Y, W), plus Ledger's to L.

        Returns:
            Dict[str, str]: spell_id or tag -> letter.
        """
        from melder.aether.spellbook.bind.bind import Bind

        mapping: Dict[str, str] = {}
        for role, letter in self.letters.items():
            mapping[self.spell_id(role)] = letter
            mapping[self.cls(role)().tag()] = letter
        mapping[Bind.spell_id_inspector(Ledger)] = "L"
        mapping["ledger"] = "L"
        return mapping


def build_shapes() -> List[AddressShape]:
    """
    Build the five shapes the probe measures.

    Returns:
        List[AddressShape]: S-category, S-protocol, S-protocol-homonym, N-scope, N-case.
    """
    return [
        AddressShape(
            "S-category", ("reports", "__default__"),
            {"first": (CategoryAlpha, "Reports"), "second": (CategoryBeta, "reports"),
             "third": (CategoryGamma, "REPORTS")},
            {"spellframe": "Reports"}, None,
        ),
        AddressShape(
            "S-protocol", ("greeter", "__default__"),
            {"first": (AlphaGreeter, Greeter), "second": (BetaGreeter, Greeter), "third": (GammaGreeter, Greeter)},
            {"spellframe": Greeter}, None,
        ),
        AddressShape(
            "S-protocol-homonym", ("greeter", "__default__"),
            {"first": (AlphaGreeter, Greeter), "second": (BetaGreeter, _TwinScope.Greeter),
             "third": (GammaGreeter, Greeter)},
            {"spellframe": Greeter}, None,
        ),
        AddressShape(
            "N-scope", ("report", "__default__"),
            {"first": (Report, None), "second": (_ScopeTwo.Report, None), "third": (_ScopeThree.Report, None)},
            {}, "Report",
        ),
        AddressShape(
            "N-case", ("report", "__default__"),
            {"first": (Report, None), "second": (report, None), "third": (REPORT, None)},
            {}, "Report",
        ),
    ]


def head(error: BaseException) -> str:
    """
    Return the first 230 characters of an error's message on one line.

    Args:
        error (BaseException): The error.

    Returns:
        str: The message head.
    """
    text = " ".join(str(error).split())
    return text if len(text) <= 230 else text[:227] + "..."


def refused(step: str, error: BaseException) -> str:
    """
    Format a refusal.

    Args:
        step (str): The public call that refused.
        error (BaseException): What it raised.

    Returns:
        str: "REFUSED at <step> (<type>): <message head>".
    """
    return f"REFUSED at {step} ({type(error).__name__}): {head(error)}"


def reset_world() -> None:
    """
    Install fresh Aether, AetherUtilitySystem, Nexus and Crystallizer singletons and rebind Spellbook/Conduit.

    Returns:
        None.
    """
    from melder.aether.aether import Aether
    from melder.aether.aether_utility_system import AetherUtilitySystem
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.crystallizer.crystallizer import Crystallizer
    from melder.nexus.nexus import Nexus

    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class ProbeWorld:
    """
    The Books, roots and frames one scenario creates, the step it is on, and their teardown.

    Contract:
        - `book(frame)` builds a Spellbook with its own default configuration and settles the frame dynamic with
          caching off the first time the frame is used (`finalized=True` freezes the configuration first, the
          recorded lane's canon, for P12).
        - `step` names the call in progress, so a setup failure is reported as PROBE-ERROR at that step.
        - `teardown` cleans every root, then every Book, and returns the failures it met (reported, not hidden).
    """

    def __init__(self, scenario: str) -> None:
        """
        Start an empty world for `scenario`.

        Args:
            scenario (str): The scenario id, used in frame and root names.

        Returns:
            None.
        """
        self.scenario: str = scenario
        self.books: List[Any] = []
        self.roots: List[Any] = []
        self.settled: List[str] = []
        self.step: str = "start"

    def frame(self, suffix: str) -> str:
        """
        Return this scenario's frame name for `suffix`.

        Args:
            suffix (str): A short frame suffix.

        Returns:
            str: The frame name.
        """
        return f"dup-{self.scenario}-{suffix}"

    def book(self, frame: str, finalized: bool = False) -> Any:
        """
        Build a Spellbook on `frame`, settling the frame dynamic (caching off) on first use.

        Args:
            frame (str): The aetheric frame.
            finalized (bool): Freeze the configuration before any bind (needed when the crystallizer records).

        Returns:
            Any: The Spellbook (unconjured).
        """
        from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
        from melder.aether.spellbook.spellbook import Spellbook

        configuration = SpellbookConfiguration(frame).with_defaults()
        if finalized:
            configuration.finalize()
        spellbook = Spellbook(aetheric_frame=frame, configuration=configuration)
        if frame not in self.settled:
            spellbook.configure_aether_frame(
                system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
            )
            self.settled.append(frame)
        self.books.append(spellbook)
        return spellbook

    def conjure(self, spellbook: Any, name: str) -> Any:
        """
        Conjure `spellbook`'s dynamic root and keep it for teardown.

        Args:
            spellbook (Any): The Book.
            name (str): The root's name suffix.

        Returns:
            Any: The root Conduit.
        """
        root = spellbook.conjure(dynamic=True, name=f"{self.scenario}-{name}")
        self.roots.append(root)
        return root

    def teardown(self) -> List[str]:
        """
        Clean every root, then every Book; collect what fails.

        Returns:
            List[str]: One "<what>: <type>: <head>" entry per failed cleanup.
        """
        failures: List[str] = []
        for root in reversed(self.roots):
            try:
                root.cleanup()
            except Exception as error:
                failures.append(f"root cleanup: {type(error).__name__}: {head(error)}")
        for spellbook in reversed(self.books):
            try:
                spellbook.cleanup()
            except Exception as error:
                failures.append(f"book cleanup: {type(error).__name__}: {head(error)}")
        return failures


def index_of(spellbook: Any, spell_id: str) -> Any:
    """
    Return the SpellIndex of the version `spellbook` holds under `spell_id`, active or parked.

    Args:
        spellbook (Any): The owning Book.
        spell_id (str): The version's spell_id.

    Returns:
        Any: Its SpellIndex.

    Raises:
        RuntimeError: When the Book holds no such version.
    """
    spell = spellbook.find_spell_by_spell_id(spell_id)
    if spell is None:
        raise RuntimeError(f"probe: the Book holds no version {spell_id[:12]}")
    return spell.spell_index


def state(world: ProbeWorld, shape: AddressShape, conduits: List[Tuple[str, Any]]) -> str:
    """
    Summarize the address: the active spells at it in every Book, the frame claims, and what each conduit's meld
    by address builds.

    Args:
        world (ProbeWorld): The scenario world (its Books are inspected).
        shape (AddressShape): The shape (its address and labels).
        conduits (List[Tuple[str, Any]]): (label, conduit) pairs whose meld by address is asked.

    Returns:
        str: "actives@A=[...]; claim=...; meld <label>=..." - two or more actives in one frame is a duplicate.
    """
    labels = shape.labels()
    actives: List[str] = []
    claims: List[str] = []
    frames_seen: List[str] = []
    for position, spellbook in enumerate(world.books, start=1):
        try:
            spells = list(spellbook._spells.values())
        except Exception:
            continue
        for spell in spells:
            if spell._key == shape.address:
                actives.append(f"{labels.get(spell.spell_id, spell.spell_id[:8])}@B{position}")
        frame_name = spellbook._aetheric_frame_name
        if frame_name not in frames_seen:
            frames_seen.append(frame_name)
            holder = spellbook._aetheric_frame.get_lookup(shape.address)
            holder_text = "none" if holder is None else labels.get(holder, holder[:8])
            claims.append(f"{frame_name.split('-')[-1]}:{holder_text}")
    melds: List[str] = []
    for label, conduit in conduits:
        try:
            built = shape.meld(conduit)
            melds.append(f"{label}->{labels.get(built.tag(), built.tag())}")
        except Exception as error:
            melds.append(f"{label}->raised {type(error).__name__}: {head(error)[:90]}")
    return f"actives@A=[{', '.join(actives)}]; claim[{', '.join(claims)}]; meld {'; '.join(melds)}"


def duplicate_in_one_frame(world: ProbeWorld, shape: AddressShape) -> bool:
    """
    Report whether two or more spells are ACTIVE at the shape's address within one frame.

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.

    Returns:
        bool: True when some frame has two or more active spells at the address.
    """
    per_frame: Dict[str, int] = {}
    for spellbook in world.books:
        try:
            spells = list(spellbook._spells.values())
            frame_name = spellbook._aetheric_frame_name
        except Exception:
            continue
        for spell in spells:
            if spell._key == shape.address:
                per_frame[frame_name] = per_frame.get(frame_name, 0) + 1
    return any(count > 1 for count in per_frame.values())


def admitted(world: ProbeWorld, shape: AddressShape, what: str, conduits: List[Tuple[str, Any]]) -> str:
    """
    Format an admission, flagging a duplicate in one frame.

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.
        what (str): What was admitted.
        conduits (List[Tuple[str, Any]]): Conduits whose meld by address is asked.

    Returns:
        str: "ADMITTED (<duplicate or not>): <what>; <state>".
    """
    flag = "TWO ACTIVE IN ONE FRAME" if duplicate_in_one_frame(world, shape) else "no second active in one frame"
    return f"ADMITTED ({flag}): {what}; {state(world, shape, conduits)}"


def p00_versions_of_one_index(world: ProbeWorld, shape: AddressShape) -> str:
    """
    Control (by design): Y staged on X's own index, then notched - versions of ONE SpellIndex.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    world.step = "conjure"
    root = world.conjure(spellbook, "root")
    world.step = "bind_inactive Y onto X's index"
    index = index_of(spellbook, x_id)
    y_id = shape.stage(root, "second", index)
    world.step = "notch to Y"
    root.notch_spell(spell_index=index, spell_id=y_id)
    return "BY DESIGN (versions of one SpellIndex; a notch moves which is active): " + state(
        world, shape, [("root", root)],
    )


def p01_bind_before_conjure(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P01: X and Y bound at one address in one Book before its conjure.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    try:
        shape.bind(spellbook, "second")
    except Exception as error:
        verdict = refused("Spellbook.bind (Y)", error)
        unregistered = spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
        world.step = "conjure after the refusal"
        root = world.conjure(spellbook, "root")
        observation = ""
        if shape.meld_name is not None:
            try:
                built = root.meld(shape.cls("second"))
                observation = f"; meld(<Y's class object>)->{shape.labels().get(built.tag(), built.tag())}"
            except Exception as meld_error:
                observation = f"; meld(<Y's class object>) raised {type(meld_error).__name__}"
        return f"{verdict} | Y unregistered: {unregistered}; {state(world, shape, [('root', root)])}{observation}"
    world.step = "conjure after the admission"
    try:
        root = world.conjure(spellbook, "root")
    except Exception as error:
        return f"ADMITTED at bind, then {refused('conjure', error)}"
    return admitted(world, shape, "both bound before conjure", [("root", root)])


def p02_bind_after_conjure(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P02: X bound and the root conjured dynamic; Y bound through the live root.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    world.step = "conjure"
    root = world.conjure(spellbook, "root")
    try:
        shape.bind(root, "second")
    except Exception as error:
        unregistered = spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
        return (f"{refused('Conduit.bind (Y, post-conjure)', error)} | Y unregistered: {unregistered}; "
                f"{state(world, shape, [('root', root)])}")
    return admitted(world, shape, "Y bound through the live root", [("root", root)])


def p03a_two_books_both_before_conjure(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P03a: Book 1 binds X and Book 2 binds Y, both before either conjures (one frame).

    Returns:
        str: The row verdict.
    """
    world.step = "bind X in Book 1"
    first_book = world.book(world.frame("a"))
    second_book = world.book(world.frame("a"))
    shape.bind(first_book, "first")
    try:
        shape.bind(second_book, "second")
    except Exception as error:
        world.step = "conjure both"
        first_root = world.conjure(first_book, "r1")
        second_root = world.conjure(second_book, "r2")
        return (f"{refused('Spellbook.bind (Y, Book 2, before either conjure)', error)} | "
                f"{state(world, shape, [('r1', first_root), ('r2', second_root)])}")
    world.step = "conjure both after the admission"
    first_root = world.conjure(first_book, "r1")
    second_root = world.conjure(second_book, "r2")
    return admitted(world, shape, "both Books bound before conjure", [("r1", first_root), ("r2", second_root)])


def p03b_two_books_after_the_others_conjure(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P03b: Book 1 binds X and conjures; Book 2 binds Y before its own conjure.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X in Book 1 and conjure"
    first_book = world.book(world.frame("a"))
    shape.bind(first_book, "first")
    first_root = world.conjure(first_book, "r1")
    second_book = world.book(world.frame("a"))
    try:
        shape.bind(second_book, "second")
    except Exception as error:
        world.step = "conjure Book 2"
        second_root = world.conjure(second_book, "r2")
        return (f"{refused('Spellbook.bind (Y, Book 2, after Book 1 conjured)', error)} | "
                f"{state(world, shape, [('r1', first_root), ('r2', second_root)])}")
    world.step = "conjure Book 2 after the admission"
    second_root = world.conjure(second_book, "r2")
    return admitted(world, shape, "Book 2 bound after Book 1 conjured", [("r1", first_root), ("r2", second_root)])


def p03c_two_books_both_conjured(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P03c: Book 1 binds X and conjures; Book 2 binds Ledger and conjures; Book 2's live root binds Y.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X in Book 1 and conjure"
    first_book = world.book(world.frame("a"))
    shape.bind(first_book, "first")
    first_root = world.conjure(first_book, "r1")
    world.step = "bind Ledger in Book 2 and conjure"
    second_book = world.book(world.frame("a"))
    second_book.bind(spell=Ledger, existence="many", permissions="create")
    second_root = world.conjure(second_book, "r2")
    try:
        shape.bind(second_root, "second")
    except Exception as error:
        return (f"{refused('Conduit.bind (Y, Book 2 root, both conjured)', error)} | "
                f"{state(world, shape, [('r1', first_root), ('r2', second_root)])}")
    return admitted(world, shape, "Book 2's live root bound Y", [("r1", first_root), ("r2", second_root)])


def p04a_bind_inactive_into_another_binding(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P04a: X active; Y staged with bind_inactive onto Ledger's index (another index, another binding).

    Returns:
        str: The row verdict.
    """
    world.step = "bind X and Ledger, conjure"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    ledger_id = spellbook.bind(spell=Ledger, existence="many", permissions="create")
    root = world.conjure(spellbook, "root")
    ledger_index = index_of(spellbook, ledger_id)
    try:
        shape.stage(root, "second", ledger_index)
    except Exception as error:
        unregistered = spellbook.find_spell_by_spell_id(shape.spell_id("second")) is None
        return (f"{refused('Conduit.bind_inactive (Y onto Ledger index)', error)} | Y unregistered: "
                f"{unregistered}; {state(world, shape, [('root', root)])}")
    return admitted(world, shape, "Y parked on Ledger's index", [("root", root)])


def p04b_bind_inactive_into_split_index_then_notch(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P04b: X active; W split off X's index (its own index at the address); Y staged onto W's index; notch to Y.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X, conjure"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "root")
    x_index = index_of(spellbook, x_id)
    world.step = "stage W onto X's index and split it off"
    w_id = shape.stage(root, "third", x_index)
    root.remove_from_spell_index(spell_id=w_id, source_index=x_index)
    w_index = index_of(spellbook, w_id)
    try:
        y_id = shape.stage(root, "second", w_index)
    except Exception as error:
        return f"{refused('Conduit.bind_inactive (Y onto the split index)', error)} | {state(world, shape, [('root', root)])}"
    staged = (f"Y staged parked on the split index (another index at A; it is active there: "
              f"{spellbook._spells.get(w_index) is not None})")
    try:
        root.notch_spell(spell_index=w_index, spell_id=y_id)
    except Exception as error:
        return f"{staged}; {refused('Conduit.notch_spell (to Y)', error)} | {state(world, shape, [('root', root)])}"
    return admitted(world, shape, f"{staged}; the notch to Y stood", [("root", root)])


def p05_remove_then_notch(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P05: X active; Y staged on X's index, notched to, melded and notched back (compiled); Y split off with
    remove_from_spell_index; notch the split index to Y (the pre-0.2.8273 C7 path).

    Returns:
        str: The row verdict.
    """
    world.step = "bind X, conjure"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "root")
    x_index = index_of(spellbook, x_id)
    world.step = "stage Y, notch to Y, meld, notch back"
    y_id = shape.stage(root, "second", x_index)
    root.notch_spell(spell_index=x_index, spell_id=y_id)
    shape.meld(root)
    root.notch_spell(spell_index=x_index, spell_id=x_id)
    world.step = "remove_from_spell_index Y"
    root.remove_from_spell_index(spell_id=y_id, source_index=x_index)
    y_index = index_of(spellbook, y_id)
    try:
        root.notch_spell(spell_index=y_index, spell_id=y_id)
    except Exception as error:
        return f"{refused('Conduit.notch_spell (split index to Y)', error)} | {state(world, shape, [('root', root)])}"
    return admitted(world, shape, "the split index was notched to Y", [("root", root)])


def p06a_add_into_another_binding(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P06a: Y (parked, split off X's index) moved with add_to_spell_index onto Ledger's index.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X and Ledger, conjure, stage and split Y"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    ledger_id = spellbook.bind(spell=Ledger, existence="many", permissions="create")
    root = world.conjure(spellbook, "root")
    x_index = index_of(spellbook, x_id)
    y_id = shape.stage(root, "second", x_index)
    root.remove_from_spell_index(spell_id=y_id, source_index=x_index)
    y_index = index_of(spellbook, y_id)
    ledger_index = index_of(spellbook, ledger_id)
    try:
        root.add_to_spell_index(spell_id=y_id, target_index=ledger_index)
    except Exception as error:
        stayed = index_of(spellbook, y_id) is y_index
        return (f"{refused('Conduit.add_to_spell_index (Y onto Ledger index)', error)} | Y stayed in its index: "
                f"{stayed}; {state(world, shape, [('root', root)])}")
    return admitted(world, shape, "Y moved onto Ledger's index", [("root", root)])


def p06b_add_back_then_notch(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P06b control (by design): Y split off X's index, moved back with add_to_spell_index, then notched.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X, conjure, stage and split Y"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "root")
    x_index = index_of(spellbook, x_id)
    y_id = shape.stage(root, "second", x_index)
    root.remove_from_spell_index(spell_id=y_id, source_index=x_index)
    world.step = "add Y back and notch to it"
    root.add_to_spell_index(spell_id=y_id, target_index=x_index)
    root.notch_spell(spell_index=x_index, spell_id=y_id)
    return "BY DESIGN (moved back into its index, then notched; one active): " + state(world, shape, [("root", root)])


def p06c_add_the_active_version(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P06c: the ACTIVE X moved with add_to_spell_index onto the split index Y left (another index at the address).

    Returns:
        str: The row verdict.
    """
    world.step = "bind X, conjure, stage and split Y"
    spellbook = world.book(world.frame("a"))
    x_id = shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "root")
    x_index = index_of(spellbook, x_id)
    y_id = shape.stage(root, "second", x_index)
    root.remove_from_spell_index(spell_id=y_id, source_index=x_index)
    y_index = index_of(spellbook, y_id)
    try:
        root.add_to_spell_index(spell_id=x_id, target_index=y_index)
    except Exception as error:
        return (f"{refused('Conduit.add_to_spell_index (active X onto the split index)', error)} | "
                f"{state(world, shape, [('root', root)])}")
    return admitted(world, shape, "the active X moved onto the split index", [("root", root)])


def scan_module(shape: AddressShape, module_name: str) -> Tuple[ModuleType, type, type]:
    """
    Build a module that declares X and Y with scan_bind, bound the shape's way.

    Contract:
        - Each declared class is a fresh subclass of the shape's class carrying the same `__name__` and the module's
          `__module__` (scan refuses re-exports), so the module-level classes are not mutated. For N-scope both are
          named `Report` under two attribute names; for N-case they are `Report` and `report`.

    Args:
        shape (AddressShape): The shape.
        module_name (str): The synthetic module's name.

    Returns:
        Tuple[ModuleType, type, type]: The module, its X class and its Y class.
    """
    from melder.aether.spellbook.bind.scan import scan_bind

    module = ModuleType(module_name)
    declared: List[type] = []
    for attribute, role in (("FirstDeclared", "first"), ("SecondDeclared", "second")):
        base, spellframe = shape.members[role]
        copy = type(base.__name__, (base,), {"__module__": module_name})
        scan_bind(existence="many", permissions="create", spellframe=spellframe)(copy)
        setattr(module, attribute, copy)
        declared.append(copy)
    return module, declared[0], declared[1]


def p07_scan(world: ProbeWorld, shape: AddressShape, after_conjure: bool) -> str:
    """
    P07: scan a module declaring both X and Y (pre-conjure through the Book, or post-conjure through the root).

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.
        after_conjure (bool): Scan through the live root instead of the unconjured Book.

    Returns:
        str: The row verdict.
    """
    from melder.aether.spellbook.bind.bind import Bind

    world.step = "build the module"
    spellbook = world.book(world.frame("a"))
    module, first_copy, second_copy = scan_module(shape, f"dup_scan_{world.scenario.replace('-', '_')}")
    root: Optional[Any] = None
    if after_conjure:
        world.step = "conjure"
        root = world.conjure(spellbook, "root")
    scanner: Any = root if root is not None else spellbook
    door = "Conduit.scan (post-conjure)" if after_conjure else "Spellbook.scan (pre-conjure)"
    try:
        scanner.scan(module)
    except Exception as error:
        first_kept = spellbook.find_spell_by_spell_id(Bind.spell_id_inspector(first_copy)) is not None
        second_kept = spellbook.find_spell_by_spell_id(Bind.spell_id_inspector(second_copy)) is not None
        if root is None:
            world.step = "conjure after the refusal"
            root = world.conjure(spellbook, "root")
        actives = [spell.spell_name for spell in spellbook._spells.values() if spell._key == shape.address]
        try:
            built = shape.meld(root)
            answer = type(built).__qualname__
        except Exception as meld_error:
            answer = f"raised {type(meld_error).__name__}"
        return (f"{refused(door + ' at the second declaration', error)} | first declaration kept: {first_kept}, "
                f"second registered: {second_kept}; active at A: {len(actives)}; meld by address -> {answer}")
    if root is None:
        world.step = "conjure after the admission"
        root = world.conjure(spellbook, "root")
    return admitted(world, shape, "the scan bound both declarations", [("root", root)])


def p08a_transfer_same_frame(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P08a: same frame - the target Book tries to serve the address with Y while the source's X holds it; then X's
    index is transferred to the target.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X in Book 1 and conjure"
    source_book = world.book(world.frame("a"))
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "src")
    target_book = world.book(world.frame("a"))
    try:
        shape.bind(target_book, "second")
        setup = "the target Book bound Y (setup admitted)"
    except Exception as error:
        setup = f"setup {refused('Spellbook.bind (Y in the target Book)', error)}"
    world.step = "conjure the target and transfer X"
    target = world.conjure(target_book, "tgt")
    try:
        source.transfer_spell_ownership(spell=x_id, target_conduit=target)
    except Exception as error:
        return f"{setup} | then {refused('transfer_spell_ownership', error)}"
    return (f"{setup} | the transfer moved X itself: {state(world, shape, [('tgt', target)])}; "
            f"two active in one frame: {duplicate_in_one_frame(world, shape)}")


def p08b_transfer_onto_a_split_index(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P08b: the target Book holds its own index at the address with no active version (W split off, V disposed); the
    source's X is transferred in; then the target notches its own index to W.

    Returns:
        str: The row verdict.
    """
    world.step = "target Book: bind Y, conjure, stage W, split W, dispose Y"
    target_book = world.book(world.frame("a"))
    y_id = shape.bind(target_book, "second")
    target = world.conjure(target_book, "tgt")
    y_index = index_of(target_book, y_id)
    w_id = shape.stage(target, "third", y_index)
    target.remove_from_spell_index(spell_id=w_id, source_index=y_index)
    w_index = index_of(target_book, w_id)
    target.cleanup_spell(spell=target_book.find_spell_by_spell_id(y_id))
    world.step = "source Book: bind X, conjure, transfer X to the target"
    source_book = world.book(world.frame("a"))
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "src")
    source.transfer_spell_ownership(spell=x_id, target_conduit=target)
    try:
        target.notch_spell(spell_index=w_index, spell_id=w_id)
    except Exception as error:
        return (f"X transferred into a Book holding a parked W at A; {refused('Conduit.notch_spell (target to W)', error)}"
                f" | {state(world, shape, [('tgt', target)])}")
    return admitted(world, shape, "X transferred in, then the target notched its own index to W", [("tgt", target)])


def p08c_transfer_across_frames(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P08c: X in frame a, Y in frame b (each frame's claim is its own); X's index transferred to frame b's root.

    Contract:
        - Admitted until 0.2.8280 (two active in frame b's Book, frame a's claim left naming the departed X); since
          0.2.8280 (the owner's ruling, 2026-11-07) `transfer_spell_ownership` refuses a target of another frame. On
          a refusal the row shows that nothing moved: both frames' actives, claims and melds, and a new frame-a
          Book's bind of W, with whether X - the spell it is refused for - is still active in frame a.

    Returns:
        str: The row verdict.
    """
    world.step = "frame a: bind X, conjure; frame b: bind Y, conjure"
    source_book = world.book(world.frame("a"))
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "src")
    target_book = world.book(world.frame("b"))
    y_id = shape.bind(target_book, "second")
    target = world.conjure(target_book, "tgt")
    try:
        source.transfer_spell_ownership(spell=x_id, target_conduit=target)
    except Exception as error:
        return (f"{refused('transfer_spell_ownership (across frames)', error)} | nothing moved: "
                f"{state(world, shape, [('src', source), ('tgt', target)])}; "
                f"{by_spell_id(source, shape, [('X', x_id)])} (src); {by_spell_id(target, shape, [('Y', y_id)])} "
                f"(tgt) | {late_frame_a_bind(world, shape, source_book, x_id)}")
    verdict = admitted(world, shape, "X's index transferred into frame b's root", [("tgt", target)])
    by_id = by_spell_id(target, shape, [("X", x_id), ("Y", y_id)])
    return f"{verdict}; {by_id} | {late_frame_a_bind(world, shape, source_book, x_id)}"


def late_frame_a_bind(world: ProbeWorld, shape: AddressShape, source_book: Any, x_id: str) -> str:
    """
    Bind W at the address in a new Book of frame a, and say whether X is still active in frame a's source Book.

    Contract:
        - A refusal naming X while X is still active in frame a is the live claim; naming X after X left frame a is
          a stale claim (the pre-0.2.8280 cross-frame transfer).

    Args:
        world (ProbeWorld): The scenario world (the new Book joins it).
        shape (AddressShape): The shape.
        source_book (Any): Frame a's source Book.
        x_id (str): X's spell_id.

    Returns:
        str: What the bind did, and whether X is still active in the source Book.
    """
    world.step = "a new Book of frame a binds W at A"
    still_there = any(spell.spell_id == x_id for spell in source_book._spells.values())
    late_book = world.book(world.frame("a"))
    try:
        shape.bind(late_book, "third")
        return f"a new Book of frame a bound W at A (X still active in frame a: {still_there})"
    except Exception as error:
        return (f"frame a's address held: {refused('Spellbook.bind (W, a new Book of frame a)', error)} "
                f"(X still active in frame a: {still_there})")


def meld_answer(shape: AddressShape, conduit: Any) -> str:
    """
    Meld the shape's address through `conduit` and name what it builds, or what it raises.

    Args:
        shape (AddressShape): The shape.
        conduit (Any): The conduit asked.

    Returns:
        str: The built spell's letter, or "raised <type>".
    """
    try:
        built = shape.meld(conduit)
        return shape.labels().get(built.tag(), built.tag())
    except Exception as error:
        return f"raised {type(error).__name__}"


def by_spell_id(conduit: Any, shape: AddressShape, members: List[Tuple[str, str]]) -> str:
    """
    Meld each (letter, spell_id) through `conduit` by spell_id and say what each builds or raises.

    Args:
        conduit (Any): The conduit asked.
        shape (AddressShape): The shape (labels).
        members (List[Tuple[str, str]]): (letter, spell_id) pairs.

    Returns:
        str: "meld(spell_id=<letter>)-><letter or error>; ...".
    """
    labels = shape.labels()
    answers: List[str] = []
    for letter, spell_id in members:
        try:
            built = conduit.meld(spell_id=spell_id)
            answers.append(f"meld(spell_id={letter})->{labels.get(built.tag(), built.tag())}")
        except Exception as error:
            code = " [DUPLICATE_SPELL_NAME]" if "DUPLICATE_SPELL_NAME" in str(error) else ""
            answers.append(f"meld(spell_id={letter})->raised {type(error).__name__}{code}")
    return "; ".join(answers)


def p08d_transfer_across_frames_then_bind(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P08d: X in frame a; frame b serves Ledger only; X's index transferred to frame b's root; frame b's root then
    binds Y at A.

    Contract:
        - Admitted until 0.2.8280: the transfer stood without moving any claim, so frame b served X at A without
          holding frame b's claim, and the later bind of Y registered Y beside X before raising. Since 0.2.8280 the
          transfer is refused; the row then shows frame b's claim and meld before the bind, what the bind did, and
          the address state of both frames after it.

    Returns:
        str: The row verdict.
    """
    world.step = "frame a: bind X, conjure; frame b: bind Ledger, conjure"
    source_book = world.book(world.frame("a"))
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "src")
    target_book = world.book(world.frame("b"))
    target_book.bind(spell=Ledger, existence="many", permissions="create")
    target = world.conjure(target_book, "tgt")
    meld_before = meld_answer(shape, target)
    try:
        source.transfer_spell_ownership(spell=x_id, target_conduit=target)
        transfer_text: Optional[str] = None
    except Exception as error:
        transfer_text = refused("transfer_spell_ownership (across frames)", error)
    holder = target_book._aetheric_frame.get_lookup(shape.address)
    claim_text = f"frame b's claim on A: {'none' if holder is None else shape.labels().get(holder)}"
    meld_after = meld_answer(shape, target)
    world.step = "the target root binds Y"
    try:
        shape.bind(target, "second")
        bound = "the target root's bind of Y returned"
    except Exception as error:
        registered = target_book.find_spell_by_spell_id(shape.spell_id("second")) is not None
        bound = f"{refused('Conduit.bind (Y in frame b)', error)} - Y left registered: {registered}"
    if transfer_text is not None:
        return (f"{transfer_text} | nothing moved: {claim_text}; meld tgt before->{meld_before}, after->"
                f"{meld_after} | then {bound}; {state(world, shape, [('src', source), ('tgt', target)])}; two active "
                f"in one frame: {duplicate_in_one_frame(world, shape)}")
    before = f"the transfer stood; {claim_text}; meld tgt->{meld_after}"
    verdict = admitted(world, shape, f"{before}; {bound}", [("tgt", target)])
    return f"{verdict}; {by_spell_id(target, shape, [('X', x_id), ('Y', shape.spell_id('second'))])}"


def lender_with_split_parked_version(world: ProbeWorld, shape: AddressShape) -> Tuple[Any, Any, str, Any]:
    """
    Build a lender whose own index at the address has no active version: X bound, W staged and split off, X disposed
    (its claim released).

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.

    Returns:
        Tuple[Any, Any, str, Any]: The lender Book, its root, W's spell_id and W's index.
    """
    world.step = "lender: bind X, conjure, stage W, split W, dispose X"
    lender_book = world.book(world.frame("a"))
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "lender")
    x_index = index_of(lender_book, x_id)
    w_id = shape.stage(lender, "third", x_index)
    lender.remove_from_spell_index(spell_id=w_id, source_index=x_index)
    w_index = index_of(lender_book, w_id)
    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(x_id))
    return lender_book, lender, w_id, w_index


def p09a_copy_arrives_at_a_serving_borrower(world: ProbeWorld, shape: AddressShape, by_index: bool) -> str:
    """
    P09a: a copy of the lender's version at the address arrives at a borrower that serves the address with its own
    Y. In one frame the only constructible form: the lender's version is parked (its index has no active version,
    so the address was free for the borrower's bind); the lender then notches it active.

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.
        by_index (bool): Share with add_index_to_contract instead of add_spell_to_contract.

    Returns:
        str: The row verdict.
    """
    lender_book, lender, w_id, w_index = lender_with_split_parked_version(world, shape)
    world.step = "borrower: bind Y, conjure, link"
    borrower_book = world.book(world.frame("a"))
    shape.bind(borrower_book, "second")
    borrower = world.conjure(borrower_book, "borrower")
    borrower.link(lender)
    door = "add_index_to_contract (W's index)" if by_index else "add_spell_to_contract (W)"
    try:
        if by_index:
            borrower.add_index_to_contract(index=w_index, conduit=lender)
        else:
            borrower.add_spell_to_contract(spell_id=w_id, conduit=lender)
        shared = f"{door} admitted (copy parked: {w_id not in borrower_book._contracted_spells_by_id.get(lender._id, {})})"
    except Exception as error:
        shared = f"{refused(door, error)}"
    try:
        lender.notch_spell(spell_index=w_index, spell_id=w_id)
    except Exception as error:
        return (f"{shared}; then {refused('lender notch_spell (to W)', error)} | "
                f"{state(world, shape, [('borrower', borrower)])}")
    return admitted(world, shape, f"{shared}; the lender's notch to W stood", [("borrower", borrower)])


def p09b_borrower_binds_over_its_copy(world: ProbeWorld, shape: AddressShape, by_index: bool) -> str:
    """
    P09b: the borrower holds a contracted copy of the lender's X; it binds its own Y at the same address.

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.
        by_index (bool): Share with add_index_to_contract instead of add_spell_to_contract.

    Returns:
        str: The row verdict.
    """
    world.step = "lender: bind X, conjure; borrower: conjure, link, pull X"
    lender_book = world.book(world.frame("a"))
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "lender")
    borrower_book = world.book(world.frame("a"))
    borrower_book.bind(spell=Ledger, existence="many", permissions="create")
    borrower = world.conjure(borrower_book, "borrower")
    borrower.link(lender)
    if by_index:
        borrower.add_index_to_contract(index=index_of(lender_book, x_id), conduit=lender)
    else:
        borrower.add_spell_to_contract(spell_id=x_id, conduit=lender)
    before = state(world, shape, [("borrower", borrower)])
    try:
        shape.bind(borrower, "second")
    except Exception as error:
        return (f"borrower holds X's copy ({before}); {refused('borrower Conduit.bind (Y)', error)} | "
                f"{state(world, shape, [('borrower', borrower)])}")
    return admitted(world, shape, "the borrower bound Y over its copy of X", [("borrower", borrower)])


def p09c_link_across_frames(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P09c: X in frame a, Y in frame b; frame b's root links to frame a's to borrow X.

    Returns:
        str: The row verdict.
    """
    world.step = "frame a: bind X, conjure; frame b: bind Y, conjure"
    lender_book = world.book(world.frame("a"))
    x_id = shape.bind(lender_book, "first")
    lender = world.conjure(lender_book, "lender")
    borrower_book = world.book(world.frame("b"))
    shape.bind(borrower_book, "second")
    borrower = world.conjure(borrower_book, "borrower")
    try:
        borrower.link(lender)
        borrower.add_spell_to_contract(spell_id=x_id, conduit=lender)
    except Exception as error:
        return f"{refused('Conduit.link (across frames)', error)} | {state(world, shape, [('borrower', borrower)])}"
    return admitted(world, shape, "a cross-frame link carried X's copy to Y's root", [("borrower", borrower)])


def p10_upgrade_to_normal(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P10: X bound in the root's Book; a lesser is upgraded to a normal root (a new, empty Book of the same frame);
    the upgraded conduit binds Y at the address.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X, conjure, create a lesser and upgrade it"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    root = world.conjure(spellbook, "root")
    lesser = root.create_lesser_conduit()
    lesser.upgrade_to_normal(f"{world.scenario}-promoted")
    world.books.append(lesser.spellbook)
    world.roots.append(lesser)
    try:
        shape.bind(lesser, "second")
    except Exception as error:
        return (f"{refused('upgraded Conduit.bind (Y, new Book)', error)} | "
                f"{state(world, shape, [('root', root), ('upgraded', lesser)])}")
    return admitted(world, shape, "the upgraded root's new Book bound Y", [("root", root), ("upgraded", lesser)])


def p11a_phase4_public(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P11a: can two spells at one address be registered before conjure, so that conjure's Phase 4 meets them?

    Returns:
        str: The row verdict.
    """
    world.step = "bind X"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    try:
        shape.bind(spellbook, "second")
    except Exception as error:
        return (f"UNREACHABLE through the public doors: {refused('Spellbook.bind (Y)', error)} - "
                "Phase 4 never meets two at one address")
    world.step = "conjure"
    try:
        root = world.conjure(spellbook, "root")
    except Exception as error:
        return f"two registered; {refused('conjure (Phase 4)', error)}"
    return admitted(world, shape, "two registered and conjured", [("root", root)])


def p11b_phase4_forced(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P11b WHITE-BOX (a forced state, not a user path): Y bound at another binding name, then its `binding_name`
    field cleared so the Phase 4 pool holds two spells whose fields give one address; conjure.

    Returns:
        str: The row verdict.
    """
    world.step = "bind X and Y (binding 'p11-forced'), clear Y's binding_name"
    spellbook = world.book(world.frame("a"))
    shape.bind(spellbook, "first")
    target, spellframe = shape.members["second"]
    y_id = spellbook.bind(spell=target, spellframe=spellframe, binding_name="p11-forced", existence="many",
                          permissions="create")
    spellbook.find_spell_by_spell_id(y_id).binding_name = None
    try:
        root = world.conjure(spellbook, "root")
    except Exception as error:
        code = "DUPLICATE_SPELL_NAME" if "DUPLICATE_SPELL_NAME" in str(error) else "no DUPLICATE_SPELL_NAME code"
        return f"WHITE-BOX: {refused('conjure (Phase 4)', error)} [{code}]"
    return f"WHITE-BOX: conjure stood with the forced state; {state(world, shape, [('root', root)])}"


def p12_graft_into_a_serving_frame(world: ProbeWorld, shape: AddressShape) -> str:
    """
    P12: X's index recorded in a source frame (the source torn down), then grafted (fresh-index mode) into a host
    frame whose Book serves the address with its own Y.

    Returns:
        str: The row verdict.
    """
    from melder.crystallizer.asset_management import crystallizer_cache
    from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
    from melder.crystallizer.crystallizer import Crystallizer

    original = crystallizer_cache.CrystallizerCache.__dict__["resolve_cache_root_path"]
    with tempfile.TemporaryDirectory(prefix="dup_address_graft_") as temporary:
        cache_root = Path(temporary) / "__melder_cache__" / "__crystallizer_cache__"
        crystallizer_cache.CrystallizerCache.resolve_cache_root_path = staticmethod(lambda: cache_root)
        try:
            verdict = _graft_scenario(world, shape, Crystallizer, CrystallizerConfiguration)
            # Teardown while the cache root still points at the temporary directory: a recording world may write
            # on cleanup, and nothing may reach the real cache.
            failures = world.teardown()
            world.roots.clear()
            world.books.clear()
            if failures:
                verdict += f" [teardown: {'; '.join(failures)}]"
            reset_world()
            return verdict
        finally:
            crystallizer_cache.CrystallizerCache.resolve_cache_root_path = original


def _graft_scenario(world: ProbeWorld, shape: AddressShape, crystallizer_type: Any, configuration_type: Any) -> str:
    """
    The body of P12, run while the crystallizer cache points at a temporary directory.

    Args:
        world (ProbeWorld): The scenario world.
        shape (AddressShape): The shape.
        crystallizer_type (Any): The Crystallizer class.
        configuration_type (Any): The CrystallizerConfiguration class.

    Returns:
        str: The row verdict.
    """
    world.step = "activate the crystallizer"
    configuration = configuration_type().with_defaults()
    configuration.activate()
    crystallizer = crystallizer_type()
    crystallizer.activate(configuration)
    world.step = "source frame: bind X, conjure, capture the graft record, tear down"
    source_book = world.book(world.frame("src"), finalized=True)
    x_id = shape.bind(source_book, "first")
    source = world.conjure(source_book, "src")
    record = json.loads(json.dumps(crystallizer.capture_index_graft(index_of(source_book, x_id).id)))
    source.cleanup()
    source_book.cleanup()
    world.roots.remove(source)
    world.books.remove(source_book)
    world.step = "host frame: bind Y, conjure"
    host_book = world.book(world.frame("host"), finalized=True)
    shape.bind(host_book, "second")
    host = world.conjure(host_book, "host")
    try:
        report_value = crystallizer.graft_index(record, host_book)
    except Exception as error:
        return (f"{refused('Crystallizer.graft_index (fresh index; anchor bind)', error)} | "
                f"{state(world, shape, [('host', host)])}")
    return admitted(world, shape, f"graft report status={report_value.get('status')}", [("host", host)])


def scenarios() -> List[Tuple[str, str, Callable[[ProbeWorld, AddressShape], str]]]:
    """
    List every (path id, description, scenario) the matrix runs, in report order.

    Returns:
        List[Tuple[str, str, Callable[[ProbeWorld, AddressShape], str]]]: The scenarios.
    """
    return [
        ("P00", "control: versions of one index", p00_versions_of_one_index),
        ("P01", "bind before conjure (one Book)", p01_bind_before_conjure),
        ("P02", "bind after conjure (live dynamic root)", p02_bind_after_conjure),
        ("P03a", "two Books, both bind before conjure", p03a_two_books_both_before_conjure),
        ("P03b", "two Books, Y after Book 1's conjure", p03b_two_books_after_the_others_conjure),
        ("P03c", "two Books, both conjured, Y via root 2", p03c_two_books_both_conjured),
        ("P04a", "bind_inactive Y onto another binding's index", p04a_bind_inactive_into_another_binding),
        ("P04b", "bind_inactive Y onto a split index, notch", p04b_bind_inactive_into_split_index_then_notch),
        ("P05", "remove_from_spell_index Y, notch it", p05_remove_then_notch),
        ("P06a", "add_to_spell_index Y onto another binding", p06a_add_into_another_binding),
        ("P06b", "control: add Y back to its index, notch", p06b_add_back_then_notch),
        ("P06c", "add_to_spell_index of the ACTIVE X", p06c_add_the_active_version),
        ("P07a", "Spellbook.scan of a module with X and Y", lambda world, shape: p07_scan(world, shape, False)),
        ("P07b", "Conduit.scan of a module with X and Y", lambda world, shape: p07_scan(world, shape, True)),
        ("P08a", "transfer X into a Book serving A (1 frame)", p08a_transfer_same_frame),
        ("P08b", "transfer X in; target notches its parked W", p08b_transfer_onto_a_split_index),
        ("P08c", "transfer X into a Book serving A (2 frames)", p08c_transfer_across_frames),
        ("P08d", "transfer X across frames, then bind Y there", p08d_transfer_across_frames_then_bind),
        ("P09a-s", "W's copy (spell) to a borrower serving A", lambda world, shape: p09a_copy_arrives_at_a_serving_borrower(world, shape, False)),
        ("P09a-i", "W's index to a borrower serving A", lambda world, shape: p09a_copy_arrives_at_a_serving_borrower(world, shape, True)),
        ("P09b-s", "borrower binds Y over X's copy (spell)", lambda world, shape: p09b_borrower_binds_over_its_copy(world, shape, False)),
        ("P09b-i", "borrower binds Y over X's copy (index)", lambda world, shape: p09b_borrower_binds_over_its_copy(world, shape, True)),
        ("P09c", "link across frames to borrow X", p09c_link_across_frames),
        ("P10", "upgrade_to_normal, then bind Y", p10_upgrade_to_normal),
        ("P11a", "Phase 4: two registered before conjure?", p11a_phase4_public),
        ("P11b", "Phase 4 WHITE-BOX forced pool", p11b_phase4_forced),
        ("P12", "graft X's index into a frame serving A", p12_graft_into_a_serving_frame),
    ]


def classify(verdict: str) -> str:
    """
    Classify a row's verdict for the leading column and the tallies.

    Contract:
        - PROBE-ERROR first (a setup step failed: not a measurement), then a duplicate in one frame (two ACTIVE at
          the address), then the controls and the unreachable/white-box rows, then any refusal, then an admission
          that left one active spell.

    Args:
        verdict (str): The scenario's verdict text.

    Returns:
        str: PROBE-ERROR, ADMITTED-DUPLICATE, BY-DESIGN, UNREACHABLE, WHITE-BOX, REFUSED, ADMITTED-ONE-ACTIVE or OTHER.
    """
    if verdict.startswith("PROBE-ERROR"):
        return "PROBE-ERROR"
    if "TWO ACTIVE IN ONE FRAME" in verdict or "two active in one frame: True" in verdict:
        return "ADMITTED-DUPLICATE"
    if verdict.startswith("BY DESIGN"):
        return "BY-DESIGN"
    if verdict.startswith("UNREACHABLE"):
        return "UNREACHABLE"
    if verdict.startswith("WHITE-BOX"):
        return "WHITE-BOX"
    if "REFUSED at" in verdict:
        return "REFUSED"
    if verdict.startswith("ADMITTED"):
        return "ADMITTED-ONE-ACTIVE"
    return "OTHER"


def run_matrix() -> int:
    """
    Run every scenario for every shape in fresh singletons and print one row each, then the tallies.

    Returns:
        int: 0 (the probe reports; it does not judge).
    """
    # `melder.__version__` the attribute is the version string; the module is read through importlib.
    version_text = importlib.import_module("melder.__version__").__version__
    gil = "on" if sys._is_gil_enabled() else "off"
    print(f"duplicate_address_paths probe | melder {version_text} | Python {sys.version.split()[0]} | GIL {gil}")
    print("row: <path> | <shape> | <kind> | <verdict>   (X, Y, W = the shape's three spells; L = Ledger; "
          "B<n> = Book n of the scenario; claim[<frame suffix>:<holder>])")
    tallies: Dict[str, int] = {}
    for path_id, description, scenario in scenarios():
        print(f"--- {path_id}: {description}")
        for shape in build_shapes():
            reset_world()
            world = ProbeWorld(f"{path_id.lower()}-{shape.label.lower()}")
            try:
                verdict = scenario(world, shape)
            except Exception as error:
                verdict = f"PROBE-ERROR at '{world.step}' ({type(error).__name__}): {head(error)}"
            failures = world.teardown()
            if failures:
                verdict += f" [teardown: {'; '.join(failures)}]"
            kind = classify(verdict)
            tallies[kind] = tallies.get(kind, 0) + 1
            print(f"{path_id:<7}| {shape.label:<19}| {kind:<19}| {verdict}")
    reset_world()
    print("--- tallies: " + ", ".join(f"{kind}={count}" for kind, count in sorted(tallies.items())))
    return 0


def _main() -> int:
    """
    Put the repository (src first) on sys.path, import this file under its own name and run the matrix from it.

    Returns:
        int: The matrix's exit status.
    """
    probe_path = Path(__file__).resolve()
    repository = probe_path.parents[4]
    for entry in (str(probe_path.parent), str(repository), str(repository / "src")):
        if entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)
    probe_module = importlib.import_module(probe_path.stem)
    return probe_module.run_matrix()


if __name__ == "__main__":
    sys.exit(_main())

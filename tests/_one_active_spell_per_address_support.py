"""
Support for the one-active-spell-per-address tests: the shapes in which two spells claim one address, and a world
that builds Books and roots on dynamic frames and tears them down.

The owner's rule (chat, 2026-11-07): "sure 2 spells with the same name without differentiation, 2 spells with the same
spellframe without a binding_name ... you can add these or extend various features for this, if we don't already have
it". Two spells are never ACTIVE at one address. An address is the normalized `(frame_key, binding_key)` pair
(`SpellInputUtils.make_spell_key_from_parts`, the key `Spell.key` holds and the frame claim is keyed by): the
spellframe's name - or the spell's own name when it is bound bare - and the binding name, both lowercased, an empty
binding name being `__default__`.

The shapes (`address_shape`):
    S-category          three classes under the string spellframe 'Reports' / 'reports' / 'REPORTS'.
    S-protocol          three classes under the Protocol `Greeter`.
    S-protocol-homonym  the second class under another Protocol also named `Greeter` (one name, one address).
    N-scope             three bare classes all named `Report`, declared in three scopes.
    N-case              three bare classes named `Report`, `report` and `REPORT`.
Every member has its own code, so its own spell_id; the default binding name throughout.

The classes are module-level (or nested in module-level scopes) so a graft can hydrate a recorded one by its
qualname. Measured by `context_compass/artifacts/duplicate_address_paths_20261107/probes/duplicate_address_paths_probe.py`.
"""
from typing import Any, Dict, List, Optional, Protocol, Tuple

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


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
    """S-category, first spell (X): bound under the string spellframe 'Reports'."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-first"


class CategoryBeta:
    """S-category, second spell (Y): bound under the string spellframe 'reports' - the same address."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-second"


class CategoryGamma:
    """S-category, third spell (W): bound under the string spellframe 'REPORTS' - the same address."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "category-third"


class AlphaGreeter:
    """S-protocol shapes, first spell (X): bound under `Greeter`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-first"


class BetaGreeter:
    """S-protocol shapes, second spell (Y): bound under `Greeter`, or under its homonym."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-second"


class GammaGreeter:
    """S-protocol shapes, third spell (W): bound under `Greeter`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "greeter-third"


class Report:
    """N shapes, first spell (X): a bare class named `Report`, at ('report', '__default__')."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-first"


class _ScopeTwo:
    """A second scope declaring a class named `Report`."""

    class Report:
        """N-scope, second spell (Y): another class named `Report`."""

        def tag(self) -> str:
            """Return this spell's role tag."""
            return "report-scope-two"


class _ScopeThree:
    """A third scope declaring a class named `Report`."""

    class Report:
        """N-scope, third spell (W): a third class named `Report`."""

        def tag(self) -> str:
            """Return this spell's role tag."""
            return "report-scope-three"


class report:
    """N-case, second spell (Y): a bare class named `report` - the same address as `Report`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-lower"


class REPORT:
    """N-case, third spell (W): a bare class named `REPORT` - the same address as `Report`."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "report-upper"


class Ledger:
    """An unrelated bare spell at ('ledger', '__default__'): another index, at another address."""

    def tag(self) -> str:
        """Return this spell's role tag."""
        return "ledger"


class AddressShape:
    """
    One way three spells - X, Y and W - claim one address.

    Contract:
        - `members` maps a role ("first" = X, "second" = Y, "third" = W) to (class, spellframe); every member
          normalizes to `address`, and each class has its own code, so its own spell_id.
        - `meld` asks the address through the meld door the shape is addressed by: `meld(spellframe=...)` for the S
          shapes, `meld("Report")` - a human SpellName - for the N shapes.
        - `letter` names the spell an object was built from ("X", "Y", "W" or "L" for Ledger), by its tag.
        - A value holder with thin call helpers; owns nothing that needs cleanup.
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
            label (str): The shape's name ("S-category", ...), used as the test id.
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

    def cls(self, role: str) -> type:
        """
        Return the class of `role`.

        Args:
            role (str): "first", "second" or "third".

        Returns:
            type: The class.
        """
        return self.members[role][0]

    def spellframe(self, role: str) -> Any:
        """
        Return the spellframe `role` is bound under (None for the N shapes).

        Args:
            role (str): "first", "second" or "third".

        Returns:
            Any: A string category, a Protocol class or None.
        """
        return self.members[role][1]

    def bind(self, binder: Any, role: str) -> str:
        """
        Bind `role`'s class ACTIVE at the shape's address through `binder`, existence `many`.

        Args:
            binder (Any): A Spellbook or a normal Conduit.
            role (str): "first", "second" or "third".

        Returns:
            str: The spell_id `bind` returned.

        Raises:
            Exception: Whatever `bind` raises; the caller asserts it.
        """
        return binder.bind(
            spell=self.cls(role), spellframe=self.spellframe(role), existence="many", permissions="create",
        )

    def stage(self, conduit: Conduit, role: str, spell_index: SpellIndex) -> str:
        """
        Stage `role`'s class PARKED on `spell_index` through `conduit.bind_inactive`, bound the shape's way.

        Args:
            conduit (Conduit): A normal dynamic conduit of the Book that owns `spell_index`.
            role (str): "first", "second" or "third".
            spell_index (SpellIndex): The index the version joins.

        Returns:
            str: The spell_id `bind_inactive` returned.

        Raises:
            Exception: Whatever `bind_inactive` raises; the caller asserts it.
        """
        return conduit.bind_inactive(
            spell=self.cls(role), spell_index=spell_index, spellframe=self.spellframe(role), existence="many",
            permissions="create",
        )

    def meld(self, conduit: Conduit) -> Any:
        """
        Meld the shape's address through `conduit`.

        Args:
            conduit (Conduit): The conduit asked.

        Returns:
            Any: The object the address builds.

        Raises:
            Exception: Whatever the meld raises (KeyError when nothing serves the address).
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
            str: The SHA256 spell_id (the class's code).
        """
        return Bind.spell_id_inspector(self.cls(role))

    def letter(self, built: Any) -> str:
        """
        Name the spell `built` was built from.

        Args:
            built (Any): An object a meld returned.

        Returns:
            str: "X", "Y", "W", "L" (Ledger), or the object's tag when it is none of them.
        """
        letters = {self.cls("first")().tag(): "X", self.cls("second")().tag(): "Y", self.cls("third")().tag(): "W",
                   "ledger": "L"}
        tag = built.tag()
        return letters.get(tag, tag)


def address_shape_labels() -> List[str]:
    """
    Return the labels of the shapes, in test-id order.

    Returns:
        List[str]: The five shape labels.
    """
    return ["S-category", "S-protocol", "S-protocol-homonym", "N-scope", "N-case"]


def address_shape(label: str) -> AddressShape:
    """
    Build the shape named `label`.

    Args:
        label (str): One of `address_shape_labels()`.

    Returns:
        AddressShape: The shape.

    Raises:
        KeyError: For an unknown label.
    """
    shapes = {
        "S-category": AddressShape(
            "S-category", ("reports", "__default__"),
            {"first": (CategoryAlpha, "Reports"), "second": (CategoryBeta, "reports"),
             "third": (CategoryGamma, "REPORTS")},
            {"spellframe": "Reports"}, None,
        ),
        "S-protocol": AddressShape(
            "S-protocol", ("greeter", "__default__"),
            {"first": (AlphaGreeter, Greeter), "second": (BetaGreeter, Greeter), "third": (GammaGreeter, Greeter)},
            {"spellframe": Greeter}, None,
        ),
        "S-protocol-homonym": AddressShape(
            "S-protocol-homonym", ("greeter", "__default__"),
            {"first": (AlphaGreeter, Greeter), "second": (BetaGreeter, _TwinScope.Greeter),
             "third": (GammaGreeter, Greeter)},
            {"spellframe": Greeter}, None,
        ),
        "N-scope": AddressShape(
            "N-scope", ("report", "__default__"),
            {"first": (Report, None), "second": (_ScopeTwo.Report, None), "third": (_ScopeThree.Report, None)},
            {}, "Report",
        ),
        "N-case": AddressShape(
            "N-case", ("report", "__default__"),
            {"first": (Report, None), "second": (report, None), "third": (REPORT, None)},
            {}, "Report",
        ),
    }
    return shapes[label]


def reset_address_world() -> None:
    """
    Install fresh AetherUtilitySystem, Nexus, Crystallizer and Aether singletons and rebind Spellbook and Conduit.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class AddressWorld:
    """
    The Books and roots one test builds on dynamic frames, the address views its assertions read, and their teardown.

    Contract:
        - `book(frame)` builds a Spellbook on frame `addr-<frame>` with its own default configuration, settling the
          frame dynamic with caching off on the frame's first Book; `finalized=True` freezes the configuration before
          any bind (the recorded lane's canon, needed while the crystallizer records).
        - `conjure` and `adopt` keep every root for `teardown`, which cleans the roots (last first), then the Books.
        - The address views read the public `Spellbook.spells` map and the frame's claim.
    """

    def __init__(self) -> None:
        """
        Start an empty world.

        Returns:
            None.
        """
        self.books: List[Spellbook] = []
        self.roots: List[Conduit] = []
        self.settled: List[str] = []

    def book(self, frame: str, *, finalized: bool = False) -> Spellbook:
        """
        Build a Spellbook on frame `addr-<frame>`, settling the frame dynamic (caching off) on first use.

        Args:
            frame (str): The frame suffix.
            finalized (bool): Freeze the configuration before any bind.

        Returns:
            Spellbook: The Book, not conjured.
        """
        frame_name = f"addr-{frame}"
        configuration = SpellbookConfiguration(frame_name).with_defaults()
        if finalized:
            configuration.finalize()
        spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
        if frame_name not in self.settled:
            spellbook.configure_aether_frame(
                system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
            )
            self.settled.append(frame_name)
        self.books.append(spellbook)
        return spellbook

    def conjure(self, spellbook: Spellbook, name: str) -> Conduit:
        """
        Conjure `spellbook`'s dynamic root and keep it for teardown.

        Args:
            spellbook (Spellbook): The Book.
            name (str): The root's name.

        Returns:
            Conduit: The root.
        """
        root = spellbook.conjure(dynamic=True, name=name)
        self.roots.append(root)
        return root

    def adopt(self, root: Conduit) -> None:
        """
        Keep a root this world did not conjure (an upgraded lesser) and its new Book for teardown.

        Args:
            root (Conduit): The normal root.

        Returns:
            None.
        """
        self.roots.append(root)
        self.books.append(root.spellbook)

    def retire(self, root: Conduit, spellbook: Spellbook) -> None:
        """
        Clean `root` and `spellbook` now and drop them from the teardown lists.

        Args:
            root (Conduit): A root this world conjured.
            spellbook (Spellbook): Its Book.

        Returns:
            None.
        """
        root.cleanup()
        spellbook.cleanup()
        self.roots.remove(root)
        self.books.remove(spellbook)

    def active_ids_at(self, address: Tuple[str, str]) -> List[str]:
        """
        Return the spell_ids ACTIVE at `address` in every live Book of this world.

        Args:
            address (Tuple[str, str]): The normalized (frame_key, binding_key).

        Returns:
            List[str]: One entry per active spell at the address; two in one frame would break the rule.
        """
        return [spell.spell_id for spellbook in self.books for spell in spellbook.spells.values()
                if spell.key == address]

    @staticmethod
    def active_ids_in(spellbook: Spellbook, address: Tuple[str, str]) -> List[str]:
        """
        Return the spell_ids ACTIVE at `address` in one Book.

        Args:
            spellbook (Spellbook): The Book read (its public `spells` map).
            address (Tuple[str, str]): The normalized (frame_key, binding_key).

        Returns:
            List[str]: One entry per active spell of that Book at the address.
        """
        return [spell.spell_id for spell in spellbook.spells.values() if spell.key == address]

    @staticmethod
    def claim(spellbook: Spellbook, address: Tuple[str, str]) -> Optional[str]:
        """
        Return the spell_id holding `address` in `spellbook`'s frame.

        Args:
            spellbook (Spellbook): A Book of the frame.
            address (Tuple[str, str]): The normalized (frame_key, binding_key).

        Returns:
            Optional[str]: The holder's spell_id, or None when nothing holds the address.
        """
        return spellbook._aetheric_frame.get_lookup(address)

    def teardown(self) -> None:
        """
        Clean every root (last first), then every Book (last first).

        Returns:
            None.

        Raises:
            Exception: A cleanup failure propagates, so a broken teardown fails the test that caused it.
        """
        for root in reversed(self.roots):
            root.cleanup()
        for spellbook in reversed(self.books):
            spellbook.cleanup()
        self.roots.clear()
        self.books.clear()


def index_of(spellbook: Spellbook, spell_id: str) -> SpellIndex:
    """
    Return the SpellIndex of the version `spellbook` holds under `spell_id`, active or parked.

    Args:
        spellbook (Spellbook): The owning Book.
        spell_id (str): The version's spell_id.

    Returns:
        SpellIndex: Its index.

    Raises:
        AssertionError: When the Book holds no such version.
    """
    spell = spellbook.find_spell_by_spell_id(spell_id)
    assert spell is not None, f"the Book holds no version {spell_id[:12]}"
    return spell.spell_index

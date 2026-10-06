"""
Apply the annotation-kind matching change set (patch annotation_kind_matching_2026_10_04) to one source tree.

Usage: python apply_kind_matching_src.py <repo_root>

Every edit anchors on exact text and asserts it occurs once; each file keeps its own line endings. Run on
the VM mirror first, then on the tree.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()


def read(rel: str):
    path = ROOT / rel
    raw = path.read_bytes()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    return path, raw.decode("utf-8"), nl


def write(path: pathlib.Path, text: str, nl: str, original_nl_text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def replace_once(text: str, old: str, new: str, nl: str, label: str) -> str:
    old_n = old.replace("\n", nl)
    new_n = new.replace("\n", nl)
    count = text.count(old_n)
    assert count == 1, f"{label}: anchor found {count} times"
    return text.replace(old_n, new_n)


# ---------------------------------------------------------------------------
# 1. New enum module
# ---------------------------------------------------------------------------
enum_dir = ROOT / "src/melder/aether/spellbook/spellframe_kind"
enum_dir.mkdir(exist_ok=True)
(enum_dir / "__init__.py").write_bytes(b"")
ENUM_SRC = '''from enum import Enum


class SpellframeKind(Enum):
    """
    What kind of thing a spell's `spellframe` is.

    Purpose:
        A spellframe is the category half of a spell's address, and a binding
        may declare it in exactly two forms: a string, which is a plain
        category label, or a `typing.Protocol` class, which is a label AND a
        contract that bind checked the spell against. The kind is recorded on
        the `Spell` at bind so Phase 3 reads it instead of inferring a meaning
        from the frame's name (a category named like a class is not a provider
        of that class).

    Contract:
        - `none`: bound without a spellframe; the address label is the spell's
          own name. The spell answers to its type and, in a collection, to its
          own name as a label.
        - `category`: a string spellframe. A pure label: reached by explicit
          addressing (`meld(spellframe=..., binding_name=...)`, `SpellMap`,
          `SpellContract`) and by collection annotations naming the label; it
          never satisfies a single annotation, whatever its spelling.
        - `contract`: a Protocol spellframe. Bind verified the spell's directly
          declared public members against it; a parameter annotated with that
          Protocol (as a class or as a `TYPE_CHECKING` string) resolves to the
          spells recorded under it, and a collection of it gathers them.
        - Any other object offered as a spellframe is refused at bind
          (TypeError); there is no fourth kind.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Users read it off a
        `Spell` (`spell.spellframe_kind`); they never pass it to `bind`.

    Subsystem Context:
        The vocabulary `Bind` writes and `CompilerPhase3` reads; the
        crystallizer records the member's name so a restore rebinds the frame
        as the kind it was.
    """

    none = "none"
    category = "category"
    contract = "contract"
'''
(enum_dir / "spellframe_kind.py").write_bytes(ENUM_SRC.replace("\n", "\r\n").encode("utf-8"))

# ---------------------------------------------------------------------------
# 2. general_helpers: is_protocol_type
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/utilities/helpers/general_helpers.py")
text = replace_once(text, '''        return raw.lower()

    @staticmethod
    def normalize_spell_name(spell: Any) -> str:
''', '''        return raw.lower()

    @staticmethod
    def is_protocol_type(candidate: Any) -> bool:
        """
        Return True when `candidate` is a `typing.Protocol` class.

        Contract:
            - True for a class carrying the `_is_protocol` / `__is_protocol__`
              flag that `typing.Protocol` sets on every protocol subclass (and
              on `Protocol` itself). `issubclass(..., Protocol)` is avoided
              because static checkers reject it on protocols that are not
              `@runtime_checkable`.
            - False for anything that is not a class, so a string category or
              an instance never reads as a contract.
            - The flags are read with `getattr` deliberately: the object is the
              typing module's, not ours, and the flag's name moved between
              Python versions.

        Args:
            candidate: Any object offered as a spellframe or found in an annotation.

        Returns:
            bool: Whether `candidate` is a Protocol class.
        """
        if not inspect.isclass(candidate):
            return False
        if getattr(candidate, "_is_protocol", False):
            return True
        return bool(getattr(candidate, "__is_protocol__", False))

    @staticmethod
    def normalize_spell_name(spell: Any) -> str:
''', nl, "helpers.is_protocol_type")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 3. spell.py: the two fields
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/aether/spellbook/spell.py")
text = replace_once(text, '''from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable
''', '''from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.general_base.cleanable import Cleanable
''', nl, "spell import")
text = replace_once(text, '''        - `spellframe` distinguishes the context it was declared in (e.g., Protocol, class,
          or string frame).
''', '''        - `spellframe` is the category half of the address: a string category or a
          Protocol contract. `spellframe_kind` records which (or `none` for a bare
          binding) and `implemented_protocols` the Protocol bind checked the spell
          against, so Phase 3 never infers a meaning from the frame's name.
''', nl, "spell key concepts")
text = replace_once(text, '''            *args: Any,
            resolvable: bool = True,
            **kwargs: Any,
    ) -> None:
        """
        Internal constructor for a bound Spell record.
''', '''            *args: Any,
            resolvable: bool = True,
            spellframe_kind: SpellframeKind = SpellframeKind.none,
            implemented_protocols: tuple[type, ...] = (),
            **kwargs: Any,
    ) -> None:
        """
        Internal constructor for a bound Spell record.
''', nl, "spell signature")
text = replace_once(text, '''            resolvable (bool): Validated per-version resolution capability. Stored natively,
                outside metadata, and independent of active/parked or compiler readiness state.
            **kwargs: Optional keyword metadata map, collected into `metadata`.
''', '''            resolvable (bool): Validated per-version resolution capability. Stored natively,
                outside metadata, and independent of active/parked or compiler readiness state.
            spellframe_kind (SpellframeKind): What `spellframe` is - `none` (bare), `category`
                (a string) or `contract` (a Protocol) - as Bind classified it. Phase 3 reads it.
            implemented_protocols (tuple[type, ...]): The Protocol(s) Bind structurally checked
                this spell against: `(spellframe,)` for a contract frame, else empty.
            **kwargs: Optional keyword metadata map, collected into `metadata`.
''', nl, "spell docstring args")
text = replace_once(text, '''        "_creation_context_failure",
        "_creation_gate",
    ]
''', '''        "_creation_context_failure",
        "_creation_gate",
        "spellframe_kind",
        "implemented_protocols",
    ]
''', nl, "spell slots (appended last: hot-slot offsets stay put)")
text = replace_once(text, '''        self.spellframe: Any | None = spellframe
        self.spell_type: SpellType = spell_type
''', '''        self.spellframe: Any | None = spellframe
        # Frame kind recorded by Bind (none / category / contract) and the
        # Protocol this spell was structurally checked against. Identity data
        # like `spellframe`: Phase 3 reads the kind instead of inferring a
        # meaning from the frame's name, and both survive cleanup.
        self.spellframe_kind: SpellframeKind = spellframe_kind
        self.implemented_protocols: tuple[type, ...] = implemented_protocols
        self.spell_type: SpellType = spell_type
''', nl, "spell fields")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 4. bind.py: classification, refusal, Spell call, delegate
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/aether/spellbook/bind/bind.py")
text = replace_once(text, '''from melder.aether.spellbook.spell import Spell
from melder._build_assets._bind_guard.bind_guard import INTERNAL_MANIFEST
''', '''from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder._build_assets._bind_guard.bind_guard import INTERNAL_MANIFEST
''', nl, "bind imports")
text = replace_once(text, '''            spellframe (Optional[Any]): Logical interface or Protocol used as the DI contract / grouping key.
            binding_name (Optional[str]): A specific key used to distinguish this spell among others in its frame.
            profile (str): Spell profile family to attach to the final Spell.
''', '''            spellframe (Optional[Any]): The category half of the address: a string label, or a
                `typing.Protocol` that is both a label and a contract the spell is checked against.
                Anything else (a concrete class, an instance) is refused with TypeError.
            binding_name (Optional[str]): A specific key used to distinguish this spell among others in its frame.
            profile (str): Spell profile family to attach to the final Spell.
''', nl, "bind() args doc")
text = replace_once(text, '''            TypeError: If a class or supplied existing object lacks a required
                directly declared Protocol member or exposes a non-callable
                value where that Protocol requires a callable, or resolvable is not a bool.
        """
        self.check_cleaned()
        if spell is None:
''', '''            TypeError: If a class or supplied existing object lacks a required
                directly declared Protocol member or exposes a non-callable
                value where that Protocol requires a callable, or resolvable is not a bool,
                or `spellframe` is neither None, a string nor a Protocol class.
        """
        self.check_cleaned()
        if spell is None:
''', nl, "bind() raises doc")
text = replace_once(text, '''        * Enforces Protocol/Spellframe semantics:
          - Protocol targets require explicit resolvable=False.
          - Class-based and existing-object spells bound under a Protocol
            spellframe must satisfy its directly declared public members.
            Existing objects are checked on the supplied value, not its class.
          - Method/lambda spells may also be grouped under Protocol or string
            spellframes (factory / handler semantics), but are not structurally
            validated against the Protocol.
''', '''        * Enforces Protocol/Spellframe semantics:
          - Protocol targets require explicit resolvable=False.
          - A spellframe is a string category or a Protocol contract; its kind
            is recorded on the Spell. Any other object is refused (TypeError).
          - Class-based and existing-object spells bound under a Protocol
            spellframe must satisfy its directly declared public members.
            Existing objects are checked on the supplied value, not its class.
          - Method/lambda spells may also be grouped under Protocol or string
            spellframes (factory / handler semantics), but are not structurally
            validated against the Protocol.
''', nl, "_bind_logic doc semantics")
text = replace_once(text, '''            spellframe (Optional[Any]): Logical interface or category for grouping
                (typically a Protocol used as a DI contract).
            binding_name (Optional[str]): A specific key used to distinguish this spell.
            profile (str): Spell profile family to attach after Spell creation.
''', '''            spellframe (Optional[Any]): A string category label or a Protocol contract;
                None binds bare. Any other object is refused.
            binding_name (Optional[str]): A specific key used to distinguish this spell.
            profile (str): Spell profile family to attach after Spell creation.
''', nl, "_bind_logic doc args")
text = replace_once(text, '''            TypeError:
                - If resolvable is not a bool, or a Protocol target is resolvable.
                - If a class or existing object under a Protocol spellframe
                  fails its directly declared public-member check.
            ValueError:
''', '''            TypeError:
                - If resolvable is not a bool, or a Protocol target is resolvable.
                - If `spellframe` is neither None, a string nor a Protocol class.
                - If a class or existing object under a Protocol spellframe
                  fails its directly declared public-member check.
            ValueError:
''', nl, "_bind_logic doc raises")
text = replace_once(text, '''            if resolvable and Bind._is_protocol_type(spell):
                raise TypeError(
                    f"Cannot bind Protocol '{spell.__name__}' as a concrete spell. "
                    f"Use it as a spellframe (DI contract), or pass resolvable=False "
                    f"to register a non-resolvable definition."
                )

            # ------------------------------------------------------------------
            # 2. Build binding profile and fingerprint
''', '''            if resolvable and Bind._is_protocol_type(spell):
                raise TypeError(
                    f"Cannot bind Protocol '{spell.__name__}' as a concrete spell. "
                    f"Use it as a spellframe (DI contract), or pass resolvable=False "
                    f"to register a non-resolvable definition."
                )

            # ------------------------------------------------------------------
            # 1.5 Classify the spellframe: category, contract, bare - or refused
            # ------------------------------------------------------------------
            # Owner ruling 2026-10-03: a spellframe is a label; a Protocol frame
            # is a label and a contract; a concrete class is not a spellframe.
            # The kind is recorded on the Spell so Phase 3 reads it instead of
            # inferring a meaning from the frame's name.
            spellframe_kind, implemented_protocols = Bind._classify_spellframe(spellframe)

            # ------------------------------------------------------------------
            # 2. Build binding profile and fingerprint
''', nl, "bind step 1.5")
text = replace_once(text, '''            # ------------------------------------------------------------------
            # 4. Protocol spellframe semantics
            # ------------------------------------------------------------------
            # If the caller provided a Protocol as the spellframe:
            #   * For classes and existing objects: check the actual target's
            #     members, including instance-only or shadowed implementations.
            #   * For callable spells: allow binding (factory/handler semantics),
            #     but do not run structural checks (no meaningful attribute set).
            if spellframe is not None and Bind._is_protocol_type(spellframe):
                if isinstance(binding_profile, ClassBindingProfile) or is_instance:
''', '''            # ------------------------------------------------------------------
            # 4. Protocol spellframe semantics
            # ------------------------------------------------------------------
            # If the caller provided a Protocol as the spellframe (kind `contract`):
            #   * For classes and existing objects: check the actual target's
            #     members, including instance-only or shadowed implementations.
            #   * For callable spells: allow binding (factory/handler semantics),
            #     but do not run structural checks (no meaningful attribute set).
            if spellframe_kind is SpellframeKind.contract:
                if isinstance(binding_profile, ClassBindingProfile) or is_instance:
''', nl, "bind step 4")
text = replace_once(text, '''                disposal_method_names=resolved_disposal_method_names,
                resolvable=resolvable,
                # Owner ruling 2026-07-19: leftover bind kwargs flow into
''', '''                disposal_method_names=resolved_disposal_method_names,
                resolvable=resolvable,
                spellframe_kind=spellframe_kind,
                implemented_protocols=implemented_protocols,
                # Owner ruling 2026-07-19: leftover bind kwargs flow into
''', nl, "bind Spell call")
text = replace_once(text, '''    @staticmethod
    def _is_protocol_type(obj: Any) -> bool:
        """
        Returns True if `obj` is a `typing.Protocol`-style interface.

        Instead of using ``issubclass(obj, Protocol)`` (which static type
        checkers complain about unless the protocol is marked
        ``@runtime_checkable``), we rely on the internal flag that
        ``typing.Protocol`` sets on all protocol subclasses.

        This keeps the check runtime-friendly and IDE-friendly while still
        correctly identifying Protocol-based spellframes.
        """
        if not inspect.isclass(obj):
            return False

        # PEP 544 / typing implementation detail:
        # Protocol subclasses have a private flag set on the class.
        # Different Python versions may use `_is_protocol` or `__is_protocol__`,
        # so we check both defensively.
        if getattr(obj, "_is_protocol", False):
            return True
        if getattr(obj, "__is_protocol__", False):
            return True

        return False
''', '''    @staticmethod
    def _is_protocol_type(obj: Any) -> bool:
        """
        Returns True if `obj` is a `typing.Protocol`-style interface.

        Delegates to `SpellInputUtils.is_protocol_type`, the one detection Bind
        and Phase 3 share, so a frame classified as a contract at bind is the
        same thing a Protocol annotation asks for at resolution. Kept on Bind as
        a thin alias for its existing callers.
        """
        return SpellInputUtils.is_protocol_type(obj)

    @staticmethod
    def _classify_spellframe(
            spellframe: Optional[Any],
    ) -> Tuple[SpellframeKind, Tuple[type, ...]]:
        """
        Classify a bind's `spellframe` into its kind, refusing anything that is not one.

        Contract:
            - None -> (`SpellframeKind.none`, ()): the address label is the spell's own name.
            - A `str` -> (`SpellframeKind.category`, ()). The string is a label; it is
              never checked against the spell and never satisfies an annotation.
            - A Protocol class (`SpellInputUtils.is_protocol_type`) ->
              (`SpellframeKind.contract`, (spellframe,)). The caller still runs the
              structural member check for class and existing-object spells.
            - Anything else - a concrete class, an instance, a number - raises
              TypeError naming what was passed and the two accepted forms. Before
              2026-10-04 such objects were accepted and keyed by their name; a concrete
              class used as a label is now written as its name string, and a class
              meant as a contract is declared as a `typing.Protocol`.

        Args:
            spellframe: The value passed to `bind(..., spellframe=...)`.

        Returns:
            Tuple[SpellframeKind, Tuple[type, ...]]: The kind and the Protocol(s) the
            spell is recorded as implementing (one for a contract, none otherwise).

        Raises:
            TypeError: When `spellframe` is neither None, a string nor a Protocol class.
        """
        if spellframe is None:
            return SpellframeKind.none, ()
        if isinstance(spellframe, str):
            return SpellframeKind.category, ()
        if SpellInputUtils.is_protocol_type(spellframe):
            return SpellframeKind.contract, (spellframe,)
        if inspect.isclass(spellframe):
            offered = f"the concrete class '{spellframe.__name__}'"
            remedy = (
                f"To group spells under it as a label, pass its name "
                f"(spellframe={spellframe.__name__!r}); to make it a contract the "
                f"spell is checked against, declare it as a typing.Protocol."
            )
        else:
            offered = f"an object of type '{type(spellframe).__name__}'"
            remedy = "Pass a string label or a typing.Protocol class."
        raise TypeError(
            "spellframe must be a string category or a Protocol contract; "
            f"got {offered}. {remedy}"
        )
''', nl, "bind _is_protocol_type + _classify_spellframe")
write(path, text, nl, text)
print("part 1 (enum, helpers, spell, bind) applied")

# ---------------------------------------------------------------------------
# 5. compiler_phase_3.py: kind-aware predicate, three-bucket index, resolvers
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py")
text = replace_once(text, '''from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Set, Tuple, Union, get_args, get_origin
''', '''from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    get_args,
    get_origin,
)
''', nl, "phase3 typing import")
text = replace_once(text, '''from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.helpers.general_helpers import SpellInputUtils
''', '''from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.helpers.general_helpers import SpellInputUtils
''', nl, "phase3 enum import")

start_anchor = "    @staticmethod" + nl + "    def _annotation_key(annotation: Any) -> str:"
end_anchor = "        ordered = sorted(collected.values(), key=lambda record: record[0])" + nl + \
             "        return {record[2]: record[3] for record in ordered}" + nl
start = text.index(start_anchor)
end = text.index(end_anchor, start) + len(end_anchor)
assert text.count(start_anchor) == 1 and text.count(end_anchor) == 1

NEW_BLOCK = '''    # Annotation kinds. Class-level constants (no module globals): the vocabulary
    # `_annotation_kind` returns and the matching table below is keyed on.
    _KIND_TYPE: ClassVar[str] = "type"
    _KIND_CONTRACT: ClassVar[str] = "contract"
    _KIND_NAME: ClassVar[str] = "name"

    @staticmethod
    def _annotation_key(annotation: Any) -> str:
        """
        Return the lowercased key a DI annotation names.

        Contract:
            A `ForwardRef` keys by its name; everything else keys through
            `SpellInputUtils.normalize_frame_key` - a class or Protocol by
            `__name__`, a string by itself, anything else by `str()` -
            lowercased, the normalization every spell address already uses.
            The key says WHAT NAME was written; `_annotation_kind` says what
            kind of thing it names, and the two together select the spell keys
            it is compared against.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: The lowercased key.
        """
        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__
        return SpellInputUtils.normalize_frame_key(annotation)

    @classmethod
    def _annotation_kind(cls, annotation: Any) -> str:
        """
        Classify a normalized annotation as a contract, a type or a bare name.

        Contract (owner ruling 2026-10-03: a spellframe is a label; a Protocol
        frame is a label and a contract; an annotation names a type or a
        contract, never a category):
            - A Protocol class (`SpellInputUtils.is_protocol_type`) is
              `_KIND_CONTRACT`: the parameter asks for whatever bind checked
              against that Protocol.
            - Any other class is `_KIND_TYPE`: the parameter asks for instances
              of that class; an existing object counts through its class.
            - A string, a `ForwardRef` (a `TYPE_CHECKING`-only import leaves one
              at runtime) or anything else is `_KIND_NAME`: the kind cannot be
              told from the value, so the name is compared against every kind
              a name may stand for in that position - a type or a contract for
              a single socket, a label for a collection.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: One of `_KIND_CONTRACT`, `_KIND_TYPE`, `_KIND_NAME`.
        """
        if inspect.isclass(annotation):
            if SpellInputUtils.is_protocol_type(annotation):
                return cls._KIND_CONTRACT
            return cls._KIND_TYPE
        return cls._KIND_NAME

    @staticmethod
    def _spell_type_key(spell_obj: Spell) -> str:
        """
        Return the spell's type key: its lowercased name.

        Contract:
            `spell_name` is a class's name, or for an existing object the name
            of its class (Bind records `type(obj).__name__`), so the type key is
            what a class annotation of that type keys to. Methods and lambdas
            carry their function name here; `require_class_spell` keeps them
            out of single resolution before this key is read.

        Args:
            spell_obj: The candidate spell.

        Returns:
            str: The lowercased type key.
        """
        return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)

    @staticmethod
    def _spell_label_key(spell_obj: Spell) -> str:
        """
        Return the spell's address label: the frame key of its address.

        Contract:
            The spellframe's lowercased name (a string category as itself, a
            Protocol by `__name__`) when one was given, else the spell's own
            name - exactly the frame key `make_spell_key_from_parts` stores at
            bind. This is what a collection annotation written as a name
            gathers: the members of that label.

        Args:
            spell_obj: The candidate spell.

        Returns:
            str: The lowercased label key.
        """
        frame = spell_obj.spellframe
        if frame is None:
            return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        return SpellInputUtils.normalize_frame_key(frame)

    @staticmethod
    def _spell_contract_keys(spell_obj: Spell) -> Tuple[str, ...]:
        """
        Return the lowercased names of the Protocols the spell was checked against.

        Contract:
            Read from `Spell.implemented_protocols`, which Bind fills with the
            Protocol spellframe when the frame kind is `contract` (one entry
            today; the field is the seam a later `implements=` would extend).
            Empty for a bare binding and for a string category, so a category
            can never be reached through a contract comparison.

        Args:
            spell_obj: The candidate spell.

        Returns:
            Tuple[str, ...]: Zero or more lowercased contract keys.
        """
        return tuple(
            SpellInputUtils.normalize_frame_key(protocol)
            for protocol in spell_obj.implemented_protocols
        )

    @staticmethod
    def _spell_definition_key(spell_obj: Spell) -> Optional[str]:
        """
        Return the type key of a spell that IS a Protocol - a descriptive definition - else None.

        Contract:
            A Protocol can be bound only with `resolvable=False` (Bind refuses it
            as a concrete spell); such a binding describes the contract itself so a
            consumer annotated with the Protocol compiles an OVERRIDE_REQUIRED socket
            the caller supplies. A Protocol annotation therefore also matches the
            Protocol's own definition by name, and the resolvers' resolvable
            preference picks a real implementer whenever one is recorded.

        Args:
            spell_obj: The candidate spell.

        Returns:
            Optional[str]: The lowercased type key when the bound object is a Protocol class.
        """
        if SpellInputUtils.is_protocol_type(spell_obj.spell):
            return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        return None

    def _spell_keys_for(
            self,
            annotation_kind: str,
            spell_obj: Spell,
            *,
            collection: bool,
    ) -> Tuple[str, ...]:
        """
        Return the spell keys an annotation of `annotation_kind` is compared against.

        The matching table (single socket | collection):
            - type:     type key                      | type key
            - contract: contract keys + definition    | contract keys + definition
            - name:     type + contract               | label key
        "definition" is the type key of a spell that is itself a Protocol (bound
        `resolvable=False` as the contract's description). A category label is
        reachable only through a collection written as a name (`list["storage"]`),
        never through a single socket, and a class annotation never reads a frame
        of any kind.

        Args:
            annotation_kind: One of the `_KIND_*` constants.
            spell_obj: The candidate spell.
            collection: True when resolving a COLLECTION_BY_ANNOTATION socket.

        Returns:
            Tuple[str, ...]: The keys to compare the annotation key against.
        """
        if annotation_kind == self._KIND_TYPE:
            return (self._spell_type_key(spell_obj),)
        if annotation_kind == self._KIND_CONTRACT:
            definition_key = self._spell_definition_key(spell_obj)
            if definition_key is None:
                return self._spell_contract_keys(spell_obj)
            return self._spell_contract_keys(spell_obj) + (definition_key,)
        if collection:
            return (self._spell_label_key(spell_obj),)
        return (self._spell_type_key(spell_obj),) + self._spell_contract_keys(spell_obj)

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
            collection: bool = False,
    ) -> bool:
        """
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by annotation kind, 2026-10-04):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell keys its kind selects (`_spell_keys_for`): a class
              annotation compares with the spell's type key; a Protocol
              annotation with the Protocols bind recorded on the spell; a string
              with the type or contract keys on a single socket and with the
              address label on a collection. A spell under a string category is
              therefore reached by its type or, in a collection, by the category's
              name - never does the category's name make it a provider of a
              class spelled the same way.
            - `binding_name`, when given, must equal the spell's binding name.
            - `require_class_spell=True` excludes METHOD/LAMBDA spell kinds.

        Args:
            annotation:
                Canonicalized annotation to match.
            binding_name:
                Optional binding-name filter.
            spell_obj:
                Candidate spell.
            require_class_spell:
                When True, only class-like spells are allowed.
            collection:
                True for a COLLECTION_BY_ANNOTATION socket (a name gathers a label).

        Returns:
            bool: `True` when the candidate should be considered for this
            dependency.
        """
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        kind = self._annotation_kind(annotation)
        if self._annotation_key(annotation) not in self._spell_keys_for(kind, spell_obj, collection=collection):
            return False
        if binding_name is not None and spell_obj.binding_name != binding_name:
            return False
        return True

    @staticmethod
    def _eq_safe_object(candidate: Any) -> bool:
        """
        Return True when equality on `candidate` is provably identity/str-like.

        Purpose:
            The structural snapshot's replayability rule: it marks a pool
            non-replayable when a bound object or spellframe carries a custom
            `__eq__`. Phase 3 itself no longer needs it - its index matches by
            key, which is exact for every pool (2026-10-03).

        Contract:
            - None, str, classes with the default `type.__eq__` metaclass
              behavior, and instances whose type uses `object.__eq__` are
              safe.
            - Anything else (custom `__eq__`, custom metaclass `__eq__`)
              flags the whole pass as eq-risky and disables the index so the
              original scan semantics are preserved byte-for-byte.
        """
        if candidate is None or isinstance(candidate, str):
            return True
        if isinstance(candidate, type):
            return type(candidate).__eq__ is type.__eq__
        return type(candidate).__eq__ is object.__eq__

    def _build_candidate_index(self, spellbook: Spellbook) -> Dict[str, Any]:
        """
        Build the pass-scoped phase-3 candidate index over the live pool.

        Purpose:
            Collapse the O(dependencies x spells) annotation scans into one
            bucket lookup per dependency. Three bucket maps, one per spell key
            kind - type, label, contract - so a lookup reads exactly the
            buckets the annotation's kind selects (`_spell_keys_for`). Keys
            derive from pass-invariant inputs (binds are transactional and the
            resolution pass runs post-bind): spellframe, its kind and spell_name.

        Contract:
            - Entries are `(pool_position, spell_index, spell_obj)` so a bucket
              can be re-sorted into `_spell_id_pool` iteration order, keeping
              collection-injection order identical to the scan implementation.
            - Each spell is appended once to `by_type` and once to `by_label`
              (the two may be the same key for a bare binding), once per
              recorded contract to `by_contract`, and - when the bound object
              is itself a Protocol - once to `by_definition` under its type key.
            - Keys are strings, so bucket membership equals scan membership for
              every pool; no equality guard is needed.

        Returns:
            Dict[str, Any]: `{"by_type": {...}, "by_label": {...}, "by_contract": {...},
            "by_definition": {...}}`, each mapping a key to its list of entries.
        """
        by_type: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_label: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_contract: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_definition: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            by_type.setdefault(self._spell_type_key(spell_obj), []).append(entry)
            by_label.setdefault(self._spell_label_key(spell_obj), []).append(entry)
            for key in self._spell_contract_keys(spell_obj):
                by_contract.setdefault(key, []).append(entry)
            definition_key = self._spell_definition_key(spell_obj)
            if definition_key is not None:
                by_definition.setdefault(definition_key, []).append(entry)
        return {
            "by_type": by_type,
            "by_label": by_label,
            "by_contract": by_contract,
            "by_definition": by_definition,
        }

    def _get_candidate_index(
            self,
            spellbook: Spellbook,
            resolution_pass_cache: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Return the usable pass-scoped candidate index, building it lazily.

        Contract:
            - Returns None (scan path) only when no pass cache was supplied;
              the key index is exact for every pool (2026-10-03).
            - Benign build race under multi-worker scheduling: the build is
              idempotent over pass-invariant inputs and the last writer wins
              with an equivalent value (same contract as the phase-4
              binding-graph memo in `validation_pass_cache`).
        """
        if resolution_pass_cache is None:
            return None
        index = resolution_pass_cache.get("phase3_candidate_index")
        if index is None:
            index = self._build_candidate_index(spellbook)
            resolution_pass_cache["phase3_candidate_index"] = index
        return index

    def _index_buckets_for(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            collection: bool,
    ) -> Tuple[Optional[List[Tuple[int, Any, Spell]]], ...]:
        """
        Select the index bucket(s) an annotation reads, by the same table as `_spell_keys_for`.

        Args:
            candidate_index: The three-map index from `_build_candidate_index`.
            annotation: The normalized annotation.
            collection: True for a COLLECTION_BY_ANNOTATION socket.

        Returns:
            Tuple[Optional[List[...]], ...]: One bucket for a type or a
            collection-name lookup; the contract and definition buckets for a
            Protocol; the type and contract buckets for a single-socket name.
            A missing bucket is None.
        """
        key = self._annotation_key(annotation)
        kind = self._annotation_kind(annotation)
        if kind == self._KIND_TYPE:
            return (candidate_index["by_type"].get(key),)
        if kind == self._KIND_CONTRACT:
            return (candidate_index["by_contract"].get(key), candidate_index["by_definition"].get(key))
        if collection:
            return (candidate_index["by_label"].get(key),)
        return (candidate_index["by_type"].get(key), candidate_index["by_contract"].get(key))

    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
            collection: bool = False,
    ) -> Dict[Any, "Spell"]:
        """
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the bucket(s) `_index_buckets_for` selects for the
              annotation's kind and socket shape; membership equals scan
              membership because both sides use the same keys and the same
              table (2026-10-04). An entry present in two buckets (a name that
              is both a type key and a contract key of one spell) is seen once.
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        """
        buckets = self._index_buckets_for(candidate_index, annotation, collection=collection)

        # Replicate the scan's dict semantics exactly: when one SpellIndex
        # matches through multiple pool entries (version lineages), the scan
        # keeps the FIRST insertion position but the LAST matching spell
        # object (dict insert-then-overwrite).
        # collected: id(index) -> [first_pos, value_pos, index, spell_obj]
        collected: Dict[int, List[Any]] = {}
        for bucket in buckets:
            for position, index, spell_obj in (bucket or ()):
                if require_class_spell and spell_obj.spell_type in (
                        SpellType.METHOD,
                        SpellType.METHOD_WITH_BINDING_NAME,
                        SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
                ):
                    continue
                record = collected.get(id(index))
                if record is None:
                    collected[id(index)] = [position, position, index, spell_obj]
                    continue
                if position < record[0]:
                    record[0] = position
                if position > record[1]:
                    record[1] = position
                    record[3] = spell_obj

        ordered = sorted(collected.values(), key=lambda record: record[0])
        return {record[2]: record[3] for record in ordered}
'''.replace("\n", nl)
text = text[:start] + NEW_BLOCK + text[end:]

# resolvers: single passes collection=False explicitly for readability; collection passes True
text = replace_once(text, '''        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=False,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=False,
                ):
                    candidates[index] = spell_obj

        return {index: candidate for index, candidate in candidates.items() if candidate.resolvable}
''', '''        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=False,
                collection=True,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=False,
                        collection=True,
                ):
                    candidates[index] = spell_obj

        return {index: candidate for index, candidate in candidates.items() if candidate.resolvable}
''', nl, "collection resolver")
text = replace_once(text, '''            Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
            spells (classes, methods, lambdas) bound under the given frame/type.
            
            This corresponds to list[FrameType]-style DI where the user explicitly
            asked for "all implementations". Non-resolvable definitions are
            excluded after the existing matching and ordering decisions.
''', '''            Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
            spells (classes, methods, lambdas) in the group the annotation names.
            
            This corresponds to list[...]-style DI where the user explicitly
            asked for "all of them": `list[Proto]` gathers the spells recorded
            under that Protocol, `list["label"]` the members of that category
            (or the bare spells named so), `list[Cls]` the spells of that class
            (2026-10-04, `_spell_keys_for`). Non-resolvable definitions are
            excluded after the existing matching and ordering decisions.
''', nl, "collection docstring")
text = replace_once(text, '''        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Prefer matching resolvable providers. Only when none exist may a single
''', '''        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        A class annotation selects spells of that class, a Protocol annotation
        the spells bind recorded under it, a string either by name - never the
        members of a string category (2026-10-04, `_spell_keys_for`).
        Prefer matching resolvable providers. Only when none exist may a single
''', nl, "single docstring")
write(path, text, nl, text)
print("part 2 (phase 3) applied")


def replace_n(text: str, old: str, new: str, nl: str, label: str, expected: int) -> str:
    old_n = old.replace("\n", nl)
    new_n = new.replace("\n", nl)
    count = text.count(old_n)
    assert count == expected, f"{label}: anchor found {count} times, expected {expected}"
    return text.replace(old_n, new_n)


# ---------------------------------------------------------------------------
# 6. SpellCrystal: frame kind and coordinates
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/crystallizer/crystals/spell_crystal.py")
text = replace_once(text, '''        "_spellframe_name",
        "_existence_name",
''', '''        "_spellframe_name",
        "_spellframe_kind",
        "_spellframe_module",
        "_spellframe_qualname",
        "_existence_name",
''', nl, "crystal slots")
text = replace_once(text, '''        self._spellframe_name: Optional[str] = (
            getattr(spellframe, "__name__", str(spellframe))
            if spellframe is not None
            else None
        )
        self._existence_name: str = spell.existence.name
''', '''        self._spellframe_name: Optional[str] = (
            getattr(spellframe, "__name__", str(spellframe))
            if spellframe is not None
            else None
        )
        # Frame kind (record 4.1.0): the kind Bind recorded ("none", "category",
        # "contract") and, for a contract, the Protocol's module coordinates so a
        # restore rebinds it as a contract rather than a same-named category.
        # Plain values only; the enum is read off the Spell, never imported here.
        self._spellframe_kind: str = spell.spellframe_kind.name
        self._spellframe_module: Optional[str] = (
            spellframe.__module__ if self._spellframe_kind == "contract" else None
        )
        self._spellframe_qualname: Optional[str] = (
            spellframe.__qualname__ if self._spellframe_kind == "contract" else None
        )
        self._existence_name: str = spell.existence.name
''', nl, "crystal ctor")
text = replace_once(text, '''            del self._spellframe_name
            del self._existence_name
''', '''            del self._spellframe_name
            del self._spellframe_kind
            del self._spellframe_module
            del self._spellframe_qualname
            del self._existence_name
''', nl, "crystal cleanup")
text = replace_once(text, '''        self.check_cleaned()
        with self._lock:
            return self._spellframe_name

    @property
    def existence_name(self) -> str:
''', '''        self.check_cleaned()
        with self._lock:
            return self._spellframe_name

    @property
    def spellframe_kind(self) -> str:
        """
        Return the frame kind recorded at bind: "none", "category" or "contract".

        Contract:
            - The `SpellframeKind` member NAME as Bind classified the frame
              (record 4.1.0); a restore reads it to rebind a Protocol frame as a
              contract instead of a same-named category.

        Returns:
            str: "none" (bound bare), "category" (a string label) or "contract"
            (a Protocol the spell was checked against).
        """
        self.check_cleaned()
        with self._lock:
            return self._spellframe_kind

    @property
    def spellframe_module(self) -> Optional[str]:
        """
        Return the Protocol's module for a contract frame, else None.

        Returns:
            Optional[str]: `__module__` of the Protocol spellframe when the kind
            is "contract"; None for a bare binding or a string category.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellframe_module

    @property
    def spellframe_qualname(self) -> Optional[str]:
        """
        Return the Protocol's qualified name for a contract frame, else None.

        Returns:
            Optional[str]: `__qualname__` of the Protocol spellframe when the
            kind is "contract"; None otherwise. With `spellframe_module` it is
            the import coordinate a loader hydrates the contract from.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellframe_qualname

    @property
    def existence_name(self) -> str:
''', nl, "crystal properties")
text = replace_once(text, '''                "spellframe_name": self._spellframe_name,
                "existence_name": self._existence_name,
''', '''                "spellframe_name": self._spellframe_name,
                "spellframe_kind": self._spellframe_kind,
                "spellframe_module": self._spellframe_module,
                "spellframe_qualname": self._spellframe_qualname,
                "existence_name": self._existence_name,
''', nl, "crystal describe")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 7. RestoreEngine: hydrate the frame kind
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/crystallizer/crystal_loader_system/restore_engine.py")
text = replace_n(text, '''            spellframe=crystal.get("spellframe_name"),
''', '''            spellframe=self._hydrate_spellframe(custody_key, crystal),
''', nl, "restore spellframe sites", 2)
text = replace_once(text, '''    @staticmethod
    def _import_qualified_target(module_name: str, qualname: str) -> Any:
''', '''    def _hydrate_spellframe(
            self,
            custody_key: str,
            crystal: Dict[str, object],
    ) -> Optional[Any]:
        """
        Rebuild one bind's spellframe as the kind it was recorded with.

        Contract:
            - Recorded kind "contract" (record 4.1.0): import the Protocol by its
              recorded coordinates (`spellframe_module`, `spellframe_qualname`)
              through the normal import lane and return the class, so the rebound
              spell is a contract member again and Protocol-typed consumers resolve
              as they did in the recorded world. A failed import files a shortfall
              (`spellframe_contract_hydration_failed`) and returns the recorded
              NAME, which binds the spell as a category: it still exists and is
              addressable by name, and the report says what was lost.
            - Any other kind, and a record older than 4.1.0 (no kind), returns the
              recorded name (or None for a bare binding) exactly as before.

        Args:
            custody_key:
                The folded custody key (shortfall anchor).
            crystal:
                The folded custody payload.

        Returns:
            Optional[Any]: A Protocol class, a string label, or None.
        """
        name = crystal.get("spellframe_name")
        if str(crystal.get("spellframe_kind")) != "contract":
            return name
        module_name = str(crystal.get("spellframe_module"))
        qualname = str(crystal.get("spellframe_qualname"))
        try:
            return self._import_qualified_target(module_name, qualname)
        except Exception as error:
            # Best-effort by contract: the frame degrades to its name and the
            # ledger carries the cause; the spell itself is still rebuilt.
            self._report.add_shortfall(
                "spell_crystal", custody_key,
                "spellframe_contract_hydration_failed ({0}.{1}): {2}; "
                "bound as the category {3!r}".format(
                    module_name, qualname, error, name
                ),
            )
            return name

    @staticmethod
    def _import_qualified_target(module_name: str, qualname: str) -> Any:
''', nl, "restore helper")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 8. GraftRunner: the same for the three graft sites
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/crystallizer/crystal_loader_system/graft_runner.py")
text = replace_once(text, '''        new_spell_id = self._host_book.bind(
            spell=target,
            existence=str(crystal.get("existence_name", "unique")),
            permissions=str(crystal.get("permissions_name", "create")),
            spellframe=crystal.get("spellframe_name"),
''', '''        new_spell_id = self._host_book.bind(
            spell=target,
            existence=str(crystal.get("existence_name", "unique")),
            permissions=str(crystal.get("permissions_name", "create")),
            spellframe=self._hydrate_spellframe(selected_id, crystal, shortfalls),
''', nl, "graft selected site")
text = replace_n(text, '''                spellframe=crystal.get("spellframe_name"),
''', '''                spellframe=self._hydrate_spellframe(spell_id, crystal, shortfalls),
''', nl, "graft parked/merge sites", 2)
text = replace_once(text, '''    @staticmethod
    def _import_target(module_name: str, qualname: str) -> Any:
''', '''    def _hydrate_spellframe(
            self,
            spell_id: str,
            crystal: Dict[str, object],
            shortfalls: List[Dict[str, object]],
    ) -> Optional[Any]:
        """
        Rebuild one member's spellframe as the kind it was recorded with.

        Contract:
            - Recorded kind "contract" (record 4.1.0): import the Protocol by its
              recorded coordinates through the normal import lane and return the
              class, so the grafted member is a contract member again. A failed
              import appends an honest shortfall row
              (`spellframe_contract_hydration_failed`) and returns the recorded
              NAME, binding the member as a category so it still exists.
            - Any other kind, and a record older than 4.1.0, returns the recorded
              name (or None) exactly as before. Never raises.

        Args:
            spell_id:
                The member's custody identity (shortfall anchor).
            crystal:
                The member's custody payload.
            shortfalls:
                Collector for honest rows.

        Returns:
            Optional[Any]: A Protocol class, a string label, or None.
        """
        name = crystal.get("spellframe_name")
        if str(crystal.get("spellframe_kind")) != "contract":
            return name
        module_name = str(crystal.get("spellframe_module"))
        qualname = str(crystal.get("spellframe_qualname"))
        try:
            return self._import_target(module_name, qualname)
        except Exception as error:
            # Best-effort by contract: degrade to the name, record the cause.
            shortfalls.append({
                "member": spell_id,
                "reason": "spellframe_contract_hydration_failed ({0}.{1}): {2}; "
                          "bound as the category {3!r}".format(
                              module_name, qualname, error, name
                          ),
            })
            return name

    @staticmethod
    def _import_target(module_name: str, qualname: str) -> Any:
''', nl, "graft helper")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 9. RecordVersion 4.1.0
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/crystallizer/persistence/record_version.py")
text = replace_once(text, '''    # Major 4 fences frame-scoped custody keys ("<spell_id>@<frame>", per-frame
    # spell ids): an older loader would fold one frame's copy over another's.
    CURRENT: ClassVar[str] = "4.0.0"
''', '''    # Major 4 fences frame-scoped custody keys ("<spell_id>@<frame>", per-frame
    # spell ids): an older loader would fold one frame's copy over another's.
    # Minor 4.1 adds the spell crystal's frame kind and the Protocol coordinates
    # of a contract frame (`spellframe_kind`, `spellframe_module`,
    # `spellframe_qualname`); 4.0 readers ignore them, and a 4.0 record read by
    # a 4.1 loader rebinds frames by name as before.
    CURRENT: ClassVar[str] = "4.1.0"
''', nl, "record version")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 10. Cache generation 20
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/utilities/caching_system/caching_system.py")
text = replace_once(text, '''    # `world_stamp` to equal the live world, so a bundle that cannot carry
    # one is cold rather than admitted as a stamp-less full hit.
    CACHE_VERSION_HISTORY: ClassVar[Mapping[int, str]] = MappingProxyType({
''', '''    # `world_stamp` to equal the live world, so a bundle that cannot carry
    # one is cold rather than admitted as a stamp-less full hit.
    # Version 20 retires bundles captured before annotation-kind matching
    # (2026-10-04): their structural rows were resolved by the name matcher,
    # which read a string category named like a class as that class's
    # provider set; the kind matcher resolves such sockets differently.
    CACHE_VERSION_HISTORY: ClassVar[Mapping[int, str]] = MappingProxyType({
''', nl, "cache comment")
text = replace_once(text, '''        19: "executor_world_stamp",
    })
''', '''        19: "executor_world_stamp",
        20: "annotation_kind_matching",
    })
''', nl, "cache table")
write(path, text, nl, text)

# ---------------------------------------------------------------------------
# 11. Package root export
# ---------------------------------------------------------------------------
path, text, nl = read("src/melder/__init__.py")
text = replace_once(text, '''from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
''', '''from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.aether.spellbook.spell import Spell
''', nl, "init import")
text = replace_once(text, '''    "SpellMap",
''', '''    "SpellMap",
    "SpellframeKind",
''', nl, "init __all__")
write(path, text, nl, text)
print("part 3 (crystallizer, record version, cache generation, export) applied")

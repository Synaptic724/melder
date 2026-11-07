from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Sequence, Tuple

from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.helpers.general_helpers import SpellInputUtils

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


class HiddenProviderReport:
    """
    Internal

    Render where a class lookup's class is bound when the lookup cannot reach it - the one wording every report of a
    hidden provider uses.

    Purpose:
        A class lookup - a class annotation, a single string annotation's type part, `list[Class]`,
        `SpellMap(spell=Class)` without a spellframe - reaches a spell only when it is bound bare, with no spellframe
        and the default binding (`CompilerPhase3._answers_class_lookup`, 2026-11-07). When such a lookup finds
        nothing while spells of that class are bound under a spellframe or a binding name, Phase 3 records them as
        hidden candidates (`SpellSocketDescriptor.hidden_spell_ids`) and four reports name them: Phase 4's
        HIDDEN_PROVIDER error (`HiddenProviderStrategy`), Phase 6's `collection_socket_no_providers`
        (`EmptyCollectionStrategy`), the meld-time `UnresolvedInputError`, and Phase 3's own RuntimeError for a
        direct `_resolve_spellmap_default` caller. This class is their single renderer, so a candidate reads the same
        everywhere (patch hidden_provider_2026_11_07, owner-approved 2026-11-07).

    Contract:
        - Pure and stateless: static and class methods over value dicts; reads a `Spell` only in `describe`; never
          looks anything up, never raises for a candidate it cannot describe.
        - A candidate is the dict `describe` returns: `spell_id`, `spell_name`, `spellframe` (a category as itself,
          a Protocol by `__name__`, None when bare), `spellframe_kind` (`SpellframeKind` value, None when unknown)
          and `binding_name` (as bound, None for the default). A candidate whose spell could not be found carries
          only its id and renders as `spell id <id>`, with no lookup.
        - Candidates are always rendered in address order - (spellframe, binding_name, spell_name), None first -
          the order AMBIGUOUS_PROVIDER uses.
        - Lookups by shape: `SHAPE_SINGLE` and `SHAPE_SPELLMAP` render the `SpellMap` that reaches the candidate's
          address (`SpellMap(spellframe=P, binding_name='b')`, a Protocol unquoted and a category quoted; the
          binding name left out for the default binding; `SpellMap(Name, binding_name='b')` or `SpellMap(Name)` for
          a bare candidate); `SHAPE_LIST` renders the collection that gathers it (`list[P]`, `list['c']`, and
          `list['Name']` for a bare candidate - a string list gathers the bare spells named so under any binding).

    Registration:
        MELDER KERNEL - internal helper of the `validation` package; never bound.

    Subsystem Context:
        Beside `SpellValidationSystem` in the `validation` package; imported by `HiddenProviderStrategy`,
        `EmptyCollectionStrategy`, `UnresolvedInputError` and `CompilerPhase3`.

    System Context:
        Phases 3, 4 and 6 of the conjure pipeline and the meld failure path; it renders, it decides nothing.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Pure renderer of hidden candidates (spells of a class bound only under a spellframe or a
        binding name): describe, order, the "where" words, the lookup per shape and the four report texts.
    """

    __slots__ = ()

    # Lookup shapes: which surface a rendered lookup reaches the candidate through.
    SHAPE_SINGLE: ClassVar[str] = "single"
    SHAPE_SPELLMAP: ClassVar[str] = "spellmap"
    SHAPE_LIST: ClassVar[str] = "list"

    @staticmethod
    def describe(candidate_id: str, spell: Optional[Spell]) -> Dict[str, Optional[str]]:
        """
        Describe one hidden candidate as a value dict.

        Contract:
            - With a spell: its name, its spellframe for display (a string category as itself, a Protocol by
              `__name__`, None when bare), the `SpellframeKind` value and the binding name as bound.
            - Without one (the caller's lookup found no spell under the id): the id and None everywhere else.
            - Reads bind-time fields only; no lock, no lookup.

        Args:
            candidate_id: The spell id the socket recorded.
            spell: The spell under that id, or None when the caller could not find it.

        Returns:
            Dict[str, Optional[str]]: `{spell_id, spell_name, spellframe, spellframe_kind, binding_name}`.
        """
        if spell is None:
            return {
                "spell_id": candidate_id, "spell_name": None, "spellframe": None,
                "spellframe_kind": None, "binding_name": None,
            }
        frame = spell.spellframe
        if frame is None:
            frame_text: Optional[str] = None
        elif isinstance(frame, str):
            frame_text = frame
        else:
            # Bind admits only a string category or a Protocol class as a spellframe.
            frame_text = frame.__name__
        return {
            "spell_id": candidate_id,
            "spell_name": spell.spell_name,
            "spellframe": frame_text,
            "spellframe_kind": spell.spellframe_kind.value,
            "binding_name": spell.binding_name,
        }

    @staticmethod
    def ordered(candidates: Sequence[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        """
        Return the candidates in address order.

        Contract:
            Sorted by (spellframe, binding_name, spell_name) with None first; the input is not mutated.

        Args:
            candidates: Candidate dicts from `describe`.

        Returns:
            List[Dict[str, Optional[str]]]: A new, ordered list.
        """
        return sorted(
            candidates,
            key=lambda entry: (entry["spellframe"] or "", entry["binding_name"] or "", entry["spell_name"] or ""),
        )

    @staticmethod
    def where(candidates: Sequence[Dict[str, Optional[str]]]) -> str:
        """
        Name where the class is bound: under a spellframe, a binding name, or either.

        Contract:
            - Reads the described candidates only (a candidate known by id alone says nothing).
            - "under a spellframe" when every described candidate has one, "under a binding name" when none has,
              "under a spellframe or a binding name" when they differ or none is described.

        Args:
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The phrase, without a leading or trailing space.
        """
        known = [entry for entry in candidates if entry["spell_name"] is not None]
        framed = [entry for entry in known if entry["spellframe"] is not None]
        if known and len(framed) == len(known):
            return "under a spellframe"
        if known and not framed:
            return "under a binding name"
        return "under a spellframe or a binding name"

    @staticmethod
    def is_default_binding(binding_name: Optional[str]) -> bool:
        """
        Return True when a binding name normalizes to the default binding.

        Contract:
            None and "" name the default binding, as in every address key (`SpellInputUtils.normalize_binding_name`).

        Args:
            binding_name: A binding name as bound or as a SpellMap wrote it.

        Returns:
            bool: Whether it is the default binding.
        """
        return SpellInputUtils.normalize_binding_name(binding_name) == SpellInputUtils.DEFAULT_BINDING_NAME

    @classmethod
    def lookup(
            cls,
            candidate: Dict[str, Optional[str]],
            *,
            shape: str,
            class_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Render the lookup that reaches one candidate through the given surface.

        Contract:
            - None for a candidate known by id alone.
            - `SHAPE_LIST`: `list[P]` for a Protocol frame, `list['c']` for a category, `list['Name']` when bare.
            - `SHAPE_SINGLE` / `SHAPE_SPELLMAP`: `SpellMap(spellframe=P, binding_name='b')` (a Protocol unquoted, a
              category quoted, the binding name left out when it is the default); a bare candidate renders
              `SpellMap(Name, binding_name='b')`, or `SpellMap(Name)` under the default binding.

        Args:
            candidate: One dict from `describe`.
            shape: `SHAPE_SINGLE`, `SHAPE_SPELLMAP` or `SHAPE_LIST`.
            class_name: The class name a bare-candidate `SpellMap` names; the candidate's own name when None.

        Returns:
            Optional[str]: The lookup, or None when the candidate is not described.
        """
        name = candidate["spell_name"]
        if name is None:
            return None
        frame = candidate["spellframe"]
        binding = candidate["binding_name"]
        is_contract = candidate["spellframe_kind"] == SpellframeKind.contract.value
        if shape == cls.SHAPE_LIST:
            if frame is None:
                return f"list[{name!r}]"
            return f"list[{frame}]" if is_contract else f"list[{frame!r}]"
        if frame is None:
            target = name if class_name is None else class_name
            if cls.is_default_binding(binding):
                return f"SpellMap({target})"
            return f"SpellMap({target}, binding_name={binding!r})"
        frame_text = frame if is_contract else repr(frame)
        if cls.is_default_binding(binding):
            return f"SpellMap(spellframe={frame_text})"
        return f"SpellMap(spellframe={frame_text}, binding_name={binding!r})"

    @classmethod
    def entry(
            cls,
            candidate: Dict[str, Optional[str]],
            *,
            shape: str,
            class_name: Optional[str] = None,
    ) -> str:
        """
        Render one candidate as `<Name> at (spellframe=..., binding_name=...) - use <lookup>`.

        Contract:
            The address part is AMBIGUOUS_PROVIDER's rendering; a candidate known by id alone renders
            `spell id <id>` with no lookup.

        Args:
            candidate: One dict from `describe`.
            shape: The lookup shape (see `lookup`).
            class_name: Passed to `lookup`.

        Returns:
            str: The rendered entry.
        """
        if candidate["spell_name"] is None:
            return f"spell id {candidate['spell_id']}"
        address = (
            f"{candidate['spell_name']} at (spellframe={candidate['spellframe']!r}, "
            f"binding_name={candidate['binding_name']!r})"
        )
        use = cls.lookup(candidate, shape=shape, class_name=class_name)
        return address if use is None else f"{address} - use {use}"

    @classmethod
    def entries(
            cls,
            candidates: Sequence[Dict[str, Optional[str]]],
            *,
            shape: str,
            class_name: Optional[str] = None,
    ) -> str:
        """
        Render every candidate, in address order, joined by "; ".

        Args:
            candidates: Candidate dicts from `describe`.
            shape: The lookup shape (see `lookup`).
            class_name: Passed to `lookup`.

        Returns:
            str: The joined entries.
        """
        return "; ".join(
            cls.entry(candidate, shape=shape, class_name=class_name) for candidate in cls.ordered(candidates)
        )

    @classmethod
    def with_uses(
            cls,
            candidates: Sequence[Dict[str, Optional[str]]],
            *,
            shape: str,
            class_name: Optional[str] = None,
    ) -> List[Dict[str, Optional[str]]]:
        """
        Return the candidates in address order, each with its lookup under "use", for a report's details payload.

        Args:
            candidates: Candidate dicts from `describe`.
            shape: The lookup shape (see `lookup`).
            class_name: Passed to `lookup`.

        Returns:
            List[Dict[str, Optional[str]]]: New dicts; the inputs are not mutated.
        """
        return [
            {**candidate, "use": cls.lookup(candidate, shape=shape, class_name=class_name)}
            for candidate in cls.ordered(candidates)
        ]

    @staticmethod
    def protocol_clause(candidates: Sequence[Dict[str, Optional[str]]]) -> str:
        """
        Offer the Protocol annotation as a second way to reach a candidate bound under a Protocol frame.

        Contract:
            - "" when no candidate is under a Protocol frame.
            - One Protocol: ", or a P annotation while that spell is the only one bound under P" - a Protocol
              annotation selects the frame's single implementation and is AMBIGUOUS_PROVIDER beside a second one.
            - Several: ", or an annotation with its Protocol while that spell is the only one bound under it".

        Args:
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The clause, starting with ", or" when not empty.
        """
        protocols = sorted({
            entry["spellframe"] for entry in candidates
            if entry["spellframe_kind"] == SpellframeKind.contract.value and entry["spellframe"] is not None
        })
        if not protocols:
            return ""
        if len(protocols) == 1:
            return f", or a {protocols[0]} annotation while that spell is the only one bound under {protocols[0]}"
        return ", or an annotation with its Protocol while that spell is the only one bound under it"

    @staticmethod
    def spell_display_name(value: object) -> str:
        """
        Name the class a `SpellMap(spell=...)` names, for display.

        Contract:
            A class renders as its `__qualname__`; any other object (an existing object a SpellMap names) as its
            type's `__qualname__`.

        Args:
            value: The SpellMap's `spell`.

        Returns:
            str: The display name.
        """
        if isinstance(value, type):
            return value.__qualname__
        return type(value).__qualname__

    @classmethod
    def spellmap_text(cls, class_name: str, binding_name: Optional[str]) -> str:
        """
        Render a class-lookup SpellMap as written: `SpellMap(X)` or `SpellMap(X, binding_name='b')`.

        Args:
            class_name: The display name of the SpellMap's spell.
            binding_name: The SpellMap's binding name (None or "" for the default binding).

        Returns:
            str: The rendering.
        """
        if cls.is_default_binding(binding_name):
            return f"SpellMap({class_name})"
        return f"SpellMap({class_name}, binding_name={binding_name!r})"

    @classmethod
    def annotation_message(
            cls,
            *,
            param_name: str,
            consumer_name: str,
            expected_type: str,
            candidates: Sequence[Dict[str, Optional[str]]],
    ) -> str:
        """
        Render HIDDEN_PROVIDER for a class annotation, a string annotation's type part or `Optional[Class]`.

        Contract:
            "Parameter 'p' on spell 'C' expects T, but a class lookup reaches T only where it is bound bare (no
            spellframe, the default binding), and T is bound only <where>: <entries>. Ask for it where it is bound -
            the SpellMap shown, as the parameter's default<protocol clause> - or bind T bare." "the SpellMap shown"
            reads "the SpellMap of the one it needs" for several candidates.

        Args:
            param_name: The consumer's parameter.
            consumer_name: The consumer spell's name.
            expected_type: The annotation's display name (`UnresolvedInputError.expected_type_name`).
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The message, without the "[HIDDEN_PROVIDER]" tag the report adds.
        """
        shown = "the SpellMap shown" if len(candidates) == 1 else "the SpellMap of the one it needs"
        return (
            f"Parameter {param_name!r} on spell {consumer_name!r} expects {expected_type}, but a class lookup reaches "
            f"{expected_type} only where it is bound bare (no spellframe, the default binding), and {expected_type} "
            f"is bound only {cls.where(candidates)}: {cls.entries(candidates, shape=cls.SHAPE_SINGLE)}. Ask for it "
            f"where it is bound - {shown}, as the parameter's default{cls.protocol_clause(candidates)} - or bind "
            f"{expected_type} bare."
        )

    @classmethod
    def spellmap_message(
            cls,
            *,
            param_name: str,
            consumer_name: str,
            class_name: str,
            binding_name: Optional[str],
            candidates: Sequence[Dict[str, Optional[str]]],
    ) -> str:
        """
        Render HIDDEN_PROVIDER for a `SpellMap(spell=X)` default without a spellframe that misses X.

        Contract:
            "Parameter 'p' on spell 'C' has the default SpellMap(X), a class lookup that reaches X only where it is
            bound bare under the default binding, but X is bound only where that lookup does not reach: <entries>.
            Point the SpellMap at the address it means, as shown, or bind X bare." With `binding_name='b'` the
            SpellMap renders with it, the scope reads "under the binding name 'b'" and the last clause "bind X bare
            under the binding name 'b'".

        Args:
            param_name: The consumer's parameter.
            consumer_name: The consumer spell's name.
            class_name: The display name of X (`spell_display_name`).
            binding_name: The SpellMap's binding name.
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The message, without the "[HIDDEN_PROVIDER]" tag the report adds.
        """
        if cls.is_default_binding(binding_name):
            scope = "the default binding"
            suffix = ""
        else:
            scope = f"the binding name {binding_name!r}"
            suffix = f" under the binding name {binding_name!r}"
        return (
            f"Parameter {param_name!r} on spell {consumer_name!r} has the default "
            f"{cls.spellmap_text(class_name, binding_name)}, a class lookup that reaches {class_name} only where it is "
            f"bound bare under {scope}, but {class_name} is bound only where that lookup does not reach: "
            f"{cls.entries(candidates, shape=cls.SHAPE_SPELLMAP, class_name=class_name)}. Point the SpellMap at the "
            f"address it means, as shown, or bind {class_name} bare{suffix}."
        )

    @classmethod
    def collection_clause(cls, candidates: Sequence[Dict[str, Optional[str]]]) -> Tuple[str, Optional[str]]:
        """
        Render the clause an empty required `list[Class]` report inserts, and the class name it uses.

        Contract:
            - The class name is the first described candidate's (address order); with none described the clause
              is "" and the name None, so the caller keeps its text without hidden candidates.
            - Clause: ": list[T] gathers T only where it is bound bare (no spellframe, the default binding), and T is
              bound only <where>: <entries>." with `SHAPE_LIST` lookups.

        Args:
            candidates: Candidate dicts from `describe`.

        Returns:
            Tuple[str, Optional[str]]: The clause (starting with ":") and the class name, or ("", None).
        """
        ordered = cls.ordered(candidates)
        names = [entry["spell_name"] for entry in ordered if entry["spell_name"] is not None]
        if not names:
            return "", None
        name = names[0]
        return (
            f": list[{name}] gathers {name} only where it is bound bare (no spellframe, the default binding), and "
            f"{name} is bound only {cls.where(ordered)}: {cls.entries(ordered, shape=cls.SHAPE_LIST)}.",
            name,
        )

    @classmethod
    def unresolved_input_message(
            cls,
            *,
            consumer_name: str,
            param_name: str,
            expected_type: str,
            candidates: Sequence[Dict[str, Optional[str]]],
    ) -> str:
        """
        Render `UnresolvedInputError`'s text for an unsupplied input whose class is bound only where it cannot be reached.

        Contract:
            "C.p expects T, but this meld did not supply it and a class lookup reaches T only where it is bound bare
            (no spellframe, the default binding), while T is bound only <where>: <entries>. Supply it with
            override={'p': ...} when melding C, a path key ending in '>p' (or '**p') when C is built as a dependency,
            ask for it where it is bound, as shown, or bind T bare."

        Args:
            consumer_name: The consumer spell's name.
            param_name: Its first missing parameter.
            expected_type: That parameter's display type.
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The message body (MeldExecutionError adds its "[MELD] ..." prefix).
        """
        return (
            f"{consumer_name}.{param_name} expects {expected_type}, but this meld did not supply it and a class lookup "
            f"reaches {expected_type} only where it is bound bare (no spellframe, the default binding), while "
            f"{expected_type} is bound only {cls.where(candidates)}: "
            f"{cls.entries(candidates, shape=cls.SHAPE_SINGLE)}. Supply it with override={{{param_name!r}: ...}} when "
            f"melding {consumer_name}, a path key ending in '>{param_name}' (or '**{param_name}') when "
            f"{consumer_name} is built as a dependency, ask for it where it is bound, as shown, or bind "
            f"{expected_type} bare."
        )

    @classmethod
    def spellmap_runtime_suffix(cls, *, class_name: str, candidates: Sequence[Dict[str, Optional[str]]]) -> str:
        """
        Render the sentence Phase 3 appends to its SpellMap RuntimeError for a direct caller.

        Contract:
            "X is bound only where this class lookup does not reach: <entries>." with `SHAPE_SPELLMAP` lookups.

        Args:
            class_name: The display name of the SpellMap's spell.
            candidates: Candidate dicts from `describe`.

        Returns:
            str: The sentence.
        """
        return (
            f"{class_name} is bound only where this class lookup does not reach: "
            f"{cls.entries(candidates, shape=cls.SHAPE_SPELLMAP, class_name=class_name)}."
        )

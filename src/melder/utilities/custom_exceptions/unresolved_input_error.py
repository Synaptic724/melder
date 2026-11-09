import annotationlib
import inspect
import types
import typing
from typing import TYPE_CHECKING, Any, Collection, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
from melder.aether.spellbook.spell_compiler.validation.hidden_provider_report import HiddenProviderReport
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor


class UnresolvedInputError(MeldExecutionError):
    """

    Purpose:
        Signal that a meld had to construct an object whose typed constructor
        parameter has no registered provider, and the meld did not supply the
        value. Names the consumer, the parameter, the expected type and how to
        supply it, instead of a bare Python missing-argument error.

    Raised When:
        Constructing an object whose Phase-3 topology carries an UNRESOLVED_INPUT
        socket (a single typed dependency no registered spell provides), and the
        constructing call's overrides did not supply that parameter. It fires only
        when that object is actually built: a stored (reused) object never demands
        its unresolved inputs, and conjure succeeds regardless. It is decided before
        construction: the many_only and generalized plans raise it before building
        anything under that object, and a solo root's call target raises it instead
        of calling the constructor (2026-09-26).

    What To Do About It:
        Supply the value in the meld's override payload: the parameter name when
        melding the consumer itself, a path key ending in `>param` (or a broadcast
        `**param`) when the consumer is built as a dependency. Or bind a provider
        for the expected type; the consumer re-resolves into a normal dependency
        on its next meld. When the expected class is registered, but only under a
        spellframe or a binding name - where a class lookup does not reach it -
        the message names each such address and the lookup that reaches it, and
        `hidden_spell_ids` lists those spells (2026-11-07).

    Contract:
        - A `MeldExecutionError`: code that catches `MeldExecutionError` keeps
          catching it. `node_id` is the consumer's spell id and `param_name` the
          first missing parameter.
        - `expected_type` is the parameter annotation's display name, read from the
          constructor signature on the failure path (Optional and forward references
          unwrapped); the lowercased frame key is used only if that is unreadable.
        - `unresolved_params` lists every missing unresolved parameter of the
          consumer, in signature order.
        - `inner` is None: nothing has been called when it is raised.
        - The text says "nothing registered provides it" only when nothing does.
          When the first missing parameter is a class lookup whose class is
          bound only under a spellframe or a binding name (found live in the
          consumer's Spellbook pool on this failure path, patch
          hidden_provider_2026_11_07), the text names each address and the
          `SpellMap` that reaches it, and `hidden_spell_ids` carries their ids.
          A socket whose Phase 3 recorded such candidates refuses its spell in
          Phase 4 (HIDDEN_PROVIDER), so this arises with candidates only where
          they appeared after the consumer compiled and nothing re-gated it.

    Owned State:
        - Inherited `spell_id`, `spell_name`, `node_id`, `param_name`, `inner`.
        - `expected_type`: display name of the first missing parameter's type.
        - `unresolved_params`: names of all missing unresolved parameters.
        - `hidden_spell_ids`: sorted ids of the spells of the expected class a
          class lookup does not reach; empty when there are none.

    Registration:
        A public exception type; import, raise, and catch freely. Like every
        Melder class it is refused as a spell registration.

    Subsystem Context:
        One of the `utilities/custom_exceptions/` types; the specific form of
        `MeldExecutionError` for the unresolved-input socket contract.

    System Context:
        Fires in the resolution layer at meld, after conjure produced the Conduit,
        before construction: from a plan (many_only, generalized) or from a solo
        root's call target. Successful melds never evaluate it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Raised at meld when an object whose typed parameter has no
        registered provider is built without that value; supply it by override
        (root key, `>param` path key or `**param`) or bind a provider for
        expected_type.
    """

    __slots__ = (
        "expected_type",
        "unresolved_params",
        "hidden_spell_ids",
    )

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            message: str,
            node_id: Optional[str] = None,
            param_name: Optional[str] = None,
            inner: Optional[BaseException] = None,
            expected_type: str,
            unresolved_params: Tuple[str, ...],
            hidden_spell_ids: Tuple[str, ...] = (),
    ) -> None:
        """
        Construct an unresolved-input failure.

        Args:
            spell_id:
                Id of the spell whose construction failed (the consumer).
            spell_name:
                Human-readable name of that spell.
            message:
                Remediation-bearing message naming the parameter, expected type
                and override keys.
            node_id:
                Consumer spell id; kept for `MeldExecutionError` attribution.
            param_name:
                First missing unresolved parameter.
            inner:
                None when Melder raises it (nothing was called); kept for the
                `MeldExecutionError` shape.
            expected_type:
                Display name of the first missing parameter's expected type.
            unresolved_params:
                Every missing unresolved parameter of the consumer, in signature
                order. Never empty.
            hidden_spell_ids:
                Ids of the spells of the first missing parameter's class that a
                class lookup does not reach (bound under a spellframe or a
                binding name), sorted; empty (the default) when there are none.

        Contract:
            - Preserves every `MeldExecutionError` field unchanged.

        Returns:
            None.
        """
        super().__init__(
            spell_id=spell_id,
            spell_name=spell_name,
            message=message,
            node_id=node_id,
            param_name=param_name,
            inner=inner,
        )
        self.expected_type: str = expected_type
        self.unresolved_params: Tuple[str, ...] = unresolved_params
        self.hidden_spell_ids: Tuple[str, ...] = hidden_spell_ids

    @staticmethod
    def expected_type_name(annotation: Any) -> str:
        """
        Render a parameter annotation as the expected-type display name.

        Purpose:
            One naming rule for the Phase-4 UNRESOLVED_INPUT warning and this
            error, so both name the type identically.

        Contract:
            - Unwraps `Optional[T]` / `Union[T, None]` to `T`, and a forward
              reference to its written name, mirroring Phase-3 matching.
            - A class renders as its `__qualname__`; any other annotation object
              as its `repr`.
            - A string renders as itself, minus one layer of matching quotes: a
              quoted annotation in a module using postponed evaluation arrives as
              the source text `'Name'`.
            - Pure: no lookups, no side effects.

        Args:
            annotation:
                The parameter's annotation: Phase-1 requirements at conjure, the
                constructor signature at meld.

        Returns:
            str: Display name of the expected type.
        """
        if isinstance(annotation, typing.ForwardRef):
            return annotation.__forward_arg__
        if isinstance(annotation, str):
            text = annotation.strip()
            if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
                return text[1:-1]
            return text
        origin = typing.get_origin(annotation)
        if origin is typing.Union or origin is types.UnionType:
            members = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
            if len(members) == 1:
                return UnresolvedInputError.expected_type_name(members[0])
        if isinstance(annotation, type):
            return annotation.__qualname__
        return repr(annotation)

    @classmethod
    def for_unsupplied(cls, spell: Spell, param_names: Collection[str]) -> UnresolvedInputError:
        """
        Build the error for unresolved inputs a plan knows are unsupplied, before any construction.

        Purpose:
            The decision before construction (design v2 S4, B6): a many_only or
            generalized plan, or a solo root's call target, raises this instead of
            calling a constructor that must fail.

        Contract:
            - Selects the consumer's UNRESOLVED_INPUT sockets named in
              `param_names` from its live Phase-3 topology and builds the message
              and fields in signature order; `inner` is None (nothing was called).

        Args:
            spell:
                The consumer about to be built.
            param_names:
                Its UNRESOLVED_INPUT parameters that the call does not supply.

        Raises:
            RuntimeError:
                When the topology has none of those sockets: the plan is stale
                (a plan is rebuilt whenever the topology re-resolves).

        Returns:
            UnresolvedInputError: The error to raise.
        """
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        wanted = set(param_names)
        missing: List[SpellSocketDescriptor] = []
        if topology is not None:
            for socket in topology.sockets:
                if socket.socket_kind is SocketKind.UNRESOLVED_INPUT and socket.param_name in wanted:
                    missing.append(socket)
        if not missing:
            raise RuntimeError(
                f"{spell.spell_name} has no unresolved input named {sorted(wanted)!r}; its plan is stale."
            )
        return cls._from_missing_sockets(spell, missing)

    @classmethod
    def _from_missing_sockets(
            cls,
            spell: Spell,
            missing: List[SpellSocketDescriptor],
    ) -> UnresolvedInputError:
        """
        Build the error from the consumer's missing UNRESOLVED_INPUT sockets.

        Contract:
            - The first missing socket (lowest position) names the type; the
              others are listed as "Also not supplied".
            - When the first socket's class lookup finds its class bound only
              under a spellframe or a binding name (`_hidden_candidates`, a live
              read of the consumer's pool), the text is
              `HiddenProviderReport.unresolved_input_message` and
              `hidden_spell_ids` carries the candidates; otherwise the text says
              nothing registered provides it, unchanged since 2026-09-26.

        Args:
            spell: The consumer.
            missing: Its unsupplied UNRESOLVED_INPUT sockets (any order; sorted here).

        Returns:
            UnresolvedInputError: The error to raise.
        """
        missing = sorted(missing, key=lambda socket: socket.position)
        first = missing[0]
        consumer = spell.spell_name
        param_name = first.param_name
        expected_type = cls._constructor_expected_type(spell, first)
        candidates = cls._hidden_candidates(spell, cls._constructor_annotation(spell, first))
        if candidates:
            message = HiddenProviderReport.unresolved_input_message(
                consumer_name=consumer,
                param_name=param_name,
                expected_type=expected_type,
                candidates=candidates,
            )
        else:
            message = (
                f"{consumer}.{param_name} expects {expected_type}, but nothing registered provides it "
                f"and this meld did not supply it. Supply it with override={{{param_name!r}: ...}} when "
                f"melding {consumer}, a path key ending in '>{param_name}' (or '**{param_name}') when "
                f"{consumer} is built as a dependency, or bind a provider for {expected_type}."
            )
        if len(missing) > 1:
            others = ", ".join(repr(socket.param_name) for socket in missing[1:])
            message += f" Also not supplied: {others}."
        spell_id = spell.spell_index.selected_spell_id
        return cls(
            spell_id=spell_id,
            spell_name=consumer,
            message=message,
            node_id=spell_id,
            param_name=param_name,
            inner=None,
            expected_type=expected_type,
            unresolved_params=tuple(socket.param_name for socket in missing),
            hidden_spell_ids=tuple(sorted(
                candidate["spell_id"] for candidate in candidates if candidate["spell_id"] is not None
            )),
        )

    @staticmethod
    def _constructor_annotation(spell: Spell, socket: SpellSocketDescriptor) -> object:
        """
        Read one unresolved parameter's annotation from the consumer's constructor signature.

        Contract:
            - Phase-1 requirements are released after resolution, so this re-reads
              the constructor signature with FORWARDREF annotations (a name that
              only exists under TYPE_CHECKING stays its written name).
            - Returns `inspect.Parameter.empty` when the signature cannot be read
              (TypeError, ValueError) or does not annotate the parameter.
            - Failure path only.

        Args:
            spell: The consumer whose construction failed.
            socket: One of its missing UNRESOLVED_INPUT sockets.

        Returns:
            object: The annotation, or `inspect.Parameter.empty`.
        """
        try:
            signature = inspect.signature(
                spell.spell,
                annotation_format=annotationlib.Format.FORWARDREF,
            )
        except (TypeError, ValueError):
            return inspect.Parameter.empty
        parameter = signature.parameters.get(socket.param_name)
        if parameter is None:
            return inspect.Parameter.empty
        annotation: object = parameter.annotation
        return annotation

    @staticmethod
    def _constructor_expected_type(spell: Spell, socket: SpellSocketDescriptor) -> str:
        """
        Name one unresolved parameter's expected type at meld time.

        Contract:
            - Renders the constructor annotation (`_constructor_annotation`)
              with `expected_type_name`.
            - When the signature cannot be read or does not annotate the
              parameter, the socket's watched frame key names the type instead.
            - Failure path only.

        Args:
            spell: The consumer whose construction failed.
            socket: Its first missing UNRESOLVED_INPUT socket.

        Returns:
            str: Display name of the expected type.
        """
        annotation = UnresolvedInputError._constructor_annotation(spell, socket)
        if annotation is not inspect.Parameter.empty:
            return UnresolvedInputError.expected_type_name(annotation)
        if socket.dependency_key is not None:
            return socket.dependency_key[0]
        return "an unregistered type"

    @staticmethod
    def _hidden_candidates(spell: Spell, annotation: object) -> List[Dict[str, Optional[str]]]:
        """
        Find, live, the spells of a class lookup's class that the lookup cannot reach.

        Purpose:
            A socket whose Phase 3 recorded hidden candidates refuses its spell
            in Phase 4 (HIDDEN_PROVIDER), so this error never sees them recorded.
            It still arises when such a spell was bound after the consumer
            compiled and nothing re-gated the consumer - then "nothing
            registered provides it" would mislead - so the failure path looks
            them up itself (patch hidden_provider_2026_11_07).

        Contract:
            - Empty for an unreadable annotation and for a Protocol annotation
              (a contract lookup, not a class lookup).
            - Otherwise the spells of the consumer's Spellbook pool whose
              `CompilerPhase3._hidden_type_key` equals the annotation's key (the
              single-socket rule: method and lambda spells excluded), one per
              SpellIndex under its selected id, described by
              `HiddenProviderReport.describe` in id order.
            - Iterates a copy of the pool: a concurrent bind may change the live
              dict, which this failure path does not lock.
            - Failure path only; raises nothing of its own.

        Args:
            spell: The consumer whose construction failed.
            annotation: The first missing parameter's annotation (`_constructor_annotation`).

        Returns:
            List[Dict[str, Optional[str]]]: The described candidates, possibly empty.
        """
        if annotation is inspect.Parameter.empty:
            return []
        normalized = CompilerPhase3()._normalize_annotation_for_matching(annotation)
        if CompilerPhase3._annotation_kind(normalized) == CompilerPhase3._KIND_CONTRACT:
            return []
        key = CompilerPhase3._annotation_key(normalized)
        found: Dict[str, Spell] = {}
        for pooled in spell._spellbook._spell_id_pool.copy().values():
            if pooled.spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                continue
            if CompilerPhase3._hidden_type_key(pooled) == key:
                found[pooled.spell_index.selected_spell_id] = pooled
        return [HiddenProviderReport.describe(spell_id, found[spell_id]) for spell_id in sorted(found)]

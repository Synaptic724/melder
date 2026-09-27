import annotationlib
import inspect
import types
import typing
from typing import TYPE_CHECKING, Any, Collection, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
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
        on its next meld.

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

    Owned State:
        - Inherited `spell_id`, `spell_name`, `node_id`, `param_name`, `inner`.
        - `expected_type`: display name of the first missing parameter's type.
        - `unresolved_params`: names of all missing unresolved parameters.

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
        )

    @staticmethod
    def _constructor_expected_type(spell: Spell, socket: SpellSocketDescriptor) -> str:
        """
        Name one unresolved parameter's expected type at meld time.

        Contract:
            - Phase-1 requirements are released after resolution, so this re-reads
              the constructor signature with FORWARDREF annotations (a name that
              only exists under TYPE_CHECKING stays its written name) and applies
              `expected_type_name`.
            - When the signature cannot be read or does not annotate the
              parameter, the socket's watched frame key names the type instead.
            - Failure path only.

        Args:
            spell: The consumer whose construction failed.
            socket: Its first missing UNRESOLVED_INPUT socket.

        Returns:
            str: Display name of the expected type.
        """
        try:
            signature = inspect.signature(
                spell.spell,
                annotation_format=annotationlib.Format.FORWARDREF,
            )
        except (TypeError, ValueError):
            signature = None
        if signature is not None:
            parameter = signature.parameters.get(socket.param_name)
            if parameter is not None and parameter.annotation is not inspect.Parameter.empty:
                return UnresolvedInputError.expected_type_name(parameter.annotation)
        if socket.dependency_key is not None:
            return socket.dependency_key[0]
        return "an unregistered type"

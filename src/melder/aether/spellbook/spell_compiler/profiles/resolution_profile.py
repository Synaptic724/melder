from typing import TYPE_CHECKING, Any, Optional, List, ClassVar

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import SpellRequirements
@mypyc_attr(native_class=True)
class SpellSymbolicNode(Cleanable):
    """
    Placeholder representation of a symbolic node in a spell's dependency graph.

    This will eventually carry enough information for:
        * per-parameter symbolic requirements,
        * relationship to frames / binding names,
        * future AI rewrites.

    For now, it is just a tagged node with an identifier and metadata bag.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["node_id", "kind", "metadata"]

    def __init__(self, node_id: str, kind: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize one symbolic dependency node.

        Args:
            node_id:
                Stable node identifier inside the symbolic graph.
            kind:
                Node kind label.
            metadata:
                Optional detached metadata payload.

        Returns:
            None.
        """
        super().__init__()
        self.node_id = node_id
        self.kind = kind
        self.metadata = dict(metadata) if metadata is not None else {}

    def cleanup(self) -> None:
        """
        Idempotently clear the symbolic node metadata payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self.metadata is not None:
            self.metadata.clear()
        del self.node_id
        del self.kind
        del self.metadata
@mypyc_attr(native_class=True)

class SpellSymbolicEdge(Cleanable):
    """
    Placeholder representation of a symbolic edge in a spell's dependency graph.

    Semantically this is:
        "node_from depends on node_to (optionally via parameter X)".
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["from_node", "to_node", "via_parameter"]

    def __init__(self, from_node: str, to_node: str, via_parameter: Optional[str] = None) -> None:
        """
        Initialize one symbolic dependency edge.

        Args:
            from_node:
                Source node identifier.
            to_node:
                Target node identifier.
            via_parameter:
                Optional parameter name describing the dependency path.

        Returns:
            None.
        """
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self.via_parameter = via_parameter

    def cleanup(self) -> None:
        """
        Idempotently clear the symbolic edge payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.from_node
        del self.to_node
        del self.via_parameter

@mypyc_attr(native_class=True)
class SpellSymbolicGraph(Cleanable):
    """
    Phase 2 artifact: local, symbolic dependency graph for a single spell.

    No global DAG semantics. No resolution against the Spellbook. This is
    purely a structural description derived from SpellRequirements.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["spell_id", "nodes", "edges"]

    def __init__(
            self,
            spell_id: str,
            nodes: Optional[List[SpellSymbolicNode]] = None,
            edges: Optional[List[SpellSymbolicEdge]] = None,
    ) -> None:
        """
        Initialize one symbolic dependency graph for a spell.

        Args:
            spell_id:
                Owning spell identifier.
            nodes:
                Optional initial symbolic nodes.
            edges:
                Optional initial symbolic edges.

        Returns:
            None.
        """
        super().__init__()
        self.spell_id = spell_id
        self.nodes: List[SpellSymbolicNode] = list(nodes) if nodes is not None else []
        self.edges: List[SpellSymbolicEdge] = list(edges) if edges is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear the symbolic graph and owned node/edge state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        for node in self.nodes:
            if isinstance(node, Cleanable):
                try:
                    node.cleanup()
                except Exception:
                    pass
        for edge in self.edges:
            if isinstance(edge, Cleanable):
                try:
                    edge.cleanup()
                except Exception:
                    pass
        self.nodes.clear()
        self.edges.clear()
        del self.nodes
        del self.edges
        del self.spell_id

@mypyc_attr(native_class=True)
class SpellResolutionFrame(Cleanable):
    """
    Phase 3 artifact: concrete, executable resolution DAG for a spell.

    This is the structure that `Meld` / the resolver will eventually walk in
    topological order to construct instances.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["spell_id", "ordered_node_ids"]

    def __init__(self, spell_id: str, ordered_node_ids: Optional[List[str]] = None) -> None:
        """
        Initialize one concrete spell resolution frame.

        Args:
            spell_id:
                Owning spell identifier.
            ordered_node_ids:
                Optional topologically ordered node ids.

        Returns:
            None.
        """
        super().__init__()
        self.spell_id = spell_id
        self.ordered_node_ids: List[str] = list(ordered_node_ids) if ordered_node_ids is not None else []
        # Implementation-specific payload goes here in a later ticket.

    def cleanup(self) -> None:
        """
        Idempotently clear the resolution frame payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if isinstance(self.ordered_node_ids, list):
            self.ordered_node_ids.clear()
        del self.ordered_node_ids
        del self.spell_id

@mypyc_attr(native_class=True)
class SpellValidationIssue(Cleanable):
    """
    One validation warning or error associated with a spell's resolution state.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["code", "message", "details"]

    def __init__(self, code: str, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize one validation issue payload.

        Args:
            code:
                Stable issue code.
            message:
                Human-readable validation message.
            details:
                Optional detached issue details payload.

        Returns:
            None.
        """
        super().__init__()
        self.code: str = code
        self.message: str = message
        self.details: Optional[dict[str, Any]] = dict(details) if details is not None else {}

    def cleanup(self) -> None:
        """
        Idempotently clear the validation issue payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self.details is not None:
            self.details.clear()
        del self.details
        del self.code
        del self.message

@mypyc_attr(native_class=True)
class SpellValidationResult(Cleanable):
    """
    Phase 4 artifact: readiness / health summary for a spell's resolution
    artifacts (requirements + symbolic graph + local frame).
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["is_valid", "errors", "warnings"]

    def __init__(
            self,
            is_valid: bool,
            errors: Optional[List[SpellValidationIssue]] = None,
            warnings: Optional[List[SpellValidationIssue]] = None,
    ) -> None:
        """
        Initialize one validation-result payload.

        Args:
            is_valid:
                Whether the spell currently validates.
            errors:
                Optional validation-error list.
            warnings:
                Optional validation-warning list.

        Returns:
            None.
        """
        super().__init__()
        self.is_valid = is_valid
        self.errors: List[SpellValidationIssue] = list(errors) if errors is not None else []
        self.warnings: List[SpellValidationIssue] = list(warnings) if warnings is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear the validation result and owned issue payloads.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        for issue in self.errors:
            if isinstance(issue, Cleanable):
                try:
                    issue.cleanup()
                except Exception:
                    pass
        for issue in self.warnings:
            if isinstance(issue, Cleanable):
                try:
                    issue.cleanup()
                except Exception:
                    pass
        self.errors.clear()
        self.warnings.clear()
        del self.is_valid
        del self.errors
        del self.warnings

@mypyc_attr(native_class=True)
class SpellResolutionProfile(Cleanable):
    """
    Canonical, in-memory representation of **how to resolve** a single Spell.

    This is the semantic payload for DI + DAG resolution, independent of any
    particular execution model (single-threaded, PhaseScheduler, agentic, etc.).

    Composition
    -----------

    * `requirements`     - Phase 1 artifact (SpellRequirements).
    * `symbolic_graph`   - Phase 2 artifact (SpellSymbolicGraph).
    * `resolution_frame` - Phase 3 artifact (SpellResolutionFrame).
    * `validation`       - Phase 4 artifact (SpellValidationResult).

    In the initial integration, you will likely populate only `requirements`,
    and leave the others as None until their phases are implemented.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell_id",
        "existence",
        "spellframe",
        "binding_name",
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "validation",
    ]


    def __init__(
            self,
            spell_id: str,
            existence: Existence,
            spellframe: Any,
            binding_name: Optional[str],
            requirements: SpellRequirements,
            symbolic_graph: Optional[SpellSymbolicGraph] = None,
            resolution_frame: Optional[SpellResolutionFrame] = None,
            validation: Optional[SpellValidationResult] = None,
    ) -> None:
        """
        Initialize one canonical spell resolution profile.

        Args:
            spell_id:
                Owning spell identifier.
            existence:
                Spell existence policy.
            spellframe:
                Spellframe associated with the spell.
            binding_name:
                Optional binding name.
            requirements:
                Phase 1 requirements artifact.
            symbolic_graph:
                Optional phase 2 symbolic graph artifact.
            resolution_frame:
                Optional phase 3 concrete resolution frame artifact.
            validation:
                Optional phase 4 validation artifact.

        Returns:
            None.
        """
        super().__init__()
        self.spell_id = spell_id
        self.existence = existence
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.requirements = requirements
        self.symbolic_graph = symbolic_graph
        self.resolution_frame = resolution_frame
        self.validation = validation

    def cleanup(self) -> None:
        """
        Idempotently clear the resolution profile and owned phase artifacts.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        for part in (self.requirements, self.symbolic_graph, self.resolution_frame, self.validation):
            if isinstance(part, Cleanable):
                try:
                    part.cleanup()
                except Exception:
                    pass
        del self.requirements
        del self.symbolic_graph
        del self.resolution_frame
        del self.validation
        del self.spell_id
        del self.existence
        del self.spellframe
        del self.binding_name

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
# Melder imports
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import SpellRequirements



@dataclass
class SpellSymbolicNode:
    """
    Placeholder representation of a symbolic node in a spell's dependency graph.

    This will eventually carry enough information for:
        * per-parameter symbolic requirements,
        * relationship to frames / binding names,
        * future AI rewrites.

    For now, it is just a tagged node with an identifier and metadata bag.
    """

    node_id: str
    kind: str
    metadata: dict[str, Any] = None


@dataclass
class SpellSymbolicEdge:
    """
    Placeholder representation of a symbolic edge in a spell's dependency graph.

    Semantically this is:
        "node_from depends on node_to (optionally via parameter X)".
    """

    from_node: str
    to_node: str
    via_parameter: Optional[str] = None


@dataclass
class SpellSymbolicGraph:
    """
    Phase 2 artifact: local, symbolic dependency graph for a single spell.

    No global DAG semantics. No resolution against the Spellbook. This is
    purely a structural description derived from SpellRequirements.
    """

    spell_id: str
    nodes: list[SpellSymbolicNode] = field(default_factory=list)
    edges: list[SpellSymbolicEdge] = field(default_factory=list)


@dataclass
class SpellResolutionFrame:
    """
    Phase 3 artifact: concrete, executable resolution DAG for a spell.

    This is the structure that `Meld` / the resolver will eventually walk in
    topological order to construct instances.
    """

    spell_id: str
    ordered_node_ids: list[str] = field(default_factory=list)
    # Implementation-specific payload goes here in a later ticket.


@dataclass
class SpellValidationIssue:
    """
    One validation warning or error associated with a spell's resolution state.
    """

    code: str
    message: str
    details: Optional[dict[str, Any]] = None


@dataclass
class SpellValidationResult:
    """
    Phase 4 artifact: readiness / health summary for a spell's resolution
    artifacts (requirements + symbolic graph + local frame).
    """

    is_valid: bool
    errors: list[SpellValidationIssue] = field(default_factory=list)
    warnings: list[SpellValidationIssue] = field(default_factory=list)


@dataclass
class SpellResolutionProfile:
    """
    Canonical, in-memory representation of **how to resolve** a single Spell.

    This is the semantic payload for DI + DAG resolution, independent of any
    particular execution model (single-threaded, PhaseScheduler, agentic, etc.).

    Composition
    -----------

    * `requirements`     – Phase 1 artifact (SpellRequirements).
    * `symbolic_graph`   – Phase 2 artifact (SpellSymbolicGraph).
    * `resolution_frame` – Phase 3 artifact (SpellResolutionFrame).
    * `validation`       – Phase 4 artifact (SpellValidationResult).

    In the initial integration, you will likely populate only `requirements`,
    and leave the others as None until their phases are implemented.
    """

    spell_id: str
    existence: Existence
    spellframe: Any
    binding_name: Optional[str]

    requirements: SpellRequirements

    symbolic_graph: Optional[SpellSymbolicGraph] = None
    resolution_frame: Optional[SpellResolutionFrame] = None
    validation: Optional[SpellValidationResult] = None

"""
Fact-strategy contract and per-module context for crystal analysis.

Fact strategies extract per-module truths (imports, from-imports, export
surfaces) and post-walk truths (topological load order). The analyzer walks
each module's AST exactly ONCE and dispatches nodes to every strategy in
registration order, so extraction order - and therefore manifest ordering -
stays byte-compatible with the pre-decomposition single-pass extractor.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import ast
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable

# TYPE_CHECKING is not needed here: ast and the result type are runtime
# collaborators for the hooks below.
from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


ImportEvent = Tuple[str, int, Optional[str], Tuple[str, ...]]


class FactContext(Cleanable):
    """
    Mutable per-module accumulator shared by one AST dispatch pass.

    Purpose:
        Carry one module's parse inputs to the fact strategies and collect
        their dependency contributions so the analyzer (the single result
        writer for manifest records) can merge them in visit order.

    Contract:
        - One context per (module, analysis pass); never reused.
        - `flat_import_targets` preserves visit order and may contain
          duplicates; the analyzer deduplicates on merge (first-seen wins),
          matching the historical extractor.
        - Value-only besides the parsed `syntax_tree` reference.
        - `import_events` preserves the mixed `Import` / `ImportFrom`
          sequence produced by `ast.walk`; each event contains only strings,
          integers, and tuples so the analyzer may memoize it without
          retaining AST nodes or live module objects.
        - Each import event has the shape (kind, relative level, raw module
          name, imported-name tuple). Strategies append events in the same
          mixed order used for immediate dependency extraction.
        - `export_all_declared` and `export_public_names` carry the
          export strategy's value output to the analyzer for freezing.
        - Source text and the AST are transient cold-path inputs; neither is
          copied into the shared memo.

    Threading:
        Thread-confined to one analyzer pass; no locks.

    Lifecycle / Cleanup:
        Cleaned by the analyzer in a finally block after the module is
        recorded. On a memo-eligible cold path, the analyzer first freezes
        event/export values into tuples, then cleanup deletes every transient
        source, AST, and accumulator reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_module_name",
        "_current_package",
        "_source_text",
        "_syntax_tree",
        "flat_import_targets",
        "from_import_targets",
        "import_events",
        "export_all_declared",
        "export_public_names",
    )

    def __init__(
            self,
            *,
            module_name: str,
            current_package: str,
            source_text: str,
            syntax_tree: ast.AST,
    ) -> None:
        """
        Initialize one per-module fact context.

        Purpose:
            Provide the default strategies one ordered, thread-confined
            workspace for cold-path extraction.

        Contract:
            - Stores source text and the parsed AST only for this module pass.
            - Allocates fresh dependency, import-event, and export-name
              accumulators; no collection is shared across modules.
            - Import/export accumulators are mutable only while strategies run.
            - Construction does not access or publish to the analyzer memo.

        Args:
            module_name:
                Canonical module name being analyzed.
            current_package:
                Package context used to resolve relative imports (derived
                by the analyzer from the live module object, mirroring the
                historical `__package__`/`__path__` fallback chain).
            source_text:
                The module source that produced `syntax_tree`.
            syntax_tree:
                Parsed AST for the module source.

        Returns:
            None.

        Threading:
            No lock is allocated; the constructing analyzer thread becomes the
            sole owner.

        Lifecycle / Cleanup:
            The analyzer retains this context only for one cold module pass
            and releases it from the enclosing finally block.
        """
        super().__init__()
        self._module_name: str = module_name
        self._current_package: str = current_package
        self._source_text: str = source_text
        self._syntax_tree: ast.AST = syntax_tree
        self.flat_import_targets: List[str] = []
        self.from_import_targets: Dict[str, List[str]] = {}
        self.import_events: List[ImportEvent] = []
        self.export_all_declared: List[str] = []
        self.export_public_names: List[str] = []

    def cleanup(self) -> None:
        """
        Idempotently release the context's retained references.

        Contract:
            - Repeated calls return immediately.
            - Deletes source text, the AST, identity/package fields, and every
              mutable accumulator.
            - Any memoized facts have already been detached as immutable
              tuples by the analyzer; cleanup cannot invalidate them.
            - The context is unusable after cleanup.

        Returns:
            None.

        Threading:
            Must run on the owning analyzer thread with no concurrent strategy
            access.

        Lifecycle / Cleanup:
            The analyzer owns this context from construction through the
            enclosing finally block and must call cleanup exactly as the
            cold-path contract requires.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._module_name
        del self._current_package
        del self._source_text
        del self._syntax_tree
        del self.flat_import_targets
        del self.from_import_targets
        del self.import_events
        del self.export_all_declared
        del self.export_public_names

    @property
    def module_name(self) -> str:
        """
        Return the canonical module name under analysis.

        Returns:
            str: Module name.
        """
        return self._module_name

    @property
    def current_package(self) -> str:
        """
        Return the package context for relative import resolution.

        Returns:
            str: Package name (possibly empty for top-level modules).
        """
        return self._current_package

    @property
    def source_text(self) -> str:
        """
        Return the module source text under analysis.

        Returns:
            str: Source text.
        """
        return self._source_text

    @property
    def syntax_tree(self) -> ast.AST:
        """
        Return the parsed module AST.

        Returns:
            ast.AST: Parsed tree for the module source.
        """
        return self._syntax_tree


class CrystalFactStrategy(Cleanable, ABC):
    """
    Contract for one fact-extraction pass over analyzed modules.

    Purpose:
        Let independent fact passes (imports, from-imports, export surface,
        dependency view) share the analyzer's single AST walk and post-walk
        finalization without owning traversal or result-recording order.

    Contract:
        - `visit_node` is called for EVERY node of the analyzer's single
          `ast.walk` over each module, in walk order; strategies act only
          on the node types they own (visit-order preservation is what
          keeps manifest ordering byte-compatible with the historical
          extractor).
        - `analyze_module` is called once per module after node dispatch,
          with the shared context and the result (strategies that record
          module-scoped facts directly, like export surfaces, do so here).
        - `finalize` is called once per analysis after the walk completes
          (post-walk facts like topological load order land here).
        - Strategies are per-analysis instances; stateless between modules
          unless their contract documents otherwise.

    Threading:
        Thread-confined to one analyzer pass; no locks.

    Lifecycle / Cleanup:
        Default cleanup is a flag flip; stateful subclasses override with
        del posture for owned fields.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the stable strategy name used in diagnostics.

        Returns:
            str: Strategy name.
        """

    def visit_node(self, node: ast.AST, context: FactContext) -> None:
        """
        Handle one AST node from the analyzer's shared walk.

        Args:
            node:
                Current node from `ast.walk` over the module tree.
            context:
                Shared per-module accumulator.

        Returns:
            None.
        """

    def analyze_module(
            self,
            context: FactContext,
            result: CrystalAnalysisResult,
    ) -> None:
        """
        Record module-scoped facts after node dispatch completes.

        Args:
            context:
                Shared per-module accumulator (fully populated).
            result:
                Analysis result available for direct fact recording.

        Returns:
            None.
        """

    def finalize(self, result: CrystalAnalysisResult) -> None:
        """
        Record post-walk facts once the whole module graph is analyzed.

        Args:
            result:
                Analysis result carrying the completed walk state.

        Returns:
            None.
        """

    def cleanup(self) -> None:
        """
        Idempotently mark the strategy cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True

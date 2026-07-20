"""
Fact strategy for module export surfaces (S1 NEW capability).

Records what one module EXPOSES: names statically declared in a top-level
`__all__` assignment plus public top-level definition/assignment names.
This is the fact MutationResearch's impact engine needs to compute the
blast radius of a removed or renamed symbol - a gap the pre-decomposition
analyzer never covered (gap map 1.1).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import ast
from typing import List, Set

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    CrystalFactStrategy,
    FactContext,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ExportSurfaceStrategy(CrystalFactStrategy):
    """
    Derive one module's static export surface.

    Purpose:
        Record `__all__`-declared names (when statically resolvable) and
        public top-level names so retained versions answer "what does this
        module expose" without a live import.

    Contract:
        - Top-level (module body) statements only; nested definitions are
          not exports.
        - `__all__` extraction is STATIC: only list/tuple literals of
          string constants resolve; dynamic `__all__` forms yield an empty
          `all_declared` (honest under-claim, never a guess).
        - Public names: top-level function/async-function/class names and
          simple assignment targets not starting with underscore, first
          seen order, deduplicated. `__all__` itself is excluded (dunder).
        - Records via `result.record_export_surface` in `analyze_module`
          (module-scoped fact; the analyzer remains the recorder for
          manifest-structural facts only).
        - Publishes the same ordered value lists through FactContext so the
          analyzer can freeze them into a memo entry after all strategies
          complete.
        - Memo replay records fresh lists into a fresh result; neither the AST
          nor the cold-path result is retained by the memo.

    Threading:
        Thread-confined to one analyzer pass; no locks and no instance
        state (`__slots__` is empty). Output lands on the caller's
        `FactContext` and `CrystalAnalysisResult`, both confined to that
        pass.

    Registration:
        MELDER KERNEL - guarded. Fact strategies are constructed by
        `CrystalAnalyzer` for one analysis, never bound as spells.
        Note the classification split: this concrete leaf IS guarded,
        while its base `CrystalFactStrategy` is deliberately NOT - see
        that class's Registration section for the MRO reasoning.

    Subsystem Context:
        One of the four fact strategies sharing the analyzer's SINGLE
        `ast.walk` per module, and NEW at the S1 decomposition rather
        than inherited from the historical extractor. It is also the one
        that records in `analyze_module` (the post-dispatch, module-scoped
        hook) instead of `visit_node`, because an export surface is a
        fact about the whole module body rather than any single node.
        Its siblings cover imports (`ImportStatementStrategy`,
        `FromImportStatementStrategy`) and post-walk load order
        (`DependencyViewStrategy`).

    System Context:
        This pass answers "what does this module expose?" for a RETAINED
        version - one that may have no importable form in the current
        environment at all. That constraint is the whole design: the
        answer must come from syntax, because importing to ask is exactly
        what the caller cannot do.
        Hence the static-only `__all__` rule. A dynamic `__all__` (built
        by comprehension, concatenation, or conditional) yields an EMPTY
        `all_declared` rather than a partial or inferred list. That is an
        honest under-claim by design: a reader who sees nothing knows to
        look, whereas a reader handed a guessed surface has no signal
        that it might be wrong. The same principle governs the public-name
        fallback, which reports only what is plainly visible at the
        module's top level.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Derive one module's static export surface. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = ()

    @property
    def name(self) -> str:
        """
        Return the stable strategy name.

        Returns:
            str: `export_surface`.
        """
        return "export_surface"

    def analyze_module(
            self,
            context: FactContext,
            result: CrystalAnalysisResult,
    ) -> None:
        """
        Record the module's static export surface into the result.

        Purpose:
            Produce one export truth that serves the current result and the
            source-stable memo value without analyzing the module twice.

        Contract:
            - Reads only top-level statements from the context's parsed tree.
            - Records newly built ordered lists in the current result.
            - Assigns those same lists to the thread-confined context for
              analyzer-side tuple freezing after strategy completion.
            - Does not access or publish the shared memo directly.

        Args:
            context:
                Shared per-module accumulator carrying the parsed tree.
            result:
                Analysis result receiving the export-surface fact.

        Returns:
            None.

        Threading:
            Mutates one thread-confined FactContext and result; no shared lock
            is required.

        Lifecycle / Cleanup:
            The result detaches the recorded values. Context lists are deleted
            when the analyzer cleans the module context.
        """
        module_body = getattr(context.syntax_tree, "body", [])
        all_declared: List[str] = []
        public_names: List[str] = []
        seen_public: Set[str] = set()

        for statement in module_body:
            if isinstance(
                    statement,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
            ):
                self._append_public(statement.name, public_names, seen_public)
                continue
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if target.id == "__all__":
                        all_declared = self._extract_static_all(statement.value)
                        continue
                    self._append_public(target.id, public_names, seen_public)
                continue
            if isinstance(statement, ast.AnnAssign):
                target = statement.target
                if isinstance(target, ast.Name):
                    if target.id == "__all__":
                        if statement.value is not None:
                            all_declared = self._extract_static_all(
                                statement.value
                            )
                        continue
                    self._append_public(target.id, public_names, seen_public)

        result.record_export_surface(
            context.module_name,
            all_declared,
            public_names,
        )
        context.export_all_declared = all_declared
        context.export_public_names = public_names

    @staticmethod
    def _append_public(
            candidate_name: str,
            public_names: List[str],
            seen_public: Set[str],
    ) -> None:
        """
        Append one public (non-underscore) name preserving first-seen order.

        Args:
            candidate_name:
                Top-level name being considered.
            public_names:
                Ordered public-name accumulator.
            seen_public:
                Dedup set matching `public_names`.

        Returns:
            None.
        """
        if candidate_name.startswith("_"):
            return
        if candidate_name in seen_public:
            return
        seen_public.add(candidate_name)
        public_names.append(candidate_name)

    @staticmethod
    def _extract_static_all(value_node: ast.AST) -> List[str]:
        """
        Extract string constants from a static `__all__` literal.

        Args:
            value_node:
                The assigned value expression for `__all__`.

        Returns:
            List[str]:
                Declared names when the literal is a list/tuple of string
                constants; empty for any dynamic form.
        """
        if not isinstance(value_node, (ast.List, ast.Tuple)):
            return []
        declared_names: List[str] = []
        for element in value_node.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                declared_names.append(element.value)
        return declared_names

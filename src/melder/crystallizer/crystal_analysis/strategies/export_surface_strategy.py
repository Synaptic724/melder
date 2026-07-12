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
    """

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

        Args:
            context:
                Shared per-module accumulator carrying the parsed tree.
            result:
                Analysis result receiving the export-surface fact.

        Returns:
            None.
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

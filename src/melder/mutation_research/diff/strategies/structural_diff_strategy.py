import ast
import hashlib
from typing import Dict, List, Optional, Tuple

from melder.mutation_research.diff.diff_strategy import DiffStrategy


class StructuralDiffStrategy(DiffStrategy):
    """
    AST-level structural comparison between two version materials.

    Purpose:
        The reasoning layer of the derived-diff family: agents thinking about
        candidate futures care about STRUCTURE - which classes, methods, and
        functions appeared, disappeared, or changed, and in what aspect
        (signature vs docstring vs body) - not about text lines. String
        diffs are transport; this strategy answers the May-model question
        "what structural parts moved between these futures".

    Contract:
        - Operates only on modules with source TEXT on both sides (synthetic
          modules always carry it); text-less modules report under
          `text_unavailable_modules`, never as fabricated verdicts.
        - Per module: module docstring change, added/removed/changed
          top-level functions and classes; per changed function or method:
          `signature_changed` (args, decorators, returns), `docstring_changed`,
          `body_changed` (docstring-stripped AST fingerprint).
        - Unparseable source reports as a per-module `parse_error` verdict
          (loud, one side named), never a crash.
        - Result is detached and value-typed; `identical` rolls up the
          structural verdict only (use the `source` strategy for byte truth).

    Threading:
        Stateless beyond the base lifecycle flag; safe to share.

    Lifecycle:
        Owned by exactly one `DiffEngine`.
    """

    __slots__ = DiffStrategy.__slots__

    @property
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Returns:
            str:
                "structural".
        """
        self.check_cleaned()
        return "structural"

    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compare two version materials structurally, module by module.

        Args:
            left_material:
                Resolver material for the left version.
            right_material:
                Resolver material for the right version.

        Returns:
            Dict[str, object]:
                Verdict payload with `identical`, `added_modules`,
                `removed_modules`, `changed_modules`, `identical_modules`,
                `text_unavailable_modules`, and per-module structural detail
                under `module_reports`.
        """
        self.check_cleaned()
        left_sources = self._string_sources(left_material)
        right_sources = self._string_sources(right_material)
        left_names = set(left_sources)
        right_names = set(right_sources)
        both_prints = self._fingerprint_union(left_material, right_material)

        added = sorted(right_names - left_names)
        removed = sorted(left_names - right_names)
        text_unavailable = sorted(
            both_prints - left_names - right_names
        )
        changed: List[str] = []
        identical: List[str] = []
        module_reports: Dict[str, object] = {}
        for module_name in sorted(left_names & right_names):
            report = self._diff_module(
                left_sources[module_name],
                right_sources[module_name],
            )
            if report is None:
                identical.append(module_name)
            else:
                changed.append(module_name)
                module_reports[module_name] = report

        return {
            "identical": not added and not removed and not changed,
            "added_modules": added,
            "removed_modules": removed,
            "changed_modules": changed,
            "identical_modules": identical,
            "text_unavailable_modules": text_unavailable,
            "module_reports": module_reports,
        }

    # ------------------------------------------------------------------
    # Module comparison
    # ------------------------------------------------------------------

    def _diff_module(
            self,
            left_text: str,
            right_text: str,
    ) -> Optional[Dict[str, object]]:
        """
        Structurally compare one module's two source texts.

        Args:
            left_text:
                Left-side module source.
            right_text:
                Right-side module source.

        Returns:
            Optional[Dict[str, object]]:
                None when structurally identical; otherwise the detail
                report (or a `parse_error` report naming the failing side).
        """
        try:
            left_tree = ast.parse(left_text)
        except SyntaxError as error:
            return {"parse_error": f"left: {error}"}
        try:
            right_tree = ast.parse(right_text)
        except SyntaxError as error:
            return {"parse_error": f"right: {error}"}

        left_shape = self._module_shape(left_tree)
        right_shape = self._module_shape(right_tree)
        report: Dict[str, object] = {}

        if left_shape["docstring"] != right_shape["docstring"]:
            report["module_docstring_changed"] = True

        function_report = self._diff_callable_maps(
            left_shape["functions"], right_shape["functions"],
        )
        if function_report:
            report.update(
                {
                    f"{key}_functions": value
                    for key, value in function_report.items()
                }
            )

        left_classes = left_shape["classes"]
        right_classes = right_shape["classes"]
        added_classes = sorted(set(right_classes) - set(left_classes))
        removed_classes = sorted(set(left_classes) - set(right_classes))
        changed_classes: Dict[str, object] = {}
        for class_name in sorted(set(left_classes) & set(right_classes)):
            class_report = self._diff_class(
                left_classes[class_name], right_classes[class_name],
            )
            if class_report:
                changed_classes[class_name] = class_report
        if added_classes:
            report["added_classes"] = added_classes
        if removed_classes:
            report["removed_classes"] = removed_classes
        if changed_classes:
            report["changed_classes"] = changed_classes

        return report if report else None

    def _diff_class(
            self,
            left_class: Dict[str, object],
            right_class: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compare one class's two structural shapes.

        Args:
            left_class:
                Left-side class shape.
            right_class:
                Right-side class shape.

        Returns:
            Dict[str, object]:
                Detail report; empty when structurally identical.
        """
        report: Dict[str, object] = {}
        if left_class["docstring"] != right_class["docstring"]:
            report["class_docstring_changed"] = True
        if left_class["bases"] != right_class["bases"]:
            report["bases_changed"] = {
                "left": left_class["bases"],
                "right": right_class["bases"],
            }
        method_report = self._diff_callable_maps(
            left_class["methods"], right_class["methods"],
        )
        if method_report:
            report.update(
                {
                    f"{key}_methods": value
                    for key, value in method_report.items()
                }
            )
        return report

    def _diff_callable_maps(
            self,
            left_map: Dict[str, Dict[str, object]],
            right_map: Dict[str, Dict[str, object]],
    ) -> Dict[str, object]:
        """
        Compare two name->shape callable maps.

        Args:
            left_map:
                Left-side callable shapes.
            right_map:
                Right-side callable shapes.

        Returns:
            Dict[str, object]:
                `added`/`removed`/`changed` keys, present only when
                non-empty; `changed` carries per-name aspect flags.
        """
        report: Dict[str, object] = {}
        added = sorted(set(right_map) - set(left_map))
        removed = sorted(set(left_map) - set(right_map))
        changed: Dict[str, object] = {}
        for name in sorted(set(left_map) & set(right_map)):
            left_shape = left_map[name]
            right_shape = right_map[name]
            aspects: Dict[str, bool] = {}
            if left_shape["signature"] != right_shape["signature"]:
                aspects["signature_changed"] = True
            if left_shape["docstring"] != right_shape["docstring"]:
                aspects["docstring_changed"] = True
            if left_shape["body_fingerprint"] != right_shape["body_fingerprint"]:
                aspects["body_changed"] = True
            if aspects:
                changed[name] = aspects
        if added:
            report["added"] = added
        if removed:
            report["removed"] = removed
        if changed:
            report["changed"] = changed
        return report

    # ------------------------------------------------------------------
    # Shape extraction
    # ------------------------------------------------------------------

    def _module_shape(self, tree: ast.Module) -> Dict[str, object]:
        """
        Extract one module's structural shape.

        Args:
            tree:
                Parsed module AST.

        Returns:
            Dict[str, object]:
                `docstring`, top-level `functions`, and `classes` shapes.
        """
        functions: Dict[str, Dict[str, object]] = {}
        classes: Dict[str, Dict[str, object]] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions[node.name] = self._callable_shape(node)
            elif isinstance(node, ast.ClassDef):
                classes[node.name] = self._class_shape(node)
        return {
            "docstring": ast.get_docstring(tree),
            "functions": functions,
            "classes": classes,
        }

    def _class_shape(self, node: ast.ClassDef) -> Dict[str, object]:
        """
        Extract one class's structural shape.

        Args:
            node:
                Class definition node.

        Returns:
            Dict[str, object]:
                `docstring`, `bases` (unparsed), and `methods` shapes.
        """
        methods: Dict[str, Dict[str, object]] = {}
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods[child.name] = self._callable_shape(child)
        return {
            "docstring": ast.get_docstring(node),
            "bases": [ast.unparse(base) for base in node.bases],
            "methods": methods,
        }

    def _callable_shape(self, node: object) -> Dict[str, object]:
        """
        Extract one function/method's comparable shape.

        Args:
            node:
                Function or async-function definition node.

        Returns:
            Dict[str, object]:
                `signature` (decorators + args + returns), `docstring`, and
                the docstring-stripped `body_fingerprint`.
        """
        decorators = [
            ast.unparse(decorator) for decorator in node.decorator_list
        ]
        returns = ast.unparse(node.returns) if node.returns else None
        signature = (
            f"decorators={decorators} args=({ast.unparse(node.args)}) "
            f"returns={returns} async={isinstance(node, ast.AsyncFunctionDef)}"
        )
        body, docstring = self._split_docstring(node)
        body_dump = "\n".join(
            ast.dump(statement, include_attributes=False)
            for statement in body
        )
        return {
            "signature": signature,
            "docstring": docstring,
            "body_fingerprint": hashlib.sha256(
                body_dump.encode("utf-8")
            ).hexdigest(),
        }

    @staticmethod
    def _split_docstring(node: object) -> Tuple[List[object], Optional[str]]:
        """
        Split one callable body into (docstring-stripped body, docstring).

        Args:
            node:
                Function or async-function definition node.

        Returns:
            Tuple[List[object], Optional[str]]:
                Body statements without the leading docstring, plus the
                docstring text when present.
        """
        docstring = ast.get_docstring(node)
        body = list(node.body)
        if (
                docstring is not None
                and body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
        ):
            body = body[1:]
        return body, docstring

    @staticmethod
    def _string_sources(material: Dict[str, object]) -> Dict[str, str]:
        """
        Extract the name->text sources mapping from a material payload.

        Args:
            material:
                Resolver material payload.

        Returns:
            Dict[str, str]:
                Detached mapping; non-string values drop out.
        """
        mapping = material.get("sources") if isinstance(material, dict) else None
        if not isinstance(mapping, dict):
            return {}
        return {
            str(name): value
            for name, value in mapping.items()
            if isinstance(value, str)
        }

    @staticmethod
    def _fingerprint_union(
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> set:
        """
        Return module names known only through fingerprints on either side.

        Args:
            left_material:
                Left resolver material.
            right_material:
                Right resolver material.

        Returns:
            set:
                Names present in either side's fingerprints mapping.
        """
        names = set()
        for material in (left_material, right_material):
            mapping = (
                material.get("fingerprints")
                if isinstance(material, dict)
                else None
            )
            if isinstance(mapping, dict):
                names.update(str(name) for name in mapping.keys())
        return names

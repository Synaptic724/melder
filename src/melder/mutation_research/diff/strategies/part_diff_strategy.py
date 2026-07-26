import ast
import difflib
from typing import Dict, List, Optional, Tuple, ClassVar

from melder.mutation_research.diff.diff_strategy import DiffStrategy


class PartDiffStrategy(DiffStrategy):
    """
    Part-grain text comparison between two version materials.

    Purpose:
        The class-code grain of the derived-diff family (owner ruling
        2026-07-11: the diff must OFFER the class code or the module, the
        agent chooses). Where the `source` strategy answers with whole
        module texts and `structural` answers with shape reports, this
        strategy breaks every common module into its top-level parts
        (functions and classes) and shows the agent EVERYTHING at that
        grain: added and removed parts WITH their full code, changed parts
        as unified text diffs, identical parts by name.

    Contract:
        - Operates only on modules with source TEXT on both sides;
          text-less modules report under `text_unavailable_modules`,
          never as fabricated verdicts (materials are recorded-only by
          the resolver's comparison law).
        - Part spans include decorators; parts are top-level only (methods
          ride their class's text - the class IS the part).
        - Module-level text outside any part (imports, constants) is
          compared as one synthetic `<module_body>` region so nothing
          escapes the verdict.
        - Unparseable source reports as a per-module `parse_error` verdict
          naming the failing side, never a crash.
        - Result is detached and value-typed; outer shape mirrors the
          sibling strategies (`identical`, module presence lists,
          per-module detail under `module_reports`).

    Threading:
        Stateless beyond the base lifecycle flag; safe to share.

    Lifecycle:
        Owned by exactly one `DiffEngine`.

    Registration:
        Your subclasses bind normally: manifest lookup is an EXACT
        `(module, qualname)` match and does not inherit.

    Subsystem Context:
        The class-code grain of the three shipped spell-diff strategies, between
        `source` (whole module text) and `structural` (shape reports). It is the
        grain a code-writing agent usually wants: enough context to read a part
        in full, without the surrounding module it did not ask about.

    System Context:
        Two details make it trustworthy rather than merely convenient. Part
        spans include DECORATORS, so a part's text is what would actually be
        executed rather than a stripped body. And module-level code outside any
        part - imports, constants - is compared as one synthetic
        `<module_body>` region, so nothing silently escapes the verdict just
        because it does not live inside a function or class.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Part-grain text comparison between two version materials. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = DiffStrategy.__slots__

    @property
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Contract:
            - Fixed key "parts" - the name `DiffEngine` registers this
              per-part code strategy under and resolves it by.

        Returns:
            str:
                "parts".

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
        """
        self.check_cleaned()
        return "parts"

    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compare two version materials part by part, module by module.

        Contract:
            - Structural presence rides EVERYTHING a side knows - text
              custody OR fingerprint - so custody absence is a
              text-availability fact, never a structural deletion (BUG-043):
              a module present by fingerprint on one side and by text on the
              other is `text_unavailable`, not removed.
            - Only modules carrying source TEXT on BOTH sides are compared
              part by part. Each shared module splits into top-level parts
              (functions and classes, decorators included) plus the residue
              outside every part as one synthetic `<module_body>` region, so
              imports and constants never escape the verdict.
            - Per module: `added_parts` / `removed_parts` carry FULL part
              text, `changed_parts` carry a unified text diff, and identical
              parts are listed by name. Methods are not separate parts - a
              class IS the part and its methods ride its text.
            - Unparseable source on either side becomes a per-module
              `parse_error` verdict naming the failing side, never a crash.
            - READ-ONLY: neither material is retained or mutated; `identical`
              is the whole-verdict rollup.

        Args:
            left_material:
                Resolver material for the left version.
            right_material:
                Resolver material for the right version.

        Returns:
            Dict[str, object]:
                Verdict payload with `identical`, `added_modules`,
                `removed_modules`, `changed_modules`, `identical_modules`,
                `text_unavailable_modules` (modules known on both sides where at
                least one side lacks text custody), and per-module part detail
                under `module_reports`.

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
        """
        self.check_cleaned()
        left_sources = self._string_sources(left_material)
        right_sources = self._string_sources(right_material)
        left_names = set(left_sources)
        right_names = set(right_sources)

        # Structural truth rides EVERYTHING a side knows (text custody OR
        # fingerprint); custody absence is a text-availability fact, never
        # a structural deletion (BUG-043).
        left_prints = self._fingerprints(left_material)
        right_prints = self._fingerprints(right_material)
        left_known = left_names | left_prints
        right_known = right_names | right_prints

        added = sorted(right_known - left_known)
        removed = sorted(left_known - right_known)
        text_unavailable = sorted(
            (left_known & right_known) - (left_names & right_names)
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
        Compare one module's two texts at part grain.

        Args:
            left_text:
                Left-side module source.
            right_text:
                Right-side module source.

        Returns:
            Optional[Dict[str, object]]:
                None when every part (and the module body) is identical;
                otherwise `{"added_parts", "removed_parts",
                "changed_parts", "identical_parts"}` (or a `parse_error`
                report naming the failing side).
        """
        try:
            left_parts = self._part_texts(left_text)
        except SyntaxError as error:
            return {"parse_error": f"left: {error}"}
        try:
            right_parts = self._part_texts(right_text)
        except SyntaxError as error:
            return {"parse_error": f"right: {error}"}

        added_parts: List[Dict[str, object]] = []
        removed_parts: List[Dict[str, object]] = []
        changed_parts: List[Dict[str, object]] = []
        identical_parts: List[str] = []

        for key in sorted(set(right_parts) - set(left_parts)):
            added_parts.append({
                "name": key[0],
                "kind": key[1],
                "text": right_parts[key],
            })
        for key in sorted(set(left_parts) - set(right_parts)):
            removed_parts.append({
                "name": key[0],
                "kind": key[1],
                "text": left_parts[key],
            })
        for key in sorted(set(left_parts) & set(right_parts)):
            left_part_text = left_parts[key]
            right_part_text = right_parts[key]
            if left_part_text == right_part_text:
                identical_parts.append(key[0])
                continue
            changed_parts.append({
                "name": key[0],
                "kind": key[1],
                "unified_diff": list(difflib.unified_diff(
                    left_part_text.splitlines(),
                    right_part_text.splitlines(),
                    fromfile=f"left/{key[0]}",
                    tofile=f"right/{key[0]}",
                    lineterm="",
                )),
            })

        if not added_parts and not removed_parts and not changed_parts:
            return None
        return {
            "added_parts": added_parts,
            "removed_parts": removed_parts,
            "changed_parts": changed_parts,
            "identical_parts": identical_parts,
        }

    def _part_texts(self, source: str) -> Dict[Tuple[str, str], str]:
        """
        Split one module text into its top-level part texts.

        Args:
            source:
                Parseable module source.

        Returns:
            Dict[Tuple[str, str], str]:
                (name, kind) -> part text (decorators included); the
                residue outside every part rides the synthetic
                `("<module_body>", "module")` key so imports/constants
                never escape comparison.

        Raises:
            SyntaxError:
                Propagated from parsing (the caller names the side).
        """
        tree = ast.parse(source)
        lines = source.splitlines()
        parts: Dict[Tuple[str, str], str] = {}
        covered: set = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "function"
            elif isinstance(node, ast.ClassDef):
                kind = "class"
            else:
                continue
            start = node.lineno
            for decorator in node.decorator_list:
                start = min(start, decorator.lineno)
            parts[(node.name, kind)] = "\n".join(
                lines[start - 1:node.end_lineno]
            )
            covered.update(range(start, node.end_lineno + 1))
        residue = "\n".join(
            line for number, line in enumerate(lines, start=1)
            if number not in covered and line.strip()
        )
        if residue:
            parts[("<module_body>", "module")] = residue
        return parts

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
    def _fingerprints(material: Dict[str, object]) -> set:
        """
        Return one side's fingerprint-known module names.

        Args:
            material:
                Resolver material payload.

        Returns:
            set:
                Names present in this side's fingerprints mapping.
        """
        mapping = (
            material.get("fingerprints")
            if isinstance(material, dict)
            else None
        )
        if not isinstance(mapping, dict):
            return set()
        return {str(name) for name in mapping}

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

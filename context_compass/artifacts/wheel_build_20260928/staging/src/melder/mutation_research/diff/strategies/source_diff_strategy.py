import difflib
from typing import Dict, List, ClassVar

from melder.mutation_research.diff.diff_strategy import DiffStrategy


class SourceDiffStrategy(DiffStrategy):
    """
    Per-module source comparison between two version materials.

    Purpose:
        The first derived-diff read: given two versions' custody material,
        report which modules were added, removed, changed, or identical,
        with unified diffs wherever source TEXT exists on both sides and
        honest fingerprint-only verdicts where it does not (physical-module
        text retention is a separate opt-in custody lane; synthetic modules
        always carry text).

    Contract:
        - Module universe = union of both sides' `sources` and
          `fingerprints` keys.
        - Text on both sides -> unified diff (identical when empty).
        - No text but fingerprints on both sides -> changed/identical by
          SHA256 with `text_unavailable: True` (never a fabricated diff).
        - One-sided presence -> added_modules / removed_modules
          (left -> right orientation).
        - Result is detached and value-typed; `identical` is the whole-verdict
          rollup.

    Threading:
        Stateless beyond the base lifecycle flag; safe to share.

    Lifecycle:
        Owned by exactly one `DiffEngine`.

    Registration:
        Your subclasses bind normally: manifest lookup is an EXACT
        `(module, qualname)` match and does not inherit.

    Subsystem Context:
        The byte-truth grain of the three shipped spell-diff strategies.
        `structural` answers in AST shapes, `parts` answers in per-class code,
        and this answers in module text. An agent picks the grain; the engine
        does not choose for it.

    System Context:
        The only strategy that can answer when text is missing, and it does so
        honestly rather than fabricating: fingerprint-only comparison marks
        `text_unavailable` instead of inventing a diff. That matters because
        physical-source retention is an opt-in custody lane - synthetic modules
        always carry text, user modules only when retention is on - so a
        recorded world can legitimately have fingerprints without source.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Per-module source comparison between two version materials. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = DiffStrategy.__slots__

    @property
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Contract:
            - Fixed key "source" - the name `DiffEngine` registers this
              whole-module-text strategy under and resolves it by. It is
              also the engine's default strategy, so an unqualified diff
              lands here.

        Returns:
            str:
                "source".

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
        """
        self.check_cleaned()
        return "source"

    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compare two version materials module by module.

        Contract:
            - The module universe is the UNION of both sides' `sources` and
              `fingerprints` keys, so an added or removed module is never
              missed by only iterating one side.
            - Text present on BOTH sides -> a `difflib` unified diff; an
              empty diff means identical. A terminal-newline-only delta that
              `splitlines()` would otherwise erase is surfaced explicitly
              (BUG-042), because the whole-module contract compares COMPLETE
              recorded text.
            - Text missing but fingerprints present on both sides -> changed
              or identical decided by SHA256, tagged `text_unavailable: True`;
              a diff is never fabricated where source was not retained.
            - One-sided presence -> `added_modules` / `removed_modules` in
              left -> right orientation.
            - READ-ONLY: neither material is retained or mutated; the verdict
              is a fresh value-typed payload and `identical` is the
              whole-verdict rollup (no adds, removes, or changes anywhere).

        Args:
            left_material:
                Resolver material for the left version.
            right_material:
                Resolver material for the right version.

        Returns:
            Dict[str, object]:
                Verdict payload with `identical`, `added_modules`,
                `removed_modules`, `changed_modules`, `identical_modules`,
                and per-module detail under `module_diffs`.

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
        """
        self.check_cleaned()
        left_sources = self._string_map(left_material, "sources")
        right_sources = self._string_map(right_material, "sources")
        left_prints = self._string_map(left_material, "fingerprints")
        right_prints = self._string_map(right_material, "fingerprints")
        left_names = set(left_sources) | set(left_prints)
        right_names = set(right_sources) | set(right_prints)

        added = sorted(right_names - left_names)
        removed = sorted(left_names - right_names)
        changed: List[str] = []
        identical: List[str] = []
        module_diffs: Dict[str, object] = {}
        for name in sorted(left_names & right_names):
            left_text = left_sources.get(name)
            right_text = right_sources.get(name)
            if left_text is not None and right_text is not None:
                diff_lines = list(
                    difflib.unified_diff(
                        left_text.splitlines(),
                        right_text.splitlines(),
                        fromfile=f"left/{name}",
                        tofile=f"right/{name}",
                        lineterm="",
                    )
                )
                if diff_lines:
                    changed.append(name)
                    module_diffs[name] = {
                        "text_unavailable": False,
                        "unified_diff": diff_lines,
                    }
                elif left_text != right_text:
                    # splitlines() erases a terminal-newline delta
                    # (BUG-042); the whole-module-text contract compares
                    # COMPLETE recorded text, so surface it explicitly.
                    changed.append(name)
                    module_diffs[name] = {
                        "text_unavailable": False,
                        "unified_diff": [
                            f"--- left/{name}",
                            f"+++ right/{name}",
                            "@@ terminal newline differs "
                            "(texts otherwise line-identical) @@",
                        ],
                    }
                else:
                    identical.append(name)
            else:
                left_print = left_prints.get(name)
                right_print = right_prints.get(name)
                if left_print == right_print and left_print is not None:
                    identical.append(name)
                else:
                    changed.append(name)
                    module_diffs[name] = {
                        "text_unavailable": True,
                        "left_fingerprint": left_print,
                        "right_fingerprint": right_print,
                    }

        return {
            "identical": not added and not removed and not changed,
            "added_modules": added,
            "removed_modules": removed,
            "changed_modules": changed,
            "identical_modules": identical,
            "module_diffs": module_diffs,
        }

    @staticmethod
    def _string_map(
            material: Dict[str, object],
            key: str,
    ) -> Dict[str, str]:
        """
        Extract one name->string mapping from a material payload.

        Args:
            material:
                Resolver material payload.
            key:
                Mapping key to extract ("sources" or "fingerprints").

        Returns:
            Dict[str, str]:
                Detached mapping; non-dict or non-string values drop out.
        """
        mapping = material.get(key) if isinstance(material, dict) else None
        if not isinstance(mapping, dict):
            return {}
        return {
            str(name): value
            for name, value in mapping.items()
            if isinstance(value, str)
        }

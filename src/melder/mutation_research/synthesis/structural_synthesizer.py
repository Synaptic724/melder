import ast
import hashlib
import threading
from typing import Dict, List, Optional, Set, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class StructuralSynthesizer(Cleanable):
    """
    AST-guided source composition over two recorded version texts.

    Purpose:
        The missing verb of the May "surgical mutation" flow (the diff
        family shipped the structured REPORT half; this is the SELECTION +
        SYNTHESIS half): pick named top-level structural parts (functions /
        classes) from a DONOR version's source and splice them into a BASE
        version's source - replacing same-named parts, appending new ones -
        producing one candidate source text ready for the codegen preview
        and, if the agent chooses, execution and multi-parent minting.

    Contract:
        - Pure text-in/text-out: the synthesizer never touches custody,
          never executes, never records. Provenance rides the verdict.
        - Selections are EXPLICIT asks: an unknown name (or a name of the
          wrong kind) refuses loudly, naming what the donor actually
          carries (teach-grade, strategy-resolution precedent).
        - Selections are UNIQUE asks: the same (name, kind) may be selected
          once. Duplicates refuse loudly - replaying one base span against
          already-spliced lines would corrupt neighboring parts, and a
          duplicated addition would append the same definition twice.
        - Parse failures on either side answer honestly (`parse_error`
          names the side and location; nothing composes) - synthesizing
          over broken recorded text is a legitimate question, not a crash.
        - Decorators travel with their def (the spliced segment starts at
          the first decorator line).
        - Replacements splice in descending base-line order so line spans
          stay valid; additions append at the tail in the caller's
          selection order.

    Threading:
        Instance `RLock`; the verb itself is stateless between calls.

    Lifecycle:
        Owned by its creator (the MutationResearch root or a test);
        `cleanup()` is idempotent; lock released last.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one stateless synthesizer.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Mark the synthesizer cleaned.

        Contract:
            - Idempotent; del posture; lock last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def synthesize(
            self,
            base_source: str,
            donor_source: str,
            *,
            take_functions: Optional[List[str]] = None,
            take_classes: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        """
        Compose one candidate source from a base text and donor selections.

        Args:
            base_source:
                The version text being upgraded (the candidate starts as
                this text).
            donor_source:
                The version text parts are taken FROM.
            take_functions:
                Top-level function names to take from the donor.
            take_classes:
                Top-level class names to take from the donor.

        Returns:
            Dict[str, object]:
                `{"parse_error": None | {"side", "message", "line"},
                "composed_source": str | None,
                "selections": [{"name", "kind", "action"}]}` where action
                is "replaced" (same-named part existed in base) or "added".

        Raises:
            ValueError:
                If no selection is supplied, either source is empty, a
                selected name is not a top-level part of that kind in the
                donor (the error names what the donor carries), or the same
                (name, kind) selection is requested more than once (the
                error names each duplicate).
        """
        self.check_cleaned()
        if not isinstance(base_source, str) or not base_source:
            raise ValueError("base_source must be a non-empty string.")
        if not isinstance(donor_source, str) or not donor_source:
            raise ValueError("donor_source must be a non-empty string.")
        functions = list(take_functions) if take_functions else []
        classes = list(take_classes) if take_classes else []
        if not functions and not classes:
            raise ValueError(
                "synthesize needs at least one selection "
                "(take_functions and/or take_classes)."
            )
        with self._lock:
            base_error = self._parse_error("base", base_source)
            if base_error is not None:
                return {
                    "parse_error": base_error,
                    "composed_source": None,
                    "selections": [],
                }
            donor_error = self._parse_error("donor", donor_source)
            if donor_error is not None:
                return {
                    "parse_error": donor_error,
                    "composed_source": None,
                    "selections": [],
                }
            base_index = self._top_level_index(base_source)
            donor_index = self._top_level_index(donor_source)
            selections: List[Dict[str, object]] = []
            replacements: List[Tuple[Tuple[int, int], str]] = []
            additions: List[str] = []
            requested = (
                [(name, "function") for name in functions]
                + [(name, "class") for name in classes]
            )
            # Duplicate selections are refused, not deduplicated: a repeated
            # replacement replays the original base span against the
            # already-spliced line list (deleting whatever follows the part),
            # and a repeated addition appends the same definition twice.
            seen_selections: Set[Tuple[str, str]] = set()
            duplicated: List[str] = []
            for name, kind in requested:
                if (name, kind) in seen_selections:
                    duplicated.append(f"{kind} '{name}'")
                seen_selections.add((name, kind))
            if duplicated:
                raise ValueError(
                    f"Duplicate selection(s): {sorted(set(duplicated))}. "
                    f"Each (name, kind) may be selected once per synthesis; "
                    f"remove the repeated ask(s)."
                )
            for name, kind in requested:
                donor_part = donor_index.get((name, kind))
                if donor_part is None:
                    available = sorted(
                        part_name
                        for part_name, part_kind in donor_index.keys()
                        if part_kind == kind
                    )
                    raise ValueError(
                        f"Donor source has no top-level {kind} '{name}'. "
                        f"Available donor parts of that kind: {available}."
                    )
                segment = self._segment(donor_source, donor_part)
                base_part = base_index.get((name, kind))
                if base_part is not None:
                    replacements.append((base_part, segment))
                    action = "replaced"
                else:
                    additions.append(segment)
                    action = "added"
                selections.append(
                    {"name": name, "kind": kind, "action": action}
                )
            composed = self._splice(base_source, replacements, additions)
        return {
            "parse_error": None,
            "composed_source": composed,
            "selections": selections,
        }

    def extract_part(
            self,
            source: str,
            name: str,
            *,
            kind: Optional[str] = None,
    ) -> Optional[Dict[str, object]]:
        """
        Return one named top-level part's text and span from one source.

        Purpose:
            The QUERY companion to synthesize(): part-grain reads
            (part_view / part_diff) locate a function or class by name
            without composing anything. Misses answer None (the caller
            decides its own honesty posture); only unparseable source and
            bad arguments refuse.

        Args:
            source:
                Parseable Python source text.
            name:
                Top-level part name to locate.
            kind:
                Optional filter: "function" or "class"; both when omitted.

        Returns:
            Optional[Dict[str, object]]:
                `{"name", "kind", "start_line", "end_line", "text"}`
                (span one-based inclusive, decorators included), or None
                when the source carries no such part.

        Raises:
            ValueError:
                If source/name are empty, kind is unknown, or the source
                does not parse (a query against broken text is loud - the
                caller asked about structure that cannot be read).
        """
        self.check_cleaned()
        if not isinstance(source, str) or not source:
            raise ValueError("source must be a non-empty string.")
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string.")
        if kind is not None and kind not in ("function", "class"):
            raise ValueError(
                f"Unknown part kind '{kind}'. Known kinds: "
                f"['class', 'function']."
            )
        with self._lock:
            error = self._parse_error("source", source)
            if error is not None:
                raise ValueError(
                    f"source does not parse (line {error['line']}): "
                    f"{error['message']}"
                )
            index = self._top_level_index(source)
            kinds = (kind,) if kind is not None else ("function", "class")
            for candidate_kind in kinds:
                span = index.get((name, candidate_kind))
                if span is not None:
                    return {
                        "name": name,
                        "kind": candidate_kind,
                        "start_line": span[0],
                        "end_line": span[1],
                        "text": self._segment(source, span),
                    }
        return None

    def list_parts(self, source: str) -> List[Dict[str, object]]:
        """
        Return every top-level part of one source, with code.

        Purpose:
            The inventory companion to extract_part(): "show me all the
            class/function code of this text" without knowing names.

        Args:
            source:
                Parseable Python source text.

        Returns:
            List[Dict[str, object]]:
                `{"name", "kind", "start_line", "end_line", "text",
                "sha256"}` rows in source order (decorators included in
                spans; sha256 = the PART FINGERPRINT over the part's
                exact text - the depth-3 change index: two versions'
                inventories compare part-by-part without pulling texts).

        Raises:
            ValueError:
                If source is empty or does not parse (loud - an inventory
                of unreadable structure is an error, not an empty list).
        """
        self.check_cleaned()
        if not isinstance(source, str) or not source:
            raise ValueError("source must be a non-empty string.")
        with self._lock:
            error = self._parse_error("source", source)
            if error is not None:
                raise ValueError(
                    f"source does not parse (line {error['line']}): "
                    f"{error['message']}"
                )
            index = self._top_level_index(source)
            rows = []
            for (name, kind), span in index.items():
                text = self._segment(source, span)
                rows.append({
                    "name": name,
                    "kind": kind,
                    "start_line": span[0],
                    "end_line": span[1],
                    "text": text,
                    "sha256": hashlib.sha256(
                        text.encode("utf-8")
                    ).hexdigest(),
                })
        rows.sort(key=lambda row: row["start_line"])
        return rows

    def _parse_error(
            self,
            side: str,
            source: str,
    ) -> Optional[Dict[str, object]]:
        """
        Parse one side and return an honest error row on failure.

        Args:
            side:
                "base" or "donor".
            source:
                Source text to parse.

        Returns:
            Optional[Dict[str, object]]:
                `{"side", "message", "line"}` or None when parseable.
        """
        try:
            ast.parse(source)
        except SyntaxError as error:
            return {
                "side": side,
                "message": str(error.msg),
                "line": error.lineno,
            }
        return None

    def _top_level_index(
            self,
            source: str,
    ) -> Dict[Tuple[str, str], Tuple[int, int]]:
        """
        Index one parseable source's top-level parts by (name, kind).

        Args:
            source:
                Parseable source text.

        Returns:
            Dict[Tuple[str, str], Tuple[int, int]]:
                (name, kind) -> ONE-BASED (start_line, end_line) span
                including decorators.
        """
        index: Dict[Tuple[str, str], Tuple[int, int]] = {}
        for node in ast.parse(source).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "function"
            elif isinstance(node, ast.ClassDef):
                kind = "class"
            else:
                continue
            start = node.lineno
            for decorator in node.decorator_list:
                start = min(start, decorator.lineno)
            index[(node.name, kind)] = (start, node.end_lineno)
        return index

    def _segment(self, source: str, span: Tuple[int, int]) -> str:
        """
        Return one span's text (one-based inclusive lines).

        Args:
            source:
                Source text.
            span:
                (start_line, end_line).

        Returns:
            str:
                Segment text without a trailing newline.
        """
        lines = source.splitlines()
        return "\n".join(lines[span[0] - 1:span[1]])

    def _splice(
            self,
            base_source: str,
            replacements: List[Tuple[Tuple[int, int], str]],
            additions: List[str],
    ) -> str:
        """
        Apply replacements (descending span order) then tail additions.

        Args:
            base_source:
                The starting text.
            replacements:
                ((start_line, end_line), segment) pairs against the BASE.
            additions:
                Segments appended at the tail in selection order.

        Returns:
            str:
                Composed source (trailing newline guaranteed).
        """
        lines = base_source.splitlines()
        for span, segment in sorted(
                replacements, key=lambda pair: pair[0][0], reverse=True,
        ):
            lines[span[0] - 1:span[1]] = segment.splitlines()
        for segment in additions:
            if lines and lines[-1].strip():
                lines.append("")
            lines.extend(segment.splitlines())
        return "\n".join(lines) + "\n"

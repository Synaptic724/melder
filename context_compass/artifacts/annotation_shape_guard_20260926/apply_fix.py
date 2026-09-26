"""Apply the caller-supplied-container fix to a repository root (argv[1]); anchored, per-file line endings kept."""
import pathlib
import sys


def edit(root: pathlib.Path, rel: str, pairs: list) -> None:
    """Replace each (old, new) exactly once in one file, preserving its line-ending style."""
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{rel}: anchor found {count} times: {old[:70]!r}")
        text = text.replace(old, new)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    print("edited", rel, repr(newline))


def cut_between(root: pathlib.Path, rel: str, start: str, stop: str, replacement: str) -> None:
    """Replace the text from `start` (inclusive) up to `stop` (exclusive), each found exactly once."""
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    if text.count(start) != 1 or text.count(stop) != 1:
        raise SystemExit(f"{rel}: cut anchors not unique")
    i = text.index(start)
    j = text.index(stop)
    text = text[:i] + replacement + text[j:]
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    print("cut", rel, repr(newline))


def guard(root: pathlib.Path) -> None:
    """AnnotationShapeGuardStrategy: drop the container branch and helper; Any is not a DI target."""
    rel = "src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py"
    edit(root, rel, [
        ("from typing import TYPE_CHECKING, Any, Tuple, get_args, get_origin\n",
         "from typing import TYPE_CHECKING, Any, get_args, get_origin\n"),
        ("""    Contract:
    - Rejects collection-style DI annotations that Melder does not support.
    - Treats `list[T]` as the only collection DI form worth deeper inspection
      in this first cut.
""", """    Contract:
    - Judges only shapes Phase 1 may inject: `list[T]` elements and forward
      references. A set, frozenset, dict or tuple parameter is never injected -
      Phase 1 classifies it PLAIN, a caller input - so this strategy does not
      judge it; `RequiredHolesStrategy` reports it as a REQUIRED_HOLE whose
      message says Melder injects collections only as `list[T]` (2026-09-26).
      Phase 1 is the single decider of injection; this strategy never breaks a
      spell over a parameter Phase 1 made a caller input.
"""),
        ("""        access: internal. Phase-4 strategy: rejects unsupported collection DI annotation shapes.
        Emits UNSUPPORTED_COLLECTION_SHAPE (set/dict/tuple of DI targets),
        LIST_ELEMENT_NOT_DI_TARGET, and UNRESOLVED_FORWARD_REF. Only list[FrameType] is valid
        collection DI.
""", """        access: internal. Phase-4 strategy: warns about list[T] elements and forward references
        Melder cannot inject. Emits LIST_ELEMENT_NOT_DI_TARGET and UNRESOLVED_FORWARD_REF
        (warnings). Only list[FrameType] is collection DI; set/dict/tuple parameters are caller
        inputs, reported by RequiredHolesStrategy.
"""),
        ('            description="Flags unsupported DI annotation shapes (set/dict/tuple, invalid list elements).",\n',
         '            description="Flags list elements and forward references Melder cannot inject.",\n'),
        ("""            - Emits `UNSUPPORTED_COLLECTION_SHAPE`,
              `UNRESOLVED_FORWARD_REF`, and `LIST_ELEMENT_NOT_DI_TARGET`
              issues when the annotation shape violates the supported DI model.
""", """            - Emits `UNRESOLVED_FORWARD_REF` and `LIST_ELEMENT_NOT_DI_TARGET`
              warnings when a list element or annotation cannot be injected.
            - Emits nothing for set, frozenset, dict or tuple parameters: Phase 1
              never injects them, so they are caller inputs, not DI errors.
"""),
        ("""        if isinstance(annotation, typing.ForwardRef):
            return True

        if isinstance(annotation, str):
            return True

        if inspect.isclass(annotation):""", """        if annotation is typing.Any:
            # A class since Python 3.11; Phase 1 never injects it, so neither
            # may this check treat it as a DI target.
            return False

        if isinstance(annotation, typing.ForwardRef):
            return True

        if isinstance(annotation, str):
            return True

        if inspect.isclass(annotation):"""),
        ("""            Returns True for forward refs, string frame keys, and non-builtin
            classes. This is intentionally heuristic rather than a full type
            system.
""", """            Returns True for forward refs, string frame keys, and non-builtin
            classes, and False for `typing.Any`, matching Phase 1's
            `SpellRequirementsFinder._looks_like_di_target`. This is
            intentionally heuristic rather than a full type system.
"""),
    ])
    cut_between(root, rel,
                "            if origin in (set, frozenset, dict, tuple):\n",
                "            if origin is list and len(args) == 1:\n", "")
    cut_between(root, rel,
                "    def _collection_args_have_di_targets(self, args: Tuple[Any, ...]) -> bool:\n",
                "    def _looks_like_di_target(self, annotation: Any) -> bool:\n", "")


def holes(root: pathlib.Path) -> None:
    """RequiredHolesStrategy: REQUIRED_HOLE names list-only collection injection for container parameters."""
    rel = "src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py"
    edit(root, rel, [
        ("from typing import TYPE_CHECKING\n", "from typing import TYPE_CHECKING, Any, get_origin\n"),
        ("""    - Emits warnings rather than hard errors because the caller may still
      provide these values at invocation time.
""", """    - Emits warnings rather than hard errors because the caller may still
      provide these values at invocation time.
    - For a set, frozenset, dict or tuple parameter the REQUIRED_HOLE message adds
      that Melder injects collections only as `list[T]`, so such a parameter is
      always supplied by the caller (2026-09-26; the Phase-4 annotation-shape
      guard no longer judges these parameters).
"""),
        ("""        default-less parameter - a hole Melder DI will never fill, so the caller must supply it
        via overrides or manual composition - plus OVERRIDE_REQUIRED and UNRESOLVED_INPUT
""", """        default-less parameter - a hole Melder DI will never fill, so the caller must supply it
        via overrides or manual composition; for set/dict/tuple parameters the message adds
        that Melder injects collections only as list[T] - plus OVERRIDE_REQUIRED and UNRESOLVED_INPUT
"""),
        ("""        - Emits one `REQUIRED_HOLE` warning per parameter that must be supplied
          by the caller.
""", """        - Emits one `REQUIRED_HOLE` warning per parameter that must be supplied
          by the caller; a set/frozenset/dict/tuple annotation adds the
          list-only collection hint (`_container_hint`).
"""),
        ("""                        "The caller must supply a value (e.g. via spell overrides "
                        "or manual composition)."
                    ),
""", """                        "The caller must supply a value (e.g. via spell overrides "
                        "or manual composition)."
                        f"{self._container_hint(param.annotation)}"
                    ),
"""),
        ("""    @staticmethod
    def _expected_type_for(requirements: SpellRequirements, param_name: str) -> str:
""", """    @staticmethod
    def _container_hint(annotation: Any) -> str:
        \"\"\"
        Return the list-only collection hint for a container-typed required hole.

        Contract:
            - Returns a leading-space sentence when the annotation's origin is set,
              frozenset, dict or tuple (bare generics such as `dict[str, X]` and
              their typing aliases); otherwise an empty string.
            - Pure; reads only the annotation object.

        Args:
            annotation: Phase-1 annotation of the required hole (may be None or a string).

        Returns:
            str: The hint sentence, or "".
        \"\"\"
        origin = get_origin(annotation)
        if origin not in (set, frozenset, dict, tuple):
            return ""
        return (
            " Melder injects collections only as list[T]; "
            f"a {origin.__name__} parameter is always supplied by the caller."
        )

    @staticmethod
    def _expected_type_for(requirements: SpellRequirements, param_name: str) -> str:
"""),
    ])


def main() -> None:
    """Apply the source edits under the root given on the command line."""
    root = pathlib.Path(sys.argv[1])
    guard(root)
    holes(root)


if __name__ == "__main__":
    main()

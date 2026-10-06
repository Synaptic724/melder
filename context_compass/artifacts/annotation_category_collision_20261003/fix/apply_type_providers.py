"""
Prototype: single type annotations select type providers; string spellframes stay categories.

Usage: python apply_type_providers.py <repo_root> [--check]
Edits compiler_phase_3.py (byte-level, CRLF-preserving, exact anchors).
"""
import pathlib
import sys

NL = "\r\n"


def crlf(text: str) -> str:
    return text.replace("\n", NL)


def patch(path: pathlib.Path, edits: list[tuple[str, str]], check: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    for old, new in edits:
        old_c, new_c = crlf(old), crlf(new)
        count = raw.count(old_c)
        if count != 1:
            raise SystemExit(f"{path.name}: anchor found {count} times (expected 1):\n{old!r}")
        raw = raw.replace(old_c, new_c)
    if check:
        print(f"OK (check) {path}")
        return
    path.write_bytes(raw.encode("utf-8"))
    print(f"patched {path}")


# 1) _spell_keys gains a sibling: the keys that denote the spell's TYPE.
OLD_SPELL_KEYS_TAIL = """        type_key = SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        frame = spell_obj.spellframe
        if frame is None:
            return (type_key,)
        frame_key = SpellInputUtils.normalize_frame_key(frame)
        if frame_key == type_key:
            return (type_key,)
        return (frame_key, type_key)

    def _matches_annotation(
"""
NEW_SPELL_KEYS_TAIL = """        type_key = SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        frame = spell_obj.spellframe
        if frame is None:
            return (type_key,)
        frame_key = SpellInputUtils.normalize_frame_key(frame)
        if frame_key == type_key:
            return (type_key,)
        return (frame_key, type_key)

    @staticmethod
    def _spell_type_keys(spell_obj: Spell) -> Tuple[str, ...]:
        \"\"\"
        Return the keys under which a spell PROVIDES A TYPE: the keys a single annotation may select.

        Contract:
            A single constructor annotation names a type. A spell provides that
            type when its own class has that name (its type key: a class's name,
            or an existing object's class name), or when it was bound under that
            type as its spellframe - a class or Protocol object used as a frame
            is a shape label, the "bind the implementation under its interface"
            idiom. A spellframe given as a STRING is a category: it groups
            definitions for explicit addressing (spellframe/binding_name,
            SpellMap, SpellContract) and for collection injection, and it never
            makes its members providers of a same-named type (owner ruling,
            2026-10-03: a category named like a type is not that type).

        Args:
            spell_obj: The candidate spell (any object with `spell_name` and `spellframe`).

        Returns:
            Tuple[str, ...]: One or two lowercased keys; a subset of `_spell_keys`.
        \"\"\"
        type_key = SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        frame = spell_obj.spellframe
        if frame is None or not isinstance(frame, type):
            return (type_key,)
        frame_key = SpellInputUtils.normalize_frame_key(frame)
        if frame_key == type_key:
            return (type_key,)
        return (frame_key, type_key)

    def _matches_annotation(
"""

# 2) _matches_annotation: the single resolver asks for type keys only.
OLD_MATCH_SIG = """    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
    ) -> bool:
        \"\"\"
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by address key, 2026-10-03):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell's keys (`_spell_keys`): its address frame key or its type
              key. A class-object annotation and its string spelling therefore
              resolve identically, an existing object is matched by its class,
              and a spellframe is a category or a shape label - never compared
              by object identity.
            - `binding_name`, when given, must equal the spell's binding name.
            - `require_class_spell=True` excludes METHOD/LAMBDA spell kinds.

        Args:
            annotation:
                Canonicalized annotation to match.
            binding_name:
                Optional binding-name filter.
            spell_obj:
                Candidate spell.
            require_class_spell:
                When True, only class-like spells are allowed.

        Returns:
            bool: `True` when the candidate should be considered for this
            dependency.
        \"\"\"
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        if self._annotation_key(annotation) not in self._spell_keys(spell_obj):
            return False
"""
NEW_MATCH_SIG = """    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
            type_providers_only: bool = False,
    ) -> bool:
        \"\"\"
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by address key, 2026-10-03; type providers, 2026-10-04):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell's keys: for a collection annotation (`type_providers_only`
              False) its address frame key or its type key (`_spell_keys`) - all
              implementations under a frame or of a type; for a single annotation
              (`type_providers_only` True) only the keys under which the spell
              provides a type (`_spell_type_keys`) - its class name, or a class
              or Protocol object it was bound under as its spellframe. A string
              spellframe is a category and never satisfies a single type
              annotation. A class-object annotation and its string spelling
              resolve identically, an existing object is matched by its class,
              and nothing is compared by object identity.
            - `binding_name`, when given, must equal the spell's binding name.
            - `require_class_spell=True` excludes METHOD/LAMBDA spell kinds.

        Args:
            annotation:
                Canonicalized annotation to match.
            binding_name:
                Optional binding-name filter.
            spell_obj:
                Candidate spell.
            require_class_spell:
                When True, only class-like spells are allowed.
            type_providers_only:
                When True, match the spell's type keys only (single annotations).

        Returns:
            bool: `True` when the candidate should be considered for this
            dependency.
        \"\"\"
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        keys = self._spell_type_keys(spell_obj) if type_providers_only else self._spell_keys(spell_obj)
        if self._annotation_key(annotation) not in keys:
            return False
"""

# 3) index: a second bucket map of type keys.
OLD_INDEX_BODY = """        Returns:
            Dict[str, Any]: `{"by_key": {key: [entries]}}`.
        \"\"\"
        by_key: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            for key in self._spell_keys(spell_obj):
                by_key.setdefault(key, []).append(entry)
        return {"by_key": by_key}
"""
NEW_INDEX_BODY = """        Returns:
            Dict[str, Any]: `{"by_key": {key: [entries]}, "by_type_key": {key: [entries]}}` -
            `by_key` buckets every address key (collection lookups), `by_type_key`
            only the keys under which a spell provides a type (`_spell_type_keys`,
            single lookups).
        \"\"\"
        by_key: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_type_key: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            for key in self._spell_keys(spell_obj):
                by_key.setdefault(key, []).append(entry)
            for key in self._spell_type_keys(spell_obj):
                by_type_key.setdefault(key, []).append(entry)
        return {"by_key": by_key, "by_type_key": by_type_key}
"""

# 4) indexed lookup: choose the bucket map.
OLD_INDEXED_SIG = """    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
    ) -> Dict[Any, "Spell"]:
        \"\"\"
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the one bucket of the annotation's key (`_annotation_key`);
              membership equals scan membership because both sides use the
              same keys (2026-10-03).
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        \"\"\"
        bucket = candidate_index["by_key"].get(self._annotation_key(annotation))
"""
NEW_INDEXED_SIG = """    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
            type_providers_only: bool = False,
    ) -> Dict[Any, "Spell"]:
        \"\"\"
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the one bucket of the annotation's key (`_annotation_key`)
              in `by_type_key` when `type_providers_only` (single annotations)
              and in `by_key` otherwise (collections); membership equals scan
              membership because both sides use the same key functions
              (`_spell_type_keys` / `_spell_keys`).
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        \"\"\"
        buckets = candidate_index["by_type_key"] if type_providers_only else candidate_index["by_key"]
        bucket = buckets.get(self._annotation_key(annotation))
"""

# 5) single resolver: type providers only, both paths.
OLD_SINGLE = """        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=True,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=True,
                ):
                    candidates[index] = spell_obj

        resolvable_candidates = {
"""
NEW_SINGLE = """        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=True,
                type_providers_only=True,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=True,
                        type_providers_only=True,
                ):
                    candidates[index] = spell_obj

        resolvable_candidates = {
"""

OLD_SINGLE_DOC = """        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Prefer matching resolvable providers. Only when none exist may a single
"""
NEW_SINGLE_DOC = """        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        A single annotation names a type, so only type providers are candidates
        (`_spell_type_keys`): spells of that class, or bound under that class or
        Protocol object as their spellframe. Members of a string-framed category
        that happens to share the type's name are not candidates (2026-10-04).

        Prefer matching resolvable providers. Only when none exist may a single
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0])
    patch(
        root / "src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py",
        [
            (OLD_SPELL_KEYS_TAIL, NEW_SPELL_KEYS_TAIL),
            (OLD_MATCH_SIG, NEW_MATCH_SIG),
            (OLD_INDEX_BODY, NEW_INDEX_BODY),
            (OLD_INDEXED_SIG, NEW_INDEXED_SIG),
            (OLD_SINGLE_DOC, NEW_SINGLE_DOC),
            (OLD_SINGLE, NEW_SINGLE),
        ],
        check,
    )


if __name__ == "__main__":
    main()

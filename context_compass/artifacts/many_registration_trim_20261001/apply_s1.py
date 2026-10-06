"""
Apply S1 (many registration trim) to a Melder tree: the store, the three emitters, the cache generation,
the tests that pin the old shape, and two new test files.

    python apply_s1.py --root <tree root> [--verb a1|a3] [--skip-tests]

Anchored: every replacement asserts its anchor occurs exactly once. Line endings are preserved per line
(creations.py is mixed CRLF/LF on the tree); inserted lines take the file's dominant ending; new files are CRLF.
"""
import argparse
import difflib
import pathlib
import sys
from typing import List, Tuple


def _read(path: pathlib.Path) -> Tuple[str, List[str]]:
    raw = path.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    endings = ["\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "") for ln in lines]
    text = "".join(ln[:-2] + "\n" if ln.endswith("\r\n") else ln for ln in lines)
    return text, endings


def _write(path: pathlib.Path, old_text: str, old_endings: List[str], new_text: str) -> None:
    dominant = "\r\n" if old_endings.count("\r\n") >= old_endings.count("\n") else "\n"
    old_lines = old_text.split("\n")
    new_lines = new_text.split("\n")
    if old_lines and old_lines[-1] == "":
        old_lines.pop()
    if new_lines and new_lines[-1] == "":
        new_lines.pop()
    out: List[str] = []
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out.append(new_lines[j1 + k] + (old_endings[i1 + k] or dominant))
        elif tag == "replace":
            for k in range(j2 - j1):
                ending = old_endings[i1 + k] if k < (i2 - i1) else dominant
                out.append(new_lines[j1 + k] + (ending or dominant))
        elif tag == "insert":
            for k in range(j2 - j1):
                out.append(new_lines[j1 + k] + dominant)
    path.write_bytes("".join(out).encode("utf-8"))


class Editor:
    def __init__(self, root: pathlib.Path, rel: str) -> None:
        self.path = root / rel
        self.text, self.endings = _read(self.path)
        self.original = self.text

    def replace(self, old: str, new: str) -> None:
        n = self.text.count(old)
        assert n == 1, f"{self.path.name}: anchor occurs {n} times: {old[:70]!r}"
        self.text = self.text.replace(old, new)

    def replace_between(self, start_anchor: str, end_anchor: str, new: str) -> None:
        assert self.text.count(start_anchor) == 1, (self.path.name, start_anchor[:60])
        assert self.text.count(end_anchor) == 1, (self.path.name, end_anchor[:60])
        i = self.text.index(start_anchor)
        j = self.text.index(end_anchor)
        assert i < j
        self.text = self.text[:i] + new + self.text[j:]

    def save(self) -> None:
        assert self.text != self.original, f"{self.path.name}: no change"
        _write(self.path, self.original, self.endings, self.text)
        print("edited", self.path)


def write_new(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    assert not path.exists(), f"{rel} exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    print("wrote ", path)


RECORD_CLASS = '''class ManyDisposalBucket:
    """
    Cleanup-only record of one `many` key that declared disposal methods.

    Purpose:
        Replace the per-entry `(object, disposal_methods)` tuples a many key
        used to mirror into `_disposable_creations` with one record per key
        (2026-10-01): the key's live bucket, aliased, plus the Spell-owned
        method list recorded once. A warm registration is then one list append
        instead of a tuple allocation and two appends.

    Contract:
        - `entries` IS the live many bucket held in `_creations` - the same
          list object, never a copy - so the live and disposal views cannot
          diverge and a single-object purge needs one removal.
        - `methods` is the Spell's established ordered disposal list, retained
          by reference (never matched, reordered or copied), identical for
          every entry of the key: a spell id hashes its resolved disposal
          names, so one key carries one declaration.
        - Both fields are borrowed. The owning `Creations` store detaches the
          record (cleanup, clear, purge, extract) and disposes from it; the
          record itself owns nothing and needs no cleanup.

    AGENT_ACCESS: internal
    """

    __slots__ = ("entries", "methods")

    def __init__(self, entries: List[object], methods: List[str]) -> None:
        """
        Bind the key's live bucket and its disposal list.

        Args:
            entries: The live many bucket of the key (aliased, not copied).
            methods: The Spell-owned ordered disposal method names.

        Returns:
            None.
        """
        self.entries = entries
        self.methods = methods


StoredDisposalEntry = Tuple[object, List[str]]
StoredDisposalValue = Union[StoredDisposalEntry, ManyDisposalBucket]
'''

REGISTER_MANY_A1 = '''    def register_many(
            self,
            key: str,
            item: object,
            disposal_methods: List[str],
    ) -> None:
        """
        Register one disposal-bearing `many` creation on the warm path.

        Purpose:
            The registration emitted plans and executors run on every creation
            of a disposal-bearing `many` root (2026-10-01). It is the
            `add_many_creations` shape without the keyword marshaling and the
            checks that verb keeps for callers it cannot trust: one lock, one
            dict read, one list append (measured 204 -> 104 ns per
            registration on 3.14t, GIL off).

        Contract:
            - Precondition, guaranteed by the emitters and NOT checked here:
              `key` is a `many` spell id whose Spell declares disposal methods,
              and `disposal_methods` is that Spell's own ordered list, the same
              object on every call for the key. A spell id hashes its resolved
              disposal names, so one key cannot carry two declarations, and one
              Existence per Spell means the key's live slot is a list or absent.
              Callers that cannot promise this use `add_many_creations`.
            - The first registration of the key creates the live bucket and
              its `ManyDisposalBucket` record (the bucket itself plus the
              method list) in one critical section; every later one appends.
            - Refuses a cleaned store exactly like `add_many_creations`: the
              object's disposal methods run and `RuntimeError` is raised.

        Args:
            key: The many spell id.
            item: The just-built object.
            disposal_methods: The Spell-owned ordered disposal method names.

        Raises:
            RuntimeError:
                If this store was cleaned while the object was being built.

        Threading:
            `_lock` is a leaf here: only the dict read, the first-use stores
            and the append run under it. A build that finishes after
            `cleanup()` observes `_cleaned` through the tombstone lock and is
            refused outside it, with no lock held while its methods run.

        Returns:
            None.
        """
        with self._lock:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(
                        bucket, disposal_methods,
                    )
                bucket.append(item)
                return
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=True,
            disposal_methods=disposal_methods,
        )

'''

REGISTER_MANY_A3_BODY_OLD = '''        with self._lock:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(
                        bucket, disposal_methods,
                    )
                bucket.append(item)
                return
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=True,
            disposal_methods=disposal_methods,
        )

'''
REGISTER_MANY_A3_BODY_NEW = '''        # Explicit acquire/release: the with-statement costs ~14 ns per call
        # on 3.14t (measured 2026-10-01), a tenth of this verb.
        lock = self._lock
        lock.acquire()
        try:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(
                        bucket, disposal_methods,
                    )
                bucket.append(item)
                return
        finally:
            lock.release()
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=True,
            disposal_methods=disposal_methods,
        )

'''

APPEND_MANY_LOCKED = '''    def _append_many_locked(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool,
            disposal_methods: Optional[List[str]],
    ) -> None:
        """
        Append one many creation through the checked public verb; caller holds `_lock`.

        Contract:
            - The caller holds `_lock` and has checked the store is not cleaned.
            - Validates before it appends, so a refused registration leaves the
              store untouched.
            - Creates the first-use bucket and, for a disposal-bearing key, its
              `ManyDisposalBucket` record in one critical section. The record
              IS the live bucket, so the live and disposal views cannot diverge
              (the BUG-073 invariant, now by construction).

        Raises:
            ValueError:
                If the key already holds a non-list live slot or a non-many
                disposable slot, or if this registration's disposal declaration
                disagrees with the key's existing entries: one many key carries
                one declaration (the spell id fixes it).
        """
        bucket = self._creations.get(key)
        if bucket is not None and not isinstance(bucket, list):
            raise ValueError(
                f"Key {key} already exists in creations with non-list slot."
            )
        record = self._disposable_creations.get(key)
        if has_disposal_methods:
            if record is None:
                if bucket:
                    raise ValueError(
                        f"Key {key} already holds many creations registered without disposal "
                        f"methods; one many key carries one disposal declaration."
                    )
            elif not isinstance(record, ManyDisposalBucket):
                raise ValueError(
                    f"Key {key} already exists in disposable creations with non-list slot."
                )
        elif record is not None:
            raise ValueError(
                f"Key {key} already holds many creations registered with disposal "
                f"methods; one many key carries one disposal declaration."
            )
        if bucket is None:
            bucket = []
            self._creations[key] = bucket
        if has_disposal_methods and record is None:
            self._disposable_creations[key] = ManyDisposalBucket(
                bucket,
                disposal_methods if disposal_methods is not None else [],
            )
        bucket.append(item)

'''

DISPOSE_MANY = '''    def _dispose_many_creations(
            self,
            bucket: ManyDisposalBucket,
    ) -> List[Exception]:
        """
        Dispose every object of one detached many record.

        Purpose:
            Share the multi-object disposal loop between targeted purge and
            whole-store cleanup without constructing a temporary registry.

        Contract:
            - Visit `bucket.entries` newest-first, preserving many disposal
              order.
            - Delegate each object to `_attempt_cleanup` paired with the key's
              one method list (`bucket.methods`), which runs every method name
              in order and returns one error per failing method.
            - Collect every failure and continue with the other objects.
            - Do not mutate the record, clear its borrowed method-name list, or
              reach into a live creation store.

        Args:
            bucket:
                The detached `ManyDisposalBucket` of one many target: its
                `entries` is the detached live bucket, still in registration
                order.

        Returns:
            List[Exception]:
                Disposal failures in attempt order. The caller aggregates or
                raises them after processing its selected retirement set.

        Threading / Lifecycle:
            The caller has already detached the record under the appropriate
            writer lock. This helper takes no lock and owns no scope policy;
            user disposal methods run after the removal locks are released.
        """
        errors: List[Exception] = []
        methods = bucket.methods
        for item in reversed(bucket.entries):
            errors.extend(self._attempt_cleanup((item, methods)))
        return errors

'''

DETACH_SINGLE = '''    def _detach_single_many_creation(
            self,
            spell_id: str,
            creation: object,
    ) -> Tuple[int, object, Optional[StoredDisposalEntry]]:
        """
        Detach one supplied object from an already-selected many bucket.

        Purpose:
            Preserve paired live/disposal removal for single-object purge without
            changing registration storage or creating a reverse discovery index.

        Contract:
            - The caller holds this store's lock and established key presence.
            - Search only this target's bucket, using object identity so custom
              equality cannot select a different creation or invoke user code.
            - Remove one retained entry. The disposal record aliases the live
              bucket, so that one removal retires it from both views; the
              returned disposal entry pairs the object with the key's method
              list when the key is disposal-bearing.
            - Preserve remaining order and remove the bucket, and its record,
              only when empty.
            - Missing references return zero; no disposal callback runs here.

        Args:
            spell_id: Existing key selected through normal spell discovery.
            creation: Original application instance requested for retirement.

        Returns:
            Tuple[int, object, Optional[StoredDisposalEntry]]:
                Count, detached live object and its optional disposal record.
                The caller retains both references until removal locks release.

        Threading / Lifecycle:
            Called only inside `_detach_purge_entries`' locked critical section.
            This helper owns no scope policy, additional lock or disposal action.
        """
        bucket = self._creations[spell_id]
        for index, retired in enumerate(bucket):
            if retired is creation:
                break
        else:
            return 0, None, None

        bucket.pop(index)
        record = self._disposable_creations.get(spell_id)
        if not bucket:
            del self._creations[spell_id]
            if record is not None:
                del self._disposable_creations[spell_id]
        if record is None:
            return 1, retired, None
        return 1, retired, (retired, record.methods)

'''

EXTRACT_MANY_OLD = '''            if isinstance(live_value, list):
                live_many = self._creations.pop(spell_id)
                disposable_many = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, list)
                    else None
                )
                for index, stored_value in enumerate(live_many):
                    entry = {
                        "scope": "many",
                        "disposable": disposable_many is not None,
                        "stored": stored_value,
                    }
                    if disposable_many is not None:
                        entry["disposal_methods"] = disposable_many[index][1]
                    extracted.append(entry)
'''
EXTRACT_MANY_NEW = '''            if isinstance(live_value, list):
                live_many = self._creations.pop(spell_id)
                record = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, ManyDisposalBucket)
                    else None
                )
                # One record per key: every row of a disposal-bearing many
                # key carries the same Spell-owned list object.
                methods = None if record is None else record.methods
                for stored_value in live_many:
                    entry = {
                        "scope": "many",
                        "disposable": methods is not None,
                        "stored": stored_value,
                    }
                    if methods is not None:
                        entry["disposal_methods"] = methods
                    extracted.append(entry)
'''

RESTORE_MANY_OLD = '''                if scope == "many":
                    existing = self._creations.get(spell_id)
                    if existing is None:
                        self._creations[spell_id] = []
                        existing = self._creations[spell_id]
                    if not isinstance(existing, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    existing.append(stored_value)
                    if is_disposable:
                        disposable_many = self._disposable_creations.get(spell_id)
                        if disposable_many is None:
                            self._disposable_creations[spell_id] = []
                            disposable_many = self._disposable_creations[spell_id]
                        if not isinstance(disposable_many, list):
                            raise RuntimeError(
                                f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                            )
                        disposable_many.append(
                            (
                                stored_value,
                                disposal_methods if disposal_methods is not None else [],
                            )
                        )
                    continue
'''
RESTORE_MANY_NEW = '''                if scope == "many":
                    existing = self._creations.get(spell_id)
                    if existing is None:
                        existing = []
                        self._creations[spell_id] = existing
                    elif not isinstance(existing, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    record = self._disposable_creations.get(spell_id)
                    if is_disposable:
                        if record is None:
                            if existing:
                                raise RuntimeError(
                                    f"Cannot restore a disposable many creation for spell '{spell_id}' "
                                    f"beside entries restored without disposal methods."
                                )
                            self._disposable_creations[spell_id] = ManyDisposalBucket(
                                existing,
                                disposal_methods if disposal_methods is not None else [],
                            )
                        elif not isinstance(record, ManyDisposalBucket):
                            raise RuntimeError(
                                f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                            )
                    elif record is not None:
                        raise RuntimeError(
                            f"Cannot restore a many creation without disposal methods for spell "
                            f"'{spell_id}' beside disposable entries."
                        )
                    existing.append(stored_value)
                    continue
'''


def edit_creations(root: pathlib.Path, verb: str) -> None:
    e = Editor(root, "src/melder/aether/conduit/creations/creations.py")
    e.replace(
        "StoredDisposalEntry = Tuple[object, List[str]]\n"
        "StoredDisposalValue = Union[StoredDisposalEntry, List[StoredDisposalEntry]]\n",
        RECORD_CLASS,
    )
    e.replace(
        "        - Disposal metadata mirrors only entries that declared disposal\n"
        "          methods:\n"
        "          - unique: `spell_id -> (object, disposal_methods)`\n"
        "          - many: `spell_id -> list[(object, disposal_methods)]`\n",
        "        - Disposal metadata mirrors only entries that declared disposal\n"
        "          methods:\n"
        "          - unique: `spell_id -> (object, disposal_methods)`\n"
        "          - many: `spell_id -> ManyDisposalBucket` whose `entries` IS the\n"
        "            live many bucket (the same list object, never a copy) and\n"
        "            whose `methods` is the Spell-owned list recorded once, at the\n"
        "            key's first registration (2026-10-01; before, a second list of\n"
        "            `(object, methods)` tuples was appended in step with the live\n"
        "            bucket, a tuple and a second append per creation). A many key\n"
        "            therefore carries one disposal declaration: every entry of the\n"
        "            key is disposal-bearing or none is.\n",
    )
    e.replace_between("    def _dispose_many_creations(\n", "    def _dispose_disposable_registry(\n", DISPOSE_MANY)
    e.replace(
        "            if isinstance(value, list):\n"
        "                errors.extend(self._dispose_many_creations(value))\n",
        "            if isinstance(value, ManyDisposalBucket):\n"
        "                errors.extend(self._dispose_many_creations(value))\n",
    )
    e.replace(
        "        Contract:\n"
        "            - Appends the live object into `_creations[key]`.\n"
        "            - Appends cleanup metadata into `_disposable_creations[key]` only\n"
        "              when disposal methods were declared.\n"
        "            - Rejects collisions with non-list slots.\n"
        "            - Preserves insertion order inside both the live many bucket and\n"
        "              the matching disposable metadata bucket.\n"
        "            - Retains the supplied disposal list directly for each entry;\n"
        "              omitted names use an empty list when disposal is enabled.\n"
        "            - First-use bucket creation and both appends are atomic with\n"
        "              respect to competing resolutions (BUG-073, 2026-07-17 audit):\n"
        "              the whole live+disposable mutation runs under `_lock`, so two\n"
        "              threads first-resolving the same key can never overwrite each\n"
        "              other's bucket and strand a successfully returned creation\n"
        "              outside lifetime and disposal tracking.\n",
        "        Contract:\n"
        "            - Appends the live object into `_creations[key]`.\n"
        "            - For a disposal-bearing key, records the Spell-owned method list\n"
        "              ONCE, at the key's first registration, in a `ManyDisposalBucket`\n"
        "              under `_disposable_creations[key]` whose `entries` is the live\n"
        "              bucket itself; later registrations of the key append only.\n"
        "            - Rejects collisions with non-list slots, and a registration whose\n"
        "              disposal declaration disagrees with the key's existing entries:\n"
        "              one many key carries one declaration (the spell id hashes the\n"
        "              resolved disposal names, so a live world cannot produce a mix).\n"
        "            - Preserves insertion order; the disposal view is the live bucket,\n"
        "              so the two cannot diverge (BUG-073, 2026-07-17 audit, now by\n"
        "              construction: the first-use bucket and its record are created\n"
        "              in one critical section under `_lock`).\n"
        "            - Retains the supplied disposal list directly; omitted names use\n"
        "              an empty list when disposal is enabled.\n"
        "            - Emitted plans and executors call `register_many` instead: the\n"
        "              same shape without the keyword marshaling and the checks this\n"
        "              public verb keeps (2026-10-01).\n",
    )
    e.replace(
        "        Raises:\n"
        "            ValueError:\n"
        "                If the key already holds a non-list slot.\n"
        "            RuntimeError:\n"
        "                If this store was cleaned while the object was being built.\n"
        "\n"
        "        Returns:\n"
        "            None.\n"
        "        \"\"\"\n"
        "        with self._lock:\n"
        "            if not self._cleaned:\n"
        "                self._append_many_locked(\n",
        "        Raises:\n"
        "            ValueError:\n"
        "                If the key already holds a non-list slot, or if the disposal\n"
        "                declaration disagrees with the key's existing entries.\n"
        "            RuntimeError:\n"
        "                If this store was cleaned while the object was being built.\n"
        "\n"
        "        Returns:\n"
        "            None.\n"
        "        \"\"\"\n"
        "        with self._lock:\n"
        "            if not self._cleaned:\n"
        "                self._append_many_locked(\n",
    )
    e.replace_between("    def _append_many_locked(\n", "    def get_creation(", REGISTER_MANY_A1 + APPEND_MANY_LOCKED)
    if verb == "a3":
        e.replace(REGISTER_MANY_A3_BODY_OLD, REGISTER_MANY_A3_BODY_NEW)
    e.replace(
        "        if isinstance(disposal, tuple):\n"
        "            errors = self._attempt_cleanup(disposal)\n"
        "        elif isinstance(disposal, list):\n"
        "            errors = self._dispose_many_creations(disposal)\n",
        "        if isinstance(disposal, tuple):\n"
        "            errors = self._attempt_cleanup(disposal)\n"
        "        elif isinstance(disposal, ManyDisposalBucket):\n"
        "            errors = self._dispose_many_creations(disposal)\n",
    )
    e.replace_between("    def _detach_single_many_creation(\n", "    def extract_spell_creations(\n", DETACH_SINGLE)
    e.replace(EXTRACT_MANY_OLD, EXTRACT_MANY_NEW)
    e.replace(
        "            - Restores both live entries and disposal metadata.\n"
        "            - Raises when the payload does not match the local slot shape.\n",
        "            - Restores both live entries and disposal metadata; a many key's\n"
        "              rows rebuild one `ManyDisposalBucket` over the restored bucket.\n"
        "            - Raises when the payload does not match the local slot shape, or\n"
        "              when the rows of one many key disagree on `disposable`.\n",
    )
    e.replace(RESTORE_MANY_OLD, RESTORE_MANY_NEW)
    e.save()


def edit_emitters(root: pathlib.Path) -> None:
    e = Editor(root, "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py")
    e.replace(
        '        lines.append(\n'
        '            f"{indent}many_store.add_many_creations({sid_name}, v{index}, "\n'
        '            f"has_disposal_methods=True, disposal_methods={disposal_name})"\n'
        '        )\n',
        '        # `register_many` (2026-10-01): the positional hot verb; the key\'s\n'
        '        # disposal list is recorded once by the store, not carried per entry.\n'
        '        lines.append(f"{indent}many_store.register_many({sid_name}, v{index}, {disposal_name})")\n',
    )
    e.save()

    solo_old = (
        "    many_creations.add_many_creations(\n"
        "        spell_id,\n"
        "        instance,\n"
        "        has_disposal_methods=True,\n"
        "        disposal_methods=disposal_methods,\n"
        "    )\n"
    )
    solo_new = "    many_creations.register_many(spell_id, instance, disposal_methods)\n"
    for rel in (
        "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py",
        "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py",
    ):
        e = Editor(root, rel)
        e.replace(solo_old, solo_new)
        e.save()

    e = Editor(root, "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py")
    e.replace(
        "            # `many` is transient (a new instance per meld, never cached), so\n"
        "            # there is no build guard. The append goes through\n"
        "            # `add_many_creations`, which takes the store lock as a leaf (the\n"
        "            # former lockless inline append could lose a first-use bucket).\n",
        "            # `many` is transient (a new instance per meld, never cached), so\n"
        "            # there is no build guard. The append goes through\n"
        "            # `register_many`, which takes the store lock as a leaf (the\n"
        "            # former lockless inline append could lose a first-use bucket)\n"
        "            # and records the step's disposal list once per key (2026-10-01).\n",
    )
    e.replace(
        "        - Singleton entries WITH disposal methods, and every disposal-bearing\n"
        "          `many` append, go through `add_creation` / `add_many_creations`,\n"
        "          which take the store lock as a LEAF so the live and disposal writes\n"
        "          land together, and refuse a store cleaned during the build.\n",
        "        - Singleton entries WITH disposal methods go through `add_creation`,\n"
        "          and every disposal-bearing `many` append through `register_many`\n"
        "          (positional; the key's disposal list is recorded once, 2026-10-01);\n"
        "          both take the store lock as a LEAF so the live and disposal writes\n"
        "          land together, and refuse a store cleaned during the build.\n",
    )
    e.replace(
        '    if existence is Existence.many:\n'
        '        # Callers emit this block only when disposal truth is present.\n'
        '        lines.extend([\n'
        '            f"{indent}creations_{step_index}.add_many_creations(",\n'
        '            f"{indent}    spell_id_{step_index},",\n'
        '            f"{indent}    instance_{step_index},",\n'
        '            *disposal_arguments,\n'
        '            f"{indent})",\n'
        '        ])\n'
        '        return\n',
        '    if existence is Existence.many:\n'
        '        # Callers emit this block only when disposal truth is present, so the\n'
        '        # positional hot verb takes the step\'s bound method list directly.\n'
        '        lines.extend([\n'
        '            f"{indent}creations_{step_index}.register_many(",\n'
        '            f"{indent}    spell_id_{step_index},",\n'
        '            f"{indent}    instance_{step_index},",\n'
        '            f"{indent}    disposal_methods_{step_index},",\n'
        '            f"{indent})",\n'
        '        ])\n'
        '        return\n',
    )
    e.save()

    e = Editor(root, "src/melder/utilities/caching_system/caching_system.py")
    e.replace(
        "    # shapes. Older bundles are treated as cold cache and regenerated.\n"
        "    CACHE_VERSION_HISTORY",
        "    # shapes. Older bundles are treated as cold cache and regenerated.\n"
        "    # Version 16 retires executors emitted before the many registration\n"
        "    # trim (2026-10-01): they still call the public `add_many_creations`\n"
        "    # and stay correct, but pay the old keyword call per creation.\n"
        "    CACHE_VERSION_HISTORY",
    )
    e.replace(
        '        15: "structural_snapshot_rows",\n    })\n',
        '        15: "structural_snapshot_rows",\n        16: "many_registration_per_key_methods",\n    })\n',
    )
    e.save()


def edit_tests(root: pathlib.Path) -> None:
    e = Editor(root, "tests/unit/melder/aether/conduit/creations/test_creations.py")
    e.replace(
        '    assert creations._creations["spell-many"] == [obj]\n'
        '    assert creations._disposable_creations["spell-many"][0] == _disposable_entry(\n'
        '        obj,\n'
        '        "dispose",\n'
        '    )\n',
        '    assert creations._creations["spell-many"] == [obj]\n'
        '    record = creations._disposable_creations["spell-many"]\n'
        '    assert isinstance(record, ManyDisposalBucket)\n'
        '    assert record.entries is creations._creations["spell-many"]\n'
        '    assert record.methods == ["dispose"]\n',
    )
    e.replace(
        "from melder.aether.conduit.creations.creations import Creations\n",
        "from melder.aether.conduit.creations.creations import Creations, ManyDisposalBucket\n",
    )
    e.save()

    e = Editor(root, "tests/unit/melder/aether/conduit/creations/test_creations_many_first_use_atomicity_regression.py")
    e.replace(
        '    disposal_bucket = store._disposable_creations["spell-many"]\n'
        '    assert len(disposal_bucket) == len(bucket) == 2, (\n'
        '        "disposal tracking does not mirror the live bucket"\n'
        '    )\n',
        '    disposal_bucket = store._disposable_creations["spell-many"]\n'
        '    assert disposal_bucket.entries is bucket and len(bucket) == 2, (\n'
        '        "disposal tracking does not mirror the live bucket"\n'
        '    )\n',
    )
    e.replace(
        '    """Behavior guard: the healthy sequential lane is unchanged.\n'
        '\n'
        '    Contract assertions:\n'
        '        - Repeated registrations append in order to one bucket.\n'
        '        - Disposal metadata is recorded only for disposal-declaring entries.\n'
        '    """\n'
        '    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")\n'
        '    probe = DisposalProbe("tracked")\n'
        '    plain = object()\n'
        '\n'
        '    store.add_many_creations(\n'
        '        "spell-seq", probe,\n'
        '        has_disposal_methods=True, disposal_methods=["dispose"],\n'
        '    )\n'
        '    store.add_many_creations("spell-seq", plain)\n'
        '\n'
        '    bucket = store._creations["spell-seq"]\n'
        '    assert bucket == [probe, plain]\n'
        '    disposal_bucket = store._disposable_creations["spell-seq"]\n'
        '    assert len(disposal_bucket) == 1\n'
        '    assert disposal_bucket[0][0] is probe\n'
        '\n'
        '    store.cleanup()\n'
        '    assert probe.dispose_calls == 1\n',
        '    """Behavior guard: the healthy sequential lane is unchanged.\n'
        '\n'
        '    Contract assertions:\n'
        '        - Repeated registrations append in order to one bucket.\n'
        '        - One many key carries one disposal declaration (2026-10-01): a\n'
        '          registration without disposal methods under a disposal-bearing\n'
        '          key is refused and leaves the bucket untouched. Before, the\n'
        '          disposal metadata was allowed to be sparse.\n'
        '    """\n'
        '    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")\n'
        '    probe = DisposalProbe("tracked")\n'
        '    second = DisposalProbe("second")\n'
        '    plain = object()\n'
        '\n'
        '    store.add_many_creations(\n'
        '        "spell-seq", probe,\n'
        '        has_disposal_methods=True, disposal_methods=["dispose"],\n'
        '    )\n'
        '    store.add_many_creations(\n'
        '        "spell-seq", second,\n'
        '        has_disposal_methods=True, disposal_methods=["dispose"],\n'
        '    )\n'
        '    with pytest.raises(ValueError, match="one disposal declaration"):\n'
        '        store.add_many_creations("spell-seq", plain)\n'
        '\n'
        '    bucket = store._creations["spell-seq"]\n'
        '    assert bucket == [probe, second]\n'
        '    disposal_bucket = store._disposable_creations["spell-seq"]\n'
        '    assert disposal_bucket.entries is bucket\n'
        '    assert disposal_bucket.methods == ["dispose"]\n'
        '\n'
        '    store.cleanup()\n'
        '    assert probe.dispose_calls == 1\n'
        '    assert second.dispose_calls == 1\n',
    )
    if "\nimport pytest\n" not in e.text:
        e.replace(
            "from typing import Any, Dict, List, Optional\n",
            "from typing import Any, Dict, List, Optional\n\nimport pytest\n",
        )
    e.save()

    e = Editor(root, "tests/integration/melder/conduit/test_conduit_integration_creations.py")
    e.replace(
        "        bucket = lesser._creations._disposable_creations.get(many_id)\n"
        "        assert bucket is not None\n"
        "        values = [entry[0] for entry in bucket]\n"
        "        assert values == [many_instance]\n",
        "        bucket = lesser._creations._disposable_creations.get(many_id)\n"
        "        assert bucket is not None\n"
        "        values = list(bucket.entries)\n"
        "        assert values == [many_instance]\n",
    )
    e.save()

    e = Editor(root, "tests/integration/melder/conduit/test_ordered_disposal_runtime.py")
    e.replace(
        "            raw_entry = conduit._creations._disposable_creations[spell_id]\n"
        "            entry = (\n"
        "                next(row for row in raw_entry if row[0] is value)\n"
        "                if spell.existence is Existence.many else raw_entry\n"
        "            )\n"
        "            assert entry[0] is value\n",
        "            raw_entry = conduit._creations._disposable_creations[spell_id]\n"
        "            if spell.existence is Existence.many:\n"
        "                # One record per many key (2026-10-01): the bucket plus the\n"
        "                # key's one method list.\n"
        "                assert any(item is value for item in raw_entry.entries)\n"
        "                entry = (value, raw_entry.methods)\n"
        "            else:\n"
        "                entry = raw_entry\n"
        "            assert entry[0] is value\n",
    )
    e.save()

    e = Editor(root, "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py")
    e.replace(
        '    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,\n'
        '                           disposal_methods: Optional[List[str]] = None) -> None:\n'
        '        """Record one disposal-bearing many instance."""\n'
        '        self.disposal_adds.append((key, item))\n',
        '    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,\n'
        '                           disposal_methods: Optional[List[str]] = None) -> None:\n'
        '        """Record one disposal-bearing many instance."""\n'
        '        self.disposal_adds.append((key, item))\n'
        '\n'
        '    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:\n'
        '        """Record one disposal-bearing many instance registered through the hot verb (2026-10-01)."""\n'
        '        self.disposal_adds.append((key, item))\n',
    )
    e.replace(
        '    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,\n'
        '                           disposal_methods: Optional[List[str]] = None) -> None:\n'
        '        """Record the many registration and the list passed."""\n'
        '        super().add_many_creations(\n'
        '            key, item, has_disposal_methods=has_disposal_methods, disposal_methods=disposal_methods,\n'
        '        )\n'
        '        self.disposal_lists.append((key, disposal_methods))\n',
        '    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,\n'
        '                           disposal_methods: Optional[List[str]] = None) -> None:\n'
        '        """Record the many registration and the list passed."""\n'
        '        super().add_many_creations(\n'
        '            key, item, has_disposal_methods=has_disposal_methods, disposal_methods=disposal_methods,\n'
        '        )\n'
        '        self.disposal_lists.append((key, disposal_methods))\n'
        '\n'
        '    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:\n'
        '        """Record the hot-verb many registration and the list passed (2026-10-01)."""\n'
        '        super().register_many(key, item, disposal_methods)\n'
        '        self.disposal_lists.append((key, disposal_methods))\n',
    )
    e.save()

    e = Editor(root, "tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py")
    e.replace(
        "    def _add_many_creations(*args, **kwargs):\n"
        "        add_many_calls.append((args, kwargs))\n"
        "\n"
        "    return SimpleNamespace(\n"
        "        add_creation=_add_creation,\n"
        "        add_many_creations=_add_many_creations,\n",
        "    def _add_many_creations(*args, **kwargs):\n"
        "        add_many_calls.append((args, kwargs))\n"
        "\n"
        "    def _register_many(*args, **kwargs):\n"
        "        # The solo templates call the positional hot verb (2026-10-01).\n"
        "        add_many_calls.append((args, kwargs))\n"
        "\n"
        "    return SimpleNamespace(\n"
        "        add_creation=_add_creation,\n"
        "        add_many_creations=_add_many_creations,\n"
        "        register_many=_register_many,\n",
    )
    e.save()

    e = Editor(root, "tests/component/melder/aether/conduit/test_conduit_component_purge.py")
    e.replace(
        'def test_single_many_purge_preserves_sparse_disposal_records() -> None:\n'
        '    """\n'
        '    Purpose: Retire a live entry when not every entry has disposal metadata.\n'
        '    Contract: Removing an undisposable entry does not remove the next object\'s\n'
        '        metadata; later single/full purges dispose the correct objects exactly once.\n'
        '    Returns: None; the native store remains reusable after its last entry is purged.\n'
        '    """\n'
        '    book = _make_spellbook()\n'
        '    spell_id = book.bind(spell=PurgeResource, existence=Existence.many)\n'
        '    root = book.conjure()\n'
        '    try:\n'
        '        spell = book._spells_by_id[spell_id]\n'
        '        first, second, third = PurgeResource(), PurgeResource(), PurgeResource()\n'
        '        root._creations.add_many_creations(spell_id, first)\n'
        '        root._creations.add_many_creations(\n'
        '            spell_id, second, has_disposal_methods=True, disposal_methods=["cleanup"],\n'
        '        )\n'
        '        root._creations.add_many_creations(\n'
        '            spell_id, third, has_disposal_methods=True, disposal_methods=["cleanup"],\n'
        '        )\n'
        '        assert root._creations.purge(spell, purge_all=False, creation=first) == 1\n'
        '        assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 0\n'
        '        assert root.purge(second, purge_all=False) == 1\n'
        '        assert second.cleanup_calls == 1\n'
        '        assert third.cleanup_calls == 0\n'
        '        assert root.purge(third) == 1\n'
        '        assert third.cleanup_calls == 1\n'
        '        assert root.purge(third) == 0\n'
        '    finally:\n'
        '        root.permanent_cleanup()\n',
        'def test_single_many_purge_keeps_the_record_over_the_remaining_entries() -> None:\n'
        '    """\n'
        '    Purpose: Retire live entries one at a time from a disposal-bearing many key.\n'
        '    Contract: One many key carries one disposal declaration (2026-10-01): a plain\n'
        '        registration under a disposal-bearing key is refused and leaves the key as\n'
        '        it was; each single purge disposes exactly its object, the record keeps\n'
        '        covering the rest, and the store is reusable after the last entry goes.\n'
        '        Before, disposal metadata could be sparse and this test pinned that shape.\n'
        '    Returns: None.\n'
        '    """\n'
        '    book = _make_spellbook()\n'
        '    spell_id = book.bind(spell=PurgeResource, existence=Existence.many)\n'
        '    root = book.conjure()\n'
        '    try:\n'
        '        spell = book._spells_by_id[spell_id]\n'
        '        first, second, third = PurgeResource(), PurgeResource(), PurgeResource()\n'
        '        root._creations.add_many_creations(\n'
        '            spell_id, first, has_disposal_methods=True, disposal_methods=["cleanup"],\n'
        '        )\n'
        '        root._creations.add_many_creations(\n'
        '            spell_id, second, has_disposal_methods=True, disposal_methods=["cleanup"],\n'
        '        )\n'
        '        with pytest.raises(ValueError, match="one disposal declaration"):\n'
        '            root._creations.add_many_creations(spell_id, third)\n'
        '        assert root._creations._creations[spell_id] == [first, second]\n'
        '        assert root._creations.purge(spell, purge_all=False, creation=first) == 1\n'
        '        assert first.cleanup_calls == 1\n'
        '        assert second.cleanup_calls == third.cleanup_calls == 0\n'
        '        assert root.purge(second, purge_all=False) == 1\n'
        '        assert second.cleanup_calls == 1\n'
        '        assert spell_id not in root._creations._creations\n'
        '        assert spell_id not in root._creations._disposable_creations\n'
        '        assert root.purge(second) == 0\n'
        '    finally:\n'
        '        root.permanent_cleanup()\n',
    )
    e.save()

    e = Editor(root, "tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py")
    e.replace(
        '        calls = store.add_many_calls if route == "many" else store.add_creation_calls\n'
        '        assert len(calls) == 1\n'
        '        assert calls[0][0] == (spell_id, result)\n'
        '        assert calls[0][1]["has_disposal_methods"] is True\n'
        '        assert calls[0][1]["disposal_methods"] == names\n'
        '        assert calls[0][1]["disposal_methods"] is names\n',
        '        calls = store.add_many_calls if route == "many" else store.add_creation_calls\n'
        '        assert len(calls) == 1\n'
        '        if route == "many":\n'
        '            # `register_many` (2026-10-01) is positional: the live list rides as the third argument.\n'
        '            assert calls[0][0] == (spell_id, result, names)\n'
        '            assert calls[0][0][2] is names\n'
        '            assert calls[0][1] == {}\n'
        '        else:\n'
        '            assert calls[0][0] == (spell_id, result)\n'
        '            assert calls[0][1]["has_disposal_methods"] is True\n'
        '            assert calls[0][1]["disposal_methods"] == names\n'
        '            assert calls[0][1]["disposal_methods"] is names\n',
    )
    e.save()

    e = Editor(root, "tests/integration/melder/spellbook/test_cache_schema_version_integration.py")
    e.replace(
        '    15: "structural_snapshot_rows",\n}\n',
        '    15: "structural_snapshot_rows",\n    16: "many_registration_per_key_methods",\n}\n',
    )
    e.save()

    e = Editor(root, "tests/experimentation/codegen_strategy_certification.py")
    e.replace(
        'REGISTER = re.compile(r"^    many_store\\.add_many_creations\\(sid(\\d+), v(\\d+), has_disposal_methods=True, disposal_methods=dm(\\d+)\\)$", re.M)\n',
        '# The emitted registration line since the trim landed (2026-10-01): the positional hot verb. The S1 transform\n'
        '# now measures the real `register_many` against its stand-in, which should be a wash.\n'
        'REGISTER = re.compile(r"^    many_store\\.register_many\\(sid(\\d+), v(\\d+), dm(\\d+)\\)$", re.M)\n',
    )
    e.save()

    e = Editor(root, "tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py")
    e.replace(
        "        _ = has_disposal_methods\n"
        "        _ = disposal_methods\n"
        "        self._disposable_creations.setdefault(spell_id, []).append(instance)\n",
        "        _ = has_disposal_methods\n"
        "        _ = disposal_methods\n"
        "        self._disposable_creations.setdefault(spell_id, []).append(instance)\n"
        "\n"
        "    def register_many(\n"
        "            self,\n"
        "            spell_id: str,\n"
        "            instance: Any,\n"
        "            disposal_methods: Sequence[str],\n"
        "    ) -> None:\n"
        "        \"\"\"Stand-in for the positional hot verb emitted since 2026-10-01.\"\"\"\n"
        "        _ = disposal_methods\n"
        "        self._disposable_creations.setdefault(spell_id, []).append(instance)\n",
    )
    e.save()


UNIT_TEST = '''"""
Unit tests of the many registration trim (2026-10-01).

Scope:
    `Creations.register_many` (the positional hot verb emitted plans call) and the
    `ManyDisposalBucket` record it writes: one record per disposal-bearing many key whose
    `entries` IS the live bucket and whose `methods` is the Spell-owned list recorded once.
    Every reader of that record is exercised through the public store surface: whole-store
    cleanup, reusable clear, whole-target and single-object purge, extract/restore, and the
    refusal of a build that finishes after cleanup.
"""

from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations, ManyDisposalBucket
from melder.aether.spellbook.existence.existence import Existence


class _Probe:
    """Disposal probe that records the order its methods ran in a shared log."""

    def __init__(self, label: str, log: List[str]) -> None:
        self.label = label
        self.log = log

    def close(self) -> None:
        """First declared method."""
        self.log.append(f"{self.label}:close")

    def dispose(self) -> None:
        """Second declared method."""
        self.log.append(f"{self.label}:dispose")


class _Raising(_Probe):
    """Probe whose first method raises so aggregation can be observed."""

    def close(self) -> None:
        """Raise, then the second method must still run."""
        self.log.append(f"{self.label}:close")
        raise ValueError(self.label)


class _ManySpell:
    """Minimal spell stand-in for purge: an id and an Existence."""

    def __init__(self, spell_id: str, existence: Existence = Existence.many) -> None:
        self.spell_id = spell_id
        self.existence = existence


@pytest.fixture
def store() -> Creations:
    """A fresh store per test."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


@pytest.fixture
def methods() -> List[str]:
    """One Spell-owned method list, shared by every registration of a key."""
    return ["close", "dispose"]


def test_register_many_first_use_creates_bucket_and_record(store: Creations, methods: List[str]) -> None:
    """The first registration creates the live bucket and one record aliasing it."""
    log: List[str] = []
    first = _Probe("a", log)

    store.register_many("spell-many", first, methods)

    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == [first]
    assert isinstance(record, ManyDisposalBucket)
    assert record.entries is bucket
    assert record.methods is methods


def test_register_many_later_registrations_append_only(store: Creations, methods: List[str]) -> None:
    """Later registrations append to the bucket; the record is unchanged and still aliases it."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "abc"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == probes
    assert record.entries is bucket
    assert len(record.entries) == 3
    assert record.methods is methods


def test_register_many_public_verb_writes_the_same_shape(store: Creations, methods: List[str]) -> None:
    """`add_many_creations` with disposal and `register_many` interleave on one record."""
    log: List[str] = []
    first = _Probe("a", log)
    second = _Probe("b", log)

    store.add_many_creations("spell-many", first, has_disposal_methods=True, disposal_methods=methods)
    store.register_many("spell-many", second, methods)

    record = store._disposable_creations["spell-many"]
    assert record.entries == [first, second]
    assert record.entries is store._creations["spell-many"]
    assert record.methods is methods


def test_cleanup_disposes_newest_first_with_the_keys_methods(store: Creations, methods: List[str]) -> None:
    """Whole-store cleanup runs every object of the record newest-first, methods in declared order."""
    log: List[str] = []
    for label in "abc":
        store.register_many("spell-many", _Probe(label, log), methods)

    store.cleanup()

    assert log == ["c:close", "c:dispose", "b:close", "b:dispose", "a:close", "a:dispose"]


def test_cleanup_orders_keys_newest_first_and_buckets_within(store: Creations, methods: List[str]) -> None:
    """Across keys the registry is walked newest key first; inside a key newest entry first."""
    log: List[str] = []
    store.register_many("leaf", _Probe("leaf1", log), methods)
    store.register_many("root", _Probe("root1", log), methods)
    store.register_many("leaf", _Probe("leaf2", log), methods)
    store.register_many("root", _Probe("root2", log), methods)

    store.cleanup()

    assert [entry.split(":")[0] for entry in log if entry.endswith(":close")] == [
        "root2", "root1", "leaf2", "leaf1",
    ]


def test_cleanup_aggregates_one_error_per_failing_method(store: Creations, methods: List[str]) -> None:
    """A failing method yields one chained RuntimeError and the other methods and objects still run."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    store.register_many("spell-many", _Raising("b", log), methods)

    with pytest.raises(ExceptionGroup) as caught:
        store.cleanup()

    assert len(caught.value.exceptions) == 1
    error = caught.value.exceptions[0]
    assert isinstance(error, RuntimeError)
    assert isinstance(error.__cause__, ValueError)
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_clear_all_disposes_and_leaves_the_store_reusable(store: Creations, methods: List[str]) -> None:
    """A reusable clear disposes the record's objects and a later registration starts a new record."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    old_record = store._disposable_creations["spell-many"]

    store.clear_all()
    assert log == ["a:close", "a:dispose"]
    assert store._creations == {}
    assert store._disposable_creations == {}

    store.register_many("spell-many", _Probe("b", log), methods)
    new_record = store._disposable_creations["spell-many"]
    assert new_record is not old_record
    assert new_record.entries is store._creations["spell-many"]


def test_purge_all_disposes_the_bucket_and_removes_both_keys(store: Creations, methods: List[str]) -> None:
    """Whole-target purge detaches the bucket and its record and disposes newest-first."""
    log: List[str] = []
    for label in "ab":
        store.register_many("spell-many", _Probe(label, log), methods)

    count = store.purge(_ManySpell("spell-many"))

    assert count == 2
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_purge_single_disposes_only_that_object_with_the_keys_methods(
        store: Creations, methods: List[str],
) -> None:
    """Single-object purge removes one entry from the aliased bucket and disposes it alone."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "abc"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    count = store.purge(_ManySpell("spell-many"), purge_all=False, creation=probes[1])

    assert count == 1
    assert log == ["b:close", "b:dispose"]
    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == [probes[0], probes[2]]
    assert record.entries is bucket
    assert record.methods is methods


def test_purge_single_of_last_entry_removes_bucket_and_record(store: Creations, methods: List[str]) -> None:
    """Retiring the last object of a key removes the live bucket and the record together."""
    log: List[str] = []
    probe = _Probe("a", log)
    store.register_many("spell-many", probe, methods)

    assert store.purge(_ManySpell("spell-many"), purge_all=False, creation=probe) == 1
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations
    assert log == ["a:close", "a:dispose"]


def test_purge_single_absent_reference_changes_nothing(store: Creations, methods: List[str]) -> None:
    """An object that is not retained under the key returns zero and disposes nothing."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)

    assert store.purge(_ManySpell("spell-many"), purge_all=False, creation=_Probe("x", log)) == 0
    assert log == []
    assert len(store._creations["spell-many"]) == 1


def test_extract_rows_carry_the_keys_methods_and_restore_rebuilds_one_record(
        store: Creations, methods: List[str],
) -> None:
    """Extract yields one row per object with the key's list; restore rebuilds the aliased record."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "ab"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    rows = store.extract_spell_creations("spell-many")

    assert [row["stored"] for row in rows] == probes
    assert all(row["scope"] == "many" and row["disposable"] for row in rows)
    assert all(row["disposal_methods"] is methods for row in rows)
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations

    target = Creations(owner_conduit_id="conduit-2", id="conduit-2")
    target.restore_spell_creations("spell-many", rows)

    bucket = target._creations["spell-many"]
    record = target._disposable_creations["spell-many"]
    assert bucket == probes
    assert record.entries is bucket
    assert record.methods is methods
    target.cleanup()
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_extract_restore_of_a_plain_many_key_keeps_it_plain(store: Creations) -> None:
    """A many key registered without disposal round-trips with no record."""
    first = object()
    store.add_many_creations("spell-plain", first)

    rows = store.extract_spell_creations("spell-plain")
    assert rows == [{"scope": "many", "disposable": False, "stored": first}]

    store.restore_spell_creations("spell-plain", rows)
    assert store._creations["spell-plain"] == [first]
    assert "spell-plain" not in store._disposable_creations


def test_restore_refuses_rows_that_disagree_on_disposable(store: Creations, methods: List[str]) -> None:
    """Rows of one many key must agree on `disposable`; a mix is refused loudly."""
    first = object()
    second = object()
    mixed = [
        {"scope": "many", "disposable": True, "stored": first, "disposal_methods": methods},
        {"scope": "many", "disposable": False, "stored": second},
    ]
    with pytest.raises(RuntimeError, match="without disposal methods"):
        store.restore_spell_creations("spell-many", mixed)

    reversed_mix = [
        {"scope": "many", "disposable": False, "stored": second},
        {"scope": "many", "disposable": True, "stored": first, "disposal_methods": methods},
    ]
    with pytest.raises(RuntimeError, match="beside entries restored without"):
        store.restore_spell_creations("spell-other", reversed_mix)


def test_public_verb_refuses_mixed_declarations_both_ways(store: Creations, methods: List[str]) -> None:
    """The checked verb refuses a plain registration under a disposal-bearing key and the reverse."""
    log: List[str] = []
    store.register_many("spell-a", _Probe("a", log), methods)
    with pytest.raises(ValueError, match="one disposal declaration"):
        store.add_many_creations("spell-a", object())
    assert len(store._creations["spell-a"]) == 1

    store.add_many_creations("spell-b", object())
    with pytest.raises(ValueError, match="one disposal declaration"):
        store.add_many_creations("spell-b", _Probe("b", log), has_disposal_methods=True, disposal_methods=methods)
    assert len(store._creations["spell-b"]) == 1
    assert "spell-b" not in store._disposable_creations


def test_public_verb_refuses_a_singleton_slot_before_appending(store: Creations, methods: List[str]) -> None:
    """A many registration under a singleton key is refused and the slot is untouched."""
    singleton = object()
    store.add_creation("spell-s", singleton)

    with pytest.raises(ValueError, match="non-list slot"):
        store.add_many_creations("spell-s", object(), has_disposal_methods=True, disposal_methods=methods)
    assert store._creations["spell-s"] is singleton
    assert "spell-s" not in store._disposable_creations


def test_register_many_into_cleaned_store_disposes_and_raises(store: Creations, methods: List[str]) -> None:
    """A build that finishes after cleanup is refused through the hot verb and its methods run."""
    log: List[str] = []
    store.cleanup()

    with pytest.raises(RuntimeError, match="was cleaned while creation"):
        store.register_many("spell-many", _Probe("late", log), methods)

    assert log == ["late:close", "late:dispose"]


def test_register_many_into_cleaned_store_chains_the_disposal_failure(
        store: Creations, methods: List[str],
) -> None:
    """The refusal chains the disposal failure of the stranded object."""
    log: List[str] = []
    store.cleanup()

    with pytest.raises(RuntimeError) as caught:
        store.register_many("spell-many", _Raising("late", log), methods)

    assert isinstance(caught.value.__cause__, RuntimeError)
    assert isinstance(caught.value.__cause__.__cause__, ValueError)
    assert log == ["late:close", "late:dispose"]


def test_reset_for_pool_fast_path_ignores_plain_buckets_only(store: Creations, methods: List[str]) -> None:
    """A pool reset with a record present takes the disposing path; without one it only clears."""
    log: List[str] = []
    store.add_many_creations("spell-plain", object())
    store.reset_for_pool()
    assert store._creations == {}

    store.register_many("spell-many", _Probe("a", log), methods)
    store.reset_for_pool()
    assert log == ["a:close", "a:dispose"]
    assert store._creations == {} and store._disposable_creations == {}


def test_record_fields_are_borrowed_not_copied(store: Creations, methods: List[str]) -> None:
    """The record never copies: appending to the live bucket is visible through it, and vice versa."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    record = store._disposable_creations["spell-many"]
    extra = _Probe("b", log)

    store._creations["spell-many"].append(extra)
    assert record.entries[-1] is extra
    methods.append("close")
    assert record.methods == ["close", "dispose", "close"]
'''


COMPONENT_TEST = '''"""
Component tests of the many registration trim through real conjures (2026-10-01).

Scope:
    The registration line the emitters write for a disposal-bearing `many` step now calls
    `Creations.register_many(sid, instance, dm)`; these tests meld such roots through a real
    Conduit and a real SpellSpace (the solo family for a leaf without dependencies, the
    generalized family for a root with one) and check the store shape and the disposal
    order at scope exit.
"""

from typing import List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import ManyDisposalBucket
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _Log:
    """Shared disposal order log, one per test."""

    def __init__(self) -> None:
        self.entries: List[str] = []


class Leaf:
    """Disposal-bearing transient with no dependencies (solo family)."""

    log: Optional[_Log] = None

    def __init__(self) -> None:
        self.serial = 0

    def cleanup(self) -> None:
        """Record the disposal."""
        assert Leaf.log is not None
        Leaf.log.entries.append(f"leaf{self.serial}")


class Root:
    """Disposal-bearing transient that depends on a Leaf (generalized family)."""

    log: Optional[_Log] = None

    def __init__(self, leaf: Leaf) -> None:
        self.leaf = leaf
        self.serial = 0

    def cleanup(self) -> None:
        """Record the disposal."""
        assert Root.log is not None
        Root.log.entries.append(f"root{self.serial}")


@pytest.fixture(autouse=True)
def reset_aether_singleton() -> None:
    """Fresh Aether per test, as the other component conduit tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _spellbook_with_disposal() -> Spellbook:
    """A Spellbook whose configuration declares `cleanup` as the disposal method."""
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _bind_world() -> Tuple[Spellbook, str, str, _Log]:
    """Bind Leaf and Root as disposal-bearing many spells; return (spellbook, leaf_id, root_id, log)."""
    log = _Log()
    Leaf.log = log
    Root.log = log
    spellbook = _spellbook_with_disposal()
    leaf_id = spellbook.bind(spell=Leaf, existence=Existence.many, permissions="create")
    root_id = spellbook.bind(spell=Root, existence=Existence.many, permissions="create")
    return spellbook, leaf_id, root_id, log


def test_conduit_meld_registers_one_record_per_key_aliasing_the_bucket() -> None:
    """Two melds of the root register leaf and root into one record each, aliased to the live buckets."""
    spellbook, leaf_id, root_id, _log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=root_id)
        second = conduit.meld(spell_id=root_id)
        store = conduit._creations
        for spell_id, expected in ((root_id, [first, second]), (leaf_id, [first.leaf, second.leaf])):
            record = store._disposable_creations[spell_id]
            assert isinstance(record, ManyDisposalBucket)
            assert record.entries is store._creations[spell_id]
            assert record.entries == expected
            spell = spellbook.find_spell_by_id(spell_id)
            assert spell is not None
            assert record.methods is spell.disposal_method_names
            assert record.methods == ["cleanup"]
    finally:
        conduit.permanent_cleanup()


def test_conduit_cleanup_disposes_roots_then_leaves_newest_first() -> None:
    """Teardown walks the registry newest key first and each bucket newest entry first."""
    spellbook, _leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    first = conduit.meld(spell_id=root_id)
    second = conduit.meld(spell_id=root_id)
    first.serial, first.leaf.serial = 1, 1
    second.serial, second.leaf.serial = 2, 2

    conduit.permanent_cleanup()

    assert log.entries == ["root2", "root1", "leaf2", "leaf1"]


def test_solo_leaf_registers_through_the_hot_verb_and_is_disposed() -> None:
    """A leaf melded on its own (solo family) is registered and disposed like any many root."""
    spellbook, leaf_id, _root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    leaf_a = conduit.meld(spell_id=leaf_id)
    leaf_b = conduit.meld(spell_id=leaf_id)
    leaf_a.serial, leaf_b.serial = 1, 2
    record = conduit._creations._disposable_creations[leaf_id]
    assert record.entries == [leaf_a, leaf_b]

    conduit.permanent_cleanup()

    assert log.entries == ["leaf2", "leaf1"]


def test_spellspace_exit_disposes_the_space_store_only() -> None:
    """A space-scoped meld registers in the space store; its exit disposes those and nothing else."""
    spellbook, leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        outer = conduit.meld(spell_id=root_id)
        outer.serial, outer.leaf.serial = 9, 9
        with conduit.enter_spellspace() as space:
            inner = space.meld(spell_id=root_id)
            inner.serial, inner.leaf.serial = 1, 1
            record = space._creations._disposable_creations[root_id]
            assert record.entries is space._creations._creations[root_id]
            assert record.entries == [inner]
            assert conduit._creations._disposable_creations[root_id].entries == [outer]
        assert log.entries == ["root1", "leaf1"]
        assert leaf_id not in space._creations._creations
    finally:
        conduit.permanent_cleanup()
    assert log.entries == ["root1", "leaf1", "root9", "leaf9"]


def test_purge_one_transient_from_a_live_conduit_keeps_the_others() -> None:
    """Purging one instance of a many root disposes it alone and keeps the record over the rest."""
    spellbook, _leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=root_id)
        second = conduit.meld(spell_id=root_id)
        first.serial, first.leaf.serial = 1, 1
        second.serial, second.leaf.serial = 2, 2

        removed = conduit.purge(first, purge_all=False)

        assert removed == 1
        assert log.entries == ["root1"]
        record = conduit._creations._disposable_creations[root_id]
        assert record.entries == [second]
        assert record.entries is conduit._creations._creations[root_id]
    finally:
        conduit.permanent_cleanup()
    assert log.entries == ["root1", "root2", "leaf2", "leaf1"]
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--verb", choices=("a1", "a3"), default="a1")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    edit_creations(root, args.verb)
    edit_emitters(root)
    if not args.skip_tests:
        edit_tests(root)
        write_new(root, "tests/unit/melder/aether/conduit/creations/test_creations_many_registration_trim.py", UNIT_TEST)
        write_new(root, "tests/component/melder/aether/conduit/test_conduit_component_many_registration_trim.py", COMPONENT_TEST)
    print("S1 applied with verb", args.verb)
    return 0


if __name__ == "__main__":
    sys.exit(main())

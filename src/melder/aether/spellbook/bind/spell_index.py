import threading
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional, Dict, Tuple, ClassVar

# Melder Imports
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.helpers.ulid_factory import new_ulid
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook

class SpellIndex(Cleanable):
    """
    A stable SpellIndex identity that points to a mutable selected-spell id and
    holds the set of member spell ids that belong to this index.

    Design:
    This class solves the "mutable dictionary key" problem. It provides a
    stable, hashable SpellIndex identity via an immutable ULID, while tracking
    both a mutable selected-spell pointer (the SHA256 id of the active spell)
    and the set of member spell ids the index contains.

    - Hashing and equality are based *only* on the immutable ULID.
    - The selected-spell pointer can be safely updated (mutated) in a thread-safe
      manner without breaking its location in a dictionary.
    - The index can hold multiple member spell ids; `selected_spell_id` is the
      one currently active. The index organizes its member ids; the spell_id
      resolves. Lookup-map propagation to owning/contracted Spellbooks is the
      Spellbook's responsibility (the notch seam), not the index's.

    Contract:
        - Hash and equality derive ONLY from the immutable ULID.
        - `selected_spell_id` is mutable and thread-safe to update.
        - The index owns its member spell ids; it does NOT own lookup-map
          propagation to owning or contracted Spellbooks - that is the
          Spellbook's notch seam.
        - THE INDEX KEEPS ITS FIRST VERSION'S BINDING (2026-10-25;
          STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, the
          owner's rule: "if you want to use notch you gotta use the signature
          that was used originally"). `binding_signature` is the kind of
          spellframe the version it was built for was bound with (none, a
          string category, a Protocol) and the address that gives (frame key
          and binding key, case-insensitive). Every version of the index is
          bound the same way: `check_admits` refuses any other, and the
          Spellbook runs it before a version is staged onto the index
          (`bind_inactive`) or moved into it (`add_to_spell_index`). So an
          index's address never moves, a notch only changes which version
          serves it, and a renamed class or a new binding name is a new spell.

    Threading:
        The selected-spell pointer is updated under lock, so a repoint is safe
        while the index sits in a dictionary.

    Registration:
        MELDER KERNEL - guarded. Created by `Bind`; users receive indexes rather
        than constructing them.

    Subsystem Context:
        The stable identity spells are organized under. `Spell` is one version;
        the index organizes versions and selects one of them. Version HISTORY
        belongs to MutationResearch, not here.

    System Context:
        The design note names the real problem this solves: the MUTABLE
        DICTIONARY KEY. Identity must stay stable so the object keeps its place
        in every map that holds it, while the thing it POINTS AT must be free to
        change. Hashing on the immutable ULID and mutating only the pointer is
        what makes a notch possible at all - repointing an index cannot corrupt
        the maps it lives in.
        That split ripples outward. Contracts carry BOTH a `Detail` (a captured
        spell_id, the answer at grant time) and an `IndexDetail` (a subscription
        to this index, following the head), so a notch updates every borrower
        without renegotiating a single contract. The crystallizer records index
        MEMBERSHIP as its own twin (`SpellIndexCrystal`) for the same reason -
        membership is the index's own truth, distinct from any one spell's custody.
        The explicit non-ownership of lookup-map propagation is the boundary
        that keeps this class small: the index organizes ids, the spell_id
        resolves, and the Spellbook is what republishes lookups on a notch.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The stable index identity (immutable ULID) pointing at a mutable
        selected spell. Hash/equality use only the ULID, so a notch can repoint the active
        member without breaking any map. Version history belongs to MutationResearch.
    """
    __slots__ = (
        "_id",          # The immutable ULID. Used for hashing and equality.
        "_selected_spell_id",  # The active spell's id (a SHA256).
        "_lock",        # RLock for thread-safe reads/writes.
        "_cleaned",     # Flag for Cleanable interface.
        "_spells_in_index",    # Set of all member spell ids in this index.
        "_binding_signature",  # (kind, frame_key, binding_key) of the first version's binding, or None.
        "_binding_text",       # That binding as a sentence for refusals, or None.
    )

    def __init__(
            self,
            initial_id: str,
            *,
            binding_signature: Optional[Tuple[str, str, str]] = None,
            binding_text: Optional[str] = None,
    ):
        """
        Initialize the SpellIndex with its permanent identity and initial member.

        Purpose:
            Provide a stable, hashable SpellIndex identity with a mutable
            selected-spell pointer, the set of member spell ids and the binding
            every version of the index is bound with.

        Contract:
            - The ULID identity never changes.
            - The selected-spell pointer is mutable and guarded by the lock.
            - The member set starts with the initial spell id.
            - The binding is written once here and never changes. Melder builds
              every index through `for_binding`, which computes both binding
              values from the first version's spellframe, name and binding
              name; an index built without them (`SpellIndex(initial_id)`, as
              unit tests build them) records no binding and `check_admits`
              refuses every version on it.

        Args:
            initial_id (str):
                The SHA256 spell id this index initially selects and contains.
            binding_signature (Optional[Tuple[str, str, str]]):
                `(kind, frame_key, binding_key)` of the first version's binding
                (`signature_of`), or None.
            binding_text (Optional[str]):
                The same binding as the sentence refusals quote
                (`_describe_binding`), or None. Given with `binding_signature`.

        Threading:
            - Initializes the internal RLock used for all mutations. The two
              binding values are immutable and read without the lock.

        Returns:
            None.
        """
        super().__init__()
        # The permanent, hashable identity for this key.
        self._id: str = new_ulid()
        self._lock: threading.RLock = threading.RLock()
        # The active spell pointer, which can be updated.
        self._selected_spell_id: str = initial_id
        # The set of member spell ids this index contains.
        self._spells_in_index: set = {initial_id}
        # The binding of the version this index was built for: every version of
        # the index is bound the same way (`check_admits`). Write-once.
        self._binding_signature: Optional[Tuple[str, str, str]] = binding_signature
        self._binding_text: Optional[str] = binding_text

    @classmethod
    def for_binding(
            cls,
            initial_id: str,
            *,
            spellframe: Any,
            spell_name: str,
            binding_name: Optional[str],
    ) -> SpellIndex:
        """
        Build the index for a version's binding, the index's first version.

        Purpose:
            The one way Melder builds an index (`Bind._bind_logic` for every
            Spell it creates; `Spellbook._apply_remove_from_index` for a
            version split off into an index of its own): the index records
            the binding of its first version, and every later version must
            be bound the same way.

        Contract:
            - The index selects and contains `initial_id`, as the
              constructor's.
            - `binding_signature` is `signature_of(...)` of the three values
              and the refusal text describes them (`_describe_binding`).
            - The values are taken as Bind accepted them: `spellframe` is
              None, a string or a Protocol class (`Bind._classify_spellframe`
              refuses anything else before an index is built).

        Args:
            initial_id (str): The first version's spell_id.
            spellframe (Any): The first version's spellframe - None, a string category or a Protocol class.
            spell_name (str): The first version's name (the class or function name Bind took).
            binding_name (Optional[str]): The first version's binding name, as passed (None or "" for the default).

        Returns:
            SpellIndex: A new index keeping that binding.
        """
        return cls(
            initial_id,
            binding_signature=SpellIndex.signature_of(
                spellframe=spellframe, spell_name=spell_name, binding_name=binding_name,
            ),
            binding_text=SpellIndex._describe_binding(
                spellframe=spellframe, spell_name=spell_name, binding_name=binding_name,
            ),
        )

    @staticmethod
    def signature_of(
            *,
            spellframe: Any,
            spell_name: str,
            binding_name: Optional[str],
    ) -> Tuple[str, str, str]:
        """
        Return the binding signature of a version bound with these values.

        Purpose:
            The comparable form of a binding: what kind of spellframe it was
            bound with and the address that gives. Two versions belong on one
            index exactly when their signatures are equal.

        Contract:
            - The kind is a `SpellframeKind` value: "none" for no spellframe,
              "category" for a string, "contract" for anything else - the
              Protocol class Bind accepted (`Bind._classify_spellframe`).
            - The address is `SpellInputUtils.make_spell_key_from_parts(...)`,
              the `(frame_key, binding_key)` `Spell._key` holds and the frame
              claim is keyed by: the spellframe's name, or the spell's own
              name when bound bare, and the binding name, both lowercased; an
              empty binding name is the default binding.
            - So the kind keeps a string category spelled like a bare class's
              name apart from that class, and two Protocols of one name give
              one signature, as they give one address.
            - Pure: reads its arguments, changes nothing.

        Args:
            spellframe (Any): None, a string category or a Protocol class.
            spell_name (str): The version's name (the address label when bound bare).
            binding_name (Optional[str]): The binding name, or None for the default.

        Returns:
            Tuple[str, str, str]: `(kind, frame_key, binding_key)`.

        Raises:
            TypeError: Propagated from the key normalizers for a value they cannot read.
        """
        if spellframe is None:
            kind = SpellframeKind.none
        elif isinstance(spellframe, str):
            kind = SpellframeKind.category
        else:
            kind = SpellframeKind.contract
        frame_key, binding_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe, spell_name=spell_name, binding_name=binding_name,
        )
        return kind.value, frame_key, binding_key

    @staticmethod
    def _describe_binding(
            *,
            spellframe: Any,
            spell_name: str,
            binding_name: Optional[str],
    ) -> str:
        """
        Internal

        Describe a binding as the sentence a refusal quotes.

        Contract:
            - "the Protocol spellframe Greeter", "the string spellframe
              'Reports'" or "no spellframe (bare, addressed by its own name
              'Report')", then " and binding_name '<name>'" or " and the
              default binding name" - the values as the caller passed them,
              so the text names what to pass again.
            - Pure.

        Args:
            spellframe (Any): None, a string category or a Protocol class.
            spell_name (str): The version's name.
            binding_name (Optional[str]): The binding name, or None for the default.

        Returns:
            str: The description.
        """
        if spellframe is None:
            frame_text = f"no spellframe (bare, addressed by its own name '{spell_name}')"
        elif isinstance(spellframe, str):
            frame_text = f"the string spellframe '{spellframe}'"
        else:
            frame_text = f"the Protocol spellframe {spellframe.__name__}"
        name_text = f"binding_name '{binding_name}'" if binding_name else "the default binding name"
        return f"{frame_text} and {name_text}"

    # ------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Release the member set and pointer and mark this index as cleaned.

        Contract:
            - Idempotent and lock-guarded.
            - Clears and drops the member set and the selected-spell pointer.
            - Keeps the binding (`binding_signature`), like the id: immutable
              values that a reader racing this cleanup must never find deleted.
            - Leaves future callers to fail through `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._spells_in_index.clear()
            del self._spells_in_index
            del self._selected_spell_id

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------
    @property
    def selected_spell_id(self) -> str:
        """
        Return the active spell's id for this SpellIndex.

        Returns:
            str: The active spell's id.

        Contract:
            - Returns the live selected-spell pointer, not a historical value.
            - Lock-free read: the pointer is one attribute holding one string
              reference, so a reader observes either the previous or the new
              id, never a torn value. `update(...)` still serializes writers
              under the instance lock.

        Threading:
            - Safe on free-threaded builds; attribute reference loads are
              atomic. This property is the hottest spell_id read in the
              compiler phases (thousands of reads per conjure), and the
              per-read RLock acquire/release dominated its cost on nogil.
        """
        return self._selected_spell_id

    def update(self, new_id: str) -> None:
        """
        Set the active spell id and add it to the index's member set.

        This is a pure index-side repoint: it changes which member is active
        and records `new_id` in the member set, and nothing else. Owning and
        contracted Spellbook lookup-map propagation is the Spellbook's
        responsibility (the notch seam), not the index's. Thread-safe; does not
        affect the object's hash or its dictionary location.

        Args:
            new_id (str): The new SHA256 spell id to select and add as a member.

        Contract:
            - SELECTS a new current spell id AND adds it to the member set, so
              selection always implies membership.
            - DOES NOT RETIRE THE PREVIOUS ID. The superseded version stays a
              MEMBER - parked in its Book - so the member set holds every version
              and the selected id names only the selected one. A lookup by spell_id
              (`Spellbook.find_spell_by_spell_id`) answers the superseded spell
              itself, never the head; the head is what `selected_spell_id` and a
              lookup by index id name.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._selected_spell_id = new_id
            self._spells_in_index.add(new_id)

    def add_member(self, spell_id: str) -> None:
        """
        Add `spell_id` to this index's member set without selecting it.

        Used to stage an inactive candidate (`Spellbook.bind_inactive`): the id
        becomes a member visible to `spells_in_index()` / `has_spell()`, but the
        active `selected_spell_id` is left unchanged. Promotion to active happens
        later via `notch`.

        Args:
            spell_id (str): The candidate member spell id to record.

        Contract:
            - Adds to the index WITHOUT changing the selected id, so it grows the
              version set without promoting anything.
            - Set semantics: re-adding an existing id is a silent no-op.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._spells_in_index.add(spell_id)

    def remove_member(self, spell_id: str) -> None:
        """
        Remove `spell_id` from this index's member set.

        Idempotent; does not touch the selected pointer. Used when a member is
        moved out of this index (`add_to_spell_index`).

        Args:
            spell_id (str): The member spell id to remove.

        Contract:
            - Uses `discard`, so removing an id that was never a member is a SILENT
              NO-OP rather than an error. Absence of an exception is not proof the
              id was present.
            - CAN REMOVE THE CURRENTLY SELECTED ID. Nothing here re-points the
              selection, so afterwards `selected_spell_id` may name an id that is no
              longer a member. Callers retiring the head must select a new one.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._spells_in_index.discard(spell_id)

    def spells_in_index(self) -> set:
        """
        Return a snapshot of every member spell id in this index.

        Returns:
            set: A detached copy of the member spell ids.

        Contract:
            - Includes the initial spell id and every id added via `update(...)`.
        """
        self.check_cleaned()
        with self._lock:
            return set(self._spells_in_index)

    def has_spell(self, spell_id: str) -> bool:
        """
        Return whether `spell_id` is a member of this index.

        Args:
            spell_id (str): The spell id to check.

        Contract:
            - Tests MEMBERSHIP OF THE INDEX, not equality with the selected id, so a
              superseded or parked version still answers True. A membership test only:
              a spell_id names its own spell (`Spellbook.find_spell_by_spell_id`), not
              the index's selected spell.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read. The cleaned check is repeated under
            that lock, the one `cleanup()` marks the index cleaned and deletes the
            member set under, so a cleanup racing this call raises the documented
            RuntimeError, never AttributeError (0.2.8230).

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`, before and after taking the lock.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if `spell_id` is in the member set, False otherwise.
        """
        self.check_cleaned()
        with self._lock:
            # Re-check under the lock: a cleanup between the unlocked check and the acquire has
            # already deleted the member set.
            self.check_cleaned()
            return spell_id in self._spells_in_index

    def _has_spell_unless_cleaned(self, spell_id: str) -> bool:
        """
        Internal

        Return whether `spell_id` is a member of this index, answering False once
        the index is cleaned.

        Purpose:
            Membership probe for walks over indexes the caller neither owns nor
            locks - a contracted map, a contract detail - which can reach an index
            after its owner cleaned it. A cleaned index owns nothing, so for such a
            walk "not a member" is the truthful answer, where `has_spell` raises.

        Contract:
            - Same membership semantics as `has_spell` (every member
              spell id, not only the selected id) while the index is live.
            - Never raises for a cleaned index; returns False.

        Threading:
            Reads the cleaned flag and the member set under `self._lock`, the lock
            `cleanup` holds while it marks the index cleaned and deletes the
            member set, so a concurrent cleanup cannot tear the answer.

        Args:
            spell_id (str): The spell id to check.

        Returns:
            bool: True if this live index's member set contains `spell_id`;
            False otherwise, and False once the index is cleaned.
        """
        with self._lock:
            if self._cleaned:
                return False
            return spell_id in self._spells_in_index

    def _is_selected_unless_cleaned(self, spell_id: str) -> bool:
        """
        Internal

        Return whether this index currently selects `spell_id`, answering False once the index is cleaned.

        Purpose:
            Selected-version probe for readers that neither own nor lock the index - `ReleaseManagedSpell`'s cold
            resolver prefers the pool of the version its index selects (STORY-2026-10-15-release_managed_spell).
            `selected_spell_id` is a lock-free read of a field `cleanup()` deletes, so such a reader racing a
            cleanup would meet an AttributeError there.

        Contract:
            - Tests SELECTION, not membership: a parked member of the index answers False.
            - Never raises for a cleaned index; returns False.
            - Pure read: changes nothing.

        Threading:
            Reads the cleaned flag and the selected id under `self._lock`, the lock `cleanup()` marks the index
            cleaned and deletes the selected id under, and `update()` repoints it under.

        Args:
            spell_id (str): The spell_id to test.

        Returns:
            bool: True if this live index selects `spell_id`; False otherwise, and False once the index is cleaned.
        """
        with self._lock:
            if self._cleaned:
                return False
            return self._selected_spell_id == spell_id

    def is_empty(self) -> bool:
        """
        Return whether this index has no members.

        O(1): tests the live member set directly without copying it.

        Contract:
            - Reports that the MEMBER SET is empty. It says nothing about the selected
              id, which member removal does not clear - an index can be empty and
              still carry a stale selected id.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if the member set is empty.
        """
        self.check_cleaned()
        with self._lock:
            return not self._spells_in_index

    def is_sole_member(self, spell_id: str) -> bool:
        """
        Return whether `spell_id` is this index's only member.

        O(1): a length test plus a membership test on the live set; no copy and
        no set construction (unlike `spells_in_index() == {spell_id}`).

        Args:
            spell_id (str): The spell id to test as the sole member.

        Contract:
            - True only when the member set has exactly one entry AND that entry is the
              supplied id; a different lone member returns False rather than raising.
            - The usual "is this the last version" test before a destructive step.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True iff the member set is exactly {spell_id}.
        """
        self.check_cleaned()
        with self._lock:
            members = self._spells_in_index
            return len(members) == 1 and spell_id in members

    @property
    def binding_signature(self) -> Optional[Tuple[str, str, str]]:
        """
        Return the binding every version of this index is bound with.

        Purpose:
            The binding of the version the index was built for: the kind of
            spellframe (none, a string category, a Protocol) and the address it
            gives. Every version of the index is bound the same way, so this is
            also the address the index serves.

        Contract:
            - `(kind, frame_key, binding_key)`, as `signature_of` builds it -
              for example ("contract", "greeter", "english") for a version bound
              under the Protocol `Greeter` with binding name "English".
            - None for an index built without a binding (not by Melder).
            - Never changes; kept after cleanup, like `id`.

        Threading:
            Lock-free read of a write-once slot; safe from any thread.

        Returns:
            Optional[Tuple[str, str, str]]: The signature, or None.
        """
        return self._binding_signature

    def check_admits(self, spell: Spell, *, verb: str) -> None:
        """
        Refuse a version bound another way than this index's versions.

        Purpose:
            The check that keeps every version of an index bound the way its
            first version was (the owner's rule, 2026-10-25). The Spellbook
            runs it before staging a version onto the index (`bind_inactive`)
            and before moving one into it (`add_to_spell_index`), so a refusal
            leaves nothing registered or moved.

        Contract:
            - Compares `signature_of(...)` of the version's `spellframe`,
              `spell_name` and `binding_name` with `binding_signature`. Equal
              admits - the case of the names aside, since the address is
              case-insensitive. Reads those three fields and `spell_id`, and
              nothing else; changes nothing.
            - A different kind of spellframe is another binding even at the
              same address, and a renamed class bound bare is another address:
              each is a new spell, to be bound on its own.

        Args:
            spell (Spell): The version to stage or move.
            verb (str): The calling verb, which opens the refusal message.

        Returns:
            None.

        Raises:
            ValueError: "<verb> refused: SpellIndex <id> keeps the binding its
                first version was bound with - <this index's binding> - and
                '<name>' (spell_id <id>) is bound with <the version's>. ...",
                with the remedy.
            RuntimeError: If the index records no binding (built without
                `for_binding` - a Melder bug), or has been cleaned.

        Threading:
            The binding is read without the lock; `check_cleaned()` guards the
            call.
        """
        self.check_cleaned()
        signature = self._binding_signature
        if signature is None:
            raise RuntimeError(
                f"{verb} refused: SpellIndex {self._id} records no binding, so it admits no version. Melder builds "
                "every index with the binding of its first version (SpellIndex.for_binding); an index built "
                "without one is a Melder bug - please report it with this message."
            )
        candidate = SpellIndex.signature_of(
            spellframe=spell.spellframe, spell_name=spell.spell_name, binding_name=spell.binding_name,
        )
        if candidate == signature:
            return
        version_text = SpellIndex._describe_binding(
            spellframe=spell.spellframe, spell_name=spell.spell_name, binding_name=spell.binding_name,
        )
        raise ValueError(
            f"{verb} refused: SpellIndex {self._id} keeps the binding its first version was bound with - "
            f"{self._binding_text} - and '{spell.spell_name}' (spell_id {spell.spell_id}) is bound with "
            f"{version_text}. Every version of an index is bound the same way, so a notch never moves its "
            "address: stage an edited class with the index's spellframe and binding_name. A renamed class or a "
            "new binding name is a new spell: bind it on its own."
        )

    @property
    def id(self) -> str:
        """
        Return the immutable ULID that defines this index's stable identity.

        Contract:
            - This value never changes for the lifetime of the index.
            - Hashing and equality are derived from this id, not from the
              mutable selected-spell pointer.

        Returns:
            str: The immutable ULID. Hash and equality derive from this alone, which
                is what lets the selected spell move without breaking dictionary placement.
        """
        return self._id

    # ------------------------------------------------------------
    # Dict-safety (Hashing and Equality)
    # ------------------------------------------------------------
    def __hash__(self) -> int:
        """
        Hash this index by immutable SpellIndex identity only.

        This ensures the hash is stable, even if _selected_spell_id changes,
        making it safe for use as a dictionary key.
        Contract:
            - Hashes on index IDENTITY ONLY, never on contents, so the hash is stable
              while membership changes. That is what allows a live index to be a dict
              key while its member set changes.
            - DELIBERATELY NOT `check_cleaned()` GUARDED, so a cleaned index stays
              hashable and can still be removed from the collections holding it.

        Threading:
            Reads a write-once slot without taking the lock; safe from any thread.

        Lifecycle / Cleanup:
            Remains valid after cleanup, by design.

        """
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        """
        Compare two `SpellIndex` objects by immutable SpellIndex identity only.

        This guarantees that key equality is stable and not affected
        by selected-spell changes.
        Contract:
            - Compares index IDENTITY ONLY. Two indexes with identical membership are
              NOT equal, and an index stays equal to itself across every mutation.
            - Returns False for non-`SpellIndex` operands rather than raising.
            - Not `check_cleaned()` guarded, matching `__hash__` so the pair stays
              consistent for collection removal after cleanup.

        Threading:
            Reads a write-once slot without taking the lock; safe from any thread.

        Lifecycle / Cleanup:
            Remains valid after cleanup, by design.

        """
        return isinstance(other, SpellIndex) and self._id == other._id

    # ------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a developer-facing snapshot of identity and selected spell.
        Contract:
            - GUARDED BY `check_cleaned()` AND TAKES THE LOCK, which is unusual for a
              repr: printing or logging a CLEANED index RAISES rather than degrading
              to a placeholder. Take care with debugger watches and log statements
              that may run after teardown.
            - Shows identity and the currently selected id, not the membership set.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        """
        self.check_cleaned()
        with self._lock:
            return f"<SpellIndex id={self._id} current={self._selected_spell_id}>"

    def __enter__(self) -> "SpellIndex":
        """
        Acquire the internal lock and return this index.

        Contract:
            - Intended for rare manual critical sections around multiple reads
              on the same `SpellIndex`.
            - Must be paired with `__exit__` to release the lock.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Release the internal lock acquired by `__enter__`.
        Contract:
            - Releases unconditionally, including when the block raised. Exception
              arguments are accepted and IGNORED, and the falsy return means no
              exception is suppressed here.
            - Exactly one release per `__enter__`; the lock is reentrant, so nested
              `with` blocks are legal and each level must exit.

        Threading:
            Releases the index lock acquired by `__enter__`.

        Lifecycle / Cleanup:
            Performs no cleaned-state check - it is purely the unlock half.

        Raises:
            RuntimeError: If called without a matching `__enter__` on this thread.

        """
        self._lock.release()

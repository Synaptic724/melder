import threading
from typing import Dict, Optional, Tuple


class LookupContainer:
    """
    Frame-wide, thread-safe registry of ACTIVE binding-signature lookups.

    Purpose:
        Hold, for one `AethericFrame`, the mapping from each active binding
        signature `(frame_key, bind_key)` to the `spell_id` currently serving
        it, together with the inverse `spell_id -> signature` index so an entry
        can be located and removed by `spell_id` in O(1). This is the
        centralized, framewide replacement for per-spellbook binding-signature
        uniqueness: at most one active spell per signature per frame.

    Contract:
        - Stores ACTIVE signatures only. A spell going inactive (notch/disable)
          or a spellbook cleaning up must release its keys; a missing key
          means "no active spell holds that signature in this frame".
        - `claim` enforces one active spell per signature: re-claiming a key
          for a DIFFERENT spell_id raises and leaves state unchanged. Claiming
          for the SAME spell_id is idempotent.
        - The forward map (`signature -> spell_id`) and the reverse map
          (`spell_id -> signature`) are maintained together by every mutating
          method, so the two never diverge. The relationship is 1:1: the
          binding signature is folded into the spell_id fingerprint, so a given
          spell_id occupies exactly one signature.
        - Resolution (signature -> SpellIndex -> Spell) is NOT this object's
          job; this is the uniqueness/claim surface only. The value is the
          active `spell_id`, which re-points on notch.

    Threading:
        - One internal `threading.Lock` serializes every read and write, so the
          forward and reverse maps cannot be observed mid-update and callers
          never take the owning frame's lock for lookup operations.
        - The lock is non-reentrant by design: no method calls another method
          while holding it.

    Lifecycle:
        - `cleanup` clears both maps and drops the lock. It is idempotent;
          after cleanup the container exposes no live surface.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Frame-wide, thread-safe registry of ACTIVE binding-signature lookups. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = ("_lookup", "_reverse", "_lock", "_cleaned")

    def __init__(self) -> None:
        """
        Initialize an empty active-signature lookup with its own lock.

        Contract:
            - Starts empty and uncleaned; owns its `threading.Lock`.
            - Forward (`signature -> spell_id`) and reverse (`spell_id ->
              signature`) maps both start empty.

        Returns:
            None.
        """
        self._lookup: Dict[Tuple[str, str], str] = {}
        self._reverse: Dict[str, Tuple[str, str]] = {}
        self._lock: threading.Lock = threading.Lock()
        self._cleaned: bool = False

    def claim(self, key: Tuple[str, str], spell_id: str) -> None:
        """
        Claim a binding signature for `spell_id` frame-wide.

        Contract:
            - Atomic check-and-set under the lock.
            - Succeeds when `key` is unclaimed or already held by the SAME
              spell_id (idempotent).
            - Raises without mutating state when `key` is already held by a
              DIFFERENT spell_id.
            - Maintains both the forward and reverse maps.

        Args:
            key: The binding signature `(frame_key, bind_key)`.
            spell_id: The spell_id taking the active slot for `key`.

        Raises:
            RuntimeError: If `key` is already active for a different spell_id
                in this frame.

        Returns:
            None.
        """
        with self._lock:
            existing = self._lookup.get(key)
            if existing is not None and existing != spell_id:
                frame_key, bind_key = key
                raise RuntimeError(
                    "Binding signature already active in this frame: "
                    f"frame_key='{frame_key}', binding_name='{bind_key}' is held by "
                    f"spell_id='{existing}'. There is one active spell per signature "
                    "per frame; use a distinct spellframe or binding_name, or notch "
                    "the existing index instead of binding a second spell onto it."
                )
            self._lookup[key] = spell_id
            self._reverse[spell_id] = key

    def update(self, key: Tuple[str, str], spell_id: str) -> None:
        """
        Re-point an active signature to a new spell_id (notch promotion).

        Contract:
            - Unconditionally sets `key -> spell_id` under the lock. Intended
              for notch, where the index keeps the signature but swaps the
              active spell behind it.
            - Maintains the reverse map: the previously active spell_id for
              `key` (when present) is dropped before the new one is recorded.

        Args:
            key: The binding signature `(frame_key, bind_key)`.
            spell_id: The new active spell_id for `key`.

        Returns:
            None.
        """
        with self._lock:
            previous = self._lookup.get(key)
            if previous is not None:
                self._reverse.pop(previous, None)
            self._lookup[key] = spell_id
            self._reverse[spell_id] = key

    def release(self, key: Tuple[str, str]) -> None:
        """
        Remove a signature from the active lookup (deactivate / disable / cleanup).

        Contract:
            - Idempotent: releasing an absent key is a no-op.
            - Maintains both maps: the released signature's spell_id is dropped
              from the reverse index.

        Args:
            key: The binding signature `(frame_key, bind_key)` to release.

        Returns:
            None.
        """
        with self._lock:
            spell_id = self._lookup.pop(key, None)
            if spell_id is not None:
                self._reverse.pop(spell_id, None)

    def release_by_spell_id(self, spell_id: str) -> None:
        """
        Remove a signature from the active lookup, located by its spell_id.

        Contract:
            - Idempotent: releasing an unknown spell_id is a no-op.
            - O(1): the signature is found through the reverse index rather
              than scanning the forward map.
            - Maintains both maps.

        Args:
            spell_id: The active spell_id whose signature should be released.

        Returns:
            None.
        """
        with self._lock:
            key = self._reverse.pop(spell_id, None)
            if key is not None:
                self._lookup.pop(key, None)

    def get(self, key: Tuple[str, str]) -> Optional[str]:
        """
        Return the active spell_id for a signature, or None when unclaimed.

        Args:
            key: The binding signature `(frame_key, bind_key)`.

        Returns:
            Optional[str]: The active spell_id, or None when no active spell
                holds `key` in this frame.
        """
        with self._lock:
            return self._lookup.get(key)

    def get_sig_by_spell_id(self, spell_id: str) -> Optional[Tuple[str, str]]:
        """
        Return the signature an active spell_id holds, or None when unknown.

        Contract:
            - O(1) reverse lookup; the counterpart to `get`.

        Args:
            spell_id: The active spell_id to resolve.

        Returns:
            Optional[Tuple[str, str]]: The `(frame_key, bind_key)` signature the
                spell_id holds, or None when it holds no active signature in
                this frame.
        """
        with self._lock:
            return self._reverse.get(spell_id)

    def contains(self, key: Tuple[str, str]) -> bool:
        """
        Report whether a signature is currently active in this frame.

        Args:
            key: The binding signature `(frame_key, bind_key)`.

        Returns:
            bool: True when an active spell holds `key`, else False.
        """
        with self._lock:
            return key in self._lookup

    def contains_spell_id(self, spell_id: str) -> bool:
        """
        Report whether a spell_id currently holds an active signature.

        Args:
            spell_id: The spell_id to test.

        Returns:
            bool: True when `spell_id` holds an active signature, else False.
        """
        with self._lock:
            return spell_id in self._reverse

    def cleanup(self) -> None:
        """
        Clear both maps and drop the lock.

        Contract:
            - Idempotent. Teardown-only: not intended to race active lookup
              operations. After cleanup the container holds no live surface.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._lookup.clear()
            self._reverse.clear()
        del self._lookup
        del self._reverse
        del self._lock

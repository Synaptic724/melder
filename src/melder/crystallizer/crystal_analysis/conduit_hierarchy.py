from collections import deque
from typing import Dict, List, Optional, Tuple


class ConduitHierarchy:
    """Validate recorded conduit structure and expand unnamed ancestor values.

    Purpose:
        Give preflight and restore one interpretation of named lesser ancestry.
        The record remains passive; this analysis never reads a live Conduit.

    Contract:
        Input payloads are borrowed and never changed. Returned support rows are
        value-only lesser descriptions. Shared ancestors build once; incompatible
        claims for one identity refuse instead of selecting an arbitrary parent.
        Legacy rows without a role remain normal roots. No application state is read.

    Threading / Lifecycle:
        Stateless static operations; owns no resources, locks or runtime references.
        Callers own the returned value maps and must not mutate input during analysis.

    Registration:
        Internal Crystallizer analysis helper; never user-bound or constructed.
    """

    @staticmethod
    def configuration(payload: Dict[str, object]) -> Dict[str, object]:
        """Read the borrowed structural mapping, with an empty legacy-root default.

        Args:
            payload: One detached conduit record.
        Returns:
            Dict[str, object]: The borrowed mapping; callers must not mutate it.
        Raises:
            ValueError: Configuration has a non-mapping shape.
        """
        if not isinstance(payload, dict):
            raise ValueError("A conduit structural record must be a mapping.")
        configuration = payload.get("configuration_payload", {})
        if not isinstance(configuration, dict):
            raise ValueError("Conduit configuration_payload must be a mapping.")
        return configuration

    @staticmethod
    def role(payload: Dict[str, object]) -> str:
        """Return normal/lesser role, rejecting pooled or cleaned structural records.

        Args:
            payload: One detached conduit record.
        Returns:
            str: The recorded role; legacy absence means normal.
        Raises:
            ValueError: Role cannot describe an active restorable scope.
        """
        role = ConduitHierarchy.configuration(payload).get("conduit_state", "normal")
        if not isinstance(role, str) or role not in ("normal", "lesser"):
            raise ValueError(f"Conduit role {role!r} is not an active normal or lesser scope.")
        return role

    @staticmethod
    def _identity(value: object, label: str) -> str:
        """Validate a structural edge without coercing absent or malformed identities.

        Args:
            value: Candidate record-local identity.
            label: Edge description included in the error.
        Returns:
            str: The unchanged nonempty identity.
        Raises:
            ValueError: The edge is not a nonempty string.
        """
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label} must be a nonempty recorded identity.")
        return value

    @staticmethod
    def build(
            conduits: Dict[str, Dict[str, object]],
            books: Dict[str, Dict[str, object]],
    ) -> Tuple[Dict[str, Dict[str, object]], Dict[str, List[str]]]:
        """Expand surviving named records and produce parent-first ids per Book.

        Contract:
            Expansion happens after journal folding, so removed named carriers
            cannot leave orphan support rows. Names are unique within their Book's
            frame, and each lesser stays within one recorded root and Book.
        Args:
            conduits: Surviving explicit root/named-scope payloads keyed by id.
            books: Recorded Book payloads, used for ownership and frame identity.
        Returns:
            Tuple: Expanded conduit rows and ordered ids grouped by Book.
        Raises:
            ValueError: Malformed ancestry, ownership, name or graph structure.
        """
        rows = dict(conduits)
        for conduit_id, payload in conduits.items():
            if ConduitHierarchy.role(payload) == "lesser":
                ConduitHierarchy._expand_lineage(conduit_id, payload, rows, books)
        return rows, ConduitHierarchy._order_rows(rows, books)

    @staticmethod
    def _expand_lineage(
            conduit_id: str,
            payload: Dict[str, object],
            rows: Dict[str, Dict[str, object]],
            books: Dict[str, Dict[str, object]],
    ) -> None:
        """Validate one named carrier's ordered ancestry and merge unnamed support.

        Args:
            conduit_id: Named carrier's recorded identity.
            payload: Borrowed carrier values.
            rows: Output map into which compatible support rows are merged.
            books: Recorded owning Book identities.
        Returns:
            None.
        Raises:
            ValueError: The carrier or one ancestry edge is inconsistent.
        """
        configuration = ConduitHierarchy.configuration(payload)
        book_id = ConduitHierarchy._identity(payload.get("spellbook_id"), "Lesser spellbook_id")
        if book_id not in books:
            raise ValueError(f"Lesser {conduit_id!r} depends on missing Spellbook {book_id!r}.")
        name = payload.get("conduit_name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Recorded lesser {conduit_id!r} must have a nonempty name.")
        if payload.get("policy_name", "default") != "default":
            raise ValueError(f"Lesser {conduit_id!r} must use default policy; only normal roots may change policy.")
        root_id = ConduitHierarchy._identity(configuration.get("root_conduit_id"), "Lesser root_conduit_id")
        parent_id = ConduitHierarchy._identity(configuration.get("parent_conduit_id"), "Lesser parent_conduit_id")
        lineage = configuration.get("lineage_ancestors")
        if not isinstance(lineage, list) or not lineage:
            raise ValueError(f"Lesser {conduit_id!r} requires ordered lineage_ancestors.")
        previous_id: Optional[str] = None
        seen = {conduit_id}
        for position, ancestor in enumerate(lineage):
            if not isinstance(ancestor, dict):
                raise ValueError(f"Lesser {conduit_id!r} contains a non-mapping ancestor.")
            ancestor_id = ConduitHierarchy._identity(ancestor.get("conduit_id"), "Ancestor conduit_id")
            if ancestor_id in seen:
                raise ValueError(f"Lesser {conduit_id!r} has cyclic/repeated ancestor {ancestor_id!r}.")
            if ancestor.get("parent_conduit_id") != previous_id:
                raise ValueError(f"Ancestor {ancestor_id!r} has an inconsistent parent edge.")
            if position == 0 and ancestor_id != root_id:
                raise ValueError(f"Lesser {conduit_id!r} lineage does not start at its recorded root.")
            seen.add(ancestor_id)
            ConduitHierarchy._merge_ancestor(ancestor, rows, book_id, root_id, bool(payload.get("dynamic", True)))
            previous_id = ancestor_id
        if previous_id != parent_id:
            raise ValueError(f"Lesser {conduit_id!r} lineage does not end at its immediate parent.")

    @staticmethod
    def _merge_ancestor(
            ancestor: Dict[str, object],
            rows: Dict[str, Dict[str, object]],
            book_id: str,
            root_id: str,
            dynamic: bool,
    ) -> None:
        """Require explicit named/root ancestors and coalesce anonymous support by identity.

        Args:
            ancestor: Validated ancestor row from one named carrier.
            rows: Mutable expanded output map.
            book_id: Owning Book shared by this hierarchy.
            root_id: The hierarchy's normal root.
            dynamic: Recorded mode inherited by supporting lesser scopes.
        Returns:
            None.
        Raises:
            ValueError: An ancestor is missing or conflicts with another carrier.
        """
        ancestor_id = ConduitHierarchy._identity(ancestor.get("conduit_id"), "Ancestor conduit_id")
        ancestor_name = ancestor.get("conduit_name")
        parent_id = ancestor.get("parent_conduit_id")
        is_root = ancestor_id == root_id
        expected_role = "normal" if is_root else "lesser"
        if not is_root and ancestor.get("policy_name", "default") != "default":
            raise ValueError(f"Lesser ancestor {ancestor_id!r} must use default policy.")
        if ancestor_name is not None and (not isinstance(ancestor_name, str) or not ancestor_name):
            raise ValueError(f"Ancestor {ancestor_id!r} has an invalid name.")
        existing = rows.get(ancestor_id)
        if existing is None:
            if is_root or ancestor_name is not None:
                raise ValueError(f"Required named/root ancestor {ancestor_id!r} has no recorded twin.")
            rows[ancestor_id] = {
                "twin_kind": "conduit", "conduit_id": ancestor_id, "spellbook_id": book_id,
                "conduit_name": None, "policy_name": ancestor.get("policy_name", "default"),
                "dynamic": dynamic, "link_targets": [],
                "configuration_payload": {
                    "conduit_state": "lesser", "root_conduit_id": root_id,
                    "parent_conduit_id": parent_id,
                },
            }
            return
        configuration = ConduitHierarchy.configuration(existing)
        if (
                existing.get("spellbook_id") != book_id
                or existing.get("conduit_name") != ancestor_name
                or ConduitHierarchy.role(existing) != expected_role
                or configuration.get("parent_conduit_id") != parent_id
                or configuration.get("root_conduit_id", ancestor_id) != root_id
                or (ancestor_name is None and not is_root
                    and existing.get("policy_name", "default") != ancestor.get("policy_name", "default"))
        ):
            raise ValueError(f"Ancestor {ancestor_id!r} has conflicting Book/root/parent/name or policy values.")

    @staticmethod
    def _order_rows(
            rows: Dict[str, Dict[str, object]],
            books: Dict[str, Dict[str, object]],
    ) -> Dict[str, List[str]]:
        """Validate cross-row ownership and topologically order each Book's hierarchy.

        Args:
            rows: Explicit and expanded supporting scope payloads.
            books: Book-to-frame ownership values for name collision checks.
        Returns:
            Dict[str, List[str]]: Root-first scope identities for each Book.
        Raises:
            ValueError: Duplicate roots/names, missing parents, cross-Book edges or cycles.
        """
        children: Dict[str, List[str]] = {}
        roots: Dict[str, str] = {}
        names: set[Tuple[str, str]] = set()
        for conduit_id, payload in rows.items():
            book_id = str(payload.get("spellbook_id", ""))
            if payload.get("conduit_id", conduit_id) != conduit_id:
                raise ValueError(f"Conduit key {conduit_id!r} disagrees with its payload identity.")
            if ConduitHierarchy.role(payload) == "normal":
                if book_id in roots:
                    raise ValueError(f"Spellbook {book_id!r} has multiple recorded normal roots.")
                roots[book_id] = conduit_id
            else:
                parent_id = ConduitHierarchy._identity(
                    ConduitHierarchy.configuration(payload).get("parent_conduit_id"), "Lesser parent_conduit_id",
                )
                if parent_id not in rows or rows[parent_id].get("spellbook_id") != book_id:
                    raise ValueError(f"Lesser {conduit_id!r} has a missing or cross-Book parent {parent_id!r}.")
                children.setdefault(parent_id, []).append(conduit_id)
            name = payload.get("conduit_name")
            if name is not None and book_id in books:
                if not isinstance(name, str) or not name:
                    raise ValueError(f"Conduit {conduit_id!r} has an invalid name.")
                key = (str(books[book_id].get("frame_name", "default")), name)
                if key in names:
                    raise ValueError(f"Duplicate recorded conduit name {name!r} in frame {key[0]!r}.")
                names.add(key)
        order: Dict[str, List[str]] = {}
        pending = deque(roots.values())
        visited = 0
        while pending:
            conduit_id = pending.popleft()
            payload = rows[conduit_id]
            book_id = str(payload.get("spellbook_id", ""))
            if ConduitHierarchy.role(payload) == "lesser":
                if ConduitHierarchy.configuration(payload).get("root_conduit_id") != roots.get(book_id):
                    raise ValueError(f"Lesser {conduit_id!r} does not belong to its Book's normal root.")
            order.setdefault(book_id, []).append(conduit_id)
            visited += 1
            pending.extend(children.get(conduit_id, []))
        if visited != len(rows):
            raise ValueError("Recorded conduit parents are cyclic or have no normal-root anchor.")
        return order

"""S4a: unresolved inputs decided in the plan (design v2 4.2 step 6, B6) - anchored edits.

Usage: python apply_s4a_edits.py <tree_root> [--check]

site_plan_lowering.py: each context of a plan (top level, shared miss) raises for the first site it builds
unconditionally whose UNRESOLVED_INPUT parameters have no winning key, before constructing anything.
unresolved_input_error.py: `for_unsupplied(spell, names)` builds today's error without a TypeError cause; the message
builder is shared with `from_failed_construction`, which stays for the solo lane and the old emitters.
Each anchor must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
ERROR = "src/melder/utilities/custom_exceptions/unresolved_input_error.py"

# --------------------------------------------------------------------------------------------------------------------
# site_plan_lowering.py
# --------------------------------------------------------------------------------------------------------------------

IMPORT_OLD = '''from melder.aether.spellbook.existence.existence import Existence
'''
IMPORT_NEW = '''from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
'''

IMPORT2_OLD = '''from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
'''
IMPORT2_NEW = '''from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
'''

HELPERS_DOC_OLD = '''        Hold the cold-path helpers a plan reads from its namespace: the
        generic construct with supplied values, the P2 refusal and the
        equal-rank conflict guard. None of them runs on a direct-call step.
'''
HELPERS_DOC_NEW = '''        Hold the cold-path helpers a plan reads from its namespace: the
        generic construct with supplied values, the P2 refusal, the
        unresolved-input refusal and the equal-rank conflict guard. None of
        them runs on a direct-call step.
'''

HELPER_OLD = '''    @staticmethod
    def conflict_guard(
            first: Any,
'''
HELPER_NEW = '''    @staticmethod
    def raise_unresolved_input(spell: Spell, param_names: Tuple[str, ...]) -> None:
        """
        Raise today's `UnresolvedInputError` for a site the plan is about to build (S4a, B6).

        Contract:
            Emitted before anything under the site is constructed, so the
            error has no TypeError cause; message and fields are the failure
            path's (`UnresolvedInputError.for_unsupplied`).

        Args:
            spell: The consumer whose unresolved inputs have no winning key.
            param_names: Those parameters, in signature order.

        Raises:
            UnresolvedInputError: Always.
        """
        raise UnresolvedInputError.for_unsupplied(spell, param_names)

    @staticmethod
    def conflict_guard(
            first: Any,
'''

LOWERING_DOC_OLD = '''        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.
'''
LOWERING_DOC_NEW = '''        - A site with UNRESOLVED_INPUT parameters and no winning key for them
          raises `UnresolvedInputError` before anything under it is built
          (S4a, 2026-09-26; B6); OVERRIDE_REQUIRED parameters keep the
          constructor's own error.
        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.
'''

EMISSION_DOC_OLD = '''        - Normal mode (S2b-2, 2026-09-26) drops `ov` from the plan and from
          every miss signature and call; nothing else changes.
'''
EMISSION_DOC_NEW = '''        - Normal mode (S2b-2, 2026-09-26) drops `ov` from the plan and from
          every miss signature and call; nothing else changes.
        - Unresolved inputs (S4a, 2026-09-26): a context (the plan top, or a
          shared site's miss) raises first for the first site it builds
          unconditionally, in step order, whose UNRESOLVED_INPUT parameters
          have no winning key: its many children, then (in a miss) the site
          itself. A stored site's miss never runs, so it never demands.
'''

NAMESPACE_OLD = '''            "_raise_existing_override": SitePlanRuntimeHelpers.raise_existing_override,
'''
NAMESPACE_NEW = '''            "_raise_existing_override": SitePlanRuntimeHelpers.raise_existing_override,
            "_raise_unresolved_input": SitePlanRuntimeHelpers.raise_unresolved_input,
'''

RENDER_OLD = '''                "root_spell_id, root_spell_name)"
            )
        if self._dict_mode:
            body.append("    instance_results = {}")
'''
RENDER_NEW = '''                "root_spell_id, root_spell_name)"
            )
        body.extend(self._unresolved_check_lines(None, "    "))
        if self._dict_mode:
            body.append("    instance_results = {}")
'''

CHECKS_OLD = '''    def _emit_context(self, context: Optional[int], indent: str, lines: List[str]) -> bool:
'''
CHECKS_NEW = '''    def _unsupplied_unresolved(self, index: int) -> Tuple[str, ...]:
        """
        Return kept step `index`'s UNRESOLVED_INPUT parameters that have no winning key, in signature order.
        """
        site_index = self._site_index(self._steps[index])
        winners = self._winners
        unresolved = SocketKind.UNRESOLVED_INPUT.value
        return tuple(
            param.name for param in self._site_graph.sites[site_index].params
            if param.socket_kind_value == unresolved and (site_index, param.name) not in winners
        )

    def _unresolved_check_lines(self, context: Optional[int], indent: str) -> List[str]:
        """
        Return the unresolved-input refusal for one context, or no lines.

        Contract:
            The sites a context builds unconditionally are its many children
            (in step order) and, for a miss, the shared site itself (after
            them, as providers precede consumers). The first with unsupplied
            unresolved inputs gets one unconditional raise at the context top,
            before any construction; shared children check in their own miss.
        """
        candidates = [child for child in self._children.get(context, []) if not self._shared[child]]
        if context is not None:
            candidates.append(context)
        for index in candidates:
            names = self._unsupplied_unresolved(index)
            if names:
                return [f"{indent}_raise_unresolved_input(spells[{index}], {names!r})"]
        return []

    def _emit_context(self, context: Optional[int], indent: str, lines: List[str]) -> bool:
'''

MISS_OLD = '''        lines.append(f"def _miss{index}({parameters}):")
        if uses_many_store:
            lines.extend(self._many_store_prologue("    "))
        lines.extend(children)
'''
MISS_NEW = '''        lines.append(f"def _miss{index}({parameters}):")
        lines.extend(self._unresolved_check_lines(index, "    "))
        if uses_many_store:
            lines.extend(self._many_store_prologue("    "))
        lines.extend(children)
'''

# --------------------------------------------------------------------------------------------------------------------
# unresolved_input_error.py
# --------------------------------------------------------------------------------------------------------------------

RAISED_OLD = '''        constructing call's overrides did not supply that parameter. It fires only
        when that object is actually built: a stored (reused) object never demands
        its unresolved inputs, and conjure succeeds regardless.
'''
RAISED_NEW = '''        constructing call's overrides did not supply that parameter. It fires only
        when that object is actually built: a stored (reused) object never demands
        its unresolved inputs, and conjure succeeds regardless. The many_only and
        generalized plans raise it before constructing anything under that object
        (2026-09-26); the solo lane raises it from the failed constructor call.
'''

INNER_DOC_OLD = '''        - `inner` carries the constructor-call exception that exposed the gap.
'''
INNER_DOC_NEW = '''        - `inner` carries the constructor-call exception that exposed the gap on
          the solo failure path; it is None when a plan raised before building.
'''

SYSCTX_OLD = '''        Fires in the resolution layer on a constructor-failure path only, after
        conjure produced the Conduit. Successful melds never evaluate it.
'''
SYSCTX_NEW = '''        Fires in the resolution layer at meld, after conjure produced the Conduit:
        from a plan before construction (many_only, generalized) or on the solo
        constructor-failure path. Successful melds never evaluate it.
'''

PURPOSE_OLD = '''        Purpose:
            The single failure-path decision every executor family consults after
            a constructor call raised. INTERIM: once the demand-driven build plan
            exists, the plan decides this error before calling and these
            failure-path hooks are removed.
'''
PURPOSE_NEW = '''        Purpose:
            The failure-path decision for the solo lane and the old step emitters
            after a constructor call raised. The many_only and generalized plans
            decide the error before calling (`for_unsupplied`, 2026-09-26); this
            hook retires with the solo guard (S4b, owner decision).
'''

TAIL_OLD = '''        if not missing:
            return None
        missing.sort(key=lambda socket: socket.position)
        first = missing[0]
'''
TAIL_NEW = '''        if not missing:
            return None
        return cls._from_missing_sockets(spell, missing, exc)

    @classmethod
    def for_unsupplied(cls, spell: Spell, param_names: Collection[str]) -> UnresolvedInputError:
        """
        Build the error for unresolved inputs a plan knows are unsupplied, before any construction.

        Purpose:
            The plan-side decision (design v2 S4a, B6): a many_only or generalized
            plan raises this instead of calling a constructor that must fail.

        Contract:
            - Selects the consumer's UNRESOLVED_INPUT sockets named in
              `param_names` from its live Phase-3 topology; message, fields and
              ordering are exactly `from_failed_construction`'s, and `inner` is
              None (nothing was called).

        Args:
            spell:
                The consumer the plan was about to build.
            param_names:
                Its UNRESOLVED_INPUT parameters that have no winning key.

        Raises:
            RuntimeError:
                When the topology has none of those sockets: the plan is stale
                (a plan is rebuilt whenever the topology re-resolves).

        Returns:
            UnresolvedInputError: The error to raise.
        """
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        wanted = set(param_names)
        missing: List[SpellSocketDescriptor] = []
        if topology is not None:
            for socket in topology.sockets:
                if socket.socket_kind is SocketKind.UNRESOLVED_INPUT and socket.param_name in wanted:
                    missing.append(socket)
        if not missing:
            raise RuntimeError(
                f"{spell.spell_name} has no unresolved input named {sorted(wanted)!r}; its plan is stale."
            )
        return cls._from_missing_sockets(spell, missing, None)

    @classmethod
    def _from_missing_sockets(
            cls,
            spell: Spell,
            missing: List[SpellSocketDescriptor],
            inner: Optional[BaseException],
    ) -> UnresolvedInputError:
        """
        Build the error from the consumer's missing UNRESOLVED_INPUT sockets (shared message builder).

        Args:
            spell: The consumer.
            missing: Its unsupplied UNRESOLVED_INPUT sockets (any order; sorted here).
            inner: The constructor-call exception, or None when nothing was called.

        Returns:
            UnresolvedInputError: The error to raise.
        """
        missing = sorted(missing, key=lambda socket: socket.position)
        first = missing[0]
'''

RETURN_OLD = '''            param_name=param_name,
            inner=exc,
            expected_type=expected_type,
'''
RETURN_NEW = '''            param_name=param_name,
            inner=inner,
            expected_type=expected_type,
'''

EDITS = {
    LOWERING: [
        ("replace", IMPORT_OLD, IMPORT_NEW),
        ("replace", IMPORT2_OLD, IMPORT2_NEW),
        ("replace", HELPERS_DOC_OLD, HELPERS_DOC_NEW),
        ("replace", HELPER_OLD, HELPER_NEW),
        ("replace", LOWERING_DOC_OLD, LOWERING_DOC_NEW),
        ("replace", EMISSION_DOC_OLD, EMISSION_DOC_NEW),
        ("replace", NAMESPACE_OLD, NAMESPACE_NEW),
        ("replace", RENDER_OLD, RENDER_NEW),
        ("replace", CHECKS_OLD, CHECKS_NEW),
        ("replace", MISS_OLD, MISS_NEW),
    ],
    ERROR: [
        ("replace", RAISED_OLD, RAISED_NEW),
        ("replace", INNER_DOC_OLD, INNER_DOC_NEW),
        ("replace", SYSCTX_OLD, SYSCTX_NEW),
        ("replace", PURPOSE_OLD, PURPOSE_NEW),
        ("replace", TAIL_OLD, TAIL_NEW),
        ("replace", RETURN_OLD, RETURN_NEW),
    ],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()

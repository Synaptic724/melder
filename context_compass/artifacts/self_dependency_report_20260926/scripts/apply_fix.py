"""Option A for self-referencing constructors, applied to a tree root (argv[1]).

Phase 3 (fable_0's rows-only C-C version) records a self-resolution as a dependency, outside the frame order,
instead of raising; SELF_DEPENDENCY names the parameter(s); the report hides CIRCULAR_DEPENDENCY behind
SELF_DEPENDENCY. Validation results are unchanged (both codes stay on the spell). Anchored whole-line edits.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import append_block, replace_block

ROOT = pathlib.Path(sys.argv[1])
SC = ROOT / "src/melder/aether/spellbook/spell_compiler"
P3 = SC / "phases/compiler_phase_3.py"
SELF = SC / "validation/strategies/self_validation_strategy.py"
ERR = ROOT / "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"
T_P3 = ROOT / "tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py"
T_SELF = ROOT / "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_self_validation_strategy.py"
T_ERR = ROOT / "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py"
T_INT = ROOT / "tests/integration/melder/spellbook/test_spellbook_integration_self_dependency.py"

# --- Phase 3 (file owned by fable_0's C-C lane; applied here only on VM copies until agreed) ----------------
replace_block(P3, """                ValueError:
                    If ``requirements`` or ``graph`` is None, or if the spell
                    resolves itself as one of its own dependencies (a direct
                    self-cycle is a configuration error, refused before any
                    registry write).""", """                ValueError:
                    If ``requirements`` or ``graph`` is None. A spell that
                    resolves itself is not refused here: the self id is recorded
                    as a dependency (outside the frame order) and Phase 4's
                    SELF_DEPENDENCY check refuses the spell (2026-09-26).""")
replace_block(P3, """                if dep_spell_id == root_id:
                    # A direct self-cycle was refused by the dependency graph
                    # before the rows replaced it; keep the refusal here, before
                    # any registry write.
                    raise ValueError(
                        f"SpellCrafter Phase 3: spell {spell.spell_name!r} resolves itself for "
                        f"parameter {dep.param_name!r}; a spell cannot depend on itself."
                    )
                dependency_spell_ids.append(dep_spell_id)""", """                # A parameter that resolves to this same spell (a constructor taking its
                # own class) is recorded like any dependency: Phase 4's SELF_DEPENDENCY
                # check then refuses the spell with a readable message. It never enters
                # the local frame order below (2026-09-26).
                dependency_spell_ids.append(dep_spell_id)""")
replace_block(P3, """        # the topological order of the star graph phase 3 used to materialize.
        ordered_node_ids: List[str] = sorted(set(dependency_spell_ids))""", """        # the topological order of the star graph phase 3 used to materialize.
        # A self-dependency stays out of the order; Phase 4 refuses that spell.
        ordered_node_ids: List[str] = sorted(set(dependency_spell_ids) - {root_id})""")

# --- SELF_DEPENDENCY names the parameter ---------------------------------------------------------------------
replace_block(SELF, "from typing import TYPE_CHECKING, List", "from typing import TYPE_CHECKING, Any, Dict, List")
replace_block(SELF, """    Contract:
    - Checks only for direct self-dependency, not longer dependency cycles.""", """    Contract:
    - Checks only for direct self-dependency, not longer dependency cycles.
    - Phase 3 records a parameter that resolves to the spell itself instead of
      aborting (2026-09-26), so this check is what refuses such a spell; the
      message names the parameter when the Phase-3 topology is available.""")
replace_block(SELF, """        - Emits one `SELF_DEPENDENCY` error when the current spell id is found
          in its own dependency list.
        \"\"\"""", """        - Emits one `SELF_DEPENDENCY` error when the current spell id is found
          in its own dependency list. The message names the constructor
          parameter(s) that resolve to the spell when they are known
          (`_self_parameter_names`) and stays generic otherwise; `details` then
          also carries `parameter_names`.
        \"\"\"""")
replace_block(SELF, """        if root_id in deps:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="SELF_DEPENDENCY",
                    message=(
                        f"Spell {spell.spell_name!r} depends on itself: one of its constructor "
                        "parameters resolves to this same spell. Remove that parameter or give "
                        "it a default."
                    ),
                    details={"spell_id": root_id},
                )
            )""", """        if root_id in deps:
            names = self._self_parameter_names(context, root_id)
            if len(names) == 1:
                cause = f"its constructor parameter {names[0]!r} resolves to this same spell"
                fix = "Remove that parameter or give it a default."
            elif names:
                listed = ", ".join(repr(name) for name in names)
                cause = f"its constructor parameters {listed} resolve to this same spell"
                fix = "Remove those parameters or give them defaults."
            else:
                cause = "one of its constructor parameters resolves to this same spell"
                fix = "Remove that parameter or give it a default."
            details: Dict[str, Any] = {"spell_id": root_id}
            if names:
                details["parameter_names"] = list(names)
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="SELF_DEPENDENCY",
                    message=f"Spell {spell.spell_name!r} depends on itself: {cause}. {fix}",
                    details=details,
                )
            )

    @staticmethod
    def _self_parameter_names(context: SpellValidationContext, root_id: str) -> List[str]:
        \"\"\"
        Name the constructor parameters that resolved to the spell itself.

        Contract:
            - Reads the live spell's Phase-3 local topology, reachable when the
              context carries the spellbook, and returns the names of the sockets
              whose `target_spell_ids` include `root_id`, in constructor order.
            - Returns an empty list without a spellbook or without a topology
              (stand-in spells, or a dependency list set without Phase 3).

        Args:
            context: Validation context of the spell under validation.
            root_id: The spell's selected version id.

        Returns:
            List[str]: Parameter names that resolve to the spell itself.
        \"\"\"
        if context.spellbook is None:
            return []
        spell = context.spell
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        if topology is None:
            return []
        return [socket.param_name for socket in topology.iter_sockets() if root_id in socket.target_spell_ids]""")

# --- report: CIRCULAR_DEPENDENCY hidden behind SELF_DEPENDENCY ------------------------------------------------
replace_block(ERR, """        - Exact duplicates are dropped; BINDING_RESOLUTION_CYCLE is hidden when
          CIRCULAR_DEPENDENCY is shown for the same spell; root_not_viable and
          broken_spell_in_dag are hidden when any other error is shown.""", """        - Exact duplicates are dropped; BINDING_RESOLUTION_CYCLE is hidden when
          CIRCULAR_DEPENDENCY is reported for the same spell, and CIRCULAR_DEPENDENCY
          when SELF_DEPENDENCY is (a spell that depends on itself); root_not_viable and
          broken_spell_in_dag are hidden when any other error is shown.""")
replace_block(ERR, '''    SUPERSEDED_BY: ClassVar[Dict[str, str]] = {"BINDING_RESOLUTION_CYCLE": "CIRCULAR_DEPENDENCY"}''', '''    SUPERSEDED_BY: ClassVar[Dict[str, str]] = {
        "BINDING_RESOLUTION_CYCLE": "CIRCULAR_DEPENDENCY",
        "CIRCULAR_DEPENDENCY": "SELF_DEPENDENCY",
    }''')

# --- tests: fable_0's Phase-3 refusal test moves to the new contract -----------------------------------------
replace_block(T_P3, '''def test_build_local_frame_dag_refuses_self_dependency_before_registry_writes() -> None:
    """A spell that resolves itself is refused with ValueError and nothing is registered."""''',
'''def test_build_local_frame_dag_records_self_dependency_outside_frame_order() -> None:
    """A spell that resolves itself is recorded as its own dependency for Phase 4, outside the frame order."""''')
replace_block(T_P3, '''    with pytest.raises(ValueError, match="cannot depend on itself"):
        phase._build_local_frame_dag(
            spell=root_spell,
            spellbook=SimpleNamespace(_spell_id_pool={"root": root_spell}),
            spell_system_states=spell_system_states,
            requirements=SimpleNamespace(parameters=[]),
            graph=graph,
            cancellation_event=_CancelStub(is_set=False),
        )

    assert spell_system_states.dependencies_calls == []
    assert spell_system_states.topology_calls == []''', '''    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={"root": root_spell}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dependency_spell_ids == ["root"]
    assert ordered_node_ids == ["root"]
    assert spell_system_states.dependencies_calls[0][1] == ["root"]
    topology = spell_system_states.topology_calls[0][1]
    assert topology.get_sockets_for_param("me")[0].target_spell_ids == ("root",)''')

append_block(T_SELF, '''

class _SocketStub:
    """
    Purpose:
        Provide a topology socket with a parameter name and resolved targets.
    """

    def __init__(self, param_name: str, target_spell_ids: tuple) -> None:
        """
        Purpose:
            Store the socket's parameter name and target ids.
        Returns:
            None.
        """
        self.param_name = param_name
        self.target_spell_ids = target_spell_ids


class _TopologyStub:
    """
    Purpose:
        Provide a local topology exposing its sockets in constructor order.
    """

    def __init__(self, sockets: list) -> None:
        """
        Purpose:
            Store the sockets.
        Returns:
            None.
        """
        self._sockets = tuple(sockets)

    def iter_sockets(self) -> tuple:
        """
        Purpose:
            Return the sockets.
        Returns:
            tuple: The sockets in constructor order.
        """
        return self._sockets


class _StatesStub:
    """
    Purpose:
        Provide a spell-system-states stand-in returning one topology.
    """

    def __init__(self, topology: object) -> None:
        """
        Purpose:
            Store the topology to return.
        Returns:
            None.
        """
        self._topology = topology

    def get_local_topology(self, spell_index: object) -> object:
        """
        Purpose:
            Return the stored topology for any spell index.
        Returns:
            object: The topology, or None.
        """
        return self._topology


def _live_context(sockets: list, issues: list) -> SpellValidationContext:
    """
    Purpose:
        Build a context whose spell carries a Phase-3 topology and whose spellbook is present.
    Returns:
        SpellValidationContext: The context.
    """
    spell = _SpellStub(spell_id="root", spell_name="Node", dependencies=["root"])
    spell._spell_system_states = _StatesStub(_TopologyStub(sockets))
    return SpellValidationContext(
        spell=spell,
        spellbook=object(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=issues,
    )


def test_validate_names_the_parameter_that_resolves_to_the_spell() -> None:
    """
    Purpose:
        Ensure the message names the self-resolving parameter when the topology is known.
    Contract:
        Only sockets targeting the spell itself are named; details carry the names.
    Returns:
        None.
    """
    issues: list[SpellValidationIssue] = []
    context = _live_context([_SocketStub("parent", ("root",)), _SocketStub("name", ())], issues)

    SelfDependencyStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].message == (
        "Spell 'Node' depends on itself: its constructor parameter 'parent' resolves to this same spell. "
        "Remove that parameter or give it a default."
    )
    assert issues[0].details == {"spell_id": "root", "parameter_names": ["parent"]}


def test_validate_names_every_self_resolving_parameter() -> None:
    """
    Purpose:
        Ensure several self-resolving parameters are all named, in constructor order.
    Returns:
        None.
    """
    issues: list[SpellValidationIssue] = []
    context = _live_context([_SocketStub("left", ("root",)), _SocketStub("right", ("other", "root"))], issues)

    SelfDependencyStrategy().validate(context)

    assert "its constructor parameters 'left', 'right' resolve to this same spell" in issues[0].message
    assert issues[0].message.endswith("Remove those parameters or give them defaults.")


def test_validate_message_stays_generic_without_a_topology() -> None:
    """
    Purpose:
        Ensure a live context whose spell has no Phase-3 topology keeps the generic message.
    Returns:
        None.
    """
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Node", dependencies=["root"])
    spell._spell_system_states = _StatesStub(None)
    context = SpellValidationContext(
        spell=spell, spellbook=object(), requirements=None, symbolic_graph=None,
        resolution_frame=None, cancel_event=None, issues=issues,
    )

    SelfDependencyStrategy().validate(context)

    assert "one of its constructor parameters resolves to this same spell" in issues[0].message
    assert issues[0].details == {"spell_id": "root"}
''')

append_block(T_ERR, '''

def test_circular_dependency_hidden_when_self_dependency_reported() -> None:
    """
    Purpose:
        Report a spell that depends on itself once.
    Contract:
        CIRCULAR_DEPENDENCY (and the binding-key cycle behind it) is hidden when SELF_DEPENDENCY is present in
        the same block; CIRCULAR_DEPENDENCY alone is still shown.
    """
    looped = _spell(name="Node", issues=[
        _issue("SELF_DEPENDENCY", "Node depends on itself."),
        _issue("CIRCULAR_DEPENDENCY", "Node cycle."),
        _issue("BINDING_RESOLUTION_CYCLE", "Node key cycle."),
    ])
    cycle = _spell(name="CycleA", spell_id="spell-2", issues=[_issue("CIRCULAR_DEPENDENCY", "Two-spell cycle.")])

    message = str(SpellbookValidationError([looped, cycle]))

    assert "Node depends on itself. [SELF_DEPENDENCY]" in message
    assert "Node cycle." not in message
    assert "Node key cycle." not in message
    assert "Two-spell cycle. [CIRCULAR_DEPENDENCY]" in message
''')

# --- integration (authored in new_files/) ------------------------------------------------------------
if T_INT.exists():
    raise SystemExit(f"{T_INT} already exists")
T_INT.write_bytes((pathlib.Path(__file__).parent / "new_files" / T_INT.name).read_bytes())
print("created", T_INT.name)
print("applied to", ROOT)

"""Cycle-consumer wording for CircularDependencyStrategy, applied to a tree root (argv[1]).

A spell that only reaches a dependency cycle is told which of its dependencies leads there and that it is not
part of that cycle; cycle members keep their message. Codes, severities and details are unchanged. Anchored
whole-line edits via patch_util (endings preserved); every edit is skipped when its new text is already present,
so a re-run is safe.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import append_block, replace_block

ROOT = pathlib.Path(sys.argv[1])
SRC = ROOT / "src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py"
T_UNIT = ROOT / "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_circular_dependency_strategy.py"
T_INT = ROOT / "tests/integration/melder/spellbook/test_spellbook_integration_validation_report.py"


def _text(path: pathlib.Path) -> str:
    """Return the file text with CR removed, for presence checks."""
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def edit(path: pathlib.Path, old: str, new: str) -> None:
    """Replace `old` with `new` once, unless `new` is already present (each `new` contains its `old`)."""
    if new in _text(path):
        print(f"skip {path.name} (already applied)")
        return
    replace_block(path, old, new)


def append_once(path: pathlib.Path, marker: str, text: str) -> None:
    """Append `text` unless `marker` is already in the file."""
    if marker in _text(path):
        print(f"skip append {path.name} (already applied)")
        return
    append_block(path, text)


# --- source ------------------------------------------------------------------------------------------------
edit(SRC, """    - Emits validation issues into the supplied context; it does not mutate the
      graph or try to break cycles automatically.""", """    - Emits validation issues into the supplied context; it does not mutate the
      graph or try to break cycles automatically.
    - Words the issue for what the spell is (2026-09-26): a cycle member is told
      it is part of the cycle; a spell that only reaches a cycle is told which of
      its dependencies leads there and that it is not part of that cycle. Either
      way the spell is refused and `details["cycle"]` holds the cycle ids.""")
edit(SRC, """        - Emits one `CIRCULAR_DEPENDENCY` issue when a reachable cycle is
          found.""", """        - Emits one `CIRCULAR_DEPENDENCY` issue when a reachable cycle is
          found. The message names the cycle; for a spell outside the cycle it
          also names the spell's direct dependency on the route to it (see
          `_cycle_message`). `details` carries the cycle ids in both cases.""")
edit(SRC, """        cycle_path: List[str] = []
""", """        cycle_path: List[str] = []
        # Path nodes before the cycle starts: empty when the spell is in the
        # cycle, otherwise the spell followed by any intermediates.
        route: List[str] = []
""")
edit(SRC, """                cycle_path.extend(path[start_idx:])""", """                cycle_path.extend(path[start_idx:])
                route.extend(path[:start_idx])""")
edit(SRC, """            pool = spellbook._spell_id_pool
            pretty = " -> ".join(
                SpellInputUtils.describe_spell_id(spell_id, pool) for spell_id in cycle_path
            )
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=(
                        f"Spell {context.spell.spell_name!r} is part of a dependency cycle: "
                        f"{pretty}. Melder cannot build any spell in the cycle; remove one of "
                        "these constructor dependencies or give that parameter a default."
                    ),
                    details={"cycle": list(cycle_path)},
                )
            )""", """            pool = spellbook._spell_id_pool
            cycle_names = [
                SpellInputUtils.describe_spell_id(spell_id, pool) for spell_id in cycle_path
            ]
            lead_name: Optional[str] = None
            lead_in_cycle = False
            if route:
                # The spell is outside the cycle and reaches it through its direct
                # dependency on the route: the cycle's first node when the route is
                # only the spell, otherwise the first intermediate.
                lead_in_cycle = len(route) == 1
                lead_id = cycle_path[0] if lead_in_cycle else route[1]
                lead_name = SpellInputUtils.describe_spell_id(lead_id, pool)
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=self._cycle_message(
                        context.spell.spell_name, cycle_names, lead_name, lead_in_cycle
                    ),
                    details={"cycle": list(cycle_path)},
                )
            )

    @staticmethod
    def _cycle_message(
        spell_name: str,
        cycle_names: List[str],
        lead_name: Optional[str],
        lead_in_cycle: bool,
    ) -> str:
        \"\"\"
        Word the CIRCULAR_DEPENDENCY message for a cycle member or a cycle consumer.

        Purpose:
            Every spell from which a cycle is reachable is refused, whether or not
            it is in the cycle. The message says which case applies so the user
            fixes the cycle rather than a spell that only uses it.

        Contract:
            - Pure; formats text only.
            - `lead_name` None: the spell is a cycle member and gets the member
              wording ("is part of a dependency cycle").
            - Otherwise the spell is a consumer: the message names its direct
              dependency on the route ("which is part of a dependency cycle" when
              that dependency is a member, "which depends on itself" when it is a
              self-loop, "which depends on a dependency cycle" when it is an
              intermediate), says how to break the cycle, and states that the
              spell itself is not part of that cycle.
            - A self-loop is a two-entry cycle ("'Node' -> 'Node'"); its fix names
              the loop spell.

        Args:
            spell_name: Name of the spell under validation (quoted here).
            cycle_names: Display names of the cycle path, already quoted by
                `SpellInputUtils.describe_spell_id`, first node repeated last.
            lead_name: Quoted display name of the spell's direct dependency on the
                route to the cycle, or None when the spell is in the cycle.
            lead_in_cycle: True when `lead_name` is itself a cycle member.

        Returns:
            str: The user-facing issue message.
        \"\"\"
        pretty = " -> ".join(cycle_names)
        if lead_name is None:
            return (
                f"Spell {spell_name!r} is part of a dependency cycle: {pretty}. Melder cannot "
                "build any spell in the cycle; remove one of these constructor dependencies "
                "or give that parameter a default."
            )
        self_loop = len(cycle_names) == 2
        if lead_in_cycle and self_loop:
            needs = f"it needs {lead_name}, which depends on itself ({pretty})"
        elif lead_in_cycle:
            needs = f"it needs {lead_name}, which is part of a dependency cycle: {pretty}"
        else:
            needs = f"it needs {lead_name}, which depends on a dependency cycle: {pretty}"
        if self_loop:
            fix = (
                f"Fix {cycle_names[0]} (remove that constructor dependency or give that "
                "parameter a default)"
            )
        else:
            fix = (
                "Break that cycle (remove one of those constructor dependencies or give that "
                "parameter a default)"
            )
        return (
            f"Spell {spell_name!r} cannot be built: {needs}. {fix}; "
            f"{spell_name!r} itself is not part of that cycle."
        )""")

# --- unit tests --------------------------------------------------------------------------------------------
append_once(T_UNIT, "def test_validate_words_a_consumer_of_a_cycle_member_as_a_consumer", '''

def test_validate_words_a_consumer_of_a_cycle_member_as_a_consumer() -> None:
    """
    Purpose:
        A spell that only needs a cycle member is not reported as part of the cycle (2026-09-26).
    Contract:
        The message names the member it needs, the cycle, the fix, and that the spell is not
        part of that cycle; code, severity and details are unchanged.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spell_c = _SpellStub(spell_id="c", spell_name="Gamma", dependencies=["a"])
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c])
    context = _make_context(spell=spell_c, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.code == "CIRCULAR_DEPENDENCY"
    assert issue.severity == "error"
    assert issue.details == {"cycle": ["a", "b", "a"]}
    assert issue.message == (
        "Spell 'Gamma' cannot be built: it needs 'Alpha', which is part of a dependency cycle: "
        "'Alpha' -> 'Beta' -> 'Alpha'. Break that cycle (remove one of those constructor "
        "dependencies or give that parameter a default); 'Gamma' itself is not part of that cycle."
    )


def test_validate_names_the_intermediate_that_leads_a_consumer_to_a_cycle() -> None:
    """
    Purpose:
        A spell that reaches a cycle through a non-member names that intermediate.
    Contract:
        "which depends on a dependency cycle" follows the intermediate; the cycle is unchanged.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spell_c = _SpellStub(spell_id="c", spell_name="Gamma", dependencies=["a"])
    spell_d = _SpellStub(spell_id="d", spell_name="Delta", dependencies=["c"])
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c, spell_d])
    context = _make_context(spell=spell_d, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert message.startswith(
        "Spell 'Delta' cannot be built: it needs 'Gamma', which depends on a dependency cycle: "
        "'Alpha' -> 'Beta' -> 'Alpha'. Break that cycle"
    )
    assert message.endswith("'Delta' itself is not part of that cycle.")
    assert issues[0].details == {"cycle": ["a", "b", "a"]}


def test_validate_words_a_consumer_of_a_self_loop() -> None:
    """
    Purpose:
        A spell that needs a spell depending on itself is told so, and the fix names that spell.
    Contract:
        "which depends on itself" with the two-entry loop; the fix is "Fix 'Node' (...)".
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    tree = _SpellStub(spell_id="t", spell_name="Tree", dependencies=["n"])
    spellbook = _SpellbookStub([node, tree])
    context = _make_context(spell=tree, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues[0].message == (
        "Spell 'Tree' cannot be built: it needs 'Node', which depends on itself ('Node' -> 'Node'). "
        "Fix 'Node' (remove that constructor dependency or give that parameter a default); "
        "'Tree' itself is not part of that cycle."
    )
    assert issues[0].details == {"cycle": ["n", "n"]}


def test_validate_names_the_intermediate_before_a_self_loop() -> None:
    """
    Purpose:
        A spell that reaches a self-loop through a non-member names the intermediate and fixes the loop spell.
    Contract:
        "which depends on a dependency cycle: 'Node' -> 'Node'" and "Fix 'Node' (...)".
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    tree = _SpellStub(spell_id="t", spell_name="Tree", dependencies=["n"])
    forest = _SpellStub(spell_id="f", spell_name="Forest", dependencies=["t"])
    spellbook = _SpellbookStub([node, tree, forest])
    context = _make_context(spell=forest, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert message.startswith(
        "Spell 'Forest' cannot be built: it needs 'Tree', which depends on a dependency cycle: "
        "'Node' -> 'Node'. Fix 'Node' (remove that constructor dependency"
    )
    assert message.endswith("'Forest' itself is not part of that cycle.")


def test_validate_keeps_the_member_wording_for_a_self_loop_member() -> None:
    """
    Purpose:
        The spell that depends on itself keeps the member wording.
    Contract:
        "Spell 'Node' is part of a dependency cycle: 'Node' -> 'Node'." with the member fix sentence.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    spellbook = _SpellbookStub([node])
    context = _make_context(spell=node, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues[0].message.startswith("Spell 'Node' is part of a dependency cycle: 'Node' -> 'Node'.")
    assert "cannot be built" not in issues[0].message
''')

# --- integration test --------------------------------------------------------------------------------------
edit(T_INT, """counted. Also pins the two misfires fixed with it: `*args: Any, **kwargs: Any` and plain data lists
and dicts no longer produce errors.""", """counted. Also pins the two misfires fixed with it: `*args: Any, **kwargs: Any` and plain data lists
and dicts no longer produce errors. A spell that only uses a cycle is named as its consumer, not as a
member of the cycle (2026-09-26).""")
edit(T_INT, """    def __init__(self, a: CycleA) -> None:
        \"\"\"Keep the first half.\"\"\"
        self.a = a
""", """    def __init__(self, a: CycleA) -> None:
        \"\"\"Keep the first half.\"\"\"
        self.a = a


class CycleUser:
    \"\"\"Needs one half of the cycle without being part of it.\"\"\"

    def __init__(self, a: CycleA) -> None:
        \"\"\"Keep the half it needs.\"\"\"
        self.a = a
""")
edit(T_INT, """    assert "1 warning not shown" in message
    assert "label" not in message
""", """    assert "1 warning not shown" in message
    assert "label" not in message


def test_cycle_consumer_is_reported_as_a_consumer() -> None:
    \"\"\"A spell that only needs a cycle member is told which dependency leads there, not that it is in the cycle.\"\"\"
    book = _book("consumer")
    book.bind(spell=CycleA, existence=Existence.many, permissions="create")
    book.bind(spell=CycleB, existence=Existence.many, permissions="create")
    book.bind(spell=CycleUser, existence=Existence.many, permissions="create")
    try:
        message = _conjure_error(book)
    finally:
        book.cleanup()

    assert (
        "Spell 'CycleUser' cannot be built: it needs 'CycleA', which is part of a dependency cycle: "
        "'CycleA' -> 'CycleB' -> 'CycleA'."
    ) in message
    assert "'CycleUser' itself is not part of that cycle." in message
    assert "Spell 'CycleUser' is part of a dependency cycle" not in message
    assert "Spell 'CycleA' is part of a dependency cycle: 'CycleA' -> 'CycleB' -> 'CycleA'." in message
""")

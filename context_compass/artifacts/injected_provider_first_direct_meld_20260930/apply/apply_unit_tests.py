"""
Update the unit tests for option B before the fix (they must run red against 0.2.8214).

Usage: python apply_unit_tests.py <repository root>
test_meld.py: `_make_phase5_root`, the four deferred-lane tests pinned to a Phase 5 root, four new lane tests.
test_spellbook_creation_system_resolution_fastpath.py: the Spellbook stub gains the pool the target pass now reads.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

MELD = "tests/unit/melder/aether/conduit/meld/test_meld.py"
FAST = "tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py"
PLAIN_SPELL = (
    "    spell = _SpellStub(\n"
    "        spell_id=\"spell-1\",\n"
    "        spellbook=spellbook,\n"
    "        resolution_required=True,\n"
    "        resolution_complete=False,\n"
    "    )\n"
)
ROOT_SPELL = (
    "    spell = _make_phase5_root(_SpellStub(\n"
    "        spell_id=\"spell-1\",\n"
    "        spellbook=spellbook,\n"
    "        resolution_required=True,\n"
    "        resolution_complete=False,\n"
    "    ))\n"
)

session = ApplySession(sys.argv[1])


def function_text(relative: str, name: str) -> str:
    """Return one top-level test function's text, from its def line to the next top-level def."""
    text = session._load(relative)
    start = text.index(f"\ndef {name}(") + 1
    end = text.index("\ndef ", start + 4)
    return text[start:end]


def edit_function(relative: str, name: str, old: str, new: str) -> None:
    """
    Replace one LF-written block inside one test function only, in the line-ending style it has there.

    The two test files are CRLF with a few LF lines, so the block is matched as CRLF first, then as LF, and the
    function text is swapped in the staged file directly (it is already in the file's own style).
    """
    body = function_text(relative, name)
    for old_variant, new_variant in ((old.replace("\n", "\r\n"), new.replace("\n", "\r\n")), (old, new)):
        count = body.count(old_variant)
        if count == 1:
            text = session.texts[relative]
            if text.count(body) != 1:
                raise SystemExit(f"{name}: function text is not unique")
            session.texts[relative] = text.replace(body, body.replace(old_variant, new_variant), 1)
            return
        if count > 1:
            raise SystemExit(f"{name}: block count {count}")
    raise SystemExit(f"{name}: block not found: {old[:80]!r}")


session.insert_before(
    MELD,
    "def test_ensure_runtime_resolution_ready_skips_when_not_required() -> None:\n",
    "def _make_phase5_root(spell: _SpellStub) -> _SpellStub:\n"
    "    \"\"\"\n"
    "    Give a stub spell a Phase 5 root blueprint for its selected id and return it.\n"
    "\n"
    "    The deferred lane keeps its 8-11 pass for a spell that is its current Phase 5 root; any other constructed\n"
    "    spell (a dependency compiled only inside a consumer's plan) runs the full target pass (5-11) instead.\n"
    "    \"\"\"\n"
    "    spell._compiler_artifact._root_blueprint_phase5 = SimpleNamespace(\n"
    "        root_spell_id=spell.spell_index.selected_spell_id,\n"
    "        cleanup=lambda: None,\n"
    "    )\n"
    "    return spell\n"
    "\n"
    "\n",
)

name = "test_ensure_runtime_resolution_ready_runs_deferred_and_marks_complete"
edit_function(
    MELD, name,
    "    Verify runtime gate executes deferred phases and marks resolution complete.\n"
    "\n"
    "    Contract:\n"
    "        - Deferred phase hook runs once for the active resolution conduit id.\n",
    "    Verify runtime gate executes deferred phases for a Phase 5 root and marks resolution complete.\n"
    "\n"
    "    Contract:\n"
    "        - A spell that is its current Phase 5 root keeps the deferred 8-11 pass: the hook runs once for\n"
    "          the active resolution conduit id and the full target pass does not run.\n",
)
edit_function(
    MELD, name,
    "    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()\n"
    "    meld = _make_meld(spellbook=spellbook)\n",
    "    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()\n"
    "    spellbook._run_resolution_phases_for_target_spell = MagicMock()\n"
    "    meld = _make_meld(spellbook=spellbook)\n",
)
edit_function(MELD, name, PLAIN_SPELL, ROOT_SPELL)
edit_function(
    MELD, name,
    "        spell,\n    )\n    assert spell.resolution_complete is True\n",
    "        spell,\n    )\n    spellbook._run_resolution_phases_for_target_spell.assert_not_called()\n"
    "    assert spell.resolution_complete is True\n",
)

name = "test_ensure_runtime_resolution_ready_failure_reflags_and_reraises"
edit_function(
    MELD, name,
    "        - Deferred phase exceptions propagate to caller.\n",
    "        - Deferred phase exceptions (a Phase 5 root's 8-11 pass) propagate to caller.\n",
)
edit_function(MELD, name, PLAIN_SPELL, ROOT_SPELL)

name = "test_meld_runs_deferred_runtime_resolution_before_context_build"
edit_function(
    MELD, name,
    "    Verify meld executes deferred runtime gate before creation-context build.\n",
    "    Verify meld executes deferred runtime gate before creation-context build (a Phase 5 root: 8-11).\n",
)
edit_function(
    MELD, name,
    "    spell = _SpellStub(\n"
    "        spell_id=\"spell-1\",\n"
    "        owner_creations=creations,\n"
    "        spellbook=spellbook,\n"
    "        resolution_required=True,\n"
    "        resolution_complete=False,\n"
    "    )\n",
    "    spell = _make_phase5_root(_SpellStub(\n"
    "        spell_id=\"spell-1\",\n"
    "        owner_creations=creations,\n"
    "        spellbook=spellbook,\n"
    "        resolution_required=True,\n"
    "        resolution_complete=False,\n"
    "    ))\n",
)

name = "test_meld_skips_context_build_when_deferred_runtime_resolution_fails"
edit_function(
    MELD, name,
    "    Verify meld does not build context when deferred runtime gate fails.\n",
    "    Verify meld does not build context when deferred runtime gate fails (a Phase 5 root: 8-11).\n",
)
edit_function(MELD, name, PLAIN_SPELL, ROOT_SPELL)

NEW_TESTS = '''def test_ensure_runtime_resolution_ready_runs_full_target_pass_without_phase5_root() -> None:
    """
    Verify the runtime gate runs the full target pass for a spell that is not its Phase 5 root.

    Contract:
        - A constructed spell with no Phase 5 root blueprint - a dependency compiled only inside a
          consumer's plan and flagged by that pass - runs `_run_resolution_phases_for_target_spell` (5-11)
          once for the active resolution conduit id.
        - The deferred 8-11 hook does not run: it skips a spell with no Phase 5 root blueprint.
        - Success flips flags to `resolution_complete=True` and `resolution_required=False`.
    """
    spellbook = _SpellbookStub()
    spellbook._run_resolution_phases_for_target_spell = MagicMock()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )

    meld._ensure_runtime_resolution_ready(spell)

    spellbook._run_resolution_phases_for_target_spell.assert_called_once_with(
        meld._resolution_conduit_id,
        spell,
    )
    spellbook._run_deferred_resolution_phases_for_target_spell.assert_not_called()
    assert spell.resolution_complete is True
    assert spell.resolution_required is False


def test_ensure_runtime_resolution_ready_keeps_deferred_pass_for_existing_creation() -> None:
    """
    Verify an existing-creation spell keeps the deferred pass even without a Phase 5 root blueprint.

    Contract:
        - Existing creations never plan (their context has its own executor path), so the lane keeps
          `_run_deferred_resolution_phases_for_target_spell` for them and never runs the full target pass.
        - Success flips flags to `resolution_complete=True` and `resolution_required=False`.
    """
    spellbook = _SpellbookStub()
    spellbook._run_resolution_phases_for_target_spell = MagicMock()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        is_existing_creation=True,
        resolution_required=True,
        resolution_complete=False,
    )

    meld._ensure_runtime_resolution_ready(spell)

    spellbook._run_deferred_resolution_phases_for_target_spell.assert_called_once_with(
        meld._resolution_conduit_id,
        spell,
    )
    spellbook._run_resolution_phases_for_target_spell.assert_not_called()
    assert spell.resolution_complete is True
    assert spell.resolution_required is False


def test_ensure_runtime_resolution_ready_full_pass_leaving_invalid_verdict_raises() -> None:
    """
    Verify a full target pass that leaves the spell unresolved for the conduit raises a validation error.

    Contract:
        - After the full pass the spell must read resolution-valid for the resolution conduit; a pass that
          records an invalid verdict (a visibility failure returns without raising) raises
          SpellbookValidationError instead of marking the spell complete.
        - The failure keeps `resolution_required=True` and `resolution_complete=False` and bumps the door
          epoch, like any failed deferred-lane pass.
    """
    resolution_state = _ResolutionStateStub()
    spellbook = _SpellbookStub()

    def _record_invalid_verdict(conduit_id: str, target_spell: _SpellStub) -> None:
        """Stand in for a full pass that ends in a visibility failure."""
        resolution_state._spell_validity[target_spell.spell_id] = SpellValidity.invalid

    spellbook._run_resolution_phases_for_target_spell = MagicMock(side_effect=_record_invalid_verdict)
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        spell_system_states=_SpellSystemStatesStub(resolution_state),
        resolution_required=True,
        resolution_complete=False,
    )
    epoch_before = spell._door_epoch

    with pytest.raises(SpellbookValidationError):
        meld._ensure_runtime_resolution_ready(spell)

    assert spell.resolution_required is True
    assert spell.resolution_complete is False
    assert spell._door_epoch == epoch_before + 1


def test_ensure_runtime_resolution_ready_full_pass_failure_reflags_and_reraises() -> None:
    """
    Verify a failing full target pass propagates and keeps the spell owing its resolution.

    Contract:
        - Exceptions from `_run_resolution_phases_for_target_spell` propagate unchanged.
        - Failure preserves `resolution_required=True` and `resolution_complete=False` and bumps the
          door epoch.
    """
    spellbook = _SpellbookStub()
    spellbook._run_resolution_phases_for_target_spell = MagicMock(
        side_effect=RuntimeError("full target pass failed"),
    )
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )
    epoch_before = spell._door_epoch

    with pytest.raises(RuntimeError, match="full target pass failed"):
        meld._ensure_runtime_resolution_ready(spell)

    assert spell.resolution_required is True
    assert spell.resolution_complete is False
    assert spell._door_epoch == epoch_before + 1


'''
session.insert_before(MELD, "def test_meld_runs_deferred_runtime_resolution_before_context_build(", NEW_TESTS)

session.replace(
    FAST,
    "        Contract:\n"
    "            - Starts with zero check_cleaned invocations.\n"
    "            - Exposes minimal configuration/logging surfaces required by the\n"
    "              tested orchestration paths.\n"
    "        Returns:\n"
    "            None.\n"
    "        \"\"\"\n"
    "        self.check_cleaned_calls = 0\n"
    "        self._configuration = _StubConfiguration()\n"
    "        self._logger = _StubLogger()\n"
    "        self._spells: Dict[Any, Any] = {}\n",
    "        Contract:\n"
    "            - Starts with zero check_cleaned invocations.\n"
    "            - Exposes minimal configuration/logging surfaces required by the\n"
    "              tested orchestration paths.\n"
    "            - Exposes an empty visible spell pool: a successful target-local\n"
    "              pass reads it to flag dependencies without a plan of their own.\n"
    "        Returns:\n"
    "            None.\n"
    "        \"\"\"\n"
    "        self.check_cleaned_calls = 0\n"
    "        self._configuration = _StubConfiguration()\n"
    "        self._logger = _StubLogger()\n"
    "        self._spells: Dict[Any, Any] = {}\n"
    "        self._spell_id_pool: Dict[str, Any] = {}\n",
)
long_lines = session.long_added_lines()
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write())

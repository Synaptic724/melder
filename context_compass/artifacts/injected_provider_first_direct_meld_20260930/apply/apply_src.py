"""
Land option B (0.2.8215): the target pass flags dependencies without a plan of their own, and the deferred lane runs
the full target pass for a spell that is not its Phase 5 root.

Usage: python apply_src.py <repository root>
Logic: spellbook_creation_system.py, meld.py. Comments/docstrings only: spellbook.py, creation_context_rebuild.py.
Version: __version__ 0.2.8214 -> 0.2.8215 (refuses any other starting version).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

CREATION = "src/melder/aether/spellbook/spellbook_creation_system.py"
MELD = "src/melder/aether/conduit/meld/meld.py"
BOOK = "src/melder/aether/spellbook/spellbook.py"
REBUILD = "src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py"
VERSION = "src/melder/__version__.py"

session = ApplySession(sys.argv[1])

session.replace(VERSION, '__version__ = "0.2.8214"', '__version__ = "0.2.8215"')

# --- SpellbookCreationSystem: the target pass tail and the flag -------------------------------------------------
session.replace(
    CREATION,
    "            Run target-local resolution phases for one spell within a conduit scope.\n"
    "        Contract:\n"
    "            - Requires non-empty conduit id and non-null target spell.\n"
    "            - Runs local foundational phases before local plan phases.\n"
    "            - Converts local KeyError dependency misses into deterministic diagnostics.\n"
    "            - Cleans scoped phase artifacts before returning.\n",
    "            Run target-local resolution phases for one spell within a conduit scope.\n"
    "        Contract:\n"
    "            - Requires non-empty conduit id and non-null target spell.\n"
    "            - Runs local foundational phases before local plan phases.\n"
    "            - Converts local KeyError dependency misses into deterministic diagnostics.\n"
    "            - Cleans scoped phase artifacts before returning.\n"
    "            - On success, flags each dependency in the target's Phase 5 scope\n"
    "              that this Book owns and that the pass compiled only inside the\n"
    "              target's plan (`flag_dependencies_without_own_plan`), so its\n"
    "              first direct meld runs its own full target pass (0.2.8215). The\n"
    "              failure paths (a validation error, a visibility failure) flag\n"
    "              nothing.\n",
)
session.replace(
    CREATION,
    "            return results\n"
    "        SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(\n"
    "            spellbook=spellbook,\n"
    "            spell_ids=scoped_spell_ids,\n"
    "        )\n"
    "        return results\n"
    "\n"
    "    @staticmethod\n"
    "    def run_deferred_resolution_phases_for_target_spell(\n",
    "            return results\n"
    "        SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(\n"
    "            spellbook=spellbook,\n"
    "            spell_ids=scoped_spell_ids,\n"
    "        )\n"
    "        SpellbookCreationSystem.flag_dependencies_without_own_plan(\n"
    "            spellbook=spellbook,\n"
    "            target_spell_id=target_spell_id,\n"
    "            scoped_spell_ids=scoped_spell_ids,\n"
    "        )\n"
    "        return results\n"
    "\n"
    "    @staticmethod\n"
    "    def run_deferred_resolution_phases_for_target_spell(\n",
)
FLAG = '''    @staticmethod
    def flag_dependencies_without_own_plan(
            spellbook: Spellbook,
            target_spell_id: str,
            scoped_spell_ids: Collection[str],
    ) -> tuple[str, ...]:
        """
        Purpose:
            Leave each dependency that a target-local pass compiled only inside
            its target's plan owing its own resolution, so its first direct
            meld resolves it instead of reaching the CreationContext builder
            with no plan (0.2.8215).
        Contract:
            - Local Phase 5 publishes root blueprints only to the target
              (2026-09-19) and local Phase 6 stamps every node of the target's
              system index valid for the conduit. A dependency first compiled
              in such a pass therefore reads valid yet has no plan of its own;
              the `resolution_required` flag, which every meld door reads, is
              what owes that work.
            - Considers each id in `scoped_spell_ids` except the target, in
              sorted order. Skips ids missing from `spellbook._spell_id_pool`,
              spells this Book does not own (`spell._spellbook is not
              spellbook`; a borrowed spell is compiled by its own Book),
              non-resolvable definitions and existing creations (neither ever
              plans).
            - Under the dependency's spell lock, flags it only when it has no
              phase-11 plan (`_compiler_artifact._spell_codegen_creation is
              None`), no published CreationContext
              (`_creation_context_switch.state < 2`; a context loaded from the
              conjure cache needs no plan) and no flag yet: sets
              `resolution_complete=False` and `resolution_required=True` and
              bumps `_door_epoch`, so no fast-door entry survives the flag.
            - Changes no verdict, Book flag or diagnostic. Idempotent: an
              already flagged dependency is skipped.
        Threading:
            Runs inside the target pass, whose meld-time caller holds the
            target's rebuild window and spell lock. Each dependency's lock is
            taken after the target's - consumer before dependency, the order
            build locks follow over the acyclic dependency graph - so the check
            and the write are atomic against that dependency's own resolution
            lane, which holds the dependency's lock for its whole pass.
        Args:
            spellbook: The Book that ran the target pass.
            target_spell_id: The pass's target; never flagged.
            scoped_spell_ids: The pass's scope: the target plus its Phase 5
                system-index nodes.
        Returns:
            tuple[str, ...]: The flagged spell ids, in sorted order.
        """
        spell_id_pool = spellbook._spell_id_pool
        flagged: list[str] = []
        for spell_id in sorted(scoped_spell_ids):
            if spell_id == target_spell_id:
                continue
            dependency = spell_id_pool.get(spell_id)
            if dependency is None or dependency._spellbook is not spellbook:
                continue
            if not dependency.resolvable or dependency.is_existing_creation:
                continue
            with dependency._lock:
                if (
                        dependency.resolution_required
                        or dependency._compiler_artifact._spell_codegen_creation is not None
                        or dependency._creation_context_switch.state >= 2
                ):
                    continue
                dependency.resolution_complete = False
                dependency.resolution_required = True
                dependency._door_epoch += 1
            flagged.append(spell_id)
        return tuple(flagged)

'''
session.insert_before(CREATION, "    @staticmethod\n    def _register_conduit_resolution_phases(\n", FLAG)

# --- Meld: the deferred lane routing ----------------------------------------------------------------------------
session.replace(
    MELD,
    "            - When required, runs exactly one deferred target-local plan pass\n"
    "              (`8-11`) under the spell lock.\n",
    "            - When required, runs exactly one target-local pass under the\n"
    "              spell's rebuild window and lock: the deferred plan pass\n"
    "              (`8-11`) for an existing creation or a spell that is its\n"
    "              current Phase 5 root; otherwise the full target pass\n"
    "              (`5-11`), which must leave the spell resolution-valid for the\n"
    "              conduit (0.2.8215). A dependency first compiled only inside a\n"
    "              consumer's plan has no Phase 5 root blueprint, and the 8-11\n"
    "              pass skips such a spell.\n",
)
session.replace(
    MELD,
    "            - On failure: preserves `resolution_required=True` and\n"
    "              `resolution_complete=False`, then re-raises.\n",
    "            - On failure: preserves `resolution_required=True` and\n"
    "              `resolution_complete=False`, bumps `_door_epoch`, then\n"
    "              re-raises.\n",
)
session.replace(
    MELD,
    "            RuntimeError: If no resolution conduit id is available.\n"
    "            Exception: Re-raises deferred resolution failures.\n",
    "            RuntimeError: If no resolution conduit id is available.\n"
    "            SpellbookValidationError: If a full target pass leaves the spell\n"
    "                unresolved for the conduit.\n"
    "            Exception: Re-raises deferred resolution failures.\n",
)
session.replace(
    MELD,
    "            try:\n"
    "                spellbook._run_deferred_resolution_phases_for_target_spell(\n"
    "                    conduit_id,\n"
    "                    spell,\n"
    "                )\n"
    "            except Exception:\n",
    "            try:\n"
    "                if self._requires_own_target_pass(spell):\n"
    "                    # No Phase 5 root blueprint: the 8-11 pass would skip this\n"
    "                    # spell, so its own full target pass (5-11) builds its plan.\n"
    "                    spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)\n"
    "                    self._raise_unless_resolution_valid(spell, conduit_id)\n"
    "                else:\n"
    "                    spellbook._run_deferred_resolution_phases_for_target_spell(\n"
    "                        conduit_id,\n"
    "                        spell,\n"
    "                    )\n"
    "            except Exception:\n",
)
LANE_HELPERS = '''    def _requires_own_target_pass(self, spell: Spell) -> bool:
        """
        Decide whether a flagged spell needs its full target pass rather than
        the deferred 8-11 pass.

        Contract:
            - True for a constructed spell that is not its current Phase 5
              root. The 8-11 pass skips a spell without a Phase 5 root
              blueprint (`SpellbookCreationSystem._is_spell_plan_phase_eligible`),
              so only the full pass (5-11) builds its plan. That is the state
              of a dependency a consumer's target-local pass compiled only
              inside the consumer's plan and flagged
              (`SpellbookCreationSystem.flag_dependencies_without_own_plan`).
            - False for an existing creation (it never plans) and for a spell
              that is its current Phase 5 root (the 8-11 pass rebuilds its
              plan, as before 0.2.8215).
            - Reads compiler state only; mutates nothing.

        Args:
            spell: The flagged spell, under its rebuild window and lock.

        Returns:
            bool: True when the full target pass must run.
        """
        if spell.is_existing_creation:
            return False
        return not self._get_spell_compiler_system().is_current_spell_phase5_root(spell)

    def _raise_unless_resolution_valid(self, spell: Spell, conduit_id: str) -> None:
        """
        Confirm that a spell's own full target pass left it resolution-valid
        for the conduit.

        Contract:
            - Reads the effective conduit-local verdict
              (`_get_resolution_validity`) after the pass; valid returns.
            - Anything else raises SpellbookValidationError. A visibility
              failure records invalid verdicts and returns without raising;
              marking that spell complete would only move the failure into the
              CreationContext build.

        Args:
            spell: The spell whose full target pass just ran.
            conduit_id: The resolution conduit id the pass ran for.

        Raises:
            SpellbookValidationError: When the verdict is not valid.
        """
        resolution_state = spell._spell_system_states.get_conduit_resolution_state(conduit_id)
        if self._get_resolution_validity(spell, resolution_state) is not SpellValidity.valid:
            raise SpellbookValidationError([spell])

'''
session.insert_before(MELD, "    def _get_cached_change_control_manager(\n", LANE_HELPERS)

# --- Comments that gave the old lane as a reason ----------------------------------------------------------------
session.replace(
    BOOK,
    "        # a freshly bound spell. resolution_required=True would instead route the\n"
    "        # deferred 8-11 lane, which cannot compile a member with no phase-5\n"
    "        # blueprint.\n",
    "        # a freshly bound spell. (Before 0.2.8215 resolution_required=True would\n"
    "        # have routed the deferred 8-11 lane, which could not compile a member\n"
    "        # with no phase-5 blueprint; that lane now runs the full target pass for\n"
    "        # such a spell, but the verdict-driven validation lane stays the owner of\n"
    "        # this recompile.)\n",
)
session.replace(
    BOOK,
    "                    # post-conjure spells get compiled via the gated revalidation\n"
    "                    # paths, not via a deferred-resolution flag.\n",
    "                    # post-conjure spells get compiled via the gated revalidation\n"
    "                    # paths, not via a deferred-resolution flag. One exception\n"
    "                    # (0.2.8215): a spell first compiled only inside a consumer's\n"
    "                    # target-local pass is flagged resolution_required there\n"
    "                    # (SpellbookCreationSystem.flag_dependencies_without_own_plan),\n"
    "                    # and its first direct meld runs its own full target pass.\n",
)
session.replace(
    REBUILD,
    "              unpublished; its next meld runs the normal validation path. It is\n"
    "              NOT marked resolution_required: that routes the deferred 8-11\n"
    "              lane, which cannot compile a spell without a Phase-5 blueprint.\n"
    "            - Resolution flags stay with the producers that ran the phases.\n",
    "              unpublished; its next meld runs the normal validation path. It is\n"
    "              NOT marked resolution_required here (before 0.2.8215 that flag\n"
    "              routed a deferred 8-11 pass, which could not compile a spell\n"
    "              without a Phase-5 blueprint; the deferred lane now runs the full\n"
    "              target pass for such a spell).\n"
    "            - Resolution flags stay with the producers that ran the phases; a\n"
    "              target-local pass flags the dependencies it compiled without a\n"
    "              plan of their own (0.2.8215).\n",
)

long_lines = session.long_added_lines()
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write())

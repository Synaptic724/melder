"""Regression: BUG-071 (2026-07-17 audit) - failed upgrade commits nothing.

Symptom:
    `Conduit.upgrade_to_normal()` mutated state, root identity, name, pool,
    ward, spellbook, and root registration BEFORE validating the supplied
    hooks. An invalid hook payload then raised - but the conduit was already
    normal, renamed, self-rooted, and re-registered. Callers received a
    failure while the topology had committed, and retry was impossible
    because only a lesser conduit may be upgraded.

Contract under test:
    The hooks payload is validated before the first mutation: an invalid
    mapping fails the upgrade with zero state change, and the same conduit
    can then be upgraded successfully on retry.
"""

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduationWorld,
)

graduation_world = graduation_support.graduation_world
isolated_graduation_roots = graduation_support.isolated_graduation_roots


def test_invalid_hook_name_fails_upgrade_with_zero_state_change(
    graduation_world: GraduationWorld,
) -> None:
    """The audited repro: an unknown hook name must not commit the upgrade.

    Contract assertions:
        - The call raises the hook-validation ValueError.
        - The conduit is STILL lesser, keeps its name and root id, keeps its
          pool, and no ward/spellbook/registration step ran (broken code:
          normal, renamed 'should-not-commit', self-rooted, registered).
        - The same conduit upgrades successfully on retry (broken code:
          retry refused because the state was already normal).
    """
    conduit = graduation_world.child
    old_name = conduit._name
    old_root_id = conduit._root_conduit_id
    old_pool = conduit._conduit_pool
    old_creations = conduit._creations

    with pytest.raises(ValueError, match="Unknown hook name"):
        conduit.upgrade_to_normal(
            name="should-not-commit",
            hooks={"not_a_real_hook": lambda: None},
        )

    assert conduit._conduit_state == ConduitState.lesser, (
        "a failed upgrade left the conduit normal "
        "(the audited BUG-071 symptom)"
    )
    assert conduit._name == old_name
    assert conduit._root_conduit_id == old_root_id
    assert conduit._conduit_pool is old_pool
    assert conduit._spellbook is graduation_world.book
    assert conduit._conduit_ward._parent_conduit is graduation_world.root
    assert conduit.id not in conduit._aetheric_frame._conduits

    # Recovery by retry - impossible on the broken code.
    conduit.upgrade_to_normal(name="alpha")

    assert conduit._conduit_state == ConduitState.normal
    assert conduit._name == "alpha"
    assert conduit._root_conduit_id == conduit._id
    assert conduit._creations is old_creations
    assert conduit._conduit_ward._parent_conduit is None
    assert conduit._aetheric_frame._conduits[conduit.id] is conduit
    assert conduit._spellbook.conduit is conduit


def test_non_callable_hook_value_fails_upgrade_with_zero_state_change(
    graduation_world: GraduationWorld,
) -> None:
    """The TypeError validation lane must also commit nothing.

    Contract assertions:
        - A non-callable hook value raises TypeError before any mutation.
        - The conduit remains lesser with its original identity fields.
    """
    conduit = graduation_world.child
    old_name = conduit._name
    old_root_id = conduit._root_conduit_id

    with pytest.raises(TypeError, match="must be a callable"):
        conduit.upgrade_to_normal(
            name="should-not-commit",
            hooks={"on_conduit_post_link": 42},
        )

    assert conduit._conduit_state == ConduitState.lesser
    assert conduit._name == old_name
    assert conduit._root_conduit_id == old_root_id
    assert conduit._conduit_ward._parent_conduit is graduation_world.root
    assert conduit._spellbook is graduation_world.book
    assert conduit.id not in conduit._aetheric_frame._conduits


def test_valid_hooks_still_register_during_upgrade(
    graduation_world: GraduationWorld,
) -> None:
    """Behavior guard: a valid hooks payload upgrades and registers hooks.

    Contract assertions:
        - The upgrade completes to normal.
        - The supplied hook is registered on the upgraded conduit's local
          hook surface (validation-then-registration, not validation-only).
    """
    conduit = graduation_world.child
    events = []

    def post_link_hook(left: Conduit, right: Conduit) -> None:
        """Recording hook double."""
        events.append((left, right))

    conduit.upgrade_to_normal(
        name="alpha",
        hooks={"on_conduit_post_link": post_link_hook},
    )

    assert conduit._conduit_state == ConduitState.normal
    assert conduit.link(graduation_world.root)
    assert events == [(conduit, graduation_world.root)]

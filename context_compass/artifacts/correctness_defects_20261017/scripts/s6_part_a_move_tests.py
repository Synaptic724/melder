"""Move the 13 integration tests that built a second managed version from one class's settings to the new rule.

A managed spell's settings are not part of its spell_id (0.2.8254), so a second version must differ in identity:
its disposal names (the Keeper precedent of the transfer suite), another class, or another binding name. Each test
keeps its intent. Run from the repository root:
    python3 context_compass/artifacts/correctness_defects_20261017/scripts/s6_part_a_move_tests.py [--dry-run]
"""
import pathlib
import sys

DRY = "--dry-run" in sys.argv
writes = {}


def load(path):
    p = pathlib.Path(path)
    if p not in writes:
        writes[p] = p.read_text(encoding="utf-8")
    return p


def sub(path, old, new):
    p = load(path)
    assert writes[p].count(old) == 1, (path, old[:90], writes[p].count(old))
    writes[p] = writes[p].replace(old, new, 1)


RELEASE = "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py"
TRANSFER = "tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py"
RECORD = "tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py"
OPTIONS = "tests/integration/melder/spellbook/test_managed_bind_options_integration.py"
QUANTITY = "tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py"
POOL = "tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py"

# Release: same class, two versions; the second differs by its disposal names (settings alone no longer do).
sub(RELEASE,
    '''    """Two versions of one index: the active one takes a same-class release; a notch moves it."""''',
    '''    """
    Two versions of one index: the active one takes a same-class release; a notch moves it.

    The parked version differs by its disposal names: a managed spell's settings are not part of its spell_id
    (0.2.8254), so the same class with only another limit would be the same spell.
    """''')
sub(RELEASE,
    "            existence=Existence.managed_spell_quantity, permissions=\"create\", disposal_method_names=[\"close\"],\n"
    "            managed_spell_limit=8,\n",
    "            existence=Existence.managed_spell_quantity, permissions=\"create\",\n"
    "            disposal_method_names=[\"close\", \"reset\"], managed_spell_limit=8,\n")

# Transfer: Session gains a second disposal step; the parked version names both.
sub(TRANSFER,
    '''    def close(self) -> None:
        """The disposal method: mark closed."""
        self.closed = True
''',
    '''    def close(self) -> None:
        """The disposal method: mark closed."""
        self.closed = True

    def flush(self) -> None:
        """A second disposal step the parked version names, so it is a version of its own (0.2.8254)."""
''')
sub(TRANSFER,
    "        target_class: Session (limit 8) or Keeper (disposal \"close\").\n",
    "        target_class: Session (limit 8, disposal \"close\" and \"flush\": a managed spell's settings are not part\n"
    "            of its spell_id since 0.2.8254, so the disposal names make the second version) or Keeper (disposal\n"
    "            \"close\").\n")
sub(TRANSFER,
    "                                        existence=Existence.managed_spell_quantity, permissions=\"create\",\n"
    "                                        disposal_method_names=[\"close\"], managed_spell_limit=8)\n",
    "                                        existence=Existence.managed_spell_quantity, permissions=\"create\",\n"
    "                                        disposal_method_names=[\"close\", \"flush\"], managed_spell_limit=8)\n")

# Record: the parked member differs by its disposal names; both still carry their own recorded settings.
sub(RECORD,
    "through bind, so each rebuilt version gets the same normalized options - and therefore the same spell id - as the\n"
    "recorded one. An active member and a parked member are covered on both lanes. Managed spells are not melded here:\n",
    "through bind, so each rebuilt version gets the same normalized options, and the same spell id, as the recorded one.\n"
    "An active member and a parked member are covered on both lanes; the parked member differs by its disposal names,\n"
    "since a managed spell's settings are not part of its spell_id (0.2.8254). Managed spells are not melded here:\n")
sub(RECORD,
    "    parked_id = root.bind_inactive(\n"
    "        spell=RecordedPool, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
    "        existence=Existence.managed_spell_quantity, **PARKED_OPTIONS,\n"
    "    )\n",
    "    parked_id = root.bind_inactive(\n"
    "        spell=RecordedPool, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
    "        existence=Existence.managed_spell_quantity, disposal_method_names=[\"flush\"], **PARKED_OPTIONS,\n"
    "    )\n")

# Options: a managed binding moves the id, its settings do not; the parked version differs by disposal names.
sub(OPTIONS,
    '''def test_a_managed_binding_and_its_options_each_change_the_spell_id() -> None:
    """The same class bound unique, managed by default, and managed with a limit gets three ids."""''',
    '''def test_a_managed_binding_changes_the_spell_id_and_its_settings_do_not() -> None:
    """The same class bound unique and managed gets two ids; managed with a limit keeps the managed one (0.2.8254)."""''')
sub(OPTIONS,
    "    assert len(set(ids)) == 3\n",
    "    assert ids[0] != ids[1]\n"
    "    assert ids[1] == ids[2]\n")
sub(OPTIONS,
    '''    """A root binds a managed class after conjure, then parks a second version with other options."""''',
    '''    """A root binds a managed class after conjure, then parks a second version (other disposal names) with its own."""''')
sub(OPTIONS,
    "            spell=PooledLogger, spell_index=active.spell_index, existence=Existence.managed_spell_quantity,\n"
    "            managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=16, managed_spell_reset_methods=[\"reset\"],\n",
    "            spell=PooledLogger, spell_index=active.spell_index, existence=Existence.managed_spell_quantity,\n"
    "            disposal_method_names=[\"flush\"], managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=16,\n"
    "            managed_spell_reset_methods=[\"reset\"],\n")

# Quantity: the second version is another class (Session has no method a disposal list could name).
sub(QUANTITY,
    '''class Handler:
    """A `many` holder of one Session."""''',
    '''class SessionNext(Session):
    """
    A second version's class: a managed spell's settings are not part of its spell_id (0.2.8254), so a version of
    its own needs another class (or address, or disposal names).
    """


class Handler:
    """A `many` holder of one Session."""''')
sub(QUANTITY,
    "        parked_id = root.bind_inactive(\n"
    "            spell=Session, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
    "            existence=Existence.managed_spell_quantity, permissions=\"create\", managed_spell_limit=8,\n"
    "        )\n",
    "        parked_id = root.bind_inactive(\n"
    "            spell=SessionNext, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
    "            existence=Existence.managed_spell_quantity, permissions=\"create\", managed_spell_limit=8,\n"
    "        )\n")
sub(QUANTITY,
    "        new = root.meld(spell=Session)\n"
    "        assert new is not old\n",
    "        new = root.meld(spell=SessionNext)\n"
    "        assert new is not old\n")

# Pool: the parked version has no disposal names, so it is a version of its own with its own pool and limit.
sub(POOL,
    "            existence=Existence.managed_spell_quantity, permissions=\"create\", disposal_method_names=[\"close\"],\n"
    "            managed_spell_limit=8,\n"
    "        )\n"
    "        active_pool = root._creations.get_managed_quantity(active_id)\n",
    "            existence=Existence.managed_spell_quantity, permissions=\"create\", disposal_method_names=[],\n"
    "            managed_spell_limit=8,\n"
    "        )\n"
    "        # No disposal names: a version of its own (0.2.8254: a managed spell's settings are not in its spell_id).\n"
    "        active_pool = root._creations.get_managed_quantity(active_id)\n")

for p, text in writes.items():
    before = set(p.read_text(encoding="utf-8").splitlines())
    long = [line for line in text.splitlines() if line not in before and len(line) > 120]
    assert not long, (p, long[:3])
    if not DRY:
        p.write_text(text, encoding="utf-8")
    print(("checked " if DRY else "wrote ") + str(p))

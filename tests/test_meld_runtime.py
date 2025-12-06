import unittest

from melder.spellbook.spellbook import Spellbook
from melder.spellbook.spellbinder import SpellBinder
from melder.spellbook.existence.existence import Existence


# Simple spells for exercising Meld
class Repo:
    def __init__(self):
        self.name = "repo"


class Service:
    def __init__(self, repo: Repo):
        self.repo = repo


class Controller:
    def __init__(self, service: Service):
        self.service = service


class Worker:
    def __init__(self):
        self.touched = True


def _bind_spell(binder: SpellBinder, spell, *, existence: Existence = Existence.unique_per_conduit):
    binder.bind(spell).with_existence(existence).finalize()


class MeldRuntimeTests(unittest.TestCase):
    def test_basic_meld_resolution(self):
        spellbook = Spellbook()
        binder = spellbook.create_binder()

        _bind_spell(binder, Repo, existence=Existence.unique_per_conduit)
        _bind_spell(binder, Service, existence=Existence.many)
        _bind_spell(binder, Controller, existence=Existence.many)

        conduit = spellbook.conjure()
        controller = conduit.meld(Controller)

        self.assertIsInstance(controller, Controller)
        self.assertIsInstance(controller.service, Service)
        self.assertIsInstance(controller.service.repo, Repo)

    def test_spell_override_on_root(self):
        spellbook = Spellbook()
        binder = spellbook.create_binder()

        _bind_spell(binder, Repo, existence=Existence.unique_per_conduit)
        _bind_spell(binder, Service, existence=Existence.many)

        conduit = spellbook.conjure()
        custom_repo = Repo()
        custom_repo.name = "custom"

        service = conduit.meld(Service, spell_override={"repo": custom_repo})
        self.assertIs(service.repo, custom_repo)
        self.assertEqual(service.repo.name, "custom")

    def test_unique_per_spell_space_reuse_and_isolation(self):
        spellbook = Spellbook()
        binder = spellbook.create_binder()
        _bind_spell(binder, Worker, existence=Existence.unique_per_spell_space)

        conduit = spellbook.conjure()

        with conduit.enter_spellspace():
            first = conduit.meld(Worker)
            second = conduit.meld(Worker)
            self.assertIs(first, second)  # reuse inside same spellspace

        with conduit.enter_spellspace():
            third = conduit.meld(Worker)
            self.assertIsNot(third, first)  # new spellspace => new instance


if __name__ == "__main__":
    unittest.main()

import pytest

from melder.spellbook.spellbook import Spellbook
from melder.spellbook.spellbinder import SpellBinder
from melder.spellbook.existence.existence import Existence


# Simple spell definitions for testing
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


def test_basic_meld_resolution():
    spellbook = Spellbook()
    binder = spellbook.create_binder()

    _bind_spell(binder, Repo, existence=Existence.unique_per_conduit)
    _bind_spell(binder, Service, existence=Existence.many)
    _bind_spell(binder, Controller, existence=Existence.many)

    conduit = spellbook.conjure()

    controller = conduit.meld(Controller)
    assert isinstance(controller, Controller)
    assert isinstance(controller.service, Service)
    assert isinstance(controller.service.repo, Repo)


def test_spell_override_on_root():
    spellbook = Spellbook()
    binder = spellbook.create_binder()

    _bind_spell(binder, Repo, existence=Existence.unique_per_conduit)
    _bind_spell(binder, Service, existence=Existence.many)

    conduit = spellbook.conjure()

    custom_repo = Repo()
    custom_repo.name = "custom"

    service = conduit.meld(Service, spell_override={"repo": custom_repo})
    assert service.repo is custom_repo
    assert service.repo.name == "custom"


def test_unique_per_spell_space_reuse_and_isolation():
    spellbook = Spellbook()
    binder = spellbook.create_binder()
    _bind_spell(binder, Worker, existence=Existence.unique_per_spell_space)

    conduit = spellbook.conjure()

    with conduit.enter_spellspace():
        first = conduit.meld(Worker)
        second = conduit.meld(Worker)
        assert first is second  # reuse inside same spellspace

    with conduit.enter_spellspace():
        third = conduit.meld(Worker)
        assert third is not first  # new spellspace => new instance


"""A stand-in for S3's store rule, to check that the module's defect tests turn green when it holds.

Not a fix and not repository code: a monkeypatch of `Creations.register_many` that moves an entry whose slot is not
a list, or whose record holds another disposal list, to a side key of the same store before registering, so the old
objects keep their own list (STORY-2026-10-18-revalidate_on_binding_change: "a changed one retires the old entry -
its objects stay alive and are torn down with their own disposal list - before the new binding builds").

To rerun: copy this file as `conftest.py` beside a copy of
tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py in an empty
scratch folder outside the repository, and run pytest there with PYTHONPATH pointing at the repository's src/.
Expected: the four defect cases XPASS(strict) (reported as failures) and the six controls pass.
"""
import pytest

from melder.aether.conduit.creations.creations import Creations, ManyDisposalBucket

_original = Creations.register_many


def _retire_then_register(self, key, item, disposal_methods):
    # S3's requirement: "a changed one retires the old entry - its objects stay alive and are torn down with their own
    # disposal list - before the new binding builds". Stand-in: move the old entry to a side key in the same store.
    with self._lock:
        slot = self._creations.get(key)
        record = self._disposable_creations.get(key)
        changed = slot is not None and not isinstance(slot, list)
        if isinstance(record, ManyDisposalBucket) and list(record.methods) != list(disposal_methods):
            changed = True
        if changed:
            side = f"{key}#retired-{id(slot)}"
            self._creations[side] = self._creations.pop(key)
            if record is not None:
                self._disposable_creations[side] = self._disposable_creations.pop(key)
    return _original(self, key, item, disposal_methods)


@pytest.fixture(autouse=True)
def s3_stand_in(monkeypatch):
    monkeypatch.setattr(Creations, "register_many", _retire_then_register)
    yield

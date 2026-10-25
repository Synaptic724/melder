"""The release-note example of STORY-2026-10-25-probe_and_purge_reach_every_version, run as written (melder_1)."""
import melder as md


class Report:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


book = md.Spellbook()
v1 = book.bind(spell=Report, existence="unique", disposal_method_names=["close"])
root = book.conjure(dynamic=True)
first = root.meld(spell_id=v1)


class Report:  # version 2: the same name, new code
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def render(self) -> str:
        return "v2"


index = root.get_spell_by_spell_id(v1).spell_index
v2 = root.bind_inactive(spell=Report, spell_index=index, existence="unique", disposal_method_names=["close"])
root.notch_spell(spell_index=index, spell_id=v2)    # version 1 is parked; its object is kept
second = root.meld(spell_id=v2)

print("has_live_creation(v1):", root.has_live_creation(spell=v1))
print("purge(v1):", root.purge(spell_id=v1), "first.closed:", first.closed, "second.closed:", second.closed)
print("has_live_creation(v1) after:", root.has_live_creation(spell=v1))
print("describe(v1) spell_id is v1:", root.describe_live_creation_status(spell=v1)["spell_id"] == v1)
try:
    root.meld(spell_id=v1)
except KeyError as error:
    print("meld(v1):", type(error).__name__, error)
active = root.get_spell_by_index_id(root.get_spell_by_spell_id(v1).spell_index.id).spell_id
print("v1 active:", active == v1, "v2 active:", active == v2)
try:
    root.purge(spell_id="0" * 64)
except KeyError as error:
    print("unknown spell_id:", type(error).__name__, error)
root.cleanup()
book.cleanup()

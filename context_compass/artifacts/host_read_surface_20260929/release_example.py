from melder import Aether, Spellbook

aether = Aether()
assert aether.find_frame("ops") is None          # looking creates nothing
book = Spellbook(aetheric_frame="ops")           # constructing a Spellbook creates the frame
frame = aether.get_frame("ops")
root = book.conjure(name="root")
assert root.spellbook is book
assert frame.shared_spellbook_configuration is None   # this frame does not share one
print(aether.list_frame_names())                 # ('ops',)

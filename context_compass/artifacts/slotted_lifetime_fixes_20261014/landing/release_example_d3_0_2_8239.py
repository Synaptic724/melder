import melder as md


class Tool:
    def __init__(self) -> None:
        self.closes = 0

    def close(self) -> None:
        self.closes += 1


class Worker:
    def __init__(self, tool: Tool) -> None:
        self.tool = tool


book = md.Spellbook()
tool_id = book.bind(spell=Tool, existence="unique", disposal_method_names=["close"])
book.bind(spell=Worker, existence="unique_per_conduit")
owner = book.conjure(dynamic=True, name="owner")
target = md.Spellbook().conjure(dynamic=True, name="target")

worker = owner.meld("Worker")
report = owner.transfer_spell_ownership(spell=tool_id, target_conduit=target)
print("options.move_creations =", report["options"]["move_creations"])
assert target.meld("Tool") is worker.tool     # 0.2.8238 built a second Tool here
owner.cleanup()                                # leaves the Tool open: the target owns it now
assert worker.tool.closes == 0
target.cleanup()                               # closes it, once
assert worker.tool.closes == 1
print("example ok")

# opt-out
book2 = md.Spellbook(aetheric_frame="optout")
t2 = book2.bind(spell=Tool, existence="unique", disposal_method_names=["close"])
o2 = book2.conjure(dynamic=True, name="owner2")
g2 = md.Spellbook(aetheric_frame="optout").conjure(dynamic=True, name="target2")
first = o2.meld(spell_id=t2)
o2.transfer_spell_ownership(spell=t2, target_conduit=g2, move_creations=False)
second = g2.meld(spell_id=t2)
print("opt-out builds anew:", second is not first)
o2.cleanup(); g2.cleanup()
print("opt-out first closes:", first.closes, "second closes:", second.closes)

"""C4's world (Dep under the category "Dep", Dep2 staged there, notch, notch back) through three lookups."""
import melder as md


class Dep:
    """Version 1."""

    def tag(self) -> str:
        """Return the version tag."""
        return "d1"


class Dep2(Dep):
    """Version 2: a renamed subclass, staged into Dep's index."""

    def tag(self) -> str:
        """Return the version tag."""
        return "d2"


class PClass:
    """Asks for the class."""

    def __init__(self, dep: Dep) -> None:
        self.dep = dep


class PFrame:
    """Asks through the frame (the interface dict), default binding."""

    def __init__(self, dep=md.SpellMap(spellframe="Dep")) -> None:
        self.dep = dep


def run(label: str, consumer: type) -> None:
    """Bind, meld, stage Dep2, notch, meld, notch back, meld."""
    book = md.Spellbook(aetheric_frame=f"c4probe_{label}")
    dep_id = book.bind(spell=Dep, existence="many", permissions="create", spellframe="Dep")
    book.bind(spell=consumer, existence="many", permissions="create")
    root = book.conjure(dynamic=True, name=f"root_{label}")
    try:
        index = book.find_spell_by_spell_id(dep_id).spell_index

        def meld() -> str:
            try:
                return root.meld(spell=consumer).dep.tag()
            except Exception as error:  # the probe reports what a caller would see
                return f"raises {type(error).__name__}"

        before = meld()
        new_id = root.bind_inactive(spell=Dep2, spell_index=index, existence="many", permissions="create",
                                    spellframe="Dep")
        root.notch_spell(spell_index=index, spell_id=new_id)
        after = meld()
        root.notch_spell(spell_index=index, spell_id=dep_id)
        back = meld()
        door = root.meld(spellframe="Dep").tag()
        print(f"  {label:34s} before={before:10s} after_notch={after:28s} after_notch_back={back:10s}"
              f" meld(spellframe='Dep')={door}")
    finally:
        root.cleanup()


run("class annotation  dep: Dep", PClass)
run("frame  SpellMap(spellframe='Dep')", PFrame)

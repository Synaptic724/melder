"""
TIER: expert (36)
GOAL: NOTHING IN THIS FILE EXISTS WHEN THE PROCESS STARTS. Three classes
      are written as text at runtime, become real importable modules with
      no file on disk, get bound as spells, and come out as LIVE OBJECTS
      that do actual work. Then we make more of them.

      This is the demo. Everything else in the tier explains a rule; this
      one just does the thing.

      THE LOOP, ONE MORE TIME BUT WITH A PAYOFF
        validate_codegen     may this exist?
        materialize_codegen  make it a real module
        import               it resolves like anything else
        bind                 it becomes a spell with custody
        meld                 you get an OBJECT
      Five steps from a string to something you can call a method on.

      AND THE OBJECTS ARE ORDINARY. That is the part worth sitting with.
      Once melded, a generated class is not a special "dynamic" thing you
      handle with tongs. It is an object. It has state, you call methods
      on it, you pass it around, it participates in the same lifecycle as
      a class you typed by hand. The generated-ness stops mattering the
      moment it lands.

      MULTIPLE OBJECTS FROM ONE GENERATED CLASS. `existence="many"` means
      every meld builds a NEW instance, so an agent can write one class
      and you can run a hundred independent copies of it - separate state,
      no shared surprises. `existence="unique"` gives you the same object
      back every time. Same generated source, two population models, and
      you choose per binding.

      WHY THIS SURVIVES A REBOOT, IN ONE LINE: the module has no file, so
      its SOURCE IS THE RECORD (expert 33). A world made of generated code
      is reproducible rather than merely re-runnable - which is what makes
      any of this more than a clever trick.
SURFACE EXERCISED: validate_codegen / materialize_codegen, Spellbook.bind
                   with existence unique and many, Conduit.meld, and the
                   generated objects actually running
VERIFY: authored 2026-08-05; not yet run.
"""
import importlib

import melder as md


FRAME = "build-world"

# An agent's output. Three cooperating pieces, written as text.
TOKENIZER = '''"""Generated: split raw text into words."""


class Tokenizer:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, text: str) -> list:
        self.calls = self.calls + 1
        return [word.strip(".,!?").lower()
                for word in text.split()
                if word.strip(".,!?")]
'''

COUNTER = '''"""Generated: count how often each word appears."""


class Counter:
    def __init__(self) -> None:
        self.total = 0

    def run(self, words: list) -> dict:
        counts: dict = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
            self.total = self.total + 1
        return counts
'''

REPORTER = '''"""Generated: turn counts into a readable line."""


class Reporter:
    def __init__(self) -> None:
        self.rendered = 0

    def run(self, counts: dict) -> str:
        self.rendered = self.rendered + 1
        top = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
        return ", ".join("%s=%d" % (word, n) for word, n in top[:3])
'''

# A fourth piece, for the population demo. It gets its OWN class name
# rather than re-binding Counter: two INDEPENDENT binds of one class
# would put two visible spells under the name "Counter", and the
# structural validator refuses that outright (expert 30).
WORKER = '''"""Generated: an independent accumulator."""


class Worker:
    def __init__(self) -> None:
        self.total = 0

    def run(self, jobs: list) -> int:
        self.total = self.total + len(jobs)
        return self.total
'''

PARTS = (
    ("build_tokenizer", TOKENIZER, "Tokenizer"),
    ("build_counter", COUNTER, "Counter"),
    ("build_reporter", REPORTER, "Reporter"),
)

TEXT = ("the record is the record and the record outlives the runtime, "
        "so the record is what you trust")


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )

    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    conduit = book.conjure(name="build-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="builder")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    print("the process is up and NONE of the three classes exist yet")
    print()

    # WRITE THEM. Validate, materialize, import, bind - per piece.
    classes = {}
    for module_name, source, class_name in PARTS:
        verdict = commands.validate_codegen(source, frame_name=FRAME)
        assert verdict["accepted"] is True, verdict
        kept = commands.materialize_codegen(
            source, module_name=module_name, frame_name=FRAME,
        )
        assert kept["materialized"] is True, kept
        module = importlib.import_module(module_name)
        classes[class_name] = getattr(module, class_name)
        book.bind(spell=classes[class_name], existence="unique",
                  permissions="create", binding_name=class_name.lower())
        print("wrote %-9s -> module %-16s -> bound as '%s'"
              % (class_name, module_name, class_name.lower()))

    # MELD THEM. Now they are objects.
    tokenizer = conduit.meld(spell=classes["Tokenizer"],
                             binding_name="tokenizer")
    counter = conduit.meld(spell=classes["Counter"], binding_name="counter")
    reporter = conduit.meld(spell=classes["Reporter"],
                            binding_name="reporter")
    print()
    print("melded three OBJECTS:", type(tokenizer).__name__,
          type(counter).__name__, type(reporter).__name__)

    # RUN THE THING. This is real work done by code that did not exist
    # when this script started.
    words = tokenizer.run(TEXT)
    counts = counter.run(words)
    line = reporter.run(counts)
    print()
    print("input :", TEXT[:58], "...")
    print("output:", line)
    assert "record" in line, line
    assert counts["record"] == 4, counts
    print()
    print("that answer was computed by three classes an agent wrote as")
    print("strings, in this process, a few milliseconds ago")

    # THEY HAVE STATE, like any object.
    assert tokenizer.calls == 1
    assert counter.total == len(words)
    assert reporter.rendered == 1
    print()
    print("and they are ORDINARY objects: tokenizer.calls =",
          tokenizer.calls, "| counter.total =", counter.total)
    print("  no tongs required. Generated-ness stopped mattering the")
    print("  moment they landed")

    # UNIQUE MEANS THE SAME OBJECT BACK.
    again = conduit.meld(spell=classes["Tokenizer"],
                         binding_name="tokenizer")
    assert again is tokenizer, "existence='unique' returns the same object"
    print()
    print("melding 'tokenizer' again -> the SAME object:",
          again is tokenizer)

    # MANY MEANS A NEW ONE EVERY TIME - a population from one generated
    # class. This is its own class rather than a second binding of
    # Counter: two independent binds of one class would put two visible
    # spells under the same name, which the validator refuses (expert 30).
    commands.validate_codegen(WORKER, frame_name=FRAME)
    kept = commands.materialize_codegen(
        WORKER, module_name="build_worker", frame_name=FRAME,
    )
    assert kept["materialized"] is True, kept
    worker_class = importlib.import_module("build_worker").Worker
    book.bind(spell=worker_class, existence="many", permissions="create",
              binding_name="worker")

    workers = [conduit.meld(spell=worker_class, binding_name="worker")
               for _ in range(5)]
    assert len({id(worker) for worker in workers}) == 5, (
        "existence='many' must build a NEW instance per meld"
    )
    for index, worker in enumerate(workers):
        worker.run(["job"] * (index + 1))
    totals = [worker.total for worker in workers]
    assert totals == [1, 2, 3, 4, 5], totals
    print()
    print("a fourth generated class, bound existence='many':")
    print("  5 melds ->", len({id(w) for w in workers}), "distinct objects")
    print("  independent state:", totals)
    print("  one class an agent wrote, a population you control")

    print()
    print("string -> module -> spell -> object -> answer")
    print("and the module has no file, so its SOURCE IS THE RECORD -")
    print("which is why this world can be rebuilt, not just re-run")


if __name__ == "__main__":
    main()

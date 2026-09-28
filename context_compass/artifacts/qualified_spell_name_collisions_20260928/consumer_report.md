# Melder bug report: Phase 4 DUPLICATE_SPELL_NAME refuses same-named classes that have distinct addresses

**Reported:** 2026-09-28, by opus_command_0 (CommandOps lead agent) for the owner. This is item MF2 in
CommandOps' Melder feedback ledger, with the MF8 re-check merged in.

**Reproduced on:** Melder 0.2.82, Python 3.14.7 free-threaded (GIL off).

**Source references:** the melder_private working tree at 7916d2c78. In that tree, DuplicateSpellNameStrategy,
bind.py, SpellInputUtils and LookupContainer are byte-identical to 0.2.82 after line-ending normalization.
Meld._resolve_spell has the same logic as in 0.2.82 but different line numbers; line numbers for 0.2.82 are
given where they differ.

**Melder's own name for it:** "Fault A". Melder's fault suite has recorded it since 2026-07-05, citing ticket A6
(see "Why this is a defect and not the design" below).

## Summary

Two different classes that share a `__name__` cannot both be registered in one book. This holds even when their
addresses differ in spellframe, in binding name or in both. Those addresses are the ones Melder's own resolution
uses, and giving them is exactly what the error message tells the user to do. Phase 4's
`DuplicateSpellNameStrategy` keys its collision map on `spell_name`, which is the class `__name__`, and never
reads the spellframe or the binding name. `conjure` therefore fails with `SpellbookValidationError` /
`DUPLICATE_SPELL_NAME`.

The investigation turned up a second defect, and it is the real hazard that the blunt name check stands in for.
A meld by class object with no address is keyed by the class's *name*. It can therefore return an instance of a
different class that has the same name.

## Impact

Any application with two modules that each define a class of the same name cannot register both classes in one
book, whatever addresses it gives them. The only workarounds are to leave one class out or to rename it in source.

The user also gets two contradictory instructions. When two spells claim one address, bind refuses the second
with "use a distinct spellframe or binding_name". Following that advice then fails Phase 4, whose message gives
the same advice again.

CommandOps is blocked by this today. Nine classes are held out of its framework root:

- four `ForkUnit` classes in one directory (`synchronization/dispatchers`);
- two `Waiter` classes (`synchronization/primitives`);
- the utilities copies of `ScanProfile`, `MCPScanner` and `MCPProfileBuilder`, whose agents-area namesakes are
  already registered.

A demo's mock `Agent` is held out the same way. The owner's design intent is that all of them register at
distinct addresses.

## Reproduction

The script in Appendix A depends only on melder. Each case gets its own fresh aetheric frame and book. The script
binds the classes, conjures a dynamic root and melds each class back by its address. `ModuleA.Repo` and
`ModuleB.Repo` are two different classes that are both named `Repo`.

```text
python repro_duplicate_spell_name.py.txt        # Python 3.14t with melder installed
```

| case | addresses bound (spellframe, binding) | bind | result on 0.2.82 | expected |
| --- | --- | --- | --- | --- |
| distinct spellframes | Repo at (users, default); Repo at (orders, default) | both ok | conjure fails, DUPLICATE_SPELL_NAME | conjure passes; each melds back by address |
| distinct binding names | (repos, a_repo); (repos, b_repo) | both ok | conjure fails, DUPLICATE_SPELL_NAME | passes |
| both distinct | (users, one); (orders, two) | both ok | conjure fails, DUPLICATE_SPELL_NAME | passes |
| discoverable twin | (users, default); (orders, default) with resolvable=False | both ok | conjure fails, DUPLICATE_SPELL_NAME | passes: meld can never select a discoverable spell |
| control: different names | Repo at (users, default); Other at (orders, default) | both ok | conjure passes; both meld back | as today |
| control: same address | (repos, repo) twice | second refused: "Binding signature already active in this frame" | conjure passes with the first | as today (correct) |
| unaddressed class meld | only ModuleA.Repo, at its default address; then `root.meld(spell=ModuleB.Repo)` | ok | **returns a ModuleA.Repo instance** | an error: ModuleB.Repo was never registered |

Appendix B has the exact results and the full error text.

## Why this is a defect and not the design

**Resolution is keyed by address, not by class name.** `SpellInputUtils` defines the resolution vocabulary
(`src/melder/utilities/helpers/general_helpers.py:120-426`). Every bind and every lookup is normalized to a
lowercase `(frame_key, bind_key)`:

- `frame_key` is the spellframe, or the spell name when no spellframe is given;
- `bind_key` is the binding name, or `"__default__"` when none is given.

`Meld._resolve_spell` (`src/melder/aether/conduit/meld/meld.py:1732-1814`; line 1698 in 0.2.82) resolves a
`spell_id` string directly. Every other input goes through that key: a name, a class object, or a spellframe with
or without a binding name. The key is looked up locally first, then in the contracted conduits in iteration
order (`meld.py:1853-1985`).

**One active spell per address is already enforced.** `LookupContainer.claim`
(`src/melder/aether/aetheric_frame/lookup_container.py:92-127`) refuses a second active spell on the same
`(frame_key, bind_key)` anywhere in the aetheric frame, and tells the user to "use a distinct spellframe or
binding_name". Within one frame, two spells therefore cannot share an address.

**The check's stated purpose is address ambiguity.** The `SpellInputUtils` docstring (`general_helpers.py:215-221`)
says the duplicate-spell-name strategy "exists precisely because two bindings normalizing to one key would make
name-based resolution ambiguous". Melder's DI Resolution Contract (`context_compass/system_docs/src_components.md`,
"By SpellName string (logical name) using a `(frame_key, bind_key)` index") says the same. So do the strategy's
docstring and its message: both tell the user to disambiguate by spellframe and/or binding_name
(`src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:13-49` and
`132-148`).

**The implementation keys on the class name.** `DuplicateSpellNameStrategy.validate` (same file, `70-149`) builds a
map from `spell.spell_name` to collisions over `spellbook._spell_id_pool`. That pool holds both owned and
contracted spells (`src/melder/aether/spellbook/spellbook.py:1122-1140` and `1290-1320`), and bind sets
`spell_name` to the class `__name__` (`src/melder/aether/spellbook/bind/bind.py:689`). The spellframe and binding
name are only copied into the issue details. `resolvable` is never read, so a discoverable twin collides too,
even though meld always refuses it.

**Melder already knows.** `tests/integration/melder/spellbook/test_spellbook_integration_di_validation_faults.py`,
added 2026-07-05, opens with: "Fault A - DuplicateSpellNameStrategy is over-strict: It keys collisions on the bare
`spell_name` and ignores spellframe / binding_name, so fully disambiguated same-name spells still error. This
contradicts ticket A6 (ambiguity keyed by (frame_key, bind_key)) and the strategy's own remediation message."
Its two `xfail` tests describe the intended behaviour. The compiler matrix's
`test_phase4_duplicate_name_still_errors_with_distinct_frame_and_binding` pins the current behaviour and labels it
"suspected fault A".

## The real hazard the name check stands in for

`meld(spell=Cls)` with no spellframe or binding name normalizes to `(Cls.__name__.lower(), "__default__")`. It
returns whatever spell holds that address, and nothing checks that the resolved spell is `Cls`: there is no
identity comparison on the resolution path (`meld.py:1784-1814`).

The last reproduction case shows the effect. Only `ModuleA.Repo` is registered, at its default address.
`root.meld(spell=ModuleB.Repo)` then returns a `ModuleA.Repo` instance, although `ModuleB.Repo` was never
registered.

A string meld (`meld("Repo")`) is keyed by name by definition, and its result is deterministic. A class-object
meld that builds a different class, however, is a type confusion. So a same-named twin of the class that holds
the name's default address is genuinely dangerous. That is exactly the shape the remaining DUPLICATE_SPELL_NAME
tests use: one class at the default binding and a same-named class at the binding `"secondary"`.

## Proposed fix (for the Melder owner to decide)

**Part 1 - the reported bug: re-key the strategy on the address.**

- Build the collision map from the normalized `(frame_key, bind_key)` of each visible *resolvable* spell. Use
  `SpellInputUtils.make_spell_key_from_parts` with the spell's spellframe, spell_name and binding_name, and skip
  discoverable spells.
- Report an address only when two or more visible spells hold it. Inside one frame, bind already prevents this,
  so in practice it fires when an address is visible both locally and through a contract (the local spell
  silently shadows the other), or through two contracted conduits (the first in iteration order wins).
- Make the message name the shared address and say which spell wins.
- Same-named classes at distinct addresses then pass.

**Part 2 - the identity hazard: make an unaddressed class meld check identity.** When `meld(spell=Cls)` resolves an
address whose spell is not `Cls`, raise a lookup error instead of building the other class. The error should name
both classes, and the addresses where `Cls` is registered if there are any. A friendlier alternative, but a
larger change, is a class-to-spell index that lets such a meld find `Cls` wherever it is bound.

**Decisions for the Melder owner:**

- **(a) Twins of the default-address holder.** With Part 2 in place, should a same-named twin of the spell at the
  name's default address still be flagged? We recommend a warning at most, because a string meld by that name
  reaches only the default holder, and does so deterministically.
- **(b) Local versus contracted.** When one address is visible both locally and through a contract, is that an
  error or a shadowing warning? When two contracted conduits expose one address, we recommend an error, because
  the winner depends on iteration order.

## Tests that change

All paths are under `tests/`. The "Hazard shape" in the table is one class at the default binding plus a
same-named class at the binding `"secondary"`.

| test | today | after the fix |
| --- | --- | --- |
| `integration/.../test_spellbook_integration_di_validation_faults.py::test_fault_a_distinct_spellframes_should_not_error` | xfail | passes; remove the xfail |
| same file `::test_fault_a_distinct_binding_names_should_clear_error` | xfail | passes; remove the xfail |
| same file `::test_fault_a_control_bare_duplicate_names_error` | hazard shape: error | decision (a) |
| `integration/.../test_spellbook_integration_di_shape_compiler_matrix.py::test_phase4_duplicate_name_still_errors_with_distinct_frame_and_binding` | pins Fault A | invert: no error |
| same file `::test_phase4_duplicate_spell_name_errors_and_breaks` | hazard shape: error | decision (a) |
| `integration/.../test_spellbook_integration_resolution_error_matrix.py::test_conjure_with_duplicate_spell_name_raises` | hazard shape: conjure raises | decision (a) |
| `component/.../validation/test_spellbook_component_validation_strategies.py::test_component_duplicate_spell_name_strategy_flags_collision` | hazard shape: error | decision (a) |
| `integration/.../test_spellbook_integration_validation_system.py::test_validation_system_duplicate_spell_name_local_only` | hazard shape: error | decision (a) |
| same file `::test_validation_system_duplicate_spell_name_across_contracted` | error for bindings "owner" and "borrower" across a contract | these addresses differ, so no error; re-target to one shared address across the contract (decision (b)) |
| same file `::test_validation_system_duplicate_name_clears_after_unlink` | same shape | re-target as above |

New tests to add:

- the four failing reproduction cases, which should conjure and meld each class back by its address;
- the unaddressed class meld of an unregistered same-named class, which should raise (Part 2);
- one address exposed through two contracted conduits (decision (b)).

## What CommandOps needs from the fix

CommandOps always melds by spell id, by explicit (spellframe, binding name), or by a string name. It never melds by
a bare class object, so Part 1 alone unblocks it. After the fix, CommandOps registers its nine held-out classes at
their planned addresses:

- the in-directory duplicates keep their directory spellframe and take module-qualified binding names, such as
  `sync_fork.ForkUnit`;
- the utilities `MCP*` trio uses its own spellframe.

Part 2 protects every other Melder user from the type confusion.

## Appendix A - reproduction script

```python
"""Minimal reproduction: Phase 4 DUPLICATE_SPELL_NAME refuses same-named classes at distinct addresses.

Run with Melder installed (Python 3.14t):  python repro_duplicate_spell_name.py.txt
Depends on melder only. Every case uses a fresh book in its own aetheric frame, binds the classes, conjures a
dynamic root and, when the conjure succeeds, melds each class back by its explicit address.

Two classes both named Repo (different __qualname__, like two modules that each define a Repo) are bound at
addresses that differ in spellframe, in binding name or in both. Melder resolves by the normalized
(frame_key, bind_key) pair, and bind already refuses a second active spell on one pair, so none of these
addresses is ambiguous - yet conjure fails. Controls: two different class names pass; a true signature
collision (same spellframe and binding name) is refused at bind, as it should be. A last case binds one Repo
at its default address and melds by the other Repo class object, to show that an unaddressed class meld is keyed
by the class name - the one situation in which a same-named twin really is hazardous.
"""
import json
import sys

import melder
from melder import Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration


class ModuleA:
    """Stands in for module a.py."""

    class Repo:
        """Repo as defined in module a."""

        def __init__(self) -> None:
            self.origin = "a"


class ModuleB:
    """Stands in for module b.py."""

    class Repo:
        """A different class that happens to share the name Repo."""

        def __init__(self) -> None:
            self.origin = "b"


class Other:
    """A differently named class, for the control case."""

    def __init__(self) -> None:
        self.origin = "other"


def new_book(tag: str) -> Spellbook:
    """Return a configured, frozen book in a fresh dynamic aetheric frame named after the case."""
    configuration = SpellbookConfiguration(aether_frame=f"repro-{tag}")
    configuration.with_defaults()
    book = Spellbook(aetheric_frame=f"repro-{tag}", configuration=configuration)
    book.configure_aether_frame(system_state="dynamic", ai_native=False, rift_enabled=False,
                                system_caching_enabled=False, disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    return book


def short(error: BaseException) -> str:
    """Return the error type and the first 600 characters of its message."""
    return f"{type(error).__name__}: {str(error)[:600]}"


def run(tag: str, plan: list) -> dict:
    """Bind every (class, spellframe, binding_name, resolvable) of plan into one book, conjure, meld each back."""
    result: dict = {"binds": [], "conjure": None, "melds": []}
    book = new_book(tag)
    root = None
    try:
        for spell, spellframe, binding_name, resolvable in plan:
            entry = {"class": spell.__qualname__, "spellframe": spellframe, "binding_name": binding_name,
                     "resolvable": resolvable}
            try:
                book.bind(spell=spell, existence="many", spellframe=spellframe, binding_name=binding_name,
                          resolvable=resolvable, disposal_method_names=[])
                entry["bind"] = "ok"
            except Exception as error:
                entry["bind"] = short(error)
            result["binds"].append(entry)
        try:
            root = book.conjure(dynamic=True, name=f"repro-root-{tag}")
            result["conjure"] = "ok"
        except Exception as error:
            result["conjure"] = short(error)
            return result
        for (spell, spellframe, binding_name, resolvable), bound in zip(plan, result["binds"]):
            if not resolvable or bound["bind"] != "ok":
                continue
            try:
                obj = root.meld(spellframe=spellframe, binding_name=binding_name)
                result["melds"].append({"address": [spellframe, binding_name], "origin": obj.origin})
            except Exception as error:
                result["melds"].append({"address": [spellframe, binding_name], "error": short(error)})
    finally:
        if root is not None:
            root.cleanup()
        book.cleanup()
    return result


cases = {
    # Bug: distinct spellframes, default binding names.
    "distinct_spellframes": [(ModuleA.Repo, "users", None, True), (ModuleB.Repo, "orders", None, True)],
    # Bug: one spellframe, distinct binding names (what the DUPLICATE_SPELL_NAME message itself advises).
    "distinct_binding_names": [(ModuleA.Repo, "repos", "a_repo", True), (ModuleB.Repo, "repos", "b_repo", True)],
    # Bug: both discriminators at once.
    "distinct_spellframes_and_binding_names": [(ModuleA.Repo, "users", "one", True),
                                               (ModuleB.Repo, "orders", "two", True)],
    # Bug: the twin is discoverable (resolvable=False), so meld can never select it, yet it still collides.
    "discoverable_twin": [(ModuleA.Repo, "users", None, True), (ModuleB.Repo, "orders", None, False)],
    # Control: two different class names at comparable addresses - passes.
    "control_different_names": [(ModuleA.Repo, "users", None, True), (Other, "orders", None, True)],
    # Control: a real signature collision (same spellframe, same binding name) - refused at bind, correctly.
    "control_same_signature": [(ModuleA.Repo, "repos", "repo", True), (ModuleB.Repo, "repos", "repo", True)],
}


def class_meld_by_name() -> dict:
    """Bind only ModuleA.Repo at its default address, then meld by the OTHER class object, ModuleB.Repo.

    Shows why the default address matters: a meld by class object with no spellframe or binding name is keyed
    by the class NAME ("repo", "__default__"), so it can return an instance of a different class of that name.
    """
    result: dict = {}
    book = new_book("class-meld")
    root = None
    try:
        book.bind(spell=ModuleA.Repo, existence="many", disposal_method_names=[])
        root = book.conjure(dynamic=True, name="repro-root-class-meld")
        obj = root.meld(spell=ModuleB.Repo)
        result["meld(spell=ModuleB.Repo)"] = {"returned_class": type(obj).__qualname__, "origin": obj.origin}
    except Exception as error:
        result["error"] = short(error)
    finally:
        if root is not None:
            root.cleanup()
        book.cleanup()
    return result


report = {"melder": melder.__version__, "python": sys.version.split()[0], "gil_enabled": sys._is_gil_enabled()}
for name, plan in cases.items():
    report[name] = run(name, plan)
report["class_meld_resolves_by_name"] = class_meld_by_name()
print(json.dumps(report, indent=1))
```

## Appendix B - results on 0.2.82

Environment: melder 0.2.82, Python 3.14.7, GIL enabled: False.

- distinct_spellframes: binds [ModuleA.Repo at (users, None, resolvable=True): ok; ModuleB.Repo at (orders, None, resolvable=True): ok]; conjure: SpellbookValidationError: Spellbook validation failed. Broken spells: Repo, Repo.; melds: none
- distinct_binding_names: binds [ModuleA.Repo at (repos, a_repo, resolvable=True): ok; ModuleB.Repo at (repos, b_repo, resolvable=True): ok]; conjure: SpellbookValidationError: Spellbook validation failed. Broken spells: Repo, Repo.; melds: none
- distinct_spellframes_and_binding_names: binds [ModuleA.Repo at (users, one, resolvable=True): ok; ModuleB.Repo at (orders, two, resolvable=True): ok]; conjure: SpellbookValidationError: Spellbook validation failed. Broken spells: Repo, Repo.; melds: none
- discoverable_twin: binds [ModuleA.Repo at (users, None, resolvable=True): ok; ModuleB.Repo at (orders, None, resolvable=False): ok]; conjure: SpellbookValidationError: Spellbook validation failed. Broken spells: Repo, Repo.; melds: none
- control_different_names: binds [ModuleA.Repo at (users, None, resolvable=True): ok; Other at (orders, None, resolvable=True): ok]; conjure: ok; melds: ['users', None] -> a; ['orders', None] -> other
- control_same_signature: binds [ModuleA.Repo at (repos, repo, resolvable=True): ok; ModuleB.Repo at (repos, repo, resolvable=True): RuntimeError: Binding signature already active in this frame: frame_key='repos', binding_name='repo' is held by spell_id='71f402e40d521d7c31338f62408ff5518f3e1b]; conjure: ok; melds: ['repos', 'repo'] -> a
- class_meld_resolves_by_name: {"meld(spell=ModuleB.Repo)": {"returned_class": "ModuleA.Repo", "origin": "a"}}

Full error for the distinct-spellframes case (the script truncates at 600 characters):

```text
SpellbookValidationError: Spellbook validation failed. Broken spells: Repo, Repo.
Repo (frame 'users'):
  - Multiple visible spells share the name 'Repo'. Name-based resolution via meld(spell_name=...) would be ambiguous. Disambiguate by using a spellframe (Protocol/string frame key) and/or a binding_name so that each resolution path is uniquely identifiable. [DUPLICATE_SPELL_NAME]
Repo (frame 'orders'):
  - Multiple visible spells share the name 'Repo'. Name-based resolution via meld(spell_name=...) would be ambiguous. Disambiguate by using a spellframe (Protocol/string frame key) and/or a binding_name so that each re
```
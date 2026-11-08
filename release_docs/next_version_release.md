# Melder 0.2.8282

**Unreleased**

## Spell ownership is never transferred across aetheric frames

**Breaking change:** `Conduit.transfer_spell_ownership` now raises RuntimeError "Cannot transfer spell ownership
across different AethericFrames: <source> != <target>. ..." when the target conduit belongs to another aetheric
frame, before anything starts - the rule `link` already follows. Such a transfer used to run and could leave the
target's Spellbook with two active spells at one address (a meld of that address raised `DUPLICATE_SPELL_NAME`) and
the source frame unable to bind that address again. To use a spell in another frame, bind it in a Spellbook of that
frame. Transfers within one frame are unchanged.

## Melder is licensed under the Apache License 2.0

Melder's license changes from the GNU Affero General Public License v3.0 or later (`AGPL-3.0-or-later`) to the
Apache License 2.0 (SPDX `Apache-2.0`). `LICENSE` carries the Apache License's text, and `NOTICE`, the package
metadata (`license` in `pyproject.toml`, `melder.__license__`) and the README state the same license. The AGPL's
terms, its network-use clause included, are replaced by the Apache License's. The trademark notice keeps its
substance: the license grants no rights in the Melder name or marks. `LICENSE`, `NOTICE`, the header of
`melder.__license__` and the documentation's copyright line name one copyright holder, Mark Thomas Geleta, and one
year, 2026.

## A class lookup reaches only a spell bound bare

**Breaking change:** a constructor parameter annotated with a class, `list[ThatClass]`, a single string
annotation naming the class, and `SpellMap(ThatClass)` now reach a spell only when it is bound bare - with
no `spellframe` and no `binding_name` - the rule `meld(ThatClass)` has always followed. A class bound under a
spellframe is reached through the frame, and one bound under a binding name through that name. An existing
object bound under a spellframe or a binding name follows the same rule.

```python
book.bind(spell=English, existence="unique", spellframe=Greeter, binding_name="english")


class Host:
    def __init__(self, greeter: English) -> None:  # no longer resolves this English
        self.greeter = greeter


class FramedHost:
    def __init__(self, greeter: Greeter) -> None:  # resolves it, through the frame
        self.greeter = greeter
```

**Breaking change:** a consumer whose class lookup finds the class only where the lookup does not reach -
under a spellframe or a binding name - is refused at `conjure()` with `SpellbookValidationError`, code
`HIDDEN_PROVIDER`, and the message names every place the class is bound and the lookup to use there:

```text
Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is
bound bare (no spellframe, the default binding), and English is bound only under a spellframe: English at
(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english').
Ask for it where it is bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while
that spell is the only one bound under Greeter - or bind English bare. [HIDDEN_PROVIDER]
```

The refusal covers a class annotation, a single string annotation naming the class, `Optional[ThatClass]`
without a default, and a `SpellMap(ThatClass)` default, which used to fail inside the compiler with
"SpellMap default could not be resolved". `override=` no longer rescues such a consumer: in a dynamic world,
binding it after `conjure()` raises the same error and leaves it registered and refused, and every meld of
it is refused, with or without `override=`. Order does not matter: a consumer compiled before its class was
bound under a spellframe is refused at its next meld, as one compiled after is refused at its bind.

A required `list[ThatClass]` left empty for the same reason refuses at `conjure()` in an automatic world
(`collection_socket_no_providers`), its message now naming where the class is bound and the list to use
(`list[Greeter]`); a dynamic world injects `[]` with a warning naming the same places. A class bound nowhere
still compiles as an unresolved input: melding the consumer raises `UnresolvedInputError` naming the
parameter unless the meld supplies it with `override=`.

How to upgrade:

1. A class bound under a Protocol: annotate the Protocol (`greeter: Greeter`) or use
   `SpellMap(spellframe=Greeter, binding_name="english")`.
2. A class bound under a string category spelled as its own name (`spellframe="English"`): drop the
   spellframe. A bare class is addressed by its own name, so its address does not change.
3. A bare class bound with a binding name: use `SpellMap(English, binding_name="v1")`, or drop the binding
   name.
4. `SpellMap(English)` aimed at a framed or named English: add its `spellframe` and `binding_name`.
5. A parameter you supplied with `override=` at every meld: point a `SpellMap` default at where the class
   is bound, bind the class bare, or give the parameter an ordinary Python default
   (`greeter: Optional[English] = None`), which Melder never injects over and the check does not look at.

What stays the same: Protocol annotations, `list[Protocol]`, `list["category"]`, frame-addressed `SpellMap`s,
every meld door, `SpellContract`, and ambiguity - two implementations of one Protocol still refuse with
`AMBIGUOUS_PROVIDER`, whose message no longer suggests `override=` (an override never rescued a refused
spell). A spellframe is the spell's interface, a dict keyed by binding name:
`meld(spellframe=Greeter)` with no binding name reads the default slot, while a `Greeter` annotation selects
the frame's single implementation.

Why: `meld(English)` refused an English bound under a frame while `greeter: English` injected it - two
answers to one question - and a consumer compiled before its framed provider arrived waited under the class
name while the provider announced its frame, so it never picked the provider up. One rule removes both, and
the refusal says where the class is instead of "nothing registered provides it". Creation-cache bundles
written before are cold once (cache generation 27).

## Canonical terminal enum names with compatible record reads

**Breaking change:** use `SpellValidity.CLEANED`, `ConduitState.CLEANED` and
`RecordedUnitState.CLEANED` instead of their former `.cleaned` Python attributes. There is no
lowercase Python alias. These enums now use string values matching their member names:
`RecordedUnitState.CLEANED.value` is `"CLEANED"`, and the formerly numeric `SpellValidity` and
`ConduitState` values are strings. `str(ConduitState.CLEANED)` still returns `"cleaned"` under
its existing diagnostic contract.

Native enum-name lookup accepts uppercase, lowercase and mixed-case declared names, including aliases.
It preserves existing lowercase-key precedence and requested-family member identity. Unknown names,
values used as names and foreign enum members are refused; a cached raw string cannot authorize an
equal foreign `StrEnum` member.

New Nexus and MutationResearch lifecycle journal keys, payloads and summaries use `"CLEANED"`.
Restore recognizes both that name and legacy `"cleaned"` within admitted record-major-5 artifacts,
so either terminal name suppresses reconstruction and reports the existing named shortfall.
Journal chronology, enabled/disabled replay, record-major admission and ownership transfer stay as before.

## String-backed enum compatibility

**Breaking change:** the migrated native enum families now use `StrEnum` values that exactly match
member names, including their case. For example, `AdmissionReason.WAIT_TIMEOUT.value` is
`"WAIT_TIMEOUT"`; a lowercase member name retains its lowercase spelling. String-enum members compare
equal to their string values and to equal-valued members of other string-enum families. Check the
concrete type when a boundary must distinguish families or when using members as dictionary/set keys.

Direct `.value` and default string/JSON representations can therefore change, including from an
integer to a string. Selected compatibility readers accept tested historical numeric inputs and
old pickle payloads; `SocketKind` continues to emit its historical integer compiler rows. Migrate
external code that directly stores or compares old enum values; external serializers have not been
exhaustively checked.

The established record projections remain at their boundaries: Nexus configuration writes plain
member names; research records retain their established strings; admission descriptions, participant
rows, aetheric session descriptions/errors and scope keys retain their historical lowercase tokens;
and claim modes retain `x`, `s` and `ix` wire tokens. Old lowercase admission and selected
transaction tokens remain readable. DevOps `TransactionSession.describe()` returns the stored request
type directly: an enum member now renders with its exact uppercase value, while a raw lowercase input
remains lowercase. Exact `BIND` and `NOTCH` strings also reach the existing structural commit
validation gate. The legacy raw `"dynamic"` configuration alias still selects `codegen`.

Bind now rejects a foreign enum family passed as a managed-spell mode, even when its value matches a
valid mode. Non-`SpellState` additions to state flags are ignored instead of retained. Supported typed
flags and ownership-transfer behavior remain covered by the focused tests.

## Packaging and documentation

The source and test maps, their indexes and the source graph reflect the selected enum changes.
Generated assets are rebuilt and verified for the current version.

The README's GitHub stars badge uses the social style and links to the stargazers page (GitHub issue #191).

The README's Spellframes, Dependency Injection and `SpellMap` passages, beginner lesson 25, the examples'
`AGENTS.md` and the agent operations guide's constructor table state the class-lookup rule and the
spellframe as an interface dict. The README's overview, its `conjure()` and Dependency Injection passages
name the `HIDDEN_PROVIDER` refusal, and its `SpellMap` passage no longer offers a meld `override` among
`AMBIGUOUS_PROVIDER`'s fixes. The source maps, their indexes and the source graph describe the refusal, the
type-key announce and creation-cache generation 27. The internal-bind guard lists 631 classes:
`HiddenProviderStrategy` and `HiddenProviderReport` joined it.

Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8282.

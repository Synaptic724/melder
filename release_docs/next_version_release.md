# Melder 0.2.8277

**Unreleased**

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

Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8277.

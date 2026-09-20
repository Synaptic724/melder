# Named binding versus public meld inputs

Executed the extended recent human-name experiment on CPython 3.14.7 free-threaded.
Initial result: **16 passed in 0.41 seconds**. With the explicit-frame follow-up below,
the complete file now passes **25 tests in 0.56 seconds**. Scoped Ruff and whitespace checks pass.

The new fixture contains only:

```python
spell_id = book.bind(spell=MyService, existence="unique", binding_name="test")
```

| Public call | Observed result |
| --- | --- |
| `conduit.meld("MyService")` | KeyError: no `('myservice', '__default__')` binding |
| `conduit.meld(MyService)` | Same missing-default-binding KeyError |
| `conduit.meld("MyService", binding_name="test")` | Returns MyService |
| `conduit.meld(spell="MyService", binding_name="test")` | Same unique instance |
| `conduit.meld(MyService, binding_name="test")` | Same unique instance |
| `conduit.meld(spell_id=spell_id)` | Same unique instance |
| `conduit.meld(binding_name="test")` | ValueError: spell or spellframe identity required |
| `conduit.meld("test")` | KeyError: searches spell/frame `test` with the default binding |
| `conduit.meld('binding_name="test"')` | KeyError: the whole string is treated as the spell/frame name |

Omitting the qualifier fails both before and after a successful named meld, so warming input or
instance caches does not produce a fallback. Missing lookup raises; it does not return None.

The same outcomes passed under automatic pre-conjure binding, dynamic pre-conjure binding and
dynamic post-conjure binding. All comparisons use unique existence for identity parity.
The original explicit-name-versus-SHA experiment also remains passing.

The lookup uses a two-part key: `(spellframe_or_name, binding_name_or_default)`. A binding name
qualifies that key; it does not replace the spell name or create an unqualified alias.

## Reproduce

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
& '.venv_new/Scripts/python.exe' -m pytest tests/experimentation/test_meld_human_spell_name_string_experiment.py -p no:cacheprovider -o addopts= -q -s
```

Evidence: `results.xml`, `results.log`. Earlier fixture/exception-formatting corrections are
retained in `setup_failure.log` and `message_assertion_failure.log`; they are not runtime defects.
No production source changes were made.

## Explicit spellframe follow-up

For `bind(spell=MyService, spellframe="ServiceFrame", binding_name="test", existence="unique")`:

| Public call | Observed result |
| --- | --- |
| `meld("MyService", binding_name="test")` | KeyError: searches `('myservice', 'test')` |
| `meld(MyService, binding_name="test")` | Same KeyError |
| `meld(binding_name="test")` | ValueError: missing spell/frame identity |
| `meld(spellframe="ServiceFrame")` | KeyError: missing default binding in that frame |
| `meld(spellframe="ServiceFrame", binding_name="test")` | Returns MyService |
| `meld("MyService", spellframe="ServiceFrame", binding_name="test")` | Same unique instance |
| `meld("ServiceFrame", binding_name="test")` | Same unique instance; positional text supplies the frame key |
| `meld(spell_id=spell_id)` | Same unique instance |

String and concrete-type frames both pass these cases in all three lifecycle modes. Failures
remain failures after successful fully qualified resolution; the input cache does not add aliases.

If the explicit frame name normalizes to the class name, such as spellframe="MyService", then
omitting the spellframe keyword succeeds because it produces the same lookup key. Three additional
cases verify that edge. It is equality of the address, not discovery of the frame from the binding.

Evidence: `framed_results.xml`, `framed_results.log`; 25 total passing tests, including the prior 16.

# Releases and migration

These pages describe **Melder {{ release }}**. Match documentation to your installed
package before relying on a signature or lifecycle rule.

```python
import melder as md

md.__version__
```

## Choose the corresponding documentation

An explicitly selected release describes that release's source. Development
documentation can include changes that are not in an older installed package.
Use the version selector when comparing supported hosted versions, and inspect
the source link on the relevant API or lesson page.

The source-controlled [release history](https://github.com/Synaptic724/melder/releases)
records published releases. The [full contents](../contents.md) and
[API inventory](api.md) provide a practical comparison route for a particular feature.

## Check the boundaries affected by an upgrade

- Verify the Python runtime and environment first.
- Run the saved examples closest to your application's binding, addressing, and lifetime choices.
- Review configuration freeze/activation and cleanup contracts if you own long-lived runtimes.
- For recorded worlds, inspect restore admission, source drift, shortfalls, and identity translation.
- For agent integrations, review the concrete room's command surface and target policy.

The documented examples use `meld(override=...)` and explicit `spell_id=` for opaque
identities. Follow the reference for the installed version rather than adapting
an older spelling by guesswork.

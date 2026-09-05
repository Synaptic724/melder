# Read the Docs / Sphinx compatibility probe

Owner: codex_2.
Ticket: ../../tickets/tasks/2026-09-04_readthedocs_sphinx_reference_discovery_task.md.

This directory holds a disposable documentation-only probe. Its virtual environment and rendered
output are ignored; authored probe inputs and measured findings are retained with the ticket.
No files here are the live Melder documentation configuration and nothing is published.

Questions: can Python 3.14 import curated Melder APIs through Sphinx autodoc, and can MyST render
the existing Markdown/SVG guides without moving or duplicating their canonical source?

Initial state: Sphinx, MyST, and the RTD theme were absent from the installed Python 3.14 environment.
The existing architecture-docs check reported ten Mermaid source hash mismatches; cause unverified.

Update 2026-09-04T21:06:12Z: Probe deferred following the owner's clarification to focus on
understanding ThreadFactory before selecting Melder's strategy. venv's ensurepip step failed;
uv venv succeeded, but dependency fetching failed with a proxy/network connection refusal.
Sphinx never ran and no HTML was produced.

The ten diagram sources are LF in Git and CRLF in the worktree. For the one checked sample,
system_context.mmd, normalizing CRLF to LF matches the manifest hash exactly:
955bca1501d7accb1f5b99ac8444f30fcbc695ba4d913e7190f0e6dabacd6eab.
No diagram was edited and no other normalized hash was compared.

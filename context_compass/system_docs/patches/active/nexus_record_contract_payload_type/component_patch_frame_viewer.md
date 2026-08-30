# Component Patch: FrameViewer

## Before
- viewer binding relies on descriptor + ACL state only
- no explicit viewer-side matching for the record-level Nexus dataset label

## After
- viewer profile binding can validate against the same record-level
  `nexus_label` / `nexus_version` cycle as ACL validation
- viewer remains descriptor-driven but no longer depends on payload labels as
  publication identity

# Component Patch: FrameACLValidator

## Before
- matches ACL requirements against payload-side labels

## After
- matches ACL requirements against record/event `nexus_label` /
  `nexus_version`
- treats spell payload detail as spell-payload-owned information rather than
  dataset identity

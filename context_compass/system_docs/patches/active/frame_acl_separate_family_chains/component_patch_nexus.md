# Component Patch: Nexus

## Before
- named ACL registration does not invalidate projected viewer cache
- only frame-global chain operations trigger cache invalidation
- attached Rift viewers refresh only when a Rift retargets

## After
- selected family-chain bumps invalidate projected viewer cache
- affected live Rifts/spaces refresh attached viewers for the bumped frame

## Contract
- Rift selection resolves view/command/codegen contract names per frame
- config revision movement is transparent to a stable selection once the
  selected family chain advances

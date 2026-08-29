# Component Patch: FrameDescriptorManager

## Before
- validates publication contracts against payload labels
- publishes spell payload detail as if it were the dataset contract

## After
- validates the record/event Nexus contract at publish time
- publishes all current records as `default:0.0.1`
- preserves spell payload detail inside spell payload fields

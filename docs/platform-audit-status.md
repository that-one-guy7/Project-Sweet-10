# ARM64 platform audit status

## Scope

Read-only review of Apple's pinned XNU 8796 ARM64 startup, CPU, VM, and platform-expert
source for the Project Sweet-10 iPhone9,1 research target.

## Findings

1. XNU has a distinct early ARM64 startup path, CPU lifecycle path, virtual-memory
   initialization path, and ARM platform-expert path.
2. The platform-expert code consumes device-tree properties for CPU state and clock
   metadata, an `arm-io` node with `device_type` and `ranges`, and panic-region
   metadata from `pram` and `/chosen`.
3. The startup assembly uses architectural CPU identity and per-CPU reset-handler data.
4. These source-level requirements are not an iPhone9,1 implementation. No target
   device-tree property values, memory ranges, interrupt assignments, or board config
   values are asserted by this audit.

## Evidence gaps

- Exact kernel build metadata corresponding to iOS 16.7.16 build 20H392.
- Reliable iPhone9,1 device-tree evidence.
- Board configuration header generation/selection.
- A reproducible unmodified XNU build.
- A verified source-to-target compatibility assessment.

## Current gate

<badge>Research only</badge>

No platform patches are approved by this audit. Do not derive or add target-specific
hardware constants from the Qualcomm SWEET project. Do not treat successful compilation
as proof of device support.

See [XNU ARM64 source map](xnu-arm64-source-map.md) and
[device-tree property inventory](../device-tree/PROPERTY_INVENTORY.md).

## Interface comparison update

A comparison of XNU 7195 and XNU 8796 platform interfaces is documented in
[ARM64 platform-interface comparison](arm64-platform-interface-comparison.md).
It finds the reviewed ARM64 boot_args field order and PE_init_platform signature
remain recognizable, while the modern CPU topology parser and CPU lifecycle
accounting have evolved. Both versions depend on DeviceTree CPU properties and
register ranges. No iPhone9,1 property values or peripheral mappings are supplied
by the generic interface comparison.

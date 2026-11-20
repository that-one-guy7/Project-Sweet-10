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
- Final runtime iPhone9,1 DeviceTree and property values. The supplied 19H422
  component hashes are verified and its decompressed tree has been fully
  parsed. Selected ARM-IO/AIC/timer values correlate with pinned XNU 8796
  generic mapping code. CPU clock fields and memory/panic values in the static
  component are zero or absent; the final iBoot/PongoOS tree remains unknown.
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

## Interrupt and timer interface comparison

The [ARM64 interrupt and timer interface audit](interrupt-timer-interface-audit.md)
compares XNU 7195 and 8796. The generic DeviceTree register-mapping helper and
ARM64 interrupt/timebase registration interfaces remain unchanged, while the
modern hardware timebase read has a nonspeculative counter selection and a
sleep/wake race retry. Neither source version supplies verified iPhone9,1 IRQ
assignments, interrupt-controller addresses, timer mappings, or counter
frequency. Those remain open target-evidence gates.

## iPhone9,1 DeviceTree evidence

Project Sweet-10 independently verified the extracted BuildManifest and
DeviceTree component hashes, decompressed the LZFSE payload, and parsed all
227 nodes including root. The parsed tree identifies `arm-io,t8010`, two CPU
nodes, an AIC master controller, and an AIC timebase. The SoC-base and AIC/
timer register inputs have been compared with the pinned XNU 8796 generic
consumers. CPU0 frequency values are zero, `/memory`/`pram`/`vram` regions
are zero, and `/chosen/embedded-panic-log-size` is absent in this static
component. Final runtime clock, memory, and panic-region values remain open.
The third-party survey's fixed-width `reg` size totals remain heuristics.

See the [19H422 survey methodology review](iphone91-19h422-survey-methodology-review.md) and [parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

See the [19H422 structure audit](iphone91-19h422-device-tree-structure-audit.md),
[artifact evidence audit](iphone91-stock-firmware-device-tree-evidence.md),
and [property inventory](../device-tree/PROPERTY_INVENTORY.md).

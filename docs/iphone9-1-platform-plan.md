# iPhone9,1 platform investigation plan

Target: iPhone 7, model identifier `iPhone9,1`.

This document defines the evidence needed for an A10 XNU platform port. It intentionally
does not provide device-modification, boot-chain bypass, or partition-writing instructions.

## Platform workstreams

### 1. Identify the exact platform

Record only non-sensitive facts: model identifier, board configuration, SoC family,
installed OS build if known, and publicly documented hardware revisions. Do not commit
serial numbers, ECIDs, IMEI, activation records, calibration blobs, or full device dumps.

### 2. XNU platform selection

Trace how the selected XNU revision chooses its platform expert, machine configuration,
CPU initialization, interrupt controller, timer, and IOKit matching. A string match for
a chip identifier in a source tree is not proof of complete platform support.

### 3. Device-tree compatibility

Build a written schema of required nodes and properties from public source and source
inspection. For each property, record its consumer, expected type, units, and evidence.
Do not transplant the SWEET project's Qualcomm FDT/ADT values.

### 4. Early diagnostics

Define a platform-neutral diagnostic contract: build identity, boot-stage marker,
memory-map summary, CPU identification, exception report, and panic reason. Keep output
read-only and avoid dumping secrets or unique device identifiers.

### 5. Display and input

Treat display output, touch input, physical buttons, and HID event delivery as separate
milestones. A visible framebuffer does not establish a functioning display service or
touch stack.

### 6. Storage and userland

Treat storage-controller support, filesystem mounting, launchd startup, system daemons,
backboardd, and SpringBoard as separate dependencies. Do not assume a working XNU build
can launch an iOS userland by itself.

## Go/no-go checklist

- [ ] Exact iPhone9,1 board identity documented from reliable evidence.
- [ ] Selected XNU revision and toolchain pinned.
- [ ] Required platform initialization paths identified in source.
- [ ] Device-tree property inventory completed.
- [ ] CPU, interrupt, timer, and memory requirements supported by evidence.
- [ ] Host-side tests pass for all parsers and metadata tools.
- [ ] Safe test and recovery strategy reviewed before any physical-device experiment.

No physical-device boot should be attempted merely because the source compiles.

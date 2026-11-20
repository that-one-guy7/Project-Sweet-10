# Feasibility assessment

An iOS 16-generation XNU port to iPhone 7 (`iPhone9,1`) is a substantial platform port,
not a configuration-only rebuild. SpringBoard is a long-range goal, not a guaranteed
outcome.

## What can be reused from ios-sweet
The public `dipa-studio/ios-sweet` project demonstrates an iOS 16-era XNU/userland
bring-up on Qualcomm SM7150. Its build workflow, diagnostic discipline, milestone
structure, and general userland investigation are useful references.

Its Qualcomm memory map, interrupt wiring, device tree, display, touch, storage, and
power drivers are platform-specific. They must not be copied as an A10 implementation.

## Sandcastle
Project Sandcastle is a useful reference for the existing research boot environment.
Its Linux-oriented loader does not automatically provide the XNU boot-argument structure,
memory map, device tree, or CPU state required by XNU.

## Main risks
1. **Boot handoff:** XNU requires a compatible boot-argument structure, memory map,
   device tree, CPU state, and command-line conventions.
2. **A10 platform support:** CPU initialization, MMU, interrupts, timers, power management,
   and secondary CPU startup need verified A10 support.
3. **Device tree:** use an iPhone9,1/A10-specific description; do not substitute a
   Qualcomm tree or another iPhone model's tree without evidence.
4. **Display and touch:** framebuffer output does not prove the full display or HID path works.
5. **Storage/root:** kernel storage support and mounting a compatible root are separate tasks.
6. **Userland:** launchd, dyld, system libraries, IOKit services, entitlements, and private
   interfaces must be compatible with the selected iOS 16 build.
7. **SpringBoard:** requires many supporting services; compiling XNU alone is insufficient.

## Go/no-go gates
- M1: evidence-backed iPhone9,1 hardware/source audit.
- M2: exact XNU revision and reproducible baseline build.
- M3: reviewed A10 boot-handoff specification.
- M4: deterministic early-kernel diagnostics in a safe test environment.
- M5: isolated display/input research.
- M6: launchd and userland dependency analysis.
- M7: SpringBoard starts and remains stable in a controlled test.

A failed gate means revise the design; do not compensate by blindly changing boot arguments
or writing more device partitions.

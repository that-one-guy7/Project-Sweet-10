# Host-side and QEMU validation plan

The first engineering loop should be reproducible and should not require changing an
iPhone's boot state or storage.

## What QEMU can validate

A virtual ARM64 machine can help test code that is deliberately written against the
virtual machine's devices and boot contract: basic kernel compilation, generic exception
handling, memory-management code paths, logging, and host-side artifact parsers.

It cannot validate iPhone9,1 device-tree correctness, A10 peripheral drivers, Apple
boot-environment behavior, display/touch hardware, or the complete iOS userland.

## ios-sweet reference

The SWEET project has a QEMU guide for its own patched kernel and a QEMU `virt` machine.
Its guide explicitly describes a virtual board and SWEET-specific memory/framebuffer
assumptions. Those settings are examples for that project, not a ready-made iPhone7
emulation profile.

## Project Sweet-10 stages

1. **Static stage:** lint documentation and validate metadata without a device.
2. **Build stage:** establish a pinned, unmodified XNU source build on a supported host.
3. **Virtual stage:** only if a compatible generic test configuration exists, exercise
   generic code in QEMU and clearly label the virtual hardware.
4. **Platform stage:** review A10-specific code and device-tree requirements independently.
5. **Hardware stage:** out of scope for this initial scaffold; requires a separately
   reviewed, reversible plan and user data preservation.

## Result reporting

Every test report should include source revision, toolchain version, build configuration,
host OS, command, exit status, and artifact SHA-256. Distinguish:
- `PASS`: the stated test completed.
- `FAIL`: the stated test failed.
- `NOT RUN`: no test was performed.
- `NOT APPLICABLE`: the test does not cover this platform or milestone.

Never report a QEMU pass as proof that an iPhone7 boot works.

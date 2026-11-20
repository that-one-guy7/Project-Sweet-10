# XNU source review and baseline selection

Status: research note; no kernel has been built or booted by this repository yet.

## Candidate baseline

The public `dipa-studio/ios-sweet` project identifies its kernel as Apple's open-source
`xnu-8796`, the iOS 16 generation. That is a useful candidate for an initial source
study because the project demonstrates a substantial iOS 16 userland bring-up.

This does **not** establish that xnu-8796 supports the iPhone 7 platform. The SWEET
project's board support is for Qualcomm SM7150. Its machine configuration, platform
expert, device-tree properties, interrupt routing, memory map, timer setup, storage,
display, and input drivers are not an A10 implementation.

## Baseline policy

1. Select and record an exact upstream XNU tag or commit before modifying source.
2. Record the matching Xcode/Clang toolchain, SDK assumptions, build configuration,
   and all required open-source companion components.
3. Build the unmodified upstream source first. Save the full build log and artifact hashes.
4. Keep local patches in a numbered series with one concern per patch.
5. Do not import the SWEET patch series wholesale. Review each patch for platform
   assumptions and classify it as generic, toolchain-only, or Qualcomm-specific.
6. Keep Apple firmware, proprietary binaries, shared caches, and extracted root filesystems
   out of this repository.

## Patch classification

| Area in ios-sweet | Reuse for A10? | Required action |
|---|---|---|
| Build workflow and patch bookkeeping | Potentially | Adapt after independently verifying toolchain and licensing |
| Compiler compatibility fixes | Maybe | Reproduce against selected XNU revision; test separately |
| SWEET machine configuration | No | Requires an iPhone9,1 platform implementation |
| SWEET device-tree platform expert | No | Requires A10/iPhone9,1 device-tree analysis |
| SWEET timer and interrupt setup | No | Do not copy GICv3/Qualcomm assumptions |
| SWEET boot CPU implementation | No | Establish A10 CPU topology and boot contract independently |
| SWEET framebuffer, touch, and buttons | No | Different display and input hardware |
| Generic diagnostics and test discipline | Conceptually | Reimplement with clear platform boundaries |
| HFS/UFS and root-volume changes | Not automatically | Verify storage controller, filesystem, and licensing separately |

## Evidence required before the first A10 patch

- Exact target board identifier and SoC revision.
- A trustworthy iPhone9,1 device-tree source and documented property meanings.
- XNU platform code paths selected by the target build configuration.
- Boot argument structure and entry-state requirements for the chosen XNU revision.
- CPU topology, exception level, MMU granule, cache state, interrupt controller, and timer.
- Reserved memory regions and a verified memory map.
- A safe, reproducible test environment and a recovery plan.

## Upstream references

- [Apple XNU source](https://github.com/apple-oss-distributions/xnu)
- [ios-sweet README](https://github.com/dipa-studio/ios-sweet/blob/main/README.md)
- [ios-sweet XNU work area](https://github.com/dipa-studio/ios-sweet/tree/main/xnu)
- [ios-sweet patch series](https://github.com/dipa-studio/ios-sweet/tree/main/xnu/patches)

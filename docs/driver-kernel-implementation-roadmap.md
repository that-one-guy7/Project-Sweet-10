# Project Sweet-10: kernel and driver implementation roadmap

## Decision

**Actual iPhone9,1 XNU kernel and hardware-driver implementation is not ready to start.** The next useful work is to close source identity, build-input, and target-platform contracts, while keeping the work host-side and read-only. Writing target driver code before those inputs are established would require guessing CPU features, memory ranges, interrupt routing, DeviceTree encodings, and IOKit ABI details.

This is an unofficial research port for iPhone 7 `iPhone9,1` / D10AP / A10-T8010, using iOS 16.7.16 build `20H392` from iPhone X / iPhone10,3 as the donor userland reference. The physical phone remains on iOS 12.1.4. No firmware, partition, boot, or device operation is part of this roadmap.

## New source-history finding

The public XNU source comparison is now broader than the original three-tag audit:

| Public XNU snapshot | Historical T8010/H9 profile in audited ARM64 paths? | Use in this project |
|---|---:|---|
| `xnu-7195.121.3` | Yes | Historical source reference |
| `xnu-8020.101.4` | No | Target-era public reference; not proven to be the exact 19H422 kernel source |
| `xnu-8019.80.24` | No | Intermediate public reference |
| `xnu-8796.101.5` | No | Early Darwin 22 public reference |
| `xnu-8796.141.3` | No | Current pinned iOS 16-generation source candidate |
| `xnu-12377.1.9` | No | Later public source reference, not a Sweet-10 baseline |

In `xnu-7195.121.3`, the normal ARM64 machine list includes `T8010`, `MACHINE_FLAGS_ARM64_T8010` maps it to `-DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane`, `board_config.h` selects the T8010 block, and that block includes `H9.h`. The later public snapshots omit the T8010 machine flag, board block, and H9 header at the audited paths.

The shipped binaries add an important qualification:

- The iPhone 7 / 19H422 target KernelCache reports XNU `8020.241.44~1` and `RELEASE_ARM64_T8010`.
- The iPhone X / 20H392 donor KernelCache reports XNU `8796.142.1.703.8~1` and `RELEASE_ARM64_T8015`.

Neither shipped version label is an exact match for the public comparison tag reviewed above. The public source snapshots therefore do **not** establish the exact Apple source commit or product-specific build inputs used for either shipped binary. The missing public profile is a provenance and porting blocker, not proof that the shipped kernels lacked their reported platform support.

The matrix is pinned in `xnu/history/*.lock.json` and checked by the host-only `tools/audit_xnu_public_source_matrix.py` test. Its purpose is to prevent a future change from accidentally describing a historical profile as present in a newer public source tree.

## Compatibility boundary

Apple's iOS 16 compatibility list starts at iPhone 8 and does not list iPhone 7. Apple's security-release table separately lists iOS 15.8.8 for iPhone 7 and iOS 16.7.16 for iPhone 8 / 8 Plus / X. Thus `20H392` is a donor reference from a supported iPhone X, not an iPhone 7 target build. Sweet-10 is researching a nonstandard cross-generation port, not enabling an Apple-supported iOS 16 configuration.

References:
- [Apple: iOS 16 supported devices](https://support.apple.com/en-us/103267)
- [Apple: iOS 16 availability announcement](https://www.apple.com/newsroom/2022/09/ios-16-is-available-today/)
- [Apple: security releases](https://support.apple.com/en-us/100100)

## What is already established

- The target identity is iPhone9,1 / D10AP / A10-T8010.
- The 19H422 target-reference DeviceTree has been parsed and its board/SoC and selected display/touch nodes inventoried.
- Target-native 19H422 KernelCache metadata contains candidate display, MIPI-DSI, LCD, SPI/HID, and backlight KEXT personalities.
- Six target DeviceTree compatible strings have static `IONameMatch` overlaps in target-native KEXT metadata: `disp0,t8010`, `mipi-dsim-1,synopsys`, `lcd,pinot`, `spi-1,samsung`, `hid-transport,k1`, and `backlight,lm3539`.
- The 19H422 / 20H392 BackBoard loader audit is complete. The target and donor records have been compared; the two HID framework records differ by one donor-only `StudyLog` edge each.
- These findings are static metadata only. They do not prove driver source availability, KPI/ABI compatibility, runtime attachment, event delivery, display operation, or SpringBoard.

## Required gates before target-specific kernel code

| Gate | Evidence required before implementation | Current status |
|---|---|---|
| K1 — Kernel source provenance | Exact source/build inputs for 20H392 donor kernel, or a documented replacement baseline with explicit uncertainty; explain target 19H422 shipped-kernel source gap too | Open |
| K2 — T8010/H9 migration closure | Full transitive dependency and configuration-consumer review for historical T8010/H9 code against the selected baseline; each macro and removed interface classified | In progress; direct consumer audit exists, full closure is incomplete |
| K3 — Reproducible baseline build | Unmodified source build with pinned host OS, Xcode/SDK, compiler, IIG/MIG, external headers, SDK device-map input, build settings, logs, and artifact hashes | Not started; the current user host is Ubuntu and Apple build inputs are unverified |
| K4 — Target platform facts | Source-backed CPU features/topology, memory map, clock/timebase, interrupt controller and routing, timer, storage, DMA, power, and security facts | Incomplete |
| K5 — DeviceTree contract | Correct cell widths, property formats, required nodes, register ranges, compatible strings, interrupts, and references, each tied to evidence | Incomplete; the unusual multitouch `reg` property remains an explicit parsing caveat |
| K6 — XNU entry contract | Exact selected-baseline `boot_args` revision, entry-state assumptions, memory ownership, DeviceTree handoff, and required early services | Incomplete |
| K7 — Host verification | Synthetic/unit tests for new platform parsers and static checks; target-specific source patch review; reproducible compile result after K1-K6 | Not started for a target-specific kernel |

**Implementation start threshold:** K1-K6 must be closed with evidence, and K7 must have passing host tests. A generic compile alone is not enough to begin a target driver: the correct platform and hardware contracts must also be known.

## Recommended implementation order once the gates pass

1. **Unmodified kernel baseline:** establish a reproducible build of the chosen source before introducing local changes. This validates the toolchain only; it does not prove iPhone9,1 support.
2. **A10/T8010 platform foundation:** prepare a small, reviewable platform configuration from the completed H9 dependency analysis. Do not copy `H9.h` wholesale or bypass the machine-selection guard.
3. **CPU, memory, and DeviceTree contracts:** establish the CPU feature set, memory ownership/map, DeviceTree interpretation, and handoff interfaces before peripheral work.
4. **Interrupt controller and timer:** these are the first hardware-service candidates because later drivers depend on them. The actual controller, node, register ranges, IRQ mapping, counter frequency, and callbacks must be identified from D10AP evidence; do not assume AIC or reuse donor/Qualcomm values.
5. **Bus controllers:** only after bus resource/interrupt/power contracts are documented, assess SPI and I2C host-controller support.
6. **Leaf devices:** then assess the target-native display chain (display controller, MIPI-DSI, Pinot panel, LM3539 backlight) and input chain (Samsung SPI, K1 HID transport, multitouch layer). Their existence in the target KernelCache is a useful reference, not a compatibility guarantee for XNU 8796.
7. **Userland integration:** expand the target/donor service and framework comparison, then address launchd and the SpringBoard dependency set. M7 remains a separate milestone.

## Best next work now

The highest-value next preparation task is the **T8010/H9 transitive source-closure audit**: map every H9 macro, board-selection path, conditional consumer, required type/header, and removed interface into its XNU 8796 counterpart. The current macro consumer note is a useful first pass but is explicitly not exhaustive. In parallel, keep collecting source-backed D10AP platform facts without turning unknown DeviceTree fields into constants.

The next driver to implement cannot responsibly be selected until the target interrupt-controller and timer contracts are resolved. The current evidence only proves selected static personality matches; it does not identify the live controller implementation or all required register/IRQ data.

## Explicit non-goals for this preparation phase

- No checkm8/PongoOS execution instructions.
- No custom image-loading or boot commands.
- No restore, flashing, partition, or boot-state changes.
- No target-specific driver constants invented from donor or Qualcomm devices.
- No claim that a generic XNU build, a loader record, or a static IOKit personality makes SpringBoard bootable.

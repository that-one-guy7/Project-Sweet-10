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
| `xnu-10002.1.13` | No | Later public source reference, not a Sweet-10 baseline |
| `xnu-10002.41.9` | No | Later public source reference; same inspected source blobs as later 10002 tags |
| `xnu-10002.61.3` | No | Later public source reference; same inspected source blobs as 10002.41.9 and .81.5 |
| `xnu-10002.81.5` | No | Later public source reference; same inspected source blobs as 10002.41.9 and .61.3 |

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
- The 19H422 target KernelCache KEXT JSON contains `com.apple.driver.AppleInterruptController` version `1.0.0d1`; its `aic,1` personality expects `AppleARMIODevice`, exactly matching the target `/arm-io/aic` compatible string. This resolves static bundle/personality presence, not runtime attachment.
- The same target KEXT JSON records T8010 platform personalities for `arm-io,t8010`, `mcc,t8010`, `error-handler,t8010`, `pmgr1,t8010`, `apcie,t8010`, `soc-tuner,t8010`, and `clpc,t8010`. Provider and release details are recorded separately.
- The 19H422 / 20H392 BackBoard loader audit is complete. The target and donor records have been compared; the two HID framework records differ by one donor-only `StudyLog` edge each.
- These findings are static metadata only. They do not prove driver source availability, KPI/ABI compatibility, runtime attachment, event delivery, display operation, or SpringBoard.

## Required gates before target-specific kernel code

| Gate | Evidence required before implementation | Current status |
|---|---|---|
| K1 — Kernel source provenance | Exact source/build inputs for 20H392 donor kernel, or a documented replacement baseline with explicit uncertainty; explain target 19H422 shipped-kernel source gap too | Open |
| K2 — T8010/H9 migration closure | Full transitive dependency and configuration-consumer review for historical T8010/H9 code against the selected baseline; each macro and removed interface classified | Full-tree textual macro inventory completed for pinned XNU 7195/8796 (12 macros, 3,508/3,961 files, 23 locally resolved include files, two resolver gaps); schema-v2 scanner now records nested preprocessor guard context and malformed directive structure, but expressions/build inputs remain unevaluated and manual dependency/migration review remains incomplete |
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
4. **Interrupt controller and timer:** these remain the first early-service research priority. The target 19H422 metadata now identifies an `AppleInterruptController` KEXT with an exact `aic,1` personality match, but the private implementation, IRQ mapping/routing, acknowledge/EOI path, timer source/frequency, and callback contract remain unresolved. Do not infer them from generic headers or reuse donor/Qualcomm values.
5. **Bus controllers:** only after bus resource/interrupt/power contracts are documented, assess SPI and I2C host-controller support.
6. **Leaf devices:** then assess the target-native display chain (display controller, MIPI-DSI, Pinot panel, LM3539 backlight) and input chain (Samsung SPI, K1 HID transport, multitouch layer). Their existence in the target KernelCache is a useful reference, not a compatibility guarantee for XNU 8796.
7. **Userland integration:** expand the target/donor service and framework comparison, then address launchd and the SpringBoard dependency set. M7 remains a separate milestone.

## Best next work now

The first target-side AIC inventory is complete: 19H422 contains
`AppleInterruptController` version `1.0.0d1`, and its personality matches
`aic,1` with provider class `AppleARMIODevice`. The seven selected
T8010 platform personalities and their provider classes are also recorded.
This resolves KEXT presence and static match-property questions only.

The next bounded evidence task is to compare those same AIC/T8010 bundle
and personality records against the 20H392 iPhone X donor KernelCache.
That comparison must preserve release boundaries and must not treat a
matching personality as binary/KPI compatibility.

The full-tree T8010/H9 source-consumer audit has now been ported onto
current `main` and merged as
[PR #137](https://github.com/that-one-guy7/Project-Sweet-10/pull/137)
(merge commit `7bd0177a7b565855c1d4aa568cc4d09cb01ccfee`). Both checks on
the merged head passed: the H9 macro-consumer audit and pinned XNU/PongoOS
source verification. This closes the integration task for the textual
inventory, not K2 itself: manual conditional, build-input, dependency, and
per-feature migration review remains open.

Then close the remaining kernel gates: exact source/build provenance,
a reproducible unmodified baseline build, target CPU/memory/platform facts,
the complete DeviceTree and XNU handoff contracts, and host-side validation.
A target-specific kernel or driver is not ready while those gates are open.

The private AIC implementation is not present in the reviewed public XNU
paths. Static plist metadata is not enough to reconstruct a controller or
timer driver. The physical target remains on iOS 12.1.4; all current work
is host-side research.

## Explicit non-goals for this preparation phase

- No checkm8/PongoOS execution instructions.
- No custom image-loading or boot commands.
- No restore, flashing, partition, or boot-state changes.
- No target-specific driver constants invented from donor or Qualcomm devices.
- No claim that a generic XNU build, a loader record, or a static IOKit personality makes SpringBoard bootable.


### Ten-snapshot public-source follow-up (2026-11-21)

A read-only CI-backed matrix now includes four additional public
`xnu-10002` tags. All four omit the T8010 board block from
`pexpert/pexpert/arm64/board_config.h`, omit T8010 from the normal ARM64
allowlist in `makedefs/MakeInc.def`, and lack the historical
`pexpert/pexpert/arm64/H9.h` path. Their normal ARM64 allowlist is
`BCM2837 T6000 T8101 T8103 VMAPPLE`. The .41.9, .61.3, and .81.5
tags share the same inspected blob hashes for the board header, machine
allowlist, and kernel selection guard. This extends the bounded public-source
history; it does not make later tags candidate target baselines.

The ten-snapshot matrix and synthetic tests passed in
[GitHub Actions run 44938201241](https://github.com/that-one-guy7/Project-Sweet-10/actions/runs/44938201241).
The scope remains limited to the selected source/build-selection paths,
not a full-tree search or Apple's private product-specific build inputs.
No exact donor source provenance, T8010 port, ABI, device support, runtime
behavior, or bootability is established. The physical iPhone 7 remains on
iOS 12.1.4; M7/SpringBoard remains not started.


## Full-tree H9 source-consumer audit (2026-11-21)

The project now carries a reproducible read-only scanner for all 12 historical
H9 feature macros across complete pinned XNU 7195 and XNU 8796 source trees.
It records every textual occurrence with path, line, and coarse context,
compares the names with XNU 8796 H13 definitions, and resolves the local
include closure reachable from H9.h. The completed scan covered 3,508
historical and 3,961 candidate source/build files; 23 include files were
resolved locally and two SDK-style includes remain unresolved.

The scan is not a C preprocessor or linker. It does not decide whether a
conditional is active in an Apple product build, expand macros, reproduce
generated/private headers, or prove a feature exists on A10. Several shared
architecture consumers persist, but H13 definitions are not substitutes for
H9 settings. Three legacy macro names had no textual matches in the scanned
8796 candidate files; that is not proof of hardware absence or complete
removal. See [the full-tree H9 audit](h9-source-fulltree-audit.md).

A first manual classification is now recorded in
[h9-t8010-migration-risk-classification.md](h9-t8010-migration-risk-classification.md).
It identifies CPU startup/topology and KTRR-versus-CTRR as critical unresolved
contracts; PMU/AIC, page/pmap protection, sleep/timebase, and historical
errata as high-risk; and the L2 PMU-event macro as unresolved. The review
confirms that H13's T8101 profile is a contrast case, not an H9 replacement.
This is source-level classification only; it does not close the transitive
preprocessor/build-input review or establish iPhone9,1 runtime behavior.
Do not copy H9.h or enable old flags based on text matches. K2 remains open.


## A10/H9 CPU topology and secondary-core handoff (2026-11-21)

A new static comparison of XNU 7195.121.3 and 8796.141.3 found a useful
positive CPU clue: the 8796 topology parser retains a non-`HAS_CLUSTER`
path and explicitly documents H10 and earlier devices as a single cluster
for MPIDR-based indexing. The historical H9 profile does not define
`HAS_CLUSTER`, while H13 does. This is consistent with an H9-style legacy
topology, but does not prove the missing T8010 product configuration selects
that path.

A follow-up review also classified the three remaining 8796
`APPLEHURRICANE` references: cache-line definitions in `proc_reg.h`,
a Hurricane-specific PMU EL3-counter setting in `monotonic_arm64.c`, and
a CPU-name string in `sleh.c`. The first two are retained functional
compile-time behavior if the macro is selected; the third is diagnostic.
This strengthens the case that some H9-era CPU assumptions remain in the
newer generic source, but it does not prove a T8010 product build enables
them.

The target 19H422 DeviceTree has two CPU entries (`reg=0` running and
`reg=1` waiting), which is structurally consistent with a simple legacy
topology. It does not by itself establish the final enabled CPU count or
runtime donor handoff.

A major unresolved difference is the physical secondary-core release
contract: XNU 7195's `AppleARMSMP::PE_cpu_start` passes the physical
`LowResetVectorBase` address to `IOPMGR::enableCPUCore`; XNU 8796 passes
zero for physical builds and passes the reset-vector address only for
`APPLEVIRTUALPLATFORM`. The relevant PMGR implementation is not established
by the public source comparison. The historical H9 HID5 EDB snoop-reservation
workaround in 7195 `start.s` is also absent from the reviewed 8796 startup
assembly.

See [the A10/H9 CPU topology and handoff audit](a10-h9-cpu-topology-handoff-audit.md)
for exact source links, evidence boundaries, and the next static research
questions. This is positive source-level compatibility evidence, not proof
of T8010 build selection, secondary-core startup, runtime behavior, or
SpringBoard. K4 remains incomplete and no target-specific CPU code is ready.
The physical iPhone 7 remains on iOS 12.1.4.

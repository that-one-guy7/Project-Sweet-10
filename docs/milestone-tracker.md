# Milestone tracker

| ID | Milestone | Exit criterion | Status |
|---|---|---|---|
| M0 | Repository scaffold | Initial docs and target metadata | Prepared |
| M1 | Hardware/source audit | Evidence-backed iPhone9,1 inventory | In progress: xnu-7195.121.3 contains T8010/H9 and lists T8010 for normal ARM64 builds; xnu-8019.80.24 and xnu-8796.141.3 omit it from the normal ARM64 machine allowlist; static 19H422 DeviceTree is hash-verified and parsed (227 nodes); selected ARM-IO/AIC/timer values are cross-checked against XNU 8796, while zero-filled runtime clock/memory/panic fields remain unresolved; the pinned PongoOS revision has a registered T8010 HAL backend with USB resources and T8010 AES/Recfg paths, but target runtime is untested; T8010 is still absent from the XNU 8796 machine allowlist |
| M2 | XNU baseline | Exact revision and reproducible host build | Candidate `xnu-8796.141.3` is pinned; uploaded 20H392 manifest is iPhone X A11/T8015 (not iPhone9,1); Apple source-to-kernelcache mapping and reproducible iPhoneOS ARM64 baseline build remain open; xnu-8796.141.3 normal ARM64 machine allowlist omits T8010 |
| M3 | Boot contract | Reviewed A10 handoff specification | XNU 8796 ARM64 `boot_args` structure identified; PongoOS iOS13 layout matches its key offsets/608-byte command line at source level; PongoOS has a source-level T8010 HAL/USB backend, AES/Recfg paths, and audited `bootr`/`loadx` extension points, but no target runtime validation or complete custom loader. Runtime clock/memory/panic fields, live boot_args values, entry state, and a complete Sweet-10 loader remain unverified |
| M4 | Early-kernel test | Deterministic diagnostics in safe test environment | Not started |
| M5 | Display/input research | Independent subsystem plans | Static tree identifies T8010 display subsystem, Pinot LCD node, Samsung SPI controller, K1 multi-touch HID transport, and LM3539 backlight; no driver implementation or input/output operation validated |
| M6 | Root/userland research | launchd job dependencies documented | In progress: donor inventory reviewed (532 LaunchDaemons; 1,668 Mach services); six GUI/core executables confirmed as ARM64 Mach-O; direct links inspected for backboardd (46), runningboardd (6), and SpringBoard (4); iPhone X 20H392 SystemOS dyld cache parsed (2,710 images; 42 subcaches); prebuilt loader records inspected for backboardd (45 regular dependents plus one weak-link record with unresolved install name), runningboardd (6), and SpringBoard (4); suspicious section offsets excluded pending parser validation; recursive dependency graph, embedded XPC/IOKit matching, and iPhone9,1 service compatibility remain unverified; four framework loader records collected successfully (BackBoardHIDEventFoundation: 10 regular; BackBoardHIDEventProcessors: 9 regular; BackBoardServices: 12 regular plus one re-export; IOMobileFramebuffer: 4 regular); the next donor-side layer is selected from these observed edges; target service compatibility remains unverified; a subsequent six-image layer was collected (BoardServices, BaseBoard, GraphicsServices, RunningBoardServices, AssertionServices, IOSurface: 44 regular, two weak-link, one raw kind-3 record source-mapped to weak-link + re-export (original ipsw label retained)); IOKit/CoreGraphics/FontServices inspection is next |
| M7 | SpringBoard | GUI starts and remains stable in controlled test | Long-term goal; not started |

## Reference-project progress

- Reviewed `ios-sweet` as the initial Qualcomm SM7150/XNU 8796 reference.
- Reviewed `ios-sunstone` revision
  `e0471191ddbfb17fde6674db41320bffa832a85b` as a later-stage XNU 8796 plus
  iPhone X 20H392 reference. It reports SpringBoard on Qualcomm SM4375 hardware.
- Reviewed `ios-qemu` as a virtualized iPhone X 20H392 userland reference. It reports
  SpringBoard on QEMU virtual hardware using a rebuilt XNU 8796-generation kernel.
- Reviewed UniXNU's shared ARM64 / SoC / device / loader / kernel / userland architecture and its 20H392 profile records. A downstream iPhone X D22AP profile reports the pinned XNU candidate; this is corroboration, not an Apple-published mapping. Its UEFI and non-Apple platform implementations are not A10 code.
- Reviewed Corellium's Sandcastle README and `loader/load-linux.c`. Its loader is
  explicitly Linux/PongoOS-specific. It is useful for boot-environment architecture,
  not as an XNU loader or source of iPhone9,1 hardware values.
- These projects are useful for source organization, patch discipline, build
  reproducibility, and subsystem boundaries. Their Qualcomm or QEMU-specific
  hardware implementations are not portable A10/T8010 code.

## Change log

- 2026-11-19: Initial documentation scaffold prepared for iPhone 7 `iPhone9,1`.
  No device changes performed.
- 2026-11-20: Pinned a candidate XNU source revision, selected the 20H392 userland
  reference, and mapped ARM64 source/configuration consumers. Exact kernel matching,
  target hardware evidence, and a reproducible baseline build remain open.
- 2026-11-20: Added the ios-sunstone cross-project comparison. Its SpringBoard result
  is an upstream report on SM4375 hardware, not evidence of A10 support.
- 2026-11-20: Added the ios-qemu reference study. Its reported 20H392 SpringBoard
  result is on a QEMU virtual board and does not establish iPhone9,1 support.
- 2026-11-20: Added a Sandcastle loader source review and an XNU handoff evidence
  checklist. No boot implementation or target-specific values were added.
- 2026-11-20: Audited pinned XNU 8796 ARM64 board configuration. The reviewed
  board_config.h has no T8010 profile; a T8010 reference in a later-branch code-signing
  test is test logic, not platform bring-up. Target support remains unverified.
- 2026-11-20: Added an index-level 20H392 restore identity audit. The six indexed
  iPhone10,1 through iPhone10,6 restore targets are A11/T8015; iPhone9,1 is
  A10/T8010 and is not in that restore set. Exact manifest/component validation
  remains open; no device operation or compatibility claim was made.
- 2026-11-20: Added a read-only BuildManifest evidence checklist. Exact donor
  manifest identities and KernelCache/DeviceTree metadata remain uninspected;
  no target-specific compatibility claim was added.
- 2026-11-20: Added a standard-library read-only IPSW BuildManifest inspector and
  synthetic unit tests. It reports every BuildIdentity without selecting a donor;
  no IPSW or device was accessed during the test design.
- 2026-11-20: Audited the user-supplied standalone 20H392 BuildManifest. It lists
  only iPhone10,3 and iPhone10,6, with four erase/update identities across
  D22AP/D221AP and A11/T8015 chip ID 0x8015. KernelCache and per-board DeviceTree
  paths/digests were recorded; no iPhone9,1 identity or compatibility was inferred.
- 2026-11-20: Compared historical Apple XNU T8010/H9 configuration across tags.
  The old profile exists in xnu-7195.121.3 but is absent at corresponding paths in
  xnu-8019.80.24 and xnu-8796.141.3. Added an explicit kernel-implementation
  readiness gate; target kernel work remains blocked on source, build, platform,
  device-tree, and handoff evidence.

- 2026-11-20: Compared XNU MakeInc.def machine allowlists across tags. T8010 is
  listed in xnu-7195.121.3 but absent from xnu-8019.80.24 and xnu-8796.141.3.
  The pinned MakeInc.kernel validates machine selections against that allowlist.
  MakeInc.top optionally uses the SDK embedded-device-map database to map target
  products to KernelPlatform; this database has not been inspected. No machine
  override or target-specific kernel configuration was added.
- 2026-11-20: Followed the public XNU path history from the XNU 7195.50.7.100.1
  import (2020-11-19) to the XNU 8019.41.5 import (2022-02-04). The parent
  snapshot has H9.h, the T8010 board block, and the T8010 ARM64 Hurricane
  machine/compiler mapping; the 8019.41.5 snapshot has none of those at the
  reviewed paths. This narrows the public snapshot transition but does not
  reveal Apple's internal rationale or prove a downstream/private implementation.
  Added docs/t8010-public-source-transition.md.
- 2026-11-20: Compared historical H9 feature macros and selected consumers
  between xnu-7195.121.3 and xnu-8796.141.3. Generic PAN, 16K-page, global
  sleep, and some PMU conditionals remain; the old MIGSTS and single-step
  workaround conditionals were not found in the corresponding reviewed files.
  XNU 8796 H13 uses CTRR rather than H9's KTRR declaration. This bounded source
  review does not establish target compatibility or provide a complete
  dependency graph. Added docs/h9-feature-macro-consumer-audit.md.
- 2026-11-20: Compared the ARM64 platform interfaces in xnu-7195.121.3 and
  xnu-8796.141.3. The visible boot_args field order and PE_init_platform
  signature remain, while CPU topology parsing has newer cpumask/cluster
  accounting and split CPU count updates. Both versions parse DeviceTree CPU
  nodes and map CPU/cluster register ranges; iPhone9,1 values remain unknown.
  Added docs/arm64-platform-interface-comparison.md.
- 2026-11-20: Compared ARM64 interrupt and timer interfaces in xnu-7195.121.3
  and xnu-8796.141.3. The DeviceTree register-mapping helper and ARM64
  ml_init_interrupt/ml_init_timebase interfaces are unchanged; AIC headers are
  byte-identical. Generic decrementer access uses CNTV_TVAL_EL0 when no
  per-CPU callback is present, while the newer timebase read adds nonspeculative
  counter selection and a sleep/wake race retry. Target IRQs, register ranges,
  and timebase frequency remain unknown. Added
  docs/interrupt-timer-interface-audit.md.
- 2026-11-20: Found public firmware metadata for iPhone9,1 / CPID 0x8010 /
  BDID 0x08 DeviceTree.d10ap.im4p components in builds 15A372, 15A402, and
  19A346, with separate per-build digest pairs and DeviceTree/RestoreDeviceTree
  names. Public indexes list 19H422 as an iPhone9,1 stock reference, but the
  checked fwkeydb snapshot does not include that build. No DT payload or
  property values were parsed; existing property rows remain Unknown. Added
  docs/iphone91-stock-firmware-device-tree-evidence.md and updated the
  DeviceTree property inventory.
- 2026-11-20: Audited public iPhone9,1 / D10AP / iOS 15.8.8
  (19H422) DeviceTree evidence. Ios-emul's scripted survey reports 226 nodes,
  two Hurricane-Zephyr CPU nodes, T8010 arm-io, an AIC child, and an
  AIC-timebase child, but omits raw register addresses, IRQ specifiers,
  timer properties, CPU state/topology values, and clock values. Orchard
  publishes the 19H422 IPSW, BuildManifest, and DeviceTree hashes; Sweet-10
  has not independently recomputed those hashes or parsed the binary.
  Updated the artifact evidence audit and property inventory; all property
  values remain Unknown. Added
  docs/iphone91-19h422-device-tree-structure-audit.md.

- 2026-11-20: Reviewed the iPhone9,1 / 19H422 DeviceTree survey generator. Its `reg` summary assumes fixed 16-byte little-endian 64-bit address/size pairs and does not validate parent cell-count properties; these totals are now classified as heuristics, not hardware register extents. Corrected the upstream survey-file link and added a method-review note. Raw target property values remain Unknown.
- 2026-11-20: Pinned an upstream PongoOS source review at `4c9b7541629234147fcc778f0ce4162482aaccef`. Its README distinguishes a Pongo shell from the consolidated PongoOS/KPF path to XNU; KPF source contains in-place kernel patch callbacks. Compared this with XNU 8796.141.3's ARM64 `boot_args` definition and `start.s` consumers. The custom Sweet-10 image-loader contract remains open; no boot attempt or device operation was performed.
- 2026-11-20: Verified the user-supplied iPhone9,1 / D10AP / iOS 15.8.8 (19H422) BuildManifest and DeviceTree IM4P. Both SHA-256 values match pinned Orchard metadata; the component SHA-384 matches the 48-byte BuildManifest Digest. The manifest lists iPhone9,1 and iPhone9,3 and contains D10AP Erase (identity 1) and Update (identity 3) entries pointing to DeviceTree.d10ap.im4p and kernelcache.release.iphone9. The IM4P is a dtre component with a bvx2 LZFSE payload. Raw DeviceTree properties remain unparsed; no firmware or device operation was performed. Added a host-side verifier, synthetic tests, and an artifact verification record.
- 2026-11-20: Decompressed and independently parsed the verified iPhone9,1 / D10AP / 19H422 DeviceTree: 227 nodes including root, full 160,572-byte input consumed, no trailing bytes. Extracted the ARM-IO ranges and cross-checked XNU 8796's SoC-base read (`0x200000000`), AIC first register window and AIC-timebase mapping inputs. Found CPU0 clock properties present but zero, memory/PRAM/VRAM regions zero, and `/chosen/embedded-panic-log-size` absent in the static component; XNU's source comments that iBoot `UpdateDeviceTree()` supplies panic-region fields. Added a privacy-filtered parser, seven synthetic tests, a sanitized JSON report, and a parsed DeviceTree audit. The raw DeviceTree is not committed because it contains device-specific identifiers and machine-specific data.

- 2026-11-20: Audited the pinned PongoOS raw-payload and KernelCache-copy implementations. The `bootr` path dispatches to an uploaded raw payload with existing boot arguments and original kernel entry point; `loadx` copies bytes over the existing KernelCache but leaves `gEntryPoint` adjustment and Mach-O parsing to another component. Pongo's SoC identifier recognizes `t8010`, which is not proof of full iPhone9,1 support. M3 remains open; no device command or kernel replacement was performed.

- 2026-11-20: Compared PongoOS's iOS13 `boot_args` view with XNU 8796.141.3's ARM64 declaration. Both use a 608-byte command-line buffer and yield matching key field offsets and a 0x2e0-byte structure on ARM64 when PongoOS's explicit padding is compared with XNU's natural alignment. This establishes source-level layout agreement only; live target values remain unknown.

- 2026-11-20: Audited PongoOS revision `4c9b7541629234147fcc778f0ce4162482aaccef` beyond SoC-name recognition. It registers an Apple A10 (T8010) HAL platform driver, selects it from DeviceTree-derived `socnum`, provides T8010 USB resource values consumed by the Synopsys OTG driver, and includes T8010 AES and Reconfig Engine paths. This establishes meaningful source-level PongoOS A10 support, not runtime validation on iPhone9,1; the XNU 8796 machine-profile and complete custom-loader gates remain open. Added `docs/pongo-t8010-platform-backend-audit.md`.

- 2026-11-20: Added pinned commit locks for public XNU tags
  xnu-7195.121.3 and xnu-8019.80.24, plus a read-only CI audit comparing
  the historical T8010/H9 machine allowlist, compiler flags, board block,
  H9 header, and kernel machine-selection guard against xnu-8796.141.3.
  Synthetic host tests cover missing and unexpectedly reintroduced profile
  elements. This validates public source identity and structure only; no XNU
  build, device operation, or iPhone9,1 compatibility claim was added.

- 2026-11-20: Started M6 with a source-pinned review of the Sunstone 20H392
  userland root tweaks, launchd logging helper, early-init diagnostic, and
  SpringBoard/HID reference patches. Added a privacy-conscious read-only
  inventory for the central launchd LaunchDaemons plist, including MachServices
  provider names and selected scheduling metadata; full arguments and
  environment values are omitted. Synthetic tests do not use an Apple root
  filesystem. Actual 20H392 rootfs inventory and iPhone9,1 dependency mapping
  remain open.

- 2026-11-20: Reviewed the user's actual mounted iPhone X 20H392 launchd
  inventory. The central plist contains 532 LaunchDaemons and advertises
  1,668 distinct Mach service names; the source plist SHA-256 is recorded in
  the M6 audit. Core donor launchd entries include backboardd, runningboardd,
  SpringBoard, configd, notifyd and mediaserverd. This is donor-side static
  configuration only; executable presence, runtime registration and
  iPhone9,1 compatibility remain unverified.

- 2026-11-20: Inspected the donor ARM64 Mach-O files for backboardd,
  runningboardd, and SpringBoard. Direct linked-library counts are 46, 6,
  and 4 respectively. backboardd directly references HID/display, IOMobileFramebuffer,
  Metal, graphics, IOKit, biometric and accessory frameworks. SpringBoard
  declares @executable_path/Frameworks; no LC_RPATH entries were reported for
  backboardd or runningboardd. This is load-command metadata only; the recursive
  dependency closure and full split-volume resolution remain unverified.


- 2026-11-20: Mounted the separate iPhone X 20H392 SystemOS Cryptex and
  inspected its split dyld shared cache with ipsw 3.1.749. The cache header
  reports iOS 16.7, 2,710 images, 42 subcaches, and UUID
  8F970452-C9E3-3E88-B114-FEB1864BC9E0. The image list includes Foundation,
  CoreFoundation, CoreGraphics, Metal, IOKit, IOSurface, AVFoundation,
  BackBoard HID, RunningBoard, and SpringBoard framework images. This is
  donor-side static cache metadata only; it does not establish transitive
  dependencies or iPhone9,1 runtime compatibility. Added
  docs/20h392-dyld-cache-inventory.md.


- 2026-11-20: Inspected the 20H392 SystemOS PrebuiltLoaderSet records for
  backboardd, runningboardd, and SpringBoard with ipsw 3.1.749. The complete
  backboardd Dependents block later supplied by the user contains 45 regular
  install names plus one weak-link record whose install name is unresolved;
  runningboardd lists six regular dependents and SpringBoard lists four.
  Bind-target records are present in the latter two outputs. Several
  Swift/Objective-C section offsets look implausible and are excluded pending
  independent parser validation. The earlier first-60-lines display was only
  a terminal excerpt; the later complete block resolves the backboardd
  dependent count. These are donor-side static loader records only; no
  iPhone9,1 runtime compatibility or SpringBoard milestone is established. Added
  docs/20h392-prebuilt-loader-audit.md.

- 2026-11-20: Added a bounded, read-only host-side plan to expand the 20H392 backboardd loader graph through BackBoardHIDEventFoundation, BackBoardHIDEventProcessors, BackBoardServices, and IOMobileFramebuffer. This records requested evidence and graph rules only; no framework-specific results or iPhone9,1 compatibility are claimed.

- 2026-11-20: Collected the four planned 20H392 BackBoard framework PrebuiltLoaderSet dependent blocks. All ipsw queries exited 0. Recorded 35 regular dependency rows plus one separately typed re-export and no weak-link rows. This expands only the iPhone X donor graph; it does not validate iPhone9,1 providers or runtime compatibility. Added docs/20h392-backboard-framework-dependency-results.md.


- 2026-11-20: Collected six additional 20H392 donor framework loader records for
  BoardServices, BaseBoard, GraphicsServices, RunningBoardServices,
  AssertionServices, and IOSurface. The supplied output contains 44 regular
  rows, two weak links to BaseBoard, and one GraphicsServices row printed as
  unknown kind 3. Pinned ipsw source shows kind 3 is the combined bit value
  1|2 (weak-link|re-export); Apple's dyld formats those flags independently,
  so this is a strong but not raw-byte-verified interpretation. No
  iPhone9,1 runtime compatibility is established. Added
  docs/20h392-platform-framework-dependency-results.md.

- 2026-11-20: Inspected the exact ipsw v3.1.749 source commit and Apple dyld
  LinkedDylibAttributes source. ipsw's exact-value formatter prints combined
  kind 3 as unknown, while Apple's one-byte bitfield defines weakLink as bit 0
  and reExport as bit 1 and formats them independently. The previously observed
  GraphicsServices kind-3 edge is therefore source-mapped as weak-link plus
  re-export; raw ipsw output remains preserved. Added the source explanation
  to the donor framework audit.

- 2026-11-20: Collected 20H392 donor loader records for IOKit, CoreGraphics,
  and libGSFont.dylib. The supplied output contains 25 regular dependencies,
  one explicit weak link, and three kind-3 entries mapped to weak-link plus
  re-export. Added the full result inventory and a bounded FontServices/CoreText
  follow-up plan. No iPhone9,1 runtime compatibility is established.

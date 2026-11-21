# Milestone tracker

| ID | Milestone | Exit criterion | Status |
|---|---|---|---|
| M0 | Repository scaffold | Initial docs and target metadata | Prepared |
| M1 | Hardware/source audit | Evidence-backed iPhone9,1 inventory | In progress: xnu-7195.121.3 contains T8010/H9 and lists T8010 for normal ARM64 builds; xnu-8019.80.24 and xnu-8796.141.3 omit it from the normal ARM64 machine allowlist; static 19H422 DeviceTree is hash-verified and parsed (227 nodes); selected ARM-IO/AIC/timer values are cross-checked against XNU 8796, while zero-filled runtime clock/memory/panic fields remain unresolved; the pinned PongoOS revision has a registered T8010 HAL backend with USB resources and T8010 AES/Recfg paths, but target runtime is untested; T8010 is still absent from the XNU 8796 machine allowlist |
| M2 | XNU baseline | Exact revision and reproducible host build | Candidate `xnu-8796.141.3` is pinned; 20H392 donor KernelCache reports XNU `8796.142.1.703.8~1` / `RELEASE_ARM64_T8015`, while the public candidate omits both T8015 and T8010 machine profiles; an independent UniXNU OnePlus 13 / SM8750 profile co-pins the same donor KernelCache SHA-256 with the same public XNU commit and reports 62 clean patch applications only (compilation, binary ABI, and hardware remain separate); its candidate kernel path is `DEVELOPMENT_ARM64_BCM2837`, not T8015/T8010; exact Apple source provenance, product-specific build inputs, and reproducible iPhoneOS ARM64 baseline build remain open |
| M3 | Boot contract | Reviewed A10 handoff specification | XNU 8796 ARM64 `boot_args` structure identified; PongoOS iOS13 layout matches its key offsets/608-byte command line at source level; PongoOS has a source-level T8010 HAL/USB backend, AES/Recfg paths, and audited `bootr`/`loadx` extension points, but no target runtime validation or complete custom loader. Runtime clock/memory/panic fields, live boot_args values, entry state, and a complete Sweet-10 loader remain unverified |
| M4 | Early-kernel test | Deterministic diagnostics in safe test environment | Not started |
| M5 | Display/input research | Independent subsystem plans | Static tree identifies T8010 display subsystem, Pinot LCD node, Samsung SPI controller, K1 multi-touch HID transport, and LM3539 backlight; target-native 19H422 KernelCache (XNU 8020.241.44~1, `RELEASE_ARM64_T8010`) includes candidate display/touch/backlight KEXTs; target IOKit personalities show exact `IONameMatch` overlaps for `disp0,t8010`, `mipi-dsim-1,synopsys`, `lcd,pinot`, `spi-1,samsung`, `hid-transport,k1`, and `backlight,lm3539`; extracted `MultitouchHID.plugin/Info.plist` has type UUID `0516B563-B15B-11DA-96EB-0014519758EF`, which exactly matches the `AppleMultitouchDriver` `IOCFPlugInTypes` key; runtime provider attachment, plugin loading, and hardware operation remain unverified |
| M6 | Root/userland research | launchd job dependencies documented | In progress: donor-side inventory covers 532 LaunchDaemons, 1,668 advertised Mach services, six ARM64 GUI/core executables, direct links for backboardd/runningboardd/SpringBoard, the 2,710-image 20H392 SystemOS cache, PrebuiltLoaderSet records, framework dependency layers through BackBoard, service/graphics, IOKit, FontServices, and CoreText, plus the extracted iPhone10,3 donor KernelCache (Darwin 22.6.0 / XNU `8796.142.1.703.8~1` / `RELEASE_ARM64_T8015`; SHA-256 `2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221`) and its four requested multitouch/HID KEXT records; target-side 19H422 DeviceTree is independently hash-verified and parsed (227 nodes), confirming D10AP/T8010 display, Pinot LCD, Samsung SPI/K1 multitouch, and LM3539 backlight node identities; the 19H422 KernelCache is extracted and inspected on the host (44,924,928 bytes; SHA-256 `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`; Darwin 21.6.0 / XNU `8020.241.44~1` / `RELEASE_ARM64_T8010`; 230 KEXT entries, including candidate display/touch/backlight bundles); static personality metadata now confirms six exact target `IONameMatch` overlaps plus a target multitouch plugin Info.plist/type-UUID link between `AppleMultitouchDriver` and `MultitouchHID.plugin`; the donor 20H392 plugin filesystem Info.plist has also been inspected (version 6140.3; minimum OS 16.7; SHA-256 recorded in the donor-plugin audit) and its type UUID, factory UUID, and IOHIDPlugInFactory declaration exactly match the target 19H422 plugin (version 5100.27; minimum OS 15.8); the donor plugin declares CFBundleExecutable=MultitouchHID; its CodeResources plist reports files and files2 as empty entries; recursive file/symlink search found no matching executable in either searched donor mount root, and the inspected target plugin directory lists only Info.plist; the complete read-only target 19H422 filesystem DMG 098-68844-067.dmg was mounted at $HOME/19H422-full-fs-mount and searched for regular files/symlinks matching MultitouchHID*, with no paths returned; the result is limited to that filesystem image and filename pattern; the target 19H422 dyld shared-cache image inventory now lists MultitouchHID.plugin/MultitouchHID at index 1948, version 5100.27.0.0.0, UUID 304953E6-6B67-3CF1-B7CA-E011978210DE; standalone filesystem file was not found and raw cache Mach-O bytes have not been separately compared; the corresponding 20H392 donor cache image is now confirmed at the same full install path (donor index 2557, version 6140.3.0.0.0) versus target index 1948, version 5100.27.0.0.0; donor AppleHIDTransportSupport is 6140.1.0.0.0 versus target 5100.32.0.0.0, and donor MultitouchSupport / MultitouchSessionFilterSupport are 6140.3.0.0.0 versus target 5100.27.0.0.0; the follow-up `ipsw dyld image -V` output showed prebuilt-loader/closure metadata (VM Size `0x20e0c000`, loader ref index 2556, five regions, and 14 dependency rows: 11 regular and three weak-link) but did not print a UUID; that reference index is not equated with image-list index 2557, and implausible section offsets are excluded; donor `MultitouchHID` UUID is now confirmed as `78E1FB55-113A-3500-9D2D-1D8E282BED45` at image-list index 2557 (load address `8757542912`), versus target UUID `304953E6-6B67-3CF1-B7CA-E011978210DE` at index 1948; the identifiers differ and raw Mach-O bytes have not been separately extracted or compared; target-native 19H422 `MultitouchHID` PrebuiltLoaderSet record has now been inspected (status 0): VM Size `0x2e9f4000`, loader ref index 1947, 5 regions, 13 dependencies (10 regular, 3 weak-link); donor record has 14 (11 regular, 3 weak-link), with donor-only printed dependency `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` and different IOKit path form; both section-offset outputs contain implausible decoded values and are excluded; target 19H422 cache image inventory now confirms records for the seven selected loader dependency names: SymptomDiagnosticReporter (index 1455, version 174.140.2.0.0, UUID ED77A600-C0BE-3240-9693-BF5238095816), WirelessDiagnostics (6), CoreAccessories (343), CoreAnalytics (262), MultitouchSupport (1249), IOKit (71), and ProtocolBuffer (186); this shows the donor-only SymptomDiagnosticReporter direct dependency edge is not a target cache-image absence; exact versions/UUIDs and paths are recorded in the dependency-image audit; equivalent selected-name comparison against donor 20H392 inventory is complete; all seven corresponding target/donor framework image records have different version strings and Mach-O UUIDs; full values are recorded in docs/20h392-19h422-multitouch-dependency-image-comparison.md; runtime IOKit attachment, plugin loading, and cross-board compatibility remain unverified; exact-set export comparison confirms zero target-only names, seven donor-only regular exports, no differing printed kinds among common names, and 277 common names with different first printed addresses (cache-layout metadata only); row totals, unique-name counts, and duplicate-name summary were not present in the pasted output |
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

- 2026-11-20: Added an independent UniXNU 20H392 source-baseline
  cross-check. The downstream OnePlus 13 / SM8750 profile co-pins the
  same iPhone10,3 donor KernelCache SHA-256 with the public
  `xnu-8796.141.3` commit used by Sweet-10. Its strict report passes
  62 ordered patch applications but explicitly excludes compilation,
  binary ABI, and hardware validation. The profile's candidate kernel
  path is `DEVELOPMENT_ARM64_BCM2837`, not a T8015/T8010 target build.
  Added docs/unixnu-20h392-xnu-baseline-crosscheck.md and updated the
  baseline selection, source-provenance, readiness, and UniXNU reference
  notes. G1/M2 remain open; no device or firmware state changed.

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


- 2026-11-20: Completed the bounded 20H392 donor FontServices/CoreText
  loader inspection. Four queries (libFontParser, FontServices,
  libGSFontCache, CoreText) exited 0. Recorded 37 regular dependents, one
  explicit weak link to SpringBoardServices, and six raw kind-3 entries
  mapped to weak-link + re-export using pinned ipsw and Apple dyld source.
  Added docs/20h392-fontservices-coretext-dependency-results.md and closed
  the corresponding inspection plan. Further broad donor crawling is
  deferred in favor of target-native iPhone9,1 applicability evidence.


- 2026-11-20: Re-mounted the 20H392 root filesystem and SystemOS Cryptex
  separately with APFS-FUSE and confirmed the installed mount layout exposes
  each filesystem below a child `root/` directory. The corrected SystemOS
  cache path was inspected with ipsw 3.1.749. The main file parsed as
  `dyld_v1   arm64`; the header/mapping report confirms iOS 16.7,
  2,710 images, 42 subcaches, and UUID
  `8F970452-C9E3-3E88-B114-FEB1864BC9E0`, with per-subcache mapping records.
  Expanded the target-native crosswalk using the already verified 19H422
  DeviceTree node inventory. The next M6 step is a host-only KEXT and IOKit
  personality inventory from the target KernelCache. The phone remains on
  iOS 12.1.4; no device or firmware operation was performed.


- 2026-11-20: The user supplied the path and size (44,924,928 bytes) of the extracted
  iPhone9,1 / 19H422 KernelCache component:
  `kernelcache.release.iPhone9,1_3`. This records artifact staging only.
  On 2026-11-20, the user supplied the resulting read-only inspection: SHA-256
  `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`, Darwin
  21.6.0 / XNU `8020.241.44~1` / `RELEASE_ARM64_T8010`, and 230 KEXT entries.
  Candidate target display, SPI/HID, multitouch, and backlight bundle IDs are
  cross-referenced with the parsed DeviceTree. IOKit personality metadata and
  provider matching remain pending. No KernelCache or KEXT binary is committed;
  no phone operation was performed.


- 2026-11-20: Inspected the 19H422 target KernelCache JSON IOKit personalities.
  Found exact `IONameMatch` overlaps between target DeviceTree compatible
  strings and the AppleMobileDispH9P display personality, ApplePinotLCD panel
  personality, AppleSamsungSPI controller personality, AppleHIDTransportSPI
  K1 transport personality, and AppleLMBacklight LM3539 personality. The
  AppleMultitouchDriver metadata references the AppleMultitouchSPI
  MultitouchHID plugin path; the AppleMultitouchSPI JSON item itself exposed
  no personality field. The target MIPI-DSI parent compatible and display
  backlight-control property remain absent from the allowlist summary.
  Runtime IOKit attachment and hardware operation remain untested. Added
  docs/iphone91-19h422-iokit-personality-crosswalk.md.


- 2026-11-20: Extended the privacy-filtered DeviceTree inspector with a
  presence-only `backlight-control` allowlist field and retained the already
  selected `/arm-io/mipi-dsim` compatible value in the report. Added synthetic
  tests for the Synopsys MIPI-DSI parent compatible, an empty boolean-style
  backlight-control marker, and continued exclusion of an unrelated display
  serial-number property. Awaiting the user's host-side output from the exact
  19H422 raw DeviceTree; no target values are inferred before inspection.


- 2026-11-20: Completed the user's host-side run of the privacy-filtered inspector on the iPhone9,1 / 19H422 DeviceTree. The parsed stream contained 227 nodes across 160,572 bytes, matched the previously recorded SHA-256 `39331154d60f05923da0b2c5dc9ac6395da6a8276f0952e997dbdcfa81c2420e`, and had zero trailing bytes. It confirmed `/arm-io/mipi-dsim` compatible `mipi-dsim-1,synopsys`, adding a sixth exact target-native `IONameMatch` overlap for `AppleSynopsysMIPIDSI`. The allowlisted output did not report `backlight-control` on `/arm-io/disp0`; the separate display-to-backlight association remains unconfirmed. The output confirms that arbitrary DeviceTree properties and unique identifiers were not emitted. The raw tree is not committed. No runtime IOKit attachment or hardware operation is claimed.


- 2026-11-20: Audited the pinned ipsw 3.1.749 implementation for KEXT JSON output
  and KEXT extraction. `kernel kexts --json` serializes the KernelCache
  `__PRELINK_INFO.__info` bundle records; `io_kit_personalities` is an
  optional `omitempty` field. The absence of that key from the
  `AppleMultitouchSPI` JSON record therefore does not prove that the KEXT's
  nested `MultitouchHID.plugin` is absent or unused. The plugin must be checked
  separately in the matching 19H422 filesystem bundle. Updated the target KEXT
  inventory to distinguish KernelCache metadata from filesystem-plugin
  metadata. No KEXT or plugin binary is committed, and no device or firmware
  operation was performed.


- 2026-11-20: Audited the pinned ipsw 3.1.749 Linux filesystem-DMG mount path
  after the user's 19H422 extraction attempt. Source review confirms that when
  both APFS and HFS+ magic probes are inconclusive, ipsw tries APFS-FUSE first
  and then falls back to HFS+. The final "no HFS+ partition found" / MBR-GPT EOF
  message can therefore be a secondary fallback error and does not establish
  that the target filesystem is HFS+ or that the IPSW is corrupt. The exact
  APFS-FUSE failure remains unknown pending verbose output. Added
  docs/ipsw-linux-dmg-mount-fallback-audit.md. Host-side analysis only; the
  iPhone remains on iOS 12.1.4.

- 2026-11-20: Inspected the mounted 20H392 donor filesystem's nested
  `MultitouchHID.plugin/Info.plist`. The file is 1,126 bytes with SHA-256
  6700b351288f1420754edcc8107a118b935d7ce250653f737ff448f9ddb7f3b1.
  It reports bundle `com.apple.iokit.plugin.MultitouchHID`, version 6140.3,
  minimum OS 16.7, and iPhoneOS. Its plugin type UUID
  0516B563-B15B-11DA-96EB-0014519758EF, factory UUID
  0CB0FBB9-15EA-11DB-A93C-001451D47183, and `IOHIDPlugInFactory`
  declaration exactly match the 19H422 target plugin; the target is version
  5100.27 with minimum OS 15.8. This is static metadata continuity only;
  executable inspection, cryptographic signature verification, runtime
  loading, and touch-event delivery remain unverified. Added
  docs/20h392-multitouch-plugin-audit.md.

- 2026-11-20: Extracted and inspected the actual iPhone10,3 / D22AP
  iOS 16.7.16 (20H392) donor KernelCache from the user's complete IPSW.
  ipsw 3.1.749 reports Darwin 22.6.0 / XNU 8796.142.1.703.8~1 /
  RELEASE_ARM64_T8015, SHA-256
  2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221.
  Four requested HID/multitouch bundles were found. The donor's
  AppleHIDTransportSPI retains hid-transport,k1 and hid-transport,spi
  IONameMatch values; its AppleMultitouchDriver uses the same plugin type
  UUID found in the extracted 19H422 target plugin Info.plist. The donor
  AppleMultitouchSPI reports version 6140.3 versus 5100.27 in the target;
  selected multitouch parser/probe properties differ. These are static
  metadata comparisons only. The donor is A11/T8015 and the target A10/T8010;
  the pinned public XNU 8796.141.3 source is not yet mapped exactly to the
  donor binary, and no cross-board or runtime compatibility is established.
  Added docs/20h392-19h422-multitouch-kernelcache-comparison.md.

- 2026-11-20: Resolved the host-side 19H422 filesystem metadata extraction
  blocker using the standalone Linux ipsw 3.1.749 archive. The Snap-packaged
  command could not see the host APFS-FUSE executable at its configured path;
  the standalone binary mounted filesystem DMG 098-68844-067.dmg and extracted
  the target `MultitouchHID.plugin/Info.plist` and
  `_CodeSignature/CodeResources`. The plugin metadata reports bundle
  `com.apple.iokit.plugin.MultitouchHID`, version 5100.27, iPhoneOS,
  minimum OS 15.8, and type UUID
  `0516B563-B15B-11DA-96EB-0014519758EF`. The target
  `AppleMultitouchDriver` KernelCache personality references the same plugin
  path with that UUID; its factory UUID matches the plugin's
  `CFPlugInFactories`. This closes the static plugin-metadata lookup, not
  runtime provider attachment, plugin loading, touch operation, or 20H392
  compatibility. No binaries or filesystem images were committed.


- 2026-11-20: Repeated a read-only filename search for the donor
  `MultitouchHID*` plugin executable across both mounted 20H392 filesystem
  roots (`mnt/root/root` and `systemos-mnt/root/root`), including regular
  files and symlinks; no matching path was returned. The donor plugin
  directory contains only `Info.plist` and
  `_CodeSignature/CodeResources`. The previously inspected target plugin
  directory contains only `Info.plist`; a full target-root filename search
  remains outstanding. Mach-O comparison is deferred until executable files
  are located. This does not prove absence from every IPSW component or an
  unmounted/shared-cache location. No device or firmware operation occurred.

- 2026-11-20: Recorded the follow-up donor plugin inspection. The donor
  `Info.plist` declares `CFBundleExecutable=MultitouchHID`; its
  `_CodeSignature/CodeResources` plist reports top-level keys `files`,
  `files2`, `rules`, and `rules2`, with the printed `files` and `files2`
  entries empty. This is not cryptographic signature verification. The
  donor executable remains unlocated in both searched donor mount roots.
  The pasted home-directory search printed no matching paths but omitted
  the exact command/scope, so a complete target-root search is not claimed.
  Mach-O comparison remains blocked pending actual executable bytes.

- 2026-11-20: Mounted the complete iPhone9,1 / 19H422 filesystem DMG
  `098-68844-067.dmg` read-only with ipsw 3.1.749 at
  `$HOME/19H422-full-fs-mount`. The mount was verified as FUSE/read-only,
  and `root/System/Library/Extensions` was present. A full-mount search for
  regular files and symlinks named `MultitouchHID*` returned no paths.
  This records absence from that mounted filesystem image under the searched
  filename pattern, not from every IPSW component or unmounted image. The
  next static check is to inventory target dyld shared-cache files and their
  image paths. No device state was accessed or changed.

- 2026-11-20: Inspected the 20H392 donor SystemOS dyld shared-cache image
  list with ipsw 3.1.749. The supplied output confirms the same full
  MultitouchHID.plugin/MultitouchHID install path at donor image index 2557,
  version 6140.3.0.0.0, versus target index 1948, version 5100.27.0.0.0.
  Related donor image-list versions are 6140.1.0.0.0 for
  AppleHIDTransportSupport and 6140.3.0.0.0 for MultitouchSupport and
  MultitouchSessionFilterSupport; their target counterparts are 5100.32.0.0.0
  and 5100.27.0.0.0 respectively. A follow-up exact-path
  `ipsw dyld image -V` query returned prebuilt-loader/closure metadata,
  loader reference index 2556, and dependencies, but no UUID. The closure
  reference is not equated with image-list index 2557; implausible section
  offsets are excluded. The donor UUID was still pending at this point in the chronology; the later
  2026-11-20 follow-up below records the resolved donor UUID. This is cache
  metadata only; raw Mach-O comparison, signature verification, runtime plugin
  loading, and cross-board compatibility are not established. Added
  docs/20h392-dyld-cache-multitouch-audit.md and recorded the follow-up.

- 2026-11-20: Inspected the target 19H422 split dyld shared-cache image
  inventory with ipsw 3.1.749. The image list contains
  `/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID`
  at index 1948, version `5100.27.0.0.0`, UUID
  `304953E6-6B67-3CF1-B7CA-E011978210DE`. Related image records include
  `MultitouchSupport`, `MultitouchSessionFilterSupport`,
  `AppleHIDTransportSupport`, BackBoard HID frameworks, and SpringBoard.
  This explains why the complete filesystem search found no standalone file:
  the compiled plugin is represented in the dyld cache. Cache metadata does
  not prove runtime loading or touch operation. Next compare the matching
  20H392 donor cache entry; no device state was accessed or changed.


- 2026-11-20: Completed the donor 20H392 dyld UUID lookup using
  `ipsw dyld info --dylibs --json`. The exact
  `MultitouchHID.plugin/MultitouchHID` record appears once at image-list
  index 2557, version `6140.3.0.0.0`, UUID
  `78E1FB55-113A-3500-9D2D-1D8E282BED45`, load address
  `8757542912`. Compared with the 19H422 target record at index 1948,
  version `5100.27.0.0.0`, UUID
  `304953E6-6B67-3CF1-B7CA-E011978210DE`, the build identifiers differ.
  This is not a byte-level comparison or compatibility verdict. Updated the
  donor cache audit, donor/target KernelCache comparison, and M6 tracker.


- 2026-11-20: Began the target-native follow-up after the donor UUID was
  resolved. The next bounded check is a host-side
  `ipsw dyld image "$TARGET_CACHE" "$IMAGE"` query against the read-only
  iPhone9,1 / 19H422 shared cache. With the pinned ipsw 3.1.749 source,
  this command prefers a PrebuiltLoaderSet record when supported and
  otherwise falls back to the legacy image-array record. The latter reports
  image name, flags, UUID, CDHash and dependency edges (where present).
  The query deliberately omits verbose initializer/terminator offsets.
  This plan is read-only and makes no claim about runtime loading, IOKit
  attachment, or touch-event delivery. Added
  docs/iphone91-19h422-target-multitouch-loader-audit-plan.md.


- 2026-11-20: Completed the target-native 19H422 MultitouchHID loader query.
  The user's `ipsw dyld image` run exited 0 and returned a PrebuiltLoaderSet
  record for the expected full plugin path: VM Size `0x2e9f4000`, loader
  reference index 1947, flags `prebuilt|in-cache-dylib|objc|never-unload`,
  Info flags `initializers|regions=5`, exports trie offset `0x025fee90`
  size `0xf0d0`, five regions, and 13 dependencies (10 regular, 3 weak-link).
  Compared with the 20H392 donor record (14 dependencies: 11 regular,
  3 weak-link), the target output does not list the donor's regular
  `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter`
  dependency. The IOKit framework appears in both outputs but with different
  printed path forms. Both section-output blocks contain implausibly large
  decoded values and are excluded. The result is cache loader metadata only.
  Next search the existing 19H422 JSON image inventory for the direct
  dependency names and their versions/UUIDs where present. Added
  `docs/20h392-19h422-multitouch-loader-comparison.md`.


- 2026-11-20: Completed a selected-name lookup in the read-only iPhone9,1
  / 19H422 dyld image inventory for dependencies from the target
  MultitouchHID PrebuiltLoaderSet record. Seven relevant image records were
  returned: SymptomDiagnosticReporter (index 1455, version 174.140.2.0.0,
  UUID ED77A600-C0BE-3240-9693-BF5238095816), WirelessDiagnostics (6),
  CoreAccessories (343), CoreAnalytics (262), MultitouchSupport (1249),
  IOKit (71), and ProtocolBuffer (186). This resolves the earlier
  distinction: SymptomDiagnosticReporter is absent from the target
  MultitouchHID direct dependency list but is present in the target cache
  image inventory. A loose IOKit substring search also returned CoreAudioKit,
  which is a separate framework. Added
  docs/iphone91-19h422-multitouch-dependency-image-inventory.md and updated
  the loader comparison, target cache audit, and loader audit plan. The
  equivalent 20H392 donor inventory lookup is next. All results are static
  cache metadata; runtime dependency resolution, plugin loading, and target
  hardware behavior remain unverified.


- 2026-11-20: Completed the donor-side selected dependency image lookup from
  the read-only iPhone10,3 / 20H392 dyld inventory. The seven records are
  SymptomDiagnosticReporter (index 928, version 229.120.4.0.0),
  WirelessDiagnostics (600, 980.0.0.0.0), CoreAccessories (312,
  793.140.4.0.0), CoreAnalytics (226, 264.140.2.0.0), MultitouchSupport
  (1648, 6140.3.0.0.0), IOKit (30, 2022.140.2.701.1), and ProtocolBuffer
  (239, 294.30.6.7.2), with UUIDs recorded in the donor audit and complete
  comparison. All seven corresponding target image families are present,
  but all seven target/donor version strings and UUIDs differ. Image-list
  indexes are cache-local. This establishes distinct cache image identities,
  not byte-level compatibility, signature validity, dependency resolution,
  or runtime behavior. Added
  docs/20h392-19h422-multitouch-dependency-image-comparison.md and updated
  donor cache audit, loader comparison, target loader audit plan, and M6
  tracker. Next bounded host-side check: inspect MultitouchSupport loader
  metadata and compare it with the already inventoried AppleMultitouchSPI
  and AppleHIDTransportSPI KernelCache records. No device state changed.


- 2026-11-20: Completed read-only target 19H422 and donor 20H392
  `MultitouchSupport` PrebuiltLoaderSet inspection for the same full
  framework path. Target reports VM Size `0x3d3f0000`, loader ref 1248,
  `regions=5`, and six regular dependent-loader rows. Donor reports VM
  Size `0x354c8000`, loader ref 1647, `overridable|regions=5`, and
  seven regular rows; the only printed row difference is donor-side
  `/usr/lib/libc++.1.dylib`. Both records have five regions with the
  same permission sequence (r-x, rw-, rw-, rw-, r--), while their region
  mappings and loader flags differ. Their separate cache image-list records
  are target index 1249/version 5100.27.0.0.0/UUID
  0EAF98B3-8D31-3A90-A578-1787797B9467 and donor index
  1648/version 6140.3.0.0.0/UUID
  1B6ABB86-B8A9-3941-A66A-EC9715F6B034. Loader-ref indexes are kept
  distinct from image-list indexes. Implausible Sections output is excluded.
  Added docs/20h392-19h422-multitouchsupport-loader-comparison.md and
  updated target/donor cache audits, dependency comparison, and docs index.
  The exact `/usr/lib/libc++.1.dylib` image-list path was then
  confirmed once in each cache: target index 150/version 1300.36.0.0.0/
  UUID 16BE14F2-A677-3DF1-984D-BBAB893EE3B9 and donor index
  93/version 1500.65.0.0.0/UUID
  07F1FD58-7392-34FF-8D56-AE101EBC175A. Thus, the donor-only
  MultitouchSupport dependent-loader row is not evidence of target
  cache-image absence. Added
  docs/20h392-19h422-libcxx-cache-image-comparison.md and updated both
  cache audits and the MultitouchSupport loader comparison. Next bounded
  host-side check: compare target/donor MultitouchSupport export metadata.
  Runtime dependency resolution, plugin loading, and touch behavior remain
  unverified.

   
- 2026-11-20: Completed the exact `/usr/lib/libc++.1.dylib` lookup in
  the read-only target 19H422 and donor 20H392 dyld image inventories.
  Both contain one matching image-list entry. The target is index 150,
  version `1300.36.0.0.0`, UUID
  `16BE14F2-A677-3DF1-984D-BBAB893EE3B9`; the donor is index 93,
  version `1500.65.0.0.0`, UUID
  `07F1FD58-7392-34FF-8D56-AE101EBC175A`. The extra donor
  `MultitouchSupport` dependent-loader row is therefore not proof that
  libc++ is missing from the target cache. Image-list presence does not
  prove loader resolution or runtime loading. Added
  docs/20h392-19h422-libcxx-cache-image-comparison.md and updated the
  target/donor cache audits, MultitouchSupport loader comparison, parent
  dependency-image comparison, and docs index. Next bounded host-side check:
  compare target/donor `MultitouchSupport` export metadata. No device or
  firmware state was accessed or changed.


- 2026-11-20: Prepared the next M6 host-side comparison after the target/donor
  libc++ cache-image lookup. Reviewed the project's pinned ipsw 3.1.749 source
  at commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`: `dyld macho --symbols
  -V` prints a `Dyld Exports` section when the cached Mach-O has a non-empty
  export trie. Added a read-only plan and a command that saves both complete
  logs while displaying only those sections. Export results have not yet been
  collected; no byte-level comparison, ABI conclusion, runtime behavior, or
  device operation is claimed. No cache files or binaries are committed.


- 2026-11-20: Received the target 19H422 and donor 20H392
  `MultitouchSupport` `Dyld Exports` output. A line-by-line preliminary
  comparison identifies seven donor-only names:
  `_MTDeviceGetMaxHoverHeightValue`,
  `_MTDeviceGetMultipleFirmwaresConfig`,
  `_MTDeviceSetBinaryFiltersProperty`,
  `_MTDeviceShouldSkipFaceDetectionMode`,
  `_MTDeviceUpdateUILockState`,
  `_OBJC_CLASS_$_MTAHTSupport`, and
  `_OBJC_METACLASS_$_MTAHTSupport`; each is printed as `regular`.
  No target-only name was noticed in the supplied excerpt, but the excerpt
  omitted the target heading and both parser exit-code lines. Exact export
  totals, duplicate rows, and both-sided set differences remain pending
  automated parsing of the saved full logs. Added
  docs/20h392-19h422-multitouchsupport-export-comparison.md and an exact-set
  parser to the export audit plan. This is cache metadata only; ABI,
  runtime loading, IOKit attachment, touch delivery, and SpringBoard
  behavior remain unverified. No device or firmware state was accessed
  or changed.


- 2026-11-20: Completed the exact-set host-side comparison of the
  saved 19H422 target and 20H392 donor `MultitouchSupport` export logs.
  The parser printed no target-only names and seven donor-only names:
  `_MTDeviceGetMaxHoverHeightValue`,
  `_MTDeviceGetMultipleFirmwaresConfig`,
  `_MTDeviceSetBinaryFiltersProperty`,
  `_MTDeviceShouldSkipFaceDetectionMode`,
  `_MTDeviceUpdateUILockState`,
  `_OBJC_CLASS_$_MTAHTSupport`, and
  `_OBJC_METACLASS_$_MTAHTSupport`; all seven are printed as
  `regular`. No differing printed kinds were reported for common names.
  The parser counted 277 common names with different first printed
  addresses; these are cache-layout-specific values, not a compatibility
  test. The output pasted for this update began at the set-difference
  section, omitting row totals, unique-name counts, and duplicate-name
  summary lines, so those counts are not recorded. This completes the
  export-name set comparison only; ABI compatibility, runtime dependency
  resolution, plugin loading, IOKit attachment, touch delivery, and
  SpringBoard stability remain unverified. The physical iPhone 7 remains
  on iOS 12.1.4. No device or firmware state was accessed or changed.


- 2026-11-20: Cross-checked the public XNU machine-configuration history
  against the already-inspected target and donor KernelCache identities.
  Public `xnu-7195.121.3` lists T8010 in its normal ARM64 machine allowlist
  and includes the matching H9 board/CPU profile. Public
  `xnu-8019.80.24` and `xnu-8796.141.3` omit T8010; public 8796 also omits
  T8015 from its normal ARM64 list and board configuration. The 20H392
  donor KernelCache nevertheless reports XNU `8796.142.1.703.8~1` and
  `RELEASE_ARM64_T8015`, while the pinned public candidate is
  `xnu-8796.141.3`. This demonstrates that the public candidate alone
  does not reproduce all machine-selection inputs reflected by the shipped
  donor binary; it does not prove that private/product-specific source
  lacks T8015 or that a later XNU build cannot support T8010. Added
  `docs/xnu-public-source-vs-shipped-kernel.md`; exact source-to-binary
  provenance and target-specific configuration remain open. No kernel,
  firmware, boot, partition, or device state was changed.


## M6 launchd inventory comparison update (2026-11-20)

The user supplied the complete read-only inspector output for both the
iPhone10,3 / D22AP / iOS 16.7.16 / 20H392 donor and the iPhone9,1 / D10AP /
iOS 15.8.8 / 19H422 stock target reference. Exact provider-index set
comparison: 1,451 common names, 217 donor-only names, and 34 target-only
names. Provider-label assignments differ for 21 names present in both.
The donor has 532 LaunchDaemons entries, 530 unique labels, 1,707 service
occurrences, 1,668 distinct service names, and 21 multi-provider names. The
target has 475 entries, 475 unique labels, 1,493 service occurrences,
1,485 distinct service names, and 8 multi-provider names. The donor repeats
the `com.apple.CommCenter` and `com.apple.sysdiagnose` labels across
separate plist entries; the target has no duplicate job labels.

Selected comparison: backboardd and runningboardd service sets match
exactly; SpringBoard has one donor-only service; configd has one donor-only
service; mediaserverd has six donor-only and one target-only service; wifid,
bluetoothd, mobileactivationd, and notifyd service sets match exactly.
The donor has an additional `CommCenter-noncellular` plist entry. All
differences remain static plist metadata from different iOS releases, not
proof of runtime behavior or iPhone9,1 compatibility. The complete lists
and source plist hashes are in
`docs/iphone91-19h422-launchd-inventory-results.md`. M6 remains in
progress; M7/SpringBoard has not started. The physical iPhone 7 remains on
iOS 12.1.4; no device or firmware state was changed.


## M6 target BackBoard loader follow-up plan (2026-11-20)

The next bounded target-side evidence task is to query the iPhone9,1 / D10AP /
19H422 shared cache for the same four BackBoard-related framework loaders
already inventoried in the iPhone10,3 / D22AP / 20H392 donor:
BackBoardHIDEventFoundation, BackBoardHIDEventProcessors,
BackBoardServices, and IOMobileFramebuffer. Added
`docs/iphone91-19h422-backboard-loader-audit-plan.md` with the exact
read-only ipsw 3.1.749 command, the previously recorded target cache path,
per-query output/error capture, comparison fields, and parser caveats.
This is a collection plan only; no target loader results are claimed yet.
M6 remains in progress and M7/SpringBoard has not started. The physical
iPhone 7 remains on iOS 12.1.4.


## M6 BackBoard cache-access diagnosis (2026-11-20)

The user's four iPhone9,1 / 19H422 BackBoard loader queries all exited 1
with the same host error: opening the target dyld shared-cache file returned
`permission denied`. This is an input-file access failure, not evidence
that the frameworks are absent; no target loader records were collected.
The audit plan now requests read-only `namei -l`, `stat`, and
`test -r` output before any retry. M6 remains in progress; M7/SpringBoard
has not started. The physical iPhone 7 remains on iOS 12.1.4.


## M6 first successful target BackBoard loader result (2026-11-20)

The user supplied a successful standalone-ipsw 3.1.749 query for the
iPhone9,1 / D10AP / 19H422 target-reference cache:
`BackBoardServices.framework/BackBoardServices`. The locally extracted
official Linux x86_64 Debian package SHA-256 was verified as
`333cab58451330f0080c3c2b7bec3d9e6f4be588b27f6213a5233dd08821d071`.
The query exited 0 with no stderr and returned a prebuilt in-cache dylib
loader record (reference index 18, VM size `0x865a8000`, five regions),
with 12 regular dependencies and one AssertionServices re-export. The
printed dependency names and kinds match the recorded 20H392 donor
BackBoardServices record in the same order. The suspicious decoded
Swift/Objective-C Sections fields remain excluded; loader reference index
18 is not a cache image-list index, and no BindTargets section was printed.
This is one successful record only: target queries for
BackBoardHIDEventFoundation, BackBoardHIDEventProcessors, and
IOMobileFramebuffer remain pending. M6 remains in progress and M7/SpringBoard
has not started. Static loader metadata does not prove runtime loading,
IOKit attachment, HID event delivery, display operation, or iPhone9,1
compatibility. The physical iPhone 7 remains on iOS 12.1.4; no device or
firmware state was accessed or changed.


## M6 target BackBoard loader comparison completed (2026-11-20)

The four planned iPhone9,1 / D10AP / iOS 15.8.8 (19H422) target-reference
loader queries returned all four requested framework records using the
standalone IPSW 3.1.749 executable. Three supplied command results explicitly
show exit status 0 and empty stderr; the BackBoardHIDEventFoundation output
contains a valid record and empty stderr, but its explicit exit-status line
was absent from the supplied excerpt and is not asserted.

The target records contain 33 regular dependency rows, one re-export, and
zero weak-link rows. The corresponding iPhone10,3 / D22AP / iOS 16.7.16
(20H392) donor records contain 35 regular rows, one re-export, and zero
weak-link rows. BackBoardServices matches exactly (12 regular plus one
AssertionServices re-export); IOMobileFramebuffer matches exactly (four
regular); each target HID framework has one fewer regular dependency because
the donor lists StudyLog and the target output does not. No target-only
dependency rows were found. This difference is not attributed to hardware:
the source records are from different iOS releases and different devices.

The exact records and row-level comparison are in
`docs/iphone91-19h422-backboard-loader-results.md`. This completes the
bounded four-framework target BackBoard audit only. M6 remains in progress
for the broader userland investigation; M7/SpringBoard has not started.
The physical iPhone 7 remains on iOS 12.1.4. No device or firmware state
was accessed or changed.


## M1/M2 public XNU source matrix expanded (2026-11-20)

Extended the public T8010/H9 source survey beyond the original
7195/8019/8796 comparison. In the official
`apple-oss-distributions/xnu` repository, `xnu-8020.101.4`,
`xnu-8796.101.5`, `xnu-8796.141.3`, and `xnu-12377.1.9` all omit
T8010/H9 from the audited normal ARM64 machine-selection and board
configuration paths. Historical `xnu-7195.121.3` includes T8010,
`-mcpu=hurricane`, and the H9 header. Added exact tag-object and peeled
commit locks plus a six-snapshot host-only CI audit.

Important caveat: the target 19H422 KernelCache reports
`8020.241.44~1/RELEASE_ARM64_T8010`, while the public comparison tag is
`xnu-8020.101.4`; the donor 20H392 KernelCache reports
`8796.142.1.703.8~1/RELEASE_ARM64_T8015`, while the public candidate is
`xnu-8796.141.3`. Neither public tag is an exact source attestation for its
shipped binary. Product-specific build inputs and exact source commits remain
unknown; public source absence is not proof of absent shipped support.

Added `docs/driver-kernel-implementation-roadmap.md`. Target-specific kernel
and hardware-driver implementation remains blocked on G1-G6 source, build,
platform, DeviceTree, and handoff evidence. The next preparation task is the
transitive T8010/H9 source dependency closure. The first hardware driver cannot
be selected until the actual D10AP interrupt-controller and timer contracts
are resolved. M6 remains in progress; M7/SpringBoard has not started. The
physical iPhone 7 remains on iOS 12.1.4; no device or firmware state changed.


## M2 H9 full-tree source audit prepared (2026-11-20)

Added a read-only scanner, synthetic tests, and a full-source GitHub Actions
workflow for the historical XNU 7195 H9 feature macros versus the selected
XNU 8796 candidate. It records every identifier-token match in selected
source/build files, line context, H13 macro definitions, and locally
resolvable includes from H9.h. The scanner deliberately does not evaluate
preprocessor branches, macro expansion, SDK/generated headers, or private
build inputs. The workflow uploads its JSON result as an artifact; the
full-tree scan is pending that workflow run.

Also corrected the interrupt/timer evidence boundary: the static 19H422
DeviceTree already identifies an AIC master and AIC-timebase node and the
first register windows consumed by XNU's generic mapper. Complete IRQ
specifier/routing, per-core delivery, EOI, runtime timebase frequency,
counter behavior, and compatible driver implementation remain unknown.
Do not describe the nodes as undiscovered or start a speculative driver.

M6 remains in progress; M7/SpringBoard has not started. The physical iPhone 7
remains on iOS 12.1.4. No device or firmware state was accessed or changed.


## M2 full-tree H9 source scan completed (2026-11-20)

The pinned, read-only GitHub Actions scan of complete XNU 7195 and XNU 8796
source trees completed successfully in run
`44864823137`. Both source checkouts, the synthetic tests, the source scan,
and the JSON artifact upload passed. The scan covered 3,508 historical and
3,961 candidate source/build files and 12 H9 feature macros. Key findings:
three Hurricane conditional consumers remain in XNU 8796 but the old
startup `start.s` occurrence is absent; generic 16K-page, PAN, global-sleep,
PMU, KPC and kernel-protection consumers remain in source; the KTRR hook is
still generic but H13 uses CTRR; `HAS_MIGSTS`,
`HAS_CPMU_L2C_EVENTS`, and `SINGLE_STEP_RETIRE_ERRATA` had no textual
matches. H13 defines some common features but does not recreate the H9
profile. All counts are textual inventory, not active compile paths or
hardware conclusions. The local include walk resolved 23 files and left two
SDK/include-path items unresolved. Exact results and cautions are recorded in
`docs/h9-source-fulltree-audit.md`.

The next preparation task is now a manual source migration assessment for
CPU startup/errata, KTRR-versus-CTRR, PMU/AIC coupling, pmap/page-size
protection, and sleep/power features. Separately, static D10AP AIC and
AIC-timebase nodes/register windows are already known; the missing facts are
interrupt routing/EOI and runtime timer semantics/frequency, plus confirmation
of a compatible AIC controller implementation. No target kernel or driver
patch is authorized by this scan. M6 remains in progress; M7/SpringBoard
has not started. The physical iPhone 7 remains on iOS 12.1.4.

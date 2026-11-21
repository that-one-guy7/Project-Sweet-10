# 19H422 / 20H392 selected KEXT metadata-field comparison

## Scope and provenance

This report records the user-supplied read-only extraction of selected
complete top-level records from the parsed KEXT JSON inventories:

- Target: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / build `19H422`
- Donor: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / build `20H392`

The extraction selected exact bundle IDs from both JSON arrays and printed
bundle identity/version fields, `io_kit_personalities`, and
`os_bundle_libraries`. It did not print every possible field in each original
JSON object, so this report is a comparison of the selected metadata fields,
not a complete-record or executable comparison. It did not inspect executable bytes or the mounted
filesystem. "Not present" below means no matching top-level record in the
selected JSON inventory.

The local test result supplied earlier was 64 tests passing. This report is
documentation based on the pasted output; it does not change the tests or
claim a new CI run.

## 1. AppleA7IOP: shared record retains T8010 and T8015 matches

Both inventories contain the same top-level ID and path:

- ID: `com.apple.driver.AppleA7IOP`
- Executable: `AppleA7IOP`
- Path: `/System/Library/Extensions/AppleA7IOP.kext`
- Target version: `1.0.2`, short version `1.0`, compatible version `1.0.0`
- Donor version fields are omitted in the supplied JSON export; donor SDK is
  `iphoneos16.7.internal`.

The supplied target and donor personality maps show the same set of
personality names and the same displayed `IOClass`,
`IOProviderClass=AppleARMIODevice`, and `IONameMatch` values. The
important graphics-IO personality is:

| Personality | IOClass | IONameMatch |
|---|---|---|
| `AppleA7IOPV2-GFX` | `AppleA7IOPV2GFX` | `iop-gfx,s8000`, `iop-gfx,t8010`, `iop-gfx,t8011` |

Both inventories also include later-generation personalities:

| Personality | IOClass | IONameMatch |
|---|---|---|
| `AppleA7IOPV4` | `AppleA7IOPV4` | `iop,t8015` |
| `AppleA7IOPV4-GFX` | `AppleA7IOPV4GFX` | `iop-gfx,t8015` |
| `AppleA7IOPV4PMP` | `AppleA7IOPV4PMP` | `iop-pmp,t8015` |
| `AppleASC-ANS2` | `AppleASCANS2` | `iop-ans2,t8015` |

This is the clearest positive cross-generation metadata result in this
extraction: the 20H392 donor's AppleA7IOP record still advertises the
T8010-capable V2 graphics-IO match, alongside T8015 V4 personalities. It
makes AppleA7IOP a high-priority candidate for further **static** study.

Both dependency maps name AppleARMPlatform, IOSlaveProcessor, and the same
six KPI IDs. The target has populated version strings
(`AppleARMPlatform=1.0.0`, `IOSlaveProcessor=1.0.0`, KPIs `8.0`);
the donor export leaves the corresponding values empty. Those empty values
are recorded as serialized metadata, not as dependency absence or ABI
failure.

The match string alone does not prove that the donor's AppleA7IOP binary
contains a functional T8010 path or that it is compatible with the target
XNU, firmware interfaces, or hardware.

## 2. AppleEmbeddedTempSensor: broad multi-generation personality set retained

Both inventories contain `com.apple.driver.AppleEmbeddedTempSensor` at
`/System/Library/Extensions/AppleEmbeddedTempSensor.kext`, with the same
personality names and the same displayed `IOClass`, provider,
`IONameMatch`, `IOUserClientClass`, and numeric action values.

In particular, both records retain the T8010 entries:

- `AppleDieTempController`: `dietempctl,t8010`
- `AppleT700XTempSensor`: `tempsensor,t8010`
- `AppleVTempDispatcher`: `vtempctl,t8010`

The `AppleDieTempController` personality also contains the T8015 match
`dietempctl,t8015`; `AppleVTempDispatcher` contains
`vtempctl,t8015`. The dedicated `AppleT8015TempSensor` personality
matches T8015/T8020/T8027/T8030, while the T8010-era
`AppleT700XTempSensor` personality has its own broader legacy list.

Selected export differences:

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| `IOResourceMatch` in the displayed personalities | `IOKit` | Empty strings |
| `IOProbeScore` in most displayed personalities | `100` | Empty strings |
| `AppleT700XTempSensor.IOProbeScore` | `100` | `100` |
| Version / short version | `1.0.0` / `1.0.0` | Omitted |
| Dependency version strings | Populated | Empty strings |

This is another positive cross-generation metadata lead, but the empty
serialized values cannot safely be interpreted as runtime property values.
No temperature readout, power-management action, or thermal behavior was
tested.

## 3. T8010 and T8015 platform roots are parallel but distinct records

The target contains `com.apple.driver.AppleT8010`; the donor contains
`com.apple.driver.AppleT8015`. The supplied records show parallel
personality structure:

| Role | Target T8010 | Donor T8015 |
|---|---|---|
| ARM-IO root | `AppleT8010IO` / `arm-io,t8010` | `AppleT8015IO` / `arm-io,t8015` |
| Memory-cache controller | `AppleT8010MemCacheController` / `mcc,t8010` | `AppleT8015MemCacheController` / `mcc,t8015` |
| Platform error handler | `AppleT8010PlatformErrorHandler` / `error-handler,t8010` | `AppleT8015PlatformErrorHandler` / `error-handler,t8015` |

The displayed provider classes also correspond structurally:
`IOPlatformDevice` for the ARM-IO root and
`AppleARMIODevice` for the memory-cache and error-handler personalities.

The key dependency difference is explicit:

- Target AppleT8010 depends on
  `com.apple.driver.AppleHurricaneErrorHandler`.
- Donor AppleT8015 depends on
  `com.apple.driver.AppleMonsoonErrorHandler`.

Both records also name AppleARMPlatform, IOReportFamily, and the displayed
KPI set. The donor dependency-version values are empty in the supplied
export, while the target values are populated. This comparison supports a
platform-family correspondence, not substitution of T8015 components for
T8010 components.

## 4. Error-handler bundle records: same class, different hardware match

The target Hurricane and donor Monsoon records both use:

- Personality name: `AppleARM64ErrorHandler`
- `IOClass=AppleARM64ErrorHandler`
- `IOProviderClass=AppleARMIODevice`

They differ in `IONameMatch`:

| Target 19H422 | Donor 20H392 |
|---|---|
| `cpu-error-handler,hurricane` | `cpu-error-handler,monsoon` |

The target record reports version `1`, short version `1.0`, and
compatible version `1.0`; the corresponding donor fields are omitted.
The target personality reports `IOPlatformActiveAction=88000`, whereas
the donor export reports `0`. This difference is recorded as a difference
in the selected serialized metadata only; it is not evidence about the
drivers' actual implementation or runtime behavior.

## 5. Display: related personality shape, different provider class and SoC IDs

The target contains `AppleMobileDispH9P`; the donor contains
`AppleMobileDispH10P`. Both use the personality name
`AppleADBE0-8970X` and show the same backlight match property
`backlight-control=true`.

They differ in the relevant driver metadata:

| Field | Target H9P | Donor H10P |
|---|---|---|
| IOClass | `AppleMobileADBE0` | `AppleCLCD` |
| IONameMatch | `disp0,t8010`, `disp1,t8010` | `disp0,t8015` |
| Bundle ID | `com.apple.driver.AppleMobileDispH9P` | `com.apple.driver.AppleMobileDispH10P` |
| Version | `140.0` | `140.0` |

The output shows different direct dependency sets: the target lists
`com.apple.AUC`, AppleM2ScalerCSCDriver, IOAVFamily,
IOMobileGraphicsFamily, IOSurface, and KPI entries; the donor includes
AppleSEPManager and a different serialized dependency-value pattern.
This is not evidence that the display drivers are interchangeable.

## 6. GPU: target AGXG9P is not in donor inventory; donor AGXG10P is not in target

The target contains `com.apple.AGXG9P`; the donor contains
`com.apple.AGXG10P`. The opposite bundle ID was not present as a selected
top-level record in each inventory.

Target AGXG9P personalities `AGXG9P_A0` and `AGXG9P_B0` both use
`IOClass=AGXAcceleratorG9P_*`, `IONameMatch=gpu,t8010`, and
`MetalPluginName=AGXMetalA10`. The target record reports version and
short version `190.23`, and `IOSourceVersion=190.23`.

Donor AGXG10P personalities `AGXG10P_A0` and `AGXG10P_B0` both use
`IONameMatch=gpu,t8015`; their classes are
`AGXAcceleratorG10P_A0` and `AGXAcceleratorG10P_B0`. The A0 entry names
`AGXMetalG10A0`, while B0 names `AGXMetalA11`. The donor export omits
the displayed version fields and contains empty `IOSourceVersion` and
dependency version values.

This is a material generation-specific gap in the inventories. No GPU
binary, userspace Metal component, firmware contract, or rendered output
was compared or tested.

## 7. Camera interface: separate H9 and H10 records

The target contains `AppleH9CameraInterface` with personality
`s5l8960x`, `IOClass=AppleH9CamIn`, and
`IONameMatch=isp,s5l8960x`.

The donor contains `AppleH10CameraInterface`, whose printed personalities
match `isp,t8015`, `isp,t8020`, `isp,t8030`, `isp,t8101`, and
`isp,t8103`, with `IOClass=AppleH10CamIn`. The donor record also names
`AppleH10PearlCameraInterface` in its dependency map; the target H9
record does not show that dependency.

These are different bundle records, classes, and platform matches. The
target's H9 camera interface is not present as a selected top-level record
in the donor inventory, and the donor H10 interface is not present in the
target inventory. No camera pipeline operation is inferred.

## Conclusions and next bounded static work

1. **Highest-priority shared candidates:** AppleA7IOP and
   AppleEmbeddedTempSensor. Both donor records preserve T8010-specific
   personality strings, and the supplied maps show their selected
   personality structure matching the target. These are promising metadata
   findings, not compatibility proof.
2. **Platform/error-handler correspondence:** AppleT8010/Hurricane and
   AppleT8015/Monsoon have parallel structures but distinct SoC matches and
   dependency identities.
3. **Hardware-specific gaps:** H9P display, AGXG9P GPU, and H9 camera are
   target records; H10P display, AGXG10P GPU, and H10 camera are donor
   records. Their distinct classes and match strings should remain separate.
4. **Next static comparison:** prioritize exact property-tree comparison of
   the shared AppleA7IOP and AppleEmbeddedTempSensor records, then compare
   target and donor userland graphics dependencies by exact image identity
   (UUID/version) from the already parsed shared-cache inventories. Avoid
   treating empty plist-export fields as runtime values.

## Evidence limits

- These are parsed KEXT JSON records, not executable code or runtime
  registry results.
- Same bundle ID, personality name, class, or T8010 match string does not
  prove binary identity, private KPI/ABI compatibility, driver attachment,
  or hardware function.
- Empty donor values and omitted donor fields are export observations, not
  proof that a property or dependency is absent at runtime.
- No KEXT binary was extracted, disassembled, executed, or loaded.
- No device, firmware, partition, or boot state was accessed or modified.
- The physical iPhone 7 remains on iOS 12.1.4. M1 remains in progress;
  M7/SpringBoard has not started.

# 19H422 / 20H392 seven-pair recursive KEXT metadata comparison

## Scope and provenance

This report records the user-supplied output of
`tools/compare_kext_record_details.py` run against the parsed KEXT JSON
inventories for:

- Target reference: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / build
  `19H422`
- Donor reference: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / build
  `20H392`

The user reports the full local test suite completed with **80 tests
passing**. This is a user-supplied local result; this documentation change
does not rerun or independently attest to that local environment.

All seven requested target/donor pairs are reported PRESENT as exact
top-level records in their respective JSON inventories. The comparison
reported **261 differing JSON paths** across the seven record pairs.

| Pair | Target/donor top-level records | Differing JSON paths |
|---|---|---:|
| AppleA7IOP / AppleA7IOP | Present / present | 25 |
| AppleEmbeddedTempSensor / AppleEmbeddedTempSensor | Present / present | 45 |
| AppleT8010 / AppleT8015 | Present / present | 39 |
| AppleHurricaneErrorHandler / AppleMonsoonErrorHandler | Present / present | 35 |
| AppleMobileDispH9P / AppleMobileDispH10P | Present / present | 35 |
| AGXG9P / AGXG10P | Present / present | 41 |
| AppleH9CameraInterface / AppleH10CameraInterface | Present / present | 41 |
| **Total** | **7 pairs** | **261** |

A differing path is not synonymous with a broken field or an incompatibility.
The total includes renamed SoC-specific personalities, build/export metadata,
empty-versus-populated dependency values, load-address metadata, and
ordinary per-generation version fields.

## 1. AppleA7IOP — 25 paths

The target and donor top-level records are both present under the same
bundle ID, `com.apple.driver.AppleA7IOP`.

**No differences were emitted under `io_kit_personalities`.** This includes
the V2 graphics-IO personality with `iop-gfx,t8010` as well as the other
displayed personality entries. The parsed donor record retains the same
serialized personality tree as the target in this comparison.

The 25 differences are outside the personality tree:

- Target build, platform, SDK-build, Xcode, package, minimum-OS, signature,
  and version metadata that is omitted in the donor export.
- A different `executable_load_addr` value.
- SDK value `iphoneos15.8.internal` versus
  `iphoneos16.7.internal`.
- Six dependency-version fields that are populated in the target and empty
  strings in the donor.
- `supported_platforms[0]` and
  `ui_required_device_capabilities[0]`, populated in the target and empty
  strings in the donor.

**Interpretation:** this is the strongest positive metadata result in the
seven-pair set. The shared donor AppleA7IOP record retains the complete
serialized T8010/T8015 personality map shown in the target. It does not prove
the donor executable contains functioning T8010 code paths or is binary/ABI
compatible with the target XNU.

## 2. AppleEmbeddedTempSensor — 45 paths

Both inventories contain the same top-level bundle ID and record path.

The displayed personality names, `IOClass` values, provider classes,
`IONameMatch` entries, user-client classes, and numeric platform action
values are retained in the donor export. In particular, the T8010 match
entries remain:

- `AppleDieTempController`: `dietempctl,t8010`
- `AppleT700XTempSensor`: `tempsensor,t8010`
- `AppleVTempDispatcher`: `vtempctl,t8010`

The 45 differences include **17 personality property paths**:

- Eight `IOProbeScore` paths: target values are `100`; donor values are
  empty strings.
- Nine `IOResourceMatch` paths: target values are `IOKit`; donor values
  are empty strings.

The T8010 `IONameMatch` entries are not among the changed paths. Other
differences include omitted target build/version metadata, the SDK
difference, a changed load-address field, and eight dependency-version
values that are populated in the target and empty in the donor. The
dependency IDs remain present in both records.

**Interpretation:** the donor metadata retains the target's T8010 sensor
personality matches. The blank `IOProbeScore` and `IOResourceMatch`
strings are observations about the serialized donor JSON, not verified
runtime property values and not proof of missing sensor functionality.

## 3. AppleT8010 / AppleT8015 — 39 paths

Both platform-root records are present, but they are distinct SoC-specific
bundles.

The records show parallel roles:

| Target T8010 | Donor T8015 | Role |
|---|---|---|
| `AppleT8010IO` / `arm-io,t8010` | `AppleT8015IO` / `arm-io,t8015` | ARM-IO root |
| `AppleT8010MemCacheController` / `mcc,t8010` | `AppleT8015MemCacheController` / `mcc,t8015` | Memory-cache controller |
| `AppleT8010PlatformErrorHandler` / `error-handler,t8010` | `AppleT8015PlatformErrorHandler` / `error-handler,t8015` | Platform error handler |

The corresponding classes and provider roles are parallel, but the names
and match strings are not interchangeable.

The dependency-map identities also differ:

- Target AppleT8010 names
  `com.apple.driver.AppleHurricaneErrorHandler` with version `1.0`.
- Donor AppleT8015 names
  `com.apple.driver.AppleMonsoonErrorHandler` with an empty serialized
  value.

The donor also serializes its common dependency-version values as empty
strings. The 39-path total includes the distinct top-level IDs, names,
paths, executables, the three target-only and three donor-only personality
keys, dependency-map keys, and build/export metadata.

**Interpretation:** the T8015 platform-root metadata is structurally
analogous to T8010, but it is explicitly configured for T8015. This does not
establish that the T8015 root driver can serve as a T8010 root driver.

## 4. Hurricane / Monsoon error handlers — 35 paths

Both error-handler records are present. They share:

- Personality key `AppleARM64ErrorHandler`
- `IOClass=AppleARM64ErrorHandler`
- `IOProviderClass=AppleARMIODevice`

They differ in hardware match:

- Target: `cpu-error-handler,hurricane`
- Donor: `cpu-error-handler,monsoon`

The target personality reports `IOPlatformActiveAction=88000`; the donor
reports `0`. The copyright range also differs by one year. Bundle IDs,
names, paths, and executable names differ accordingly, and donor dependency
version values are empty strings.

**Interpretation:** same class and provider shape, but distinct SoC match
strings and a different serialized platform action value. This is evidence
of a related driver family, not evidence that the binaries have identical
behavior or can be substituted.

## 5. H9P / H10P display — 35 paths

Both display bundle records are present. Their single printed personality
key is `AppleADBE0-8970X`, and their BacklightMatching property includes
`backlight-control=true` on both sides.

The important differences are:

| Field | Target H9P | Donor H10P |
|---|---|---|
| IOClass | `AppleMobileADBE0` | `AppleCLCD` |
| IONameMatch | `disp0,t8010`, `disp1,t8010` | `disp0,t8015` |
| Number of match entries | 2 | 1 |
| Bundle | `AppleMobileDispH9P` | `AppleMobileDispH10P` |

The serialized dependency maps also differ: the donor includes an
`AppleSEPManager` key with an empty value, while several target-listed
dependencies and their values differ. Both records have display version
`140.0` in the inspected metadata, but that shared version label does not
mean the driver implementations are the same.

**Interpretation:** the provider class and SoC display matches differ. This
is a significant target-specific display gap; the donor H10P personality is
not shown matching the target's T8010 display nodes.

## 6. AGXG9P / AGXG10P GPU — 41 paths

Both GPU bundle records are present, but each inventory contains its own
generation-specific record and personality names.

Target AGXG9P has:

- `AGXG9P_A0` and `AGXG9P_B0`
- Classes `AGXAcceleratorG9P_A0` and
  `AGXAcceleratorG9P_B0`
- `IONameMatch=gpu,t8010`
- `MetalPluginName=AGXMetalA10`

Donor AGXG10P has:

- `AGXG10P_A0` and `AGXG10P_B0`
- Classes `AGXAcceleratorG10P_A0` and
  `AGXAcceleratorG10P_B0`
- `IONameMatch=gpu,t8015`
- Metal plugin labels `AGXMetalG10A0` and `AGXMetalA11`

The target record reports `190.23` version/source metadata. Donor export
fields for those version/source values are omitted or empty. The target's
and donor's dependency maps share many IDs, but the donor version values
are empty strings.

**Interpretation:** unlike AppleA7IOP, the GPU records do not share the
same T8010/T8015 personality tree. Their accelerator classes, SoC matches,
and Metal plugin labels are generation-specific. This is the clearest
graphics-specific compatibility gap in the supplied KEXT comparison.
No binary or userland Metal image compatibility was tested.

## 7. H9 / H10 camera interfaces — 41 paths

Both camera-interface records are present, but the personality trees
are different.

Target AppleH9CameraInterface has:

- Personality key `s5l8960x`
- `IOClass=AppleH9CamIn`
- `IONameMatch=isp,s5l8960x`

Donor AppleH10CameraInterface has five personalities named `t8015`,
`t8020`, `t8030`, `t8101`, and `t8103`. They use
`IOClass=AppleH10CamIn` and match the corresponding ISP SoC string.
The donor also names `AppleH10PearlCameraInterface` as a dependency,
with an empty serialized value.

**Interpretation:** the donor record does not advertise a T8010 or
`s5l8960x` camera personality. The target H9 camera personality is not
present in the donor record. This is a target-specific camera gap in the
selected inventories; it is not a statement about every possible alternate
camera path.

## Overall interpretation and priority

The recursive comparison separates the seven pairs into three useful
groups:

1. **Most encouraging shared metadata**
   - AppleA7IOP has no personality-tree differences, including the T8010
     graphics-IO match.
   - AppleEmbeddedTempSensor retains the target's T8010 match strings;
     donor empty fields remain unresolved export values.

2. **Parallel but SoC-specific platform families**
   - AppleT8010 versus AppleT8015.
   - Hurricane versus Monsoon error handlers.
   - These pairs share recognizable structure but have different match
     strings and dependency identities.

3. **Clear target/donor hardware-specific differences**
   - H9P versus H10P display.
   - AGXG9P versus AGXG10P GPU.
   - H9 versus H10 camera.
   - Their personality names, classes, and SoC match strings differ.

The next useful work is to prioritize source-level interface research for
AppleA7IOP and AppleEmbeddedTempSensor, and keep the H9P display and AGXG9P
GPU as independent target-specific research areas. Metadata should guide
which interfaces to investigate, not be used to declare a binary compatible.

## Evidence boundaries

- The comparison reads parsed JSON records only.
- Difference counts are metadata-path counts, not compatibility scores.
- Empty strings and omitted keys are not interpreted as runtime absence.
- A matching personality tree does not prove executable identity, private
  KPI/ABI compatibility, provider attachment, or hardware operation.
- No KEXT binary was inspected, executed, or loaded.
- No device, firmware, partition, or boot state was accessed or changed.
- The physical iPhone 7 remains on iOS 12.1.4.
- M1 remains in progress; M7/SpringBoard has not started.

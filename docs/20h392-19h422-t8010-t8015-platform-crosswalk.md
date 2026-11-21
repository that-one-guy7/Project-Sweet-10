# 19H422 T8010 vs 20H392 T8015 platform KEXT metadata crosswalk

## Scope and inputs

This note records the read-only output supplied from
`tools/search_kext_inventory.py` after PR #92. The search scanned parsed
`ipsw kernel kext --json` inventories:

- Target: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / `19H422`
  (230 top-level records).
- Donor: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / `20H392`
  (239 top-level records).

The normalized terms were `hurricane`, `errorhandler`,
`platformerror`, `t8010`, `t8015`, and `h9`. The search reported 15
target records and 19 donor records with at least one hit. Category counts
overlap: a record can match identity, personality, dependency, and other
metadata categories simultaneously. The broad `h9` substring also matched
large encoded `HIDScrollAccelerationTable` values in TopCase trackpad
personalities; those are incidental keyword hits, not evidence of H9 hardware
support.

The user's full local test run after PR #92 reported:

```text
Ran 64 tests in 0.283s

OK
```

## Main finding: Hurricane and Monsoon are parallel metadata records

The exact-ID supporting inventory result remains unchanged:
`com.apple.driver.AppleHurricaneErrorHandler` is present in the target's
selected top-level inventory and absent from the donor's selected top-level
inventory.

The keyword scan found a plausible donor-side counterpart under a different
identity:

| Evidence | Target 19H422 / T8010 | Donor 20H392 / T8015 |
|---|---|---|
| Top-level bundle ID | `com.apple.driver.AppleHurricaneErrorHandler` | `com.apple.driver.AppleMonsoonErrorHandler` |
| Bundle name / executable | `AppleHurricaneErrorHandler` | `AppleMonsoonErrorHandler` |
| Bundle path | `/System/Library/Extensions/AppleHurricaneErrorHandler.kext` | `/System/Library/Extensions/AppleMonsoonErrorHandler.kext` |
| Personality name | `AppleARM64ErrorHandler` | `AppleARM64ErrorHandler` |
| Personality IOClass | `AppleARM64ErrorHandler` | `AppleARM64ErrorHandler` |
| Personality IONameMatch | `cpu-error-handler,hurricane` | `cpu-error-handler,monsoon` |

The parent SoC bundles show a matching structural pattern:

| Evidence | Target 19H422 | Donor 20H392 |
|---|---|---|
| Parent bundle | `AppleT8010` | `AppleT8015` |
| Platform-error personality | `AppleT8010PlatformErrorHandler` | `AppleT8015PlatformErrorHandler` |
| Personality IOClass | `AppleT8010PlatformErrorHandler` | `AppleT8015PlatformErrorHandler` |
| Personality IONameMatch | `error-handler,t8010` | `error-handler,t8015` |
| Direct dependency reference | `com.apple.driver.AppleHurricaneErrorHandler` | `com.apple.driver.AppleMonsoonErrorHandler` |

This is strong evidence of parallel *metadata roles*: both SoC bundles name a
platform-error-handler personality and reference a SoC-named supporting error
handler; both supporting bundles expose the same `AppleARM64ErrorHandler`
IOClass, while their match strings identify different CPU families.

It is **not** evidence that the two KEXT executables are byte-identical,
share a private KPI/ABI, can be substituted, attach to the same provider, or
behave equivalently. The different `IONameMatch` strings are material
hardware-specific distinctions and must be preserved.

## Other cross-generation metadata

### AppleA7IOP

Both inventories contain `com.apple.driver.AppleA7IOP`. Both report the
`AppleA7IOPV2-GFX` personality with an `iop-gfx,t8010` match. The same
records also contain T8015-specific personalities/matches, including
`AppleA7IOPV4` (`iop,t8015`), `AppleA7IOPV4-GFX`
(`iop-gfx,t8015`), and `AppleA7IOPV4PMP` (`iop-pmp,t8015`).

This is a useful lead: the serialized metadata contains both T8010 and T8015
match strings in one bundle. It does not show which personality is selected
on a given board, whether the corresponding provider exists, or whether the
driver implementation works on both devices.

### AppleEmbeddedTempSensor

Both inventories contain `com.apple.driver.AppleEmbeddedTempSensor`. The
printed metadata includes T8010 and T8015 match strings in shared
personalities: `dietempctl,t8010` / `dietempctl,t8015`,
`tempsensor,t8010`, and `vtempctl,t8010` / `vtempctl,t8015`.
The output also shows an `AppleT8015TempSensor` personality matched to
`tempsensor,t8015`.

This is another example of multi-generation strings in a shared bundle,
not proof of driver attachment or cross-board behavior.

## Clear target/donor hardware-specific splits

The scan also reinforces that major display and GPU KEXT identities differ:

| Subsystem | Target 19H422 / T8010 | Donor 20H392 / T8015 |
|---|---|---|
| Display KEXT | `AppleMobileDispH9P`, matches `disp0,t8010` and `disp1,t8010` | `AppleMobileDispH10P`, matches `disp0,t8015` |
| GPU KEXT | `AGXG9P`, matches `gpu,t8010` | `AGXG10P`, matches `gpu,t8015` |
| Camera interface identity | `AppleH9CameraInterface` | `AppleH10CameraInterface`, with `isp,t8015` match |

The identities and match strings are target/donor-specific in these exports.
This makes the target-native display/GPU/camera metadata more important to
preserve, rather than assuming the donor's H10P/G10P records apply to T8010.

## Interpretation

The scan refines, but does not erase, the 20-ID exact-inventory result:

- All 20 selected IDs remain present in target 19H422.
- 13 of 20 selected exact IDs remain present in donor 20H392.
- The exact Hurricane ID remains the single supporting exact-ID omission.
- The donor has a differently named Monsoon record with a parallel
  `AppleARM64ErrorHandler` personality and a matching T8015 parent-bundle
  dependency pattern.
- Some shared KEXT records advertise both T8010 and T8015 strings.
- Display/GPU/camera KEXT identities are visibly SoC-specific.

A JSON keyword hit does not validate executable code, ABI, private KPI
contracts, provider construction, service attachment, device-tree matching
at runtime, or hardware operation. Empty or omitted export fields are not
interpreted as negative values. No KernelCache binary or KEXT executable was
examined for this note.

## Next bounded host-side work

Prioritize detailed JSON metadata crosswalks for the shared
`AppleA7IOP` and `AppleEmbeddedTempSensor` bundles, followed by the target
H9P/G9P and donor H10P/G10P dependency/personality records. Keep exact bundle
identity, personality match strings, provider declarations, and dependency
names as separate evidence categories.

M1 remains in progress; M7/SpringBoard has not started. The physical iPhone 7
remains on iOS 12.1.4. No device, firmware, partition, binary, or boot state
was accessed or changed.
